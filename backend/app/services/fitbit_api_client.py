from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from app.services.fitbit_http_client import FitbitHttpResponse


FITBIT_API_BASE_URL = "https://api.fitbit.com/1.2/user/-"

FITBIT_API_ERROR_REQUEST_FAILED = "fitbit_api_request_failed"
FITBIT_API_ERROR_INVALID_RESPONSE = "fitbit_api_invalid_response"
FITBIT_API_ERROR_UNAUTHORIZED = "fitbit_api_unauthorized"
FITBIT_API_ERROR_PERMISSION_DENIED = "fitbit_api_permission_denied"
FITBIT_API_ERROR_SCOPE_MISSING = "fitbit_api_scope_missing"
FITBIT_API_ERROR_RATE_LIMITED = "fitbit_api_rate_limited"
FITBIT_API_ERROR_PROVIDER_UNAVAILABLE = "fitbit_api_provider_unavailable"
FITBIT_API_ERROR_HTTP = "fitbit_api_http_error"


@dataclass(frozen=True)
class FitbitApiRequestPreview:
    """
    Non-sensitive preview of a Fitbit API request.

    This intentionally does not expose access tokens or Authorization header
    values.
    """

    endpoint: str
    method: str
    uses_bearer_auth: bool


class FitbitApiClientError(RuntimeError):
    """Raised when the Fitbit API client boundary cannot complete safely."""

    def __init__(
        self,
        code: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def build_fitbit_bearer_headers(access_token: str) -> dict[str, str]:
    """
    Build Fitbit API headers for bearer-token requests.

    The returned Authorization header contains sensitive token material and
    must not be returned from API responses or printed to logs.
    """

    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


def build_fitbit_sleep_date_endpoint(date: str) -> str:
    """
    Build the Fitbit sleep-by-date endpoint.

    Fitbit's sleep endpoint shape is:
    /1.2/user/-/sleep/date/{date}.json
    """

    return f"{FITBIT_API_BASE_URL}/sleep/date/{date}.json"


def build_fitbit_api_request_preview(
    *,
    endpoint: str,
    uses_bearer_auth: bool,
) -> FitbitApiRequestPreview:
    """Build a non-sensitive Fitbit API request preview."""

    return FitbitApiRequestPreview(
        endpoint=endpoint,
        method="GET",
        uses_bearer_auth=uses_bearer_auth,
    )


def get_fitbit_json(
    *,
    endpoint: str,
    access_token: str,
    timeout_seconds: float = 10.0,
    http_get: Callable[..., Any] | None = None,
) -> FitbitHttpResponse:
    """
    GET JSON data from a Fitbit API endpoint.

    Response data may contain personal health/sleep data. Callers must avoid
    returning raw Fitbit payloads directly from app-facing APIs. The raised
    errors expose only allow-listed codes and optional HTTP status values.
    """

    headers = build_fitbit_bearer_headers(access_token)
    request = http_get or httpx.get

    try:
        response = request(
            endpoint,
            headers=headers,
            timeout=timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise FitbitApiClientError(FITBIT_API_ERROR_REQUEST_FAILED) from exc

    status_code = int(response.status_code)

    try:
        response_data = response.json() if response.content else {}
    except ValueError as exc:
        if status_code >= 400:
            raise FitbitApiClientError(
                _classify_http_error(status_code, {}),
                status_code=status_code,
            ) from exc
        raise FitbitApiClientError(
            FITBIT_API_ERROR_INVALID_RESPONSE,
            status_code=status_code,
        ) from exc

    if not isinstance(response_data, dict):
        if status_code >= 400:
            raise FitbitApiClientError(
                _classify_http_error(status_code, {}),
                status_code=status_code,
            )
        raise FitbitApiClientError(
            FITBIT_API_ERROR_INVALID_RESPONSE,
            status_code=status_code,
        )

    if status_code >= 400:
        raise FitbitApiClientError(
            _classify_http_error(status_code, response_data),
            status_code=status_code,
        )

    return FitbitHttpResponse(
        status_code=status_code,
        data=response_data,
    )


def _classify_http_error(
    status_code: int,
    response_data: dict[str, Any],
) -> str:
    """Return an allow-listed error code without returning provider payloads."""

    if status_code == 401:
        return FITBIT_API_ERROR_UNAUTHORIZED

    if status_code == 403:
        markers = _extract_safe_error_markers(response_data)
        if any("scope" in marker for marker in markers):
            return FITBIT_API_ERROR_SCOPE_MISSING
        return FITBIT_API_ERROR_PERMISSION_DENIED

    if status_code == 429:
        return FITBIT_API_ERROR_RATE_LIMITED

    if status_code >= 500:
        return FITBIT_API_ERROR_PROVIDER_UNAVAILABLE

    return FITBIT_API_ERROR_HTTP


def _extract_safe_error_markers(
    response_data: dict[str, Any],
) -> tuple[str, ...]:
    """
    Extract only classifier markers from Fitbit's error list.

    Provider messages and the original payload are intentionally discarded.
    """

    errors = response_data.get("errors")
    if not isinstance(errors, list):
        return ()

    markers: list[str] = []
    for error in errors:
        if not isinstance(error, dict):
            continue
        for key in ("errorType", "fieldName"):
            value = error.get(key)
            if isinstance(value, str) and value:
                markers.append(value.strip().lower())

    return tuple(markers)
