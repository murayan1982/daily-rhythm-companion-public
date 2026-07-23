from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA = "no_sleep_data"
FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE = "invalid_sleep_response"


@dataclass(frozen=True)
class NormalizedFitbitSleepSummary:
    """
    App-facing normalized Fitbit sleep summary.

    This shape intentionally contains only summary-level sleep values. It does
    not expose the raw Fitbit sleep payload.
    """

    date: str
    source: str
    total_sleep_minutes: int
    time_in_bed_minutes: int | None
    efficiency: int | None
    main_sleep_start_time: str | None
    main_sleep_end_time: str | None
    quality_label: str
    confidence: str
    is_real_data: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary dictionary."""

        return {
            "date": self.date,
            "source": self.source,
            "total_sleep_minutes": self.total_sleep_minutes,
            "time_in_bed_minutes": self.time_in_bed_minutes,
            "efficiency": self.efficiency,
            "main_sleep_start_time": self.main_sleep_start_time,
            "main_sleep_end_time": self.main_sleep_end_time,
            "quality_label": self.quality_label,
            "confidence": self.confidence,
            "is_real_data": self.is_real_data,
            "message": self.message,
        }


@dataclass(frozen=True)
class FitbitSleepNormalizeResult:
    """
    Result of normalizing Fitbit sleep API data.

    raw Fitbit payloads should stay outside app-facing API responses.
    """

    success: bool
    summary: NormalizedFitbitSleepSummary | None = None
    error: str | None = None
    message: str | None = None


def normalize_fitbit_sleep_response(
    data: dict[str, Any],
    *,
    target_date: str,
) -> FitbitSleepNormalizeResult:
    """
    Normalize Fitbit sleep API data into a conservative app-facing summary.

    The normalizer prefers the main sleep entry and may fall back to the
    summary-level total. A positive usable sleep duration is required before
    the result can be treated as accepted real-provider data.
    """

    if not isinstance(data, dict):
        return _invalid_response("Fitbit sleep response was not an object.")

    sleep_entries = data.get("sleep")
    summary_data = data.get("summary")

    if sleep_entries is not None and not isinstance(sleep_entries, list):
        return _invalid_response("Fitbit sleep response had an invalid sleep field.")

    if summary_data is not None and not isinstance(summary_data, dict):
        return _invalid_response("Fitbit sleep response had an invalid summary field.")

    if not sleep_entries and not summary_data:
        return _no_sleep_data()

    main_sleep = _find_main_sleep_entry(sleep_entries or [])
    total_result = _extract_total_sleep_minutes(
        main_sleep=main_sleep,
        summary_data=summary_data or {},
    )

    if total_result.invalid:
        return _invalid_response("Fitbit sleep duration had an invalid value.")

    total_sleep_minutes = total_result.value
    if total_sleep_minutes is None or total_sleep_minutes <= 0:
        return _no_sleep_data()

    start_time = _optional_string(main_sleep or {}, "startTime")
    end_time = _optional_string(main_sleep or {}, "endTime")
    used_complete_main_sleep = (
        total_result.used_main_sleep
        and start_time is not None
        and end_time is not None
    )

    normalized_summary = NormalizedFitbitSleepSummary(
        date=target_date,
        source="fitbit",
        total_sleep_minutes=total_sleep_minutes,
        time_in_bed_minutes=_optional_non_negative_int(
            main_sleep or {},
            "timeInBed",
        ),
        efficiency=_optional_bounded_int(
            main_sleep or {},
            "efficiency",
            minimum=0,
            maximum=100,
        ),
        main_sleep_start_time=start_time,
        main_sleep_end_time=end_time,
        quality_label=_quality_label(total_sleep_minutes),
        confidence="high" if used_complete_main_sleep else "medium",
        is_real_data=True,
        message="Fitbit sleep summary was normalized into SleepSummary fields.",
    )

    return FitbitSleepNormalizeResult(
        success=True,
        summary=normalized_summary,
        error=None,
        message="Fitbit sleep response normalized successfully.",
    )


@dataclass(frozen=True)
class _TotalSleepResult:
    value: int | None
    used_main_sleep: bool
    invalid: bool


def _find_main_sleep_entry(
    sleep_entries: list[Any],
) -> dict[str, Any] | None:
    """Return the main sleep entry, or the first object entry as fallback."""

    dict_entries = [entry for entry in sleep_entries if isinstance(entry, dict)]

    for entry in dict_entries:
        if entry.get("isMainSleep") is True:
            return entry

    if dict_entries:
        return dict_entries[0]

    return None


def _extract_total_sleep_minutes(
    *,
    main_sleep: dict[str, Any] | None,
    summary_data: dict[str, Any],
) -> _TotalSleepResult:
    if main_sleep and "minutesAsleep" in main_sleep:
        value, valid = _parse_non_negative_int(main_sleep.get("minutesAsleep"))
        if not valid:
            return _TotalSleepResult(None, True, True)
        if value is not None:
            return _TotalSleepResult(value, True, False)

    if "totalMinutesAsleep" in summary_data:
        value, valid = _parse_non_negative_int(
            summary_data.get("totalMinutesAsleep")
        )
        if not valid:
            return _TotalSleepResult(None, False, True)
        return _TotalSleepResult(value, False, False)

    return _TotalSleepResult(None, False, False)


def _optional_string(
    data: dict[str, Any],
    key: str,
) -> str | None:
    value = data.get(key)

    if isinstance(value, str) and value.strip():
        return value.strip()

    return None


def _optional_non_negative_int(
    data: dict[str, Any],
    key: str,
) -> int | None:
    value, valid = _parse_non_negative_int(data.get(key))
    return value if valid else None


def _optional_bounded_int(
    data: dict[str, Any],
    key: str,
    *,
    minimum: int,
    maximum: int,
) -> int | None:
    value = _optional_non_negative_int(data, key)
    if value is None or value < minimum or value > maximum:
        return None
    return value


def _parse_non_negative_int(value: Any) -> tuple[int | None, bool]:
    if value is None:
        return None, True

    if isinstance(value, bool):
        return None, False

    if isinstance(value, int):
        return (value, True) if value >= 0 else (None, False)

    if isinstance(value, str) and value.isdigit():
        return int(value), True

    return None, False


def _quality_label(total_sleep_minutes: int) -> str:
    if total_sleep_minutes >= 420:
        return "good"
    if total_sleep_minutes >= 360:
        return "fair"
    return "short"


def _no_sleep_data() -> FitbitSleepNormalizeResult:
    return FitbitSleepNormalizeResult(
        success=False,
        error=FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA,
        message="Fitbit sleep response did not contain usable sleep data.",
    )


def _invalid_response(message: str) -> FitbitSleepNormalizeResult:
    return FitbitSleepNormalizeResult(
        success=False,
        error=FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE,
        message=message,
    )
