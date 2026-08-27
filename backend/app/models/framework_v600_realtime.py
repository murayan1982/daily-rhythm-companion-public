from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

MAX_INPUT_TEXT_CHARS = 4096
MAX_SAFE_TEXT_CHARS = 240
MAX_EVENT_PAYLOAD_ITEMS = 8
MAX_EVENT_PAYLOAD_TEXT_CHARS = 120


class FrameworkV600AdapterStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    OPEN = "open"
    CLOSED = "closed"
    FAILED = "failed"


class FrameworkV600TurnOutcome(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    CLOSED = "closed"


class FrameworkV600RecoveryAction(str, Enum):
    NONE = "none"
    RETRY = "retry"
    REOPEN_REQUIRED = "reopen_required"
    CHECK_FRAMEWORK_INSTALL = "check_framework_install"
    CONTRACT_REVIEW_REQUIRED = "contract_review_required"


class FrameworkV600RealtimeEvent(BaseModel):
    schema_version: str = "drc.v4.framework-v600-realtime-event.1"
    event_type: str
    session_id: str
    turn_id: str | None = None
    generation_id: str | None = None
    sequence: int
    phase: str
    terminal: bool = False
    public_error_code: str | None = None
    safe_message: str = ""
    retryable: bool = False
    payload: dict[str, str | int | bool | None] = Field(default_factory=dict)

    @field_validator("event_type", "session_id", "turn_id", "generation_id", "phase", "public_error_code", "safe_message")
    @classmethod
    def _bounded_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return str(value)[:MAX_SAFE_TEXT_CHARS]

    @field_validator("sequence")
    @classmethod
    def _positive_sequence(cls, value: int) -> int:
        if value < 1:
            raise ValueError("event sequence must be >= 1")
        return value


class FrameworkV600RuntimeCapabilityState(BaseModel):
    configured: bool = False
    runtime_available: bool = False
    guarded: bool = True
    fake_runtime: bool = False
    real_runtime: bool = False
    unavailable_reason: str | None = None


class FrameworkV600TextGenerationCapability(BaseModel):
    runtime: FrameworkV600RuntimeCapabilityState
    streaming_supported: bool = False
    cooperative_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False


class FrameworkV600VoiceInputCapability(BaseModel):
    runtime: FrameworkV600RuntimeCapabilityState
    streaming_supported: bool = False
    cooperative_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False
    audio_chunk_input_supported: bool = False
    partial_transcript_supported: bool = False
    final_transcript_supported: bool = False
    input_abort_supported: bool = False
    backpressure_supported: bool = False


class FrameworkV600VoiceOutputCapability(BaseModel):
    runtime: FrameworkV600RuntimeCapabilityState
    streaming_audio_supported: bool = False
    generation_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False
    pending_flush_supported: bool = False
    active_audio_invalidation_supported: bool = False
    playback_ownership: str | None = None
    host_playback_stop_request_supported: bool = False
    host_playback_stop_ack_supported: bool = False


class FrameworkV600MotionCapability(BaseModel):
    runtime: FrameworkV600RuntimeCapabilityState
    request_cancel_supported: bool = False
    completion_event_supported: bool = False
    provider_neutral_intent_supported: bool = False
    stop_motion_supported: bool = False


class FrameworkV600CapabilitySnapshot(BaseModel):
    schema_version: str = "drc.v4.framework-v600-capability-snapshot.1"
    snapshot_scope: str = "session"
    snapshot_generation: int = 0
    session_id: str
    supports_text_chat: bool = False
    supports_voice_input: bool = False
    supports_voice_output: bool = False
    supports_motion: bool = False
    real_runtime_enabled: bool = False
    hard_cancel_supported: bool = False
    tts_queue_flush_supported: bool = False
    text_generation: str = "unknown"
    voice_input: str = "unknown"
    voice_output: str = "unknown"
    motion: str = "unknown"
    fake_runtime: str = "unknown"
    real_runtime: str = "unavailable"
    guarded: bool = True
    runtime_available: bool = False
    unavailable_reason: str | None = None
    cooperative_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False
    pending_flush_supported: bool = False
    host_playback_owned_by_drc: bool = True
    real_unified_runtime_available: bool = False
    unified_real_pipeline_claimed: bool = False
    text_generation_detail: FrameworkV600TextGenerationCapability | None = None
    voice_input_detail: FrameworkV600VoiceInputCapability | None = None
    voice_output_detail: FrameworkV600VoiceOutputCapability | None = None
    motion_detail: FrameworkV600MotionCapability | None = None


class FrameworkV600InterruptResult(BaseModel):
    schema_version: str = "drc.v4.framework-v600-interrupt-result.1"
    outcome: str
    scope: str
    reason: str = ""
    provider_cancel_supported: bool = False
    provider_cancel_applied: bool = False
    queue_flush_supported: bool = False
    queue_flush_applied: bool = False
    host_playback_stop_supported: bool = False
    host_playback_stop_applied: bool = False
    safe_message: str = ""
    retryable: bool = False


class FrameworkV600DiagnosticsSnapshot(BaseModel):
    schema_version: str = "drc.v4.framework-v600-diagnostics.1"
    session_id: str
    state: str = "unknown"
    phase: str = "unknown"
    is_closed: bool = False
    active_turn_id: str | None = None
    active_generation_id: str | None = None
    queue_depth: int = 0
    active_generation_count: int = 0
    last_terminal_event_type: str | None = None
    last_terminal_turn_id: str | None = None
    last_terminal_generation_id: str | None = None
    last_terminal_outcome: str | None = None
    last_terminal_public_error_code: str | None = None
    last_terminal_retryable: bool = False
    last_terminal_recovery_action: str | None = None
    last_safe_error_code: str | None = None
    stale_completion_count: int = 0
    duplicate_terminal_count: int = 0
    overflow_count: int = 0


class FrameworkV600OpenResult(BaseModel):
    schema_version: str = "drc.v4.framework-v600-open-result.1"
    status: FrameworkV600AdapterStatus
    available: bool = False
    session_id: str | None = None
    public_error_code: str | None = None
    safe_message: str = ""
    retryable: bool = False
    real_runtime_requested: bool = False
    real_runtime_enabled: bool = False
    runtime_executable: bool = False
    capabilities: FrameworkV600CapabilitySnapshot | None = None


class FrameworkV600TurnResult(BaseModel):
    schema_version: str = "drc.v4.framework-v600-turn-result.1"
    outcome: FrameworkV600TurnOutcome
    terminal: bool = False
    session_id: str | None = None
    turn_id: str | None = None
    generation_id: str | None = None
    public_error_code: str | None = None
    safe_message: str = ""
    retryable: bool = False
    recovery_action: FrameworkV600RecoveryAction = FrameworkV600RecoveryAction.NONE
    events: list[FrameworkV600RealtimeEvent] = Field(default_factory=list)
    capabilities: FrameworkV600CapabilitySnapshot | None = None
    interrupt: FrameworkV600InterruptResult | None = None
    diagnostics: FrameworkV600DiagnosticsSnapshot | None = None
