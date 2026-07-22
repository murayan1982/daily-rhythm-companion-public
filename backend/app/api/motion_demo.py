from fastapi import APIRouter

from app.config import load_config
from app.models.motion_demo import (
    MotionDemoRequest,
    MotionDemoRequestResponse,
    MotionDemoStatusResponse,
)
from app.services.motion_demo_service import MotionDemoService

router = APIRouter()


@router.get("/demo/motion/status", response_model=MotionDemoStatusResponse)
def get_motion_demo_status():
    """Return the guarded v0.36.0 Live2D/VTS motion demo boundary status."""

    return MotionDemoService(load_config()).build_status()


@router.post("/demo/motion", response_model=MotionDemoRequestResponse)
def create_motion_demo_request(request: MotionDemoRequest):
    """Accept a metadata-only Live2D/VTS motion demo request.

    This endpoint is intentionally a safe contract placeholder. It does not
    connect to VTube Studio, load Live2D runtime dependencies, or send motion
    commands yet; it returns the current capability status and a clear
    not-started result for the future Flutter motion flow.
    """

    return MotionDemoService(load_config()).submit_request(request)
