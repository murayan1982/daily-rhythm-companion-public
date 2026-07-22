from app.models.weekly_sleep_summary import (
    WeeklySleepSummary,
    WeeklySleepSummaryLabel,
)
from app.services.daily_record_store import DailyRecordStore


MIN_WEEKLY_RECORDS = 2
WEEKLY_DAYS = 7
SHORT_AVERAGE_THRESHOLD_MINUTES = 6 * 60
ENOUGH_AVERAGE_THRESHOLD_MINUTES = 7 * 60


class WeeklySleepSummaryService:
    """Build a lightweight weekly recap from historical DailyRecords."""

    def __init__(self, store: DailyRecordStore | None = None) -> None:
        self.store = store or DailyRecordStore()

    def summarize_weekly_history(
        self,
        *,
        reference_date: str,
        days: int = WEEKLY_DAYS,
    ) -> WeeklySleepSummary:
        """
        Return a conservative weekly summary for History UI.

        The summary is a short retrospective label. It must not diagnose the
        user, promise improvement, or present history as today's sleep result.
        """

        records = self.store.list_recent_sleep_available_records(
            reference_date=reference_date,
            days=days,
            limit=days,
        )

        if len(records) < MIN_WEEKLY_RECORDS:
            return _build_weekly_summary(
                reference_date=reference_date,
                days=days,
                label="insufficient_data",
                usable_record_count=len(records),
                average_total_sleep_minutes=None,
                recent_dates=[record.date for record in records],
            )

        total_minutes = [record.sleep_summary.total_sleep_minutes for record in records]
        average_minutes = round(sum(total_minutes) / len(total_minutes))

        return _build_weekly_summary(
            reference_date=reference_date,
            days=days,
            label=_label_from_average_minutes(average_minutes),
            usable_record_count=len(records),
            average_total_sleep_minutes=average_minutes,
            recent_dates=[record.date for record in records],
        )


def _build_weekly_summary(
    *,
    reference_date: str,
    days: int,
    label: WeeklySleepSummaryLabel,
    usable_record_count: int,
    average_total_sleep_minutes: int | None,
    recent_dates: list[str],
) -> WeeklySleepSummary:
    return WeeklySleepSummary(
        reference_date=reference_date,
        days=days,
        label=label,
        usable_record_count=usable_record_count,
        average_total_sleep_minutes=average_total_sleep_minutes,
        recent_dates=recent_dates,
        display_label=_display_label_for_label(label),
        display_summary=_display_summary_for_label(
            label=label,
            usable_record_count=usable_record_count,
            average_total_sleep_minutes=average_total_sleep_minutes,
        ),
        display_coverage=(
            f"対象: 直近{days}日 / 使用記録: {usable_record_count}件"
        ),
        display_note=(
            "過去のDailyRecordから作る軽い振り返りです。"
            "今日の睡眠や健康状態の診断には使いません。"
        ),
        action_hint=_action_hint_for_label(label),
    )


def _label_from_average_minutes(average_minutes: int) -> WeeklySleepSummaryLabel:
    if average_minutes < SHORT_AVERAGE_THRESHOLD_MINUTES:
        return "weekly_short"

    if average_minutes >= ENOUGH_AVERAGE_THRESHOLD_MINUTES:
        return "weekly_enough"

    return "weekly_balanced"


def _display_label_for_label(label: WeeklySleepSummaryLabel) -> str:
    return {
        "weekly_short": "今週は短め寄り",
        "weekly_balanced": "今週はほどほど安定",
        "weekly_enough": "今週は確保できた日が多め",
        "insufficient_data": "週次まとめはまだ参考程度",
    }[label]


def _display_summary_for_label(
    *,
    label: WeeklySleepSummaryLabel,
    usable_record_count: int,
    average_total_sleep_minutes: int | None,
) -> str:
    average = _format_sleep_minutes(average_total_sleep_minutes)

    if label == "insufficient_data":
        return (
            f"使える過去記録は{usable_record_count}件です。"
            "もう少し記録が増えると、軽い週次まとめを表示できます。"
        )

    if label == "weekly_short":
        return (
            f"直近の使える記録では、平均睡眠が{average}で短め寄りです。"
            "予定や休憩を軽く見直す参考にできます。"
        )

    if label == "weekly_enough":
        return (
            f"直近の使える記録では、平均睡眠が{average}です。"
            "比較的確保できた日が多めの週として振り返れます。"
        )

    return (
        f"直近の使える記録では、平均睡眠が{average}です。"
        "大きく崩れすぎない週として軽く振り返れます。"
    )


def _action_hint_for_label(label: WeeklySleepSummaryLabel) -> str:
    return {
        "weekly_short": "短めの日が続く時は、無理な予定を詰めすぎない参考にしてください。",
        "weekly_balanced": "今のリズムを軽く見返しながら、無理なく続ける参考にしてください。",
        "weekly_enough": "良さそうな流れを振り返り、続けやすい要素を探す参考にしてください。",
        "insufficient_data": "まずはDailyRecordをためて、あとで週の流れを見返します。",
    }[label]


def _format_sleep_minutes(value: int | None) -> str:
    if value is None:
        return "-"

    hours = value // 60
    minutes = value % 60
    return f"{hours}時間{minutes}分"
