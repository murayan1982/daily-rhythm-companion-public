from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.engines.mock_engine import MockConversationEngine
from app.models.advice import AdviceRequest
from app.models.character import CharacterContext
from app.models.daily_record import DailyRecordCreateRequest
from app.models.sleep import SleepSummary
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver
from app.services.advice_prompt_builder import build_advice_prompt
from app.services.daily_record_store import DailyRecordStore
from app.services.recent_sleep_trend_service import RecentSleepTrendService


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")
        trend_service = RecentSleepTrendService(store)

        _save_record(store, "2026-05-06", 330)
        _save_record(store, "2026-05-07", 350)
        _save_record(store, "2026-05-08", 340)

        request = AdviceRequest(
            character=CharacterContext(
                character_id="gentle_mina",
                display_name="ミナ",
                personality_type="gentle",
                speaking_style="casual",
                advice_style="rest_focused",
            ),
            sleep=_unavailable_sleep("2026-05-09"),
            mood="tired",
        )

        trend = trend_service.summarize_for_unavailable_today(
            current_sleep=request.sleep,
        )
        request_with_trend = request.model_copy(
            update={"recent_sleep_trend": trend},
        )

        prompt = build_advice_prompt(request_with_trend)
        assert "Recent sleep trend fallback:" in prompt
        assert "Label: recently_short" in prompt
        assert "historical context only" in prompt
        assert "Do not present it as today's sleep" in prompt

        response = MockConversationEngine().create_advice(request_with_trend)
        assert "最近の記録では、睡眠が短め" in response.message
        assert "今の気分「だるい」" in response.message

        saver = AdviceDailyRecordSaver(store)
        saved = saver.save(
            request=request_with_trend,
            response=response,
            advice_basis="recent_sleep_trend+mood+character",
        )

        assert saved.date == "2026-05-09"
        assert saved.advice_basis == "recent_sleep_trend+mood+character"

    print("[advice-recent-sleep-trend-context-check-v0.28.0] OK")


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
        )
    )


def _unavailable_sleep(date: str) -> SleepSummary:
    return SleepSummary(
        date=date,
        total_sleep_minutes=0,
        available=False,
        message="睡眠データを確認できませんでした。",
        unavailable_reason="mock_unavailable",
    )


if __name__ == "__main__":
    main()