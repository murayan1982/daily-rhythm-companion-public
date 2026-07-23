from urllib.parse import urlencode

from app.config import AppConfig
from app.models.fitbit import (
    FitbitCallbackResponse,
    FitbitConnectionState,
    FitbitConnectResponse,
    FitbitStatusResponse,
)
from app.services.fitbit_oauth_state_store import FitbitOAuthStateStore
from app.services.fitbit_token_exchange import exchange_fitbit_code_stub
from app.services.fitbit_token_store import FitbitTokenStatus, FitbitTokenStore


def _has_fitbit_token_exchange_config(config: AppConfig) -> bool:
    return bool(
        config.fitbit_client_id
        and config.fitbit_client_secret
        and config.fitbit_redirect_uri
    )


def _classify_token_status(
    token_status: FitbitTokenStatus,
) -> FitbitConnectionState:
    if token_status.exists and not token_status.readable:
        return FitbitConnectionState.ERROR

    if not token_status.has_access_token and token_status.has_refresh_token:
        return FitbitConnectionState.REFRESH_REQUIRED

    if not token_status.has_access_token:
        return FitbitConnectionState.AUTHORIZATION_READY

    if token_status.should_refresh:
        if token_status.has_refresh_token:
            return FitbitConnectionState.REFRESH_REQUIRED
        return FitbitConnectionState.RECONNECT_REQUIRED

    return FitbitConnectionState.TOKEN_PRESENT_UNVERIFIED


def _status_message(
    state: FitbitConnectionState,
    token_status: FitbitTokenStatus,
) -> str:
    if state == FitbitConnectionState.ERROR:
        return (
            "Fitbit local token data could not be read safely. "
            "Reconnect is required before real-use verification."
        )

    if state == FitbitConnectionState.REFRESH_REQUIRED:
        return (
            "Fitbit local token data requires the guarded refresh path. "
            "Live refresh and real token validity are not verified by status."
        )

    if state == FitbitConnectionState.RECONNECT_REQUIRED:
        return (
            "Fitbit local access token data cannot be refreshed safely. "
            "Start the authorization flow again."
        )

    if state == FitbitConnectionState.TOKEN_PRESENT_UNVERIFIED:
        if token_status.is_development_dummy:
            return (
                "Fitbit development dummy token data was detected. "
                "It does not represent a real Fitbit connection."
            )
        return (
            "Fitbit appears to be connected using local development "
            "token data. Real token validation is not implemented yet."
        )

    return (
        "Fitbit credentials are configured, but local token data "
        "is not available yet."
    )


def get_fitbit_status(
    config: AppConfig,
    token_store: FitbitTokenStore | None = None,
) -> FitbitStatusResponse:
    """
    Return a non-sensitive Fitbit connection classification.

    This endpoint does not call Fitbit or refresh tokens. The legacy connected
    boolean remains backward compatible for token files containing both access
    and refresh tokens, while connection_state carries the conservative W-2
    lifecycle classification.
    """

    if not _has_fitbit_token_exchange_config(config):
        return FitbitStatusResponse(
            connected=False,
            provider="fitbit",
            message="Fitbit integration is not configured yet.",
            connection_state=FitbitConnectionState.UNCONFIGURED,
            verified=False,
        )

    store = token_store or FitbitTokenStore()
    token_status = store.get_status()
    state = _classify_token_status(token_status)

    # Preserve the legacy route's bool contract: both token-like fields still
    # produce connected=True, but verified remains False until W-5 acceptance.
    legacy_connected = bool(
        token_status.readable
        and token_status.has_access_token
        and token_status.has_refresh_token
    )

    return FitbitStatusResponse(
        connected=legacy_connected,
        provider="fitbit",
        message=_status_message(state, token_status),
        connection_state=state,
        verified=False,
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


def build_fitbit_connect_response(
    config: AppConfig,
    state_store: FitbitOAuthStateStore | None = None,
) -> FitbitConnectResponse:
    """Prepare a new OAuth authorization or reconnect URL."""

    if not config.fitbit_client_id or not config.fitbit_redirect_uri:
        return FitbitConnectResponse(
            ready=False,
            connect_url=None,
            message=(
                "Fitbit OAuth connect flow is not available yet. "
                "FITBIT_CLIENT_ID and FITBIT_REDIRECT_URI are not configured."
            ),
            connection_state=FitbitConnectionState.UNCONFIGURED,
            verified=False,
        )

    store = state_store or FitbitOAuthStateStore()
    state = store.create_and_save_state()

    return FitbitConnectResponse(
        ready=True,
        connect_url=_build_fitbit_authorize_url(config, state=state),
        message="Fitbit OAuth connect URL is ready. Open the URL to continue.",
        connection_state=FitbitConnectionState.AUTHORIZATION_READY,
        verified=False,
    )


def handle_fitbit_callback_stub(
    config: AppConfig,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    *,
    state_store: FitbitOAuthStateStore | None = None,
    token_store: FitbitTokenStore | None = None,
) -> FitbitCallbackResponse:
    """Handle the guarded Fitbit OAuth callback and one-time state lifecycle."""

    store = state_store or FitbitOAuthStateStore()

    if error:
        consume_result = store.consume_state(
            state,
            config.fitbit_oauth_state_ttl_seconds,
        )
        state_consume_failed = (
            consume_result.matched
            and not consume_result.expired
            and not consume_result.consumed
        )
        permission_blocked = (
            error.lower() == "access_denied"
            and consume_result.consumed
        )
        if state_consume_failed:
            callback_state = FitbitConnectionState.ERROR
        elif permission_blocked:
            callback_state = FitbitConnectionState.PERMISSION_BLOCKED
        else:
            callback_state = FitbitConnectionState.RECONNECT_REQUIRED

        return FitbitCallbackResponse(
            received_code=False,
            received_state=bool(state),
            state_valid=consume_result.consumed,
            state_expired=consume_result.expired,
            token_exchange_attempted=False,
            token_request_prepared=False,
            real_token_exchange_enabled=False,
            token_saved=False,
            message="Fitbit authorization returned an error.",
            error=error,
            error_description=error_description,
            token_exchange_error=None,
            connection_state=callback_state,
            verified=False,
        )

    if code:
        consume_result = store.consume_state(
            state,
            config.fitbit_oauth_state_ttl_seconds,
        )

        if not consume_result.matched:
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
                connection_state=FitbitConnectionState.RECONNECT_REQUIRED,
                verified=False,
            )

        if (
            consume_result.matched
            and not consume_result.consumed
            and not consume_result.expired
        ):
            return FitbitCallbackResponse(
                received_code=True,
                received_state=bool(state),
                state_valid=False,
                state_expired=False,
                token_exchange_attempted=False,
                token_request_prepared=False,
                real_token_exchange_enabled=False,
                token_saved=False,
                message="Fitbit OAuth state could not be consumed safely.",
                error="state_consume_failed",
                error_description=(
                    "The saved OAuth state could not be invalidated before token exchange."
                ),
                token_exchange_error=None,
                connection_state=FitbitConnectionState.ERROR,
                verified=False,
            )

        if consume_result.expired:
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
                connection_state=FitbitConnectionState.RECONNECT_REQUIRED,
                verified=False,
            )

        exchange_result = exchange_fitbit_code_stub(
            config=config,
            code=code,
            state=state,
            save_dummy_token=config.fitbit_dev_save_dummy_token,
            token_store=token_store,
        )

        if exchange_result.saved:
            connection_state = FitbitConnectionState.TOKEN_PRESENT_UNVERIFIED
        elif exchange_result.error:
            connection_state = FitbitConnectionState.ERROR
        else:
            # The authorization code and state are one-time values. When the
            # guarded exchange is disabled, the operator must start again.
            connection_state = FitbitConnectionState.RECONNECT_REQUIRED

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
            connection_state=connection_state,
            verified=False,
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
        connection_state=FitbitConnectionState.RECONNECT_REQUIRED,
        verified=False,
    )
