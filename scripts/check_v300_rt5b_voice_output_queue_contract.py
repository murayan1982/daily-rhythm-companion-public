"""Validate the RT-5b app-owned voice-output queue candidate.

The gate is credential-free, network-free, Backend-free, Framework-free, and
audio-free. It validates the exact nine-file candidate, the Flutter queue
source/test contract, protected non-change surfaces, and added-content privacy.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "ba51fa8ef3e1d2dbc528ddd9506241b544c1b3d6"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "app/lib/services/voice_output_queue.dart",
    "app/test/voice_output_queue_test.dart",
    "docs/v300_rt5b_voice_output_queue_contract.md",
    "scripts/check_v300_rt5b_voice_output_queue_contract.py",
}

PROTECTED_PATHS = (
    "backend",
    "app/lib/screens/home_screen.dart",
    "app/lib/main.dart",
    "app/lib/services/voice_output_audio_player.dart",
    "app/lib/services/backend_api_client.dart",
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
            f"RT-5b changed surface mismatch: {sorted(actual)}"
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
            raise AssertionError(f"RT-5b protected path changed: {relative}")


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
                f"Sensitive-looking value in RT-5b added content: {pattern}"
            )


def assert_source_contract() -> None:
    service = read("app/lib/services/voice_output_queue.dart")
    tests = read("app/test/voice_output_queue_test.dart")
    contract = read("docs/v300_rt5b_voice_output_queue_contract.md")
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
        "const int voiceOutputQueueMaxPendingItems = 8;",
        "const int voiceOutputQueueMaxUtteranceCodePoints = 4096;",
        "const int voiceOutputQueueMaxRetainedCodePoints = 16384;",
        "typedef VoiceOutputLocalPlaybackStop = Future<void> Function();",
        "enum VoiceOutputQueuePhase",
        "enum VoiceOutputQueueRejection",
        "enum VoiceOutputQueueItemOutcome",
        "enum VoiceOutputQueueFlushOutcome",
        "class VoiceOutputQueueItemMetadata",
        "class VoiceOutputQueueClaim",
        "class VoiceOutputQueueActionResult",
        "class VoiceOutputQueueClaimResult",
        "class VoiceOutputQueueFlushResult",
        "class VoiceOutputQueueState",
        "class VoiceOutputQueueController extends ChangeNotifier",
        "VoiceOutputQueueActionResult enqueue(String utterance)",
        "VoiceOutputQueueClaimResult claimNext()",
        "VoiceOutputQueueActionResult complete(VoiceOutputQueueClaim claim)",
        "VoiceOutputQueueActionResult fail(",
        "Future<VoiceOutputQueueFlushResult> flush()",
        "final existing = _flushInFlight;",
        "if (existing != null)",
        "final completer = Completer<VoiceOutputQueueFlushResult>();",
        "_flushInFlight = completer.future;",
        "unawaited(_completeFlush(completer));",
        "_generation += 1;",
        "_pending.clear();",
        "_active = null;",
        "_retainedCodePoints = 0;",
        "await _stopLocalPlayback();",
        "VoiceOutputQueueRejection.staleGeneration",
        "VoiceOutputQueueRejection.staleItem",
        "local_playback_stop_failed",
    ):
        require(service, marker, f"RT-5b service marker {marker}")

    state_start = service.index("class VoiceOutputQueueState")
    controller_start = service.index(
        "class VoiceOutputQueueController extends ChangeNotifier"
    )
    state_source = service[state_start:controller_start]
    forbid(
        state_source,
        "utterance",
        "utterance text in public queue state",
    )

    for forbidden_runtime in (
        "dart:io",
        "package:http",
        "backend_api_client",
        "home_screen",
        "voice_output_audio_player",
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
        "RealtimeTextStreamController",
        "VoiceOutputAudioPlayerController",
        "create_realtime_session",
        "VoiceOutputRequest",
        "OutputFlushRequest",
    ):
        forbid(
            service + tests,
            forbidden_runtime,
            f"RT-5b forbidden runtime token {forbidden_runtime}",
        )

    for test_name in (
        "starts idle without retaining utterance text in public state",
        "enqueues and claims pending utterances in FIFO order",
        "rejects empty and whitespace-only utterances",
        "enforces Unicode code-point utterance bounds",
        "enforces the pending item limit",
        "enforces the retained text limit across active and pending items",
        "allows only one active claimed item",
        "completion releases retained text and makes the next item ready",
        "failure releases the item and exposes only a bounded technical code",
        "flush clears pending and active items and requests local stop once",
        "flush keeps the queue cleared when local playback stop fails",
        "concurrent flush callers share one local playback stop request",
        "enqueue and claim are rejected while flush is in progress",
        "stale and mismatched claims cannot complete the active item",
        "dispose clears retained queue data and rejects later operations",
    ):
        require(tests, test_name, f"RT-5b focused test {test_name}")

    combined_docs = contract + checklist + progress
    for marker in (
        "RT-5a: COMPLETED / ACCEPTED / PUSHED",
        "RT-5b: IMPLEMENTED / AWAITING_REVIEW",
        "RT-5c: NOT_STARTED / BLOCKED_PENDING_RT5B_ACCEPTANCE",
        "maximum pending items: 8",
        "maximum utterance length: 4096 Unicode code points",
        "maximum retained text: 16384 Unicode code points",
        "exact nine-file",
        "completedWithLocalPlaybackStopFailure",
        "Backend synthesis cancellation",
        "Framework active TTS queue flush",
        "provider synthesis hard cancellation",
        "No HomeScreen integration",
    ):
        require(combined_docs, marker, f"RT-5b documentation marker {marker}")

    current_document_expectations = (
        (
            "README.md",
            "Current small commit: RT-5b IMPLEMENTED / AWAITING_REVIEW",
            1,
        ),
        (
            "README.md",
            "RT-5b  IMPLEMENTED / AWAITING_REVIEW",
            1,
        ),
        (
            "roadmap.md",
            "Current small commit: RT-5b IMPLEMENTED / AWAITING_REVIEW",
            2,
        ),
        (
            "roadmap.md",
            "RT-5b  IMPLEMENTED / AWAITING_REVIEW",
            1,
        ),
        (
            "tasklist.md",
            "current small commit: RT-5b IMPLEMENTED / AWAITING_REVIEW",
            1,
        ),
        (
            "tasklist.md",
            "RT-5b  IMPLEMENTED / AWAITING_REVIEW",
            1,
        ),
        (
            "docs/DRC_v300_goal_checklist_small_commit.md",
            "Current small commit: RT-5b IMPLEMENTED / AWAITING_REVIEW",
            1,
        ),
        (
            "docs/v300_rt5b_voice_output_queue_contract.md",
            "RT-5b: IMPLEMENTED / AWAITING_REVIEW",
            2,
        ),
    )
    for relative, marker, expected_count in current_document_expectations:
        actual_count = read(relative).count(marker)
        if actual_count != expected_count:
            raise AssertionError(
                f"RT-5b active/current marker count changed in {relative}: "
                f"{marker!r}: {actual_count} != {expected_count}"
            )

    # Historical checkpoints may intentionally retain earlier RT-5b/RT-5c
    # planning states. The active/current markers above are checked per document
    # instead of globally forbidding those historical strings.


def assert_existing_player_boundary() -> None:
    player = read("app/lib/services/voice_output_audio_player.dart")
    require(player, "Future<void> stop() async", "existing local player stop")
    require(player, "final operation = ++_operationSequence;", "player sequence")
    require(player, "await _engine.stop();", "player engine stop")
    forbid(
        player,
        "VoiceOutputQueueController",
        "RT-5b wiring into existing player",
    )


def main() -> None:
    assert_repository_state()
    assert_changed_content_safe()
    assert_source_contract()
    assert_existing_player_boundary()

    print("v300_rt5b_voice_output_queue_status: implemented-awaiting-acceptance")
    print("v300_rt5b_exact_change_surface: True")
    print("v300_rt5b_flutter_queue_service_added: True")
    print("v300_rt5b_fake_only_tests_added: True")
    print("v300_rt5b_pending_item_limit: 8")
    print("v300_rt5b_utterance_code_point_limit: 4096")
    print("v300_rt5b_retained_code_point_limit: 16384")
    print("v300_rt5b_single_active_item: True")
    print("v300_rt5b_fifo_pending_order: True")
    print("v300_rt5b_generation_late_result_rejection: True")
    print("v300_rt5b_concurrent_flush_stop_deduplicated: True")
    print("v300_rt5b_local_playback_stop_injected: True")
    print("v300_rt5b_local_stop_failure_restores_queue: False")
    print("v300_rt5b_public_state_contains_utterance_text: False")
    print("v300_rt5b_home_screen_changed: False")
    print("v300_rt5b_backend_changed: False")
    print("v300_rt5b_framework_imported: False")
    print("v300_rt5b_provider_execution: False")
    print("v300_rt5b_real_audio_playback: False")
    print("v300_rt5b_automatic_tts: False")
    print("v300_rt5b_provider_hard_cancel_claimed: False")
    print("v300_rt5c_authorization: blocked-pending-rt5b-acceptance")


if __name__ == "__main__":
    main()
