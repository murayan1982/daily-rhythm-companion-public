from __future__ import annotations

from dataclasses import dataclass

from app.config import AppConfig


GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_PLACEHOLDER_API_BASE_URL = (
    "placeholder_api_base_url"
)
GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_SLEEP_API_PATH_NOT_CONFIGURED = (
    "sleep_api_path_not_configured"
)
GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_INVALID_API_TIMEOUT = "invalid_api_timeout"
GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_ENDPOINT_NOT_VERIFIED = "endpoint_not_verified"
GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_REAL_API_OPT_IN_REQUIRED = (
    "real_api_opt_in_required"
)

_PLACEHOLDER_API_BASE_URLS = {
    "https://example.invalid/google-health",
    "http://example.invalid/google-health",
    "https://example.com/google-health",
    "http://example.com/google-health",
    "placeholder",
    "replace-me",
}
_PLACEHOLDER_API_BASE_URL_MARKERS = (
    "example.invalid",
    "example.com",
    "placeholder",
    "replace-me",
)


@dataclass(frozen=True)
class GoogleHealthRuntimeGuardResult:
    """
    Safe runtime evaluation for Google Health real API settings.

    This object intentionally contains only configuration readiness metadata.
    It must never include credentials, tokens, authorization codes, or raw
    health payloads.
    """

    real_api_requested: bool
    real_api_allowed: bool
    api_base_url_placeholder: bool
    endpoint_verified: bool
    real_api_opt_in: bool
    sleep_api_path_configured: bool
    api_timeout_valid: bool
    message: str
    next_action: str
    error: str | None = None


def is_google_health_placeholder_api_base_url(base_url: str | None) -> bool:
    """Return True when the API base URL is still the safe placeholder."""

    normalized = (base_url or "").strip().rstrip("/").lower()
    return (
        not normalized
        or normalized in _PLACEHOLDER_API_BASE_URLS
        or any(marker in normalized for marker in _PLACEHOLDER_API_BASE_URL_MARKERS)
    )


def evaluate_google_health_runtime_guard(
    config: AppConfig,
) -> GoogleHealthRuntimeGuardResult:
    """
    Evaluate whether Google Health real API requests may run safely.

    Disabled real API requests are always safe. When real API requests are
    explicitly enabled, placeholder endpoint settings and invalid request
    settings block the HTTP call before any outbound request is attempted.
    """

    api_base_url_placeholder = is_google_health_placeholder_api_base_url(
        config.google_health_api_base_url
    )
    endpoint_verified = config.google_health_real_endpoint_verified
    real_api_opt_in = config.google_health_real_api_opt_in
    sleep_api_path_configured = bool(config.google_health_sleep_api_path.strip())
    api_timeout_valid = config.google_health_api_timeout_seconds > 0

    if not config.google_health_enable_real_api_requests:
        return GoogleHealthRuntimeGuardResult(
            real_api_requested=False,
            real_api_allowed=False,
            api_base_url_placeholder=api_base_url_placeholder,
            endpoint_verified=endpoint_verified,
            real_api_opt_in=real_api_opt_in,
            sleep_api_path_configured=sleep_api_path_configured,
            api_timeout_valid=api_timeout_valid,
            message="Google Health real API requests are disabled.",
            next_action=(
                "Keep real requests disabled during normal development. For a "
                "guarded local real request, confirm the minimal sleep scope, set "
                "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1, then temporarily enable "
                "both GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1 and "
                "GOOGLE_HEALTH_REAL_API_OPT_IN=1. Return both flags to 0 after testing."
            ),
            error=None,
        )

    if api_base_url_placeholder:
        return GoogleHealthRuntimeGuardResult(
            real_api_requested=True,
            real_api_allowed=False,
            api_base_url_placeholder=True,
            endpoint_verified=endpoint_verified,
            real_api_opt_in=real_api_opt_in,
            sleep_api_path_configured=sleep_api_path_configured,
            api_timeout_valid=api_timeout_valid,
            message=(
                "Google Health real API requests are enabled, but the API "
                "base URL is still the placeholder. Set "
                "GOOGLE_HEALTH_API_BASE_URL to a verified endpoint before "
                "enabling real requests."
            ),
            next_action=(
                "Replace GOOGLE_HEALTH_API_BASE_URL with the official endpoint, "
                "confirm the matching OAuth scope, keep "
                "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0 until that check is done, "
                "and rerun the endpoint gate."
            ),
            error=GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_PLACEHOLDER_API_BASE_URL,
        )

    if not endpoint_verified:
        return GoogleHealthRuntimeGuardResult(
            real_api_requested=True,
            real_api_allowed=False,
            api_base_url_placeholder=False,
            endpoint_verified=False,
            real_api_opt_in=real_api_opt_in,
            sleep_api_path_configured=sleep_api_path_configured,
            api_timeout_valid=api_timeout_valid,
            message=(
                "Google Health real API requests are enabled, but the real "
                "endpoint/scope has not been operator-verified. Set "
                "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1 only after checking "
                "the official endpoint and OAuth scope."
            ),
            next_action=(
                "Verify the configured endpoint and OAuth scope against the "
                "official provider documentation, then set "
                "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1 and rerun the endpoint gate."
            ),
            error=GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_ENDPOINT_NOT_VERIFIED,
        )

    if not real_api_opt_in:
        return GoogleHealthRuntimeGuardResult(
            real_api_requested=True,
            real_api_allowed=False,
            api_base_url_placeholder=False,
            endpoint_verified=True,
            real_api_opt_in=False,
            sleep_api_path_configured=sleep_api_path_configured,
            api_timeout_valid=api_timeout_valid,
            message=(
                "Google Health real API requests are enabled and the endpoint "
                "is marked verified, but the final real API opt-in flag is "
                "still disabled."
            ),
            next_action=(
                "After confirming the endpoint, OAuth scope, and token refresh "
                "check, set GOOGLE_HEALTH_REAL_API_OPT_IN=1 for the narrow "
                "local smoke that is allowed to make the first real request."
            ),
            error=GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_REAL_API_OPT_IN_REQUIRED,
        )

    if not sleep_api_path_configured:
        return GoogleHealthRuntimeGuardResult(
            real_api_requested=True,
            real_api_allowed=False,
            api_base_url_placeholder=False,
            endpoint_verified=endpoint_verified,
            real_api_opt_in=real_api_opt_in,
            sleep_api_path_configured=False,
            api_timeout_valid=api_timeout_valid,
            message="Google Health sleep API path is not configured.",
            next_action=(
                "Set GOOGLE_HEALTH_SLEEP_API_PATH to the verified sleep endpoint "
                "path before attempting a real request."
            ),
            error=GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_SLEEP_API_PATH_NOT_CONFIGURED,
        )

    if not api_timeout_valid:
        return GoogleHealthRuntimeGuardResult(
            real_api_requested=True,
            real_api_allowed=False,
            api_base_url_placeholder=False,
            endpoint_verified=endpoint_verified,
            real_api_opt_in=real_api_opt_in,
            sleep_api_path_configured=True,
            api_timeout_valid=False,
            message="Google Health API timeout must be greater than zero.",
            next_action="Set GOOGLE_HEALTH_API_TIMEOUT_SECONDS to a positive number.",
            error=GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_INVALID_API_TIMEOUT,
        )

    return GoogleHealthRuntimeGuardResult(
        real_api_requested=True,
        real_api_allowed=True,
        api_base_url_placeholder=False,
        endpoint_verified=True,
        real_api_opt_in=True,
        sleep_api_path_configured=True,
        api_timeout_valid=True,
        message="Google Health real API request settings passed the runtime guard.",
        next_action=(
            "Run the guarded local self-check and confirm real_http_attempted is "
            "true only when real API requests were intentionally enabled."
        ),
        error=None,
    )
