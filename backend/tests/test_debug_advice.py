import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api import debug_advice
from app.config import AppConfig
from app.main import app
from app.services.framework_text_chat_drc_live_reply import (
    FrameworkTextChatDrcLiveReplyService,
)


URL = "/debug/ai-advice"
CHARACTERS = {
    "gentle_mina": ("ミナ", "gentle", "casual", "rest_focused"),
    "cheerful_sora": ("ソラ", "cheerful", "casual", "positive"),
    "cool_rei": ("レイ", "cool", "concise", "practical"),
}
REPLIES = {
    "energetic": {"message": "気持ちのよいペースで始めましょう。", "expression_tag": "happy"},
    "normal": {"message": "できることを一つ選びましょう。", "expression_tag": "idle"},
    "tired": {"message": "ひと息ついてから始めましょう。", "expression_tag": "supportive"},
}


@pytest.fixture
def provider(monkeypatch):
    mock = Mock(spec=FrameworkTextChatDrcLiveReplyService)
    monkeypatch.setitem(app.dependency_overrides, debug_advice.get_debug_advice_provider, lambda: mock)
    return mock


@pytest.mark.parametrize("mood", REPLIES)
@pytest.mark.parametrize("character_id", CHARACTERS)
@pytest.mark.parametrize("with_sleep", [True, False])
def test_mood_character_and_optional_sleep_reach_provider(provider, mood, character_id, with_sleep):
    expected = REPLIES[mood]
    provider.reply.return_value = SimpleNamespace(
        status="responded", reply_text=json.dumps(expected, ensure_ascii=False)
    )
    payload = {"mood": mood, "character_id": character_id}
    if with_sleep:
        payload["sleep_summary"] = {"total_sleep_minutes": 385}

    result = TestClient(app).post(URL, json=payload)

    assert result.status_code == 200
    assert result.json() == expected
    provider.reply.assert_called_once()
    prompt = provider.reply.call_args.kwargs["prompt"]
    name, personality, speaking_style, advice_style = CHARACTERS[character_id]
    for expected_text in (
        f"You are {name},",
        f"Character ID: {character_id}",
        f"Personality type: {personality}",
        f"Speaking style: {speaking_style}",
        f"Advice style: {advice_style}",
        f"User mood: {mood}",
        "one or two short Japanese sentences",
        '"expression_tag" must be one of: idle, happy, thinking, supportive, speaking',
    ):
        assert expected_text in prompt
    if with_sleep:
        assert "Total sleep: 6h 25m" in prompt
    else:
        assert "Sleep data is unavailable today." in prompt
        assert "Total sleep:" not in prompt
        assert "do not invent sleep details" in prompt


@pytest.mark.parametrize(
    "changes",
    [
        {"mood": "excited"},
        {"character_id": "unknown"},
        {"sleep_summary": {}},
        {"sleep_summary": {"total_sleep_minutes": -1}},
        {"sleep_summary": {"total_sleep_minutes": 1441}},
        {"sleep_summary": {"total_sleep_minutes": True}},
        {"sleep_summary": {"total_sleep_minutes": "385"}},
        {"sleep_summary": {"total_sleep_minutes": 385, "sleep_start": "00:00"}},
        {"prior_messages": []},
    ],
)
def test_invalid_input_never_reaches_provider(provider, changes):
    result = TestClient(app).post(
        URL, json={"mood": "tired", "character_id": "gentle_mina", **changes}
    )
    assert result.status_code == 422
    provider.reply.assert_not_called()


def test_route_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(debug_advice, "config", AppConfig())
    result = TestClient(app).post(URL, json={"mood": "tired", "character_id": "gentle_mina"})
    assert result.status_code == 503
    assert result.json() == {"detail": "Debug AI advice is disabled."}


@pytest.mark.parametrize(
    ("status", "code", "detail"),
    [
        ("blocked-framework-root-missing", 503, "AI advice provider is unavailable."),
        ("error", 502, "AI advice generation failed."),
        ("error-empty-response", 502, "AI advice generation failed."),
    ],
)
def test_provider_status_is_sanitized(provider, status, code, detail):
    provider.reply.return_value = SimpleNamespace(status=status, reply_text="private-provider-detail")
    result = TestClient(app).post(URL, json={"mood": "tired", "character_id": "gentle_mina"})
    assert result.status_code == code
    assert result.json() == {"detail": detail}


def test_provider_exception_is_sanitized(provider):
    provider.reply.side_effect = TimeoutError("private-provider-detail")
    result = TestClient(app).post(URL, json={"mood": "tired", "character_id": "gentle_mina"})
    assert result.status_code == 502
    assert result.json() == {"detail": "AI advice generation failed."}


@pytest.mark.parametrize(
    "reply_text",
    [
        "not JSON",
        '{"message":"   ","expression_tag":"idle"}',
        '{"message":"休みましょう。","expression_tag":"unsupported"}',
        '{"message":"休みましょう。","expression_tag":"idle","extra":true}',
        json.dumps({"message": "休" * 241, "expression_tag": "idle"}),
    ],
)
def test_invalid_provider_output_is_rejected(provider, reply_text):
    provider.reply.return_value = SimpleNamespace(status="responded", reply_text=reply_text)
    result = TestClient(app).post(URL, json={"mood": "tired", "character_id": "gentle_mina"})
    assert result.status_code == 502
    assert result.json() == {"detail": "Invalid AI advice response."}
