from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import AppConfig, GOOGLE_HEALTH_SLEEP_READONLY_SCOPE
from app.services.google_health_connection_ux import (
    GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED,
    GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY,
    GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE,
    GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED,
    GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED,
    get_google_health_connection_ux,
)
from app.services.google_health_token_store import GoogleHealthTokenStore


_CALLBACK_URL = "http://127.0.0.1:8000/google-health/oauth/callback"


def _config(**overrides: object) -> AppConfig:
    values = {
        "conversation_engine": "mock",
        "sleep_provider": "mock",
        "google_health_credentials_file": None,
        "google_health_redirect_uri": None,
        "google_health_oauth_scopes": (GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,),
        "google_health_required_sleep_scope": GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,
        "google_health_enable_real_token_exchange": False,
        "google_health_enable_real_token_refresh": False,
        "google_health_enable_real_api_requests": False,
        "google_health_real_api_opt_in": False,
        "google_health_real_endpoint_verified": False,
    }
    values.update(overrides)
    return AppConfig(**values)


def _isolated_token_store(tmp_dir: Path) -> GoogleHealthTokenStore:
    return GoogleHealthTokenStore(token_file=tmp_dir / "google_health_token.json")


def _write_credentials(path: Path) -> None:
    path.write_text(
        """
{
  "web": {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": [
      "http://127.0.0.1:8000/google-health/oauth/callback"
    ]
  }
}
""".strip(),
        encoding="utf-8",
    )


def _write_token(path: Path) -> None:
    path.write_text(
        f"""
{{
  "access_token": "test-access-token",
  "refresh_token": "test-refresh-token",
  "scope": "{GOOGLE_HEALTH_SLEEP_READONLY_SCOPE}",
  "token_type": "Bearer"
}}
""".strip(),
        encoding="utf-8",
    )


def _assert_user_facing_response_is_sanitized(ux: object) -> None:
    assert not hasattr(ux, "token_file"), "UX response must not expose token_file"
    assert not hasattr(ux, "commands"), "UX response must not expose developer commands"


def _check_mock_mode() -> None:
    with TemporaryDirectory() as tmp:
        token_store = _isolated_token_store(Path(tmp))
        ux = get_google_health_connection_ux(config=_config(), token_store=token_store)

    assert ux.state == GOOGLE_HEALTH_CONNECTION_UX_STATE_MOCK_MODE
    assert ux.sleep_provider == "mock"
    assert ux.real_api_allowed is False
    assert ux.can_use_guarded_real_request is False
    assert ux.token_stored is False
    _assert_user_facing_response_is_sanitized(ux)


def _check_not_configured() -> None:
    with TemporaryDirectory() as tmp:
        token_store = _isolated_token_store(Path(tmp))
        ux = get_google_health_connection_ux(
            config=_config(sleep_provider="google_health"),
            token_store=token_store,
        )

    assert ux.state == GOOGLE_HEALTH_CONNECTION_UX_STATE_NOT_CONFIGURED
    assert ux.sleep_provider == "google_health"
    assert ux.can_start_oauth is False
    assert ux.real_api_allowed is False
    _assert_user_facing_response_is_sanitized(ux)


def _check_authorization_required() -> None:
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        credentials_path = tmp_dir / "credentials.json"
        _write_credentials(credentials_path)
        token_store = _isolated_token_store(tmp_dir)

        ux = get_google_health_connection_ux(
            config=_config(
                sleep_provider="google_health",
                google_health_credentials_file=str(credentials_path),
                google_health_redirect_uri=_CALLBACK_URL,
                google_health_oauth_scopes=(GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,),
            ),
            token_store=token_store,
        )

    assert ux.state == GOOGLE_HEALTH_CONNECTION_UX_STATE_AUTHORIZATION_REQUIRED
    assert ux.can_start_oauth is True
    assert ux.token_stored is False
    assert ux.real_api_allowed is False
    _assert_user_facing_response_is_sanitized(ux)


def _check_real_request_disabled() -> None:
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        credentials_path = tmp_dir / "credentials.json"
        _write_credentials(credentials_path)
        token_store = _isolated_token_store(tmp_dir)
        _write_token(token_store.token_file)

        ux = get_google_health_connection_ux(
            config=_config(
                sleep_provider="google_health",
                google_health_credentials_file=str(credentials_path),
                google_health_redirect_uri=_CALLBACK_URL,
                google_health_oauth_scopes=(GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,),
            ),
            token_store=token_store,
        )

    assert ux.state == GOOGLE_HEALTH_CONNECTION_UX_STATE_REAL_REQUEST_DISABLED
    assert ux.token_stored is True
    assert ux.real_api_requested is False
    assert ux.real_api_allowed is False
    assert ux.can_use_guarded_real_request is False
    _assert_user_facing_response_is_sanitized(ux)


def _check_guarded_real_request_ready() -> None:
    with TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        credentials_path = tmp_dir / "credentials.json"
        _write_credentials(credentials_path)
        token_store = _isolated_token_store(tmp_dir)
        _write_token(token_store.token_file)

        ux = get_google_health_connection_ux(
            config=_config(
                sleep_provider="google_health",
                google_health_credentials_file=str(credentials_path),
                google_health_redirect_uri=_CALLBACK_URL,
                google_health_oauth_scopes=(GOOGLE_HEALTH_SLEEP_READONLY_SCOPE,),
                google_health_enable_real_api_requests=True,
                google_health_real_api_opt_in=True,
                google_health_real_endpoint_verified=True,
            ),
            token_store=token_store,
        )

    assert ux.state == GOOGLE_HEALTH_CONNECTION_UX_STATE_GUARDED_REAL_REQUEST_READY
    assert ux.token_stored is True
    assert ux.real_api_requested is True
    assert ux.real_api_allowed is True
    assert ux.can_use_guarded_real_request is True
    _assert_user_facing_response_is_sanitized(ux)


def main() -> None:
    _check_mock_mode()
    _check_not_configured()
    _check_authorization_required()
    _check_real_request_disabled()
    _check_guarded_real_request_ready()

    print("[google-health-connection-ux-check-v0.29.0] OK")


if __name__ == "__main__":
    main()
