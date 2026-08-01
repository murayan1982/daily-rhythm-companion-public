"""Guarded default-off adapter for FW root-public mock motion sessions.

RT-6c imports only the configured root ``framework`` facade. It forces the mock
adapter, disables real adapter and provider execution, applies at most three
commands synchronously, and returns only bounded DRC-owned result models.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
import importlib
import os
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Iterator

from app.models.character_motion import (
    CharacterMotionCommand,
    CharacterMotionCommandIntent,
    CharacterMotionMappingOutcome,
    CharacterMotionPlan,
)
from app.models.character_motion_adapter import (
    FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES,
    FRAMEWORK_MOCK_MOTION_MAX_RESULT_TEXT_CHARS,
    FrameworkMockMotionCommandResult,
    FrameworkMockMotionExecutionResult,
    FrameworkMockMotionExecutionStatus,
)


_ALLOWED_EVENT_TYPES = frozenset(
    {
        "motion.session.created",
        "motion.adapter.preflight.completed",
        "motion.requested",
        "motion.started",
        "motion.completed",
        "motion.interrupted",
        "motion.failed",
        "motion.unsupported",
        "motion.session.closed",
    }
)
_ALLOWED_OUTCOMES = frozenset(
    {
        "completed",
        "unsupported",
        "unavailable",
        "not_configured",
        "not_implemented",
        "interrupted",
        "failed",
        "closed",
    }
)
_ALLOWED_STATES = frozenset(
    {
        "idle",
        "preparing",
        "speaking",
        "expressing",
        "gesturing",
        "interrupted",
        "failed",
        "closed",
        "unavailable",
    }
)
_ALLOWED_ADAPTER_STATUSES = frozenset(
    {
        "disabled",
        "mock_available",
        "not_configured",
        "token_missing",
        "provider_execution_not_allowed",
        "runtime_not_installed",
        "model_not_selected",
        "not_implemented",
        "unsupported_adapter",
        "closed",
    }
)
_ALLOWED_ERROR_CODES = frozenset(
    {
        "none",
        "unavailable",
        "unsupported",
        "not_configured",
        "token_missing",
        "provider_execution_not_allowed",
        "runtime_not_installed",
        "model_not_selected",
        "not_implemented",
        "interrupted",
        "session_closed",
        "provider_error",
    }
)


class FrameworkMockMotionSessionAdapter:
    """Execute one bounded plan through a new local FW mock session."""

    def __init__(
        self,
        *,
        framework_root: str | Path | None,
        enabled: bool = False,
    ) -> None:
        self._framework_root = framework_root
        self._enabled = bool(enabled)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def execute(self, plan: CharacterMotionPlan) -> FrameworkMockMotionExecutionResult:
        """Execute a mapped plan or return a typed safe non-execution result."""

        if not isinstance(plan, CharacterMotionPlan):
            raise TypeError("plan must be a CharacterMotionPlan")

        if not self._enabled:
            return self._result(
                plan,
                status=FrameworkMockMotionExecutionStatus.DISABLED,
                commands_requested=len(plan.commands),
                reason_code="framework_mock_motion_disabled",
                safe_message="Framework mock motion execution is disabled.",
            )

        if plan.outcome is CharacterMotionMappingOutcome.IGNORED:
            return self._result(
                plan,
                status=FrameworkMockMotionExecutionStatus.IGNORED,
                commands_requested=0,
                reason_code=plan.reason_code,
                safe_message="Character motion plan was ignored before Framework import.",
            )

        framework_root = self._resolve_framework_root()
        if framework_root is None:
            return self._result(
                plan,
                status=FrameworkMockMotionExecutionStatus.UNAVAILABLE,
                commands_requested=len(plan.commands),
                reason_code="framework_root_missing",
                safe_message="Configured Framework root is unavailable.",
            )

        event_types: list[str] = []
        command_results: list[FrameworkMockMotionCommandResult] = []
        commands_completed = 0
        session: Any | None = None
        framework_import_attempted = False
        session_created = False
        session_closed = False
        status = FrameworkMockMotionExecutionStatus.FAILED
        reason_code = "framework_mock_motion_failed"
        safe_message = "Framework mock motion execution failed."

        try:
            framework_import_attempted = True
            with _framework_public_import_context(framework_root):
                framework = importlib.import_module("framework")
                public_api = _FrameworkMotionPublicApi.from_module(framework)
                session = public_api.create_motion_session(
                    project_root=str(framework_root),
                    adapter="mock",
                    real_adapter_enabled=False,
                    allow_provider_execution=False,
                    public_metadata={
                        "boundary": "drc_rt6c",
                        "mode": "mock",
                    },
                )
                if session is None:
                    raise RuntimeError("Framework motion session creation returned no session")
                session_created = True
                _register_event_observer(session, event_types)
                capability = _preflight(session)
                if not _is_mock_capability_available(capability):
                    status = FrameworkMockMotionExecutionStatus.UNAVAILABLE
                    reason_code = "mock_capability_unavailable"
                    safe_message = "Framework mock motion capability is unavailable."
                else:
                    status = FrameworkMockMotionExecutionStatus.COMPLETED
                    reason_code = "framework_mock_motion_completed"
                    safe_message = "Framework mock motion commands completed locally."
                    for command in plan.commands:
                        request = _convert_command(
                            public_api,
                            command,
                            cue=plan.cue.value if plan.cue is not None else None,
                            character_id=plan.character_id,
                        )
                        raw_result = _apply_motion(session, request)
                        normalized = _normalize_command_result(command, raw_result)
                        command_results.append(normalized)
                        if normalized.outcome != "completed":
                            status = _status_for_non_completed(normalized.outcome)
                            reason_code = "framework_mock_motion_non_completed"
                            safe_message = "Framework mock motion command did not complete."
                            break
                        commands_completed += 1
        except Exception:
            status = FrameworkMockMotionExecutionStatus.FAILED
            reason_code = "framework_mock_motion_failed"
            safe_message = "Framework mock motion execution failed."
        finally:
            if session_created and session is not None:
                try:
                    close = getattr(session, "close", None)
                    if not callable(close):
                        raise RuntimeError("Framework motion session has no close method")
                    close()
                    session_closed = True
                except Exception:
                    session_closed = False
                    status = FrameworkMockMotionExecutionStatus.FAILED
                    reason_code = "framework_mock_motion_close_failed"
                    safe_message = "Framework mock motion session cleanup failed."

        return self._result(
            plan,
            status=status,
            commands_requested=len(plan.commands),
            commands_completed=commands_completed,
            command_results=command_results,
            event_types=event_types,
            framework_import_attempted=framework_import_attempted,
            session_created=session_created,
            session_closed=session_closed,
            reason_code=reason_code,
            safe_message=safe_message,
        )

    def _resolve_framework_root(self) -> Path | None:
        configured = self._framework_root
        if configured is None or not str(configured).strip():
            return None
        try:
            root = Path(configured).expanduser().resolve()
        except (OSError, RuntimeError, ValueError):
            return None
        if not root.exists() or not root.is_dir():
            return None
        return root

    @staticmethod
    def _result(
        plan: CharacterMotionPlan,
        *,
        status: FrameworkMockMotionExecutionStatus,
        commands_requested: int,
        commands_completed: int = 0,
        command_results: list[FrameworkMockMotionCommandResult] | None = None,
        event_types: list[str] | None = None,
        framework_import_attempted: bool = False,
        session_created: bool = False,
        session_closed: bool = False,
        reason_code: str,
        safe_message: str,
    ) -> FrameworkMockMotionExecutionResult:
        return FrameworkMockMotionExecutionResult(
            status=status,
            source_fact=plan.source_fact,
            cue=plan.cue,
            source_event_type=plan.source_event_type,
            source_session_id=plan.session_id,
            source_turn_id=plan.turn_id,
            character_id=plan.character_id,
            commands_requested=commands_requested,
            commands_completed=commands_completed,
            command_results=list(command_results or []),
            event_types=list(event_types or [])[:FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES],
            framework_import_attempted=framework_import_attempted,
            session_created=session_created,
            session_closed=session_closed,
            adapter="mock",
            real_adapter_enabled=False,
            provider_execution_allowed=False,
            provider_execution_attempted=False,
            network_execution=False,
            reason_code=reason_code,
            safe_message=safe_message,
        )


class _FrameworkMotionPublicApi:
    """Validated references obtained from the root-public Framework module."""

    def __init__(self, *, create_motion_session: Any, motion_request: Any, motion_intent: Any) -> None:
        self.create_motion_session = create_motion_session
        self.motion_request = motion_request
        self.motion_intent = motion_intent

    @classmethod
    def from_module(cls, module: ModuleType | Any) -> "_FrameworkMotionPublicApi":
        create_motion_session = getattr(module, "create_motion_session", None)
        motion_request = getattr(module, "MotionRequest", None)
        motion_intent = getattr(module, "MotionIntent", None)
        if not callable(create_motion_session):
            raise RuntimeError("Framework root-public create_motion_session is unavailable")
        if motion_request is None or motion_intent is None:
            raise RuntimeError("Framework root-public motion request types are unavailable")
        return cls(
            create_motion_session=create_motion_session,
            motion_request=motion_request,
            motion_intent=motion_intent,
        )


def _convert_command(
    public_api: _FrameworkMotionPublicApi,
    command: CharacterMotionCommand,
    *,
    cue: str | None,
    character_id: str | None,
) -> Any:
    metadata = {
        "boundary": "drc_rt6c",
        "command_order": command.order,
        "drc_intent": command.intent.value,
        "drc_cue": cue,
    }
    request_type = public_api.motion_request
    if command.intent is CharacterMotionCommandIntent.EXPRESSION:
        return request_type.expression_change(
            command.expression_id,
            character_id=character_id,
            public_metadata=metadata,
        )
    if command.intent is CharacterMotionCommandIntent.SPEAKING_STATE:
        return request_type.speaking_state(
            command.speaking,
            character_id=character_id,
            public_metadata=metadata,
        )
    if command.intent is CharacterMotionCommandIntent.STOP_MOTION:
        return request_type.stop_motion(
            character_id=character_id,
            public_metadata=metadata,
        )
    if command.intent is CharacterMotionCommandIntent.IDLE_MOTION:
        return request_type(
            intent=public_api.motion_intent.IDLE_MOTION,
            character_id=character_id,
            public_metadata=metadata,
        )
    if command.intent is CharacterMotionCommandIntent.RESET_EXPRESSION:
        return request_type(
            intent=public_api.motion_intent.RESET_EXPRESSION,
            character_id=character_id,
            public_metadata=metadata,
        )
    raise RuntimeError("Unsupported DRC motion command intent")


def _preflight(session: Any) -> Any:
    preflight = getattr(session, "preflight", None)
    if not callable(preflight):
        raise RuntimeError("Framework motion session has no preflight method")
    return preflight()


def _apply_motion(session: Any, request: Any) -> Any:
    apply_motion = getattr(session, "apply_motion", None)
    if not callable(apply_motion):
        raise RuntimeError("Framework motion session has no apply_motion method")
    return apply_motion(request)


def _register_event_observer(session: Any, event_types: list[str]) -> None:
    on_event = getattr(session, "on_event", None)
    if not callable(on_event):
        raise RuntimeError("Framework motion session has no event registration method")

    def observe(payload: Any) -> None:
        if len(event_types) >= FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES:
            return
        event_type = payload.get("type") if isinstance(payload, Mapping) else None
        if isinstance(event_type, str) and event_type in _ALLOWED_EVENT_TYPES:
            event_types.append(event_type)

    on_event(observe)


def _is_mock_capability_available(capability: Any) -> bool:
    adapter_status = _enum_text(getattr(capability, "adapter_status", ""))
    return (
        adapter_status == "mock_available"
        and bool(getattr(capability, "supports_motion_session", False))
        and bool(getattr(capability, "supports_mock_motion", False))
        and not bool(getattr(capability, "supports_real_adapter", False))
    )


def _normalize_command_result(
    command: CharacterMotionCommand,
    raw_result: Any,
) -> FrameworkMockMotionCommandResult:
    outcome = _allowlisted_enum_text(
        getattr(raw_result, "outcome", "failed"),
        allowed=_ALLOWED_OUTCOMES,
        fallback="failed",
    )
    return FrameworkMockMotionCommandResult(
        order=command.order,
        intent=command.intent,
        outcome=outcome,
        state=_allowlisted_enum_text(
            getattr(raw_result, "state", "unavailable"),
            allowed=_ALLOWED_STATES,
            fallback="unavailable",
        ),
        adapter_status=_allowlisted_enum_text(
            getattr(raw_result, "adapter_status", "disabled"),
            allowed=_ALLOWED_ADAPTER_STATUSES,
            fallback="disabled",
        ),
        public_error_code=_allowlisted_enum_text(
            getattr(raw_result, "public_error_code", "provider_error"),
            allowed=_ALLOWED_ERROR_CODES,
            fallback="provider_error",
        ),
        retryable=bool(getattr(raw_result, "retryable", False)),
        safe_message=(
            "" if outcome == "completed" else "Framework mock motion command did not complete."
        ),
    )


def _status_for_non_completed(outcome: str) -> FrameworkMockMotionExecutionStatus:
    if outcome in {
        "unsupported",
        "unavailable",
        "not_configured",
        "not_implemented",
        "closed",
    }:
        return FrameworkMockMotionExecutionStatus.UNAVAILABLE
    return FrameworkMockMotionExecutionStatus.FAILED


def _enum_text(value: Any) -> str:
    raw = getattr(value, "value", value)
    text = str(raw or "")
    return text[:64]


def _allowlisted_enum_text(
    value: Any,
    *,
    allowed: frozenset[str],
    fallback: str,
) -> str:
    text = _enum_text(value)
    return text if text in allowed else fallback


@contextmanager
def _framework_public_import_context(project_root: Path) -> Iterator[None]:
    """Temporarily expose only the configured Framework checkout and cwd."""

    roots = [project_root]
    framework_dir = project_root / "framework"
    if _has_registry_module(framework_dir) and not _has_registry_module(project_root):
        roots.append(framework_dir)

    added: list[str] = []
    previous_cwd = Path.cwd()
    try:
        for root in reversed(roots):
            root_text = str(root)
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
                added.append(root_text)
        os.chdir(project_root)
        yield
    finally:
        os.chdir(previous_cwd)
        for root_text in added:
            try:
                sys.path.remove(root_text)
            except ValueError:
                pass


def _has_registry_module(path: Path) -> bool:
    return (path / "registry.py").exists() or (path / "registry" / "__init__.py").exists()
