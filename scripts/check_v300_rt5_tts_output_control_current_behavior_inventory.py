# Validate DRC v3.0.0 RT-5a TTS output-control current behavior inventory.

from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "2b4364f8777cd95a686104dd1868ebcfe72064c9"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt5_tts_output_control_current_behavior_inventory.md",
    "scripts/check_v300_rt5_tts_output_control_current_behavior_inventory.py",
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
            f"RT-5a changed surface mismatch: {sorted(actual_paths)}"
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
                f"Sensitive-looking value in RT-5a added content: {pattern}"
            )


def assert_drc_backend_behavior() -> None:
    route = read("backend/app/api/voice_output_demo.py")
    service = read("backend/app/services/voice_output_demo_service.py")
    adapter = read("backend/app/services/framework_voice_output_adapter.py")
    realtime_route = read("backend/app/api/realtime_text.py")
    realtime_service = read(
        "backend/app/services/realtime_text_stream_service.py"
    )
    realtime_adapter = read(
        "backend/app/services/framework_realtime_text_stream_adapter.py"
    )
    main = read("backend/app/main.py")

    require(
        route,
        '@router.post("/demo/voice-output"',
        "one-shot voice-output POST route",
    )
    require(
        route,
        '@router.get("/demo/voice-output/audio/{artifact_id}"',
        "opaque audio artifact route",
    )
    forbid(route, "voice-output/cancel", "voice-output cancel route")
    forbid(route, "voice-output/flush", "voice-output flush route")
    forbid(route, "tts/queue", "TTS queue route")

    require(
        service,
        "if not status.real_tts_enabled:",
        "default-off real-TTS guard",
    )
    require(
        service,
        "adapter.synthesize(",
        "guarded one-shot Framework synthesis call",
    )
    require(
        service,
        'playback_status = "requires_operator_confirmation" if accepted else "not_started"',
        "explicit playback confirmation boundary",
    )
    require(
        service,
        "publish_framework_artifact(",
        "DRC opaque artifact publication",
    )
    require(
        service,
        "audio_artifact_ref = None",
        "private Framework artifact suppression",
    )
    forbid(service, "cancel_synthesis", "Backend synthesis cancellation")
    forbid(service, "flush_output", "Backend output flush")
    forbid(service, "queued_count", "Backend TTS queue state")

    require(
        adapter,
        "class FrameworkVoiceOutputAdapter:",
        "Framework voice-output adapter",
    )
    require(
        adapter,
        "def synthesize(",
        "one-shot adapter synthesis method",
    )
    forbid(adapter, "TTSQueueState", "Framework TTS queue ownership in DRC adapter")
    forbid(adapter, "OutputFlushRequest", "Framework output flush in DRC adapter")
    forbid(adapter, "BargeInPolicy", "Framework barge-in policy in DRC adapter")

    require(
        main,
        "app.include_router(voice_output_demo.router)",
        "voice-output router registration",
    )

    require(
        realtime_route,
        'router = APIRouter(prefix="/realtime/text"',
        "actual realtime text route",
    )
    require(
        realtime_route,
        "FrameworkRealtimeTextStreamAdapter",
        "actual realtime Framework adapter wiring",
    )
    require(
        realtime_service,
        "class RealtimeTextStreamService:",
        "actual realtime text state service",
    )
    require(
        realtime_adapter,
        "class FrameworkRealtimeTextStreamAdapter:",
        "actual root-public realtime text adapter",
    )
    for source_name, source in (
        ("realtime route", realtime_route),
        ("realtime service", realtime_service),
        ("realtime adapter", realtime_adapter),
    ):
        forbid(
            source,
            "FrameworkVoiceOutputAdapter",
            f"{source_name} voice-output adapter wiring",
        )
        forbid(
            source,
            "VoiceOutputRequest",
            f"{source_name} voice-output request wiring",
        )
        forbid(
            source,
            "/demo/voice-output",
            f"{source_name} voice-output route wiring",
        )

    backend_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "backend" / "app").rglob("*.py")
    )
    for token in (
        '"/demo/voice-output/cancel"',
        '"/demo/voice-output/flush"',
        '"/tts/queue"',
        "class TTSUtteranceQueue",
        "class TtsUtteranceQueue",
    ):
        forbid(backend_source, token, f"DRC Backend TTS runtime token {token}")


def assert_flutter_behavior() -> None:
    home = read("app/lib/screens/home_screen.dart")
    api_client = read("app/lib/services/backend_api_client.dart")
    player = read("app/lib/services/voice_output_audio_player.dart")
    engine = read("app/lib/services/audioplayers_voice_output_audio_engine.dart")
    stream_controller = read(
        "app/lib/services/realtime_text_stream_controller.dart"
    )

    require(
        api_client,
        "Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest",
        "one-shot Flutter voice-output request",
    )
    require(
        api_client,
        "Uri.parse('$baseUrl/demo/voice-output')",
        "voice-output endpoint",
    )
    forbid(api_client, "/demo/voice-output/cancel", "Flutter synthesis cancel")
    forbid(api_client, "/demo/voice-output/flush", "Flutter output flush")
    forbid(api_client, "/tts/queue", "Flutter TTS queue route")

    require(
        player,
        "Uri? _source;",
        "single current playback source",
    )
    require(
        player,
        "Future<void> play(Uri source)",
        "local play boundary",
    )
    require(
        player,
        "Future<void> stop()",
        "local playback stop boundary",
    )
    require(
        player,
        "Future<void> replay()",
        "local replay boundary",
    )
    require(
        player,
        "Future<void> reset()",
        "local reset boundary",
    )
    forbid(player, "Queue<", "Flutter playback queue")
    forbid(player, "queuedCount", "Flutter queue count")
    forbid(player, "OutputFlushResult", "Flutter FW flush result")
    forbid(player, "cancelSynthesis", "Flutter synthesis cancellation")

    require(
        engine,
        "await _mapDriverOperation(_driver!.stop);",
        "platform local playback stop",
    )
    forbid(engine, "cancelSynthesis", "platform provider cancellation")
    forbid(engine, "flushOutput", "platform FW output flush")

    require(
        home,
        "Future<void> _submitVoiceOutputDemoRequest()",
        "explicit HomeScreen voice generation action",
    )
    require(
        home,
        "key: const Key('voice-output-play-button')",
        "explicit HomeScreen play button",
    )
    require(
        home,
        "key: const Key('voice-output-stop-button')",
        "explicit HomeScreen stop button",
    )
    require(
        home,
        "await _voiceOutputAudioPlayerController.stop();",
        "HomeScreen local stop invocation",
    )

    if home.count("widget.apiClient.submitVoiceOutputDemoRequest(") != 1:
        raise AssertionError(
            "HomeScreen must have exactly one explicit Backend voice-output "
            "submission call."
        )

    submit_start = home.index(
        "Future<void> _submitVoiceOutputDemoRequest()"
    )
    submit_end = home.index(
        "Future<void> _submitMotionDemoRequest()",
        submit_start,
    )
    submit_method = home[submit_start:submit_end]
    forbid(
        submit_method,
        "_voiceOutputAudioPlayerController.play(",
        "automatic playback after voice-output generation",
    )

    stream_handler_start = home.index(
        "void _handleRealtimeTextStreamControllerChanged()"
    )
    stream_handler_end = home.index(
        "void _handleRealtimeTextStreamTranscriptHandoffChanged()",
        stream_handler_start,
    )
    stream_handler = home[stream_handler_start:stream_handler_end]
    forbid(
        stream_handler,
        "submitVoiceOutputDemoRequest",
        "realtime stream handler automatic voice-output request",
    )
    forbid(
        stream_handler,
        "_playVoiceOutputAudio",
        "realtime stream handler automatic playback",
    )
    forbid(
        stream_handler,
        "_voiceOutputAudioPlayerController",
        "realtime stream handler audio-player wiring",
    )

    forbid(home, "_enqueueVoiceOutput", "HomeScreen TTS enqueue")
    forbid(home, "_flushVoiceOutputQueue", "HomeScreen queue flush")
    forbid(home, "_handleSpeechBargeIn", "speech-triggered barge-in")

    forbid(
        stream_controller,
        "VoiceOutput",
        "realtime text controller to voice-output wiring",
    )
    forbid(
        stream_controller,
        "submitVoiceOutputDemoRequest",
        "automatic stream-to-TTS request",
    )


def assert_framework_public_surface(root: Path) -> None:
    python = framework_python(root)
    source = r"""
from dataclasses import fields
import framework

required = (
    "VoiceOutputSession",
    "VoiceOutputRequest",
    "VoiceOutputResult",
    "RealtimeSession",
    "RealtimeSessionInfo",
    "InterruptRequest",
    "InterruptResult",
    "OutputFlushRequest",
    "OutputFlushResult",
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
assert queue.queued_count == 0
assert queue.is_playing is False
assert queue.supports_flush is False
assert queue.supports_provider_cancel is False

flush_result = session.flush_output(framework.OutputFlushRequest())
assert isinstance(flush_result, framework.OutputFlushResult)
assert getattr(flush_result.outcome, "value", str(flush_result.outcome)) == "nothing_to_flush"

interrupt_result = session.interrupt(framework.InterruptRequest())
assert isinstance(interrupt_result, framework.InterruptResult)
assert getattr(interrupt_result.outcome, "value", str(interrupt_result.outcome)) == "no_active_turn"
assert interrupt_result.provider_cancel_supported is False
assert interrupt_result.queue_flush_supported is False

policy = framework.BargeInPolicy.flush_output()
session.set_barge_in_policy(policy)
decision = session.decide_barge_in()
assert isinstance(decision, framework.BargeInDecision)
assert decision.should_flush_queue is True
assert decision.should_cancel_current_turn is False

session.close()
print("rt5_public_output_control_surface_ok")
"""
    output = run(str(python), "-c", source, cwd=root, capture=True)
    if output.strip() != "rt5_public_output_control_surface_ok":
        raise AssertionError(
            f"Unexpected FW public output-control result: {output!r}"
        )


def assert_planning_contract() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "inventory": read(
            "docs/v300_rt5_tts_output_control_current_behavior_inventory.md"
        ),
    }
    combined = "\n".join(sources.values())

    for marker in (
        "RT-5 CURRENT / NOT_COMPLETED",
        "RT-5a IMPLEMENTED / AWAITING_REVIEW",
        "RT-5b NOT_STARTED / BLOCKED_PENDING_RT5A_ACCEPTANCE",
        "PARTIAL_READY_FOR_DRC_APP_OWNED_QUEUE_AND_LOCAL_PLAYBACK_FLUSH",
        "local playback stop exists: true",
        "DRC app-owned TTS queue exists: false",
        "FW public output-control data contract exists: true",
        "automatic stream-to-TTS exists: false",
        "real speech-triggered barge-in exists: false",
        "exact seven-file",
        DRC_BASELINE_HEAD,
        FW_HEAD,
    ):
        require(combined, marker, f"RT-5a planning marker {marker}")

    gate_source = read(
        "scripts/check_v300_rt5_tts_output_control_current_behavior_inventory.py"
    )
    tree = ast.parse(gate_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("framework."):
                raise AssertionError(
                    "RT-5a gate imports a Framework internal module"
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("framework."):
                    raise AssertionError(
                        "RT-5a gate imports a Framework internal module"
                    )
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
                    f"RT-5a gate performs network execution: {name}"
                )


def main() -> None:
    fw_root = assert_repository_state()
    assert_changed_content_safe()
    assert_drc_backend_behavior()
    assert_flutter_behavior()
    assert_framework_public_surface(fw_root)
    assert_planning_contract()

    print(
        "v300_rt5_tts_output_control_inventory_status: "
        "implemented-awaiting-acceptance"
    )
    print("v300_rt5a_backend_runtime_changed: False")
    print("v300_rt5a_flutter_runtime_changed: False")
    print("v300_rt5a_existing_tests_changed: False")
    print("v300_rt5a_drc_one_shot_voice_output_exists: True")
    print("v300_rt5a_drc_local_playback_stop_exists: True")
    print("v300_rt5a_drc_tts_queue_exists: False")
    print("v300_rt5a_drc_output_flush_endpoint_exists: False")
    print("v300_rt5a_automatic_stream_to_tts_exists: False")
    print("v300_rt5a_real_tts_executed: False")
    print("v300_rt5a_network_execution: False")
    print("v300_rt5a_audio_playback_executed: False")
    print("v300_rt5a_microphone_used: False")
    print("v300_rt5a_fw_public_output_control_contract_exists: True")
    print("v300_rt5a_fw_real_runtime_enabled: False")
    print("v300_rt5a_fw_tts_queue_flush_supported: False")
    print("v300_rt5a_fw_hard_cancel_supported: False")
    print("v300_rt5a_fw_internal_import: False")
    print(
        "v300_rt5b_authorization: "
        "blocked-pending-rt5a-acceptance"
    )


if __name__ == "__main__":
    main()
