from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.models.daily_record import DailyRecordCreateRequest
from app.models.sleep import SleepSummary
from app.services.daily_record_store import DailyRecordStore
from app.services.recent_sleep_trend_service import RecentSleepTrendService

def main() -> None:
    with TemporaryDirectory() as temp_dir:
        store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")
        service = RecentSleepTrendService(store)

        _save_record(store, "2026-05-06", 330)
        _save_record(store, "2026-05-07", 350)
        _save_record(store, "2026-05-08", 340)

        trend = service.summarize_for_unavailable_today(
            current_sleep=_unavailable_sleep("2026-05-09"),
        )

        assert trend.label == "recently_short"
        assert trend.usable_record_count == 3
        assert trend.average_total_sleep_minutes == 340
        assert trend.recent_dates == ["2026-05-08", "2026-05-07", "2026-05-06"]

        insufficient = service.summarize_for_unavailable_today(
            current_sleep=_unavailable_sleep("2026-05-05"),
        )

        assert insufficient.label == "insufficient_data"
        assert insufficient.usable_record_count == 0
        assert insufficient.average_total_sleep_minutes is None

        not_used = service.summarize_for_unavailable_today(
            current_sleep=SleepSummary(
                date="2026-05-09",
                total_sleep_minutes=420,
                quality_label="good",
                available=True,
            ),
        )

        assert not_used.label == "insufficient_data"
        assert not_used.usable_record_count == 0

    print("[recent-sleep-trend-check-v0.28.0] OK")


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