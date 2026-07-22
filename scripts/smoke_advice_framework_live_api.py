"""Optional live /advice API smoke for the v0.31.0 framework pipeline.

This smoke validates the app-facing API path with a real local AI Character
Framework checkout:

/advice -> FrameworkConversationEngine -> real framework session.ask ->
AdviceResponse -> DailyRecord advice_basis=...+framework

It is intentionally opt-in. Without --ask it prints SKIP and succeeds. With
--ask it may call a real LLM provider through AI Character Framework, depending
on the configured framework route and API keys.

The check avoids printing API keys, prompts, or full model responses.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.config import AppConfig, load_config  # noqa: E402
from app.engines.factory import create_conversation_engine  # noqa: E402
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver  # noqa: E402
from app.services.daily_record_store import DailyRecordStore  # noqa: E402


SMOKE_LABEL = "advice-framework-live-api-smoke-v0.31.0"
SMOKE_DATE = "2026-05-13"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ask",
        action="store_true",
        help="Run a live /advice request through the real framework/LLM path.",
    )
    parser.add_argument(
        "--require-framework",
        action="store_true",
        help="Fail instead of SKIP when FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is absent.",
    )
    args = parser.parse_args()

    config = _load_live_framework_config()
    if not config.framework_project_root:
        message = (
            "FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is unset; "
            "skipping live /advice framework API smoke."
        )
        if args.require_framework:
            print(f"[{SMOKE_LABEL}] FAIL: {message}")
            return 1

        print(f"[{SMOKE_LABEL}] SKIP: {message}")
        return 0

    if not args.ask:
        _print_safe_config_summary(config=config, ask=False)
        print(
            f"[{SMOKE_LABEL}] SKIP: "
            "live /advice framework API call is opt-in; pass --ask to run it."
        )
        return 0

    _print_safe_config_summary(config=config, ask=True)

    with TemporaryDirectory(prefix="drc_live_framework_api_") as temp_dir:
        db_path = Path(temp_dir) / "daily_records.sqlite3"
        try:
            with _patched_advice_api(config=config, db_path=db_path):
                response_payload = _post_live_framework_advice()
                record = DailyRecordStore(db_path).get(SMOKE_DATE)

            _assert_live_framework_response(response_payload)
            _assert_live_framework_daily_record(record, response_payload)
        except Exception as exc:  # pragma: no cover - operator diagnostics.
            print(f"[{SMOKE_LABEL}] FAIL: {_format_exception(exc)}")
            return 1

    message_length = len(response_payload.get("message", ""))
    print(
        f"[{SMOKE_LABEL}] OK: "
        "live /advice returned non-empty FW advice "
        f"({message_length} chars) and saved advice_basis=...+framework."
    )
    return 0


@contextmanager
def _patched_advice_api(*, config: AppConfig, db_path: Path) -> Iterator[None]:
    """Patch app.api.advice globals so backend/.env mock-safe can stay intact."""

    import app.api.advice as advice_api

    previous_config = advice_api.config
    previous_conversation_engine = advice_api.conversation_engine
    previous_daily_record_saver = advice_api.daily_record_saver
    previous_framework_modules = _pop_framework_modules()

    advice_api.config = config
    advice_api.conversation_engine = create_conversation_engine(config)
    advice_api.daily_record_saver = AdviceDailyRecordSaver(
        store=DailyRecordStore(db_path)
    )

    try:
        yield
    finally:
        advice_api.config = previous_config
        advice_api.conversation_engine = previous_conversation_engine
        advice_api.daily_record_saver = previous_daily_record_saver
        _pop_framework_modules()
        sys.modules.update(previous_framework_modules)
        importlib.invalidate_caches()


def _pop_framework_modules() -> dict[str, object]:
    popped: dict[str, object] = {}
    for module_name in list(sys.modules):
        if module_name == "framework" or module_name.startswith("framework."):
            popped[module_name] = sys.modules.pop(module_name)
    return popped


def _post_live_framework_advice() -> dict[str, str]:
    from app.main import app

    client = TestClient(app)
    response = client.post("/advice", json=_sample_advice_payload())
    if response.status_code != 200:
        raise AssertionError(
            f"/advice returned unexpected status {response.status_code}: {response.text}"
        )

    payload = response.json()
    if not isinstance(payload, dict):
        raise AssertionError("/advice response was not a JSON object")

    return payload


def _sample_advice_payload() -> dict[str, object]:
    return {
        "character": {
            "character_id": "gentle_mina",
            "display_name": "ミナ",
            "personality_type": "gentle",
            "speaking_style": "casual",
            "advice_style": "rest_focused",
        },
        "sleep": {
            "date": SMOKE_DATE,
            "total_sleep_minutes": 390,
            "efficiency": 88,
            "deep_sleep_minutes": 72,
            "rem_sleep_minutes": 90,
            "awake_minutes": 24,
            "source": "mock",
            "available": True,
            "message": "Mock sleep summary is available.",
            "sleep_start": "2026-05-12T23:40:00+09:00",
            "sleep_end": "2026-05-13T06:34:00+09:00",
            "quality_label": "fair",
            "confidence": "mock",
            "is_real_data": False,
            "unavailable_reason": None,
        },
        "mood": "normal",
    }


def _assert_live_framework_response(payload: dict[str, str]) -> None:
    message = payload.get("message", "")
    character_name = payload.get("character_name", "")

    if not isinstance(message, str) or not message.strip():
        raise AssertionError("/advice returned an empty framework advice message")

    if character_name != "ミナ":
        raise AssertionError(
            f"AdviceResponse.character_name changed unexpectedly: {character_name!r}"
        )


def _assert_live_framework_daily_record(
    record: object | None,
    response_payload: dict[str, str],
) -> None:
    if record is None:
        raise AssertionError("/advice did not auto-save a DailyRecord")

    advice_basis = getattr(record, "advice_basis", "")
    advice_message = getattr(record, "advice_message", "")

    if advice_basis != "sleep+mood+character+framework":
        raise AssertionError(
            f"DailyRecord.advice_basis was {advice_basis!r}, expected +framework"
        )

    if advice_message != response_payload.get("message"):
        raise AssertionError("DailyRecord did not store the live framework advice message")


def _load_live_framework_config() -> AppConfig:
    loaded = load_config()
    framework_root = (
        _empty_to_none(os.getenv("FRAMEWORK_ROOT"))
        or _empty_to_none(os.getenv("FRAMEWORK_PROJECT_ROOT"))
        or loaded.framework_project_root
    )

    return AppConfig(
        conversation_engine="framework",
        framework_project_root=framework_root,
        framework_preset=_env_or_loaded("FRAMEWORK_PRESET", loaded.framework_preset),
        framework_character=_env_or_loaded(
            "FRAMEWORK_CHARACTER",
            loaded.framework_character,
        ),
        framework_adapter_mode=_env_or_loaded(
            "FRAMEWORK_ADAPTER_MODE",
            loaded.framework_adapter_mode,
        ),
        gemini_api_key=loaded.gemini_api_key,
        xai_api_key=loaded.xai_api_key,
        sleep_provider="mock",
    )


def _print_safe_config_summary(*, config: AppConfig, ask: bool) -> None:
    """Print useful local FW smoke context without exposing secrets."""

    root = Path(config.framework_project_root or "").expanduser().resolve()
    print(f"[{SMOKE_LABEL}] framework_root={root}")
    print(f"[{SMOKE_LABEL}] framework_preset={config.framework_preset}")
    print(f"[{SMOKE_LABEL}] framework_character={config.framework_character}")
    print(f"[{SMOKE_LABEL}] framework_adapter_mode={config.framework_adapter_mode}")
    print(f"[{SMOKE_LABEL}] ask_enabled={ask}")


def _format_exception(exc: BaseException) -> str:
    message = str(exc)
    cause = getattr(exc, "__cause__", None)
    if cause is None:
        return message

    cause_message = str(cause).strip()
    if not cause_message:
        cause_message = repr(cause)
    return f"{message} Cause: {type(cause).__name__}: {cause_message}"


def _env_or_loaded(name: str, loaded_value: str) -> str:
    return _empty_to_none(os.getenv(name)) or loaded_value


def _empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    raise SystemExit(main())
