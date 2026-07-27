"""Validate accepted RT-2e-a exact-surface and recorder-package readiness."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACCEPTANCE_SYNC_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_microphone_real_capture_adapter_readiness.md",
    "scripts/check_v300_microphone_real_capture_adapter_readiness.py",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"RT-2e-a missing {label}: {marker}")


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
        raise AssertionError(f"RT-2e-a git check failed: {detail}")
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


def validate_surface() -> None:
    actual = changed_paths()
    if not actual:
        return
    unexpected = sorted(actual - ACCEPTANCE_SYNC_PATHS)
    missing = sorted(ACCEPTANCE_SYNC_PATHS - actual)
    if unexpected or missing:
        details: list[str] = []
        if unexpected:
            details.append("unexpected changed paths:\n" + "\n".join(unexpected))
        if missing:
            details.append("missing acceptance-sync paths:\n" + "\n".join(missing))
        details.append("accepted worktree forms are: clean tree or exact seven-file sync")
        raise AssertionError(
            "RT-2e-a accepted-state surface mismatch:\n" + "\n".join(details)
        )


def validate_exact_runtime_surface() -> None:
    pubspec = read("app/pubspec.yaml")
    lock = read("app/pubspec.lock")
    capture = read("app/lib/services/microphone_capture.dart")
    permission = read(
        "app/lib/services/permission_handler_microphone_permission_gateway.dart"
    )
    android = read("app/android/app/src/main/AndroidManifest.xml")
    ios = read("app/ios/Runner/Info.plist")

    require(pubspec, "sdk: ^3.11.5", "Dart SDK baseline")
    require(pubspec, "permission_handler: 12.0.3", "permission dependency")
    if re.search(r"^\s{2}record\s*:", pubspec, re.MULTILINE):
        raise AssertionError("RT-2e-a must not add direct record dependency")
    if re.search(r"^\s{2}path_provider\s*:", pubspec, re.MULTILINE):
        raise AssertionError("RT-2e-a must not add direct path_provider dependency")
    require(lock, "  path_provider:\n    dependency: transitive", "transitive path_provider")
    if re.search(r"^  record:$", lock, re.MULTILINE):
        raise AssertionError("RT-2e-a lockfile must not resolve record package")

    for forbidden in (
        "package:record/record.dart",
        "package:path_provider/path_provider.dart",
        "AudioRecorder(",
        ".startStream(",
    ):
        if forbidden in capture:
            raise AssertionError(f"RT-2e-a runtime adapter started early: {forbidden}")

    require(
        permission,
        "PermissionHandlerMicrophonePermissionGateway",
        "existing permission gateway",
    )
    require(android, "android.permission.RECORD_AUDIO", "Android RECORD_AUDIO")
    require(ios, "NSMicrophoneUsageDescription", "iOS microphone usage")


def validate_docs() -> None:
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    contract = read("docs/v300_microphone_real_capture_adapter_readiness.md")

    for source, marker, label in (
        (readme, "Current small commit: RT-2e-b (**CURRENT / NOT_COMPLETED**)", "README current commit"),
        (readme, "RT-2e-a  COMPLETED / ACCEPTED", "README accepted RT-2e-a"),
        (roadmap, "Current small commit: RT-2e-b CURRENT / NOT_COMPLETED", "roadmap current commit"),
        (roadmap, "RT-2e-b authorization: authorized-injectable-record-adapter-and-private-temporary-artifact-fake-tests-only", "roadmap authorization"),
        (tasklist, "status: COMPLETED / ACCEPTED", "tasklist accepted status"),
        (tasklist, "status: CURRENT / NOT_COMPLETED", "tasklist RT-2e-b current status"),
        (checklist, "Current small commit: RT-2e-b CURRENT / NOT_COMPLETED", "checklist current commit"),
        (checklist, "Implementation state: COMPLETED / ACCEPTED", "checklist accepted RT-2e-a"),
        (contract, "Current small commit: RT-2e-a COMPLETED / ACCEPTED", "contract accepted status"),
        (contract, "Next small commit: RT-2e-b CURRENT / NOT_COMPLETED; NOT_STARTED", "contract next commit"),
        (scripts_readme, "v300_microphone_real_capture_adapter_readiness_status: completed-accepted", "script expected status"),
    ):
        require(source, marker, label)

    combined = "\n".join(
        (readme, roadmap, tasklist, scripts_readme, checklist, contract)
    )
    for marker in (
        "record 6.2.1",
        "record 7.x",
        "Dart 3.12",
        "startStream",
        "private temporary",
        "opaque capture",
        "authorized-injectable-record-adapter-and-private-temporary-artifact-fake-tests-only",
        "blocked-pending-rt2eb-acceptance",
    ):
        require(combined, marker, "planning marker")


def main() -> None:
    validate_surface()
    validate_exact_runtime_surface()
    validate_docs()

    print("v300_microphone_real_capture_adapter_readiness_status: completed-accepted")
    print("v300_rt2ea_exact_current_surface_inspected: True")
    print("v300_rt2ea_record_candidate_selected: record-6.2.1")
    print("v300_rt2ea_record_7x_compatible_with_current_sdk: False")
    print("v300_rt2ea_dependency_added: False")
    print("v300_rt2ea_flutter_runtime_changed: False")
    print("v300_rt2ea_platform_files_changed: False")
    print("v300_rt2ea_permission_request_executed: False")
    print("v300_rt2ea_microphone_accessed: False")
    print("v300_rt2ea_audio_captured: False")
    print("v300_rt2e_parent_status: current-pending-rt2eb-implementation")
    print("v300_rt2eb_authorization: authorized-injectable-record-adapter-and-private-temporary-artifact-fake-tests-only")


if __name__ == "__main__":
    main()
