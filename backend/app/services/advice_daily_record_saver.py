from app.models.advice import AdviceRequest, AdviceResponse
from app.models.daily_record import DailyRecordCreateRequest, DailyRecordResponse
from app.services.daily_record_store import DailyRecordStore


class AdviceDailyRecordSaver:
    """Save generated advice as a daily snapshot for history and trend fallback."""

    def __init__(self, store: DailyRecordStore | None = None) -> None:
        self.store = store or DailyRecordStore()

    def save(
        self,
        *,
        request: AdviceRequest,
        response: AdviceResponse,
        advice_basis: str = "sleep+mood+character",
    ) -> DailyRecordResponse:
        daily_record = DailyRecordCreateRequest(
            date=request.sleep.date,
            character_id=request.character.character_id,
            character_name=response.character_name,
            mood=request.mood,
            sleep_summary=request.sleep,
            advice_message=response.message,
            advice_basis=advice_basis,
            advice_source=response.source,
        )

        return self.store.upsert(daily_record)
