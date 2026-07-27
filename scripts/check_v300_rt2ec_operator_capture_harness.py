"""Validate RT-2e-c2 operator harness without real microphone execution."""

from __future__ import annotations

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
    "docs/v300_rt2ec_operator_capture_harness.md",
    "scripts/check_v300_rt2ec_operator_capture_harness.py",
    "app/lib/main_rt2ec_operator.dart",
    "app/lib/operators/rt2ec_microphone_capture_operator.dart",
    "app/test/rt2ec_microphone_capture_operator_test.dart",
}

ACCEPTANCE_SYNC_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_record_microphone_capture_adapter.md",
    "docs/v300_rt2ec_operator_capture_harness_readiness.md",
    "docs/v300_rt2ec_operator_capture_harness.md",
    "scripts/check_v300_rt2ec_operator_capture_harness.py",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"RT-2e-c2 missing {label}: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"RT-2e-c2 forbidden {label}: {marker}")


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
        raise AssertionError(f"RT-2e-c2 git check failed: {detail}")
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
    if actual == IMPLEMENTATION_PATHS or actual == ACCEPTANCE_SYNC_PATHS:
        return

    unexpected = sorted(actual - IMPLEMENTATION_PATHS)
    missing_implementation = sorted(IMPLEMENTATION_PATHS - actual)
    missing_acceptance = sorted(ACCEPTANCE_SYNC_PATHS - actual)
    details: list[str] = []
    if unexpected:
        details.append("unexpected changed paths:\n" + "\n".join(unexpected))
    if missing_implementation:
        details.append(
            "missing twelve-file implementation paths:\n"
            + "\n".join(missing_implementation)
        )
    if missing_acceptance:
        details.append(
            "missing nine-file acceptance-sync paths:\n"
            + "\n".join(missing_acceptance)
        )
    details.append(
        "required worktree form: clean tree, exact twelve-file implementation/acceptance surface, or exact nine-file acceptance sync"
    )
    raise AssertionError(
        "RT-2e-c2 accepted-state surface mismatch:\n" + "\n".join(details)
    )


def validate_default_app_unchanged() -> None:
    main = read("app/lib/main.dart")
    home = read("app/lib/screens/home_screen.dart")
    pubspec = read("app/pubspec.yaml")
    android = read("app/android/app/src/main/AndroidManifest.xml")
    ios = read("app/ios/Runner/Info.plist")

    require(main, "home: const HomeScreen()", "normal HomeScreen startup")
    for marker in (
        "main_rt2ec_operator.dart",
        "Rt2ecOperatorCaptureApp",
        "MicrophoneCaptureController",
        "RecordMicrophoneCaptureEngine",
    ):
        forbid(main, marker, "default main wiring")
    for marker in (
        "Rt2ecOperatorCaptureApp",
        "MicrophoneCaptureController",
        "PermissionHandlerMicrophonePermissionGateway",
        "RecordMicrophoneCaptureEngine",
    ):
        forbid(home, marker, "HomeScreen operator wiring")

    require(pubspec, "  permission_handler: 12.0.3", "permission pin")
    require(pubspec, "  path_provider: 2.1.6", "path_provider pin")
    require(pubspec, "  record: 6.2.1", "record pin")
    require(android, "android.permission.RECORD_AUDIO", "Android declaration")
    require(ios, "NSMicrophoneUsageDescription", "iOS declaration")


def validate_operator_entrypoint() -> None:
    entrypoint = read("app/lib/main_rt2ec_operator.dart")
    require(entrypoint, "bool.fromEnvironment(", "compile-time flag")
    require(entrypoint, "'DRC_RT2EC_OPERATOR'", "operator flag name")
    require(entrypoint, "defaultValue: false", "fail-closed default")
    require(
        entrypoint,
        "dependenciesFactory: _createProductionDependencies",
        "lazy production factory",
    )
    require(
        entrypoint,
        "PermissionHandlerMicrophonePermissionGateway()",
        "production permission gateway",
    )
    require(
        entrypoint,
        "RecordMicrophoneCaptureEngine.mobile()",
        "production record engine",
    )
    require(
        entrypoint,
        "maximumAllowedDuration: rt2ecOperatorMaximumCaptureDuration",
        "15-second production controller bound",
    )
    forbid(entrypoint, ".requestPermission()", "startup permission request")
    forbid(entrypoint, ".start(", "startup capture start")
    forbid(entrypoint, "print(", "runtime logging")
    forbid(entrypoint, "debugPrint(", "runtime debug logging")


def validate_operator_harness() -> None:
    operator = read("app/lib/operators/rt2ec_microphone_capture_operator.dart")

    for marker, label in (
        ("Duration(seconds: 15)", "15-second constant"),
        ("operatorTargetEnabled", "compile-time state input"),
        ("_acknowledged", "in-app acknowledgement"),
        ("widget.dependenciesFactory()", "post-ack dependency creation"),
        ("checkPermission()", "explicit permission check"),
        ("requestPermission()", "explicit permission request"),
        ("_captureController.start(", "explicit capture start"),
        ("_captureController.stop()", "explicit capture stop"),
        ("_captureController.cancel()", "explicit capture cancel"),
        ("discardPrivateArtifact(", "immediate private artifact discard"),
        ("rt2ecOperatorMaximumCaptureDuration", "bounded request"),
        ("Rt2ecOperatorCaptureEvidence", "safe evidence model"),
        ("private artifact discarded", "discard evidence"),
        ("raw audio exposed", "raw audio evidence"),
    ):
        require(operator, marker, label)

    acknowledgement_guard = (
        "if (!widget.operatorTargetEnabled || !_acknowledged)"
    )
    require(operator, acknowledgement_guard, "double opt-in factory guard")

    for forbidden_marker, label in (
        ("resolvePrivateArtifactPath(", "private path resolution"),
        ("startStream(", "raw stream capture"),
        ("print(", "runtime logging"),
        ("debugPrint(", "runtime debug logging"),
        ("BackendApiClient", "Backend integration"),
        ("transcript", "transcript integration"),
    ):
        forbid(operator, forbidden_marker, label)

    safe_map_start = operator.index("Map<String, Object> toSafeMap()")
    safe_map_end = operator.index("class Rt2ecOperatorCaptureDependencies")
    safe_map = operator[safe_map_start:safe_map_end]
    for marker in (
        "operator target enabled",
        "acknowledgement completed",
        "permission status",
        "permission request attempted",
        "capture phase",
        "capture outcome",
        "technical code",
        "requested maximum duration",
        "captured duration",
        "microphone accessed",
        "audio captured",
        "raw audio exposed",
        "private artifact registered",
        "private artifact discarded",
        "cleanup succeeded",
    ):
        require(safe_map, marker, "safe evidence allowlist")
    for marker in ("opaque", "private path", "bytes", "audio content"):
        forbid(safe_map, marker, "unsafe evidence field")


def validate_fake_widget_tests() -> None:
    tests = read("app/test/rt2ec_microphone_capture_operator_test.dart")
    require(tests, "factoryCalls, 0", "disabled/pre-ack lazy construction test")
    require(tests, "permission.checkCalls, 0", "no startup permission test")
    require(tests, "permission.requestCalls, 0", "no startup request test")
    require(tests, "engine.startCalls, 0", "no startup capture test")
    require(tests, "rt2ecOperatorMaximumCaptureDuration", "15-second test")
    require(tests, "discardedIds", "opaque-id discard test")
    require(tests, "find.textContaining('opaque-internal-1'), findsNothing", "id redaction test")
    require(tests, "safe evidence map contains only the accepted allowlist", "allowlist test")
    require(tests, "_OperatorFakeCaptureEngine", "fake capture engine")
    require(tests, "FakeMicrophonePermissionGateway", "fake permission gateway")
    forbid(
        tests,
        "PermissionHandlerMicrophonePermissionGateway",
        "production permission execution in tests",
    )
    forbid(
        tests,
        "RecordMicrophoneCaptureEngine.mobile",
        "production recorder execution in tests",
    )


def validate_docs() -> None:
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readiness = read("docs/v300_rt2ec_operator_capture_harness_readiness.md")
    adapter = read("docs/v300_record_microphone_capture_adapter.md")
    contract = read("docs/v300_rt2ec_operator_capture_harness.md")

    for source, marker, label in (
        (readme, "RT-2e-c3 (**CURRENT / NOT_COMPLETED**)", "README current commit"),
        (roadmap, "RT-2e-c2 implementation: COMPLETED / ACCEPTED", "roadmap accepted state"),
        (tasklist, "implementation: COMPLETED / ACCEPTED", "tasklist state"),
        (checklist, "Implementation: COMPLETED / ACCEPTED", "checklist state"),
        (readiness, "RT-2e-c2 is COMPLETED / ACCEPTED", "readiness follow-up"),
        (adapter, "RT-2e-c2 is COMPLETED / ACCEPTED", "adapter follow-up"),
        (contract, "Status: COMPLETED / ACCEPTED", "contract status"),
        (scripts_readme, "v300_rt2ec_operator_capture_harness_status: completed-accepted", "expected gate"),
    ):
        require(source, marker, label)

    combined = "\n".join(
        (readme, roadmap, tasklist, scripts_readme, checklist, readiness, adapter, contract)
    )
    for marker in (
        "main_rt2ec_operator.dart",
        "DRC_RT2EC_OPERATOR=true",
        "in-app acknowledgement",
        "15 seconds",
        "discardPrivateArtifact",
        "safe evidence",
        "fake/widget tests",
        "authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only",
        "No real permission request",
        "No upload or STT",
    ):
        require(combined, marker, "operator implementation marker")


def main() -> None:
    validate_changed_surface()
    validate_default_app_unchanged()
    validate_operator_entrypoint()
    validate_operator_harness()
    validate_fake_widget_tests()
    validate_docs()

    print("v300_rt2ec_operator_capture_harness_status: completed-accepted")
    print("v300_rt2ec2_separate_entrypoint_added: True")
    print("v300_rt2ec2_compile_time_opt_in_added: True")
    print("v300_rt2ec2_acknowledgement_before_dependencies: True")
    print("v300_rt2ec2_explicit_permission_actions_added: True")
    print("v300_rt2ec2_bounded_capture_seconds: 15")
    print("v300_rt2ec2_private_artifact_auto_discard_added: True")
    print("v300_rt2ec2_safe_evidence_allowlist_added: True")
    print("v300_rt2ec2_fake_widget_tests_added: True")
    print("v300_rt2ec2_default_app_wiring_changed: False")
    print("v300_rt2ec2_dependency_changed: False")
    print("v300_rt2ec2_platform_files_changed: False")
    print("v300_rt2ec2_real_permission_request_executed: False")
    print("v300_rt2ec2_real_microphone_accessed: False")
    print("v300_rt2ec2_real_audio_captured: False")
    print("v300_rt2ec_parent_status: current-pending-rt2ec3-implementation")
    print("v300_rt2ec3_authorization: authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only")


if __name__ == "__main__":
    main()
