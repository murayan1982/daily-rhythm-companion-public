from __future__ import annotations

from app.config import AppConfig
from app.models.google_health import (
    GoogleHealthRefreshRequestPreviewModel,
    GoogleHealthTokenRefreshCheckResponse,
)
from app.services.google_health_credentials import load_google_health_credentials
from app.services.google_health_service import GOOGLE_HEALTH_PROVIDER_NAME
from app.services.google_health_token_refresh import (
    GoogleHealthRefreshRequestPreview,
    refresh_google_health_access_token_if_needed,
)
from app.services.google_health_token_store import GoogleHealthTokenStore


def run_google_health_token_refresh_check(
    *,
    config: AppConfig,
    token_store: GoogleHealthTokenStore | None = None,
) -> GoogleHealthTokenRefreshCheckResponse:
    """Run the token-refresh boundary without requesting sleep API data."""

    credentials_result = load_google_health_credentials(
        config.google_health_credentials_file
    )
    store = token_store or GoogleHealthTokenStore()
    stored_tokens = store.load_tokens()
    refresh_recommended = (
        stored_tokens.should_refresh_access_token() if stored_tokens else None
    )

    if not credentials_result.loaded or credentials_result.credentials is None:
        return GoogleHealthTokenRefreshCheckResponse(
            provider=GOOGLE_HEALTH_PROVIDER_NAME,
            credentials_loaded=False,
            token_stored=stored_tokens is not None,
            refresh_recommended=refresh_recommended,
            real_token_refresh_enabled=config.google_health_enable_real_token_refresh,
            attempted=False,
            request_prepared=False,
            refreshed=False,
            saved=False,
            request_preview=None,
            message="Google Health token refresh check skipped because credentials are not loaded.",
            error=credentials_result.error,
        )

    result = refresh_google_health_access_token_if_needed(
        config=config,
        credentials=credentials_result.credentials,
        token_store=store,
    )

    return GoogleHealthTokenRefreshCheckResponse(
        provider=GOOGLE_HEALTH_PROVIDER_NAME,
        credentials_loaded=True,
        token_stored=stored_tokens is not None,
        refresh_recommended=refresh_recommended,
        real_token_refresh_enabled=result.real_refresh_enabled,
        attempted=result.attempted,
        request_prepared=result.request_prepared,
        refreshed=result.refreshed,
        saved=result.saved,
        request_preview=_build_preview_model(result.request_preview),
        message=result.message,
        error=result.error,
    )


def _build_preview_model(
    preview: GoogleHealthRefreshRequestPreview | None,
) -> GoogleHealthRefreshRequestPreviewModel | None:
    if preview is None:
        return None

    return GoogleHealthRefreshRequestPreviewModel(
        endpoint=preview.endpoint,
        grant_type=preview.grant_type,
        has_client_id=preview.has_client_id,
        has_client_secret=preview.has_client_secret,
        has_refresh_token=preview.has_refresh_token,
    )
