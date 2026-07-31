"""Validate the RT-5d fake-only HomeScreen voice-output controls candidate.

The default gate is commit-scoped to the accepted RT-5c baseline and validates
the exact ten-file working-tree surface. It is credential-free, network-free,
Backend-runtime-free, Framework-free, provider-free, and platform-audio-free.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "04b52a2e12d5f4dafd4e9a1172d628c6c58f9a70"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "app/lib/screens/home_screen.dart",
    "app/lib/services/realtime_terminal_voice_output_home_screen_binding.dart",
    "app/test/realtime_terminal_voice_output_home_screen_widget_test.dart",
    "docs/v300_rt5d_home_screen_voice_output_controls.md",
    "scripts/check_v300_rt5d_home_screen_voice_output_controls.py",
}

PROTECTED_PATHS = (
    "backend",
    "app/lib/main.dart",
    "app/lib/services/configured_realtime_text_stream_runtime.dart",
    "app/lib/services/backend_api_client.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/lib/services/realtime_terminal_voice_output_orchestrator.dart",
    "app/lib/services/voice_output_queue.dart",
    "app/lib/services/voice_output_audio_player.dart",
    "app/lib/services/audioplayers_voice_output_audio_engine.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
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


def _compact_code_marker(value: str) -> str:
    # Source checks validate code tokens, not formatter-selected commas.
    # Whitespace and commas are therefore ignored for these specific markers.
    return re.sub(r"[\s,]+", "", value)


def require_code(text: str, needle: str, label: str) -> None:
    require(
        _compact_code_marker(text),
        _compact_code_marker(needle),
        label,
    )


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
            f"RT-5d changed surface mismatch: {sorted(actual)}"
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
            raise AssertionError(f"RT-5d protected path changed: {relative}")


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
                f"Sensitive-looking value in RT-5d added content: {pattern}"
            )


def extract_method(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        character = source[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"Could not parse method body: {signature}")


def assert_source_contract() -> None:
    home = read("app/lib/screens/home_screen.dart")
    binding = read(
        "app/lib/services/realtime_terminal_voice_output_home_screen_binding.dart"
    )
    tests = read(
        "app/test/realtime_terminal_voice_output_home_screen_widget_test.dart"
    )
    contract = read("docs/v300_rt5d_home_screen_voice_output_controls.md")
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
        "typedef RealtimeTerminalVoiceOutputHomeScreenBindingFactory =",
        "abstract interface class RealtimeTerminalVoiceOutputHomeScreenBinding",
        "class OwnedRealtimeTerminalVoiceOutputHomeScreenBinding",
        "required this.orchestrator",
        "VoidCallback? disposeOwnedResources",
        "bool _isDisposed = false;",
        "if (_isDisposed)",
        "orchestrator.dispose();",
        "_disposeOwnedResources?.call();",
    ):
        require_code(binding, marker, f"RT-5d binding marker {marker}")

    for forbidden in (
        "BackendApiClient",
        "VoiceOutputAudioPlayerController",
        "package:http",
        "dart:io",
        "package:framework",
        "print(",
        "debugPrint(",
        "developer.log",
    ):
        forbid(binding, forbidden, f"RT-5d binding runtime token {forbidden}")

    for marker in (
        "this.realtimeTerminalVoiceOutputBindingFactory,",
        "final RealtimeTerminalVoiceOutputHomeScreenBindingFactory?",
        "RealtimeTerminalVoiceOutputHomeScreenBinding?",
        "_realtimeTerminalVoiceOutputOptedIn = false;",
        "_realtimeTerminalVoiceOutputProcessUiSequence",
        "_realtimeTerminalVoiceOutputFlushUiSequence",
        "_handleRealtimeTerminalVoiceOutputChanged",
        "_enqueueRealtimeTerminalVoiceOutput()",
        "_processNextRealtimeTerminalVoiceOutput()",
        "_flushRealtimeTerminalVoiceOutput()",
        "orchestrator.enqueueCompletedTerminal(controller.state)",
        "final result = await orchestrator.processNext();",
        "final result = await orchestrator.flush();",
        "++_realtimeTerminalVoiceOutputProcessUiSequence;",
        "realtime-terminal-voice-output-opt-in",
        "realtime-terminal-voice-output-enqueue-button",
        "realtime-terminal-voice-output-process-button",
        "realtime-terminal-voice-output-flush-button",
        "This fake RT-5 lifecycle does not control the existing Voice Output Demo player.",
        "_buildRealtimeTerminalVoiceOutputSection(context)",
        "configuration_failed",
    ):
        require_code(home, marker, f"RT-5d HomeScreen marker {marker}")

    controller_listener = extract_method(
        home,
        "void _handleRealtimeTextStreamControllerChanged()",
    )
    for forbidden in (
        "enqueueCompletedTerminal",
        "processNext",
        "_enqueueRealtimeTerminalVoiceOutput",
        "_processNextRealtimeTerminalVoiceOutput",
    ):
        forbid(
            controller_listener,
            forbidden,
            f"automatic voice action in realtime listener: {forbidden}",
        )

    rt5d_start = home.index(
        "RealtimeTerminalVoiceOutputOrchestrator?"
    )
    rt5d_end = home.index("Widget _buildDemoCapabilityRow(", rt5d_start)
    rt5d_source = home[rt5d_start:rt5d_end]
    for forbidden in (
        "_voiceOutputAudioPlayerController",
        "submitVoiceOutputDemoRequest",
        "widget.apiClient",
        "BackendApiClient",
        "AudioplayersVoiceOutputAudioEngine",
        "package:http",
        "Framework",
    ):
        forbid(
            rt5d_source,
            forbidden,
            f"RT-5d HomeScreen section runtime token {forbidden}",
        )

    dispose_method = extract_method(home, "void dispose()")
    for marker in (
        "_isDisposing = true;",
        "++_realtimeTerminalVoiceOutputProcessUiSequence;",
        "++_realtimeTerminalVoiceOutputFlushUiSequence;",
        "removeListener(",
        "_realtimeTerminalVoiceOutputBinding?.dispose();",
    ):
        require_code(dispose_method, marker, f"RT-5d dispose marker {marker}")

    init_method = extract_method(home, "void initState()")
    for marker in (
        "realtimeTextStreamController != null",
        "widget.realtimeTerminalVoiceOutputBindingFactory != null",
        "realtimeTerminalVoiceOutputBindingFactory",
        "addListener(_handleRealtimeTerminalVoiceOutputChanged)",
        "configuration_failed",
    ):
        require_code(init_method, marker, f"RT-5d init marker {marker}")

    for test_name in (
        "unconfigured binding keeps manual voice controls disabled",
        "binding factory runs once and opt-in defaults off",
        "stream completion and opt-in alone do not start voice output",
        "explicit enqueue does not automatically process",
        "duplicate completed terminal is visibly rejected",
        "one process click completes one fake queued item",
        "duplicate process tap is guarded synchronously",
        "queued items remain manual one by one",
        "manual flush clears pending and requests only local fake stop",
        "duplicate flush tap shares one local fake stop",
        "flush during synthesis prevents late playback and stale UI",
        "flush during playback ignores late playback terminal",
        "flush releases UI for a new generation while old future waits",
        "binding disposal is exactly once and late work is inert",
        "configuration failure is bounded and hides raw exception",
        "voice section never displays text IDs URI or raw errors",
    ):
        require(tests, test_name, f"RT-5d focused widget test {test_name}")

    for marker in (
        "engine.loadCalls, 0",
        "engine.playCalls, 0",
        "engine.stopCalls, 0",
        "fixture.disposeOwnedCalls, 1",
        "fixture.localStopCalls, 1",
        "find.textContaining('raw binding failure details'), findsNothing",
        "visibleText, isNot(contains(secretText))",
        "visibleText, isNot(contains(audioUri))",
    ):
        require_code(tests, marker, f"RT-5d safety assertion {marker}")

    combined_docs = contract + checklist + progress
    for marker in (
        "RT-5c: COMPLETED / ACCEPTED / PUSHED",
        "RT-5d: IMPLEMENTED / AWAITING_REVIEW",
        "RT-5e: NOT_STARTED / BLOCKED_PENDING_RT5D_ACCEPTANCE",
        "session-local",
        "off by default",
        "one explicit process action per queued item",
        "configuration_failed",
        "existing Voice Output Demo player",
        "new generation",
        "exact ten-file",
        "No Backend HTTP",
        "Framework real output flush",
        "provider hard cancel",
        "speech-triggered barge-in",
        "do not commit or push without explicit approval",
    ):
        require(combined_docs, marker, f"RT-5d documentation marker {marker}")

    for relative in EXPECTED_PATHS:
        require(contract, relative, f"RT-5d exact surface path {relative}")


def main() -> None:
    assert_repository_state()
    assert_changed_content_safe()
    assert_source_contract()

    print("v300_rt5d_home_screen_voice_output_status: implemented-awaiting-review")
    print("v300_rt5d_exact_change_surface: True")
    print("v300_rt5d_default_opt_in: False")
    print("v300_rt5d_explicit_enqueue_only: True")
    print("v300_rt5d_one_item_per_process_click: True")
    print("v300_rt5d_manual_flush_only: True")
    print("v300_rt5d_binding_dispose_idempotent: True")
    print("v300_rt5d_old_future_ui_invalidation: True")
    print("v300_rt5d_main_changed: False")
    print("v300_rt5d_backend_changed: False")
    print("v300_rt5d_framework_imported: False")
    print("v300_rt5d_existing_real_player_wired: False")
    print("v300_rt5d_real_synthesis: False")
    print("v300_rt5d_real_audio_playback: False")
    print("v300_rt5d_automatic_tts: False")
    print("v300_rt5d_provider_hard_cancel_claimed: False")
    print("v300_rt5e_authorization: blocked-pending-rt5d-acceptance")
    print(f"v300_rt5d_baseline_head: {DRC_BASELINE_HEAD}")


if __name__ == "__main__":
    main()
