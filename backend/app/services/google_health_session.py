from __future__ import annotations

from dataclasses import dataclass

from app.config import AppConfig
from app.services.google_health_api_client import (
    GoogleHealthApiClientResult,
    GoogleHealthApiRequestPreview,
    GoogleHealthProviderErrorSummary,
    build_google_health_api_endpoint,
    get_google_health_json_with_tokens_if_enabled,
)
from app.services.google_health_credentials import GoogleHealthOAuthCredentials
from app.services.google_health_token_refresh import (
    GoogleHealthTokenRefreshResult,
    refresh_google_health_access_token_if_needed,
)
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_SESSION_ERROR_NO_STORED_TOKENS = "no_stored_tokens"
GOOGLE_HEALTH_SESSION_ERROR_REFRESH_NOT_COMPLETED = "refresh_not_completed"
GOOGLE_HEALTH_SESSION_ERROR_REFRESHED_TOKENS_NOT_FOUND = (
    "refreshed_tokens_not_found"
)


@dataclass(frozen=True)
class GoogleHealthTokenRefreshSummary:
    """
    Safe summary of the token-refresh boundary.

    The source refresh result can contain internal request parts with secrets.
    This summary intentionally keeps only non-sensitive fields and preview data.
    """

    attempted: bool
    request_prepared: bool
    real_refresh_enabled: bool
    refreshed: bool
    saved: bool
    message: str
    request_preview: object | None = None
    error: str | None = None


@dataclass(frozen=True)
class GoogleHealthApiClientSummary:
    """
    Safe summary of the API-client boundary.

    Raw API response data can contain personal health data, so the coordinator
    only exposes status and request preview information by default.
    """

    attempted: bool
    request_prepared: bool
    real_api_enabled: bool
    succeeded: bool
    message: str
    request_preview: GoogleHealthApiRequestPreview | None = None
    status_code: int | None = None
    error: str | None = None
    provider_error_category: str | None = None
    provider_error_summary: GoogleHealthProviderErrorSummary | None = None


@dataclass(frozen=True)
class GoogleHealthSessionResult:
    """
    Coordinator result for refresh-before-API behavior.

    This app-facing result must not contain access tokens, refresh tokens,
    Authorization headers, client secrets, or raw personal health payloads.
    """

    token_available: bool
    refresh_checked: bool
    api_requested: bool
    succeeded: bool
    endpoint: str
    message: str
    refresh_summary: GoogleHealthTokenRefreshSummary | None = None
    api_summary: GoogleHealthApiClientSummary | None = None
    # Internal-only provider response data. Do not expose this from diagnostics
    # or app-facing API models. Sleep source normalization may read it and return
    # only the safe SleepSummary shape.
    api_response_data: dict | None = None
    error: str | None = None


class GoogleHealthSessionBoundaryError(RuntimeError):
    """Raised when the Google Health session boundary is used unsafely."""


def get_google_health_json_after_refresh_if_needed(
    *,
    config: AppConfig,
    credentials: GoogleHealthOAuthCredentials,
    api_path: str,
    query_params: dict[str, str] | None = None,
    token_store: GoogleHealthTokenStore | None = None,
    timeout_seconds: float = 10.0,
) -> GoogleHealthSessionResult:
    """
    Coordinate Google OAuth token refresh before an API request.

    Responsibilities stay intentionally separated:
    - token_store loads the current token snapshot
    - token_refresh refreshes expired tokens when explicitly enabled
    - api_client builds/performs guarded API requests

    If refresh is required but not completed, the API request is skipped.
    """

    store = token_store or GoogleHealthTokenStore()
    endpoint = build_google_health_api_endpoint(
        base_url=config.google_health_api_base_url,
        path=api_path,
    )

    stored_tokens = store.load_tokens()
    if stored_tokens is None:
        return GoogleHealthSessionResult(
            token_available=False,
            refresh_checked=False,
            api_requested=False,
            succeeded=False,
            endpoint=endpoint,
            message="Google Health session skipped because no tokens are stored.",
            refresh_summary=None,
            api_summary=None,
            api_response_data=None,
            error=GOOGLE_HEALTH_SESSION_ERROR_NO_STORED_TOKENS,
        )

    refresh_summary: GoogleHealthTokenRefreshSummary | None = None

    if stored_tokens.should_refresh_access_token():
        refresh_result = refresh_google_health_access_token_if_needed(
            config=config,
            credentials=credentials,
            token_store=store,
        )
        refresh_summary = summarize_google_health_token_refresh_result(
            refresh_result
        )

        if not refresh_result.refreshed:
            return GoogleHealthSessionResult(
                token_available=True,
                refresh_checked=True,
                api_requested=False,
                succeeded=False,
                endpoint=endpoint,
                message=(
                    "Google Health API request skipped because token refresh "
                    "was required but did not complete."
                ),
                refresh_summary=refresh_summary,
                api_summary=None,
                api_response_data=None,
                error=(
                    refresh_result.error
                    or GOOGLE_HEALTH_SESSION_ERROR_REFRESH_NOT_COMPLETED
                ),
            )

        refreshed_tokens = store.load_tokens()
        if refreshed_tokens is None:
            return GoogleHealthSessionResult(
                token_available=True,
                refresh_checked=True,
                api_requested=False,
                succeeded=False,
                endpoint=endpoint,
                message=(
                    "Google Health API request skipped because refreshed "
                    "tokens could not be loaded."
                ),
                refresh_summary=refresh_summary,
                api_summary=None,
                api_response_data=None,
                error=GOOGLE_HEALTH_SESSION_ERROR_REFRESHED_TOKENS_NOT_FOUND,
            )

        stored_tokens = refreshed_tokens

    api_result = get_google_health_json_with_tokens_if_enabled(
        config=config,
        endpoint=endpoint,
        stored_tokens=stored_tokens,
        query_params=query_params,
        timeout_seconds=timeout_seconds,
    )
    api_summary = summarize_google_health_api_client_result(api_result)

    return GoogleHealthSessionResult(
        token_available=True,
        refresh_checked=refresh_summary is not None,
        api_requested=True,
        succeeded=api_result.succeeded,
        endpoint=endpoint,
        message=api_result.message,
        refresh_summary=refresh_summary,
        api_summary=api_summary,
        api_response_data=api_result.response.data if api_result.response else None,
        error=api_result.error,
    )


def summarize_google_health_token_refresh_result(
    result: GoogleHealthTokenRefreshResult,
) -> GoogleHealthTokenRefreshSummary:
    """Build a safe summary from a token-refresh result."""

    return GoogleHealthTokenRefreshSummary(
        attempted=result.attempted,
        request_prepared=result.request_prepared,
        real_refresh_enabled=result.real_refresh_enabled,
        refreshed=result.refreshed,
        saved=result.saved,
        message=result.message,
        request_preview=result.request_preview,
        error=result.error,
    )


def summarize_google_health_api_client_result(
    result: GoogleHealthApiClientResult,
) -> GoogleHealthApiClientSummary:
    """Build a safe summary from an API-client result."""

    return GoogleHealthApiClientSummary(
        attempted=result.attempted,
        request_prepared=result.request_prepared,
        real_api_enabled=result.real_api_enabled,
        succeeded=result.succeeded,
        message=result.message,
        request_preview=result.request_preview,
        status_code=result.response.status_code if result.response else None,
        error=result.error,
        provider_error_category=result.provider_error_category,
        provider_error_summary=result.provider_error_summary,
    )
