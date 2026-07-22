from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import (  # noqa: E402
    AppConfig,
    GOOGLE_HEALTH_API_BASE_URL,
    GOOGLE_HEALTH_SLEEP_API_PATH,
)
from app.services.google_health_api_client import (  # noqa: E402
    GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
    GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG,
    build_google_health_api_endpoint,
    get_google_health_json_with_tokens_if_enabled,
)
from app.services.google_health_runtime_guard import (  # noqa: E402
    GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_ENDPOINT_NOT_VERIFIED,
    GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_INVALID_API_TIMEOUT,
    GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_PLACEHOLDER_API_BASE_URL,
    GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_REAL_API_OPT_IN_REQUIRED,
    GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_SLEEP_API_PATH_NOT_CONFIGURED,
    evaluate_google_health_runtime_guard,
)
from app.services.google_health_token_store import StoredGoogleHealthTokens  # noqa: E402


def _tokens() -> StoredGoogleHealthTokens:
    return StoredGoogleHealthTokens(
        access_token="test-access-token",
        token_type="Bearer",
        refresh_token="test-refresh-token",
    )


def _endpoint(config: AppConfig) -> str:
    return build_google_health_api_endpoint(
        base_url=config.google_health_api_base_url,
        path=config.google_health_sleep_api_path,
    )


def _assert_blocked_api_result(config: AppConfig) -> None:
    result = get_google_health_json_with_tokens_if_enabled(
        config=config,
        endpoint=_endpoint(config),
        stored_tokens=_tokens(),
        query_params={"filter": 'sleep.interval.civil_end_time >= "2026-05-04"'},
    )
    assert not result.attempted
    assert result.request_prepared
    assert result.real_api_enabled
    assert not result.succeeded
    assert result.request_parts is None
    assert result.request_preview is not None
    assert result.request_preview.has_bearer_auth
    assert result.error == GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG


def main() -> None:
    # Safe default: the official endpoint/path may be present, but no real API
    # request is allowed until all three operator gates are explicitly enabled.
    default_config = AppConfig()
    default_guard = evaluate_google_health_runtime_guard(default_config)
    assert not default_guard.real_api_requested
    assert not default_guard.real_api_allowed
    assert not default_guard.api_base_url_placeholder
    assert not default_guard.endpoint_verified
    assert not default_guard.real_api_opt_in
    assert default_guard.sleep_api_path_configured
    assert default_guard.api_timeout_valid
    assert default_guard.error is None

    disabled_result = get_google_health_json_with_tokens_if_enabled(
        config=default_config,
        endpoint=_endpoint(default_config),
        stored_tokens=_tokens(),
        query_params={"filter": 'sleep.interval.civil_end_time >= "2026-05-04"'},
    )
    assert not disabled_result.attempted
    assert disabled_result.request_prepared
    assert not disabled_result.real_api_enabled
    assert not disabled_result.succeeded
    assert disabled_result.request_parts is not None
    assert disabled_result.request_preview is not None
    assert disabled_result.request_preview.has_bearer_auth
    assert disabled_result.error == GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED

    # Gate 1: real requests enabled, but a placeholder endpoint remains blocked.
    placeholder_config = AppConfig(
        google_health_enable_real_api_requests=True,
        google_health_real_endpoint_verified=True,
        google_health_real_api_opt_in=True,
        google_health_api_base_url="https://example.invalid/google-health",
    )
    placeholder_guard = evaluate_google_health_runtime_guard(placeholder_config)
    assert placeholder_guard.real_api_requested
    assert not placeholder_guard.real_api_allowed
    assert placeholder_guard.api_base_url_placeholder
    assert placeholder_guard.endpoint_verified
    assert placeholder_guard.real_api_opt_in
    assert placeholder_guard.error == GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_PLACEHOLDER_API_BASE_URL
    _assert_blocked_api_result(placeholder_config)

    # Gate 2: the official endpoint must be operator-verified separately.
    unverified_config = AppConfig(
        google_health_enable_real_api_requests=True,
        google_health_real_endpoint_verified=False,
        google_health_real_api_opt_in=True,
        google_health_api_base_url=GOOGLE_HEALTH_API_BASE_URL,
    )
    unverified_guard = evaluate_google_health_runtime_guard(unverified_config)
    assert unverified_guard.real_api_requested
    assert not unverified_guard.real_api_allowed
    assert not unverified_guard.api_base_url_placeholder
    assert not unverified_guard.endpoint_verified
    assert unverified_guard.real_api_opt_in
    assert unverified_guard.error == GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_ENDPOINT_NOT_VERIFIED
    _assert_blocked_api_result(unverified_config)

    # Gate 3: endpoint verification alone is insufficient without the narrow
    # final operator opt-in.
    no_opt_in_config = AppConfig(
        google_health_enable_real_api_requests=True,
        google_health_real_endpoint_verified=True,
        google_health_real_api_opt_in=False,
        google_health_api_base_url=GOOGLE_HEALTH_API_BASE_URL,
    )
    no_opt_in_guard = evaluate_google_health_runtime_guard(no_opt_in_config)
    assert no_opt_in_guard.real_api_requested
    assert not no_opt_in_guard.real_api_allowed
    assert not no_opt_in_guard.api_base_url_placeholder
    assert no_opt_in_guard.endpoint_verified
    assert not no_opt_in_guard.real_api_opt_in
    assert no_opt_in_guard.error == GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_REAL_API_OPT_IN_REQUIRED
    _assert_blocked_api_result(no_opt_in_config)

    missing_path_config = AppConfig(
        google_health_enable_real_api_requests=True,
        google_health_real_endpoint_verified=True,
        google_health_real_api_opt_in=True,
        google_health_api_base_url=GOOGLE_HEALTH_API_BASE_URL,
        google_health_sleep_api_path="",
    )
    missing_path_guard = evaluate_google_health_runtime_guard(missing_path_config)
    assert not missing_path_guard.real_api_allowed
    assert not missing_path_guard.sleep_api_path_configured
    assert missing_path_guard.error == GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_SLEEP_API_PATH_NOT_CONFIGURED

    invalid_timeout_config = AppConfig(
        google_health_enable_real_api_requests=True,
        google_health_real_endpoint_verified=True,
        google_health_real_api_opt_in=True,
        google_health_api_base_url=GOOGLE_HEALTH_API_BASE_URL,
        google_health_sleep_api_path=GOOGLE_HEALTH_SLEEP_API_PATH,
        google_health_api_timeout_seconds=0,
    )
    invalid_timeout_guard = evaluate_google_health_runtime_guard(invalid_timeout_config)
    assert not invalid_timeout_guard.real_api_allowed
    assert not invalid_timeout_guard.api_timeout_valid
    assert invalid_timeout_guard.error == GOOGLE_HEALTH_RUNTIME_GUARD_ERROR_INVALID_API_TIMEOUT

    # The guard may report allowed only when all operator gates and safe request
    # settings are present. This check deliberately does not call the API in the
    # allowed state.
    allowed_config = AppConfig(
        google_health_enable_real_api_requests=True,
        google_health_real_endpoint_verified=True,
        google_health_real_api_opt_in=True,
        google_health_api_base_url=GOOGLE_HEALTH_API_BASE_URL,
        google_health_sleep_api_path=GOOGLE_HEALTH_SLEEP_API_PATH,
        google_health_api_timeout_seconds=5,
    )
    allowed_guard = evaluate_google_health_runtime_guard(allowed_config)
    assert allowed_guard.real_api_requested
    assert allowed_guard.real_api_allowed
    assert not allowed_guard.api_base_url_placeholder
    assert allowed_guard.endpoint_verified
    assert allowed_guard.real_api_opt_in
    assert allowed_guard.sleep_api_path_configured
    assert allowed_guard.api_timeout_valid
    assert allowed_guard.error is None

    print("[google-health-runtime-guard-check] OK")


if __name__ == "__main__":
    main()
