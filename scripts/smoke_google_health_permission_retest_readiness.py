from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCRIPT_NAME = "google-health-permission-retest-readiness-smoke-v0.23.0"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"


class SmokeFailure(AssertionError):
    """Raised when the permission-retest readiness smoke fails."""


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


def _require_list_of_strings(value: Any, field: str) -> list[str]:
    _require(isinstance(value, list), f"Expected {field} to be a list.")
    _require(
        all(isinstance(item, str) for item in value),
        f"Expected {field} to contain only strings.",
    )
    return list(value)


def run_smoke(*, base_url: str, require_ready: bool) -> None:
    status, body = _request_json(base_url, "/google-health/permission-retest-readiness")
    _require(status == 200, f"permission-retest-readiness returned HTTP {status}: {body}")

    _require(body.get("provider") == "google_health", "Expected provider=google_health.")
    _require(isinstance(body.get("status"), str) and body.get("status"), "Expected status text.")
    _require(
        isinstance(body.get("required_sleep_scope"), (str, type(None))),
        "Expected required_sleep_scope to be string or null.",
    )

    for field in (
        "ready_for_guarded_permission_retest",
        "scope_ready",
        "cloud_api_enabled_confirmed",
        "oauth_consent_sleep_scope_confirmed",
        "oauth_test_user_confirmed",
        "endpoint_query_confirmed",
    ):
        _require(isinstance(body.get(field), bool), f"Expected {field} to be bool.")

    confirmed_checks = _require_list_of_strings(body.get("confirmed_checks"), "confirmed_checks")
    unresolved_checks = _require_list_of_strings(body.get("unresolved_checks"), "unresolved_checks")

    for field in ("message", "next_action"):
        _require(isinstance(body.get(field), str) and body.get(field), f"Expected {field} text.")

    if require_ready:
        _require(
            body.get("ready_for_guarded_permission_retest") is True,
            "Expected ready_for_guarded_permission_retest=True. Confirm required sleep scope, "
            "Cloud API enablement, OAuth consent sleep scope, test-user/app approval, "
            "and endpoint/query details before retrying.",
        )
        _require(not unresolved_checks, "Expected no unresolved manual checks.")

    print(
        "[google-health-permission-retest-readiness] "
        f"status={body.get('status')} "
        f"scope_ready={body.get('scope_ready')} "
        f"ready_for_guarded_permission_retest={body.get('ready_for_guarded_permission_retest')}"
    )
    print(
        "[google-health-permission-retest-readiness] "
        f"cloud_api_enabled_confirmed={body.get('cloud_api_enabled_confirmed')} "
        f"oauth_consent_sleep_scope_confirmed={body.get('oauth_consent_sleep_scope_confirmed')} "
        f"oauth_test_user_confirmed={body.get('oauth_test_user_confirmed')} "
        f"endpoint_query_confirmed={body.get('endpoint_query_confirmed')}"
    )
    print(
        "[google-health-permission-retest-readiness] "
        f"confirmed_count={len(confirmed_checks)} unresolved_count={len(unresolved_checks)}"
    )
    for index, item in enumerate(unresolved_checks, start=1):
        print(f"  unresolved {index}. {item}")
    print(f"[google-health-permission-retest-readiness] next_action={body.get('next_action')}")
    print(f"[{SCRIPT_NAME}] OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check local readiness for a guarded Google Health 403 permission_denied "
            "retest without calling Google APIs."
        )
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Fail unless all manual confirmation flags and required sleep scope are ready.",
    )
    args = parser.parse_args()

    try:
        run_smoke(base_url=args.base_url, require_ready=args.require_ready)
    except SmokeFailure as exc:
        print(f"[{SCRIPT_NAME}] FAILED: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
