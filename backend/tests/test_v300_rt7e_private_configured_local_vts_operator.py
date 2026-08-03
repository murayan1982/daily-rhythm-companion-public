"""Credential-free tests for the inert-by-default RT-7e operator runner."""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys
from typing import Any
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_v300_rt7e_private_configured_local_vts_operator as runner


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        status: int = 200,
        content_type: str = "application/json",
        content_length: str | None = None,
    ) -> None:
        self.status = status
        self.headers: dict[str, str] = {"content-type": content_type}
        if content_length is not None:
            self.headers["content-length"] = content_length
        self._payload = payload

    def read(self, amount: int = -1) -> bytes:
        if amount < 0:
            return self._payload
        return self._payload[:amount]

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        return None


def completed_payload() -> dict[str, object]:
    return {
        "schema_version": runner.RESULT_SCHEMA_VERSION,
        "status": "completed",
        "commands_requested": 1,
        "commands_applied": 1,
        "commands_completed": 1,
        "optional_commands_skipped": 0,
        "command_results": [
            {
                "order": 1,
                "intent": "gesture",
                "outcome": "completed",
                "state": "idle",
                "adapter_status": "configured",
                "public_error_code": "none",
                "retryable": False,
                "skipped": False,
                "safe_message": "",
            }
        ],
        "event_types": [],
        "framework_import_attempted": True,
        "session_created": True,
        "session_closed": True,
        "adapter": "vts",
        "real_adapter_enabled": True,
        "provider_execution_allowed": True,
        "provider_execution_attempted": True,
        "network_execution_attempted": True,
        # Fixed FW v5.5.0 intentionally leaves physical motion unclaimed.
        "real_motion_executed": False,
        "reason_code": "framework_vts_motion_completed",
        "safe_message": "Framework VTS motion commands completed.",
    }


def response_for(payload: dict[str, object]) -> FakeResponse:
    raw = json.dumps(payload).encode("utf-8")
    return FakeResponse(raw, content_length=str(len(raw)))


def test_without_explicit_flag_performs_zero_requests() -> None:
    calls: list[Request] = []

    def fail_open(request: Request, timeout: float) -> FakeResponse:
        calls.append(request)
        raise AssertionError("request must not be attempted")

    stdout = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=False,
        open_request=fail_open,
        stdout=stdout,
        stderr=io.StringIO(),
    )
    assert code == 2
    assert calls == []
    assert "http_request_attempted: False" in stdout.getvalue()


def test_non_loopback_or_changed_backend_url_is_rejected() -> None:
    calls: list[Request] = []
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=True,
        base_url="http://example.invalid:8000",
        open_request=lambda request, timeout: calls.append(request),  # type: ignore[arg-type,return-value]
        confirm_visible_motion=lambda: True,
        stdout=io.StringIO(),
        stderr=stderr,
    )
    assert code == 3
    assert calls == []
    assert stderr.getvalue() == "v300_rt7e_operator_error: backend_url_not_allowed\n"


def test_fixed_gesture_request_uses_exactly_one_post_and_operator_acceptance() -> None:
    calls: list[tuple[Request, float]] = []
    stdout = io.StringIO()

    def open_request(request: Request, timeout: float) -> FakeResponse:
        calls.append((request, timeout))
        return response_for(completed_payload())

    code = runner.run_operator(
        execute_real_vts=True,
        open_request=open_request,
        confirm_visible_motion=lambda: True,
        stdout=stdout,
        stderr=io.StringIO(),
    )
    assert code == 0
    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.full_url == runner.ENDPOINT
    assert request.get_method() == "POST"
    assert timeout == runner.REQUEST_TIMEOUT_SECONDS
    assert json.loads(request.data.decode("utf-8")) == runner._fixed_request_body()
    output = stdout.getvalue()
    assert "backend_contract_valid: True" in output
    assert "backend_real_motion_executed: False" in output
    assert "visible_motion_confirmed: True" in output
    assert "v300_rt7e_operator_real_motion_executed: True" in output


def test_redirect_handler_never_follows_redirects() -> None:
    handler = runner._NoRedirectHandler()
    request = Request(runner.ENDPOINT, method="POST")
    redirected = handler.redirect_request(
        request,
        io.BytesIO(b""),
        302,
        "Found",
        {},
        "http://127.0.0.1:8001/private",
    )
    assert redirected is None


def test_response_is_bounded_to_65536_bytes() -> None:
    stderr = io.StringIO()

    def open_request(request: Request, timeout: float) -> FakeResponse:
        del request, timeout
        return FakeResponse(
            b"x" * (runner.MAX_RESPONSE_BYTES + 1),
            content_length=str(runner.MAX_RESPONSE_BYTES + 1),
        )

    code = runner.run_operator(
        execute_real_vts=True,
        open_request=open_request,
        confirm_visible_motion=lambda: True,
        stdout=io.StringIO(),
        stderr=stderr,
    )
    assert code == 3
    assert stderr.getvalue() == "v300_rt7e_operator_error: bounded_request_failed\n"


def test_backend_real_motion_must_remain_false_before_operator_confirmation() -> None:
    payload = completed_payload()
    payload["real_motion_executed"] = True
    confirmed: list[bool] = []
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=True,
        open_request=lambda request, timeout: response_for(payload),
        confirm_visible_motion=lambda: confirmed.append(True) or True,
        stdout=io.StringIO(),
        stderr=stderr,
    )
    assert code == 3
    assert confirmed == []
    assert stderr.getvalue().startswith(
        "v300_rt7e_operator_error: "
        "marker_failed:backend_real_motion_executed\n"
    )


def test_visible_motion_confirmation_false_never_promotes_real_motion() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=True,
        open_request=lambda request, timeout: response_for(completed_payload()),
        confirm_visible_motion=lambda: False,
        stdout=stdout,
        stderr=stderr,
    )
    assert code == 3
    assert "backend_contract_valid: True" in stdout.getvalue()
    assert "backend_real_motion_executed: False" in stdout.getvalue()
    assert "v300_rt7e_operator_real_motion_executed: True" not in stdout.getvalue()
    assert stderr.getvalue() == (
        "v300_rt7e_operator_error: visible_motion_not_confirmed\n"
    )


def test_non_completed_response_prints_only_allowlisted_safe_diagnostics() -> None:
    payload = completed_payload()
    payload.update(
        {
            "status": "failed",
            "commands_applied": 0,
            "commands_completed": 0,
            "session_created": True,
            "session_closed": True,
            "provider_execution_attempted": True,
            "network_execution_attempted": True,
            "real_motion_executed": False,
            "reason_code": "framework_vts_motion_non_completed",
            "authentication_token": "private-token-should-not-appear",
            "hotkey_id": "private-hotkey-should-not-appear",
            "provider_payload": {"raw": "private-provider-payload"},
        }
    )
    payload["command_results"] = [
        {
            "intent": "gesture",
            "outcome": "not_configured",
            "public_error_code": "not_configured",
            "retryable": False,
            "private_name": "private-hotkey-should-not-appear",
        }
    ]
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=True,
        open_request=lambda request, timeout: response_for(payload),
        confirm_visible_motion=lambda: True,
        stdout=io.StringIO(),
        stderr=stderr,
    )
    assert code == 3
    rendered = stderr.getvalue()
    assert "v300_rt7e_operator_error: marker_failed:status" in rendered
    for expected in (
        "diagnostic_status: failed",
        "diagnostic_reason_code: framework_vts_motion_non_completed",
        "diagnostic_commands_requested: 1",
        "diagnostic_commands_applied: 0",
        "diagnostic_commands_completed: 0",
        "diagnostic_session_created: True",
        "diagnostic_session_closed: True",
        "diagnostic_provider_execution_attempted: True",
        "diagnostic_network_execution_attempted: True",
        "diagnostic_backend_real_motion_executed: False",
        "diagnostic_command_intent: gesture",
        "diagnostic_command_outcome: not_configured",
        "diagnostic_command_public_error_code: not_configured",
        "diagnostic_command_retryable: False",
    ):
        assert expected in rendered
    for forbidden in (
        "private-token-should-not-appear",
        "private-hotkey-should-not-appear",
        "private-provider-payload",
        "authentication_token",
        "hotkey_id",
        "provider_payload",
        "private_name",
    ):
        assert forbidden not in rendered


def test_success_output_never_echoes_private_or_raw_response_fields() -> None:
    payload = completed_payload()
    payload["authentication_token"] = "private-token-should-not-appear"
    payload["hotkey_id"] = "private-hotkey-should-not-appear"
    payload["provider_payload"] = {"raw": "private-provider-payload"}
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=True,
        open_request=lambda request, timeout: response_for(payload),
        confirm_visible_motion=lambda: True,
        stdout=stdout,
        stderr=stderr,
    )
    assert code == 0
    rendered = stdout.getvalue() + stderr.getvalue()
    for forbidden in (
        "private-token-should-not-appear",
        "private-hotkey-should-not-appear",
        "private-provider-payload",
        "authentication_token",
        "hotkey_id",
        "provider_payload",
    ):
        assert forbidden not in rendered
