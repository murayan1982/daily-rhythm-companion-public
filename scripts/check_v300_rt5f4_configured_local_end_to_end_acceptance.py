from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "ec6844c63b89803041e0b4e064d45c924e2d0438"
RT5F3_IMPLEMENTATION = "75504424c37222234ea8a4314d01ce386ff92d23"
RT5F3_IMPLEMENTATION_BASELINE = "888814d09fad75039733a4a94719454e0a69db63"
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

RT5F3_IMPLEMENTATION_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md",
    "scripts/check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py",
    "app/lib/main.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/services/integrated_voice_turn_coordinator.dart",
    "app/lib/services/speech_activity_source.dart",
    "app/lib/services/record_speech_activity_source.dart",
    "app/lib/services/integrated_voice_turn_home_screen_binding.dart",
    "app/lib/services/configured_integrated_voice_turn_runtime.dart",
    "app/test/integrated_voice_turn_coordinator_test.dart",
    "app/test/speech_activity_source_test.dart",
    "app/test/record_speech_activity_source_test.dart",
    "app/test/integrated_voice_turn_home_screen_binding_test.dart",
    "app/test/integrated_voice_turn_home_screen_widget_test.dart",
    "app/test/main_integrated_voice_turn_wiring_widget_test.dart",
}

RT5F3_ACCEPTANCE_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md",
    "scripts/check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py",
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


def main() -> None:
    if git("rev-parse", "HEAD").strip() != EXPECTED_HEAD:
        raise RuntimeError("unexpected RT-5f4 checkpoint baseline HEAD")
    if git("rev-parse", "HEAD^").strip() != RT5F3_IMPLEMENTATION:
        raise RuntimeError("RT-5f3 acceptance parent mismatch")
    if git("rev-parse", f"{RT5F3_IMPLEMENTATION}^").strip() != RT5F3_IMPLEMENTATION_BASELINE:
        raise RuntimeError("RT-5f3 implementation parent mismatch")
    if commit_files(RT5F3_IMPLEMENTATION) != RT5F3_IMPLEMENTATION_FILES:
        raise RuntimeError("RT-5f3 exact twenty-file implementation surface mismatch")
    if commit_files(EXPECTED_HEAD) != RT5F3_ACCEPTANCE_FILES:
        raise RuntimeError("RT-5f3 exact seven-file acceptance surface mismatch")

    changed = changed_files()
    if changed != EXPECTED_FILES:
        missing = sorted(EXPECTED_FILES - changed)
        unexpected = sorted(changed - EXPECTED_FILES)
        raise RuntimeError(
            f"RT-5f4 exact seven-file surface mismatch; missing={missing}; "
            f"unexpected={unexpected}"
        )

    main_dart = read("app/lib/main.dart")
    runtime = read("app/lib/services/configured_integrated_voice_turn_runtime.dart")
    binding = read("app/lib/services/integrated_voice_turn_home_screen_binding.dart")
    coordinator = read("app/lib/services/integrated_voice_turn_coordinator.dart")
    source_contract = read("app/lib/services/speech_activity_source.dart")
    record_source = read("app/lib/services/record_speech_activity_source.dart")
    voice_runtime = read(
        "app/lib/services/configured_realtime_terminal_voice_output_runtime.dart"
    )
    stream_controller = read("app/lib/services/realtime_text_stream_controller.dart")
    home = read("app/lib/screens/home_screen.dart")

    for marker in (
        "ConfiguredIntegratedVoiceTurnRuntime.fromEnvironment",
        "integratedVoiceTurnBindingFactory",
    ):
        require(main_dart, marker, "main configured wiring")

    for marker in (
        "DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN",
        "defaultValue: false",
        "DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM",
        "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
        "defaultTargetPlatform == TargetPlatform.android",
        "defaultTargetPlatform == TargetPlatform.iOS",
        "RecordMicrophoneCaptureEngine.mobile()",
        "BackendProviderNeutralTranscriptProvider",
        "RecordSpeechActivitySource()",
        "final dedicatedVoiceBinding = voiceBindingFactory()",
        "uri.hasQuery",
        "uri.path.isEmpty || uri.path == '/'",
    ):
        require(runtime, marker, "configured integrated runtime")
    if runtime.count("defaultValue: false") < 3:
        raise RuntimeError("all three configured integrated prerequisites must default off")

    for marker in (
        "integratedVoiceTurnCaptureMaximumDuration = Duration(",
        "seconds: 15",
        "session-local",
        "_authorizedTurnGeneration",
        "IntegratedVoiceTurnPhase.staging",
        "IntegratedVoiceTurnPhase.acquiringTranscript",
        "IntegratedVoiceTurnPhase.streaming",
        "IntegratedVoiceTurnPhase.voiceOutput",
        "speechActivitySource.disarm()",
        "coordinator.handleSpeechActivity",
        "captureSession.cancel()",
    ):
        require(binding, marker, "integrated HomeScreen binding")
    forbid(
        binding,
        "IntegratedVoiceTurnPhase.capturing ||",
        "capture-phase speech arming",
    )

    for marker in (
        "++_operationEpoch;",
        "_activeTurn = null;",
        "_detachOperation(operation, requestCooperativeCancel: true)",
        "final flushFuture = _voiceOutput.flush();",
        "flushResult.localPlaybackStopRequested",
        "flushResult.localPlaybackStopSucceeded",
        "IntegratedVoiceTurnSpeechOutcome.interrupted",
        "integrated_voice_turn_interrupted",
        "_hasExclusiveVoiceOutputAccess()",
        "_sameVoiceOutputItem(processResult.item, enqueuedItem)",
    ):
        require(coordinator, marker, "integrated coordinator")
    if coordinator.index("++_operationEpoch;") > coordinator.index(
        "final flushFuture = _voiceOutput.flush();"
    ):
        raise RuntimeError("operation epoch must invalidate before asynchronous flush")

    for marker in (
        "speechActivityDefaultThresholdDbfs = -24.0",
        "speechActivityDefaultRequiredConsecutiveSamples = 3",
        "milliseconds: 100",
        "milliseconds: 1500",
        "seconds: 90",
        "Public state is metadata-only",
    ):
        require(source_contract, marker, "speech activity contract")

    for marker in (
        "AudioEncoder.pcm16bits",
        "sampleRate: 16000",
        "numChannels: 1",
        "autoGain: true",
        "echoCancel: true",
        "noiseSuppress: true",
        "Intentionally drain and drop every chunk.",
        "One confirmed event is permitted per arming generation.",
    ):
        require(record_source, marker, "record speech activity source")

    for marker in (
        "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
        "defaultValue: false",
        "AudioplayersVoiceOutputAudioEngine",
        "VoiceOutputAudioPlayerController",
    ):
        require(voice_runtime, marker, "configured voice-output runtime")
    for marker in (
        "cancelMode: 'cooperative'",
        "RealtimeTextStreamControllerPhase.cancelRequested",
        "Future<void> cancel()",
    ):
        require(stream_controller, marker, "cooperative stream controller")

    for marker in (
        "Integrated Voice Turn",
        "Integrated configuration: $configuration",
        "Integrated opt-in:",
        "Coordinator phase:",
        "Speech source phase:",
        "Operation epoch:",
        "Turn generation:",
        "Interruption count:",
        "Pending voice output:",
        "Local stop retry required:",
    ):
        require(home, marker, "metadata-only HomeScreen")

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
        "RT-5f4: IMPLEMENTED / PRIVATE_OPERATOR_EXECUTION_PENDING",
        EXPECTED_HEAD,
        RT5F3_IMPLEMENTATION,
        FW_BASELINE,
        "exact implementation surface: 7 files",
        "private operator execution: NOT_AUTHORIZED",
        "commit/push: NOT_AUTHORIZED",
        "RT-5: CURRENT / NOT_COMPLETED",
        "natural full-turn control",
        "silent-playback negative control",
        "Real user-speech interruption",
        "Recovery turn",
        "audible playback stops within 3 seconds",
        "old audio does not resume during the following 5 seconds",
        "operator acceptance: NOT_EXECUTED / NOT_CLAIMED",
    ):
        require(combined, marker, "RT-5f4 checkpoint documents")

    for marker in (
        "provider-level LLM hard cancel",
        "Backend HTTP hard cancel",
        "provider TTS synthesis hard cancel",
        "FW real TTS queue flush",
        "v3.0.0 release readiness",
    ):
        require(contract, marker, "RT-5f4 non-claims")

    for forbidden in (
        "RT-5f4: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "RT-5f4: COMPLETED / ACCEPTED",
        "RT-5f4: PUSHED",
        "private operator execution: COMPLETED",
        "operator acceptance: ACCEPTED",
        "RT-5f: COMPLETED / ACCEPTED",
        "RT-5: COMPLETED / ACCEPTED",
    ):
        forbid(combined, forbidden, "premature RT-5f4 acceptance")

    private_patterns = {
        "credential-shaped value": r"\b(?:sk|sess)-[A-Za-z0-9_-]{16,}\b",
        "private IPv4 URL": r"https?://(?:10\.|127\.|169\.254\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.)",
        "Windows private absolute path": r"[A-Za-z]:\\(?:Users|work|private|temp)\\",
    }
    for label, pattern in private_patterns.items():
        if re.search(pattern, contract, flags=re.IGNORECASE):
            raise RuntimeError(f"RT-5f4 documents contain {label}")

    print("v300_rt5f4_status: implemented-private-operator-execution-pending")
    print("v300_rt5f4_exact_change_surface: True")
    print("v300_rt5f4_exact_file_count: 7")
    print("v300_rt5f3_implementation_surface: 20")
    print("v300_rt5f3_acceptance_surface: 7")
    print("v300_rt5f4_runtime_changed: False")
    print("v300_rt5f4_backend_changed: False")
    print("v300_rt5f4_framework_changed: False")
    print("v300_rt5f4_dependency_changed: False")
    print("v300_rt5f4_default_off_runtime_preserved: True")
    print("v300_rt5f4_capture_phase_speech_activity_armed: False")
    print("v300_rt5f4_dedicated_stream_and_voice_output_ownership: True")
    print("v300_rt5f4_drc_local_soft_barge_in_only: True")
    print("v300_rt5f4_private_operator_execution: not-authorized-not-executed")
    print("v300_rt5f4_commit_push_authorized: False")
    print("v300_rt5_parent_status: current-not-completed")


if __name__ == "__main__":
    main()
