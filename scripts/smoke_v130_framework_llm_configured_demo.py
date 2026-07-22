"""Configured-only AI Character Framework / LLM smoke for v1.3.0 Day3.

Default behavior is safe for public/local source-tree checks:
- If FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is unset, print SKIP and exit 0.
- If a framework root is configured, verify the public framework import boundary.
- With --create-session, create a text chat session but do not call ask().
- With --ask, call the advice path only when an explicit LLM smoke gate and a
  provider key are present.

The script avoids printing provider keys, raw prompts, raw provider payloads,
full model responses, authorization headers, token values, or private local
paths.
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

SMOKE_LABEL = "v130-framework-llm-configured-smoke"
LLM_SMOKE_GATE = "DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE"
PROVIDER_KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "XAI_API_KEY")


class SmokeSkip(Exception):
    """Raised when the configured-only smoke should report SKIP."""


class SmokeFail(Exception):
    """Raised when a required configured smoke condition fails."""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run a configured-only AI Character Framework smoke. "
            "Unset configuration is reported as SKIP unless require flags are used."
        )
    )
    parser.add_argument(
        "--create-session",
        action="store_true",
        help="Create a framework text chat session without calling ask().",
    )
    parser.add_argument(
        "--ask",
        action="store_true",
        help=(
            "Run the advice path and call session.ask(). Requires "
            f"{LLM_SMOKE_GATE}=1 and a provider key."
        ),
    )
    parser.add_argument(
        "--require-framework",
        action="store_true",
        help="Fail instead of SKIP when FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is missing.",
    )
    parser.add_argument(
        "--require-llm",
        action="store_true",
        help="Fail instead of SKIP when the explicit LLM smoke gate/provider key is missing.",
    )
    parser.add_argument(
        "--ignore-dotenv",
        action="store_true",
        help="Read only process environment variables. Used by source-tree fixture checks.",
    )
    args = parser.parse_args()

    try:
        config = _load_smoke_config(ignore_dotenv=args.ignore_dotenv)
        _require_framework_root(config=config, require_framework=args.require_framework)
        engine = FrameworkConversationEngine(config=config)
        original_cwd = Path.cwd()

        if args.ask:
            _require_llm_gate(require_llm=args.require_llm)
            request = _build_sample_request()
            response = engine.create_advice(request)
            if Path.cwd() != original_cwd:
                raise SmokeFail("Framework smoke did not restore the current working directory.")
            if not response.message.strip():
                raise SmokeFail("Configured FW/LLM advice response was empty.")
            if response.source.engine != "framework":
                raise SmokeFail(
                    "Configured FW/LLM advice source was not framework: "
                    f"{response.source.engine}"
                )
            print(
                f"[{SMOKE_LABEL}] OK: configured FW/LLM advice returned "
                f"non-empty text ({len(response.message)} chars)."
            )
            return 0

        if args.create_session:
            session = engine._get_or_create_session(config.framework_character)  # noqa: SLF001
            if Path.cwd() != original_cwd:
                raise SmokeFail("Framework smoke did not restore the current working directory.")
            if not hasattr(session, "ask") or not callable(session.ask):
                raise SmokeFail("framework text session does not expose ask(text).")
            print(
                f"[{SMOKE_LABEL}] OK: framework text session was created; "
                "session.ask() was not called."
            )
            return 0

        framework_root = Path(config.framework_project_root or "").expanduser().resolve()
        create_text_chat_session = engine._load_framework_facade(framework_root)  # noqa: SLF001
        if not callable(create_text_chat_session):
            raise SmokeFail("framework.create_text_chat_session is not callable.")
        print(
            f"[{SMOKE_LABEL}] OK: framework public facade is importable; "
            "session was not created and ask() was not called."
        )
        return 0

    except SmokeSkip as exc:
        print(f"[{SMOKE_LABEL}] SKIP: {exc}")
        return 0
    except (SmokeFail, FrameworkEngineError, AssertionError) as exc:
        print(f"[{SMOKE_LABEL}] FAIL: {_safe_exception_message(exc)}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive operator diagnostics.
        print(
            f"[{SMOKE_LABEL}] FAIL: unexpected {type(exc).__name__}: "
            f"{_safe_exception_message(exc)}",
            file=sys.stderr,
        )
        return 1


def _load_smoke_config(*, ignore_dotenv: bool) -> AppConfig:
    if ignore_dotenv:
        framework_root = _empty_to_none(
            os.getenv("FRAMEWORK_PROJECT_ROOT") or os.getenv("FRAMEWORK_ROOT")
        )
        gemini_or_google_key = _empty_to_none(
            os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        )
        return AppConfig(
            conversation_engine="framework",
            framework_project_root=framework_root,
            framework_preset=os.getenv("FRAMEWORK_PRESET", "text_chat").strip()
            or "text_chat",
            framework_character=os.getenv("FRAMEWORK_CHARACTER", "default").strip()
            or "default",
            framework_adapter_mode=os.getenv(
                "FRAMEWORK_ADAPTER_MODE",
                "local_import",
            ).strip().lower()
            or "local_import",
            gemini_api_key=gemini_or_google_key,
            xai_api_key=_empty_to_none(os.getenv("XAI_API_KEY")),
            sleep_provider=os.getenv("SLEEP_PROVIDER", "mock").strip().lower() or "mock",
        )

    loaded = load_config()
    framework_root = (
        loaded.framework_project_root
        or _empty_to_none(os.getenv("FRAMEWORK_ROOT"))
        or _empty_to_none(os.getenv("FRAMEWORK_PROJECT_ROOT"))
    )
    gemini_or_google_key = loaded.gemini_api_key or _empty_to_none(
        os.getenv("GOOGLE_API_KEY")
    )
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=framework_root,
        framework_preset=loaded.framework_preset,
        framework_character=loaded.framework_character,
        framework_adapter_mode=loaded.framework_adapter_mode,
        gemini_api_key=gemini_or_google_key,
        xai_api_key=loaded.xai_api_key,
        sleep_provider=loaded.sleep_provider,
    )


def _require_framework_root(*, config: AppConfig, require_framework: bool) -> None:
    if config.framework_project_root:
        return

    message = "FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is not configured."
    if require_framework:
        raise SmokeFail(message)
    raise SmokeSkip(message)


def _require_llm_gate(*, require_llm: bool) -> None:
    gate_enabled = os.getenv(LLM_SMOKE_GATE, "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    has_provider_key = any(_empty_to_none(os.getenv(name)) for name in PROVIDER_KEY_NAMES)

    if gate_enabled and has_provider_key:
        return

    missing: list[str] = []
    if not gate_enabled:
        missing.append(f"{LLM_SMOKE_GATE}=1")
    if not has_provider_key:
        missing.append("one provider key")

    message = (
        "Configured FW/LLM ask smoke requires explicit opt-in: "
        + ", ".join(missing)
        + "."
    )
    if require_llm:
        raise SmokeFail(message)
    raise SmokeSkip(message)


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
            date="2026-05-21",
            total_sleep_minutes=390,
            efficiency=88,
            deep_sleep_minutes=72,
            rem_sleep_minutes=90,
            awake_minutes=24,
            source="mock",
            available=True,
            sleep_start="2026-05-20T23:40:00+09:00",
            sleep_end="2026-05-21T06:34:00+09:00",
            quality_label="fair",
            confidence="mock",
            is_real_data=False,
        ),
        mood="normal",
    )


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


def _safe_exception_message(exc: BaseException) -> str:
    """Return a concise message without provider values or local path expansion."""

    message = str(exc).strip() or type(exc).__name__
    cause = getattr(exc, "__cause__", None)
    if cause is not None:
        cause_message = str(cause).strip() or type(cause).__name__
        message = f"{message} Cause: {type(cause).__name__}: {cause_message}"

    for key_name in PROVIDER_KEY_NAMES:
        value = os.getenv(key_name)
        if value:
            message = message.replace(value, "<redacted-provider-key>")
    return message


if __name__ == "__main__":
    raise SystemExit(main())
