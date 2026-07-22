from __future__ import annotations

from datetime import datetime, timezone

from app.config import AppConfig
from app.models.google_health import (
    GoogleHealthCallbackResponse,
    GoogleHealthConnectResponse,
    GoogleHealthStatusResponse,
    GoogleHealthTokenRequestPreviewModel,
)
from app.services.google_health_credentials import (
    load_google_health_credentials,
)
from app.services.google_health_oauth_state_store import (
    GoogleHealthOAuthState,
    GoogleHealthOAuthStateStore,
)
from app.services.google_health_oauth_url import (
    build_google_health_authorization_url,
)
from app.services.google_health_runtime_guard import (
    evaluate_google_health_runtime_guard,
)
from app.services.google_health_token_exchange import (
    exchange_google_health_authorization_code,
)


GOOGLE_HEALTH_PROVIDER_NAME = "google_health"


def get_google_health_status(
    config: AppConfig,
) -> GoogleHealthStatusResponse:
    """Return Google Health OAuth readiness status."""

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    redirect_uri_configured = bool(config.google_health_redirect_uri)
    configured = credentials_result.loaded and redirect_uri_configured
    runtime_guard = evaluate_google_health_runtime_guard(config)

    if configured:
        return GoogleHealthStatusResponse(
            configured=True,
            credentials_loaded=True,
            redirect_uri_configured=True,
            provider=GOOGLE_HEALTH_PROVIDER_NAME,
            message="Google Health OAuth readiness is configured.",
            error=runtime_guard.error,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            real_token_refresh_enabled=config.google_health_enable_real_token_refresh,
            real_api_requests_enabled=config.google_health_enable_real_api_requests,
            endpoint_verified=runtime_guard.endpoint_verified,
            real_api_requests_allowed=runtime_guard.real_api_allowed,
            api_base_url_placeholder=runtime_guard.api_base_url_placeholder,
            sleep_api_path_configured=runtime_guard.sleep_api_path_configured,
            api_timeout_valid=runtime_guard.api_timeout_valid,
        )

    return GoogleHealthStatusResponse(
        configured=False,
        credentials_loaded=credentials_result.loaded,
        redirect_uri_configured=redirect_uri_configured,
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        message="Google Health OAuth readiness is not fully configured.",
        error=credentials_result.error
        if not credentials_result.loaded
        else "redirect_uri_not_configured",
        real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
        real_token_refresh_enabled=config.google_health_enable_real_token_refresh,
        real_api_requests_enabled=config.google_health_enable_real_api_requests,
        endpoint_verified=runtime_guard.endpoint_verified,
        real_api_requests_allowed=runtime_guard.real_api_allowed,
        api_base_url_placeholder=runtime_guard.api_base_url_placeholder,
        sleep_api_path_configured=runtime_guard.sleep_api_path_configured,
        api_timeout_valid=runtime_guard.api_timeout_valid,
    )


def build_google_health_connect_response(
    config: AppConfig,
    state_store: GoogleHealthOAuthStateStore | None = None,
) -> GoogleHealthConnectResponse:
    """
    Build a Google Health OAuth connect response.

    This prepares an authorization URL only. It does not prove that a sleep
    data API/scope is available yet.
    """

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )

    if not credentials_result.loaded or credentials_result.credentials is None:
        return GoogleHealthConnectResponse(
            ready=False,
            connect_url=None,
            state=None,
            message=credentials_result.message
            or "Google Health credentials could not be loaded.",
            error=credentials_result.error,
        )

    store = state_store or GoogleHealthOAuthStateStore()
    oauth_state = store.create_state()

    url_result = build_google_health_authorization_url(
        config=config,
        credentials=credentials_result.credentials,
        state=oauth_state.state,
        scopes=config.google_health_oauth_scopes,
    )

    return GoogleHealthConnectResponse(
        ready=url_result.ready,
        connect_url=url_result.auth_url,
        state=url_result.state,
        message=url_result.message,
        error=url_result.error,
    )


def handle_google_health_callback_stub(
    *,
    config: AppConfig,
    code: str | None,
    state: str | None,
    error: str | None,
    error_description: str | None,
    state_store: GoogleHealthOAuthStateStore | None = None,
) -> GoogleHealthCallbackResponse:
    """
    Handle a Google Health OAuth callback.

    v0.14.0 Day5 receives callback parameters, validates OAuth state, prepares
    a token request preview, and optionally performs guarded token exchange.
    """

    if error:
        return GoogleHealthCallbackResponse(
            received_code=bool(code),
            received_state=bool(state),
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health authorization returned an error.",
            error=error,
            error_description=error_description,
            token_request_preview=None,
        )

    if not code and not state:
        return GoogleHealthCallbackResponse(
            received_code=False,
            received_state=False,
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health callback was called without authorization data.",
            error=None,
            error_description=None,
            token_request_preview=None,
        )

    if not code:
        return GoogleHealthCallbackResponse(
            received_code=False,
            received_state=bool(state),
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health callback did not include an authorization code.",
            error="missing_code",
            error_description=None,
            token_request_preview=None,
        )

    if not state:
        return GoogleHealthCallbackResponse(
            received_code=True,
            received_state=False,
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health callback did not include an OAuth state.",
            error="missing_state",
            error_description=None,
            token_request_preview=None,
        )

    store = state_store or GoogleHealthOAuthStateStore()
    stored_state = store.load_state()

    if stored_state is None:
        return GoogleHealthCallbackResponse(
            received_code=True,
            received_state=True,
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health OAuth state was not found.",
            error="missing_saved_state",
            error_description=None,
            token_request_preview=None,
        )

    if stored_state.state != state:
        return GoogleHealthCallbackResponse(
            received_code=True,
            received_state=True,
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health OAuth state validation failed.",
            error="invalid_state",
            error_description="The callback state did not match the saved OAuth state.",
            token_request_preview=None,
        )

    if _is_state_expired(stored_state):
        return GoogleHealthCallbackResponse(
            received_code=True,
            received_state=True,
            state_valid=False,
            state_expired=True,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health OAuth state expired.",
            error="invalid_state_expired",
            error_description="The saved OAuth state expired before the callback was received.",
            token_request_preview=None,
        )

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )

    if not credentials_result.loaded or credentials_result.credentials is None:
        return GoogleHealthCallbackResponse(
            received_code=True,
            received_state=True,
            state_valid=True,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=config.google_health_enable_real_token_exchange,
            token_saved=False,
            message="Google Health callback received, but credentials could not be loaded.",
            error=credentials_result.error,
            error_description=credentials_result.message,
            token_request_preview=None,
        )

    exchange_result = exchange_google_health_authorization_code(
        config=config,
        credentials=credentials_result.credentials,
        code=code,
    )

    preview_model = _build_preview_model(exchange_result.request_preview)

    return GoogleHealthCallbackResponse(
        received_code=True,
        received_state=True,
        state_valid=True,
        state_expired=False,
        token_exchange_attempted=exchange_result.attempted,
        token_request_prepared=exchange_result.request_prepared,
        real_token_exchange_enabled=exchange_result.real_exchange_enabled,
        token_saved=exchange_result.saved,
        message=exchange_result.message,
        error=exchange_result.error,
        error_description=None,
        token_request_preview=preview_model,
    )


def _build_preview_model(
    preview,
) -> GoogleHealthTokenRequestPreviewModel | None:
    if preview is None:
        return None

    return GoogleHealthTokenRequestPreviewModel(
        endpoint=preview.endpoint,
        grant_type=preview.grant_type,
        redirect_uri=preview.redirect_uri,
        has_client_id=preview.has_client_id,
        has_client_secret=preview.has_client_secret,
        has_code=preview.has_code,
    )


def _is_state_expired(
    oauth_state: GoogleHealthOAuthState,
) -> bool:
    try:
        expires_at = datetime.fromisoformat(oauth_state.expires_at)
    except ValueError:
        return True

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) >= expires_at