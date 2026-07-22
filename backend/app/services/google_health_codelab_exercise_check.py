from __future__ import annotations

from app.config import AppConfig
from app.models.google_health import GoogleHealthCodelabExerciseCheckResponse
from app.services.google_health_api_client import (
    build_google_health_api_endpoint,
    get_google_health_json_with_tokens_if_enabled,
)
from app.services.google_health_credentials import load_google_health_credentials
from app.services.google_health_self_check import _build_session_model
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_session import (
    GoogleHealthSessionResult,
    summarize_google_health_api_client_result,
    summarize_google_health_token_refresh_result,
)
from app.services.google_health_token_refresh import (
    refresh_google_health_access_token_if_needed,
)
from app.services.google_health_token_store import GoogleHealthTokenStore


CODELAB_REFERENCE = "google_health_first_api_call_exercise_dataPoints"


def run_google_health_codelab_exercise_check(
    *,
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthCodelabExerciseCheckResponse:
    """Run the official Codelab-style exercise dataPoints smoke safely.

    The Google Health Codelab validates the basic Fitbit/Google Health account
    linkage by calling ``users/me/dataTypes/exercise/dataPoints`` after adding
    a manual Fitbit activity. This endpoint returns only safe metadata here:
    status, endpoint preview, and data-point count. Raw health payloads remain
    internal.
    """

    store = token_store or GoogleHealthTokenStore()
    endpoint = build_google_health_api_endpoint(
        base_url=config.google_health_api_base_url,
        path=config.google_health_exercise_api_path,
    )

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    if not credentials_result.loaded or credentials_result.credentials is None:
        return GoogleHealthCodelabExerciseCheckResponse(
            provider=GOOGLE_HEALTH_PROVIDER_NAME,
            codelab_reference=CODELAB_REFERENCE,
            endpoint=endpoint,
            real_http_attempted=False,
            data_point_count=None,
            data_points_present=None,
            next_page_token_present=None,
            session=None,
            message="Google Health credentials are not ready.",
            next_action="Configure Google Health credentials before running the Codelab exercise smoke.",
            error=credentials_result.error,
        )

    stored_tokens = store.load_tokens()
    if stored_tokens is None:
        session = GoogleHealthSessionResult(
            token_available=False,
            refresh_checked=False,
            api_requested=False,
            succeeded=False,
            endpoint=endpoint,
            message="Google Health Codelab exercise check skipped because no tokens are stored.",
            refresh_summary=None,
            api_summary=None,
            error="no_stored_tokens",
        )
        return GoogleHealthCodelabExerciseCheckResponse(
            provider=GOOGLE_HEALTH_PROVIDER_NAME,
            codelab_reference=CODELAB_REFERENCE,
            endpoint=endpoint,
            real_http_attempted=False,
            data_point_count=None,
            data_points_present=None,
            next_page_token_present=None,
            session=_build_session_model(session),
            message=session.message,
            next_action="Run the Google Health OAuth helper before the Codelab exercise smoke.",
            error=session.error,
        )

    refresh_summary = None
    if stored_tokens.should_refresh_access_token():
        refresh_result = refresh_google_health_access_token_if_needed(
            config=config,
            credentials=credentials_result.credentials,
            token_store=store,
        )
        refresh_summary = summarize_google_health_token_refresh_result(
            refresh_result
        )
        if not refresh_result.refreshed:
            session = GoogleHealthSessionResult(
                token_available=True,
                refresh_checked=True,
                api_requested=False,
                succeeded=False,
                endpoint=endpoint,
                message="Google Health Codelab exercise check skipped because token refresh did not complete.",
                refresh_summary=refresh_summary,
                api_summary=None,
                error=refresh_result.error or "refresh_not_completed",
            )
            return GoogleHealthCodelabExerciseCheckResponse(
                provider=GOOGLE_HEALTH_PROVIDER_NAME,
                codelab_reference=CODELAB_REFERENCE,
                endpoint=endpoint,
                real_http_attempted=False,
                data_point_count=None,
                data_points_present=None,
                next_page_token_present=None,
                session=_build_session_model(session),
                message=session.message,
                next_action="Enable token refresh and rerun the Codelab exercise smoke.",
                error=session.error,
            )

        refreshed_tokens = store.load_tokens()
        if refreshed_tokens is not None:
            stored_tokens = refreshed_tokens

    api_result = get_google_health_json_with_tokens_if_enabled(
        config=config,
        endpoint=endpoint,
        stored_tokens=stored_tokens,
        query_params={},
        timeout_seconds=config.google_health_api_timeout_seconds,
    )
    api_summary = summarize_google_health_api_client_result(api_result)
    session = GoogleHealthSessionResult(
        token_available=True,
        refresh_checked=refresh_summary is not None,
        api_requested=True,
        succeeded=api_result.succeeded,
        endpoint=endpoint,
        refresh_summary=refresh_summary,
        api_summary=api_summary,
        message=api_result.message,
        error=api_result.error,
    )

    data_points = None
    next_page_token_present = None
    if api_result.succeeded and api_result.response is not None:
        raw_data_points = api_result.response.data.get("dataPoints")
        data_points = len(raw_data_points) if isinstance(raw_data_points, list) else 0
        next_page_token = api_result.response.data.get("nextPageToken")
        next_page_token_present = isinstance(next_page_token, str) and bool(next_page_token)

    return GoogleHealthCodelabExerciseCheckResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        codelab_reference=CODELAB_REFERENCE,
        endpoint=endpoint,
        real_http_attempted=bool(api_result.attempted),
        data_point_count=data_points,
        data_points_present=(data_points is not None and data_points > 0),
        next_page_token_present=next_page_token_present,
        session=_build_session_model(session),
        message=api_result.message,
        next_action=_next_action(api_result.succeeded, data_points),
        error=api_result.error,
    )


def _next_action(succeeded: bool, data_point_count: int | None) -> str:
    if not succeeded:
        return (
            "If this returns the GaiaMint/UberMint permission error, confirm the "
            "Fitbit mobile app is signed in with Google and the same account used "
            "for DRC OAuth. If it returns a scope error, add the Codelab exercise "
            "scope to Data Access and re-authorize with prompt=consent."
        )

    if not data_point_count:
        return (
            "The Codelab endpoint is reachable. Add a manual Fitbit activity, "
            "sync the Fitbit mobile app, and rerun this smoke if dataPoints is empty."
        )

    return "The Codelab exercise endpoint returned dataPoints. Continue comparing exercise vs sleep behavior."
