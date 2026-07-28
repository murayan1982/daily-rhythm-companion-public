from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    FrameworkVoiceInputFakeHandoffAdapter,
    FrameworkVoiceInputFakeHandoffError,
    FrameworkVoiceInputFakeHandoffRequest,
    _FrameworkVoiceInputPublicApi,
)
from app.services.voice_input_staging_store import VoiceInputStagingStore


def _wav_bytes(payload_size: int = 24) -> bytes:
    return b"RIFF" + (payload_size + 4).to_bytes(4, "little") + b"WAVE" + (b"\x00" * payload_size)


def _framework_root(tmp_path: Path) -> Path:
    root = tmp_path / "fw"
    package = root / "framework"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("# synthetic public package\n", encoding="utf-8")
    return root


def _config(root: Path | None) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=str(root) if root is not None else None,
        voice_input_demo_enabled=True,
        voice_input_adapter_mode="framework",
    )


class FakePublicApiState:
    def __init__(self, *, fail_transcribe: bool = False, unsafe_result: bool = False) -> None:
        self.fail_transcribe = fail_transcribe
        self.unsafe_result = unsafe_result
        self.source_path: str | None = None
        self.session_created = False
        self.session_closed = False
        self.provider_execution_allowed: bool | None = None
        self.real_stt_enabled: bool | None = None


class _AudioFormat:
    @classmethod
    def wav(cls, **kwargs):
        return SimpleNamespace(**kwargs)


class _AudioSource:
    @classmethod
    def from_file_path(cls, path: str, **kwargs):
        return SimpleNamespace(path=path, source_kind=SimpleNamespace(value="file_path"), **kwargs)


class _VoiceRequest:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)


class _FakeAdapter:
    def __init__(self, *, transcript: str, language: str | None, public_metadata) -> None:
        self.transcript = transcript
        self.language = language
        self.public_metadata = public_metadata


def _context_factory(state: FakePublicApiState):
    @contextmanager
    def context(_root: Path):
        def create_voice_input_session(**kwargs):
            state.session_created = True
            state.provider_execution_allowed = kwargs.get("allow_provider_execution")
            state.real_stt_enabled = kwargs.get("real_stt_enabled")

            class Session:
                is_closed = False

                def transcribe_audio_result(self, source, *, request, adapter):
                    state.source_path = source.path
                    assert Path(source.path).is_file()
                    if state.fail_transcribe:
                        raise RuntimeError("synthetic fake-session failure")
                    metadata = {
                        "adapter": "fake",
                        "source_kind": "file_path",
                        "audio_read": state.unsafe_result,
                        "microphone_accessed": False,
                        "provider_execution_executed": False,
                        "audio_id": "not-returned-to-drc",
                    }
                    return SimpleNamespace(
                        outcome=SimpleNamespace(value="completed"),
                        text=adapter.transcript,
                        language=adapter.language,
                        duration_ms=source.audio_format.duration_ms,
                        public_error_code=SimpleNamespace(value="none"),
                        safe_message="",
                        retryable=False,
                        public_metadata=metadata,
                        is_completed=True,
                    )

                def close(self):
                    self.is_closed = True
                    state.session_closed = True

            return Session()

        yield _FrameworkVoiceInputPublicApi(
            VoiceInputAudioFormat=_AudioFormat,
            VoiceInputAudioSource=_AudioSource,
            VoiceInputRequest=_VoiceRequest,
            FakeVoiceInputProviderAdapter=_FakeAdapter,
            create_voice_input_session=create_voice_input_session,
        )

    return context


def test_fake_public_session_handoff_is_path_free_and_single_use(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    store = VoiceInputStagingStore(tmp_path / "staging")
    staged = store.stage_chunks((_wav_bytes(),))
    state = FakePublicApiState()
    adapter = FrameworkVoiceInputFakeHandoffAdapter(
        _config(root),
        store,
        public_api_context_factory=_context_factory(state),
    )

    result = adapter.transcribe_staged_artifact(
        FrameworkVoiceInputFakeHandoffRequest(
            staging_id=staged.staging_id,
            language="ja-JP",
            duration_ms=4820,
        )
    )

    assert result.status == "completed"
    assert result.request_state == "fake_transcribed"
    assert result.transcript == "DRC fake STT public-session transcript"
    assert result.fake_transcription_completed is True
    assert result.staged_artifact_consumed is True
    assert result.session_closed is True
    assert result.audio_read is False
    assert result.microphone_accessed is False
    assert result.provider_execution_executed is False
    assert result.stt_executed is False
    assert "path" not in result.__dict__
    assert "staging_id" not in result.__dict__
    assert str(tmp_path) not in repr(result)
    assert state.session_created is True
    assert state.session_closed is True
    assert state.provider_execution_allowed is False
    assert state.real_stt_enabled is False
    assert state.source_path is not None
    assert not Path(state.source_path).exists()
    assert store.artifact_count() == 0

    with pytest.raises(FrameworkVoiceInputFakeHandoffError) as reused:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputFakeHandoffRequest(staging_id=staged.staging_id)
        )
    assert reused.value.code == "artifact_not_found"


def test_fake_session_failure_closes_session_and_discards_artifact(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    store = VoiceInputStagingStore(tmp_path / "staging")
    staged = store.stage_chunks((_wav_bytes(),))
    state = FakePublicApiState(fail_transcribe=True)
    adapter = FrameworkVoiceInputFakeHandoffAdapter(
        _config(root),
        store,
        public_api_context_factory=_context_factory(state),
    )

    with pytest.raises(FrameworkVoiceInputFakeHandoffError) as error:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputFakeHandoffRequest(staging_id=staged.staging_id)
        )

    assert error.value.code == "framework_fake_session_failed"
    assert error.value.retryable is True
    assert state.session_closed is True
    assert store.has_artifact(staged.staging_id) is False


def test_preflight_failure_preserves_artifact_for_retry(tmp_path: Path) -> None:
    store = VoiceInputStagingStore(tmp_path / "staging")
    staged = store.stage_chunks((_wav_bytes(),))
    adapter = FrameworkVoiceInputFakeHandoffAdapter(_config(None), store)

    with pytest.raises(FrameworkVoiceInputFakeHandoffError) as error:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputFakeHandoffRequest(staging_id=staged.staging_id)
        )

    assert error.value.code == "framework_root_not_configured"
    assert store.has_artifact(staged.staging_id) is True


def test_unsafe_fake_result_is_rejected_and_artifact_is_discarded(tmp_path: Path) -> None:
    root = _framework_root(tmp_path)
    store = VoiceInputStagingStore(tmp_path / "staging")
    staged = store.stage_chunks((_wav_bytes(),))
    state = FakePublicApiState(unsafe_result=True)
    adapter = FrameworkVoiceInputFakeHandoffAdapter(
        _config(root),
        store,
        public_api_context_factory=_context_factory(state),
    )

    with pytest.raises(FrameworkVoiceInputFakeHandoffError) as error:
        adapter.transcribe_staged_artifact(
            FrameworkVoiceInputFakeHandoffRequest(staging_id=staged.staging_id)
        )

    assert error.value.code == "unsafe_fake_handoff_result"
    assert state.session_closed is True
    assert store.has_artifact(staged.staging_id) is False
