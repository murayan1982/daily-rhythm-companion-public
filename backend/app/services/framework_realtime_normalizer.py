from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any

from app.models.realtime import (
    RealtimeCapabilities,
    RealtimeCapabilityStatus,
    RealtimeEvent,
    RealtimeEventType,
    RealtimeSessionSnapshot,
    RealtimeState,
)


_SECRET_KEY_FRAGMENTS = (
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "password",
    "secret",
    "token",
    "private_path",
    "local_path",
    "raw_payload",
    "raw_audio",
)

_EVENT_TYPES: dict[str, RealtimeEventType] = {
    "realtime.session.created": RealtimeEventType.SESSION_CREATED,
    "realtime.turn.started": RealtimeEventType.TURN_STARTED,
    "realtime.voice_input.started": RealtimeEventType.VOICE_INPUT_STARTED,
    "realtime.voice_input.completed": RealtimeEventType.VOICE_INPUT_COMPLETED,
    "realtime.text_chat.started": RealtimeEventType.TEXT_CHAT_STARTED,
    "realtime.text_chat.completed": RealtimeEventType.TEXT_CHAT_COMPLETED,
    "realtime.voice_output.started": RealtimeEventType.VOICE_OUTPUT_STARTED,
    "realtime.voice_output.completed": RealtimeEventType.VOICE_OUTPUT_COMPLETED,
    "realtime.motion.started": RealtimeEventType.MOTION_STARTED,
    "realtime.motion.completed": RealtimeEventType.MOTION_COMPLETED,
    "realtime.turn.completed": RealtimeEventType.TURN_COMPLETED,
    "realtime.turn.interrupted": RealtimeEventType.TURN_INTERRUPTED,
    "realtime.turn.failed": RealtimeEventType.TURN_FAILED,
    "realtime.session.closed": RealtimeEventType.SESSION_CLOSED,
    "realtime.interrupt.requested": RealtimeEventType.INTERRUPT_REQUESTED,
    "realtime.interrupt.accepted": RealtimeEventType.INTERRUPT_ACCEPTED,
    "realtime.interrupt.completed": RealtimeEventType.INTERRUPT_COMPLETED,
    "realtime.interrupt.unsupported": RealtimeEventType.INTERRUPT_UNSUPPORTED,
    "realtime.output.flush.requested": RealtimeEventType.OUTPUT_FLUSH_REQUESTED,
    "realtime.output.flush.completed": RealtimeEventType.OUTPUT_FLUSH_COMPLETED,
    "realtime.output.flush.unsupported": RealtimeEventType.OUTPUT_FLUSH_UNSUPPORTED,
    "realtime.barge_in.detected": RealtimeEventType.BARGE_IN_DETECTED,
    "realtime.barge_in.accepted": RealtimeEventType.BARGE_IN_ACCEPTED,
    "realtime.barge_in.rejected": RealtimeEventType.BARGE_IN_REJECTED,
}

_STATE_VALUES = {state.value: state for state in RealtimeState}

_INFERRED_STATES: dict[RealtimeEventType, RealtimeState] = {
    RealtimeEventType.SESSION_CREATED: RealtimeState.IDLE,
    RealtimeEventType.TURN_STARTED: RealtimeState.LISTENING,
    RealtimeEventType.VOICE_INPUT_STARTED: RealtimeState.LISTENING,
    RealtimeEventType.VOICE_INPUT_COMPLETED: RealtimeState.TRANSCRIBING,
    RealtimeEventType.TEXT_CHAT_STARTED: RealtimeState.THINKING,
    RealtimeEventType.TEXT_CHAT_COMPLETED: RealtimeState.RESPONDING,
    RealtimeEventType.VOICE_OUTPUT_STARTED: RealtimeState.SPEAKING,
    RealtimeEventType.VOICE_OUTPUT_COMPLETED: RealtimeState.COMPLETED,
    RealtimeEventType.MOTION_STARTED: RealtimeState.MOTION,
    RealtimeEventType.MOTION_COMPLETED: RealtimeState.COMPLETED,
    RealtimeEventType.TURN_COMPLETED: RealtimeState.COMPLETED,
    RealtimeEventType.TURN_INTERRUPTED: RealtimeState.INTERRUPTED,
    RealtimeEventType.TURN_FAILED: RealtimeState.FAILED,
    RealtimeEventType.SESSION_CLOSED: RealtimeState.CLOSED,
    RealtimeEventType.INTERRUPT_COMPLETED: RealtimeState.INTERRUPTED,
}


class FrameworkRealtimeContractNormalizer:
    """Normalize FW v5.2.0 public objects without importing Framework.

    Session-specific v5.2.0 metadata takes precedence over the older global
    capability snapshot because the v5.2.0 tag still reports the new public
    boundaries as missing through ``get_capabilities()``.
    """

    def normalize_event(self, event: object) -> RealtimeEvent:
        source_event_type = _text(_read(event, "type")) or "unknown"
        event_type = _EVENT_TYPES.get(source_event_type, RealtimeEventType.UNKNOWN)

        payload = _mapping(_read(event, "payload"))
        public_metadata = {
            **_mapping(_read(event, "public_metadata")),
            **payload,
        }

        source_state = _text(_read(event, "state"))
        if not source_state:
            source_state = _text(public_metadata.get("state"))
        state = _normalize_state(source_state)
        if state is RealtimeState.UNKNOWN:
            state = _INFERRED_STATES.get(event_type, RealtimeState.UNKNOWN)

        source_previous_state = _text(_read(event, "previous_state")) or None
        previous_state = (
            _normalize_state(source_previous_state)
            if source_previous_state is not None
            else None
        )

        turn_id = _optional_text(_read(event, "turn_id")) or _optional_text(
            public_metadata.get("turn_id")
        )
        session_id = _optional_text(_read(event, "session_id")) or _optional_text(
            public_metadata.get("session_id")
        )

        return RealtimeEvent(
            event_type=event_type,
            source_event_type=source_event_type,
            state=state,
            source_state=source_state or state.value,
            previous_state=previous_state,
            source_previous_state=source_previous_state,
            turn_id=turn_id,
            session_id=session_id,
            boundary=_text(_read(event, "boundary")) or "realtime",
            public_error_code=_optional_text(_read(event, "public_error_code")),
            safe_message=_text(_read(event, "safe_message")),
            retryable=_bool(_read(event, "retryable")),
            public_metadata=_sanitize_mapping(public_metadata),
        )

    def normalize_capabilities(
        self,
        *,
        global_capabilities: object | None = None,
        voice_input_info: object | None = None,
        realtime_info: object | None = None,
        motion_info: object | None = None,
    ) -> RealtimeCapabilities:
        voice_input = self._voice_input_capability(
            voice_input_info,
            _read(global_capabilities, "voice_input"),
        )
        realtime = self._realtime_capability(
            realtime_info,
            _read(global_capabilities, "realtime"),
        )
        hard_cancel = self._realtime_feature_capability(
            name="hard_cancel",
            realtime_info=realtime_info,
            contract_flag="supports_interrupt",
            runtime_flag="hard_cancel_supported",
            reason_code="hard_cancel_not_implemented",
            safe_message="Framework hard cancellation is not implemented.",
        )
        tts_queue_flush = self._realtime_feature_capability(
            name="tts_queue_flush",
            realtime_info=realtime_info,
            contract_flag="supports_output_flush",
            runtime_flag="tts_queue_flush_supported",
            reason_code="tts_queue_flush_not_implemented",
            safe_message="Framework real TTS queue flush is not implemented.",
        )
        barge_in = self._realtime_feature_capability(
            name="barge_in",
            realtime_info=realtime_info,
            contract_flag="supports_barge_in_policy",
            runtime_flag="barge_in_runtime_supported",
            reason_code="barge_in_detection_not_implemented",
            safe_message="Framework barge-in policy exists, but real audio detection is not implemented.",
        )
        motion = self._motion_capability(
            motion_info,
            _read(global_capabilities, "motion"),
        )
        return RealtimeCapabilities(
            voice_input=voice_input,
            realtime=realtime,
            hard_cancel=hard_cancel,
            tts_queue_flush=tts_queue_flush,
            barge_in=barge_in,
            motion=motion,
        )

    def normalize_session(
        self,
        session_info: object,
        *,
        capabilities: RealtimeCapabilities | None = None,
    ) -> RealtimeSessionSnapshot:
        source_state = _text(_read(session_info, "state")) or "unknown"
        state = _normalize_state(source_state)
        closed = _bool(_read(session_info, "is_closed")) or state is RealtimeState.CLOSED
        normalized_capabilities = capabilities or self.normalize_capabilities(
            realtime_info=session_info
        )

        return RealtimeSessionSnapshot(
            session_id=_optional_text(_read(session_info, "session_id")),
            session_type=_text(_read(session_info, "session_type")) or "realtime",
            state=state,
            source_state=source_state,
            active_turn_id=_optional_text(_read(session_info, "active_turn_id")),
            is_closed=closed,
            real_runtime_enabled=_bool(_read(session_info, "real_runtime_enabled")),
            capabilities=normalized_capabilities,
            public_metadata=_sanitize_mapping(
                _mapping(_read(session_info, "public_metadata"))
            ),
        )

    def _voice_input_capability(
        self,
        info: object | None,
        global_status: object | None,
    ) -> RealtimeCapabilityStatus:
        if info is not None:
            contract = _bool(_read(info, "supports_listen_result")) or (
                _text(_read(info, "session_type")) == "voice_input"
            )
            real_supported = _bool(_read(info, "supports_real_stt"))
            real_configured = _bool(_read(info, "real_stt_enabled"))
            provider_status = _text(_read(info, "provider_status")) or "unknown"
            return RealtimeCapabilityStatus(
                name="voice_input",
                public_contract_released=contract,
                mock_contract_available=contract,
                real_runtime_supported=real_supported,
                real_runtime_configured=real_configured,
                real_runtime_available=real_supported and real_configured,
                source="voice_input_session_info",
                reason_code=provider_status,
                safe_message=_text(_read(info, "safe_message")),
            )
        return _from_global_status("voice_input", global_status)

    def _realtime_capability(
        self,
        info: object | None,
        global_status: object | None,
    ) -> RealtimeCapabilityStatus:
        if info is not None:
            contract = _bool(_read(info, "supports_run_turn")) or (
                _text(_read(info, "session_type")) == "realtime"
            )
            real_enabled = _bool(_read(info, "real_runtime_enabled"))
            return RealtimeCapabilityStatus(
                name="realtime",
                public_contract_released=contract,
                mock_contract_available=contract,
                real_runtime_supported=real_enabled,
                real_runtime_configured=real_enabled,
                real_runtime_available=False,
                source="realtime_session_info",
                reason_code=(
                    "real_runtime_not_implemented"
                    if not real_enabled
                    else "real_runtime_not_verified"
                ),
                safe_message=(
                    "Framework realtime public lifecycle is available in mock-safe mode; real orchestration is not implemented."
                ),
            )
        return _from_global_status("realtime", global_status)

    def _realtime_feature_capability(
        self,
        *,
        name: str,
        realtime_info: object | None,
        contract_flag: str,
        runtime_flag: str,
        reason_code: str,
        safe_message: str,
    ) -> RealtimeCapabilityStatus:
        contract = _bool(_read(realtime_info, contract_flag))
        real_supported = _bool(_read(realtime_info, runtime_flag))
        return RealtimeCapabilityStatus(
            name=name,
            public_contract_released=contract,
            mock_contract_available=contract,
            real_runtime_supported=real_supported,
            real_runtime_configured=False,
            real_runtime_available=False,
            source="realtime_session_info" if realtime_info is not None else "default",
            reason_code=("real_runtime_supported" if real_supported else reason_code),
            safe_message=safe_message,
        )

    def _motion_capability(
        self,
        info: object | None,
        global_status: object | None,
    ) -> RealtimeCapabilityStatus:
        if info is not None:
            contract = _bool(_read(info, "supports_apply_motion")) or (
                _text(_read(info, "session_type")) == "motion"
            )
            real_supported = _bool(_read(info, "real_adapter_supported"))
            real_configured = _bool(_read(info, "real_adapter_enabled"))
            adapter_status = _text(_read(info, "adapter_status")) or "unknown"
            return RealtimeCapabilityStatus(
                name="motion",
                public_contract_released=contract,
                mock_contract_available=contract,
                real_runtime_supported=real_supported,
                real_runtime_configured=real_configured,
                real_runtime_available=real_supported and real_configured,
                source="motion_session_info",
                reason_code=adapter_status,
                safe_message=(
                    "Framework mock motion contract is available; real Live2D/VTS execution is not implemented."
                ),
            )
        return _from_global_status("motion", global_status)


def _from_global_status(name: str, status: object | None) -> RealtimeCapabilityStatus:
    supported = _bool(_read(status, "supported"))
    configured = _bool(_read(status, "configured"))
    available = _bool(_read(status, "available")) and not _bool(
        _read(status, "blocked")
    )
    return RealtimeCapabilityStatus(
        name=name,
        public_contract_released=supported,
        mock_contract_available=supported,
        real_runtime_supported=available,
        real_runtime_configured=configured,
        real_runtime_available=available,
        source="global_capability_snapshot" if status is not None else "default",
        reason_code=_optional_text(_read(status, "reason_code")),
        safe_message=_text(_read(status, "safe_message")),
    )


def _read(value: object | None, name: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _mapping(value: object | None) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items()}
    return {}


def _text(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, Enum):
        return str(value.value)
    return str(value)


def _optional_text(value: object | None) -> str | None:
    text = _text(value).strip()
    return text or None


def _bool(value: object | None) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "available"}
    return bool(value)


def _normalize_state(value: str | None) -> RealtimeState:
    normalized = (value or "").strip().lower()
    return _STATE_VALUES.get(normalized, RealtimeState.UNKNOWN)


def _sanitize_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): _sanitize_value(value, key=str(key))
        for key, value in values.items()
    }


def _sanitize_value(value: Any, *, key: str = "") -> Any:
    lowered_key = key.lower()
    if any(fragment in lowered_key for fragment in _SECRET_KEY_FRAGMENTS):
        return "<redacted>"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return _sanitize_mapping(value)
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_value(item) for item in value]
    return f"<{type(value).__name__}>"
