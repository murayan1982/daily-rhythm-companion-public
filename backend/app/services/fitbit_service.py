from urllib.parse import urlencode

from app.config import AppConfig
from app.models.fitbit import (
    FitbitCallbackResponse,
    FitbitConnectResponse,
    FitbitStatusResponse,
)
from app.services.fitbit_oauth_state_store import FitbitOAuthStateStore
from app.services.fitbit_token_exchange import exchange_fitbit_code_stub
from app.services.fitbit_token_store import FitbitTokenStore


def get_fitbit_status(config: AppConfig) -> FitbitStatusResponse:
    """
    Return the current Fitbit connection status.

    v0.4.0+ checks configuration and a local token-store placeholder. Real
    OAuth/token validation will be added in a later version.
    """

    has_config = all(
        [
            config.fitbit_client_id,
            config.fitbit_client_secret,
            config.fitbit_redirect_uri,
        ]
    )

    token_status = FitbitTokenStore().get_status()
    has_tokens = (
        token_status.exists
        and token_status.has_access_token
        and token_status.has_refresh_token
    )

    if has_config and has_tokens:
        return FitbitStatusResponse(
            connected=True,
            provider="fitbit",
            message=(
                "Fitbit appears to be connected using local development "
                "token data. Real token validation is not implemented yet."
            ),
        )

    if has_config:
        return FitbitStatusResponse(
            connected=False,
            provider="fitbit",
            message=(
                "Fitbit credentials are configured, but local token data "
                "is not available yet."
            ),
        )

    return FitbitStatusResponse(
        connected=False,
        provider="fitbit",
        message="Fitbit integration is not configured yet.",
    )


def _build_fitbit_authorize_url(config: AppConfig, state: str) -> str:
    """Build a Fitbit OAuth authorization URL."""

    query = urlencode(
        {
            "response_type": "code",
            "client_id": config.fitbit_client_id,
            "redirect_uri": config.fitbit_redirect_uri,
            "scope": "sleep",
            "state": state,
        }
    )

    return f"https://www.fitbit.com/oauth2/authorize?{query}"


def build_fitbit_connect_response(config: AppConfig) -> FitbitConnectResponse:
    """
    Return a placeholder response for the future Fitbit OAuth connect flow.

    v0.7.0+ uses a future-ready response shape:
    - ready
    - connect_url
    - message

    v0.9.0 generates and stores OAuth state when Fitbit configuration is
    available.
    """

    if not config.fitbit_client_id or not config.fitbit_redirect_uri:
        return FitbitConnectResponse(
            ready=False,
            connect_url=None,
            message=(
                "Fitbit OAuth connect flow is not available yet. "
                "FITBIT_CLIENT_ID and FITBIT_REDIRECT_URI are not configured."
            ),
        )

    state = FitbitOAuthStateStore().create_and_save_state()

    return FitbitConnectResponse(
        ready=True,
        connect_url=_build_fitbit_authorize_url(config, state=state),
        message="Fitbit OAuth connect URL is ready. Open the URL to continue.",
    )


def handle_fitbit_callback_stub(
    config: AppConfig,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
) -> FitbitCallbackResponse:
    """
    Handle the Fitbit OAuth callback placeholder.

    v0.9.0 validates callback state before reaching the future token exchange
    boundary. Real token exchange and real token storage will be added later.
    """

    if error:
        return FitbitCallbackResponse(
            received_code=False,
            received_state=bool(state),
            state_valid=False,
            state_expired=False,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=False,
            token_saved=False,
            message="Fitbit authorization returned an error.",
            error=error,
            error_description=error_description,
            token_exchange_error=None,
        )

    if code:
        state_store = FitbitOAuthStateStore()
        state_valid = state_store.validate_state(state)

        if not state_valid:
            return FitbitCallbackResponse(
                received_code=True,
                received_state=bool(state),
                state_valid=False,
                state_expired=False,
                token_exchange_attempted=False,
                token_request_prepared=False,
                real_token_exchange_enabled=False,
                token_saved=False,
                message="Fitbit OAuth state validation failed.",
                error="invalid_state",
                error_description=(
                    "The callback state did not match the saved OAuth state."
                ),
                token_exchange_error=None,
            )

        state_expired = state_store.is_state_expired(
            config.fitbit_oauth_state_ttl_seconds
        )

        if state_expired:
            return FitbitCallbackResponse(
                received_code=True,
                received_state=bool(state),
                state_valid=False,
                state_expired=True,
                token_exchange_attempted=False,
                token_request_prepared=False,
                real_token_exchange_enabled=False,
                token_saved=False,
                message="Fitbit OAuth state has expired.",
                error="invalid_state_expired",
                error_description=(
                    "The saved OAuth state is older than the configured lifetime."
                ),
                token_exchange_error=None,
            )

        exchange_result = exchange_fitbit_code_stub(
            config=config,
            code=code,
            state=state,
            save_dummy_token=config.fitbit_dev_save_dummy_token,
        )

        return FitbitCallbackResponse(
            received_code=True,
            received_state=bool(state),
            state_valid=True,
            state_expired=False,
            token_exchange_attempted=exchange_result.attempted,
            token_request_prepared=exchange_result.request_prepared,
            real_token_exchange_enabled=exchange_result.real_exchange_enabled,
            token_saved=exchange_result.saved,
            message=exchange_result.message,
            error=None,
            error_description=None,
            token_exchange_error=exchange_result.error,
        )

    return FitbitCallbackResponse(
        received_code=False,
        received_state=bool(state),
        state_valid=False,
        state_expired=False,
        token_exchange_attempted=False,
        token_request_prepared=False,
        real_token_exchange_enabled=False,
        token_saved=False,
        message="Fitbit callback was called without authorization data.",
        error=None,
        error_description=None,
        token_exchange_error=None,
    )
