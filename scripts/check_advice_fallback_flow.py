from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.engines.mock_engine import MockConversationEngine  # noqa: E402
from app.models.advice import AdviceRequest  # noqa: E402
from app.models.character import CharacterContext  # noqa: E402
from app.models.sleep import SleepSummary  # noqa: E402
from app.services.advice_prompt_builder import build_advice_prompt  # noqa: E402

SCRIPT_NAME = "advice-fallback-flow-check-v0.24.0"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _character() -> CharacterContext:
    return CharacterContext(
        character_id="default",
        display_name="Default",
        description="Default test character",
        personality_type="friendly",
        speaking_style="casual",
        advice_style="light",
    )


def _unavailable_sleep() -> SleepSummary:
    return SleepSummary(
        date="2026-05-06",
        total_sleep_minutes=0,
        source="google_health",
        available=False,
        message="Google Health returned no sleep dataPoints for the target date.",
        quality_label="unavailable",
        confidence="none",
        is_real_data=False,
        unavailable_reason="no_sleep_data_points",
    )


def check_prompt_does_not_invent_sleep_duration() -> None:
    prompt = build_advice_prompt(
        AdviceRequest(
            character=_character(),
            mood="tired",
            sleep=_unavailable_sleep(),
        )
    )

    _assert("Sleep data is unavailable today." in prompt, prompt)
    _assert("Unavailable reason: no_sleep_data_points" in prompt, prompt)
    _assert("Base the advice mainly on the user's mood." in prompt, prompt)
    _assert("Total sleep: 0h 0m" not in prompt, prompt)
    _assert("Sleep efficiency: 0" not in prompt, prompt)


def check_mock_engine_falls_back_to_mood() -> None:
    response = MockConversationEngine().create_advice(
        AdviceRequest(
            character=_character(),
            mood="tired",
            sleep=_unavailable_sleep(),
        )
    )

    _assert("君の眠りを観測できなかった" in response.message, response.message)
    _assert("だるい" in response.message, response.message)
    _assert("軽めのタスクを1つ" in response.message, response.message)
    _assert("0時間0分" not in response.message, response.message)
    _assert("Google Healthの実データ" not in response.message, response.message)


def main() -> int:
    check_prompt_does_not_invent_sleep_duration()
    check_mock_engine_falls_back_to_mood()
    print(f"[{SCRIPT_NAME}] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
