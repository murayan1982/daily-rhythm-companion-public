from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.config import load_config
from app.services.fitbit_api_client import (
    FITBIT_API_ERROR_HTTP,
    FITBIT_API_ERROR_INVALID_RESPONSE,
    FITBIT_API_ERROR_PERMISSION_DENIED,
    FITBIT_API_ERROR_PROVIDER_UNAVAILABLE,
    FITBIT_API_ERROR_RATE_LIMITED,
    FITBIT_API_ERROR_REQUEST_FAILED,
    FITBIT_API_ERROR_SCOPE_MISSING,
    FITBIT_API_ERROR_UNAUTHORIZED,
    FitbitApiClientError,
    FitbitApiRequestPreview,
    build_fitbit_api_request_preview,
    build_fitbit_sleep_date_endpoint,
    get_fitbit_json,
)
from app.services.fitbit_http_client import FitbitHttpResponse
from app.services.fitbit_token_exchange import refresh_fitbit_access_token
from app.services.fitbit_token_store import FitbitTokenStore


FITBIT_SLEEP_ERROR_NO_TOKEN = "no_fitbit_token"
FITBIT_SLEEP_ERROR_NO_ACCESS_TOKEN_AFTER_REFRESH = "no_access_token_after_refresh"
FITBIT_SLEEP_ERROR_REFRESH_FAILED = "fitbit_token_refresh_failed"
FITBIT_SLEEP_ERROR_API_REQUEST_FAILED = "fitbit_sleep_api_request_failed"
FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED = "reconnect_required"
FITBIT_SLEEP_ERROR_PERMISSION_DENIED = "permission_denied"
FITBIT_SLEEP_ERROR_SCOPE_MISSING = "scope_missing"
FITBIT_SLEEP_ERROR_RATE_LIMITED = "rate_limited"
FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE = "provider_unavailable"
FITBIT_SLEEP_ERROR_INVALID_RESPONSE = "invalid_response"


@dataclass(frozen=True)
class FitbitSleepApiResult:
    """
    Internal result for Fitbit sleep API reads.

    raw_data may contain personal health/sleep data. Do not expose it directly
    from app-facing API responses unless that is explicitly intended.
    """

    attempted: bool
    success: bool
    date: str
    request_preview: FitbitApiRequestPreview | None = None
    raw_data: dict[str, Any] | None = None
    error: str | None = None
    message: str | None = None
    refresh_attempted: bool = False
    refresh_succeeded: bool = False
    refresh_error: str | None = None


def fetch_fitbit_sleep_for_date(
    target_date: date,
    token_store: FitbitTokenStore | None = None,
    api_get: Callable[..., FitbitHttpResponse] | None = None,
) -> FitbitSleepApiResult:
    """
    Fetch raw Fitbit sleep data for a single date.

    This is an internal service boundary used by the Fitbit sleep provider.
    `api_get` exists for deterministic mock-safe regression tests; normal
    runtime uses the guarded Fitbit API client.
    """

    store = token_store or FitbitTokenStore()
    tokens = store.load_tokens()
    date_text = target_date.isoformat()
    endpoint = build_fitbit_sleep_date_endpoint(date_text)

    request_preview = build_fitbit_api_request_preview(
        endpoint=endpoint,
        uses_bearer_auth=bool(tokens and tokens.access_token),
    )

    if tokens is None:
        return FitbitSleepApiResult(
            attempted=False,
            success=False,
            date=date_text,
            request_preview=request_preview,
            raw_data=None,
            error=FITBIT_SLEEP_ERROR_NO_TOKEN,
            message="Fitbit sleep data could not be fetched because no local token exists.",
        )

    refresh_attempted = False
    refresh_succeeded = False
    refresh_error: str | None = None

    if tokens.should_refresh_access_token():
        refresh_attempted = True
        refresh_result = refresh_fitbit_access_token(
            config=load_config(),
            refresh_token=tokens.refresh_token,
        )

        if not refresh_result.saved:
            return FitbitSleepApiResult(
                attempted=False,
                success=False,
                date=date_text,
                request_preview=request_preview,
                raw_data=None,
                error=FITBIT_SLEEP_ERROR_REFRESH_FAILED,
                message="Fitbit sleep data could not be fetched because token refresh failed.",
                refresh_attempted=True,
                refresh_succeeded=False,
                refresh_error=refresh_result.error,
            )

        refresh_succeeded = True
        tokens = store.load_tokens()

        if tokens is None:
            return FitbitSleepApiResult(
                attempted=False,
                success=False,
                date=date_text,
                request_preview=request_preview,
                raw_data=None,
                error=FITBIT_SLEEP_ERROR_NO_ACCESS_TOKEN_AFTER_REFRESH,
                message="Fitbit sleep data could not be fetched because refreshed token data was unavailable.",
                refresh_attempted=True,
                refresh_succeeded=True,
                refresh_error=None,
            )

        request_preview = build_fitbit_api_request_preview(
            endpoint=endpoint,
            uses_bearer_auth=bool(tokens.access_token),
        )

    request = api_get or get_fitbit_json

    try:
        response = request(
            endpoint=endpoint,
            access_token=tokens.access_token,
        )
    except FitbitApiClientError as exc:
        safe_error = _map_api_error(exc.code)
        return FitbitSleepApiResult(
            attempted=True,
            success=False,
            date=date_text,
            request_preview=request_preview,
            raw_data=None,
            error=safe_error,
            message=_safe_api_error_message(safe_error),
            refresh_attempted=refresh_attempted,
            refresh_succeeded=refresh_succeeded,
            refresh_error=refresh_error,
        )

    return FitbitSleepApiResult(
        attempted=True,
        success=True,
        date=date_text,
        request_preview=request_preview,
        raw_data=response.data,
        error=None,
        message="Fitbit sleep API request completed.",
        refresh_attempted=refresh_attempted,
        refresh_succeeded=refresh_succeeded,
        refresh_error=refresh_error,
    )


def _map_api_error(api_error: str) -> str:
    mapping = {
        FITBIT_API_ERROR_UNAUTHORIZED: FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED,
        FITBIT_API_ERROR_PERMISSION_DENIED: FITBIT_SLEEP_ERROR_PERMISSION_DENIED,
        FITBIT_API_ERROR_SCOPE_MISSING: FITBIT_SLEEP_ERROR_SCOPE_MISSING,
        FITBIT_API_ERROR_RATE_LIMITED: FITBIT_SLEEP_ERROR_RATE_LIMITED,
        FITBIT_API_ERROR_PROVIDER_UNAVAILABLE: FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE,
        FITBIT_API_ERROR_REQUEST_FAILED: FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE,
        FITBIT_API_ERROR_INVALID_RESPONSE: FITBIT_SLEEP_ERROR_INVALID_RESPONSE,
        FITBIT_API_ERROR_HTTP: FITBIT_SLEEP_ERROR_API_REQUEST_FAILED,
    }
    return mapping.get(api_error, FITBIT_SLEEP_ERROR_API_REQUEST_FAILED)


def _safe_api_error_message(error: str) -> str:
    messages = {
        FITBIT_SLEEP_ERROR_RECONNECT_REQUIRED: (
            "Fitbit sleep access requires reconnection."
        ),
        FITBIT_SLEEP_ERROR_PERMISSION_DENIED: (
            "Fitbit sleep access was denied by the provider."
        ),
        FITBIT_SLEEP_ERROR_SCOPE_MISSING: (
            "Fitbit sleep access is missing the required scope."
        ),
        FITBIT_SLEEP_ERROR_RATE_LIMITED: (
            "Fitbit sleep access is temporarily rate limited."
        ),
        FITBIT_SLEEP_ERROR_PROVIDER_UNAVAILABLE: (
            "Fitbit sleep service is temporarily unavailable."
        ),
        FITBIT_SLEEP_ERROR_INVALID_RESPONSE: (
            "Fitbit sleep service returned an invalid response."
        ),
    }
    return messages.get(error, "Fitbit sleep API request failed.")
