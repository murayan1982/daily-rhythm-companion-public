from pathlib import Path
from tempfile import TemporaryDirectory
import os
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Keep this smoke safe even when the local .env is incomplete.
os.environ.setdefault("CONVERSATION_ENGINE", "mock")
os.environ.setdefault("SLEEP_PROVIDER", "mock")


from fastapi.testclient import TestClient

from app.api import advice as advice_api
from app.config import AppConfig
from app.engines.mock_engine import MockConversationEngine
from app.main import app
from app.models.daily_record import DailyRecordCreateRequest
from app.models.sleep import SleepSummary
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver
from app.services.daily_record_store import DailyRecordStore
from app.services.recent_sleep_trend_service import RecentSleepTrendService


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")

        # Patch API-level singletons so this smoke is isolated and deterministic.
        advice_api.config = AppConfig(conversation_engine="mock", sleep_provider="mock")
        advice_api.conversation_engine = MockConversationEngine()
        advice_api.mock_conversation_engine = MockConversationEngine()
        advice_api.daily_record_saver = AdviceDailyRecordSaver(store)
        advice_api.recent_sleep_trend_service = RecentSleepTrendService(store)

        _save_record(store, "2026-05-06", 330)
        _save_record(store, "2026-05-07", 350)
        _save_record(store, "2026-05-08", 340)

        client = TestClient(app)

        unavailable_response = client.post(
            "/advice",
            json={
                "character": _character_payload(),
                "sleep": _unavailable_sleep_payload("2026-05-09"),
                "mood": "tired",
            },
        )

        assert unavailable_response.status_code == 200, unavailable_response.text

        unavailable_body = unavailable_response.json()
        unavailable_message = unavailable_body["message"]

        assert "最近の記録では、睡眠が短め" in unavailable_message
        assert "今の気分「だるい」" in unavailable_message

        unavailable_record = store.get("2026-05-09")
        assert unavailable_record is not None
        assert unavailable_record.sleep_summary.available is False
        assert (
            unavailable_record.advice_basis
            == "recent_sleep_trend+mood+character+mock"
        )

        available_response = client.post(
            "/advice",
            json={
                "character": _character_payload(),
                "sleep": {
                    "date": "2026-05-10",
                    "total_sleep_minutes": 420,
                    "quality_label": "good",
                    "available": True,
                },
                "mood": "normal",
            },
        )

        assert available_response.status_code == 200, available_response.text

        available_body = available_response.json()
        available_message = available_body["message"]

        assert "最近の記録では" not in available_message

        available_record = store.get("2026-05-10")
        assert available_record is not None
        assert available_record.sleep_summary.available is True
        assert available_record.advice_basis == "sleep+mood+character+mock"

    print("[advice-api-smoke-recent-sleep-trend-fallback-v0.30.0] OK")


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