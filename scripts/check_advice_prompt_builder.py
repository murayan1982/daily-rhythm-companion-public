from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.sleep import SleepSummary
from app.services.advice_prompt_builder import build_advice_prompt


SCRIPT_NAME = "advice-prompt-builder-check-v0.26.0"


def _character() -> CharacterContext:
    return CharacterContext(
        character_id="default",
        display_name="Default",
        personality_type="friendly",
        speaking_style="casual",
        advice_style="light",
    )


def _sleep_summary(
    *,
    quality_label: str,
    available: bool = True,
    total_sleep_minutes: int = 490,
    source: str = "google_health",
    is_real_data: bool = True,
    unavailable_reason: str | None = None,
    message: str | None = None,
) -> SleepSummary:
    if not available:
        return SleepSummary(
            date="2026-05-06",
            total_sleep_minutes=0,
            source=source,
            available=False,
            message=message or "Sleep data is unavailable.",
            unavailable_reason=unavailable_reason or "provider_permission_denied",
            quality_label=quality_label,
            confidence="low",
            is_real_data=False,
        )

    return SleepSummary(
        date="2026-05-06",
        total_sleep_minutes=total_sleep_minutes,
        source=source,
        available=True,
        sleep_start="2026-05-05T16:59:30Z",
        sleep_end="2026-05-06T01:09:30Z",
        quality_label=quality_label,
        confidence="medium",
        is_real_data=is_real_data,
    )


def _build_prompt(
    *,
    quality_label: str,
    mood: str,
    available: bool = True,
    total_sleep_minutes: int = 490,
) -> str:
    return build_advice_prompt(
        AdviceRequest(
            character=_character(),
            mood=mood,
            sleep=_sleep_summary(
                quality_label=quality_label,
                available=available,
                total_sleep_minutes=total_sleep_minutes,
            ),
        )
    )


def _assert_contains(text: str, expected: str) -> None:
    if expected not in text:
        raise AssertionError(f"Expected prompt to contain {expected!r}.")


def _assert_not_contains(text: str, unexpected: str) -> None:
    if unexpected in text:
        raise AssertionError(f"Prompt should not contain {unexpected!r}.")


def _assert_common_prompt_rules(prompt: str) -> None:
    _assert_contains(prompt, "Please give short, gentle, practical advice in Japanese.")
    _assert_contains(prompt, "without sounding medical")
    _assert_contains(prompt, "Do not sound diagnostic, clinical, or overly confident.")
    _assert_contains(prompt, "Keep it suitable for a morning companion app.")
    _assert_contains(prompt, "Follow the character's speaking style and advice style")
    _assert_contains(prompt, "Advice guidance:")


def check_real_sleep_prompt() -> None:
    prompt = _build_prompt(
        quality_label="good",
        mood="normal",
        available=True,
        total_sleep_minutes=490,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Source: google_health")
    _assert_contains(prompt, "Data kind: real provider data")
    _assert_contains(prompt, "Total sleep: 8h 10m")
    _assert_contains(prompt, "Sleep quality label: good")
    _assert_contains(prompt, "Confidence: medium")
    _assert_contains(prompt, "Advice should reflect total sleep")
    _assert_contains(prompt, "If real sleep data is available")


def check_unavailable_sleep_prompt() -> None:
    prompt = build_advice_prompt(
        AdviceRequest(
            character=_character(),
            mood="tired",
            sleep=_sleep_summary(
                quality_label="unavailable",
                available=False,
                unavailable_reason="provider_permission_denied",
                message="Sleep data is unavailable.",
            ),
        )
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Sleep data is unavailable today.")
    _assert_contains(prompt, "Unavailable reason: provider_permission_denied")
    _assert_contains(prompt, "Base the advice mainly on the user's mood.")
    _assert_contains(prompt, "Do not invent sleep details.")
    _assert_contains(prompt, "low-pressure advice")
    _assert_contains(prompt, "Do not tell the user to push harder.")
    _assert_not_contains(prompt, "Total sleep: 0h 0m")


def check_short_tired_guidance() -> None:
    prompt = _build_prompt(
        quality_label="short",
        mood="tired",
        available=True,
        total_sleep_minutes=320,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Sleep quality label: short")
    _assert_contains(prompt, "User mood: tired")
    _assert_contains(prompt, "The user had short sleep and feels tired.")
    _assert_contains(prompt, "low-pressure planning")
    _assert_contains(prompt, "small first steps")
    _assert_contains(prompt, "Do not tell the user to push harder.")
    _assert_contains(prompt, "Suggest reducing today's load where possible.")


def check_short_energetic_guidance() -> None:
    prompt = _build_prompt(
        quality_label="short",
        mood="energetic",
        available=True,
        total_sleep_minutes=320,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Sleep quality label: short")
    _assert_contains(prompt, "User mood: energetic")
    _assert_contains(prompt, "The user had short sleep but feels energetic.")
    _assert_contains(prompt, "Acknowledge the positive mood.")
    _assert_contains(prompt, "Gently warn against overdoing it.")
    _assert_contains(prompt, "planning breaks")
    _assert_contains(prompt, "Avoid suggesting an overloaded schedule.")


def check_good_tired_guidance() -> None:
    prompt = _build_prompt(
        quality_label="good",
        mood="tired",
        available=True,
        total_sleep_minutes=490,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Sleep quality label: good")
    _assert_contains(prompt, "User mood: tired")
    _assert_contains(prompt, "The user slept well but feels tired.")
    _assert_contains(prompt, "Respect the user's mood.")
    _assert_contains(prompt, "Do not imply they should feel energetic.")
    _assert_contains(prompt, "gentle warm-up")


def check_good_energetic_guidance() -> None:
    prompt = _build_prompt(
        quality_label="good",
        mood="energetic",
        available=True,
        total_sleep_minutes=490,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Sleep quality label: good")
    _assert_contains(prompt, "User mood: energetic")
    _assert_contains(prompt, "The user slept well and feels energetic.")
    _assert_contains(prompt, "one meaningful task")
    _assert_contains(prompt, "Avoid suggesting an overloaded schedule.")
    _assert_contains(prompt, "Encourage steady progress rather than doing everything at once.")


def check_fair_tired_guidance() -> None:
    prompt = _build_prompt(
        quality_label="fair",
        mood="tired",
        available=True,
        total_sleep_minutes=410,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "Sleep quality label: fair")
    _assert_contains(prompt, "User mood: tired")
    _assert_contains(prompt, "The sleep summary looks moderate, but the user feels tired.")
    _assert_contains(prompt, "Prioritize the user's current mood.")
    _assert_contains(prompt, "realistic workload")


def check_unknown_mood_keeps_stable_prompt() -> None:
    prompt = _build_prompt(
        quality_label="short",
        mood="sluggish",
        available=True,
        total_sleep_minutes=320,
    )

    _assert_common_prompt_rules(prompt)
    _assert_contains(prompt, "User mood: sluggish")
    _assert_contains(prompt, "The user had short sleep and feels normal.")
    _assert_contains(prompt, "Keep the day realistic.")


def main() -> int:
    check_real_sleep_prompt()
    check_unavailable_sleep_prompt()
    check_short_tired_guidance()
    check_short_energetic_guidance()
    check_good_tired_guidance()
    check_good_energetic_guidance()
    check_fair_tired_guidance()
    check_unknown_mood_keeps_stable_prompt()
    print(f"[{SCRIPT_NAME}] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())