"""DRC-owned bounded models for guarded FW v5.5.0 VTS motion execution.

RT-7c keeps private endpoint, authentication, hotkey, model, provider payload,
Framework identifier, and raw exception values outside these models.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


FRAMEWORK_VTS_MOTION_MAX_COMMANDS = 5
FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES = 16
FRAMEWORK_VTS_MOTION_MAX_ID_CHARS = 128
FRAMEWORK_VTS_MOTION_MAX_RESULT_TEXT_CHARS = 256
FRAMEWORK_VTS_MOTION_MAX_ENUM_TEXT_CHARS = 64


class FrameworkVtsMotionIntent(str, Enum):
    """Released v5.5.0 VTS intent vocabulary accepted by DRC RT-7c."""

    EXPRESSION = "expression"
    EMOTION = "emotion"
    GESTURE = "gesture"
    RESET_EXPRESSION = "reset_expression"
    STOP_MOTION = "stop_motion"


class FrameworkVtsMotionCommand(BaseModel):
    """One ordered provider-neutral command for the guarded VTS adapter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    order: int = Field(ge=1, le=FRAMEWORK_VTS_MOTION_MAX_COMMANDS)
    intent: FrameworkVtsMotionIntent
    expression: str | None = Field(
        default=None, max_length=FRAMEWORK_VTS_MOTION_MAX_ID_CHARS
    )
    emotion: str | None = Field(
        default=None, max_length=FRAMEWORK_VTS_MOTION_MAX_ID_CHARS
    )
    gesture: str | None = Field(
        default=None, max_length=FRAMEWORK_VTS_MOTION_MAX_ID_CHARS
    )
    character_id: str | None = Field(
        default=None, max_length=FRAMEWORK_VTS_MOTION_MAX_ID_CHARS
    )

    @model_validator(mode="after")
    def validate_intent_payload(self) -> "FrameworkVtsMotionCommand":
        """Reject unsupported or ambiguous payload shapes before Framework use."""

        payloads = {
            FrameworkVtsMotionIntent.EXPRESSION: self.expression,
            FrameworkVtsMotionIntent.EMOTION: self.emotion,
            FrameworkVtsMotionIntent.GESTURE: self.gesture,
        }
        supplied = [
            value
            for value in (self.expression, self.emotion, self.gesture)
            if value is not None
        ]

        if self.intent in payloads:
            expected = payloads[self.intent]
            if expected is None or not expected.strip() or len(supplied) != 1:
                raise ValueError(
                    f"{self.intent.value} command requires exactly its matching payload"
                )
        elif supplied:
            raise ValueError(
                f"{self.intent.value} command cannot carry expression/emotion/gesture"
            )

        return self


class FrameworkVtsMotionExecutionStatus(str, Enum):
    """Aggregate result for one guarded RT-7c execution."""

    COMPLETED = "completed"
    COMPLETED_WITH_OPTIONAL_SKIP = "completed_with_optional_skip"
    DISABLED = "disabled"
    PROVIDER_EXECUTION_NOT_ALLOWED = "provider_execution_not_allowed"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class FrameworkVtsMotionCommandResult(BaseModel):
    """Bounded normalized result for one command."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    order: int = Field(ge=1, le=FRAMEWORK_VTS_MOTION_MAX_COMMANDS)
    intent: FrameworkVtsMotionIntent
    outcome: str = Field(max_length=FRAMEWORK_VTS_MOTION_MAX_ENUM_TEXT_CHARS)
    state: str = Field(max_length=FRAMEWORK_VTS_MOTION_MAX_ENUM_TEXT_CHARS)
    adapter_status: str = Field(max_length=FRAMEWORK_VTS_MOTION_MAX_ENUM_TEXT_CHARS)
    public_error_code: str = Field(max_length=FRAMEWORK_VTS_MOTION_MAX_ENUM_TEXT_CHARS)
    retryable: bool = False
    skipped: bool = False
    safe_message: str = Field(
        default="", max_length=FRAMEWORK_VTS_MOTION_MAX_RESULT_TEXT_CHARS
    )


class FrameworkVtsMotionExecutionResult(BaseModel):
    """Public-safe aggregate result without private VTS or Framework identifiers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "drc.v3.framework-vts-motion-execution.1"
    status: FrameworkVtsMotionExecutionStatus

    commands_requested: int = Field(ge=0, le=FRAMEWORK_VTS_MOTION_MAX_COMMANDS)
    commands_applied: int = Field(ge=0, le=FRAMEWORK_VTS_MOTION_MAX_COMMANDS)
    commands_completed: int = Field(ge=0, le=FRAMEWORK_VTS_MOTION_MAX_COMMANDS)
    optional_commands_skipped: int = Field(
        ge=0, le=FRAMEWORK_VTS_MOTION_MAX_COMMANDS
    )
    command_results: list[FrameworkVtsMotionCommandResult] = Field(
        default_factory=list,
        max_length=FRAMEWORK_VTS_MOTION_MAX_COMMANDS,
    )
    event_types: list[str] = Field(
        default_factory=list,
        max_length=FRAMEWORK_VTS_MOTION_MAX_EVENT_TYPES,
    )

    framework_import_attempted: bool = False
    session_created: bool = False
    session_closed: bool = False

    adapter: str = "vts"
    real_adapter_enabled: bool = False
    provider_execution_allowed: bool = False
    provider_execution_attempted: bool = False
    network_execution_attempted: bool = False
    real_motion_executed: bool = False

    reason_code: str = Field(max_length=FRAMEWORK_VTS_MOTION_MAX_ENUM_TEXT_CHARS)
    safe_message: str = Field(
        default="", max_length=FRAMEWORK_VTS_MOTION_MAX_RESULT_TEXT_CHARS
    )

    @model_validator(mode="after")
    def validate_execution_shape(self) -> "FrameworkVtsMotionExecutionResult":
        """Reject inconsistent or unsafe aggregate claims."""

        if self.adapter != "vts":
            raise ValueError("RT-7c result adapter must remain vts")
        if self.commands_applied > self.commands_requested:
            raise ValueError("commands_applied cannot exceed commands_requested")
        if self.commands_completed > self.commands_applied:
            raise ValueError("commands_completed cannot exceed commands_applied")
        if self.optional_commands_skipped > self.commands_requested:
            raise ValueError(
                "optional_commands_skipped cannot exceed commands_requested"
            )
        if len(self.command_results) > self.commands_requested:
            raise ValueError("command_results cannot exceed commands_requested")

        orders = [result.order for result in self.command_results]
        if orders != list(range(1, len(self.command_results) + 1)):
            raise ValueError("command results must use contiguous one-based order")

        if not self.real_adapter_enabled and (
            self.provider_execution_attempted
            or self.network_execution_attempted
            or self.real_motion_executed
        ):
            raise ValueError("execution claims require an enabled real adapter")
        if not self.provider_execution_allowed and (
            self.provider_execution_attempted
            or self.network_execution_attempted
            or self.real_motion_executed
        ):
            raise ValueError("execution claims require provider execution opt-in")
        if self.real_motion_executed and not self.network_execution_attempted:
            raise ValueError("real motion execution requires network execution")

        if self.status in {
            FrameworkVtsMotionExecutionStatus.DISABLED,
            FrameworkVtsMotionExecutionStatus.PROVIDER_EXECUTION_NOT_ALLOWED,
        }:
            if (
                self.framework_import_attempted
                or self.session_created
                or self.session_closed
                or self.commands_applied
                or self.command_results
            ):
                raise ValueError("closed guards cannot touch Framework or commands")

        if self.status is FrameworkVtsMotionExecutionStatus.COMPLETED:
            if self.commands_requested == 0:
                raise ValueError("completed execution requires commands")
            if self.commands_completed != self.commands_requested:
                raise ValueError("completed execution requires every command completed")
            if self.optional_commands_skipped != 0:
                raise ValueError("completed execution cannot contain optional skips")
            if not self.session_created or not self.session_closed:
                raise ValueError("completed execution requires closed session")
        elif (
            self.status
            is FrameworkVtsMotionExecutionStatus.COMPLETED_WITH_OPTIONAL_SKIP
        ):
            if self.optional_commands_skipped == 0:
                raise ValueError(
                    "completed_with_optional_skip requires an optional skip"
                )
            if self.commands_completed + self.optional_commands_skipped != (
                self.commands_requested
            ):
                raise ValueError(
                    "completed_with_optional_skip must account for every command"
                )
            if not self.session_created or not self.session_closed:
                raise ValueError(
                    "completed_with_optional_skip requires closed session"
                )

        return self
