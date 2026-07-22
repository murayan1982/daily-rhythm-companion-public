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
    total_sleep_minutes: int | None
    time_in_bed_minutes: int | None
    efficiency: int | None
    main_sleep_start_time: str | None
    main_sleep_end_time: str | None
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
    Normalize raw Fitbit sleep API data into an app-facing summary shape.

    Fitbit's sleep/date response usually contains a `sleep` list and a
    `summary` object. This normalizer prefers the main sleep entry when
    available, and falls back to summary-level values.
    """

    sleep_entries = data.get("sleep")
    summary_data = data.get("summary")

    if sleep_entries is not None and not isinstance(sleep_entries, list):
        return FitbitSleepNormalizeResult(
            success=False,
            error=FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE,
            message="Fitbit sleep response had an invalid sleep field.",
        )

    if summary_data is not None and not isinstance(summary_data, dict):
        return FitbitSleepNormalizeResult(
            success=False,
            error=FITBIT_SLEEP_NORMALIZE_ERROR_INVALID_RESPONSE,
            message="Fitbit sleep response had an invalid summary field.",
        )

    if not sleep_entries and not summary_data:
        return FitbitSleepNormalizeResult(
            success=False,
            error=FITBIT_SLEEP_NORMALIZE_ERROR_NO_SLEEP_DATA,
            message="Fitbit sleep response did not contain sleep data.",
        )

    main_sleep = _find_main_sleep_entry(sleep_entries or [])

    total_sleep_minutes = _extract_total_sleep_minutes(
        main_sleep=main_sleep,
        summary_data=summary_data or {},
    )
    time_in_bed_minutes = _extract_time_in_bed_minutes(
        main_sleep=main_sleep,
    )

    normalized_summary = NormalizedFitbitSleepSummary(
        date=target_date,
        source="fitbit",
        total_sleep_minutes=total_sleep_minutes,
        time_in_bed_minutes=time_in_bed_minutes,
        efficiency=_optional_int(main_sleep or {}, "efficiency"),
        main_sleep_start_time=_optional_string(main_sleep or {}, "startTime"),
        main_sleep_end_time=_optional_string(main_sleep or {}, "endTime"),
        message="Fitbit sleep summary was normalized.",
    )

    return FitbitSleepNormalizeResult(
        success=True,
        summary=normalized_summary,
        error=None,
        message="Fitbit sleep response normalized successfully.",
    )


def _find_main_sleep_entry(
    sleep_entries: list[Any],
) -> dict[str, Any] | None:
    """
    Return the main sleep entry when available.

    Fitbit can return multiple sleep entries. The entry with `isMainSleep=true`
    is the best fit for a daily summary.
    """

    dict_entries = [
        entry for entry in sleep_entries if isinstance(entry, dict)
    ]

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
) -> int | None:
    if main_sleep:
        minutes_asleep = _optional_int(main_sleep, "minutesAsleep")

        if minutes_asleep is not None:
            return minutes_asleep

    return _optional_int(summary_data, "totalMinutesAsleep")


def _extract_time_in_bed_minutes(
    *,
    main_sleep: dict[str, Any] | None,
) -> int | None:
    if not main_sleep:
        return None

    return _optional_int(main_sleep, "timeInBed")


def _optional_string(
    data: dict[str, Any],
    key: str,
) -> str | None:
    value = data.get(key)

    if isinstance(value, str) and value:
        return value

    return None


def _optional_int(
    data: dict[str, Any],
    key: str,
) -> int | None:
    value = data.get(key)

    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return None