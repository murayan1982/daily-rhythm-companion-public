from pydantic import BaseModel


class SleepSummary(BaseModel):
    date: str
    total_sleep_minutes: int
    efficiency: int | None = None
    deep_sleep_minutes: int | None = None
    rem_sleep_minutes: int | None = None
    awake_minutes: int | None = None
    source: str = "mock"
    available: bool = True
    message: str | None = None

    # Real-provider normalized fields. These stay optional so existing mock and
    # legacy Fitbit responses remain compatible while Google Health dataPoints
    # normalization can expose useful app-facing metadata without leaking raw
    # provider payloads.
    sleep_start: str | None = None
    sleep_end: str | None = None
    quality_label: str | None = None
    confidence: str | None = None
    is_real_data: bool = False
    unavailable_reason: str | None = None