"""Private local RT-7e VTube Studio operator runner.

The default invocation is inert. Real local execution requires the explicit
``--execute-real-vts`` flag and is further constrained to the accepted local
Backend route on ``http://127.0.0.1:8000``. The runner never reads private
configuration itself and never prints raw response JSON, provider payloads,
private paths, tokens, or hotkey identifiers.

The fixed Framework v5.5.0 transport reports a completed provider hotkey
request while keeping ``real_motion_executed`` false. Physical motion is
accepted only after the operator visibly observes the configured gesture and
types exactly ``ACCEPT``.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
import json
import sys
from typing import Any, BinaryIO, Protocol, TextIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    OpenerDirector,
    Request,
    build_opener,
)

BASE_URL = "http://127.0.0.1:8000"
PRESENTATION_PATH = "/demo/character-motion/vts/presentation"
ENDPOINT = f"{BASE_URL}{PRESENTATION_PATH}"
REQUEST_TIMEOUT_SECONDS = 10.0
MAX_RESPONSE_BYTES = 65536
ACCEPTANCE_GESTURE_ALIAS = "rt7e_acceptance_gesture"
REQUEST_SCHEMA_VERSION = "drc.v3.framework-vts-motion-presentation-request.1"
RESULT_SCHEMA_VERSION = "drc.v3.framework-vts-motion-execution.1"

_ALLOWED_STATUSES = frozenset(
    {
        "completed",
        "completed_with_optional_skip",
        "disabled",
        "provider_execution_not_allowed",
        "unavailable",
        "unsupported",
        "failed",
    }
)
_ALLOWED_REASON_CODES = frozenset(
    {
        "framework_vts_configuration_invalid",
        "framework_vts_motion_disabled",
        "provider_execution_not_allowed",
        "framework_v550_vendor_missing",
        "framework_vts_preflight_unavailable",
        "framework_vts_optional_stop_unsupported",
        "framework_vts_required_intent_unsupported",
        "framework_vts_motion_non_completed",
        "framework_vts_motion_failed",
        "framework_vts_motion_close_failed",
        "framework_vts_motion_completed",
    }
)
_ALLOWED_INTENTS = frozenset(
    {
        "expression",
        "emotion",
        "gesture",
        "reset_expression",
        "stop_motion",
    }
)
_ALLOWED_OUTCOMES = frozenset(
    {
        "completed",
        "unsupported",
        "unavailable",
        "not_configured",
        "not_implemented",
        "interrupted",
        "failed",
        "closed",
    }
)
_ALLOWED_PUBLIC_ERROR_CODES = frozenset(
    {
        "none",
        "unavailable",
        "unsupported",
        "not_configured",
        "token_missing",
        "provider_execution_not_allowed",
        "runtime_not_installed",
        "model_not_selected",
        "not_implemented",
        "interrupted",
        "session_closed",
        "provider_error",
    }
)


class _Response(Protocol):
    status: int
    headers: Any

    def read(self, amount: int = -1) -> bytes: ...

    def __enter__(self) -> "_Response": ...

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None: ...


OpenRequest = Callable[[Request, float], _Response]
ConfirmVisibleMotion = Callable[[], bool]


class _NoRedirectHandler(HTTPRedirectHandler):
    """Reject every redirect instead of following it."""

    def redirect_request(
        self,
        req: Request,
        fp: BinaryIO,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        del req, fp, code, msg, headers, newurl
        return None


def _build_opener() -> OpenerDirector:
    return build_opener(_NoRedirectHandler())


def _default_open(request: Request, timeout: float) -> _Response:
    return _build_opener().open(request, timeout=timeout)


def _fixed_request_body() -> dict[str, object]:
    return {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "command": {
            "order": 1,
            "intent": "gesture",
            "expression": None,
            "emotion": None,
            "gesture": ACCEPTANCE_GESTURE_ALIAS,
            "character_id": None,
        },
    }


def _valid_fixed_base_url(value: str) -> bool:
    if value != BASE_URL:
        return False
    parsed = urlsplit(value)
    return (
        parsed.scheme == "http"
        and parsed.hostname == "127.0.0.1"
        and parsed.port == 8000
        and parsed.path == ""
        and parsed.query == ""
        and parsed.fragment == ""
        and parsed.username is None
        and parsed.password is None
    )


def _strict_int(value: Any, expected: int) -> bool:
    return type(value) is int and value == expected


def _strict_bool(value: Any, expected: bool) -> bool:
    return type(value) is bool and value is expected


def _validate_result(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "response_not_object"

    checks: tuple[tuple[str, bool], ...] = (
        (
            "schema_version",
            payload.get("schema_version") == RESULT_SCHEMA_VERSION,
        ),
        ("status", payload.get("status") == "completed"),
        ("commands_requested", _strict_int(payload.get("commands_requested"), 1)),
        ("commands_applied", _strict_int(payload.get("commands_applied"), 1)),
        ("commands_completed", _strict_int(payload.get("commands_completed"), 1)),
        (
            "optional_commands_skipped",
            _strict_int(payload.get("optional_commands_skipped"), 0),
        ),
        (
            "framework_import_attempted",
            _strict_bool(payload.get("framework_import_attempted"), True),
        ),
        ("session_created", _strict_bool(payload.get("session_created"), True)),
        ("session_closed", _strict_bool(payload.get("session_closed"), True)),
        (
            "real_adapter_enabled",
            _strict_bool(payload.get("real_adapter_enabled"), True),
        ),
        (
            "provider_execution_allowed",
            _strict_bool(payload.get("provider_execution_allowed"), True),
        ),
        (
            "provider_execution_attempted",
            _strict_bool(payload.get("provider_execution_attempted"), True),
        ),
        (
            "network_execution_attempted",
            _strict_bool(payload.get("network_execution_attempted"), True),
        ),
        (
            "backend_real_motion_executed",
            _strict_bool(payload.get("real_motion_executed"), False),
        ),
    )
    for marker, passed in checks:
        if not passed:
            return False, f"marker_failed:{marker}"

    command_results = payload.get("command_results")
    if not isinstance(command_results, list) or len(command_results) != 1:
        return False, "marker_failed:command_results"
    command = command_results[0]
    if not isinstance(command, dict):
        return False, "marker_failed:command_result_shape"
    if command.get("intent") != "gesture":
        return False, "marker_failed:command_intent"
    if command.get("outcome") != "completed":
        return False, "marker_failed:command_outcome"
    if type(command.get("skipped")) is not bool or command.get("skipped") is not False:
        return False, "marker_failed:command_skipped"
    return True, "completed"


def _safe_text(value: Any, *, allowed: frozenset[str]) -> str:
    return value if isinstance(value, str) and value in allowed else "unrecognized"


def _safe_count(value: Any) -> str:
    if type(value) is int and 0 <= value <= 5:
        return str(value)
    return "unrecognized"


def _safe_bool(value: Any) -> str:
    if type(value) is bool:
        return str(value)
    return "unrecognized"


def _safe_failure_diagnostic_lines(payload: Any) -> tuple[str, ...]:
    """Return only bounded, allowlisted public fields from a failed result."""

    if not isinstance(payload, Mapping):
        return ()

    command: Mapping[str, Any] = {}
    command_results = payload.get("command_results")
    if (
        isinstance(command_results, list)
        and len(command_results) == 1
        and isinstance(command_results[0], Mapping)
    ):
        command = command_results[0]

    values = (
        (
            "status",
            _safe_text(payload.get("status"), allowed=_ALLOWED_STATUSES),
        ),
        (
            "reason_code",
            _safe_text(
                payload.get("reason_code"),
                allowed=_ALLOWED_REASON_CODES,
            ),
        ),
        ("commands_requested", _safe_count(payload.get("commands_requested"))),
        ("commands_applied", _safe_count(payload.get("commands_applied"))),
        ("commands_completed", _safe_count(payload.get("commands_completed"))),
        ("session_created", _safe_bool(payload.get("session_created"))),
        ("session_closed", _safe_bool(payload.get("session_closed"))),
        (
            "provider_execution_attempted",
            _safe_bool(payload.get("provider_execution_attempted")),
        ),
        (
            "network_execution_attempted",
            _safe_bool(payload.get("network_execution_attempted")),
        ),
        (
            "backend_real_motion_executed",
            _safe_bool(payload.get("real_motion_executed")),
        ),
        (
            "command_intent",
            _safe_text(command.get("intent"), allowed=_ALLOWED_INTENTS),
        ),
        (
            "command_outcome",
            _safe_text(command.get("outcome"), allowed=_ALLOWED_OUTCOMES),
        ),
        (
            "command_public_error_code",
            _safe_text(
                command.get("public_error_code"),
                allowed=_ALLOWED_PUBLIC_ERROR_CODES,
            ),
        ),
        ("command_retryable", _safe_bool(command.get("retryable"))),
    )
    return tuple(
        f"v300_rt7e_operator_diagnostic_{name}: {value}\n"
        for name, value in values
    )


def _read_json_response(response: _Response) -> Any:
    content_type = str(response.headers.get("content-type", ""))
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type != "application/json":
        raise ValueError("response_content_type_invalid")

    raw_length = response.headers.get("content-length")
    if raw_length is not None:
        try:
            declared = int(raw_length)
        except (TypeError, ValueError) as error:
            raise ValueError("response_content_length_invalid") from error
        if declared < 0 or declared > MAX_RESPONSE_BYTES:
            raise ValueError("response_too_large")

    data = response.read(MAX_RESPONSE_BYTES + 1)
    if len(data) > MAX_RESPONSE_BYTES:
        raise ValueError("response_too_large")
    return json.loads(data.decode("utf-8", errors="strict"))


def _prompt_visible_motion(
    *,
    input_stream: TextIO = sys.stdin,
    output_stream: TextIO = sys.stdout,
) -> bool:
    output_stream.write(
        "Did VTube Studio visibly perform the configured acceptance gesture? "
        "Type ACCEPT to confirm: "
    )
    output_stream.flush()
    answer = input_stream.readline()
    return answer.strip() == "ACCEPT"


def run_operator(
    *,
    execute_real_vts: bool,
    base_url: str = BASE_URL,
    open_request: OpenRequest = _default_open,
    confirm_visible_motion: ConfirmVisibleMotion | None = None,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    """Run one bounded local acceptance attempt or remain inert."""

    if not execute_real_vts:
        stdout.write("v300_rt7e_operator_execution_authorized: False\n")
        stdout.write("v300_rt7e_operator_http_request_attempted: False\n")
        stdout.write("v300_rt7e_operator_provider_execution_attempted: False\n")
        stdout.write("v300_rt7e_operator_network_execution_attempted: False\n")
        stdout.write("v300_rt7e_operator_real_motion_executed: False\n")
        return 2

    if not _valid_fixed_base_url(base_url):
        stderr.write("v300_rt7e_operator_error: backend_url_not_allowed\n")
        return 3

    request = Request(
        ENDPOINT,
        data=json.dumps(
            _fixed_request_body(),
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    try:
        with open_request(request, REQUEST_TIMEOUT_SECONDS) as response:
            if type(response.status) is not int or response.status != 200:
                raise ValueError("unexpected_http_status")
            payload = _read_json_response(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        stderr.write("v300_rt7e_operator_error: bounded_request_failed\n")
        return 3

    valid, reason = _validate_result(payload)
    if not valid:
        stderr.write(f"v300_rt7e_operator_error: {reason}\n")
        for line in _safe_failure_diagnostic_lines(payload):
            stderr.write(line)
        return 3

    stdout.write("v300_rt7e_operator_backend_contract_valid: True\n")
    stdout.write("v300_rt7e_operator_backend_real_motion_executed: False\n")

    confirmation = confirm_visible_motion
    if confirmation is None:
        confirmation = lambda: _prompt_visible_motion()  # noqa: E731
    if confirmation() is not True:
        stderr.write("v300_rt7e_operator_error: visible_motion_not_confirmed\n")
        return 3

    stdout.write("v300_rt7e_operator_execution_authorized: True\n")
    stdout.write("v300_rt7e_operator_http_post_count: 1\n")
    stdout.write("v300_rt7e_operator_status: completed\n")
    stdout.write("v300_rt7e_operator_commands_requested: 1\n")
    stdout.write("v300_rt7e_operator_commands_applied: 1\n")
    stdout.write("v300_rt7e_operator_commands_completed: 1\n")
    stdout.write("v300_rt7e_operator_session_created: True\n")
    stdout.write("v300_rt7e_operator_session_closed: True\n")
    stdout.write("v300_rt7e_operator_provider_execution_attempted: True\n")
    stdout.write("v300_rt7e_operator_network_execution_attempted: True\n")
    stdout.write("v300_rt7e_operator_visible_motion_confirmed: True\n")
    stdout.write("v300_rt7e_operator_real_motion_executed: True\n")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run exactly one private local RT-7e VTube Studio acceptance request."
        )
    )
    parser.add_argument(
        "--execute-real-vts",
        action="store_true",
        help="Explicitly authorize one local real-VTS request.",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Must remain exactly http://127.0.0.1:8000.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    return run_operator(
        execute_real_vts=args.execute_real_vts,
        base_url=args.base_url,
    )


if __name__ == "__main__":
    raise SystemExit(main())
