from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

from app.config import AppConfig
from app.services.fitbit_http_client import (
    FitbitHttpClientError,
    post_fitbit_form,
)
from app.services.fitbit_token_store import FitbitTokenStore


FITBIT_TOKEN_ENDPOINT = "https://api.fitbit.com/oauth2/token"

TOKEN_EXCHANGE_ERROR_CONFIG_INCOMPLETE = "config_incomplete"
TOKEN_EXCHANGE_ERROR_NO_REFRESH_TOKEN = "no_refresh_token"
TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED = "http_request_failed"
TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE = "invalid_token_response"


@dataclass(frozen=True)
class FitbitTokenRequestParts:
    """
    Internal request parts for the Fitbit token exchange.

    This may contain sensitive values and must not be returned directly
    from API responses or printed to logs.
    """

    endpoint: str
    method: str
    headers: dict[str, str]
    form_data: dict[str, str]


@dataclass(frozen=True)
class FitbitTokenRequestPreview:
    """
    Non-sensitive preview of the Fitbit token request.

    This intentionally does not expose client secrets, authorization codes,
    refresh tokens, or Authorization header values.
    """

    endpoint: str
    grant_type: str
    redirect_uri: str
    uses_basic_auth: bool
    has_refresh_token: bool = False


@dataclass(frozen=True)
class FitbitNormalizedTokenResponse:
    """
    Normalized Fitbit token response for local storage.

    This object contains token values. Do not expose it through API responses
    or logs.
    """

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    scope: str | None = None
    user_id: str | None = None

    def to_storage_dict(self) -> dict[str, Any]:
        """Return token data in a JSON-serializable storage shape."""

        data: dict[str, Any] = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
        }

        if self.scope:
            data["scope"] = self.scope

        if self.user_id:
            data["user_id"] = self.user_id

        return data


@dataclass(frozen=True)
class FitbitTokenExchangeResult:
    """
    Result of the Fitbit token exchange boundary.

    Real token exchange remains guarded by configuration and is not enabled by
    default. Successful real responses are intentionally not exposed directly.
    """

    attempted: bool
    request_prepared: bool
    real_exchange_enabled: bool
    saved: bool
    message: str
    request_preview: FitbitTokenRequestPreview | None = None
    error: str | None = None


def _build_basic_auth_header(
    client_id: str,
    client_secret: str,
) -> str:
    """
    Build the HTTP Basic Authorization header value.

    The returned value contains secret material and must not be exposed
    through API responses or logs.
    """

    raw_value = f"{client_id}:{client_secret}".encode("utf-8")
    encoded_value = base64.b64encode(raw_value).decode("ascii")
    return f"Basic {encoded_value}"


def _build_fitbit_token_form_data(
    config: AppConfig,
    code: str,
) -> dict[str, str]:
    """Build the form payload for the Fitbit authorization-code token request."""

    return {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.fitbit_redirect_uri or "",
    }


def _build_fitbit_refresh_token_form_data(
    refresh_token: str,
) -> dict[str, str]:
    """Build the form payload for the Fitbit refresh-token request."""

    return {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }


def build_fitbit_token_request_parts(
    config: AppConfig,
    code: str,
) -> FitbitTokenRequestParts:
    """
    Build internal request parts for the Fitbit token exchange.

    The returned object can contain secrets and authorization codes.
    """

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    if config.fitbit_client_id and config.fitbit_client_secret:
        headers["Authorization"] = _build_basic_auth_header(
            client_id=config.fitbit_client_id,
            client_secret=config.fitbit_client_secret,
        )

    return FitbitTokenRequestParts(
        endpoint=FITBIT_TOKEN_ENDPOINT,
        method="POST",
        headers=headers,
        form_data=_build_fitbit_token_form_data(
            config=config,
            code=code,
        ),
    )


def build_fitbit_refresh_token_request_parts(
    config: AppConfig,
    refresh_token: str,
) -> FitbitTokenRequestParts:
    """
    Build internal request parts for the Fitbit refresh-token exchange.

    The returned object can contain secrets and refresh tokens.
    """

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    if config.fitbit_client_id and config.fitbit_client_secret:
        headers["Authorization"] = _build_basic_auth_header(
            client_id=config.fitbit_client_id,
            client_secret=config.fitbit_client_secret,
        )

    return FitbitTokenRequestParts(
        endpoint=FITBIT_TOKEN_ENDPOINT,
        method="POST",
        headers=headers,
        form_data=_build_fitbit_refresh_token_form_data(
            refresh_token=refresh_token,
        ),
    )


def build_fitbit_token_request_preview_from_parts(
    request_parts: FitbitTokenRequestParts,
) -> FitbitTokenRequestPreview:
    """Build a non-sensitive preview from internal request parts."""

    return FitbitTokenRequestPreview(
        endpoint=request_parts.endpoint,
        grant_type=request_parts.form_data.get("grant_type", ""),
        redirect_uri=request_parts.form_data.get("redirect_uri", ""),
        uses_basic_auth="Authorization" in request_parts.headers,
        has_refresh_token=bool(request_parts.form_data.get("refresh_token")),
    )


def build_fitbit_token_request_preview(
    config: AppConfig,
    code: str,
) -> FitbitTokenRequestPreview:
    """
    Build a non-sensitive preview of the Fitbit token request.

    This intentionally does not expose client secrets, authorization codes,
    or Authorization header values.
    """

    request_parts = build_fitbit_token_request_parts(
        config=config,
        code=code,
    )

    return build_fitbit_token_request_preview_from_parts(request_parts)


def build_fitbit_refresh_token_request_preview(
    config: AppConfig,
    refresh_token: str,
) -> FitbitTokenRequestPreview:
    """
    Build a non-sensitive preview of the Fitbit refresh-token request.

    This intentionally does not expose client secrets, refresh tokens,
    or Authorization header values.
    """

    request_parts = build_fitbit_refresh_token_request_parts(
        config=config,
        refresh_token=refresh_token,
    )

    return build_fitbit_token_request_preview_from_parts(request_parts)


def _has_real_token_exchange_config(config: AppConfig) -> bool:
    """Return whether all required real token exchange settings exist."""

    return bool(
        config.fitbit_client_id
        and config.fitbit_client_secret
        and config.fitbit_redirect_uri
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

    if value is None:
        return None

    if isinstance(value, str) and value:
        return value

    return None


def _parse_expires_in(data: dict[str, Any]) -> int:
    value = data.get("expires_in")

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    raise ValueError("expires_in")


def normalize_fitbit_token_response(
    data: dict[str, Any],
) -> FitbitNormalizedTokenResponse:
    """
    Normalize a Fitbit token response before local storage.

    The returned object contains token values and must not be exposed through
    API responses or logs.
    """

    return FitbitNormalizedTokenResponse(
        access_token=_require_string(data, "access_token"),
        refresh_token=_require_string(data, "refresh_token"),
        token_type=_optional_string(data, "token_type") or "Bearer",
        expires_in=_parse_expires_in(data),
        scope=_optional_string(data, "scope"),
        user_id=_optional_string(data, "user_id"),
    )


def _exchange_fitbit_code_real(
    config: AppConfig,
    request_parts: FitbitTokenRequestParts,
) -> FitbitTokenExchangeResult:
    """
    Exchange a Fitbit authorization code through the guarded real HTTP path.

    Successful token values are normalized and saved locally, but are never
    returned in the API response.
    """

    request_preview = build_fitbit_token_request_preview_from_parts(
        request_parts
    )

    if not _has_real_token_exchange_config(config):
        return FitbitTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message=(
                "Real Fitbit token exchange was requested, but configuration "
                "is incomplete."
            ),
            request_preview=request_preview,
            error=TOKEN_EXCHANGE_ERROR_CONFIG_INCOMPLETE,
        )

    try:
        response = post_fitbit_form(
            endpoint=request_parts.endpoint,
            headers=request_parts.headers,
            form_data=request_parts.form_data,
        )
    except FitbitHttpClientError:
        return FitbitTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Real Fitbit token exchange failed.",
            request_preview=request_preview,
            error=TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
        )

    try:
        token_data = normalize_fitbit_token_response(response.data)
    except ValueError:
        return FitbitTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Real Fitbit token exchange returned an invalid token response.",
            request_preview=request_preview,
            error=TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
        )

    FitbitTokenStore().save_real_tokens(
        token_data=token_data.to_storage_dict(),
        source="fitbit_oauth_token_exchange",
    )

    return FitbitTokenExchangeResult(
        attempted=True,
        request_prepared=True,
        real_exchange_enabled=True,
        saved=True,
        message="Real Fitbit token exchange completed and token data was saved.",
        request_preview=request_preview,
        error=None,
    )


def _exchange_fitbit_refresh_token_real(
    config: AppConfig,
    request_parts: FitbitTokenRequestParts,
) -> FitbitTokenExchangeResult:
    """
    Refresh a Fitbit access token through the guarded real HTTP path.

    Successful token values are normalized and saved locally, but are never
    returned in the API response.
    """

    request_preview = build_fitbit_token_request_preview_from_parts(
        request_parts
    )

    if not _has_real_token_exchange_config(config):
        return FitbitTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message=(
                "Real Fitbit token refresh was requested, but configuration "
                "is incomplete."
            ),
            request_preview=request_preview,
            error=TOKEN_EXCHANGE_ERROR_CONFIG_INCOMPLETE,
        )

    try:
        response = post_fitbit_form(
            endpoint=request_parts.endpoint,
            headers=request_parts.headers,
            form_data=request_parts.form_data,
        )
    except FitbitHttpClientError:
        return FitbitTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Real Fitbit token refresh failed.",
            request_preview=request_preview,
            error=TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
        )

    try:
        token_data = normalize_fitbit_token_response(response.data)
    except ValueError:
        return FitbitTokenExchangeResult(
            attempted=True,
            request_prepared=True,
            real_exchange_enabled=True,
            saved=False,
            message="Real Fitbit token refresh returned an invalid token response.",
            request_preview=request_preview,
            error=TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
        )

    FitbitTokenStore().save_real_tokens(
        token_data=token_data.to_storage_dict(),
        source="fitbit_refresh_token_exchange",
    )

    return FitbitTokenExchangeResult(
        attempted=True,
        request_prepared=True,
        real_exchange_enabled=True,
        saved=True,
        message="Real Fitbit token refresh completed and token data was saved.",
        request_preview=request_preview,
        error=None,
    )


def exchange_fitbit_code_stub(
    config: AppConfig,
    code: str,
    state: str | None = None,
    save_dummy_token: bool = False,
) -> FitbitTokenExchangeResult:
    """
    Placeholder-compatible Fitbit OAuth token exchange entry point.

    This builds internal request parts and a non-sensitive preview. Real HTTP
    POST remains disabled unless explicitly enabled in configuration.
    """

    request_parts = build_fitbit_token_request_parts(
        config=config,
        code=code,
    )
    request_preview = build_fitbit_token_request_preview_from_parts(
        request_parts
    )

    if config.fitbit_enable_real_token_exchange:
        return _exchange_fitbit_code_real(
            config=config,
            request_parts=request_parts,
        )

    saved = False

    if save_dummy_token:
        FitbitTokenStore().save_dummy_tokens_for_development(
            authorization_code=code,
            state=state,
        )
        saved = True

    if saved:
        message = (
            "Fitbit token exchange stub reached. "
            "Token request was prepared and development dummy token data was saved."
        )
    else:
        message = (
            "Fitbit token exchange stub reached. "
            "Token request was prepared, but real token exchange is disabled."
        )

    return FitbitTokenExchangeResult(
        attempted=True,
        request_prepared=True,
        real_exchange_enabled=False,
        saved=saved,
        message=message,
        request_preview=request_preview,
        error=None,
    )


def refresh_fitbit_access_token(
    config: AppConfig,
    refresh_token: str | None,
) -> FitbitTokenExchangeResult:
    """
    Refresh a Fitbit access token using a locally stored refresh token.

    Real HTTP POST remains disabled unless explicitly enabled in configuration.
    Refresh token values are never exposed through the returned preview.
    """

    if not refresh_token:
        return FitbitTokenExchangeResult(
            attempted=False,
            request_prepared=False,
            real_exchange_enabled=config.fitbit_enable_real_token_exchange,
            saved=False,
            message="Fitbit token refresh could not be prepared because no refresh token exists.",
            request_preview=None,
            error=TOKEN_EXCHANGE_ERROR_NO_REFRESH_TOKEN,
        )

    request_parts = build_fitbit_refresh_token_request_parts(
        config=config,
        refresh_token=refresh_token,
    )
    request_preview = build_fitbit_token_request_preview_from_parts(
        request_parts
    )

    if config.fitbit_enable_real_token_exchange:
        return _exchange_fitbit_refresh_token_real(
            config=config,
            request_parts=request_parts,
        )

    return FitbitTokenExchangeResult(
        attempted=True,
        request_prepared=True,
        real_exchange_enabled=False,
        saved=False,
        message=(
            "Fitbit token refresh request was prepared, but real token "
            "exchange is disabled."
        ),
        request_preview=request_preview,
        error=None,
    )