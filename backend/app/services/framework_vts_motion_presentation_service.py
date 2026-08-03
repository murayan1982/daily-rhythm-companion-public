"""Default-off manual Backend composition for the accepted RT-7c adapter."""

from collections.abc import Callable

from app.config import AppConfig
from app.models.framework_vts_motion import (
    FrameworkVtsMotionExecutionResult,
    FrameworkVtsMotionExecutionStatus,
)
from app.models.framework_vts_motion_presentation import (
    FrameworkVtsMotionPresentationRequest,
)
from app.services.framework_vts_motion_session_adapter import (
    FrameworkVtsMotionPrivateConfig,
    FrameworkVtsMotionSessionAdapter,
)

AdapterFactory = Callable[[FrameworkVtsMotionPrivateConfig], FrameworkVtsMotionSessionAdapter]


class FrameworkVtsMotionPresentationService:
    """Execute one explicit command; never reuse the RT-6 lifecycle mapper."""

    def __init__(self, config: AppConfig, *, adapter_factory: AdapterFactory | None = None) -> None:
        self._config = config
        self._adapter_factory = adapter_factory or FrameworkVtsMotionSessionAdapter

    def submit(self, request: FrameworkVtsMotionPresentationRequest) -> FrameworkVtsMotionExecutionResult:
        if not isinstance(request, FrameworkVtsMotionPresentationRequest):
            raise TypeError("request must be FrameworkVtsMotionPresentationRequest")

        if self._config.framework_vts_motion_configuration_error is not None:
            return _unavailable("framework_vts_configuration_invalid")

        try:
            private_config = FrameworkVtsMotionPrivateConfig(
                enabled=self._config.framework_vts_motion_enabled,
                allow_provider_execution=(
                    self._config.framework_vts_motion_allow_provider_execution
                ),
                runtime_available=self._config.framework_vts_motion_runtime_available,
                model_selected=self._config.framework_vts_motion_model_selected,
                endpoint_host=self._config.framework_vts_motion_endpoint_host,
                endpoint_port=self._config.framework_vts_motion_endpoint_port,
                authentication_token=(
                    self._config.framework_vts_motion_authentication_token
                ),
                hotkey_bindings=self._config.framework_vts_motion_hotkey_bindings,
            )
        except (TypeError, ValueError):
            return _unavailable("framework_vts_configuration_invalid")

        return self._adapter_factory(private_config).execute([request.command])


def _unavailable(reason_code: str) -> FrameworkVtsMotionExecutionResult:
    return FrameworkVtsMotionExecutionResult(
        status=FrameworkVtsMotionExecutionStatus.UNAVAILABLE,
        commands_requested=1,
        commands_applied=0,
        commands_completed=0,
        optional_commands_skipped=0,
        adapter="vts",
        real_adapter_enabled=False,
        provider_execution_allowed=False,
        reason_code=reason_code,
        safe_message="Framework VTS motion configuration is unavailable.",
    )
