from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any, Callable
from uuid import uuid4

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
    framework_voice_input_public_api_context,
)
from app.services.framework_voice_input_openai_real_executor_assembly import (
    FrameworkVoiceInputOpenAIRealExecutorAssembler,
    FrameworkVoiceInputOpenAIRealExecutorAssemblyError,
    FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest,
)
from app.services.private_voice_input_credential_source import (
    PrivateVoiceInputCredentialError,
    PrivateVoiceInputCredentialSource,
)
from app.services.voice_input_staging_store import (
    StagedVoiceInputArtifact,
    VoiceInputStagingError,
    VoiceInputStagingStore,
)


_MAX_TRANSCRIPT_CODE_POINTS = 4096
_REAL_STT_EXECUTION_LOCK = Lock()


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


@dataclass(frozen=True)
class FrameworkVoiceInputAppTranscriptRequest:
    """Provider-neutral metadata for one app-visible staged STT execution."""

    staging_id: str
    foreground_opt_in: bool
    language: str | None = "ja"
    duration_ms: int | None = None
    max_duration_ms: int = 15000
    model: str = "gpt-4o-mini-transcribe"
    timeout_seconds: float = 120.0

    def __post_init__(self) -> None:
        staging_id = str(self.staging_id).strip()
        language = None if self.language is None else str(self.language).strip()
        model = str(self.model).strip()
        if len(staging_id) != 32 or any(
            character not in "0123456789abcdef" for character in staging_id
        ):
            raise ValueError("staging_id must be 32 lowercase hexadecimal characters")
        if not model:
            raise ValueError("model must be non-empty")
        if language == "":
            language = None
        if language is not None and len(language) > 32:
            raise ValueError("language must not exceed 32 characters")
        if self.duration_ms is not None and not 1 <= self.duration_ms <= self.max_duration_ms:
            raise ValueError("duration_ms must be within the configured duration bound")
        if self.max_duration_ms <= 0:
            raise ValueError("max_duration_ms must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        object.__setattr__(self, "staging_id", staging_id)
        object.__setattr__(self, "language", language)
        object.__setattr__(self, "model", model)


@dataclass(frozen=True)
class FrameworkVoiceInputAppTranscriptResult:
    """Public app result with transcript fields excluded from repr output."""

    result_id: str
    text: str = field(repr=False, compare=False)
    is_final: bool = True


class FrameworkVoiceInputAppTranscriptError(RuntimeError):
    """Typed public-safe failure for the app-visible transcript boundary."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class FrameworkVoiceInputAppTranscriptAdapter:
    """Execute one bounded FW root-public real STT and return a final transcript.

    The private staged path is scoped to VoiceInputStagingStore.consume(). The
    credential source builds only the released Framework credential object. No
    provider client or provider SDK is imported directly by DRC.
    """

    def __init__(
        self,
        config: AppConfig,
        store: VoiceInputStagingStore,
        credential_source: PrivateVoiceInputCredentialSource,
        *,
        public_api_context_factory: Callable[[Path], Any] | None = None,
        execution_lock: Any | None = None,
    ) -> None:
        self._config = config
        self._store = store
        self._credential_source = credential_source
        self._public_api_context_factory = (
            public_api_context_factory or framework_voice_input_public_api_context
        )
        self._execution_lock = execution_lock or _REAL_STT_EXECUTION_LOCK

    def transcribe_staged_artifact(
        self,
        request: FrameworkVoiceInputAppTranscriptRequest,
    ) -> FrameworkVoiceInputAppTranscriptResult:
        self._require_preconditions(request)
        framework_root = self._resolve_framework_root()

        acquired = bool(self._execution_lock.acquire(blocking=False))
        if not acquired:
            raise FrameworkVoiceInputAppTranscriptError(
                "app_transcript_busy",
                "Voice-input transcription is already active.",
                retryable=True,
            )

        try:
            return self._store.consume(
                request.staging_id,
                lambda artifact_path, metadata: self._execute(
                    framework_root=framework_root,
                    artifact_path=artifact_path,
                    metadata=metadata,
                    request=request,
                ),
            )
        except VoiceInputStagingError:
            raise
        finally:
            self._execution_lock.release()

    def _require_preconditions(
        self,
        request: FrameworkVoiceInputAppTranscriptRequest,
    ) -> None:
        if not request.foreground_opt_in:
            raise FrameworkVoiceInputAppTranscriptError(
                "foreground_opt_in_required",
                "Foreground voice-input opt-in is required.",
                retryable=False,
            )
        if not self._config.voice_input_demo_enabled:
            raise FrameworkVoiceInputAppTranscriptError(
                "voice_input_demo_disabled",
                "Voice input is disabled.",
                retryable=False,
            )
        if self._config.conversation_engine.strip().lower() != "framework":
            raise FrameworkVoiceInputAppTranscriptError(
                "voice_input_engine_not_framework",
                "Voice input requires Framework conversation mode.",
                retryable=False,
            )
        if self._config.voice_input_adapter_mode.strip().lower() != "framework":
            raise FrameworkVoiceInputAppTranscriptError(
                "voice_input_adapter_not_framework",
                "Voice input requires the Framework adapter mode.",
                retryable=False,
            )
        if not self._config.voice_input_real_stt_enabled:
            raise FrameworkVoiceInputAppTranscriptError(
                "real_stt_disabled",
                "Real voice-input transcription is disabled.",
                retryable=False,
            )
        if not self._credential_source.is_available():
            raise FrameworkVoiceInputAppTranscriptError(
                "private_credential_unavailable",
                "Private voice-input credentials are unavailable.",
                retryable=False,
            )

    def _resolve_framework_root(self) -> Path:
        configured = self._config.framework_project_root
        if not configured:
            raise FrameworkVoiceInputAppTranscriptError(
                "framework_root_not_configured",
                "Framework root is not configured.",
                retryable=True,
            )
        try:
            root = Path(configured).expanduser().resolve()
        except OSError as exc:
            raise FrameworkVoiceInputAppTranscriptError(
                "framework_root_invalid",
                "Configured Framework root is invalid.",
                retryable=True,
            ) from exc
        if not root.is_dir() or not (root / "framework" / "__init__.py").is_file():
            raise FrameworkVoiceInputAppTranscriptError(
                "framework_root_invalid",
                "Configured Framework root is unavailable.",
                retryable=True,
            )
        return root

    def _execute(
        self,
        *,
        framework_root: Path,
        artifact_path: Path,
        metadata: StagedVoiceInputArtifact,
        request: FrameworkVoiceInputAppTranscriptRequest,
    ) -> FrameworkVoiceInputAppTranscriptResult:
        if metadata.byte_count > self._config.voice_input_staging_max_bytes:
            raise FrameworkVoiceInputAppTranscriptError(
                "staged_audio_too_large",
                "Staged voice input exceeds the configured byte limit.",
                retryable=False,
            )

        try:
            with self._public_api_context_factory(framework_root) as public_api:
                self._require_public_audio_contract(public_api)

                @contextmanager
                def reuse_public_api(_root: Path):
                    yield public_api

                assembler = FrameworkVoiceInputOpenAIRealExecutorAssembler(
                    self._config,
                    public_api_context_factory=reuse_public_api,
                )
                assembly = assembler.assemble_for_private_operator(
                    FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest(
                        model=request.model,
                        max_audio_bytes=self._config.voice_input_staging_max_bytes,
                        timeout_seconds=request.timeout_seconds,
                        max_retries=0,
                        operator_handoff_enabled=True,
                        allow_provider_execution=True,
                        credentials_available=True,
                        allow_provider_sdk_import=True,
                        allow_provider_client_creation=True,
                        allow_real_provider_execution=True,
                    ),
                    private_credential_builder=self._credential_source.build_for,
                )

                audio_format = public_api.VoiceInputAudioFormat.wav(
                    sample_rate_hz=16000,
                    channel_count=1,
                    duration_ms=request.duration_ms,
                    byte_count=metadata.byte_count,
                    host_owner="drc_backend_private_staging",
                    private_path_exposed=False,
                )
                audio_source = public_api.VoiceInputAudioSource.from_file_path(
                    str(artifact_path),
                    audio_format=audio_format,
                    language=request.language,
                    max_duration_ms=request.max_duration_ms,
                    public_metadata={
                        "host_app": "DRC",
                        "artifact_scope": "backend_private_staging",
                        "single_use_cleanup_required": True,
                        "private_path_exposed": False,
                    },
                )
                voice_request = public_api.VoiceInputRequest(
                    language=request.language,
                    timeout_ms=max(1, int(request.timeout_seconds * 1000)),
                    max_duration_ms=request.max_duration_ms,
                    metadata={
                        "host_app": "DRC",
                        "execution_mode": "app_visible_real_stt",
                        "real_provider_execution_allowed": True,
                        "transcript_public_output_allowed": True,
                    },
                )
                result = assembly.private_operator_executor.execute(
                    audio_source=audio_source,
                    request=voice_request,
                )
        except FrameworkVoiceInputAppTranscriptError:
            raise
        except PrivateVoiceInputCredentialError as exc:
            raise FrameworkVoiceInputAppTranscriptError(
                exc.code,
                str(exc),
                retryable=False,
            ) from exc
        except FrameworkVoiceInputOpenAIRealExecutorAssemblyError as exc:
            raise FrameworkVoiceInputAppTranscriptError(
                exc.code,
                str(exc),
                retryable=exc.retryable,
            ) from exc
        except Exception as exc:
            raise FrameworkVoiceInputAppTranscriptError(
                "framework_app_transcript_execution_failed",
                "Framework voice-input transcription failed safely.",
                retryable=True,
            ) from exc

        public_metadata = dict(getattr(result, "public_metadata", {}) or {})
        unsafe_true_keys = (
            "private_path_exposed",
            "audio_path_exposed",
            "raw_audio_exposed",
            "provider_payload_exposed",
            "provider_response_exposed",
            "provider_error_body_exposed",
            "request_id_exposed",
            "credential_exposed",
            "private_credential_exposed",
            "microphone_accessed",
        )
        if any(bool(public_metadata.get(key, False)) for key in unsafe_true_keys):
            raise FrameworkVoiceInputAppTranscriptError(
                "unsafe_app_transcript_result",
                "Framework voice-input result reported unsafe exposure.",
                retryable=False,
            )

        outcome = _enum_value(getattr(result, "outcome", "failed"))
        completed = bool(getattr(result, "is_completed", outcome == "completed"))
        transcript = str(getattr(result, "text", "") or "").strip()
        if not completed or outcome != "completed" or not transcript:
            raise FrameworkVoiceInputAppTranscriptError(
                "real_transcript_unavailable",
                "Voice-input transcription did not return a final transcript.",
                retryable=bool(getattr(result, "retryable", True)),
            )
        if len(transcript) > _MAX_TRANSCRIPT_CODE_POINTS:
            raise FrameworkVoiceInputAppTranscriptError(
                "transcript_too_large",
                "Voice-input transcript exceeded the configured text limit.",
                retryable=False,
            )

        return FrameworkVoiceInputAppTranscriptResult(
            result_id=uuid4().hex,
            text=transcript,
            is_final=True,
        )

    @staticmethod
    def _require_public_audio_contract(public_api: _FrameworkVoiceInputPublicApi) -> None:
        for name in ("VoiceInputAudioFormat", "VoiceInputAudioSource", "VoiceInputRequest"):
            if getattr(public_api, name, None) is None:
                raise FrameworkVoiceInputAppTranscriptError(
                    "public_voice_input_audio_contract_missing",
                    "Configured Framework is missing the public audio contract.",
                    retryable=True,
                )
