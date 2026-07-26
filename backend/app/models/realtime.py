from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RealtimeState(str, Enum):
    """DRC-owned realtime lifecycle state."""

    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    RESPONDING = "responding"
    SPEAKING = "speaking"
    MOTION = "motion"
    INTERRUPTED = "interrupted"
    FAILED = "failed"
    COMPLETED = "completed"
    CLOSED = "closed"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class RealtimeEventType(str, Enum):
    """DRC-owned event vocabulary normalized from Framework public events."""

    SESSION_CREATED = "session_created"
    TURN_STARTED = "turn_started"
    VOICE_INPUT_STARTED = "voice_input_started"
    VOICE_INPUT_COMPLETED = "voice_input_completed"
    TEXT_CHAT_STARTED = "text_chat_started"
    TEXT_CHAT_COMPLETED = "text_chat_completed"
    VOICE_OUTPUT_STARTED = "voice_output_started"
    VOICE_OUTPUT_COMPLETED = "voice_output_completed"
    MOTION_STARTED = "motion_started"
    MOTION_COMPLETED = "motion_completed"
    TURN_COMPLETED = "turn_completed"
    TURN_INTERRUPTED = "turn_interrupted"
    TURN_FAILED = "turn_failed"
    SESSION_CLOSED = "session_closed"
    INTERRUPT_REQUESTED = "interrupt_requested"
    INTERRUPT_ACCEPTED = "interrupt_accepted"
    INTERRUPT_COMPLETED = "interrupt_completed"
    INTERRUPT_UNSUPPORTED = "interrupt_unsupported"
    OUTPUT_FLUSH_REQUESTED = "output_flush_requested"
    OUTPUT_FLUSH_COMPLETED = "output_flush_completed"
    OUTPUT_FLUSH_UNSUPPORTED = "output_flush_unsupported"
    BARGE_IN_DETECTED = "barge_in_detected"
    BARGE_IN_ACCEPTED = "barge_in_accepted"
    BARGE_IN_REJECTED = "barge_in_rejected"
    UNKNOWN = "unknown"


class RealtimeCapabilityStatus(BaseModel):
    """Normalized status for one DRC realtime capability."""

    name: str
    public_contract_released: bool = False
    mock_contract_available: bool = False
    real_runtime_supported: bool = False
    real_runtime_configured: bool = False
    real_runtime_available: bool = False
    source: str = "default"
    reason_code: str | None = None
    safe_message: str = ""


class RealtimeCapabilities(BaseModel):
    """DRC-owned aggregate capability snapshot."""

    schema_version: str = "drc.v3.realtime-capabilities.1"
    voice_input: RealtimeCapabilityStatus
    realtime: RealtimeCapabilityStatus
    hard_cancel: RealtimeCapabilityStatus
    tts_queue_flush: RealtimeCapabilityStatus
    barge_in: RealtimeCapabilityStatus
    motion: RealtimeCapabilityStatus


class RealtimeEvent(BaseModel):
    """Provider-neutral event consumed by future DRC realtime services."""

    schema_version: str = "drc.v3.realtime-event.1"
    event_type: RealtimeEventType
    source_event_type: str
    state: RealtimeState = RealtimeState.UNKNOWN
    source_state: str = "unknown"
    previous_state: RealtimeState | None = None
    source_previous_state: str | None = None
    turn_id: str | None = None
    session_id: str | None = None
    boundary: str = "realtime"
    public_error_code: str | None = None
    safe_message: str = ""
    retryable: bool = False
    public_metadata: dict[str, Any] = Field(default_factory=dict)


class RealtimeSessionSnapshot(BaseModel):
    """DRC-owned normalized session metadata without runtime ownership."""

    schema_version: str = "drc.v3.realtime-session.1"
    session_id: str | None = None
    session_type: str = "realtime"
    state: RealtimeState = RealtimeState.UNKNOWN
    source_state: str = "unknown"
    active_turn_id: str | None = None
    is_closed: bool = False
    real_runtime_enabled: bool = False
    capabilities: RealtimeCapabilities
    public_metadata: dict[str, Any] = Field(default_factory=dict)
