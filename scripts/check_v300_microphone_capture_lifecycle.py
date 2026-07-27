"""Validate RT-2d capture lifecycle contracts and fake engine only."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CAPTURE = ROOT / "app/lib/services/microphone_capture.dart"
FOCUSED_TEST = ROOT / "app/test/microphone_capture_test.dart"
PERMISSION = ROOT / "app/lib/services/microphone_permission.dart"
PLATFORM_GATEWAY = (
    ROOT
    / "app/lib/services/permission_handler_microphone_permission_gateway.dart"
)
HOME_SCREEN = ROOT / "app/lib/screens/home_screen.dart"
MAIN_DART = ROOT / "app/lib/main.dart"
PUBSPEC = ROOT / "app/pubspec.yaml"
ANDROID_MANIFEST = ROOT / "app/android/app/src/main/AndroidManifest.xml"
IOS_INFO = ROOT / "app/ios/Runner/Info.plist"

ACCEPTANCE_SYNC_DOC_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_capture_lifecycle.md",
    "scripts/check_v300_microphone_capture_lifecycle.py",
}

IMPLEMENTATION_PATHS = {
    "app/lib/services/microphone_capture.dart",
    "app/test/microphone_capture_test.dart",
}

ACCEPTED_WORKTREE_PATH_SETS = (
    ACCEPTANCE_SYNC_DOC_PATHS,
    ACCEPTANCE_SYNC_DOC_PATHS | IMPLEMENTATION_PATHS,
)

PLANNING_PATHS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_capture_lifecycle.md",
)


def require(source: str, marker: str, label: str) -> None:
    if marker not in source:
        raise AssertionError(f"missing {label}: {marker}")


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise AssertionError(f"RT-2d git check failed: {detail}")
    return result.stdout


def changed_paths() -> set[str]:
    paths: set[str] = set()
    output = run_git("status", "--porcelain=v1", "--untracked-files=all")
    for raw_line in output.splitlines():
        if not raw_line:
            continue
        path = raw_line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def validate_changed_surface() -> None:
    changed = changed_paths()
    if not changed:
        return

    if any(changed == expected for expected in ACCEPTED_WORKTREE_PATH_SETS):
        return

    all_allowed = ACCEPTANCE_SYNC_DOC_PATHS | IMPLEMENTATION_PATHS
    unexpected = sorted(changed - all_allowed)
    missing_doc_paths = sorted(ACCEPTANCE_SYNC_DOC_PATHS - changed)
    partial_implementation_paths = sorted(changed & IMPLEMENTATION_PATHS)

    details: list[str] = []
    if unexpected:
        details.append("unexpected changed paths:\n" + "\n".join(unexpected))
    if missing_doc_paths:
        details.append(
            "missing acceptance-sync document paths:\n"
            + "\n".join(missing_doc_paths)
        )
    if partial_implementation_paths and changed != all_allowed:
        details.append(
            "implementation paths must be either both present or both already committed:\n"
            + "\n".join(partial_implementation_paths)
        )
    details.append(
        "accepted worktree forms are: clean tree, 7-file acceptance sync, "
        "or 9-file implementation-plus-acceptance sync"
    )
    raise AssertionError(
        "RT-2d accepted-state surface mismatch:\n" + "\n".join(details)
    )

def validate_capture_contract() -> None:
    source = CAPTURE.read_text(encoding="utf-8")
    test_source = FOCUSED_TEST.read_text(encoding="utf-8")

    source_markers = (
        "enum MicrophoneCapturePhase",
        "checkingPermission",
        "permanentlyDenied",
        "timedOut",
        "enum MicrophoneCaptureOutcome",
        "busy",
        "noActiveCapture",
        "class MicrophoneCaptureRequest",
        "class MicrophoneCaptureEngineResult",
        "class MicrophoneCaptureResult",
        "class MicrophoneCaptureState",
        "abstract interface class MicrophoneCaptureEngine",
        "class FakeMicrophoneCaptureEngine",
        "abstract interface class MicrophoneCaptureDeadlineScheduler",
        "class MicrophoneCaptureController extends ChangeNotifier",
        "maximumAllowedDuration",
        "capture_duration_exceeds_limit",
        "capture_busy",
        "capture_timed_out",
        "capture_cancel_cleanup_failed",
        "_permissionGateway.checkPermission()",
        "'microphone_accessed': false",
        "'audio_captured': false",
        "'raw_audio_exposed': false",
    )
    for marker in source_markers:
        require(source, marker, "RT-2d capture contract marker")

    test_markers = (
        "granted permission starts only the fake engine",
        "permanently denied remains distinct",
        "a second start is busy",
        "duration must be positive",
        "stop returns only opaque fake completion data",
        "deadline produces a typed timeout",
        "start failure cleans a partially active fake engine",
        "stop failure attempts cancellation cleanup",
        "cancel cleanup failure stays typed and safe",
        "permission check exception is converted without raw details",
        "close cancels an active fake capture",
        "request and result metadata are immutable",
        "_FakeDeadlineScheduler",
        "FakeMicrophonePermissionGateway",
        "FakeMicrophoneCaptureEngine",
    )
    for marker in test_markers:
        require(test_source, marker, "RT-2d focused test marker")

    forbidden_source_markers = (
        "package:permission_handler/",
        "package:record/",
        "package:flutter_sound/",
        "package:sound_stream/",
        "package:mic_stream/",
        "dart:io",
        "Uint8List",
        "ByteData",
        "AudioRecorder(",
        "MediaRecorder(",
        "getUserMedia(",
        "startRecorder(",
        "startStream(",
        "openAudioSession(",
        "requestPermission()",
        "openAppSettings()",
        "http.post",
        "WebSocket",
        "SpeechToText",
    )
    for marker in forbidden_source_markers:
        if marker in source:
            raise AssertionError(f"RT-2d forbidden capture/runtime marker: {marker}")

    raw_exposure_markers = (
        "audioBytes",
        "rawAudio",
        "filePath",
        "localPath",
        "platformHandle",
    )
    for marker in raw_exposure_markers:
        if marker in source:
            raise AssertionError(f"RT-2d raw audio exposure is forbidden: {marker}")


def validate_existing_permission_boundary() -> None:
    permission = PERMISSION.read_text(encoding="utf-8")
    gateway = PLATFORM_GATEWAY.read_text(encoding="utf-8")
    require(
        permission,
        "abstract interface class MicrophonePermissionGateway",
        "accepted permission gateway",
    )
    require(
        permission,
        "class FakeMicrophonePermissionGateway",
        "accepted fake permission gateway",
    )
    require(
        gateway,
        "class PermissionHandlerMicrophonePermissionGateway",
        "accepted platform permission gateway",
    )


def validate_no_real_capture_dependency() -> None:
    pubspec = PUBSPEC.read_text(encoding="utf-8")
    forbidden_dependencies = (
        "\n  record:",
        "\n  flutter_sound:",
        "\n  sound_stream:",
        "\n  mic_stream:",
        "\n  audio_waveforms:",
    )
    for marker in forbidden_dependencies:
        if marker in pubspec:
            raise AssertionError(
                f"RT-2d real capture dependency is forbidden: {marker.strip()}"
            )


def validate_no_ui_or_platform_change() -> None:
    combined_ui = MAIN_DART.read_text(encoding="utf-8") + "\n" + HOME_SCREEN.read_text(
        encoding="utf-8"
    )
    forbidden_ui = (
        "microphone_capture.dart",
        "MicrophoneCaptureController",
        "FakeMicrophoneCaptureEngine",
        "MicrophoneCaptureRequest",
    )
    for marker in forbidden_ui:
        if marker in combined_ui:
            raise AssertionError(f"RT-2d UI/startup wiring is forbidden: {marker}")

    android = ANDROID_MANIFEST.read_text(encoding="utf-8")
    ios = IOS_INFO.read_text(encoding="utf-8")
    require(android, "android.permission.RECORD_AUDIO", "accepted Android permission")
    require(ios, "NSMicrophoneUsageDescription", "accepted iOS permission")


def validate_planning() -> None:
    combined_parts: list[str] = []
    for relative in PLANNING_PATHS:
        path = ROOT / relative
        if not path.exists():
            raise AssertionError(f"RT-2d planning file missing: {relative}")
        text = path.read_text(encoding="utf-8")
        require(text, "RT-2d", f"{relative} RT-2d marker")
        combined_parts.append(text)

    combined = "\n".join(combined_parts)
    markers = (
        "RT-2d COMPLETED / ACCEPTED",
        "capture lifecycle",
        "fake capture engine",
        "single active capture",
        "bounded duration",
        "no microphone access",
        "RT-2e CURRENT / NOT_COMPLETED",
        "NOT_STARTED",
        "authorized-explicit-opt-in-bounded-real-capture-adapter-only",
    )
    for marker in markers:
        require(combined, marker, "RT-2d planning marker")


def main() -> None:
    validate_changed_surface()
    validate_capture_contract()
    validate_existing_permission_boundary()
    validate_no_real_capture_dependency()
    validate_no_ui_or_platform_change()
    validate_planning()

    print("v300_microphone_capture_lifecycle_status: completed-accepted")
    print("v300_rt2d_capture_contract_added: True")
    print("v300_rt2d_controller_added: True")
    print("v300_rt2d_fake_engine_added: True")
    print("v300_rt2d_single_active_capture_enforced: True")
    print("v300_rt2d_bounded_duration_enforced: True")
    print("v300_rt2d_permission_request_executed: False")
    print("v300_rt2d_real_capture_dependency_added: False")
    print("v300_rt2d_ui_changed: False")
    print("v300_rt2d_backend_changed: False")
    print("v300_rt2d_microphone_accessed: False")
    print("v300_rt2d_audio_captured: False")
    print("v300_rt2d_raw_audio_exposed: False")
    print("v300_rt2_parent_status: current-pending-rt2e-implementation")
    print("v300_rt2e_authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only")


if __name__ == "__main__":
    main()
