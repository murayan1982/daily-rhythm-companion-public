from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "bf17538f8b33aa504671289edda8f55c511fe77d"
CHECKPOINT_COMMIT = "c84617e7ce07ecb1ca1605956eda7435b797c2fe"
CHECKPOINT_BASELINE = "ec6844c63b89803041e0b4e064d45c924e2d0438"
RT5F3_IMPLEMENTATION = "75504424c37222234ea8a4314d01ce386ff92d23"
FW_BASELINE = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f4_configured_local_end_to_end_acceptance.md",
    "scripts/check_v300_rt5f4_configured_local_end_to_end_acceptance.py",
}

CHECKPOINT_FILES = set(EXPECTED_FILES)
CORRECTIVE_FILES = {
    "app/lib/services/integrated_voice_turn_home_screen_binding.dart",
    "app/lib/services/record_speech_activity_source.dart",
    "app/test/integrated_voice_turn_home_screen_binding_test.dart",
    "app/test/integrated_voice_turn_home_screen_widget_test.dart",
    "app/test/record_speech_activity_source_test.dart",
}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise RuntimeError(f"{label} missing marker: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise RuntimeError(f"{label} contains forbidden marker: {marker}")


def changed_files() -> set[str]:
    tracked = {
        line.strip()
        for line in git("diff", "HEAD", "--name-only").splitlines()
        if line.strip()
    }
    untracked = {
        line.strip()
        for line in git("ls-files", "--others", "--exclude-standard").splitlines()
        if line.strip()
    }
    return tracked | untracked


def commit_files(commit: str) -> set[str]:
    return {
        line.strip()
        for line in git(
            "diff-tree", "--no-commit-id", "--name-only", "-r", commit
        ).splitlines()
        if line.strip()
    }


def validate_git_scope() -> None:
    if git("rev-parse", "HEAD").strip() != EXPECTED_HEAD:
        raise RuntimeError("unexpected RT-5f4 accepted corrective HEAD")
    if git("rev-parse", "HEAD^").strip() != CHECKPOINT_COMMIT:
        raise RuntimeError("RT-5f4 corrective parent mismatch")
    if git("rev-parse", f"{CHECKPOINT_COMMIT}^").strip() != CHECKPOINT_BASELINE:
        raise RuntimeError("RT-5f4 checkpoint parent mismatch")
    if commit_files(CHECKPOINT_COMMIT) != CHECKPOINT_FILES:
        raise RuntimeError("RT-5f4 exact seven-file checkpoint surface mismatch")
    if commit_files(EXPECTED_HEAD) != CORRECTIVE_FILES:
        raise RuntimeError("RT-5f4 exact five-file corrective surface mismatch")

    changed = changed_files()
    if changed != EXPECTED_FILES:
        missing = sorted(EXPECTED_FILES - changed)
        unexpected = sorted(changed - EXPECTED_FILES)
        raise RuntimeError(
            "RT-5f4 exact seven-file acceptance-sync surface mismatch; "
            f"missing={missing}; unexpected={unexpected}"
        )


def validate_source() -> None:
    binding = read("app/lib/services/integrated_voice_turn_home_screen_binding.dart")
    record_source = read("app/lib/services/record_speech_activity_source.dart")
    binding_test = read("app/test/integrated_voice_turn_home_screen_binding_test.dart")
    widget_test = read("app/test/integrated_voice_turn_home_screen_widget_test.dart")
    record_test = read("app/test/record_speech_activity_source_test.dart")
    runtime = read("app/lib/services/configured_integrated_voice_turn_runtime.dart")
    coordinator = read("app/lib/services/integrated_voice_turn_coordinator.dart")

    for marker in (
        "class IntegratedVoiceTurnCaptureSession extends ChangeNotifier",
        "captureSession.addListener(_handleCaptureSessionChanged)",
        "captureSession.removeListener(_handleCaptureSessionChanged)",
        "void _handleCaptureSessionChanged()",
        "super.dispose();",
    ):
        require(binding, marker, "repeated Stop Capture corrective")
    if binding.count("notifyListeners();") < 5:
        raise RuntimeError("capture-session notification propagation is incomplete")

    for marker in (
        "const RecordConfig recordSpeechActivityRecordConfig",
        "AudioInterruptionMode.none",
        "AudioEncoder.pcm16bits",
        "sampleRate: 16000",
        "numChannels: 1",
        "autoGain: true",
        "echoCancel: true",
        "noiseSuppress: true",
    ):
        require(record_source, marker, "playback-time speech detection corrective")

    require(
        binding_test,
        "second authorized turn exposes stop without a permission rebuild",
        "binding corrective regression",
    )
    require(
        widget_test,
        "second capture enables stop when permission is already granted",
        "widget corrective regression",
    )
    require(
        record_test,
        "production config remains active during local playback",
        "record corrective regression",
    )

    for marker in (
        "DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN",
        "DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM",
        "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
        "defaultValue: false",
        "RecordMicrophoneCaptureEngine.mobile()",
        "BackendProviderNeutralTranscriptProvider",
        "RecordSpeechActivitySource()",
    ):
        require(runtime, marker, "default-off configured runtime")
    if runtime.count("defaultValue: false") < 3:
        raise RuntimeError("all configured integrated prerequisites must remain default off")

    for marker in (
        "++_operationEpoch;",
        "_detachOperation(operation, requestCooperativeCancel: true)",
        "final flushFuture = _voiceOutput.flush();",
        "IntegratedVoiceTurnSpeechOutcome.interrupted",
        "_hasExclusiveVoiceOutputAccess()",
    ):
        require(coordinator, marker, "DRC-local soft-barge-in boundary")
    if coordinator.index("++_operationEpoch;") > coordinator.index(
        "final flushFuture = _voiceOutput.flush();"
    ):
        raise RuntimeError("operation epoch must invalidate before asynchronous flush")


def validate_docs() -> None:
    docs = {
        path: read(path)
        for path in EXPECTED_FILES
        if not path.startswith("scripts/check_")
    }
    combined = "\n".join(docs.values())
    contract = docs[
        "docs/v300_rt5f4_configured_local_end_to_end_acceptance.md"
    ]

    for marker in (
        "RT-5f4: COMPLETED / ACCEPTED / PUSHED",
        "RT-5f: COMPLETED / ACCEPTED",
        "RT-5: COMPLETED / ACCEPTED",
        "RT-6: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        CHECKPOINT_BASELINE,
        CHECKPOINT_COMMIT,
        EXPECTED_HEAD,
        RT5F3_IMPLEMENTATION,
        FW_BASELINE,
        "exact checkpoint surface: 7 files",
        "exact corrective surface: 5 files",
        "acceptance sync surface: exact seven files",
        "private operator execution: COMPLETED / ACCEPTED",
        "operator acceptance: ACCEPTED",
        "Control A: PASS / ACCEPTED",
        "Control B: PASS / ACCEPTED",
        "Control C: PASS / ACCEPTED",
        "Control D: PASS / ACCEPTED",
        "repeated Stop Capture corrective: REAL-DEVICE PASS",
        "playback-time speech detection corrective: REAL-DEVICE PASS",
        "Backend full: 204 passed, 1 existing warning",
        "Flutter analyze: No issues found",
        "Flutter full: 411 passed",
        "acceptance-sync commit/push: NOT_AUTHORIZED",
    ):
        require(combined, marker, "RT-5f4 acceptance documents")

    for marker in (
        "provider-level LLM hard cancel",
        "Backend HTTP hard cancel",
        "provider TTS synthesis hard cancel",
        "FW real TTS queue flush",
        "configured Live2D / VTS adapter execution",
        "v3.0.0 release readiness",
    ):
        require(contract, marker, "RT-5f4 non-claims")

    for forbidden in (
        "Current implementation state: IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING",
        "current implementation state: IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING",
        "RT-5f4: IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING",
        "RT-5f4 IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING",
    ):
        forbid(combined, forbidden, "stale RT-5f4 current state")

    private_patterns = {
        "credential-shaped value": r"\b(?:sk|sess)-[A-Za-z0-9_-]{16,}\b",
        "private IPv4 URL": r"https?://(?:10\.|127\.|169\.254\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)",
        "Windows private absolute path": r"[A-Za-z]:\\(?:Users|work|private|temp)\\",
    }
    for label, pattern in private_patterns.items():
        if re.search(pattern, contract, flags=re.IGNORECASE):
            raise RuntimeError(f"RT-5f4 acceptance documents contain {label}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Validate the RT-5f4 acceptance-state sync"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Skip git ancestry/worktree checks for an extracted handoff snapshot",
    )
    args = parser.parse_args(argv)

    if not args.snapshot:
        validate_git_scope()
    else:
        missing = sorted(path for path in EXPECTED_FILES | CORRECTIVE_FILES if not (ROOT / path).is_file())
        if missing:
            raise RuntimeError(f"snapshot missing required files: {missing}")

    validate_source()
    validate_docs()

    print("v300_rt5f4_status: completed-accepted-pushed")
    print("v300_rt5f4_exact_acceptance_sync_surface: True")
    print("v300_rt5f4_acceptance_sync_file_count: 7")
    print("v300_rt5f4_checkpoint_surface: 7")
    print("v300_rt5f4_corrective_surface: 5")
    print("v300_rt5f4_runtime_changed_by_acceptance_sync: False")
    print("v300_rt5f4_backend_changed: False")
    print("v300_rt5f4_framework_changed: False")
    print("v300_rt5f4_dependency_changed: False")
    print("v300_rt5f4_control_a_accepted: True")
    print("v300_rt5f4_control_b_accepted: True")
    print("v300_rt5f4_control_c_accepted: True")
    print("v300_rt5f4_control_d_accepted: True")
    print("v300_rt5f4_repeated_stop_capture_corrective_passed: True")
    print("v300_rt5f4_playback_time_speech_detection_corrective_passed: True")
    print("v300_rt5f4_backend_full_passed: 204")
    print("v300_rt5f4_flutter_analyze_passed: True")
    print("v300_rt5f4_flutter_full_passed: 411")
    print("v300_rt5f4_private_operator_execution: completed-accepted")
    print("v300_rt5f4_drc_local_soft_barge_in_only: True")
    print("v300_rt5_parent_status: completed-accepted")
    print("v300_rt6_status: ready-for-exact-contract-review-not-authorized")
    print("v300_rt5f4_acceptance_sync_commit_push_authorized: False")
    print("v300_rt5f4_snapshot_mode:", args.snapshot)


if __name__ == "__main__":
    main()
