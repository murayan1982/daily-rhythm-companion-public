from __future__ import annotations

from app.config import AppConfig
from app.models.google_health import GoogleHealthPermissionRetestReadinessResponse
from app.services.google_health_scope_check import get_google_health_scope_check
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_NEEDS_SCOPE_READY = "needs_scope_ready"
GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_NEEDS_MANUAL_CONFIRMATION = (
    "needs_manual_confirmation"
)
GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_READY = "ready_for_guarded_permission_retest"


MANUAL_CHECKS: tuple[tuple[str, str, str], ...] = (
    (
        "cloud_api_enabled_confirmed",
        "Google Health API is enabled in the same Google Cloud project as credentials.json.",
        "Set GOOGLE_HEALTH_CLOUD_API_ENABLED_CONFIRMED=1 after checking Google Cloud Console > APIs & Services.",
    ),
    (
        "oauth_consent_sleep_scope_confirmed",
        "OAuth consent screen includes the configured sleep read scope.",
        "Set GOOGLE_HEALTH_OAUTH_CONSENT_SLEEP_SCOPE_CONFIRMED=1 after confirming the OAuth consent screen scopes.",
    ),
    (
        "oauth_test_user_confirmed",
        "The signed-in Google account is an allowed test user or the app is approved for the requested scope.",
        "Set GOOGLE_HEALTH_OAUTH_TEST_USER_CONFIRMED=1 after confirming test-user/app approval access.",
    ),
    (
        "endpoint_query_confirmed",
        "Google Health sleep endpoint/path/query parameters match the current official docs.",
        "Set GOOGLE_HEALTH_ENDPOINT_QUERY_CONFIRMED=1 after confirming the dataPoints.list path and query names.",
    ),
)


def get_google_health_permission_retest_readiness(
    *,
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthPermissionRetestReadinessResponse:
    """
    Summarize local readiness for a guarded 403 permission_denied retest.

    This v0.23 helper intentionally does not call Google APIs. It combines the
    safe scope-check result with operator-confirmed local checklist flags so the
    next real request is done only after the likely non-code causes have been
    reviewed.
    """

    scope_check = get_google_health_scope_check(
        config=config,
        token_store=token_store,
    )
    scope_ready = scope_check.ready_for_permission_retest

    manual_values = {
        "cloud_api_enabled_confirmed": config.google_health_cloud_api_enabled_confirmed,
        "oauth_consent_sleep_scope_confirmed": config.google_health_oauth_consent_sleep_scope_confirmed,
        "oauth_test_user_confirmed": config.google_health_oauth_test_user_confirmed,
        "endpoint_query_confirmed": config.google_health_endpoint_query_confirmed,
    }

    confirmed_checks: list[str] = []
    unresolved_checks: list[str] = []
    for key, confirmed_text, unresolved_text in MANUAL_CHECKS:
        if manual_values[key]:
            confirmed_checks.append(confirmed_text)
        else:
            unresolved_checks.append(unresolved_text)

    if not scope_ready:
        status = GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_NEEDS_SCOPE_READY
        message = "Required Google Health sleep scope is not ready in the stored token yet."
        next_action = scope_check.next_action
        error = status
    elif unresolved_checks:
        status = GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_NEEDS_MANUAL_CONFIRMATION
        message = (
            "Required sleep scope is ready, but some manual permission-denied "
            "checks are still unconfirmed."
        )
        next_action = "Confirm the unresolved Google Cloud/OAuth/endpoint checks before another guarded real request."
        error = status
    else:
        status = GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_READY
        message = (
            "Required sleep scope and manual permission-denied checks are ready "
            "for one guarded real request retest."
        )
        next_action = (
            "Temporarily enable GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1 and "
            "GOOGLE_HEALTH_REAL_API_OPT_IN=1, restart the backend, run the real "
            "sleep smoke with --allow-real-request, then turn both flags back to 0."
        )
        error = None

    return GoogleHealthPermissionRetestReadinessResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        status=status,
        ready_for_guarded_permission_retest=(
            status == GOOGLE_HEALTH_PERMISSION_RETEST_STATUS_READY
        ),
        scope_ready=scope_ready,
        cloud_api_enabled_confirmed=config.google_health_cloud_api_enabled_confirmed,
        oauth_consent_sleep_scope_confirmed=(
            config.google_health_oauth_consent_sleep_scope_confirmed
        ),
        oauth_test_user_confirmed=config.google_health_oauth_test_user_confirmed,
        endpoint_query_confirmed=config.google_health_endpoint_query_confirmed,
        required_sleep_scope=scope_check.required_sleep_scope,
        confirmed_checks=confirmed_checks,
        unresolved_checks=unresolved_checks,
        message=message,
        next_action=next_action,
        error=error,
    )
