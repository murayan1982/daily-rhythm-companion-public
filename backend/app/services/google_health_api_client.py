from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any
from urllib.parse import urlencode, urljoin

import httpx

from app.config import AppConfig
from app.services.google_health_runtime_guard import (
    evaluate_google_health_runtime_guard,
)
from app.services.google_health_token_store import (
    GoogleHealthTokenStore,
    StoredGoogleHealthTokens,
)


GOOGLE_HEALTH_API_CLIENT_ERROR_NO_STORED_TOKENS = "no_stored_tokens"
GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED = "api_request_disabled"
GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_REQUEST_FAILED = "http_request_failed"
GOOGLE_HEALTH_API_CLIENT_ERROR_INVALID_JSON_RESPONSE = "invalid_json_response"
GOOGLE_HEALTH_API_CLIENT_ERROR_UNEXPECTED_RESPONSE_SHAPE = (
    "unexpected_response_shape"
)
GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_ERROR = "http_error"
GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG = "unsafe_real_api_config"

GOOGLE_HEALTH_PROVIDER_ERROR_AUTH_FAILED = "auth_failed"
GOOGLE_HEALTH_PROVIDER_ERROR_PERMISSION_DENIED = "permission_denied"
GOOGLE_HEALTH_PROVIDER_ERROR_NOT_FOUND = "not_found"
GOOGLE_HEALTH_PROVIDER_ERROR_RATE_LIMITED = "rate_limited"
GOOGLE_HEALTH_PROVIDER_ERROR_SERVER_ERROR = "server_error"
GOOGLE_HEALTH_PROVIDER_ERROR_HTTP_ERROR = "http_error"
GOOGLE_HEALTH_PROVIDER_ERROR_NETWORK_ERROR = "network_error"
GOOGLE_HEALTH_PROVIDER_ERROR_INVALID_RESPONSE = "invalid_response"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GoogleHealthApiRequestParts:
    """
    Internal request parts for Google Health API calls.

    headers contains an Authorization bearer token and must not be returned from
    API responses, previews, or logs.
    """

    endpoint: str
    method: str
    headers: dict[str, str]
    query_params: dict[str, str]


@dataclass(frozen=True)
class GoogleHealthApiRequestPreview:
    """
    Non-sensitive preview of a Google Health API request.

    This intentionally does not expose access tokens or Authorization header
    values.
    """

    endpoint: str
    method: str
    has_bearer_auth: bool
    query_param_keys: tuple[str, ...]
    query_params: dict[str, str]
    preview_url: str


@dataclass(frozen=True)
class GoogleHealthApiResponse:
    """
    Internal Google Health API response wrapper.

    Response data may contain personal health data. Do not return raw payloads
    from app-facing APIs unless that is explicitly intended.
    """

    status_code: int
    data: dict[str, Any]


@dataclass(frozen=True)
class GoogleHealthProviderErrorSummary:
    """
    Safe provider-error summary for troubleshooting Google Health failures.

    The summary intentionally keeps only Google-style error metadata and short
    message hints. It must not include tokens, Authorization headers, client
    secrets, or raw health payloads.
    """

    http_status_code: int | None = None
    provider_error_code: int | None = None
    provider_error_status: str | None = None
    provider_error_message_hint: str | None = None
    provider_error_reason: str | None = None
    provider_error_domain: str | None = None
    provider_error_metadata_keys: tuple[str, ...] = ()
    www_authenticate_hint: str | None = None
    suggested_cause: str | None = None


@dataclass(frozen=True)
class GoogleHealthApiClientResult:
    """
    Result of the Google Health API client boundary.

    request_parts may contain a bearer token and must stay internal.
    """

    attempted: bool
    request_prepared: bool
    real_api_enabled: bool
    succeeded: bool
    message: str
    request_parts: GoogleHealthApiRequestParts | None = None
    request_preview: GoogleHealthApiRequestPreview | None = None
    response: GoogleHealthApiResponse | None = None
    error: str | None = None
    provider_error_category: str | None = None
    provider_error_summary: GoogleHealthProviderErrorSummary | None = None


class GoogleHealthApiClientError(RuntimeError):
    """Raised when the Google Health API boundary cannot complete safely."""


def build_google_health_bearer_headers(access_token: str) -> dict[str, str]:
    """
    Build Google Health API headers for bearer-token requests.

    The returned Authorization header contains sensitive token material and must
    not be returned from API responses or printed to logs.
    """

    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }


def build_google_health_api_endpoint(
    *,
    base_url: str,
    path: str,
) -> str:
    """
    Build a Google Health API endpoint from a base URL and path.

    Day2 intentionally keeps the concrete API path external to this helper so
    later work can switch from placeholder routes to real API-specific routes
    without changing the request boundary.
    """

    normalized_base_url = base_url.rstrip("/") + "/"
    normalized_path = path.lstrip("/")
    return urljoin(normalized_base_url, normalized_path)


def prepare_google_health_api_get_request(
    *,
    endpoint: str,
    access_token: str,
    query_params: dict[str, str] | None = None,
) -> GoogleHealthApiClientResult:
    """
    Prepare internal request parts for a Google Health API GET request.

    This does not perform HTTP GET. It only builds request parts and a
    non-sensitive preview.
    """

    request_parts = GoogleHealthApiRequestParts(
        endpoint=endpoint,
        method="GET",
        headers=build_google_health_bearer_headers(access_token),
        query_params=dict(query_params or {}),
    )

    return GoogleHealthApiClientResult(
        attempted=False,
        request_prepared=True,
        real_api_enabled=False,
        succeeded=False,
        message="Google Health API request was prepared.",
        request_parts=request_parts,
        request_preview=build_google_health_api_request_preview(request_parts),
        response=None,
        error=None,
    )


def build_google_health_api_request_preview(
    request_parts: GoogleHealthApiRequestParts,
) -> GoogleHealthApiRequestPreview:
    """Build a non-sensitive preview from internal API request parts."""

    authorization_header = request_parts.headers.get("Authorization", "")

    query_params = dict(sorted(request_parts.query_params.items()))
    query_string = urlencode(query_params)
    preview_url = (
        f"{request_parts.endpoint}?{query_string}"
        if query_string
        else request_parts.endpoint
    )

    return GoogleHealthApiRequestPreview(
        endpoint=request_parts.endpoint,
        method=request_parts.method,
        has_bearer_auth=authorization_header.startswith("Bearer "),
        query_param_keys=tuple(query_params.keys()),
        query_params=query_params,
        preview_url=preview_url,
    )


def get_google_health_json_if_enabled(
    *,
    config: AppConfig,
    endpoint: str,
    query_params: dict[str, str] | None = None,
    token_store: GoogleHealthTokenStore | None = None,
    timeout_seconds: float = 10.0,
) -> GoogleHealthApiClientResult:
    """
    GET JSON data from a Google Health API endpoint when explicitly enabled.

    Real HTTP GET remains disabled unless
    GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1.
    """

    store = token_store or GoogleHealthTokenStore()
    stored_tokens = store.load_tokens()

    if stored_tokens is None:
        return GoogleHealthApiClientResult(
            attempted=False,
            request_prepared=False,
            real_api_enabled=config.google_health_enable_real_api_requests,
            succeeded=False,
            message="Google Health API request skipped because no tokens are stored.",
            request_parts=None,
            request_preview=None,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_NO_STORED_TOKENS,
        )

    prepare_result = prepare_google_health_api_get_request(
        endpoint=endpoint,
        access_token=stored_tokens.access_token,
        query_params=query_params,
    )

    if not prepare_result.request_parts:
        return prepare_result

    guard_result = evaluate_google_health_runtime_guard(config)

    if not guard_result.real_api_requested:
        return GoogleHealthApiClientResult(
            attempted=False,
            request_prepared=True,
            real_api_enabled=False,
            succeeded=False,
            message=(
                "Google Health API request was prepared, but real API "
                "requests are disabled."
            ),
            request_parts=prepare_result.request_parts,
            request_preview=prepare_result.request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
        )

    if not guard_result.real_api_allowed:
        return GoogleHealthApiClientResult(
            attempted=False,
            request_prepared=True,
            real_api_enabled=True,
            succeeded=False,
            message=guard_result.message,
            request_parts=None,
            request_preview=prepare_result.request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG,
        )

    return _get_google_health_json(
        request_parts=prepare_result.request_parts,
        request_preview=prepare_result.request_preview,
        timeout_seconds=timeout_seconds,
    )


def get_google_health_json_with_tokens_if_enabled(
    *,
    config: AppConfig,
    endpoint: str,
    stored_tokens: StoredGoogleHealthTokens,
    query_params: dict[str, str] | None = None,
    timeout_seconds: float = 10.0,
) -> GoogleHealthApiClientResult:
    """
    GET JSON data using already-loaded Google OAuth tokens.

    This variant lets later services refresh tokens first, then pass the loaded
    token object into the API boundary without re-reading local storage.
    """

    prepare_result = prepare_google_health_api_get_request(
        endpoint=endpoint,
        access_token=stored_tokens.access_token,
        query_params=query_params,
    )

    if not prepare_result.request_parts:
        return prepare_result

    guard_result = evaluate_google_health_runtime_guard(config)

    if not guard_result.real_api_requested:
        return GoogleHealthApiClientResult(
            attempted=False,
            request_prepared=True,
            real_api_enabled=False,
            succeeded=False,
            message=(
                "Google Health API request was prepared, but real API "
                "requests are disabled."
            ),
            request_parts=prepare_result.request_parts,
            request_preview=prepare_result.request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
        )

    if not guard_result.real_api_allowed:
        return GoogleHealthApiClientResult(
            attempted=False,
            request_prepared=True,
            real_api_enabled=True,
            succeeded=False,
            message=guard_result.message,
            request_parts=None,
            request_preview=prepare_result.request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG,
        )

    return _get_google_health_json(
        request_parts=prepare_result.request_parts,
        request_preview=prepare_result.request_preview,
        timeout_seconds=timeout_seconds,
    )


def classify_google_health_provider_error(
    *,
    status_code: int | None,
    response_data: dict[str, Any] | None = None,
    client_error: str | None = None,
) -> str | None:
    """Classify provider/API failures without exposing raw response payloads."""

    if client_error == GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_REQUEST_FAILED:
        return GOOGLE_HEALTH_PROVIDER_ERROR_NETWORK_ERROR

    if client_error in {
        GOOGLE_HEALTH_API_CLIENT_ERROR_INVALID_JSON_RESPONSE,
        GOOGLE_HEALTH_API_CLIENT_ERROR_UNEXPECTED_RESPONSE_SHAPE,
    }:
        return GOOGLE_HEALTH_PROVIDER_ERROR_INVALID_RESPONSE

    if status_code is None:
        return None

    provider_status = _extract_google_health_error_status(response_data or {})
    provider_status_normalized = provider_status.upper() if provider_status else ""

    if status_code in {401, 403}:
        if status_code == 401:
            return GOOGLE_HEALTH_PROVIDER_ERROR_AUTH_FAILED
        if provider_status_normalized in {
            "PERMISSION_DENIED",
            "ACCESS_DENIED",
            "REQUEST_DENIED",
        }:
            return GOOGLE_HEALTH_PROVIDER_ERROR_PERMISSION_DENIED
        return GOOGLE_HEALTH_PROVIDER_ERROR_PERMISSION_DENIED

    if status_code == 404:
        return GOOGLE_HEALTH_PROVIDER_ERROR_NOT_FOUND

    if status_code == 429:
        return GOOGLE_HEALTH_PROVIDER_ERROR_RATE_LIMITED

    if status_code >= 500:
        return GOOGLE_HEALTH_PROVIDER_ERROR_SERVER_ERROR

    if status_code >= 400:
        return GOOGLE_HEALTH_PROVIDER_ERROR_HTTP_ERROR

    return None


def _extract_google_health_error_status(response_data: dict[str, Any]) -> str | None:
    """Extract a provider error status string from a Google-style error body."""

    error = response_data.get("error")
    if not isinstance(error, dict):
        return None

    status = error.get("status")
    return status if isinstance(status, str) and status else None


def build_google_health_provider_error_summary(
    *,
    status_code: int | None,
    response_data: dict[str, Any] | None = None,
    www_authenticate: str | None = None,
) -> GoogleHealthProviderErrorSummary | None:
    """Build a sanitized Google provider-error summary for diagnostics."""

    if status_code is None and not response_data and not www_authenticate:
        return None

    response_data = response_data or {}
    error = response_data.get("error")
    if not isinstance(error, dict):
        return GoogleHealthProviderErrorSummary(
            http_status_code=status_code,
            www_authenticate_hint=_sanitize_www_authenticate(www_authenticate),
            suggested_cause=_suggest_google_health_error_cause(
                status_code=status_code,
                provider_status=None,
                reason=None,
                provider_message=None,
                www_authenticate=www_authenticate,
            ),
        )

    details = error.get("details")
    reason: str | None = None
    domain: str | None = None
    metadata_keys: tuple[str, ...] = ()

    if isinstance(details, list):
        for detail in details:
            if not isinstance(detail, dict):
                continue

            detail_reason = detail.get("reason")
            detail_domain = detail.get("domain")
            metadata = detail.get("metadata")

            if reason is None and isinstance(detail_reason, str) and detail_reason:
                reason = detail_reason
            if domain is None and isinstance(detail_domain, str) and detail_domain:
                domain = detail_domain
            if not metadata_keys and isinstance(metadata, dict):
                metadata_keys = tuple(sorted(str(key) for key in metadata.keys()))

            if reason or domain or metadata_keys:
                break

    provider_status = _safe_str(error.get("status"))

    return GoogleHealthProviderErrorSummary(
        http_status_code=status_code,
        provider_error_code=_safe_int(error.get("code")),
        provider_error_status=provider_status,
        provider_error_message_hint=_shorten_error_message(_safe_str(error.get("message"))),
        provider_error_reason=reason,
        provider_error_domain=domain,
        provider_error_metadata_keys=metadata_keys,
        www_authenticate_hint=_sanitize_www_authenticate(www_authenticate),
        suggested_cause=_suggest_google_health_error_cause(
            status_code=status_code,
            provider_status=provider_status,
            reason=reason,
            provider_message=_safe_str(error.get("message")),
            www_authenticate=www_authenticate,
        ),
    )


def _safe_str(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _safe_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _safe_response_key_summary(response_data: dict[str, Any]) -> tuple[str, ...]:
    """Return response keys only, without logging provider payload values."""

    return tuple(sorted(str(key) for key in response_data.keys()))


def _shorten_error_message(value: str | None, *, max_length: int = 220) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized

    return normalized[: max_length - 3] + "..."


def _sanitize_www_authenticate(value: str | None, *, max_length: int = 260) -> str | None:
    if not value:
        return None

    sanitized = " ".join(value.split())
    # Defensive redaction in case an upstream proxy ever includes token-like
    # material in this header. Google auth error headers normally do not.
    sanitized = sanitized.replace("Authorization:", "Authorization:<redacted>")
    if len(sanitized) <= max_length:
        return sanitized

    return sanitized[: max_length - 3] + "..."


def _suggest_google_health_error_cause(
    *,
    status_code: int | None,
    provider_status: str | None,
    reason: str | None,
    provider_message: str | None,
    www_authenticate: str | None,
) -> str | None:
    """Return a short non-authoritative next diagnostic hint."""

    combined = " ".join(
        part.upper()
        for part in (provider_status, reason, provider_message, www_authenticate)
        if isinstance(part, str) and part
    )

    if status_code == 401:
        return "auth_token_invalid_or_expired"

    if status_code == 403:
        if "GAIAMINT" in combined and "UBERMINT" in combined:
            return "fitbit_google_account_linkage_required"
        if "INSUFFICIENT" in combined and "SCOPE" in combined:
            return "token_scope_or_reauthorization_required"
        if "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in combined:
            return "token_scope_or_reauthorization_required"
        if "API_KEY_SERVICE_BLOCKED" in combined or "SERVICE_DISABLED" in combined:
            return "cloud_api_or_project_access_not_enabled"
        if "PERMISSION_DENIED" in combined or "ACCESS_DENIED" in combined:
            return "provider_permission_or_project_access_denied"
        return "provider_permission_or_project_access_denied"

    if status_code == 404:
        return "endpoint_or_resource_not_found"

    if status_code == 429:
        return "rate_limited"

    if status_code is not None and status_code >= 500:
        return "provider_server_error"

    return None


def _get_google_health_json(
    *,
    request_parts: GoogleHealthApiRequestParts,
    request_preview: GoogleHealthApiRequestPreview | None,
    timeout_seconds: float,
) -> GoogleHealthApiClientResult:
    """Perform the guarded Google Health API GET request."""

    try:
        response = httpx.get(
            request_parts.endpoint,
            headers=request_parts.headers,
            params=request_parts.query_params,
            timeout=timeout_seconds,
        )
    except httpx.HTTPError:
        return GoogleHealthApiClientResult(
            attempted=True,
            request_prepared=True,
            real_api_enabled=True,
            succeeded=False,
            message="Google Health API request failed.",
            request_parts=None,
            request_preview=request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_REQUEST_FAILED,
            provider_error_category=classify_google_health_provider_error(
                status_code=None,
                client_error=GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_REQUEST_FAILED,
            ),
        )

    try:
        response_data = response.json() if response.content else {}
    except ValueError:
        return GoogleHealthApiClientResult(
            attempted=True,
            request_prepared=True,
            real_api_enabled=True,
            succeeded=False,
            message="Google Health API returned invalid JSON.",
            request_parts=None,
            request_preview=request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_INVALID_JSON_RESPONSE,
            provider_error_category=classify_google_health_provider_error(
                status_code=response.status_code,
                client_error=GOOGLE_HEALTH_API_CLIENT_ERROR_INVALID_JSON_RESPONSE,
            ),
        )

    if not isinstance(response_data, dict):
        return GoogleHealthApiClientResult(
            attempted=True,
            request_prepared=True,
            real_api_enabled=True,
            succeeded=False,
            message="Google Health API returned an unexpected response shape.",
            request_parts=None,
            request_preview=request_preview,
            response=None,
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_UNEXPECTED_RESPONSE_SHAPE,
            provider_error_category=classify_google_health_provider_error(
                status_code=response.status_code,
                client_error=GOOGLE_HEALTH_API_CLIENT_ERROR_UNEXPECTED_RESPONSE_SHAPE,
            ),
        )

    if response.status_code >= 400:
        provider_error_category = classify_google_health_provider_error(
            status_code=response.status_code,
            response_data=response_data,
            client_error=GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_ERROR,
        )
        logger.debug(
            "Google Health provider error response captured internally: "
            "status_code=%s category=%s response_keys=%s",
            response.status_code,
            provider_error_category,
            _safe_response_key_summary(response_data),
        )
        provider_error_summary = build_google_health_provider_error_summary(
            status_code=response.status_code,
            response_data=response_data,
            www_authenticate=response.headers.get("WWW-Authenticate"),
        )
        return GoogleHealthApiClientResult(
            attempted=True,
            request_prepared=True,
            real_api_enabled=True,
            succeeded=False,
            message="Google Health API returned an error response.",
            request_parts=None,
            request_preview=request_preview,
            response=GoogleHealthApiResponse(
                status_code=response.status_code,
                data=response_data,
            ),
            error=GOOGLE_HEALTH_API_CLIENT_ERROR_HTTP_ERROR,
            provider_error_category=provider_error_category,
            provider_error_summary=provider_error_summary,
        )

    return GoogleHealthApiClientResult(
        attempted=True,
        request_prepared=True,
        real_api_enabled=True,
        succeeded=True,
        message="Google Health API request completed.",
        request_parts=None,
        request_preview=request_preview,
        response=GoogleHealthApiResponse(
            status_code=response.status_code,
            data=response_data,
        ),
        error=None,
    )
