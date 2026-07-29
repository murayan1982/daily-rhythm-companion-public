# Validate DRC v3.0.0 RT-4a streaming/cancel current behavior inventory.

from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DRC_BASELINE_HEAD = "eecf13d7dce653f341721ad007ca39aca91f497e"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt4_streaming_cancel_current_behavior_inventory.md",
    "scripts/check_v300_rt4_streaming_cancel_current_behavior_inventory.py",
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
    output = run("git", "status", "--porcelain", "--untracked-files=all", capture=True)
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
        raise AssertionError("FRAMEWORK_ROOT must point to the clean FW v5.4.0 checkout.")
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
        raise AssertionError(f"RT-4a changed surface mismatch: {sorted(actual_paths)}")

    if run("git", "rev-parse", "HEAD", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")
    if run("git", "rev-parse", "origin/main", capture=True) != DRC_BASELINE_HEAD:
        raise AssertionError("Unexpected DRC origin/main.")

    root = framework_root()
    if run("git", "rev-parse", "HEAD", cwd=root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW HEAD.")
    if run("git", "rev-list", "-n", "1", "v5.4.0", cwd=root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW v5.4.0 tag target.")
    if run("git", "status", "--porcelain", "--untracked-files=all", cwd=root, capture=True):
        raise AssertionError("FW working tree is not clean.")
    return root


def assert_drc_current_behavior() -> None:
    live_reply = read("backend/app/services/framework_text_chat_drc_live_reply.py")
    chat_route = read("backend/app/api/chat.py")
    main = read("backend/app/main.py")
    realtime = read("backend/app/models/realtime.py")
    voice_input_route = read("backend/app/api/voice_input_demo.py")
    api_client = read("app/lib/services/backend_api_client.dart")
    home = read("app/lib/screens/home_screen.dart")

    require(live_reply, 'getattr(session, "ask", None)', "full-response FW ask boundary")
    require(live_reply, "return ask(prompt)", "full-response FW ask invocation")
    forbid(live_reply, 'getattr(session, "ask_stream"', "DRC ask_stream invocation")

    require(chat_route, '@router.post("/sessions"', "chat session route")
    require(chat_route, '"/sessions/{session_id}/messages"', "chat message route")
    forbid(chat_route, "StreamingResponse", "chat streaming response")
    forbid(chat_route, "text/event-stream", "chat SSE media type")
    forbid(chat_route, "@router.websocket", "chat WebSocket route")

    require(main, "app.include_router(chat.router)", "synchronous chat router registration")
    forbid(main, "realtime_text", "RT-4 router registration")

    require(realtime, 'TEXT_CHAT_STARTED = "text_chat_started"', "normalized text start event")
    require(realtime, 'TEXT_CHAT_COMPLETED = "text_chat_completed"', "normalized text completion event")
    forbid(realtime, "TEXT_CHAT_CHUNK", "DRC stream chunk event")
    forbid(realtime, "chunk_sequence", "DRC chunk sequence")

    require(api_client, "createPostAdviceChatSession", "Flutter full-response chat create")
    require(api_client, "sendPostAdviceChatMessage", "Flutter full-response message send")
    forbid(api_client, "text/event-stream", "Flutter SSE client")
    forbid(api_client, "EventSource", "Flutter EventSource client")
    forbid(api_client, "WebSocketChannel", "Flutter WebSocket client")
    forbid(api_client, "/realtime/text", "Flutter RT-4 endpoint")

    require(home, "await widget.apiClient.sendPostAdviceChatMessage", "Flutter awaited full response")
    forbid(home, "RealtimeTextStreamController", "Flutter stream controller")

    forbid(voice_input_route, "framework_text_chat", "voice input to LLM streaming wiring")

    backend_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "backend" / "app").rglob("*.py")
    )
    flutter_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "app" / "lib").rglob("*.dart")
    )
    for token in (
        "from fastapi.responses import StreamingResponse",
        "StreamingResponse(",
        'media_type="text/event-stream"',
        "@router.websocket",
    ):
        forbid(backend_source, token, f"Backend streaming transport token {token}")
    for token in ("EventSource(", "WebSocketChannel.connect", "/realtime/text"):
        forbid(flutter_source, token, f"Flutter streaming transport token {token}")


def assert_framework_public_surface(root: Path) -> None:
    python = framework_python(root)
    source = r'''
from dataclasses import fields
import inspect
import framework

required = (
    "TextChatSession",
    "TextChatSessionInfo",
    "TextChatSessionEvent",
    "TextChatStateChange",
    "create_text_chat_session",
    "RealtimeSession",
    "RealtimeSessionInfo",
    "InterruptRequest",
    "InterruptResult",
)
missing = [name for name in required if not hasattr(framework, name)]
assert not missing, missing

info_defaults = {field.name: field.default for field in fields(framework.TextChatSessionInfo)}
assert info_defaults["supports_streaming"] is True
assert info_defaults["supports_interrupt"] is True
assert info_defaults["supports_events"] is True

ask_source = inspect.getsource(framework.TextChatSession.ask)
stream_source = inspect.getsource(framework.TextChatSession.ask_stream)
interrupt_source = inspect.getsource(framework.TextChatSession.interrupt)
assert "self.ask_stream" in ask_source
assert "response_chunk" in stream_source
assert "_interrupt_requested" in stream_source
assert "_interrupt_requested = True" in interrupt_source
assert "provider-level hard cancellation" in interrupt_source

realtime_defaults = {field.name: field.default for field in fields(framework.RealtimeSessionInfo)}
assert realtime_defaults["real_runtime_enabled"] is False
assert realtime_defaults["hard_cancel_supported"] is False
assert realtime_defaults["tts_queue_flush_supported"] is False

print("rt4_public_surface_ok")
'''
    output = run(str(python), "-c", source, cwd=root, capture=True)
    if output.strip() != "rt4_public_surface_ok":
        raise AssertionError(f"Unexpected FW public surface result: {output!r}")


def assert_planning_contract() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "inventory": read("docs/v300_rt4_streaming_cancel_current_behavior_inventory.md"),
    }
    combined = "\n".join(sources.values())

    for marker in (
        "RT-4a",
        "IMPLEMENTED / AWAITING_ACCEPTANCE",
        "RT-4b",
        "NOT_STARTED",
        "cooperative cancel",
        "provider-level hard cancel",
        "ask_stream()",
        "session.ask()",
        "RT-5",
        "exact seven-file",
        "eecf13d7dce653f341721ad007ca39aca91f497e",
        "d313eb6acb643103fe25988720ebee5976a04f78",
    ):
        require(combined, marker, f"RT-4a planning marker {marker}")

    gate_source = read("scripts/check_v300_rt4_streaming_cancel_current_behavior_inventory.py")
    tree = ast.parse(gate_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("framework."):
                raise AssertionError("RT-4a gate imports a Framework internal module")
        elif isinstance(node, ast.Call):
            target = node.func
            name = ""
            if isinstance(target, ast.Name):
                name = target.id
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                name = f"{target.value.id}.{target.attr}"
            if name in {"requests.get", "requests.post", "httpx.get", "httpx.post"}:
                raise AssertionError(f"RT-4a gate performs network execution: {name}")



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
        run("git", "ls-files", "--others", "--exclude-standard", capture=True).splitlines()
    )
    for relative in sorted(EXPECTED_PATHS & untracked):
        added_lines.append(read(relative))
    added_text = "\n".join(added_lines)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, added_text):
            raise AssertionError(f"Sensitive-looking value in RT-4a added content: {pattern}")


def main() -> None:
    fw_root = assert_repository_state()
    assert_changed_content_safe()
    assert_drc_current_behavior()
    assert_framework_public_surface(fw_root)
    assert_planning_contract()

    print("v300_rt4_streaming_cancel_inventory_status: implemented-awaiting-acceptance")
    print("v300_rt4a_backend_runtime_changed: False")
    print("v300_rt4a_flutter_runtime_changed: False")
    print("v300_rt4a_existing_tests_changed: False")
    print("v300_rt4a_streaming_transport_added: False")
    print("v300_rt4a_provider_execution: False")
    print("v300_rt4a_hard_cancel_claimed: False")
    print("v300_rt4a_fw_internal_import: False")
    print("v300_rt4b_authorization: blocked-pending-rt4a-acceptance")


if __name__ == "__main__":
    main()
