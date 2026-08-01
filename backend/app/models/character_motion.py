"""App-owned provider-neutral character-motion mapping models.

RT-6b intentionally defines only deterministic DRC data contracts. This module
must not import AI Character Framework, Live2D, VTube Studio, websocket,
network, audio, microphone, or provider SDK modules.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


CHARACTER_MOTION_MAX_COMMANDS = 3
CHARACTER_MOTION_MAX_ID_CHARS = 128
CHARACTER_MOTION_MAX_EXPRESSION_CHARS = 64


class CharacterMotionLifecycleFact(str, Enum):
    """Bounded app-owned lifecycle facts accepted by the RT-6b mapper."""

    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    RESPONDING = "responding"
    TTS_PREPARING = "tts_preparing"
    SPEAKING = "speaking"
    MOTION_ACTIVE = "motion_active"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"
    FAILED = "failed"
    CLOSED = "closed"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class CharacterMotionCue(str, Enum):
    """DRC-owned cue vocabulary compatible with the existing motion demo."""

    GREETING = "greeting"
    THINKING = "thinking"
    HAPPY = "happy"
    TIRED_SUPPORTIVE = "tired_supportive"
    SPEAKING = "speaking"
    IDLE = "idle"


class CharacterMotionCommandIntent(str, Enum):
    """Provider-neutral command intents without Framework runtime ownership."""

    EXPRESSION = "expression"
    SPEAKING_STATE = "speaking_state"
    IDLE_MOTION = "idle_motion"
    STOP_MOTION = "stop_motion"
    RESET_EXPRESSION = "reset_expression"


class CharacterMotionMappingOutcome(str, Enum):
    """Whether one lifecycle fact produced a bounded motion plan."""

    MAPPED = "mapped"
    IGNORED = "ignored"


class CharacterMotionMappingInput(BaseModel):
    """Public-safe deterministic input for character-motion planning."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "drc.v3.character-motion-mapping-input.1"
    fact: CharacterMotionLifecycleFact
    source_event_type: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    session_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    turn_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    character_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )


class CharacterMotionCommand(BaseModel):
    """One ordered, bounded app-owned command in a motion plan."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    order: int = Field(ge=1, le=CHARACTER_MOTION_MAX_COMMANDS)
    intent: CharacterMotionCommandIntent
    expression_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_EXPRESSION_CHARS
    )
    motion_event: CharacterMotionCue | None = None
    speaking: bool | None = None

    @model_validator(mode="after")
    def validate_intent_payload(self) -> "CharacterMotionCommand":
        """Reject ambiguous commands before any later adapter sees them."""

        if self.intent is CharacterMotionCommandIntent.EXPRESSION:
            if not self.expression_id or self.motion_event is not None or self.speaking is not None:
                raise ValueError("expression command requires only expression_id")
        elif self.intent is CharacterMotionCommandIntent.SPEAKING_STATE:
            if self.speaking is None or self.expression_id is not None or self.motion_event is not None:
                raise ValueError("speaking_state command requires only speaking")
        elif self.intent is CharacterMotionCommandIntent.IDLE_MOTION:
            if self.motion_event is not CharacterMotionCue.IDLE:
                raise ValueError("idle_motion command requires idle motion_event")
            if self.expression_id is not None or self.speaking is not None:
                raise ValueError("idle_motion command cannot carry expression or speaking")
        else:
            if self.expression_id is not None or self.motion_event is not None or self.speaking is not None:
                raise ValueError(f"{self.intent.value} command cannot carry payload")
        return self


class CharacterMotionPlan(BaseModel):
    """Deterministic mapping result with at most three ordered commands."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "drc.v3.character-motion-plan.1"
    outcome: CharacterMotionMappingOutcome
    source_fact: CharacterMotionLifecycleFact
    cue: CharacterMotionCue | None = None
    reason_code: str = Field(max_length=64)
    commands: list[CharacterMotionCommand] = Field(
        default_factory=list, max_length=CHARACTER_MOTION_MAX_COMMANDS
    )
    source_event_type: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    session_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    turn_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    character_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )

    @model_validator(mode="after")
    def validate_plan_shape(self) -> "CharacterMotionPlan":
        orders = [command.order for command in self.commands]
        if orders != list(range(1, len(self.commands) + 1)):
            raise ValueError("commands must use contiguous one-based order")
        if self.outcome is CharacterMotionMappingOutcome.IGNORED:
            if self.cue is not None or self.commands:
                raise ValueError("ignored plan cannot contain a cue or commands")
        elif self.cue is None or not self.commands:
            raise ValueError("mapped plan requires a cue and at least one command")
        return self
