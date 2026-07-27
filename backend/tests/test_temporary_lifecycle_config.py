"""Configuration regression tests for bounded temporary resources."""

from __future__ import annotations

from app.config import load_config


def test_temporary_lifecycle_defaults_are_bounded(monkeypatch) -> None:
    for name in (
        "POST_ADVICE_CHAT_TTL_SECONDS",
        "POST_ADVICE_CHAT_MAX_SESSIONS",
        "POST_ADVICE_CHAT_MAX_TURNS",
        "VOICE_OUTPUT_ARTIFACT_TTL_SECONDS",
        "VOICE_OUTPUT_ARTIFACT_MAX_COUNT",
        "VOICE_INPUT_STAGING_TTL_SECONDS",
        "VOICE_INPUT_STAGING_MAX_COUNT",
        "VOICE_INPUT_STAGING_MAX_BYTES",
    ):
        monkeypatch.delenv(name, raising=False)

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 1800
    assert config.post_advice_chat_max_sessions == 100
    assert config.post_advice_chat_max_turns == 8
    assert config.voice_output_artifact_ttl_seconds == 86400
    assert config.voice_output_artifact_max_count == 100
    assert config.voice_input_staging_ttl_seconds == 300
    assert config.voice_input_staging_max_count == 8
    assert config.voice_input_staging_max_bytes == 1048576


def test_temporary_lifecycle_values_can_be_overridden(monkeypatch) -> None:
    monkeypatch.setenv("POST_ADVICE_CHAT_TTL_SECONDS", "45")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_SESSIONS", "7")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_TURNS", "5")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_TTL_SECONDS", "90")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_MAX_COUNT", "9")
    monkeypatch.setenv("VOICE_INPUT_STAGING_TTL_SECONDS", "30")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_COUNT", "4")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_BYTES", "2048")

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 45
    assert config.post_advice_chat_max_sessions == 7
    assert config.post_advice_chat_max_turns == 5
    assert config.voice_output_artifact_ttl_seconds == 90
    assert config.voice_output_artifact_max_count == 9
    assert config.voice_input_staging_ttl_seconds == 30
    assert config.voice_input_staging_max_count == 4
    assert config.voice_input_staging_max_bytes == 2048


def test_invalid_temporary_lifecycle_values_use_safe_defaults(monkeypatch) -> None:
    monkeypatch.setenv("POST_ADVICE_CHAT_TTL_SECONDS", "0")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_SESSIONS", "-1")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_TURNS", "invalid")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_TTL_SECONDS", "invalid")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_MAX_COUNT", "")
    monkeypatch.setenv("VOICE_INPUT_STAGING_TTL_SECONDS", "0")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_COUNT", "-1")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_BYTES", "invalid")

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 1800
    assert config.post_advice_chat_max_sessions == 100
    assert config.post_advice_chat_max_turns == 8
    assert config.voice_output_artifact_ttl_seconds == 86400
    assert config.voice_output_artifact_max_count == 100
    assert config.voice_input_staging_ttl_seconds == 300
    assert config.voice_input_staging_max_count == 8
    assert config.voice_input_staging_max_bytes == 1048576
