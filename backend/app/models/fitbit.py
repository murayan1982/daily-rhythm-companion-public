from pydantic import BaseModel


class FitbitStatusResponse(BaseModel):
    connected: bool
    provider: str
    message: str


class FitbitConnectResponse(BaseModel):
    ready: bool
    connect_url: str | None = None
    message: str


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


class FitbitStubResponse(BaseModel):
    message: str
