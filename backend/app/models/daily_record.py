from pydantic import BaseModel, Field

from app.models.advice import AdviceSource
from app.models.sleep import SleepSummary


class DailyRecordCreateRequest(BaseModel):
    date: str = Field(..., min_length=1)
    character_id: str = Field(..., min_length=1)
    character_name: str = Field(..., min_length=1)
    mood: str = Field(..., min_length=1)
    sleep_summary: SleepSummary
    advice_message: str = Field(..., min_length=1)
    advice_basis: str = "sleep+mood+character"
    advice_source: AdviceSource | None = None


class DailyRecordResponse(DailyRecordCreateRequest):
    created_at: str
    updated_at: str
