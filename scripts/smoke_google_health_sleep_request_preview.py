from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_EXPECTED_ENDPOINT = (
    "https://health.googleapis.com/v4/users/me/dataTypes/sleep/dataPoints"
)
DEFAULT_EXPECTED_QUERY_KEYS = ("filter",)
EXPECTED_FILTER_PREFIX = 'sleep.interval.civil_end_time >= "'
EXPECTED_FILTER_OPERATOR = '" AND sleep.interval.civil_end_time < "'


class SmokeFailure(AssertionError):
    """Raised when the Google Health sleep preview smoke fails."""


def _read_json(url: str) -> dict:
    try:
        with urlopen(url, timeout=10) as response:
            payload = response.read().decode("utf-8")
    except URLError as exc:
        raise SmokeFailure(f"Failed to call {url}: {exc}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"Invalid JSON response from {url}: {exc}") from exc

    if not isinstance(data, dict):
        raise SmokeFailure(f"Expected JSON object from {url}.")

    return data


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _assert_sleep_filter_value(filter_value: str) -> None:
    _expect(
        filter_value.startswith(EXPECTED_FILTER_PREFIX),
        f"Expected sleep filter to start with {EXPECTED_FILTER_PREFIX!r}, got {filter_value!r}.",
    )
    _expect(
        EXPECTED_FILTER_OPERATOR in filter_value,
        f"Expected sleep filter to contain {EXPECTED_FILTER_OPERATOR!r}, got {filter_value!r}.",
    )
    _expect(
        filter_value.endswith('\"'),
        f"Expected sleep filter to end with a civil date literal, got {filter_value!r}.",
    )


def run_smoke(
    *,
    base_url: str,
    target_date: str,
    expected_endpoint: str,
    expected_query_keys: tuple[str, ...],
) -> None:
    query = urlencode({"target_date": target_date})
    url = f"{_normalize_base_url(base_url)}/google-health/self-check?{query}"
    data = _read_json(url)

    session = data.get("session") or {}
    api = session.get("api") or {}
    preview = api.get("request_preview") or {}

    _expect(
        data.get("real_http_attempted") is False,
        "Expected real_http_attempted=False for preview-only smoke.",
    )
    _expect(
        data.get("source_status") == "api_disabled",
        f"Expected source_status=api_disabled, got {data.get('source_status')!r}.",
    )
    _expect(
        api.get("attempted") is False,
        "Expected API attempted=False while real requests are disabled.",
    )
    _expect(
        api.get("request_prepared") is True,
        "Expected API request_prepared=True for preview-only smoke.",
    )
    _expect(
        preview.get("endpoint") == expected_endpoint,
        f"Expected endpoint {expected_endpoint!r}, got {preview.get('endpoint')!r}.",
    )
    _expect(
        preview.get("method") == "GET",
        f"Expected method='GET', got {preview.get('method')!r}.",
    )
    _expect(
        preview.get("has_bearer_auth") is True,
        "Expected has_bearer_auth=True without exposing the token value.",
    )

    query_keys = tuple(sorted(preview.get("query_param_keys") or ()))
    _expect(
        query_keys == tuple(sorted(expected_query_keys)),
        f"Expected query keys {expected_query_keys!r}, got {query_keys!r}.",
    )

    query_params = preview.get("query_params") or {}
    for key in expected_query_keys:
        _expect(key in query_params, f"Expected query_params to include {key!r}.")
        _expect(
            isinstance(query_params[key], str) and query_params[key],
            f"Expected query parameter {key!r} to be a non-empty string.",
        )

    if expected_query_keys == ("filter",):
        _assert_sleep_filter_value(query_params["filter"])

    preview_url = preview.get("preview_url") or ""
    _expect(
        preview_url.startswith(expected_endpoint + "?"),
        f"Expected preview_url to start with endpoint and query string, got {preview_url!r}.",
    )
    _expect(
        "sleep.interval.civil_end_time" in preview_url,
        f"Expected preview_url to include encoded sleep filter, got {preview_url!r}.",
    )

    print(f"[google-health-sleep-preview] endpoint={preview.get('endpoint')}")
    print(f"[google-health-sleep-preview] query_param_keys={','.join(query_keys)}")
    print(f"[google-health-sleep-preview] filter={query_params.get('filter')}")
    print(
        "[google-health-sleep-preview] "
        f"real_http_attempted={data.get('real_http_attempted')} "
        f"source_status={data.get('source_status')}"
    )
    print("[google-health-sleep-request-preview-smoke-v0.23.0] OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test Google Health sleep dataPoints.list filter preview."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--target-date", default=date.today().isoformat())
    parser.add_argument("--expected-endpoint", default=DEFAULT_EXPECTED_ENDPOINT)
    parser.add_argument(
        "--expected-query-keys",
        default=",".join(DEFAULT_EXPECTED_QUERY_KEYS),
        help="Comma-separated expected query parameter keys.",
    )
    args = parser.parse_args()

    expected_query_keys = tuple(
        key.strip() for key in args.expected_query_keys.split(",") if key.strip()
    )

    try:
        run_smoke(
            base_url=args.base_url,
            target_date=args.target_date,
            expected_endpoint=args.expected_endpoint,
            expected_query_keys=expected_query_keys,
        )
    except SmokeFailure as exc:
        print(f"[google-health-sleep-request-preview-smoke-v0.23.0] FAILED: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
