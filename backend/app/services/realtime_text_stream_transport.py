from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
from queue import Empty, Full, Queue
from threading import RLock
from time import monotonic
from typing import Any, Callable, Protocol

from app.config import AppConfig, load_config
from app.models.realtime_text_stream import (
    RealtimeTextStreamCallbackResult,
    RealtimeTextStreamEvent,
    RealtimeTextStreamEventType,
    RealtimeTextStreamState,
)
from app.models.realtime_text_stream_transport import RealtimeTextStreamProblem
from app.services.realtime_text_stream_service import RealtimeTextStreamService


STREAM_PROBLEM_NOT_FOUND = "stream_not_found"
STREAM_PROBLEM_CAPACITY = "stream_capacity_reached"
STREAM_PROBLEM_CONSUMER_ATTACHED = "stream_consumer_already_attached"
STREAM_PROBLEM_CONSUMED = "stream_already_consumed"
STREAM_PROBLEM_IDLE_TIMEOUT = "stream_idle_timeout"
STREAM_PROBLEM_DURATION = "stream_duration_exceeded"
STREAM_PROBLEM_DISCONNECTED = "stream_disconnected"
STREAM_PROBLEM_EVENT_BUFFER = "stream_event_buffer_exceeded"
STREAM_PROBLEM_EVENT_BYTES = "stream_event_bytes_exceeded"


class RealtimeTextStreamTransportError(RuntimeError):
    """Typed public-safe transport error raised before a response body starts."""

    def __init__(self, *, status_code: int, problem: RealtimeTextStreamProblem) -> None:
        super().__init__(problem.message)
        self.status_code = status_code
        self.problem = problem


@dataclass(frozen=True)
class RealtimeTextStreamTransportSettings:
    idle_ttl_seconds: int
    max_duration_seconds: int
    max_sessions: int
    max_pending_events: int
    max_event_bytes: int


@dataclass
class _TransportEntry:
    service: RealtimeTextStreamService
    input_text: str
    created_at: float
    last_activity_at: float
    events: Queue[RealtimeTextStreamEvent]
    consumer_attached: bool = False
    terminal_queued: bool = False


@dataclass(frozen=True)
class RealtimeTextStreamCancelOperation:
    request_result: RealtimeTextStreamCallbackResult
    terminal_result: RealtimeTextStreamCallbackResult | None

    @property
    def final_result(self) -> RealtimeTextStreamCallbackResult:
        return self.terminal_result or self.request_result


class RealtimeTextStreamProducerHandle(Protocol):
    def request_interrupt(self) -> bool:
        """Request cooperative upstream interruption without hard-cancel claims."""


class RealtimeTextStreamProducer(Protocol):
    def start_stream(
        self,
        *,
        session_id: str,
        turn_id: str,
        input_text: str,
        callbacks: Any,
    ) -> tuple[Any, RealtimeTextStreamProducerHandle | None]:
        """Start producing normalized stream callbacks for one DRC turn."""


class RealtimeTextStreamTransportRegistry:
    """Bounded in-memory registry and SSE event buffer for RT-4c.

    RT-4c owns transport lifecycle only. It stores one bounded input string for a
    future RT-4d Framework adapter, queues normalized RT-4b events, allows one
    consumer, and performs no provider, Framework, network, or background-worker
    execution.
    """

    def __init__(
        self,
        *,
        config: AppConfig | None = None,
        now: Callable[[], float] | None = None,
        service_factory: Callable[[], RealtimeTextStreamService] | None = None,
        producer: RealtimeTextStreamProducer | None = None,
    ) -> None:
        resolved = config or load_config()
        self.settings = RealtimeTextStreamTransportSettings(
            idle_ttl_seconds=max(1, resolved.realtime_text_stream_idle_ttl_seconds),
            max_duration_seconds=max(1, resolved.realtime_text_stream_max_duration_seconds),
            max_sessions=max(1, resolved.realtime_text_stream_max_sessions),
            max_pending_events=max(1, resolved.realtime_text_stream_max_pending_events),
            max_event_bytes=max(1024, resolved.realtime_text_stream_max_event_bytes),
        )
        self._now = now or monotonic
        self._service_factory = service_factory or RealtimeTextStreamService
        self._producer = producer
        self._producer_handles: dict[str, RealtimeTextStreamProducerHandle] = {}
        self._entries: dict[str, _TransportEntry] = {}
        self._removed: dict[str, RealtimeTextStreamProblem] = {}
        self._removed_order: list[str] = []
        self._lock = RLock()

    def create_session(self, *, input_text: str) -> RealtimeTextStreamCallbackResult:
        """Create one session/turn and queue its normalized start event."""

        with self._lock:
            self._cleanup_inactive_locked()
            if len(self._entries) >= self.settings.max_sessions:
                raise self._error(
                    status_code=429,
                    code=STREAM_PROBLEM_CAPACITY,
                    message="The text-stream session capacity is currently full.",
                    retryable=True,
                )

            service = self._service_factory()
            started = service.start_turn()
            if not started.accepted or started.event is None or started.turn is None:
                raise self._error(
                    status_code=503,
                    code="stream_start_failed",
                    message="The text-stream session could not be started.",
                    retryable=True,
                )

            current_time = self._now()
            entry = _TransportEntry(
                service=service,
                input_text=input_text,
                created_at=current_time,
                last_activity_at=current_time,
                events=Queue(maxsize=self.settings.max_pending_events),
            )
            self._entries[started.session.session_id] = entry
            self._removed.pop(started.session.session_id, None)
            self._queue_result_locked(entry, started)
            self._start_producer_locked(entry, started)
            return started

    def input_text_for_session(self, session_id: str) -> str:
        """Return the private in-memory input for a future Backend adapter only."""

        with self._lock:
            return self._entry_locked(session_id).input_text

    def acquire_consumer(self, session_id: str) -> None:
        """Claim the only allowed SSE consumer for one stream session."""

        with self._lock:
            self._cleanup_inactive_locked()
            entry = self._entry_locked(session_id)
            if entry.consumer_attached:
                raise self._error(
                    status_code=409,
                    code=STREAM_PROBLEM_CONSUMER_ATTACHED,
                    message="A text-stream consumer is already attached.",
                    retryable=False,
                )
            entry.consumer_attached = True

    async def next_event(
        self,
        session_id: str,
        *,
        timeout_seconds: float = 0.1,
    ) -> RealtimeTextStreamEvent | None:
        """Wait briefly for one queued event without blocking the event loop."""

        with self._lock:
            entry = self._entry_locked(session_id)
            queue = entry.events
        try:
            return await asyncio.to_thread(
                queue.get,
                True,
                max(0.01, timeout_seconds),
            )
        except Empty:
            return None

    def enforce_timeouts(self, session_id: str) -> RealtimeTextStreamCallbackResult | None:
        """Terminalize one attached stream when its idle or duration bound wins."""

        with self._lock:
            entry = self._entry_locked(session_id)
            if entry.terminal_queued:
                return None
            current_time = self._now()
            if current_time - entry.created_at >= self.settings.max_duration_seconds:
                result = entry.service.fail(
                    turn_id=self._active_turn_id(entry),
                    public_error_code=STREAM_PROBLEM_DURATION,
                    safe_message="The text stream reached its maximum duration.",
                    retryable=True,
                )
                self._queue_result_locked(entry, result)
                return result
            if current_time - entry.last_activity_at >= self.settings.idle_ttl_seconds:
                result = entry.service.fail(
                    turn_id=self._active_turn_id(entry),
                    public_error_code=STREAM_PROBLEM_IDLE_TIMEOUT,
                    safe_message="The text stream ended after an idle timeout.",
                    retryable=True,
                )
                self._queue_result_locked(entry, result)
                return result
            return None

    def publish_chunk(
        self,
        *,
        session_id: str,
        turn_id: str,
        text: str,
    ) -> RealtimeTextStreamCallbackResult:
        """Queue one provider-neutral bounded chunk for the attached/future consumer."""

        with self._lock:
            entry = self._entry_locked(session_id)
            result = entry.service.append_chunk(turn_id=turn_id, text=text)
            self._queue_result_locked(entry, result)
            return result

    def complete_session(
        self,
        *,
        session_id: str,
        turn_id: str,
    ) -> RealtimeTextStreamCallbackResult:
        with self._lock:
            entry = self._entry_locked(session_id)
            result = entry.service.complete(turn_id=turn_id)
            self._queue_result_locked(entry, result)
            return result

    def fail_session(
        self,
        *,
        session_id: str,
        turn_id: str,
        public_error_code: str,
        safe_message: str,
        retryable: bool,
    ) -> RealtimeTextStreamCallbackResult:
        with self._lock:
            entry = self._entry_locked(session_id)
            result = entry.service.fail(
                turn_id=turn_id,
                public_error_code=public_error_code,
                safe_message=safe_message,
                retryable=retryable,
            )
            self._queue_result_locked(entry, result)
            return result

    def request_cancel(self, session_id: str) -> RealtimeTextStreamCancelOperation:
        """Queue cancel-request and cancelled terminal events without hard-cancel claims."""

        with self._lock:
            entry = self._entry_locked(session_id)
            turn_id = self._active_turn_id(entry)
            handle = self._producer_handles.get(session_id)
            if handle is not None:
                handle.request_interrupt()
            requested = entry.service.request_cancel(turn_id=turn_id)
            self._queue_result_locked(entry, requested)
            terminal: RealtimeTextStreamCallbackResult | None = None
            if requested.accepted:
                terminal = entry.service.cancel(turn_id=turn_id)
                self._queue_result_locked(entry, terminal)
            return RealtimeTextStreamCancelOperation(
                request_result=requested,
                terminal_result=terminal,
            )

    def release_consumer(self, session_id: str, *, terminal_seen: bool) -> None:
        """Remove a consumed stream or close/remove it after client disconnect."""

        with self._lock:
            entry = self._entries.get(session_id)
            if entry is None:
                return
            entry.consumer_attached = False
            if terminal_seen:
                self._remove_locked(
                    session_id,
                    RealtimeTextStreamProblem(
                        code=STREAM_PROBLEM_CONSUMED,
                        message="The text stream has already been consumed.",
                        retryable=False,
                    ),
                )
                return

            turn_id = entry.service.session.active_turn_id
            entry.service.close(turn_id=turn_id)
            self._remove_locked(
                session_id,
                RealtimeTextStreamProblem(
                    code=STREAM_PROBLEM_DISCONNECTED,
                    message="The text stream was closed after its consumer disconnected.",
                    retryable=True,
                ),
            )

    def serialize_sse(self, event: RealtimeTextStreamEvent) -> str:
        """Serialize one normalized event into a bounded UTF-8 SSE frame."""

        data = json.dumps(
            event.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        frame = f"id: {event.sequence}\nevent: {event.event_type.value}\ndata: {data}\n\n"
        if len(frame.encode("utf-8")) > self.settings.max_event_bytes:
            raise self._error(
                status_code=500,
                code=STREAM_PROBLEM_EVENT_BYTES,
                message="A text-stream event exceeded the configured byte limit.",
                retryable=False,
            )
        return frame

    def has_session(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._entries

    @property
    def session_count(self) -> int:
        with self._lock:
            self._cleanup_inactive_locked()
            return len(self._entries)

    def _queue_result_locked(
        self,
        entry: _TransportEntry,
        result: RealtimeTextStreamCallbackResult,
    ) -> None:
        if not result.accepted or result.event is None:
            return
        event = result.event
        # Validate the exact outgoing frame before retaining it.
        try:
            self.serialize_sse(event)
        except RealtimeTextStreamTransportError:
            self._replace_with_transport_failure_locked(
                entry,
                code=STREAM_PROBLEM_EVENT_BYTES,
                message="A text-stream event exceeded the configured byte limit.",
            )
            return

        try:
            entry.events.put_nowait(event)
        except Full:
            self._replace_with_transport_failure_locked(
                entry,
                code=STREAM_PROBLEM_EVENT_BUFFER,
                message="The text-stream event buffer reached its configured limit.",
            )
            return

        entry.last_activity_at = self._now()
        if event.terminal is not None:
            entry.terminal_queued = True
            entry.input_text = ""

    def _replace_with_transport_failure_locked(
        self,
        entry: _TransportEntry,
        *,
        code: str,
        message: str,
    ) -> None:
        while True:
            try:
                entry.events.get_nowait()
            except Empty:
                break
        if entry.service.session.active_turn_id is None:
            return
        failure = entry.service.fail(
            turn_id=entry.service.session.active_turn_id,
            public_error_code=code,
            safe_message=message,
            retryable=True,
        )
        if failure.event is not None and failure.event.terminal is not None:
            # A transport-limit failure must itself remain deliverable. Do not
            # repeat the partial generated text in this fallback terminal.
            terminal = failure.event.terminal.model_copy(update={"final_text": ""})
            safe_event = failure.event.model_copy(update={"terminal": terminal})
            self.serialize_sse(safe_event)
            entry.events.put_nowait(safe_event)
            entry.terminal_queued = True
            entry.input_text = ""
            entry.last_activity_at = self._now()

    def _cleanup_inactive_locked(self) -> None:
        current_time = self._now()
        expired: list[tuple[str, RealtimeTextStreamProblem]] = []
        for session_id, entry in self._entries.items():
            if entry.consumer_attached:
                continue
            if current_time - entry.created_at >= self.settings.max_duration_seconds:
                expired.append(
                    (
                        session_id,
                        RealtimeTextStreamProblem(
                            code=STREAM_PROBLEM_DURATION,
                            message="The text stream expired before it was consumed.",
                            retryable=True,
                        ),
                    )
                )
            elif current_time - entry.last_activity_at >= self.settings.idle_ttl_seconds:
                expired.append(
                    (
                        session_id,
                        RealtimeTextStreamProblem(
                            code=STREAM_PROBLEM_IDLE_TIMEOUT,
                            message="The text stream expired after an idle timeout.",
                            retryable=True,
                        ),
                    )
                )
        for session_id, problem in expired:
            entry = self._entries.get(session_id)
            if entry is not None:
                entry.service.close(turn_id=entry.service.session.active_turn_id)
            self._remove_locked(session_id, problem)

    def _entry_locked(self, session_id: str) -> _TransportEntry:
        entry = self._entries.get(session_id)
        if entry is not None:
            return entry
        remembered = self._removed.get(session_id)
        if remembered is not None:
            raise RealtimeTextStreamTransportError(status_code=410, problem=remembered)
        raise self._error(
            status_code=404,
            code=STREAM_PROBLEM_NOT_FOUND,
            message="The text-stream session was not found.",
            retryable=False,
        )

    def _active_turn_id(self, entry: _TransportEntry) -> str:
        turn_id = entry.service.session.active_turn_id
        if turn_id is None:
            raise self._error(
                status_code=409,
                code="stream_not_active",
                message="The text-stream session has no active turn.",
                retryable=False,
            )
        return turn_id

    def _remove_locked(
        self,
        session_id: str,
        problem: RealtimeTextStreamProblem,
    ) -> None:
        entry = self._entries.pop(session_id, None)
        if entry is not None:
            entry.input_text = ""
        self._removed[session_id] = problem
        self._producer_handles.pop(session_id, None)
        self._removed_order.append(session_id)
        while len(self._removed_order) > self.settings.max_sessions:
            oldest = self._removed_order.pop(0)
            self._removed.pop(oldest, None)

    @staticmethod
    def _error(
        *,
        status_code: int,
        code: str,
        message: str,
        retryable: bool,
    ) -> RealtimeTextStreamTransportError:
        return RealtimeTextStreamTransportError(
            status_code=status_code,
            problem=RealtimeTextStreamProblem(
                code=code,
                message=message,
                retryable=retryable,
            ),
        )

    def _start_producer_locked(
        self,
        entry: _TransportEntry,
        started: RealtimeTextStreamCallbackResult,
    ) -> None:
        if self._producer is None or started.turn is None:
            return
        session_id = started.session.session_id
        producer_start, handle = self._producer.start_stream(
            session_id=session_id,
            turn_id=started.turn.turn_id,
            input_text=entry.input_text,
            callbacks=self,
        )
        if handle is not None:
            self._producer_handles[session_id] = handle
        if not getattr(producer_start, "accepted", False):
            result = entry.service.fail(
                turn_id=started.turn.turn_id,
                public_error_code=str(
                    getattr(producer_start, "status", "framework_text_stream_unavailable")
                ),
                safe_message=str(
                    getattr(
                        producer_start,
                        "safe_message",
                        "The framework text stream is unavailable.",
                    )
                ),
                retryable=True,
            )
            self._queue_result_locked(entry, result)
