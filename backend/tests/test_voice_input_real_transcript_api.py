from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import voice_input_demo
from app.config import AppConfig
from app.services.framework_voice_input_app_transcript import (
    FrameworkVoiceInputAppTranscriptError,
    FrameworkVoiceInputAppTranscriptResult,
)
from app.services.voice_input_staging_store import VoiceInputStagingStore


@dataclass
class _RecordingAdapter:
    result: FrameworkVoiceInputAppTranscriptResult | None = None
    error: Exception | None = None
    request = None
    calls: int = 0

    def transcribe_staged_artifact(self, request):
        self.calls += 1
        self.request = request
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def _config(**overrides) -> AppConfig:
    values = {
        "conversation_engine": "framework",
        "voice_input_demo_enabled": True,
        "voice_input_adapter_mode": "framework",
        "voice_input_real_stt_enabled": True,
    }
    values.update(overrides)
    return AppConfig(**values)


def _client(monkeypatch, tmp_path: Path, adapter: _RecordingAdapter):
    config = _config()
    store = VoiceInputStagingStore(root_dir=tmp_path / "private", config=config)
    monkeypatch.setattr(voice_input_demo, "load_config", lambda: config)
    monkeypatch.setattr(
        voice_input_demo,
        "_create_voice_input_staging_store",
        lambda _config: store,
    )
    monkeypatch.setattr(
        voice_input_demo,
        "_create_private_voice_input_credential_source",
        lambda: object(),
    )
    monkeypatch.setattr(
        voice_input_demo,
        "_create_framework_voice_input_app_transcript_adapter",
        lambda _config, _store, _credential_source: adapter,
    )
    app = FastAPI()
    app.include_router(voice_input_demo.router)
    return TestClient(app)


def _payload(**overrides):
    values = {
        "staging_id": "0123456789abcdef0123456789abcdef",
        "foreground_opt_in": True,
        "language": "ja",
        "duration_ms": 1000,
    }
    values.update(overrides)
    return values


def test_real_transcript_route_is_body_only_minimal_and_no_store(
    monkeypatch,
    tmp_path,
):
    transcript = "synthetic transcript not for logs"
    adapter = _RecordingAdapter(
        result=FrameworkVoiceInputAppTranscriptResult(
            result_id="abcdef0123456789abcdef0123456789",
            text=transcript,
            is_final=True,
        )
    )
    client = _client(monkeypatch, tmp_path, adapter)

    with client:
        response = client.post("/demo/voice-input/transcript", json=_payload())

    assert response.status_code == 200
    assert response.request.url.path == "/demo/voice-input/transcript"
    assert _payload()["staging_id"] not in response.request.url.path
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.json() == {
        "accepted": True,
        "request_state": "final_transcript_ready",
        "result_id": "abcdef0123456789abcdef0123456789",
        "text": transcript,
        "is_final": True,
    }
    assert set(response.json()) == {
        "accepted",
        "request_state",
        "result_id",
        "text",
        "is_final",
    }
    assert adapter.calls == 1
    assert adapter.request.staging_id == _payload()["staging_id"]
    assert adapter.request.foreground_opt_in is True


def test_request_validation_rejects_invalid_id_and_duration_without_adapter(
    monkeypatch,
    tmp_path,
):
    adapter = _RecordingAdapter(
        result=FrameworkVoiceInputAppTranscriptResult(
            result_id="abcdef0123456789abcdef0123456789",
            text="unused",
        )
    )
    client = _client(monkeypatch, tmp_path, adapter)

    with client:
        invalid_id = client.post(
            "/demo/voice-input/transcript",
            json=_payload(staging_id="../private.wav"),
        )
        invalid_type = client.post(
            "/demo/voice-input/transcript",
            json=_payload(staging_id={"private": "must-not-echo"}),
        )
        invalid_duration = client.post(
            "/demo/voice-input/transcript",
            json=_payload(duration_ms=15001),
        )

    assert invalid_id.status_code == 400
    assert invalid_type.status_code == 400
    assert invalid_duration.status_code == 422
    assert adapter.calls == 0
    assert "../private.wav" not in repr(invalid_id.json())
    assert "must-not-echo" not in repr(invalid_type.json())


def test_route_redacts_internal_provider_failure(monkeypatch, tmp_path):
    private_detail = "provider body /private/path credential-value transcript-text"
    adapter = _RecordingAdapter(
        error=FrameworkVoiceInputAppTranscriptError(
            "framework_app_transcript_execution_failed",
            private_detail,
            retryable=True,
        )
    )
    client = _client(monkeypatch, tmp_path, adapter)

    with client:
        response = client.post("/demo/voice-input/transcript", json=_payload())

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "code": "voice_input_transcript_unavailable",
            "message": "音声の文字起こしを利用できません。",
            "retryable": True,
        }
    }
    public_text = repr(response.json())
    assert private_detail not in public_text
    assert _payload()["staging_id"] not in public_text


def test_foreground_and_busy_errors_use_fixed_public_codes(monkeypatch, tmp_path):
    opt_in_adapter = _RecordingAdapter(
        error=FrameworkVoiceInputAppTranscriptError(
            "foreground_opt_in_required",
            "internal",
        )
    )
    opt_in_client = _client(monkeypatch, tmp_path / "opt", opt_in_adapter)
    with opt_in_client:
        opt_in = opt_in_client.post(
            "/demo/voice-input/transcript",
            json=_payload(foreground_opt_in=False),
        )
    assert opt_in.status_code == 403
    assert opt_in.json()["detail"]["code"] == (
        "voice_input_transcript_opt_in_required"
    )

    busy_adapter = _RecordingAdapter(
        error=FrameworkVoiceInputAppTranscriptError(
            "app_transcript_busy",
            "internal",
            retryable=True,
        )
    )
    busy_client = _client(monkeypatch, tmp_path / "busy", busy_adapter)
    with busy_client:
        busy = busy_client.post("/demo/voice-input/transcript", json=_payload())
    assert busy.status_code == 409
    assert busy.json()["detail"]["code"] == "voice_input_transcript_busy"
    assert busy.json()["detail"]["retryable"] is True
