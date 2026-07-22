from typing import Literal

from pydantic import BaseModel, Field

from app.models.rhythm_report import (
    RhythmReportDataQuality,
    RhythmReportDataScope,
    RhythmReportPeriod,
    RhythmReportSourceLabel,
)


ReportHandoffAdviceBasisPrefix = Literal[
    "rhythm_report",
    "rhythm_report_partial",
    "none",
]


class ReportHandoffContext(BaseModel):
    """Small, conservative context distilled from a RhythmReport.

    This model is intentionally narrower than the full RhythmReport payload. It
    preserves source, scope, and data-quality labels while adding safe
    user-facing copy and prompt guidance. Report context is historical only and
    must not be treated as today's sleep result, diagnosis, treatment advice, or
    a medical score.
    """

    period: RhythmReportPeriod
    range_start: str
    range_end: str
    label: str
    display_summary: str
    action_hint: str
    source_label: RhythmReportSourceLabel
    data_scope: RhythmReportDataScope
    data_quality: RhythmReportDataQuality
    total_record_count: int = Field(..., ge=0)
    usable_sleep_record_count: int = Field(..., ge=0)
    is_medical_advice: bool = False
    should_inform_advice: bool = False
    advice_basis_prefix: ReportHandoffAdviceBasisPrefix = "none"
    user_facing_source_label: str
    user_facing_scope_label: str
    user_facing_quality_label: str
    user_facing_summary: str
    prompt_guidance: str
