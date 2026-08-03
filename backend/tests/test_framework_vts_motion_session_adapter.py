from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any, Iterator

import pytest
from pydantic import ValidationError

from app.models.framework_vts_motion import (
    FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES,
    FrameworkVtsMotionCommand,
    FrameworkVtsMotionExecutionStatus,
    FrameworkVtsMotionIntent,
)
from app.services.framework_vts_motion_session_adapter import (
    FrameworkVtsMotionPrivateConfig,
    FrameworkVtsMotionSessionAdapter,
    _vendored_framework_root_public,
)


class FakeMotionIntent(str, Enum):
    EXPRESSION = "expression"
    EMOTION = "emotion"
    GESTURE = "gesture"
    RESET_EXPRESSION = "reset_expression"
    STOP_MOTION = "stop_motion"


@dataclass
class FakeMotionRequest:
    intent: FakeMotionIntent
    expression: str | None = None
    emotion: str | None = None
    gesture: str | None = None
    character_id: str | None = None
    public_metadata: dict[str, Any] | None = None

    @classmethod
    def expression_change(
        cls,
        expression: str,
        **kwargs: Any,
    ) -> "FakeMotionRequest":
        return cls(
            intent=FakeMotionIntent.EXPRESSION,
            expression=expression,
            **kwargs,
        )

    @classmethod
    def emotion_update(
        cls,
        emotion: str,
        **kwargs: Any,
    ) -> "FakeMotionRequest":
        return cls(
            intent=FakeMotionIntent.EMOTION,
            emotion=emotion,
            **kwargs,
        )

    @classmethod
    def stop_motion(cls, **kwargs: Any) -> "FakeMotionRequest":
        return cls(intent=FakeMotionIntent.STOP_MOTION, **kwargs)


@dataclass
class FakeMotionResult:
    outcome: str = "completed"
    state: str = "idle"
    adapter_status: str = "configured"
    public_error_code: str = "none"
    retryable: bool = False
    safe_message: str = ""
    request_id: str = "must-not-escape-request"
    session_id: str = "must-not-escape-session"
    public_metadata: dict[str, Any] | None = None


class FakeCapability:
    def __init__(
        self,
        *,
        status: str = "configured",
        supports_real_adapter: bool = True,
        supported: set[FakeMotionIntent] | None = None,
        public_metadata: dict[str, Any] | None = None,
    ) -> None:
        self.adapter_status = status
        self.supports_motion_session = True
        self.supports_real_adapter = supports_real_adapter
        self._supported = (
            set(FakeMotionIntent)
            if supported is None
            else set(supported)
        )
        self.public_metadata = public_metadata or {}

    def supports_intent(self, intent: FakeMotionIntent) -> bool:
        return intent in self._supported


class FakeSession:
    def __init__(
        self,
        *,
        capability: FakeCapability | None = None,
        results: list[FakeMotionResult] | None = None,
        preflight_error: Exception | None = None,
        apply_error: Exception | None = None,
        close_error: Exception | None = None,
        event_burst: int = 0,
    ) -> None:
        self.capability = capability or FakeCapability()
        self.results = list(results or [])
        self.preflight_error = preflight_error
        self.apply_error = apply_error
        self.close_error = close_error
        self.event_burst = event_burst
        self.callbacks: list[Any] = []
        self.applied: list[FakeMotionRequest] = []
        self.preflight_calls = 0
        self.close_calls = 0

    def on_event(self, callback: Any) -> None:
        self.callbacks.append(callback)

    def _emit(self, event_type: str) -> None:
        for callback in self.callbacks:
            callback(
                {
                    "type": event_type,
                    "session_id": "must-not-escape",
                    "request_id": "must-not-escape",
                    "public_metadata": {
                        "authentication_token": "must-not-escape",
                    },
                }
            )

    def preflight(self) -> FakeCapability:
        self.preflight_calls += 1
        if self.preflight_error is not None:
            raise self.preflight_error
        self._emit("motion.adapter.preflight.completed")
        self._emit("private.provider.event")
        for _ in range(self.event_burst):
            self._emit("motion.requested")
        return self.capability

    def apply_motion(self, request: FakeMotionRequest) -> FakeMotionResult:
        if self.apply_error is not None:
            raise self.apply_error
        self.applied.append(request)
        self._emit("motion.requested")
        self._emit("motion.started")
        result = self.results.pop(0) if self.results else FakeMotionResult()
        self._emit(
            "motion.completed"
            if result.outcome == "completed"
            else "motion.unsupported"
        )
        return result

    def close(self) -> None:
        self.close_calls += 1
        if self.close_error is not None:
            raise self.close_error
        self._emit("motion.session.closed")


class FakeFrameworkModule:
    MotionRequest = FakeMotionRequest
    MotionIntent = FakeMotionIntent

    class MotionSessionInfo:
        api_version = "5.5.0"

    def __init__(
        self,
        *,
        module_file: Path,
        session_factory: Any | None = None,
    ) -> None:
        self.__file__ = str(module_file)
        self.session_factory = session_factory or FakeSession
        self.create_calls: list[dict[str, Any]] = []
        self.sessions: list[FakeSession] = []

    def create_motion_session(self, **kwargs: Any) -> FakeSession:
        self.create_calls.append(kwargs)
        session = self.session_factory()
        self.sessions.append(session)
        return session


def _vendor(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "fixed-vendor"
    framework_init = root / "framework" / "__init__.py"
    framework_init.parent.mkdir(parents=True)
    framework_init.write_text("# fake root-public package\n", encoding="utf-8")
    return root, framework_init


def _module_context(module: Any):
    @contextmanager
    def factory(_: Path) -> Iterator[Any]:
        yield module

    return factory


def _config(
    *,
    enabled: bool = True,
    allow_provider_execution: bool = True,
) -> FrameworkVtsMotionPrivateConfig:
    return FrameworkVtsMotionPrivateConfig(
        enabled=enabled,
        allow_provider_execution=allow_provider_execution,
        runtime_available=True,
        model_selected=True,
        endpoint_host="loopback.test",
        endpoint_port=8001,
        authentication_token="test-authentication-value",
        hotkey_bindings={
            "expression:smile": "test-expression-hotkey",
            "emotion:happy": "test-emotion-hotkey",
            "gesture:wave": "test-gesture-hotkey",
            "reset_expression": "test-reset-hotkey",
        },
    )


def _commands(
    *,
    include_stop: bool = False,
) -> list[FrameworkVtsMotionCommand]:
    commands = [
        FrameworkVtsMotionCommand(
            order=1,
            intent=FrameworkVtsMotionIntent.EXPRESSION,
            expression="smile",
            character_id="gentle_mina",
        ),
        FrameworkVtsMotionCommand(
            order=2,
            intent=FrameworkVtsMotionIntent.EMOTION,
            emotion="happy",
            character_id="gentle_mina",
        ),
        FrameworkVtsMotionCommand(
            order=3,
            intent=FrameworkVtsMotionIntent.GESTURE,
            gesture="wave",
            character_id="gentle_mina",
        ),
        FrameworkVtsMotionCommand(
            order=4,
            intent=FrameworkVtsMotionIntent.RESET_EXPRESSION,
            character_id="gentle_mina",
        ),
    ]
    if include_stop:
        commands.append(
            FrameworkVtsMotionCommand(
                order=5,
                intent=FrameworkVtsMotionIntent.STOP_MOTION,
                character_id="gentle_mina",
            )
        )
    return commands


def _adapter(
    tmp_path: Path,
    module: FakeFrameworkModule,
    *,
    config: FrameworkVtsMotionPrivateConfig | None = None,
) -> FrameworkVtsMotionSessionAdapter:
    vendor_root, _ = _vendor(tmp_path)
    return FrameworkVtsMotionSessionAdapter(
        config or _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    )


def test_disabled_guard_precedes_vendor_and_framework_import(
    tmp_path: Path,
) -> None:
    calls = 0

    @contextmanager
    def forbidden_loader(_: Path) -> Iterator[Any]:
        nonlocal calls
        calls += 1
        raise AssertionError("Framework loader must not run")
        yield

    result = FrameworkVtsMotionSessionAdapter(
        _config(enabled=False),
        _module_context_factory=forbidden_loader,
        _vendor_root=tmp_path / "missing",
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.DISABLED
    assert result.framework_import_attempted is False
    assert result.session_created is False
    assert result.real_adapter_enabled is False
    assert calls == 0


def test_provider_execution_guard_precedes_vendor_and_framework_import(
    tmp_path: Path,
) -> None:
    calls = 0

    @contextmanager
    def forbidden_loader(_: Path) -> Iterator[Any]:
        nonlocal calls
        calls += 1
        raise AssertionError("Framework loader must not run")
        yield

    result = FrameworkVtsMotionSessionAdapter(
        _config(allow_provider_execution=False),
        _module_context_factory=forbidden_loader,
        _vendor_root=tmp_path / "missing",
    ).execute(_commands())

    assert (
        result.status
        is FrameworkVtsMotionExecutionStatus.PROVIDER_EXECUTION_NOT_ALLOWED
    )
    assert result.framework_import_attempted is False
    assert result.provider_execution_allowed is False
    assert calls == 0


def test_missing_fixed_vendor_returns_typed_unavailable_without_path(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "private" / "missing-vendor"
    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _vendor_root=missing,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.UNAVAILABLE
    assert result.reason_code == "framework_v550_vendor_missing"
    assert result.framework_import_attempted is False
    assert str(missing) not in result.model_dump_json()


def test_unexpected_framework_origin_fails_closed(
    tmp_path: Path,
) -> None:
    vendor_root, _ = _vendor(tmp_path)
    outside = tmp_path / "outside" / "framework" / "__init__.py"
    outside.parent.mkdir(parents=True)
    outside.write_text("# wrong origin\n", encoding="utf-8")
    module = FakeFrameworkModule(module_file=outside)

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.FAILED
    assert result.session_created is False
    assert str(outside) not in result.model_dump_json()


@pytest.mark.parametrize(
    "missing",
    ["create_motion_session", "MotionRequest", "MotionIntent", "MotionSessionInfo"],
)
def test_missing_root_public_symbol_fails_closed(
    tmp_path: Path,
    missing: str,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(module_file=framework_init)
    setattr(module, missing, None)

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.FAILED
    assert result.session_created is False


def test_session_creation_uses_exact_vts_double_opt_in_and_private_values(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(module_file=framework_init)

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.COMPLETED
    call = module.create_calls[0]
    assert call["adapter"] == "vts"
    assert call["real_adapter_enabled"] is True
    assert call["allow_provider_execution"] is True
    assert call["runtime_available"] is True
    assert call["model_selected"] is True
    assert call["vts_endpoint_host"] == "loopback.test"
    assert call["vts_endpoint_port"] == 8001
    assert call["vts_authentication_token"] == "test-authentication-value"
    assert call["vts_hotkey_bindings"]["gesture:wave"] == "test-gesture-hotkey"
    assert call["public_metadata"] == {
        "boundary": "drc_rt7c",
        "mode": "guarded_vts",
    }
    serialized = result.model_dump_json()
    assert "loopback.test" not in serialized
    assert "test-authentication-value" not in serialized
    assert "test-gesture-hotkey" not in serialized


def test_required_four_intents_convert_and_complete_in_order(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(module_file=framework_init)
    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.COMPLETED
    assert result.commands_requested == 4
    assert result.commands_applied == 4
    assert result.commands_completed == 4
    assert result.session_closed is True

    applied = module.sessions[0].applied
    assert [request.intent for request in applied] == [
        FakeMotionIntent.EXPRESSION,
        FakeMotionIntent.EMOTION,
        FakeMotionIntent.GESTURE,
        FakeMotionIntent.RESET_EXPRESSION,
    ]
    assert applied[0].expression == "smile"
    assert applied[1].emotion == "happy"
    assert applied[2].gesture == "wave"
    assert applied[3].expression is None
    assert all(
        request.public_metadata["boundary"] == "drc_rt7c"
        for request in applied
    )
    assert [item.order for item in result.command_results] == [1, 2, 3, 4]


def test_unsupported_required_intent_is_typed_and_not_applied(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    supported = set(FakeMotionIntent) - {FakeMotionIntent.EMOTION}
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            capability=FakeCapability(supported=supported)
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.UNSUPPORTED
    assert result.commands_applied == 1
    assert result.commands_completed == 1
    assert len(module.sessions[0].applied) == 1
    assert result.command_results[1].intent is FrameworkVtsMotionIntent.EMOTION
    assert result.command_results[1].skipped is False


def test_unsupported_stop_motion_is_optional_safe_degradation(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    supported = set(FakeMotionIntent) - {FakeMotionIntent.STOP_MOTION}
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            capability=FakeCapability(supported=supported)
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands(include_stop=True))

    assert (
        result.status
        is FrameworkVtsMotionExecutionStatus.COMPLETED_WITH_OPTIONAL_SKIP
    )
    assert result.commands_requested == 5
    assert result.commands_applied == 4
    assert result.commands_completed == 4
    assert result.optional_commands_skipped == 1
    assert result.command_results[-1].intent is FrameworkVtsMotionIntent.STOP_MOTION
    assert result.command_results[-1].skipped is True
    assert len(module.sessions[0].applied) == 4


@pytest.mark.parametrize(
    "intent",
    ["speaking_state", "idle_motion", "look_at"],
)
def test_unreleased_assumptions_are_rejected_by_model(
    intent: str,
) -> None:
    with pytest.raises(ValidationError):
        FrameworkVtsMotionCommand.model_validate(
            {
                "order": 1,
                "intent": intent,
            }
        )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "order": 1,
            "intent": "expression",
            "emotion": "happy",
        },
        {
            "order": 1,
            "intent": "reset_expression",
            "gesture": "wave",
        },
        {
            "order": 1,
            "intent": "gesture",
        },
    ],
)
def test_ambiguous_or_missing_command_payload_is_rejected(
    payload: dict[str, Any],
) -> None:
    with pytest.raises(ValidationError):
        FrameworkVtsMotionCommand.model_validate(payload)


def test_preflight_unavailable_stops_before_apply_and_closes(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            capability=FakeCapability(
                status="token_missing",
                supports_real_adapter=False,
            )
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    session = module.sessions[0]
    assert result.status is FrameworkVtsMotionExecutionStatus.UNAVAILABLE
    assert session.preflight_calls == 1
    assert session.applied == []
    assert session.close_calls == 1
    assert result.session_closed is True


def test_preflight_exception_is_normalized_and_session_closes(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    raw = "private-preflight-details"
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            preflight_error=RuntimeError(raw)
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.FAILED
    assert result.session_closed is True
    assert raw not in result.model_dump_json()


def test_apply_exception_is_normalized_and_session_closes(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    raw = "private-provider-payload"
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            apply_error=RuntimeError(raw)
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.FAILED
    assert result.session_closed is True
    assert result.commands_applied == 0
    assert raw not in result.model_dump_json()


def test_close_exception_returns_fixed_cleanup_failure(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    raw = "private-close-details"
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            close_error=RuntimeError(raw)
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.status is FrameworkVtsMotionExecutionStatus.FAILED
    assert result.reason_code == "framework_vts_motion_close_failed"
    assert result.session_closed is False
    assert raw not in result.model_dump_json()


def test_event_types_are_allowlisted_bounded_and_payload_free(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            event_burst=FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES * 2
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert len(result.event_types) == FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES
    assert "private.provider.event" not in result.event_types
    serialized = result.model_dump_json()
    assert "must-not-escape" not in serialized


def test_execution_markers_are_copied_only_as_booleans(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    result_metadata = {
        "provider_protocol_call_executed": True,
        "network_execution_attempted": True,
        "real_motion_executed": True,
        "authentication_token": "must-not-escape",
    }
    module = FakeFrameworkModule(
        module_file=framework_init,
        session_factory=lambda: FakeSession(
            results=[
                FakeMotionResult(public_metadata=result_metadata)
                for _ in range(4)
            ]
        ),
    )

    result = FrameworkVtsMotionSessionAdapter(
        _config(),
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    assert result.provider_execution_attempted is True
    assert result.network_execution_attempted is True
    assert result.real_motion_executed is True
    assert "must-not-escape" not in result.model_dump_json()


def test_private_config_rejects_non_boolean_execution_flags() -> None:
    invalid_values: tuple[Any, ...] = (
        "false",
        "true",
        1,
        0,
        None,
        object(),
    )
    for field_name in (
        "enabled",
        "allow_provider_execution",
        "runtime_available",
        "model_selected",
    ):
        for invalid in invalid_values:
            with pytest.raises(
                TypeError,
                match=rf"^{field_name} must be a literal bool$",
            ):
                FrameworkVtsMotionPrivateConfig(**{field_name: invalid})


def test_non_boolean_readiness_capability_fails_closed_before_apply(
    tmp_path: Path,
) -> None:
    cases = (
        ("supports_motion_session", "false"),
        ("supports_real_adapter", "false"),
    )
    for index, (field_name, value) in enumerate(cases):
        case_root = tmp_path / str(index)
        vendor_root, framework_init = _vendor(case_root)
        capability = FakeCapability()
        setattr(capability, field_name, value)
        module = FakeFrameworkModule(
            module_file=framework_init,
            session_factory=lambda capability=capability: FakeSession(
                capability=capability
            ),
        )

        result = FrameworkVtsMotionSessionAdapter(
            _config(),
            _module_context_factory=_module_context(module),
            _vendor_root=vendor_root,
        ).execute(_commands())

        session = module.sessions[0]
        assert result.status is FrameworkVtsMotionExecutionStatus.UNAVAILABLE
        assert session.applied == []
        assert session.close_calls == 1
        assert result.session_closed is True


def test_non_boolean_intent_capability_is_not_supported(
    tmp_path: Path,
) -> None:
    class CallableCapability(FakeCapability):
        def supports_intent(self, intent: FakeMotionIntent) -> Any:
            del intent
            return "false"

    class AttributeCapability(FakeCapability):
        supports_intent = None
        supports_expression = "false"

    for index, capability in enumerate(
        (CallableCapability(), AttributeCapability())
    ):
        case_root = tmp_path / str(index)
        vendor_root, framework_init = _vendor(case_root)
        module = FakeFrameworkModule(
            module_file=framework_init,
            session_factory=lambda capability=capability: FakeSession(
                capability=capability
            ),
        )

        result = FrameworkVtsMotionSessionAdapter(
            _config(),
            _module_context_factory=_module_context(module),
            _vendor_root=vendor_root,
        ).execute([_commands()[0]])

        session = module.sessions[0]
        assert result.status is FrameworkVtsMotionExecutionStatus.UNSUPPORTED
        assert session.applied == []
        assert result.command_results[0].outcome == "unsupported"


def test_retryable_requires_literal_true(tmp_path: Path) -> None:
    for index, (raw_retryable, expected) in enumerate(
        (("false", False), (True, True))
    ):
        case_root = tmp_path / str(index)
        vendor_root, framework_init = _vendor(case_root)
        module = FakeFrameworkModule(
            module_file=framework_init,
            session_factory=lambda raw_retryable=raw_retryable: FakeSession(
                results=[
                    FakeMotionResult(
                        outcome="failed",
                        public_error_code="provider_error",
                        retryable=raw_retryable,
                    )
                ]
            ),
        )

        result = FrameworkVtsMotionSessionAdapter(
            _config(),
            _module_context_factory=_module_context(module),
            _vendor_root=vendor_root,
        ).execute([_commands()[0]])

        assert result.status is FrameworkVtsMotionExecutionStatus.FAILED
        assert result.command_results[0].retryable is expected


def test_private_config_repr_and_result_do_not_expose_values(
    tmp_path: Path,
) -> None:
    config = _config()
    representation = repr(config)
    assert "loopback.test" not in representation
    assert "test-authentication-value" not in representation
    assert "test-expression-hotkey" not in representation

    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(module_file=framework_init)
    result = FrameworkVtsMotionSessionAdapter(
        config,
        _module_context_factory=_module_context(module),
        _vendor_root=vendor_root,
    ).execute(_commands())

    serialized = result.model_dump_json()
    assert "loopback.test" not in serialized
    assert "test-authentication-value" not in serialized
    assert "test-expression-hotkey" not in serialized


def test_command_order_must_be_contiguous(
    tmp_path: Path,
) -> None:
    vendor_root, framework_init = _vendor(tmp_path)
    module = FakeFrameworkModule(module_file=framework_init)
    commands = [
        FrameworkVtsMotionCommand(
            order=2,
            intent=FrameworkVtsMotionIntent.RESET_EXPRESSION,
        )
    ]

    with pytest.raises(ValueError, match="contiguous"):
        FrameworkVtsMotionSessionAdapter(
            _config(),
            _module_context_factory=_module_context(module),
            _vendor_root=vendor_root,
        ).execute(commands)


def test_source_contains_no_cwd_or_sys_path_workaround(
    tmp_path: Path,
) -> None:
    source_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "services"
        / "framework_vts_motion_session_adapter.py"
    )
    source = source_path.read_text(encoding="utf-8")
    assert "os.chdir" not in source
    assert "sys.path.insert" not in source
    assert "sys.path.append" not in source
    assert "sys.path.remove" not in source
    assert "FRAMEWORK_PROJECT_ROOT" not in source
    assert "FRAMEWORK_ROOT" not in source
    assert "import pyvts" not in source
    assert "import websockets" not in source
    assert "from framework." not in source

    vendor_root = tmp_path / "fixed-vendor"
    framework_dir = vendor_root / "framework"
    llm_dir = vendor_root / "llm"
    config_dir = vendor_root / "config"
    framework_dir.mkdir(parents=True)
    llm_dir.mkdir()
    config_dir.mkdir()

    (llm_dir / "base.py").write_text(
        'VENDOR_LLM_MARKER = "vendor-llm"\n',
        encoding="utf-8",
    )
    (config_dir / "prompt_builder.py").write_text(
        "def build_final_system_instruction():\n"
        '    return "vendor-config"\n',
        encoding="utf-8",
    )
    (framework_dir / "__init__.py").write_text(
        "from llm.base import VENDOR_LLM_MARKER\n"
        "from config.prompt_builder import build_final_system_instruction\n"
        "ROOT_PUBLIC_MARKER = (\n"
        "    VENDOR_LLM_MARKER,\n"
        "    build_final_system_instruction(),\n"
        ")\n",
        encoding="utf-8",
    )

    sentinel_llm = SimpleNamespace(source="outside")
    previous_llm = sys.modules.get("llm")
    had_llm = "llm" in sys.modules
    sys.modules["llm"] = sentinel_llm
    original_path = tuple(sys.path)
    original_cwd = Path.cwd()

    try:
        with _vendored_framework_root_public(vendor_root) as module:
            assert module.ROOT_PUBLIC_MARKER == (
                "vendor-llm",
                "vendor-config",
            )
            assert Path(module.__file__).resolve() == (
                framework_dir / "__init__.py"
            ).resolve()
            assert tuple(sys.path) == original_path
            assert Path.cwd() == original_cwd
        assert sys.modules.get("llm") is sentinel_llm
        assert "llm.base" not in sys.modules
        assert "config" not in sys.modules
        assert "config.prompt_builder" not in sys.modules
        assert tuple(sys.path) == original_path
        assert Path.cwd() == original_cwd
    finally:
        if had_llm:
            sys.modules["llm"] = previous_llm
        else:
            sys.modules.pop("llm", None)
