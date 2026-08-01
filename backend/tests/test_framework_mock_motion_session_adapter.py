from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from app.models.character_motion import (
    CharacterMotionCommand,
    CharacterMotionCommandIntent,
    CharacterMotionCue,
    CharacterMotionLifecycleFact,
    CharacterMotionMappingOutcome,
    CharacterMotionPlan,
)
from app.models.character_motion_adapter import (
    FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES,
    FrameworkMockMotionExecutionResult,
    FrameworkMockMotionExecutionStatus,
)
from app.services.character_motion_mapper import CharacterMotionMapper
from app.models.character_motion import CharacterMotionMappingInput
from app.services.framework_mock_motion_session_adapter import (
    FrameworkMockMotionSessionAdapter,
)


class FakeMotionIntent(str, Enum):
    EXPRESSION = "expression"
    SPEAKING_STATE = "speaking_state"
    IDLE_MOTION = "idle_motion"
    STOP_MOTION = "stop_motion"
    RESET_EXPRESSION = "reset_expression"


@dataclass
class FakeMotionRequest:
    intent: FakeMotionIntent
    expression: str | None = None
    speaking: bool | None = None
    character_id: str | None = None
    public_metadata: dict[str, Any] | None = None

    @classmethod
    def expression_change(cls, expression: str, **kwargs: Any) -> "FakeMotionRequest":
        return cls(intent=FakeMotionIntent.EXPRESSION, expression=expression, **kwargs)

    @classmethod
    def speaking_state(cls, speaking: bool, **kwargs: Any) -> "FakeMotionRequest":
        return cls(intent=FakeMotionIntent.SPEAKING_STATE, speaking=speaking, **kwargs)

    @classmethod
    def stop_motion(cls, **kwargs: Any) -> "FakeMotionRequest":
        return cls(intent=FakeMotionIntent.STOP_MOTION, **kwargs)


@dataclass
class FakeMotionResult:
    outcome: str = "completed"
    state: str = "idle"
    adapter_status: str = "mock_available"
    public_error_code: str = "none"
    retryable: bool = False
    safe_message: str = ""
    request_id: str = "raw-request-id"
    session_id: str = "raw-session-id"
    public_metadata: dict[str, Any] | None = None


@dataclass
class FakeCapability:
    adapter_status: str = "mock_available"
    supports_motion_session: bool = True
    supports_mock_motion: bool = True
    supports_real_adapter: bool = False


class FakeSession:
    def __init__(
        self,
        *,
        results: list[FakeMotionResult] | None = None,
        capability: FakeCapability | None = None,
        apply_error: Exception | None = None,
        close_error: Exception | None = None,
        event_burst: int = 0,
    ) -> None:
        self.results = list(results or [])
        self.capability = capability or FakeCapability()
        self.apply_error = apply_error
        self.close_error = close_error
        self.event_burst = event_burst
        self.callbacks: list[Any] = []
        self.applied: list[FakeMotionRequest] = []
        self.close_calls = 0
        self.preflight_calls = 0

    def on_event(self, callback: Any) -> None:
        self.callbacks.append(callback)

    def _emit(self, event_type: str) -> None:
        for callback in self.callbacks:
            callback(
                {
                    "type": event_type,
                    "session_id": "must-not-escape",
                    "request_id": "must-not-escape",
                    "public_metadata": {"secret": "must-not-escape"},
                }
            )

    def preflight(self) -> FakeCapability:
        self.preflight_calls += 1
        self._emit("motion.adapter.preflight.completed")
        for index in range(self.event_burst):
            self._emit("motion.requested")
        return self.capability

    def apply_motion(self, request: FakeMotionRequest) -> FakeMotionResult:
        if self.apply_error is not None:
            raise self.apply_error
        self.applied.append(request)
        self._emit("motion.requested")
        self._emit("motion.started")
        result = self.results.pop(0) if self.results else FakeMotionResult()
        self._emit("motion.completed" if result.outcome == "completed" else "motion.unsupported")
        return result

    def close(self) -> None:
        self.close_calls += 1
        if self.close_error is not None:
            raise self.close_error
        self._emit("motion.session.closed")


class FakeFrameworkModule:
    MotionRequest = FakeMotionRequest
    MotionIntent = FakeMotionIntent

    def __init__(self, session_factory: Any | None = None) -> None:
        self.session_factory = session_factory or (lambda: FakeSession())
        self.create_calls: list[dict[str, Any]] = []
        self.sessions: list[FakeSession] = []

    def create_motion_session(self, **kwargs: Any) -> FakeSession:
        self.create_calls.append(kwargs)
        session = self.session_factory()
        self.sessions.append(session)
        return session


def _mapped_plan(fact: CharacterMotionLifecycleFact = CharacterMotionLifecycleFact.IDLE) -> CharacterMotionPlan:
    return CharacterMotionMapper().map(
        CharacterMotionMappingInput(
            fact=fact,
            source_event_type="turn_started",
            session_id="drc-session",
            turn_id="drc-turn",
            character_id="gentle_mina",
        )
    )


def _ignored_plan() -> CharacterMotionPlan:
    return CharacterMotionMapper().map(
        CharacterMotionMappingInput(fact=CharacterMotionLifecycleFact.MOTION_ACTIVE)
    )


def _install_fake_import(monkeypatch: pytest.MonkeyPatch, module: FakeFrameworkModule) -> list[str]:
    imports: list[str] = []

    def fake_import(name: str, package: str | None = None) -> Any:
        imports.append(name)
        if name == "framework":
            return module
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr(importlib, "import_module", fake_import)
    return imports


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "framework-root"
    (root / "framework").mkdir(parents=True)
    return root


def test_adapter_defaults_disabled_without_framework_import(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    imports = _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(framework_root=_root(tmp_path)).execute(
        _mapped_plan()
    )
    assert result.status is FrameworkMockMotionExecutionStatus.DISABLED
    assert result.framework_import_attempted is False
    assert result.session_created is False
    assert result.commands_requested == 3
    assert imports == []
    assert module.create_calls == []


def test_disabled_precedes_ignored_and_still_does_not_import(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    imports = _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(framework_root=_root(tmp_path)).execute(
        _ignored_plan()
    )
    assert result.status is FrameworkMockMotionExecutionStatus.DISABLED
    assert imports == []


def test_enabled_ignored_plan_stops_before_framework_import(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    imports = _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_ignored_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.IGNORED
    assert result.commands_requested == 0
    assert result.reason_code == "recursive_motion_fact_ignored"
    assert imports == []


@pytest.mark.parametrize("configured", [None, "", "   "])
def test_missing_framework_root_returns_typed_unavailable_without_import(
    monkeypatch: pytest.MonkeyPatch, configured: str | None
) -> None:
    module = FakeFrameworkModule()
    imports = _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=configured, enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.UNAVAILABLE
    assert result.reason_code == "framework_root_missing"
    assert result.framework_import_attempted is False
    assert imports == []


def test_nonexistent_framework_root_does_not_expose_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    imports = _install_fake_import(monkeypatch, FakeFrameworkModule())
    missing = tmp_path / "private" / "missing"
    result = FrameworkMockMotionSessionAdapter(
        framework_root=missing, enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.UNAVAILABLE
    assert str(missing) not in result.safe_message
    assert str(missing) not in result.model_dump_json()
    assert imports == []


def test_file_framework_root_is_rejected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root_file = tmp_path / "framework-file"
    root_file.write_text("not a directory", encoding="utf-8")
    imports = _install_fake_import(monkeypatch, FakeFrameworkModule())
    result = FrameworkMockMotionSessionAdapter(
        framework_root=root_file, enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.UNAVAILABLE
    assert imports == []


def test_root_public_module_name_is_the_only_dynamic_framework_import(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    imports = _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.COMPLETED
    assert imports == ["framework"]


@pytest.mark.parametrize("missing", ["create_motion_session", "MotionRequest", "MotionIntent"])
def test_missing_root_public_symbol_fails_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, missing: str
) -> None:
    module = FakeFrameworkModule()
    setattr(module, missing, None)
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.FAILED
    assert result.reason_code == "framework_mock_motion_failed"
    assert result.safe_message == "Framework mock motion execution failed."
    assert result.session_created is False


def test_session_creation_forces_mock_and_disables_real_provider_execution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    call = module.create_calls[0]
    assert call["adapter"] == "mock"
    assert call["real_adapter_enabled"] is False
    assert call["allow_provider_execution"] is False
    assert call["public_metadata"] == {"boundary": "drc_rt6c", "mode": "mock"}
    assert result.provider_execution_attempted is False
    assert result.network_execution is False


def test_preflight_runs_once_before_apply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    session = module.sessions[0]
    assert session.preflight_calls == 1
    assert len(session.applied) == 3


@pytest.mark.parametrize(
    "capability",
    [
        FakeCapability(adapter_status="disabled"),
        FakeCapability(supports_motion_session=False),
        FakeCapability(supports_mock_motion=False),
        FakeCapability(supports_real_adapter=True),
    ],
)
def test_preflight_capability_mismatch_fails_closed_before_apply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capability: FakeCapability
) -> None:
    module = FakeFrameworkModule(lambda: FakeSession(capability=capability))
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    session = module.sessions[0]
    assert result.status is FrameworkMockMotionExecutionStatus.UNAVAILABLE
    assert result.reason_code == "mock_capability_unavailable"
    assert result.commands_completed == 0
    assert session.applied == []
    assert session.close_calls == 1
    assert result.session_closed is True


def test_expression_command_conversion(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan(CharacterMotionLifecycleFact.THINKING))
    request = module.sessions[0].applied[1]
    assert request.intent is FakeMotionIntent.EXPRESSION
    assert request.expression == "thinking"
    assert request.character_id == "gentle_mina"


@pytest.mark.parametrize(
    ("fact", "expected"),
    [
        (CharacterMotionLifecycleFact.SPEAKING, True),
        (CharacterMotionLifecycleFact.LISTENING, False),
    ],
)
def test_speaking_state_command_conversion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fact: CharacterMotionLifecycleFact,
    expected: bool,
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan(fact))
    requests = module.sessions[0].applied
    speaking = next(request for request in requests if request.intent is FakeMotionIntent.SPEAKING_STATE)
    assert speaking.speaking is expected


def test_stop_reset_and_idle_intents_use_root_public_motion_intent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    adapter = FrameworkMockMotionSessionAdapter(framework_root=_root(tmp_path), enabled=True)
    adapter.execute(_mapped_plan(CharacterMotionLifecycleFact.INTERRUPTED))
    assert [request.intent for request in module.sessions[0].applied] == [
        FakeMotionIntent.STOP_MOTION,
        FakeMotionIntent.SPEAKING_STATE,
        FakeMotionIntent.RESET_EXPRESSION,
    ]
    adapter.execute(_mapped_plan(CharacterMotionLifecycleFact.IDLE))
    assert [request.intent for request in module.sessions[1].applied] == [
        FakeMotionIntent.SPEAKING_STATE,
        FakeMotionIntent.RESET_EXPRESSION,
        FakeMotionIntent.IDLE_MOTION,
    ]


def test_command_order_and_bounded_metadata_are_preserved(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert [item.order for item in result.command_results] == [1, 2, 3]
    metadata = [request.public_metadata for request in module.sessions[0].applied]
    assert [item["command_order"] for item in metadata] == [1, 2, 3]
    assert all(item["boundary"] == "drc_rt6c" for item in metadata)
    assert all(item["drc_cue"] == "idle" for item in metadata)


def test_source_identifiers_are_not_forwarded_to_framework_metadata(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.source_event_type == "turn_started"
    assert result.source_session_id == "drc-session"
    assert result.source_turn_id == "drc-turn"
    assert result.character_id == "gentle_mina"
    for request in module.sessions[0].applied:
        text = repr(request.public_metadata)
        assert "drc-session" not in text
        assert "drc-turn" not in text
        assert "turn_started" not in text


def test_all_completed_returns_bounded_aggregate_and_closes_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.COMPLETED
    assert result.commands_requested == 3
    assert result.commands_completed == 3
    assert result.session_created is True
    assert result.session_closed is True
    assert module.sessions[0].close_calls == 1


def test_non_completed_result_fails_fast_and_closes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    results = [
        FakeMotionResult(),
        FakeMotionResult(
            outcome="not_implemented",
            state="unavailable",
            adapter_status="not_implemented",
            public_error_code="not_implemented",
        ),
        FakeMotionResult(),
    ]
    module = FakeFrameworkModule(lambda: FakeSession(results=results))
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.UNAVAILABLE
    assert result.commands_completed == 1
    assert len(result.command_results) == 2
    assert len(module.sessions[0].applied) == 2
    assert module.sessions[0].close_calls == 1


def test_failed_result_maps_to_failed_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule(
        lambda: FakeSession(results=[FakeMotionResult(outcome="failed")])
    )
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.FAILED
    assert result.commands_completed == 0


def test_apply_exception_is_fixed_safe_failure_and_closes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    private = tmp_path / "private-token-path"
    module = FakeFrameworkModule(
        lambda: FakeSession(apply_error=RuntimeError(f"secret at {private}"))
    )
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.FAILED
    assert result.safe_message == "Framework mock motion execution failed."
    assert str(private) not in result.model_dump_json()
    assert module.sessions[0].close_calls == 1
    assert result.session_closed is True


def test_close_exception_is_fixed_safe_failure_without_raw_exception(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule(
        lambda: FakeSession(close_error=RuntimeError("private close detail"))
    )
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert result.status is FrameworkMockMotionExecutionStatus.FAILED
    assert result.reason_code == "framework_mock_motion_close_failed"
    assert result.safe_message == "Framework mock motion session cleanup failed."
    assert "private close detail" not in result.model_dump_json()
    assert result.session_closed is False


def test_event_retention_is_type_only_and_bounded(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule(lambda: FakeSession(event_burst=30))
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert len(result.event_types) == FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES
    serialized = result.model_dump_json()
    assert "must-not-escape" not in serialized
    assert "secret" not in serialized


def test_raw_framework_identifiers_and_objects_are_not_exposed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule(
        lambda: FakeSession(
            results=[
                FakeMotionResult(
                    outcome="unexpected-private-outcome",
                    state="private-state",
                    adapter_status="private-adapter",
                    public_error_code="private-error",
                    safe_message="private path and token detail",
                )
            ]
        )
    )
    _install_fake_import(monkeypatch, module)
    result = FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    serialized = result.model_dump_json()
    assert "raw-request-id" not in serialized
    assert "raw-session-id" not in serialized
    assert "public_metadata" not in FrameworkMockMotionExecutionResult.model_fields
    assert "private" not in serialized
    assert result.command_results[0].outcome == "failed"
    assert result.command_results[0].state == "unavailable"
    assert result.command_results[0].adapter_status == "disabled"
    assert result.command_results[0].public_error_code == "provider_error"
    assert isinstance(result, FrameworkMockMotionExecutionResult)


def test_adapter_creates_a_new_session_for_each_execution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    adapter = FrameworkMockMotionSessionAdapter(framework_root=_root(tmp_path), enabled=True)
    adapter.execute(_mapped_plan())
    adapter.execute(_mapped_plan(CharacterMotionLifecycleFact.SPEAKING))
    assert len(module.sessions) == 2
    assert module.sessions[0] is not module.sessions[1]
    assert all(session.close_calls == 1 for session in module.sessions)


def test_import_context_restores_cwd_and_sys_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = _root(tmp_path)
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    cwd_before = Path.cwd()
    sys_path_before = list(sys.path)
    FrameworkMockMotionSessionAdapter(framework_root=root, enabled=True).execute(
        _mapped_plan()
    )
    assert Path.cwd() == cwd_before
    assert sys.path == sys_path_before


def test_wrong_plan_type_is_rejected(tmp_path: Path) -> None:
    adapter = FrameworkMockMotionSessionAdapter(framework_root=_root(tmp_path), enabled=True)
    with pytest.raises(TypeError, match="CharacterMotionPlan"):
        adapter.execute(object())  # type: ignore[arg-type]


def test_result_model_rejects_real_or_provider_execution_claims() -> None:
    with pytest.raises(ValueError):
        FrameworkMockMotionExecutionResult(
            status=FrameworkMockMotionExecutionStatus.UNAVAILABLE,
            source_fact=CharacterMotionLifecycleFact.IDLE,
            cue=CharacterMotionCue.IDLE,
            commands_requested=3,
            commands_completed=0,
            real_adapter_enabled=True,
            reason_code="invalid",
        )


def test_adapter_source_contains_no_internal_framework_import_or_runtime_dependency() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "framework_mock_motion_session_adapter.py"
    )
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any(name == "framework" or name.startswith("framework.") for name in imported)
    forbidden = ["websocket", "vtube", "live2d", "provider_sdk"]
    assert not any(name in imported for name in forbidden)
    assert 'import_module("framework")' in source
    assert 'import_module("framework.motion")' not in source
    assert 'import_module("framework.motion_session")' not in source


def test_maximum_apply_calls_is_three(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = FakeFrameworkModule()
    _install_fake_import(monkeypatch, module)
    FrameworkMockMotionSessionAdapter(
        framework_root=_root(tmp_path), enabled=True
    ).execute(_mapped_plan())
    assert len(module.sessions[0].applied) == 3


def test_execution_result_has_no_arbitrary_metadata_channel() -> None:
    fields = FrameworkMockMotionExecutionResult.model_fields
    assert "public_metadata" not in fields
    assert "metadata" not in fields
    assert "raw_result" not in fields
    assert "framework_session_id" not in fields
    assert "framework_request_id" not in fields
