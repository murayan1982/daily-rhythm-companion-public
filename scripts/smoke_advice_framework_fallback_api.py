from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Keep this smoke safe even when the local .env is incomplete or framework mode
# is not configured for normal development.
os.environ.setdefault("CONVERSATION_ENGINE", "mock")
os.environ.setdefault("SLEEP_PROVIDER", "mock")

from fastapi.testclient import TestClient

from app.api import advice as advice_api
from app.config import AppConfig
from app.engines.framework_engine import FrameworkConversationEngine
from app.engines.mock_engine import MockConversationEngine
from app.main import app
from app.models.daily_record import DailyRecordCreateRequest
from app.models.sleep import SleepSummary
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver
from app.services.daily_record_store import DailyRecordStore
from app.services.recent_sleep_trend_service import RecentSleepTrendService


def main() -> None:
    original_config = advice_api.config
    original_conversation_engine = advice_api.conversation_engine
    original_mock_conversation_engine = advice_api.mock_conversation_engine
    original_daily_record_saver = advice_api.daily_record_saver
    original_recent_sleep_trend_service = advice_api.recent_sleep_trend_service

    try:
        with TemporaryDirectory() as temp_dir:
            store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")
            framework_config = AppConfig(
                conversation_engine="framework",
                framework_project_root=None,
                framework_preset="text_chat",
                framework_character="default",
                sleep_provider="mock",
            )

            # Patch API-level singletons so this smoke proves the public /advice
            # path falls back safely when framework mode is selected but local
            # framework configuration is unavailable.
            advice_api.config = framework_config
            advice_api.conversation_engine = FrameworkConversationEngine(
                framework_config
            )
            advice_api.mock_conversation_engine = MockConversationEngine()
            advice_api.daily_record_saver = AdviceDailyRecordSaver(store)
            advice_api.recent_sleep_trend_service = RecentSleepTrendService(store)

            client = TestClient(app)

            _check_available_sleep_framework_fallback(client, store)
            _check_recent_trend_framework_fallback(client, store)
    finally:
        advice_api.config = original_config
        advice_api.conversation_engine = original_conversation_engine
        advice_api.mock_conversation_engine = original_mock_conversation_engine
        advice_api.daily_record_saver = original_daily_record_saver
        advice_api.recent_sleep_trend_service = original_recent_sleep_trend_service

    print("[advice-framework-fallback-api-smoke-v0.30.0] OK")


def _check_available_sleep_framework_fallback(
    client: TestClient,
    store: DailyRecordStore,
) -> None:
    response = client.post(
        "/advice",
        json={
            "character": _character_payload(),
            "sleep": {
                "date": "2026-05-11",
                "total_sleep_minutes": 420,
                "quality_label": "good",
                "available": True,
            },
            "mood": "normal",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body["character_name"] == "ミナ"
    assert body["message"]

    record = store.get("2026-05-11")
    assert record is not None
    assert record.sleep_summary.available is True
    assert record.advice_basis == "sleep+mood+character+framework_fallback"


def _check_recent_trend_framework_fallback(
    client: TestClient,
    store: DailyRecordStore,
) -> None:
    _save_record(store, "2026-05-06", 330)
    _save_record(store, "2026-05-07", 350)
    _save_record(store, "2026-05-08", 340)

    response = client.post(
        "/advice",
        json={
            "character": _character_payload(),
            "sleep": _unavailable_sleep_payload("2026-05-09"),
            "mood": "tired",
        },
    )

    assert response.status_code == 200, response.text

    body = response.json()
    assert body["character_name"] == "ミナ"
    assert "最近の記録では、睡眠が短め" in body["message"]

    record = store.get("2026-05-09")
    assert record is not None
    assert record.sleep_summary.available is False
    assert (
        record.advice_basis
        == "recent_sleep_trend+mood+character+framework_fallback"
    )


def _save_record(store: DailyRecordStore, date: str, total_sleep_minutes: int) -> None:
    store.upsert(
        DailyRecordCreateRequest(
            date=date,
            character_id="gentle_mina",
            character_name="ミナ",
            mood="normal",
            sleep_summary=SleepSummary(
                date=date,
                total_sleep_minutes=total_sleep_minutes,
                quality_label="short" if total_sleep_minutes < 360 else "fair",
                available=True,
            ),
            advice_message="今日も無理せずいこうね。",
            advice_basis="sleep+mood+character+mock",
        )
    )


def _character_payload() -> dict:
    return {
        "character_id": "gentle_mina",
        "display_name": "ミナ",
        "personality_type": "gentle",
        "speaking_style": "casual",
        "advice_style": "rest_focused",
    }


def _unavailable_sleep_payload(date: str) -> dict:
    return {
        "date": date,
        "total_sleep_minutes": 0,
        "available": False,
        "message": "睡眠データを確認できませんでした。",
        "unavailable_reason": "mock_unavailable",
    }


if __name__ == "__main__":
    main()
