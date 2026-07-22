import json
import sqlite3
from datetime import date as Date, datetime, timedelta, timezone
from pathlib import Path
from collections.abc import Iterator
from contextlib import contextmanager

from app.models.advice import AdviceSource
from app.models.daily_record import (
    DailyRecordCreateRequest,
    DailyRecordResponse,
)
from app.models.sleep import SleepSummary


DEFAULT_DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "local_data"
    / "daily_records.sqlite3"
)


class DailyRecordStore:
    """Persist app-facing daily snapshots for history and future trend fallback."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def upsert(self, request: DailyRecordCreateRequest) -> DailyRecordResponse:
        now = _utc_now()

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT created_at FROM daily_records WHERE date = ?",
                (request.date,),
            ).fetchone()

            created_at = existing["created_at"] if existing else now

            connection.execute(
                """
                INSERT INTO daily_records (
                    date,
                    character_id,
                    character_name,
                    mood,
                    sleep_summary_json,
                    advice_message,
                    advice_basis,
                    advice_source_json,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    character_id = excluded.character_id,
                    character_name = excluded.character_name,
                    mood = excluded.mood,
                    sleep_summary_json = excluded.sleep_summary_json,
                    advice_message = excluded.advice_message,
                    advice_basis = excluded.advice_basis,
                    advice_source_json = excluded.advice_source_json,
                    updated_at = excluded.updated_at
                """,
                (
                    request.date,
                    request.character_id,
                    request.character_name,
                    request.mood,
                    json.dumps(
                        request.sleep_summary.model_dump(mode="json"),
                        ensure_ascii=False,
                    ),
                    request.advice_message,
                    request.advice_basis,
                    _dump_advice_source(request.advice_source),
                    created_at,
                    now,
                ),
            )

        record = self.get(request.date)
        if record is None:
            raise RuntimeError("Daily record upsert did not create a record.")

        return record

    def get(self, date: str) -> DailyRecordResponse | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM daily_records WHERE date = ?",
                (date,),
            ).fetchone()

        if row is None:
            return None

        return _row_to_daily_record(row)

    def list_recent(self, limit: int = 30) -> list[DailyRecordResponse]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM daily_records
                ORDER BY date DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [_row_to_daily_record(row) for row in rows]

    def list_recent_sleep_available_records(
        self,
        *,
        reference_date: str,
        days: int = 7,
        limit: int = 7,
    ) -> list[DailyRecordResponse]:
        """Return recent records with usable sleep data for future trend fallback."""

        if days < 1:
            raise ValueError("days must be greater than or equal to 1.")

        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1.")

        end_date = Date.fromisoformat(reference_date)
        start_date = end_date - timedelta(days=days - 1)

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM daily_records
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            ).fetchall()

        records = [_row_to_daily_record(row) for row in rows]

        return [
            record
            for record in records
            if record.sleep_summary.available
            and (record.sleep_summary.total_sleep_minutes or 0) > 0
        ][:limit]

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_records (
                    date TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    character_name TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    sleep_summary_json TEXT NOT NULL,
                    advice_message TEXT NOT NULL,
                    advice_basis TEXT NOT NULL,
                    advice_source_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            column_names = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(daily_records)")
            }
            if "advice_source_json" not in column_names:
                connection.execute(
                    "ALTER TABLE daily_records ADD COLUMN advice_source_json TEXT"
                )


def _row_to_daily_record(row: sqlite3.Row) -> DailyRecordResponse:
    return DailyRecordResponse(
        date=row["date"],
        character_id=row["character_id"],
        character_name=row["character_name"],
        mood=row["mood"],
        sleep_summary=SleepSummary(**json.loads(row["sleep_summary_json"])),
        advice_message=row["advice_message"],
        advice_basis=row["advice_basis"],
        advice_source=_load_advice_source(row),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _dump_advice_source(advice_source: AdviceSource | None) -> str | None:
    if advice_source is None:
        return None

    return json.dumps(advice_source.model_dump(mode="json"), ensure_ascii=False)


def _load_advice_source(row: sqlite3.Row) -> AdviceSource | None:
    if "advice_source_json" not in row.keys():
        return None

    value = row["advice_source_json"]
    if not value:
        return None

    try:
        return AdviceSource(**json.loads(value))
    except (TypeError, ValueError):
        return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
