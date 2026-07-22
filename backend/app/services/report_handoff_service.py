from app.models.report_handoff import (
    ReportHandoffAdviceBasisPrefix,
    ReportHandoffContext,
)
from app.models.rhythm_report import RhythmReport


SOURCE_LABEL_COPY = {
    "saved_daily_record_history": "保存済みDailyRecordからの振り返り",
    "saved_daily_record_history_with_mock_sleep": "保存済みDailyRecord（デモ睡眠データ）からの振り返り",
    "saved_daily_record_history_with_real_sleep": "保存済みDailyRecord（連携睡眠データ）からの振り返り",
    "insufficient_saved_history": "保存済み記録が少ないため参考表示",
}

DATA_SCOPE_COPY = {
    "weekly_history": "週次の保存履歴",
    "monthly_history": "月次の保存履歴",
}

DATA_QUALITY_COPY = {
    "usable": "参考にしやすい保存記録があります",
    "partial": "保存記録が少なめなので参考程度です",
    "insufficient": "レポートに使える保存記録がまだ少ないです",
}


def build_report_handoff_context(report: RhythmReport) -> ReportHandoffContext:
    """Return the safe report-to-advice handoff boundary for a report.

    The returned context is not wired into /advice yet. It exists so later days
    can connect report-informed advice without passing the full RhythmReport or
    raw provider/debug details through the prompt, mood, sleep, or character
    fields.
    """

    should_inform_advice = _should_inform_advice(report)
    advice_basis_prefix = _advice_basis_prefix(report)
    user_facing_summary = _user_facing_summary(report)
    prompt_guidance = _prompt_guidance(
        report=report,
        should_inform_advice=should_inform_advice,
        advice_basis_prefix=advice_basis_prefix,
    )

    return ReportHandoffContext(
        period=report.period,
        range_start=report.range_start,
        range_end=report.range_end,
        label=report.label,
        display_summary=report.display_summary,
        action_hint=report.action_hint,
        source_label=report.source_label,
        data_scope=report.data_scope,
        data_quality=report.data_quality,
        total_record_count=report.total_record_count,
        usable_sleep_record_count=report.usable_sleep_record_count,
        is_medical_advice=report.is_medical_advice,
        should_inform_advice=should_inform_advice,
        advice_basis_prefix=advice_basis_prefix,
        user_facing_source_label=SOURCE_LABEL_COPY[report.source_label],
        user_facing_scope_label=DATA_SCOPE_COPY[report.data_scope],
        user_facing_quality_label=DATA_QUALITY_COPY[report.data_quality],
        user_facing_summary=user_facing_summary,
        prompt_guidance=prompt_guidance,
    )


def build_report_handoff_prompt_section(
    context: ReportHandoffContext | None,
) -> str:
    """Build a conservative prompt section for a future advice integration."""

    if context is None:
        return ""

    return (
        "Report handoff context:\n"
        f"- Period: {context.period}\n"
        f"- Date range: {context.range_start} to {context.range_end}\n"
        f"- Label: {context.label}\n"
        f"- Source label: {context.source_label}\n"
        f"- Data scope: {context.data_scope}\n"
        f"- Data quality: {context.data_quality}\n"
        f"- Records: {context.total_record_count} saved / "
        f"{context.usable_sleep_record_count} usable sleep records\n"
        f"- User-facing source: {context.user_facing_source_label}\n"
        f"- User-facing scope: {context.user_facing_scope_label}\n"
        f"- User-facing quality: {context.user_facing_quality_label}\n"
        f"- Summary: {context.user_facing_summary}\n"
        f"- Action hint: {context.action_hint}\n"
        f"- Advice basis prefix: {context.advice_basis_prefix}\n"
        f"- Should inform advice: {context.should_inform_advice}\n"
        f"- Guidance: {context.prompt_guidance}\n"
        "- Treat this as historical context only.\n"
        "- Do not present this as today's sleep result.\n"
        "- Do not diagnose, score health, or make treatment claims.\n\n"
    )


def _should_inform_advice(report: RhythmReport) -> bool:
    if report.is_medical_advice:
        return False

    return report.data_quality in {"usable", "partial"}


def _advice_basis_prefix(report: RhythmReport) -> ReportHandoffAdviceBasisPrefix:
    if report.is_medical_advice:
        return "none"

    if report.data_quality == "usable":
        return "rhythm_report"

    if report.data_quality == "partial":
        return "rhythm_report_partial"

    return "none"


def _user_facing_summary(report: RhythmReport) -> str:
    if report.data_quality == "insufficient":
        return (
            "レポートに使える保存記録がまだ少ないので、"
            "今回は気分や今日の睡眠を中心に扱います。"
        )

    if report.data_quality == "partial":
        return (
            f"{report.display_summary}"
            "保存記録が少なめなので、レポート要素は参考程度に扱います。"
        )

    return (
        f"{report.display_summary}"
        "過去の保存記録から見た軽い振り返りとして扱います。"
    )


def _prompt_guidance(
    *,
    report: RhythmReport,
    should_inform_advice: bool,
    advice_basis_prefix: ReportHandoffAdviceBasisPrefix,
) -> str:
    if not should_inform_advice or advice_basis_prefix == "none":
        return (
            "Report data is insufficient or unsafe for report-informed advice. "
            "Do not use it to make strong conclusions. Fall back to today's "
            "sleep summary, mood, and character guidance."
        )

    if advice_basis_prefix == "rhythm_report_partial":
        return (
            "Use this report only as low-confidence historical context. "
            "Say it is参考程度, avoid firm conclusions, and prioritize mood and "
            "today's available sleep summary."
        )

    return (
        "Use this report as lightweight historical context only. "
        "It may gently inform pacing or reflection, but today's available sleep "
        "summary and mood remain more important than the historical report."
    )
