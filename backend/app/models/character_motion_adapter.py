"""DRC-owned results for guarded FW mock motion execution.

RT-6c normalizes released Framework root-public motion results into bounded
application models. Raw Framework objects, identifiers, metadata mappings,
private paths, credentials, provider payloads, and exception text are never
retained by these contracts.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.character_motion import (
    CHARACTER_MOTION_MAX_COMMANDS,
    CHARACTER_MOTION_MAX_ID_CHARS,
    CharacterMotionCommandIntent,
    CharacterMotionCue,
    CharacterMotionLifecycleFact,
)


FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES = 12
FRAMEWORK_MOCK_MOTION_MAX_RESULT_TEXT_CHARS = 256
FRAMEWORK_MOCK_MOTION_MAX_ENUM_TEXT_CHARS = 64


class FrameworkMockMotionExecutionStatus(str, Enum):
    """Application-owned aggregate status for one bounded adapter execution."""

    COMPLETED = "completed"
    IGNORED = "ignored"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


class FrameworkMockMotionCommandResult(BaseModel):
    """Bounded normalized outcome for one applied command."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    order: int = Field(ge=1, le=CHARACTER_MOTION_MAX_COMMANDS)
    intent: CharacterMotionCommandIntent
    outcome: str = Field(max_length=FRAMEWORK_MOCK_MOTION_MAX_ENUM_TEXT_CHARS)
    state: str = Field(max_length=FRAMEWORK_MOCK_MOTION_MAX_ENUM_TEXT_CHARS)
    adapter_status: str = Field(max_length=FRAMEWORK_MOCK_MOTION_MAX_ENUM_TEXT_CHARS)
    public_error_code: str = Field(max_length=FRAMEWORK_MOCK_MOTION_MAX_ENUM_TEXT_CHARS)
    retryable: bool = False
    safe_message: str = Field(
        default="", max_length=FRAMEWORK_MOCK_MOTION_MAX_RESULT_TEXT_CHARS
    )


class FrameworkMockMotionExecutionResult(BaseModel):
    """Public-safe aggregate result for one RT-6c adapter call."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "drc.v3.framework-mock-motion-execution.1"
    status: FrameworkMockMotionExecutionStatus
    source_fact: CharacterMotionLifecycleFact
    cue: CharacterMotionCue | None = None

    source_event_type: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    source_session_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    source_turn_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )
    character_id: str | None = Field(
        default=None, max_length=CHARACTER_MOTION_MAX_ID_CHARS
    )

    commands_requested: int = Field(ge=0, le=CHARACTER_MOTION_MAX_COMMANDS)
    commands_completed: int = Field(ge=0, le=CHARACTER_MOTION_MAX_COMMANDS)
    command_results: list[FrameworkMockMotionCommandResult] = Field(
        default_factory=list,
        max_length=CHARACTER_MOTION_MAX_COMMANDS,
    )
    event_types: list[str] = Field(
        default_factory=list,
        max_length=FRAMEWORK_MOCK_MOTION_MAX_EVENT_TYPES,
    )

    framework_import_attempted: bool = False
    session_created: bool = False
    session_closed: bool = False

    adapter: str = "mock"
    real_adapter_enabled: bool = False
    provider_execution_allowed: bool = False
    provider_execution_attempted: bool = False
    network_execution: bool = False

    reason_code: str = Field(max_length=FRAMEWORK_MOCK_MOTION_MAX_ENUM_TEXT_CHARS)
    safe_message: str = Field(
        default="", max_length=FRAMEWORK_MOCK_MOTION_MAX_RESULT_TEXT_CHARS
    )

    @model_validator(mode="after")
    def validate_execution_shape(self) -> "FrameworkMockMotionExecutionResult":
        """Reject inconsistent aggregate counts and execution safety flags."""

        if self.commands_completed > self.commands_requested:
            raise ValueError("commands_completed cannot exceed commands_requested")
        if len(self.command_results) > self.commands_requested:
            raise ValueError("command_results cannot exceed commands_requested")
        if self.commands_completed > len(self.command_results):
            raise ValueError("completed commands require corresponding results")
        orders = [result.order for result in self.command_results]
        if orders != list(range(1, len(self.command_results) + 1)):
            raise ValueError("command results must use contiguous one-based order")
        if self.adapter != "mock":
            raise ValueError("RT-6c adapter result must remain mock")
        if (
            self.real_adapter_enabled
            or self.provider_execution_allowed
            or self.provider_execution_attempted
            or self.network_execution
        ):
            raise ValueError("RT-6c result cannot claim real/provider/network execution")
        if self.status is FrameworkMockMotionExecutionStatus.COMPLETED:
            if self.commands_requested == 0:
                raise ValueError("completed execution requires commands")
            if self.commands_completed != self.commands_requested:
                raise ValueError("completed execution requires all commands completed")
            if len(self.command_results) != self.commands_requested:
                raise ValueError("completed execution requires all command results")
            if not self.framework_import_attempted or not self.session_created:
                raise ValueError("completed execution requires a Framework session")
            if not self.session_closed:
                raise ValueError("completed execution requires a closed session")
        if self.status in {
            FrameworkMockMotionExecutionStatus.IGNORED,
            FrameworkMockMotionExecutionStatus.DISABLED,
        }:
            if self.command_results or self.commands_completed:
                raise ValueError("ignored/disabled execution cannot contain results")
            if self.framework_import_attempted or self.session_created or self.session_closed:
                raise ValueError("ignored/disabled execution cannot touch Framework")
        return self
