from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.framework_v600_realtime import (
    MAX_INPUT_TEXT_CHARS,
    FrameworkV600CapabilitySnapshot,
    FrameworkV600DiagnosticsSnapshot,
    FrameworkV600InterruptResult,
    FrameworkV600OpenResult,
    FrameworkV600TurnResult,
)

VALID_INTERRUPT_SCOPES = (
    "current_turn",
    "llm_stream",
    "tts_queue",
    "voice_output",
    "motion",
    "all",
)
VALID_INTERRUPT_REASONS = (
    "user_barge_in",
    "user_cancel",
    "new_turn_started",
    "session_closed",
    "timeout",
    "host_app_request",
    "provider_failure",
)


class FrameworkV600RealtimeTurnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_text: str = Field(..., min_length=1, max_length=MAX_INPUT_TEXT_CHARS)

    @field_validator("input_text")
    @classmethod
    def _non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("input_text is required")
        return value


class FrameworkV600RealtimeInterruptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scope: str = "current_turn"
    reason: str = "host_app_request"

    @field_validator("scope")
    @classmethod
    def _valid_scope(cls, value: str) -> str:
        if value not in VALID_INTERRUPT_SCOPES:
            raise ValueError("invalid interrupt scope")
        return value

    @field_validator("reason")
    @classmethod
    def _valid_reason(cls, value: str) -> str:
        if value not in VALID_INTERRUPT_REASONS:
            raise ValueError("invalid interrupt reason")
        return value


class FrameworkV600RealtimeApiProblem(BaseModel):
    code: str
    message: str
    retryable: bool = False


__all__ = [
    "FrameworkV600CapabilitySnapshot",
    "FrameworkV600DiagnosticsSnapshot",
    "FrameworkV600InterruptResult",
    "FrameworkV600OpenResult",
    "FrameworkV600RealtimeApiProblem",
    "FrameworkV600RealtimeInterruptRequest",
    "FrameworkV600RealtimeTurnRequest",
    "FrameworkV600TurnResult",
    "VALID_INTERRUPT_REASONS",
    "VALID_INTERRUPT_SCOPES",
]
