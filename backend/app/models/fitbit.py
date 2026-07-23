from enum import Enum

from pydantic import BaseModel


class FitbitConnectionState(str, Enum):
    """Provider-neutral app-facing Fitbit connection states."""

    UNCONFIGURED = "unconfigured"
    AUTHORIZATION_READY = "authorization_ready"
    TOKEN_PRESENT_UNVERIFIED = "token_present_unverified"
    CONNECTED = "connected"
    REFRESH_REQUIRED = "refresh_required"
    RECONNECT_REQUIRED = "reconnect_required"
    PERMISSION_BLOCKED = "permission_blocked"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class FitbitStatusResponse(BaseModel):
    connected: bool
    provider: str
    message: str
    connection_state: FitbitConnectionState = FitbitConnectionState.UNAVAILABLE
    verified: bool = False


class FitbitConnectResponse(BaseModel):
    ready: bool
    connect_url: str | None = None
    message: str
    connection_state: FitbitConnectionState = FitbitConnectionState.UNAVAILABLE
    verified: bool = False


class FitbitCallbackResponse(BaseModel):
    received_code: bool
    received_state: bool
    state_valid: bool = False
    state_expired: bool = False
    token_exchange_attempted: bool = False
    token_request_prepared: bool = False
    real_token_exchange_enabled: bool = False
    token_saved: bool = False
    message: str
    error: str | None = None
    error_description: str | None = None
    token_exchange_error: str | None = None
    connection_state: FitbitConnectionState = FitbitConnectionState.UNAVAILABLE
    verified: bool = False


class FitbitStubResponse(BaseModel):
    message: str
