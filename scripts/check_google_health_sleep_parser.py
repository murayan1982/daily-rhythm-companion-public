from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.google_health_sleep_parser import (  # noqa: E402
    GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_DATA_POINTS,
    GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_USABLE_INTERVALS,
    GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK,
    parse_google_health_sleep_data_points,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_safe_summary(summary_json: str) -> None:
    forbidden = (
        "access_token",
        "refresh_token",
        "client_secret",
        "authorization",
        "bearer ",
        "raw_payload",
    )
    lower = summary_json.lower()
    leaked = [fragment for fragment in forbidden if fragment in lower]
    _assert(not leaked, f"SleepSummary leaked raw/sensitive fragments: {leaked}")


def check_official_sleep_summary_metrics_are_preferred() -> None:
    payload = {
        "dataPoints": [
            {
                "name": "users/me/dataTypes/sleep/dataPoints/one",
                "dataSource": {"platform": "FITBIT"},
                "sleep": {
                    "interval": {
                        "startTime": "2026-05-05T15:00:00Z",
                        "endTime": "2026-05-05T23:00:00Z",
                    },
                    "summary": {
                        "minutesInSleepPeriod": "480",
                        "minutesAsleep": "430",
                        "minutesAwake": "35",
                        "stagesSummary": [
                            {"type": "LIGHT", "minutes": "240", "count": "8"},
                            {"type": "DEEP", "minutes": "90", "count": "4"},
                            {"type": "REM", "minutes": "100", "count": "5"},
                            {"type": "AWAKE", "minutes": "35", "count": "6"},
                        ],
                    },
                },
            }
        ],
        "nextPageToken": "",
    }

    result = parse_google_health_sleep_data_points(
        payload=payload,
        target_date="2026-05-06",
    )

    _assert(result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK, result.status)
    _assert(result.data_point_count == 1, str(result.data_point_count))
    _assert(result.usable_interval_count == 1, str(result.usable_interval_count))
    _assert(result.summary.available is True, "summary should be available")
    _assert(result.summary.source == "google_health", result.summary.source)
    _assert(result.summary.total_sleep_minutes == 430, str(result.summary.total_sleep_minutes))
    _assert(result.summary.awake_minutes == 35, str(result.summary.awake_minutes))
    _assert(result.summary.deep_sleep_minutes == 90, str(result.summary.deep_sleep_minutes))
    _assert(result.summary.rem_sleep_minutes == 100, str(result.summary.rem_sleep_minutes))
    _assert(result.summary.efficiency == 90, str(result.summary.efficiency))
    _assert(result.summary.sleep_start == "2026-05-05T15:00:00Z", result.summary.sleep_start or "")
    _assert(result.summary.sleep_end == "2026-05-05T23:00:00Z", result.summary.sleep_end or "")
    _assert(result.summary.quality_label == "good", result.summary.quality_label or "")
    _assert(result.summary.confidence == "high", result.summary.confidence or "")
    _assert(result.summary.is_real_data is True, "summary should mark real data")
    _assert(result.summary.unavailable_reason is None, result.summary.unavailable_reason or "")
    _assert_safe_summary(result.summary.model_dump_json())


def check_stage_summary_fallback() -> None:
    payload = {
        "dataPoints": [
            {
                "sleep": {
                    "interval": {
                        "startTime": "2026-05-05T15:00:00Z",
                        "endTime": "2026-05-05T22:30:00Z",
                    },
                    "summary": {
                        "stagesSummary": [
                            {"type": "LIGHT", "minutes": "230"},
                            {"type": "DEEP", "minutes": "80"},
                            {"type": "REM", "minutes": "75"},
                            {"type": "AWAKE", "minutes": "40"},
                        ]
                    },
                }
            }
        ]
    }

    result = parse_google_health_sleep_data_points(
        payload=payload,
        target_date="2026-05-06",
    )

    _assert(result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK, result.status)
    _assert(result.summary.total_sleep_minutes == 385, str(result.summary.total_sleep_minutes))
    _assert(result.summary.awake_minutes == 40, str(result.summary.awake_minutes))
    _assert(result.summary.deep_sleep_minutes == 80, str(result.summary.deep_sleep_minutes))
    _assert(result.summary.rem_sleep_minutes == 75, str(result.summary.rem_sleep_minutes))
    _assert(result.summary.efficiency == 86, str(result.summary.efficiency))
    _assert(result.summary.quality_label == "fair", result.summary.quality_label or "")
    _assert(result.summary.confidence == "high", result.summary.confidence or "")


def check_interval_fallback_and_overlap_cap() -> None:
    payload = {
        "dataPoints": [
            {
                "sleep": {
                    "interval": {
                        "startTime": "2026-05-05T15:00:00Z",
                        "endTime": "2026-05-05T20:00:00Z",
                    }
                }
            },
            {
                "sleep": {
                    "interval": {
                        "startTime": "2026-05-05T19:00:00Z",
                        "endTime": "2026-05-05T22:00:00Z",
                    }
                }
            },
        ]
    }

    result = parse_google_health_sleep_data_points(
        payload=payload,
        target_date="2026-05-06",
    )

    _assert(result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK, result.status)
    _assert(result.summary.total_sleep_minutes == 420, str(result.summary.total_sleep_minutes))
    _assert(result.summary.efficiency == 100, str(result.summary.efficiency))
    _assert(result.summary.awake_minutes is None, str(result.summary.awake_minutes))
    _assert(result.summary.deep_sleep_minutes is None, str(result.summary.deep_sleep_minutes))
    _assert(result.summary.rem_sleep_minutes is None, str(result.summary.rem_sleep_minutes))
    _assert(result.summary.quality_label == "good", result.summary.quality_label or "")
    _assert(result.summary.confidence == "medium", result.summary.confidence or "")


def check_no_data_points() -> None:
    result = parse_google_health_sleep_data_points(
        payload={"dataPoints": []},
        target_date="2026-05-06",
    )

    _assert(result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_DATA_POINTS, result.status)
    _assert(result.summary.available is False, "summary should be unavailable")
    _assert(result.summary.total_sleep_minutes == 0, str(result.summary.total_sleep_minutes))
    _assert(result.summary.quality_label == "unavailable", result.summary.quality_label or "")
    _assert(result.summary.confidence == "none", result.summary.confidence or "")
    _assert(result.summary.is_real_data is False, "no data should not be marked real")
    _assert(result.summary.unavailable_reason == "no_sleep_data_points", result.summary.unavailable_reason or "")
    _assert_safe_summary(result.summary.model_dump_json())


def check_unusable_intervals() -> None:
    result = parse_google_health_sleep_data_points(
        payload={
            "dataPoints": [
                {
                    "sleep": {
                        "interval": {
                            "startTime": "bad",
                            "endTime": "also-bad",
                        }
                    }
                }
            ]
        },
        target_date="2026-05-06",
    )

    _assert(result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_USABLE_INTERVALS, result.status)
    _assert(result.summary.available is False, "summary should be unavailable")
    _assert(result.summary.unavailable_reason == "no_usable_sleep_intervals", result.summary.unavailable_reason or "")


def main() -> int:
    check_official_sleep_summary_metrics_are_preferred()
    check_stage_summary_fallback()
    check_interval_fallback_and_overlap_cap()
    check_no_data_points()
    check_unusable_intervals()
    print("[google-health-sleep-parser-check] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
