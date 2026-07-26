"""Mock-safe tests for the DRC-owned Framework realtime normalizer."""

from __future__ import annotations

from enum import Enum
from types import SimpleNamespace

from app.models.realtime import RealtimeEventType, RealtimeState
from app.services.framework_realtime_normalizer import (
    FrameworkRealtimeContractNormalizer,
)


class _Value(str, Enum):
    TURN_STARTED = "realtime.turn.started"
    LISTENING = "listening"
    IDLE = "idle"
    NONE = "none"


def _v520_realtime_info() -> SimpleNamespace:
    return SimpleNamespace(
        api_version="5.2.0",
        session_type="realtime",
        session_id="session-001",
        state=_Value.IDLE,
        supports_run_turn=True,
        supports_interrupt=True,
        supports_output_flush=True,
        supports_barge_in_policy=True,
        real_runtime_enabled=False,
        hard_cancel_supported=False,
        tts_queue_flush_supported=False,
        public_metadata={"boundary": "realtime"},
    )


def test_normalize_realtime_event_object() -> None:
    normalizer = FrameworkRealtimeContractNormalizer()
    event = SimpleNamespace(
        type=_Value.TURN_STARTED,
        state=_Value.LISTENING,
        previous_state=_Value.IDLE,
        turn_id="turn-001",
        session_id="session-001",
        boundary="realtime",
        public_error_code=_Value.NONE,
        safe_message="",
        retryable=False,
        public_metadata={"stage": "voice_input"},
    )

    normalized = normalizer.normalize_event(event)

    assert normalized.event_type is RealtimeEventType.TURN_STARTED
    assert normalized.source_event_type == "realtime.turn.started"
    assert normalized.state is RealtimeState.LISTENING
    assert normalized.previous_state is RealtimeState.IDLE
    assert normalized.turn_id == "turn-001"
    assert normalized.session_id == "session-001"
    assert normalized.public_error_code == "none"
    assert normalized.public_metadata == {"stage": "voice_input"}


def test_normalize_mapping_event_infers_state_and_preserves_unknown_type() -> None:
    normalizer = FrameworkRealtimeContractNormalizer()

    completed = normalizer.normalize_event(
        {
            "type": "realtime.turn.completed",
            "payload": {"turn_id": "turn-002", "session_id": "session-002"},
        }
    )
    unknown = normalizer.normalize_event({"type": "future.event.kind"})

    assert completed.event_type is RealtimeEventType.TURN_COMPLETED
    assert completed.state is RealtimeState.COMPLETED
    assert completed.turn_id == "turn-002"
    assert completed.session_id == "session-002"
    assert unknown.event_type is RealtimeEventType.UNKNOWN
    assert unknown.source_event_type == "future.event.kind"
    assert unknown.state is RealtimeState.UNKNOWN


def test_session_specific_v520_info_overrides_stale_global_snapshot() -> None:
    normalizer = FrameworkRealtimeContractNormalizer()
    stale_global = SimpleNamespace(
        voice_input=SimpleNamespace(
            supported=False,
            configured=False,
            available=False,
            reason_code="public_boundary_missing",
            safe_message="missing",
        ),
        realtime=SimpleNamespace(
            supported=False,
            configured=False,
            available=False,
            reason_code="public_boundary_missing",
            safe_message="missing",
        ),
        motion=SimpleNamespace(
            supported=False,
            configured=False,
            available=False,
            reason_code="public_boundary_missing",
            safe_message="missing",
        ),
    )
    voice_info = SimpleNamespace(
        session_type="voice_input",
        supports_listen_result=True,
        supports_real_stt=False,
        real_stt_enabled=False,
        provider_status="disabled",
        safe_message="Real STT is disabled.",
    )
    motion_info = SimpleNamespace(
        session_type="motion",
        supports_apply_motion=True,
        real_adapter_supported=False,
        real_adapter_enabled=False,
        adapter_status="mock_available",
    )

    capabilities = normalizer.normalize_capabilities(
        global_capabilities=stale_global,
        voice_input_info=voice_info,
        realtime_info=_v520_realtime_info(),
        motion_info=motion_info,
    )

    assert capabilities.voice_input.public_contract_released is True
    assert capabilities.voice_input.real_runtime_supported is False
    assert capabilities.realtime.public_contract_released is True
    assert capabilities.realtime.real_runtime_available is False
    assert capabilities.hard_cancel.public_contract_released is True
    assert capabilities.hard_cancel.real_runtime_supported is False
    assert capabilities.tts_queue_flush.public_contract_released is True
    assert capabilities.tts_queue_flush.real_runtime_supported is False
    assert capabilities.barge_in.public_contract_released is True
    assert capabilities.barge_in.real_runtime_supported is False
    assert capabilities.motion.public_contract_released is True
    assert capabilities.motion.real_runtime_supported is False


def test_normalize_session_builds_drc_owned_snapshot() -> None:
    normalizer = FrameworkRealtimeContractNormalizer()
    info = _v520_realtime_info()
    capabilities = normalizer.normalize_capabilities(realtime_info=info)

    snapshot = normalizer.normalize_session(info, capabilities=capabilities)

    assert snapshot.session_id == "session-001"
    assert snapshot.session_type == "realtime"
    assert snapshot.state is RealtimeState.IDLE
    assert snapshot.is_closed is False
    assert snapshot.real_runtime_enabled is False
    assert snapshot.capabilities.realtime.mock_contract_available is True


def test_public_metadata_redacts_sensitive_keys_and_opaque_objects() -> None:
    normalizer = FrameworkRealtimeContractNormalizer()
    event = {
        "type": "realtime.turn.failed",
        "state": "failed",
        "public_metadata": {
            "api_key": "should-not-leak",
            "nested": {"authorization": "Bearer private", "safe": "ok"},
            "opaque": object(),
        },
    }

    normalized = normalizer.normalize_event(event)

    assert normalized.public_metadata["api_key"] == "<redacted>"
    assert normalized.public_metadata["nested"]["authorization"] == "<redacted>"
    assert normalized.public_metadata["nested"]["safe"] == "ok"
    assert normalized.public_metadata["opaque"] == "<object>"


def test_normalizer_module_does_not_require_framework_package() -> None:
    normalizer = FrameworkRealtimeContractNormalizer()

    capabilities = normalizer.normalize_capabilities()

    assert capabilities.voice_input.public_contract_released is False
    assert capabilities.realtime.public_contract_released is False
    assert capabilities.motion.public_contract_released is False
