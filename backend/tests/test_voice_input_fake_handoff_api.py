from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import voice_input_demo
from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    FrameworkVoiceInputFakeHandoffAdapter,
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


def _config(root: Path | None, **overrides) -> AppConfig:
    values = {
        "conversation_engine": "framework",
        "framework_project_root": str(root) if root is not None else None,
        "voice_input_demo_enabled": True,
        "voice_input_adapter_mode": "framework",
    }
    values.update(overrides)
    return AppConfig(**values)


def _api_context(*, fail: bool = False):
    @contextmanager
    def context(_root: Path):
        class AudioFormat:
            @classmethod
            def wav(cls, **kwargs):
                return SimpleNamespace(**kwargs)

        class AudioSource:
            @classmethod
            def from_file_path(cls, path: str, **kwargs):
                return SimpleNamespace(path=path, source_kind=SimpleNamespace(value="file_path"), **kwargs)

        class VoiceRequest:
            def __init__(self, **kwargs) -> None:
                self.__dict__.update(kwargs)

        class FakeAdapter:
            def __init__(self, *, transcript, language, public_metadata) -> None:
                self.transcript = transcript
                self.language = language

        def create_voice_input_session(**_kwargs):
            class Session:
                is_closed = False

                def transcribe_audio_result(self, source, *, request, adapter):
                    assert Path(source.path).is_file()
                    if fail:
                        raise RuntimeError("synthetic failure")
                    return SimpleNamespace(
                        outcome=SimpleNamespace(value="completed"),
                        text=adapter.transcript,
                        language=adapter.language,
                        duration_ms=source.audio_format.duration_ms,
                        public_error_code=SimpleNamespace(value="none"),
                        safe_message="",
                        retryable=False,
                        public_metadata={
                            "adapter": "fake",
                            "source_kind": "file_path",
                            "audio_read": False,
                            "microphone_accessed": False,
                            "provider_execution_executed": False,
                        },
                        is_completed=True,
                    )

                def close(self):
                    self.is_closed = True

            return Session()

        yield _FrameworkVoiceInputPublicApi(
            VoiceInputAudioFormat=AudioFormat,
            VoiceInputAudioSource=AudioSource,
            VoiceInputRequest=VoiceRequest,
            FakeVoiceInputProviderAdapter=FakeAdapter,
            create_voice_input_session=create_voice_input_session,
        )

    return context


def _client(monkeypatch, tmp_path: Path, config: AppConfig, *, fail: bool = False):
    store = VoiceInputStagingStore(root_dir=tmp_path / "private", config=config)
    monkeypatch.setattr(voice_input_demo, "load_config", lambda: config)
    monkeypatch.setattr(
        voice_input_demo,
        "_create_voice_input_staging_store",
        lambda _config: store,
    )
    monkeypatch.setattr(
        voice_input_demo,
        "_create_framework_voice_input_fake_handoff_adapter",
        lambda _config, _store: FrameworkVoiceInputFakeHandoffAdapter(
            config,
            store,
            public_api_context_factory=_api_context(fail=fail),
        ),
    )
    app = FastAPI()
    app.include_router(voice_input_demo.router)
    return TestClient(app), store


def test_fake_handoff_returns_path_free_result_and_consumes_once(monkeypatch, tmp_path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    client, store = _client(monkeypatch, tmp_path, config)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/fake-handoff",
            json={"language": "ja-JP", "duration_ms": 4820},
        )
        reused = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/fake-handoff",
            json={"language": "ja-JP", "duration_ms": 4820},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["request_state"] == "fake_transcribed"
    assert payload["outcome"] == "completed"
    assert payload["adapter_name"] == "fake"
    assert payload["fake_transcription_completed"] is True
    assert payload["staged_artifact_consumed"] is True
    assert payload["session_closed"] is True
    assert payload["audio_read"] is False
    assert payload["provider_execution_executed"] is False
    assert payload["stt_executed"] is False
    public_text = repr(payload).lower()
    assert staged.staging_id not in public_text
    assert str(tmp_path).lower() not in public_text
    assert ".wav" not in public_text
    assert store.artifact_count() == 0
    assert reused.status_code == 404
    assert reused.json()["detail"]["code"] == "artifact_not_found"


def test_fake_handoff_guard_failure_preserves_staged_artifact(monkeypatch, tmp_path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root, voice_input_demo_enabled=False)
    client, store = _client(monkeypatch, tmp_path, config)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/fake-handoff",
            json={"duration_ms": 1000},
        )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "voice_input_staging_disabled"
    assert store.has_artifact(staged.staging_id) is True


def test_fake_handoff_framework_preflight_failure_preserves_artifact(monkeypatch, tmp_path) -> None:
    config = _config(None)
    client, store = _client(monkeypatch, tmp_path, config)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/fake-handoff",
            json={"duration_ms": 1000},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "framework_root_not_configured",
        "message": "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
        "retryable": True,
    }
    assert store.has_artifact(staged.staging_id) is True


def test_fake_handoff_callback_failure_is_safe_and_single_use(monkeypatch, tmp_path) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    client, store = _client(monkeypatch, tmp_path, config, fail=True)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/fake-handoff",
            json={"duration_ms": 1000},
        )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "framework_fake_session_failed"
    assert response.json()["detail"]["retryable"] is True
    assert store.has_artifact(staged.staging_id) is False
