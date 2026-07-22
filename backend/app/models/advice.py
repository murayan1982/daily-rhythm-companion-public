from pydantic import BaseModel

from app.models.character import CharacterContext
from app.models.recent_sleep_trend import RecentSleepTrend
from app.models.report_handoff import ReportHandoffContext
from app.models.sleep import SleepSummary


class AdviceRequest(BaseModel):
    character: CharacterContext
    sleep: SleepSummary
    mood: str
    recent_sleep_trend: RecentSleepTrend | None = None
    report_handoff: ReportHandoffContext | None = None


class AdviceSource(BaseModel):
    """App-facing metadata describing how an advice message was generated."""

    engine: str
    drc_character_id: str
    drc_character_name: str
    framework_preset: str | None = None
    framework_character: str | None = None
    framework_character_source: str | None = None
    report_handoff: ReportHandoffContext | None = None


class AdviceResponse(BaseModel):
    message: str
    character_name: str
    source: AdviceSource | None = None
