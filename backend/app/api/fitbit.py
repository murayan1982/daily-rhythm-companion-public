from fastapi import APIRouter, Query

from app.config import load_config
from app.models.fitbit import (
    FitbitCallbackResponse,
    FitbitConnectResponse,
    FitbitStatusResponse,
)
from app.services.fitbit_service import (
    build_fitbit_connect_response,
    get_fitbit_status,
    handle_fitbit_callback_stub,
)

router = APIRouter(prefix="/fitbit", tags=["fitbit"])


@router.get("/status", response_model=FitbitStatusResponse)
def read_fitbit_status() -> FitbitStatusResponse:
    config = load_config()
    return get_fitbit_status(config)


@router.get("/connect", response_model=FitbitConnectResponse)
def connect_fitbit() -> FitbitConnectResponse:
    config = load_config()
    return build_fitbit_connect_response(config)


@router.get("/callback", response_model=FitbitCallbackResponse)
def fitbit_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
) -> FitbitCallbackResponse:
    config = load_config()

    return handle_fitbit_callback_stub(
        config=config,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
    )
