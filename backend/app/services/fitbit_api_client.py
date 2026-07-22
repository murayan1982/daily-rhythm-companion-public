from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.fitbit_http_client import (
    FitbitHttpClientError,
    FitbitHttpResponse,
)

import httpx


FITBIT_API_BASE_URL = "https://api.fitbit.com/1.2/user/-"


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
) -> FitbitHttpResponse:
    """
    GET JSON data from a Fitbit API endpoint.

    Response data may contain personal health/sleep data. Callers must avoid
    returning raw Fitbit payloads directly from app-facing APIs unless that is
    explicitly intended.
    """

    headers = build_fitbit_bearer_headers(access_token)

    try:
        response = httpx.get(
            endpoint,
            headers=headers,
            timeout=timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise FitbitApiClientError("fitbit_api_request_failed") from exc

    try:
        response_data = response.json() if response.content else {}
    except ValueError as exc:
        raise FitbitApiClientError("fitbit_api_invalid_json_response") from exc

    if not isinstance(response_data, dict):
        raise FitbitApiClientError("fitbit_api_unexpected_response_shape")

    if response.status_code >= 400:
        raise FitbitApiClientError("fitbit_api_http_error")

    return FitbitHttpResponse(
        status_code=response.status_code,
        data=response_data,
    )