"""Credential-free RT-7e operator-contract corrective verification."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f"
EXPECTED = {
    "scripts/run_v300_rt7e_private_configured_local_vts_operator.py",
    "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
}
DOC = "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md"
RUNNER = "scripts/run_v300_rt7e_private_configured_local_vts_operator.py"
TEST = "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py"


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt7e_corrective_gate_error: {message}")


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def changed_paths() -> set[str]:
    tracked = {
        line.replace("\\", "/")
        for line in git("diff", "--name-only", "HEAD").splitlines()
        if line.strip()
    }
    untracked = {
        line.replace("\\", "/")
        for line in git(
            "ls-files",
            "--others",
            "--exclude-standard",
        ).splitlines()
        if line.strip()
    }
    return tracked | untracked


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        fail(f"{label} missing required marker: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        fail(f"{label} contains forbidden marker: {marker}")


def validate_scope(snapshot: bool) -> None:
    missing = sorted(path for path in EXPECTED if not (ROOT / path).is_file())
    if missing:
        fail(f"missing corrective files: {missing}")
    if snapshot:
        return
    if git("rev-parse", "HEAD") != BASELINE:
        fail("HEAD is not the accepted RT-7e Stage 1 baseline")
    actual = changed_paths()
    if actual != EXPECTED:
        fail(
            "exact corrective change surface mismatch: "
            f"expected={sorted(EXPECTED)}, actual={sorted(actual)}"
        )


def validate_doc() -> None:
    text = read(DOC)
    for marker in (
        "RT-7e operator corrective: IMPLEMENTED / AWAITING_REVIEW",
        BASELINE,
        "exact 4 files",
        "Control A: PASS",
        "Control B first attempt: NOT_ACCEPTED",
        "Control B corrective attempt: NOT_ACCEPTED",
        "manual VTube Studio hotkey verification: PASS",
        "private binding rewritten",
        "additional real VTube Studio execution: NOT_AUTHORIZED",
        "RT-7e acceptance sync: NOT_AUTHORIZED",
        "commit / push: NOT_AUTHORIZED",
        "Backend `real_motion_executed: false`",
        "operator confirmation promotes real motion",
        "allowlisted safe diagnostics",
        "backend/app/**",
        "app/**",
        "vendor/**",
        "one POST, no redirect, no retry, no loop",
        "at most 65536 response bytes",
    ):
        require(text, marker, "RT-7e corrective documentation")

    private_patterns = {
        "credential-shaped value": r"\b(?:sk|sess)-[A-Za-z0-9_-]{16,}\b",
        "private LAN IPv4": (
            r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|"
            r"192\.168\.(?:\d{1,3}\.)\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})\b"
        ),
        "Windows private path": r"[A-Za-z]:\\(?:Users|work|private|temp)\\",
    }
    for label, pattern in private_patterns.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"corrective document contains {label}")


def validate_runner_source() -> None:
    runner = read(RUNNER)
    for marker in (
        'BASE_URL = "http://127.0.0.1:8000"',
        'PRESENTATION_PATH = "/demo/character-motion/vts/presentation"',
        "REQUEST_TIMEOUT_SECONDS = 10.0",
        "MAX_RESPONSE_BYTES = 65536",
        'ACCEPTANCE_GESTURE_ALIAS = "rt7e_acceptance_gesture"',
        '"--execute-real-vts"',
        'method="POST"',
        "class _NoRedirectHandler(HTTPRedirectHandler)",
        "return None",
        "if not execute_real_vts:",
        "if not _valid_fixed_base_url(base_url):",
        "response.read(MAX_RESPONSE_BYTES + 1)",
        '"backend_real_motion_executed"',
        '_strict_bool(payload.get("real_motion_executed"), False)',
        "def _safe_failure_diagnostic_lines",
        "v300_rt7e_operator_backend_contract_valid: True",
        "v300_rt7e_operator_backend_real_motion_executed: False",
        "if confirmation() is not True:",
        "v300_rt7e_operator_visible_motion_confirmed: True",
        "v300_rt7e_operator_real_motion_executed: True",
    ):
        require(runner, marker, "RT-7e corrective operator runner")

    for marker in (
        "os.environ",
        "load_dotenv",
        "dotenv_values",
        "backend/.env",
        "pyvts",
        "websockets",
        "AI-Character-Framework\\Development",
        "AI-Character-Framework/Development",
        "print(payload",
        "print(response",
        "json.dumps(payload",
    ):
        forbid(runner, marker, "RT-7e corrective operator runner")

    test_text = read(TEST)
    test_names = re.findall(r"^def (test_[A-Za-z0-9_]+)\(", test_text, flags=re.MULTILINE)
    if len(test_names) != 9:
        fail(f"focused corrective test count must remain exactly 9, got {len(test_names)}")
    for marker in (
        "test_without_explicit_flag_performs_zero_requests",
        "test_non_loopback_or_changed_backend_url_is_rejected",
        "test_fixed_gesture_request_uses_exactly_one_post_and_operator_acceptance",
        "test_redirect_handler_never_follows_redirects",
        "test_response_is_bounded_to_65536_bytes",
        "test_backend_real_motion_must_remain_false_before_operator_confirmation",
        "test_visible_motion_confirmation_false_never_promotes_real_motion",
        "test_non_completed_response_prints_only_allowlisted_safe_diagnostics",
        "test_success_output_never_echoes_private_or_raw_response_fields",
    ):
        require(test_text, marker, "RT-7e corrective focused tests")


def _import_runner() -> Any:
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    import run_v300_rt7e_private_configured_local_vts_operator as runner

    return runner


def validate_inert_runtime() -> None:
    runner = _import_runner()
    attempted: list[object] = []

    def forbidden_open(request: object, timeout: float) -> object:
        attempted.append((request, timeout))
        raise AssertionError("corrective gate attempted HTTP")

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=False,
        open_request=forbidden_open,
        stdout=stdout,
        stderr=stderr,
    )
    if code != 2 or attempted:
        fail("default corrective runner did not remain transport-inert")
    output = stdout.getvalue()
    for marker in (
        "v300_rt7e_operator_execution_authorized: False",
        "v300_rt7e_operator_http_request_attempted: False",
        "v300_rt7e_operator_provider_execution_attempted: False",
        "v300_rt7e_operator_network_execution_attempted: False",
        "v300_rt7e_operator_real_motion_executed: False",
    ):
        require(output, marker, "inert corrective runner output")
    if stderr.getvalue():
        fail("inert corrective runner wrote unexpected stderr output")


def validate_corrected_runtime_contract() -> None:
    runner = _import_runner()

    payload = {
        "schema_version": runner.RESULT_SCHEMA_VERSION,
        "status": "completed",
        "commands_requested": 1,
        "commands_applied": 1,
        "commands_completed": 1,
        "optional_commands_skipped": 0,
        "command_results": [
            {
                "intent": "gesture",
                "outcome": "completed",
                "skipped": False,
            }
        ],
        "framework_import_attempted": True,
        "session_created": True,
        "session_closed": True,
        "real_adapter_enabled": True,
        "provider_execution_allowed": True,
        "provider_execution_attempted": True,
        "network_execution_attempted": True,
        "real_motion_executed": False,
        "reason_code": "framework_vts_motion_completed",
    }
    encoded = json.dumps(payload).encode("utf-8")

    class FakeResponse:
        status = 200
        headers = {
            "content-type": "application/json",
            "content-length": str(len(encoded)),
        }

        def read(self, amount: int = -1) -> bytes:
            return encoded if amount < 0 else encoded[:amount]

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
            return None

    requests: list[object] = []

    def fake_open(request: object, timeout: float) -> FakeResponse:
        requests.append((request, timeout))
        return FakeResponse()

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=True,
        open_request=fake_open,
        confirm_visible_motion=lambda: True,
        stdout=stdout,
        stderr=stderr,
    )
    if code != 0 or len(requests) != 1 or stderr.getvalue():
        fail("corrected fake acceptance path did not complete exactly once")
    output = stdout.getvalue()
    for marker in (
        "v300_rt7e_operator_backend_contract_valid: True",
        "v300_rt7e_operator_backend_real_motion_executed: False",
        "v300_rt7e_operator_visible_motion_confirmed: True",
        "v300_rt7e_operator_real_motion_executed: True",
    ):
        require(output, marker, "corrected fake acceptance output")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate the RT-7e operator-contract corrective"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip HEAD and worktree checks for an extracted candidate snapshot.",
    )
    args = parser.parse_args(argv)

    validate_scope(args.snapshot)
    validate_doc()
    validate_runner_source()
    validate_inert_runtime()
    validate_corrected_runtime_contract()

    print("v300_rt7e_corrective_status: implemented-awaiting-review")
    print("v300_rt7e_corrective_baseline:", BASELINE)
    print("v300_rt7e_corrective_exact_change_surface: True")
    print("v300_rt7e_corrective_change_file_count: 4")
    print("v300_rt7e_backend_runtime_changed: False")
    print("v300_rt7e_flutter_runtime_changed: False")
    print("v300_rt7e_vendor_framework_changed: False")
    print("v300_rt7e_private_configuration_read: False")
    print("v300_rt7e_provider_execution_attempted: False")
    print("v300_rt7e_network_execution_attempted: False")
    print("v300_rt7e_real_motion_executed: False")
    print("v300_rt7e_backend_real_motion_marker_required_false: True")
    print("v300_rt7e_operator_confirmation_promotes_real_motion: True")
    print("v300_rt7e_allowlisted_failure_diagnostics: True")
    print("v300_rt7e_additional_real_execution_authorized: False")
    print("v300_rt7e_acceptance_sync_authorized: False")
    print("v300_rt7e_commit_push_authorized: False")
    print("v300_rt7e_corrective_snapshot_mode:", args.snapshot)


if __name__ == "__main__":
    main()
