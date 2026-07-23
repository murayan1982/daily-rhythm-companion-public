"""Explicit opt-in W-5 real Fitbit backend execution smoke.

This script calls only the configured local DRC backend. The backend may perform
real Fitbit token refresh and sleep retrieval. Output is restricted to
allow-listed status and boolean markers; exact sleep values and private URLs are
not printed.
"""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCRIPT_NAME = "v210-fitbit-real-operator-execution"
FORBIDDEN_RESPONSE_KEYS = {
    "access_token",
    "refresh_token",
    "authorization",
    "authorization_code",
    "oauth_state",
    "raw_payload",
    "raw_response",
    "sleep",
    "summary",
    "errors",
}
ALLOWED_STATUS_STATES = {
    "token_present_unverified",
    "refresh_required",
    "connected",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _request_json(base_url: str, path: str) -> dict[str, Any]:
    request = Request(base_url.rstrip("/") + path, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=20.0) as response:  # noqa: S310 - explicit operator URL
            status = int(response.status)
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"backend returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("backend request failed") from exc

    _require(status == 200, f"backend returned HTTP {status}")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("backend returned invalid JSON") from exc
    _require(isinstance(data, dict), "backend response was not a JSON object")
    return data


def _assert_no_private_keys(data: dict[str, Any], label: str) -> None:
    leaked = sorted(FORBIDDEN_RESPONSE_KEYS.intersection(key.lower() for key in data))
    _require(not leaked, f"{label} exposed forbidden private/raw fields")


def run(base_url: str) -> None:
    providers = _request_json(base_url, "/sleep/providers")
    _assert_no_private_keys(providers, "provider selection")
    _require(
        providers.get("configured_provider") == "fitbit",
        "configured sleep provider is not fitbit",
    )

    status = _request_json(base_url, "/fitbit/status")
    _assert_no_private_keys(status, "fitbit status")
    connection_state = status.get("connection_state")
    _require(
        connection_state in ALLOWED_STATUS_STATES,
        "Fitbit status does not indicate usable real-token preparation",
    )

    summary = _request_json(base_url, "/sleep/summary")
    _assert_no_private_keys(summary, "sleep summary")
    _require(summary.get("source") == "fitbit", "sleep source is not fitbit")
    _require(summary.get("available") is True, "Fitbit sleep data is unavailable")
    _require(summary.get("is_real_data") is True, "sleep data is not marked real")
    duration = summary.get("total_sleep_minutes")
    _require(isinstance(duration, int) and duration > 0, "sleep duration is not positive")
    _require(bool(summary.get("sleep_start")), "normalized sleep start is missing")
    _require(bool(summary.get("sleep_end")), "normalized sleep end is missing")
    _require(
        summary.get("quality_label") not in {None, "", "unavailable"},
        "quality label is unavailable",
    )
    _require(
        summary.get("confidence") not in {None, "", "none"},
        "confidence is unavailable",
    )
    _require(
        summary.get("unavailable_reason") in {None, ""},
        "sleep summary has an unavailable reason",
    )

    print("v210_fitbit_real_operator_execution_real_http_attempted: True")
    print("v210_fitbit_real_operator_execution_provider_selection_fitbit: True")
    print(f"v210_fitbit_real_operator_execution_connection_state: {connection_state}")
    print(
        "v210_fitbit_real_operator_execution_status_verified_field: "
        f"{status.get('verified') is True}"
    )
    print("v210_fitbit_real_operator_execution_sleep_source_fitbit: True")
    print("v210_fitbit_real_operator_execution_sleep_available: True")
    print("v210_fitbit_real_operator_execution_sleep_is_real_data: True")
    print("v210_fitbit_real_operator_execution_positive_duration: True")
    print("v210_fitbit_real_operator_execution_sleep_window_present: True")
    print("v210_fitbit_real_operator_execution_raw_payload_exposed: False")
    print("v210_fitbit_real_operator_execution_smartphone_web_required: True")
    print("v210_fitbit_real_operator_execution_smartphone_web_verified: False")
    print(f"[{SCRIPT_NAME}] OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the explicit opt-in real Fitbit backend verification smoke."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--allow-real-request", action="store_true")
    args = parser.parse_args()

    if not args.allow_real_request:
        print(f"[{SCRIPT_NAME}] ERROR: explicit --allow-real-request is required")
        return 2

    try:
        run(args.base_url)
    except RuntimeError as exc:
        print(f"[{SCRIPT_NAME}] ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
