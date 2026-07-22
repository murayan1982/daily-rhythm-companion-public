from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig  # noqa: E402
from app.services.google_health_credentials import (  # noqa: E402
    GoogleHealthOAuthCredentials,
)
from app.services.google_health_token_refresh import (  # noqa: E402
    GOOGLE_HEALTH_TOKEN_REFRESH_ERROR_NO_STORED_TOKENS,
    prepare_google_health_token_refresh_request,
    refresh_google_health_access_token_if_needed,
)
from app.services.google_health_token_store import (  # noqa: E402
    GoogleHealthTokenStore,
)


SECRET_VALUES = (
    "client-secret-test-value",
    "refresh-token-test-value",
    "access-token-test-value",
)


def main() -> None:
    _check_store_expiry_and_refresh_decision()
    _check_refresh_request_preview_hides_sensitive_values()
    _check_refresh_is_guarded_when_disabled()
    _check_missing_tokens_result()
    print("[google-health-token-boundary-check] OK")


def _check_store_expiry_and_refresh_decision() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        token_file = Path(temp_dir) / "google_health_tokens.json"
        token_file.write_text(
            json.dumps(
                {
                    "access_token": "access-token-test-value",
                    "token_type": "Bearer",
                    "refresh_token": "refresh-token-test-value",
                    "scope": "scope-a scope-b",
                    "expires_at": (
                        datetime.now(timezone.utc) - timedelta(minutes=1)
                    ).isoformat(),
                    "source": "test",
                }
            ),
            encoding="utf-8",
        )

        tokens = GoogleHealthTokenStore(token_file=token_file).load_tokens()

        assert tokens is not None
        assert tokens.is_access_token_expired()
        assert tokens.should_refresh_access_token()


def _check_refresh_request_preview_hides_sensitive_values() -> None:
    result = prepare_google_health_token_refresh_request(
        token_uri="https://oauth2.example.test/token",
        client_id="client-id-test-value",
        client_secret="client-secret-test-value",
        refresh_token="refresh-token-test-value",
    )

    assert result.request_prepared
    assert result.request_parts is not None
    assert result.request_preview is not None
    assert result.request_parts.form_data["client_secret"] == (
        "client-secret-test-value"
    )
    assert result.request_parts.form_data["refresh_token"] == (
        "refresh-token-test-value"
    )

    preview_text = repr(result.request_preview)
    assert "has_client_secret=True" in preview_text
    assert "has_refresh_token=True" in preview_text
    _assert_no_secret_values(preview_text)


def _check_refresh_is_guarded_when_disabled() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        token_file = Path(temp_dir) / "google_health_tokens.json"
        token_file.write_text(
            json.dumps(
                {
                    "access_token": "access-token-test-value",
                    "token_type": "Bearer",
                    "refresh_token": "refresh-token-test-value",
                    "expires_at": (
                        datetime.now(timezone.utc) - timedelta(minutes=1)
                    ).isoformat(),
                }
            ),
            encoding="utf-8",
        )

        result = refresh_google_health_access_token_if_needed(
            config=AppConfig(google_health_enable_real_token_refresh=False),
            credentials=_credentials(),
            token_store=GoogleHealthTokenStore(token_file=token_file),
        )

        assert not result.attempted
        assert result.request_prepared
        assert not result.real_refresh_enabled
        assert not result.refreshed
        assert not result.saved
        assert result.request_parts is not None
        assert result.request_preview is not None
        _assert_no_secret_values(repr(result.request_preview))


def _check_missing_tokens_result() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        result = refresh_google_health_access_token_if_needed(
            config=AppConfig(google_health_enable_real_token_refresh=False),
            credentials=_credentials(),
            token_store=GoogleHealthTokenStore(
                token_file=Path(temp_dir) / "missing_tokens.json"
            ),
        )

        assert not result.attempted
        assert not result.request_prepared
        assert result.error == GOOGLE_HEALTH_TOKEN_REFRESH_ERROR_NO_STORED_TOKENS


def _credentials() -> GoogleHealthOAuthCredentials:
    return GoogleHealthOAuthCredentials(
        client_id="client-id-test-value",
        client_secret="client-secret-test-value",
        auth_uri="https://oauth2.example.test/auth",
        token_uri="https://oauth2.example.test/token",
        redirect_uris=("http://127.0.0.1:8000/google-health/callback",),
    )


def _assert_no_secret_values(text: str) -> None:
    for secret_value in SECRET_VALUES:
        assert secret_value not in text


if __name__ == "__main__":
    main()
