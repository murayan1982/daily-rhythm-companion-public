"""SQLite DailyRecord regression tests using only temporary test data."""

from __future__ import annotations

from app.models.advice import AdviceSource
from app.models.daily_record import DailyRecordCreateRequest
from app.models.sleep import SleepSummary
from app.services.daily_record_store import DailyRecordStore


def _request(*, message: str, mood: str = "normal") -> DailyRecordCreateRequest:
    return DailyRecordCreateRequest(
        date="2026-07-22",
        character_id="gentle_mina",
        character_name="ミナ",
        mood=mood,
        sleep_summary=SleepSummary(
            date="2026-07-22",
            total_sleep_minutes=390,
            efficiency=84,
            source="mock",
            available=True,
        ),
        advice_message=message,
        advice_basis="sleep+mood+character+mock",
        advice_source=AdviceSource(
            engine="mock",
            drc_character_id="gentle_mina",
            drc_character_name="ミナ",
        ),
    )


def test_daily_record_store_upserts_and_reads_from_temporary_database(tmp_path) -> None:
    store = DailyRecordStore(tmp_path / "daily_records.sqlite3")

    created = store.upsert(_request(message="最初のアドバイス"))
    loaded = store.get("2026-07-22")

    assert loaded is not None
    assert loaded.model_dump() == created.model_dump()
    assert loaded.advice_source is not None
    assert loaded.advice_source.engine == "mock"

    updated = store.upsert(_request(message="更新後のアドバイス", mood="tired"))

    assert updated.created_at == created.created_at
    assert updated.advice_message == "更新後のアドバイス"
    assert updated.mood == "tired"
    assert len(store.list_recent(limit=30)) == 1
