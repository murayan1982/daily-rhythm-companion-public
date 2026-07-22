from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class FitbitHttpResponse:
    """
    Internal Fitbit HTTP response wrapper.

    Response data may contain sensitive token values. Do not return it directly
    from API responses or print it to logs.
    """

    status_code: int
    data: dict[str, Any]


class FitbitHttpClientError(RuntimeError):
    """Raised when the Fitbit HTTP boundary cannot complete safely."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


def post_fitbit_form(
    *,
    endpoint: str,
    headers: dict[str, str],
    form_data: dict[str, str],
    timeout_seconds: float = 10.0,
) -> FitbitHttpResponse:
    """
    POST form data to a Fitbit endpoint.

    This function is intentionally small and internal. Callers are responsible
    for building non-sensitive API responses.
    """

    try:
        response = httpx.post(
            endpoint,
            headers=headers,
            data=form_data,
            timeout=timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise FitbitHttpClientError("fitbit_http_request_failed") from exc

    try:
        response_data = response.json() if response.content else {}
    except ValueError as exc:
        raise FitbitHttpClientError(
            "fitbit_invalid_json_response",
            status_code=response.status_code,
        ) from exc

    if not isinstance(response_data, dict):
        raise FitbitHttpClientError(
            "fitbit_unexpected_response_shape",
            status_code=response.status_code,
        )

    if response.status_code >= 400:
        raise FitbitHttpClientError(
            "fitbit_http_error",
            status_code=response.status_code,
        )

    return FitbitHttpResponse(
        status_code=response.status_code,
        data=response_data,
    )