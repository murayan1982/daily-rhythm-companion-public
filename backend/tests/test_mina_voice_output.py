from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from app.api import debug_advice
from app.api import voice_output_demo as voice_api
from app.config import AppConfig
from app.main import app
from app.services import voice_output_demo_service as voice_service
from app.services.debug_advice_voice_store import DebugAdviceVoiceStore
from app.services.debug_advice_conversation import (
    ConversationReply,
    ConversationUnavailable,
    DebugAdviceConversationStore,
)
from app.services.framework_voice_output_adapter import FrameworkVoiceOutputResult
from app.services.public_advice import (
    InMemoryDailyAdviceQuota,
    LocalAdviceTokenVerifier,
    PublicAdviceRuntime,
)
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
_MINA_ADVICE = "/debug/mina/ai-advice"
_MINA_AUDIO = "/debug/mina/voice"
_ADVICE_INPUT = {"mood": "tired", "character_id": "gentle_mina"}
_CHARACTER_ADVICE = "/debug/character/ai-advice"
_CHARACTER_AUDIO = "/debug/character/voice"
_INVITE_ADVICE = "/debug/invite/advice"
_CHARACTERS = {
    "gentle_mina": ("今日は短い休憩を入れましょう。", "thinking", "MINA", _VOICE),
    "cheerful_sora": ("元気に一歩ずつ進もう。", "happy", "SORA", "offline-sora"),
    "cool_rei": ("やることを一つ決めよう。", "thinking", "REI", "offline-rei"),
}


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


@pytest.fixture
def generated_advice(monkeypatch):
    now = [10.0]
    store = DebugAdviceVoiceStore(clock=lambda: now[0])
    monkeypatch.setattr(debug_advice, "advice_voice", store)
    monkeypatch.setattr(debug_advice, "config", AppConfig(debug_ai_advice_enabled=True))
    message = _CHARACTERS["gentle_mina"][0]

    def reply(*, prompt):
        character_id = next(
            character_id for character_id in _CHARACTERS
            if f"Character ID: {character_id}" in prompt
        )
        text, tag, _, _ = _CHARACTERS[character_id]
        return SimpleNamespace(
            status="responded",
            reply_text=json.dumps({"message": f"  {text}  ", "expression_tag": tag}),
        )

    monkeypatch.setitem(
        app.dependency_overrides,
        debug_advice.get_debug_advice_provider,
        lambda: SimpleNamespace(reply=reply),
    )
    return message, now


def test_generated_mina_retries_and_synthesizes_exact_displayed_text(local_voice, generated_advice):
    client, calls, outcomes, _ = local_voice
    message, _ = generated_advice
    advice = client.post(_MINA_ADVICE, json=_ADVICE_INPUT)
    assert advice.status_code == 200
    assert advice.headers["cache-control"] == "no-store"
    data = advice.json()
    assert data["message"] == message
    assert data["expression_tag"] == "thinking"
    assert not calls

    request = {"voice_ref": data["voice_ref"]}
    outcomes.append(RuntimeError("private provider details"))
    failed = client.post(_MINA_AUDIO, json=request)
    assert failed.status_code == 200
    assert failed.json() == {
        "accepted": False, "audio_ready": False, "audio_format": "mp3", "audio_url": None,
    }
    voiced = client.post(_MINA_AUDIO, json=request)
    assert voiced.status_code == 200
    assert message not in voiced.text and _VOICE not in voiced.text
    payload = voiced.json()
    assert payload["accepted"] and payload["audio_ready"]
    audio = client.get(payload["audio_url"])
    assert audio.status_code == 200 and audio.content == _MP3
    assert [call["text"] for call in calls] == [data["message"], data["message"]]


def test_generated_mina_rejects_unknown_expired_and_client_supplied_text(local_voice, generated_advice):
    client, calls, _, _ = local_voice
    message, now = generated_advice
    assert client.post(_MINA_ADVICE, json={**_ADVICE_INPUT, "character_id": "cool_rei"}).status_code == 422
    advice = client.post(_MINA_ADVICE, json=_ADVICE_INPUT).json()
    request = {"voice_ref": advice["voice_ref"]}
    assert client.post(_MINA_AUDIO, json={"voice_ref": "!"}).status_code == 422
    assert client.post(_MINA_AUDIO, json={"voice_ref": "g" * 32}).status_code == 404
    assert client.post(_MINA_AUDIO, json={**request, "text_content": message}).status_code == 422
    assert client.post(_ROUTE, json={**_FIXTURE, "text_content": message}).json()[
        "request_state"
    ] == "blocked_invalid_request"
    now[0] += 300
    assert client.post(_MINA_AUDIO, json=request).status_code == 404
    assert not calls


def test_generated_mina_voice_requires_debug_and_direct_mode(
    local_voice, generated_advice, monkeypatch
):
    client, calls, _, _ = local_voice
    advice = client.post(_MINA_ADVICE, json=_ADVICE_INPUT).json()
    request = {"voice_ref": advice["voice_ref"]}
    monkeypatch.setenv("VOICE_OUTPUT_ADAPTER_MODE", "framework")
    assert client.post(_MINA_AUDIO, json=request).status_code == 503
    monkeypatch.setenv("VOICE_OUTPUT_ADAPTER_MODE", "elevenlabs_mina")
    monkeypatch.setattr(debug_advice, "config", AppConfig())
    assert client.post(_MINA_AUDIO, json=request).status_code == 503
    assert not calls


@pytest.mark.parametrize("character_id", _CHARACTERS)
def test_generated_advice_synthesizes_only_matching_character_and_text(
    local_voice, generated_advice, monkeypatch, character_id
):
    client, calls, _, _ = local_voice
    text, tag, voice_key, voice_id = _CHARACTERS[character_id]
    monkeypatch.setenv(f"DRC_DEBUG_{voice_key}_ELEVENLABS_VOICE_ID", voice_id)
    if character_id != "gentle_mina":
        monkeypatch.delenv("DRC_DEBUG_MINA_ELEVENLABS_VOICE_ID")
    response = client.post(_CHARACTER_ADVICE, json={**_ADVICE_INPUT, "character_id": character_id})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    advice = response.json()
    assert advice["message"] == text and advice["expression_tag"] == tag
    assert not calls

    request = {"character_id": character_id, "voice_ref": advice["voice_ref"]}
    other = next(other for other in _CHARACTERS if other != character_id)
    assert client.post(_CHARACTER_AUDIO, json={**request, "character_id": other}).status_code == 404
    if character_id != "gentle_mina":
        assert client.post(_MINA_AUDIO, json={"voice_ref": request["voice_ref"]}).status_code == 404
    assert client.post(_CHARACTER_AUDIO, json={**request, "text_content": text}).status_code == 422
    assert client.post(_CHARACTER_AUDIO, json={**request, "voice_ref": "x" * 32}).status_code == 404
    assert not calls
    audio_response = client.post(_CHARACTER_AUDIO, json=request)
    assert audio_response.status_code == 200
    audio = audio_response.json()
    assert audio["accepted"] and audio["audio_ready"] and audio["audio_format"] == "mp3"
    assert voice_id not in audio_response.text and text not in audio_response.text
    downloaded = client.get(audio["audio_url"])
    assert downloaded.status_code == 200 and downloaded.content == _MP3
    assert len(calls) == 1 and (calls[0]["text"], calls[0]["voice_id"]) == (text, voice_id)
    _, now = generated_advice
    now[0] += 300
    assert client.post(_CHARACTER_AUDIO, json=request).status_code == 404
    assert len(calls) == 1


def test_missing_character_voice_keeps_advice_without_an_audio_reference(
    local_voice, generated_advice, monkeypatch
):
    client, calls, _, _ = local_voice
    monkeypatch.delenv("DRC_DEBUG_SORA_ELEVENLABS_VOICE_ID", raising=False)
    request = {**_ADVICE_INPUT, "character_id": "cheerful_sora"}
    no_voice = client.post(_CHARACTER_ADVICE, json=request)
    text, tag, _, voice = _CHARACTERS["cheerful_sora"]
    assert no_voice.status_code == 200
    assert no_voice.json() == {"message": text, "expression_tag": tag, "voice_ref": None}
    monkeypatch.setenv("DRC_DEBUG_SORA_ELEVENLABS_VOICE_ID", voice)
    issued = client.post(_CHARACTER_ADVICE, json=request).json()["voice_ref"]
    monkeypatch.delenv("DRC_DEBUG_SORA_ELEVENLABS_VOICE_ID")
    rejected = client.post(_CHARACTER_AUDIO, json={"character_id": "cheerful_sora", "voice_ref": issued})
    assert rejected.status_code == 200 and not rejected.json()["accepted"] and not calls


@pytest.mark.parametrize("character_id", _CHARACTERS)
def test_invite_voice_plays_the_validated_text_with_the_selected_voice(
    local_voice, generated_advice, monkeypatch, character_id
):
    client, calls, _, _ = local_voice
    text, _, voice_key, voice_id = _CHARACTERS[character_id]
    monkeypatch.setenv(f"DRC_DEBUG_{voice_key}_ELEVENLABS_VOICE_ID", voice_id)
    requests = []

    def generate(**selection):
        requests.append(selection)
        return f"  {text}  "

    monkeypatch.setattr(
        app.state,
        "public_advice_runtime",
        PublicAdviceRuntime(
            authenticate=LocalAdviceTokenVerifier({"test-token": "tester"}),
            quota=InMemoryDailyAdviceQuota(per_user=1, total=1),
            generate=generate,
        ),
        raising=False,
    )
    selection = {**_ADVICE_INPUT, "character_id": character_id}
    headers = {"Authorization": "Bearer test-token"}
    assert client.post(_INVITE_ADVICE, json=selection).status_code == 401
    assert client.post(
        _INVITE_ADVICE, json={**selection, "sleep_summary": {}}, headers=headers
    ).status_code == 422
    assert not requests

    response = client.post(_INVITE_ADVICE, json=selection, headers=headers)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    advice = response.json()
    assert advice["message"] == text
    assert requests == [selection]
    assert client.post(_INVITE_ADVICE, json=selection, headers=headers).status_code == 429
    other = next(other for other in _CHARACTERS if other != character_id)
    voice = {"character_id": character_id, "voice_ref": advice["voice_ref"]}
    assert client.post(_CHARACTER_AUDIO, json={**voice, "character_id": other}).status_code == 404
    assert not calls

    audio = client.post(_CHARACTER_AUDIO, json=voice)
    assert audio.status_code == 200 and audio.json()["audio_ready"]
    downloaded = client.get(audio.json()["audio_url"])
    assert downloaded.status_code == 200 and downloaded.content == _MP3
    assert [(call["text"], call["voice_id"]) for call in calls] == [(text, voice_id)]


def test_invite_voice_route_is_disabled_by_default(local_voice, monkeypatch):
    client, calls, _, _ = local_voice
    monkeypatch.setattr(debug_advice, "config", AppConfig())
    assert client.post(_INVITE_ADVICE, json=_ADVICE_INPUT).status_code == 503
    assert not calls


def test_invite_sleep_duration_reaches_only_the_development_generator(
    local_voice, generated_advice, monkeypatch
):
    client, audio_calls, _, _ = local_voice
    plain = []
    with_sleep = []

    def generate(**selection):
        plain.append(selection)
        return "気分に合わせてひと息つきましょう。"

    def generate_with_sleep(**selection):
        with_sleep.append(selection)
        return "眠れた時間を踏まえてゆっくり始めましょう。"

    monkeypatch.setattr(
        app.state,
        "public_advice_runtime",
        PublicAdviceRuntime(
            authenticate=LocalAdviceTokenVerifier({"test-token": "tester"}),
            quota=InMemoryDailyAdviceQuota(per_user=2, total=2),
            generate=generate,
            generate_with_sleep=generate_with_sleep,
        ),
        raising=False,
    )
    headers = {"Authorization": "Bearer test-token"}
    payload = {**_ADVICE_INPUT, "total_sleep_minutes": 367}
    assert client.post("/v1/advice", json=payload, headers=headers).status_code == 422
    for invalid in (0, -1, 1441, "367", True):
        assert client.post(
            _INVITE_ADVICE, json={**payload, "total_sleep_minutes": invalid}, headers=headers
        ).status_code == 422
    assert client.post(
        _INVITE_ADVICE, json={**payload, "bedtime": "01:00"}, headers=headers
    ).status_code == 422
    assert client.post(_INVITE_ADVICE, json=payload, headers=headers).status_code == 200
    assert client.post(_INVITE_ADVICE, json=_ADVICE_INPUT, headers=headers).status_code == 200
    assert with_sleep == [payload]
    assert plain == [_ADVICE_INPUT]
    assert not audio_calls


@pytest.mark.parametrize("character_id", _CHARACTERS)
def test_debug_conversation_uses_advice_and_two_turns_with_retry(
    local_voice, monkeypatch, character_id
):
    client, calls, _, artifacts = local_voice
    store = DebugAdviceConversationStore(ttl=60, capacity=8, turn_limit=8)
    monkeypatch.setattr(debug_advice, "conversations", store)
    monkeypatch.setattr(debug_advice, "config", AppConfig(debug_ai_advice_enabled=True))
    advice, tag, voice_key, voice_id = _CHARACTERS[character_id]
    monkeypatch.setenv(f"DRC_DEBUG_{voice_key}_ELEVENLABS_VOICE_ID", voice_id)
    prompts = []

    def reply(*, prompt):
        prompts.append(prompt)
        if len(prompts) == 2:
            raise RuntimeError("offline provider failure")
        output = advice if len(prompts) == 1 else f"返信{len(prompts)}。"
        return SimpleNamespace(
            status="responded",
            reply_text=json.dumps({"message": output, "expression_tag": tag}),
        )

    monkeypatch.setitem(
        app.dependency_overrides,
        debug_advice.get_debug_advice_provider,
        lambda: SimpleNamespace(reply=reply),
    )
    path = "/debug/conversation"
    assert client.post(path + "/start", json={"advice_ref": "x" * 32}).status_code == 404
    assert not prompts
    generated = client.post(path + "/advice", json={**_ADVICE_INPUT, "character_id": character_id}).json()
    assert generated["message"] == advice and len(prompts) == 1
    started = client.post(path + "/start", json={"advice_ref": generated["advice_ref"]})
    assert started.status_code == 200 and len(prompts) == 1 and not calls
    session = {"session_id": started.json()["session_id"]}
    first_request = {**session, "turn": 1, "message": "最初の質問"}
    assert client.post(path + "/turn", json=first_request).status_code == 502
    first = client.post(path + "/turn", json=first_request).json()
    assert first["message"] == "返信3。"
    assert client.post(path + "/turn", json=first_request).json() == first
    assert len(prompts) == 3
    assert client.post(path + "/turn", json={**first_request, "message": "別の質問"}).status_code == 409

    second = client.post(
        path + "/turn", json={**session, "turn": 2, "message": "追加質問"},
    ).json()
    assert second["message"] == "返信4。" and second["expression_tag"] == tag
    assert f"({character_id})" in prompts[-1] and advice in prompts[-1]
    assert prompts[-1].count("最初の質問") == 1
    assert prompts[-1].count(first["message"]) == 1 and "追加質問" in prompts[-1]
    assert not calls
    voice = {**session, "voice_ref": second["voice_ref"]}
    assert client.post(path + "/voice", json={**voice, "message": "任意の本文"}).status_code == 422
    audio = client.post(path + "/voice", json=voice)
    assert audio.status_code == 200 and audio.headers["content-type"] == "audio/mpeg"
    assert audio.content == _MP3 and audio.headers["cache-control"] == "no-store"
    assert len(calls) == 1 and (calls[0]["text"], calls[0]["voice_id"]) == (second["message"], voice_id)
    assert not list(artifacts.framework_artifact_dir.iterdir())

    assert client.post(path + "/end", json=session).json() == {"closed": True}
    assert client.post(path + "/voice", json=voice).status_code == 404
    assert client.post(path + "/turn", json=first_request).status_code == 404
    fresh = client.post(path + "/start", json={"advice_ref": generated["advice_ref"]}).json()
    assert fresh["session_id"] != session["session_id"]
    client.post(path + "/turn", json={"session_id": fresh["session_id"], "turn": 1, "message": "新しい質問"})
    assert "最初の質問" not in prompts[-1] and "追加質問" not in prompts[-1]


def test_ending_a_debug_conversation_discards_the_inflight_turn():
    store = DebugAdviceConversationStore(ttl=60, capacity=8, turn_limit=8)
    session = store.start(store.remember_advice("gentle_mina", "助言"))

    def generate(*_):
        store.end(session)
        return ConversationReply("古い返信", "idle", "x" * 32)

    with pytest.raises(ConversationUnavailable):
        store.reply(session, 1, "質問", generate)
    assert store.resolve_voice(session, "x" * 32) is None


def test_invite_conversation_reuses_character_advice_and_free_topic_history(
    generated_advice, monkeypatch
):
    store = DebugAdviceConversationStore(ttl=60, capacity=8, turn_limit=4)
    monkeypatch.setattr(debug_advice, "conversations", store)
    monkeypatch.setenv("VOICE_OUTPUT_DEMO_ENABLED", "0")
    initial_advice = "焦らず始めましょう。"
    monkeypatch.setattr(
        app.state,
        "public_advice_runtime",
        PublicAdviceRuntime(
            authenticate=LocalAdviceTokenVerifier({"test-token": "tester"}),
            quota=InMemoryDailyAdviceQuota(per_user=1, total=1),
            generate=lambda **selection: initial_advice,
        ),
        raising=False,
    )
    prompts = []

    def reply(*, prompt):
        prompts.append(prompt)
        return SimpleNamespace(
            status="responded",
            reply_text=json.dumps({
                "message": f"猫についての返信{len(prompts)}。",
                "expression_tag": "idle",
            }),
        )

    monkeypatch.setitem(
        app.dependency_overrides,
        debug_advice.get_debug_advice_provider,
        lambda: SimpleNamespace(reply=reply),
    )
    path = "/debug/invite/conversation/advice"
    client = TestClient(app)
    selection = {"mood": "normal", "character_id": "cheerful_sora"}
    assert client.post(path, json=selection).status_code == 401
    issued = client.post(path, json=selection, headers={"Authorization": "Bearer test-token"})
    assert issued.status_code == 200
    assert issued.headers["cache-control"] == "no-store"
    assert issued.json()["message"] == initial_advice
    anchor = {"advice_ref": issued.json()["advice_ref"]}
    session = client.post("/debug/conversation/start", json=anchor).json()["session_id"]
    assert not prompts

    def send(session_id, turn, message):
        return client.post(
            "/debug/conversation/turn",
            json={"session_id": session_id, "turn": turn, "message": message},
        )

    first = send(session, 1, "好きな動物は？")
    assert first.status_code == 200
    assert send(session, 2, "どんな猫？").status_code == 200
    latest = prompts[-1]
    assert "ソラ (cheerful_sora)" in latest
    assert "Casual conversation on topics unrelated to advice is welcome" in latest
    context = json.loads(latest.splitlines()[1])
    assert context == {
        "advice": initial_advice,
        "messages": [
            {"role": "user", "content": "好きな動物は？"},
            {"role": "assistant", "content": first.json()["message"]},
            {"role": "user", "content": "どんな猫？"},
        ],
    }
    assert client.post("/debug/conversation/end", json={"session_id": session}).status_code == 200
    assert send(session, 3, "続きは？").status_code == 404
    reopened = client.post("/debug/conversation/start", json=anchor).json()["session_id"]
    assert reopened != session
    assert send(reopened, 1, "映画も好き？").status_code == 200
    assert "好きな動物は？" not in prompts[-1]
