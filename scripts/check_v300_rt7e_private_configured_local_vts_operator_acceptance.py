\
"""Credential-free RT-7e Control C contract-corrective verification."""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "84429683d5ea26e5480bff17f5e29ad201b6ee71"
EXPECTED = {
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
}
DOC = "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md"
RUNNER = "scripts/run_v300_rt7e_private_configured_local_vts_operator.py"
TEST = "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py"
MAIN_DART = "app/lib/main.dart"
RUNTIME_DART = (
    "app/lib/services/"
    "configured_framework_vts_motion_presentation_runtime.dart"
)
HOME_DART = "app/lib/screens/home_screen.dart"
PANEL_DART = "app/lib/widgets/framework_vts_motion_presentation_panel.dart"
MODEL_DART = "app/lib/models/framework_vts_motion_presentation.dart"


def fail(message: str) -> None:
    raise SystemExit(
        f"v300_rt7e_control_c_contract_corrective_gate_error: {message}"
    )


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
    required = {
        DOC,
        RUNNER,
        TEST,
        MAIN_DART,
        RUNTIME_DART,
        HOME_DART,
        PANEL_DART,
        MODEL_DART,
        *EXPECTED,
    }
    missing = sorted(path for path in required if not (ROOT / path).is_file())
    if missing:
        fail(f"missing Control C contract files: {missing}")
    if snapshot:
        return
    if git("rev-parse", "HEAD") != BASELINE:
        fail("HEAD is not the accepted RT-7e operator-corrective baseline")
    actual = changed_paths()
    if actual != EXPECTED:
        fail(
            "exact Control C contract-corrective surface mismatch: "
            f"expected={sorted(EXPECTED)}, actual={sorted(actual)}"
        )


def validate_doc() -> None:
    text = read(DOC)
    for marker in (
        "RT-7e operator corrective: COMPLETED / VERIFIED / COMMITTED / PUSHED",
        "84429683d5ea26e5480bff17f5e29ad201b6ee71",
        "Control A: PASS",
        "Control B: PASS / ACCEPTED",
        "Control B exactly-one POST: PASS",
        "Control B process cleanup: PASS",
        "Control C contract corrective: IMPLEMENTED / AWAITING_REVIEW",
        "Control C execution: NOT_AUTHORIZED",
        "exact two-file corrective",
        "exact change surface: true",
        "change file count: 2",
        "Backend / Flutter transport fact:",
        "real_motion_executed: false",
        "Operator-observed physical fact:",
        "--dart-define=DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION=true",
        "HomeScreen session-local opt-in",
        "Apply one VTS command exactly once",
        "Real motion executed: false",
        "operator visible motion confirmed: true",
        "Control C final real motion accepted: true",
        "Flutter Apply count: exactly 1",
        "Reset local state",
        "Control D remains blocked until Control C passes",
        "Control E remains blocked until Controls C and D pass",
        "backend/app/**",
        "app/lib/**",
        "vendor/**",
        "RT-7e acceptance sync: NOT_AUTHORIZED",
        "Control C corrective commit / push: NOT_AUTHORIZED",
    ):
        require(text, marker, "RT-7e Control C corrective documentation")

    for marker in (
        "Flutter real_motion_executed: true",
        "Backend real_motion_executed: true",
        "Control C execution: AUTHORIZED",
        "RT-7e acceptance sync: AUTHORIZED",
    ):
        forbid(text, marker, "RT-7e Control C corrective documentation")

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
            fail(f"Control C corrective document contains {label}")


def validate_control_b_corrective_preserved() -> None:
    runner = read(RUNNER)
    for marker in (
        'BASE_URL = "http://127.0.0.1:8000"',
        'PRESENTATION_PATH = "/demo/character-motion/vts/presentation"',
        "REQUEST_TIMEOUT_SECONDS = 10.0",
        "MAX_RESPONSE_BYTES = 65536",
        'ACCEPTANCE_GESTURE_ALIAS = "rt7e_acceptance_gesture"',
        'method="POST"',
        "class _NoRedirectHandler(HTTPRedirectHandler)",
        "return None",
        '_strict_bool(payload.get("real_motion_executed"), False)',
        "v300_rt7e_operator_backend_real_motion_executed: False",
        "if confirmation() is not True:",
        "v300_rt7e_operator_visible_motion_confirmed: True",
        "v300_rt7e_operator_real_motion_executed: True",
    ):
        require(runner, marker, "accepted RT-7e operator runner")

    test_text = read(TEST)
    test_names = re.findall(
        r"^def (test_[A-Za-z0-9_]+)\(",
        test_text,
        flags=re.MULTILINE,
    )
    if len(test_names) != 9:
        fail(
            "accepted operator focused test count must remain exactly 9, "
            f"got {len(test_names)}"
        )
    for marker in (
        "test_fixed_gesture_request_uses_exactly_one_post_and_operator_acceptance",
        "test_backend_real_motion_must_remain_false_before_operator_confirmation",
        "test_visible_motion_confirmation_false_never_promotes_real_motion",
        "test_non_completed_response_prints_only_allowlisted_safe_diagnostics",
    ):
        require(test_text, marker, "accepted RT-7e operator tests")


def validate_flutter_control_c_source() -> None:
    main = read(MAIN_DART)
    runtime = read(RUNTIME_DART)
    home = read(HOME_DART)
    panel = read(PANEL_DART)
    model = read(MODEL_DART)

    for marker in (
        "ConfiguredFrameworkVtsMotionPresentationRuntime.fromEnvironment",
        "frameworkVtsMotionPresentationControllerFactory:",
        "configuredFrameworkVtsMotionRuntime.buildControllerFactory()",
    ):
        require(main, marker, "Flutter main VTS wiring")

    for marker in (
        "'DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION'",
        "defaultValue: false",
        "if (!enabled || !_validBaseUrl(base)) return null;",
        "http.Request('POST', endpoint)",
        "..followRedirects = false",
        "..maxRedirects = 0",
        "configuredFrameworkVtsMotionTimeout = Duration(seconds: 10)",
        "configuredFrameworkVtsMotionMaxResponseBytes = 65536",
        "configuredFrameworkVtsMotionPresentationPath =",
        "'/demo/character-motion/vts/presentation'",
    ):
        require(runtime, marker, "Flutter configured VTS runtime")

    for marker in (
        "bool _frameworkVtsMotionOptedIn = false;",
        "return _frameworkVtsMotionOptedIn &&",
        "void _setFrameworkVtsMotionOptIn(bool value)",
        "Future<void> _applyFrameworkVtsMotion() async",
        "await controller.apply(request);",
        "FrameworkVtsMotionPresentationRequest(",
    ):
        require(home, marker, "Flutter HomeScreen VTS control")

    for marker in (
        "'Enable manual configured VTS motion'",
        "'Apply one VTS command'",
        "'Reset local state'",
        "'Real motion executed'",
        "'${result?.realMotionExecuted ?? false}'",
        "'Commands requested'",
        "'Commands applied'",
        "'Commands completed'",
        "'Session closed'",
        "'Provider attempted'",
        "'Network attempted'",
    ):
        require(panel, marker, "Flutter VTS presentation panel")

    for marker in (
        "'real_motion_executed'",
        "realMotionExecuted: _bool(",
        "json['real_motion_executed']",
        "'order': 1",
        "'intent': intent.wireName",
        "'gesture': intent == FrameworkVtsMotionIntent.gesture",
    ):
        require(model, marker, "Flutter VTS result/request model")


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
        raise AssertionError("Control C corrective gate attempted HTTP")

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        execute_real_vts=False,
        open_request=forbidden_open,
        stdout=stdout,
        stderr=stderr,
    )
    if code != 2 or attempted:
        fail("default operator runner did not remain transport-inert")
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
        fail("inert operator runner wrote unexpected stderr output")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate the RT-7e Control C contract corrective"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip HEAD and worktree checks for an extracted candidate snapshot.",
    )
    args = parser.parse_args(argv)

    validate_scope(args.snapshot)
    validate_doc()
    validate_control_b_corrective_preserved()
    validate_flutter_control_c_source()
    validate_inert_runtime()

    print(
        "v300_rt7e_control_c_contract_corrective_status: "
        "implemented-awaiting-review"
    )
    print("v300_rt7e_control_c_contract_corrective_baseline:", BASELINE)
    print("v300_rt7e_control_c_contract_exact_change_surface: True")
    print("v300_rt7e_control_c_contract_change_file_count: 2")
    print("v300_rt7e_control_b_accepted: True")
    print("v300_rt7e_backend_runtime_changed: False")
    print("v300_rt7e_flutter_runtime_changed: False")
    print("v300_rt7e_vendor_framework_changed: False")
    print("v300_rt7e_flutter_compile_flag_explicit: True")
    print("v300_rt7e_flutter_session_opt_in_required: True")
    print("v300_rt7e_flutter_explicit_apply_exactly_one: True")
    print(
        "v300_rt7e_flutter_backend_real_motion_marker_required_false: True"
    )
    print(
        "v300_rt7e_operator_visual_confirmation_promotes_control_c_real_motion: "
        "True"
    )
    print("v300_rt7e_private_configuration_read: False")
    print("v300_rt7e_provider_execution_attempted: False")
    print("v300_rt7e_network_execution_attempted: False")
    print("v300_rt7e_real_motion_executed: False")
    print("v300_rt7e_control_c_execution_authorized: False")
    print("v300_rt7e_acceptance_sync_authorized: False")
    print("v300_rt7e_commit_push_authorized: False")
    print("v300_rt7e_control_c_contract_snapshot_mode:", args.snapshot)


if __name__ == "__main__":
    main()
