"""Smoke check for the v0.31.0 framework-backed advice pipeline.

Default behavior:
- If FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is unset, the smoke prints SKIP and
  exits successfully so mock-safe local checks remain green.
- If framework config is present, the smoke prepares a FrameworkConversationEngine
  session and verifies that the framework text session exposes ask(text).
- With --ask, the smoke also sends a small DRC advice request through
  FrameworkConversationEngine.create_advice() and requires a non-empty response.

This script intentionally avoids printing prompts, raw provider payloads, API
keys, or full LLM responses.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig, load_config  # noqa: E402
from app.engines.errors import FrameworkEngineError  # noqa: E402
from app.engines.framework_engine import FrameworkConversationEngine  # noqa: E402
from app.models.advice import AdviceRequest  # noqa: E402
from app.models.character import CharacterContext  # noqa: E402
from app.models.sleep import SleepSummary  # noqa: E402
from app.services.advice_prompt_builder import build_advice_prompt  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Call session.ask through FrameworkConversationEngine.create_advice().",
    )
    parser.add_argument(
        "--require-framework",
        action="store_true",
        help="Fail instead of SKIP when FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is absent.",
    )
    args = parser.parse_args()

    config = _load_framework_config()
    if not config.framework_project_root:
        message = (
            "FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is unset; "
            "skipping optional framework advice pipeline smoke."
        )
        if args.require_framework:
            print(f"[framework-advice-pipeline-smoke] FAIL: {message}")
            return 1

        print(f"[framework-advice-pipeline-smoke] SKIP: {message}")
        return 0

    request = _build_sample_request()
    prompt = build_advice_prompt(request)
    _assert_prompt_contains_app_context(prompt)

    engine = FrameworkConversationEngine(config=config)

    try:
        framework_character_name = engine._resolve_framework_character_name(  # noqa: SLF001
            request.character.character_id
        )
        session = engine._get_or_create_session(framework_character_name)  # noqa: SLF001
        if not hasattr(session, "ask") or not callable(session.ask):
            raise AssertionError("framework text session does not expose ask(text)")

        if args.ask:
            response = engine.create_advice(request)
            if not response.message.strip():
                raise AssertionError("framework advice response message is empty")
            if response.character_name != request.character.display_name:
                raise AssertionError("AdviceResponse.character_name changed unexpectedly")

            print(
                "[framework-advice-pipeline-smoke] OK: "
                f"session.ask returned non-empty advice text ({len(response.message)} chars)."
            )
            return 0

        print(
            "[framework-advice-pipeline-smoke] OK: "
            "framework session prepared and ask(text) is available. "
            "Pass --ask to perform a live FW/LLM advice call."
        )
        return 0

    except (AssertionError, FrameworkEngineError) as exc:
        print(f"[framework-advice-pipeline-smoke] FAIL: {exc}")
        return 1


def _load_framework_config() -> AppConfig:
    """Load config and force framework mode for this smoke only."""

    config = load_config()
    framework_root = (
        config.framework_project_root
        or _empty_to_none(os.getenv("FRAMEWORK_ROOT"))
        or _empty_to_none(os.getenv("FRAMEWORK_PROJECT_ROOT"))
    )

    return AppConfig(
        conversation_engine="framework",
        framework_project_root=framework_root,
        framework_preset=config.framework_preset,
        framework_character=config.framework_character,
        framework_adapter_mode=config.framework_adapter_mode,
        gemini_api_key=config.gemini_api_key,
        xai_api_key=config.xai_api_key,
        sleep_provider=config.sleep_provider,
    )


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


def _build_sample_request() -> AdviceRequest:
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
            total_sleep_minutes=390,
            efficiency=88,
            deep_sleep_minutes=72,
            rem_sleep_minutes=90,
            awake_minutes=24,
            source="mock",
            available=True,
            sleep_start="2026-05-09T23:40:00+09:00",
            sleep_end="2026-05-10T06:34:00+09:00",
            quality_label="fair",
            confidence="mock",
            is_real_data=False,
        ),
        mood="normal",
    )


def _assert_prompt_contains_app_context(prompt: str) -> None:
    required_fragments = (
        "You are ミナ, a daily rhythm companion.",
        "Character ID: gentle_mina",
        "User sleep summary:",
        "User mood: normal",
        "Please give short, gentle, practical advice in Japanese.",
    )

    missing = [fragment for fragment in required_fragments if fragment not in prompt]
    if missing:
        raise AssertionError(
            "advice prompt is missing required app context: " + ", ".join(missing)
        )


if __name__ == "__main__":
    raise SystemExit(main())
