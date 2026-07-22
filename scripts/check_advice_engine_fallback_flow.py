from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.api import advice as advice_api
from app.config import AppConfig
from app.engines.errors import FrameworkEngineError
from app.models.advice import AdviceRequest, AdviceResponse
from app.models.character import CharacterContext
from app.models.sleep import SleepSummary


class _StaticAdviceEngine:
    def __init__(self, message: str):
        self._message = message

    def create_advice(self, request: AdviceRequest) -> AdviceResponse:
        return AdviceResponse(
            message=self._message,
            character_name=request.character.display_name,
        )


class _FailingFrameworkEngine:
    def create_advice(self, request: AdviceRequest) -> AdviceResponse:
        raise FrameworkEngineError("simulated framework unavailable")


class _SaveCapture:
    def __init__(self):
        self.calls: list[dict[str, Any]] = []

    def save(
        self,
        *,
        request: AdviceRequest,
        response: AdviceResponse,
        advice_basis: str,
    ) -> None:
        self.calls.append(
            {
                "request": request,
                "response": response,
                "advice_basis": advice_basis,
            }
        )


def _sample_request() -> AdviceRequest:
    return AdviceRequest(
        character=CharacterContext(
            character_id="gentle_mina",
            display_name="ミナ",
            personality_type="gentle",
            speaking_style="casual",
            advice_style="rest_focused",
        ),
        sleep=SleepSummary(
            date="2026-05-10",
            total_sleep_minutes=420,
            quality_label="good",
            source="mock",
            available=True,
        ),
        mood="neutral",
    )


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _check_mock_advice_basis() -> None:
    capture = _SaveCapture()
    _replace_advice_globals(
        config=AppConfig(conversation_engine="mock"),
        conversation_engine=_StaticAdviceEngine("mock advice"),
        mock_conversation_engine=_StaticAdviceEngine("unused fallback"),
        daily_record_saver=capture,
    )

    response = advice_api.create_advice(_sample_request())

    _expect(response.message == "mock advice", "mock advice should be returned")
    _expect(len(capture.calls) == 1, "mock advice should be saved once")
    _expect(
        capture.calls[0]["advice_basis"] == "sleep+mood+character+mock",
        "mock advice basis should include +mock",
    )


def _check_framework_fallback_advice_basis() -> None:
    capture = _SaveCapture()
    _replace_advice_globals(
        config=AppConfig(conversation_engine="framework"),
        conversation_engine=_FailingFrameworkEngine(),
        mock_conversation_engine=_StaticAdviceEngine("framework fallback advice"),
        daily_record_saver=capture,
    )

    response = advice_api.create_advice(_sample_request())

    _expect(
        response.message == "framework fallback advice",
        "framework fallback advice should be returned",
    )
    _expect(len(capture.calls) == 1, "fallback advice should be saved once")
    _expect(
        capture.calls[0]["advice_basis"]
        == "sleep+mood+character+framework_fallback",
        "framework fallback advice basis should include +framework_fallback",
    )


def _check_framework_success_advice_basis() -> None:
    capture = _SaveCapture()
    _replace_advice_globals(
        config=AppConfig(conversation_engine="framework"),
        conversation_engine=_StaticAdviceEngine("framework advice"),
        mock_conversation_engine=_StaticAdviceEngine("unused fallback"),
        daily_record_saver=capture,
    )

    response = advice_api.create_advice(_sample_request())

    _expect(
        response.message == "framework advice",
        "framework advice should be returned",
    )
    _expect(len(capture.calls) == 1, "framework advice should be saved once")
    _expect(
        capture.calls[0]["advice_basis"] == "sleep+mood+character+framework",
        "framework advice basis should include +framework",
    )


def _replace_advice_globals(
    *,
    config: AppConfig,
    conversation_engine: Any,
    mock_conversation_engine: Any,
    daily_record_saver: Any,
) -> None:
    advice_api.config = config
    advice_api.conversation_engine = conversation_engine
    advice_api.mock_conversation_engine = mock_conversation_engine
    advice_api.daily_record_saver = daily_record_saver


def main() -> None:
    original_config = advice_api.config
    original_conversation_engine = advice_api.conversation_engine
    original_mock_conversation_engine = advice_api.mock_conversation_engine
    original_daily_record_saver = advice_api.daily_record_saver

    try:
        _check_mock_advice_basis()
        _check_framework_success_advice_basis()
        _check_framework_fallback_advice_basis()
    finally:
        _replace_advice_globals(
            config=original_config,
            conversation_engine=original_conversation_engine,
            mock_conversation_engine=original_mock_conversation_engine,
            daily_record_saver=original_daily_record_saver,
        )

    print("[advice-engine-fallback-flow-check-v0.30.0] OK")


if __name__ == "__main__":
    main()