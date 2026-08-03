"""Default-off manual RT-7d VTS presentation endpoint."""

from fastapi import APIRouter

from app.config import load_config
from app.models.framework_vts_motion import FrameworkVtsMotionExecutionResult
from app.models.framework_vts_motion_presentation import FrameworkVtsMotionPresentationRequest
from app.services.framework_vts_motion_presentation_service import FrameworkVtsMotionPresentationService

router = APIRouter()


@router.post(
    "/demo/character-motion/vts/presentation",
    response_model=FrameworkVtsMotionExecutionResult,
)
def create_framework_vts_motion_presentation(
    request: FrameworkVtsMotionPresentationRequest,
) -> FrameworkVtsMotionExecutionResult:
    """Apply one explicit command through the guarded RT-7c adapter."""

    return FrameworkVtsMotionPresentationService(load_config()).submit(request)
