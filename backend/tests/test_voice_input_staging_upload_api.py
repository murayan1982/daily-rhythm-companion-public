from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import voice_input_demo
from app.config import AppConfig
from app.services.voice_input_staging_store import VoiceInputStagingStore


def _wav_bytes(payload_size: int = 24) -> bytes:
    return b"RIFF" + (payload_size + 4).to_bytes(4, "little") + b"WAVE" + (b"\x00" * payload_size)


def _enabled_config(**overrides) -> AppConfig:
    values = {
        "conversation_engine": "framework",
        "voice_input_demo_enabled": True,
        "voice_input_adapter_mode": "framework",
        "voice_input_staging_ttl_seconds": 300,
        "voice_input_staging_max_count": 8,
        "voice_input_staging_max_bytes": 1048576,
    }
    values.update(overrides)
    return AppConfig(**values)


def _client(monkeypatch, tmp_path: Path, config: AppConfig) -> tuple[TestClient, VoiceInputStagingStore]:
    store = VoiceInputStagingStore(root_dir=tmp_path, config=config)
    monkeypatch.setattr(voice_input_demo, "load_config", lambda: config)
    monkeypatch.setattr(
        voice_input_demo,
        "_create_voice_input_staging_store",
        lambda _config: store,
    )
    app = FastAPI()
    app.include_router(voice_input_demo.router)
    return TestClient(app), store


def _headers(**overrides: str) -> dict[str, str]:
    values = {
        "Content-Type": "audio/wav",
        "X-DRC-Audio-Format": "wav",
        "X-DRC-Sample-Rate-Hz": "16000",
        "X-DRC-Channel-Count": "1",
        "X-DRC-Duration-Ms": "4820",
    }
    values.update(overrides)
    return values


def test_staging_upload_streams_wav_and_returns_path_free_metadata(monkeypatch, tmp_path) -> None:
    config = _enabled_config()
    client, store = _client(monkeypatch, tmp_path, config)
    body = _wav_bytes()

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=body,
            headers=_headers(),
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload == {
        "accepted": True,
        "request_state": "staged",
        "staging_id": payload["staging_id"],
        "audio_format": "wav",
        "media_type": "audio/wav",
        "byte_count": len(body),
        "sample_rate_hz": 16000,
        "channel_count": 1,
        "duration_ms": 4820,
        "expires_in_seconds": 300,
    }
    assert len(payload["staging_id"]) == 32
    assert store.has_artifact(payload["staging_id"]) is True
    public_text = str(payload).lower()
    assert str(tmp_path).lower() not in public_text
    assert ".wav" not in public_text
    assert "riff" not in public_text


def test_staging_upload_is_guarded_by_explicit_voice_input_enablement(monkeypatch, tmp_path) -> None:
    config = _enabled_config(voice_input_demo_enabled=False)
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(),
        )

    assert response.status_code == 403
    assert response.json()["detail"] == {
        "code": "voice_input_staging_disabled",
        "message": "Voice-input staging is disabled.",
        "retryable": False,
    }
    assert store.artifact_count() == 0


def test_staging_upload_requires_framework_engine(monkeypatch, tmp_path) -> None:
    config = _enabled_config(conversation_engine="mock")
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(),
        )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "voice_input_engine_not_framework"
    assert store.artifact_count() == 0


def test_staging_upload_requires_framework_adapter_mode(monkeypatch, tmp_path) -> None:
    config = _enabled_config(voice_input_adapter_mode="disabled")
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(),
        )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "voice_input_adapter_not_framework"
    assert store.artifact_count() == 0


def test_staging_upload_rejects_non_wav_media_type(monkeypatch, tmp_path) -> None:
    config = _enabled_config()
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(**{"Content-Type": "application/octet-stream"}),
        )

    assert response.status_code == 415
    assert response.json()["detail"]["code"] == "unsupported_media_type"
    assert store.artifact_count() == 0


def test_staging_upload_rejects_missing_safe_audio_metadata(monkeypatch, tmp_path) -> None:
    config = _enabled_config()
    client, store = _client(monkeypatch, tmp_path, config)
    headers = _headers()
    del headers["X-DRC-Duration-Ms"]

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=headers,
        )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "missing_audio_metadata"
    assert store.artifact_count() == 0


def test_staging_upload_rejects_wrong_sample_rate_and_channel_count(monkeypatch, tmp_path) -> None:
    config = _enabled_config()
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        sample_rate = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(**{"X-DRC-Sample-Rate-Hz": "48000"}),
        )
        channels = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(**{"X-DRC-Channel-Count": "2"}),
        )

    assert sample_rate.status_code == 400
    assert sample_rate.json()["detail"]["code"] == "unsupported_sample_rate"
    assert channels.status_code == 400
    assert channels.json()["detail"]["code"] == "unsupported_channel_count"
    assert store.artifact_count() == 0


def test_staging_upload_rejects_duration_over_fifteen_seconds(monkeypatch, tmp_path) -> None:
    config = _enabled_config()
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(),
            headers=_headers(**{"X-DRC-Duration-Ms": "15001"}),
        )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "capture_duration_exceeded"
    assert store.artifact_count() == 0


def test_staging_upload_rejects_declared_or_streamed_body_over_limit(monkeypatch, tmp_path) -> None:
    config = _enabled_config(voice_input_staging_max_bytes=32)
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=_wav_bytes(payload_size=64),
            headers=_headers(),
        )

    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "artifact_too_large"
    assert store.artifact_count() == 0
    staging_dir = tmp_path / "staging"
    assert not staging_dir.exists() or list(staging_dir.iterdir()) == []


def test_staging_upload_rejects_invalid_wav_without_leaving_partial(monkeypatch, tmp_path) -> None:
    config = _enabled_config()
    client, store = _client(monkeypatch, tmp_path, config)

    with client:
        response = client.post(
            "/demo/voice-input/staging",
            content=b"not-a-wave-file",
            headers=_headers(),
        )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_wav_header"
    assert store.artifact_count() == 0
    staging_dir = tmp_path / "staging"
    assert not staging_dir.exists() or list(staging_dir.iterdir()) == []
