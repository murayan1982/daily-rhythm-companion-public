"""Strict request contract for the RT-6f manual motion presentation route."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.character_motion import (
    CHARACTER_MOTION_MAX_ID_CHARS,
    CharacterMotionLifecycleFact,
)


CHARACTER_MOTION_MANUAL_EVENT_TYPE = "home_screen_manual_motion"


class CharacterMotionPresentationRequest(BaseModel):
    """One explicit HomeScreen Apply request for the local mock adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[
        "drc.v3.character-motion-presentation-request.1"
    ] = "drc.v3.character-motion-presentation-request.1"
    source_fact: CharacterMotionLifecycleFact
    source_event_type: str = Field(max_length=CHARACTER_MOTION_MAX_ID_CHARS)
    source_session_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    source_turn_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    character_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )

    @model_validator(mode="after")
    def validate_manual_boundary(self) -> "CharacterMotionPresentationRequest":
        """Keep RT-6f limited to the accepted manual HomeScreen boundary."""

        if self.source_event_type != CHARACTER_MOTION_MANUAL_EVENT_TYPE:
            raise ValueError("source_event_type must be home_screen_manual_motion")
        if self.source_session_id is not None or self.source_turn_id is not None:
            raise ValueError("manual motion presentation does not accept session or turn IDs")
        return self
