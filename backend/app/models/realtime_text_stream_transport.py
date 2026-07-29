from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.models.realtime_text_stream import (
    REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS,
    RealtimeTextStreamSession,
    RealtimeTextStreamState,
    RealtimeTextStreamTurn,
)

REALTIME_TEXT_STREAM_MAX_INPUT_CHARS = REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS
REALTIME_TEXT_STREAM_MAX_PROBLEM_MESSAGE_CHARS = 240


class RealtimeTextStreamCreateRequest(BaseModel):
    """Create one bounded Backend-owned incremental text stream session."""

    input_text: str = Field(
        min_length=1,
        max_length=REALTIME_TEXT_STREAM_MAX_INPUT_CHARS,
    )

    @field_validator("input_text")
    @classmethod
    def validate_input_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("input_text must contain non-whitespace text")
        return normalized


class RealtimeTextStreamCreateResponse(BaseModel):
    """Public-safe creation response without echoing the input text."""

    schema_version: str = "drc.v3.realtime-text-stream-create.1"
    accepted: bool = True
    session: RealtimeTextStreamSession
    turn: RealtimeTextStreamTurn
    events_path: str
    cancel_path: str
    idle_ttl_seconds: int = Field(ge=1)
    max_duration_seconds: int = Field(ge=1)
    max_pending_events: int = Field(ge=1)
    max_event_bytes: int = Field(ge=1)


class RealtimeTextStreamCancelResponse(BaseModel):
    """Public-safe cooperative cancel response."""

    schema_version: str = "drc.v3.realtime-text-stream-cancel.1"
    accepted: bool
    session_id: str
    turn_id: str | None = None
    state: RealtimeTextStreamState
    cancel_mode: str = "cooperative"
    hard_cancel_supported: bool = False
    terminal: bool = False
    safe_message: str = Field(
        default="",
        max_length=REALTIME_TEXT_STREAM_MAX_PROBLEM_MESSAGE_CHARS,
    )


class RealtimeTextStreamProblem(BaseModel):
    """Bounded HTTP problem detail for the RT-4 transport boundary."""

    schema_version: str = "drc.v3.realtime-text-stream-problem.1"
    code: str
    message: str = Field(max_length=REALTIME_TEXT_STREAM_MAX_PROBLEM_MESSAGE_CHARS)
    retryable: bool = False
