"""Mock conversation engine regression tests without external providers."""

from __future__ import annotations

from app.engines.mock_engine import MockConversationEngine
from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.sleep import SleepSummary


def test_mock_advice_uses_stable_character_and_source_metadata() -> None:
    request = AdviceRequest(
        character=CharacterContext(
            character_id="cool_rei",
            display_name="レイ",
            personality_type="cool",
            speaking_style="concise",
            advice_style="practical",
        ),
        sleep=SleepSummary(
            date="2026-07-22",
            total_sleep_minutes=420,
            efficiency=88,
            source="mock",
            available=True,
            quality_label="good",
        ),
        mood="normal",
    )

    response = MockConversationEngine().create_advice(request)

    assert response.character_name == "レイ"
    assert response.source is not None
    assert response.source.engine == "mock"
    assert response.source.drc_character_id == "cool_rei"
    assert response.source.drc_character_name == "レイ"
    assert "7時間0分" in response.message
    assert "今の気分は「ふつう」" in response.message
    assert "睡眠は良さそう" in response.message


def test_mock_advice_does_not_invent_sleep_when_unavailable() -> None:
    request = AdviceRequest(
        character=CharacterContext(
            character_id="gentle_mina",
            display_name="ミナ",
            personality_type="gentle",
            speaking_style="casual",
            advice_style="rest_focused",
        ),
        sleep=SleepSummary(
            date="2026-07-22",
            total_sleep_minutes=0,
            source="mock",
            available=False,
            unavailable_reason="not_connected",
        ),
        mood="tired",
    )

    response = MockConversationEngine().create_advice(request)

    assert "眠り" in response.message
    assert "観測できなかった" in response.message
    assert "0時間0分" not in response.message
    assert "だるい" in response.message
