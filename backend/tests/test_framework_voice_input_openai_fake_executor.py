from __future__ import annotations

from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
)
from app.services.framework_voice_input_openai_fake_executor import (
    FrameworkVoiceInputOpenAIFakeExecutorAdapter,
    FrameworkVoiceInputOpenAIFakeExecutorError,
    FrameworkVoiceInputOpenAIFakeExecutorRequest,
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
    (package / "__init__.py").write_text(
        "# synthetic public package\n",
        encoding="utf-8",
    )
    return root


def _config(root: Path | None) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=str(root) if root is not None else None,
        voice_input_demo_enabled=True,
        voice_input_adapter_mode="framework",
        voice_input_staging_max_bytes=1024,
    )


class _State:
    def __init__(self, *, fail: bool = False, unsafe: bool = False) -> None:
        self.fail = fail
        self.unsafe = unsafe
        self.source_path: str | None = None
        self.fake_call_count = 0
        self.audio_bytes_read = 0
        self.marked_client = False
        self.model = ""


def _context_factory(state: _State, *, contract_missing: bool = False):
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
                    ref=SimpleNamespace(
                        value=path,
                        audio_format=kwargs["audio_format"],
                    ),
                    source_kind=SimpleNamespace(value="file_path"),
                    **kwargs,
                )

        class VoiceRequest:
            def __init__(self, **kwargs) -> None:
                self.__dict__.update(kwargs)

        class Marker:
            ai_character_framework_fake_stt_client = True

        class Adapter:
            def __init__(
                self,
                *,
                execution_config,
                model,
                client,
                public_metadata,
            ) -> None:
                self.execution_config = execution_config
                self.model = model
                self.client = client
                self.public_metadata = public_metadata

        class Policy:
            def __init__(
                self,
                *,
                max_audio_bytes,
                allow_fake_client_execution,
            ) -> None:
                self.max_audio_bytes = max_audio_bytes
                self.allow_fake_client_execution = allow_fake_client_execution

        class Executor:
            def __init__(self, *, adapter, policy) -> None:
                self.adapter = adapter
                self.policy = policy

            def execute(self, *, audio_source, request):
                state.source_path = audio_source.path
                assert Path(audio_source.path).is_file()
                state.marked_client = isinstance(self.adapter.client, Marker)
                state.model = self.adapter.model
                if state.fail:
                    raise RuntimeError("synthetic executor failure")
                audio_bytes = Path(audio_source.path).read_bytes()
                assert len(audio_bytes) <= self.policy.max_audio_bytes
                payload = BytesIO(audio_bytes)
                payload.name = "audio.wav"
                response = self.adapter.client.audio.transcriptions.create(
                    model=self.adapter.model,
                    file=payload,
                    language=request.language,
                )
                payload.close()
                state.fake_call_count += 1
                state.audio_bytes_read = len(audio_bytes)
                return SimpleNamespace(
                    outcome=SimpleNamespace(value="completed"),
                    text=response["text"],
                    language=response["language"],
                    duration_ms=audio_source.audio_format.duration_ms,
                    public_error_code=SimpleNamespace(value="none"),
                    safe_message="",
                    retryable=False,
                    public_metadata={
                        "fake_execution_status": "completed",
                        "fake_provider_protocol_call_executed": True,
                        "audio_bytes_read": len(audio_bytes),
                        "provider_sdk_imported": False,
                        "provider_client_created": False,
                        "credential_values_read": False,
                        "real_provider_execution_executed": state.unsafe,
                        "audio_path_exposed": False,
                        "raw_audio_exposed": False,
                        "provider_payload_exposed": False,
                        "microphone_accessed": False,
                    },
                    is_completed=True,
                )

        def resolve_config(**kwargs):
            return SimpleNamespace(**kwargs)

        module = (
            SimpleNamespace()
            if contract_missing
            else SimpleNamespace(
                resolve_voice_input_provider_execution_config=resolve_config,
                OpenAIVoiceInputProviderAdapter=Adapter,
                OpenAIVoiceInputFakeClientMarker=Marker,
                OpenAIVoiceInputFakeExecutionPolicy=Policy,
                OpenAIVoiceInputFakeExecutor=Executor,
            )
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


def test_marked_fake_executor_reads_bounded_audio_and_consumes_once(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(tmp_path / "staging", config=config)
    staged = store.stage_chunks((_wav_bytes(),))
    state = _State()
    adapter = FrameworkVoiceInputOpenAIFakeExecutorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(state),
    )

    result = adapter.transcribe_staged_artifact(
        FrameworkVoiceInputOpenAIFakeExecutorRequest(
            staging_id=staged.staging_id,
            language="ja",
            duration_ms=4820,
        )
    )

    assert result.status == "completed"
    assert result.request_state == "marked_fake_transcribed"
    assert result.transcript == "DRC bounded marked-fake STT transcript"
    assert result.adapter_name == "openai"
    assert result.executor_name == "openai_marked_fake"
    assert result.fake_provider_protocol_call_executed is True
    assert result.audio_read is True
    assert result.audio_bytes_read == staged.byte_count
    assert result.fake_stt_executed is True
    assert result.real_stt_executed is False
    assert result.real_provider_execution_executed is False
    assert result.provider_sdk_imported is False
    assert result.provider_client_created is False
    assert result.credential_values_read is False
    assert state.marked_client is True
    assert state.fake_call_count == 1
    assert state.model == "drc-v300-marked-fake-transcribe"
    assert state.source_path is not None
    assert not Path(state.source_path).exists()
    assert store.artifact_count() == 0
    assert "path" not in result.__dict__
    assert "staging_id" not in result.__dict__
    assert str(tmp_path) not in repr(result)

    with pytest.raises(FrameworkVoiceInputOpenAIFakeExecutorError) as reused:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputOpenAIFakeExecutorRequest(
                staging_id=staged.staging_id,
            )
        )
    assert reused.value.code == "artifact_not_found"


def test_missing_public_executor_contract_preserves_artifact(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(tmp_path / "staging", config=config)
    staged = store.stage_chunks((_wav_bytes(),))
    adapter = FrameworkVoiceInputOpenAIFakeExecutorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(
            _State(),
            contract_missing=True,
        ),
    )

    with pytest.raises(FrameworkVoiceInputOpenAIFakeExecutorError) as error:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputOpenAIFakeExecutorRequest(
                staging_id=staged.staging_id,
            )
        )

    assert error.value.code == "public_openai_fake_executor_contract_missing"
    assert error.value.retryable is True
    assert store.has_artifact(staged.staging_id) is True


def test_executor_failure_discards_artifact_and_is_safe(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(tmp_path / "staging", config=config)
    staged = store.stage_chunks((_wav_bytes(),))
    adapter = FrameworkVoiceInputOpenAIFakeExecutorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(_State(fail=True)),
    )

    with pytest.raises(FrameworkVoiceInputOpenAIFakeExecutorError) as error:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputOpenAIFakeExecutorRequest(
                staging_id=staged.staging_id,
            )
        )

    assert error.value.code == "framework_openai_fake_executor_failed"
    assert error.value.retryable is True
    assert store.has_artifact(staged.staging_id) is False
    assert str(tmp_path) not in str(error.value)


def test_unsafe_executor_metadata_is_rejected_and_consumed(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(tmp_path / "staging", config=config)
    staged = store.stage_chunks((_wav_bytes(),))
    adapter = FrameworkVoiceInputOpenAIFakeExecutorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(_State(unsafe=True)),
    )

    with pytest.raises(FrameworkVoiceInputOpenAIFakeExecutorError) as error:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputOpenAIFakeExecutorRequest(
                staging_id=staged.staging_id,
            )
        )

    assert error.value.code == "unsafe_openai_fake_executor_result"
    assert error.value.retryable is False
    assert store.has_artifact(staged.staging_id) is False
