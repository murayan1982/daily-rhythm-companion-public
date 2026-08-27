from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import os
import sys
from types import MappingProxyType, SimpleNamespace
from typing import Any

from importlib import metadata

from app.models.framework_v600_realtime import MAX_INPUT_TEXT_CHARS
from app.services import framework_v600_realtime_session_adapter as adapter_module
from app.services.framework_v600_realtime_session_adapter import (
    CANONICAL_PROVIDER_FREE_EVENT_ORDER,
    FrameworkV600RealtimeSessionAdapter,
)

SESSION_ID = "fw_session_0123456789abcdef0123456789abcdef"
TURN_ID = "fw_turn_0123456789abcdef0123456789abcdef"
GENERATION_ID = "fw_generation_0123456789abcdef0123456789abcdef"
EXPECTED_PROVIDER_FREE_EVENT_ORDER = [
    "realtime.turn.started",
    "realtime.listening.started",
    "realtime.listening.completed",
    "realtime.transcript.final",
    "realtime.response.started",
    "realtime.response.completed",
    "realtime.synthesis.started",
    "realtime.synthesis.completed",
    "realtime.turn.completed",
]
VALID_INTERRUPT_SCOPES = {"current_turn", "llm_stream", "tts_queue", "voice_output", "motion", "all"}
VALID_INTERRUPT_REASONS = {
    "user_barge_in",
    "user_cancel",
    "new_turn_started",
    "session_closed",
    "timeout",
    "host_app_request",
    "provider_failure",
}


class RealtimeSessionConstructionStatus(str, Enum):
    MOCK_READY = "mock_ready"


class CapabilitySnapshotScope(str, Enum):
    SESSION = "session"


class RealtimeState(str, Enum):
    IDLE = "idle"
    RESPONDING = "responding"


class RealtimePhase(str, Enum):
    COMPLETED = "completed"
    RESPONSE = "response"


class InterruptOutcome(str, Enum):
    NO_ACTIVE_TURN = "no_active_turn"
    ACCEPTED = "accepted"


class TurnOutcome(str, Enum):
    COMPLETED = "completed"


class RecoveryAction(str, Enum):
    NONE = "none"


class SafeErrorCode(str, Enum):
    SAFE_CODE = "safe_code"


@dataclass
class FakeEvent:
    event_type: str
    sequence: int
    terminal: bool = False

    def as_v6_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "type": self.event_type,
            "session_id": SESSION_ID,
            "turn_id": TURN_ID,
            "generation_id": GENERATION_ID,
            "sequence": self.sequence,
            "phase": RealtimePhase.COMPLETED if self.terminal else self.event_type.rsplit(".", 1)[-1],
            "terminal": self.terminal,
            "payload": {
                "source": "provider_free",
                "transcript": "must-not-escape",
                "credential": "must-not-escape",
                "count": 1,
            },
        })


@dataclass(frozen=True)
class FakeConstructionResult:
    status: RealtimeSessionConstructionStatus = RealtimeSessionConstructionStatus.MOCK_READY
    real_runtime_requested: bool = False
    real_runtime_enabled: bool = False
    runtime_executable: bool = True
    session_id: str = SESSION_ID


@dataclass(frozen=True)
class FakeRuntimeCapabilityState:
    configured: bool = True
    runtime_available: bool = True
    guarded: bool = False
    fake_runtime: bool = True
    real_runtime: bool = False
    unavailable_reason: str | None = "provider_free"

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "configured": self.configured,
            "runtime_available": self.runtime_available,
            "guarded": self.guarded,
            "fake_runtime": self.fake_runtime,
            "real_runtime": self.real_runtime,
            "unavailable_reason": self.unavailable_reason,
        })


@dataclass(frozen=True)
class FakeTextGenerationCapability:
    runtime: FakeRuntimeCapabilityState = field(default_factory=FakeRuntimeCapabilityState)
    streaming_supported: bool = False
    cooperative_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "runtime": self.runtime,
            "streaming_supported": self.streaming_supported,
            "cooperative_cancel_supported": self.cooperative_cancel_supported,
            "provider_hard_cancel_supported": self.provider_hard_cancel_supported,
        })


@dataclass(frozen=True)
class FakeVoiceInputCapability:
    runtime: FakeRuntimeCapabilityState = field(default_factory=FakeRuntimeCapabilityState)
    audio_chunk_input_supported: bool = False
    partial_transcript_supported: bool = False
    final_transcript_supported: bool = True
    input_abort_supported: bool = False
    backpressure_supported: bool = False
    streaming_supported: bool = False
    cooperative_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "runtime": self.runtime,
            "audio_chunk_input_supported": self.audio_chunk_input_supported,
            "partial_transcript_supported": self.partial_transcript_supported,
            "final_transcript_supported": self.final_transcript_supported,
            "input_abort_supported": self.input_abort_supported,
            "backpressure_supported": self.backpressure_supported,
            "streaming_supported": self.streaming_supported,
            "cooperative_cancel_supported": self.cooperative_cancel_supported,
            "provider_hard_cancel_supported": self.provider_hard_cancel_supported,
        })


@dataclass(frozen=True)
class FakeVoiceOutputCapability:
    runtime: FakeRuntimeCapabilityState = field(
        default_factory=lambda: FakeRuntimeCapabilityState(unavailable_reason=None)
    )
    streaming_audio_supported: bool = False
    generation_cancel_supported: bool = False
    provider_hard_cancel_supported: bool = False
    pending_flush_supported: bool = False
    active_audio_invalidation_supported: bool = False
    playback_ownership: str = "host"
    host_playback_stop_request_supported: bool = True
    host_playback_stop_ack_supported: bool = True

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "runtime": self.runtime,
            "streaming_audio_supported": self.streaming_audio_supported,
            "generation_cancel_supported": self.generation_cancel_supported,
            "provider_hard_cancel_supported": self.provider_hard_cancel_supported,
            "pending_flush_supported": self.pending_flush_supported,
            "active_audio_invalidation_supported": self.active_audio_invalidation_supported,
            "playback_ownership": self.playback_ownership,
            "host_playback_stop_request_supported": self.host_playback_stop_request_supported,
            "host_playback_stop_ack_supported": self.host_playback_stop_ack_supported,
        })


@dataclass(frozen=True)
class FakeMotionCapability:
    runtime: FakeRuntimeCapabilityState = field(
        default_factory=lambda: FakeRuntimeCapabilityState(
            configured=False,
            runtime_available=False,
            guarded=False,
            fake_runtime=False,
            real_runtime=False,
            unavailable_reason="not_wired_to_realtime_session",
        )
    )
    request_cancel_supported: bool = False
    completion_event_supported: bool = False
    provider_neutral_intent_supported: bool = False
    stop_motion_supported: bool = False

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "runtime": self.runtime,
            "request_cancel_supported": self.request_cancel_supported,
            "completion_event_supported": self.completion_event_supported,
            "provider_neutral_intent_supported": self.provider_neutral_intent_supported,
            "stop_motion_supported": self.stop_motion_supported,
        })


@dataclass(frozen=True)
class FakeCapabilitySnapshot:
    snapshot_scope: CapabilitySnapshotScope = CapabilitySnapshotScope.SESSION
    snapshot_generation: int = 1
    session_id: str = SESSION_ID
    supports_text_chat: bool = True
    supports_voice_input: bool = True
    supports_voice_output: bool = True
    supports_motion: bool = False
    real_runtime_enabled: bool = False
    hard_cancel_supported: bool = False
    tts_queue_flush_supported: bool = False
    text_generation: FakeTextGenerationCapability = field(default_factory=FakeTextGenerationCapability)
    voice_input: FakeVoiceInputCapability = field(default_factory=FakeVoiceInputCapability)
    voice_output: FakeVoiceOutputCapability = field(default_factory=FakeVoiceOutputCapability)
    motion: FakeMotionCapability = field(default_factory=FakeMotionCapability)
    real_unified_runtime_available: bool = False
    unified_real_pipeline_claimed: bool = False

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "snapshot_scope": self.snapshot_scope,
            "snapshot_generation": self.snapshot_generation,
            "session_id": self.session_id,
            "supports_text_chat": self.supports_text_chat,
            "supports_voice_input": self.supports_voice_input,
            "supports_voice_output": self.supports_voice_output,
            "supports_motion": self.supports_motion,
            "real_runtime_enabled": self.real_runtime_enabled,
            "hard_cancel_supported": self.hard_cancel_supported,
            "tts_queue_flush_supported": self.tts_queue_flush_supported,
            "text_generation": self.text_generation,
            "voice_input": self.voice_input,
            "voice_output": self.voice_output,
            "motion": self.motion,
        })


@dataclass(frozen=True)
class FakeTerminalResult:
    event_type: str = "realtime.turn.completed"
    session_id: str = SESSION_ID
    turn_id: str = TURN_ID
    generation_id: str = GENERATION_ID
    outcome: TurnOutcome = TurnOutcome.COMPLETED
    public_error_code: SafeErrorCode | None = None
    retryable: bool = False
    recovery_action: RecoveryAction = RecoveryAction.NONE


@dataclass(frozen=True)
class FakeTurnResult:
    session_id: str = SESSION_ID
    turn_id: str = TURN_ID
    generation_id: str = GENERATION_ID
    outcome: TurnOutcome = TurnOutcome.COMPLETED
    is_terminal: bool = True
    public_error_code: SafeErrorCode | None = None
    retryable: bool = False
    recovery_action: RecoveryAction = RecoveryAction.NONE


@dataclass(frozen=True)
class FakeDiagnosticsSnapshot:
    session_id: str = SESSION_ID
    state: RealtimeState = RealtimeState.IDLE
    phase: RealtimePhase = RealtimePhase.COMPLETED
    is_closed: bool = False
    active_turn_id: str | None = None
    active_generation_id: str | None = None
    queue_depth: int = 0
    active_generation_count: int = 0
    last_terminal_result: FakeTerminalResult = FakeTerminalResult()
    last_safe_error_code: SafeErrorCode | None = None
    stale_completion_count: int = 0
    duplicate_terminal_count: int = 0
    overflow_count: int = 0
    transcript: str = "must-not-escape"
    audio: str = "must-not-escape"
    provider_payload: str = "must-not-escape"

    def as_dict(self) -> MappingProxyType:
        return MappingProxyType({
            "session_id": self.session_id,
            "state": self.state,
            "phase": self.phase,
            "is_closed": self.is_closed,
            "active_turn_id": self.active_turn_id,
            "active_generation_id": self.active_generation_id,
            "queue_depth": self.queue_depth,
            "active_generation_count": self.active_generation_count,
            "last_terminal_result": self.last_terminal_result,
            "last_safe_error_code": self.last_safe_error_code,
            "stale_completion_count": self.stale_completion_count,
            "duplicate_terminal_count": self.duplicate_terminal_count,
            "overflow_count": self.overflow_count,
            "transcript": self.transcript,
            "audio": self.audio,
            "provider_payload": self.provider_payload,
        })


class FakeInterruptRequest:
    def __init__(self, *, scope: str, reason: str) -> None:
        if scope not in VALID_INTERRUPT_SCOPES:
            raise ValueError("invalid interrupt scope")
        if reason not in VALID_INTERRUPT_REASONS:
            raise ValueError("invalid interrupt reason")
        self.scope = scope
        self.reason = reason


class FakeSession:
    def __init__(
        self,
        *,
        construction: Any | None = None,
        capabilities: Any | None = None,
        diagnostics: Any | None = None,
        events: list[FakeEvent] | None = None,
        result: dict[str, Any] | None = None,
    ) -> None:
        self.session_id = SESSION_ID
        self.construction_result = construction or FakeConstructionResult()
        self.capabilities = capabilities or FakeCapabilitySnapshot()
        self.diagnostics_snapshot = diagnostics or FakeDiagnosticsSnapshot()
        self.events = events or [
            FakeEvent(event_type, index, event_type == "realtime.turn.completed")
            for index, event_type in enumerate(CANONICAL_PROVIDER_FREE_EVENT_ORDER, start=1)
        ]
        self.result = result or FakeTurnResult()
        self.callbacks: list[Any] = []
        self.close_calls = 0
        self.run_turn_async_calls: list[str] = []
        self.interrupt_requests: list[Any] = []

    def on_event(self, callback: Any) -> None:
        self.callbacks.append(callback)

    async def run_turn_async(self, *, input_text: str) -> dict[str, Any]:
        self.run_turn_async_calls.append(input_text)
        for event in self.events:
            for callback in self.callbacks:
                callback(event)
        return self.result

    def interrupt(self, request: Any) -> dict[str, Any]:
        self.interrupt_requests.append(request)
        return {
            "outcome": InterruptOutcome.NO_ACTIVE_TURN,
            "scope": getattr(request, "scope", "current_turn"),
            "reason": getattr(request, "reason", "host_app_request"),
            "provider_cancel_supported": False,
            "provider_cancel_applied": False,
            "queue_flush_supported": True,
            "queue_flush_applied": True,
            "host_playback_stop_supported": False,
            "host_playback_stop_applied": False,
            "safe_message": "Cooperative interrupt observed.",
            "retryable": False,
        }

    def close(self) -> None:
        self.close_calls += 1


class FakeFrameworkRoot:
    __name__ = "framework"
    InterruptRequest = FakeInterruptRequest

    def __init__(self, session: FakeSession | None = None) -> None:
        self.session = session or FakeSession()
        self.create_calls = 0

    def create_realtime_session(self) -> FakeSession:
        self.create_calls += 1
        return self.session


def _adapter(root: FakeFrameworkRoot | None = None) -> FrameworkV600RealtimeSessionAdapter:
    return FrameworkV600RealtimeSessionAdapter(
        distribution_version=lambda name: "6.0.0",
        import_module=lambda name: root or FakeFrameworkRoot(),
    )


def test_adapter_module_import_alone_does_not_import_framework(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "framework", raising=False)
    assert "framework" not in sys.modules
    assert adapter_module.FRAMEWORK_DISTRIBUTION == "ai-character-framework"


def test_missing_distribution_returns_typed_unavailable_without_session() -> None:
    def missing(_: str) -> str:
        raise metadata.PackageNotFoundError

    imported: list[str] = []
    adapter = FrameworkV600RealtimeSessionAdapter(
        distribution_version=missing,
        import_module=lambda name: imported.append(name),
    )

    result = adapter.open()

    assert result.available is False
    assert result.public_error_code == "framework_distribution_missing"
    assert imported == []


def test_wrong_distribution_version_returns_typed_unavailable_without_session() -> None:
    imported: list[str] = []
    adapter = FrameworkV600RealtimeSessionAdapter(
        distribution_version=lambda name: "5.5.0",
        import_module=lambda name: imported.append(name),
    )

    result = adapter.open()

    assert result.available is False
    assert result.public_error_code == "framework_distribution_version_mismatch"
    assert imported == []


def test_correct_version_allows_lazy_root_import_and_only_root_framework_module() -> None:
    imported: list[str] = []
    root = FakeFrameworkRoot()
    adapter = FrameworkV600RealtimeSessionAdapter(
        distribution_version=lambda name: "6.0.0",
        import_module=lambda name: imported.append(name) or root,
    )

    result = adapter.open()

    assert result.available is True
    assert imported == ["framework"]
    assert root.create_calls == 1


def test_open_does_not_mutate_sys_path_cwd_or_use_project_root_behavior() -> None:
    before_path = list(sys.path)
    before_cwd = Path.cwd()
    root = FakeFrameworkRoot()

    result = _adapter(root).open()

    assert result.available is True
    assert sys.path == before_path
    assert Path.cwd() == before_cwd
    assert "FRAMEWORK_ROOT" not in os.environ


def test_default_construction_requires_mock_ready() -> None:
    session = FakeSession(construction=FakeConstructionResult(status="not_ready"))
    result = _adapter(FakeFrameworkRoot(session)).open()

    assert result.available is False
    assert result.public_error_code == "framework_contract_mismatch"


def test_construction_rejects_real_runtime_requested_enabled_and_non_executable() -> None:
    for key, value in (
        ("real_runtime_requested", True),
        ("real_runtime_enabled", True),
        ("runtime_executable", False),
    ):
        construction = FakeConstructionResult(**{key: value})
        result = _adapter(FakeFrameworkRoot(FakeSession(construction=construction))).open()
        assert result.available is False
        assert result.public_error_code == "framework_contract_mismatch"


def test_session_identity_capability_correlation_and_real_runtime_false() -> None:
    result = _adapter(FakeFrameworkRoot()).open()

    assert result.session_id == SESSION_ID
    assert result.capabilities is not None
    assert result.capabilities.session_id == SESSION_ID
    assert result.capabilities.real_runtime_enabled is False
    assert result.real_runtime_requested is False
    assert result.real_runtime_enabled is False
    assert result.runtime_executable is True


def test_capability_mismatch_fails_closed() -> None:
    session = FakeSession(capabilities=FakeCapabilitySnapshot(session_id="fw_session_ffffffffffffffffffffffffffffffff"))

    result = _adapter(FakeFrameworkRoot(session)).open()

    assert result.available is False
    assert result.public_error_code == "framework_contract_mismatch"


def test_async_run_turn_path_used_and_input_is_bounded() -> None:
    session = FakeSession()
    adapter = _adapter(FakeFrameworkRoot(session))
    assert adapter.open().available is True

    completed = asyncio.run(adapter.run_turn(input_text="hello"))
    blank = asyncio.run(adapter.run_turn(input_text=" "))
    oversized = asyncio.run(adapter.run_turn(input_text="x" * (MAX_INPUT_TEXT_CHARS + 1)))

    assert completed.outcome.value == "completed"
    assert session.run_turn_async_calls == ["hello"]
    assert blank.public_error_code == "invalid_input"
    assert oversized.public_error_code == "invalid_input"


def test_canonical_completed_event_order_exact_sequence_generation_and_terminal() -> None:
    adapter = _adapter(FakeFrameworkRoot())
    adapter.open()

    result = asyncio.run(adapter.run_turn(input_text="hello"))

    assert [event.event_type for event in result.events] == EXPECTED_PROVIDER_FREE_EVENT_ORDER
    assert [event.sequence for event in result.events] == list(range(1, 10))
    assert {event.generation_id for event in result.events} == {GENERATION_ID}
    assert [event.event_type for event in result.events if event.terminal] == ["realtime.turn.completed"]
    assert result.terminal is True
    assert result.outcome.value == "completed"
    assert result.session_id == SESSION_ID
    assert result.turn_id == TURN_ID
    assert result.generation_id == GENERATION_ID


def test_actual_shape_turn_result_uses_is_terminal_without_terminal_field() -> None:
    turn_result = FakeTurnResult()
    assert not hasattr(turn_result, "terminal")
    session = FakeSession(result=turn_result)
    adapter = _adapter(FakeFrameworkRoot(session))
    adapter.open()

    result = asyncio.run(adapter.run_turn(input_text="hello"))

    assert result.outcome.value == "completed"
    assert result.terminal is True
    assert result.session_id == SESSION_ID
    assert result.turn_id == TURN_ID
    assert result.generation_id == GENERATION_ID


def test_inconsistent_identity_fails_closed_without_silent_repair() -> None:
    session = FakeSession(result=FakeTurnResult(turn_id="fw_turn_ffffffffffffffffffffffffffffffff"))
    adapter = _adapter(FakeFrameworkRoot(session))
    adapter.open()

    result = asyncio.run(adapter.run_turn(input_text="hello"))

    assert result.outcome.value == "failed"
    assert result.public_error_code == "framework_contract_mismatch"


def test_event_order_sequence_duplicate_terminal_and_generation_mismatch_fail_closed() -> None:
    cases = [
        [FakeEvent("realtime.listening.started", 1), FakeEvent("realtime.turn.started", 2)],
        [FakeEvent(event, 1, event == "realtime.turn.completed") for event in CANONICAL_PROVIDER_FREE_EVENT_ORDER],
        [
            *[FakeEvent(event, i, False) for i, event in enumerate(CANONICAL_PROVIDER_FREE_EVENT_ORDER[:-1], start=1)],
            FakeEvent("realtime.turn.completed", 9, True),
            FakeEvent("realtime.turn.completed", 10, True),
        ],
    ]
    for events in cases:
        session = FakeSession(events=events)
        adapter = _adapter(FakeFrameworkRoot(session))
        adapter.open()
        result = asyncio.run(adapter.run_turn(input_text="hello"))
        assert result.outcome.value == "failed"
        assert result.public_error_code == "framework_contract_mismatch"


def test_safe_capability_projection_preserves_provider_neutral_truth() -> None:
    adapter = _adapter(FakeFrameworkRoot())
    result = adapter.open()
    capability = result.capabilities

    assert capability is not None
    assert capability.supports_text_chat is True
    assert capability.supports_voice_input is True
    assert capability.supports_voice_output is True
    assert capability.supports_motion is False
    assert capability.snapshot_scope == "session"
    assert capability.text_generation == "fake"
    assert capability.voice_input == "fake"
    assert capability.voice_output == "fake"
    assert capability.motion == "unavailable"
    assert capability.fake_runtime == "true"
    assert capability.real_runtime == "false"
    assert capability.cooperative_cancel_supported is False
    assert capability.provider_hard_cancel_supported is False
    assert capability.pending_flush_supported is False
    assert capability.host_playback_owned_by_drc is True
    assert capability.real_unified_runtime_available is False
    assert capability.unified_real_pipeline_claimed is False
    assert capability.text_generation_detail is not None
    assert capability.text_generation_detail.runtime.configured is True
    assert capability.text_generation_detail.runtime.guarded is False
    assert capability.text_generation_detail.runtime.fake_runtime is True
    assert capability.text_generation_detail.runtime.real_runtime is False
    assert capability.text_generation_detail.cooperative_cancel_supported is False
    assert capability.voice_input_detail is not None
    assert capability.voice_input_detail.final_transcript_supported is True
    assert capability.voice_input_detail.audio_chunk_input_supported is False
    assert capability.voice_output_detail is not None
    assert capability.voice_output_detail.pending_flush_supported is False
    assert capability.voice_output_detail.playback_ownership == "host"
    assert capability.voice_output_detail.host_playback_stop_request_supported is True
    assert capability.voice_output_detail.host_playback_stop_ack_supported is True
    assert capability.motion_detail is not None
    assert capability.motion_detail.runtime.configured is False
    assert capability.motion_detail.runtime.runtime_available is False
    assert capability.motion_detail.runtime.fake_runtime is False
    assert capability.motion_detail.runtime.unavailable_reason == "not_wired_to_realtime_session"
    assert capability.motion_detail.provider_neutral_intent_supported is False


def test_nested_capability_runtime_is_not_stringified_or_read_from_wrong_level() -> None:
    capability_shape = FakeCapabilitySnapshot(
        text_generation=FakeTextGenerationCapability(
            runtime=FakeRuntimeCapabilityState(
                configured=True,
                runtime_available=True,
                fake_runtime=False,
                real_runtime=False,
                unavailable_reason="text_runtime_specific",
            ),
            cooperative_cancel_supported=True,
        ),
        voice_output=FakeVoiceOutputCapability(
            runtime=FakeRuntimeCapabilityState(
                configured=True,
                runtime_available=True,
                fake_runtime=True,
                real_runtime=False,
                unavailable_reason=None,
            ),
            pending_flush_supported=True,
            playback_ownership="host",
            host_playback_stop_request_supported=True,
            host_playback_stop_ack_supported=True,
        ),
    )
    result = _adapter(FakeFrameworkRoot(FakeSession(capabilities=capability_shape))).open()
    capability = result.capabilities

    assert capability is not None
    assert capability.text_generation_detail is not None
    assert capability.text_generation_detail.runtime.unavailable_reason == "text_runtime_specific"
    assert capability.text_generation_detail.runtime.fake_runtime is False
    assert capability.voice_output_detail is not None
    assert capability.voice_output_detail.runtime.fake_runtime is True
    assert capability.pending_flush_supported is True
    assert capability.voice_output_detail.pending_flush_supported is True
    assert capability.voice_output_detail.playback_ownership == "host"
    assert "FakeRuntimeCapabilityState" not in capability.model_dump_json()


def test_typed_interrupt_projection_does_not_infer_provider_hard_cancel() -> None:
    session = FakeSession()
    adapter = _adapter(FakeFrameworkRoot(session))
    adapter.open()

    result = adapter.interrupt()

    assert result.outcome == "no_active_turn"
    assert result.scope == "current_turn"
    assert result.reason == "host_app_request"
    assert result.provider_cancel_supported is False
    assert result.provider_cancel_applied is False
    assert result.queue_flush_supported is True
    assert result.queue_flush_applied is True
    assert session.interrupt_requests[0].scope == "current_turn"


def test_interrupt_uses_fw_v6_valid_scope_and_reason_not_old_defaults() -> None:
    session = FakeSession()
    adapter = _adapter(FakeFrameworkRoot(session))
    adapter.open()

    old = adapter.interrupt(scope="turn", reason="operator_requested")
    current = adapter.interrupt(scope="current_turn", reason="host_app_request")

    assert old.outcome == "failed"
    assert len(session.interrupt_requests) == 1
    assert current.scope == "current_turn"
    assert current.reason == "host_app_request"
    assert current.outcome == "no_active_turn"


def test_diagnostics_projection_exact_and_nonzero_counters_preserved() -> None:
    diagnostics = FakeDiagnosticsSnapshot(
        state=RealtimeState.RESPONDING,
        phase=RealtimePhase.RESPONSE,
        active_turn_id=TURN_ID,
        active_generation_id=GENERATION_ID,
        queue_depth=2,
        active_generation_count=1,
        last_safe_error_code=SafeErrorCode.SAFE_CODE,
        stale_completion_count=3,
        duplicate_terminal_count=4,
        overflow_count=5,
    )
    adapter = _adapter(FakeFrameworkRoot(FakeSession(diagnostics=diagnostics)))
    adapter.open()

    projected = adapter.diagnostics_snapshot()

    assert projected is not None
    assert projected.session_id == SESSION_ID
    assert projected.state == "responding"
    assert projected.phase == "response"
    assert projected.queue_depth == 2
    assert projected.last_terminal_outcome == "completed"
    assert projected.last_terminal_recovery_action == "none"
    assert projected.last_safe_error_code == "safe_code"
    assert projected.stale_completion_count == 3
    assert projected.duplicate_terminal_count == 4
    assert projected.overflow_count == 5
    assert "must-not-escape" not in projected.model_dump_json()


def test_nonzero_diagnostics_counters_fail_completed_turn_contract() -> None:
    session = FakeSession(diagnostics=FakeDiagnosticsSnapshot(stale_completion_count=1))
    adapter = _adapter(FakeFrameworkRoot(session))
    adapter.open()

    result = asyncio.run(adapter.run_turn(input_text="hello"))

    assert result.outcome.value == "failed"
    assert result.public_error_code == "framework_contract_mismatch"


def test_close_is_idempotent_and_use_after_close_fails_safely() -> None:
    session = FakeSession()
    adapter = _adapter(FakeFrameworkRoot(session))
    adapter.open()

    closed_once = adapter.close()
    closed_twice = adapter.close()
    result = asyncio.run(adapter.run_turn(input_text="hello"))

    assert closed_once.status.value == "closed"
    assert closed_twice.status.value == "closed"
    assert session.close_calls == 1
    assert result.public_error_code == "adapter_not_open"


def test_static_protected_v3_files_are_not_part_of_v4_2_surface() -> None:
    protected = {
        "backend/app/models/realtime.py",
        "backend/app/services/framework_realtime_normalizer.py",
        "backend/app/services/framework_realtime_text_stream_adapter.py",
        "backend/app/services/framework_mock_motion_session_adapter.py",
    }
    assert protected.isdisjoint(adapter_module.__file__.replace("\\", "/").splitlines())


def test_production_adapter_source_has_no_forbidden_framework_workarounds() -> None:
    source = Path(adapter_module.__file__).read_text(encoding="utf-8")
    forbidden = (
        "framework.realtime",
        "framework.realtime_session",
        "framework.identity",
        "framework.session_diagnostics",
        "sys.path",
        "sys.modules",
        "invalidate_caches",
        "os.chdir",
        "FRAMEWORK_ROOT",
        "framework_project_root",
        "inspect.signature",
        "dir(",
        "real_runtime_enabled=True",
        "voice_input_stage",
        "text_generation_stage",
        "voice_output_stage",
        "motion_stage",
    )
    for marker in forbidden:
        assert marker not in source
