from __future__ import annotations

from pathlib import Path

from app.config import AppConfig
from app.models.google_health import (
    GoogleHealthPreflightApiModel,
    GoogleHealthPreflightCredentialsModel,
    GoogleHealthPreflightOAuthModel,
    GoogleHealthPreflightResponse,
    GoogleHealthPreflightTokenModel,
)
from app.services.google_health_credentials import load_google_health_credentials
from app.services.google_health_oauth_state_store import GoogleHealthOAuthStateStore
from app.services.google_health_oauth_url import build_google_health_authorization_url
from app.services.google_health_runtime_guard import evaluate_google_health_runtime_guard
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_PREFLIGHT_STATUS_MOCK_MODE = "mock_mode"
GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_CREDENTIALS = "needs_credentials"
GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_REDIRECT_URI = "needs_redirect_uri"
GOOGLE_HEALTH_PREFLIGHT_STATUS_REDIRECT_URI_NOT_REGISTERED = "redirect_uri_not_registered"
GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_SCOPES = "needs_scopes"
GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_AUTH = "needs_auth"
GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_TOKEN_REFRESH = "needs_token_refresh"
GOOGLE_HEALTH_PREFLIGHT_STATUS_API_DISABLED = "api_disabled"
GOOGLE_HEALTH_PREFLIGHT_STATUS_API_BLOCKED = "api_blocked"
GOOGLE_HEALTH_PREFLIGHT_STATUS_READY_FOR_REAL_API = "ready_for_real_api"


def get_google_health_preflight(
    config: AppConfig,
    *,
    token_store: GoogleHealthTokenStore | None = None,
    state_store: GoogleHealthOAuthStateStore | None = None,
) -> GoogleHealthPreflightResponse:
    """
    Return a non-sensitive preflight checklist for v0.21 real API testing.

    The response intentionally contains only configured/missing and
    allowed/blocked style metadata. It must never expose client secrets,
    authorization codes, token values, Authorization headers, or raw Google
    Health payloads.
    """

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    redirect_uri = config.google_health_redirect_uri
    redirect_uri_configured = bool(redirect_uri)
    redirect_uri_registered = _is_redirect_uri_registered(
        redirect_uri=redirect_uri,
        registered_uris=credentials_result.preview.redirect_uris
        if credentials_result.preview
        else (),
    )

    credentials_model = GoogleHealthPreflightCredentialsModel(
        credentials_file_configured=bool(config.google_health_credentials_file),
        credentials_file_exists=_credentials_file_exists(
            credentials_result.credentials_file
        ),
        credentials_loaded=credentials_result.loaded,
        client_id_configured=bool(
            credentials_result.preview and credentials_result.preview.client_id_configured
        ),
        client_secret_configured=bool(
            credentials_result.preview
            and credentials_result.preview.client_secret_configured
        ),
        redirect_uri_configured=redirect_uri_configured,
        redirect_uri_registered=redirect_uri_registered,
        message=credentials_result.message,
        error=credentials_result.error,
    )

    oauth_model = _build_oauth_model(
        config=config,
        credentials_loaded=credentials_result.loaded,
        credentials=credentials_result.credentials,
        state_store=state_store or GoogleHealthOAuthStateStore(),
    )
    token_model = _build_token_model(token_store or GoogleHealthTokenStore())
    runtime_guard = evaluate_google_health_runtime_guard(config)
    api_model = GoogleHealthPreflightApiModel(
        real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
        real_token_refresh_enabled=config.google_health_enable_real_token_refresh,
        real_api_requests_enabled=config.google_health_enable_real_api_requests,
        endpoint_verified=runtime_guard.endpoint_verified,
        real_api_opt_in=runtime_guard.real_api_opt_in,
        real_api_requests_allowed=runtime_guard.real_api_allowed,
        api_base_url_placeholder=runtime_guard.api_base_url_placeholder,
        sleep_api_path_configured=runtime_guard.sleep_api_path_configured,
        api_timeout_valid=runtime_guard.api_timeout_valid,
        message=runtime_guard.message,
        next_action=runtime_guard.next_action,
        error=runtime_guard.error,
    )

    status, message, next_action, error = _classify_preflight(
        config=config,
        credentials=credentials_model,
        oauth=oauth_model,
        token=token_model,
        api=api_model,
    )

    return GoogleHealthPreflightResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        status=status,
        ready_for_oauth=bool(
            credentials_model.credentials_loaded
            and credentials_model.redirect_uri_configured
            and credentials_model.redirect_uri_registered is not False
            and oauth_model.scopes_configured
            and oauth_model.auth_url_ready
        ),
        ready_for_auth_callback=bool(oauth_model.auth_url_ready),
        ready_for_token_refresh=bool(
            token_model.stored
            and token_model.has_refresh_token
            and config.google_health_enable_real_token_refresh
        ),
        ready_for_real_api_request=bool(
            token_model.stored and not token_model.refresh_recommended and api_model.real_api_requests_allowed
        ),
        credentials=credentials_model,
        oauth=oauth_model,
        token=token_model,
        api=api_model,
        message=message,
        next_action=next_action,
        error=error,
    )


def _credentials_file_exists(credentials_file: str | None) -> bool:
    return bool(credentials_file and Path(credentials_file).exists())


def _is_redirect_uri_registered(
    *,
    redirect_uri: str | None,
    registered_uris: tuple[str, ...],
) -> bool | None:
    if not redirect_uri:
        return None

    if not registered_uris:
        return None

    return redirect_uri in registered_uris


def _build_oauth_model(
    *,
    config: AppConfig,
    credentials_loaded: bool,
    credentials,
    state_store: GoogleHealthOAuthStateStore,
) -> GoogleHealthPreflightOAuthModel:
    scopes = config.google_health_oauth_scopes
    scopes_configured = bool(scopes)

    if not credentials_loaded or credentials is None:
        return GoogleHealthPreflightOAuthModel(
            scopes_configured=scopes_configured,
            scope_count=len(scopes),
            auth_url_ready=False,
            state_ready=False,
            message="Google Health OAuth URL was not prepared because credentials are not loaded.",
            error="credentials_not_loaded",
        )

    oauth_state = state_store.create_state()
    url_result = build_google_health_authorization_url(
        config=config,
        credentials=credentials,
        state=oauth_state.state,
        scopes=scopes,
    )

    return GoogleHealthPreflightOAuthModel(
        scopes_configured=scopes_configured,
        scope_count=len(url_result.scopes),
        auth_url_ready=url_result.ready,
        state_ready=bool(url_result.state),
        message=url_result.message,
        error=url_result.error,
    )


def _build_token_model(token_store: GoogleHealthTokenStore) -> GoogleHealthPreflightTokenModel:
    tokens = token_store.load_tokens()

    if tokens is None:
        return GoogleHealthPreflightTokenModel(stored=False)

    return GoogleHealthPreflightTokenModel(
        stored=True,
        has_refresh_token=bool(tokens.refresh_token),
        access_token_expired=tokens.is_access_token_expired(),
        refresh_recommended=tokens.should_refresh_access_token(),
        scope_configured=bool(tokens.scope),
    )


def _classify_preflight(
    *,
    config: AppConfig,
    credentials: GoogleHealthPreflightCredentialsModel,
    oauth: GoogleHealthPreflightOAuthModel,
    token: GoogleHealthPreflightTokenModel,
    api: GoogleHealthPreflightApiModel,
) -> tuple[str, str, str, str | None]:
    if config.sleep_provider != GOOGLE_HEALTH_PROVIDER_NAME:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_MOCK_MODE,
            "SLEEP_PROVIDER is not google_health.",
            "Set SLEEP_PROVIDER=google_health when you are ready to test the real Google Health path.",
            None,
        )

    if not credentials.credentials_loaded:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_CREDENTIALS,
            "Google Health credentials are not loaded.",
            "Place local credentials.json under backend/ or update GOOGLE_HEALTH_CREDENTIALS_FILE.",
            credentials.error or "credentials_not_loaded",
        )

    if not credentials.redirect_uri_configured:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_REDIRECT_URI,
            "GOOGLE_HEALTH_REDIRECT_URI is not configured.",
            "Set GOOGLE_HEALTH_REDIRECT_URI to the local callback URL registered in Google Cloud.",
            "redirect_uri_not_configured",
        )

    if credentials.redirect_uri_registered is False:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_REDIRECT_URI_NOT_REGISTERED,
            "GOOGLE_HEALTH_REDIRECT_URI is not listed in credentials.json redirect_uris.",
            "Register the callback URI in Google Cloud and download updated web credentials.",
            "redirect_uri_not_registered",
        )

    if not oauth.scopes_configured:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_SCOPES,
            "GOOGLE_HEALTH_OAUTH_SCOPES is empty.",
            "Set conservative OAuth scopes before starting the connect flow.",
            "oauth_scopes_not_configured",
        )

    if not token.stored:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_AUTH,
            "OAuth setup is ready, but no local token snapshot is stored.",
            "Open /google-health/connect, complete OAuth, and return through /google-health/callback.",
            "no_stored_tokens",
        )

    if token.refresh_recommended:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_NEEDS_TOKEN_REFRESH,
            "A stored token exists, but token refresh is recommended before real API testing.",
            "Enable GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1 and run /google-health/self-check locally.",
            "token_refresh_recommended",
        )

    if not api.real_api_requests_enabled:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_API_DISABLED,
            "Real Google Health API requests are disabled by guard.",
            (
                "Verify the official sleep endpoint and OAuth scope, set "
                "GOOGLE_HEALTH_API_BASE_URL / GOOGLE_HEALTH_SLEEP_API_PATH, "
                "set GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1, and only then "
                "enable GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1 for a guarded local test."
            ),
            None,
        )

    if not api.real_api_requests_allowed:
        return (
            GOOGLE_HEALTH_PREFLIGHT_STATUS_API_BLOCKED,
            api.message or "Google Health real API request settings are blocked.",
            api.next_action or "Fix the runtime guard error before attempting a real HTTP request.",
            api.error,
        )

    return (
        GOOGLE_HEALTH_PREFLIGHT_STATUS_READY_FOR_REAL_API,
        "Google Health real credentials preflight is ready for guarded real API testing.",
        "Run /google-health/self-check and then /sleep/summary with SLEEP_PROVIDER=google_health.",
        None,
    )
