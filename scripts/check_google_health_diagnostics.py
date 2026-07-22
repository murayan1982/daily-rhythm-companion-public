from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.config import AppConfig
from app.services.google_health_diagnostics import (
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_BLOCKED,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_DISABLED,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_MOCK_MODE,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_AUTH,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_CREDENTIALS,
    GOOGLE_HEALTH_DIAGNOSTICS_STATUS_READY_FOR_REAL_API,
    get_google_health_diagnostics,
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
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        credentials_file = temp_path / "credentials.json"
        token_file = temp_path / "google_health_tokens.json"
        isolated_token_store = GoogleHealthTokenStore(token_file=token_file)

        # Keep the check hermetic. A developer may already have an ignored local
        # OAuth token snapshot under backend/local_data/, but source-tree checks
        # must never read or depend on that private operator state.
        default_diagnostics = get_google_health_diagnostics(
            AppConfig(),
            token_store=isolated_token_store,
        )
        assert default_diagnostics.overall_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_MOCK_MODE
        assert not default_diagnostics.ready_for_oauth
        assert not default_diagnostics.ready_for_sleep_provider
        assert not default_diagnostics.ready_for_real_api_request
        assert not default_diagnostics.token.stored

        needs_credentials = get_google_health_diagnostics(
            AppConfig(sleep_provider="google_health"),
            token_store=isolated_token_store,
        )
        assert needs_credentials.overall_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_CREDENTIALS
        assert needs_credentials.error == "credentials_file_not_configured"

        _write_credentials(credentials_file)

        configured = AppConfig(
            sleep_provider="google_health",
            google_health_credentials_file=str(credentials_file),
            google_health_redirect_uri="http://127.0.0.1:8000/google-health/callback",
        )
        empty_token_store = GoogleHealthTokenStore(token_file=token_file)
        needs_auth = get_google_health_diagnostics(
            configured,
            token_store=empty_token_store,
        )
        assert needs_auth.overall_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_NEEDS_AUTH
        assert needs_auth.ready_for_oauth
        assert not needs_auth.token.stored
        assert not needs_auth.ready_for_sleep_provider

        _write_tokens(token_file)
        stored_token_store = GoogleHealthTokenStore(token_file=token_file)
        api_disabled = get_google_health_diagnostics(
            configured,
            token_store=stored_token_store,
        )
        assert api_disabled.overall_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_DISABLED
        assert api_disabled.ready_for_sleep_provider
        assert not api_disabled.ready_for_real_api_request
        assert api_disabled.token.stored
        assert api_disabled.token.has_refresh_token
        assert api_disabled.token.scope_configured
        assert api_disabled.token.token_type == "Bearer"

        api_blocked = get_google_health_diagnostics(
            AppConfig(
                sleep_provider="google_health",
                google_health_credentials_file=str(credentials_file),
                google_health_redirect_uri="http://127.0.0.1:8000/google-health/callback",
                google_health_enable_real_api_requests=True,
            ),
            token_store=stored_token_store,
        )
        assert api_blocked.overall_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_API_BLOCKED
        assert not api_blocked.runtime_guard.api_base_url_placeholder
        assert not api_blocked.runtime_guard.endpoint_verified
        assert not api_blocked.ready_for_real_api_request
        assert api_blocked.error == "endpoint_not_verified"

        api_ready = get_google_health_diagnostics(
            AppConfig(
                sleep_provider="google_health",
                google_health_credentials_file=str(credentials_file),
                google_health_redirect_uri="http://127.0.0.1:8000/google-health/callback",
                google_health_enable_real_api_requests=True,
                google_health_real_endpoint_verified=True,
                google_health_real_api_opt_in=True,
                google_health_api_timeout_seconds=5,
            ),
            token_store=stored_token_store,
        )
        assert api_ready.overall_status == GOOGLE_HEALTH_DIAGNOSTICS_STATUS_READY_FOR_REAL_API
        assert api_ready.ready_for_oauth
        assert api_ready.ready_for_sleep_provider
        assert api_ready.ready_for_real_api_request
        assert not api_ready.runtime_guard.api_base_url_placeholder
        assert api_ready.error is None

    print("[google-health-diagnostics-check] OK")


if __name__ == "__main__":
    main()
