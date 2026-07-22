from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.models.sleep import SleepSummary


GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK = "ok"
GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_DATA_POINTS = "no_data_points"
GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_USABLE_INTERVALS = "no_usable_intervals"
GOOGLE_HEALTH_SLEEP_PARSE_STATUS_INVALID_PAYLOAD = "invalid_payload"

_SLEEP_STAGE_ASLEEP_TYPES = {"ASLEEP", "LIGHT", "REM", "DEEP"}


@dataclass(frozen=True)
class GoogleHealthSleepParseResult:
    """Safe normalized result from a Google Health sleep dataPoints payload.

    The original Google Health response can contain personal health data. This
    parser returns only the DRC app-facing SleepSummary and small parse metadata.
    """

    status: str
    summary: SleepSummary
    data_point_count: int = 0
    usable_interval_count: int = 0
    message: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class _ParsedSleepDataPoint:
    start: datetime
    end: datetime
    minutes_asleep: int
    minutes_awake: int | None
    deep_sleep_minutes: int | None
    rem_sleep_minutes: int | None
    used_official_summary: bool


def parse_google_health_sleep_data_points(
    *,
    payload: dict[str, Any],
    target_date: str,
) -> GoogleHealthSleepParseResult:
    """Normalize Google Health sleep dataPoints into DRC's SleepSummary shape.

    Google Health v4 sleep data points expose an observed interval and may also
    expose ``sleep.summary`` metrics. The provider's ``minutesAsleep`` and
    ``minutesAwake`` values are preferred over the interval duration. Stage
    summaries are used for deep/REM values and as a secondary asleep/awake
    fallback. Only when no usable provider summary exists does the parser fall
    back to the observed interval duration.
    """

    if not isinstance(payload, dict):
        return _unavailable_result(
            status=GOOGLE_HEALTH_SLEEP_PARSE_STATUS_INVALID_PAYLOAD,
            target_date=target_date,
            unavailable_reason="invalid_payload",
            message="Google Health sleep payload was not an object.",
            error="invalid_payload",
        )

    raw_data_points = payload.get("dataPoints")
    if not isinstance(raw_data_points, list) or not raw_data_points:
        return _unavailable_result(
            status=GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_DATA_POINTS,
            target_date=target_date,
            unavailable_reason="no_sleep_data_points",
            data_point_count=0,
            message="Google Health returned no sleep dataPoints for the target date.",
            error="no_sleep_data_points",
        )

    parsed_points: list[_ParsedSleepDataPoint] = []
    for data_point in raw_data_points:
        parsed_point = _parse_sleep_data_point(data_point)
        if parsed_point is not None:
            parsed_points.append(parsed_point)

    if not parsed_points:
        return _unavailable_result(
            status=GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_USABLE_INTERVALS,
            target_date=target_date,
            unavailable_reason="no_usable_sleep_intervals",
            data_point_count=len(raw_data_points),
            message="Google Health sleep dataPoints did not contain usable sleep intervals.",
            error="no_usable_sleep_intervals",
        )

    intervals = [(point.start, point.end) for point in parsed_points]
    merged_intervals = _merge_intervals(intervals)
    observed_period_minutes = sum(
        max(0, int((end - start).total_seconds() // 60))
        for start, end in merged_intervals
    )

    # Provider summaries can overlap when multiple sources describe the same
    # observed period. Cap aggregate metrics to the merged observed duration so
    # DRC never reports more sleep than the returned intervals can contain.
    total_sleep_minutes = min(
        sum(point.minutes_asleep for point in parsed_points),
        observed_period_minutes,
    )
    awake_minutes = _capped_optional_sum(
        [point.minutes_awake for point in parsed_points],
        cap=observed_period_minutes,
    )
    deep_sleep_minutes = _capped_optional_sum(
        [point.deep_sleep_minutes for point in parsed_points],
        cap=total_sleep_minutes,
    )
    rem_sleep_minutes = _capped_optional_sum(
        [point.rem_sleep_minutes for point in parsed_points],
        cap=total_sleep_minutes,
    )

    sleep_start = min(start for start, _ in merged_intervals)
    sleep_end = max(end for _, end in merged_intervals)
    efficiency = _sleep_efficiency(
        total_sleep_minutes=total_sleep_minutes,
        observed_period_minutes=observed_period_minutes,
    )
    used_only_official_summaries = all(
        point.used_official_summary for point in parsed_points
    )

    normalization_source = (
        "official Google Health sleep summary metrics"
        if used_only_official_summaries
        else "Google Health sleep summary metrics with interval fallback"
    )

    summary = SleepSummary(
        date=target_date,
        total_sleep_minutes=total_sleep_minutes,
        efficiency=efficiency,
        deep_sleep_minutes=deep_sleep_minutes,
        rem_sleep_minutes=rem_sleep_minutes,
        awake_minutes=awake_minutes,
        source="google_health",
        available=True,
        message=f"{normalization_source} were normalized into SleepSummary.",
        sleep_start=_format_rfc3339_z(sleep_start),
        sleep_end=_format_rfc3339_z(sleep_end),
        quality_label=_quality_label(total_sleep_minutes),
        confidence="high" if used_only_official_summaries else "medium",
        is_real_data=True,
        unavailable_reason=None,
    )

    return GoogleHealthSleepParseResult(
        status=GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK,
        summary=summary,
        data_point_count=len(raw_data_points),
        usable_interval_count=len(parsed_points),
        message=summary.message,
        error=None,
    )


def _parse_sleep_data_point(data_point: object) -> _ParsedSleepDataPoint | None:
    interval = _extract_sleep_interval(data_point)
    if interval is None or not isinstance(data_point, dict):
        return None

    sleep = data_point.get("sleep")
    if not isinstance(sleep, dict):
        return None

    start, end = interval
    interval_minutes = max(0, int((end - start).total_seconds() // 60))
    summary = sleep.get("summary")
    summary_metrics = summary if isinstance(summary, dict) else {}
    stage_metrics = _extract_stage_summary_minutes(summary_metrics)

    minutes_asleep = _optional_non_negative_int(summary_metrics.get("minutesAsleep"))
    if minutes_asleep is None:
        minutes_asleep = _sum_stage_minutes(stage_metrics, _SLEEP_STAGE_ASLEEP_TYPES)

    used_official_summary = minutes_asleep is not None
    if minutes_asleep is None:
        minutes_asleep = interval_minutes

    minutes_awake = _optional_non_negative_int(summary_metrics.get("minutesAwake"))
    if minutes_awake is None:
        minutes_awake = stage_metrics.get("AWAKE")

    return _ParsedSleepDataPoint(
        start=start,
        end=end,
        minutes_asleep=min(minutes_asleep, interval_minutes),
        minutes_awake=minutes_awake,
        deep_sleep_minutes=stage_metrics.get("DEEP"),
        rem_sleep_minutes=stage_metrics.get("REM"),
        used_official_summary=used_official_summary,
    )


def _extract_sleep_interval(data_point: object) -> tuple[datetime, datetime] | None:
    if not isinstance(data_point, dict):
        return None

    sleep = data_point.get("sleep")
    if not isinstance(sleep, dict):
        return None

    interval = sleep.get("interval")
    if not isinstance(interval, dict):
        return None

    start_value = _first_string(interval, "startTime", "start_time")
    end_value = _first_string(interval, "endTime", "end_time")
    if not start_value or not end_value:
        return None

    start = _parse_datetime(start_value)
    end = _parse_datetime(end_value)
    if start is None or end is None or end <= start:
        return None

    return start, end


def _extract_stage_summary_minutes(summary: dict[str, Any]) -> dict[str, int]:
    raw_stages = summary.get("stagesSummary")
    if not isinstance(raw_stages, list):
        return {}

    stage_minutes: dict[str, int] = {}
    for stage in raw_stages:
        if not isinstance(stage, dict):
            continue

        raw_type = stage.get("type")
        minutes = _optional_non_negative_int(stage.get("minutes"))
        if not isinstance(raw_type, str) or minutes is None:
            continue

        stage_type = raw_type.strip().upper()
        if not stage_type:
            continue
        stage_minutes[stage_type] = stage_minutes.get(stage_type, 0) + minutes

    return stage_minutes


def _sum_stage_minutes(
    stage_minutes: dict[str, int],
    included_types: set[str],
) -> int | None:
    values = [
        minutes
        for stage_type, minutes in stage_minutes.items()
        if stage_type in included_types
    ]
    return sum(values) if values else None


def _optional_non_negative_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            parsed = int(normalized)
        except ValueError:
            return None
        return parsed if parsed >= 0 else None
    return None


def _capped_optional_sum(values: list[int | None], *, cap: int) -> int | None:
    present_values = [value for value in values if value is not None]
    if not present_values:
        return None
    return min(sum(present_values), max(0, cap))


def _first_string(source: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = source.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _parse_datetime(value: str) -> datetime | None:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _merge_intervals(
    intervals: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    sorted_intervals = sorted(intervals, key=lambda item: item[0])
    merged: list[tuple[datetime, datetime]] = []

    for start, end in sorted_intervals:
        if not merged:
            merged.append((start, end))
            continue

        previous_start, previous_end = merged[-1]
        if start <= previous_end:
            merged[-1] = (previous_start, max(previous_end, end))
        else:
            merged.append((start, end))

    return merged


def _sleep_efficiency(
    *,
    total_sleep_minutes: int,
    observed_period_minutes: int,
) -> int | None:
    if observed_period_minutes <= 0:
        return None
    return min(100, max(0, round(total_sleep_minutes * 100 / observed_period_minutes)))


def _quality_label(total_sleep_minutes: int) -> str:
    if total_sleep_minutes >= 420:
        return "good"
    if total_sleep_minutes >= 360:
        return "fair"
    return "short"


def _format_rfc3339_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _unavailable_result(
    *,
    status: str,
    target_date: str,
    unavailable_reason: str,
    message: str,
    data_point_count: int = 0,
    error: str | None = None,
) -> GoogleHealthSleepParseResult:
    summary = SleepSummary(
        date=target_date,
        total_sleep_minutes=0,
        efficiency=None,
        deep_sleep_minutes=None,
        rem_sleep_minutes=None,
        awake_minutes=None,
        source="google_health",
        available=False,
        message=message,
        sleep_start=None,
        sleep_end=None,
        quality_label="unavailable",
        confidence="none",
        is_real_data=False,
        unavailable_reason=unavailable_reason,
    )
    return GoogleHealthSleepParseResult(
        status=status,
        summary=summary,
        data_point_count=data_point_count,
        usable_interval_count=0,
        message=message,
        error=error,
    )
