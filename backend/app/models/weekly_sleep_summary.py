from typing import Literal

from pydantic import BaseModel, Field


WeeklySleepSummaryLabel = Literal[
    "weekly_short",
    "weekly_balanced",
    "weekly_enough",
    "insufficient_data",
]


class WeeklySleepSummary(BaseModel):
    """
    Conservative weekly recap built from historical DailyRecords.

    This model is user-facing history context only. It intentionally avoids
    diagnosis, health-state assertions, or replacing the current-day sleep
    summary.
    """

    reference_date: str
    days: int
    label: WeeklySleepSummaryLabel
    usable_record_count: int
    average_total_sleep_minutes: int | None = None
    recent_dates: list[str] = Field(default_factory=list)
    display_title: str = "Simple Weekly Summary"
    display_label: str = "週次まとめはまだ参考程度"
    display_summary: str = "もう少し記録が増えると、軽い週次まとめを表示できます。"
    display_coverage: str = "対象: 直近7日 / 使用記録: 0件"
    display_note: str = (
        "過去のDailyRecordから作る軽い振り返りです。"
        "今日の睡眠や健康状態の診断には使いません。"
    )
    action_hint: str = "まずは記録をためながら、日々の流れを軽く振り返ります。"
    data_scope: str = "weekly_history"
    is_medical_advice: bool = False
