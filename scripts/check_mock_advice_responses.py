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

SCRIPT_NAME = "mock-advice-responses-check-v0.26.0"


def _assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise AssertionError(f"Expected response to contain {expected!r}.\n{text}")


def _assert_not_contains(text: str, unexpected: str) -> None:
    if unexpected in text:
        raise AssertionError(f"Response should not contain {unexpected!r}.\n{text}")


def _character() -> CharacterContext:
    return CharacterContext(
        character_id="gentle_mina",
        display_name="ミナ",
        description="Gentle test character",
        personality_type="gentle",
        speaking_style="casual",
        advice_style="rest_focused",
    )


def _cheerful_character() -> CharacterContext:
    return CharacterContext(
        character_id="cheerful_sora",
        display_name="ソラ",
        description="Cheerful test character",
        personality_type="cheerful",
        speaking_style="casual",
        advice_style="positive",
    )


def _cool_character() -> CharacterContext:
    return CharacterContext(
        character_id="cool_rei",
        display_name="レイ",
        description="Cool test character",
        personality_type="cool",
        speaking_style="concise",
        advice_style="practical",
    )


def _sleep_summary(
    *,
    quality_label: str,
    available: bool = True,
    total_sleep_minutes: int = 490,
    is_real_data: bool = True,
) -> SleepSummary:
    if not available:
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

    return SleepSummary(
        date="2026-05-06",
        total_sleep_minutes=total_sleep_minutes,
        source="google_health",
        available=True,
        sleep_start="2026-05-05T16:59:30Z",
        sleep_end="2026-05-06T01:09:30Z",
        quality_label=quality_label,
        confidence="medium",
        is_real_data=is_real_data,
    )


def _response_message(
    *,
    quality_label: str,
    mood: str,
    available: bool = True,
    total_sleep_minutes: int = 490,
    character: CharacterContext | None = None,
) -> str:
    response = MockConversationEngine().create_advice(
        AdviceRequest(
            character=character or _character(),
            mood=mood,
            sleep=_sleep_summary(
                quality_label=quality_label,
                available=available,
                total_sleep_minutes=total_sleep_minutes,
            ),
        )
    )

    return response.message


def check_short_tired_response() -> None:
    message = _response_message(
        quality_label="short",
        mood="tired",
        total_sleep_minutes=320,
    )

    _assert_contains(message, "Google Healthの実データ")
    _assert_contains(message, "5時間20分")
    _assert_contains(message, "睡眠評価は「短め」")
    _assert_contains(message, "気分も少し重そう")
    _assert_contains(message, "回復優先")
    _assert_contains(message, "予定の負荷も少し下げる")
    _assert_not_contains(message, "睡眠の回復感を活かしつつ")


def check_short_energetic_response() -> None:
    message = _response_message(
        quality_label="short",
        mood="energetic",
        total_sleep_minutes=320,
    )

    _assert_contains(message, "睡眠評価は「短め」")
    _assert_contains(message, "今は動けそう")
    _assert_contains(message, "後半に疲れが出るかもしれない")
    _assert_contains(message, "休憩も先に予定")
    _assert_not_contains(message, "回復優先")


def check_good_energetic_response() -> None:
    message = _response_message(
        quality_label="good",
        mood="energetic",
        total_sleep_minutes=490,
    )

    _assert_contains(message, "8時間10分")
    _assert_contains(message, "睡眠評価は「良好」")
    _assert_contains(message, "睡眠も気分も良さそう")
    _assert_contains(message, "大事なタスクを1つ")
    _assert_contains(message, "予定を詰め込みすぎず")


def check_good_tired_response() -> None:
    message = _response_message(
        quality_label="good",
        mood="tired",
        total_sleep_minutes=490,
    )

    _assert_contains(message, "睡眠評価は「良好」")
    _assert_contains(message, "今のだるさも大事")
    _assert_contains(message, "いきなり全力にせず")
    _assert_contains(message, "軽い準備運動")


def check_fair_tired_response() -> None:
    message = _response_message(
        quality_label="fair",
        mood="tired",
        total_sleep_minutes=410,
    )

    _assert_contains(message, "睡眠評価は「ふつう」")
    _assert_contains(message, "気分は少し重そう")
    _assert_contains(message, "無理に上げようとせず")
    _assert_contains(message, "休憩をはさむ")


def check_unavailable_gentle_tired_response() -> None:
    message = _response_message(
        quality_label="unavailable",
        mood="tired",
        available=False,
        character=_character(),
    )

    _assert_contains(message, "ミナです。")
    _assert_contains(message, "ごめんね")
    _assert_contains(message, "君の眠りを観測できなかった")
    _assert_contains(message, "今の気分「だるい」")
    _assert_contains(message, "軽めのタスクを1つ")
    _assert_not_contains(message, "0時間0分")
    _assert_not_contains(message, "Google Healthの実データ")


def check_unavailable_cheerful_energetic_response() -> None:
    message = _response_message(
        quality_label="unavailable",
        mood="energetic",
        available=False,
        character=_cheerful_character(),
    )

    _assert_contains(message, "ソラです。")
    _assert_contains(message, "ごめん")
    _assert_contains(message, "君の眠りをうまく見つけられなかった")
    _assert_contains(message, "今の気分「元気」")
    _assert_contains(message, "調子の良さを活かしつつ")
    _assert_contains(message, "休憩も先に入れて")
    _assert_not_contains(message, "0時間0分")
    _assert_not_contains(message, "Google Healthの実データ")


def check_unavailable_cool_tired_response() -> None:
    message = _response_message(
        quality_label="unavailable",
        mood="tired",
        available=False,
        character=_cool_character(),
    )

    _assert_contains(message, "レイです。")
    _assert_contains(message, "睡眠データを確認できませんでした")
    _assert_contains(message, "今の気分「だるい」")
    _assert_contains(message, "今日の負荷を少し下げ")
    _assert_contains(message, "小さなタスク")
    _assert_not_contains(message, "0時間0分")
    _assert_not_contains(message, "Google Healthの実データ")


def main() -> int:
    check_short_tired_response()
    check_short_energetic_response()
    check_good_energetic_response()
    check_good_tired_response()
    check_fair_tired_response()
    check_unavailable_gentle_tired_response()
    check_unavailable_cheerful_energetic_response()
    check_unavailable_cool_tired_response()
    print(f"[{SCRIPT_NAME}] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())