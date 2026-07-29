from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
)
from app.services.framework_voice_input_openai_real_operator import (
    FrameworkVoiceInputOpenAIRealOperatorAdapter,
    FrameworkVoiceInputOpenAIRealOperatorError,
    FrameworkVoiceInputOpenAIRealOperatorRequest,
)
from app.services.voice_input_staging_store import (
    VoiceInputStagingError,
    VoiceInputStagingStore,
)


def _wav_bytes(payload_size: int = 32) -> bytes:
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


def _config(root: Path) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=str(root),
        voice_input_demo_enabled=True,
        voice_input_adapter_mode="framework",
        voice_input_staging_max_bytes=1024,
    )


def _request(
    staging_id: str,
) -> FrameworkVoiceInputOpenAIRealOperatorRequest:
    return FrameworkVoiceInputOpenAIRealOperatorRequest(
        staging_id=staging_id,
        language="ja-JP",
        duration_ms=900,
        max_duration_ms=15000,
        model="gpt-4o-mini-transcribe",
        max_audio_bytes=1024,
        timeout_seconds=30.0,
        max_retries=0,
        operator_handoff_enabled=True,
        allow_provider_execution=True,
        credentials_available=True,
        allow_provider_sdk_import=True,
        allow_provider_client_creation=True,
        allow_real_provider_execution=True,
    )


class _State:
    def __init__(
        self,
        *,
        fail_execution: bool = False,
        unsafe_metadata: bool = False,
    ) -> None:
        self.fail_execution = fail_execution
        self.unsafe_metadata = unsafe_metadata
        self.context_entries = 0
        self.builder_calls = 0
        self.client_factory_calls = 0
        self.executor_calls = 0
        self.audio_bytes_seen = 0
        self.source_path: str | None = None


class _AudioFormat:
    @classmethod
    def wav(cls, **kwargs):
        return SimpleNamespace(**kwargs)


class _AudioSource:
    @classmethod
    def from_file_path(cls, path: str, **kwargs):
        return SimpleNamespace(path=path, **kwargs)


class _VoiceRequest:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


def _context_factory(state: _State):
    @contextmanager
    def context(_root: Path):
        state.context_entries += 1

        class Credential:
            def __init__(self, api_key: str) -> None:
                self.api_key = api_key

        class RuntimeMode:
            REAL = "real"

        class Policy:
            def __init__(self, **kwargs) -> None:
                self.__dict__.update(kwargs)

        class ClientFactory:
            def __init__(self, *, credential, policy) -> None:
                self.credential = credential
                self.policy = policy

            def __call__(self):
                state.client_factory_calls += 1
                return SimpleNamespace(kind="synthetic-client")

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
                self.client = None
                self.client_factory = client_factory
                self.public_metadata = public_metadata

        class Executor:
            def __init__(self, *, adapter) -> None:
                self.adapter = adapter

            def execute(self, *, audio_source, request=None):
                state.executor_calls += 1
                if state.fail_execution:
                    raise RuntimeError(
                        "synthetic provider body with private path and secret"
                    )

                self.adapter.client_factory()
                state.source_path = audio_source.path
                data = Path(audio_source.path).read_bytes()
                state.audio_bytes_seen = len(data)

                metadata = {
                    "audio_read": True,
                    "audio_bytes_read": len(data),
                    "provider_sdk_imported": True,
                    "provider_client_created": True,
                    "network_request_executed": True,
                    "provider_execution_executed": True,
                    "real_provider_execution_executed": True,
                    "private_path_exposed": False,
                    "raw_audio_exposed": False,
                    "provider_payload_exposed": state.unsafe_metadata,
                    "provider_response_exposed": False,
                    "provider_error_body_exposed": False,
                    "request_id_exposed": False,
                    "credential_exposed": False,
                    "private_credential_exposed": False,
                    "transcript_exposed": False,
                    "microphone_accessed": False,
                }
                return SimpleNamespace(
                    outcome=SimpleNamespace(value="completed"),
                    text="synthetic private transcript",
                    language="ja-JP",
                    confidence=None,
                    duration_ms=900,
                    public_error_code=SimpleNamespace(value="none"),
                    safe_message="",
                    retryable=False,
                    public_metadata=metadata,
                    is_completed=True,
                )

        def resolve_config(**kwargs):
            return SimpleNamespace(
                configured=(
                    kwargs["provider"] == "openai"
                    and kwargs["allow_provider_execution"] is True
                    and kwargs["credentials_available"] is True
                ),
                **kwargs,
            )

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
            VoiceInputAudioFormat=_AudioFormat,
            VoiceInputAudioSource=_AudioSource,
            VoiceInputRequest=_VoiceRequest,
            FakeVoiceInputProviderAdapter=object,
            create_voice_input_session=lambda **_kwargs: None,
            module=module,
        )

    return context


def _builder(state: _State):
    def build(credential_type):
        state.builder_calls += 1
        return credential_type("<synthetic-placeholder>")

    return build


def test_executes_real_operator_contract_inside_single_use_consume(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(
        root_dir=tmp_path / "private",
        config=config,
    )
    staged = store.stage_chunks((_wav_bytes(),))
    state = _State()
    adapter = FrameworkVoiceInputOpenAIRealOperatorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(state),
    )

    result = adapter.transcribe_staged_artifact(
        _request(staged.staging_id),
        private_credential_builder=_builder(state),
    )

    assert result.status == "completed"
    assert result.request_state == "private_real_stt_transcribed"
    assert result.outcome == "completed"
    assert result.real_transcription_completed is True
    assert result.staged_artifact_consumed is True
    assert result.audio_read is True
    assert result.audio_bytes_read == len(_wav_bytes())
    assert result.provider_sdk_imported is True
    assert result.provider_client_created is True
    assert result.network_request_executed is True
    assert result.real_provider_execution_executed is True
    assert result.microphone_accessed is False
    assert result.private_path_exposed is False
    assert result.raw_audio_exposed is False
    assert result.provider_payload_exposed is False
    assert result.transcript_exposed is False
    assert result.credential_value_read_by_drc is False
    assert result.private_transcript == "synthetic private transcript"
    assert state.context_entries == 1
    assert state.builder_calls == 1
    assert state.client_factory_calls == 1
    assert state.executor_calls == 1
    assert state.audio_bytes_seen == len(_wav_bytes())
    assert not store.has_artifact(staged.staging_id)

    public_repr = repr(result)
    assert "synthetic private transcript" not in public_repr
    assert staged.staging_id not in public_repr
    assert str(tmp_path) not in public_repr


def test_incomplete_opt_in_fails_before_context_builder_and_consume(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(
        root_dir=tmp_path / "private",
        config=config,
    )
    staged = store.stage_chunks((_wav_bytes(),))
    state = _State()
    adapter = FrameworkVoiceInputOpenAIRealOperatorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(state),
    )
    request = FrameworkVoiceInputOpenAIRealOperatorRequest(
        staging_id=staged.staging_id,
        operator_handoff_enabled=True,
        allow_provider_execution=True,
        credentials_available=True,
        allow_provider_sdk_import=True,
        allow_provider_client_creation=True,
        allow_real_provider_execution=False,
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealOperatorError,
        match="every explicit operator gate",
    ) as captured:
        adapter.transcribe_staged_artifact(
            request,
            private_credential_builder=_builder(state),
        )

    assert captured.value.code == "real_operator_opt_in_incomplete"
    assert state.context_entries == 0
    assert state.builder_calls == 0
    assert state.client_factory_calls == 0
    assert state.executor_calls == 0
    assert store.has_artifact(staged.staging_id)


def test_execution_failure_is_safe_and_consumes_artifact_once(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(
        root_dir=tmp_path / "private",
        config=config,
    )
    staged = store.stage_chunks((_wav_bytes(),))
    state = _State(fail_execution=True)
    adapter = FrameworkVoiceInputOpenAIRealOperatorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(state),
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealOperatorError,
        match="failed safely",
    ) as captured:
        adapter.transcribe_staged_artifact(
            _request(staged.staging_id),
            private_credential_builder=_builder(state),
        )

    assert captured.value.code == "framework_real_operator_execution_failed"
    assert "synthetic provider body" not in str(captured.value)
    assert str(tmp_path) not in str(captured.value)
    assert state.builder_calls == 1
    assert state.executor_calls == 1
    assert not store.has_artifact(staged.staging_id)


def test_unsafe_public_metadata_is_rejected_and_artifact_is_removed(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(
        root_dir=tmp_path / "private",
        config=config,
    )
    staged = store.stage_chunks((_wav_bytes(),))
    state = _State(unsafe_metadata=True)
    adapter = FrameworkVoiceInputOpenAIRealOperatorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(state),
    )

    with pytest.raises(
        FrameworkVoiceInputOpenAIRealOperatorError,
        match="unsafe public exposure",
    ) as captured:
        adapter.transcribe_staged_artifact(
            _request(staged.staging_id),
            private_credential_builder=_builder(state),
        )

    assert captured.value.code == "unsafe_real_operator_result"
    assert not store.has_artifact(staged.staging_id)


def test_successful_artifact_cannot_be_reused(
    tmp_path: Path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    store = VoiceInputStagingStore(
        root_dir=tmp_path / "private",
        config=config,
    )
    staged = store.stage_chunks((_wav_bytes(),))
    state = _State()
    adapter = FrameworkVoiceInputOpenAIRealOperatorAdapter(
        config,
        store,
        public_api_context_factory=_context_factory(state),
    )

    adapter.transcribe_staged_artifact(
        _request(staged.staging_id),
        private_credential_builder=_builder(state),
    )

    with pytest.raises(VoiceInputStagingError) as captured:
        adapter.transcribe_staged_artifact(
            _request(staged.staging_id),
            private_credential_builder=_builder(state),
        )

    assert captured.value.code == "artifact_not_found"
    assert state.executor_calls == 1
