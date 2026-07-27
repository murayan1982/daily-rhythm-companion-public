"""Validate RT-2c mobile microphone permission wiring without audio capture."""

from __future__ import annotations

import plistlib
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PUBSPEC = ROOT / "app/pubspec.yaml"
LOCKFILE = ROOT / "app/pubspec.lock"
ANDROID_MANIFEST = ROOT / "app/android/app/src/main/AndroidManifest.xml"
IOS_INFO = ROOT / "app/ios/Runner/Info.plist"
GATEWAY = (
    ROOT
    / "app/lib/services/permission_handler_microphone_permission_gateway.dart"
)
FOCUSED_TEST = (
    ROOT / "app/test/permission_handler_microphone_permission_gateway_test.dart"
)
HOME_SCREEN = ROOT / "app/lib/screens/home_screen.dart"
MAIN_DART = ROOT / "app/lib/main.dart"
WINDOWS_REGISTRANT = (
    ROOT / "app/windows/flutter/generated_plugin_registrant.cc"
)
WINDOWS_PLUGINS_CMAKE = (
    ROOT / "app/windows/flutter/generated_plugins.cmake"
)

ALLOWED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_permission_contract.md",
    "docs/v300_microphone_platform_permission_wiring.md",
    "scripts/check_v300_microphone_platform_permission_wiring.py",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "app/android/app/src/main/AndroidManifest.xml",
    "app/ios/Runner/Info.plist",
    "app/windows/flutter/generated_plugin_registrant.cc",
    "app/windows/flutter/generated_plugins.cmake",
    "app/lib/services/permission_handler_microphone_permission_gateway.dart",
    "app/test/permission_handler_microphone_permission_gateway_test.dart",
}

PLANNING_PATHS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_platform_permission_wiring.md",
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
        raise AssertionError(f"RT-2c git check failed: {detail}")
    return result.stdout


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for raw_line in run_git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if not raw_line:
            continue
        path = raw_line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def validate_changed_surface() -> None:
    changed = changed_paths()
    unexpected = sorted(changed - ALLOWED_CHANGED_PATHS)
    if unexpected:
        raise AssertionError(
            "RT-2c unexpected changed paths:\n" + "\n".join(unexpected)
        )

    required = {
        "app/pubspec.yaml",
        "app/pubspec.lock",
        "app/android/app/src/main/AndroidManifest.xml",
        "app/ios/Runner/Info.plist",
        "app/windows/flutter/generated_plugin_registrant.cc",
        "app/windows/flutter/generated_plugins.cmake",
        "app/lib/services/permission_handler_microphone_permission_gateway.dart",
        "app/test/permission_handler_microphone_permission_gateway_test.dart",
        "docs/v300_microphone_platform_permission_wiring.md",
        "scripts/check_v300_microphone_platform_permission_wiring.py",
    }
    missing = sorted(required - changed)
    if missing:
        raise AssertionError(
            "RT-2c expected changed paths are missing; run flutter pub get first:\n"
            + "\n".join(missing)
        )


def validate_dependency_and_lock() -> None:
    pubspec = PUBSPEC.read_text(encoding="utf-8")
    lockfile = LOCKFILE.read_text(encoding="utf-8")

    require(pubspec, "  permission_handler: 12.0.3", "pinned permission dependency")
    section_match = re.search(
        r"(?ms)^  permission_handler:\n.*?(?=^  [A-Za-z0-9_]+:\n|\Z)",
        lockfile,
    )
    if section_match is None:
        raise AssertionError("missing permission lock entry")
    section = section_match.group(0)
    require(section, '    dependency: "direct main"', "direct-main lock marker")
    require(section, '    version: "12.0.3"', "resolved permission version")

    capture_dependencies = (
        "\n  record:",
        "\n  flutter_sound:",
        "\n  sound_stream:",
        "\n  mic_stream:",
        "\n  audio_waveforms:",
    )
    for marker in capture_dependencies:
        if marker in pubspec:
            raise AssertionError(f"RT-2c capture dependency is forbidden: {marker.strip()}")


def validate_android_declaration() -> None:
    tree = ET.parse(ANDROID_MANIFEST)
    root = tree.getroot()
    android_name = "{http://schemas.android.com/apk/res/android}name"
    permissions = [
        element.attrib.get(android_name)
        for element in root.findall("uses-permission")
    ]
    if permissions.count("android.permission.RECORD_AUDIO") != 1:
        raise AssertionError(
            "RT-2c requires exactly one Android RECORD_AUDIO declaration"
        )


def validate_ios_declaration() -> None:
    with IOS_INFO.open("rb") as stream:
        info = plistlib.load(stream)
    expected = (
        "音声入力ボタンを操作したときに、話した内容を入力するため"
        "マイクを使用します。"
    )
    if info.get("NSMicrophoneUsageDescription") != expected:
        raise AssertionError("RT-2c iOS microphone usage description mismatch")
    if "NSSpeechRecognitionUsageDescription" in info:
        raise AssertionError("RT-2c must not declare Apple Speech recognition")


def validate_windows_generated_registration() -> None:
    registrant = WINDOWS_REGISTRANT.read_text(encoding="utf-8")
    plugins_cmake = WINDOWS_PLUGINS_CMAKE.read_text(encoding="utf-8")

    include_marker = (
        "#include <permission_handler_windows/"
        "permission_handler_windows_plugin.h>"
    )
    registration_marker = "PermissionHandlerWindowsPluginRegisterWithRegistrar("
    registrar_name_marker = (
        'registry->GetRegistrarForPlugin("PermissionHandlerWindowsPlugin")'
    )
    cmake_marker = "  permission_handler_windows\n"

    for source, marker, label in (
        (registrant, include_marker, "Windows permission plugin include"),
        (registrant, registration_marker, "Windows permission plugin registration"),
        (registrant, registrar_name_marker, "Windows permission plugin registrar name"),
        (plugins_cmake, cmake_marker, "Windows permission plugin CMake entry"),
    ):
        require(source, marker, label)
        if source.count(marker) != 1:
            raise AssertionError(f"RT-2c duplicate {label}: {marker}")


def validate_gateway() -> None:
    source = GATEWAY.read_text(encoding="utf-8")
    test_source = FOCUSED_TEST.read_text(encoding="utf-8")

    gateway_markers = (
        "abstract interface class PermissionHandlerMicrophoneDriver",
        "class DefaultPermissionHandlerMicrophoneDriver",
        "class PermissionHandlerMicrophonePermissionGateway",
        "implements MicrophonePermissionGateway",
        "handler.Permission.microphone.status",
        "handler.Permission.microphone.request()",
        "handler.openAppSettings()",
        "TargetPlatform.android",
        "TargetPlatform.iOS",
        "MissingPluginException",
        "permission_handler_unexpected_",
        "'microphone_accessed': false",
        "'audio_captured': false",
    )
    for marker in gateway_markers:
        require(source, marker, "RT-2c gateway marker")

    test_markers = (
        "PermissionHandlerMicrophonePermissionGateway",
        "_FakePermissionHandlerDriver",
        "PermissionStatus.granted",
        "PermissionStatus.permanentlyDenied",
        "PermissionStatus.limited",
        "PermissionStatus.provisional",
        "MissingPluginException",
        "TargetPlatform.windows",
        "settings launch failure",
    )
    for marker in test_markers:
        require(test_source, marker, "RT-2c focused test marker")

    forbidden_runtime_markers = (
        "package:record/",
        "package:flutter_sound/",
        "package:sound_stream/",
        "package:mic_stream/",
        "MediaRecorder(",
        "getUserMedia(",
        "AudioRecorder(",
        "RecorderController(",
        ".startRecorder(",
        ".startStream(",
        ".openAudioSession(",
    )
    combined = source + "\n" + test_source
    for marker in forbidden_runtime_markers:
        if marker in combined:
            raise AssertionError(f"RT-2c capture runtime marker is forbidden: {marker}")


def validate_no_ui_wiring() -> None:
    combined = MAIN_DART.read_text(encoding="utf-8") + "\n" + HOME_SCREEN.read_text(
        encoding="utf-8"
    )
    forbidden = (
        "permission_handler_microphone_permission_gateway.dart",
        "PermissionHandlerMicrophonePermissionGateway",
        "Permission.microphone",
        "requestPermission()",
    )
    for marker in forbidden:
        if marker in combined:
            raise AssertionError(f"RT-2c UI/startup wiring is forbidden: {marker}")


def validate_planning() -> None:
    combined_parts: list[str] = []
    for relative in PLANNING_PATHS:
        path = ROOT / relative
        if not path.exists():
            raise AssertionError(f"RT-2c planning file missing: {relative}")
        text = path.read_text(encoding="utf-8")
        require(text, "RT-2c", f"{relative} RT-2c marker")
        combined_parts.append(text)

    combined = "\n".join(combined_parts)
    planning_markers = (
        "IMPLEMENTED / NOT_ACCEPTED",
        "permission_handler",
        "RECORD_AUDIO",
        "NSMicrophoneUsageDescription",
        "explicit user action",
        "no capture",
        "RT-2d",
        "blocked-pending-rt2c-acceptance",
    )
    for marker in planning_markers:
        require(combined, marker, "RT-2c planning marker")


def main() -> None:
    validate_changed_surface()
    validate_dependency_and_lock()
    validate_android_declaration()
    validate_ios_declaration()
    validate_windows_generated_registration()
    validate_gateway()
    validate_no_ui_wiring()
    validate_planning()

    print("v300_microphone_platform_permission_wiring_status: implemented-not-accepted")
    print("v300_rt2c_permission_dependency_added: True")
    print("v300_rt2c_lock_resolved: True")
    print("v300_rt2c_gateway_added: True")
    print("v300_rt2c_android_record_audio_added: True")
    print("v300_rt2c_ios_microphone_usage_added: True")
    print("v300_rt2c_windows_generated_registration_added: True")
    print("v300_rt2c_ui_changed: False")
    print("v300_rt2c_backend_changed: False")
    print("v300_rt2c_permission_request_executed: False")
    print("v300_rt2c_microphone_accessed: False")
    print("v300_rt2c_audio_captured: False")
    print("v300_rt2_parent_status: current-pending-rt2c-acceptance")
    print("v300_rt2d_authorization: blocked-pending-rt2c-acceptance")


if __name__ == "__main__":
    main()
