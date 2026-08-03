"""Guarded fixed-vendor FW v5.5.0 VTS motion-session adapter.

RT-7c owns only bounded command validation, fixed-vendor root-public loading,
session orchestration, capability branching, and public-safe normalization.
It does not read environment variables, discover another Framework checkout,
change cwd/sys.path, import Framework internals or pyvts, own a WebSocket, or
read/write token files.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
import importlib.util
from importlib.machinery import PathFinder
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, ContextManager
import math
import sys
import threading

from app.models.framework_vts_motion import (
    FRAMEWORK_VTS_MOTION_MAX_COMMANDS,
    FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES,
    FRAMEWORK_VTS_MOTION_MAX_RESULT_TEXT_CHARS,
    FrameworkVtsMotionCommand,
    FrameworkVtsMotionCommandResult,
    FrameworkVtsMotionExecutionResult,
    FrameworkVtsMotionExecutionStatus,
    FrameworkVtsMotionIntent,
)


FRAMEWORK_V550_VENDOR_RELATIVE = Path("vendor/ai-character-framework-5.5.0")
_FRAMEWORK_PACKAGE_NAME = "framework"
_FRAMEWORK_API_VERSION = "5.5.0"
_MAX_HOTKEY_BINDINGS = 256
_MAX_PRIVATE_TEXT_CHARS = 4096

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
        "configured",
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
_PROVIDER_ATTEMPT_KEYS = frozenset(
    {
        "provider_import_attempted",
        "provider_client_factory_invoked",
        "provider_client_created",
        "provider_protocol_call_executed",
    }
)
_NETWORK_ATTEMPT_KEYS = frozenset(
    {
        "network_execution_attempted",
        "connected",
        "authenticated",
    }
)
_FRAMEWORK_IMPORT_LOCK = threading.RLock()


FrameworkModuleContextFactory = Callable[[Path], ContextManager[ModuleType]]


@dataclass(frozen=True, slots=True)
class FrameworkVtsMotionPrivateConfig:
    """Explicit-only private VTS inputs for a later separately owned loader."""

    enabled: bool = False
    allow_provider_execution: bool = False
    runtime_available: bool = False
    model_selected: bool = False

    endpoint_host: str = field(default="", repr=False)
    endpoint_port: int | None = field(default=None, repr=False)
    authentication_token: str = field(default="", repr=False)
    hotkey_bindings: Mapping[str, str] = field(
        default_factory=dict,
        repr=False,
    )

    connect_timeout_seconds: float = 3.0
    authenticate_timeout_seconds: float = 3.0
    request_timeout_seconds: float = 3.0
    close_timeout_seconds: float = 2.0

    def __post_init__(self) -> None:
        """Normalize without reading environment, filesystem, or provider state."""

        endpoint_host = str(self.endpoint_host or "").strip()
        authentication_token = str(self.authentication_token or "").strip()

        if len(endpoint_host) > _MAX_PRIVATE_TEXT_CHARS:
            raise ValueError("endpoint_host is too long")
        if len(authentication_token) > _MAX_PRIVATE_TEXT_CHARS:
            raise ValueError("authentication_token is too long")

        port = self.endpoint_port
        if port is not None:
            if isinstance(port, bool):
                raise ValueError("endpoint_port must be an integer")
            try:
                port = int(port)
            except (TypeError, ValueError) as error:
                raise ValueError("endpoint_port must be an integer") from error
            if not 1 <= port <= 65535:
                raise ValueError("endpoint_port must be between 1 and 65535")

        bindings = dict(self.hotkey_bindings)
        if len(bindings) > _MAX_HOTKEY_BINDINGS:
            raise ValueError("hotkey_bindings contains too many entries")
        normalized_bindings: dict[str, str] = {}
        for raw_selector, raw_hotkey in bindings.items():
            if not isinstance(raw_selector, str) or not isinstance(raw_hotkey, str):
                raise TypeError("hotkey_bindings must contain string pairs")
            selector = raw_selector.strip()
            hotkey = raw_hotkey.strip()
            if not selector or not hotkey:
                raise ValueError("hotkey_bindings cannot contain blank values")
            if (
                len(selector) > _MAX_PRIVATE_TEXT_CHARS
                or len(hotkey) > _MAX_PRIVATE_TEXT_CHARS
            ):
                raise ValueError("hotkey_bindings contains an oversized value")
            normalized_bindings[selector] = hotkey

        for field_name in (
            "connect_timeout_seconds",
            "authenticate_timeout_seconds",
            "request_timeout_seconds",
            "close_timeout_seconds",
        ):
            value = float(getattr(self, field_name))
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{field_name} must be finite and positive")
            object.__setattr__(self, field_name, value)

        object.__setattr__(self, "enabled", bool(self.enabled))
        object.__setattr__(
            self,
            "allow_provider_execution",
            bool(self.allow_provider_execution),
        )
        object.__setattr__(
            self,
            "runtime_available",
            bool(self.runtime_available),
        )
        object.__setattr__(self, "model_selected", bool(self.model_selected))
        object.__setattr__(self, "endpoint_host", endpoint_host)
        object.__setattr__(self, "endpoint_port", port)
        object.__setattr__(
            self,
            "authentication_token",
            authentication_token,
        )
        object.__setattr__(
            self,
            "hotkey_bindings",
            MappingProxyType(normalized_bindings),
        )


class FrameworkVtsMotionSessionAdapter:
    """Execute one bounded command list through the fixed vendored FW root."""

    def __init__(
        self,
        config: FrameworkVtsMotionPrivateConfig,
        *,
        _module_context_factory: FrameworkModuleContextFactory | None = None,
        _vendor_root: Path | None = None,
    ) -> None:
        if not isinstance(config, FrameworkVtsMotionPrivateConfig):
            raise TypeError("config must be FrameworkVtsMotionPrivateConfig")
        self._config = config
        self._module_context_factory = (
            _module_context_factory or _vendored_framework_root_public
        )
        self._vendor_root_override = _vendor_root

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def execute(
        self,
        commands: Sequence[FrameworkVtsMotionCommand],
    ) -> FrameworkVtsMotionExecutionResult:
        """Execute explicit commands or return a typed closed-guard result."""

        normalized_commands = _validate_commands(commands)

        if not self._config.enabled:
            return self._result(
                status=FrameworkVtsMotionExecutionStatus.DISABLED,
                commands_requested=len(normalized_commands),
                reason_code="framework_vts_motion_disabled",
                safe_message="Framework VTS motion execution is disabled.",
            )

        if not self._config.allow_provider_execution:
            return self._result(
                status=(
                    FrameworkVtsMotionExecutionStatus
                    .PROVIDER_EXECUTION_NOT_ALLOWED
                ),
                commands_requested=len(normalized_commands),
                real_adapter_enabled=True,
                reason_code="provider_execution_not_allowed",
                safe_message="Framework VTS provider execution is not allowed.",
            )

        vendor_root = self._resolve_vendor_root()
        if vendor_root is None:
            return self._result(
                status=FrameworkVtsMotionExecutionStatus.UNAVAILABLE,
                commands_requested=len(normalized_commands),
                real_adapter_enabled=True,
                provider_execution_allowed=True,
                reason_code="framework_v550_vendor_missing",
                safe_message="The fixed Framework v5.5.0 vendor is unavailable.",
            )

        event_types: list[str] = []
        command_results: list[FrameworkVtsMotionCommandResult] = []
        commands_applied = 0
        commands_completed = 0
        optional_commands_skipped = 0
        session: Any | None = None
        framework_import_attempted = False
        session_created = False
        session_closed = False
        provider_execution_attempted = False
        network_execution_attempted = False
        real_motion_executed = False
        status = FrameworkVtsMotionExecutionStatus.FAILED
        reason_code = "framework_vts_motion_failed"
        safe_message = "Framework VTS motion execution failed."

        try:
            framework_import_attempted = True
            with self._module_context_factory(vendor_root) as framework:
                public_api = _FrameworkMotionPublicApi.from_module(
                    framework,
                    vendor_root=vendor_root,
                )
                session = public_api.create_motion_session(
                    adapter="vts",
                    real_adapter_enabled=True,
                    allow_provider_execution=True,
                    runtime_available=self._config.runtime_available,
                    model_selected=self._config.model_selected,
                    vts_endpoint_host=self._config.endpoint_host,
                    vts_endpoint_port=self._config.endpoint_port,
                    vts_authentication_token=(
                        self._config.authentication_token
                    ),
                    vts_hotkey_bindings=dict(self._config.hotkey_bindings),
                    vts_connect_timeout_seconds=(
                        self._config.connect_timeout_seconds
                    ),
                    vts_authenticate_timeout_seconds=(
                        self._config.authenticate_timeout_seconds
                    ),
                    vts_request_timeout_seconds=(
                        self._config.request_timeout_seconds
                    ),
                    vts_close_timeout_seconds=(
                        self._config.close_timeout_seconds
                    ),
                    public_metadata={
                        "boundary": "drc_rt7c",
                        "mode": "guarded_vts",
                    },
                )
                if session is None:
                    raise RuntimeError("Framework motion session was not created")
                session_created = True
                _register_event_observer(session, event_types)

                capability = _preflight(session)
                (
                    provider_execution_attempted,
                    network_execution_attempted,
                    real_motion_executed,
                ) = _merge_execution_markers(
                    capability,
                    provider_execution_attempted,
                    network_execution_attempted,
                    real_motion_executed,
                )

                if not _is_ready_real_vts_capability(capability):
                    status = _status_for_capability(capability)
                    reason_code = "framework_vts_preflight_unavailable"
                    safe_message = "Framework VTS motion capability is unavailable."
                else:
                    status = FrameworkVtsMotionExecutionStatus.COMPLETED
                    reason_code = "framework_vts_motion_completed"
                    safe_message = "Framework VTS motion commands completed."

                    for command in normalized_commands:
                        if not _supports_command(
                            public_api,
                            capability,
                            command.intent,
                        ):
                            result = _unsupported_command_result(command)
                            command_results.append(result)
                            if (
                                command.intent
                                is FrameworkVtsMotionIntent.STOP_MOTION
                            ):
                                optional_commands_skipped += 1
                                status = (
                                    FrameworkVtsMotionExecutionStatus
                                    .COMPLETED_WITH_OPTIONAL_SKIP
                                )
                                reason_code = (
                                    "framework_vts_optional_stop_unsupported"
                                )
                                safe_message = (
                                    "Required VTS motion commands completed; "
                                    "optional stop motion was unavailable."
                                )
                                continue

                            status = FrameworkVtsMotionExecutionStatus.UNSUPPORTED
                            reason_code = (
                                "framework_vts_required_intent_unsupported"
                            )
                            safe_message = (
                                "A required Framework VTS motion intent is "
                                "unsupported."
                            )
                            break

                        request = _convert_command(public_api, command)
                        raw_result = _apply_motion(session, request)
                        commands_applied += 1
                        normalized_result = _normalize_command_result(
                            command,
                            raw_result,
                        )
                        command_results.append(normalized_result)
                        (
                            provider_execution_attempted,
                            network_execution_attempted,
                            real_motion_executed,
                        ) = _merge_execution_markers(
                            raw_result,
                            provider_execution_attempted,
                            network_execution_attempted,
                            real_motion_executed,
                        )

                        if normalized_result.outcome != "completed":
                            status = _status_for_non_completed(
                                normalized_result.outcome
                            )
                            reason_code = (
                                "framework_vts_motion_non_completed"
                            )
                            safe_message = (
                                "A Framework VTS motion command did not "
                                "complete."
                            )
                            break
                        commands_completed += 1

        except Exception:
            status = FrameworkVtsMotionExecutionStatus.FAILED
            reason_code = "framework_vts_motion_failed"
            safe_message = "Framework VTS motion execution failed."
        finally:
            if session_created and session is not None:
                try:
                    close = getattr(session, "close", None)
                    if not callable(close):
                        raise RuntimeError(
                            "Framework motion session has no close method"
                        )
                    close()
                    session_closed = True
                except Exception:
                    session_closed = False
                    status = FrameworkVtsMotionExecutionStatus.FAILED
                    reason_code = "framework_vts_motion_close_failed"
                    safe_message = (
                        "Framework VTS motion session cleanup failed."
                    )

        return self._result(
            status=status,
            commands_requested=len(normalized_commands),
            commands_applied=commands_applied,
            commands_completed=commands_completed,
            optional_commands_skipped=optional_commands_skipped,
            command_results=command_results,
            event_types=event_types,
            framework_import_attempted=framework_import_attempted,
            session_created=session_created,
            session_closed=session_closed,
            real_adapter_enabled=True,
            provider_execution_allowed=True,
            provider_execution_attempted=provider_execution_attempted,
            network_execution_attempted=network_execution_attempted,
            real_motion_executed=real_motion_executed,
            reason_code=reason_code,
            safe_message=safe_message,
        )

    def _resolve_vendor_root(self) -> Path | None:
        root = (
            self._vendor_root_override
            if self._vendor_root_override is not None
            else _repository_root() / FRAMEWORK_V550_VENDOR_RELATIVE
        )
        try:
            resolved = Path(root).resolve()
        except (OSError, RuntimeError, ValueError):
            return None
        framework_init = resolved / "framework" / "__init__.py"
        if not resolved.is_dir() or not framework_init.is_file():
            return None
        return resolved

    @staticmethod
    def _result(
        *,
        status: FrameworkVtsMotionExecutionStatus,
        commands_requested: int,
        commands_applied: int = 0,
        commands_completed: int = 0,
        optional_commands_skipped: int = 0,
        command_results: list[FrameworkVtsMotionCommandResult] | None = None,
        event_types: list[str] | None = None,
        framework_import_attempted: bool = False,
        session_created: bool = False,
        session_closed: bool = False,
        real_adapter_enabled: bool = False,
        provider_execution_allowed: bool = False,
        provider_execution_attempted: bool = False,
        network_execution_attempted: bool = False,
        real_motion_executed: bool = False,
        reason_code: str,
        safe_message: str,
    ) -> FrameworkVtsMotionExecutionResult:
        return FrameworkVtsMotionExecutionResult(
            status=status,
            commands_requested=commands_requested,
            commands_applied=commands_applied,
            commands_completed=commands_completed,
            optional_commands_skipped=optional_commands_skipped,
            command_results=list(command_results or []),
            event_types=list(event_types or [])[
                :FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES
            ],
            framework_import_attempted=framework_import_attempted,
            session_created=session_created,
            session_closed=session_closed,
            adapter="vts",
            real_adapter_enabled=real_adapter_enabled,
            provider_execution_allowed=provider_execution_allowed,
            provider_execution_attempted=provider_execution_attempted,
            network_execution_attempted=network_execution_attempted,
            real_motion_executed=real_motion_executed,
            reason_code=reason_code,
            safe_message=safe_message[
                :FRAMEWORK_VTS_MOTION_MAX_RESULT_TEXT_CHARS
            ],
        )


class _FrameworkMotionPublicApi:
    """Validated references from the fixed vendored Framework root facade."""

    def __init__(
        self,
        *,
        create_motion_session: Any,
        motion_request: Any,
        motion_intent: Any,
    ) -> None:
        self.create_motion_session = create_motion_session
        self.motion_request = motion_request
        self.motion_intent = motion_intent

    @classmethod
    def from_module(
        cls,
        module: ModuleType | Any,
        *,
        vendor_root: Path,
    ) -> "_FrameworkMotionPublicApi":
        expected_init = (
            vendor_root / "framework" / "__init__.py"
        ).resolve()
        module_file = getattr(module, "__file__", None)
        if module_file is None:
            raise RuntimeError("Framework root-public module has no origin")
        try:
            origin = Path(module_file).resolve()
        except (OSError, RuntimeError, ValueError) as error:
            raise RuntimeError(
                "Framework root-public module origin is invalid"
            ) from error
        if origin != expected_init:
            raise RuntimeError(
                "Framework root-public module origin is outside the fixed vendor"
            )

        create_motion_session = getattr(
            module,
            "create_motion_session",
            None,
        )
        motion_request = getattr(module, "MotionRequest", None)
        motion_intent = getattr(module, "MotionIntent", None)
        motion_session_info = getattr(module, "MotionSessionInfo", None)

        if not callable(create_motion_session):
            raise RuntimeError(
                "Framework root-public create_motion_session is unavailable"
            )
        if motion_request is None or motion_intent is None:
            raise RuntimeError(
                "Framework root-public motion request types are unavailable"
            )
        if motion_session_info is None:
            raise RuntimeError(
                "Framework root-public MotionSessionInfo is unavailable"
            )
        api_version = getattr(motion_session_info(), "api_version", None)
        if api_version != _FRAMEWORK_API_VERSION:
            raise RuntimeError("Unexpected Framework motion API version")

        return cls(
            create_motion_session=create_motion_session,
            motion_request=motion_request,
            motion_intent=motion_intent,
        )


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _validate_commands(
    commands: Sequence[FrameworkVtsMotionCommand],
) -> tuple[FrameworkVtsMotionCommand, ...]:
    if isinstance(commands, (str, bytes)) or not isinstance(commands, Sequence):
        raise TypeError("commands must be a sequence")
    normalized = tuple(commands)
    if not normalized:
        raise ValueError("commands must not be empty")
    if len(normalized) > FRAMEWORK_VTS_MOTION_MAX_COMMANDS:
        raise ValueError("commands contains too many entries")
    if any(
        not isinstance(command, FrameworkVtsMotionCommand)
        for command in normalized
    ):
        raise TypeError("commands must contain FrameworkVtsMotionCommand")
    orders = [command.order for command in normalized]
    if orders != list(range(1, len(normalized) + 1)):
        raise ValueError("commands must use contiguous one-based order")
    return normalized


def _convert_command(
    public_api: _FrameworkMotionPublicApi,
    command: FrameworkVtsMotionCommand,
) -> Any:
    metadata = {
        "boundary": "drc_rt7c",
        "command_order": command.order,
        "drc_intent": command.intent.value,
    }
    request_type = public_api.motion_request

    if command.intent is FrameworkVtsMotionIntent.EXPRESSION:
        return request_type.expression_change(
            command.expression,
            character_id=command.character_id,
            public_metadata=metadata,
        )
    if command.intent is FrameworkVtsMotionIntent.EMOTION:
        return request_type.emotion_update(
            command.emotion,
            character_id=command.character_id,
            public_metadata=metadata,
        )
    if command.intent is FrameworkVtsMotionIntent.GESTURE:
        return request_type(
            intent=public_api.motion_intent.GESTURE,
            gesture=command.gesture,
            character_id=command.character_id,
            public_metadata=metadata,
        )
    if command.intent is FrameworkVtsMotionIntent.RESET_EXPRESSION:
        return request_type(
            intent=public_api.motion_intent.RESET_EXPRESSION,
            character_id=command.character_id,
            public_metadata=metadata,
        )
    if command.intent is FrameworkVtsMotionIntent.STOP_MOTION:
        return request_type.stop_motion(
            character_id=command.character_id,
            public_metadata=metadata,
        )
    raise RuntimeError("Unsupported DRC VTS motion command intent")


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


def _register_event_observer(
    session: Any,
    event_types: list[str],
) -> None:
    on_event = getattr(session, "on_event", None)
    if not callable(on_event):
        raise RuntimeError(
            "Framework motion session has no event registration method"
        )

    def observe(payload: Any) -> None:
        if len(event_types) >= FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES:
            return
        event_type = (
            payload.get("type")
            if isinstance(payload, Mapping)
            else None
        )
        if (
            isinstance(event_type, str)
            and event_type in _ALLOWED_EVENT_TYPES
        ):
            event_types.append(event_type)

    on_event(observe)


def _is_ready_real_vts_capability(capability: Any) -> bool:
    return (
        _enum_text(getattr(capability, "adapter_status", ""))
        == "configured"
        and bool(getattr(capability, "supports_motion_session", False))
        and bool(getattr(capability, "supports_real_adapter", False))
    )


def _status_for_capability(
    capability: Any,
) -> FrameworkVtsMotionExecutionStatus:
    status = _enum_text(getattr(capability, "adapter_status", ""))
    if status == "provider_execution_not_allowed":
        return (
            FrameworkVtsMotionExecutionStatus
            .PROVIDER_EXECUTION_NOT_ALLOWED
        )
    return FrameworkVtsMotionExecutionStatus.UNAVAILABLE


def _supports_command(
    public_api: _FrameworkMotionPublicApi,
    capability: Any,
    intent: FrameworkVtsMotionIntent,
) -> bool:
    public_intent = {
        FrameworkVtsMotionIntent.EXPRESSION:
            public_api.motion_intent.EXPRESSION,
        FrameworkVtsMotionIntent.EMOTION:
            public_api.motion_intent.EMOTION,
        FrameworkVtsMotionIntent.GESTURE:
            public_api.motion_intent.GESTURE,
        FrameworkVtsMotionIntent.RESET_EXPRESSION:
            public_api.motion_intent.RESET_EXPRESSION,
        FrameworkVtsMotionIntent.STOP_MOTION:
            public_api.motion_intent.STOP_MOTION,
    }[intent]

    supports_intent = getattr(capability, "supports_intent", None)
    if callable(supports_intent):
        return bool(supports_intent(public_intent))

    attribute = {
        FrameworkVtsMotionIntent.EXPRESSION: "supports_expression",
        FrameworkVtsMotionIntent.EMOTION: "supports_emotion",
        FrameworkVtsMotionIntent.GESTURE: "supports_gesture",
        FrameworkVtsMotionIntent.RESET_EXPRESSION:
            "supports_reset_expression",
        FrameworkVtsMotionIntent.STOP_MOTION: "supports_stop_motion",
    }[intent]
    return bool(getattr(capability, attribute, False))


def _unsupported_command_result(
    command: FrameworkVtsMotionCommand,
) -> FrameworkVtsMotionCommandResult:
    optional = command.intent is FrameworkVtsMotionIntent.STOP_MOTION
    return FrameworkVtsMotionCommandResult(
        order=command.order,
        intent=command.intent,
        outcome="unsupported",
        state="unavailable",
        adapter_status="configured",
        public_error_code="unsupported",
        retryable=False,
        skipped=optional,
        safe_message=(
            "Optional stop motion is unsupported."
            if optional
            else "Required VTS motion intent is unsupported."
        ),
    )


def _normalize_command_result(
    command: FrameworkVtsMotionCommand,
    raw_result: Any,
) -> FrameworkVtsMotionCommandResult:
    outcome = _allowlisted_enum_text(
        getattr(raw_result, "outcome", "failed"),
        allowed=_ALLOWED_OUTCOMES,
        fallback="failed",
    )
    safe_message = ""
    if outcome != "completed":
        safe_message = "Framework VTS motion command did not complete."
    return FrameworkVtsMotionCommandResult(
        order=command.order,
        intent=command.intent,
        outcome=outcome,
        state=_allowlisted_enum_text(
            getattr(raw_result, "state", "unavailable"),
            allowed=_ALLOWED_STATES,
            fallback="unavailable",
        ),
        adapter_status=_allowlisted_enum_text(
            getattr(raw_result, "adapter_status", "configured"),
            allowed=_ALLOWED_ADAPTER_STATUSES,
            fallback="configured",
        ),
        public_error_code=_allowlisted_enum_text(
            getattr(raw_result, "public_error_code", "provider_error"),
            allowed=_ALLOWED_ERROR_CODES,
            fallback="provider_error",
        ),
        retryable=bool(getattr(raw_result, "retryable", False)),
        skipped=False,
        safe_message=safe_message,
    )


def _status_for_non_completed(
    outcome: str,
) -> FrameworkVtsMotionExecutionStatus:
    if outcome == "unsupported":
        return FrameworkVtsMotionExecutionStatus.UNSUPPORTED
    if outcome in {
        "unavailable",
        "not_configured",
        "not_implemented",
        "closed",
    }:
        return FrameworkVtsMotionExecutionStatus.UNAVAILABLE
    return FrameworkVtsMotionExecutionStatus.FAILED


def _enum_text(value: Any) -> str:
    raw = getattr(value, "value", value)
    return str(raw or "")[:64]


def _allowlisted_enum_text(
    value: Any,
    *,
    allowed: frozenset[str],
    fallback: str,
) -> str:
    text = _enum_text(value)
    return text if text in allowed else fallback


def _merge_execution_markers(
    source: Any,
    provider_attempted: bool,
    network_attempted: bool,
    real_motion_executed: bool,
) -> tuple[bool, bool, bool]:
    metadata = getattr(source, "public_metadata", None)
    if not isinstance(metadata, Mapping):
        return (
            provider_attempted,
            network_attempted,
            real_motion_executed,
        )
    provider_attempted = provider_attempted or any(
        metadata.get(key) is True for key in _PROVIDER_ATTEMPT_KEYS
    )
    network_attempted = network_attempted or any(
        metadata.get(key) is True for key in _NETWORK_ATTEMPT_KEYS
    )
    real_motion_executed = (
        real_motion_executed
        or metadata.get("real_motion_executed") is True
    )
    return (
        provider_attempted,
        network_attempted,
        real_motion_executed,
    )


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        resolved = path.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def _fixed_vendor_importable_roots(vendor_root: Path) -> frozenset[str]:
    """Return non-stdlib top-level module names physically present in vendor."""

    roots = {_FRAMEWORK_PACKAGE_NAME}
    stdlib_names = frozenset(getattr(sys, "stdlib_module_names", ()))
    try:
        children = tuple(vendor_root.iterdir())
    except OSError as error:
        raise RuntimeError("Could not inspect the fixed Framework vendor") from error

    for child in children:
        name: str | None = None
        if child.is_file() and child.suffix == ".py":
            name = child.stem
        elif child.is_dir():
            name = child.name
        if (
            name
            and name.isidentifier()
            and name not in stdlib_names
            and name != "app"
        ):
            roots.add(name)
    return frozenset(roots)


class _FixedVendorTopLevelFinder:
    """Resolve vendor-owned top-level packages without changing sys.path."""

    def __init__(
        self,
        vendor_root: Path,
        managed_roots: frozenset[str],
    ) -> None:
        self._vendor_root = vendor_root.resolve()
        self._managed_roots = managed_roots

    def find_spec(
        self,
        fullname: str,
        path: object | None = None,
        target: object | None = None,
    ) -> Any | None:
        del target
        root_name = fullname.partition(".")[0]
        if path is not None or fullname != root_name:
            return None
        if root_name not in self._managed_roots:
            return None

        spec = PathFinder.find_spec(fullname, [str(self._vendor_root)])
        if spec is None:
            return None

        origin = getattr(spec, "origin", None)
        if origin not in {None, "namespace"}:
            if not _path_is_within(Path(origin), self._vendor_root):
                raise RuntimeError(
                    "Fixed-vendor import resolver produced an outside origin"
                )

        locations = getattr(spec, "submodule_search_locations", None)
        if locations is not None:
            for location in locations:
                if not _path_is_within(Path(location), self._vendor_root):
                    raise RuntimeError(
                        "Fixed-vendor package search location escaped vendor"
                    )
        return spec


def _assert_vendor_module_origins(
    *,
    vendor_root: Path,
    managed_roots: frozenset[str],
) -> None:
    """Ensure every temporarily managed import resolves inside fixed vendor."""

    for name, module in tuple(sys.modules.items()):
        if name.partition(".")[0] not in managed_roots:
            continue

        module_file = getattr(module, "__file__", None)
        if module_file is not None:
            if not _path_is_within(Path(module_file), vendor_root):
                raise RuntimeError(
                    "A managed Framework import resolved outside fixed vendor"
                )
            continue

        package_paths = getattr(module, "__path__", None)
        if package_paths is None:
            raise RuntimeError("A managed Framework import has no public origin")
        for package_path in package_paths:
            if not _path_is_within(Path(package_path), vendor_root):
                raise RuntimeError(
                    "A managed Framework package path escaped fixed vendor"
                )


@contextmanager
def _vendored_framework_root_public(
    vendor_root: Path,
) -> Iterator[ModuleType]:
    """Load the fixed root facade with a bounded vendor-only import resolver.

    The released root facade uses absolute imports for sibling top-level
    packages such as ``llm`` and ``config``. This context resolves only names
    physically present under the fixed vendor, without changing cwd or sys.path.
    """

    vendor_root = vendor_root.resolve()
    framework_init = (
        vendor_root / "framework" / "__init__.py"
    ).resolve()
    framework_dir = framework_init.parent
    managed_roots = _fixed_vendor_importable_roots(vendor_root)

    with _FRAMEWORK_IMPORT_LOCK:
        previous_modules = {
            name: module
            for name, module in tuple(sys.modules.items())
            if name.partition(".")[0] in managed_roots
        }
        for name in previous_modules:
            sys.modules.pop(name, None)

        finder = _FixedVendorTopLevelFinder(
            vendor_root,
            managed_roots,
        )
        sys.meta_path.insert(0, finder)

        spec = importlib.util.spec_from_file_location(
            _FRAMEWORK_PACKAGE_NAME,
            framework_init,
            submodule_search_locations=[str(framework_dir)],
        )
        if spec is None or spec.loader is None:
            raise RuntimeError(
                "Could not load the fixed Framework root-public package"
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules[_FRAMEWORK_PACKAGE_NAME] = module
        try:
            spec.loader.exec_module(module)
            _assert_vendor_module_origins(
                vendor_root=vendor_root,
                managed_roots=managed_roots,
            )
            yield module
        finally:
            try:
                sys.meta_path.remove(finder)
            except ValueError:
                pass

            for name in tuple(sys.modules):
                if name.partition(".")[0] in managed_roots:
                    sys.modules.pop(name, None)
            sys.modules.update(previous_modules)
