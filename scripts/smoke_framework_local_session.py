"""Optional smoke for a real local AI Character Framework checkout.

Default behavior:
- If FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is unset, print SKIP and succeed.
- If FRAMEWORK_ROOT is set, import the public ``framework`` package from that
  root, create a text chat session, and verify ``session.ask`` exists.
- With --ask, send a sample DRC advice request through
  FrameworkConversationEngine.create_advice(). This may call a real LLM provider
  depending on the configured framework route, so it is never run by default.

The check avoids printing prompts, API keys, or full model responses.
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


SMOKE_LABEL = "framework-local-session-smoke-v0.31.0"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Run a real session.ask call through create_advice().",
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
            "skipping real local framework session smoke."
        )
        if args.require_framework:
            print(f"[{SMOKE_LABEL}] FAIL: {message}")
            return 1

        print(f"[{SMOKE_LABEL}] SKIP: {message}")
        return 0

    _print_safe_config_summary(config=config, ask=args.ask)

    request = _build_sample_request()
    engine = FrameworkConversationEngine(config=config)

    try:
        original_cwd = Path.cwd()
        framework_character_name = engine._resolve_framework_character_name(  # noqa: SLF001
            request.character.character_id
        )
        session = engine._get_or_create_session(framework_character_name)  # noqa: SLF001

        if Path.cwd() != original_cwd:
            raise AssertionError("FrameworkConversationEngine did not restore cwd")

        if not hasattr(session, "ask") or not callable(session.ask):
            raise AssertionError("framework text session does not expose ask(text)")

        module_path = _framework_module_path()
        if module_path and not _is_relative_to(
            module_path,
            Path(config.framework_project_root).resolve(),
        ):
            raise AssertionError(
                "framework module was imported from an unexpected path: "
                f"{module_path}"
            )

        if args.ask:
            response = engine.create_advice(request)
            if not response.message.strip():
                raise AssertionError("real framework advice response was empty")
            print(
                f"[{SMOKE_LABEL}] OK: "
                "real local framework session.ask returned non-empty advice "
                f"({len(response.message)} chars)."
            )
            return 0

        print(
            f"[{SMOKE_LABEL}] OK: "
            "real local framework session was created and ask(text) is available. "
            "Pass --ask to perform a live FW/LLM advice call."
        )
        return 0

    except (AssertionError, FrameworkEngineError) as exc:
        print(f"[{SMOKE_LABEL}] FAIL: {_format_exception(exc)}")
        return 1
    except Exception as exc:  # pragma: no cover - defensive operator diagnostics.
        print(f"[{SMOKE_LABEL}] FAIL: unexpected {type(exc).__name__}: {exc}")
        return 1


def _format_exception(exc: BaseException) -> str:
    message = str(exc)
    cause = getattr(exc, "__cause__", None)
    if cause is None:
        return message

    cause_message = str(cause).strip()
    if not cause_message:
        cause_message = repr(cause)
    return f"{message} Cause: {type(cause).__name__}: {cause_message}"


def _load_framework_config() -> AppConfig:
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


def _print_safe_config_summary(*, config: AppConfig, ask: bool) -> None:
    """Print useful local FW smoke context without exposing secrets."""

    root = Path(config.framework_project_root or "").expanduser().resolve()
    print(f"[{SMOKE_LABEL}] framework_root={root}")
    print(f"[{SMOKE_LABEL}] framework_preset={config.framework_preset}")
    print(f"[{SMOKE_LABEL}] framework_character={config.framework_character}")
    print(f"[{SMOKE_LABEL}] framework_adapter_mode={config.framework_adapter_mode}")
    print(f"[{SMOKE_LABEL}] ask_enabled={ask}")


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
            date="2026-05-12",
            total_sleep_minutes=390,
            efficiency=88,
            deep_sleep_minutes=72,
            rem_sleep_minutes=90,
            awake_minutes=24,
            source="mock",
            available=True,
            sleep_start="2026-05-11T23:40:00+09:00",
            sleep_end="2026-05-12T06:34:00+09:00",
            quality_label="fair",
            confidence="mock",
            is_real_data=False,
        ),
        mood="normal",
    )


def _framework_module_path() -> Path | None:
    module = sys.modules.get("framework")
    if module is None:
        return None

    module_file = getattr(module, "__file__", None)
    if not module_file:
        return None

    try:
        return Path(module_file).resolve()
    except OSError:
        return None


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
