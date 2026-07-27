"""Validate RT-2e-c1 operator harness readiness without real execution."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IMPLEMENTATION_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_record_microphone_capture_adapter.md",
    "docs/v300_rt2ec_operator_capture_harness_readiness.md",
    "scripts/check_v300_rt2ec_operator_capture_harness_readiness.py",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"RT-2e-c1 missing {label}: {marker}")


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise AssertionError(f"RT-2e-c1 git check failed: {detail}")
    return completed.stdout


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for raw in run_git(
        "status", "--porcelain=v1", "--untracked-files=all"
    ).splitlines():
        if not raw:
            continue
        path = raw[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def validate_changed_surface() -> None:
    actual = changed_paths()
    if not actual:
        return
    unexpected = sorted(actual - IMPLEMENTATION_PATHS)
    missing = sorted(IMPLEMENTATION_PATHS - actual)
    if unexpected or missing:
        details: list[str] = []
        if unexpected:
            details.append("unexpected changed paths:\n" + "\n".join(unexpected))
        if missing:
            details.append("missing acceptance-sync paths:\n" + "\n".join(missing))
        details.append(
            "required worktree form: clean tree or exact eight-file docs/test-only acceptance sync"
        )
        raise AssertionError(
            "RT-2e-c1 accepted-state surface mismatch:\n" + "\n".join(details)
        )


def lock_package_block(lock: str, package: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(package)}:\n(.*?)(?=^  [a-zA-Z0-9_]+:|\Z)",
        lock,
    )
    if match is None:
        raise AssertionError(f"RT-2e-c1 lockfile missing package: {package}")
    return match.group(1)


def validate_exact_current_surface() -> None:
    pubspec = read("app/pubspec.yaml")
    lock = read("app/pubspec.lock")
    main = read("app/lib/main.dart")
    home = read("app/lib/screens/home_screen.dart")
    capture = read("app/lib/services/microphone_capture.dart")
    permission = read(
        "app/lib/services/permission_handler_microphone_permission_gateway.dart"
    )
    adapter = read("app/lib/services/record_microphone_capture_engine.dart")
    android = read("app/android/app/src/main/AndroidManifest.xml")
    ios = read("app/ios/Runner/Info.plist")

    require(pubspec, "sdk: ^3.11.5", "Dart SDK baseline")
    require(pubspec, "  permission_handler: 12.0.3", "permission dependency")
    require(pubspec, "  path_provider: 2.1.6", "path_provider pin")
    require(pubspec, "  record: 6.2.1", "record pin")
    for package, version in (("record", "6.2.1"), ("path_provider", "2.1.6")):
        block = lock_package_block(lock, package)
        require(block, 'dependency: "direct main"', f"{package} direct lock entry")
        require(block, f'version: "{version}"', f"{package} locked version")

    require(main, "home: const HomeScreen()", "normal startup boundary")
    for forbidden in (
        "microphone_capture.dart",
        "microphone_permission.dart",
        "record_microphone_capture_engine.dart",
        "main_rt2ec_operator.dart",
    ):
        if forbidden in main:
            raise AssertionError(f"RT-2e-c1 default main changed early: {forbidden}")

    for forbidden in (
        "MicrophoneCaptureController",
        "PermissionHandlerMicrophonePermissionGateway",
        "RecordMicrophoneCaptureEngine",
        "requestPermission()",
    ):
        if forbidden in home:
            raise AssertionError(f"RT-2e-c1 HomeScreen wiring started early: {forbidden}")

    require(capture, "maximumAllowedDuration = const Duration(seconds: 60)", "capture hard ceiling")
    require(capture, "Future<MicrophoneCaptureResult> start(", "capture start boundary")
    require(permission, "requestMicrophonePermission()", "explicit permission driver boundary")
    require(adapter, "factory RecordMicrophoneCaptureEngine.mobile()", "mobile adapter factory")
    require(adapter, "AudioEncoder.wav", "WAV file mode")
    require(adapter, "'sample_rate_hz': 16000", "sample rate marker")
    require(adapter, "'channels': 1", "mono marker")
    require(adapter, "discardPrivateArtifact", "private artifact cleanup boundary")
    if ".startStream(" in adapter:
        raise AssertionError("RT-2e-c1 startStream remains forbidden")

    require(android, "android.permission.RECORD_AUDIO", "Android RECORD_AUDIO")
    require(ios, "NSMicrophoneUsageDescription", "iOS usage description")

    for relative in (
        "app/lib/main_rt2ec_operator.dart",
        "app/lib/operators/rt2ec_microphone_capture_operator.dart",
        "app/test/rt2ec_microphone_capture_operator_test.dart",
    ):
        if (ROOT / relative).exists():
            raise AssertionError(f"RT-2e-c1 executable harness added early: {relative}")


def validate_docs() -> None:
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    adapter_contract = read("docs/v300_record_microphone_capture_adapter.md")
    contract = read("docs/v300_rt2ec_operator_capture_harness_readiness.md")

    for source, marker, label in (
        (readme, "Current small commit: RT-2e-c2 (**CURRENT / NOT_COMPLETED**)", "README current commit"),
        (roadmap, "Current small commit: RT-2e-c2 CURRENT / NOT_COMPLETED", "roadmap current commit"),
        (tasklist, "implementation: COMPLETED / ACCEPTED; docs/test-only", "tasklist implementation state"),
        (checklist, "#### RT-2e-c1 operator-only harness/readiness contract", "checklist split"),
        (adapter_contract, "## RT-2e-c1 operator harness readiness decision", "adapter follow-up"),
        (contract, "Status: COMPLETED / ACCEPTED", "contract status"),
        (scripts_readme, "v300_rt2ec_operator_capture_harness_readiness_status: completed-accepted", "expected gate status"),
    ):
        require(source, marker, label)

    combined = "\n".join(
        (readme, roadmap, tasklist, scripts_readme, checklist, adapter_contract, contract)
    )
    for marker in (
        "main_rt2ec_operator.dart",
        "DRC_RT2EC_OPERATOR=true",
        "in-app acknowledgement",
        "15 seconds",
        "WAV 16 kHz mono",
        "opaque id",
        "discardPrivateArtifact",
        "safe evidence",
        "default app",
        "authorized-separate-operator-harness-and-fake-widget-tests-only",
        "blocked-pending-rt2ec2-acceptance",
        "No upload or STT",
    ):
        require(combined, marker, "operator readiness marker")


def main() -> None:
    validate_changed_surface()
    validate_exact_current_surface()
    validate_docs()

    print("v300_rt2ec_operator_capture_harness_readiness_status: completed-accepted")
    print("v300_rt2ec1_exact_current_surface_inspected: True")
    print("v300_rt2ec1_separate_operator_entrypoint_planned: True")
    print("v300_rt2ec1_compile_time_opt_in_required: True")
    print("v300_rt2ec1_in_app_acknowledgement_required: True")
    print("v300_rt2ec1_permission_actions_explicit_only: True")
    print("v300_rt2ec1_maximum_capture_seconds: 15")
    print("v300_rt2ec1_private_artifact_auto_discard_required: True")
    print("v300_rt2ec1_safe_evidence_allowlist_required: True")
    print("v300_rt2ec1_default_app_wiring_changed: False")
    print("v300_rt2ec1_flutter_runtime_changed: False")
    print("v300_rt2ec1_permission_request_executed: False")
    print("v300_rt2ec1_microphone_accessed: False")
    print("v300_rt2ec1_audio_captured: False")
    print("v300_rt2ec_parent_status: current-pending-rt2ec2-implementation")
    print("v300_rt2ec2_authorization: authorized-separate-operator-harness-and-fake-widget-tests-only")
    print("v300_rt2ec3_authorization: blocked-pending-rt2ec2-acceptance")


if __name__ == "__main__":
    main()
