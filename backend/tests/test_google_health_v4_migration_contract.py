"""Mock-safe W-5b1 audit of the Google Health API v4 sleep contract."""
from __future__ import annotations
from datetime import date

from app.config import (
    AppConfig,
    GOOGLE_HEALTH_API_BASE_URL,
    GOOGLE_HEALTH_SLEEP_API_PATH,
    GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,
)
from app.services.google_health_api_client import (
    build_google_health_api_endpoint,
    prepare_google_health_api_get_request,
)
from app.services.google_health_sleep_parser import (
    GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_DATA_POINTS,
    GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK,
    parse_google_health_sleep_data_points,
)
from app.services.google_health_sleep_source import (
    build_google_health_sleep_data_points_query_params,
)
from app.services.sleep_provider_selection_service import get_sleep_provider_selection_status


def _official_sleep_payload(*, include_minutes_asleep: bool = True) -> dict[str, object]:
    summary: dict[str, object] = {
        "minutesAwake": "25",
        "stagesSummary": [
            {"type": "LIGHT", "minutes": "250", "count": "8"},
            {"type": "DEEP", "minutes": "70", "count": "3"},
            {"type": "REM", "minutes": "90", "count": "4"},
            {"type": "AWAKE", "minutes": "25", "count": "6"},
        ],
    }
    if include_minutes_asleep:
        summary["minutesAsleep"] = "410"
    return {
        "dataPoints": [
            {
                "dataSource": {"platform": "FITBIT"},
                "sleep": {
                    "interval": {
                        "startTime": "2026-07-23T14:00:00Z",
                        "endTime": "2026-07-23T21:30:00Z",
                    },
                    "summary": summary,
                },
            }
        ]
    }


def test_defaults_target_google_health_v4_sleep_list() -> None:
    config = AppConfig()
    assert GOOGLE_HEALTH_API_BASE_URL == "https://health.googleapis.com/v4"
    assert GOOGLE_HEALTH_SLEEP_API_PATH == "/users/me/dataTypes/sleep/dataPoints"
    assert GOOGLE_HEALTH_SLEEP_READONLY_SCOPE == "https://www.googleapis.com/auth/googlehealth.sleep.readonly"
    assert config.google_health_api_base_url == GOOGLE_HEALTH_API_BASE_URL
    assert config.google_health_sleep_api_path == GOOGLE_HEALTH_SLEEP_API_PATH


def test_endpoint_builder_matches_v4_list_endpoint() -> None:
    endpoint = build_google_health_api_endpoint(base_url=GOOGLE_HEALTH_API_BASE_URL, path=GOOGLE_HEALTH_SLEEP_API_PATH)
    assert endpoint == "https://health.googleapis.com/v4/users/me/dataTypes/sleep/dataPoints"


def test_sleep_filter_uses_civil_end_date_closed_open_range() -> None:
    query = build_google_health_sleep_data_points_query_params(config=AppConfig(), target_date=date(2026, 7, 24))
    assert query == {"filter": 'sleep.interval.civil_end_time >= "2026-07-24" AND sleep.interval.civil_end_time < "2026-07-25"'}


def test_request_preview_does_not_expose_bearer_token() -> None:
    result = prepare_google_health_api_get_request(endpoint="https://health.googleapis.com/v4/users/me/dataTypes/sleep/dataPoints", access_token="private-token", query_params={"filter": 'sleep.interval.civil_end_time >= "2026-07-24"'})
    assert result.request_preview is not None
    assert result.request_preview.has_bearer_auth is True
    assert "private-token" not in result.request_preview.preview_url
    assert "private-token" not in repr(result.request_preview)


def test_parser_accepts_official_v4_sleep_summary_shape() -> None:
    result = parse_google_health_sleep_data_points(payload=_official_sleep_payload(), target_date="2026-07-24")
    assert result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK
    assert result.summary.source == "google_health"
    assert result.summary.is_real_data is True
    assert result.summary.total_sleep_minutes == 410
    assert result.summary.deep_sleep_minutes == 70
    assert result.summary.rem_sleep_minutes == 90


def test_parser_uses_stage_summary_when_minutes_asleep_missing() -> None:
    result = parse_google_health_sleep_data_points(payload=_official_sleep_payload(include_minutes_asleep=False), target_date="2026-07-24")
    assert result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK
    assert result.summary.total_sleep_minutes == 410


def test_parser_handles_empty_v4_response_without_inventing_data() -> None:
    result = parse_google_health_sleep_data_points(payload={"dataPoints": []}, target_date="2026-07-24")
    assert result.status == GOOGLE_HEALTH_SLEEP_PARSE_STATUS_NO_DATA_POINTS
    assert result.summary.available is False
    assert result.summary.is_real_data is False


def test_provider_metadata_prefers_google_health_and_retires_legacy_fitbit() -> None:
    google = get_sleep_provider_selection_status(AppConfig(sleep_provider="google_health"))
    legacy = get_sleep_provider_selection_status(AppConfig(sleep_provider="fitbit"))
    assert google.configured_provider_role == "configured_real_provider"
    assert legacy.configured_provider_role == "legacy_migration_reference"
    assert legacy.provider_options[-1].real_operator_verification_required is False
