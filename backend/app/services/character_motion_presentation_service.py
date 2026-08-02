"""RT-6f assembly from the accepted mapper to the accepted FW mock adapter."""

from __future__ import annotations

from app.config import AppConfig
from app.models.character_motion import CharacterMotionMappingInput
from app.models.character_motion_adapter import FrameworkMockMotionExecutionResult
from app.models.character_motion_presentation import CharacterMotionPresentationRequest
from app.services.character_motion_mapper import CharacterMotionMapper
from app.services.framework_mock_motion_session_adapter import (
    FrameworkMockMotionSessionAdapter,
)


class CharacterMotionPresentationService:
    """Execute one explicit, bounded, provider-free local mock motion request."""

    def __init__(
        self,
        config: AppConfig,
        *,
        mapper: CharacterMotionMapper | None = None,
    ) -> None:
        self._config = config
        self._mapper = mapper or CharacterMotionMapper()

    def submit(
        self, request: CharacterMotionPresentationRequest
    ) -> FrameworkMockMotionExecutionResult:
        plan = self._mapper.map(
            CharacterMotionMappingInput(
                fact=request.source_fact,
                source_event_type=request.source_event_type,
                session_id=request.source_session_id,
                turn_id=request.source_turn_id,
                character_id=request.character_id,
            )
        )
        adapter = FrameworkMockMotionSessionAdapter(
            framework_root=self._config.framework_project_root,
            enabled=self._config.framework_mock_motion_presentation_enabled,
        )
        return adapter.execute(plan)
