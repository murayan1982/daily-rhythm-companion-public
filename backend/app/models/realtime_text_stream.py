from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS = 512
REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS = 4096
REALTIME_TEXT_STREAM_MAX_SAFE_MESSAGE_CHARS = 240


class RealtimeTextStreamState(str, Enum):
    """DRC-owned incremental text-stream lifecycle state."""

    IDLE = "idle"
    STREAMING = "streaming"
    CANCEL_REQUESTED = "cancel_requested"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    CLOSED = "closed"


class RealtimeTextStreamEventType(str, Enum):
    """Provider-neutral event types for one incremental text stream."""

    STREAM_STARTED = "stream_started"
    STREAM_CHUNK = "stream_chunk"
    CANCEL_REQUESTED = "cancel_requested"
    STREAM_COMPLETED = "stream_completed"
    STREAM_CANCELLED = "stream_cancelled"
    STREAM_FAILED = "stream_failed"
    STREAM_CLOSED = "stream_closed"


class RealtimeTextStreamTerminalOutcome(str, Enum):
    """Terminal outcomes accepted by the RT-4 Backend boundary."""

    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    CLOSED = "closed"


class RealtimeTextStreamCallbackReason(str, Enum):
    """Public-safe reason for accepting or rejecting one callback."""

    ACCEPTED = "accepted"
    SESSION_CLOSED = "session_closed"
    ACTIVE_TURN = "active_turn"
    NO_ACTIVE_TURN = "no_active_turn"
    STALE_TURN = "stale_turn"
    CANCEL_REQUESTED = "cancel_requested"
    EMPTY_CHUNK = "empty_chunk"


class RealtimeTextStreamSession(BaseModel):
    """Snapshot of one DRC-owned stream session."""

    schema_version: str = "drc.v3.realtime-text-stream-session.1"
    session_id: str
    state: RealtimeTextStreamState = RealtimeTextStreamState.IDLE
    active_turn_id: str | None = None
    last_sequence: int = Field(default=0, ge=0)
    is_closed: bool = False
    cancel_mode: str = "cooperative"
    hard_cancel_supported: bool = False


class RealtimeTextStreamTurn(BaseModel):
    """Snapshot of one incremental response turn."""

    schema_version: str = "drc.v3.realtime-text-stream-turn.1"
    session_id: str
    turn_id: str
    state: RealtimeTextStreamState
    chunk_count: int = Field(default=0, ge=0)
    output_char_count: int = Field(default=0, ge=0)
    cancel_requested: bool = False
    terminal_outcome: RealtimeTextStreamTerminalOutcome | None = None


class RealtimeTextStreamChunk(BaseModel):
    """One bounded text delta with a monotonic session sequence."""

    schema_version: str = "drc.v3.realtime-text-stream-chunk.1"
    sequence: int = Field(ge=1)
    text: str = Field(max_length=REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS)
    output_char_count: int = Field(ge=0)


class RealtimeTextStreamTerminal(BaseModel):
    """One bounded terminal payload for completed or stopped streams."""

    schema_version: str = "drc.v3.realtime-text-stream-terminal.1"
    sequence: int = Field(ge=1)
    outcome: RealtimeTextStreamTerminalOutcome
    final_text: str = Field(
        default="", max_length=REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS
    )
    output_char_count: int = Field(default=0, ge=0)
    public_error_code: str | None = None
    safe_message: str = Field(
        default="", max_length=REALTIME_TEXT_STREAM_MAX_SAFE_MESSAGE_CHARS
    )
    retryable: bool = False


class RealtimeTextStreamEvent(BaseModel):
    """Normalized lifecycle, chunk, or terminal event for future transport use."""

    schema_version: str = "drc.v3.realtime-text-stream-event.1"
    event_type: RealtimeTextStreamEventType
    session_id: str
    turn_id: str | None = None
    sequence: int = Field(ge=1)
    state: RealtimeTextStreamState
    chunk: RealtimeTextStreamChunk | None = None
    terminal: RealtimeTextStreamTerminal | None = None
    safe_message: str = Field(
        default="", max_length=REALTIME_TEXT_STREAM_MAX_SAFE_MESSAGE_CHARS
    )


class RealtimeTextStreamCallbackResult(BaseModel):
    """Result of applying one fake/provider callback to the state machine."""

    schema_version: str = "drc.v3.realtime-text-stream-callback.1"
    accepted: bool
    reason: RealtimeTextStreamCallbackReason
    event: RealtimeTextStreamEvent | None = None
    session: RealtimeTextStreamSession
    turn: RealtimeTextStreamTurn | None = None
