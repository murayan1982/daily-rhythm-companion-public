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
    mood: str = "tired",
    advice_message: str = "今日は回復優先でいきましょう。",
) -> DailyRecordCreateRequest:
    return DailyRecordCreateRequest(
        date="2026-05-08",
        character_id="gentle_mina",
        character_name="ミナ",
        mood=mood,
        sleep_summary=SleepSummary(
            date="2026-05-08",
            total_sleep_minutes=330,
            efficiency=82,
            source="mock",
            available=True,
            quality_label="short",
            confidence="mock",
        ),
        advice_message=advice_message,
        advice_basis="sleep+mood+character",
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")

        saved = store.upsert(_build_record())

        _assert(saved.date == "2026-05-08", "saved record date mismatch")
        _assert(saved.character_id == "gentle_mina", "character_id mismatch")
        _assert(saved.sleep_summary.quality_label == "short", "sleep snapshot mismatch")
        _assert(saved.created_at, "created_at should be set")
        _assert(saved.updated_at, "updated_at should be set")

        updated = store.upsert(
            _build_record(
                mood="energetic",
                advice_message="動けそうだけど、飛ばしすぎには注意しよう。",
            )
        )

        _assert(updated.mood == "energetic", "upsert did not update mood")
        _assert(
            updated.advice_message == "動けそうだけど、飛ばしすぎには注意しよう。",
            "upsert did not update advice message",
        )
        _assert(
            updated.created_at == saved.created_at,
            "upsert should preserve created_at",
        )

        fetched = store.get("2026-05-08")
        _assert(fetched is not None, "saved record should be readable")
        _assert(fetched.mood == "energetic", "fetched record mismatch")

        missing = store.get("2099-01-01")
        _assert(missing is None, "missing record should return None")

        records = store.list_recent()
        _assert(len(records) == 1, "list_recent should return saved record")

    print("[daily-record-store-check-v0.27.0] OK")


if __name__ == "__main__":
    main()