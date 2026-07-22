from app.models.recent_sleep_trend import RecentSleepTrend, RecentSleepTrendLabel
from app.models.sleep import SleepSummary
from app.services.daily_record_store import DailyRecordStore


MIN_USABLE_RECORDS = 2
RECENT_DAYS = 7
SHORT_SLEEP_THRESHOLD_MINUTES = 6 * 60
GOOD_SLEEP_THRESHOLD_MINUTES = 7 * 60


class RecentSleepTrendService:
    """Summarize recent usable DailyRecords without inventing today's sleep."""

    def __init__(self, store: DailyRecordStore | None = None) -> None:
        self.store = store or DailyRecordStore()

    def summarize_recent_history(
        self,
        *,
        reference_date: str,
        days: int = RECENT_DAYS,
    ) -> RecentSleepTrend:
        """
        Return a user-facing recent history trend label.

        The returned trend is always historical/reference context. It can help
        the History screen explain recent records, but it must not replace or
        reinterpret the current-day sleep summary.
        """

        records = self.store.list_recent_sleep_available_records(
            reference_date=reference_date,
            days=days,
            limit=days,
        )

        if len(records) < MIN_USABLE_RECORDS:
            return _build_trend(
                reference_date=reference_date,
                days=days,
                label="insufficient_data",
                usable_record_count=len(records),
                average_total_sleep_minutes=None,
                recent_dates=[record.date for record in records],
            )

        total_minutes = [record.sleep_summary.total_sleep_minutes for record in records]
        average_minutes = round(sum(total_minutes) / len(total_minutes))
        label = _label_from_average_minutes(average_minutes)

        return _build_trend(
            reference_date=reference_date,
            days=days,
            label=label,
            usable_record_count=len(records),
            average_total_sleep_minutes=average_minutes,
            recent_dates=[record.date for record in records],
        )

    def summarize_for_unavailable_today(
        self,
        *,
        current_sleep: SleepSummary,
        days: int = RECENT_DAYS,
    ) -> RecentSleepTrend:
        """
        Return a recent trend only when today's sleep summary is unavailable.

        Available current-day sleep should remain the source of truth and should
        not be overridden by history. This service is a fallback helper for the
        unavailable case only.
        """

        if current_sleep.available:
            return _build_trend(
                reference_date=current_sleep.date,
                days=days,
                label="insufficient_data",
                usable_record_count=0,
                average_total_sleep_minutes=None,
                recent_dates=[],
                message=(
                    "Current-day sleep data is available; "
                    "recent trend fallback is not used."
                ),
                display_summary=(
                    "今日は睡眠データを取得済みです。直近傾向フォールバックは使いません。"
                ),
            )

        return self.summarize_recent_history(
            reference_date=current_sleep.date,
            days=days,
        )


def _build_trend(
    *,
    reference_date: str,
    days: int,
    label: RecentSleepTrendLabel,
    usable_record_count: int,
    average_total_sleep_minutes: int | None,
    recent_dates: list[str],
    message: str | None = None,
    display_summary: str | None = None,
) -> RecentSleepTrend:
    return RecentSleepTrend(
        reference_date=reference_date,
        days=days,
        label=label,
        usable_record_count=usable_record_count,
        average_total_sleep_minutes=average_total_sleep_minutes,
        recent_dates=recent_dates,
        message=message or _message_for_label(label),
        display_label=_display_label_for_label(label),
        display_summary=display_summary or _display_summary_for_label(
            label=label,
            usable_record_count=usable_record_count,
            average_total_sleep_minutes=average_total_sleep_minutes,
        ),
        display_note=(
            "履歴から見た参考情報です。今日の睡眠データや健康状態の断定には使いません。"
        ),
    )


def _label_from_average_minutes(average_minutes: int) -> RecentSleepTrendLabel:
    if average_minutes < SHORT_SLEEP_THRESHOLD_MINUTES:
        return "recently_short"

    if average_minutes >= GOOD_SLEEP_THRESHOLD_MINUTES:
        return "recently_good"

    return "recently_stable"


def _message_for_label(label: RecentSleepTrendLabel) -> str:
    return {
        "recently_short": "Recent usable records suggest shorter sleep than ideal.",
        "recently_stable": "Recent usable records suggest a moderate sleep rhythm.",
        "recently_good": "Recent usable records suggest enough sleep overall.",
        "insufficient_data": (
            "Not enough recent usable sleep records are available for a trend."
        ),
    }[label]


def _display_label_for_label(label: RecentSleepTrendLabel) -> str:
    return {
        "recently_short": "最近は短め傾向",
        "recently_stable": "最近は安定傾向",
        "recently_good": "最近は十分め傾向",
        "insufficient_data": "傾向はまだ参考程度",
    }[label]


def _display_summary_for_label(
    *,
    label: RecentSleepTrendLabel,
    usable_record_count: int,
    average_total_sleep_minutes: int | None,
) -> str:
    average = _format_average_sleep_minutes(average_total_sleep_minutes)

    if label == "insufficient_data":
        return (
            f"使える過去記録は{usable_record_count}件です。"
            "もう少し記録が増えると、直近傾向を表示できます。"
        )

    if label == "recently_short":
        return f"直近の使える記録では、平均睡眠が{average}で短めの傾向です。"

    if label == "recently_good":
        return f"直近の使える記録では、平均睡眠が{average}で比較的十分めです。"

    return f"直近の使える記録では、平均睡眠が{average}で大きな崩れは少なめです。"


def _format_average_sleep_minutes(value: int | None) -> str:
    if value is None:
        return "-"

    hours = value // 60
    minutes = value % 60
    return f"{hours}時間{minutes}分"
