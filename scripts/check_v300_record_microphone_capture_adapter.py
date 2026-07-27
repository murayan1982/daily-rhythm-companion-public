"""Validate accepted RT-2e-b record adapter without real execution."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_IMPLEMENTATION_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_real_capture_adapter_readiness.md",
    "docs/v300_record_microphone_capture_adapter.md",
    "scripts/check_v300_record_microphone_capture_adapter.py",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "app/lib/services/microphone_capture.dart",
    "app/lib/services/record_microphone_capture_engine.dart",
    "app/test/microphone_capture_test.dart",
    "app/test/record_microphone_capture_engine_test.dart",
}

ACCEPTANCE_SYNC_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_real_capture_adapter_readiness.md",
    "docs/v300_record_microphone_capture_adapter.md",
    "scripts/check_v300_record_microphone_capture_adapter.py",
}


OPTIONAL_GENERATED_PLUGIN_PATHS = {
    "app/android/app/src/main/java/io/flutter/plugins/GeneratedPluginRegistrant.java",
    "app/ios/Runner/GeneratedPluginRegistrant.m",
    "app/linux/flutter/generated_plugin_registrant.cc",
    "app/linux/flutter/generated_plugins.cmake",
    "app/macos/Flutter/GeneratedPluginRegistrant.swift",
    "app/windows/flutter/generated_plugin_registrant.cc",
    "app/windows/flutter/generated_plugins.cmake",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"RT-2e-b missing {label}: {marker}")


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
        raise AssertionError(f"RT-2e-b git check failed: {detail}")
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


def validate_changed_surface() -> set[str]:
    actual = changed_paths()
    if not actual or actual == ACCEPTANCE_SYNC_PATHS:
        return actual

    allowed = REQUIRED_IMPLEMENTATION_PATHS | OPTIONAL_GENERATED_PLUGIN_PATHS
    unexpected = sorted(actual - allowed)
    missing = sorted(REQUIRED_IMPLEMENTATION_PATHS - actual)
    if unexpected or missing:
        details: list[str] = []
        if unexpected:
            details.append("unexpected changed paths:\n" + "\n".join(unexpected))
        if missing:
            details.append(
                "missing implementation/acceptance paths; run flutter pub get before the gate:\n"
                + "\n".join(missing)
            )
        details.append(
            "accepted worktree forms are: clean tree, exact eight-file acceptance "
            "sync, or full implementation plus optional generated plugin files"
        )
        raise AssertionError(
            "RT-2e-b accepted-state surface mismatch:\n" + "\n".join(details)
        )
    return actual


def lock_package_block(lock: str, package: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(package)}:\n(.*?)(?=^  [a-zA-Z0-9_]+:|\Z)",
        lock,
    )
    if match is None:
        raise AssertionError(f"RT-2e-b lockfile missing package: {package}")
    return match.group(1)


def validate_dependencies() -> None:
    pubspec = read("app/pubspec.yaml")
    lock = read("app/pubspec.lock")

    require(pubspec, "  path_provider: 2.1.6", "direct path_provider pin")
    require(pubspec, "  record: 6.2.1", "direct record pin")
    if re.search(r"^\s{2}record:\s*[\^><~]", pubspec, re.MULTILINE):
        raise AssertionError("RT-2e-b record dependency must be exactly pinned")

    record_block = lock_package_block(lock, "record")
    path_provider_block = lock_package_block(lock, "path_provider")
    for block, package, version in (
        (record_block, "record", "6.2.1"),
        (path_provider_block, "path_provider", "2.1.6"),
    ):
        require(block, 'dependency: "direct main"', f"{package} direct lock entry")
        require(block, f'version: "{version}"', f"{package} locked version")


def validate_adapter() -> None:
    adapter = read("app/lib/services/record_microphone_capture_engine.dart")
    capture = read("app/lib/services/microphone_capture.dart")
    adapter_tests = read("app/test/record_microphone_capture_engine_test.dart")
    capture_tests = read("app/test/microphone_capture_test.dart")

    for marker in (
        "package:path_provider/path_provider.dart",
        "package:record/record.dart",
        "RecordMicrophoneCaptureDriver",
        "RecordPackageMicrophoneCaptureDriver",
        "RecordMicrophoneCapturePrivateFileSystem",
        "PathProviderRecordMicrophoneCapturePrivateFileSystem",
        "RecordMicrophoneCapturePrivateArtifactAccess",
        "RecordMicrophoneCaptureEngine",
        "AudioRecorder()",
        "AudioEncoder.wav",
        "sampleRate: request.sampleRate",
        "numChannels: request.numChannels",
        "record_capture_start_failed",
        "record_capture_stop_failed",
        "record_capture_artifact_missing",
        "record_capture_artifact_path_mismatch",
        "record_capture_cancel_failed",
        "private_artifact_registered",
        "raw_audio_exposed': false",
    ):
        require(adapter, marker, "adapter contract marker")

    for forbidden in (
        ".hasPermission(",
        ".startStream(",
        "Uint8List",
        "BackendApiClient",
        "create_voice_input_session",
    ):
        if forbidden in adapter:
            raise AssertionError(f"RT-2e-b forbidden adapter marker: {forbidden}")

    for marker in (
        "_safePublicEngineResult(engineResult)",
        "safeEngineResult.publicMetadata['microphone_accessed'] == true",
        "safeEngineResult.publicMetadata['audio_captured'] == true",
        "safeEngineResult.publicMetadata['raw_audio_exposed'] == true",
        "safeEngineResult.publicMetadata['private_artifact_registered'] == true",
        "publicMetadata['microphone_accessed'] == true",
        "publicMetadata['audio_captured'] == true",
        "publicMetadata['raw_audio_exposed'] == true",
    ):
        require(capture, marker, "safe controller metadata propagation")

    if adapter_tests.count("    test(") < 15:
        raise AssertionError("RT-2e-b focused adapter test count is below 15")
    for marker in (
        "_FakeRecordDriver",
        "_FakePrivateFileSystem",
        "record_capture_start_failed",
        "record_capture_stop_failed",
        "record_capture_artifact_missing",
        "record_capture_artifact_path_mismatch",
        "record_capture_opaque_id_failed",
        "resolvePrivateArtifactPath",
        "discardPrivateArtifact",
        "isNot(contains(fixture.paths.firstPath))",
    ):
        require(adapter_tests, marker, "fake-only adapter test marker")

    for forbidden in (
        "RecordPackageMicrophoneCaptureDriver(",
        "RecordMicrophoneCaptureEngine.mobile(",
        "flutter run",
        "integration_test",
    ):
        if forbidden in adapter_tests:
            raise AssertionError(f"RT-2e-b test executes real boundary: {forbidden}")

    require(
        capture_tests,
        "stop propagates only safe engine capture metadata",
        "controller metadata focused test",
    )
    require(
        capture_tests,
        "result.engineResult!.publicMetadata",
        "sanitized engine-result metadata assertion",
    )
    require(
        capture_tests,
        "isNot(contains('private_path'))",
        "private path non-propagation assertion",
    )


def validate_generated_plugins(actual: set[str]) -> None:
    for relative in sorted(actual & OPTIONAL_GENERATED_PLUGIN_PATHS):
        content = read(relative).lower()
        if "record" not in content:
            raise AssertionError(
                f"RT-2e-b changed generated file lacks record registration: {relative}"
            )


def validate_docs() -> None:
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readiness = read("docs/v300_microphone_real_capture_adapter_readiness.md")
    contract = read("docs/v300_record_microphone_capture_adapter.md")

    for source, marker, label in (
        (readme, "Current small commit: RT-2e-c (**CURRENT / NOT_COMPLETED**)", "README current commit"),
        (roadmap, "Current small commit: RT-2e-c CURRENT / NOT_COMPLETED", "roadmap current commit"),
        (tasklist, "current small commit: RT-2e-c CURRENT / NOT_COMPLETED", "tasklist current commit"),
        (checklist, "Current small commit: RT-2e-c CURRENT / NOT_COMPLETED", "checklist current commit"),
        (readiness, "Completed small commit: RT-2e-b COMPLETED / ACCEPTED", "readiness accepted state"),
        (contract, "Current small commit: RT-2e-b COMPLETED / ACCEPTED", "contract accepted state"),
        (scripts_readme, "v300_record_microphone_capture_adapter_status: completed-accepted", "script expected status"),
    ):
        require(source, marker, label)

    combined = "\n".join(
        (readme, roadmap, tasklist, scripts_readme, checklist, readiness, contract)
    )
    for marker in (
        "record 6.2.1",
        "`path_provider` 2.1.6",
        "fake-driver",
        "private temporary",
        "opaque capture id",
        "startStream",
        "authorized-explicit-opt-in-real-device-bounded-capture-evidence-only",
        "no real microphone",
    ):
        require(combined, marker, "planning marker")


def main() -> None:
    actual = validate_changed_surface()
    validate_dependencies()
    validate_adapter()
    validate_generated_plugins(actual)
    validate_docs()

    print("v300_record_microphone_capture_adapter_status: completed-accepted")
    print("v300_rt2eb_record_dependency_resolved: True")
    print("v300_rt2eb_path_provider_direct_dependency: True")
    print("v300_rt2eb_injectable_driver_added: True")
    print("v300_rt2eb_private_artifact_boundary_added: True")
    print("v300_rt2eb_controller_safe_metadata_propagation_added: True")
    print("v300_rt2eb_fake_driver_tests_added: True")
    print("v300_rt2eb_generated_plugin_registration_review_ready: True")
    print("v300_rt2eb_real_permission_request_executed: False")
    print("v300_rt2eb_real_microphone_accessed: False")
    print("v300_rt2eb_real_audio_captured: False")
    print("v300_rt2eb_raw_audio_exposed: False")
    print("v300_rt2e_parent_status: current-pending-rt2ec-implementation")
    print("v300_rt2ec_authorization: authorized-explicit-opt-in-real-device-bounded-capture-evidence-only")


if __name__ == "__main__":
    main()
