from fastapi import APIRouter, HTTPException

from app.config import load_config
from app.models.sleep import SleepSummary
from app.services.sleep_summary_service import get_sleep_summary

router = APIRouter()


@router.get("/sleep/summary", response_model=SleepSummary)
def read_sleep_summary() -> SleepSummary:
    config = load_config()

    try:
        return get_sleep_summary(config)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc