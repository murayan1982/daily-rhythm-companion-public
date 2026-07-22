from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCRIPT_NAME = "google-health-verified-endpoint-gate-smoke-v0.22.0"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"


@dataclass(frozen=True)
class SmokeResponse:
    path: str
    status: int
    body: dict[str, Any]


def _get_json(base_url: str, path: str) -> SmokeResponse:
    url = f"{base_url.rstrip('/')}{path}"
    request = Request(url, method="GET")

    try:
        with urlopen(request, timeout=10) as response:
            raw_body = response.read().decode("utf-8")
            body = json.loads(raw_body)
            return SmokeResponse(path=path, status=response.status, body=body)
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            body = {"raw_body": raw_body}
        return SmokeResponse(path=path, status=exc.code, body=body)
    except URLError as exc:
        raise AssertionError(
            f"Could not connect to {url}. Start the backend before running this smoke."
        ) from exc
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{url} did not return JSON.") from exc


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _bool_field(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    _require(isinstance(value, bool), f"Expected {key} to be a boolean, got {value!r}.")
    return value


def _assert_preflight(preflight: dict[str, Any]) -> None:
    api = preflight.get("api")
    _require(isinstance(api, dict), "preflight.api is missing or not an object.")

    _require(
        _bool_field(api, "endpoint_verified") is True,
        "Expected preflight.api.endpoint_verified=True. Set GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1 only after official endpoint/scope verification.",
    )
    _require(
        _bool_field(api, "api_base_url_placeholder") is False,
        "Expected preflight.api.api_base_url_placeholder=False. Configure the verified API base URL before this smoke.",
    )
    _require(
        _bool_field(api, "real_api_opt_in") is False,
        "Expected preflight.api.real_api_opt_in=False for the Day3 gate. Do not enable final opt-in yet.",
    )
    _require(
        _bool_field(api, "real_api_requests_enabled") is False,
        "Expected preflight.api.real_api_requests_enabled=False for the Day3 gate. Keep real API requests disabled.",
    )
    _require(
        _bool_field(api, "real_api_requests_allowed") is False,
        "Expected preflight.api.real_api_requests_allowed=False while final opt-in and real requests are disabled.",
    )

    ready_for_real_api_request = preflight.get("ready_for_real_api_request")
    _require(
        ready_for_real_api_request is False,
        f"Expected preflight.ready_for_real_api_request=False, got {ready_for_real_api_request!r}.",
    )


def _assert_self_check(self_check: dict[str, Any]) -> None:
    _require(
        self_check.get("diagnostics_status") == "api_disabled",
        f"Expected self-check diagnostics_status=api_disabled, got {self_check.get('diagnostics_status')!r}.",
    )
    _require(
        self_check.get("real_http_attempted") is False,
        "Expected self-check real_http_attempted=False. Day3 must not send a real sleep API request.",
    )
    _require(
        self_check.get("safe_to_use_sleep_summary") is False,
        "Expected self-check safe_to_use_sleep_summary=False until the final real-request smoke succeeds.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the v0.22.0 Day3 Google Health gate: endpoint/scope marked verified "
            "locally, but real API request and final opt-in still disabled."
        )
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"Backend base URL. Defaults to {DEFAULT_BASE_URL}.",
    )
    args = parser.parse_args()

    try:
        preflight = _get_json(args.base_url, "/google-health/preflight")
        self_check = _get_json(args.base_url, "/google-health/self-check")

        _require(preflight.status == 200, f"preflight returned HTTP {preflight.status}: {preflight.body}")
        _require(self_check.status == 200, f"self-check returned HTTP {self_check.status}: {self_check.body}")

        _assert_preflight(preflight.body)
        _assert_self_check(self_check.body)
    except AssertionError as exc:
        print(f"[{SCRIPT_NAME}] FAILED: {exc}")
        return 1

    api = preflight.body["api"]
    print(
        "[endpoint-verified-gate] "
        f"endpoint_verified={api['endpoint_verified']} "
        f"api_base_url_placeholder={api['api_base_url_placeholder']} "
        f"real_api_requests_enabled={api['real_api_requests_enabled']} "
        f"real_api_opt_in={api['real_api_opt_in']} "
        f"real_api_requests_allowed={api['real_api_requests_allowed']}"
    )
    print(
        "[endpoint-verified-gate] "
        f"diagnostics_status={self_check.body['diagnostics_status']} "
        f"real_http_attempted={self_check.body['real_http_attempted']} "
        f"safe_to_use_sleep_summary={self_check.body['safe_to_use_sleep_summary']}"
    )
    print(f"[{SCRIPT_NAME}] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
