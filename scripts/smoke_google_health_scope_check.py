from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCRIPT_NAME = "google-health-scope-check-smoke-v0.23.0"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"


class SmokeFailure(AssertionError):
    """Raised when the Google Health scope-check smoke fails."""


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


def run_smoke(*, base_url: str, require_scope_ready: bool) -> None:
    status, body = _request_json(base_url, "/google-health/scope-check")
    _require(status == 200, f"scope-check returned HTTP {status}: {body}")

    configured_scopes = _require_list_of_strings(
        body.get("configured_scopes"),
        "configured_scopes",
    )
    token_scopes = _require_list_of_strings(body.get("token_scopes"), "token_scopes")
    missing_configured = _require_list_of_strings(
        body.get("missing_configured_scopes_in_token"),
        "missing_configured_scopes_in_token",
    )
    missing_required = _require_list_of_strings(
        body.get("missing_required_scopes_in_token"),
        "missing_required_scopes_in_token",
    )
    missing_optional = _require_list_of_strings(
        body.get("missing_optional_configured_scopes_in_token"),
        "missing_optional_configured_scopes_in_token",
    )

    for field in (
        "required_sleep_scope_configured",
        "token_stored",
        "token_scope_configured",
        "reconnect_recommended",
        "ready_for_permission_retest",
    ):
        _require(isinstance(body.get(field), bool), f"Expected {field} to be bool.")

    for field in ("message", "next_action"):
        _require(isinstance(body.get(field), str) and body.get(field), f"Expected {field} text.")

    _require(
        set(missing_configured) == set(missing_required + missing_optional),
        "Expected missing_configured_scopes_in_token to be split into required and optional lists.",
    )

    if require_scope_ready:
        _require(
            body.get("ready_for_permission_retest") is True,
            "Expected ready_for_permission_retest=True. Confirm required sleep scope, "
            "add it to GOOGLE_HEALTH_OAUTH_SCOPES, reconnect/re-authorize, then retry.",
        )
        _require(
            not missing_required,
            "Expected no missing required sleep scopes before permission retest.",
        )
        _require(
            body.get("reconnect_recommended") is False,
            "Expected reconnect_recommended=False when the required sleep scope is present. "
            "Optional identity scopes must not block permission retest readiness.",
        )

    print(
        "[google-health-scope-check] "
        f"required_sleep_scope_configured={body.get('required_sleep_scope_configured')} "
        f"required_sleep_scope={body.get('required_sleep_scope')!r}"
    )
    print(
        "[google-health-scope-check] "
        f"configured_scope_count={len(configured_scopes)} "
        f"token_stored={body.get('token_stored')} "
        f"token_scope_count={len(token_scopes)}"
    )
    print(
        "[google-health-scope-check] "
        f"missing_required_scopes_in_token={missing_required} "
        f"missing_optional_configured_scopes_in_token={missing_optional}"
    )
    print(
        "[google-health-scope-check] "
        f"reconnect_recommended={body.get('reconnect_recommended')} "
        f"ready_for_permission_retest={body.get('ready_for_permission_retest')}"
    )
    print(f"[google-health-scope-check] next_action={body.get('next_action')}")
    print(f"[{SCRIPT_NAME}] OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check Google Health configured OAuth scopes against the locally stored "
            "token scope without refreshing tokens or sending real API requests."
        )
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--require-scope-ready",
        action="store_true",
        help="Fail unless the stored token includes the required sleep-read scope.",
    )
    args = parser.parse_args()

    try:
        run_smoke(
            base_url=args.base_url,
            require_scope_ready=args.require_scope_ready,
        )
    except SmokeFailure as exc:
        print(f"[{SCRIPT_NAME}] FAILED: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
