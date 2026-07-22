from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import AppConfig
from app.services.google_health_credentials import GoogleHealthOAuthCredentials
from app.services.google_health_token_exchange import (
    GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
    GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
    GoogleHealthNormalizedTokenResponse,
    normalize_google_health_token_response,
)
from app.services.google_health_token_store import (
    GoogleHealthTokenStore,
    StoredGoogleHealthTokens,
)


GOOGLE_HEALTH_TOKEN_REFRESH_ERROR_NO_STORED_TOKENS = "no_stored_tokens"
GOOGLE_HEALTH_TOKEN_REFRESH_ERROR_NO_REFRESH_TOKEN = "no_refresh_token"


@dataclass(frozen=True)
class GoogleHealthRefreshRequestParts:
    """
    Internal request parts for Google OAuth token refresh.

    This may contain sensitive values such as client_secret and refresh_token.
    Do not return it directly from API responses or print it to logs.
    """

    endpoint: str
    method: str
    headers: dict[str, str]
    form_data: dict[str, str]


@dataclass(frozen=True)
class GoogleHealthRefreshRequestPreview:
    """
    Non-sensitive preview of a Google OAuth refresh request.

    This intentionally does not expose client secrets or refresh tokens.
    """

    endpoint: str
    grant_type: str
    has_client_id: bool
    has_client_secret: bool
    has_refresh_token: bool


@dataclass(frozen=True)
class GoogleHealthTokenRefreshResult:
    """
    Result of the Google OAuth token refresh boundary.

    request_parts may contain sensitive values and must stay internal.
    """

    attempted: bool
    request_prepared: bool
    real_refresh_enabled: bool
    refreshed: bool
    saved: bool
    message: str
    request_parts: GoogleHealthRefreshRequestParts | None = None
    request_preview: GoogleHealthRefreshRequestPreview | None = None
    error: str | None = None


def prepare_google_health_token_refresh_request(
    *,
    token_uri: str,
    client_id: str,
    client_secret: str,
    refresh_token: str | None,
) -> GoogleHealthTokenRefreshResult:
    """
    Prepare internal request parts for Google OAuth refresh-token exchange.

    This does not perform HTTP POST. It only builds request parts and a
    non-sensitive preview.
    """

    if not refresh_token:
        return GoogleHealthTokenRefreshResult(
            attempted=False,
            request_prepared=False,
            real_refresh_enabled=False,
            refreshed=False,
            saved=False,
            message=(
                "Google Health token refresh request could not be prepared "
                "because no refresh token is stored."
            ),
            request_parts=None,
            request_preview=None,
            error=GOOGLE_HEALTH_TOKEN_REFRESH_ERROR_NO_REFRESH_TOKEN,
        )

    request_parts = GoogleHealthRefreshRequestParts(
        endpoint=token_uri,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        form_data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    return GoogleHealthTokenRefreshResult(
        attempted=False,
        request_prepared=True,
        real_refresh_enabled=False,
        refreshed=False,
        saved=False,
        message="Google Health token refresh request was prepared.",
        request_parts=request_parts,
        request_preview=build_google_health_refresh_request_preview(
            request_parts
        ),
        error=None,
    )


def refresh_google_health_access_token_if_needed(
    *,
    config: AppConfig,
    credentials: GoogleHealthOAuthCredentials,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthTokenRefreshResult:
    """
    Refresh the stored Google OAuth access token when it is expired.

    Real HTTP POST remains disabled unless
    GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1.
    """

    store = token_store or GoogleHealthTokenStore()
    stored_tokens = store.load_tokens()

    if stored_tokens is None:
        return GoogleHealthTokenRefreshResult(
            attempted=False,
            request_prepared=False,
            real_refresh_enabled=config.google_health_enable_real_token_refresh,
            refreshed=False,
            saved=False,
            message="Google Health token refresh skipped because no tokens are stored.",
            request_parts=None,
            request_preview=None,
            error=GOOGLE_HEALTH_TOKEN_REFRESH_ERROR_NO_STORED_TOKENS,
        )

    if not stored_tokens.should_refresh_access_token():
        return GoogleHealthTokenRefreshResult(
            attempted=False,
            request_prepared=False,
            real_refresh_enabled=config.google_health_enable_real_token_refresh,
            refreshed=False,
            saved=False,
            message="Google Health access token is still valid.",
            request_parts=None,
            request_preview=None,
            error=None,
        )

    prepare_result = prepare_google_health_token_refresh_request(
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        refresh_token=stored_tokens.refresh_token,
    )

    if not prepare_result.request_prepared or prepare_result.request_parts is None:
        return prepare_result

    if not config.google_health_enable_real_token_refresh:
        return GoogleHealthTokenRefreshResult(
            attempted=False,
            request_prepared=True,
            real_refresh_enabled=False,
            refreshed=False,
            saved=False,
            message=(
                "Google Health token refresh request was prepared, but real "
                "token refresh is disabled."
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
        return GoogleHealthTokenRefreshResult(
            attempted=True,
            request_prepared=True,
            real_refresh_enabled=True,
            refreshed=False,
            saved=False,
            message="Google Health token refresh failed.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
        )

    try:
        response_data = response.json() if response.content else {}
    except ValueError:
        return GoogleHealthTokenRefreshResult(
            attempted=True,
            request_prepared=True,
            real_refresh_enabled=True,
            refreshed=False,
            saved=False,
            message="Google Health token refresh returned invalid JSON.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
        )

    if not isinstance(response_data, dict) or response.status_code >= 400:
        return GoogleHealthTokenRefreshResult(
            attempted=True,
            request_prepared=True,
            real_refresh_enabled=True,
            refreshed=False,
            saved=False,
            message="Google Health token refresh returned an error response.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_HTTP_REQUEST_FAILED,
        )

    try:
        token_data = normalize_google_health_refresh_response(
            data=response_data,
            previous_tokens=stored_tokens,
        )
    except ValueError:
        return GoogleHealthTokenRefreshResult(
            attempted=True,
            request_prepared=True,
            real_refresh_enabled=True,
            refreshed=False,
            saved=False,
            message="Google Health token refresh returned an invalid token response.",
            request_parts=None,
            request_preview=prepare_result.request_preview,
            error=GOOGLE_HEALTH_TOKEN_EXCHANGE_ERROR_INVALID_TOKEN_RESPONSE,
        )

    store.save_tokens(
        token_data=token_data.to_storage_dict(),
        source="google_health_token_refresh",
    )

    return GoogleHealthTokenRefreshResult(
        attempted=True,
        request_prepared=True,
        real_refresh_enabled=True,
        refreshed=True,
        saved=True,
        message="Google Health token refresh completed and token data was saved.",
        request_parts=None,
        request_preview=prepare_result.request_preview,
        error=None,
    )


def build_google_health_refresh_request_preview(
    request_parts: GoogleHealthRefreshRequestParts,
) -> GoogleHealthRefreshRequestPreview:
    """Build a non-sensitive preview from internal refresh request parts."""

    form_data = request_parts.form_data

    return GoogleHealthRefreshRequestPreview(
        endpoint=request_parts.endpoint,
        grant_type=form_data.get("grant_type", ""),
        has_client_id=bool(form_data.get("client_id")),
        has_client_secret=bool(form_data.get("client_secret")),
        has_refresh_token=bool(form_data.get("refresh_token")),
    )


def normalize_google_health_refresh_response(
    *,
    data: dict[str, Any],
    previous_tokens: StoredGoogleHealthTokens,
) -> GoogleHealthNormalizedTokenResponse:
    """
    Normalize a Google OAuth refresh response before local storage.

    Google token refresh responses often omit refresh_token. In that case, keep
    the previously stored refresh token so future refreshes remain possible.
    """

    refreshed = normalize_google_health_token_response(data)

    return GoogleHealthNormalizedTokenResponse(
        access_token=refreshed.access_token,
        token_type=refreshed.token_type,
        expires_in=refreshed.expires_in,
        refresh_token=refreshed.refresh_token or previous_tokens.refresh_token,
        scope=refreshed.scope or previous_tokens.scope,
    )
