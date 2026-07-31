from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from types import SimpleNamespace

import pytest

from app.config import AppConfig
from app.services.framework_voice_input_app_transcript import (
    FrameworkVoiceInputAppTranscriptAdapter,
    FrameworkVoiceInputAppTranscriptError,
    FrameworkVoiceInputAppTranscriptRequest,
)
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
)
from app.services.private_voice_input_credential_source import (
    PrivateVoiceInputCredentialSource,
)
from app.services.voice_input_staging_store import VoiceInputStagingStore


def _wav_bytes(payload_size: int = 24) -> bytes:
    return (
        b"RIFF"
        + (payload_size + 4).to_bytes(4, "little")
        + b"WAVE"
        + (b"\x00" * payload_size)
    )


def _framework_root(tmp_path: Path) -> Path:
    root = tmp_path / "fw"
    package = root / "framework"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("# synthetic public package\n")
    return root


def _config(root: Path, **overrides) -> AppConfig:
    values = {
        "conversation_engine": "framework",
        "framework_project_root": str(root),
        "voice_input_demo_enabled": True,
        "voice_input_adapter_mode": "framework",
        "voice_input_staging_max_bytes": 1024,
        "voice_input_real_stt_enabled": True,
    }
    values.update(overrides)
    return AppConfig(**values)


def _credential_source(value: str | None = "synthetic-private-value"):
    return PrivateVoiceInputCredentialSource(
        _environment_reader=lambda _name: value,
    )


def _api_context(
    *,
    transcript: str = "synthetic final transcript",
    completed: bool = True,
    unsafe: bool = False,
):
    @contextmanager
    def context(_root: Path):
        class AudioFormat:
            @classmethod
            def wav(cls, **kwargs):
                return SimpleNamespace(**kwargs)

        class AudioSource:
            @classmethod
            def from_file_path(cls, path: str, **kwargs):
                return SimpleNamespace(
                    path=path,
                    ref=SimpleNamespace(value=path),
                    **kwargs,
                )

        class VoiceRequest:
            def __init__(self, **kwargs) -> None:
                self.__dict__.update(kwargs)

        class Credential:
            def __init__(self, api_key: str) -> None:
                if not api_key:
                    raise ValueError("missing key")
                self._api_key = api_key

            def __repr__(self) -> str:
                return "Credential(<redacted>)"

        class RuntimeMode:
            REAL = "real"

        class Policy:
            def __init__(self, **kwargs) -> None:
                self.__dict__.update(kwargs)

        class ClientFactory:
            def __init__(self, *, credential, policy) -> None:
                self.credential = credential
                self.policy = policy

        class Adapter:
            def __init__(
                self,
                *,
                execution_config,
                model,
                client_factory,
                public_metadata,
            ) -> None:
                self.execution_config = execution_config
                self.model = model
                self.client_factory = client_factory
                self.public_metadata = public_metadata
                self.client = None

        class Executor:
            def __init__(self, *, adapter) -> None:
                self.adapter = adapter

            def execute(self, *, audio_source, request):
                audio = Path(audio_source.path).read_bytes()
                return SimpleNamespace(
                    outcome=SimpleNamespace(
                        value="completed" if completed else "failed"
                    ),
                    text=transcript if completed else "",
                    language=request.language,
                    duration_ms=audio_source.audio_format.duration_ms,
                    public_error_code=SimpleNamespace(
                        value="none" if completed else "provider_error"
                    ),
                    safe_message="" if completed else "synthetic failure",
                    retryable=not completed,
                    is_completed=completed,
                    public_metadata={
                        "audio_bytes_read": len(audio),
                        "provider_sdk_imported": False,
                        "provider_client_created": False,
                        "real_provider_execution_executed": completed,
                        "private_path_exposed": unsafe,
                        "audio_path_exposed": False,
                        "raw_audio_exposed": False,
                        "provider_payload_exposed": False,
                        "microphone_accessed": False,
                    },
                )

        def resolve_config(**_kwargs):
            return SimpleNamespace(configured=True)

        module = SimpleNamespace(
            resolve_voice_input_provider_execution_config=resolve_config,
            OpenAIVoiceInputPrivateCredential=Credential,
            OpenAIVoiceInputRealProviderPolicy=Policy,
            OpenAIVoiceInputRuntimeMode=RuntimeMode,
            OpenAIVoiceInputRealClientFactory=ClientFactory,
            OpenAIVoiceInputProviderAdapter=Adapter,
            OpenAIVoiceInputRealProviderExecutor=Executor,
        )
        yield _FrameworkVoiceInputPublicApi(
            VoiceInputAudioFormat=AudioFormat,
            VoiceInputAudioSource=AudioSource,
            VoiceInputRequest=VoiceRequest,
            FakeVoiceInputProviderAdapter=object,
            create_voice_input_session=lambda **_kwargs: None,
            module=module,
        )

    return context


def _adapter(
    tmp_path: Path,
    *,
    config: AppConfig | None = None,
    credential_value: str | None = "synthetic-private-value",
    transcript: str = "synthetic final transcript",
    completed: bool = True,
    unsafe: bool = False,
    execution_lock=None,
):
    root = _framework_root(tmp_path)
    config = config or _config(root)
    store = VoiceInputStagingStore(root_dir=tmp_path / "private", config=config)
    adapter = FrameworkVoiceInputAppTranscriptAdapter(
        config,
        store,
        _credential_source(credential_value),
        public_api_context_factory=_api_context(
            transcript=transcript,
            completed=completed,
            unsafe=unsafe,
        ),
        execution_lock=execution_lock,
    )
    return adapter, store


def _request(staging_id: str, **overrides):
    values = {
        "staging_id": staging_id,
        "foreground_opt_in": True,
        "language": "ja",
        "duration_ms": 1000,
    }
    values.update(overrides)
    return FrameworkVoiceInputAppTranscriptRequest(**values)


def test_app_transcript_success_consumes_once_and_hides_text_from_repr(tmp_path):
    adapter, store = _adapter(tmp_path)
    staged = store.stage_chunks((_wav_bytes(),))

    result = adapter.transcribe_staged_artifact(_request(staged.staging_id))

    assert result.is_final is True
    assert result.text == "synthetic final transcript"
    assert len(result.result_id) == 32
    assert result.text not in repr(result)
    assert staged.staging_id not in repr(result)
    assert store.artifact_count() == 0
    with pytest.raises(Exception):
        adapter.transcribe_staged_artifact(_request(staged.staging_id))


def test_missing_credential_fails_before_artifact_consume(tmp_path):
    adapter, store = _adapter(tmp_path, credential_value=None)
    staged = store.stage_chunks((_wav_bytes(),))

    with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
        adapter.transcribe_staged_artifact(_request(staged.staging_id))

    assert captured.value.code == "private_credential_unavailable"
    assert store.has_artifact(staged.staging_id) is True


def test_default_off_fails_before_artifact_consume(tmp_path):
    root = _framework_root(tmp_path)
    config = _config(root, voice_input_real_stt_enabled=False)
    store = VoiceInputStagingStore(root_dir=tmp_path / "private", config=config)
    adapter = FrameworkVoiceInputAppTranscriptAdapter(
        config,
        store,
        _credential_source(),
        public_api_context_factory=_api_context(),
    )
    staged = store.stage_chunks((_wav_bytes(),))

    with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
        adapter.transcribe_staged_artifact(_request(staged.staging_id))

    assert captured.value.code == "real_stt_disabled"
    assert store.has_artifact(staged.staging_id) is True


def test_foreground_opt_in_is_required_before_artifact_consume(tmp_path):
    adapter, store = _adapter(tmp_path)
    staged = store.stage_chunks((_wav_bytes(),))

    with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
        adapter.transcribe_staged_artifact(
            _request(staged.staging_id, foreground_opt_in=False)
        )

    assert captured.value.code == "foreground_opt_in_required"
    assert store.has_artifact(staged.staging_id) is True


def test_busy_slot_preserves_artifact(tmp_path):
    lock = Lock()
    lock.acquire()
    try:
        adapter, store = _adapter(tmp_path, execution_lock=lock)
        staged = store.stage_chunks((_wav_bytes(),))

        with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
            adapter.transcribe_staged_artifact(_request(staged.staging_id))

        assert captured.value.code == "app_transcript_busy"
        assert store.has_artifact(staged.staging_id) is True
    finally:
        lock.release()


@pytest.mark.parametrize(
    ("length", "accepted"),
    ((4096, True), (4097, False)),
)
def test_transcript_code_point_bound(tmp_path, length, accepted):
    adapter, store = _adapter(tmp_path, transcript="あ" * length)
    staged = store.stage_chunks((_wav_bytes(),))

    if accepted:
        result = adapter.transcribe_staged_artifact(_request(staged.staging_id))
        assert len(result.text) == 4096
    else:
        with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
            adapter.transcribe_staged_artifact(_request(staged.staging_id))
        assert captured.value.code == "transcript_too_large"
    assert store.artifact_count() == 0


def test_nonfinal_or_unsafe_result_is_rejected_and_consumed(tmp_path):
    adapter, store = _adapter(tmp_path, completed=False)
    staged = store.stage_chunks((_wav_bytes(),))
    with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
        adapter.transcribe_staged_artifact(_request(staged.staging_id))
    assert captured.value.code == "real_transcript_unavailable"
    assert store.artifact_count() == 0

    unsafe_adapter, unsafe_store = _adapter(tmp_path / "unsafe", unsafe=True)
    unsafe_staged = unsafe_store.stage_chunks((_wav_bytes(),))
    with pytest.raises(FrameworkVoiceInputAppTranscriptError) as captured:
        unsafe_adapter.transcribe_staged_artifact(_request(unsafe_staged.staging_id))
    assert captured.value.code == "unsafe_app_transcript_result"
    assert unsafe_store.artifact_count() == 0
