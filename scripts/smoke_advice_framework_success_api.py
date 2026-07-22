"""Smoke check for the v0.31.0 /advice framework success path.

This smoke uses a temporary fake AI Character Framework package so it can prove
DRC's API wiring without requiring a local framework checkout or live LLM call.
It verifies:
- /advice can be routed through FrameworkConversationEngine.
- FrameworkConversationEngine calls session.ask(prompt).
- The prompt contains DRC sleep, mood, and character context.
- DailyRecord advice_basis is stored with +framework, not +framework_fallback.

No API keys, provider calls, or real framework dependencies are required.
"""

from __future__ import annotations

from contextlib import contextmanager
import importlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.config import AppConfig  # noqa: E402
from app.engines.factory import create_conversation_engine  # noqa: E402
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver  # noqa: E402
from app.services.daily_record_store import DailyRecordStore  # noqa: E402


SMOKE_DATE = "2026-05-11"
EXPECTED_MARKER = "[fake-framework-advice]"


def main() -> int:
    with TemporaryDirectory(prefix="drc_fake_framework_") as temp_dir:
        temp_path = Path(temp_dir)
        framework_root = temp_path / "fake_fw_root"
        db_path = temp_path / "daily_records.sqlite3"
        _write_fake_framework(framework_root)

        with _patched_advice_api(framework_root=framework_root, db_path=db_path):
            response_payload = _post_framework_advice()
            record = DailyRecordStore(db_path).get(SMOKE_DATE)

        _assert_framework_response(response_payload)
        _assert_framework_daily_record(record)

    print(
        "[advice-framework-success-api-smoke-v0.31.0] OK: "
        "/advice returned fake FW advice and saved advice_basis=...+framework."
    )
    return 0


def _write_fake_framework(framework_root: Path) -> None:
    framework_package = framework_root / "framework"
    framework_package.mkdir(parents=True)
    (framework_package / "facade.py").write_text(
        "\n".join(
            [
                "class FakeTextChatSession:",
                "    def ask(self, prompt):",
                "        required = (",
                "            'You are ミナ, a daily rhythm companion.',",
                "            'Character ID: gentle_mina',",
                "            'User sleep summary:',",
                "            'Total sleep: 6h 30m',",
                "            'User mood: tired',",
                "            'Please give short, gentle, practical advice in Japanese.',",
                "        )",
                "        missing = [fragment for fragment in required if fragment not in prompt]",
                "        if missing:",
                "            raise RuntimeError('missing prompt context: ' + ', '.join(missing))",
                "        return '[fake-framework-advice] ミナです。今日は少し負荷を下げて進めましょう。'",
                "",
                "def create_text_chat_session(*, preset, character_name):",
                "    if preset != 'text_chat':",
                "        raise RuntimeError('unexpected preset: ' + str(preset))",
                "    if character_name != 'default':",
                "        raise RuntimeError('unexpected character_name: ' + str(character_name))",
                "    return FakeTextChatSession()",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (framework_package / "__init__.py").write_text(
        "from .facade import create_text_chat_session\n",
        encoding="utf-8",
    )


@contextmanager
def _patched_advice_api(*, framework_root: Path, db_path: Path) -> Iterator[None]:
    """Patch app.api.advice globals so .env mock-safe values remain untouched."""

    import app.api.advice as advice_api

    config = AppConfig(
        conversation_engine="framework",
        framework_project_root=str(framework_root),
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        sleep_provider="mock",
    )

    previous_config = advice_api.config
    previous_conversation_engine = advice_api.conversation_engine
    previous_daily_record_saver = advice_api.daily_record_saver
    previous_framework_module = sys.modules.pop("framework", None)

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
        sys.modules.pop("framework", None)
        if previous_framework_module is not None:
            sys.modules["framework"] = previous_framework_module
        importlib.invalidate_caches()


def _post_framework_advice() -> dict[str, str]:
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
            "sleep_start": "2026-05-10T23:40:00+09:00",
            "sleep_end": "2026-05-11T06:34:00+09:00",
            "quality_label": "fair",
            "confidence": "mock",
            "is_real_data": False,
            "unavailable_reason": None,
        },
        "mood": "tired",
    }


def _assert_framework_response(payload: dict[str, str]) -> None:
    message = payload.get("message", "")
    character_name = payload.get("character_name", "")

    if EXPECTED_MARKER not in message:
        raise AssertionError(
            "framework success smoke did not receive the fake framework advice message"
        )

    if character_name != "ミナ":
        raise AssertionError(
            f"AdviceResponse.character_name changed unexpectedly: {character_name!r}"
        )


def _assert_framework_daily_record(record: object | None) -> None:
    if record is None:
        raise AssertionError("/advice did not auto-save a DailyRecord")

    advice_basis = getattr(record, "advice_basis", "")
    advice_message = getattr(record, "advice_message", "")

    if advice_basis != "sleep+mood+character+framework":
        raise AssertionError(
            f"DailyRecord.advice_basis was {advice_basis!r}, expected +framework"
        )

    if EXPECTED_MARKER not in advice_message:
        raise AssertionError("DailyRecord did not store the framework advice message")


if __name__ == "__main__":
    raise SystemExit(main())
