from datetime import date as Date, timedelta

from app.models.daily_record import DailyRecordResponse
from app.models.rhythm_report import (
    RhythmReport,
    RhythmReportDataQuality,
    RhythmReportLabel,
    RhythmReportPeriod,
    RhythmReportSourceLabel,
)
from app.services.daily_record_store import DailyRecordStore


WEEKLY_DAYS = 7
MONTHLY_DAYS = 30
MIN_WEEKLY_RECORDS = 2
MIN_MONTHLY_RECORDS = 5
SHORT_AVERAGE_THRESHOLD_MINUTES = 6 * 60
ENOUGH_AVERAGE_THRESHOLD_MINUTES = 7 * 60


class RhythmReportService:
    """Build conservative weekly/monthly rhythm reports from DailyRecord history."""

    def __init__(self, store: DailyRecordStore | None = None) -> None:
        self.store = store or DailyRecordStore()

    def build_report(
        self,
        *,
        period: RhythmReportPeriod,
        reference_date: str,
    ) -> RhythmReport:
        """Return a deterministic report without external providers or LLM calls."""

        days = _days_for_period(period)
        min_records = _minimum_usable_records_for_period(period)
        range_start, range_end = _range_for_reference_date(
            reference_date=reference_date,
            days=days,
        )
        records = _filter_records_in_range(
            records=self.store.list_recent(limit=365),
            range_start=range_start,
            range_end=range_end,
        )
        usable_records = _usable_sleep_records(records)

        average_minutes = None
        if usable_records:
            total_minutes = [
                record.sleep_summary.total_sleep_minutes for record in usable_records
            ]
            average_minutes = round(sum(total_minutes) / len(total_minutes))

        label = _label_for_report(
            period=period,
            usable_record_count=len(usable_records),
            average_total_sleep_minutes=average_minutes,
        )
        data_quality = _data_quality_for_count(
            usable_record_count=len(usable_records),
            minimum_usable_records=min_records,
        )

        return RhythmReport(
            period=period,
            reference_date=reference_date,
            range_start=range_start.isoformat(),
            range_end=range_end.isoformat(),
            days=days,
            label=label,
            total_record_count=len(records),
            usable_sleep_record_count=len(usable_records),
            average_total_sleep_minutes=average_minutes,
            record_dates=[record.date for record in usable_records],
            display_title=_display_title_for_period(period),
            display_label=_display_label_for_label(label),
            display_summary=_display_summary_for_label(
                label=label,
                period=period,
                usable_record_count=len(usable_records),
                average_total_sleep_minutes=average_minutes,
            ),
            display_coverage=(
                f"対象: 直近{days}日 / 保存記録: {len(records)}件 / "
                f"使用記録: {len(usable_records)}件"
            ),
            display_note=(
                "過去のDailyRecordから作る軽い振り返りです。"
                "今日の睡眠や健康状態の診断には使いません。"
            ),
            action_hint=_action_hint_for_label(label),
            source_label=_source_label_for_records(usable_records),
            data_scope=f"{period}_history",  # type: ignore[arg-type]
            data_quality=data_quality,
            is_medical_advice=False,
        )


def _days_for_period(period: RhythmReportPeriod) -> int:
    return WEEKLY_DAYS if period == "weekly" else MONTHLY_DAYS


def _minimum_usable_records_for_period(period: RhythmReportPeriod) -> int:
    return MIN_WEEKLY_RECORDS if period == "weekly" else MIN_MONTHLY_RECORDS


def _range_for_reference_date(*, reference_date: str, days: int) -> tuple[Date, Date]:
    range_end = Date.fromisoformat(reference_date)
    range_start = range_end - timedelta(days=days - 1)
    return range_start, range_end


def _filter_records_in_range(
    *,
    records: list[DailyRecordResponse],
    range_start: Date,
    range_end: Date,
) -> list[DailyRecordResponse]:
    filtered: list[DailyRecordResponse] = []

    for record in records:
        try:
            record_date = Date.fromisoformat(record.date)
        except ValueError:
            continue

        if range_start <= record_date <= range_end:
            filtered.append(record)

    return sorted(filtered, key=lambda record: record.date, reverse=True)


def _usable_sleep_records(
    records: list[DailyRecordResponse],
) -> list[DailyRecordResponse]:
    return [
        record
        for record in records
        if record.sleep_summary.available
        and (record.sleep_summary.total_sleep_minutes or 0) > 0
    ]


def _label_for_report(
    *,
    period: RhythmReportPeriod,
    usable_record_count: int,
    average_total_sleep_minutes: int | None,
) -> RhythmReportLabel:
    if period == "weekly":
        if usable_record_count < MIN_WEEKLY_RECORDS or average_total_sleep_minutes is None:
            return "insufficient_data"
        if average_total_sleep_minutes < SHORT_AVERAGE_THRESHOLD_MINUTES:
            return "weekly_short"
        if average_total_sleep_minutes >= ENOUGH_AVERAGE_THRESHOLD_MINUTES:
            return "weekly_enough"
        return "weekly_balanced"

    if usable_record_count < MIN_MONTHLY_RECORDS or average_total_sleep_minutes is None:
        return "monthly_sparse"
    if average_total_sleep_minutes < SHORT_AVERAGE_THRESHOLD_MINUTES:
        return "monthly_mixed"
    if average_total_sleep_minutes >= ENOUGH_AVERAGE_THRESHOLD_MINUTES:
        return "monthly_enough"
    return "monthly_stable"


def _data_quality_for_count(
    *,
    usable_record_count: int,
    minimum_usable_records: int,
) -> RhythmReportDataQuality:
    if usable_record_count <= 0:
        return "insufficient"
    if usable_record_count < minimum_usable_records:
        return "partial"
    return "usable"


def _source_label_for_records(
    records: list[DailyRecordResponse],
) -> RhythmReportSourceLabel:
    if not records:
        return "insufficient_saved_history"

    has_real_sleep = any(record.sleep_summary.is_real_data for record in records)
    if has_real_sleep:
        return "saved_daily_record_history_with_real_sleep"

    has_mock_sleep = any(record.sleep_summary.source == "mock" for record in records)
    if has_mock_sleep:
        return "saved_daily_record_history_with_mock_sleep"

    return "saved_daily_record_history"


def _display_title_for_period(period: RhythmReportPeriod) -> str:
    return "Weekly Rhythm Report" if period == "weekly" else "Monthly Rhythm Report"


def _display_label_for_label(label: RhythmReportLabel) -> str:
    return {
        "insufficient_data": "週次レポートはまだ参考程度",
        "weekly_short": "今週は短め寄り",
        "weekly_balanced": "今週はほどほど安定",
        "weekly_enough": "今週は確保できた日が多め",
        "monthly_sparse": "月次レポートはまだ参考程度",
        "monthly_mixed": "今月は短めの日もありそう",
        "monthly_stable": "今月はほどほど安定",
        "monthly_enough": "今月は確保できた日が多め",
    }[label]


def _display_summary_for_label(
    *,
    label: RhythmReportLabel,
    period: RhythmReportPeriod,
    usable_record_count: int,
    average_total_sleep_minutes: int | None,
) -> str:
    average = _format_sleep_minutes(average_total_sleep_minutes)

    if label in {"insufficient_data", "monthly_sparse"}:
        return (
            f"使える過去記録は{usable_record_count}件です。"
            "記録が少ないので、今は参考メモとして見てください。"
        )

    if label in {"weekly_short", "monthly_mixed"}:
        return (
            f"保存済み記録から見ると、平均睡眠は{average}で短め寄りです。"
            "予定や休憩を軽く見直す参考にできます。"
        )

    if label in {"weekly_enough", "monthly_enough"}:
        return (
            f"保存済み記録から見ると、平均睡眠は{average}です。"
            "比較的確保できた日が多めの流れとして振り返れます。"
        )

    if period == "monthly":
        return (
            f"保存済み記録から見ると、平均睡眠は{average}です。"
            "大きく崩れすぎない月として軽く振り返れます。"
        )

    return (
        f"保存済み記録から見ると、平均睡眠は{average}です。"
        "大きく崩れすぎない週として軽く振り返れます。"
    )


def _action_hint_for_label(label: RhythmReportLabel) -> str:
    return {
        "insufficient_data": "まずはDailyRecordをためて、あとで週の流れを見返します。",
        "weekly_short": "短めの日が続く時は、無理な予定を詰めすぎない参考にしてください。",
        "weekly_balanced": "今のリズムを軽く見返しながら、無理なく続ける参考にしてください。",
        "weekly_enough": "良さそうな流れを振り返り、続けやすい要素を探す参考にしてください。",
        "monthly_sparse": "まずはDailyRecordをためて、あとで月の流れを見返します。",
        "monthly_mixed": "短めの日が重なる時期だけ軽く見直す参考にしてください。",
        "monthly_stable": "月全体の流れを軽く見返しながら、無理なく続ける参考にしてください。",
        "monthly_enough": "確保できた日の共通点をゆるく探す参考にしてください。",
    }[label]


def _format_sleep_minutes(value: int | None) -> str:
    if value is None:
        return "-"

    hours = value // 60
    minutes = value % 60
    return f"{hours}時間{minutes}分"
