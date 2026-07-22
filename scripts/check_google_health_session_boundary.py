from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig  # noqa: E402
from app.services.google_health_credentials import (  # noqa: E402
    GoogleHealthOAuthCredentials,
)
from app.services.google_health_session import (  # noqa: E402
    GOOGLE_HEALTH_SESSION_ERROR_NO_STORED_TOKENS,
    GOOGLE_HEALTH_SESSION_ERROR_REFRESH_NOT_COMPLETED,
    get_google_health_json_after_refresh_if_needed,
    summarize_google_health_api_client_result,
    summarize_google_health_token_refresh_result,
)
from app.services.google_health_api_client import (  # noqa: E402
    GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
    get_google_health_json_with_tokens_if_enabled,
)
from app.services.google_health_token_refresh import (  # noqa: E402
    prepare_google_health_token_refresh_request,
)
from app.services.google_health_token_store import (  # noqa: E402
    GoogleHealthTokenStore,
    StoredGoogleHealthTokens,
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


def _check_missing_tokens_skips_refresh_and_api() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        result = get_google_health_json_after_refresh_if_needed(
            config=_config(),
            credentials=_credentials(),
            api_path="/v1/sleep:summary",
            token_store=GoogleHealthTokenStore(
                token_file=Path(temp_dir) / "missing_tokens.json"
            ),
        )

    _assert(not result.token_available, "missing token result should mark token unavailable")
    _assert(not result.refresh_checked, "missing tokens should not trigger refresh")
    _assert(not result.api_requested, "missing tokens should not request API")
    _assert(result.error == GOOGLE_HEALTH_SESSION_ERROR_NO_STORED_TOKENS, "missing token error should be explicit")
    _assert_not_leaked(result, "missing token session result")


def _check_valid_token_flows_to_guarded_api_client() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        token_file = Path(temp_dir) / "google_health_tokens.json"
        _write_tokens(
            token_file=token_file,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        result = get_google_health_json_after_refresh_if_needed(
            config=_config(),
            credentials=_credentials(),
            api_path="/v1/sleep:summary",
            query_params={"date": "2026-05-04"},
            token_store=GoogleHealthTokenStore(token_file=token_file),
        )

    _assert(result.token_available, "valid token should be available")
    _assert(not result.refresh_checked, "valid token should not refresh")
    _assert(result.api_requested, "valid token should flow to API client")
    _assert(result.api_summary is not None, "API summary should exist")
    _assert(result.api_summary.request_prepared, "API request should be prepared")
    _assert(
        result.api_summary.error == GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
        "guarded API client should return disabled error",
    )
    _assert_not_leaked(result, "valid token session result")


def _check_expired_token_skips_api_when_refresh_is_not_completed() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        token_file = Path(temp_dir) / "google_health_tokens.json"
        _write_tokens(
            token_file=token_file,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )

        result = get_google_health_json_after_refresh_if_needed(
            config=_config(),
            credentials=_credentials(),
            api_path="/v1/sleep:summary",
            query_params={"date": "2026-05-04"},
            token_store=GoogleHealthTokenStore(token_file=token_file),
        )

    _assert(result.token_available, "expired token should still be loaded")
    _assert(result.refresh_checked, "expired token should check refresh")
    _assert(not result.api_requested, "API should be skipped when refresh does not complete")
    _assert(result.refresh_summary is not None, "refresh summary should exist")
    _assert(result.refresh_summary.request_prepared, "refresh request should be prepared")
    _assert(
        result.error == GOOGLE_HEALTH_SESSION_ERROR_REFRESH_NOT_COMPLETED,
        "incomplete guarded refresh should be explicit",
    )
    _assert_not_leaked(result, "expired token session result")


def _check_safe_summaries_do_not_include_internal_request_parts() -> None:
    refresh_result = prepare_google_health_token_refresh_request(
        token_uri="https://oauth2.example.test/token",
        client_id="client-id-test-value",
        client_secret="client-secret-test-value",
        refresh_token="refresh-token-test-value",
    )
    refresh_summary = summarize_google_health_token_refresh_result(refresh_result)

    _assert(refresh_result.request_parts is not None, "test refresh result should have request parts")
    _assert_not_leaked(refresh_summary, "refresh summary")

    api_result = get_google_health_json_with_tokens_if_enabled(
        config=_config(),
        endpoint="https://example.invalid/google-health/v1/sleep:summary",
        stored_tokens=StoredGoogleHealthTokens(
            access_token="ya29.secret-google-health-access-token",
            token_type="Bearer",
            refresh_token="refresh-token-test-value",
        ),
        query_params={"date": "2026-05-04"},
    )
    api_summary = summarize_google_health_api_client_result(api_result)

    _assert(api_result.request_parts is not None, "test API result should have request parts")
    _assert_not_leaked(api_summary, "API summary")


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
    _check_missing_tokens_skips_refresh_and_api()
    _check_valid_token_flows_to_guarded_api_client()
    _check_expired_token_skips_api_when_refresh_is_not_completed()
    _check_safe_summaries_do_not_include_internal_request_parts()
    print("[google-health-session-boundary-check] OK")


if __name__ == "__main__":
    main()
