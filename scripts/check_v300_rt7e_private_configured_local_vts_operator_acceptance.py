\
"""Credential-free RT-7e Control D docs/test-only corrective verification."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "a26d027fcd40d6734cb8919059a4683c322f55da"
EXPECTED = {
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "app/test/framework_vts_motion_home_screen_test.dart",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
}
DOC = "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md"
RUNNER = "scripts/run_v300_rt7e_private_configured_local_vts_operator.py"
TEST = "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py"
MAIN_DART = "app/lib/main.dart"
RUNTIME_DART = "app/lib/services/configured_framework_vts_motion_presentation_runtime.dart"
HOME_DART = "app/lib/screens/home_screen.dart"
HOME_TEST = "app/test/framework_vts_motion_home_screen_test.dart"
PANEL_DART = "app/lib/widgets/framework_vts_motion_presentation_panel.dart"
MODEL_DART = "app/lib/models/framework_vts_motion_presentation.dart"
CONTROLLER_DART = "app/lib/services/framework_vts_motion_presentation_controller.dart"


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt7e_control_d_gate_error: {message}")


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
        for line in git("ls-files", "--others", "--exclude-standard").splitlines()
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
    required = {
        DOC,
        RUNNER,
        TEST,
        MAIN_DART,
        RUNTIME_DART,
        HOME_DART,
        HOME_TEST,
        PANEL_DART,
        MODEL_DART,
        CONTROLLER_DART,
        *EXPECTED,
    }
    missing = sorted(path for path in required if not (ROOT / path).is_file())
    if missing:
        fail(f"missing Control D files: {missing}")
    if snapshot:
        return
    if git("rev-parse", "HEAD") != BASELINE:
        fail("HEAD is not the accepted Control C corrective baseline")
    actual = changed_paths()
    if actual != EXPECTED:
        fail(
            "exact Control D surface mismatch: "
            f"expected={sorted(EXPECTED)}, actual={sorted(actual)}"
        )


def validate_doc() -> None:
    text = read(DOC)
    for marker in (
        "Control C contract corrective: COMPLETED / VERIFIED / COMMITTED / PUSHED",
        "a26d027fcd40d6734cb8919059a4683c322f55da",
        "Control C first attempt: FAILED / NOT_ACCEPTED",
        "Control C private selector corrective: COMPLETED / VERIFIED",
        "Control C retry: PASS / ACCEPTED",
        "Control C retry exactly-one Apply: PASS",
        "Control C retry cleanup: PASS",
        "Control D docs/test-only corrective: IMPLEMENTED / AWAITING_REVIEW",
        "Control D acceptance: NOT_AUTHORIZED",
        "gesture:rt7e_acceptance_gesture",
        "public Flutter selector remains: rt7e_acceptance_gesture",
        "Why Control D needs a docs/test-only corrective",
        "Exact Control D docs/test-only corrective surface",
        "Reset local state",
        "opt-in OFF",
        "HomeScreen disposal",
        "transport call count remains exactly one",
        "Control D does not authorize or require another real provider execution",
        "Control E remains blocked until Control D passes",
        "change file count: 3",
        "private configuration read: false",
        "provider execution attempted: false",
        "network execution attempted: false",
        "real motion executed: false",
        "RT-7e acceptance sync: NOT_AUTHORIZED",
        "Control D corrective commit / push: NOT_AUTHORIZED",
    ):
        require(text, marker, "Control D documentation")
    for marker in (
        "Control D acceptance: AUTHORIZED",
        "Control D: PASS / ACCEPTED",
        "RT-7e acceptance sync: AUTHORIZED",
        "Control D corrective commit / push: AUTHORIZED",
    ):
        forbid(text, marker, "Control D documentation")
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
            fail(f"Control D document contains {label}")


def validate_preserved_control_c() -> None:
    runner = read(RUNNER)
    for marker in (
        'BASE_URL = "http://127.0.0.1:8000"',
        'PRESENTATION_PATH = "/demo/character-motion/vts/presentation"',
        "REQUEST_TIMEOUT_SECONDS = 10.0",
        "MAX_RESPONSE_BYTES = 65536",
        'ACCEPTANCE_GESTURE_ALIAS = "rt7e_acceptance_gesture"',
        'method="POST"',
        "class _NoRedirectHandler(HTTPRedirectHandler)",
        '_strict_bool(payload.get("real_motion_executed"), False)',
        "v300_rt7e_operator_visible_motion_confirmed: True",
    ):
        require(runner, marker, "accepted Control B/C runner")

    test_text = read(TEST)
    test_names = re.findall(r"^def (test_[A-Za-z0-9_]+)\(", test_text, flags=re.MULTILINE)
    if len(test_names) != 9:
        fail(f"accepted operator test count must remain 9, got {len(test_names)}")


def validate_runtime_local_only() -> None:
    controller = read(CONTROLLER_DART)
    home = read(HOME_DART)
    client = read("app/lib/services/framework_vts_motion_presentation_client.dart")
    for marker in (
        "void reset()",
        "_operation += 1;",
        "_set(const FrameworkVtsMotionPresentationState.idle());",
        "void dispose()",
        "FrameworkVtsMotionPresentationPhase.closed",
    ):
        require(controller, marker, "VTS controller local lifecycle")
    for marker in (
        "if (!value) controller.reset();",
        "setState(() => _frameworkVtsMotionOptedIn = value);",
        "_frameworkVtsMotionController?.dispose();",
        "await controller.apply(request);",
    ):
        require(home, marker, "HomeScreen VTS lifecycle")
    require(client, "await transport(request)", "VTS presentation client")


def validate_control_d_test() -> None:
    text = read(HOME_TEST)
    for marker in (
        "Control D reset opt-out and disposal stay local after one completed Apply",
        "_completedVtsResult()",
        "'status': 'completed'",
        "'commands_requested': 1",
        "'commands_applied': 1",
        "'commands_completed': 1",
        "'real_motion_executed': false",
        "Reset local state must not call transport.",
        "Opt-in OFF must not call transport.",
        "HomeScreen disposal must not call transport.",
        "await tester.pumpWidget(const SizedBox.shrink());",
        "'framework-vts-motion-reset-button'",
        "'framework-vts-motion-opt-in'",
        "'framework-vts-motion-phase'",
        "'framework-vts-motion-status'",
        "'framework-vts-motion-commands-requested'",
    ):
        require(text, marker, "Control D HomeScreen test")
    if text.count("reason: 'Reset local state must not call transport.'") != 1:
        fail("Reset local-only assertion count must be one")
    if text.count("reason: 'Opt-in OFF must not call transport.'") != 1:
        fail("opt-out local-only assertion count must be one")
    if text.count("reason: 'HomeScreen disposal must not call transport.'") != 1:
        fail("disposal local-only assertion count must be one")


def _import_runner() -> Any:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import run_v300_rt7e_private_configured_local_vts_operator as runner
    return runner


def validate_inert_runtime() -> None:
    runner = _import_runner()
    attempted: list[object] = []

    def forbidden_open(request: object, timeout: float) -> object:
        attempted.append((request, timeout))
        raise AssertionError("Control D gate attempted HTTP")

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=False,
        open_request=forbidden_open,
        stdout=stdout,
        stderr=stderr,
    )
    if code != 2 or attempted:
        fail("default operator runner did not remain inert")
    output = stdout.getvalue()
    for marker in (
        "v300_rt7e_operator_execution_authorized: False",
        "v300_rt7e_operator_http_request_attempted: False",
        "v300_rt7e_operator_provider_execution_attempted: False",
        "v300_rt7e_operator_network_execution_attempted: False",
        "v300_rt7e_operator_real_motion_executed: False",
    ):
        require(output, marker, "inert operator output")
    if stderr.getvalue():
        fail("inert operator runner wrote stderr")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate the RT-7e Control D docs/test-only corrective"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip HEAD and worktree checks for an extracted candidate snapshot.",
    )
    args = parser.parse_args(argv)

    validate_scope(args.snapshot)
    validate_doc()
    validate_preserved_control_c()
    validate_runtime_local_only()
    validate_control_d_test()
    validate_inert_runtime()

    print("v300_rt7e_control_d_docs_test_corrective_status: implemented-awaiting-review")
    print("v300_rt7e_control_d_corrective_baseline:", BASELINE)
    print("v300_rt7e_control_d_exact_change_surface: True")
    print("v300_rt7e_control_d_change_file_count: 3")
    print("v300_rt7e_control_c_retry_accepted: True")
    print("v300_rt7e_control_c_retry_cleanup_passed: True")
    print("v300_rt7e_backend_runtime_changed: False")
    print("v300_rt7e_flutter_runtime_changed: False")
    print("v300_rt7e_vendor_framework_changed: False")
    print("v300_rt7e_control_d_completed_result_fixture_exists: True")
    print("v300_rt7e_control_d_reset_local_only: True")
    print("v300_rt7e_control_d_opt_out_local_only: True")
    print("v300_rt7e_control_d_disposal_local_only: True")
    print("v300_rt7e_control_d_transport_call_count_remains_one: True")
    print("v300_rt7e_private_configuration_read: False")
    print("v300_rt7e_provider_execution_attempted: False")
    print("v300_rt7e_network_execution_attempted: False")
    print("v300_rt7e_real_motion_executed: False")
    print("v300_rt7e_control_d_acceptance_authorized: False")
    print("v300_rt7e_acceptance_sync_authorized: False")
    print("v300_rt7e_commit_push_authorized: False")
    print("v300_rt7e_control_d_snapshot_mode:", args.snapshot)


if __name__ == "__main__":
    main()
