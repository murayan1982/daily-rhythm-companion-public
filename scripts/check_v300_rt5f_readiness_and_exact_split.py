# Validate DRC v3.0.0 RT-5f0 readiness and exact split candidate.

from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "6272f613906317de3fecd899d4389ce0f13155e8"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5f_readiness_and_exact_split.md",
    "scripts/check_v300_rt5f_readiness_and_exact_split.py",
}

SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b",
)


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


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


def framework_root() -> Path:
    value = os.environ.get("FRAMEWORK_ROOT", "").strip()
    if not value:
        raise AssertionError(
            "FRAMEWORK_ROOT must point to the clean FW v5.4.0 checkout."
        )
    root = Path(value).expanduser().resolve()
    if not (root / ".git").exists():
        raise AssertionError("FRAMEWORK_ROOT is not a Git checkout.")
    return root


def framework_python(root: Path) -> Path:
    candidate = root / ".venv" / "Scripts" / "python.exe"
    return candidate if candidate.is_file() else Path(sys.executable)


def assert_repository_state() -> Path:
    actual_paths = changed_paths()
    if actual_paths != EXPECTED_PATHS:
        raise AssertionError(
            f"RT-5f0 changed surface mismatch: {sorted(actual_paths)}"
        )

    if run("git", "rev-parse", "HEAD", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")
    if run("git", "rev-parse", "origin/main", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC origin/main.")

    root = framework_root()
    if run("git", "rev-parse", "HEAD", cwd=root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW HEAD.")
    if run("git", "rev-list", "-n", "1", "v5.4.0", cwd=root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW v5.4.0 tag target.")
    if run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        cwd=root,
        capture=True,
    ):
        raise AssertionError("FW working tree is not clean.")
    return root


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
                f"Sensitive-looking value in RT-5f0 added content: {pattern}"
            )


def assert_private_real_stt_boundary() -> None:
    operator = read(
        "backend/app/services/framework_voice_input_openai_real_operator.py"
    )
    api = read("backend/app/api/voice_input_demo.py")
    rt3d3 = read("docs/v300_rt3d3_private_real_stt_operator_boundary.md")

    for marker in (
        "Public-safe result plus a private in-memory transcript handoff.",
        "def private_transcript(self) -> str:",
        "transcript_exposed=False",
        "_transcript=transcript",
    ):
        require(operator, marker, f"private real-STT marker {marker}")

    forbid(
        api,
        "framework_voice_input_openai_real_operator",
        "app-visible real-STT operator route",
    )
    forbid(api, "openai-real", "app-visible real-STT route path")
    require(
        rt3d3,
        "It does not expose a public API route",
        "RT-3d3 no-route marker",
    )
    require(
        rt3d3,
        "does not change the Flutter app",
        "RT-3d3 no-Flutter marker",
    )


def assert_flutter_input_and_handoff_boundary() -> None:
    main = read("app/lib/main.dart")
    home = read("app/lib/screens/home_screen.dart")
    model = read("app/lib/models/provider_neutral_transcript.dart")
    handoff = read(
        "app/lib/services/realtime_text_stream_transcript_handoff.dart"
    )
    record_adapter = read(
        "app/lib/services/record_microphone_capture_engine.dart"
    )

    require(main, "ConfiguredRealtimeTextStreamRuntime", "configured stream runtime")
    require(
        main,
        "ConfiguredRealtimeTerminalVoiceOutputRuntime",
        "configured voice-output runtime",
    )
    for token in (
        "RecordMicrophoneCaptureEngine",
        "MicrophoneCaptureController",
        "RealtimeTextStreamTranscriptHandoff",
        "ProviderNeutralTranscriptProvider",
    ):
        forbid(main, token, f"normal startup real-input wiring {token}")

    require(
        home,
        "RealtimeTextStreamTranscriptHandoffFactory?",
        "optional HomeScreen transcript handoff",
    )
    require(
        handoff,
        "typedef ProviderNeutralTranscriptProvider",
        "provider-neutral transcript provider",
    )
    require(
        handoff,
        "await _controller.start(inputText: normalizedTranscript);",
        "transcript-to-stream call",
    )
    require(
        model,
        "providerNeutralTranscriptMaxTextChars = 4096",
        "bounded transcript text",
    )
    require(
        model,
        "providerNeutralTranscriptMaxRememberedResultIds = 32",
        "bounded transcript dedup window",
    )

    for token in (
        "onAmplitudeChanged",
        "getAmplitude",
        "SpeechActivity",
        "speechOnset",
        "speech_onset",
    ):
        forbid(record_adapter, token, f"production speech-activity source {token}")
    for method in (
        "Future<void> start(",
        "Future<String?> stop()",
        "Future<void> cancel()",
        "Future<void> dispose()",
    ):
        require(record_adapter, method, f"record driver method {method}")
    forbid(home, "_handleSpeechBargeIn", "HomeScreen speech-triggered barge-in")


def assert_local_soft_interruption_primitives() -> None:
    queue = read("app/lib/services/voice_output_queue.dart")
    orchestrator = read(
        "app/lib/services/realtime_terminal_voice_output_orchestrator.dart"
    )
    runtime = read(
        "app/lib/services/configured_realtime_terminal_voice_output_runtime.dart"
    )
    stream = read("app/lib/services/realtime_text_stream_controller.dart")

    for marker in (
        "int _generation = 1;",
        "Future<VoiceOutputQueueFlushResult> flush()",
        "localPlaybackStopRequested",
        "await _stopLocalPlayback();",
    ):
        require(queue, marker, f"queue soft-interruption marker {marker}")
    for marker in (
        "int _operationEpoch = 0;",
        "Future<VoiceOutputQueueFlushResult> flush()",
        "++_operationEpoch;",
    ):
        require(orchestrator, marker, f"orchestrator invalidation marker {marker}")
    require(runtime, "await controller.stop();", "binding-owned local player stop")
    require(stream, "Future<void> cancel() async", "cooperative stream cancel")

    backend_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "backend" / "app").rglob("*.py")
    )
    for token in (
        "/demo/voice-output/cancel",
        "/demo/voice-output/flush",
        "cancel_synthesis",
        "provider_hard_cancel",
    ):
        forbid(backend_source, token, f"Backend/provider hard output control {token}")


def assert_framework_public_surface(root: Path) -> None:
    python = framework_python(root)
    source = r"""
from dataclasses import fields
import framework

required = (
    "RealtimeSessionInfo",
    "InterruptRequest",
    "OutputFlushRequest",
    "TTSQueueState",
    "BargeInPolicy",
    "BargeInDecision",
    "create_realtime_session",
)
missing = [name for name in required if not hasattr(framework, name)]
assert not missing, missing

defaults = {field.name: field.default for field in fields(framework.RealtimeSessionInfo)}
assert defaults["real_runtime_enabled"] is False
assert defaults["hard_cancel_supported"] is False
assert defaults["tts_queue_flush_supported"] is False

session = framework.create_realtime_session()
queue = session.get_tts_queue_state()
assert queue.supports_flush is False
assert queue.supports_provider_cancel is False
flush_result = session.flush_output(framework.OutputFlushRequest())
assert getattr(flush_result.outcome, "value", str(flush_result.outcome)) == "nothing_to_flush"
interrupt_result = session.interrupt(framework.InterruptRequest())
assert getattr(interrupt_result.outcome, "value", str(interrupt_result.outcome)) == "no_active_turn"
assert interrupt_result.provider_cancel_supported is False
assert interrupt_result.queue_flush_supported is False
policy = framework.BargeInPolicy.flush_output()
session.set_barge_in_policy(policy)
decision = session.decide_barge_in()
assert isinstance(decision, framework.BargeInDecision)
assert decision.should_flush_queue is True
session.close()
print("rt5f0_public_readiness_surface_ok")
"""
    output = run(str(python), "-c", source, cwd=root, capture=True)
    if output.strip() != "rt5f0_public_readiness_surface_ok":
        raise AssertionError(f"Unexpected FW RT-5f0 probe result: {output!r}")


def assert_planning_contract() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "contract": read("docs/v300_rt5f_readiness_and_exact_split.md"),
    }
    combined = "\n".join(sources.values())
    for marker in (
        "RT-5f0 IMPLEMENTED / AWAITING_REVIEW",
        "RT-5f1 NOT_STARTED / BLOCKED_PENDING_RT5F0_ACCEPTANCE / NOT_AUTHORIZED",
        "PARTIAL_READY_FOR_APP_VISIBLE_REAL_STT_AND_DRC_LOCAL_SOFT_BARGE_IN",
        "app-visible real-STT source exists: false",
        "speech-triggered DRC-local soft barge-in",
        "Backend HTTP hard cancellation: false",
        "provider synthesis hard cancellation: false",
        "FW real TTS queue flush: false",
        "Exact seven-file docs/test-only surface.",
        "RT-5f1 — App-visible provider-neutral real-STT source",
        "RT-5f2 — Fake-only integrated voice-turn and soft-barge-in coordinator",
        "RT-5f3 — Default-off HomeScreen and production speech-activity wiring",
        "RT-5f4 — Configured local end-to-end and audible soft-barge-in acceptance",
        DRC_BASELINE_HEAD,
        FW_HEAD,
    ):
        require(combined, marker, f"RT-5f0 planning marker {marker}")

    gate_source = read("scripts/check_v300_rt5f_readiness_and_exact_split.py")
    tree = ast.parse(gate_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("framework."):
                raise AssertionError("RT-5f0 gate imports a Framework internal module")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("framework."):
                    raise AssertionError("RT-5f0 gate imports a Framework internal module")
        elif isinstance(node, ast.Call):
            target = node.func
            name = ""
            if isinstance(target, ast.Name):
                name = target.id
            elif isinstance(target, ast.Attribute) and isinstance(
                target.value, ast.Name
            ):
                name = f"{target.value.id}.{target.attr}"
            if name in {
                "requests.get",
                "requests.post",
                "httpx.get",
                "httpx.post",
            }:
                raise AssertionError(
                    f"RT-5f0 gate performs network execution: {name}"
                )


def main() -> None:
    fw_root = assert_repository_state()
    assert_changed_content_safe()
    assert_private_real_stt_boundary()
    assert_flutter_input_and_handoff_boundary()
    assert_local_soft_interruption_primitives()
    assert_framework_public_surface(fw_root)
    assert_planning_contract()

    print("v300_rt5f0_readiness_status: implemented-awaiting-review")
    print("v300_rt5f0_exact_change_surface: True")
    print("v300_rt5f0_backend_runtime_changed: False")
    print("v300_rt5f0_flutter_runtime_changed: False")
    print("v300_rt5f0_existing_tests_changed: False")
    print("v300_rt5f0_app_visible_real_stt_source_exists: False")
    print("v300_rt5f0_transcript_handoff_boundary_exists: True")
    print("v300_rt5f0_normal_main_microphone_or_stt_wiring_exists: False")
    print("v300_rt5f0_speech_activity_source_exists: False")
    print("v300_rt5f0_local_soft_barge_in_primitives_exist: True")
    print("v300_rt5f0_fw_real_runtime_enabled: False")
    print("v300_rt5f0_fw_tts_queue_flush_supported: False")
    print("v300_rt5f0_fw_hard_cancel_supported: False")
    print("v300_rt5f0_network_execution: False")
    print("v300_rt5f0_provider_execution: False")
    print("v300_rt5f0_microphone_used: False")
    print("v300_rt5f0_audio_playback_executed: False")
    print("v300_rt5f0_transcript_created_or_exposed: False")
    print("v300_rt5f0_fw_internal_import: False")
    print("v300_rt5f0_final_claim: drc-local-soft-barge-in-only")
    print("v300_rt5f1_authorization: blocked-pending-rt5f0-acceptance")


if __name__ == "__main__":
    main()
