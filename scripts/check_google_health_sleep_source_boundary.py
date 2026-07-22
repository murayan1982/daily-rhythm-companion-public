from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import asdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig  # noqa: E402
from app.services.google_health_credentials import (  # noqa: E402
    GoogleHealthOAuthCredentials,
)
from app.services.google_health_sleep_source import (  # noqa: E402
    GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED,
    GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_AUTH,
    GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_REFRESH_REQUIRED,
    fetch_google_health_sleep_summary,
)
from app.services.google_health_token_store import GoogleHealthTokenStore  # noqa: E402
from app.services.sleep_providers.factory import (  # noqa: E402
    SUPPORTED_SLEEP_PROVIDERS,
    create_sleep_provider,
)
from app.services.sleep_providers.google_health import (  # noqa: E402
    GoogleHealthSleepProvider,
)


SECRET_VALUES = (
    "ya29.secret-google-health-access-token",
    "refresh-token-test-value",
    "client-secret-test-value",
    "Bearer test-access-token",
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_not_leaked(value: object, label: str) -> None:
    rendered = repr(value)
    for secret in SECRET_VALUES:
        _assert(secret not in rendered, f"{label} leaked secret in repr()")

    if hasattr(value, "__dataclass_fields__"):
        rendered_dict = repr(asdict(value))
        for secret in SECRET_VALUES:
            _assert(secret not in rendered_dict, f"{label} leaked secret in asdict()")


def _check_missing_tokens_returns_needs_auth_summary() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        result = fetch_google_health_sleep_summary(
            config=_config(),
            credentials=_credentials(),
            token_store=GoogleHealthTokenStore(
                token_file=Path(temp_dir) / "missing_tokens.json"
            ),
            target_date=date(2026, 5, 4),
        )

    _assert(result.status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_NEEDS_AUTH, "missing tokens should request auth")
    _assert(not result.summary.available, "missing tokens should be unavailable")
    _assert(result.summary.source == "google_health", "summary source should identify Google Health")
    _assert(result.summary.date == "2026-05-04", "summary should preserve target date")
    _assert_not_leaked(result, "missing token sleep source result")


def _check_valid_token_prepares_guarded_api_without_raw_payload() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        token_file = Path(temp_dir) / "google_health_tokens.json"
        _write_tokens(
            token_file=token_file,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        result = fetch_google_health_sleep_summary(
            config=_config(),
            credentials=_credentials(),
            token_store=GoogleHealthTokenStore(token_file=token_file),
            target_date=date(2026, 5, 4),
        )

    _assert(
        result.status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_API_DISABLED,
        "guarded API request should stay disabled",
    )
    _assert(not result.summary.available, "disabled real API should be unavailable")
    _assert(result.session is not None, "session summary should exist")
    _assert(result.session.api_summary is not None, "API summary should exist")
    _assert(result.session.api_summary.request_preview is not None, "safe request preview should exist")
    preview = result.session.api_summary.request_preview
    _assert(
        preview.query_param_keys == ("filter",),
        "sleep source should pass the current Google Health filter query parameter",
    )
    _assert(
        preview.query_params.get("filter")
        == 'sleep.interval.civil_end_time >= "2026-05-04" '
        'AND sleep.interval.civil_end_time < "2026-05-05"',
        "sleep source should pass the guarded target civil-end-date filter",
    )
    _assert(not hasattr(result.session.api_summary, "response"), "safe API summary should not expose raw response")
    _assert_not_leaked(result, "valid token sleep source result")


def _check_expired_token_does_not_reach_api_when_refresh_is_guarded() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        token_file = Path(temp_dir) / "google_health_tokens.json"
        _write_tokens(
            token_file=token_file,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )

        result = fetch_google_health_sleep_summary(
            config=_config(),
            credentials=_credentials(),
            token_store=GoogleHealthTokenStore(token_file=token_file),
            target_date=date(2026, 5, 4),
        )

    _assert(
        result.status == GOOGLE_HEALTH_SLEEP_SOURCE_STATUS_REFRESH_REQUIRED,
        "expired token should report refresh-required boundary",
    )
    _assert(not result.summary.available, "refresh-required result should be unavailable")
    _assert(result.session is not None, "session summary should exist")
    _assert(not result.session.api_requested, "API should not be requested before refresh completes")
    _assert_not_leaked(result, "expired token sleep source result")


def _check_factory_supports_google_health_provider() -> None:
    provider = create_sleep_provider(AppConfig(sleep_provider="google_health"))

    _assert("google_health" in SUPPORTED_SLEEP_PROVIDERS, "factory should list google_health provider")
    _assert(isinstance(provider, GoogleHealthSleepProvider), "factory should create GoogleHealthSleepProvider")


def _write_tokens(
    *,
    token_file: Path,
    expires_at: datetime,
) -> None:
    token_file.write_text(
        json.dumps(
            {
                "access_token": "ya29.secret-google-health-access-token",
                "token_type": "Bearer",
                "refresh_token": "refresh-token-test-value",
                "scope": "scope-a scope-b",
                "expires_at": expires_at.isoformat(),
                "source": "test",
            }
        ),
        encoding="utf-8",
    )


def _config() -> AppConfig:
    return AppConfig(
        google_health_enable_real_token_refresh=False,
        google_health_enable_real_api_requests=False,
        google_health_api_base_url="https://example.invalid/google-health",
    )


def _credentials() -> GoogleHealthOAuthCredentials:
    return GoogleHealthOAuthCredentials(
        client_id="client-id-test-value",
        client_secret="client-secret-test-value",
        auth_uri="https://oauth2.example.test/auth",
        token_uri="https://oauth2.example.test/token",
        redirect_uris=("http://127.0.0.1:8000/google-health/callback",),
    )


def main() -> None:
    _check_missing_tokens_returns_needs_auth_summary()
    _check_valid_token_prepares_guarded_api_without_raw_payload()
    _check_expired_token_does_not_reach_api_when_refresh_is_guarded()
    _check_factory_supports_google_health_provider()
    print("[google-health-sleep-source-boundary-check] OK")


if __name__ == "__main__":
    main()
