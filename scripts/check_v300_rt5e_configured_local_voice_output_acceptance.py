"""Validate the RT-5e configured local voice-output implementation candidate.

The default mode is bound to the accepted RT-5d baseline and exact thirteen-file
working-tree surface. It is credential-free, network-free, Backend-runtime-free,
Framework-runtime-free, provider-free, and platform-audio-free.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "ead613d27cd32c625b1b0a07eef96387027d70d5"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5e_configured_local_voice_output_acceptance.md",
    "scripts/check_v300_rt5e_configured_local_voice_output_acceptance.py",
    "app/lib/main.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/services/configured_realtime_terminal_voice_output_runtime.dart",
    "app/test/configured_realtime_terminal_voice_output_runtime_test.dart",
    "app/test/main_realtime_terminal_voice_output_wiring_widget_test.dart",
    "app/test/realtime_terminal_voice_output_home_screen_widget_test.dart",
}

PROTECTED_PATHS = (
    "backend",
    "app/lib/models/voice_output_demo.dart",
    "app/lib/services/backend_api_client.dart",
    "app/lib/services/realtime_terminal_voice_output_home_screen_binding.dart",
    "app/lib/services/realtime_terminal_voice_output_orchestrator.dart",
    "app/lib/services/voice_output_queue.dart",
    "app/lib/services/voice_output_audio_player.dart",
    "app/lib/services/audioplayers_voice_output_audio_engine.dart",
    "app/lib/services/configured_realtime_text_stream_runtime.dart",
    "app/lib/services/realtime_text_stream_controller.dart",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "app/android",
    "app/ios",
    "app/windows",
    "app/web",
    "release_notes",
)

SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)"
    r"\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)"
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


def compact(value: str) -> str:
    return re.sub(r"[\s,]+", "", value)


def require_code(text: str, needle: str, label: str) -> None:
    require(compact(text), compact(needle), label)


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


def assert_repository_state(*, snapshot: bool) -> None:
    actual = changed_paths()
    if actual != EXPECTED_PATHS:
        raise AssertionError(
            f"RT-5e changed surface mismatch: {sorted(actual)}"
        )

    if not snapshot:
        if run("git", "rev-parse", "HEAD", capture=True) != DRC_BASELINE_HEAD:
            raise AssertionError("Unexpected DRC baseline HEAD.")
        if (
            run("git", "rev-parse", "origin/main", capture=True)
            != DRC_BASELINE_HEAD
        ):
            raise AssertionError("Unexpected DRC origin/main.")

    for relative in PROTECTED_PATHS:
        completed = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=ROOT,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(f"RT-5e protected path changed: {relative}")

    completed = subprocess.run(
        ["git", "-c", "core.whitespace=cr-at-eol", "diff", "--check"],
        cwd=ROOT,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError("git diff --check failed")


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
                f"Sensitive-looking value in RT-5e added content: {pattern}"
            )


def assert_source_contract() -> None:
    main = read("app/lib/main.dart")
    home = read("app/lib/screens/home_screen.dart")
    runtime = read(
        "app/lib/services/configured_realtime_terminal_voice_output_runtime.dart"
    )
    runtime_tests = read(
        "app/test/configured_realtime_terminal_voice_output_runtime_test.dart"
    )
    main_tests = read(
        "app/test/main_realtime_terminal_voice_output_wiring_widget_test.dart"
    )
    home_tests = read(
        "app/test/realtime_terminal_voice_output_home_screen_widget_test.dart"
    )
    contract = read(
        "docs/v300_rt5e_configured_local_voice_output_acceptance.md"
    )
    progress = "\n".join(
        read(relative)
        for relative in (
            "README.md",
            "roadmap.md",
            "tasklist.md",
            "scripts/README.md",
            "docs/DRC_v300_goal_checklist_small_commit.md",
        )
    )

    for marker in (
        "ConfiguredRealtimeTerminalVoiceOutputRuntime.fromEnvironment(",
        "realtimeTerminalVoiceOutputBindingFactory:",
        "configuredVoiceOutputRuntime.buildBindingFactory()",
        "final RealtimeTerminalVoiceOutputHomeScreenBindingFactory?",
    ):
        require_code(main, marker, f"main wiring marker {marker}")

    for marker in (
        "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT",
        "defaultValue: false",
        "class ConfiguredRealtimeTerminalVoiceOutputRuntime",
        "RealtimeTerminalVoiceOutputHomeScreenBindingFactory? buildBindingFactory()",
        "if (!enabled || !_isValidBackendBaseUrl(configuredBaseUrl))",
        "VoiceOutputAudioPlayerController(",
        "engine: _audioEngineFactory()",
        "VoiceOutputQueueController(",
        "stopLocalPlayback: terminalPlayback.stop",
        "RealtimeTerminalVoiceOutputOrchestrator(",
        "synthesize: synthesis.call",
        "playToTerminal: terminalPlayback.playToTerminal",
        "apiClient.submitVoiceOutputDemoRequest(",
        "clientEventId: configuredRealtimeTerminalVoiceOutputClientEventId",
        "outputMode: 'tts'",
        "textContent: request.utterance",
        "audioFormat: 'mp3'",
        "utterancePurpose: configuredRealtimeTerminalVoiceOutputPurpose",
        "framework.create_voice_output_session().create_output",
        "response.audioArtifactRef == null",
        "response.audioHandoffKind == 'url'",
        "response.audioFormat == 'mp3'",
        r"^/demo/voice-output/audio/[0-9a-f]{32}$",
        "controller.addListener(_handleStateChanged)",
        "await controller.stop()",
        "controller.removeListener(_handleStateChanged)",
        "terminalPlayback.dispose()",
        "queue.dispose()",
    ):
        require_code(runtime, marker, f"configured runtime marker {marker}")

    for forbidden in (
        "elevenlabs",
        "framework.audio._provider_adapter",
        "package:framework",
        "dart:io",
        "print(",
        "debugPrint(",
        "developer.log",
        "processNext();\n      processNext()",
        "while (",
    ):
        forbid(runtime, forbidden, f"configured runtime forbidden token {forbidden}")

    for marker in (
        "RT-5 binding-owned lifecycle",
        "Enable manual voice output",
        "Flush app queue / local playback",
        "Local playback stop requested",
        "Local playback stop succeeded",
        "owns a separate local player",
    ):
        require(home, marker, f"HomeScreen RT-5e wording {marker}")

    for forbidden in (
        "RT-5 fake/in-memory lifecycle only",
        "Enable manual fake voice output",
        "Local fake stop requested",
        "Local fake stop succeeded",
        "This fake RT-5 lifecycle",
    ):
        forbid(home, forbidden, f"obsolete HomeScreen wording {forbidden}")

    for marker in (
        "disabled runtime returns no binding factory",
        "binding construction starts no synthesis or playback",
        "one explicit process uses exact Backend contract and dedicated player",
        "wrong FW API name is rejected before local playback",
        "absolute or non-opaque audio handoff is rejected before playback",
        "flush clears pending work and stops only the dedicated player",
        "binding dispose is idempotent",
    ):
        require(runtime_tests, marker, f"runtime test marker {marker}")

    for marker in (
        "default app leaves RT-5 voice output unconfigured",
        "configured factories build one ready default-off binding",
        "binding factory is not called without realtime stream",
        "app teardown disposes the configured binding once",
    ):
        require(main_tests, marker, f"main widget test marker {marker}")

    for marker in (
        "Enable manual voice output",
        "Local playback stop requested: true",
        "Local playback stop succeeded: true",
    ):
        require(home_tests, marker, f"HomeScreen test marker {marker}")

    for marker in (
        "IMPLEMENTED / AWAITING_REVIEW",
        "DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT=false",
        "framework.create_voice_output_session().create_output",
        "automatic terminal-to-TTS",
        "provider synthesis hard cancellation",
        "Framework real queue flush",
        "speech-triggered barge-in",
        "Exact implementation surface",
        "Explicit non-change surface",
        "Stop before commit and push",
        "RT-5e acceptance does not authorize RT-5f",
    ):
        require(contract, marker, f"RT-5e contract marker {marker}")

    for marker in (
        "RT-5e IMPLEMENTED / AWAITING_REVIEW",
        "configured local Backend/FW one-shot synthesis",
        "implementation commit: not committed",
        "do not commit or push without explicit approval",
    ):
        require(progress, marker, f"progress marker {marker}")

    for forbidden in (
        "RT-5e COMPLETED / ACCEPTED",
        "RT-5f CURRENT",
        "provider hard cancel accepted",
        "Framework real flush accepted",
        "barge-in accepted",
    ):
        forbid(progress, forbidden, f"premature progress claim {forbidden}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the exact RT-5e implementation candidate"
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help=(
            "Skip only the canonical commit-SHA checks when validating an "
            "extracted handoff snapshot; exact surface and source checks remain."
        ),
    )
    args = parser.parse_args()

    assert_repository_state(snapshot=args.snapshot)
    assert_changed_content_safe()
    assert_source_contract()

    print("v300_rt5e_configured_local_voice_output_status: candidate-valid")
    print("v300_rt5e_default_enabled: False")
    print("v300_rt5e_automatic_enqueue: False")
    print("v300_rt5e_automatic_queue_drain: False")
    print("v300_rt5e_backend_route_changed: False")
    print("v300_rt5e_framework_source_changed: False")
    print("v300_rt5e_existing_demo_player_shared: False")
    print("v300_rt5e_provider_hard_cancel_claimed: False")
    print("v300_rt5e_framework_real_flush_claimed: False")
    print("v300_rt5e_barge_in_claimed: False")
    print("v300_rt5e_real_stt_to_tts_claimed: False")
    print("v300_rt5e_commit_authorized: False")
    print("v300_rt5e_push_authorized: False")


if __name__ == "__main__":
    main()
