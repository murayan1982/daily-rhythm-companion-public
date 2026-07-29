from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from app.config import AppConfig
from app.services.framework_realtime_text_stream_adapter import (
    FrameworkRealtimeTextStreamAdapter,
)
from app.services.realtime_text_stream_transport import (
    RealtimeTextStreamTransportRegistry,
)


def _config(framework_root: Path) -> AppConfig:
    return AppConfig(
        framework_project_root=str(framework_root),
        framework_preset="text_chat",
        framework_character="default",
        realtime_text_stream_idle_ttl_seconds=10,
        realtime_text_stream_max_duration_seconds=20,
        realtime_text_stream_max_sessions=2,
        realtime_text_stream_max_pending_events=8,
        realtime_text_stream_max_event_bytes=32768,
        realtime_text_stream_framework_enabled=True,
    )


def _write_fake_framework(root: Path, *, body: str) -> None:
    package = root / "framework"
    package.mkdir()
    (package / "__init__.py").write_text(body, encoding="utf-8")


async def _collect_until_terminal(
    registry: RealtimeTextStreamTransportRegistry,
    session_id: str,
) -> list[str]:
    frames: list[str] = []
    for _ in range(20):
        event = await registry.next_event(session_id, timeout_seconds=0.05)
        if event is None:
            await asyncio.sleep(0.01)
            continue
        frames.append(registry.serialize_sse(event))
        if event.terminal is not None:
            break
    return frames


def test_adapter_streams_fake_public_ask_stream_chunks(tmp_path, monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "framework", raising=False)
    _write_fake_framework(
        tmp_path,
        body="""
class TextChatSession:
    def __init__(self):
        self.closed = False

    def ask_stream(self, text):
        yield "hello "
        yield {"text": "world"}

    def close(self):
        self.closed = True

def create_text_chat_session(*, preset, character_name):
    return TextChatSession()
""",
    )
    config = _config(tmp_path)
    registry = RealtimeTextStreamTransportRegistry(
        config=config,
        producer=FrameworkRealtimeTextStreamAdapter(config),
    )
    started = registry.create_session(input_text="synthetic prompt")
    session_id = started.session.session_id
    registry.acquire_consumer(session_id)

    frames = asyncio.run(_collect_until_terminal(registry, session_id))

    assert "synthetic prompt" not in "".join(frames)
    assert [line for frame in frames for line in frame.splitlines() if line.startswith("event: ")] == [
        "event: stream_started",
        "event: stream_chunk",
        "event: stream_chunk",
        "event: stream_completed",
    ]
    assert '"text":"hello "' in frames[1]
    assert '"text":"world"' in frames[2]
    assert '"outcome":"completed"' in frames[-1]
    assert started.session.hard_cancel_supported is False


def test_adapter_cancel_requests_public_interrupt_without_hard_cancel_claim(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.delitem(sys.modules, "framework", raising=False)
    marker = tmp_path / "interrupt_called.txt"
    _write_fake_framework(
        tmp_path,
        body=f"""
from pathlib import Path
from time import sleep

class TextChatSession:
    def ask_stream(self, text):
        yield "partial"
        marker = Path({str(marker)!r})
        while not marker.exists():
            sleep(0.01)

    def interrupt(self):
        Path({str(marker)!r}).write_text("called", encoding="utf-8")

    def dispose(self):
        pass

def create_text_chat_session(*, preset, character_name):
    return TextChatSession()
""",
    )
    config = _config(tmp_path)
    registry = RealtimeTextStreamTransportRegistry(
        config=config,
        producer=FrameworkRealtimeTextStreamAdapter(config),
    )
    started = registry.create_session(input_text="cancel this")
    session_id = started.session.session_id

    async def wait_for_chunk() -> None:
        for _ in range(20):
            event = await registry.next_event(session_id, timeout_seconds=0.05)
            if event is not None and event.event_type.value == "stream_chunk":
                return
        raise AssertionError("fake public ask_stream did not publish a chunk")

    asyncio.run(wait_for_chunk())
    cancelled = registry.request_cancel(session_id)

    assert marker.read_text(encoding="utf-8") == "called"
    assert cancelled.final_result.accepted is True
    assert cancelled.final_result.session.hard_cancel_supported is False
    assert cancelled.final_result.event is not None
    assert cancelled.final_result.event.terminal is not None
    assert cancelled.final_result.event.terminal.outcome.value == "cancelled"


def test_adapter_missing_public_root_fails_with_safe_terminal(tmp_path) -> None:
    config = _config(tmp_path / "missing-fw")
    registry = RealtimeTextStreamTransportRegistry(
        config=config,
        producer=FrameworkRealtimeTextStreamAdapter(config),
    )

    started = registry.create_session(input_text="synthetic prompt")
    session_id = started.session.session_id
    frames = asyncio.run(_collect_until_terminal(registry, session_id))

    assert "synthetic prompt" not in "".join(frames)
    assert frames[-1].splitlines()[1] == "event: stream_failed"
    assert "blocked-framework-root-missing" in frames[-1]
    assert "path" not in frames[-1].lower()
