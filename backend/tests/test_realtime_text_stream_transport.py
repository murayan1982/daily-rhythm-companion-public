from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import realtime_text
from app.config import AppConfig
from app.services.realtime_text_stream_transport import (
    STREAM_PROBLEM_CAPACITY,
    STREAM_PROBLEM_CONSUMED,
    STREAM_PROBLEM_DURATION,
    STREAM_PROBLEM_EVENT_BUFFER,
    STREAM_PROBLEM_IDLE_TIMEOUT,
    RealtimeTextStreamTransportError,
    RealtimeTextStreamTransportRegistry,
)


class _Clock:
    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _config(**overrides) -> AppConfig:
    values = {
        "realtime_text_stream_idle_ttl_seconds": 10,
        "realtime_text_stream_max_duration_seconds": 20,
        "realtime_text_stream_max_sessions": 2,
        "realtime_text_stream_max_pending_events": 8,
        "realtime_text_stream_max_event_bytes": 32768,
    }
    values.update(overrides)
    return AppConfig(**values)


def _client(monkeypatch, registry: RealtimeTextStreamTransportRegistry) -> TestClient:
    monkeypatch.setattr(realtime_text, "_stream_registry", registry)
    app = FastAPI()
    app.include_router(realtime_text.router)
    return TestClient(app)


def _parse_sse(body: str) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for block in body.strip().split("\n\n"):
        fields: dict[str, str] = {}
        for line in block.splitlines():
            key, value = line.split(": ", 1)
            fields[key] = value
        events.append(
            {
                "id": int(fields["id"]),
                "event": fields["event"],
                "data": json.loads(fields["data"]),
            }
        )
    return events


def test_create_route_returns_opaque_bounded_session_without_echoing_input(monkeypatch) -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    client = _client(monkeypatch, registry)

    with client:
        response = client.post(
            "/realtime/text/sessions",
            json={"input_text": "synthetic operator-free prompt"},
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["session"]["state"] == "streaming"
    assert payload["session"]["cancel_mode"] == "cooperative"
    assert payload["session"]["hard_cancel_supported"] is False
    assert payload["turn"]["state"] == "streaming"
    assert payload["events_path"].endswith("/events")
    assert payload["cancel_path"].endswith("/cancel")
    assert payload["idle_ttl_seconds"] == 10
    assert payload["max_duration_seconds"] == 20
    assert payload["max_pending_events"] == 8
    assert payload["max_event_bytes"] == 32768
    assert "synthetic operator-free prompt" not in response.text
    assert registry.input_text_for_session(payload["session"]["session_id"]) == (
        "synthetic operator-free prompt"
    )


def test_sse_route_streams_monotonic_start_chunks_and_terminal(monkeypatch) -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    client = _client(monkeypatch, registry)
    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    turn_id = started.turn.turn_id if started.turn is not None else ""
    registry.publish_chunk(session_id=session_id, turn_id=turn_id, text="hello ")
    registry.publish_chunk(session_id=session_id, turn_id=turn_id, text="world")
    registry.complete_session(session_id=session_id, turn_id=turn_id)

    with client:
        response = client.get(f"/realtime/text/sessions/{session_id}/events")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert response.headers["cache-control"] == "no-cache, no-store"
    assert response.headers["x-accel-buffering"] == "no"
    events = _parse_sse(response.text)
    assert [item["id"] for item in events] == [1, 2, 3, 4]
    assert [item["event"] for item in events] == [
        "stream_started",
        "stream_chunk",
        "stream_chunk",
        "stream_completed",
    ]
    assert events[1]["data"]["chunk"]["text"] == "hello "
    assert events[2]["data"]["chunk"]["text"] == "world"
    assert events[3]["data"]["terminal"]["final_text"] == "hello world"
    assert registry.has_session(session_id) is False


def test_cancel_route_queues_request_and_cooperative_terminal(monkeypatch) -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    client = _client(monkeypatch, registry)
    started = registry.create_session(input_text="cancel me")
    session_id = started.session.session_id

    with client:
        cancelled = client.post(f"/realtime/text/sessions/{session_id}/cancel")
        streamed = client.get(f"/realtime/text/sessions/{session_id}/events")

    assert cancelled.status_code == 200
    payload = cancelled.json()
    assert payload["accepted"] is True
    assert payload["state"] == "cancelled"
    assert payload["cancel_mode"] == "cooperative"
    assert payload["hard_cancel_supported"] is False
    assert payload["terminal"] is True
    events = _parse_sse(streamed.text)
    assert [item["event"] for item in events] == [
        "stream_started",
        "cancel_requested",
        "stream_cancelled",
    ]
    assert events[-1]["data"]["terminal"]["outcome"] == "cancelled"


def test_unknown_session_and_consumed_session_return_public_safe_problems(monkeypatch) -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    client = _client(monkeypatch, registry)

    with client:
        missing = client.post("/realtime/text/sessions/missing/cancel")

    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "stream_not_found"
    assert "path" not in missing.text.lower()

    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    turn_id = started.turn.turn_id if started.turn is not None else ""
    registry.complete_session(session_id=session_id, turn_id=turn_id)
    with client:
        assert client.get(f"/realtime/text/sessions/{session_id}/events").status_code == 200
        consumed = client.get(f"/realtime/text/sessions/{session_id}/events")
    assert consumed.status_code == 410
    assert consumed.json()["detail"]["code"] == STREAM_PROBLEM_CONSUMED


def test_capacity_is_bounded_and_inactive_timeout_frees_a_slot() -> None:
    clock = _Clock()
    registry = RealtimeTextStreamTransportRegistry(
        config=_config(realtime_text_stream_max_sessions=1),
        now=clock,
    )
    registry.create_session(input_text="first")

    try:
        registry.create_session(input_text="second")
    except RealtimeTextStreamTransportError as exc:
        assert exc.status_code == 429
        assert exc.problem.code == STREAM_PROBLEM_CAPACITY
    else:
        raise AssertionError("capacity limit did not reject the second session")

    clock.advance(10)
    second = registry.create_session(input_text="second")
    assert second.accepted is True
    assert registry.session_count == 1


def test_only_one_sse_consumer_can_attach() -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    registry.acquire_consumer(session_id)

    try:
        registry.acquire_consumer(session_id)
    except RealtimeTextStreamTransportError as exc:
        assert exc.status_code == 409
        assert exc.problem.code == "stream_consumer_already_attached"
    else:
        raise AssertionError("a second stream consumer was accepted")


def test_idle_timeout_emits_retryable_failed_terminal() -> None:
    clock = _Clock()
    registry = RealtimeTextStreamTransportRegistry(config=_config(), now=clock)
    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    registry.acquire_consumer(session_id)
    clock.advance(10)

    result = registry.enforce_timeouts(session_id)

    assert result is not None
    assert result.event is not None
    assert result.event.event_type.value == "stream_failed"
    assert result.event.terminal is not None
    assert result.event.terminal.public_error_code == STREAM_PROBLEM_IDLE_TIMEOUT
    assert result.event.terminal.retryable is True


def test_max_duration_wins_over_idle_timeout() -> None:
    clock = _Clock()
    registry = RealtimeTextStreamTransportRegistry(
        config=_config(
            realtime_text_stream_idle_ttl_seconds=100,
            realtime_text_stream_max_duration_seconds=5,
        ),
        now=clock,
    )
    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    registry.acquire_consumer(session_id)
    clock.advance(5)

    result = registry.enforce_timeouts(session_id)

    assert result is not None
    assert result.event is not None
    assert result.event.terminal is not None
    assert result.event.terminal.public_error_code == STREAM_PROBLEM_DURATION


def test_pending_event_overflow_drops_buffer_and_queues_safe_terminal() -> None:
    registry = RealtimeTextStreamTransportRegistry(
        config=_config(realtime_text_stream_max_pending_events=2)
    )
    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    turn_id = started.turn.turn_id if started.turn is not None else ""
    registry.publish_chunk(session_id=session_id, turn_id=turn_id, text="a")

    overflow = registry.publish_chunk(session_id=session_id, turn_id=turn_id, text="b")

    assert overflow.accepted is True

    async def read_one():
        return await registry.next_event(session_id)

    event = asyncio.run(read_one())
    assert event is not None
    assert event.event_type.value == "stream_failed"
    assert event.terminal is not None
    assert event.terminal.public_error_code == STREAM_PROBLEM_EVENT_BUFFER
    assert event.terminal.retryable is True


def test_disconnected_generator_closes_and_removes_session(monkeypatch) -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    monkeypatch.setattr(realtime_text, "_stream_registry", registry)
    started = registry.create_session(input_text="not public")
    session_id = started.session.session_id
    registry.acquire_consumer(session_id)

    class Request:
        calls = 0

        async def is_disconnected(self) -> bool:
            self.calls += 1
            return self.calls > 1

    async def consume_one() -> list[str]:
        frames: list[str] = []
        async for frame in realtime_text._iter_realtime_text_events(
            request=Request(),
            session_id=session_id,
        ):
            frames.append(frame)
        return frames

    frames = asyncio.run(consume_one())

    assert len(frames) == 1
    assert "event: stream_started" in frames[0]
    assert registry.has_session(session_id) is False
    try:
        registry.acquire_consumer(session_id)
    except RealtimeTextStreamTransportError as exc:
        assert exc.status_code == 410
        assert exc.problem.code == "stream_disconnected"
    else:
        raise AssertionError("disconnected stream was retained")


def test_sse_frame_is_compact_utf8_and_contains_no_raw_input() -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    started = registry.create_session(input_text="private synthetic input")
    assert started.event is not None

    frame = registry.serialize_sse(started.event)

    assert frame.startswith("id: 1\nevent: stream_started\ndata: {")
    assert frame.endswith("\n\n")
    assert "private synthetic input" not in frame
    assert len(frame.encode("utf-8")) <= registry.settings.max_event_bytes


def test_event_byte_overflow_replaces_chunk_with_deliverable_safe_terminal() -> None:
    registry = RealtimeTextStreamTransportRegistry(
        config=_config(realtime_text_stream_max_event_bytes=1024)
    )
    started = registry.create_session(input_text="synthetic")
    session_id = started.session.session_id
    turn_id = started.turn.turn_id if started.turn is not None else ""

    published = registry.publish_chunk(
        session_id=session_id,
        turn_id=turn_id,
        text="あ" * 512,
    )

    assert published.accepted is True

    async def read_events():
        first = await registry.next_event(session_id)
        second = await registry.next_event(session_id)
        return first, second

    first, second = asyncio.run(read_events())
    assert first is not None
    assert first.event_type.value == "stream_failed"
    assert first.terminal is not None
    assert first.terminal.public_error_code == "stream_event_bytes_exceeded"
    assert first.terminal.final_text == ""
    assert len(registry.serialize_sse(first).encode("utf-8")) <= 1024
    assert second is None


def test_create_route_rejects_whitespace_only_input(monkeypatch) -> None:
    registry = RealtimeTextStreamTransportRegistry(config=_config())
    client = _client(monkeypatch, registry)

    with client:
        response = client.post(
            "/realtime/text/sessions",
            json={"input_text": "   \n  "},
        )

    assert response.status_code == 422
    assert registry.session_count == 0
