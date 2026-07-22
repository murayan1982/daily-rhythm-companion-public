from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import AppConfig
from app.services.google_health_credentials import GoogleHealthOAuthCredentials
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_REDIRECT_URI_NOT_CONFIGURED = (
    "redirect_uri_not_configured"
)
GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED = "http_request_failed"
GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE = (
    "invalid_token_response"
)


@dataclass(frozen=True)
class GoogleHealthTokenRequestParts:
    """
    Internal request parts for Google OAuth token exchange.

    This may contain sensitive values such as client_secret and authorization
    code. Do not return it directly from API responses or print it to logs.
    """

    endpoint: str
    method: str
    headers: dict[str, str]
    form_data: dict[str, str]


@dataclass(frozen=True)
class GoogleHealthTokenRequestPreview:
    """
    Non-sensitive preview of a Google OAuth token request.

    This intentionally does not expose client secrets or authorization codes.
    """

    endpoint: str
    grant_type: str
    redirect_uri: str
    has_client_id: bool
    has_client_secret: bool
    has_code: bool


@dataclass(frozen=True)
class GoogleHealthNormalizedTokenResponse:
    """
    Normalized Google OAuth token response for local storage.

    Token values are sensitive. Do not expose this object through API
    responses or logs.
    """

    access_token: str
    token_type: str
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None

    def to_storage_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "access_token": self.access_token,
            "token_type": self.token_type,
        }

        if self.expires_in is not None:
            data["expires_in"] = self.expires_in

        if self.refresh_token:
            data["refresh_token"] = self.refresh_token

        if self.scope:
            data["scope"] = self.scope

        return data


@dataclass(frozen=True)
class GoogleHealthTokenExchangeResult:
    """
    Result of the Google OAuth token exchange boundary.

    request_parts may contain sensitive values and must stay internal.
    """

    attempted: bool
    request_prepared: bool
    real_exchange_enabled: bool
    saved: bool
    message: str
    request_parts: GoogleHealthTokenRequestParts | None = None
    request_preview: GoogleHealthTokenRequestPreview | None = None
    error: str | None = None


def prepare_google_health_token_exchange_request(
    *,
    token_uri: str,
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str | None,
) -> GoogleHealthTokenExchangeResult:
    """
    Prepare internal request parts for Google OAuth authorization-code exchange.

    This does not perform HTTP POST. It only builds request parts and a
    non-sensitive preview.
    """

    if not redirect_uri:
        return GoogleHealthTokenExchangeResult(
            attempted=False,
            request_prepared=False,
            real_exchange_enabled=False,
            saved=False,
            message=(
                "Google Health token request could not be prepared because "
                "redirect URI is not configured."
            ),
            request_parts=None,
            request_preview=None,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_REDIRECT_URI_NOT_CONFIGURED,
        )

    request_parts = GoogleHealthTokenRequestParts(
        endpoint=token_uri,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        form_data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
    )

    return GoogleHealthTokenExchangeResult(
        attempted=False,
        request_prepared=True,
        real_exchange_enabled=False,
        saved=False,
        message="Google Health token request was prepared.",
        request_parts=request_parts,
        request_preview=build_google_health_token_request_preview(
            request_parts
        ),
        error=None,
    )


def exchange_google_health_authorization_code(
    *,
    config: AppConfig,
    credentials: GoogleHealthOAuthCredentials,
    code: str,
) -> GoogleHealthTokenExchangeResult:
    """
    Prepare and optionally exchange a Google OAuth authorization code.

    Real HTTP POST remains disabled unless
    GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1.
    """

    prepare_result = prepare_google_health_token_exchange_request(
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        code=code,
        redirect_uri=config.google_health_redirect_uri,
    )

    if not prepare_result.request_prepared or prepare_result.request_parts is None:
        return prepare_result

    if not config.google_health_enable_real_token_exchange:
        return GoogleHealthTokenExchangeResult(
            attempted=False,
            request_prepared=True,
            real_exchange_enabled=False,
            saved=False,
            message=(
                "Google Health token request was prepared, but real token "
                "exchange is disabled."
            ),
            request_parts=prepare_result.request_parts,
            request_preview=prepare_result.request_preview,
            error=None,
        )

    try:
        response = httpx.post(
            prepare_result.request_parts.endpoint,
            headers=prepare_result.request_parts.headers,
            data=prepare_result.request_parts.form_data,
            timeout=10.0,
        )
    except httpx.HTTPError:
        return GoogleHealthTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Google Health token exchange failed.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
        )

    try:
        response_data = response.json() if response.content else {}
    except ValueError:
        return GoogleHealthTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Google Health token exchange returned invalid JSON.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
        )

    if not isinstance(response_data, dict) or response.status_code >= 400:
        return GoogleHealthTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Google Health token exchange returned an error response.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
        )

    try:
        token_data = normalize_google_health_token_response(response_data)
    except ValueError:
        return GoogleHealthTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Google Health token exchange returned an invalid token response.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
        )

    GoogleHealthTokenStore().save_tokens(
        token_data=token_data.to_storage_dict(),
        source="google_health_token_exchange",
    )

    return GoogleHealthTokenExchangeResult(
        attempted=True,
        request_prepared=True,
        real_exchange_enabled=True,
        saved=True,
        message="Google Health token exchange completed and token data was saved.",
        request_parts=None,
        request_preview=prepare_result.request_preview,
        error=None,
    )


def build_google_health_token_request_preview(
    request_parts: GoogleHealthTokenRequestParts,
) -> GoogleHealthTokenRequestPreview:
    """Build a non-sensitive preview from internal token request parts."""

    form_data = request_parts.form_data

    return GoogleHealthTokenRequestPreview(
        endpoint=request_parts.endpoint,
        grant_type=form_data.get("grant_type", ""),
        redirect_uri=form_data.get("redirect_uri", ""),
        has_client_id=bool(form_data.get("client_id")),
        has_client_secret=bool(form_data.get("client_secret")),
        has_code=bool(form_data.get("code")),
    )


def normalize_google_health_token_response(
    data: dict[str, Any],
) -> GoogleHealthNormalizedTokenResponse:
    """
    Normalize Google OAuth token response data before local storage.

    id_token is intentionally not stored yet. It may contain identity claims and
    is not needed for the current readiness boundary.
    """

    return GoogleHealthNormalizedTokenResponse(
        access_token=_require_string(data, "access_token"),
        token_type=_optional_string(data, "token_type") or "Bearer",
        expires_in=_optional_int(data, "expires_in"),
        refresh_token=_optional_string(data, "refresh_token"),
        scope=_optional_string(data, "scope"),
    )


def _require_string(
    data: dict[str, Any],
    key: str,
) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value:
        raise ValueError(key)

    return value


def _optional_string(
    data: dict[str, Any],
    key: str,
) -> str | None:
    value = data.get(key)

    if isinstance(value, str) and value:
        return value

    return None


def _optional_int(
    data: dict[str, Any],
    key: str,
) -> int | None:
    value = data.get(key)

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return None