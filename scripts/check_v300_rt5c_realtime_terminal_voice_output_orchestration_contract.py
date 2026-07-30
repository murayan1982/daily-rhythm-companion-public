"""Validate the RT-5c fake-only terminal voice-output orchestration candidate.

The default gate is commit-scoped and validates the exact nine-file working-tree
surface against the accepted RT-5b baseline. It is credential-free,
network-free, Backend-runtime-free, Framework-free, provider-free, and
platform-audio-free.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "5fcac869f81e1070e854550f4376353e109905e5"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "app/lib/services/realtime_terminal_voice_output_orchestrator.dart",
    "app/test/realtime_terminal_voice_output_orchestrator_test.dart",
    "docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md",
    "scripts/check_v300_rt5c_realtime_terminal_voice_output_orchestration_contract.py",
}

PROTECTED_PATHS = (
    "backend",
    "app/lib/screens/home_screen.dart",
    "app/lib/main.dart",
    "app/lib/services/backend_api_client.dart",
    "app/lib/services/voice_output_audio_player.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/lib/services/voice_output_queue.dart",
    "app/pubspec.yaml",
    "release_notes",
)

SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)"
    r"\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)"
    r"\.\d{1,3}\.\d{1,3}\b",
)


def run(*args: str, capture: bool = False, check: bool = True) -> str:
    completed = subprocess.run(
        list(args),
        cwd=ROOT,
        check=check,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def changed_paths() -> set[str]:
    output = run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        capture=True,
    )
    paths: set[str] = set()
    for line in output.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def assert_repository_state() -> None:
    actual = changed_paths()
    if actual != EXPECTED_PATHS:
        raise AssertionError(
            f"RT-5c changed surface mismatch: {sorted(actual)}"
        )

    if run("git", "rev-parse", "HEAD", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")
    if run("git", "rev-parse", "origin/main", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC origin/main.")

    for relative in PROTECTED_PATHS:
        completed = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=ROOT,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(f"RT-5c protected path changed: {relative}")


def assert_changed_content_safe() -> None:
    diff = run(
        "git",
        "diff",
        "HEAD",
        "--unified=0",
        "--",
        *sorted(EXPECTED_PATHS),
        capture=True,
    )
    added_lines = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]

    untracked = set(
        run(
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            capture=True,
        ).splitlines()
    )
    for relative in sorted(EXPECTED_PATHS & untracked):
        added_lines.append(read(relative))

    added_text = "\n".join(added_lines)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added_text):
            raise AssertionError(
                f"Sensitive-looking value in RT-5c added content: {pattern}"
            )


def assert_source_contract() -> None:
    service = read(
        "app/lib/services/realtime_terminal_voice_output_orchestrator.dart"
    )
    tests = read(
        "app/test/realtime_terminal_voice_output_orchestrator_test.dart"
    )
    contract = read(
        "docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md"
    )
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    progress = "\n".join(
        read(relative)
        for relative in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
        )
    )

    for marker in (
        "const int realtimeTerminalVoiceOutputMaxAudioUriCodePoints = 2048;",
        "const int realtimeTerminalVoiceOutputMaxRememberedTerminals = 32;",
        "typedef RealtimeTerminalVoiceSynthesis =",
        "typedef RealtimeTerminalVoicePlayback =",
        "enum RealtimeTerminalVoiceOutputPhase",
        "enum RealtimeTerminalVoiceOutputEnqueueRejection",
        "enum RealtimeTerminalVoiceSynthesisOutcome",
        "enum RealtimeTerminalVoicePlaybackOutcome",
        "enum RealtimeTerminalVoiceOutputProcessOutcome",
        "class RealtimeTerminalVoiceSynthesisRequest",
        "class RealtimeTerminalVoiceSynthesisResult",
        "class RealtimeTerminalVoicePlaybackResult",
        "class RealtimeTerminalVoiceOutputEnqueueResult",
        "class RealtimeTerminalVoiceOutputProcessResult",
        "class RealtimeTerminalVoiceOutputState",
        "class RealtimeTerminalVoiceOutputOrchestrator extends ChangeNotifier",
        "enqueueCompletedTerminal(",
        "Future<RealtimeTerminalVoiceOutputProcessResult> processNext()",
        "Future<VoiceOutputQueueFlushResult> flush()",
        "final Set<_CompletedTerminalKey> _rememberedTerminals",
        "_rememberedTerminals.remove(_rememberedTerminals.first);",
        "final epoch = ++_operationEpoch;",
        "_activeProcessToken = null;",
        "queueState.generation == claim.item.generation",
        "queueState.activeItem?.itemId == claim.item.itemId",
        "final source = _validatedAudioUri",
        "playbackFuture = _playToTerminal(source);",
        "_queue.complete(claim)",
        "_queue.fail(claim, technicalCode: technicalCode)",
        "unawaited(_queue.flush()",
        "synthesis_rejected",
        "synthesis_request_failed",
        "invalid_audio_uri",
        "playback_failed",
        "playback_expired",
        "playback_stopped",
        "playback_lifecycle_failed",
    ):
        require(service, marker, f"RT-5c service marker {marker}")

    state_start = service.index("class RealtimeTerminalVoiceOutputState")
    controller_start = service.index(
        "class RealtimeTerminalVoiceOutputOrchestrator extends ChangeNotifier"
    )
    state_source = service[state_start:controller_start]
    for private_field in (
        "utterance",
        "outputText",
        "sessionId",
        "turnId",
        "opaqueAudioUri",
        "Uri?",
    ):
        forbid(
            state_source,
            private_field,
            f"private field in public orchestrator state: {private_field}",
        )

    for forbidden_runtime in (
        "dart:io",
        "package:http",
        "backend_api_client",
        "BackendApiClient",
        "home_screen",
        "HomeScreen",
        "voice_output_audio_player",
        "VoiceOutputAudioPlayerController",
        "audioplayers",
        "import 'package:framework",
        "import 'framework",
        "File(",
        "Directory(",
        "SharedPreferences",
        "print(",
        "debugPrint(",
        "developer.log",
        "submitVoiceOutputDemoRequest",
        "create_realtime_session",
        "VoiceOutputRequest",
        "OutputFlushRequest",
    ):
        forbid(
            service + tests,
            forbidden_runtime,
            f"RT-5c forbidden runtime token {forbidden_runtime}",
        )

    for test_name in (
        "starts idle without retaining terminal text in public state",
        "requires explicit enqueue and one explicit process call",
        "rejects non-completed and inconsistent terminal snapshots",
        "deduplicates only after queue enqueue succeeds",
        "keeps bounded completed-terminal deduplication across flush",
        "processes FIFO items one per explicit process call",
        "rejects concurrent processing without replacing active work",
        "maps synthesis rejection failure and exception to bounded codes",
        "accepts only bounded absolute opaque HTTP audio URIs",
        "completes the queue only for completed playback terminal",
        "maps playback lifecycle exception without exposing it",
        "flush from synthesizing notification prevents synthesis start",
        "flush during synthesis prevents late playback start",
        "flush during playback requests one stop and ignores late terminal",
        "flushing notification exposes an already-invalidated queue",
        "publishes the in-flight flush before flushing notification",
        "concurrent flush callers share one local stop request",
        "flush releases the process slot for a new generation",
        "flush stop failure never restores pending or active items",
        "dispose invalidates late work and rejects later operations",
        "public state and results do not expose text IDs URI or raw errors",
        "returns typed empty-queue result without synthesis",
    ):
        require(tests, test_name, f"RT-5c focused test {test_name}")

    combined_docs = contract + checklist + progress
    for marker in (
        "RT-5a: COMPLETED / ACCEPTED / PUSHED",
        "RT-5b: COMPLETED / ACCEPTED / PUSHED",
        "RT-5c: IMPLEMENTED / AWAITING_REVIEW",
        "RT-5d: NOT_STARTED / BLOCKED_PENDING_RT5C_ACCEPTANCE",
        "explicit",
        "one queue item",
        "2048 Unicode code points",
        "32 entries",
        "flush during synthesis cannot start late playback",
        "new-generation work may start after flush",
        "No HomeScreen integration",
        "Backend synthesis cancellation",
        "Framework real output flush",
        "provider hard cancellation",
        "speech-triggered barge-in",
        "exact nine-file",
        "do not commit or push without explicit approval",
    ):
        require(combined_docs, marker, f"RT-5c documentation marker {marker}")

    for relative in EXPECTED_PATHS:
        require(
            contract,
            relative,
            f"RT-5c exact surface path {relative}",
        )


def main() -> None:
    assert_repository_state()
    assert_changed_content_safe()
    assert_source_contract()

    print("v300_rt5c_realtime_terminal_voice_output_status: implemented-awaiting-review")
    print("v300_rt5c_exact_change_surface: True")
    print("v300_rt5c_explicit_enqueue_only: True")
    print("v300_rt5c_one_item_per_process_call: True")
    print("v300_rt5c_completed_terminal_dedup_limit: 32")
    print("v300_rt5c_audio_uri_code_point_limit: 2048")
    print("v300_rt5c_generation_and_epoch_late_result_rejection: True")
    print("v300_rt5c_concurrent_flush_stop_deduplicated: True")
    print("v300_rt5c_home_screen_changed: False")
    print("v300_rt5c_backend_changed: False")
    print("v300_rt5c_framework_imported: False")
    print("v300_rt5c_real_synthesis: False")
    print("v300_rt5c_real_audio_playback: False")
    print("v300_rt5c_automatic_tts: False")
    print("v300_rt5c_provider_hard_cancel_claimed: False")
    print("v300_rt5d_authorization: blocked-pending-rt5c-acceptance")
    print(f"v300_rt5c_baseline_head: {DRC_BASELINE_HEAD}")


if __name__ == "__main__":
    main()
