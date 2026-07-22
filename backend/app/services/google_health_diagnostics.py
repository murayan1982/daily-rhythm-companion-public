from __future__ import annotations

from datetime import datetime, timezone

from app.config import AppConfig
from app.models.google_health import (
    GoogleHealthDiagnosticConfigModel,
    GoogleHealthDiagnosticRuntimeGuardModel,
    GoogleHealthDiagnosticsResponse,
    GoogleHealthDiagnosticTokenModel,
)
from app.services.google_health_credentials import load_google_health_credentials
from app.services.google_health_runtime_guard import (
    GoogleHealthRuntimeGuardResult,
    evaluate_google_health_runtime_guard,
)
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_store import (
    GoogleHealthTokenStore,
    StoredGoogleHealthTokens,
)


GOOGLE_HEALTH_DIAGNOSTICS_STATUS_MOCK_MODE = "mock_mode"
GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_CREDENTIALS = "needs_credentials"
GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_AUTH = "needs_auth"
GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_DISABLED = "api_disabled"
GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_BLOCKED = "api_blocked"
GOOGLE_HEALTH_DIAGNOSTICS_STATUS_READY_FOR_REAL_API = "ready_for_real_api"


def get_google_health_diagnostics(
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthDiagnosticsResponse:
    """
    Build a non-sensitive Google Health diagnostics response.

    This endpoint is for local development and release checks. It reports which
    setup gate is currently blocking the Google Health path without exposing
    tokens, client secrets, authorization codes, or raw health payloads.
    """

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    redirect_uri_configured = bool(config.google_health_redirect_uri)
    oauth_configured = credentials_result.loaded and redirect_uri_configured
    runtime_guard = evaluate_google_health_runtime_guard(config)
    token = _load_token_summary(token_store or GoogleHealthTokenStore())

    config_summary = GoogleHealthDiagnosticConfigModel(
        sleep_provider=config.sleep_provider,
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        oauth_configured=oauth_configured,
        credentials_file_configured=bool(config.google_health_credentials_file),
        credentials_loaded=credentials_result.loaded,
        redirect_uri_configured=redirect_uri_configured,
        real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
        real_token_refresh_enabled=config.google_health_enable_real_token_refresh,
        real_api_requests_enabled=config.google_health_enable_real_api_requests,
        endpoint_verified=config.google_health_real_endpoint_verified,
        real_api_opt_in=config.google_health_real_api_opt_in,
    )
    guard_summary = _build_guard_summary(runtime_guard)

    overall_status, message, error = _classify_diagnostics(
        config=config,
        oauth_configured=oauth_configured,
        credentials_error=credentials_result.error,
        runtime_guard=runtime_guard,
        token=token,
    )

    ready_for_sleep_provider = oauth_configured and token.stored
    ready_for_real_api_request = ready_for_sleep_provider and runtime_guard.real_api_allowed

    return GoogleHealthDiagnosticsResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        overall_status=overall_status,
        ready_for_oauth=oauth_configured,
        ready_for_sleep_provider=ready_for_sleep_provider,
        ready_for_real_api_request=ready_for_real_api_request,
        config=config_summary,
        runtime_guard=guard_summary,
        token=token,
        message=message,
        error=error,
    )


def _load_token_summary(token_store: GoogleHealthTokenStore) -> GoogleHealthDiagnosticTokenModel:
    """Load a safe token summary without exposing token values."""

    stored_tokens = token_store.load_tokens()
    if stored_tokens is None:
        return GoogleHealthDiagnosticTokenModel(stored=False)

    return _build_token_summary(stored_tokens)


def _build_token_summary(
    stored_tokens: StoredGoogleHealthTokens,
) -> GoogleHealthDiagnosticTokenModel:
    now = datetime.now(timezone.utc)
    access_token_expired = stored_tokens.is_access_token_expired(now=now)
    refresh_recommended = stored_tokens.should_refresh_access_token(now=now)

    return GoogleHealthDiagnosticTokenModel(
        stored=True,
        has_refresh_token=bool(stored_tokens.refresh_token),
        access_token_expired=access_token_expired,
        refresh_recommended=refresh_recommended,
        expires_at=stored_tokens.expires_at.isoformat()
        if stored_tokens.expires_at
        else None,
        token_type=stored_tokens.token_type,
        scope_configured=bool(stored_tokens.scope),
    )


def _build_guard_summary(
    runtime_guard: GoogleHealthRuntimeGuardResult,
) -> GoogleHealthDiagnosticRuntimeGuardModel:
    return GoogleHealthDiagnosticRuntimeGuardModel(
        real_api_requested=runtime_guard.real_api_requested,
        real_api_allowed=runtime_guard.real_api_allowed,
        api_base_url_placeholder=runtime_guard.api_base_url_placeholder,
        endpoint_verified=runtime_guard.endpoint_verified,
        real_api_opt_in=runtime_guard.real_api_opt_in,
        sleep_api_path_configured=runtime_guard.sleep_api_path_configured,
        api_timeout_valid=runtime_guard.api_timeout_valid,
        message=runtime_guard.message,
        next_action=runtime_guard.next_action,
        error=runtime_guard.error,
    )


def _classify_diagnostics(
    *,
    config: AppConfig,
    oauth_configured: bool,
    credentials_error: str | None,
    runtime_guard: GoogleHealthRuntimeGuardResult,
    token: GoogleHealthDiagnosticTokenModel,
) -> tuple[str, str, str | None]:
    """Classify the current Google Health setup into one actionable status."""

    if config.sleep_provider != GOOGLE_HEALTH_PROVIDER_NAME:
        return (
            GOOGLE_HEALTH_DIAGNOSTICS_STATUS_MOCK_MODE,
            (
                "SLEEP_PROVIDER is not google_health. The app can keep using "
                "mock or wearable_stub data while Google Health is configured."
            ),
            None,
        )

    if not oauth_configured:
        return (
            GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_CREDENTIALS,
            (
                "Google Health OAuth is not fully configured. Add local "
                "credentials.json and GOOGLE_HEALTH_REDIRECT_URI before "
                "starting the connect flow."
            ),
            credentials_error or "redirect_uri_not_configured",
        )

    if not token.stored:
        return (
            GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_AUTH,
            (
                "Google Health OAuth settings are ready, but no local token "
                "snapshot is stored yet. Use /google-health/connect and "
                "/google-health/callback in local development."
            ),
            "no_stored_tokens",
        )

    if not runtime_guard.real_api_requested:
        return (
            GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_DISABLED,
            (
                "Google Health token state exists, but real API requests are "
                "disabled. This is the expected safe default. The next setup "
                "step is to verify the official endpoint and OAuth scope before "
                "setting GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1."
            ),
            None,
        )

    if not runtime_guard.real_api_allowed:
        return (
            GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_BLOCKED,
            runtime_guard.message,
            runtime_guard.error,
        )

    return (
        GOOGLE_HEALTH_DIAGNOSTICS_STATUS_READY_FOR_REAL_API,
        (
            "Google Health configuration, stored token state, and runtime "
            "API guard are ready for a real API request."
        ),
        None,
    )
