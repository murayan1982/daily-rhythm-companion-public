from fastapi import APIRouter

from app.config import load_config
from app.models.demo_status import DemoStatusResponse
from app.services.demo_status_service import DemoStatusService

router = APIRouter()


@router.get("/demo/status", response_model=DemoStatusResponse)
def get_demo_status():
    """Return app-facing demo mode and capability availability."""

    return DemoStatusService(load_config()).build_status()
