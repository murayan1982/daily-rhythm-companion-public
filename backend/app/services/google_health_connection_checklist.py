from __future__ import annotations

from app.config import AppConfig, GOOGLE_HEALTH_SLEEP_READONLY_SCOPE
from app.models.google_health import (
    GoogleHealthConnectionChecklistCommandModel,
    GoogleHealthConnectionChecklistItemModel,
    GoogleHealthConnectionChecklistResponse,
)
from app.services.google_health_credentials import load_google_health_credentials
from app.services.google_health_runtime_guard import evaluate_google_health_runtime_guard
from app.services.google_health_scope_check import get_google_health_scope_check
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_CONNECTION_CHECKLIST_STATUS_READY = "ready"
GOOGLE_HEALTH_CONNECTION_CHECKLIST_STATUS_NEEDS_REVIEW = "needs_review"
GOOGLE_HEALTH_CONNECTION_CHECKLIST_STATUS_WARN = "warn"

_UNNECESSARY_DEFAULT_SCOPES = {
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
}


def get_google_health_connection_checklist(
    *,
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthConnectionChecklistResponse:
    """
    Build a developer-facing Google Health connection checklist.

    This combines the setup checks that v0.25.0 needs most often: credentials,
    redirect URI, minimal scope, stored token scope, reconnect guidance, and
    real API safety flags. The response intentionally avoids token values,
    client secrets, authorization codes, Authorization headers, and raw health
    payloads.
    """

    store = token_store or GoogleHealthTokenStore()
    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    scope_check = get_google_health_scope_check(config=config, token_store=store)
    guard = evaluate_google_health_runtime_guard(config)

    configured_scopes = sorted(set(config.google_health_oauth_scopes))
    mixed_scope_warnings = sorted(set(configured_scopes) & _UNNECESSARY_DEFAULT_SCOPES)
    credentials_loaded = credentials_result.loaded
    redirect_uri_configured = bool(config.google_health_redirect_uri)
    required_scope_in_config = scope_check.required_sleep_scope_in_config is True
    required_scope_in_token = scope_check.required_sleep_scope_in_token is True
    token_stored = scope_check.token_stored
    reconnect_recommended = scope_check.reconnect_recommended
    safe_preview_ready = bool(required_scope_in_config and not guard.real_api_requested)
    guarded_real_request_ready = bool(
        credentials_loaded
        and token_stored
        and required_scope_in_config
        and required_scope_in_token
        and not reconnect_recommended
        and guard.real_api_allowed
    )

    checks = [
        _item(
            key="credentials_file",
            label="OAuth credentials file",
            ok=credentials_loaded,
            message=(
                "Google Health OAuth credentials are loaded."
                if credentials_loaded
                else "Google Health OAuth credentials are not loaded."
            ),
            next_action=(
                "No action needed."
                if credentials_loaded
                else "Place credentials.json under backend/ or set GOOGLE_HEALTH_CREDENTIALS_FILE."
            ),
        ),
        _item(
            key="redirect_uri",
            label="OAuth redirect URI",
            ok=redirect_uri_configured,
            message=(
                "GOOGLE_HEALTH_REDIRECT_URI is configured."
                if redirect_uri_configured
                else "GOOGLE_HEALTH_REDIRECT_URI is not configured."
            ),
            next_action=(
                "No action needed."
                if redirect_uri_configured
                else "Set GOOGLE_HEALTH_REDIRECT_URI to the local callback URL registered in Google Cloud."
            ),
        ),
        _item(
            key="minimal_sleep_scope_config",
            label="Minimal sleep scope in config",
            ok=required_scope_in_config,
            message=(
                "Configured OAuth scopes include the required Google Health sleep scope."
                if required_scope_in_config
                else "Configured OAuth scopes do not include the required Google Health sleep scope."
            ),
            next_action=(
                "No action needed."
                if required_scope_in_config
                else "Set GOOGLE_HEALTH_OAUTH_SCOPES to the recommended sleep-read scope."
            ),
        ),
        _item(
            key="mixed_scopes",
            label="Mixed/unnecessary OAuth scopes",
            ok=not mixed_scope_warnings,
            message=(
                "No mixed or unnecessary scopes are configured."
                if not mixed_scope_warnings
                else "Mixed or unnecessary scopes are configured."
            ),
            next_action=(
                "Keep the minimal sleep scope as the default path."
                if not mixed_scope_warnings
                else "Remove unrelated identity/Fitbit/activity scopes unless a specific test plan needs them."
            ),
            status="warn" if mixed_scope_warnings else "ok",
        ),
        _item(
            key="stored_token",
            label="Local OAuth token snapshot",
            ok=token_stored,
            message=(
                "A local Google Health token snapshot exists."
                if token_stored
                else "No local Google Health token snapshot exists."
            ),
            next_action=(
                "No action needed."
                if token_stored
                else "Run the OAuth helper and complete the local callback flow."
            ),
        ),
        _item(
            key="token_sleep_scope",
            label="Minimal sleep scope in token",
            ok=required_scope_in_token,
            message=(
                "Stored token metadata includes the required sleep scope."
                if required_scope_in_token
                else "Stored token metadata does not confirm the required sleep scope."
            ),
            next_action=(
                "No action needed."
                if required_scope_in_token
                else "Reset local OAuth token/state files and reauthorize with the minimal sleep scope."
            ),
        ),
        _item(
            key="real_api_safety_flags",
            label="Real API request safety flags",
            ok=not guard.real_api_requested,
            message=(
                "Real Google Health API requests are disabled. This is the safe default."
                if not guard.real_api_requested
                else "Real Google Health API requests are currently requested."
            ),
            next_action=(
                "Use the preview smoke for normal development."
                if not guard.real_api_requested
                else "Return GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS and GOOGLE_HEALTH_REAL_API_OPT_IN to 0 after guarded testing."
            ),
            status="warn" if guard.real_api_requested else "ok",
        ),
    ]

    blocking_checks = [check for check in checks if not check.ok and check.status == "blocked"]
    warning_checks = [check for check in checks if not check.ok and check.status == "warn"]

    if blocking_checks:
        status = GOOGLE_HEALTH_CONNECTION_CHECKLIST_STATUS_NEEDS_REVIEW
        message = "Google Health connection setup needs review before reauthorization or real API testing."
        next_action = blocking_checks[0].next_action
        error = blocking_checks[0].key
    elif warning_checks:
        status = GOOGLE_HEALTH_CONNECTION_CHECKLIST_STATUS_WARN
        message = "Google Health connection setup is usable, but warnings should be reviewed."
        next_action = warning_checks[0].next_action
        error = warning_checks[0].key
    else:
        status = GOOGLE_HEALTH_CONNECTION_CHECKLIST_STATUS_READY
        message = "Google Health connection setup matches the v0.25.0 minimal sleep-scope workflow."
        next_action = "Use safe preview checks by default; guarded real requests only when explicitly testing."
        error = None

    return GoogleHealthConnectionChecklistResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        status=status,
        ready_for_local_oauth=bool(
            credentials_loaded and redirect_uri_configured and required_scope_in_config
        ),
        ready_for_reauthorization=bool(
            credentials_loaded and redirect_uri_configured and required_scope_in_config
        ),
        ready_for_safe_preview=safe_preview_ready,
        ready_for_guarded_real_request=guarded_real_request_ready,
        reconnect_recommended=reconnect_recommended,
        recommended_sleep_scope=GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,
        configured_scopes=configured_scopes,
        mixed_scope_warnings=mixed_scope_warnings,
        token_store_configured=bool(store.token_file),
        token_stored=token_stored,
        required_sleep_scope_in_config=scope_check.required_sleep_scope_in_config,
        required_sleep_scope_in_token=scope_check.required_sleep_scope_in_token,
        real_api_requested=guard.real_api_requested,
        real_api_allowed=guard.real_api_allowed,
        runtime_guard_error=guard.error,
        checks=checks,
        commands=GoogleHealthConnectionChecklistCommandModel(
            oauth_helper="python scripts\\authorize_google_health_oauth.py",
            reset_dry_run="python scripts\\reset_google_health_local_oauth.py",
            reset_apply="python scripts\\reset_google_health_local_oauth.py --apply",
            config_check="python scripts\\check_google_health_connection_config.py",
            connection_checklist="python scripts\\check_google_health_connection_checklist.py",
            safe_preview="python scripts\\smoke_google_health_sleep_request_preview.py --base-url http://127.0.0.1:8000",
        ),
        message=message,
        next_action=next_action,
        error=error,
    )


def _item(
    *,
    key: str,
    label: str,
    ok: bool,
    message: str,
    next_action: str,
    status: str | None = None,
) -> GoogleHealthConnectionChecklistItemModel:
    return GoogleHealthConnectionChecklistItemModel(
        key=key,
        label=label,
        ok=ok,
        status=status or ("ok" if ok else "blocked"),
        message=message,
        next_action=next_action,
    )
