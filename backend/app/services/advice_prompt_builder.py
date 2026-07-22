from app.models.advice import AdviceRequest
from app.models.recent_sleep_trend import RecentSleepTrend
from app.models.report_handoff import ReportHandoffContext
from app.models.sleep import SleepSummary
from app.services.report_handoff_service import build_report_handoff_prompt_section


QUALITY_LABELS = {
    "good": "good",
    "fair": "fair",
    "short": "short",
    "unavailable": "unavailable",
}

MOOD_LABELS = {
    "energetic": "energetic",
    "normal": "normal",
    "tired": "tired",
}


def build_advice_prompt(request: AdviceRequest) -> str:
    """
    Build a prompt for daily advice generation.

    This prompt keeps Daily Rhythm Companion character and sleep context
    explicit even when the framework-side character is mapped to "default".
    It also keeps Google Health data in an app-level SleepSummary shape so the
    LLM never needs provider-specific raw payloads.

    Mood values are treated as stable internal IDs. Future UI layers may
    generate character-specific, sleep-aware, or lightly randomized mood choice
    labels, but the advice prompt should continue to depend on stable mood IDs
    such as energetic, normal, and tired.
    """

    character = request.character
    sleep = request.sleep
    mood = _format_mood_label(request.mood)
    recent_sleep_trend = getattr(request, "recent_sleep_trend", None)
    report_handoff = _active_report_handoff_context(
        getattr(request, "report_handoff", None)
    )

    character_id = getattr(character, "character_id", "unknown")
    display_name = getattr(character, "display_name", character_id)
    personality_type = getattr(character, "personality_type", "gentle")
    speaking_style = getattr(character, "speaking_style", "casual")
    advice_style = getattr(character, "advice_style", "practical")

    return (
        f"You are {display_name}, a daily rhythm companion.\n"
        f"Character ID: {character_id}\n"
        f"Personality type: {personality_type}\n"
        f"Speaking style: {speaking_style}\n"
        f"Advice style: {advice_style}\n"
        "Follow the character's speaking style and advice style, "
        "but keep the advice clear and suitable for a daily companion app.\n\n"
        f"{_build_sleep_context(sleep)}\n"
        f"{_build_recent_sleep_trend_context(recent_sleep_trend)}"
        f"{build_report_handoff_prompt_section(report_handoff)}"
        f"User mood: {mood}\n\n"
        f"{_build_advice_guidance(sleep, mood, recent_sleep_trend, report_handoff)}\n\n"
        "Please give short, gentle, practical advice in Japanese. "
        "Use the normalized sleep summary and the user's mood. "
        "If real sleep data is available, reflect it naturally without sounding medical. "
        "If sleep data is unavailable, do not invent sleep details. "
        "If recent sleep trend context is available, treat it as historical context only. "
        "If report handoff context is available, treat it as historical context only. "
        "Do not present recent history as today's sleep. "
        "Do not present report context as today's sleep. "
        "Do not sound diagnostic, clinical, or overly confident. "
        "Keep it suitable for a morning companion app."
    )


def _active_report_handoff_context(
    context: ReportHandoffContext | None,
) -> ReportHandoffContext | None:
    """Return report context only when it is safe to inform advice."""

    if context is None:
        return None

    if context.is_medical_advice:
        return None

    if not context.should_inform_advice:
        return None

    if context.advice_basis_prefix == "none":
        return None

    return context


def _build_sleep_context(sleep: SleepSummary) -> str:
    sleep_available = getattr(sleep, "available", True)
    sleep_source = getattr(sleep, "source", "unknown")
    is_real_data = getattr(sleep, "is_real_data", False)
    sleep_message = getattr(sleep, "message", None)
    unavailable_reason = getattr(sleep, "unavailable_reason", None)

    if not sleep_available:
        return (
            "User sleep summary:\n"
            f"- Date: {sleep.date}\n"
            f"- Source: {sleep_source}\n"
            f"- Data kind: {_format_data_kind(is_real_data, sleep_source)}\n"
            "- Sleep data is unavailable today.\n"
            f"- Unavailable reason: {unavailable_reason or 'unknown'}\n"
            f"- User-facing reason: {sleep_message or 'Sleep data is not available.'}\n"
            "- Do not mention exact sleep duration, sleep efficiency, deep sleep, REM sleep, or awake time.\n"
            "- Do not blame the user or mention technical implementation details.\n"
            "- Gently acknowledge that sleep data could not be checked today.\n"
            "- Base the advice mainly on the user's mood.\n"
        )

    total_hours = sleep.total_sleep_minutes // 60
    total_minutes = sleep.total_sleep_minutes % 60

    return (
        "User sleep summary:\n"
        f"- Date: {sleep.date}\n"
        f"- Source: {sleep_source}\n"
        f"- Data kind: {_format_data_kind(is_real_data, sleep_source)}\n"
        f"- Total sleep: {total_hours}h {total_minutes}m\n"
        f"- Sleep window start: {sleep.sleep_start or 'unknown'}\n"
        f"- Sleep window end: {sleep.sleep_end or 'unknown'}\n"
        f"- Sleep quality label: {_format_quality_label(sleep.quality_label)}\n"
        f"- Confidence: {sleep.confidence or 'unknown'}\n"
        f"- Sleep efficiency: {_format_optional_minutes_or_percent(sleep.efficiency, '%')}\n"
        f"- Deep sleep: {_format_optional_minutes_or_percent(sleep.deep_sleep_minutes, ' minutes')}\n"
        f"- REM sleep: {_format_optional_minutes_or_percent(sleep.rem_sleep_minutes, ' minutes')}\n"
        f"- Awake time: {_format_optional_minutes_or_percent(sleep.awake_minutes, ' minutes')}\n"
        "- Advice should reflect total sleep, sleep quality label, data kind, and mood.\n"
    )


def _build_recent_sleep_trend_context(trend: RecentSleepTrend | None) -> str:
    """Build optional historical sleep context for unavailable current-day sleep."""

    if trend is None or trend.label == "insufficient_data":
        return ""

    average = _format_average_sleep_minutes(trend.average_total_sleep_minutes)
    recent_dates = ", ".join(trend.recent_dates) or "unknown"

    return (
        "Recent sleep trend fallback:\n"
        f"- Reference date: {trend.reference_date}\n"
        f"- Window: last {trend.days} days\n"
        f"- Label: {trend.label}\n"
        f"- Usable record count: {trend.usable_record_count}\n"
        f"- Average total sleep: {average}\n"
        f"- Recent record dates: {recent_dates}\n"
        "- This is historical context only. Do not present it as today's sleep.\n"
        "- Use it only to gently adjust the advice when today's sleep data is unavailable.\n\n"
    )


def _format_average_sleep_minutes(value: int | None) -> str:
    if value is None:
        return "unknown"

    hours = value // 60
    minutes = value % 60
    return f"{hours}h {minutes}m"


def _build_advice_guidance(
    sleep: SleepSummary,
    mood: str,
    recent_sleep_trend: RecentSleepTrend | None = None,
    report_handoff: ReportHandoffContext | None = None,
) -> str:
    """
    Build high-level guidance for the LLM.

    This is intentionally separate from the raw sleep summary. The sleep summary
    tells the model what happened; this guidance tells it how to respond in a
    stable daily-companion tone.
    """

    if not getattr(sleep, "available", True):
        return _append_report_handoff_guidance(
            _build_unavailable_sleep_guidance(mood, recent_sleep_trend),
            report_handoff,
        )

    quality_label = _format_quality_label(getattr(sleep, "quality_label", None))

    if quality_label == "short":
        return _append_report_handoff_guidance(
            _build_short_sleep_guidance(mood),
            report_handoff,
        )

    if quality_label == "good":
        return _append_report_handoff_guidance(
            _build_good_sleep_guidance(mood),
            report_handoff,
        )

    if quality_label == "fair":
        return _append_report_handoff_guidance(
            _build_fair_sleep_guidance(mood),
            report_handoff,
        )

    return _append_report_handoff_guidance(
        _build_unknown_sleep_guidance(mood),
        report_handoff,
    )


def _append_report_handoff_guidance(
    guidance: str,
    report_handoff: ReportHandoffContext | None,
) -> str:
    if report_handoff is None:
        return guidance

    return (
        f"{guidance}"
        "- Report handoff context is available. Use it only as historical reflection.\n"
        "- Do not present report context as today's sleep result.\n"
        "- Keep report-informed advice lightweight, mood-aware, and non-medical.\n"
    )


def _build_unavailable_sleep_guidance(
    mood: str,
    recent_sleep_trend: RecentSleepTrend | None = None,
) -> str:
    mood_note = {
        "tired": (
            "- The user feels tired, so prioritize low-pressure advice.\n"
            "- Suggest one small first step and one way to reduce today's load.\n"
            "- Do not tell the user to push harder.\n"
        ),
        "energetic": (
            "- The user feels energetic, so use the positive mood.\n"
            "- Still avoid making claims about sleep quality.\n"
        ),
        "normal": (
            "- The user feels normal, so keep the advice balanced and simple.\n"
        ),
    }.get(
        mood,
        "- Keep the advice balanced and based mainly on the user's stated mood.\n",
    )

    trend_guidance = _build_recent_sleep_trend_guidance(recent_sleep_trend)

    return (
        "Advice guidance:\n"
        "- Sleep data is unavailable today.\n"
        "- Do not invent sleep details.\n"
        "- Do not present recent sleep history as today's sleep.\n"
        "- Gently acknowledge that sleep data could not be checked today.\n"
        "- Avoid technical error details.\n"
        f"{trend_guidance}"
        f"{mood_note}"
    )


def _build_recent_sleep_trend_guidance(trend: RecentSleepTrend | None) -> str:
    if trend is None or trend.label == "insufficient_data":
        return "- Base the advice mainly on the user's mood.\n"

    if trend.label == "recently_short":
        return (
            "- Recent sleep history suggests shorter sleep overall.\n"
            "- Use this only as historical context, not as today's sleep result.\n"
            "- Suggest lower-pressure planning and recovery-friendly pacing.\n"
        )

    if trend.label == "recently_good":
        return (
            "- Recent sleep history suggests enough sleep overall.\n"
            "- Use this only as historical context, not as today's sleep result.\n"
            "- Keep advice positive but still avoid claiming today's sleep was good.\n"
        )

    return (
        "- Recent sleep history suggests a moderate sleep rhythm.\n"
        "- Use this only as historical context, not as today's sleep result.\n"
        "- Keep advice balanced and mood-aware.\n"
    )


def _build_short_sleep_guidance(mood: str) -> str:
    if mood == "tired":
        return (
            "Advice guidance:\n"
            "- The user had short sleep and feels tired.\n"
            "- Prioritize recovery, low-pressure planning, and small first steps.\n"
            "- Do not tell the user to push harder.\n"
            "- Suggest reducing today's load where possible.\n"
            "- Suggest one gentle morning action.\n"
        )

    if mood == "energetic":
        return (
            "Advice guidance:\n"
            "- The user had short sleep but feels energetic.\n"
            "- Acknowledge the positive mood.\n"
            "- Gently warn against overdoing it.\n"
            "- Suggest doing important tasks earlier and planning breaks.\n"
            "- Avoid suggesting an overloaded schedule.\n"
        )

    return (
        "Advice guidance:\n"
        "- The user had short sleep and feels normal.\n"
        "- Keep the day realistic.\n"
        "- Suggest a lighter plan and short breaks.\n"
        "- Avoid suggesting an overloaded schedule.\n"
    )


def _build_good_sleep_guidance(mood: str) -> str:
    if mood == "tired":
        return (
            "Advice guidance:\n"
            "- The user slept well but feels tired.\n"
            "- Respect the user's mood.\n"
            "- Do not imply they should feel energetic.\n"
            "- Suggest a gentle warm-up before starting important tasks.\n"
        )

    if mood == "energetic":
        return (
            "Advice guidance:\n"
            "- The user slept well and feels energetic.\n"
            "- Help them use the good condition for one meaningful task.\n"
            "- Avoid suggesting an overloaded schedule.\n"
            "- Encourage steady progress rather than doing everything at once.\n"
        )

    return (
        "Advice guidance:\n"
        "- The user slept well and feels normal.\n"
        "- Suggest steady progress and a balanced rhythm.\n"
        "- Encourage one manageable focus for the day.\n"
    )


def _build_fair_sleep_guidance(mood: str) -> str:
    if mood == "tired":
        return (
            "Advice guidance:\n"
            "- The sleep summary looks moderate, but the user feels tired.\n"
            "- Prioritize the user's current mood.\n"
            "- Suggest pacing, small breaks, and a realistic workload.\n"
        )

    if mood == "energetic":
        return (
            "Advice guidance:\n"
            "- The user has moderate sleep and feels energetic.\n"
            "- Suggest using the momentum without overcommitting.\n"
            "- Encourage planned breaks so the day does not become too heavy.\n"
        )

    return (
        "Advice guidance:\n"
        "- The user has moderate sleep and feels normal.\n"
        "- Keep the advice balanced.\n"
        "- Suggest one manageable focus for the day.\n"
    )


def _build_unknown_sleep_guidance(mood: str) -> str:
    if mood == "tired":
        mood_instruction = (
            "- The user feels tired, so keep the advice gentle and low-pressure.\n"
        )
    elif mood == "energetic":
        mood_instruction = (
            "- The user feels energetic, so suggest using that momentum carefully.\n"
        )
    else:
        mood_instruction = (
            "- Keep the advice balanced and easy to act on.\n"
        )

    return (
        "Advice guidance:\n"
        "- The sleep quality label is unknown or not yet categorized.\n"
        "- Use the available sleep summary carefully without over-interpreting it.\n"
        f"{mood_instruction}"
    )


def _format_data_kind(is_real_data: bool, source: str) -> str:
    if is_real_data:
        return "real provider data"

    if source == "mock" or source.endswith("_stub"):
        return "demo/fallback data"

    return "unknown data kind"


def _format_quality_label(value: str | None) -> str:
    if not value:
        return "unknown"

    return QUALITY_LABELS.get(value, value)


def _format_mood_label(value: str | None) -> str:
    if not value:
        return "normal"

    return MOOD_LABELS.get(value, value)


def _format_optional_minutes_or_percent(value: int | None, suffix: str) -> str:
    if value is None:
        return "unknown"

    return f"{value}{suffix}"