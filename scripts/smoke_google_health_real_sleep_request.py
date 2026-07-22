from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SCRIPT_NAME = "google-health-real-sleep-request-smoke-v0.23.0"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_EXPECTED_ENDPOINT = (
    "https://health.googleapis.com/v4/users/me/dataTypes/sleep/dataPoints"
)
DEFAULT_EXPECTED_QUERY_KEYS = ("filter",)
BLOCKING_API_ERRORS = {
    "api_request_disabled",
    "unsafe_real_api_config",
    "no_stored_tokens",
    "refresh_not_completed",
    "refreshed_tokens_not_found",
}


class SmokeFailure(AssertionError):
    """Raised when the guarded real Google Health smoke fails."""


class SmokeRefused(SmokeFailure):
    """Raised when the operator did not provide explicit real-request consent."""


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
            "Refusing to run a real Google Health request. Re-run with "
            "--allow-real-request only after verifying endpoint, scope, date range, "
            "filter query, and .env opt-in flags."
        )


def _assert_preflight_allows_real_request(preflight: dict[str, Any]) -> None:
    api = preflight.get("api")
    _require(isinstance(api, dict), "preflight.api is missing or not an object.")

    expected_true_fields = (
        "endpoint_verified",
        "real_api_requests_enabled",
        "real_api_opt_in",
        "real_api_requests_allowed",
    )
    for field in expected_true_fields:
        _require(
            api.get(field) is True,
            f"Expected preflight.api.{field}=True before the real smoke, got {api.get(field)!r}.",
        )

    _require(
        api.get("api_base_url_placeholder") is False,
        "Expected preflight.api.api_base_url_placeholder=False.",
    )
    _require(
        preflight.get("ready_for_real_api_request") is True,
        "Expected preflight.ready_for_real_api_request=True before the real smoke.",
    )


def _assert_provider_error_summary_is_safe(api: dict[str, Any]) -> None:
    summary = api.get("provider_error_summary")
    if summary is None:
        return

    _require(
        isinstance(summary, dict),
        "Expected provider_error_summary to be an object when present.",
    )

    forbidden_fragments = (
        "access_token",
        "refresh_token",
        "client_secret",
        "authorization",
        "bearer ",
    )
    serialized = json.dumps(summary, sort_keys=True).lower()
    leaked_fragments = [
        fragment for fragment in forbidden_fragments if fragment in serialized
    ]
    _require(
        not leaked_fragments,
        f"Provider error summary may contain sensitive fragments: {leaked_fragments}.",
    )


def _assert_real_self_check(
    self_check: dict[str, Any],
    *,
    expected_endpoint: str,
    expected_query_keys: tuple[str, ...],
    require_http_status: bool,
) -> None:
    session = self_check.get("session") or {}
    api = session.get("api") or {}
    preview = api.get("request_preview") or {}

    _require(
        self_check.get("real_http_attempted") is True,
        "Expected real_http_attempted=True. The request did not reach the HTTP boundary.",
    )
    _require(api.get("requested") is True, "Expected session.api.requested=True.")
    _require(api.get("attempted") is True, "Expected session.api.attempted=True.")
    _require(
        api.get("request_prepared") is True,
        "Expected session.api.request_prepared=True.",
    )
    _require(
        api.get("real_api_enabled") is True,
        "Expected session.api.real_api_enabled=True.",
    )

    error = api.get("error") or self_check.get("error")
    _require(
        error not in BLOCKING_API_ERRORS,
        f"Real request was still blocked by boundary error: {error!r}.",
    )

    _require(
        preview.get("endpoint") == expected_endpoint,
        f"Expected endpoint {expected_endpoint!r}, got {preview.get('endpoint')!r}.",
    )
    _require(preview.get("method") == "GET", "Expected request method GET.")
    _require(
        preview.get("has_bearer_auth") is True,
        "Expected has_bearer_auth=True without exposing the token value.",
    )

    query_keys = tuple(sorted(preview.get("query_param_keys") or ()))
    _require(
        query_keys == tuple(sorted(expected_query_keys)),
        f"Expected query keys {expected_query_keys!r}, got {query_keys!r}.",
    )

    query_params = preview.get("query_params") or {}
    if expected_query_keys == ("filter",):
        filter_value = query_params.get("filter")
        _require(
            isinstance(filter_value, str) and filter_value,
            "Expected request preview to include a non-empty filter query parameter.",
        )
        _require(
            filter_value.startswith('sleep.interval.civil_end_time >= "'),
            f"Expected sleep civil-end-date filter, got {filter_value!r}.",
        )
        _require(
            '" AND sleep.interval.civil_end_time < "' in filter_value,
            f"Expected sleep civil-end-date range filter, got {filter_value!r}.",
        )

    status_code = api.get("status_code")
    if require_http_status:
        _require(
            isinstance(status_code, int),
            "Expected session.api.status_code to be an integer after the real HTTP request.",
        )

    raw_payload_indicators = {"data", "response", "raw_payload", "payload"}
    leaked_keys = raw_payload_indicators.intersection(api.keys())
    _require(
        not leaked_keys,
        f"Self-check API summary exposed raw payload-like fields: {sorted(leaked_keys)}.",
    )
    _assert_provider_error_summary_is_safe(api)


def _assert_backend_sleep_summary(summary: dict[str, Any]) -> None:
    _require(
        summary.get("source") == "google_health",
        f"Expected /sleep/summary source='google_health', got {summary.get('source')!r}.",
    )
    _require(
        summary.get("available") is True,
        f"Expected /sleep/summary available=True, got {summary.get('available')!r}.",
    )
    _require(
        summary.get("is_real_data") is True,
        f"Expected /sleep/summary is_real_data=True, got {summary.get('is_real_data')!r}.",
    )

    total_sleep_minutes = summary.get("total_sleep_minutes")
    _require(
        isinstance(total_sleep_minutes, int) and total_sleep_minutes > 0,
        "Expected /sleep/summary to contain a positive normalized sleep duration.",
    )
    _require(
        summary.get("unavailable_reason") in (None, ""),
        "Expected /sleep/summary unavailable_reason to be empty for accepted real data.",
    )

    forbidden_payload_keys = {
        "data_points",
        "raw_payload",
        "raw_response",
        "sleep_events",
        "authorization_header",
        "access_token",
        "refresh_token",
    }
    leaked = sorted(forbidden_payload_keys.intersection(summary.keys()))
    _require(
        not leaked,
        f"/sleep/summary exposed forbidden raw/private fields: {leaked}.",
    )

def _print_provider_error_summary(api: dict[str, Any]) -> None:
    summary = api.get("provider_error_summary")
    if not isinstance(summary, dict):
        print("[google-health-real-sleep] provider_error_summary=None")
        return

    print(
        "[google-health-real-sleep] "
        f"provider_error_category={api.get('provider_error_category')} "
        f"provider_error_status={summary.get('provider_error_status')} "
        f"provider_error_reason={summary.get('provider_error_reason')} "
        f"suggested_cause={summary.get('suggested_cause')}"
    )
    print(
        "[google-health-real-sleep] "
        f"provider_error_message_hint={summary.get('provider_error_message_hint')}"
    )

    auth_hint = summary.get("www_authenticate_hint")
    if auth_hint:
        print(f"[google-health-real-sleep] www_authenticate_hint={auth_hint}")


def run_smoke(
    *,
    base_url: str,
    target_date: str,
    allow_real_request: bool,
    expected_endpoint: str,
    expected_query_keys: tuple[str, ...],
    require_http_status: bool,
) -> None:
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
    _assert_real_self_check(
        self_check,
        expected_endpoint=expected_endpoint,
        expected_query_keys=expected_query_keys,
        require_http_status=require_http_status,
    )

    summary_status, sleep_summary = _request_json(base_url, "/sleep/summary")
    _require(
        summary_status == 200,
        f"/sleep/summary returned HTTP {summary_status}: {sleep_summary}",
    )
    _assert_backend_sleep_summary(sleep_summary)

    api = (self_check.get("session") or {}).get("api") or {}
    preview = api.get("request_preview") or {}
    status_code = api.get("status_code")
    print(f"[google-health-real-sleep] endpoint={preview.get('endpoint')}")
    print(
        "[google-health-real-sleep] "
        f"target_date_supplied={bool(target_date)} status_code={status_code} "
        f"source_status={self_check.get('source_status')} "
        f"error={self_check.get('error')}"
    )
    print(
        "[google-health-real-sleep] "
        f"real_http_attempted={self_check.get('real_http_attempted')} "
        f"safe_to_use_sleep_summary={self_check.get('safe_to_use_sleep_summary')}"
    )
    print(
        "[google-health-real-sleep] "
        "backend_sleep_summary_source=google_health "
        "backend_sleep_summary_available=True "
        "backend_sleep_summary_is_real_data=True "
        "backend_sleep_summary_positive_duration=True"
    )
    _print_provider_error_summary(api)
    print(f"[{SCRIPT_NAME}] OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the guarded v0.23.0 Google Health sleep filter real request smoke. "
            "This sends one real GET only when --allow-real-request and all backend "
            "runtime opt-in gates are enabled."
        )
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--target-date", default=date.today().isoformat())
    parser.add_argument(
        "--allow-real-request",
        action="store_true",
        help="Required. Without this flag the script refuses to send a real request.",
    )
    parser.add_argument("--expected-endpoint", default=DEFAULT_EXPECTED_ENDPOINT)
    parser.add_argument(
        "--expected-query-keys",
        default=",".join(DEFAULT_EXPECTED_QUERY_KEYS),
        help="Comma-separated expected query parameter keys.",
    )
    parser.add_argument(
        "--allow-network-failure-without-status",
        action="store_true",
        help=(
            "Advanced troubleshooting only. By default the smoke expects an HTTP "
            "status code from Google Health, even when the provider returns a 4xx."
        ),
    )
    args = parser.parse_args()

    expected_query_keys = tuple(
        key.strip() for key in args.expected_query_keys.split(",") if key.strip()
    )

    try:
        run_smoke(
            base_url=args.base_url,
            target_date=args.target_date,
            allow_real_request=args.allow_real_request,
            expected_endpoint=args.expected_endpoint,
            expected_query_keys=expected_query_keys,
            require_http_status=not args.allow_network_failure_without_status,
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
