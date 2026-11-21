from __future__ import annotations

from pathlib import Path
import re
import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from app.api import voice_output_demo as voice_api
from app.main import app
from app.services import voice_output_demo_service as voice_service
from app.services.framework_voice_output_adapter import FrameworkVoiceOutputResult
from app.services.voice_output_artifact_store import VoiceOutputArtifactStore


_ROUTE = "/demo/voice-output"
_FIXTURE = {
    "output_mode": "tts",
    "text_content": "ひと息ついてから、できることを一つ選びましょう。",
    "character_id": "gentle_mina",
    "voice_profile_id": "gentle_mina",
    "audio_format": "mp3",
}
_MP3 = b"ID3\x04\x00\x00offline audio fixture"
_KEY = "offline-key-fixture"
_VOICE = "offline-voice-fixture"


@pytest.fixture
def local_voice(monkeypatch, tmp_path):
    for name, value in {
        "VOICE_OUTPUT_ADAPTER_MODE": "elevenlabs_mina",
        "VOICE_OUTPUT_DEMO_ENABLED": "1",
        "VOICE_OUTPUT_REAL_TTS_ENABLED": "1",
        "ELEVENLABS_API_KEY": _KEY,
        "DRC_DEBUG_MINA_ELEVENLABS_VOICE_ID": _VOICE,
    }.items():
        monkeypatch.setenv(name, value)

    artifacts = VoiceOutputArtifactStore(tmp_path / "voice")
    for module in (voice_api, voice_service):
        monkeypatch.setattr(module, "VoiceOutputArtifactStore", lambda **_: artifacts)

    calls = []
    outcomes = []

    class FakeElevenLabs:
        def __init__(self, *, api_key, **_):
            assert api_key == _KEY
            self.text_to_speech = SimpleNamespace(convert=self.convert)

        def convert(self, **request):
            calls.append(request)
            outcome = outcomes.pop(0) if outcomes else _MP3
            if isinstance(outcome, Exception):
                yield b"partial audio"
                raise outcome
            yield outcome[:3]
            yield outcome[3:]

    monkeypatch.setitem(
        sys.modules, "elevenlabs.client", SimpleNamespace(ElevenLabs=FakeElevenLabs)
    )
    with TestClient(app) as client:
        yield client, calls, outcomes, artifacts


def _assert_playable(client, response):
    assert response.status_code == 200
    assert _KEY not in response.text and _VOICE not in response.text
    data = response.json()
    assert data["accepted"] and data["audio_ready"] and data["is_generated"]
    assert data["request_state"] == "generated"
    assert data["audio_format"] == "mp3"
    assert data["audio_handoff_kind"] == "url" and data["has_audio_handoff"]
    assert data["audio_artifact_ref"] is None
    assert re.fullmatch(r"/demo/voice-output/audio/[0-9a-f]{32}", data["audio_url"])
    audio = client.get(data["audio_url"])
    assert audio.status_code == 200
    assert audio.headers["content-type"] == "audio/mpeg"
    assert audio.content == _MP3
    return data


def test_direct_mina_posts_and_gets_identical_mp3(local_voice):
    client, calls, _, _ = local_voice
    assert client.get(_ROUTE + "/status").json()["capability"]["status"] == "available"
    assert not calls
    data = _assert_playable(client, client.post(_ROUTE, json=_FIXTURE))
    assert data["adapter_mode"] == "elevenlabs_mina"
    assert data["framework_call_state"] == "not_called"
    assert calls == [{
        "voice_id": _VOICE,
        "text": _FIXTURE["text_content"],
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128",
        "request_options": {"max_retries": 0},
    }]


def test_failed_stream_leaks_no_details_or_partial_artifact_and_allows_retry(local_voice):
    client, calls, outcomes, artifacts = local_voice
    outcomes.append(RuntimeError(f"provider-private response with {_KEY} and {_VOICE}"))
    failed = client.post(_ROUTE, json=_FIXTURE)
    assert failed.status_code == 200
    assert "provider-private" not in failed.text
    assert _KEY not in failed.text and _VOICE not in failed.text
    data = failed.json()
    assert data["request_state"] == "failed"
    assert not data["accepted"] and not data["audio_ready"]
    assert data["audio_url"] is None
    assert not list(artifacts.framework_artifact_dir.iterdir())
    _assert_playable(client, client.post(_ROUTE, json=_FIXTURE))
    assert len(calls) == 2


@pytest.mark.parametrize("field,value", [
    ("text_content", "unexpected input"),
    ("character_id", "cheerful_sora"),
    ("audio_format", "wav"),
    ("output_mode", "other"),
])
def test_direct_mode_keeps_provider_requests_limited_to_mina_fixture(local_voice, field, value):
    client, calls, _, _ = local_voice
    response = client.post(_ROUTE, json={**_FIXTURE, field: value})
    assert response.json()["request_state"] == "blocked_invalid_request"
    assert not calls


@pytest.mark.parametrize("name,value,expected", [
    ("VOICE_OUTPUT_REAL_TTS_ENABLED", "0", "guarded_not_started"),
    ("VOICE_OUTPUT_DEMO_ENABLED", "0", "not_started"),
    ("ELEVENLABS_API_KEY", "", "not_started"),
    ("DRC_DEBUG_MINA_ELEVENLABS_VOICE_ID", "", "not_started"),
])
def test_direct_mode_requires_opt_in_and_credentials(local_voice, monkeypatch, name, value, expected):
    client, calls, _, _ = local_voice
    monkeypatch.setenv(name, value)
    response = client.post(_ROUTE, json=_FIXTURE)
    assert response.json()["request_state"] == expected
    assert not calls


def test_framework_mode_keeps_legacy_file_handoff(local_voice, monkeypatch, tmp_path):
    client, calls, _, _ = local_voice
    monkeypatch.setenv("VOICE_OUTPUT_ADAPTER_MODE", "framework")
    monkeypatch.setenv("CONVERSATION_ENGINE", "framework")
    monkeypatch.setenv("FRAMEWORK_ROOT", str(tmp_path))
    public_api = tmp_path / "framework" / "__init__.py"
    public_api.parent.mkdir()
    public_api.write_text("create_voice_output_session", encoding="utf-8")
    boundary = public_api.parent / "audio" / "voice_output.py"
    boundary.parent.mkdir()
    boundary.touch()

    class FakeFrameworkAdapter:
        def __init__(self, root, *, artifact_dir, **_):
            assert root == tmp_path.resolve()
            path = Path(artifact_dir) / "legacy.mp3"
            path.write_bytes(_MP3)
            self.result = FrameworkVoiceOutputResult(
                status="generated",
                audio_artifact_ref=str(path),
                audio_format="mp3",
                is_generated=True,
                audio_ready=True,
                audio_handoff_kind="artifact_ref",
                has_audio_handoff=True,
                message="legacy fixture",
            )

        def synthesize(self, request):
            assert request.text == _FIXTURE["text_content"]
            return self.result

    monkeypatch.setattr(voice_service, "FrameworkVoiceOutputAdapter", FakeFrameworkAdapter)
    data = _assert_playable(client, client.post(_ROUTE, json=_FIXTURE))
    assert data["adapter_mode"] == "framework"
    assert data["framework_call_state"] == "generated"
    assert not calls
