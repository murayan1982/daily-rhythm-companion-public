from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "75504424c37222234ea8a4314d01ce386ff92d23"
IMPLEMENTATION_BASELINE = "888814d09fad75039733a4a94719454e0a69db63"
IMPLEMENTATION_COMMIT = "75504424c37222234ea8a4314d01ce386ff92d23"
FW_BASELINE = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md",
    "scripts/check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py",
}

IMPLEMENTATION_FILES = EXPECTED_FILES | {
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
        for line in git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        if line.strip()
    }


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise RuntimeError(f"{label} missing marker: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise RuntimeError(f"{label} contains forbidden marker: {marker}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    if git("rev-parse", "HEAD").strip() != EXPECTED_HEAD:
        raise RuntimeError("unexpected RT-5f3 acceptance-sync baseline HEAD")
    if git("rev-parse", f"{IMPLEMENTATION_COMMIT}^").strip() != IMPLEMENTATION_BASELINE:
        raise RuntimeError("RT-5f3 implementation parent mismatch")
    if commit_files(IMPLEMENTATION_COMMIT) != IMPLEMENTATION_FILES:
        raise RuntimeError("RT-5f3 exact twenty-file implementation commit mismatch")
    if changed_files() != EXPECTED_FILES:
        raise RuntimeError("RT-5f3 acceptance-sync exact seven-file surface mismatch")

    coordinator = read("app/lib/services/integrated_voice_turn_coordinator.dart")
    source_contract = read("app/lib/services/speech_activity_source.dart")
    record_source = read("app/lib/services/record_speech_activity_source.dart")
    binding = read("app/lib/services/integrated_voice_turn_home_screen_binding.dart")
    runtime = read("app/lib/services/configured_integrated_voice_turn_runtime.dart")
    main_dart = read("app/lib/main.dart")
    home = read("app/lib/screens/home_screen.dart")

    for marker in (
        "_hasExclusiveVoiceOutputAccess()",
        "Voice output must remain empty and idle after phase notification.",
        "_sameVoiceOutputItem(processResult.item, enqueuedItem)",
        "actual.itemId == expected.itemId",
        "actual.generation == expected.generation",
        "integratedVoiceTurnMaxRememberedSpeechEventIds = 32",
    ):
        require(coordinator, marker, "coordinator")
    if coordinator.count("if (!_hasExclusiveVoiceOutputAccess())") < 3:
        raise RuntimeError("three RT-5f2 voice-output exclusivity checks are required")
    for marker in (
        "Fake-only RT-5f2 coordinator",
        "fake input",
        "fake capture",
        "fake staging",
        "fake text stream",
        "fake voice output",
    ):
        forbid(coordinator, marker, "production-neutral coordinator")

    for marker in (
        "speechActivityDefaultThresholdDbfs = -24.0",
        "speechActivityDefaultRequiredConsecutiveSamples = 3",
        "milliseconds: 100",
        "milliseconds: 1500",
        "seconds: 90",
        "abstract class SpeechActivitySource extends ChangeNotifier",
        "Future<bool> arm({required int generation, required bool foreground})",
    ):
        require(source_contract, marker, "speech source contract")

    for marker in (
        "AudioEncoder.pcm16bits",
        "sampleRate: 16000",
        "numChannels: 1",
        "autoGain: true",
        "echoCancel: true",
        "noiseSuppress: true",
        "Intentionally drain and drop every chunk.",
        "One confirmed event is permitted per arming generation.",
        "speech_activity_driver_start_failed",
        "speech_activity_driver_stream_failed",
        "speech_activity_maximum_lifetime_reached",
        "_driverStartOperation",
    ):
        require(record_source, marker, "record speech source")

    for marker in (
        "class IntegratedVoiceTurnHomeScreenBinding extends ChangeNotifier",
        "session-local",
        "!coordinator.state.isBusy",
        "captureSession.cancel()",
        "IntegratedVoiceTurnPhase.staging",
        "IntegratedVoiceTurnPhase.acquiringTranscript",
        "IntegratedVoiceTurnPhase.streaming",
        "IntegratedVoiceTurnPhase.voiceOutput",
        "speechActivitySource.disarm()",
        "_speechActivityTail",
        "_authorizedTurnGeneration",
        "_enqueueSpeechActivityOperation",
        "coordinator.handleSpeechActivity",
    ):
        require(binding, marker, "HomeScreen binding")

    for marker in (
        "DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN",
        "defaultValue: false",
        "DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM",
        "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
        "RecordMicrophoneCaptureEngine.mobile()",
        "PermissionHandlerMicrophonePermissionGateway()",
        "RecordSpeechActivitySource()",
        "final dedicatedVoiceBinding = voiceBindingFactory()",
        "uri.hasQuery",
        "uri.path.isEmpty || uri.path == '/'",
    ):
        require(runtime, marker, "configured integrated runtime")

    for marker in (
        "ConfiguredIntegratedVoiceTurnRuntime.fromEnvironment",
        "integratedVoiceTurnBindingFactory",
    ):
        require(main_dart, marker, "main wiring")

    for marker in (
        "Integrated Voice Turn",
        "Integrated configuration: $configuration",
        "Integrated opt-in:",
        "integrated-voice-turn-start-button",
        "integrated-voice-turn-stop-capture-button",
        "Coordinator phase:",
        "Speech source phase:",
        "Operation epoch:",
        "Turn generation:",
        "Interruption count:",
        "Pending voice output:",
        "Local stop retry required:",
        "does not display transcript text",
        "does not share the manual RT-4f4 / RT-5e resources",
    ):
        require(home, marker, "HomeScreen")
    if home.count("Configuration: $configuration") != 0:
        raise RuntimeError("integrated configuration label must remain unique")
    if home.count("Integrated configuration: $configuration") != 1:
        raise RuntimeError("exactly one integrated configuration label is required")

    focused_tests = "\n".join(
        read(path)
        for path in (
            "app/test/integrated_voice_turn_coordinator_test.dart",
            "app/test/speech_activity_source_test.dart",
            "app/test/record_speech_activity_source_test.dart",
            "app/test/integrated_voice_turn_home_screen_binding_test.dart",
            "app/test/integrated_voice_turn_home_screen_widget_test.dart",
            "app/test/main_integrated_voice_turn_wiring_widget_test.dart",
        )
    )
    for marker in (
        "three consecutive threshold samples emit exactly once",
        "below-threshold sample resets consecutive confirmation",
        "a new arming generation may emit a new event",
        "background disarms active source",
        "maximum lifetime disarms",
        "late samples after disarm are inert",
        "session opt-in defaults off",
        "speech source stays disarmed during capture and arms after stop",
        "opt-out disarms activity and cancels an active capture",
        "confirmed foreground event is forwarded once and invalidates turn",
        "metadata section never renders private sentinel values",
        "configured runtime requires every compile-time prerequisite",
        "default main app keeps integrated wiring unconfigured",
        "public coordinator messages are production-neutral",
    ):
        require(focused_tests, marker, "focused RT-5f3 tests")

    docs = {
        path: read(path)
        for path in EXPECTED_FILES
        if not path.startswith("scripts/check_")
    }
    combined = "\n".join(docs.values())
    for marker in (
        "RT-5f3: COMPLETED / ACCEPTED / PUSHED",
        IMPLEMENTATION_BASELINE,
        IMPLEMENTATION_COMMIT,
        FW_BASELINE,
        "exact implementation surface: 20 files",
        "acceptance sync surface: exact seven files",
        "focused Flutter: 53 passed",
        "Flutter full: 408 passed",
        "real operator acceptance: NOT_EXECUTED / NOT_CLAIMED",
        "RT-5f4: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "RT-5: CURRENT / NOT_COMPLETED",
    ):
        require(combined, marker, "acceptance documents")

    contract = docs["docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md"]
    for marker in (
        "Status: **COMPLETED / ACCEPTED / PUSHED**",
        "## Acceptance record",
        "exact acceptance review: PASS",
        "blocking findings: 0",
        "This seven-file acceptance sync changes documentation and this gate only.",
    ):
        require(contract, marker, "accepted contract")

    readme = docs["README.md"]
    require(
        readme,
        "RT-5f3 is COMPLETED / ACCEPTED / PUSHED at "
        f"`{IMPLEMENTATION_COMMIT}` under the exact twenty-file contract.",
        "README accepted RT-5f3 summary",
    )
    require(
        readme,
        "  RT-5f4  NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / "
        "NOT_AUTHORIZED  Configured local end-to-end and audible soft-barge-in acceptance",
        "README RT-5f4 state",
    )
    require(
        docs["roadmap.md"],
        "Current implementation boundary: accepted exact twenty-file Flutter "
        "runtime/UI/tests plus docs/gate implementation; Backend, Framework, "
        "dependencies, lockfiles, platform manifests, versions, release metadata, "
        "and existing manual RT-4f4/RT-5e ownership remain unchanged.",
        "roadmap accepted implementation boundary",
    )
    require(
        docs["docs/DRC_v300_goal_checklist_small_commit.md"],
        "RT-5f4 NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "v3 checklist RT-5f4 state",
    )

    for forbidden in (
        "RT-5f3: IMPLEMENTED / AWAITING_REVIEW",
        "Current implementation state: IMPLEMENTED / AWAITING_REVIEW",
        "implementation commit: none",
        "commit/push: NOT_AUTHORIZED",
        "real audible soft-barge-in accepted",
        "provider hard cancel accepted",
        "release readiness: true",
    ):
        forbid(combined, forbidden, "acceptance documents")

    print("v300_rt5f3_status: completed-accepted-pushed")
    print("v300_rt5f3_exact_implementation_surface: 20")
    print("v300_rt5f3_exact_acceptance_sync_surface: 7")
    print("v300_rt5f3_default_off: True")
    print("v300_rt5f3_session_local_opt_in_default_off: True")
    print("v300_rt5f3_capture_phase_speech_activity_armed: False")
    print("v300_rt5f3_single_event_per_arming_generation: True")
    print("v300_rt5f3_dedicated_stream_and_voice_output_ownership: True")
    print("v300_rt5f3_home_screen_metadata_only: True")
    print("v300_rt5f3_backend_changed: False")
    print("v300_rt5f3_framework_changed: False")
    print("v300_rt5f3_dependency_changed: False")
    print("v300_rt5f3_real_operator_acceptance: not-executed-not-claimed")
    print("v300_rt5f4_authorization: ready-for-exact-contract-review-not-authorized")


if __name__ == "__main__":
    main()
