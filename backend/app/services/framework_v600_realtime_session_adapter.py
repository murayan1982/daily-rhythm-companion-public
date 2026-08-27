from __future__ import annotations

import importlib
from importlib import metadata
import re
from collections.abc import Callable, Mapping
from typing import Any

from app.models.framework_v600_realtime import (
    MAX_EVENT_PAYLOAD_ITEMS,
    MAX_EVENT_PAYLOAD_TEXT_CHARS,
    MAX_INPUT_TEXT_CHARS,
    MAX_SAFE_TEXT_CHARS,
    FrameworkV600AdapterStatus,
    FrameworkV600CapabilitySnapshot,
    FrameworkV600DiagnosticsSnapshot,
    FrameworkV600InterruptResult,
    FrameworkV600MotionCapability,
    FrameworkV600OpenResult,
    FrameworkV600RealtimeEvent,
    FrameworkV600RecoveryAction,
    FrameworkV600RuntimeCapabilityState,
    FrameworkV600TextGenerationCapability,
    FrameworkV600TurnOutcome,
    FrameworkV600TurnResult,
    FrameworkV600VoiceInputCapability,
    FrameworkV600VoiceOutputCapability,
)

FRAMEWORK_DISTRIBUTION = "ai-character-framework"
FRAMEWORK_REQUIRED_VERSION = "6.0.0"
CANONICAL_PROVIDER_FREE_EVENT_ORDER = (
    "realtime.turn.started",
    "realtime.listening.started",
    "realtime.listening.completed",
    "realtime.transcript.final",
    "realtime.response.started",
    "realtime.response.completed",
    "realtime.synthesis.started",
    "realtime.synthesis.completed",
    "realtime.turn.completed",
)
SESSION_ID_PATTERN = re.compile(r"^fw_session_[0-9a-f]{32}$")
TURN_ID_PATTERN = re.compile(r"^fw_turn_[0-9a-f]{32}$")
GENERATION_ID_PATTERN = re.compile(r"^fw_generation_[0-9a-f]{32}$")


class FrameworkV600RealtimeSessionAdapter:
    """Provider-free FW v6 RealtimeSession adapter using only root framework."""

    def __init__(
        self,
        *,
        distribution_version: Callable[[str], str] | None = None,
        import_module: Callable[[str], Any] | None = None,
    ) -> None:
        self._distribution_version = distribution_version or metadata.version
        self._import_module = import_module or importlib.import_module
        self._framework: Any | None = None
        self._session: Any | None = None
        self._events: list[FrameworkV600RealtimeEvent] = []
        self._closed = False
        self._last_diagnostics: FrameworkV600DiagnosticsSnapshot | None = None

    @property
    def is_open(self) -> bool:
        return self._session is not None and not self._closed

    def open(self) -> FrameworkV600OpenResult:
        if self._closed:
            return self._unavailable(
                "adapter_closed",
                "The FW v6 realtime adapter is closed.",
                retryable=False,
            )
        version_result = self._verify_distribution()
        if version_result is not None:
            return version_result
        try:
            framework = self._import_module("framework")
            create_session = getattr(framework, "create_realtime_session", None)
            if not callable(create_session):
                return self._unavailable(
                    "framework_realtime_unavailable",
                    "FW v6 RealtimeSession is unavailable.",
                    retryable=True,
                )
            session = create_session()
        except Exception:
            return self._unavailable(
                "framework_realtime_unavailable",
                "FW v6 RealtimeSession is unavailable.",
                retryable=True,
            )

        result = self._validate_opened_session(session)
        if result.available:
            self._framework = framework
            self._session = session
            self._events.clear()
            self._register_event_callback(session)
        return result

    async def run_turn(self, *, input_text: str) -> FrameworkV600TurnResult:
        invalid = self._validate_input(input_text)
        if invalid is not None:
            return invalid
        session = self._session
        if session is None or self._closed:
            return self._failed_turn(
                "adapter_not_open",
                "Open the FW v6 realtime adapter before running a turn.",
                recovery_action=FrameworkV600RecoveryAction.REOPEN_REQUIRED,
            )
        run_turn_async = getattr(session, "run_turn_async", None)
        if not callable(run_turn_async):
            return self._failed_turn(
                "framework_contract_mismatch",
                "FW v6 async turn execution is unavailable.",
                recovery_action=FrameworkV600RecoveryAction.CONTRACT_REVIEW_REQUIRED,
            )
        self._events.clear()
        try:
            raw_result = await run_turn_async(input_text=input_text)
        except Exception:
            return self._failed_turn(
                "framework_turn_failed",
                "FW v6 provider-free turn failed safely.",
                retryable=True,
            )
        return self._validate_turn_result(raw_result)

    def interrupt(
        self,
        *,
        scope: str = "current_turn",
        reason: str = "host_app_request",
    ) -> FrameworkV600InterruptResult:
        session = self._session
        framework = self._framework
        if session is None or framework is None or self._closed:
            return FrameworkV600InterruptResult(
                outcome="unavailable",
                scope=scope,
                reason=_bounded(reason),
                safe_message="The FW v6 realtime adapter is not open.",
                retryable=False,
            )
        try:
            request_type = getattr(framework, "InterruptRequest", None)
            request = request_type(scope=scope, reason=reason) if callable(request_type) else None
            raw = session.interrupt(request) if request is not None else session.interrupt()
        except Exception:
            return FrameworkV600InterruptResult(
                outcome="failed",
                scope=scope,
                reason=_bounded(reason),
                safe_message="FW v6 interrupt failed safely.",
                retryable=True,
            )
        return _project_interrupt(raw, fallback_scope=scope, fallback_reason=reason)

    def diagnostics_snapshot(self) -> FrameworkV600DiagnosticsSnapshot | None:
        session = self._session
        if session is None:
            return self._last_diagnostics
        snapshot = _project_diagnostics(getattr(session, "diagnostics_snapshot", None))
        self._last_diagnostics = snapshot
        return snapshot

    def close(self) -> FrameworkV600OpenResult:
        session = self._session
        if session is not None:
            try:
                close = getattr(session, "close", None)
                if callable(close):
                    close()
            except Exception:
                pass
            self._last_diagnostics = _project_diagnostics(
                getattr(session, "diagnostics_snapshot", None)
            )
        self._session = None
        self._framework = None
        self._closed = True
        return FrameworkV600OpenResult(
            status=FrameworkV600AdapterStatus.CLOSED,
            available=False,
            safe_message="The FW v6 realtime adapter is closed.",
        )

    def _verify_distribution(self) -> FrameworkV600OpenResult | None:
        try:
            version = self._distribution_version(FRAMEWORK_DISTRIBUTION)
        except metadata.PackageNotFoundError:
            return self._unavailable(
                "framework_distribution_missing",
                "Required FW v6 distribution is not installed.",
                recovery_action=FrameworkV600RecoveryAction.CHECK_FRAMEWORK_INSTALL,
            )
        except Exception:
            return self._unavailable(
                "framework_distribution_unavailable",
                "Required FW v6 distribution cannot be verified.",
                recovery_action=FrameworkV600RecoveryAction.CHECK_FRAMEWORK_INSTALL,
            )
        if version != FRAMEWORK_REQUIRED_VERSION:
            return self._unavailable(
                "framework_distribution_version_mismatch",
                "Installed FW version does not match the required v6.0.0 contract.",
                recovery_action=FrameworkV600RecoveryAction.CHECK_FRAMEWORK_INSTALL,
            )
        return None

    def _validate_opened_session(self, session: Any) -> FrameworkV600OpenResult:
        construction = _public_mapping(
            getattr(session, "construction_result", None),
            allowed=(
                "status",
                "real_runtime_requested",
                "real_runtime_enabled",
                "runtime_executable",
                "session_id",
            ),
        )
        session_id = _string_value(construction, session, "session_id")
        if not _valid_session_id(session_id):
            return self._unavailable("framework_contract_mismatch", "FW v6 session identity is invalid.")
        if construction.get("status") != "mock_ready":
            return self._unavailable("framework_contract_mismatch", "FW v6 provider-free construction was not mock_ready.")
        if construction.get("real_runtime_requested") is not False:
            return self._unavailable("framework_contract_mismatch", "FW v6 construction requested real runtime unexpectedly.")
        if construction.get("real_runtime_enabled") is not False:
            return self._unavailable("framework_contract_mismatch", "FW v6 construction enabled real runtime unexpectedly.")
        if construction.get("runtime_executable") is not True:
            return self._unavailable("framework_contract_mismatch", "FW v6 provider-free runtime is not executable.")
        capability = _project_capabilities(getattr(session, "capabilities", None), session_id=session_id)
        if capability.session_id != session_id or capability.real_runtime_enabled:
            return self._unavailable("framework_contract_mismatch", "FW v6 capability snapshot is not correlated.")
        return FrameworkV600OpenResult(
            status=FrameworkV600AdapterStatus.OPEN,
            available=True,
            session_id=session_id,
            real_runtime_requested=False,
            real_runtime_enabled=False,
            runtime_executable=True,
            capabilities=capability,
        )

    def _register_event_callback(self, session: Any) -> None:
        callback = self._events.append

        def normalize(raw: Any) -> None:
            event = _project_event(raw)
            if event is not None:
                callback(event)

        for name in ("on_event", "add_event_callback", "register_event_callback"):
            method = getattr(session, name, None)
            if callable(method):
                method(normalize)
                return

    def _validate_turn_result(self, raw_result: Any) -> FrameworkV600TurnResult:
        result = _public_mapping(
            raw_result,
            allowed=(
                "session_id",
                "turn_id",
                "generation_id",
                "outcome",
                "is_terminal",
                "public_error_code",
                "retryable",
                "recovery_action",
            ),
        )
        events = list(self._events)
        failure = _validate_event_contract(events)
        if failure is not None:
            return self._failed_turn(
                "framework_contract_mismatch",
                failure,
                events=events,
                recovery_action=FrameworkV600RecoveryAction.CONTRACT_REVIEW_REQUIRED,
            )
        terminal = events[-1]
        result_session_id = _string_value(result, raw_result, "session_id")
        result_turn_id = _string_value(result, raw_result, "turn_id")
        result_generation_id = _string_value(result, raw_result, "generation_id")
        result_outcome = _string_value(result, raw_result, "outcome")
        result_terminal = _bool_value(result, raw_result, "is_terminal")
        if (
            result_outcome != "completed"
            or result_terminal is not True
            or result_session_id != terminal.session_id
            or result_turn_id != terminal.turn_id
            or result_generation_id != terminal.generation_id
        ):
            return self._failed_turn(
                "framework_contract_mismatch",
                "FW v6 terminal result identity correlation failed.",
                events=events,
                recovery_action=FrameworkV600RecoveryAction.CONTRACT_REVIEW_REQUIRED,
            )
        diagnostics = self.diagnostics_snapshot()
        if diagnostics is not None and (
            diagnostics.stale_completion_count != 0
            or diagnostics.duplicate_terminal_count != 0
            or diagnostics.overflow_count != 0
        ):
            return self._failed_turn(
                "framework_contract_mismatch",
                "FW v6 diagnostics reported stale, duplicate, or overflow counters.",
                events=events,
                diagnostics=diagnostics,
                recovery_action=FrameworkV600RecoveryAction.CONTRACT_REVIEW_REQUIRED,
            )
        return FrameworkV600TurnResult(
            outcome=FrameworkV600TurnOutcome.COMPLETED,
            terminal=True,
            session_id=terminal.session_id,
            turn_id=terminal.turn_id,
            generation_id=terminal.generation_id,
            events=events,
            capabilities=self._current_capabilities(),
            diagnostics=diagnostics,
        )

    def _validate_input(self, input_text: str) -> FrameworkV600TurnResult | None:
        if not isinstance(input_text, str) or not input_text.strip():
            return self._failed_turn("invalid_input", "Input text is required.", retryable=False)
        if len(input_text) > MAX_INPUT_TEXT_CHARS:
            return self._failed_turn("invalid_input", "Input text is too long.", retryable=False)
        return None

    def _current_capabilities(self) -> FrameworkV600CapabilitySnapshot | None:
        session = self._session
        if session is None:
            return None
        session_id = getattr(session, "session_id", None)
        if not isinstance(session_id, str):
            construction = _public_mapping(
                getattr(session, "construction_result", None),
                allowed=("session_id",),
            )
            session_id = construction.get("session_id")
        if not isinstance(session_id, str):
            return None
        return _project_capabilities(getattr(session, "capabilities", None), session_id=session_id)

    def _unavailable(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = True,
        recovery_action: FrameworkV600RecoveryAction = FrameworkV600RecoveryAction.CONTRACT_REVIEW_REQUIRED,
    ) -> FrameworkV600OpenResult:
        return FrameworkV600OpenResult(
            status=FrameworkV600AdapterStatus.UNAVAILABLE,
            available=False,
            public_error_code=code,
            safe_message=message,
            retryable=retryable,
        )

    def _failed_turn(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = True,
        events: list[FrameworkV600RealtimeEvent] | None = None,
        diagnostics: FrameworkV600DiagnosticsSnapshot | None = None,
        recovery_action: FrameworkV600RecoveryAction = FrameworkV600RecoveryAction.RETRY,
    ) -> FrameworkV600TurnResult:
        return FrameworkV600TurnResult(
            outcome=FrameworkV600TurnOutcome.FAILED,
            terminal=True,
            public_error_code=code,
            safe_message=message,
            retryable=retryable,
            recovery_action=recovery_action,
            events=events or [],
            diagnostics=diagnostics,
        )


def _public_mapping(
    value: Any,
    *,
    allowed: tuple[str, ...] | None = None,
    prefer_v6: bool = True,
    prefer_dict: bool = True,
) -> dict[str, Any]:
    if value is None:
        return {}
    method_names = []
    if prefer_v6:
        method_names.append("as_v6_dict")
    if prefer_dict:
        method_names.append("as_dict")
    for method_name in method_names:
        method = getattr(value, method_name, None)
        if callable(method):
            raw = method()
            if isinstance(raw, Mapping):
                return _normalize_mapping(raw, allowed=allowed)
    if isinstance(value, Mapping):
        return _normalize_mapping(value, allowed=allowed)
    if allowed is None:
        return {}
    projected: dict[str, Any] = {}
    for name in allowed:
        if hasattr(value, name):
            projected[name] = _normalize_public_value(getattr(value, name))
    return projected


def _normalize_mapping(value: Mapping[Any, Any], *, allowed: tuple[str, ...] | None) -> dict[str, Any]:
    items = value.items() if allowed is None else ((name, value[name]) for name in allowed if name in value)
    return {str(key): _normalize_public_value(raw) for key, raw in items}


def _normalize_public_value(value: Any) -> Any:
    enum_value = getattr(value, "value", None)
    if isinstance(enum_value, str):
        return enum_value
    return value


def _project_event(raw: Any) -> FrameworkV600RealtimeEvent | None:
    data = _public_mapping(
        raw,
        allowed=(
            "type",
            "event_type",
            "session_id",
            "turn_id",
            "generation_id",
            "sequence",
            "phase",
            "terminal",
            "public_error_code",
            "safe_message",
            "retryable",
            "payload",
        ),
    )
    event_type = _safe_str(data.get("type") or data.get("event_type"))
    session_id = _safe_str(data.get("session_id"))
    sequence = data.get("sequence")
    if not event_type or not session_id or not isinstance(sequence, int):
        return None
    payload = _safe_payload(data.get("payload"))
    return FrameworkV600RealtimeEvent(
        event_type=event_type,
        session_id=session_id,
        turn_id=_optional_safe_str(data.get("turn_id")),
        generation_id=_optional_safe_str(data.get("generation_id")),
        sequence=sequence,
        phase=_safe_str(data.get("phase") or "unknown"),
        terminal=bool(data.get("terminal", False)),
        public_error_code=_optional_safe_str(data.get("public_error_code")),
        safe_message=_safe_str(data.get("safe_message") or ""),
        retryable=bool(data.get("retryable", False)),
        payload=payload,
    )


def _project_capabilities(raw: Any, *, session_id: str) -> FrameworkV600CapabilitySnapshot:
    data = _public_mapping(
        raw,
        allowed=(
            "schema_version",
            "snapshot_scope",
            "snapshot_generation",
            "session_id",
            "supports_text_chat",
            "supports_voice_input",
            "supports_voice_output",
            "supports_motion",
            "real_runtime_enabled",
            "hard_cancel_supported",
            "tts_queue_flush_supported",
            "text_generation",
            "voice_input",
            "voice_output",
            "motion",
            "fake_runtime",
            "real_runtime",
            "guarded",
            "runtime_available",
            "unavailable_reason",
            "cooperative_cancel_supported",
            "provider_hard_cancel_supported",
            "pending_flush_supported",
            "host_playback_owned_by_drc",
            "host_playback_stop_supported",
            "real_unified_runtime_available",
            "unified_real_pipeline_claimed",
        ),
    )
    text_generation = _project_text_generation_capability(data.get("text_generation"))
    voice_input = _project_voice_input_capability(data.get("voice_input"))
    voice_output = _project_voice_output_capability(data.get("voice_output"))
    motion = _project_motion_capability(data.get("motion"))
    runtime_sources = (
        voice_output.runtime,
        text_generation.runtime,
        voice_input.runtime,
        motion.runtime,
    )
    return FrameworkV600CapabilitySnapshot(
        snapshot_scope=_safe_str(data.get("snapshot_scope") or "session"),
        snapshot_generation=int(data.get("snapshot_generation") or 0),
        session_id=_safe_str(data.get("session_id") or session_id),
        supports_text_chat=bool(data.get("supports_text_chat", False)),
        supports_voice_input=bool(data.get("supports_voice_input", False)),
        supports_voice_output=bool(data.get("supports_voice_output", False)),
        supports_motion=bool(data.get("supports_motion", False)),
        real_runtime_enabled=bool(data.get("real_runtime_enabled", False)),
        hard_cancel_supported=bool(data.get("hard_cancel_supported", False)),
        tts_queue_flush_supported=bool(data.get("tts_queue_flush_supported", False)),
        text_generation=_stage_summary(text_generation.runtime),
        voice_input=_stage_summary(voice_input.runtime),
        voice_output=_stage_summary(voice_output.runtime),
        motion=_stage_summary(motion.runtime),
        fake_runtime=str(any(state.fake_runtime for state in runtime_sources)).lower(),
        real_runtime=str(any(state.real_runtime for state in runtime_sources)).lower(),
        guarded=all(state.guarded for state in runtime_sources),
        runtime_available=any(state.runtime_available for state in runtime_sources),
        unavailable_reason=_first_runtime_unavailable_reason(runtime_sources),
        cooperative_cancel_supported=text_generation.cooperative_cancel_supported,
        provider_hard_cancel_supported=(
            text_generation.provider_hard_cancel_supported
            or voice_output.provider_hard_cancel_supported
        ),
        pending_flush_supported=voice_output.pending_flush_supported,
        host_playback_owned_by_drc=voice_output.playback_ownership in ("host", "drc", "host_local", "drc_host"),
        real_unified_runtime_available=False,
        unified_real_pipeline_claimed=False,
        text_generation_detail=text_generation,
        voice_input_detail=voice_input,
        voice_output_detail=voice_output,
        motion_detail=motion,
    )


def _project_interrupt(raw: Any, *, fallback_scope: str, fallback_reason: str) -> FrameworkV600InterruptResult:
    data = _public_mapping(
        raw,
        allowed=(
            "outcome",
            "scope",
            "reason",
            "provider_cancel_supported",
            "provider_cancel_applied",
            "queue_flush_supported",
            "queue_flush_applied",
            "host_playback_stop_supported",
            "host_playback_stop_applied",
            "safe_message",
            "retryable",
        ),
    )
    return FrameworkV600InterruptResult(
        outcome=_safe_str(data.get("outcome") or "supported"),
        scope=_safe_str(data.get("scope") or fallback_scope),
        reason=_safe_str(data.get("reason") or fallback_reason),
        provider_cancel_supported=bool(data.get("provider_cancel_supported", False)),
        provider_cancel_applied=bool(data.get("provider_cancel_applied", False)),
        queue_flush_supported=bool(data.get("queue_flush_supported", False)),
        queue_flush_applied=bool(data.get("queue_flush_applied", False)),
        host_playback_stop_supported=bool(data.get("host_playback_stop_supported", False)),
        host_playback_stop_applied=bool(data.get("host_playback_stop_applied", False)),
        safe_message=_safe_str(data.get("safe_message") or ""),
        retryable=bool(data.get("retryable", False)),
    )


def _project_diagnostics(raw: Any) -> FrameworkV600DiagnosticsSnapshot | None:
    data = _public_mapping(
        raw,
        allowed=(
            "session_id",
            "state",
            "phase",
            "is_closed",
            "active_turn_id",
            "active_generation_id",
            "queue_depth",
            "active_generation_count",
            "last_terminal_result",
            "last_terminal",
            "last_terminal_summary",
            "last_safe_error_code",
            "stale_completion_count",
            "duplicate_terminal_count",
            "overflow_count",
        ),
    )
    session_id = _safe_str(data.get("session_id"))
    if not session_id:
        return None
    last_terminal = _public_mapping(
        data.get("last_terminal_result") or data.get("last_terminal") or data.get("last_terminal_summary"),
        allowed=(
            "type",
            "event_type",
            "session_id",
            "turn_id",
            "generation_id",
            "outcome",
            "public_error_code",
            "retryable",
            "recovery_action",
        ),
    )
    return FrameworkV600DiagnosticsSnapshot(
        session_id=session_id,
        state=_safe_str(data.get("state") or "unknown"),
        phase=_safe_str(data.get("phase") or "unknown"),
        is_closed=bool(data.get("is_closed", False)),
        active_turn_id=_optional_safe_str(data.get("active_turn_id")),
        active_generation_id=_optional_safe_str(data.get("active_generation_id")),
        queue_depth=max(0, int(data.get("queue_depth") or 0)),
        active_generation_count=max(0, int(data.get("active_generation_count") or 0)),
        last_terminal_event_type=_optional_safe_str(last_terminal.get("event_type") or last_terminal.get("type")),
        last_terminal_turn_id=_optional_safe_str(last_terminal.get("turn_id")),
        last_terminal_generation_id=_optional_safe_str(last_terminal.get("generation_id")),
        last_terminal_outcome=_optional_safe_str(last_terminal.get("outcome")),
        last_terminal_public_error_code=_optional_safe_str(last_terminal.get("public_error_code")),
        last_terminal_retryable=bool(last_terminal.get("retryable", False)),
        last_terminal_recovery_action=_optional_safe_str(last_terminal.get("recovery_action")),
        last_safe_error_code=_optional_safe_str(data.get("last_safe_error_code")),
        stale_completion_count=max(0, int(data.get("stale_completion_count") or 0)),
        duplicate_terminal_count=max(0, int(data.get("duplicate_terminal_count") or 0)),
        overflow_count=max(0, int(data.get("overflow_count") or 0)),
    )


def _validate_event_contract(events: list[FrameworkV600RealtimeEvent]) -> str | None:
    if [event.event_type for event in events] != list(CANONICAL_PROVIDER_FREE_EVENT_ORDER):
        return "FW v6 provider-free canonical event order changed."
    terminal_events = [event for event in events if event.terminal]
    if len(terminal_events) != 1 or terminal_events[0].event_type != "realtime.turn.completed":
        return "FW v6 provider-free turn did not produce exactly one terminal."
    previous = 0
    session_ids = {event.session_id for event in events}
    turn_ids = {event.turn_id for event in events if event.turn_id is not None}
    generation_ids = {event.generation_id for event in events if event.generation_id is not None}
    if len(session_ids) != 1 or not _valid_session_id(next(iter(session_ids))):
        return "FW v6 event session identity correlation failed."
    if len(turn_ids) != 1 or not _valid_turn_id(next(iter(turn_ids))):
        return "FW v6 event turn identity correlation failed."
    if len(generation_ids) != 1 or not _valid_generation_id(next(iter(generation_ids))):
        return "FW v6 event generation identity correlation failed."
    for event in events:
        if event.sequence <= previous:
            return "FW v6 event sequence is not strictly increasing."
        previous = event.sequence
    return None


def _safe_payload(raw: Any) -> dict[str, str | int | bool | None]:
    if not isinstance(raw, Mapping):
        return {}
    safe: dict[str, str | int | bool | None] = {}
    for key in sorted(raw)[:MAX_EVENT_PAYLOAD_ITEMS]:
        if key not in {"source", "mode", "code", "count", "enabled", "available", "reason"}:
            continue
        value = raw[key]
        if isinstance(value, str):
            safe[key] = value[:MAX_EVENT_PAYLOAD_TEXT_CHARS]
        elif isinstance(value, bool) or isinstance(value, int) or value is None:
            safe[key] = value
    return safe


def _string_value(data: dict[str, Any], raw: Any, name: str) -> str | None:
    value = data.get(name)
    if value is None and raw is not None:
        value = getattr(raw, name, None)
    return _optional_safe_str(value)


def _bool_value(data: dict[str, Any], raw: Any, name: str) -> bool | None:
    value = data.get(name)
    if value is None and raw is not None:
        value = getattr(raw, name, None)
    return value if isinstance(value, bool) else None


def _safe_str(value: Any) -> str:
    value = _normalize_public_value(value)
    return "" if value is None else str(value)[:MAX_SAFE_TEXT_CHARS]


def _optional_safe_str(value: Any) -> str | None:
    if value is None:
        return None
    return _safe_str(value)


def _bounded(value: str) -> str:
    return value[:MAX_SAFE_TEXT_CHARS]


def _valid_session_id(value: str | None) -> bool:
    return isinstance(value, str) and SESSION_ID_PATTERN.fullmatch(value) is not None


def _valid_turn_id(value: str | None) -> bool:
    return isinstance(value, str) and TURN_ID_PATTERN.fullmatch(value) is not None


def _valid_generation_id(value: str | None) -> bool:
    return isinstance(value, str) and GENERATION_ID_PATTERN.fullmatch(value) is not None


def _project_runtime_state(value: Any) -> FrameworkV600RuntimeCapabilityState:
    data = _public_mapping(
        value,
        allowed=(
            "configured",
            "runtime_available",
            "guarded",
            "fake_runtime",
            "real_runtime",
            "unavailable_reason",
        ),
    )
    return FrameworkV600RuntimeCapabilityState(
        configured=bool(data.get("configured", False)),
        runtime_available=bool(data.get("runtime_available", False)),
        guarded=bool(data.get("guarded", True)),
        fake_runtime=bool(data.get("fake_runtime", False)),
        real_runtime=bool(data.get("real_runtime", False)),
        unavailable_reason=_optional_safe_str(data.get("unavailable_reason")),
    )


def _project_text_generation_capability(value: Any) -> FrameworkV600TextGenerationCapability:
    data = _stage_mapping(value)
    return FrameworkV600TextGenerationCapability(
        runtime=_project_runtime_state(data.get("runtime")),
        streaming_supported=bool(data.get("streaming_supported", False)),
        cooperative_cancel_supported=bool(data.get("cooperative_cancel_supported", False)),
        provider_hard_cancel_supported=bool(data.get("provider_hard_cancel_supported", False)),
    )


def _project_voice_input_capability(value: Any) -> FrameworkV600VoiceInputCapability:
    data = _stage_mapping(value)
    return FrameworkV600VoiceInputCapability(
        runtime=_project_runtime_state(data.get("runtime")),
        streaming_supported=bool(data.get("streaming_supported", False)),
        cooperative_cancel_supported=bool(data.get("cooperative_cancel_supported", False)),
        provider_hard_cancel_supported=bool(data.get("provider_hard_cancel_supported", False)),
        audio_chunk_input_supported=bool(data.get("audio_chunk_input_supported", False)),
        partial_transcript_supported=bool(data.get("partial_transcript_supported", False)),
        final_transcript_supported=bool(data.get("final_transcript_supported", False)),
        input_abort_supported=bool(data.get("input_abort_supported", False)),
        backpressure_supported=bool(data.get("backpressure_supported", False)),
    )


def _project_voice_output_capability(value: Any) -> FrameworkV600VoiceOutputCapability:
    data = _stage_mapping(value)
    return FrameworkV600VoiceOutputCapability(
        runtime=_project_runtime_state(data.get("runtime")),
        streaming_audio_supported=bool(data.get("streaming_audio_supported", False)),
        generation_cancel_supported=bool(data.get("generation_cancel_supported", False)),
        provider_hard_cancel_supported=bool(data.get("provider_hard_cancel_supported", False)),
        pending_flush_supported=bool(data.get("pending_flush_supported", False)),
        active_audio_invalidation_supported=bool(data.get("active_audio_invalidation_supported", False)),
        playback_ownership=_optional_safe_str(data.get("playback_ownership")),
        host_playback_stop_request_supported=bool(data.get("host_playback_stop_request_supported", False)),
        host_playback_stop_ack_supported=bool(data.get("host_playback_stop_ack_supported", False)),
    )


def _project_motion_capability(value: Any) -> FrameworkV600MotionCapability:
    data = _stage_mapping(value)
    return FrameworkV600MotionCapability(
        runtime=_project_runtime_state(data.get("runtime")),
        request_cancel_supported=bool(data.get("request_cancel_supported", False)),
        completion_event_supported=bool(data.get("completion_event_supported", False)),
        provider_neutral_intent_supported=bool(data.get("provider_neutral_intent_supported", False)),
        stop_motion_supported=bool(data.get("stop_motion_supported", False)),
    )


def _stage_mapping(value: Any) -> dict[str, Any]:
    return _public_mapping(
        value,
        allowed=(
            "runtime",
            "streaming_supported",
            "cooperative_cancel_supported",
            "provider_hard_cancel_supported",
            "audio_chunk_input_supported",
            "partial_transcript_supported",
            "final_transcript_supported",
            "input_abort_supported",
            "backpressure_supported",
            "streaming_audio_supported",
            "generation_cancel_supported",
            "pending_flush_supported",
            "active_audio_invalidation_supported",
            "playback_ownership",
            "host_playback_stop_request_supported",
            "host_playback_stop_ack_supported",
            "request_cancel_supported",
            "completion_event_supported",
            "provider_neutral_intent_supported",
            "stop_motion_supported",
        ),
    )


def _stage_summary(runtime: FrameworkV600RuntimeCapabilityState) -> str:
    if runtime.real_runtime:
        return "real"
    if runtime.fake_runtime:
        return "fake"
    if runtime.runtime_available:
        return "available"
    return "unavailable"


def _first_runtime_unavailable_reason(
    states: tuple[FrameworkV600RuntimeCapabilityState, ...],
) -> str | None:
    for state in states:
        if state.unavailable_reason is not None:
            return state.unavailable_reason
    return None
