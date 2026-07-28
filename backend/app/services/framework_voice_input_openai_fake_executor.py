from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    FrameworkVoiceInputFakeHandoffError,
    _FrameworkVoiceInputPublicApi,
    framework_voice_input_public_api_context,
)
from app.services.voice_input_staging_store import (
    StagedVoiceInputArtifact,
    VoiceInputStagingError,
    VoiceInputStagingStore,
)


@dataclass(frozen=True)
class FrameworkVoiceInputOpenAIFakeExecutorRequest:
    """Safe request for one bounded FW v5.4.0 marked-fake execution."""

    staging_id: str
    language: str | None = "ja"
    duration_ms: int | None = None
    max_duration_ms: int = 15000

    def __post_init__(self) -> None:
        if self.duration_ms is not None and self.duration_ms <= 0:
            raise ValueError("duration_ms must be positive when provided")
        if self.max_duration_ms <= 0:
            raise ValueError("max_duration_ms must be positive")
        if self.duration_ms is not None and self.duration_ms > self.max_duration_ms:
            raise ValueError("duration_ms must not exceed max_duration_ms")


@dataclass(frozen=True)
class FrameworkVoiceInputOpenAIFakeExecutorResult:
    """Path-free normalized result from the bounded marked-fake executor."""

    status: str
    request_state: str
    outcome: str
    transcript: str
    language: str | None
    duration_ms: int | None
    public_error_code: str
    safe_message: str
    retryable: bool
    framework_api_name: str
    adapter_name: str
    executor_name: str
    fake_transcription_completed: bool
    fake_provider_protocol_call_executed: bool
    staged_artifact_consumed: bool
    audio_read: bool
    audio_bytes_read: int
    microphone_accessed: bool
    provider_sdk_imported: bool
    provider_client_created: bool
    credential_values_read: bool
    real_provider_execution_executed: bool
    fake_stt_executed: bool
    real_stt_executed: bool


class FrameworkVoiceInputOpenAIFakeExecutorError(RuntimeError):
    """Typed public-safe failure for the DRC bounded fake-executor boundary."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class _MarkedFakeTranscriptions:
    def __init__(self, transcript: str) -> None:
        self._transcript = transcript
        self.calls = 0
        self.audio_bytes_seen = 0
        self.model_seen = ""
        self.language_seen: str | None = None

    def create(self, **kwargs: Any) -> object:
        self.calls += 1
        payload = kwargs.get("file")
        if not isinstance(payload, BytesIO):
            raise TypeError("marked fake client requires an in-memory WAV payload")
        audio_bytes = payload.read()
        self.audio_bytes_seen = len(audio_bytes)
        self.model_seen = str(kwargs.get("model", ""))
        language = kwargs.get("language")
        self.language_seen = str(language) if language is not None else None
        return {
            "text": self._transcript,
            "language": self.language_seen,
        }


class _MarkedFakeAudio:
    def __init__(self, transcript: str) -> None:
        self.transcriptions = _MarkedFakeTranscriptions(transcript)


def _build_marked_fake_client(marker_type: type[Any], transcript: str) -> Any:
    class DRCMarkedFakeOpenAIClient(marker_type):
        ai_character_framework_fake_stt_client = True

        def __init__(self) -> None:
            self.audio = _MarkedFakeAudio(transcript)

    return DRCMarkedFakeOpenAIClient()


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


class FrameworkVoiceInputOpenAIFakeExecutorAdapter:
    """Consume one private staged WAV through FW's bounded marked-fake executor.

    This adapter imports only the configured Framework public package, constructs
    an explicit OpenAI provider-execution configuration, injects a nominally
    marked fake client, and executes only ``OpenAIVoiceInputFakeExecutor``.
    No credential value, OpenAI SDK, real provider client, network request, or
    microphone is used.
    """

    _MODEL = "drc-v300-marked-fake-transcribe"
    _TRANSCRIPT = "DRC bounded marked-fake STT transcript"

    def __init__(
        self,
        config: AppConfig,
        store: VoiceInputStagingStore,
        *,
        public_api_context_factory: Callable[[Path], Any] | None = None,
        fake_transcript: str | None = None,
    ) -> None:
        self._config = config
        self._store = store
        self._public_api_context_factory = (
            public_api_context_factory or framework_voice_input_public_api_context
        )
        self._fake_transcript = fake_transcript or self._TRANSCRIPT

    def transcribe_staged_artifact(
        self,
        request: FrameworkVoiceInputOpenAIFakeExecutorRequest,
    ) -> FrameworkVoiceInputOpenAIFakeExecutorResult:
        framework_root = self._resolve_framework_root()

        try:
            with self._public_api_context_factory(framework_root) as public_api:
                module = self._require_executor_contract(public_api)
                return self._store.consume(
                    request.staging_id,
                    lambda path, metadata: self._execute(
                        public_api,
                        module,
                        path,
                        metadata,
                        request,
                    ),
                )
        except FrameworkVoiceInputOpenAIFakeExecutorError:
            raise
        except FrameworkVoiceInputFakeHandoffError as exc:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                exc.code,
                str(exc),
                retryable=exc.retryable,
            ) from exc
        except VoiceInputStagingError as exc:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                exc.code,
                str(exc),
                retryable=exc.code in {"cleanup_failed", "staging_failed"},
            ) from exc
        except Exception as exc:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "framework_openai_fake_executor_failed",
                "Framework bounded marked-fake execution failed safely.",
                retryable=True,
            ) from exc

    def _resolve_framework_root(self) -> Path:
        configured = self._config.framework_project_root
        if not configured:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "framework_root_not_configured",
                "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
                retryable=True,
            )
        try:
            root = Path(configured).expanduser().resolve()
        except OSError as exc:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "framework_root_invalid",
                "Configured Framework root could not be resolved.",
                retryable=True,
            ) from exc
        if not root.is_dir() or not (root / "framework" / "__init__.py").is_file():
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "framework_root_invalid",
                "Configured Framework root does not expose the public framework package.",
                retryable=True,
            )
        return root

    def _require_executor_contract(
        self,
        public_api: _FrameworkVoiceInputPublicApi,
    ) -> Any:
        module = public_api.module
        required = (
            "resolve_voice_input_provider_execution_config",
            "OpenAIVoiceInputProviderAdapter",
            "OpenAIVoiceInputFakeClientMarker",
            "OpenAIVoiceInputFakeExecutionPolicy",
            "OpenAIVoiceInputFakeExecutor",
        )
        missing = (
            required
            if module is None
            else tuple(name for name in required if not hasattr(module, name))
        )
        if missing:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "public_openai_fake_executor_contract_missing",
                "Configured Framework is missing the public bounded fake-executor contract.",
                retryable=True,
            )
        marker_type = getattr(module, "OpenAIVoiceInputFakeClientMarker")
        if not isinstance(marker_type, type):
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "public_openai_fake_executor_contract_missing",
                "Configured Framework exposes an invalid fake-client marker.",
                retryable=True,
            )
        return module

    def _execute(
        self,
        public_api: _FrameworkVoiceInputPublicApi,
        module: Any,
        artifact_path: Path,
        metadata: StagedVoiceInputArtifact,
        request: FrameworkVoiceInputOpenAIFakeExecutorRequest,
    ) -> FrameworkVoiceInputOpenAIFakeExecutorResult:
        execution_config = module.resolve_voice_input_provider_execution_config(
            provider="openai",
            allow_provider_execution=True,
            credentials_available=True,
        )
        client = _build_marked_fake_client(
            module.OpenAIVoiceInputFakeClientMarker,
            self._fake_transcript,
        )
        adapter = module.OpenAIVoiceInputProviderAdapter(
            execution_config=execution_config,
            model=self._MODEL,
            client=client,
            public_metadata={
                "host_app": "DRC",
                "execution_mode": "bounded_marked_fake",
                "credential_values_read": False,
            },
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
            max_duration_ms=request.max_duration_ms,
            metadata={
                "host_app": "DRC",
                "execution_mode": "bounded_marked_fake",
                "real_provider_execution_allowed": False,
            },
        )
        executor = module.OpenAIVoiceInputFakeExecutor(
            adapter=adapter,
            policy=module.OpenAIVoiceInputFakeExecutionPolicy(
                max_audio_bytes=self._config.voice_input_staging_max_bytes,
                allow_fake_client_execution=True,
            ),
        )
        result = executor.execute(
            audio_source=audio_source,
            request=voice_request,
        )

        public_metadata = dict(getattr(result, "public_metadata", {}) or {})
        unsafe_true_keys = (
            "provider_sdk_imported",
            "provider_client_created",
            "credential_values_read",
            "real_provider_execution_executed",
            "audio_path_exposed",
            "raw_audio_exposed",
            "provider_payload_exposed",
            "microphone_accessed",
        )
        if any(bool(public_metadata.get(key, False)) for key in unsafe_true_keys):
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "unsafe_openai_fake_executor_result",
                "Framework marked-fake execution reported an unsafe side effect.",
                retryable=False,
            )

        fake_status = str(public_metadata.get("fake_execution_status", ""))
        fake_call = bool(
            public_metadata.get("fake_provider_protocol_call_executed", False)
        )
        audio_bytes_read = int(public_metadata.get("audio_bytes_read", 0) or 0)
        transcriptions = client.audio.transcriptions
        if (
            fake_status != "completed"
            or not fake_call
            or transcriptions.calls != 1
            or transcriptions.audio_bytes_seen != metadata.byte_count
            or audio_bytes_read != metadata.byte_count
            or transcriptions.model_seen != self._MODEL
        ):
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "unexpected_openai_fake_executor_contract",
                "Framework marked-fake execution returned an unexpected contract.",
                retryable=False,
            )

        outcome = _enum_value(getattr(result, "outcome", "failed"))
        transcript = str(getattr(result, "text", "") or "")
        completed = bool(getattr(result, "is_completed", outcome == "completed"))
        if not completed or not transcript:
            raise FrameworkVoiceInputOpenAIFakeExecutorError(
                "fake_transcript_unavailable",
                "Framework marked-fake execution did not return a completed transcript.",
                retryable=True,
            )

        return FrameworkVoiceInputOpenAIFakeExecutorResult(
            status="completed",
            request_state="marked_fake_transcribed",
            outcome=outcome,
            transcript=transcript,
            language=getattr(result, "language", None),
            duration_ms=getattr(result, "duration_ms", None),
            public_error_code=_enum_value(
                getattr(result, "public_error_code", "provider_error")
            ),
            safe_message=str(getattr(result, "safe_message", "") or ""),
            retryable=bool(getattr(result, "retryable", False)),
            framework_api_name="OpenAIVoiceInputFakeExecutor.execute",
            adapter_name="openai",
            executor_name="openai_marked_fake",
            fake_transcription_completed=True,
            fake_provider_protocol_call_executed=True,
            staged_artifact_consumed=True,
            audio_read=audio_bytes_read > 0,
            audio_bytes_read=audio_bytes_read,
            microphone_accessed=False,
            provider_sdk_imported=False,
            provider_client_created=False,
            credential_values_read=False,
            real_provider_execution_executed=False,
            fake_stt_executed=True,
            real_stt_executed=False,
        )
