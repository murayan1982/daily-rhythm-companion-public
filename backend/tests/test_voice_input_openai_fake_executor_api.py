from __future__ import annotations

from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import voice_input_demo
from app.config import AppConfig
from app.services.framework_voice_input_fake_handoff import (
    _FrameworkVoiceInputPublicApi,
)
from app.services.framework_voice_input_openai_fake_executor import (
    FrameworkVoiceInputOpenAIFakeExecutorAdapter,
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


def _config(root: Path | None, **overrides) -> AppConfig:
    values = {
        "conversation_engine": "framework",
        "framework_project_root": str(root) if root is not None else None,
        "voice_input_demo_enabled": True,
        "voice_input_adapter_mode": "framework",
        "voice_input_staging_max_bytes": 1024,
    }
    values.update(overrides)
    return AppConfig(**values)


def _api_context(*, unsafe: bool = False):
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
            def __init__(self, *, execution_config, model, client, public_metadata):
                self.execution_config = execution_config
                self.model = model
                self.client = client
                self.public_metadata = public_metadata

        class Policy:
            def __init__(self, *, max_audio_bytes, allow_fake_client_execution):
                self.max_audio_bytes = max_audio_bytes
                self.allow_fake_client_execution = allow_fake_client_execution

        class Executor:
            def __init__(self, *, adapter, policy):
                self.adapter = adapter
                self.policy = policy

            def execute(self, *, audio_source, request):
                audio_bytes = Path(audio_source.path).read_bytes()
                payload = BytesIO(audio_bytes)
                payload.name = "audio.wav"
                response = self.adapter.client.audio.transcriptions.create(
                    model=self.adapter.model,
                    file=payload,
                    language=request.language,
                )
                payload.close()
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
                        "real_provider_execution_executed": unsafe,
                        "audio_path_exposed": False,
                        "raw_audio_exposed": False,
                        "provider_payload_exposed": False,
                        "microphone_accessed": False,
                    },
                    is_completed=True,
                )

        def resolve_config(**kwargs):
            return SimpleNamespace(**kwargs)

        module = SimpleNamespace(
            resolve_voice_input_provider_execution_config=resolve_config,
            OpenAIVoiceInputProviderAdapter=Adapter,
            OpenAIVoiceInputFakeClientMarker=Marker,
            OpenAIVoiceInputFakeExecutionPolicy=Policy,
            OpenAIVoiceInputFakeExecutor=Executor,
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


def _client(
    monkeypatch,
    tmp_path: Path,
    config: AppConfig,
    *,
    unsafe: bool = False,
):
    store = VoiceInputStagingStore(root_dir=tmp_path / "private", config=config)
    monkeypatch.setattr(voice_input_demo, "load_config", lambda: config)
    monkeypatch.setattr(
        voice_input_demo,
        "_create_voice_input_staging_store",
        lambda _config: store,
    )
    monkeypatch.setattr(
        voice_input_demo,
        "_create_framework_voice_input_openai_fake_executor_adapter",
        lambda _config, _store: FrameworkVoiceInputOpenAIFakeExecutorAdapter(
            config,
            store,
            public_api_context_factory=_api_context(unsafe=unsafe),
        ),
    )
    app = FastAPI()
    app.include_router(voice_input_demo.router)
    return TestClient(app), store


def test_openai_fake_executor_route_is_path_free_and_single_use(
    monkeypatch,
    tmp_path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    client, store = _client(monkeypatch, tmp_path, config)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/openai-fake-executor",
            json={"language": "ja", "duration_ms": 4820},
        )
        reused = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/openai-fake-executor",
            json={"language": "ja", "duration_ms": 4820},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["request_state"] == "marked_fake_transcribed"
    assert payload["outcome"] == "completed"
    assert payload["adapter_name"] == "openai"
    assert payload["executor_name"] == "openai_marked_fake"
    assert payload["fake_provider_protocol_call_executed"] is True
    assert payload["audio_read"] is True
    assert payload["audio_bytes_read"] == staged.byte_count
    assert payload["provider_sdk_imported"] is False
    assert payload["provider_client_created"] is False
    assert payload["credential_values_read"] is False
    assert payload["real_provider_execution_executed"] is False
    assert payload["fake_stt_executed"] is True
    assert payload["real_stt_executed"] is False
    public_text = repr(payload).lower()
    assert staged.staging_id not in public_text
    assert str(tmp_path).lower() not in public_text
    assert ".wav" not in public_text
    assert store.artifact_count() == 0
    assert reused.status_code == 404
    assert reused.json()["detail"]["code"] == "artifact_not_found"


def test_openai_fake_executor_guard_failure_preserves_artifact(
    monkeypatch,
    tmp_path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root, voice_input_demo_enabled=False)
    client, store = _client(monkeypatch, tmp_path, config)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/openai-fake-executor",
            json={"duration_ms": 1000},
        )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "voice_input_staging_disabled"
    assert store.has_artifact(staged.staging_id) is True


def test_openai_fake_executor_framework_preflight_preserves_artifact(
    monkeypatch,
    tmp_path,
) -> None:
    config = _config(None)
    client, store = _client(monkeypatch, tmp_path, config)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/openai-fake-executor",
            json={"duration_ms": 1000},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "framework_root_not_configured",
        "message": "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured.",
        "retryable": True,
    }
    assert store.has_artifact(staged.staging_id) is True


def test_openai_fake_executor_unsafe_result_is_rejected_and_consumed(
    monkeypatch,
    tmp_path,
) -> None:
    root = _framework_root(tmp_path)
    config = _config(root)
    client, store = _client(monkeypatch, tmp_path, config, unsafe=True)
    staged = store.stage_chunks((_wav_bytes(),))

    with client:
        response = client.post(
            f"/demo/voice-input/staging/{staged.staging_id}/openai-fake-executor",
            json={"duration_ms": 1000},
        )

    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "unsafe_openai_fake_executor_result"
    assert response.json()["detail"]["retryable"] is False
    assert store.has_artifact(staged.staging_id) is False
