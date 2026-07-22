from __future__ import annotations

import hashlib

from app.config import AppConfig
from app.models.google_health import GoogleHealthProjectAccessReadinessResponse
from app.services.google_health_credentials import load_google_health_credentials
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME


GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_CREDENTIALS = "needs_credentials"
GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_CLIENT_CONFIRMATION = (
    "needs_client_confirmation"
)
GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_ACCESS_CONFIRMATION = (
    "needs_access_confirmation"
)
GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_READY_FOR_ACCESS_RETEST = (
    "ready_for_access_retest"
)


MANUAL_ACCESS_CHECKS: tuple[tuple[str, str, str], ...] = (
    (
        "cloud_api_enabled_confirmed",
        "Google Health API is enabled in the same Cloud project as the OAuth client.",
        "Confirm Google Cloud Console > APIs & Services > Enabled APIs for the same project as credentials.json.",
    ),
    (
        "oauth_consent_sleep_scope_confirmed",
        "OAuth consent screen includes the Google Health sleep readonly scope.",
        "Confirm Google Cloud Console > APIs & Services > OAuth consent screen scopes.",
    ),
    (
        "data_access_scope_confirmed",
        "OAuth Data Access lists the Google Health sleep readonly scope for this app.",
        "Confirm Google Cloud Console > OAuth consent screen > Data Access > Google Health API includes googlehealth.sleep.readonly and is saved.",
    ),
    (
        "oauth_publishing_status_testing_confirmed",
        "OAuth app publishing status is Testing for the current retest setup.",
        "Confirm Google Cloud Console > OAuth consent screen > Audience shows publishing status=Testing, or update this diagnostic if the app is Production.",
    ),
    (
        "oauth_user_type_external_confirmed",
        "OAuth app user type is External for the current test-user flow.",
        "Confirm Google Cloud Console > OAuth consent screen > Audience shows user type=External.",
    ),
    (
        "oauth_test_user_confirmed",
        "A test-user allowance has been confirmed for the signed-in Google account.",
        "Confirm Google Cloud Console > OAuth consent screen > Audience/Test users allows the signed-in account, or the app is published/verified for this account.",
    ),
    (
        "test_user_email_confirmed",
        "The exact Google account used for OAuth is present in the test-user list.",
        "Confirm the same Google account used to grant OAuth is listed under Test users. Re-authorize after fixing it.",
    ),
    (
        "endpoint_query_confirmed",
        "Google Health dataPoints.list endpoint and sleep filter query were checked against official docs.",
        "Confirm the current official Google Health dataPoints.list docs still match the implemented endpoint/query.",
    ),
)


def get_google_health_project_access_readiness(
    *,
    config: AppConfig,
) -> GoogleHealthProjectAccessReadinessResponse:
    """
    Summarize safe Google Cloud/OAuth project-access diagnostics.

    This endpoint intentionally performs no network calls and exposes no client
    secret, access token, refresh token, or raw provider error payload. It is a
    local consistency checklist for investigating persistent 403 responses after
    request shape and scope checks already look correct.
    """

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    credentials = credentials_result.credentials
    credentials_client_id = credentials.client_id if credentials else None
    expected_client_id = config.google_health_expected_client_id

    client_id_hash = _hash_identifier(credentials_client_id)
    client_id_suffix = _suffix_identifier(credentials_client_id)
    expected_client_id_hash = _hash_identifier(expected_client_id)
    expected_client_id_suffix = _suffix_identifier(expected_client_id)

    expected_client_id_configured = bool(expected_client_id)
    client_id_matches_expected = None
    if expected_client_id_configured and credentials_client_id:
        client_id_matches_expected = credentials_client_id == expected_client_id

    manual_values = {
        "cloud_api_enabled_confirmed": config.google_health_cloud_api_enabled_confirmed,
        "oauth_consent_sleep_scope_confirmed": config.google_health_oauth_consent_sleep_scope_confirmed,
        "oauth_test_user_confirmed": config.google_health_oauth_test_user_confirmed,
        "endpoint_query_confirmed": config.google_health_endpoint_query_confirmed,
        "data_access_scope_confirmed": config.google_health_data_access_scope_confirmed,
        "oauth_publishing_status_testing_confirmed": (
            config.google_health_oauth_publishing_status_testing_confirmed
        ),
        "oauth_user_type_external_confirmed": (
            config.google_health_oauth_user_type_external_confirmed
        ),
        "test_user_email_confirmed": config.google_health_test_user_email_confirmed,
    }

    confirmed_checks: list[str] = []
    unresolved_checks: list[str] = []
    for key, confirmed_text, unresolved_text in MANUAL_ACCESS_CHECKS:
        if manual_values[key]:
            confirmed_checks.append(confirmed_text)
        else:
            unresolved_checks.append(unresolved_text)

    if not credentials_result.loaded or not credentials_client_id:
        status = GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_CREDENTIALS
        ready = False
        message = "Google Health OAuth credentials are not loaded, so project/client access consistency cannot be checked yet."
        next_action = "Configure GOOGLE_HEALTH_CREDENTIALS_FILE with the OAuth web client credentials.json used by DRC."
        error = credentials_result.error or status
    elif expected_client_id_configured and client_id_matches_expected is False:
        status = GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_CLIENT_CONFIRMATION
        ready = False
        message = "Configured expected OAuth client ID does not match credentials.json."
        next_action = "Use the OAuth client from the same Google Cloud project where Google Health API, OAuth consent, scopes, and test users were configured."
        error = "oauth_client_mismatch"
    elif not expected_client_id_configured:
        status = GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_CLIENT_CONFIRMATION
        ready = False
        message = "credentials.json is loaded, but the Cloud Console OAuth client ID has not been manually cross-checked yet."
        next_action = "Copy the OAuth client ID from Google Cloud Console into GOOGLE_HEALTH_EXPECTED_CLIENT_ID, restart the backend, and rerun this smoke."
        error = "expected_client_id_not_configured"
    elif unresolved_checks:
        status = GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_NEEDS_ACCESS_CONFIRMATION
        ready = False
        message = "OAuth client consistency looks checkable, but some Cloud/OAuth/Data Access/Audience confirmations are still unresolved."
        next_action = "Resolve the listed Cloud project, OAuth consent, Data Access, Audience/test-user, and endpoint docs checks before another guarded real request."
        error = status
    else:
        status = GOOGLE_HEALTH_PROJECT_ACCESS_STATUS_READY_FOR_ACCESS_RETEST
        ready = True
        message = "Cloud project, OAuth client, Data Access, Audience, and endpoint checks are ready for one guarded 403 retest."
        next_action = "Run the existing guarded real sleep smoke once with real API request flags enabled, then return both real API flags to 0."
        error = None

    return GoogleHealthProjectAccessReadinessResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        status=status,
        ready_for_access_retest=ready,
        credentials_file_configured=bool(config.google_health_credentials_file),
        credentials_loaded=credentials_result.loaded,
        credentials_error=credentials_result.error,
        credentials_project_id_present=bool(credentials and credentials.project_id),
        credentials_project_id_hash=_hash_identifier(
            credentials.project_id if credentials else None
        ),
        credentials_project_id_suffix=_suffix_identifier(
            credentials.project_id if credentials else None
        ),
        credentials_client_id_present=bool(credentials_client_id),
        credentials_client_id_hash=client_id_hash,
        credentials_client_id_suffix=client_id_suffix,
        expected_client_id_configured=expected_client_id_configured,
        expected_client_id_hash=expected_client_id_hash,
        expected_client_id_suffix=expected_client_id_suffix,
        client_id_matches_expected=client_id_matches_expected,
        cloud_api_enabled_confirmed=config.google_health_cloud_api_enabled_confirmed,
        oauth_consent_sleep_scope_confirmed=(
            config.google_health_oauth_consent_sleep_scope_confirmed
        ),
        oauth_test_user_confirmed=config.google_health_oauth_test_user_confirmed,
        endpoint_query_confirmed=config.google_health_endpoint_query_confirmed,
        data_access_scope_confirmed=config.google_health_data_access_scope_confirmed,
        oauth_publishing_status_testing_confirmed=(
            config.google_health_oauth_publishing_status_testing_confirmed
        ),
        oauth_user_type_external_confirmed=(
            config.google_health_oauth_user_type_external_confirmed
        ),
        test_user_email_confirmed=config.google_health_test_user_email_confirmed,
        access_approval_confirmed=config.google_health_access_approval_confirmed,
        confirmed_checks=confirmed_checks,
        unresolved_checks=unresolved_checks,
        message=message,
        next_action=next_action,
        error=error,
    )


def _hash_identifier(value: str | None) -> str | None:
    if not value:
        return None

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _suffix_identifier(value: str | None) -> str | None:
    if not value:
        return None

    visible = 8
    if len(value) <= visible:
        return "***"

    return f"***{value[-visible:]}"
