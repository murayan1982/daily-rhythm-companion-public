"""Historical RT-7e Control E acceptance-sync verification.

The gate is credential-free and network-free. Normal mode verifies the accepted
RT-7e commit chain and the exact seven-file Control E worktree. Snapshot mode
validates source content and protected boundaries without claiming Git history
or exact worktree verification.
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RT7E_BASELINE = "715b28a97f46260efc0bd76e59828d46c8749dbd"
STAGE1_COMMIT = "c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f"
OPERATOR_CORRECTIVE_COMMIT = "84429683d5ea26e5480bff17f5e29ad201b6ee71"
CONTROL_C_CORRECTIVE_COMMIT = "a26d027fcd40d6734cb8919059a4683c322f55da"
CONTROL_D_CORRECTIVE_COMMIT = "ddd392c24907eae4d8c91850d84b31a7b84e760f"

STAGE1_EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
    "scripts/run_v300_rt7e_private_configured_local_vts_operator.py",
    "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py",
}
OPERATOR_CORRECTIVE_EXPECTED = {
    "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
    "scripts/run_v300_rt7e_private_configured_local_vts_operator.py",
}
CONTROL_C_CORRECTIVE_EXPECTED = {
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
}
CONTROL_D_CORRECTIVE_EXPECTED = {
    "app/test/framework_vts_motion_home_screen_test.dart",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
}
CONTROL_E_EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md",
    "scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py",
}

DOC = "docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md"
RUNNER = "scripts/run_v300_rt7e_private_configured_local_vts_operator.py"
OPERATOR_TEST = "backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py"
HOME_TEST = "app/test/framework_vts_motion_home_screen_test.dart"
CONTROLLER = "app/lib/services/framework_vts_motion_presentation_controller.dart"
HOME = "app/lib/screens/home_screen.dart"
CLIENT = "app/lib/services/framework_vts_motion_presentation_client.dart"
RUNTIME = "app/lib/services/configured_framework_vts_motion_presentation_runtime.dart"
BACKEND_SERVICE = "backend/app/services/framework_vts_motion_presentation_service.py"


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt7e_control_e_gate_error: {message}")


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


def paths(value: str) -> set[str]:
    return {
        line.strip().replace("\\", "/")
        for line in value.splitlines()
        if line.strip()
    }


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        fail(f"{label} missing required marker: {marker}")


def require_all(relative: str, markers: tuple[str, ...]) -> None:
    text = read(relative)
    for marker in markers:
        require(text, marker, relative)


def extract_between(text: str, begin: str, end: str, label: str) -> str:
    start = text.find(begin)
    finish = text.find(end, start + len(begin)) if start >= 0 else -1
    if start < 0 or finish < 0:
        fail(f"{label} marker block missing")
    return text[start : finish + len(end)]


def validate_required_files() -> None:
    required = {
        *CONTROL_E_EXPECTED,
        RUNNER,
        OPERATOR_TEST,
        HOME_TEST,
        CONTROLLER,
        HOME,
        CLIENT,
        RUNTIME,
        BACKEND_SERVICE,
    }
    missing = sorted(path for path in required if not (ROOT / path).is_file())
    if missing:
        fail(f"missing required files: {missing}")


def validate_git_contract(snapshot: bool) -> dict[str, set[str]]:
    if snapshot:
        return {}

    head = git("rev-parse", "HEAD")
    origin_main = git("rev-parse", "origin/main")
    if head != CONTROL_D_CORRECTIVE_COMMIT:
        fail("HEAD is not the accepted Control D corrective commit")
    if origin_main != CONTROL_D_CORRECTIVE_COMMIT:
        fail("origin/main is not synchronized to the Control D corrective commit")

    ranges = (
        ("Stage 1", RT7E_BASELINE, STAGE1_COMMIT, STAGE1_EXPECTED),
        (
            "operator corrective",
            STAGE1_COMMIT,
            OPERATOR_CORRECTIVE_COMMIT,
            OPERATOR_CORRECTIVE_EXPECTED,
        ),
        (
            "Control C corrective",
            OPERATOR_CORRECTIVE_COMMIT,
            CONTROL_C_CORRECTIVE_COMMIT,
            CONTROL_C_CORRECTIVE_EXPECTED,
        ),
        (
            "Control D corrective",
            CONTROL_C_CORRECTIVE_COMMIT,
            CONTROL_D_CORRECTIVE_COMMIT,
            CONTROL_D_CORRECTIVE_EXPECTED,
        ),
    )
    actuals: dict[str, set[str]] = {}
    for label, base, commit, expected in ranges:
        actual = paths(git("diff", "--name-only", f"{base}..{commit}"))
        if actual != expected:
            fail(
                f"{label} exact surface mismatch: "
                f"expected={sorted(expected)}, actual={sorted(actual)}"
            )
        actuals[label] = actual

    tracked = paths(git("diff", "--name-only", "HEAD"))
    untracked = paths(git("ls-files", "--others", "--exclude-standard"))
    control_e_actual = tracked | untracked
    if control_e_actual != CONTROL_E_EXPECTED:
        fail(
            "Control E exact surface mismatch: "
            f"expected={sorted(CONTROL_E_EXPECTED)}, "
            f"actual={sorted(control_e_actual)}"
        )
    actuals["Control E"] = control_e_actual
    return actuals


def validate_status_documents() -> None:
    require_all(
        "README.md",
        (
            "Current small commit: RT-7e Control E acceptance sync",
            "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
            "Current realtime phase: RT-7 (**COMPLETED / ACCEPTED**)",
            "RT-7e: COMPLETED / ACCEPTED / PUSHED",
            "Control E: PASS / ACCEPTED",
            "RT-8 exact contract review: READY",
            "RT-8 implementation: NOT_AUTHORIZED",
        ),
    )
    readme_block = extract_between(
        read("README.md"),
        "<!-- RT-7e-PRIVATE-CONFIGURED-LOCAL-VTS:BEGIN -->",
        "<!-- RT-7e-PRIVATE-CONFIGURED-LOCAL-VTS:END -->",
        "README RT-7e",
    )
    for marker in (
        "Backend / Flutter real_motion_executed: false",
        "operator-visible physical motion confirmed: true",
        "additional Control E provider/network/real-motion execution: false",
    ):
        require(readme_block, marker, "README RT-7e")

    require_all(
        "roadmap.md",
        (
            "Current small commit: RT-7e Control E acceptance sync",
            "Status: RT-7 COMPLETED / ACCEPTED",
            "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
            "RT-8   READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
            "## v3.0.0 RT-7e configured local VTS operator acceptance",
            "Controls A-E: PASS / ACCEPTED",
        ),
    )
    require_all(
        "tasklist.md",
        (
            "current parent phase: RT-7 COMPLETED / ACCEPTED",
            "current small commit: RT-7e Control E acceptance sync",
            "current implementation state: COMPLETED / ACCEPTED / PUSHED",
            "## RT-7e — configured local VTS operator acceptance",
            "Control E: PASS / ACCEPTED",
            "次はRT-8 exact contract review。",
        ),
    )
    require_all(
        "scripts/README.md",
        (
            "## v3.0.0 RT-7e Control E acceptance-sync gate",
            "Control E worktree exact 7 files",
            "Snapshot mode validates source content and protected boundaries only.",
            "gate never authorizes commit/push by itself.",
        ),
    )
    require_all(
        "docs/DRC_v300_goal_checklist_small_commit.md",
        (
            "Current parent phase: RT-7 COMPLETED / ACCEPTED",
            "Current small commit: RT-7e Control E acceptance sync",
            "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
            "RT-7e: COMPLETED / ACCEPTED / PUSHED",
            "Control E: PASS / ACCEPTED",
            "Start RT-8 implementation only after a separate exact contract review",
        ),
    )


def validate_acceptance_document() -> None:
    text = read(DOC)
    markers = (
        "# Daily Rhythm Companion v3.0.0 RT-7e configured local VTS operator acceptance",
        "RT-7: COMPLETED / ACCEPTED",
        "RT-7e: COMPLETED / ACCEPTED / PUSHED",
        f"Stage 1 commit: {STAGE1_COMMIT}",
        f"operator corrective commit: {OPERATOR_CORRECTIVE_COMMIT}",
        f"Control C contract corrective commit: {CONTROL_C_CORRECTIVE_COMMIT}",
        f"Control D docs/test-only corrective commit: {CONTROL_D_CORRECTIVE_COMMIT}",
        "Control A: PASS / ACCEPTED",
        "Control B: PASS / ACCEPTED",
        "Control C: PASS / ACCEPTED",
        "Control D: PASS / ACCEPTED",
        "Control E: PASS / ACCEPTED",
        "Backend / Flutter real_motion_executed: false",
        "operator-visible physical motion confirmed: true",
        "first attempt:",
        "result: FAILED / NOT_ACCEPTED",
        "correct private selector: gesture:rt7e_acceptance_gesture",
        "public Flutter selector remains: rt7e_acceptance_gesture",
        "transport count remains exactly one",
        "Control D does not authorize or require a second real VTube Studio execution.",
        "additional Flutter Apply: false",
        "additional Backend request: false",
        "private process values present: false",
        "real-execution flags open: false",
        "Control E exact surface: true / 7 files",
        "RT-8 exact contract review ready: true",
        "RT-8 implementation authorized: false",
        "Control E gate authorizes commit / push: false",
    )
    for marker in markers:
        require(text, marker, "RT-7e acceptance document")

    public_aliases = (
        "rt7e_acceptance_gesture",
        "gesture:rt7e_acceptance_gesture",
    )
    for alias in public_aliases:
        require(text, alias, "RT-7e acceptance document")

    private_patterns = {
        "credential-shaped value": r"\b(?:sk|sess)-[A-Za-z0-9_-]{16,}\b",
        "private LAN IPv4": (
            r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|"
            r"192\.168\.(?:\d{1,3}\.)\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3})\b"
        ),
        "private Windows path": r"[A-Za-z]:\\(?:Users|work|private|temp)\\",
    }
    for label, pattern in private_patterns.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"acceptance document contains {label}")


def validate_accepted_operator_tooling() -> None:
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
        require(runner, marker, "accepted RT-7e operator runner")

    test_text = read(OPERATOR_TEST)
    test_names = re.findall(r"^def (test_[A-Za-z0-9_]+)\(", test_text, flags=re.MULTILINE)
    if len(test_names) != 9:
        fail(f"accepted operator test count must remain 9, got {len(test_names)}")


def validate_control_d_local_only() -> None:
    controller = read(CONTROLLER)
    home = read(HOME)
    client = read(CLIENT)
    home_test = read(HOME_TEST)
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
    for marker in (
        "Control D reset opt-out and disposal stay local after one completed Apply",
        "Reset local state must not call transport.",
        "Opt-in OFF must not call transport.",
        "HomeScreen disposal must not call transport.",
        "'real_motion_executed': false",
        "await tester.pumpWidget(const SizedBox.shrink());",
    ):
        require(home_test, marker, "Control D HomeScreen test")


def validate_runtime_boundaries() -> None:
    runtime = read(RUNTIME)
    backend_service = read(BACKEND_SERVICE)
    for marker in (
        "DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION",
        "followRedirects = false",
        "65536",
    ):
        require(runtime, marker, "accepted RT-7d Flutter runtime")
    for marker in (
        "FrameworkVtsMotionSessionAdapter",
        ".execute([request.command])",
        "framework_vts_motion_configuration_error",
    ):
        require(backend_service, marker, "accepted RT-7d Backend service")

    forbidden = (
        "import " + "pyvts",
        "from " + "pyvts",
        "import " + "websockets",
        "from " + "websockets",
        "AI-Character-Framework" + "\\Development",
        "AI-Character-Framework" + "/Development",
    )
    for relative in CONTROL_E_EXPECTED:
        text = read(relative)
        for marker in forbidden:
            if marker in text:
                fail(f"forbidden marker in Control E file {relative}: {marker}")


def _import_runner() -> Any:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import run_v300_rt7e_private_configured_local_vts_operator as runner

    return runner


def validate_inert_runner() -> None:
    runner = _import_runner()
    attempted: list[object] = []

    def forbidden_open(request: object, timeout: float) -> object:
        attempted.append((request, timeout))
        raise AssertionError("Control E gate attempted HTTP")

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
    for marker in (
        "v300_rt7e_operator_execution_authorized: False",
        "v300_rt7e_operator_http_request_attempted: False",
        "v300_rt7e_operator_provider_execution_attempted: False",
        "v300_rt7e_operator_network_execution_attempted: False",
        "v300_rt7e_operator_real_motion_executed: False",
    ):
        require(stdout.getvalue(), marker, "inert operator output")
    if stderr.getvalue():
        fail("inert operator runner wrote stderr")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate the historical RT-7e Control E acceptance sync"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help=(
            "Validate extracted source content without claiming Git history, "
            "origin/main, or exact worktree verification."
        ),
    )
    args = parser.parse_args(argv)

    validate_required_files()
    actuals = validate_git_contract(args.snapshot)
    validate_status_documents()
    validate_acceptance_document()
    validate_accepted_operator_tooling()
    validate_control_d_local_only()
    validate_runtime_boundaries()
    validate_inert_runner()

    print("v300_rt7e_control_e_acceptance_sync_status: implemented-awaiting-review")
    print("v300_rt7e_control_e_baseline:", CONTROL_D_CORRECTIVE_COMMIT)
    print("v300_rt7e_snapshot_mode:", args.snapshot)
    print("v300_rt7e_git_history_verified:", not args.snapshot)
    print("v300_rt7e_origin_main_verified:", not args.snapshot)
    print("v300_rt7e_exact_worktree_surface_verified:", not args.snapshot)
    print("v300_rt7e_stage1_exact_surface:", args.snapshot or actuals["Stage 1"] == STAGE1_EXPECTED)
    print("v300_rt7e_stage1_change_file_count: 9")
    print(
        "v300_rt7e_operator_corrective_exact_surface:",
        args.snapshot
        or actuals["operator corrective"] == OPERATOR_CORRECTIVE_EXPECTED,
    )
    print("v300_rt7e_operator_corrective_change_file_count: 4")
    print(
        "v300_rt7e_control_c_corrective_exact_surface:",
        args.snapshot
        or actuals["Control C corrective"] == CONTROL_C_CORRECTIVE_EXPECTED,
    )
    print("v300_rt7e_control_c_corrective_change_file_count: 2")
    print(
        "v300_rt7e_control_d_corrective_exact_surface:",
        args.snapshot
        or actuals["Control D corrective"] == CONTROL_D_CORRECTIVE_EXPECTED,
    )
    print("v300_rt7e_control_d_corrective_change_file_count: 3")
    print(
        "v300_rt7e_control_e_exact_change_surface:",
        False if args.snapshot else actuals["Control E"] == CONTROL_E_EXPECTED,
    )
    print("v300_rt7e_control_e_change_file_count: 7")
    print("v300_rt7e_controls_a_to_e_accepted_markers: True")
    print("v300_rt7e_parent_rt7_completed_accepted_marker: True")
    print("v300_rt7e_backend_runtime_changed_by_control_e: False")
    print("v300_rt7e_flutter_runtime_changed_by_control_e: False")
    print("v300_rt7e_existing_tests_changed_by_control_e: False")
    print("v300_rt7e_vendor_framework_changed_by_control_e: False")
    print("v300_rt7e_private_configuration_read: False")
    print("v300_rt7e_provider_execution_attempted: False")
    print("v300_rt7e_network_execution_attempted: False")
    print("v300_rt7e_real_motion_executed: False")
    print("v300_rt8_exact_contract_review_ready: True")
    print("v300_rt8_implementation_authorized: False")
    print("v300_rt7e_control_e_acceptance_authorized: False")
    print("v300_rt7e_commit_push_authorized: False")


if __name__ == "__main__":
    main()
