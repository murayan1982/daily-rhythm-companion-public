"""Validate accepted RT-2e-c3b marker-only real Android evidence."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "ddae21944ac0e251cd8194bf93982bd5dc7a4ae8"
ACCEPTANCE_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_record_microphone_capture_adapter.md",
    "docs/v300_rt2ec_operator_capture_harness_readiness.md",
    "docs/v300_rt2ec_operator_capture_harness.md",
    "docs/v300_rt2ec_real_android_capture_preflight.md",
    "docs/v300_rt2ec_real_android_capture_evidence.md",
    "scripts/check_v300_rt2ec_real_android_capture_evidence.py",
}

FINAL_STATUS_SYNC_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt2ec_operator_capture_harness.md",
    "docs/v300_rt2ec_real_android_capture_preflight.md",
    "docs/v300_rt2ec_real_android_capture_evidence.md",
    "scripts/check_v300_rt2ec_operator_capture_harness.py",
    "scripts/check_v300_rt2ec_real_android_capture_preflight.py",
    "scripts/check_v300_rt2ec_real_android_capture_evidence.py",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"RT-2e-c3b missing {label}: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"RT-2e-c3b forbidden {label}: {marker}")


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
        raise AssertionError(f"RT-2e-c3b git check failed: {detail}")
    return completed.stdout


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for raw in run_git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if not raw:
            continue
        path = raw[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        normalized = path.replace("\\", "/")
        if "/__pycache__/" in f"/{normalized}" or normalized.endswith(".pyc"):
            continue
        paths.add(normalized)
    return paths


def validate_changed_surface() -> None:
    actual = changed_paths()
    if not actual or actual in (ACCEPTANCE_PATHS, FINAL_STATUS_SYNC_PATHS):
        return
    unexpected = sorted(actual - ACCEPTANCE_PATHS)
    missing = sorted(ACCEPTANCE_PATHS - actual)
    missing_final_sync = sorted(FINAL_STATUS_SYNC_PATHS - actual)
    details: list[str] = []
    if unexpected:
        details.append("unexpected changed paths:\n" + "\n".join(unexpected))
    if missing:
        details.append("missing eleven-file acceptance paths:\n" + "\n".join(missing))
    if missing_final_sync:
        details.append("missing eleven-file final-status-sync paths:\n" + "\n".join(missing_final_sync))
    details.append("required worktree form: clean tree, exact eleven-file RT-2e-c3b acceptance surface, or exact eleven-file final-status sync")
    raise AssertionError("RT-2e-c3b source/surface mismatch:\n" + "\n".join(details))


def validate_source_commit() -> None:
    run_git("cat-file", "-e", f"{SOURCE_COMMIT}^{{commit}}")
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_COMMIT, "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "RT-2e-c3b accepted source commit is not an ancestor of HEAD"
        )


def validate_runtime_contract() -> None:
    entrypoint = read("app/lib/main_rt2ec_operator.dart")
    operator = read("app/lib/operators/rt2ec_microphone_capture_operator.dart")
    capture = read("app/lib/services/microphone_capture.dart")
    adapter = read("app/lib/services/record_microphone_capture_engine.dart")

    for marker, label in (
        ("'DRC_RT2EC_OPERATOR'", "compile-time opt-in"),
        ("defaultValue: false", "fail-closed default"),
        ("dependenciesFactory: _createProductionDependencies", "lazy production factory"),
    ):
        require(entrypoint, marker, label)
    for marker, label in (
        ("Duration(seconds: 15)", "15-second bound"),
        ("_acknowledged", "in-app acknowledgement"),
        ("requestPermission()", "explicit permission request"),
        ("discardPrivateArtifact", "private artifact discard"),
        ("Rt2ecOperatorCaptureEvidence", "safe evidence model"),
    ):
        require(operator, marker, label)
    require(capture, "capture_completed", "completed technical code")
    for marker, label in (
        ("'encoding': 'wav'", "WAV encoding"),
        ("'sample_rate_hz': 16000", "sample rate"),
        ("'channels': 1", "mono channel"),
        ("'raw_audio_exposed': false", "raw-audio boundary"),
    ):
        require(adapter, marker, label)
    for source, label in ((entrypoint, "entrypoint"), (operator, "operator")):
        forbid(source, "print(", f"{label} logging")
        forbid(source, "debugPrint(", f"{label} debug logging")
    forbid(operator, "startStream(", "raw stream capture")
    forbid(operator, "resolvePrivateArtifactPath(", "private path resolution")


def validate_evidence() -> None:
    evidence = read("docs/v300_rt2ec_real_android_capture_evidence.md")
    markers = (
        ("Status: COMPLETED / ACCEPTED", "accepted status"),
        (f"Source commit: {SOURCE_COMMIT}", "source commit"),
        ('"schema": "drc-v300-rt2ec3b-real-android-capture-v1"', "schema"),
        (f'"source_commit": "{SOURCE_COMMIT}"', "marker source"),
        ('"target_class": "physical-android"', "physical target"),
        ('"operator_target_enabled": true', "operator target"),
        ('"acknowledgement_completed": true', "acknowledgement"),
        ('"permission_status": "granted"', "permission status"),
        ('"permission_request_attempted": true', "permission request"),
        ('"capture_phase": "completed"', "capture phase"),
        ('"capture_outcome": "completed"', "capture outcome"),
        ('"technical_code": "capture_completed"', "technical code"),
        ('"requested_maximum_duration_milliseconds": 15000', "requested maximum"),
        ('"captured_duration_milliseconds": 4820', "captured duration"),
        ('"microphone_accessed": true', "microphone access"),
        ('"audio_captured": true', "audio captured"),
        ('"raw_audio_exposed": false', "raw audio boundary"),
        ('"private_artifact_registered": true', "artifact registration"),
        ('"private_artifact_discarded": true', "artifact discard"),
        ('"cleanup_succeeded": true', "cleanup"),
        ('"backend_started": false', "Backend exclusion"),
        ('"audio_uploaded": false', "upload exclusion"),
        ('"stt_executed": false', "STT exclusion"),
        ('"private_path_recorded": false', "private path exclusion"),
        ('"opaque_capture_id_recorded": false', "opaque id exclusion"),
        ('"device_identifier_recorded": false', "device id exclusion"),
        ('"raw_audio_recorded": false', "raw audio record exclusion"),
        ('"raw_screenshot_committed": false', "screenshot exclusion"),
        ('"post_run_working_tree_clean": true', "clean tree evidence"),
        ("first operator session", "non-acceptance dry-run disclosure"),
        ("exactly one completed capture", "accepted-session capture count"),
        ("RT-3 BLOCKED_REAL_STT_NOT_IMPLEMENTED", "next blocked phase"),
    )
    for marker, label in markers:
        require(evidence, marker, label)

    for marker, label in (
        ('"captured_duration_milliseconds": 0', "zero duration"),
        ('"captured_duration_milliseconds": 15001', "over-limit duration"),
        ('"raw_audio_exposed": true', "raw audio exposure"),
        ('"private_artifact_discarded": false', "artifact retention"),
        ('"cleanup_succeeded": false', "cleanup failure"),
        ('"backend_started": true', "Backend execution"),
        ('"audio_uploaded": true', "audio upload"),
        ('"stt_executed": true', "STT execution"),
        ('"private_path_recorded": true', "private path record"),
        ('"opaque_capture_id_recorded": true', "opaque id record"),
        ('"device_identifier_recorded": true', "device identifier record"),
        ('"raw_audio_recorded": true', "raw audio record"),
        ('"raw_screenshot_committed": true', "committed screenshot"),
    ):
        forbid(evidence, marker, label)


def validate_docs_state() -> None:
    paths = (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "docs/v300_record_microphone_capture_adapter.md",
        "docs/v300_rt2ec_operator_capture_harness_readiness.md",
        "docs/v300_rt2ec_operator_capture_harness.md",
        "docs/v300_rt2ec_real_android_capture_preflight.md",
    )
    combined = "\n".join(read(path) for path in paths)
    for marker, label in (
        ("RT-2e-c3b COMPLETED / ACCEPTED", "accepted evidence step"),
        ("RT-2 COMPLETED / ACCEPTED", "accepted parent phase"),
        (SOURCE_COMMIT, "accepted source commit"),
        ("4820", "accepted duration"),
        ("marker-only", "safe evidence mode"),
        ("post-run working tree", "clean-tree record"),
        ("RT-3", "next phase"),
        ("BLOCKED_REAL_STT_NOT_IMPLEMENTED", "STT block"),
        ("No upload or STT", "upload/STT exclusion"),
    ):
        require(combined, marker, label)
    require(
        read("docs/v300_rt2ec_real_android_capture_evidence.md"),
        "Final checkpoint-gate status synchronization",
        "final checkpoint status synchronization record",
    )

    harness_gate = read("scripts/check_v300_rt2ec_operator_capture_harness.py")
    preflight_gate = read("scripts/check_v300_rt2ec_real_android_capture_preflight.py")
    for source, label in ((harness_gate, "operator harness gate"), (preflight_gate, "preflight gate")):
        require(source, 'print("v300_rt2ec_parent_status: completed-accepted")', f"{label} final parent output")
        require(source, 'print("v300_rt2_status: completed-accepted")', f"{label} RT-2 output")
        require(source, 'print("v300_next_phase: blocked-real-stt-not-implemented")', f"{label} next-phase output")
        forbid(source, 'print("v300_rt2ec_parent_status: current-pending-', f"{label} stale executable pending output")

    require(
        read("scripts/README.md"),
        "v300_rt2ec_real_android_capture_evidence_status: completed-accepted",
        "expected gate output",
    )


def main() -> None:
    validate_changed_surface()
    validate_source_commit()
    validate_runtime_contract()
    validate_evidence()
    validate_docs_state()

    print("v300_rt2ec_real_android_capture_evidence_status: completed-accepted")
    print(f"v300_rt2ec3b_source_commit: {SOURCE_COMMIT}")
    print("v300_rt2ec3b_target_class: physical-android")
    print("v300_rt2ec3b_operator_target_enabled: True")
    print("v300_rt2ec3b_acknowledgement_completed: True")
    print("v300_rt2ec3b_permission_status: granted")
    print("v300_rt2ec3b_permission_request_attempted: True")
    print("v300_rt2ec3b_capture_outcome: completed")
    print("v300_rt2ec3b_technical_code: capture_completed")
    print("v300_rt2ec3b_requested_maximum_duration_milliseconds: 15000")
    print("v300_rt2ec3b_captured_duration_milliseconds: 4820")
    print("v300_rt2ec3b_microphone_accessed: True")
    print("v300_rt2ec3b_audio_captured: True")
    print("v300_rt2ec3b_raw_audio_exposed: False")
    print("v300_rt2ec3b_private_artifact_registered: True")
    print("v300_rt2ec3b_private_artifact_discarded: True")
    print("v300_rt2ec3b_cleanup_succeeded: True")
    print("v300_rt2ec3b_backend_started: False")
    print("v300_rt2ec3b_audio_uploaded: False")
    print("v300_rt2ec3b_stt_executed: False")
    print("v300_rt2ec3b_post_run_working_tree_clean: True")
    print("v300_rt2_status: completed-accepted")
    print("v300_next_phase: blocked-real-stt-not-implemented")


if __name__ == "__main__":
    main()
