from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HEAD = "c538dc89c2aa9780cd3014aa4ba11c17a9e378e6"
EXPECTED_FILES = {
    "app/lib/services/integrated_voice_turn_coordinator.dart",
    "app/test/integrated_voice_turn_coordinator_test.dart",
    "docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md",
    "scripts/check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py",
}


def run_git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise RuntimeError(f"{label} is missing marker: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise RuntimeError(f"{label} contains forbidden marker: {marker}")


def changed_files() -> set[str]:
    tracked = {
        line.strip()
        for line in run_git("diff", "HEAD", "--name-only").splitlines()
        if line.strip()
    }
    untracked = {
        line.strip()
        for line in run_git("ls-files", "--others", "--exclude-standard").splitlines()
        if line.strip()
    }
    return tracked | untracked


def main() -> None:
    head = run_git("rev-parse", "HEAD").strip()
    if head != EXPECTED_HEAD:
        raise RuntimeError(f"unexpected DRC HEAD: {head}")

    actual = changed_files()
    if actual != EXPECTED_FILES:
        raise RuntimeError(
            "RT-5f2 corrective exact change surface mismatch\n"
            f"expected={sorted(EXPECTED_FILES)}\nactual={sorted(actual)}"
        )

    source = (ROOT / "app/lib/services/integrated_voice_turn_coordinator.dart").read_text(
        encoding="utf-8"
    )
    tests = (ROOT / "app/test/integrated_voice_turn_coordinator_test.dart").read_text(
        encoding="utf-8"
    )
    contract = (
        ROOT / "docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md"
    ).read_text(encoding="utf-8")
    progress = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
        )
    )

    for marker in (
        "class IntegratedVoiceTurnCoordinator extends ChangeNotifier",
        "IntegratedVoiceTurnCaptureCompletion",
        "IntegratedVoiceTurnStaging",
        "RealtimeTextStreamTranscriptHandoff",
        "RealtimeTextStreamController",
        "RealtimeTerminalVoiceOutputOrchestrator",
        "integratedVoiceTurnMaxSpeechEventIdCodePoints = 128",
        "integratedVoiceTurnMaxRememberedSpeechEventIds = 32",
        "localStopRetryRequired",
        "_operationEpoch",
        "_rememberedSpeechEventIds",
        "requestCooperativeCancel: true",
        "_voiceOutput.flush()",
        "_hasExclusiveVoiceOutputAccess()",
        "voiceState.pendingCount == 0",
        "voiceState.activeItem == null",
        "!voiceState.isProcessing",
        "RealtimeTerminalVoiceOutputPhase.flushing",
        "RealtimeTerminalVoiceOutputPhase.disposed",
        "integrated_voice_turn_voice_output_busy",
        "integrated_voice_turn_voice_output_not_exclusive",
        "final enqueuedItem = enqueueResult.item!",
        "_sameVoiceOutputItem(processResult.item, enqueuedItem)",
        "actual.itemId == expected.itemId",
        "actual.generation == expected.generation",
        "integrated_voice_turn_voice_output_item_mismatch",
    ):
        require(source, marker, "coordinator source")

    if source.count("if (!_hasExclusiveVoiceOutputAccess())") < 3:
        raise RuntimeError(
            "coordinator source must check exclusive voice output at start, "
            "before phase notification, and immediately after phase listeners"
        )

    for forbidden in (
        "package:http",
        "dart:io",
        "BackendProviderNeutralTranscriptProvider",
        "BackendVoiceInputStagingConsumer",
        "RecordMicrophoneCaptureEngine",
        "OpenAI",
        "framework/",
    ):
        forbid(source, forbidden, "coordinator source")

    for marker in (
        "happy-path full fake voice turn completes exactly once",
        "speech during capture makes a late capture result inert",
        "speech during staging makes a late staging result inert",
        "speech during transcript acquisition makes late STT inert",
        "speech during stream requests one cooperative cancel",
        "speech during synthesis permits a new turn before old Future completion",
        "speech during playback permits new playback before old Future completion",
        "duplicate speech is rejected and concurrent distinct events coalesce",
        "local playback stop failure blocks turns until speech retry",
        "stream cancel request failure does not revive old work",
        "cancelled stream terminal never reaches TTS",
        "dispose during interruption makes late completion inert",
        "dispose during capture makes late capture inert",
        "dispose during staging makes late staging inert",
        "dispose during transcript acquisition makes late STT inert",
        "dispose during stream makes a late terminal inert",
        "dispose during synthesis makes a late synthesis result inert",
        "dispose during playback makes a late playback result inert",
        "public state retains no transcript IDs text URI or raw error",
        "pre-existing pending voice output blocks turn before capture",
        "pre-existing active synthesis blocks turn before capture",
        "voice output becoming non-exclusive before terminal enqueue rejects turn",
        "voice-output phase listener cannot enqueue between exclusivity check and enqueue",
        "processed voice-output item must match current terminal item",
        "_MismatchedVoiceOutputOrchestrator",
    ):
        require(tests, marker, "focused Flutter tests")

    for marker in (
        "RT-5f2: IMPLEMENTED / CORRECTIVE_PATCH_AWAITING_REVIEW",
        "RT-5f2 implementation commit: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6",
        "RT-5f2 corrective patch baseline: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6",
        "fake-only integrated voice-turn coordinator",
        "fake-only DRC-local soft-barge-in behavior",
        "Exclusive voice-output ownership",
        "after synchronous coordinator phase listeners return",
        "same `itemId` and `generation`",
        "exact four-file surface",
        "corrective patch commit/push: not authorized",
        "RT-5f3: BLOCKED_PENDING_RT5F2_ACCEPTANCE / NOT_AUTHORIZED",
    ):
        require(contract, marker, "RT-5f2 contract")

    # The five progress documents are intentionally outside the corrective
    # surface. Their implementation-candidate markers remain unchanged until a
    # separate accepted docs sync is authorized.
    for marker in (
        "RT-5f2 IMPLEMENTED / AWAITING_REVIEW",
        "implementation commit: none",
        "do not commit or push without explicit approval",
        "RT-5f3 BLOCKED_PENDING_RT5F2_ACCEPTANCE / NOT_AUTHORIZED",
    ):
        require(progress, marker, "unchanged progress documents")

    print("v300_rt5f2_status: corrective-patch-awaiting-review")
    print("v300_rt5f2_corrective_baseline: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6")
    print("v300_rt5f2_exact_corrective_surface: True")
    print("v300_rt5f2_fake_only: True")
    print("v300_rt5f2_operation_epoch_invalidation: True")
    print("v300_rt5f2_voice_output_exclusive_before_capture: True")
    print("v300_rt5f2_voice_output_exclusive_before_enqueue: True")
    print("v300_rt5f2_voice_output_exclusive_after_phase_notification: True")
    print("v300_rt5f2_processed_item_identity_required: True")
    print("v300_rt5f2_duplicate_speech_bound: 32")
    print("v300_rt5f2_speech_event_id_max_code_points: 128")
    print("v300_rt5f2_cooperative_stream_cancel_only: True")
    print("v300_rt5f2_local_player_stop_only: True")
    print("v300_rt5f2_existing_runtime_files_changed: False")
    print("v300_rt5f2_main_changed: False")
    print("v300_rt5f2_home_screen_changed: False")
    print("v300_rt5f2_backend_changed: False")
    print("v300_rt5f2_network_execution: False")
    print("v300_rt5f2_provider_execution: False")
    print("v300_rt5f2_microphone_used: False")
    print("v300_rt5f2_audio_playback_executed: False")
    print("v300_rt5f3_authorization: blocked-pending-rt5f2-acceptance")


if __name__ == "__main__":
    main()
