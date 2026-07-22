from __future__ import annotations

from pathlib import Path

from app.config import AppConfig
from app.models.demo_status import CapabilityStatus, DemoStatusResponse
from app.services.google_health_runtime_guard import evaluate_google_health_runtime_guard
from app.services.voice_input_demo_service import VoiceInputDemoService


class DemoStatusService:
    """
    Build an app-facing demo status snapshot from backend configuration.

    This service is intentionally conservative: it only reports a capability as
    available when the current DRC configuration can safely expose that path.
    It does not create framework sessions, call providers, touch microphones, or
    require optional Live2D/VTS dependencies.
    """

    def __init__(self, config: AppConfig):
        self._config = config

    def build_status(self) -> DemoStatusResponse:
        """Return the current engine, demo mode, and capability statuses."""

        engine = self._normalized_engine()

        return DemoStatusResponse(
            engine=engine,
            mode=self._resolve_mode(engine),
            capabilities={
                "llm_response": self._build_llm_response_status(engine),
                "voice_input": self._build_voice_input_status(engine),
                "voice_output": self._build_voice_output_status(engine),
                "live2d_motion": self._build_live2d_motion_status(engine),
                "google_health_real_api": self._build_google_health_real_api_status(),
            },
        )


    def _build_google_health_real_api_status(self) -> CapabilityStatus:
        """Return Google Health real API status without making real requests.

        v0.40.0 treats Google Health real API as a visible demo capability:
        safe by default, explicit opt-in when verified, and never silently
        hidden behind the mock-safe profile.  This method only evaluates
        configuration and the runtime guard; it does not load tokens, call
        Google Health, or expose sensitive local details.
        """

        provider = self._config.sleep_provider.strip().lower() or "mock"
        runtime_guard = evaluate_google_health_runtime_guard(self._config)

        if provider != "google_health":
            return CapabilityStatus(
                status="skipped",
                source=(
                    "mock_sleep_provider"
                    if provider == "mock"
                    else "sleep_provider_not_google_health"
                ),
                message=(
                    "Google Health real API is not active because "
                    f"SLEEP_PROVIDER={provider}. Mock-safe sleep remains the "
                    "default; set SLEEP_PROVIDER=google_health and enable the "
                    "explicit real API gates only for guarded verification."
                ),
            )

        if runtime_guard.real_api_allowed:
            return CapabilityStatus(
                status="available",
                source="google_health_real_api_guarded",
                message=(
                    "Google Health real API request settings passed the runtime "
                    "guard. /sleep/summary may use Google Health-backed "
                    "SleepSummary when OAuth token and sleep data are available."
                ),
            )

        if not runtime_guard.real_api_requested:
            return CapabilityStatus(
                status="unavailable",
                source="google_health_real_api_disabled",
                message=runtime_guard.message,
            )

        return CapabilityStatus(
            status="unavailable",
            source="google_health_real_api_blocked",
            message=runtime_guard.message,
        )

    def _build_voice_input_status(self, engine: str) -> CapabilityStatus:
        """Return voice input status while preserving v0.33 default compatibility.

        v0.34.0 adds a dedicated /demo/voice-input/status endpoint for the
        detailed guarded voice-input boundary.  The existing /demo/status
        contract remains conservative by default so older v0.33 baseline checks
        continue to treat voice input as a future capability until the demo is
        explicitly enabled.
        """

        if not self._config.voice_input_demo_enabled:
            return CapabilityStatus(
                status="unavailable",
                source="not_implemented",
                message="Voice input demo is planned for a later version.",
            )

        return VoiceInputDemoService(self._config).build_capability_status(engine)

    def _build_voice_output_status(self, engine: str) -> CapabilityStatus:
        """Return voice output status while preserving v0.34 default compatibility.

        v0.35.0 adds a dedicated /demo/voice-output/status endpoint for the
        detailed guarded voice-output boundary. The existing /demo/status
        contract remains conservative by default so v0.34 baseline checks can
        continue to treat voice output/TTS as a future capability until the demo
        is explicitly enabled.
        """

        if not self._config.voice_output_demo_enabled:
            return CapabilityStatus(
                status="unavailable",
                source="not_implemented",
                message="Voice output/TTS demo is planned for a later version.",
            )

        from app.services.voice_output_demo_service import VoiceOutputDemoService

        return VoiceOutputDemoService(self._config).build_capability_status(engine)

    def _build_live2d_motion_status(self, engine: str) -> CapabilityStatus:
        """Return Live2D/VTS motion status while preserving v0.35 compatibility.

        v0.36.0 adds a dedicated /demo/motion/status endpoint for the guarded
        motion-demo boundary. The existing /demo/status contract remains
        conservative by default so v0.35 baseline checks continue to treat
        Live2D/VTS motion as a future capability until the demo is explicitly
        enabled.
        """

        if not self._config.motion_demo_enabled:
            return CapabilityStatus(
                status="unavailable",
                source="not_implemented",
                message="Live2D/VTS motion demo is planned for a later version.",
            )

        from app.services.motion_demo_service import MotionDemoService

        return MotionDemoService(self._config).build_capability_status(engine)

    def _normalized_engine(self) -> str:
        return self._config.conversation_engine.strip().lower() or "mock"

    def _resolve_mode(self, engine: str) -> str:
        if engine == "framework":
            return "framework_local"

        if engine == "mock" and self._is_mock_safe_profile():
            return "mock_safe"

        if engine == "mock":
            return "mock"

        return "unsupported"

    def _is_mock_safe_profile(self) -> bool:
        return (
            self._config.sleep_provider == "mock"
            and not self._config.gemini_api_key
            and not self._config.xai_api_key
            and not self._config.google_health_enable_real_token_exchange
            and not self._config.google_health_enable_real_token_refresh
            and not self._config.google_health_enable_real_api_requests
            and not self._config.google_health_real_api_opt_in
            and not self._config.fitbit_enable_real_token_exchange
        )

    def _build_llm_response_status(self, engine: str) -> CapabilityStatus:
        if engine == "mock":
            return CapabilityStatus(
                status="unavailable",
                source="mock",
                message="LLM response is unavailable in mock mode.",
            )

        if engine != "framework":
            return CapabilityStatus(
                status="unavailable",
                source="unsupported_engine",
                message=f"Unsupported conversation engine: {engine}",
            )

        framework_readiness = self._inspect_framework_readiness()
        if framework_readiness == "available":
            return CapabilityStatus(
                status="available",
                source="framework",
                message="Framework text/LLM response path is configured.",
            )

        if framework_readiness == "unsupported_adapter":
            return CapabilityStatus(
                status="unavailable",
                source="framework_adapter_unsupported",
                message=(
                    "Unsupported FRAMEWORK_ADAPTER_MODE: "
                    f"{self._config.framework_adapter_mode}"
                ),
            )

        if framework_readiness == "missing_root":
            return CapabilityStatus(
                status="unavailable",
                source="framework_config_missing",
                message="FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
            )

        return CapabilityStatus(
            status="unavailable",
            source="framework_config_invalid",
            message="Configured FRAMEWORK_ROOT does not look like an AI Character Framework checkout.",
        )

    def _inspect_framework_readiness(self) -> str:
        adapter_mode = self._config.framework_adapter_mode.strip().lower()
        if adapter_mode != "local_import":
            return "unsupported_adapter"

        root = self._config.framework_project_root
        if not root:
            return "missing_root"

        try:
            framework_root = Path(root).expanduser().resolve()
        except OSError:
            return "invalid_root"

        if not framework_root.exists():
            return "invalid_root"

        facade_path = framework_root / "framework" / "facade.py"
        package_init_path = framework_root / "framework" / "__init__.py"
        if facade_path.exists() or package_init_path.exists():
            return "available"

        return "invalid_root"
