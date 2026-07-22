from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.models.advice import AdviceRequest, AdviceResponse
from app.models.character import CharacterContext
from app.models.sleep import SleepSummary
from app.services.advice_daily_record_saver import AdviceDailyRecordSaver
from app.services.daily_record_store import DailyRecordStore


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        store = DailyRecordStore(Path(temp_dir) / "daily_records.sqlite3")
        saver = AdviceDailyRecordSaver(store=store)

        request = AdviceRequest(
            character=CharacterContext(
                character_id="gentle_mina",
                display_name="ミナ",
                personality_type="gentle",
                speaking_style="casual",
                advice_style="rest_focused",
            ),
            sleep=SleepSummary(
                date="2026-05-08",
                total_sleep_minutes=330,
                efficiency=82,
                deep_sleep_minutes=None,
                rem_sleep_minutes=None,
                awake_minutes=None,
                source="mock",
                available=True,
                message="Mock sleep summary is available.",
                sleep_start=None,
                sleep_end=None,
                quality_label="short",
                confidence="mock",
                is_real_data=False,
                unavailable_reason=None,
            ),
            mood="tired",
        )

        response = AdviceResponse(
            message="今日は回復優先でいきましょう。",
            character_name="ミナ",
        )

        saved = saver.save(
            request=request,
            response=response,
        )

        _assert(saved.date == "2026-05-08", "saved date mismatch")
        _assert(saved.character_id == "gentle_mina", "character_id mismatch")
        _assert(saved.character_name == "ミナ", "character_name mismatch")
        _assert(saved.mood == "tired", "mood mismatch")
        _assert(saved.sleep_summary.quality_label == "short", "sleep snapshot mismatch")
        _assert(
            saved.advice_message == "今日は回復優先でいきましょう。",
            "advice message mismatch",
        )
        _assert(
            saved.advice_basis == "sleep+mood+character",
            "advice basis mismatch",
        )

        fetched = store.get("2026-05-08")
        _assert(fetched is not None, "daily record should be persisted")
        _assert(fetched.advice_message == response.message, "persisted advice mismatch")

    print("[advice-daily-record-flow-check-v0.27.0] OK")


if __name__ == "__main__":
    main()