"""Validate the RT-4d FW root-public text streaming adapter boundary.

This gate uses only a fake root ``framework`` package. It does not import
Framework internals, create a provider client, call a network API, read
credentials, read transcripts, touch Flutter, or claim provider hard cancel.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

EXPECTED_RT4D_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/api/realtime_text.py",
    "backend/app/services/realtime_text_stream_transport.py",
    "backend/app/services/framework_realtime_text_stream_adapter.py",
    "backend/tests/test_framework_realtime_text_stream_adapter.py",
    "backend/tests/test_temporary_lifecycle_config.py",
    "docs/v300_rt4_framework_public_streaming_adapter.md",
    "scripts/check_v300_rt4_framework_public_streaming_adapter.py",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:\\Users\\[^<\r\n]+",
    r"/(?:home|users)/[^/\s]+/",
    r"192\.168\.\d{1,3}\.\d{1,3}",
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def assert_source_contract() -> None:
    adapter = read("backend/app/services/framework_realtime_text_stream_adapter.py")
    transport = read("backend/app/services/realtime_text_stream_transport.py")
    api = read("backend/app/api/realtime_text.py")
    config = read("backend/app/config.py")
    tests = read("backend/tests/test_framework_realtime_text_stream_adapter.py")
    doc = read("docs/v300_rt4_framework_public_streaming_adapter.md")

    for marker in (
        "importlib.import_module(self._module_name)",
        '"create_text_chat_session"',
        '"ask_stream"',
        '"interrupt"',
        '"close"',
        '"dispose"',
        "framework_text_chat_import_context(project_root)",
        "provider_call_attempted=True",
    ):
        require(adapter, marker, f"RT-4d adapter marker {marker}")

    for forbidden in (
        "from framework.",
        "import framework.",
        "OpenAI(",
        "AsyncOpenAI(",
        "google.genai.Client",
        "requests.",
        "httpx.",
        "hard_cancel_supported=True",
        "provider-level hard cancel: true",
    ):
        forbid(adapter + transport + api + tests, forbidden, "forbidden RT-4d wiring")

    require(config, "DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM", "RT-4d env gate")
    require(api, "realtime_text_stream_framework_enabled", "RT-4d API gate use")
    require(transport, "request_interrupt()", "cooperative interrupt request")
    require(doc, "hard_cancel_supported=false", "hard cancel non-claim")
    require(doc, "Framework internal-module import: forbidden", "internal import rule")
    require(doc, "Flutter changed: false", "Flutter non-change")


def assert_fake_runtime_contract() -> None:
    from app.config import AppConfig
    from app.services.framework_realtime_text_stream_adapter import (
        FrameworkRealtimeTextStreamAdapter,
    )
    from app.services.realtime_text_stream_transport import (
        RealtimeTextStreamTransportRegistry,
    )

    framework_before = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }

    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        package = root / "framework"
        package.mkdir()
        (package / "__init__.py").write_text(
            """
class TextChatSession:
    def ask_stream(self, text):
        yield "alpha "
        yield {"text": "beta"}

    def interrupt(self):
        self.interrupted = True

    def close(self):
        self.closed = True

def create_text_chat_session(*, preset, character_name):
    return TextChatSession()
""",
            encoding="utf-8",
        )
        sys.modules.pop("framework", None)
        config = AppConfig(
            framework_project_root=str(root),
            realtime_text_stream_framework_enabled=True,
            realtime_text_stream_idle_ttl_seconds=10,
            realtime_text_stream_max_duration_seconds=20,
            realtime_text_stream_max_sessions=2,
            realtime_text_stream_max_pending_events=8,
            realtime_text_stream_max_event_bytes=32768,
        )
        registry = RealtimeTextStreamTransportRegistry(
            config=config,
            producer=FrameworkRealtimeTextStreamAdapter(config),
        )
        started = registry.create_session(input_text="private fake input")
        registry.acquire_consumer(started.session.session_id)

        async def collect() -> list[str]:
            frames: list[str] = []
            for _ in range(20):
                event = await registry.next_event(
                    started.session.session_id,
                    timeout_seconds=0.05,
                )
                if event is None:
                    await asyncio.sleep(0.01)
                    continue
                frames.append(registry.serialize_sse(event))
                if event.terminal is not None:
                    break
            return frames

        frames = asyncio.run(collect())
        joined = "".join(frames)
        if "private fake input" in joined:
            raise AssertionError("RT-4d leaked input text into SSE")
        if "event: stream_chunk" not in joined or "event: stream_completed" not in joined:
            raise AssertionError("RT-4d fake public stream did not complete")
        if started.session.hard_cancel_supported:
            raise AssertionError("RT-4d lost hard_cancel_supported=false")

    sys.modules.pop("framework", None)
    framework_after = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }
    if framework_after - framework_before:
        raise AssertionError("RT-4d left fake framework modules cached")


def assert_changed_content_safe() -> None:
    diff = subprocess.run(
        [
            "git",
            "diff",
            "--unified=0",
            "--",
            *sorted(EXPECTED_RT4D_FILES),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=True,
    ).stdout
    added_lines = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        capture_output=True,
    ).stdout.splitlines()
    added_lines.extend(
        read(relative)
        for relative in sorted(set(untracked) & EXPECTED_RT4D_FILES)
        if relative != "scripts/check_v300_rt4_framework_public_streaming_adapter.py"
    )
    combined = "\n".join(added_lines)
    combined = combined.replace(
        'r"/(?:Users|home|mnt|tmp)/[^\\s:\'\\"]+"',
        "<private-path-redaction-regex>",
    )
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in RT-4d content: {pattern}")


def main() -> None:
    assert_source_contract()
    assert_fake_runtime_contract()
    assert_changed_content_safe()

    print("v300_rt4_framework_public_streaming_adapter_status: implemented-awaiting-acceptance")
    print("v300_rt4d_framework_root_public_api_only: True")
    print("v300_rt4d_fake_public_ask_stream_chunks: True")
    print("v300_rt4d_cooperative_interrupt_requested: True")
    print("v300_rt4d_framework_internal_import: False")
    print("v300_rt4d_drc_provider_client: False")
    print("v300_rt4d_provider_level_hard_cancel_claimed: False")
    print("v300_rt4d_flutter_changed: False")


if __name__ == "__main__":
    main()
