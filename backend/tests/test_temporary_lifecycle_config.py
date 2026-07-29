"""Configuration regression tests for bounded temporary resources."""

from __future__ import annotations

from app.config import load_config


def test_temporary_lifecycle_defaults_are_bounded(monkeypatch) -> None:
    for name in (
        "POST_ADVICE_CHAT_TTL_SECONDS",
        "POST_ADVICE_CHAT_MAX_SESSIONS",
        "POST_ADVICE_CHAT_MAX_TURNS",
        "REALTIME_TEXT_STREAM_IDLE_TTL_SECONDS",
        "REALTIME_TEXT_STREAM_MAX_DURATION_SECONDS",
        "REALTIME_TEXT_STREAM_MAX_SESSIONS",
        "REALTIME_TEXT_STREAM_MAX_PENDING_EVENTS",
        "REALTIME_TEXT_STREAM_MAX_EVENT_BYTES",
        "DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM",
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
    assert config.realtime_text_stream_idle_ttl_seconds == 120
    assert config.realtime_text_stream_max_duration_seconds == 60
    assert config.realtime_text_stream_max_sessions == 8
    assert config.realtime_text_stream_max_pending_events == 32
    assert config.realtime_text_stream_max_event_bytes == 32768
    assert config.realtime_text_stream_framework_enabled is False
    assert config.voice_output_artifact_ttl_seconds == 86400
    assert config.voice_output_artifact_max_count == 100
    assert config.voice_input_staging_ttl_seconds == 300
    assert config.voice_input_staging_max_count == 8
    assert config.voice_input_staging_max_bytes == 1048576


def test_temporary_lifecycle_values_can_be_overridden(monkeypatch) -> None:
    monkeypatch.setenv("POST_ADVICE_CHAT_TTL_SECONDS", "45")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_SESSIONS", "7")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_TURNS", "5")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_IDLE_TTL_SECONDS", "12")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_DURATION_SECONDS", "20")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_SESSIONS", "3")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_PENDING_EVENTS", "6")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_EVENT_BYTES", "4096")
    monkeypatch.setenv("DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM", "1")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_TTL_SECONDS", "90")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_MAX_COUNT", "9")
    monkeypatch.setenv("VOICE_INPUT_STAGING_TTL_SECONDS", "30")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_COUNT", "4")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_BYTES", "2048")

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 45
    assert config.post_advice_chat_max_sessions == 7
    assert config.post_advice_chat_max_turns == 5
    assert config.realtime_text_stream_idle_ttl_seconds == 12
    assert config.realtime_text_stream_max_duration_seconds == 20
    assert config.realtime_text_stream_max_sessions == 3
    assert config.realtime_text_stream_max_pending_events == 6
    assert config.realtime_text_stream_max_event_bytes == 4096
    assert config.realtime_text_stream_framework_enabled is True
    assert config.voice_output_artifact_ttl_seconds == 90
    assert config.voice_output_artifact_max_count == 9
    assert config.voice_input_staging_ttl_seconds == 30
    assert config.voice_input_staging_max_count == 4
    assert config.voice_input_staging_max_bytes == 2048


def test_invalid_temporary_lifecycle_values_use_safe_defaults(monkeypatch) -> None:
    monkeypatch.setenv("POST_ADVICE_CHAT_TTL_SECONDS", "0")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_SESSIONS", "-1")
    monkeypatch.setenv("POST_ADVICE_CHAT_MAX_TURNS", "invalid")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_IDLE_TTL_SECONDS", "0")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_DURATION_SECONDS", "invalid")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_SESSIONS", "-1")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_PENDING_EVENTS", "")
    monkeypatch.setenv("REALTIME_TEXT_STREAM_MAX_EVENT_BYTES", "invalid")
    monkeypatch.setenv("DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM", "0")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_TTL_SECONDS", "invalid")
    monkeypatch.setenv("VOICE_OUTPUT_ARTIFACT_MAX_COUNT", "")
    monkeypatch.setenv("VOICE_INPUT_STAGING_TTL_SECONDS", "0")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_COUNT", "-1")
    monkeypatch.setenv("VOICE_INPUT_STAGING_MAX_BYTES", "invalid")

    config = load_config()

    assert config.post_advice_chat_ttl_seconds == 1800
    assert config.post_advice_chat_max_sessions == 100
    assert config.post_advice_chat_max_turns == 8
    assert config.realtime_text_stream_idle_ttl_seconds == 120
    assert config.realtime_text_stream_max_duration_seconds == 60
    assert config.realtime_text_stream_max_sessions == 8
    assert config.realtime_text_stream_max_pending_events == 32
    assert config.realtime_text_stream_max_event_bytes == 32768
    assert config.realtime_text_stream_framework_enabled is False
    assert config.voice_output_artifact_ttl_seconds == 86400
    assert config.voice_output_artifact_max_count == 100
    assert config.voice_input_staging_ttl_seconds == 300
    assert config.voice_input_staging_max_count == 8
    assert config.voice_input_staging_max_bytes == 1048576
