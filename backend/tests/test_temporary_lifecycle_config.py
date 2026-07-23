"""Configuration regression tests for bounded temporary resources."""

from __future__ import annotations

from app.config import load_config


def test_temporary_lifecycle_defaults_are_bounded(monkeypatch) -> None:
    for name in (
        "POST_ADVICE_CHAT_TTL_SECONDS",
        "POST_ADVICE_CHAT_MAX_SESSIONS",
        "VOICE_OUTPUT_ARTIFACT_TTL_SECONDS",
        "VOICE_OUTPUT_ARTIFACT_MAX_COUNT",
    ):
        monkeypatch.delenv(name, raising=False)

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 1800
    assert config.post_advice_chat_max_sessions == 100
    assert config.voice_output_artifact_ttl_seconds == 86400
    assert config.voice_output_artifact_max_count == 100


def test_temporary_lifecycle_values_can_be_overridden(monkeypatch) -> None:
    monkeypatch.setenv("POST_ADVICE_CHAT_TTL_SECONDS", "45")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_SESSIONS", "7")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_TTL_SECONDS", "90")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_MAX_COUNT", "9")

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 45
    assert config.post_advice_chat_max_sessions == 7
    assert config.voice_output_artifact_ttl_seconds == 90
    assert config.voice_output_artifact_max_count == 9


def test_invalid_temporary_lifecycle_values_use_safe_defaults(monkeypatch) -> None:
    monkeypatch.setenv("POST_ADVICE_CHAT_TTL_SECONDS", "0")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_SESSIONS", "-1")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_TTL_SECONDS", "invalid")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_MAX_COUNT", "")

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 1800
    assert config.post_advice_chat_max_sessions == 100
    assert config.voice_output_artifact_ttl_seconds == 86400
    assert config.voice_output_artifact_max_count == 100
