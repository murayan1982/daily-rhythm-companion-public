from __future__ import annotations

import json
import os
import shutil
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
BACKEND_ENV_FILE = BACKEND_ROOT / ".env"
GOOGLE_HEALTH_TOKEN_FILE = BACKEND_ROOT / "local_data" / "google_health_tokens.json"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


SECRET_VALUES = (
    "ya29.secret-google-health-access-token",
    "refresh-token-test-value",
    "client-secret-test-value",
    "Bearer test-access-token",
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_response_does_not_leak_secrets(payload: object, label: str) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for secret in SECRET_VALUES:
        _assert(secret not in rendered, f"{label} leaked secret value")


@contextmanager
def _temporary_backend_env(contents: str) -> Iterator[None]:
    """Temporarily replace backend/.env so load_config sees test settings."""

    backup_file = BACKEND_ENV_FILE.with_suffix(".env.check-backup")
    had_env = BACKEND_ENV_FILE.exists()

    if backup_file.exists():
        backup_file.unlink()

    if had_env:
        shutil.copy2(BACKEND_ENV_FILE, backup_file)

    BACKEND_ENV_FILE.write_text(contents, encoding="utf-8")

    try:
        yield
    finally:
        if had_env:
            shutil.move(str(backup_file), str(BACKEND_ENV_FILE))
        else:
            BACKEND_ENV_FILE.unlink(missing_ok=True)

        backup_file.unlink(missing_ok=True)


@contextmanager
def _temporary_google_health_token_file() -> Iterator[Path]:
    """Temporarily isolate the default Google Health local token file."""

    backup_file = GOOGLE_HEALTH_TOKEN_FILE.with_suffix(".json.check-backup")
    had_token = GOOGLE_HEALTH_TOKEN_FILE.exists()

    if backup_file.exists():
        backup_file.unlink()

    if had_token:
        GOOGLE_HEALTH_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(GOOGLE_HEALTH_TOKEN_FILE, backup_file)

    GOOGLE_HEALTH_TOKEN_FILE.unlink(missing_ok=True)

    try:
        yield GOOGLE_HEALTH_TOKEN_FILE
    finally:
        GOOGLE_HEALTH_TOKEN_FILE.unlink(missing_ok=True)

        if had_token:
            GOOGLE_HEALTH_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup_file), str(GOOGLE_HEALTH_TOKEN_FILE))

        backup_file.unlink(missing_ok=True)


@contextmanager
def _temporary_google_credentials_file() -> Iterator[Path]:
    credentials_file = BACKEND_ROOT / "google_health_test_credentials.json"
    credentials_file.write_text(
        json.dumps(
            {
                "web": {
                    "client_id": "client-id-test-value",
                    "client_secret": "client-secret-test-value",
                    "auth_uri": "https://oauth2.example.test/auth",
                    "token_uri": "https://oauth2.example.test/token",
                    "redirect_uris": [
                        "http://127.0.0.1:8000/google-health/callback"
                    ],
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    try:
        yield credentials_file
    finally:
        credentials_file.unlink(missing_ok=True)


def _env_contents(*, sleep_provider: str, credentials_file: Path | None = None) -> str:
    lines = [
        "CONVERSATION_ENGINE=mock",
        f"SLEEP_PROVIDER={sleep_provider}",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0",
        "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0",
        "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0",
        "GOOGLE_HEALTH_API_BASE_URL=https://example.invalid/google-health",
    ]

    if credentials_file is not None:
        lines.append(f"GOOGLE_HEALTH_CREDENTIALS_FILE={credentials_file}")
    else:
        lines.append("GOOGLE_HEALTH_CREDENTIALS_FILE=")

    return "\n".join(lines) + "\n"


def _write_valid_google_health_tokens(token_file: Path) -> None:
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(
        json.dumps(
            {
                "access_token": "ya29.secret-google-health-access-token",
                "token_type": "Bearer",
                "refresh_token": "refresh-token-test-value",
                "scope": "scope-a scope-b",
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(hours=1)
                ).isoformat(),
                "source": "test",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _get_sleep_summary() -> dict[str, object]:
    client = TestClient(app)
    response = client.get("/sleep/summary")
    _assert(response.status_code == 200, f"expected 200, got {response.status_code}: {response.text}")
    return response.json()


def _check_mock_sleep_summary_still_works() -> None:
    with _temporary_backend_env(_env_contents(sleep_provider="mock")):
        payload = _get_sleep_summary()

    _assert(payload["source"] == "mock", "mock provider should still return mock source")
    _assert(payload["available"] is True, "mock provider should remain available")
    _assert_response_does_not_leak_secrets(payload, "mock sleep summary response")


def _check_google_health_without_tokens_returns_needs_auth_response() -> None:
    with _temporary_google_credentials_file() as credentials_file:
        with _temporary_backend_env(
            _env_contents(
                sleep_provider="google_health",
                credentials_file=credentials_file,
            )
        ):
            with _temporary_google_health_token_file():
                payload = _get_sleep_summary()

    _assert(payload["source"] == "google_health", "Google Health response should identify source")
    _assert(payload["available"] is False, "missing token response should be unavailable")
    _assert(payload["total_sleep_minutes"] == 0, "guarded response should not invent sleep data")
    _assert("not connected" in (payload.get("message") or ""), "missing token response should explain auth is needed")
    _assert_response_does_not_leak_secrets(payload, "Google Health missing-token response")


def _check_google_health_valid_token_stays_guarded_when_real_api_disabled() -> None:
    with _temporary_google_credentials_file() as credentials_file:
        with _temporary_backend_env(
            _env_contents(
                sleep_provider="google_health",
                credentials_file=credentials_file,
            )
        ):
            with _temporary_google_health_token_file() as token_file:
                _write_valid_google_health_tokens(token_file)
                payload = _get_sleep_summary()

    _assert(payload["source"] == "google_health", "Google Health response should identify source")
    _assert(payload["available"] is False, "disabled real API response should be unavailable")
    _assert(payload["total_sleep_minutes"] == 0, "guarded response should not expose raw data")
    _assert("disabled" in (payload.get("message") or ""), "disabled API response should explain guarded state")
    _assert_response_does_not_leak_secrets(payload, "Google Health guarded API response")


def _check_invalid_provider_returns_400() -> None:
    client = TestClient(app)

    with _temporary_backend_env(_env_contents(sleep_provider="unknown_provider")):
        response = client.get("/sleep/summary")

    _assert(response.status_code == 400, f"invalid provider should return 400, got {response.status_code}")
    _assert("Unsupported sleep provider" in response.text, "invalid provider response should explain the configuration issue")


def main() -> None:
    # Avoid inherited environment values interfering with the temporary .env checks.
    for key in tuple(os.environ):
        if key.startswith("GOOGLE_HEALTH_") or key == "SLEEP_PROVIDER":
            os.environ.pop(key, None)

    _check_mock_sleep_summary_still_works()
    _check_google_health_without_tokens_returns_needs_auth_response()
    _check_google_health_valid_token_stays_guarded_when_real_api_disabled()
    _check_invalid_provider_returns_400()
    print("[sleep-summary-api-provider-boundary-check] OK")


if __name__ == "__main__":
    main()
