from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
    framework_voice_input_public_api_context,
)
from app.services.framework_voice_input_openai_real_executor_assembly import (
    FrameworkVoiceInputOpenAIRealExecutorAssembler,
    FrameworkVoiceInputOpenAIRealExecutorAssemblyError,
    FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest,
    PrivateCredentialBuilder,
)
from app.services.voice_input_staging_store import (
    StagedVoiceInputArtifact,
    VoiceInputStagingStore,
)


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


@dataclass(frozen=True)
class FrameworkVoiceInputOpenAIRealOperatorRequest:
    """Explicit operator-only request for one staged real-STT execution."""

    staging_id: str
    language: str | None = "ja"
    duration_ms: int | None = None
    max_duration_ms: int = 15000
    model: str = "gpt-4o-mini-transcribe"
    max_audio_bytes: int = 1048576
    timeout_seconds: float = 120.0
    max_retries: int = 0
    operator_handoff_enabled: bool = False
    allow_provider_execution: bool = False
    credentials_available: bool = False
    allow_provider_sdk_import: bool = False
    allow_provider_client_creation: bool = False
    allow_real_provider_execution: bool = False

    def __post_init__(self) -> None:
        staging_id = str(self.staging_id).strip()
        model = str(self.model).strip()
        language = None if self.language is None else str(self.language).strip()

        if not staging_id:
            raise ValueError("staging_id must be non-empty")
        if not model:
            raise ValueError("model must be non-empty")
        if language == "":
            language = None
        if self.duration_ms is not None and self.duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        if self.max_duration_ms <= 0:
            raise ValueError("max_duration_ms must be positive")
        if (
            self.duration_ms is not None
            and self.duration_ms > self.max_duration_ms
        ):
            raise ValueError("duration_ms must not exceed max_duration_ms")
        if self.max_audio_bytes <= 0:
            raise ValueError("max_audio_bytes must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        object.__setattr__(self, "staging_id", staging_id)
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "language", language)


@dataclass(frozen=True)
class FrameworkVoiceInputOpenAIRealOperatorResult:
    """Public-safe result plus a private in-memory transcript handoff."""

    status: str
    request_state: str
    outcome: str
    language: str | None
    confidence: float | None
    duration_ms: int | None
    public_error_code: str
    safe_message: str
    retryable: bool
    framework_api_name: str
    adapter_name: str
    executor_name: str
    real_transcription_completed: bool
    staged_artifact_consumed: bool
    audio_read: bool
    audio_bytes_read: int
    microphone_accessed: bool
    provider_sdk_imported: bool
    provider_client_created: bool
    network_request_executed: bool
    real_provider_execution_executed: bool
    credential_value_read_by_drc: bool
    private_path_exposed: bool
    raw_audio_exposed: bool
    provider_payload_exposed: bool
    transcript_exposed: bool
    _transcript: str = field(repr=False, compare=False)

    @property
    def private_transcript(self) -> str:
        """Return the transcript only to the private operator caller."""

        return self._transcript


class FrameworkVoiceInputOpenAIRealOperatorError(RuntimeError):
    """Typed public-safe failure for the DRC private real-STT operator path."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        public_error_code: str = "provider_error",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.public_error_code = public_error_code


class FrameworkVoiceInputOpenAIRealOperatorAdapter:
    """Execute FW v5.4.0 real STT inside one private staging consume scope.

    This adapter does not resolve credentials itself. The private operator
    supplies a builder only after every execution opt-in gate is true.

    The staged private path exists only inside VoiceInputStagingStore.consume().
    The transcript remains an in-memory private field and is excluded from repr.
    No API route, console evidence, provider payload, private path, raw audio, or
    transcript persistence is added here.
    """

    def __init__(
        self,
        config: AppConfig,
        store: VoiceInputStagingStore,
        *,
        public_api_context_factory: Callable[[Path], Any] | None = None,
    ) -> None:
        self._config = config
        self._store = store
        self._public_api_context_factory = (
            public_api_context_factory
            or framework_voice_input_public_api_context
        )

    def transcribe_staged_artifact(
        self,
        request: FrameworkVoiceInputOpenAIRealOperatorRequest,
        *,
        private_credential_builder: PrivateCredentialBuilder,
    ) -> FrameworkVoiceInputOpenAIRealOperatorResult:
        self._require_explicit_operator_opt_in(request)
        if not callable(private_credential_builder):
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "private_credential_builder_required",
                "Private real-STT execution requires a credential-object builder.",
                retryable=False,
            )
        if request.max_audio_bytes > self._config.voice_input_staging_max_bytes:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "operator_audio_limit_exceeds_staging_limit",
                "Private real-STT audio limit exceeds the DRC staging limit.",
                retryable=False,
            )

        framework_root = self._resolve_framework_root()

        def consume(
            artifact_path: Path,
            metadata: StagedVoiceInputArtifact,
        ) -> FrameworkVoiceInputOpenAIRealOperatorResult:
            return self._execute(
                framework_root=framework_root,
                artifact_path=artifact_path,
                metadata=metadata,
                request=request,
                private_credential_builder=private_credential_builder,
            )

        return self._store.consume(request.staging_id, consume)

    def _execute(
        self,
        *,
        framework_root: Path,
        artifact_path: Path,
        metadata: StagedVoiceInputArtifact,
        request: FrameworkVoiceInputOpenAIRealOperatorRequest,
        private_credential_builder: PrivateCredentialBuilder,
    ) -> FrameworkVoiceInputOpenAIRealOperatorResult:
        if metadata.byte_count > request.max_audio_bytes:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "staged_audio_too_large",
                "Staged voice input exceeds the private operator audio limit.",
                retryable=False,
            )

        try:
            with self._public_api_context_factory(framework_root) as public_api:
                module = self._require_execution_contract(public_api)

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
                        max_audio_bytes=request.max_audio_bytes,
                        timeout_seconds=request.timeout_seconds,
                        max_retries=request.max_retries,
                        operator_handoff_enabled=(
                            request.operator_handoff_enabled
                        ),
                        allow_provider_execution=(
                            request.allow_provider_execution
                        ),
                        credentials_available=request.credentials_available,
                        allow_provider_sdk_import=(
                            request.allow_provider_sdk_import
                        ),
                        allow_provider_client_creation=(
                            request.allow_provider_client_creation
                        ),
                        allow_real_provider_execution=(
                            request.allow_real_provider_execution
                        ),
                    ),
                    private_credential_builder=private_credential_builder,
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
                        "execution_mode": "private_real_stt_operator",
                        "real_provider_execution_allowed": True,
                        "transcript_public_output_allowed": False,
                    },
                )
                result = assembly.private_operator_executor.execute(
                    audio_source=audio_source,
                    request=voice_request,
                )
        except FrameworkVoiceInputOpenAIRealOperatorError:
            raise
        except FrameworkVoiceInputOpenAIRealExecutorAssemblyError as exc:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                exc.code,
                str(exc),
                retryable=exc.retryable,
            ) from exc
        except Exception as exc:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "framework_real_operator_execution_failed",
                "Framework private real-STT execution failed safely.",
                retryable=True,
            ) from exc

        public_metadata = dict(
            getattr(result, "public_metadata", {}) or {}
        )
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
            "transcript_exposed",
            "microphone_accessed",
        )
        if any(
            bool(public_metadata.get(key, False))
            for key in unsafe_true_keys
        ):
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "unsafe_real_operator_result",
                "Framework real-STT execution reported unsafe public exposure.",
                retryable=False,
            )

        outcome = _enum_value(getattr(result, "outcome", "failed"))
        transcript = str(getattr(result, "text", "") or "")
        completed = bool(
            getattr(result, "is_completed", outcome == "completed")
        )
        if not completed or not transcript:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "real_transcript_unavailable",
                str(
                    getattr(
                        result,
                        "safe_message",
                        "Framework real-STT did not return a transcript.",
                    )
                    or "Framework real-STT did not return a transcript."
                ),
                retryable=bool(getattr(result, "retryable", True)),
                public_error_code=_enum_value(
                    getattr(result, "public_error_code", "provider_error")
                ),
            )

        audio_bytes_read = int(
            public_metadata.get("audio_bytes_read", metadata.byte_count) or 0
        )
        provider_execution = bool(
            public_metadata.get(
                "real_provider_execution_executed",
                public_metadata.get(
                    "provider_execution_executed",
                    completed,
                ),
            )
        )
        network_execution = bool(
            public_metadata.get(
                "network_request_executed",
                provider_execution,
            )
        )

        return FrameworkVoiceInputOpenAIRealOperatorResult(
            status="completed",
            request_state="private_real_stt_transcribed",
            outcome=outcome,
            language=getattr(result, "language", None),
            confidence=getattr(result, "confidence", None),
            duration_ms=getattr(result, "duration_ms", None),
            public_error_code=_enum_value(
                getattr(result, "public_error_code", "none")
            ),
            safe_message=str(getattr(result, "safe_message", "") or ""),
            retryable=bool(getattr(result, "retryable", False)),
            framework_api_name=(
                "OpenAIVoiceInputRealProviderExecutor.execute"
            ),
            adapter_name="openai",
            executor_name="openai_real_provider",
            real_transcription_completed=True,
            staged_artifact_consumed=True,
            audio_read=bool(
                public_metadata.get("audio_read", audio_bytes_read > 0)
            ),
            audio_bytes_read=audio_bytes_read,
            microphone_accessed=False,
            provider_sdk_imported=bool(
                public_metadata.get("provider_sdk_imported", False)
            ),
            provider_client_created=bool(
                public_metadata.get("provider_client_created", False)
            ),
            network_request_executed=network_execution,
            real_provider_execution_executed=provider_execution,
            credential_value_read_by_drc=False,
            private_path_exposed=False,
            raw_audio_exposed=False,
            provider_payload_exposed=False,
            transcript_exposed=False,
            _transcript=transcript,
        )

    @staticmethod
    def _require_explicit_operator_opt_in(
        request: FrameworkVoiceInputOpenAIRealOperatorRequest,
    ) -> None:
        required_flags = (
            request.operator_handoff_enabled,
            request.allow_provider_execution,
            request.credentials_available,
            request.allow_provider_sdk_import,
            request.allow_provider_client_creation,
            request.allow_real_provider_execution,
        )
        if not all(required_flags):
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "real_operator_opt_in_incomplete",
                "Private real-STT execution requires every explicit operator gate.",
                retryable=False,
            )

    def _resolve_framework_root(self) -> Path:
        configured = self._config.framework_project_root
        if not configured:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "framework_root_not_configured",
                "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
                retryable=True,
            )

        try:
            root = Path(configured).expanduser().resolve()
        except OSError as exc:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "framework_root_invalid",
                "Configured Framework root could not be resolved.",
                retryable=True,
            ) from exc

        if (
            not root.is_dir()
            or not (root / "framework" / "__init__.py").is_file()
        ):
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "framework_root_invalid",
                "Configured Framework root does not expose the public package.",
                retryable=True,
            )
        return root

    @staticmethod
    def _require_execution_contract(
        public_api: _FrameworkVoiceInputPublicApi,
    ) -> Any:
        module = public_api.module
        required_module_symbols = (
            "resolve_voice_input_provider_execution_config",
            "OpenAIVoiceInputPrivateCredential",
            "OpenAIVoiceInputRealProviderPolicy",
            "OpenAIVoiceInputRuntimeMode",
            "OpenAIVoiceInputRealClientFactory",
            "OpenAIVoiceInputProviderAdapter",
            "OpenAIVoiceInputRealProviderExecutor",
        )
        missing = (
            required_module_symbols
            if module is None
            else tuple(
                name
                for name in required_module_symbols
                if not hasattr(module, name)
            )
        )
        if missing:
            raise FrameworkVoiceInputOpenAIRealOperatorError(
                "public_openai_real_execution_contract_missing",
                "Configured Framework is missing the public real-STT contract.",
                retryable=True,
            )

        for name in (
            "VoiceInputAudioFormat",
            "VoiceInputAudioSource",
            "VoiceInputRequest",
        ):
            if getattr(public_api, name, None) is None:
                raise FrameworkVoiceInputOpenAIRealOperatorError(
                    "public_voice_input_audio_contract_missing",
                    "Configured Framework is missing the public audio contract.",
                    retryable=True,
                )
        return module
