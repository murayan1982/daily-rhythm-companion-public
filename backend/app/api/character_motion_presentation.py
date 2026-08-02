"""Configured local RT-6f character-motion presentation endpoint."""

from fastapi import APIRouter

from app.config import load_config
from app.models.character_motion_adapter import FrameworkMockMotionExecutionResult
from app.models.character_motion_presentation import CharacterMotionPresentationRequest
from app.services.character_motion_presentation_service import (
    CharacterMotionPresentationService,
)

router = APIRouter()


@router.post(
    "/demo/character-motion/presentation",
    response_model=FrameworkMockMotionExecutionResult,
)
def create_character_motion_presentation(
    request: CharacterMotionPresentationRequest,
) -> FrameworkMockMotionExecutionResult:
    """Apply one explicit HomeScreen request through the FW mock-only adapter."""

    return CharacterMotionPresentationService(load_config()).submit(request)
