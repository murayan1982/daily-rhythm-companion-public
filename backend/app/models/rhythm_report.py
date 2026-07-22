from typing import Literal

from pydantic import BaseModel, Field


RhythmReportPeriod = Literal["weekly", "monthly"]
RhythmReportSourceLabel = Literal[
    "saved_daily_record_history",
    "saved_daily_record_history_with_mock_sleep",
    "saved_daily_record_history_with_real_sleep",
    "insufficient_saved_history",
]
RhythmReportDataQuality = Literal["insufficient", "partial", "usable"]
RhythmReportDataScope = Literal["weekly_history", "monthly_history"]
RhythmReportLabel = Literal[
    "insufficient_data",
    "weekly_short",
    "weekly_balanced",
    "weekly_enough",
    "monthly_sparse",
    "monthly_mixed",
    "monthly_stable",
    "monthly_enough",
]


class RhythmReport(BaseModel):
    """Lightweight weekly/monthly reflection built from saved DailyRecords.

    This model is intentionally historical and conservative. It summarizes saved
    records for reflection and must not be presented as today's sleep result,
    diagnosis, treatment advice, or a medical score.
    """

    period: RhythmReportPeriod
    reference_date: str
    range_start: str
    range_end: str
    days: int
    label: RhythmReportLabel
    total_record_count: int
    usable_sleep_record_count: int
    average_total_sleep_minutes: int | None = None
    record_dates: list[str] = Field(default_factory=list)
    display_title: str
    display_label: str
    display_summary: str
    display_coverage: str
    display_note: str = (
        "過去のDailyRecordから作る軽い振り返りです。"
        "今日の睡眠や健康状態の診断には使いません。"
    )
    action_hint: str
    source_label: RhythmReportSourceLabel
    data_scope: RhythmReportDataScope
    data_quality: RhythmReportDataQuality
    is_medical_advice: bool = False
