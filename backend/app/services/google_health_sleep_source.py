from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.config import AppConfig
from app.models.sleep import SleepSummary
from app.services.google_health_api_client import (
    GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
    GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG,
)
from app.services.google_health_credentials import (
    GoogleHealthOAuthCredentials,
    load_google_health_credentials,
)
from app.services.google_health_session import (
    GOOGLE_HEALTH_SESSION_ERROR_NO_STORED_TOKENS,
    GOOGLE_HEALTH_SESSION_ERROR_REFRESH_NOT_COMPLETED,
    GoogleHealthSessionResult,
    get_google_health_json_after_refresh_if_needed,
)
from app.services.google_health_sleep_parser import (
    GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK,
    parse_google_health_sleep_data_points,
)
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_CREDENTIALS = "needs_credentials"
GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_AUTH = "needs_auth"
GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_REFRESH_REQUIRED = "refresh_required"
GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED = "api_disabled"
GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_UNAVAILABLE = "unavailable"
GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_OK = "ok"

DEFAULT_GOOGLE_HEALTH_SLEEP_API_PATH = "/v1/sleep:summary"


@dataclass(frozen=True)
class GoogleHealthSleepSourceResult:
    """
    Safe result for the Google Health sleep source boundary.

    This result is app-facing and intentionally excludes access tokens,
    refresh tokens, Authorization headers, client secrets, and raw personal
    health payloads.
    """

    status: str
    summary: SleepSummary
    session: GoogleHealthSessionResult | None = None
    message: str | None = None
    error: str | None = None


class GoogleHealthSleepSourceError(RuntimeError):
    """Raised when the Google Health sleep source is used unsafely."""


def fetch_google_health_sleep_summary(
    *,
    config: AppConfig,
    target_date: date | None = None,
    credentials: GoogleHealthOAuthCredentials | None = None,
    token_store: GoogleHealthTokenStore | None = None,
    api_path: str | None = None,
) -> GoogleHealthSleepSourceResult:
    """
    Fetch an app-facing sleep summary through the Google Health session boundary.

    The actual Google Health/Fit API endpoint and payload schema are still kept
    behind this source boundary. Until those are finalized, this source only
    exposes a safe SleepSummary status and does not leak raw API payloads.
    """

    sleep_date = target_date or date.today()
    oauth_credentials = credentials

    if oauth_credentials is None:
        credentials_result = load_google_health_credentials(
            config.google_health_credentials_file
        )
        if not credentials_result.loaded or credentials_result.credentials is None:
            return _build_source_result(
                status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_CREDENTIALS,
                target_date=sleep_date,
                available=False,
                message=(
                    "Google Health credentials are not ready. Today, advice "
                    "will use your mood input instead of sleep data."
                ),
                error=credentials_result.error,
            )

        oauth_credentials = credentials_result.credentials

    session_result = get_google_health_json_after_refresh_if_needed(
        config=config,
        credentials=oauth_credentials,
        api_path=api_path or config.google_health_sleep_api_path,
        query_params=build_google_health_sleep_data_points_query_params(
            config=config,
            target_date=sleep_date,
        ),
        token_store=token_store,
        timeout_seconds=config.google_health_api_timeout_seconds,
    )

    if session_result.error == GOOGLE_HEALTH_SESSION_ERROR_NO_STORED_TOKENS:
        return _build_source_result(
            status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_AUTH,
            target_date=sleep_date,
            available=False,
            message=(
                "Google Health is not connected yet. Today, advice will use "
                "your mood input instead of sleep data."
            ),
            session=session_result,
            error=session_result.error,
        )

    if session_result.error == GOOGLE_HEALTH_SESSION_ERROR_REFRESH_NOT_COMPLETED:
        return _build_source_result(
            status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_REFRESH_REQUIRED,
            target_date=sleep_date,
            available=False,
            message=(
                "Google Health access needs to be refreshed before sleep data "
                "can be used. Today, advice will use your mood input instead."
            ),
            session=session_result,
            error=session_result.error,
        )

    if session_result.error == GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED:
        return _build_source_result(
            status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED,
            target_date=sleep_date,
            available=False,
            message=(
                "Google Health API request is prepared but disabled. This is "
                "expected until the real API endpoint is verified."
            ),
            session=session_result,
            error=session_result.error,
        )

    if session_result.error == GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG:
        return _build_source_result(
            status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED,
            target_date=sleep_date,
            available=False,
            message=(
                "Google Health real API requests are blocked by runtime "
                "configuration guard. Check GOOGLE_HEALTH_API_BASE_URL, "
                "GOOGLE_HEALTH_SLEEP_API_PATH, and timeout settings."
            ),
            session=session_result,
            error=session_result.error,
        )

    if not session_result.succeeded:
        return _build_source_result(
            status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_UNAVAILABLE,
            target_date=sleep_date,
            available=False,
            message=(
                "Google Health sleep data is currently unavailable. Today, "
                "advice will use your mood input instead."
            ),
            session=session_result,
            error=session_result.error,
        )

    parse_result = parse_google_health_sleep_data_points(
        payload=session_result.api_response_data or {},
        target_date=sleep_date.isoformat(),
    )

    if parse_result.status != GOOGLE_HEALTH_SLEEP_PARSE_STATUS_OK:
        return GoogleHealthSleepSourceResult(
            status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_UNAVAILABLE,
            summary=parse_result.summary,
            session=session_result,
            message=parse_result.message,
            error=parse_result.error,
        )

    return GoogleHealthSleepSourceResult(
        status=GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_OK,
        summary=parse_result.summary,
        session=session_result,
        message=parse_result.message,
        error=None,
    )


def build_google_health_sleep_data_points_query_params(
    *,
    config: AppConfig,
    target_date: date,
) -> dict[str, str]:
    """Build the Google Health sleep dataPoints.list filter query.

    Google Health dataPoints.list uses a single ``filter`` query parameter for
    date ranges. The sleep-specific ``sleep.interval.civil_end_time`` field
    selects sessions by the user's civil end date, avoiding UTC date shifts for
    sleep that ends in the local morning.
    """

    filter_expression = build_google_health_sleep_civil_end_date_filter(
        start_date=target_date,
        end_date=target_date + timedelta(days=1),
    )

    return {config.google_health_sleep_filter_query_param: filter_expression}


def build_google_health_sleep_civil_end_date_filter(
    *,
    start_date: date,
    end_date: date,
) -> str:
    """Build the sleep-specific civil-end-date list filter value."""

    return (
        f'sleep.interval.civil_end_time >= "{start_date.isoformat()}" '
        f'AND sleep.interval.civil_end_time < "{end_date.isoformat()}"'
    )


def _build_source_result(
    *,
    status: str,
    target_date: date,
    available: bool,
    message: str,
    session: GoogleHealthSessionResult | None = None,
    error: str | None = None,
) -> GoogleHealthSleepSourceResult:
    """Build a safe app-facing Google Health sleep source result."""

    return GoogleHealthSleepSourceResult(
        status=status,
        summary=SleepSummary(
            date=target_date.isoformat(),
            total_sleep_minutes=0,
            efficiency=None,
            deep_sleep_minutes=None,
            rem_sleep_minutes=None,
            awake_minutes=None,
            source="google_health",
            available=available,
            message=message,
        ),
        session=session,
        message=message,
        error=error,
    )
