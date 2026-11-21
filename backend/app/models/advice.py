from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.models.character import CharacterContext
from app.models.recent_sleep_trend import RecentSleepTrend
from app.models.report_handoff import ReportHandoffContext
from app.models.sleep import SleepSummary


AdviceMood = Literal["energetic", "normal", "tired"]
AdviceCharacterId = Literal["gentle_mina", "cheerful_sora", "cool_rei"]
AdviceMessage = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)]


class PublicAdviceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    mood: AdviceMood
    character_id: AdviceCharacterId


class PublicAdviceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    message: AdviceMessage


class PublicAdviceProblem(BaseModel):
    detail: Literal[
        "invalid_request",
        "authentication_required",
        "user_quota_exceeded",
        "global_quota_exceeded",
        "upstream_failure",
        "advice_unavailable",
    ]


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
