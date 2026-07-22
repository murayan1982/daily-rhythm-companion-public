from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.models.daily_record import DailyRecordCreateRequest
from app.models.sleep import SleepSummary
from app.services.daily_record_store import DailyRecordStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _build_record(
    *,
    date: str,
    available: bool,
    total_sleep_minutes: int,
    quality_label: str | None,
) -> DailyRecordCreateRequest:
    return DailyRecordCreateRequest(
        date=date,
        character_id="gentle_mina",
        character_name="ミナ",
        mood="tired",
        sleep_summary=SleepSummary(
            date=date,
            total_sleep_minutes=total_sleep_minutes,
            efficiency=82 if available else None,
            deep_sleep_minutes=None,
            rem_sleep_minutes=None,
            awake_minutes=None,
            source="mock",
            available=available,
            message=(
                "Mock sleep summary is available."
                if available
                else "Sleep data is unavailable."
            ),
            sleep_start=None,
            sleep_end=None,
            quality_label=quality_label,
            confidence="mock" if available else "none",
            is_real_data=False,
            unavailable_reason=None if available else "smoke_unavailable",
        ),
        advice_message="今日は回復優先でいきましょう。",
        advice_basis="sleep+mood+character",
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")

        store.upsert(
            _build_record(
                date="2026-05-08",
                available=True,
                total_sleep_minutes=330,
                quality_label="short",
            )
        )
        store.upsert(
            _build_record(
                date="2026-05-07",
                available=False,
                total_sleep_minutes=0,
                quality_label="unavailable",
            )
        )
        store.upsert(
            _build_record(
                date="2026-05-06",
                available=True,
                total_sleep_minutes=490,
                quality_label="good",
            )
        )
        store.upsert(
            _build_record(
                date="2026-04-28",
                available=True,
                total_sleep_minutes=360,
                quality_label="fair",
            )
        )

        records = store.list_recent_sleep_available_records(
            reference_date="2026-05-08",
            days=7,
        )

        _assert(
            [record.date for record in records] == ["2026-05-08", "2026-05-06"],
            "recent available sleep records should exclude unavailable and old data",
        )
        _assert(
            records[0].sleep_summary.quality_label == "short",
            "newest sleep record should be first",
        )

        limited_records = store.list_recent_sleep_available_records(
            reference_date="2026-05-08",
            days=7,
            limit=1,
        )

        _assert(len(limited_records) == 1, "limit should be respected")
        _assert(
            limited_records[0].date == "2026-05-08",
            "limited result should keep newest record",
        )

    print("[daily-record-history-query-check-v0.27.0] OK")


if __name__ == "__main__":
    main()