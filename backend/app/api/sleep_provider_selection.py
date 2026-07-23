from fastapi import APIRouter

from app.config import load_config
from app.models.sleep_provider_selection import SleepProviderSelectionStatus
from app.services.sleep_provider_selection_service import (
    get_sleep_provider_selection_status,
)

router = APIRouter()


@router.get("/sleep/providers", response_model=SleepProviderSelectionStatus)
def read_sleep_provider_selection() -> SleepProviderSelectionStatus:
    return get_sleep_provider_selection_status(load_config())
