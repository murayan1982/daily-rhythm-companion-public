from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import AppConfig
from app.models.demo_status import CapabilityStatus
from app.models.voice_input_demo import (
    VoiceInputDemoProbeCheck,
    VoiceInputDemoRequest,
    VoiceInputDemoRequestResponse,
    VoiceInputDemoStatusResponse,
)


@dataclass(frozen=True)
class _FrameworkVoiceInputProbeResult:
    """Result of a no-import scan of a local AI Character Framework checkout."""

    root_state: str
    boundary_state: str
    candidate_paths: tuple[str, ...]
    public_api_candidates: tuple[str, ...]
    checks: tuple[VoiceInputDemoProbeCheck, ...]


class VoiceInputDemoService:
    """Build conservative status for the voice input demo boundary.

    The v0.34.0 boundary is intentionally safe-first. It does not import
    framework audio modules, open microphones, read audio files, or start
    realtime sessions. Day2 added a file-system probe for likely FW
    voice/realtime/audio files. Day6 keeps that no-import rule and adds a
    public-boundary probe so DRC can tell whether a configured FW checkout
    exposes a stable app-facing voice input API before wiring an adapter.
    """

    _FRAMEWORK_VOICE_CANDIDATES: tuple[tuple[str, str], ...] = (
        ("framework/runtime/realtime_voice.py", "FW realtime voice runtime module"),
        ("framework/runtime/voice_input.py", "FW runtime voice input module"),
        ("framework/audio/voice_input.py", "FW audio voice input module"),
        ("framework/voice/input.py", "FW voice input module"),
        ("framework/realtime/voice_input.py", "FW realtime voice input module"),
        ("runtime/realtime_voice.py", "legacy realtime voice runtime module"),
        ("runtime/voice_input.py", "legacy runtime voice input module"),
        ("audio/voice_input.py", "legacy audio voice input module"),
        ("voice", "legacy voice package or directory"),
        ("realtime", "legacy realtime package or directory"),
    )

    _PUBLIC_API_FILES: tuple[str, ...] = (
        "framework/__init__.py",
        "framework/facade.py",
        "framework/app_sdk.py",
        "framework/session.py",
        "framework/sessions.py",
    )

    _PUBLIC_VOICE_API_SYMBOLS: tuple[str, ...] = (
        "create_voice_input_session",
        "VoiceInputSession",
        "VoiceInputSessionInfo",
        "create_realtime_voice_session",
        "RealtimeVoiceSession",
        "VoiceRuntimeSession",
        "transcribe_voice_input",
        "transcribe_audio",
    )

    def __init__(self, config: AppConfig):
        self._config = config

    def build_status(self) -> VoiceInputDemoStatusResponse:
        """Return a standalone voice input demo status response."""

        engine = self._normalized_engine()
        probe = self._build_probe_result(engine)
        return VoiceInputDemoStatusResponse(
            engine=engine,
            mode=self._resolve_mode(engine),
            adapter_mode=self._normalized_voice_adapter_mode(),
            capability=self.build_capability_status(engine, probe),
            checks=list(probe.checks),
            candidate_paths=list(probe.candidate_paths),
            public_api_candidates=list(probe.public_api_candidates),
        )

    def submit_request(
        self,
        request: VoiceInputDemoRequest,
    ) -> VoiceInputDemoRequestResponse:
        """Return a safe response for a voice input demo request.

        The request contract is intentionally guarded. Even when the framework
        checkout probe detects likely voice modules or public API symbols, this
        method does not import FW audio code, read ``audio_reference``, open a
        microphone, or attempt speech recognition.
        """

        status = self.build_status()
        return VoiceInputDemoRequestResponse(
            accepted=False,
            request_state="not_started",
            engine=status.engine,
            mode=status.mode,
            adapter_mode=status.adapter_mode,
            input_mode=request.input_mode,
            client_event_id=request.client_event_id,
            capability=status.capability,
            transcript=None,
            message=self._build_request_not_started_message(status.capability),
            checks=status.checks,
            candidate_paths=status.candidate_paths,
            public_api_candidates=status.public_api_candidates,
        )

    def build_capability_status(
        self,
        engine: str | None = None,
        probe: _FrameworkVoiceInputProbeResult | None = None,
    ) -> CapabilityStatus:
        """Return the voice_input capability status used by /demo/status."""

        engine = engine or self._normalized_engine()
        probe = probe or self._build_probe_result(engine)

        if not self._config.voice_input_demo_enabled:
            return CapabilityStatus(
                status="unavailable",
                source="not_configured",
                message="Voice input demo is disabled. Set VOICE_INPUT_DEMO_ENABLED=1 to test the guarded demo boundary.",
            )

        if engine == "mock":
            return CapabilityStatus(
                status="unavailable",
                source="mock",
                message="Voice input demo requires framework mode; mock mode does not provide voice input.",
            )

        if engine != "framework":
            return CapabilityStatus(
                status="unavailable",
                source="unsupported_engine",
                message=f"Unsupported conversation engine for voice input demo: {engine}",
            )

        adapter_mode = self._normalized_voice_adapter_mode()
        if adapter_mode != "framework":
            return CapabilityStatus(
                status="unavailable",
                source="voice_input_adapter_unsupported",
                message=f"Unsupported VOICE_INPUT_ADAPTER_MODE: {self._config.voice_input_adapter_mode}",
            )

        if probe.root_state == "missing_root":
            return CapabilityStatus(
                status="unavailable",
                source="framework_config_missing",
                message="FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured for voice input demo.",
            )

        if probe.root_state == "invalid_root":
            return CapabilityStatus(
                status="unavailable",
                source="framework_config_invalid",
                message="Configured FRAMEWORK_ROOT does not look like an AI Character Framework checkout.",
            )

        if probe.boundary_state == "public_boundary_detected":
            return CapabilityStatus(
                status="unavailable",
                source="framework_voice_input_adapter_not_wired",
                message="Framework public voice input API candidates were detected, but DRC has not wired the guarded adapter yet.",
            )

        if probe.boundary_state == "public_boundary_missing":
            return CapabilityStatus(
                status="unavailable",
                source="framework_voice_input_public_boundary_missing",
                message="Framework voice/realtime/audio files were detected, but no stable public voice input API candidate was exposed by the safe probe.",
            )

        return CapabilityStatus(
            status="unavailable",
            source="framework_voice_input_boundary_missing",
            message="Framework root is configured, but no known voice/realtime/audio input boundary was detected by the safe probe.",
        )

    def _build_request_not_started_message(self, capability: CapabilityStatus) -> str:
        """Explain why the guarded request did not process audio."""

        return (
            "Voice input demo request was received, but no audio was processed "
            f"because voice input is {capability.status} / {capability.source}. "
            f"{capability.message}"
        )

    def _build_probe_result(self, engine: str) -> _FrameworkVoiceInputProbeResult:
        """Inspect config and FW checkout shape without importing FW modules."""

        checks: list[VoiceInputDemoProbeCheck] = [
            VoiceInputDemoProbeCheck(
                name="voice_input_demo_enabled",
                status="pass" if self._config.voice_input_demo_enabled else "skip",
                message=(
                    "Voice input demo is enabled."
                    if self._config.voice_input_demo_enabled
                    else "Voice input demo is disabled."
                ),
            )
        ]

        if not self._config.voice_input_demo_enabled:
            checks.extend(self._skip_checks("VOICE_INPUT_DEMO_ENABLED is disabled."))
            return self._probe_result("not_checked", "not_checked", (), (), checks)

        if engine != "framework":
            checks.extend(
                [
                    VoiceInputDemoProbeCheck(
                        name="conversation_engine",
                        status="fail",
                        message=f"Voice input demo requires framework mode; current engine is {engine}.",
                    ),
                    *self._skip_checks("conversation engine is not framework.", include_engine=False),
                ]
            )
            return self._probe_result("not_checked", "not_checked", (), (), checks)

        checks.append(
            VoiceInputDemoProbeCheck(
                name="conversation_engine",
                status="pass",
                message="Conversation engine is framework.",
            )
        )

        adapter_mode = self._normalized_voice_adapter_mode()
        if adapter_mode != "framework":
            checks.extend(
                [
                    VoiceInputDemoProbeCheck(
                        name="voice_input_adapter_mode",
                        status="fail",
                        message=f"Unsupported VOICE_INPUT_ADAPTER_MODE: {self._config.voice_input_adapter_mode}.",
                    ),
                    *self._skip_checks("voice input adapter mode is unsupported.", include_engine=False),
                ]
            )
            return self._probe_result("not_checked", "not_checked", (), (), checks)

        checks.append(
            VoiceInputDemoProbeCheck(
                name="voice_input_adapter_mode",
                status="pass",
                message="Voice input adapter mode is framework.",
            )
        )

        root = self._config.framework_project_root
        if not root:
            checks.extend(
                [
                    VoiceInputDemoProbeCheck(
                        name="framework_root",
                        status="fail",
                        message="FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
                    ),
                    VoiceInputDemoProbeCheck(
                        name="framework_voice_boundary",
                        status="skip",
                        message="Skipped because framework root is not configured.",
                    ),
                    VoiceInputDemoProbeCheck(
                        name="framework_voice_public_boundary",
                        status="skip",
                        message="Skipped because framework root is not configured.",
                    ),
                ]
            )
            return self._probe_result("missing_root", "not_checked", (), (), checks)

        try:
            framework_root = Path(root).expanduser().resolve()
        except OSError:
            checks.extend(self._invalid_root_checks("FRAMEWORK_ROOT could not be resolved."))
            return self._probe_result("invalid_root", "not_checked", (), (), checks)

        if not self._looks_like_framework_checkout(framework_root):
            checks.extend(
                self._invalid_root_checks(
                    "Configured FRAMEWORK_ROOT does not look like an AI Character Framework checkout."
                )
            )
            return self._probe_result("invalid_root", "not_checked", (), (), checks)

        checks.append(
            VoiceInputDemoProbeCheck(
                name="framework_root",
                status="pass",
                message="Configured FRAMEWORK_ROOT looks like an AI Character Framework checkout.",
            )
        )

        candidate_paths = self._find_voice_boundary_candidates(framework_root)
        if not candidate_paths:
            checks.extend(
                [
                    VoiceInputDemoProbeCheck(
                        name="framework_voice_boundary",
                        status="fail",
                        message="Safe no-import probe did not detect known FW voice/realtime/audio input boundary files.",
                    ),
                    VoiceInputDemoProbeCheck(
                        name="framework_voice_public_boundary",
                        status="skip",
                        message="Skipped because no voice/realtime/audio candidate files were detected.",
                    ),
                ]
            )
            return self._probe_result("available", "candidate_missing", (), (), checks)

        checks.append(
            VoiceInputDemoProbeCheck(
                name="framework_voice_boundary",
                status="pass",
                message="Safe no-import probe detected possible FW voice/realtime/audio input boundary files.",
            )
        )

        public_api_candidates = self._find_public_voice_api_candidates(framework_root)
        if public_api_candidates:
            checks.append(
                VoiceInputDemoProbeCheck(
                    name="framework_voice_public_boundary",
                    status="pass",
                    message="Safe no-import probe detected public voice input API candidates.",
                )
            )
            return self._probe_result(
                "available",
                "public_boundary_detected",
                candidate_paths,
                public_api_candidates,
                checks,
            )

        checks.append(
            VoiceInputDemoProbeCheck(
                name="framework_voice_public_boundary",
                status="fail",
                message="Voice/realtime/audio files were detected, but no public voice input API candidate was found.",
            )
        )
        return self._probe_result(
            "available",
            "public_boundary_missing",
            candidate_paths,
            (),
            checks,
        )

    def _probe_result(
        self,
        root_state: str,
        boundary_state: str,
        candidate_paths: tuple[str, ...],
        public_api_candidates: tuple[str, ...],
        checks: list[VoiceInputDemoProbeCheck],
    ) -> _FrameworkVoiceInputProbeResult:
        return _FrameworkVoiceInputProbeResult(
            root_state=root_state,
            boundary_state=boundary_state,
            candidate_paths=candidate_paths,
            public_api_candidates=public_api_candidates,
            checks=tuple(checks),
        )

    def _skip_checks(
        self,
        reason: str,
        *,
        include_engine: bool = True,
    ) -> list[VoiceInputDemoProbeCheck]:
        checks: list[VoiceInputDemoProbeCheck] = []
        if include_engine:
            checks.append(
                VoiceInputDemoProbeCheck(
                    name="conversation_engine",
                    status="skip",
                    message=f"Skipped because {reason}",
                )
            )
        checks.extend(
            [
                VoiceInputDemoProbeCheck(
                    name="framework_root",
                    status="skip",
                    message=f"Skipped because {reason}",
                ),
                VoiceInputDemoProbeCheck(
                    name="framework_voice_boundary",
                    status="skip",
                    message=f"Skipped because {reason}",
                ),
                VoiceInputDemoProbeCheck(
                    name="framework_voice_public_boundary",
                    status="skip",
                    message=f"Skipped because {reason}",
                ),
            ]
        )
        return checks

    def _invalid_root_checks(self, framework_root_message: str) -> list[VoiceInputDemoProbeCheck]:
        return [
            VoiceInputDemoProbeCheck(
                name="framework_root",
                status="fail",
                message=framework_root_message,
            ),
            VoiceInputDemoProbeCheck(
                name="framework_voice_boundary",
                status="skip",
                message="Skipped because framework root is invalid.",
            ),
            VoiceInputDemoProbeCheck(
                name="framework_voice_public_boundary",
                status="skip",
                message="Skipped because framework root is invalid.",
            ),
        ]

    def _normalized_engine(self) -> str:
        return self._config.conversation_engine.strip().lower() or "mock"

    def _normalized_voice_adapter_mode(self) -> str:
        return self._config.voice_input_adapter_mode.strip().lower() or "disabled"

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

    def _looks_like_framework_checkout(self, framework_root: Path) -> bool:
        if not framework_root.exists():
            return False

        facade_path = framework_root / "framework" / "facade.py"
        package_init_path = framework_root / "framework" / "__init__.py"
        return facade_path.exists() or package_init_path.exists()

    def _find_voice_boundary_candidates(self, framework_root: Path) -> tuple[str, ...]:
        detected: list[str] = []
        for relative_path, _description in self._FRAMEWORK_VOICE_CANDIDATES:
            candidate = framework_root / relative_path
            if candidate.exists():
                detected.append(relative_path)
        return tuple(detected)

    def _find_public_voice_api_candidates(self, framework_root: Path) -> tuple[str, ...]:
        """Return public voice API symbol candidates without importing FW code."""

        detected: list[str] = []
        for relative_path in self._PUBLIC_API_FILES:
            public_file = framework_root / relative_path
            if not public_file.exists() or not public_file.is_file():
                continue

            try:
                text = public_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = public_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for symbol in self._PUBLIC_VOICE_API_SYMBOLS:
                if symbol in text:
                    detected.append(f"{relative_path}:{symbol}")

        return tuple(detected)
