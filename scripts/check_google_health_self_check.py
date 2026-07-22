from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import AppConfig
from app.services.google_health_api_client import (
    GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
    GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG,
)
from app.services.google_health_diagnostics import (
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_BLOCKED,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_DISABLED,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_MOCK_MODE,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_AUTH,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_CREDENTIALS,
)
from app.services.google_health_self_check import (
    GOOGLE_HEALTH_SELF_CHECK_STATUS_SKIPPED,
    run_google_health_self_check,
)
from app.services.google_health_sleep_source import (
    GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED,
    GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_AUTH,
    GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_CREDENTIALS,
)
from app.services.google_health_token_store import GoogleHealthTokenStore


def _write_credentials(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "web": {
                    "client_id": "test-client-id",
                    "client_secret": "test-client-secret",
                    "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [
                        "http://127.0.0.1:8000/google-health/callback"
                    ],
                }
            }
        ),
        encoding="utf-8",
    )


def _write_tokens(path: Path) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    path.write_text(
        json.dumps(
            {
                "access_token": "test-access-token",
                "token_type": "Bearer",
                "refresh_token": "test-refresh-token",
                "scope": "test-scope",
                "expires_at": expires_at.isoformat(),
            }
        ),
        encoding="utf-8",
    )


def main() -> None:
    target_date = date(2026, 5, 4)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        credentials_file = temp_path / "credentials.json"
        token_file = temp_path / "google_health_tokens.json"
        isolated_token_store = GoogleHealthTokenStore(token_file=token_file)

        # Keep source-tree checks independent from ignored private operator
        # tokens that may already exist under backend/local_data/.
        mock_mode = run_google_health_self_check(
            config=AppConfig(),
            target_date=target_date,
            token_store=isolated_token_store,
        )
        assert mock_mode.diagnostics_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_MOCK_MODE
        assert mock_mode.source_status == GOOGLE_HEALTH_SELF_CHECK_STATUS_SKIPPED
        assert not mock_mode.real_http_attempted
        assert mock_mode.session is None

        needs_credentials = run_google_health_self_check(
            config=AppConfig(sleep_provider="google_health"),
            target_date=target_date,
            token_store=isolated_token_store,
        )
        assert needs_credentials.diagnostics_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_CREDENTIALS
        assert needs_credentials.source_status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_CREDENTIALS
        assert not needs_credentials.safe_to_use_sleep_summary
        assert not needs_credentials.real_http_attempted
        assert needs_credentials.session is None

        _write_credentials(credentials_file)

        configured = AppConfig(
            sleep_provider="google_health",
            google_health_credentials_file=str(credentials_file),
            google_health_redirect_uri="http://127.0.0.1:8000/google-health/callback",
        )
        empty_store = GoogleHealthTokenStore(token_file=token_file)

        needs_auth = run_google_health_self_check(
            config=configured,
            target_date=target_date,
            token_store=empty_store,
        )
        assert needs_auth.diagnostics_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_AUTH
        assert needs_auth.source_status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_AUTH
        assert needs_auth.session is not None
        assert not needs_auth.session.token_available
        assert not needs_auth.session.api_requested
        assert not needs_auth.real_http_attempted

        _write_tokens(token_file)
        stored_store = GoogleHealthTokenStore(token_file=token_file)
        api_disabled = run_google_health_self_check(
            config=configured,
            target_date=target_date,
            token_store=stored_store,
        )
        assert api_disabled.diagnostics_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_DISABLED
        assert api_disabled.source_status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED
        assert api_disabled.session is not None
        assert api_disabled.session.api is not None
        assert api_disabled.session.api.request_prepared
        assert not api_disabled.session.api.attempted
        assert not api_disabled.real_http_attempted
        assert api_disabled.session.api.error == GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED
        assert api_disabled.session.api.request_preview is not None
        assert api_disabled.session.api.request_preview.has_bearer_auth
        assert api_disabled.session.api.request_preview.query_param_keys == ["filter"]
        filter_value = api_disabled.session.api.request_preview.query_params["filter"]
        assert filter_value.startswith('sleep.interval.civil_end_time >= "2026-05-04"')
        assert 'sleep.interval.civil_end_time < "2026-05-05"' in filter_value

        api_blocked = run_google_health_self_check(
            config=AppConfig(
                sleep_provider="google_health",
                google_health_credentials_file=str(credentials_file),
                google_health_redirect_uri="http://127.0.0.1:8000/google-health/callback",
                google_health_enable_real_api_requests=True,
            ),
            target_date=target_date,
            token_store=stored_store,
        )
        assert api_blocked.diagnostics_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_BLOCKED
        assert api_blocked.source_status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED
        assert api_blocked.session is not None
        assert api_blocked.session.api is not None
        assert api_blocked.session.api.request_prepared
        assert not api_blocked.session.api.attempted
        assert not api_blocked.real_http_attempted
        assert api_blocked.session.api.error == GOOGLE_HEALTH_API_CLIENT_ERROR_UNSAFE_REAL_API_CONFIG

    print("[google-health-self-check] OK")


if __name__ == "__main__":
    main()
