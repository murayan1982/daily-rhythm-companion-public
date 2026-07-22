from __future__ import annotations

from datetime import date

from app.config import AppConfig
from app.models.google_health import (
    GoogleHealthApiRequestPreviewModel,
    GoogleHealthProviderErrorSummaryModel,
    GoogleHealthSelfCheckApiModel,
    GoogleHealthSelfCheckRefreshModel,
    GoogleHealthSelfCheckResponse,
    GoogleHealthSelfCheckSessionModel,
)
from app.services.google_health_diagnostics import get_google_health_diagnostics
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_session import (
    GoogleHealthApiClientSummary,
    GoogleHealthSessionResult,
    GoogleHealthTokenRefreshSummary,
)
from app.services.google_health_sleep_source import fetch_google_health_sleep_summary
from app.services.google_health_token_store import GoogleHealthTokenStore


GOOGLE_HEALTH_SELF_CHECK_STATUS_SKIPPED = "skipped"


def run_google_health_self_check(
    *,
    config: AppConfig,
    target_date: date | None = None,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthSelfCheckResponse:
    """
    Run a safe Google Health smoke path for local development.

    The check uses the same source/session/API-client boundary as
    /sleep/summary with SLEEP_PROVIDER=google_health, but returns only safe
    status metadata. It never returns tokens, authorization headers, client
    secrets, or raw health payloads.
    """

    check_date = target_date or date.today()
    store = token_store or GoogleHealthTokenStore()
    diagnostics = get_google_health_diagnostics(config, token_store=store)

    if config.sleep_provider != GOOGLE_HEALTH_PROVIDER_NAME:
        return GoogleHealthSelfCheckResponse(
            provider=GOOGLE_HEALTH_PROVIDER_NAME,
            target_date=check_date.isoformat(),
            diagnostics_status=diagnostics.overall_status,
            source_status=GOOGLE_HEALTH_SELF_CHECK_STATUS_SKIPPED,
            safe_to_use_sleep_summary=False,
            real_http_attempted=False,
            session=None,
            message=(
                "Google Health self-check skipped because SLEEP_PROVIDER is "
                "not google_health. Set SLEEP_PROVIDER=google_health to test "
                "the sleep source path."
            ),
            error=diagnostics.error,
        )

    source_result = fetch_google_health_sleep_summary(
        config=config,
        target_date=check_date,
        token_store=store,
    )
    session_model = _build_session_model(source_result.session)
    real_http_attempted = bool(
        session_model
        and session_model.api
        and session_model.api.attempted
    )

    return GoogleHealthSelfCheckResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        target_date=check_date.isoformat(),
        diagnostics_status=diagnostics.overall_status,
        source_status=source_result.status,
        safe_to_use_sleep_summary=source_result.summary.available,
        real_http_attempted=real_http_attempted,
        session=session_model,
        message=source_result.message or source_result.summary.message or "",
        error=source_result.error,
    )


def _build_session_model(
    session: GoogleHealthSessionResult | None,
) -> GoogleHealthSelfCheckSessionModel | None:
    if session is None:
        return None

    return GoogleHealthSelfCheckSessionModel(
        token_available=session.token_available,
        refresh_checked=session.refresh_checked,
        api_requested=session.api_requested,
        succeeded=session.succeeded,
        endpoint=session.endpoint,
        refresh=_build_refresh_model(session.refresh_summary),
        api=_build_api_model(session.api_summary),
        message=session.message,
        error=session.error,
    )


def _build_refresh_model(
    refresh: GoogleHealthTokenRefreshSummary | None,
) -> GoogleHealthSelfCheckRefreshModel | None:
    if refresh is None:
        return None

    return GoogleHealthSelfCheckRefreshModel(
        checked=True,
        attempted=refresh.attempted,
        request_prepared=refresh.request_prepared,
        real_refresh_enabled=refresh.real_refresh_enabled,
        refreshed=refresh.refreshed,
        saved=refresh.saved,
        message=refresh.message,
        error=refresh.error,
    )


def _build_api_model(
    api: GoogleHealthApiClientSummary | None,
) -> GoogleHealthSelfCheckApiModel | None:
    if api is None:
        return None

    preview = api.request_preview
    preview_model = None
    if preview is not None:
        preview_model = GoogleHealthApiRequestPreviewModel(
            endpoint=preview.endpoint,
            method=preview.method,
            has_bearer_auth=preview.has_bearer_auth,
            query_param_keys=list(preview.query_param_keys),
            query_params=dict(preview.query_params),
            preview_url=preview.preview_url,
        )

    provider_error_summary_model = None
    if api.provider_error_summary is not None:
        provider_error_summary_model = GoogleHealthProviderErrorSummaryModel(
            http_status_code=api.provider_error_summary.http_status_code,
            provider_error_code=api.provider_error_summary.provider_error_code,
            provider_error_status=api.provider_error_summary.provider_error_status,
            provider_error_message_hint=api.provider_error_summary.provider_error_message_hint,
            provider_error_reason=api.provider_error_summary.provider_error_reason,
            provider_error_domain=api.provider_error_summary.provider_error_domain,
            provider_error_metadata_keys=list(
                api.provider_error_summary.provider_error_metadata_keys
            ),
            www_authenticate_hint=api.provider_error_summary.www_authenticate_hint,
            suggested_cause=api.provider_error_summary.suggested_cause,
        )

    return GoogleHealthSelfCheckApiModel(
        requested=True,
        attempted=api.attempted,
        request_prepared=api.request_prepared,
        real_api_enabled=api.real_api_enabled,
        succeeded=api.succeeded,
        status_code=api.status_code,
        request_preview=preview_model,
        provider_error_category=api.provider_error_category,
        provider_error_summary=provider_error_summary_model,
        message=api.message,
        error=api.error,
    )
