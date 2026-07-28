from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import importlib
from pathlib import Path
import sys
from threading import RLock
from types import ModuleType
from typing import Any, Callable, Iterator

from app.config import AppConfig
from app.services.voice_input_staging_store import (
    StagedVoiceInputArtifact,
    VoiceInputStagingError,
    VoiceInputStagingStore,
)


@dataclass(frozen=True)
class FrameworkVoiceInputFakeHandoffRequest:
    """Safe DRC request for one fake FW public-session handoff."""

    staging_id: str
    language: str | None = "ja-JP"
    duration_ms: int | None = None
    max_duration_ms: int = 15000

    def __post_init__(self) -> None:
        if self.duration_ms is not None and self.duration_ms <= 0:
            raise ValueError("duration_ms must be positive when provided")
        if self.duration_ms is not None and self.duration_ms > self.max_duration_ms:
            raise ValueError("duration_ms must not exceed max_duration_ms")
        if self.max_duration_ms <= 0:
            raise ValueError("max_duration_ms must be positive")


@dataclass(frozen=True)
class FrameworkVoiceInputFakeHandoffResult:
    """Path-free normalized result from the FW fake voice-input adapter."""

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
    fake_transcription_completed: bool
    staged_artifact_consumed: bool
    session_closed: bool
    audio_read: bool
    microphone_accessed: bool
    provider_execution_executed: bool
    stt_executed: bool = False


class FrameworkVoiceInputFakeHandoffError(RuntimeError):
    """Typed safe failure for the DRC-to-FW fake handoff boundary."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


@dataclass(frozen=True)
class _FrameworkVoiceInputPublicApi:
    VoiceInputAudioFormat: Any
    VoiceInputAudioSource: Any
    VoiceInputRequest: Any
    FakeVoiceInputProviderAdapter: Any
    create_voice_input_session: Callable[..., Any]
    module: ModuleType | None = None


_PublicApiContextFactory = Callable[[Path], Iterator[_FrameworkVoiceInputPublicApi]]
_FRAMEWORK_PUBLIC_IMPORT_LOCK = RLock()


class FrameworkVoiceInputFakeHandoffAdapter:
    """Consume one staged WAV through FW v5.3.0 public fake STT contracts.

    The adapter passes a private Backend file path only into the data-only FW
    ``VoiceInputAudioSource`` constructor while the staging-store consume scope
    is active. It explicitly selects ``FakeVoiceInputProviderAdapter`` and never
    enables provider execution. The staged file is single-use and is removed by
    ``VoiceInputStagingStore.consume`` on success or callback failure.
    """

    _FAKE_TRANSCRIPT = "DRC fake STT public-session transcript"

    def __init__(
        self,
        config: AppConfig,
        store: VoiceInputStagingStore,
        *,
        public_api_context_factory: Callable[
            [Path], Any
        ] | None = None,
        fake_transcript: str | None = None,
    ) -> None:
        self._config = config
        self._store = store
        self._public_api_context_factory = (
            public_api_context_factory or framework_voice_input_public_api_context
        )
        self._fake_transcript = fake_transcript or self._FAKE_TRANSCRIPT

    def transcribe_staged_artifact(
        self,
        request: FrameworkVoiceInputFakeHandoffRequest,
    ) -> FrameworkVoiceInputFakeHandoffResult:
        framework_root = self._resolve_framework_root()

        try:
            with self._public_api_context_factory(framework_root) as public_api:
                return self._store.consume(
                    request.staging_id,
                    lambda path, metadata: self._run_public_fake_handoff(
                        public_api,
                        framework_root,
                        path,
                        metadata,
                        request,
                    ),
                )
        except FrameworkVoiceInputFakeHandoffError:
            raise
        except VoiceInputStagingError as exc:
            raise FrameworkVoiceInputFakeHandoffError(
                exc.code,
                str(exc),
                retryable=exc.code in {"cleanup_failed", "staging_failed"},
            ) from exc
        except Exception as exc:
            raise FrameworkVoiceInputFakeHandoffError(
                "framework_fake_handoff_failed",
                "Framework fake voice-input handoff failed safely.",
                retryable=True,
            ) from exc

    def _resolve_framework_root(self) -> Path:
        configured = self._config.framework_project_root
        if not configured:
            raise FrameworkVoiceInputFakeHandoffError(
                "framework_root_not_configured",
                "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
                retryable=True,
            )

        try:
            framework_root = Path(configured).expanduser().resolve()
        except OSError as exc:
            raise FrameworkVoiceInputFakeHandoffError(
                "framework_root_invalid",
                "Configured Framework root could not be resolved.",
                retryable=True,
            ) from exc

        if not framework_root.is_dir() or not (
            framework_root / "framework" / "__init__.py"
        ).is_file():
            raise FrameworkVoiceInputFakeHandoffError(
                "framework_root_invalid",
                "Configured Framework root does not expose the public framework package.",
                retryable=True,
            )
        return framework_root

    def _run_public_fake_handoff(
        self,
        public_api: _FrameworkVoiceInputPublicApi,
        framework_root: Path,
        artifact_path: Path,
        metadata: StagedVoiceInputArtifact,
        request: FrameworkVoiceInputFakeHandoffRequest,
    ) -> FrameworkVoiceInputFakeHandoffResult:
        session: Any | None = None
        session_closed = False
        try:
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
                    "handoff_mode": "fake_public_session",
                    "provider_execution_allowed": False,
                },
            )
            fake_adapter = public_api.FakeVoiceInputProviderAdapter(
                transcript=self._fake_transcript,
                language=request.language,
                public_metadata={
                    "host_app": "DRC",
                    "synthetic_contract_check": True,
                },
            )
            session = public_api.create_voice_input_session(
                project_root=framework_root,
                language=request.language,
                real_stt_enabled=False,
                allow_provider_execution=False,
                public_metadata={
                    "host_app": "DRC",
                    "handoff_mode": "fake_public_session",
                },
            )
            result = session.transcribe_audio_result(
                audio_source,
                request=voice_request,
                adapter=fake_adapter,
            )
        except FrameworkVoiceInputFakeHandoffError:
            raise
        except Exception as exc:
            raise FrameworkVoiceInputFakeHandoffError(
                "framework_fake_session_failed",
                "Framework fake voice-input session failed safely.",
                retryable=True,
            ) from exc
        finally:
            if session is not None:
                try:
                    session.close()
                    session_closed = bool(getattr(session, "is_closed", True))
                except Exception as exc:
                    raise FrameworkVoiceInputFakeHandoffError(
                        "framework_session_close_failed",
                        "Framework voice-input session cleanup failed.",
                        retryable=True,
                    ) from exc

        if not session_closed:
            raise FrameworkVoiceInputFakeHandoffError(
                "framework_session_not_closed",
                "Framework voice-input session did not report a closed state.",
                retryable=True,
            )

        public_metadata = dict(getattr(result, "public_metadata", {}) or {})
        audio_read = bool(public_metadata.get("audio_read", False))
        microphone_accessed = bool(public_metadata.get("microphone_accessed", False))
        provider_execution_executed = bool(
            public_metadata.get("provider_execution_executed", False)
        )
        adapter_name = str(public_metadata.get("adapter", ""))
        source_kind = str(public_metadata.get("source_kind", ""))

        if audio_read or microphone_accessed or provider_execution_executed:
            raise FrameworkVoiceInputFakeHandoffError(
                "unsafe_fake_handoff_result",
                "Framework fake handoff reported an unexpected runtime side effect.",
                retryable=False,
            )
        if adapter_name != "fake" or source_kind != "file_path":
            raise FrameworkVoiceInputFakeHandoffError(
                "unexpected_fake_handoff_contract",
                "Framework fake handoff returned an unexpected public contract.",
                retryable=False,
            )

        outcome = _enum_value(getattr(result, "outcome", "failed"))
        public_error_code = _enum_value(
            getattr(result, "public_error_code", "provider_error")
        )
        transcript = str(getattr(result, "text", "") or "")
        completed = bool(getattr(result, "is_completed", outcome == "completed"))
        if not completed or not transcript:
            raise FrameworkVoiceInputFakeHandoffError(
                "fake_transcript_unavailable",
                "Framework fake handoff did not return a completed transcript.",
                retryable=True,
            )

        return FrameworkVoiceInputFakeHandoffResult(
            status="completed",
            request_state="fake_transcribed",
            outcome=outcome,
            transcript=transcript,
            language=getattr(result, "language", None),
            duration_ms=getattr(result, "duration_ms", None),
            public_error_code=public_error_code,
            safe_message=str(getattr(result, "safe_message", "") or ""),
            retryable=bool(getattr(result, "retryable", False)),
            framework_api_name=(
                "create_voice_input_session.transcribe_audio_result"
            ),
            adapter_name=adapter_name,
            fake_transcription_completed=True,
            staged_artifact_consumed=True,
            session_closed=session_closed,
            audio_read=False,
            microphone_accessed=False,
            provider_execution_executed=False,
            stt_executed=False,
        )


def _enum_value(value: Any) -> str:
    enum_value = getattr(value, "value", value)
    return str(enum_value)


@contextmanager
def framework_voice_input_public_api_context(
    framework_root: Path,
) -> Iterator[_FrameworkVoiceInputPublicApi]:
    """Temporarily import only the configured FW public package."""

    with _FRAMEWORK_PUBLIC_IMPORT_LOCK:
        original_sys_path = list(sys.path)
        saved_framework_modules = {
            name: module
            for name, module in sys.modules.items()
            if name == "framework" or name.startswith("framework.")
        }

        for name in saved_framework_modules:
            sys.modules.pop(name, None)

        sys.path.insert(0, str(framework_root))
        importlib.invalidate_caches()
        try:
            try:
                module = importlib.import_module("framework")
            except Exception as exc:
                raise FrameworkVoiceInputFakeHandoffError(
                    "public_framework_import_failed",
                    "Configured Framework public package could not be imported.",
                    retryable=True,
                ) from exc
            yield _public_api_from_module(module)
        finally:
            for name in list(sys.modules):
                if name == "framework" or name.startswith("framework."):
                    sys.modules.pop(name, None)
            sys.modules.update(saved_framework_modules)
            sys.path[:] = original_sys_path
            importlib.invalidate_caches()


def _public_api_from_module(module: ModuleType) -> _FrameworkVoiceInputPublicApi:
    required = (
        "VoiceInputAudioFormat",
        "VoiceInputAudioSource",
        "VoiceInputRequest",
        "FakeVoiceInputProviderAdapter",
        "create_voice_input_session",
    )
    missing = tuple(name for name in required if not hasattr(module, name))
    if missing:
        raise FrameworkVoiceInputFakeHandoffError(
            "public_voice_input_contract_missing",
            "Configured Framework is missing the required public voice-input contract.",
            retryable=True,
        )
    return _FrameworkVoiceInputPublicApi(
        VoiceInputAudioFormat=getattr(module, "VoiceInputAudioFormat"),
        VoiceInputAudioSource=getattr(module, "VoiceInputAudioSource"),
        VoiceInputRequest=getattr(module, "VoiceInputRequest"),
        FakeVoiceInputProviderAdapter=getattr(
            module, "FakeVoiceInputProviderAdapter"
        ),
        create_voice_input_session=getattr(module, "create_voice_input_session"),
        module=module,
    )
