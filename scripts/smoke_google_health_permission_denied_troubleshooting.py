from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SCRIPT_NAME = "google-health-permission-denied-troubleshooting-smoke-v0.22.0"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
RAW_PAYLOAD_KEYS = {"data", "response", "raw_payload", "payload", "provider_response"}
SAFE_TROUBLESHOOTING_CATEGORIES = {
    "permission_denied",
    "auth_failed",
    "not_found",
    "rate_limited",
    "server_error",
    "http_error",
    "network_error",
    "invalid_response",
}

CHECKLIST = [
    "Confirm the Google Health API is enabled in the same Google Cloud project as the OAuth client.",
    "Confirm the OAuth consent screen includes the required Google Health sleep read scope.",
    "If scopes changed, reconnect/re-authorize so the local refresh token is minted with the new scope.",
    "Confirm the Google account is an allowed test user or the app is approved for the requested scope.",
    "Confirm credentials.json client_id/client_secret belong to the project where the Health API and consent screen are configured.",
    "Confirm the sleep endpoint path and query parameter names still match the official Google Health docs.",
]


class SmokeFailure(AssertionError):
    """Raised when the permission-denied troubleshooting smoke fails."""


class SmokeRefused(SmokeFailure):
    """Raised when explicit real-request consent was not provided."""


def _request_json(base_url: str, path: str) -> tuple[int, dict[str, Any]]:
    url = f"{base_url.rstrip('/')}{path}"
    request = Request(url, method="GET")

    try:
        with urlopen(request, timeout=20) as response:
            raw_body = response.read().decode("utf-8")
            return response.status, _loads_json_object(raw_body, url)
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        return exc.code, _loads_json_object(raw_body, url)
    except URLError as exc:
        raise SmokeFailure(
            f"Could not connect to {url}. Start the backend before running this smoke."
        ) from exc


def _loads_json_object(raw_body: str, url: str) -> dict[str, Any]:
    try:
        body = json.loads(raw_body) if raw_body else {}
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"{url} did not return JSON: {exc}") from exc

    if not isinstance(body, dict):
        raise SmokeFailure(f"{url} returned {type(body).__name__}, expected object.")

    return body


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def _require_allow_real_request(allow_real_request: bool) -> None:
    if not allow_real_request:
        raise SmokeRefused(
            "Refusing to run Google Health permission_denied troubleshooting without "
            "explicit operator consent. Re-run with --allow-real-request only during "
            "a narrow local troubleshooting window with the .env real request gates enabled."
        )


def _assert_preflight_allows_real_request(preflight: dict[str, Any]) -> None:
    api = preflight.get("api")
    _require(isinstance(api, dict), "preflight.api is missing or not an object.")

    for field in (
        "endpoint_verified",
        "real_api_requests_enabled",
        "real_api_opt_in",
        "real_api_requests_allowed",
    ):
        _require(
            api.get(field) is True,
            f"Expected preflight.api.{field}=True for a narrow troubleshooting run, "
            f"got {api.get(field)!r}.",
        )


def _assert_no_raw_payload_leaks(*, self_check: dict[str, Any], session: dict[str, Any], api: dict[str, Any]) -> None:
    for container_name, container in (
        ("self_check", self_check),
        ("session", session),
        ("session.api", api),
    ):
        leaked_keys = RAW_PAYLOAD_KEYS.intersection(container.keys())
        _require(
            not leaked_keys,
            f"{container_name} exposed raw provider payload-like keys: {sorted(leaked_keys)}.",
        )


def _extract_api_result(self_check: dict[str, Any]) -> tuple[int, str, str]:
    session = self_check.get("session") or {}
    api = session.get("api") or {}
    _require(isinstance(session, dict), "self-check.session is not an object.")
    _require(isinstance(api, dict), "self-check.session.api is not an object.")

    _require(
        self_check.get("real_http_attempted") is True,
        "Expected real_http_attempted=True during permission_denied troubleshooting.",
    )
    _require(
        self_check.get("safe_to_use_sleep_summary") is False,
        "Expected safe_to_use_sleep_summary=False while the provider is unavailable.",
    )

    status_code = api.get("status_code")
    _require(isinstance(status_code, int), "Expected session.api.status_code as an integer.")

    provider_error_category = api.get("provider_error_category")
    _require(
        provider_error_category in SAFE_TROUBLESHOOTING_CATEGORIES,
        "Expected a safe provider_error_category for troubleshooting, "
        f"got {provider_error_category!r}.",
    )

    _assert_no_raw_payload_leaks(self_check=self_check, session=session, api=api)

    source_status = str(self_check.get("source_status") or "")
    return status_code, str(provider_error_category), source_status


def _print_checklist() -> None:
    print("[google-health-permission-denied] troubleshooting_checklist:")
    for index, item in enumerate(CHECKLIST, start=1):
        print(f"  {index}. {item}")


def run_smoke(*, base_url: str, target_date: str, allow_real_request: bool) -> None:
    _require_allow_real_request(allow_real_request)

    preflight_status, preflight = _request_json(base_url, "/google-health/preflight")
    _require(preflight_status == 200, f"preflight returned HTTP {preflight_status}: {preflight}")
    _assert_preflight_allows_real_request(preflight)

    query = urlencode({"target_date": target_date})
    self_check_status, self_check = _request_json(
        base_url,
        f"/google-health/self-check?{query}",
    )
    _require(
        self_check_status == 200,
        f"self-check returned HTTP {self_check_status}: {self_check}",
    )

    status_code, provider_error_category, source_status = _extract_api_result(self_check)

    _require(
        source_status == "unavailable",
        f"Expected source_status=unavailable while provider error is unresolved, got {source_status!r}.",
    )

    print(
        "[google-health-permission-denied] "
        f"target_date={target_date} status_code={status_code} "
        f"provider_error_category={provider_error_category} source_status={source_status}"
    )
    print(
        "[google-health-permission-denied] "
        f"real_http_attempted={self_check.get('real_http_attempted')} "
        f"safe_to_use_sleep_summary={self_check.get('safe_to_use_sleep_summary')}"
    )

    if provider_error_category == "permission_denied":
        _print_checklist()
    else:
        print(
            "[google-health-permission-denied] "
            "provider_error_category was not permission_denied; use the category-specific "
            "Google Health troubleshooting path before retrying sleep normalization."
        )

    print(f"[{SCRIPT_NAME}] OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run a narrow Google Health troubleshooting smoke for the current "
            "provider-side rejection and print the permission_denied checklist "
            "without exposing raw provider payloads."
        )
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--target-date", default=date.today().isoformat())
    parser.add_argument(
        "--allow-real-request",
        action="store_true",
        help="Required. This smoke calls self-check while real API gates are enabled.",
    )
    args = parser.parse_args()

    try:
        run_smoke(
            base_url=args.base_url,
            target_date=args.target_date,
            allow_real_request=args.allow_real_request,
        )
    except SmokeRefused as exc:
        print(f"[{SCRIPT_NAME}] REFUSED: {exc}")
        return 2
    except SmokeFailure as exc:
        print(f"[{SCRIPT_NAME}] FAILED: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
