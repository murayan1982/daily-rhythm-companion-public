"""Validate RT-2e-c3a real-Android preflight without real execution."""

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
    "docs/v300_rt2ec_real_android_capture_preflight.md",
    "scripts/check_v300_rt2ec_real_android_capture_preflight.py",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"RT-2e-c3a missing {label}: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"RT-2e-c3a forbidden {label}: {marker}")


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
        raise AssertionError(f"RT-2e-c3a git check failed: {detail}")
    return completed.stdout


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        for line in run_git(*args).splitlines():
            path = line.strip().replace("\\", "/")
            if not path:
                continue
            if "/__pycache__/" in f"/{path}" or path.endswith(".pyc"):
                continue
            paths.add(path)
    return paths


def validate_changed_surface() -> None:
    actual = changed_paths()
    if not actual:
        return
    if actual == IMPLEMENTATION_PATHS:
        return

    unexpected = sorted(actual - IMPLEMENTATION_PATHS)
    missing = sorted(IMPLEMENTATION_PATHS - actual)
    details: list[str] = []
    if unexpected:
        details.append("unexpected changed paths:\n" + "\n".join(unexpected))
    if missing:
        details.append("missing ten-file implementation paths:\n" + "\n".join(missing))
    details.append("required worktree form: clean tree or exact ten-file RT-2e-c3a surface")
    raise AssertionError(
        "RT-2e-c3a source/surface mismatch:\n" + "\n".join(details)
    )


def validate_existing_operator_contract() -> None:
    entrypoint = read("app/lib/main_rt2ec_operator.dart")
    operator = read("app/lib/operators/rt2ec_microphone_capture_operator.dart")
    capture = read("app/lib/services/microphone_capture.dart")
    record_adapter = read("app/lib/services/record_microphone_capture_engine.dart")
    permission = read(
        "app/lib/services/permission_handler_microphone_permission_gateway.dart"
    )
    android = read("app/android/app/src/main/AndroidManifest.xml")
    pubspec = read("app/pubspec.yaml")

    for marker, label in (
        ("'DRC_RT2EC_OPERATOR'", "compile-time operator flag"),
        ("defaultValue: false", "fail-closed default"),
        ("dependenciesFactory: _createProductionDependencies", "production factory"),
        ("RecordMicrophoneCaptureEngine.mobile()", "mobile record adapter"),
    ):
        require(entrypoint, marker, label)

    for marker, label in (
        ("Duration(seconds: 15)", "15-second bound"),
        ("_acknowledged", "in-app acknowledgement"),
        ("checkPermission()", "explicit permission check"),
        ("requestPermission()", "explicit permission request"),
        ("_startCapture()", "explicit capture start"),
        ("_stopCapture()", "explicit capture stop"),
        ("discardPrivateArtifact", "immediate private artifact discard"),
        ("Rt2ecOperatorCaptureEvidence", "safe evidence model"),
        ("private artifact discarded", "discard evidence field"),
        ("raw audio exposed", "raw audio evidence field"),
    ):
        require(operator, marker, label)

    for marker, label in (
        ("capture_completed", "completed technical code"),
        ("MicrophoneCapturePhase.completed", "completed phase"),
    ):
        require(capture, marker, label)

    for marker, label in (
        ("'record_version': '6.2.1'", "record version metadata"),
        ("'encoding': 'wav'", "WAV metadata"),
        ("'sample_rate_hz': 16000", "sample rate metadata"),
        ("'channels': 1", "mono metadata"),
        ("'microphone_accessed': _driver.accessesRealMicrophone", "real microphone marker"),
        ("'audio_captured': _driver.accessesRealMicrophone", "real audio marker"),
        ("'raw_audio_exposed': false", "raw audio boundary"),
        ("'private_artifact_registered': true", "private artifact registration"),
    ):
        require(record_adapter, marker, label)

    require(permission, "Permission.microphone", "permission_handler microphone adapter")
    require(android, "android.permission.RECORD_AUDIO", "Android RECORD_AUDIO declaration")
    require(pubspec, "  permission_handler: 12.0.3", "permission pin")
    require(pubspec, "  path_provider: 2.1.6", "path_provider pin")
    require(pubspec, "  record: 6.2.1", "record pin")

    for source, label in (
        (entrypoint, "entrypoint logging"),
        (operator, "operator logging"),
    ):
        forbid(source, "print(", label)
        forbid(source, "debugPrint(", label)
    forbid(operator, "resolvePrivateArtifactPath(", "private path resolution")
    forbid(operator, "startStream(", "raw stream capture")


def validate_preflight_contract() -> None:
    contract = read("docs/v300_rt2ec_real_android_capture_preflight.md")

    for marker, label in (
        ("Status: COMPLETED / ACCEPTED", "accepted status"),
        ("RT-2e-c3b CURRENT / NOT_COMPLETED", "current evidence step"),
        ("18d39ea0676bcd3213c104a71fd5ce2c096c6b96002eb7aaef7ceccd06a2fd86", "archive hash"),
        ("one physical Android handset", "physical Android requirement"),
        ("Android emulator", "emulator exclusion"),
        ("--target lib/main_rt2ec_operator.dart", "separate target command"),
        ("--dart-define=DRC_RT2EC_OPERATOR=true", "compile-time opt-in"),
        ("In Android settings, revoke/deny microphone permission", "permission reset"),
        ("approximately 2 to 5 seconds", "bounded spoken duration"),
        ("before 15 seconds", "hard duration stop"),
        ("discardPrivateArtifact", "private artifact cleanup"),
        ("drc-v300-rt2ec3b-real-android-capture-v1", "evidence schema"),
        ('"target_class": "physical-android"', "target marker"),
        ('"permission_request_attempted": true', "permission request evidence"),
        ('"permission_status": "granted"', "permission granted evidence"),
        ('"capture_outcome": "completed"', "completed evidence"),
        ('"requested_maximum_duration_milliseconds": 15000', "maximum evidence"),
        ('"microphone_accessed": true', "microphone evidence"),
        ('"audio_captured": true', "audio evidence"),
        ('"raw_audio_exposed": false', "raw audio boundary evidence"),
        ('"private_artifact_discarded": true', "discard evidence"),
        ('"cleanup_succeeded": true', "cleanup evidence"),
        ('"backend_started": false', "Backend exclusion evidence"),
        ('"audio_uploaded": false', "upload exclusion evidence"),
        ('"stt_executed": false', "STT exclusion evidence"),
        ("captured duration in 1..15000 ms", "duration acceptance range"),
        ("post-run working tree clean", "clean-tree acceptance"),
        ("No Flutter/runtime/dependency/platform/Backend source changed", "docs-only statement"),
    ):
        require(contract, marker, label)

    for marker, label in (
        ("adb shell pm revoke", "hard-coded package mutation command"),
        ("com.example", "hard-coded application id"),
        ("startStream", "raw stream instruction"),
        ("audio playback", "audio playback instruction"),
    ):
        forbid(contract, marker, label)


def validate_docs_state() -> None:
    docs = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "adapter": read("docs/v300_record_microphone_capture_adapter.md"),
        "readiness": read("docs/v300_rt2ec_operator_capture_harness_readiness.md"),
        "harness": read("docs/v300_rt2ec_operator_capture_harness.md"),
    }

    combined = "\n".join(docs.values())
    for marker, label in (
        ("RT-2e-c3a", "accepted preflight step"),
        ("COMPLETED / ACCEPTED", "accepted state"),
        ("RT-2e-c3b", "current real evidence step"),
        ("authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only", "real evidence authorization"),
        ("physical Android", "physical target"),
        ("15-second", "duration bound"),
        ("marker-only", "safe evidence mode"),
        ("No real permission request", "non-execution statement"),
        ("No upload or STT", "upload/STT exclusion"),
    ):
        require(combined, marker, label)

    require(
        docs["scripts README"],
        "v300_rt2ec_real_android_capture_preflight_status: completed-accepted",
        "expected gate output",
    )


def main() -> None:
    validate_changed_surface()
    validate_existing_operator_contract()
    validate_preflight_contract()
    validate_docs_state()

    print("v300_rt2ec_real_android_capture_preflight_status: completed-accepted")
    print("v300_rt2ec3a_exact_current_surface_inspected: True")
    print("v300_rt2ec3a_physical_android_required: True")
    print("v300_rt2ec3a_separate_operator_target_required: True")
    print("v300_rt2ec3a_compile_time_opt_in_required: True")
    print("v300_rt2ec3a_in_app_acknowledgement_required: True")
    print("v300_rt2ec3a_explicit_permission_request_required: True")
    print("v300_rt2ec3a_single_bounded_capture_required: True")
    print("v300_rt2ec3a_maximum_capture_seconds: 15")
    print("v300_rt2ec3a_private_artifact_cleanup_required: True")
    print("v300_rt2ec3a_safe_evidence_contract_added: True")
    print("v300_rt2ec3a_default_app_wiring_changed: False")
    print("v300_rt2ec3a_flutter_runtime_changed: False")
    print("v300_rt2ec3a_permission_request_executed: False")
    print("v300_rt2ec3a_microphone_accessed: False")
    print("v300_rt2ec3a_audio_captured: False")
    print("v300_rt2ec_parent_status: current-pending-rt2ec3b-execution")
    print("v300_rt2ec3b_authorization: authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only")


if __name__ == "__main__":
    main()
