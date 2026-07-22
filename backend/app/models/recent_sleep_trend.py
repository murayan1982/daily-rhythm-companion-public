from typing import Literal

from pydantic import BaseModel, Field


RecentSleepTrendLabel = Literal[
    "recently_short",
    "recently_stable",
    "recently_good",
    "insufficient_data",
]


class RecentSleepTrend(BaseModel):
    """
    Summarized recent sleep trend for app-facing history context.

    This model is intentionally framed as historical/reference context. It must
    not be used to present recent records as today's sleep result.
    """

    reference_date: str
    days: int
    label: RecentSleepTrendLabel
    usable_record_count: int
    average_total_sleep_minutes: int | None = None
    recent_dates: list[str] = Field(default_factory=list)
    message: str
    display_label: str = "傾向はまだ参考程度"
    display_summary: str = "もう少し記録が増えると、直近傾向を表示できます。"
    display_note: str = "履歴から見た参考情報です。今日の睡眠としては扱いません。"
    data_scope: str = "recent_history"
    is_fallback_context: bool = True
