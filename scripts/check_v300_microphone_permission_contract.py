"""Validate RT-2b app-owned microphone permission contract and fake gateway."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_PATHS = (
    "backend",
    "app/android",
    "app/ios",
    "release_notes",
    "app/pubspec.yaml",
    "app/lib/main.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/models/voice_input_demo.dart",
    "app/lib/services/backend_api_client.dart",
)

PLANNING_FILES = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_permission_contract.md",
)

SERVICE_PATH = ROOT / "app/lib/services/microphone_permission.dart"
TEST_PATH = ROOT / "app/test/microphone_permission_test.dart"


def changed_protected_paths() -> list[str]:
    """Return tracked or untracked protected paths changed from HEAD.

    Git status is used instead of hashing the whole filesystem so ignored local
    artifacts such as caches, private environment files, and generated outputs do
    not make the gate platform- or machine-dependent.
    """

    command = [
        "git",
        "-C",
        str(ROOT),
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        *PROTECTED_PATHS,
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise AssertionError(f"RT-2b git protected-surface check failed: {detail}")
    return [line for line in completed.stdout.splitlines() if line.strip()]


def require(source: str, marker: str, label: str) -> None:
    if marker not in source:
        raise AssertionError(f"missing {label}: {marker}")


def validate_protected_surfaces() -> None:
    changed = changed_protected_paths()
    if changed:
        raise AssertionError(
            "RT-2b protected surface changed:\n" + "\n".join(changed)
        )


def validate_contract_source() -> None:
    if not SERVICE_PATH.is_file():
        raise AssertionError("RT-2b service file missing")
    if not TEST_PATH.is_file():
        raise AssertionError("RT-2b focused test file missing")

    service = SERVICE_PATH.read_text(encoding="utf-8")
    test_source = TEST_PATH.read_text(encoding="utf-8")

    for marker in (
        "enum MicrophonePermissionStatus",
        "unknown,",
        "granted,",
        "denied,",
        "permanentlyDenied,",
        "restricted,",
        "unsupported,",
        "failed,",
        "enum MicrophonePermissionOperation",
        "class MicrophonePermissionResult",
        "abstract interface class MicrophonePermissionGateway",
        "class FakeMicrophonePermissionGateway",
        "Future<MicrophonePermissionResult> checkPermission()",
        "Future<MicrophonePermissionResult> requestPermission()",
        "Future<MicrophonePermissionResult> openAppSettings()",
        "'platform_permission_requested': false",
        "'settings_opened': false",
    ):
        require(service, marker, "RT-2b contract marker")

    for marker in (
        "MicrophonePermissionResult",
        "FakeMicrophonePermissionGateway",
        "request sequence is deterministic",
        "open settings is recorded but not executed",
        "platform_permission_requested",
    ):
        require(test_source, marker, "RT-2b focused test marker")

    forbidden = (
        "package:permission_handler",
        "package:record",
        "package:flutter_sound",
        "package:mic_stream",
        "dart:io",
        "MethodChannel",
        "EventChannel",
        "getUserMedia",
        "mediaDevices",
        "AudioRecorder",
        "RecordConfig",
        "framework/",
        "package:framework",
    )
    combined = service + "\n" + test_source
    for marker in forbidden:
        if marker in combined:
            raise AssertionError(f"RT-2b forbidden runtime marker: {marker}")


def validate_planning_state() -> None:
    combined_parts: list[str] = []
    for relative in PLANNING_FILES:
        source = (ROOT / relative).read_text(encoding="utf-8")
        combined_parts.append(source)
        require(source, "RT-2b", f"{relative} RT-2b marker")
        require(source, "COMPLETED / ACCEPTED", f"{relative} acceptance state")

    combined = "\n".join(combined_parts)
    for marker in (
        "RT-2c",
        "CURRENT / NOT_COMPLETED",
        "NOT_STARTED",
        "permission contract",
        "fake gateway",
        "microphone access",
        "audio capture",
        "provider",
        "STT",
    ):
        require(combined, marker, "RT-2b planning marker")


def main() -> None:
    validate_protected_surfaces()
    validate_contract_source()
    validate_planning_state()

    print("v300_microphone_permission_contract_status: completed-accepted")
    print("v300_rt2b_flutter_contract_added: True")
    print("v300_rt2b_focused_tests_added: True")
    print("v300_rt2b_dependency_added: False")
    print("v300_rt2b_platform_permission_added: False")
    print("v300_rt2b_method_channel_added: False")
    print("v300_rt2b_ui_changed: False")
    print("v300_rt2b_backend_changed: False")
    print("v300_rt2b_microphone_accessed: False")
    print("v300_rt2b_audio_captured: False")
    print("v300_rt2_parent_status: current-pending-rt2c-implementation")
    print("v300_rt2c_authorization: authorized-platform-permission-wiring-without-capture-only")


if __name__ == "__main__":
    main()
