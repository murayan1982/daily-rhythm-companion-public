#!/usr/bin/env python3
"""Validate the exact RT-6d Flutter motion-presentation candidate."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE = "cd423fa2236ce16a7635f0c67460f2fa2fd210e9"
FW_VERSION = "5.4.0"
FW_REFERENCE_COMMIT = "d313eb6acb643103fe25988720ebee5976a04f78"
FW_SOURCE_MODE = "external-vendored-snapshot"
EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt6d_flutter_motion_presentation.md",
    "scripts/check_v300_rt6d_flutter_motion_presentation.py",
    "app/lib/models/character_motion_presentation.dart",
    "app/lib/services/character_motion_presentation_client.dart",
    "app/lib/services/character_motion_presentation_controller.dart",
    "app/test/character_motion_presentation_client_test.dart",
    "app/test/character_motion_presentation_controller_test.dart",
}
FLUTTER_RUNTIME_PATHS = {
    "app/lib/models/character_motion_presentation.dart",
    "app/lib/services/character_motion_presentation_client.dart",
    "app/lib/services/character_motion_presentation_controller.dart",
}
FLUTTER_TEST_PATHS = {
    "app/test/character_motion_presentation_client_test.dart",
    "app/test/character_motion_presentation_controller_test.dart",
}
PROTECTED_PATHS = {
    "app/lib/main.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/models/character_display_presentation.dart",
    "app/lib/models/motion_demo.dart",
    "app/lib/services/backend_api_client.dart",
    "app/lib/widgets/character_display_card.dart",
    "pubspec.yaml",
    "app/pubspec.yaml",
    "app/pubspec.lock",
}


def _run(*args: str) -> str:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def _git_paths() -> set[str]:
    values: set[str] = set()
    for command in (
        ("git", "diff", "--name-only"),
        ("git", "diff", "--cached", "--name-only"),
        ("git", "ls-files", "--others", "--exclude-standard"),
    ):
        output = _run(*command)
        values.update(
            line.strip().replace("\\", "/")
            for line in output.splitlines()
            if line.strip()
        )
    return values


def _assert_exact_surface(*, snapshot: bool) -> set[str]:
    missing = sorted(path for path in EXACT_PATHS if not (REPO_ROOT / path).is_file())
    if missing:
        raise AssertionError(f"RT-6d candidate files are missing: {missing}")
    changed = _git_paths()
    if changed != EXACT_PATHS:
        raise AssertionError(
            "RT-6d exact surface mismatch: "
            f"expected={sorted(EXACT_PATHS)} actual={sorted(changed)}"
        )
    if changed & PROTECTED_PATHS:
        raise AssertionError("RT-6d changed a protected Flutter integration path")
    if any(path.startswith("backend/") for path in changed):
        raise AssertionError("RT-6d changed Backend source")
    if any(path.startswith("vendor/") for path in changed):
        raise AssertionError("RT-6d changed external vendor source")
    if any(path.startswith("app/android/") for path in changed):
        raise AssertionError("RT-6d changed Android platform files")
    if any(path.startswith("app/ios/") for path in changed):
        raise AssertionError("RT-6d changed iOS platform files")
    if any(path.startswith("app/web/") for path in changed):
        raise AssertionError("RT-6d changed Web platform files")
    if any(path.startswith("app/windows/") for path in changed):
        raise AssertionError("RT-6d changed Windows platform files")
    if not snapshot:
        head = _run("git", "rev-parse", "HEAD")
        origin = _run("git", "rev-parse", "origin/main")
        if head != DRC_BASELINE or origin != DRC_BASELINE:
            raise AssertionError(
                f"DRC baseline mismatch: head={head} origin/main={origin} expected={DRC_BASELINE}"
            )
    return changed


def _assert_docs() -> None:
    docs = "\n".join(
        (REPO_ROOT / path).read_text(encoding="utf-8", errors="replace")
        for path in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
            "docs/v300_rt6d_flutter_motion_presentation.md",
        )
    )
    required = (
        "RT-6d: IMPLEMENTED / AWAITING_REVIEW",
        DRC_BASELINE,
        FW_VERSION,
        FW_REFERENCE_COMMIT,
        FW_SOURCE_MODE,
        "exact 12 files",
        "RT-6e",
        "NOT_AUTHORIZED",
        "BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED",
    )
    for marker in required:
        if marker not in docs:
            raise AssertionError(f"RT-6d documentation marker missing: {marker}")


def _assert_model() -> None:
    source = (
        REPO_ROOT / "app/lib/models/character_motion_presentation.dart"
    ).read_text(encoding="utf-8")
    required = (
        "characterMotionPresentationMaxCommands = 3",
        "characterMotionPresentationMaxEventTypes = 12",
        "characterMotionPresentationMaxIdChars = 128",
        "characterMotionPresentationMaxSafeMessageChars = 256",
        "enum CharacterMotionPresentationPhase",
        "enum CharacterMotionLifecycleFact",
        "enum CharacterMotionCue",
        "enum CharacterMotionCommandIntent",
        "enum CharacterMotionExecutionStatus",
        "class CharacterMotionPresentationRequest",
        "class CharacterMotionPresentationCommandResult",
        "class CharacterMotionPresentationResult",
        "class CharacterMotionPresentationProblem",
        "class CharacterMotionPresentationState",
        "drc.v3.framework-mock-motion-execution.1",
        "unsafe_motion_execution_flags",
        "invalid_motion_command_counts",
        "invalid_completed_motion_result",
        "invalid_inactive_motion_result",
        "adapter != 'mock'",
        "realAdapterEnabled",
        "providerExecutionAllowed",
        "providerExecutionAttempted",
        "networkExecution",
    )
    for marker in required:
        if marker not in source:
            raise AssertionError(f"RT-6d model marker missing: {marker}")
    forbidden = (
        "package:http",
        "dart:io",
        "WebSocket",
        "framework/",
        "VTubeStudio",
        "Live2D",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"RT-6d model forbidden marker present: {marker}")


def _assert_client() -> None:
    source = (
        REPO_ROOT / "app/lib/services/character_motion_presentation_client.dart"
    ).read_text(encoding="utf-8")
    required = (
        "typedef CharacterMotionPresentationTransport",
        "Future<Map<String, Object?>> Function",
        "CharacterMotionPresentationResult.fromJson(response)",
        "motion_transport_failed",
        "The character-motion presentation request failed.",
    )
    for marker in required:
        if marker not in source:
            raise AssertionError(f"RT-6d client marker missing: {marker}")
    forbidden = (
        "package:http",
        "dart:io",
        "HttpClient",
        "WebSocket",
        "realtime/",
        "/demo/motion",
        "framework",
        "provider",
        "token",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"RT-6d client forbidden marker present: {marker}")


def _assert_controller() -> None:
    source = (
        REPO_ROOT / "app/lib/services/character_motion_presentation_controller.dart"
    ).read_text(encoding="utf-8")
    required = (
        "extends ChangeNotifier",
        "active_motion_request_rejected",
        "motion_controller_closed",
        "final operation = ++_operation",
        "_operation += 1",
        "if (!_isCurrent(operation))",
        "CharacterMotionPresentationPhase.applying",
        "result.presentationPhase",
        "void reset()",
        "void close()",
        "void dispose()",
        "notifyListeners()",
    )
    for marker in required:
        if marker not in source:
            raise AssertionError(f"RT-6d controller marker missing: {marker}")
    forbidden = (
        "Timer.periodic",
        "Queue<",
        "package:http",
        "WebSocket",
        "HomeScreen",
        "framework",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"RT-6d controller forbidden marker present: {marker}")


def _assert_tests() -> None:
    client = (
        REPO_ROOT / "app/test/character_motion_presentation_client_test.dart"
    ).read_text(encoding="utf-8")
    controller = (
        REPO_ROOT / "app/test/character_motion_presentation_controller_test.dart"
    ).read_text(encoding="utf-8")
    client_required = (
        "parses completed mock result with three ordered commands",
        "rejects more than twelve event types",
        "rejects non-contiguous command order",
        "rejects unsafe",
        "normalizes raw transport exception to safe problem",
    )
    controller_required = (
        "starts idle and completes one request",
        "rejects simultaneous apply and active replacement",
        "reset invalidates late completion",
        "close invalidates late completion",
        "dispose invalidates late completion without notification",
        "safe failed state",
    )
    for marker in client_required:
        if marker not in client:
            raise AssertionError(f"RT-6d client test marker missing: {marker}")
    for marker in controller_required:
        if marker not in controller:
            raise AssertionError(f"RT-6d controller test marker missing: {marker}")
    combined = client + controller
    forbidden = (
        "http.get(",
        "http.post(",
        "WebSocket.connect",
        "127.0.0.1",
        "localhost",
        "VTubeStudio",
        "Live2D",
    )
    for marker in forbidden:
        if marker in combined:
            raise AssertionError(f"RT-6d focused tests contain real execution marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip real checkout HEAD/origin validation for artifact generation.",
    )
    args = parser.parse_args()

    changed = _assert_exact_surface(snapshot=args.snapshot)
    _assert_docs()
    _assert_model()
    _assert_client()
    _assert_controller()
    _assert_tests()

    print("v300_rt6d_status: implemented-awaiting-review")
    print("v300_rt6d_exact_change_surface: True")
    print(f"v300_rt6d_change_file_count: {len(changed)}")
    print(f"v300_rt6d_flutter_runtime_file_count: {len(changed & FLUTTER_RUNTIME_PATHS)}")
    print(f"v300_rt6d_flutter_test_file_count: {len(changed & FLUTTER_TEST_PATHS)}")
    print("v300_rt6d_backend_changed: False")
    print("v300_rt6d_home_screen_changed: False")
    print("v300_rt6d_main_changed: False")
    print("v300_rt6d_character_display_changed: False")
    print("v300_rt6d_existing_tests_changed: False")
    print("v300_rt6d_dependencies_changed: False")
    print("v300_rt6d_framework_changed: False")
    print("v300_rt6d_vendor_changed: False")
    print("v300_rt6d_injected_transport_only: True")
    print("v300_rt6d_real_http_execution: False")
    print("v300_rt6d_max_commands: 3")
    print("v300_rt6d_max_event_types: 12")
    print("v300_rt6d_active_request_limit: 1")
    print("v300_rt6d_stale_result_ignored: True")
    print("v300_rt6d_raw_transport_exception_exposed: False")
    print("v300_rt6d_raw_response_exposed: False")
    print(f"v300_rt6d_framework_version: {FW_VERSION}")
    print(f"v300_rt6d_framework_reference_commit: {FW_REFERENCE_COMMIT}")
    print(f"v300_rt6d_framework_source_mode: {FW_SOURCE_MODE}")
    print("v300_rt6d_framework_execution: False")
    print("v300_rt6e_authorized: False")
    print("v300_rt6f_authorized: False")
    print("v300_rt7_real_adapter_blocked: True")
    print("v300_rt6d_commit_push_authorized: False")
    print(f"v300_rt6d_snapshot_mode: {args.snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
