from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig  # noqa: E402
from app.services.google_health_api_client import (  # noqa: E402
    GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
    build_google_health_api_endpoint,
    build_google_health_api_request_preview,
    get_google_health_json_with_tokens_if_enabled,
    prepare_google_health_api_get_request,
)
from app.services.google_health_token_store import StoredGoogleHealthTokens  # noqa: E402


SECRET_ACCESS_TOKEN = "ya29.secret-google-health-access-token"
SECRET_AUTH_HEADER = f"Bearer {SECRET_ACCESS_TOKEN}"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_not_leaked(value: object, secret: str, label: str) -> None:
    rendered = repr(value)
    _assert(secret not in rendered, f"{label} leaked secret in repr()")

    if hasattr(value, "__dataclass_fields__"):
        rendered_dict = repr(asdict(value))
        _assert(secret not in rendered_dict, f"{label} leaked secret in asdict()")


def _check_endpoint_builder() -> None:
    endpoint = build_google_health_api_endpoint(
        base_url="https://example.invalid/google-health/",
        path="/v1/sleep:summary",
    )

    _assert(
        endpoint == "https://example.invalid/google-health/v1/sleep:summary",
        "endpoint builder should join base URL and path predictably",
    )


def _check_prepare_request_boundary() -> None:
    result = prepare_google_health_api_get_request(
        endpoint="https://example.invalid/google-health/v1/sleep:summary",
        access_token=SECRET_ACCESS_TOKEN,
        query_params={"date": "2026-05-04"},
    )

    _assert(result.request_prepared, "request should be prepared")
    _assert(result.request_parts is not None, "request parts should exist")
    _assert(result.request_preview is not None, "request preview should exist")
    _assert(
        result.request_parts.headers.get("Authorization") == SECRET_AUTH_HEADER,
        "internal request parts should contain bearer auth",
    )
    _assert(
        result.request_preview.has_bearer_auth,
        "preview should indicate bearer auth without exposing it",
    )
    _assert(
        result.request_preview.query_param_keys == ("date",),
        "preview should expose query param keys only",
    )

    _assert_not_leaked(result.request_preview, SECRET_ACCESS_TOKEN, "request preview")
    _assert_not_leaked(result.request_preview, SECRET_AUTH_HEADER, "request preview")


def _check_preview_builder_boundary() -> None:
    prepared = prepare_google_health_api_get_request(
        endpoint="https://example.invalid/google-health/v1/sleep:summary",
        access_token=SECRET_ACCESS_TOKEN,
        query_params={"date": "2026-05-04", "timezone": "Asia/Tokyo"},
    )

    assert prepared.request_parts is not None
    preview = build_google_health_api_request_preview(prepared.request_parts)

    _assert(
        preview.query_param_keys == ("date", "timezone"),
        "preview should sort query param keys",
    )
    _assert_not_leaked(preview, SECRET_ACCESS_TOKEN, "direct preview")
    _assert_not_leaked(preview, SECRET_AUTH_HEADER, "direct preview")


def _check_guarded_api_request_boundary() -> None:
    config = AppConfig(
        google_health_enable_real_api_requests=False,
    )
    tokens = StoredGoogleHealthTokens(
        access_token=SECRET_ACCESS_TOKEN,
        token_type="Bearer",
        refresh_token="refresh-token-should-not-matter-here",
    )

    result = get_google_health_json_with_tokens_if_enabled(
        config=config,
        endpoint="https://example.invalid/google-health/v1/sleep:summary",
        stored_tokens=tokens,
        query_params={"date": "2026-05-04"},
    )

    _assert(not result.attempted, "disabled real API requests should not attempt HTTP")
    _assert(result.request_prepared, "disabled request should still be prepared")
    _assert(
        result.error == GOOGLE_HEALTH_API_CLIENT_ERROR_API_REQUEST_DISABLED,
        "disabled request should return the guard error",
    )
    _assert(result.request_preview is not None, "disabled request should expose preview")
    _assert_not_leaked(result.request_preview, SECRET_ACCESS_TOKEN, "guarded result preview")
    _assert_not_leaked(result.request_preview, SECRET_AUTH_HEADER, "guarded result preview")


def main() -> None:
    _check_endpoint_builder()
    _check_prepare_request_boundary()
    _check_preview_builder_boundary()
    _check_guarded_api_request_boundary()
    print("[google-health-api-client-boundary-check] OK")


if __name__ == "__main__":
    main()
