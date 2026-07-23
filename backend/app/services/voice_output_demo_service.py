from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from app.config import AppConfig
from app.models.demo_status import CapabilityStatus
from app.models.voice_output_demo import (
    VoiceOutputDemoProbeCheck,
    VoiceOutputDemoRequest,
    VoiceOutputDemoRequestResponse,
    VoiceOutputDemoStatusResponse,
)
from app.services.framework_voice_output_adapter import (
    FrameworkVoiceOutputAdapter,
    FrameworkVoiceOutputRequest,
)
from app.services.voice_output_artifact_store import VoiceOutputArtifactStore


@dataclass(frozen=True)
class _FrameworkVoiceOutputProbeResult:
    """Result of a no-import scan of a local AI Character Framework checkout."""

    root_state: str
    boundary_state: str
    candidate_paths: tuple[str, ...]
    public_api_candidates: tuple[str, ...]
    checks: tuple[VoiceOutputDemoProbeCheck, ...]


class VoiceOutputDemoService:
    """Build conservative status for the voice output / TTS demo boundary.

    The default path is safe-first and does not call providers, synthesize
    audio, generate audio files, or play sound. Default check path does not import FW audio code or synthesize text. A real TTS call is attempted only when
    the operator enables the explicit real-TTS runtime gate and a framework
    public voice-output boundary is detected.
    """

    _FRAMEWORK_VOICE_OUTPUT_CANDIDATES: tuple[tuple[str, str], ...] = (
        ("framework/runtime/voice_output.py", "FW realtime voice output runtime module"),
        ("framework/runtime/text_to_speech.py", "FW runtime TTS synthesis module"),
        ("framework/audio/voice_output.py", "FW audio voice output module"),
        ("framework/audio/tts.py", "FW audio TTS module"),
        ("framework/voice/output.py", "FW voice output module"),
        ("framework/voice/synthesis.py", "FW voice synthesis module"),
        ("framework/realtime/voice_output.py", "FW realtime voice output module"),
        ("runtime/voice_output.py", "legacy runtime voice output module"),
        ("audio/tts.py", "legacy audio TTS module"),
        ("voice", "legacy voice package or directory"),
        ("synthesis", "legacy synthesis package or directory"),
    )

    _PUBLIC_API_FILES: tuple[str, ...] = (
        "framework/__init__.py",
        "framework/facade.py",
        "framework/app_sdk.py",
        "framework/session.py",
        "framework/sessions.py",
        "framework/api.py",
        "framework/public.py",
        "framework/exports.py",
    )

    _PUBLIC_TTS_API_SYMBOLS: tuple[str, ...] = (
        "create_voice_output_session",
        "VoiceOutputRequest",
        "VoiceOutputResult",
        "VoiceOutputSession",
        "VoiceOutputSessionInfo",
        "create_tts_session",
        "TTSSession",
        "synthesize_text",
        "speak_text",
        "voice_output_session",
        "tts_session",
        "text_to_speech",
    )

    def __init__(
        self,
        config: AppConfig,
        *,
        artifact_store: VoiceOutputArtifactStore | None = None,
    ) -> None:
        self._config = config
        self._artifact_store = artifact_store or VoiceOutputArtifactStore(config=config)

    def build_status(self) -> VoiceOutputDemoStatusResponse:
        """Return a standalone voice output demo status response."""

        engine = self._normalized_engine()
        probe = self._build_probe_result(engine)
        return VoiceOutputDemoStatusResponse(
            engine=engine,
            mode=self._resolve_mode(engine),
            adapter_mode=self._normalized_voice_output_adapter_mode(),
            real_tts_enabled=self._config.voice_output_real_tts_enabled,
            capability=self.build_capability_status(engine, probe),
            checks=list(probe.checks),
            candidate_paths=list(probe.candidate_paths),
            public_api_candidates=list(probe.public_api_candidates),
        )

    def submit_request(
        self,
        request: VoiceOutputDemoRequest,
    ) -> VoiceOutputDemoRequestResponse:
        """Handle a guarded voice output demo request."""

        status = self.build_status()
        output_mode = self._normalized_request_value(request.output_mode) or "tts"
        text_content = self._normalized_request_value(request.text_content)
        character_id = self._normalized_request_value(request.character_id)
        voice_profile_id = self._normalized_request_value(request.voice_profile_id)
        requested_audio_format = self._normalized_request_value(request.audio_format)
        utterance_purpose = (
            self._normalized_request_value(request.utterance_purpose)
            or self._config.voice_output_utterance_purpose
        )
        request_warnings = self._build_request_warnings(
            text_content,
            requested_audio_format,
        )

        base_response_kwargs = dict(
            engine=status.engine,
            mode=status.mode,
            adapter_mode=status.adapter_mode,
            real_tts_enabled=status.real_tts_enabled,
            output_mode=output_mode,
            client_event_id=self._normalized_request_value(request.client_event_id),
            text_content=text_content,
            character_id=character_id,
            voice_profile_id=voice_profile_id,
            requested_audio_format=requested_audio_format,
            utterance_purpose=utterance_purpose,
            request_warnings=request_warnings,
            capability=status.capability,
            checks=status.checks,
            candidate_paths=status.candidate_paths,
            public_api_candidates=status.public_api_candidates,
        )

        if text_content is None:
            return VoiceOutputDemoRequestResponse(
                **base_response_kwargs,
                accepted=False,
                request_state="blocked_invalid_request",
                framework_call_state="not_called",
                audio_url=None,
                audio_format=None,
                audio_playback_status="not_started",
                evidence_status="not_evidence",
                runtime_notes=[
                    "No framework voice output call was made because text_content was empty."
                ],
                message="Voice output request was blocked because text_content is required.",
            )

        if not status.real_tts_enabled:
            return VoiceOutputDemoRequestResponse(
                **base_response_kwargs,
                accepted=False,
                request_state="guarded_not_started",
                framework_call_state="not_called",
                audio_url=None,
                audio_format=None,
                audio_playback_status="not_started",
                evidence_status="not_evidence",
                runtime_notes=[
                    "Set VOICE_OUTPUT_REAL_TTS_ENABLED=1 only during private operator evidence runs.",
                    "Default checks must remain provider-free and audio-free.",
                ],
                message=self._build_runtime_guard_message(status.capability),
            )

        if status.capability.status != "available":
            return VoiceOutputDemoRequestResponse(
                **base_response_kwargs,
                accepted=False,
                request_state="not_started",
                framework_call_state="not_called",
                audio_url=None,
                audio_format=None,
                audio_playback_status="not_started",
                evidence_status="not_evidence",
                runtime_notes=[
                    "Real TTS was enabled, but the framework voice output boundary is not available."
                ],
                message=self._build_request_not_started_message(status.capability),
            )

        framework_root = Path(self._config.framework_project_root or "").expanduser().resolve()
        adapter = FrameworkVoiceOutputAdapter(
            framework_root,
            real_tts_enabled=self._config.voice_output_real_tts_enabled,
            artifact_dir=self._artifact_store.framework_artifact_dir,
        )
        adapter_result = adapter.synthesize(
            FrameworkVoiceOutputRequest(
                text=text_content,
                voice_profile_id=voice_profile_id,
                requested_audio_format=requested_audio_format,
                character_id=character_id,
                utterance_purpose=utterance_purpose,
            )
        )

        request_state = self._request_state_from_adapter_status(adapter_result.status)
        audio_url = adapter_result.audio_url
        # Local FW artifact refs are backend-internal in every result state.
        audio_artifact_ref = None
        audio_format = adapter_result.audio_format
        audio_ready = adapter_result.audio_ready
        audio_handoff_kind = adapter_result.audio_handoff_kind
        has_audio_handoff = adapter_result.has_audio_handoff
        message = adapter_result.message
        handoff_notes: list[str] = []

        if (
            adapter_result.status == "generated"
            and adapter_result.is_generated
            and adapter_result.audio_ready
            and adapter_result.audio_handoff_kind == "url"
            and not self._is_safe_public_audio_url(adapter_result.audio_url)
        ):
            request_state = "generated_handoff_invalid"
            audio_url = None
            audio_ready = False
            audio_handoff_kind = "none"
            has_audio_handoff = False
            message = (
                "Framework generated audio, but DRC rejected the URL handoff "
                "because it was not a safe HTTP(S) or root-relative Web URL."
            )
            handoff_notes.append(
                "Unsafe or local-path-like FW audio URLs are not exposed through the DRC API."
            )

        if (
            adapter_result.status == "generated"
            and adapter_result.is_generated
            and adapter_result.audio_ready
            and adapter_result.audio_handoff_kind == "artifact_ref"
        ):
            published_artifact = self._artifact_store.publish_framework_artifact(
                adapter_result.audio_artifact_ref,
                audio_format=adapter_result.audio_format,
            )
            # Never return a local FW artifact ref, including failure cases.
            audio_artifact_ref = None

            if published_artifact is None:
                request_state = "generated_handoff_invalid"
                audio_url = None
                audio_ready = False
                audio_handoff_kind = "none"
                has_audio_handoff = False
                message = (
                    "Framework generated audio, but DRC rejected the local artifact "
                    "handoff because it was missing, unsupported, or outside the managed store."
                )
                handoff_notes.append(
                    "The FW artifact was not exposed because it did not pass the DRC-managed Web handoff guard."
                )
            else:
                audio_url = published_artifact.audio_url
                audio_format = published_artifact.audio_format
                audio_ready = True
                audio_handoff_kind = "url"
                has_audio_handoff = True
                message = (
                    "Framework generated audio and DRC published an opaque local Web audio URL. "
                    "Audible browser playback still requires private operator confirmation."
                )
                handoff_notes.extend(
                    [
                        "The local FW artifact path was replaced with a DRC-managed opaque URL.",
                        "The generated audio remains local-only and must not be committed.",
                    ]
                )

        accepted = (
            adapter_result.status == "generated"
            and adapter_result.is_generated
            and audio_ready
            and has_audio_handoff
            and audio_handoff_kind == "url"
            and audio_url is not None
        )
        playback_status = "requires_operator_confirmation" if accepted else "not_started"
        runtime_notes = [
            *adapter_result.runtime_notes,
            *handoff_notes,
            "A backend generated/audio_ready response is not sufficient for v2.0.0 acceptance.",
            "Web UI audible playback and screenshot evidence must be privately recorded.",
        ]

        return VoiceOutputDemoRequestResponse(
            **base_response_kwargs,
            accepted=accepted,
            request_state=request_state,
            framework_call_state=adapter_result.status,
            framework_api_name=adapter_result.framework_api_name,
            audio_url=audio_url,
            audio_artifact_ref=audio_artifact_ref,
            audio_format=audio_format,
            audio_ready=audio_ready,
            audio_handoff_kind=audio_handoff_kind,
            has_audio_handoff=has_audio_handoff,
            is_generated=adapter_result.is_generated,
            audio_playback_status=playback_status,
            evidence_status="not_evidence",
            runtime_notes=runtime_notes,
            message=message,
        )

    def _is_safe_public_audio_url(self, value: str | None) -> bool:
        """Accept only HTTP(S) URLs or root-relative Web paths."""

        if value is None:
            return False

        normalized = value.strip()
        if not normalized or "\\" in normalized or "\x00" in normalized:
            return False

        try:
            parsed = urlsplit(normalized)
        except ValueError:
            return False

        if parsed.scheme:
            return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)

        if parsed.netloc or not parsed.path.startswith("/"):
            return False

        path_segments = [segment for segment in parsed.path.split("/") if segment]
        return ".." not in path_segments

    def _normalized_request_value(self, value: str | None) -> str | None:
        """Normalize optional request metadata without changing the safe contract."""

        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    def _build_request_warnings(
        self,
        text_content: str | None,
        requested_audio_format: str | None,
    ) -> list[str]:
        """Return non-blocking request warnings for guarded TTS wiring."""

        warnings: list[str] = []
        if text_content is None:
            warnings.append("text_content is empty; TTS synthesis requires text.")
        if requested_audio_format is None:
            warnings.append("audio_format is empty; the framework may choose a default format.")
        return warnings

    def build_capability_status(
        self,
        engine: str | None = None,
        probe: _FrameworkVoiceOutputProbeResult | None = None,
    ) -> CapabilityStatus:
        """Return the voice_output capability status used by /demo/status."""

        engine = engine or self._normalized_engine()
        probe = probe or self._build_probe_result(engine)

        if not self._config.voice_output_demo_enabled:
            return CapabilityStatus(
                status="unavailable",
                source="not_configured",
                message=(
                    "Voice output demo is disabled. Set VOICE_OUTPUT_DEMO_ENABLED=1 "
                    "to test the guarded TTS demo boundary."
                ),
            )

        if engine == "mock":
            return CapabilityStatus(
                status="unavailable",
                source="mock",
                message="Voice output demo requires framework mode; mock mode does not provide TTS.",
            )

        if engine != "framework":
            return CapabilityStatus(
                status="unavailable",
                source="unsupported_engine",
                message=f"Unsupported conversation engine for voice output demo: {engine}",
            )

        adapter_mode = self._normalized_voice_output_adapter_mode()
        if adapter_mode != "framework":
            return CapabilityStatus(
                status="unavailable",
                source="voice_output_adapter_unsupported",
                message=f"Unsupported VOICE_OUTPUT_ADAPTER_MODE: {self._config.voice_output_adapter_mode}",
            )

        if probe.root_state == "missing_root":
            return CapabilityStatus(
                status="unavailable",
                source="framework_config_missing",
                message="FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured for voice output demo.",
            )

        if probe.root_state == "invalid_root":
            return CapabilityStatus(
                status="unavailable",
                source="framework_config_invalid",
                message="Configured FRAMEWORK_ROOT does not look like an AI Character Framework checkout.",
            )

        if probe.boundary_state == "public_boundary_detected":
            if self._config.voice_output_real_tts_enabled:
                return CapabilityStatus(
                    status="available",
                    source="framework_voice_output_runtime_enabled",
                    message=(
                        "Framework public voice output/TTS API candidates were detected, "
                        "and the explicit real TTS runtime gate is enabled."
                    ),
                )

            return CapabilityStatus(
                status="unavailable",
                source="real_tts_runtime_disabled",
                message=(
                    "Framework public voice output/TTS API candidates were detected, "
                    "but VOICE_OUTPUT_REAL_TTS_ENABLED is disabled. No audio will be generated."
                ),
            )

        if probe.boundary_state == "public_boundary_missing":
            return CapabilityStatus(
                status="unavailable",
                source="framework_voice_output_public_boundary_missing",
                message=(
                    "Framework voice/audio/TTS files were detected, but no stable public "
                    "voice output API candidate was exposed by the safe probe."
                ),
            )

        return CapabilityStatus(
            status="unavailable",
            source="framework_voice_output_boundary_missing",
            message=(
                "Framework root is configured, but no known voice output/audio/TTS "
                "boundary was detected by the safe probe."
            ),
        )

    def _build_runtime_guard_message(self, capability: CapabilityStatus) -> str:
        """Explain why the guarded request did not call real TTS."""

        return (
            "Voice output demo request was received, but no audio was generated. "
            "The real TTS runtime gate is disabled by default. "
            f"Current capability is {capability.status} / {capability.source}. "
            f"{capability.message}"
        )

    def _build_request_not_started_message(self, capability: CapabilityStatus) -> str:
        """Explain why the guarded request did not generate audio."""

        return (
            "Voice output demo request was received, but no audio was generated "
            f"because voice output is {capability.status} / {capability.source}. "
            f"{capability.message}"
        )

    def _request_state_from_adapter_status(self, adapter_status: str) -> str:
        if adapter_status == "generated":
            return "generated"
        if adapter_status == "legacy_audio_ready":
            return "legacy_audio_ready"
        if adapter_status == "audio_generated_unserved":
            return "audio_generated_unserved"
        if adapter_status == "generated_handoff_invalid":
            return "generated_handoff_invalid"
        if adapter_status in {"unavailable", "skipped", "rejected", "failed"}:
            return adapter_status
        if adapter_status == "framework_result_without_audio":
            return "framework_result_without_audio"
        if adapter_status == "public_voice_output_callable_missing":
            return "framework_public_callable_missing"
        if adapter_status == "public_framework_import_failed":
            return "framework_public_import_failed"
        if adapter_status == "framework_voice_output_call_failed":
            return "framework_call_failed"
        return "framework_runtime_unavailable"

    def _build_probe_result(self, engine: str) -> _FrameworkVoiceOutputProbeResult:
        """Inspect config and FW checkout shape without importing FW modules."""

        checks: list[VoiceOutputDemoProbeCheck] = [
            VoiceOutputDemoProbeCheck(
                name="voice_output_demo_enabled",
                status="pass" if self._config.voice_output_demo_enabled else "skip",
                message=(
                    "Voice output demo is enabled."
                    if self._config.voice_output_demo_enabled
                    else "Voice output demo is disabled."
                ),
            ),
            VoiceOutputDemoProbeCheck(
                name="voice_output_real_tts_enabled",
                status="pass" if self._config.voice_output_real_tts_enabled else "skip",
                message=(
                    "Explicit real TTS runtime gate is enabled."
                    if self._config.voice_output_real_tts_enabled
                    else "Explicit real TTS runtime gate is disabled."
                ),
            ),
        ]

        if not self._config.voice_output_demo_enabled:
            checks.extend(self._skip_checks("VOICE_OUTPUT_DEMO_ENABLED is disabled."))
            return self._probe_result("not_checked", "not_checked", (), (), checks)

        if engine != "framework":
            checks.extend(
                [
                    VoiceOutputDemoProbeCheck(
                        name="conversation_engine",
                        status="fail",
                        message=f"Voice output demo requires framework mode; current engine is {engine}.",
                    ),
                    *self._skip_checks(
                        "conversation engine is not framework.",
                        include_engine=False,
                    ),
                ]
            )
            return self._probe_result("not_checked", "not_checked", (), (), checks)

        checks.append(
            VoiceOutputDemoProbeCheck(
                name="conversation_engine",
                status="pass",
                message="Conversation engine is framework.",
            )
        )

        adapter_mode = self._normalized_voice_output_adapter_mode()
        if adapter_mode != "framework":
            checks.extend(
                [
                    VoiceOutputDemoProbeCheck(
                        name="voice_output_adapter_mode",
                        status="fail",
                        message=f"Unsupported VOICE_OUTPUT_ADAPTER_MODE: {self._config.voice_output_adapter_mode}.",
                    ),
                    *self._skip_checks(
                        "voice output adapter mode is unsupported.",
                        include_engine=False,
                    ),
                ]
            )
            return self._probe_result("not_checked", "not_checked", (), (), checks)

        checks.append(
            VoiceOutputDemoProbeCheck(
                name="voice_output_adapter_mode",
                status="pass",
                message="Voice output adapter mode is framework.",
            )
        )

        root = self._config.framework_project_root
        if not root:
            checks.extend(
                [
                    VoiceOutputDemoProbeCheck(
                        name="framework_root",
                        status="fail",
                        message="FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
                    ),
                    VoiceOutputDemoProbeCheck(
                        name="framework_voice_output_boundary",
                        status="skip",
                        message="Skipped because framework root is not configured.",
                    ),
                    VoiceOutputDemoProbeCheck(
                        name="framework_voice_output_public_boundary",
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
            VoiceOutputDemoProbeCheck(
                name="framework_root",
                status="pass",
                message="Configured FRAMEWORK_ROOT looks like an AI Character Framework checkout.",
            )
        )

        candidate_paths = self._find_voice_output_boundary_candidates(framework_root)
        if not candidate_paths:
            checks.extend(
                [
                    VoiceOutputDemoProbeCheck(
                        name="framework_voice_output_boundary",
                        status="fail",
                        message=(
                            "Safe no-import probe did not detect known FW "
                            "voice output/audio/TTS boundary files."
                        ),
                    ),
                    VoiceOutputDemoProbeCheck(
                        name="framework_voice_output_public_boundary",
                        status="skip",
                        message=(
                            "Skipped because no voice output/audio/TTS candidate "
                            "files were detected."
                        ),
                    ),
                ]
            )
            return self._probe_result("available", "candidate_missing", (), (), checks)

        checks.append(
            VoiceOutputDemoProbeCheck(
                name="framework_voice_output_boundary",
                status="pass",
                message="Safe no-import probe detected possible FW voice output/audio/TTS boundary files.",
            )
        )

        public_api_candidates = self._find_public_voice_output_api_candidates(framework_root)
        if public_api_candidates:
            checks.append(
                VoiceOutputDemoProbeCheck(
                    name="framework_voice_output_public_boundary",
                    status="pass",
                    message="Safe no-import probe detected public voice output/TTS API candidates.",
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
            VoiceOutputDemoProbeCheck(
                name="framework_voice_output_public_boundary",
                status="fail",
                message="Voice output/audio/TTS files were detected, but no public TTS API candidate was found.",
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
        checks: list[VoiceOutputDemoProbeCheck],
    ) -> _FrameworkVoiceOutputProbeResult:
        return _FrameworkVoiceOutputProbeResult(
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
    ) -> list[VoiceOutputDemoProbeCheck]:
        checks: list[VoiceOutputDemoProbeCheck] = []
        if include_engine:
            checks.append(
                VoiceOutputDemoProbeCheck(
                    name="conversation_engine",
                    status="skip",
                    message=f"Skipped because {reason}",
                )
            )
        checks.extend(
            [
                VoiceOutputDemoProbeCheck(
                    name="framework_root",
                    status="skip",
                    message=f"Skipped because {reason}",
                ),
                VoiceOutputDemoProbeCheck(
                    name="framework_voice_output_boundary",
                    status="skip",
                    message=f"Skipped because {reason}",
                ),
                VoiceOutputDemoProbeCheck(
                    name="framework_voice_output_public_boundary",
                    status="skip",
                    message=f"Skipped because {reason}",
                ),
            ]
        )
        return checks

    def _invalid_root_checks(self, framework_root_message: str) -> list[VoiceOutputDemoProbeCheck]:
        return [
            VoiceOutputDemoProbeCheck(
                name="framework_root",
                status="fail",
                message=framework_root_message,
            ),
            VoiceOutputDemoProbeCheck(
                name="framework_voice_output_boundary",
                status="skip",
                message="Skipped because framework root is invalid.",
            ),
            VoiceOutputDemoProbeCheck(
                name="framework_voice_output_public_boundary",
                status="skip",
                message="Skipped because framework root is invalid.",
            ),
        ]

    def _normalized_engine(self) -> str:
        return self._config.conversation_engine.strip().lower() or "mock"

    def _normalized_voice_output_adapter_mode(self) -> str:
        return self._config.voice_output_adapter_mode.strip().lower() or "disabled"

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

    def _find_voice_output_boundary_candidates(self, framework_root: Path) -> tuple[str, ...]:
        detected: list[str] = []
        for relative_path, _description in self._FRAMEWORK_VOICE_OUTPUT_CANDIDATES:
            candidate = framework_root / relative_path
            if candidate.exists():
                detected.append(relative_path)
        return tuple(detected)

    def _find_public_voice_output_api_candidates(self, framework_root: Path) -> tuple[str, ...]:
        """Return public voice output/TTS API symbol candidates without importing FW code."""

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

            for symbol in self._PUBLIC_TTS_API_SYMBOLS:
                if symbol in text:
                    detected.append(f"{relative_path}:{symbol}")

        return tuple(detected)
