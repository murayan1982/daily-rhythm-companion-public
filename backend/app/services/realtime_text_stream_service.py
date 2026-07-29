from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from uuid import uuid4

from app.models.realtime_text_stream import (
    RealtimeTextStreamCallbackReason,
    RealtimeTextStreamCallbackResult,
    RealtimeTextStreamChunk,
    RealtimeTextStreamEvent,
    RealtimeTextStreamEventType,
    RealtimeTextStreamSession,
    RealtimeTextStreamState,
    RealtimeTextStreamTerminal,
    RealtimeTextStreamTerminalOutcome,
    RealtimeTextStreamTurn,
    REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS,
    REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS,
    REALTIME_TEXT_STREAM_MAX_SAFE_MESSAGE_CHARS,
)

DEFAULT_MAX_STREAM_CHUNK_CHARS = REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS
DEFAULT_MAX_STREAM_OUTPUT_CHARS = REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS


class RealtimeTextStreamService:
    """Deterministic provider-neutral text-stream state machine.

    RT-4b accepts caller-supplied fake chunks only. It does not own a route,
    transport, Framework session, provider client, worker, or background task.
    """

    def __init__(
        self,
        *,
        session_id: str | None = None,
        id_factory: Callable[[], str] | None = None,
        max_chunk_chars: int = DEFAULT_MAX_STREAM_CHUNK_CHARS,
        max_output_chars: int = DEFAULT_MAX_STREAM_OUTPUT_CHARS,
    ) -> None:
        if not 0 < max_chunk_chars <= REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS:
            raise ValueError(
                "max_chunk_chars must be between 1 and "
                f"{REALTIME_TEXT_STREAM_MAX_CHUNK_CHARS}"
            )
        if not 0 < max_output_chars <= REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS:
            raise ValueError(
                "max_output_chars must be between 1 and "
                f"{REALTIME_TEXT_STREAM_MAX_OUTPUT_CHARS}"
            )

        self._id_factory = id_factory or (lambda: uuid4().hex)
        self._max_chunk_chars = max_chunk_chars
        self._max_output_chars = max_output_chars
        self._lock = RLock()
        self._session_id = session_id or self._next_id("session")
        self._state = RealtimeTextStreamState.IDLE
        self._sequence = 0
        self._is_closed = False
        self._active_turn_id: str | None = None
        self._turn: RealtimeTextStreamTurn | None = None
        self._output_parts: list[str] = []

    @property
    def session(self) -> RealtimeTextStreamSession:
        with self._lock:
            return self._session_snapshot()

    @property
    def turn(self) -> RealtimeTextStreamTurn | None:
        with self._lock:
            return self._turn.model_copy(deep=True) if self._turn is not None else None

    @property
    def max_chunk_chars(self) -> int:
        return self._max_chunk_chars

    @property
    def max_output_chars(self) -> int:
        return self._max_output_chars

    def start_turn(
        self, *, turn_id: str | None = None
    ) -> RealtimeTextStreamCallbackResult:
        """Start one new turn unless the stream session is closed."""

        with self._lock:
            if self._is_closed:
                return self._rejected(RealtimeTextStreamCallbackReason.SESSION_CLOSED)
            if self._active_turn_id is not None:
                return self._rejected(RealtimeTextStreamCallbackReason.ACTIVE_TURN)

            resolved_turn_id = turn_id or self._next_id("turn")
            self._active_turn_id = resolved_turn_id
            self._state = RealtimeTextStreamState.STREAMING
            self._output_parts = []
            self._turn = RealtimeTextStreamTurn(
                session_id=self._session_id,
                turn_id=resolved_turn_id,
                state=self._state,
            )
            event = self._event(
                event_type=RealtimeTextStreamEventType.STREAM_STARTED,
                turn_id=resolved_turn_id,
                state=self._state,
            )
            return self._accepted(event)

    def append_chunk(
        self,
        *,
        turn_id: str,
        text: str,
    ) -> RealtimeTextStreamCallbackResult:
        """Append one bounded callback chunk to the active turn."""

        with self._lock:
            rejected = self._reject_callback(turn_id)
            if rejected is not None:
                return rejected
            if self._state is RealtimeTextStreamState.CANCEL_REQUESTED:
                return self._rejected(RealtimeTextStreamCallbackReason.CANCEL_REQUESTED)
            if text == "":
                return self._rejected(RealtimeTextStreamCallbackReason.EMPTY_CHUNK)

            if len(text) > self._max_chunk_chars:
                return self._terminal_result(
                    outcome=RealtimeTextStreamTerminalOutcome.FAILED,
                    event_type=RealtimeTextStreamEventType.STREAM_FAILED,
                    public_error_code="chunk_limit_exceeded",
                    safe_message="The response chunk exceeded the configured text limit.",
                    retryable=True,
                )

            current_text = self._output_text()
            if len(current_text) + len(text) > self._max_output_chars:
                return self._terminal_result(
                    outcome=RealtimeTextStreamTerminalOutcome.FAILED,
                    event_type=RealtimeTextStreamEventType.STREAM_FAILED,
                    public_error_code="output_limit_exceeded",
                    safe_message="The streamed response exceeded the configured output limit.",
                    retryable=True,
                )

            self._output_parts.append(text)
            if self._turn is None:  # guarded by _reject_callback
                raise AssertionError("active stream turn is missing")
            self._turn = self._turn.model_copy(
                update={
                    "chunk_count": self._turn.chunk_count + 1,
                    "output_char_count": len(self._output_text()),
                }
            )
            sequence = self._next_sequence()
            chunk = RealtimeTextStreamChunk(
                sequence=sequence,
                text=text,
                output_char_count=self._turn.output_char_count,
            )
            event = RealtimeTextStreamEvent(
                event_type=RealtimeTextStreamEventType.STREAM_CHUNK,
                session_id=self._session_id,
                turn_id=turn_id,
                sequence=sequence,
                state=self._state,
                chunk=chunk,
            )
            return self._accepted(event)

    def request_cancel(self, *, turn_id: str) -> RealtimeTextStreamCallbackResult:
        """Record one cooperative cancellation request without claiming hard cancel."""

        with self._lock:
            rejected = self._reject_callback(turn_id)
            if rejected is not None:
                return rejected
            if self._state is RealtimeTextStreamState.CANCEL_REQUESTED:
                return self._rejected(RealtimeTextStreamCallbackReason.CANCEL_REQUESTED)

            self._state = RealtimeTextStreamState.CANCEL_REQUESTED
            if self._turn is None:
                raise AssertionError("active stream turn is missing")
            self._turn = self._turn.model_copy(
                update={
                    "state": self._state,
                    "cancel_requested": True,
                }
            )
            event = self._event(
                event_type=RealtimeTextStreamEventType.CANCEL_REQUESTED,
                turn_id=turn_id,
                state=self._state,
                safe_message="Cooperative stream cancellation was requested.",
            )
            return self._accepted(event)

    def complete(self, *, turn_id: str) -> RealtimeTextStreamCallbackResult:
        """Complete the active turn, or cancel it when cancellation already won."""

        with self._lock:
            rejected = self._reject_callback(turn_id)
            if rejected is not None:
                return rejected
            if self._state is RealtimeTextStreamState.CANCEL_REQUESTED:
                return self._terminal_result(
                    outcome=RealtimeTextStreamTerminalOutcome.CANCELLED,
                    event_type=RealtimeTextStreamEventType.STREAM_CANCELLED,
                    safe_message="The streamed response stopped after a cancellation request.",
                    retryable=True,
                )
            return self._terminal_result(
                outcome=RealtimeTextStreamTerminalOutcome.COMPLETED,
                event_type=RealtimeTextStreamEventType.STREAM_COMPLETED,
            )

    def cancel(self, *, turn_id: str) -> RealtimeTextStreamCallbackResult:
        """Mark the active turn cancelled after cooperative stop handling."""

        with self._lock:
            rejected = self._reject_callback(turn_id)
            if rejected is not None:
                return rejected
            return self._terminal_result(
                outcome=RealtimeTextStreamTerminalOutcome.CANCELLED,
                event_type=RealtimeTextStreamEventType.STREAM_CANCELLED,
                safe_message="The streamed response was cancelled cooperatively.",
                retryable=True,
            )

    def fail(
        self,
        *,
        turn_id: str,
        public_error_code: str = "stream_failed",
        safe_message: str = "The streamed response failed.",
        retryable: bool = False,
    ) -> RealtimeTextStreamCallbackResult:
        """Finish the active turn with one public-safe failure result."""

        with self._lock:
            rejected = self._reject_callback(turn_id)
            if rejected is not None:
                return rejected
            return self._terminal_result(
                outcome=RealtimeTextStreamTerminalOutcome.FAILED,
                event_type=RealtimeTextStreamEventType.STREAM_FAILED,
                public_error_code=self._normalize_error_code(public_error_code),
                safe_message=self._normalize_safe_message(safe_message),
                retryable=retryable,
            )

    def close(self, *, turn_id: str | None = None) -> RealtimeTextStreamCallbackResult:
        """Close the stream session and terminalize an active turn when present."""

        with self._lock:
            if self._is_closed:
                return self._rejected(RealtimeTextStreamCallbackReason.SESSION_CLOSED)
            if turn_id is not None and self._active_turn_id != turn_id:
                return self._rejected(RealtimeTextStreamCallbackReason.STALE_TURN)

            active_turn_id = self._active_turn_id
            self._is_closed = True
            self._state = RealtimeTextStreamState.CLOSED
            if self._turn is not None and active_turn_id is not None:
                self._turn = self._turn.model_copy(
                    update={
                        "state": self._state,
                        "terminal_outcome": RealtimeTextStreamTerminalOutcome.CLOSED,
                    }
                )

            sequence = self._next_sequence()
            terminal = RealtimeTextStreamTerminal(
                sequence=sequence,
                outcome=RealtimeTextStreamTerminalOutcome.CLOSED,
                final_text=self._output_text(),
                output_char_count=len(self._output_text()),
                safe_message="The text stream session was closed.",
                retryable=False,
            )
            event = RealtimeTextStreamEvent(
                event_type=RealtimeTextStreamEventType.STREAM_CLOSED,
                session_id=self._session_id,
                turn_id=active_turn_id,
                sequence=sequence,
                state=self._state,
                terminal=terminal,
                safe_message=terminal.safe_message,
            )
            self._active_turn_id = None
            return self._accepted(event)

    def _terminal_result(
        self,
        *,
        outcome: RealtimeTextStreamTerminalOutcome,
        event_type: RealtimeTextStreamEventType,
        public_error_code: str | None = None,
        safe_message: str = "",
        retryable: bool = False,
    ) -> RealtimeTextStreamCallbackResult:
        if self._turn is None or self._active_turn_id is None:
            return self._rejected(RealtimeTextStreamCallbackReason.NO_ACTIVE_TURN)

        state = RealtimeTextStreamState(outcome.value)
        self._state = state
        self._turn = self._turn.model_copy(
            update={
                "state": state,
                "output_char_count": len(self._output_text()),
                "terminal_outcome": outcome,
            }
        )
        sequence = self._next_sequence()
        terminal = RealtimeTextStreamTerminal(
            sequence=sequence,
            outcome=outcome,
            final_text=self._output_text(),
            output_char_count=len(self._output_text()),
            public_error_code=public_error_code,
            safe_message=safe_message,
            retryable=retryable,
        )
        event = RealtimeTextStreamEvent(
            event_type=event_type,
            session_id=self._session_id,
            turn_id=self._active_turn_id,
            sequence=sequence,
            state=state,
            terminal=terminal,
            safe_message=safe_message,
        )
        self._active_turn_id = None
        return self._accepted(event)

    def _reject_callback(
        self,
        turn_id: str,
    ) -> RealtimeTextStreamCallbackResult | None:
        if self._is_closed:
            return self._rejected(RealtimeTextStreamCallbackReason.SESSION_CLOSED)
        if self._active_turn_id is None:
            if self._turn is not None and self._turn.turn_id == turn_id:
                return self._rejected(RealtimeTextStreamCallbackReason.STALE_TURN)
            return self._rejected(RealtimeTextStreamCallbackReason.NO_ACTIVE_TURN)
        if self._active_turn_id != turn_id:
            return self._rejected(RealtimeTextStreamCallbackReason.STALE_TURN)
        return None

    def _event(
        self,
        *,
        event_type: RealtimeTextStreamEventType,
        turn_id: str | None,
        state: RealtimeTextStreamState,
        safe_message: str = "",
    ) -> RealtimeTextStreamEvent:
        return RealtimeTextStreamEvent(
            event_type=event_type,
            session_id=self._session_id,
            turn_id=turn_id,
            sequence=self._next_sequence(),
            state=state,
            safe_message=safe_message,
        )

    def _accepted(
        self, event: RealtimeTextStreamEvent
    ) -> RealtimeTextStreamCallbackResult:
        return RealtimeTextStreamCallbackResult(
            accepted=True,
            reason=RealtimeTextStreamCallbackReason.ACCEPTED,
            event=event,
            session=self._session_snapshot(),
            turn=self._turn.model_copy(deep=True) if self._turn is not None else None,
        )

    def _rejected(
        self,
        reason: RealtimeTextStreamCallbackReason,
    ) -> RealtimeTextStreamCallbackResult:
        return RealtimeTextStreamCallbackResult(
            accepted=False,
            reason=reason,
            session=self._session_snapshot(),
            turn=self._turn.model_copy(deep=True) if self._turn is not None else None,
        )

    def _session_snapshot(self) -> RealtimeTextStreamSession:
        return RealtimeTextStreamSession(
            session_id=self._session_id,
            state=self._state,
            active_turn_id=self._active_turn_id,
            last_sequence=self._sequence,
            is_closed=self._is_closed,
            cancel_mode="cooperative",
            hard_cancel_supported=False,
        )

    def _next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    def _next_id(self, label: str) -> str:
        value = str(self._id_factory()).strip()
        if not value:
            raise ValueError(f"{label} id_factory returned an empty value")
        return value

    def _output_text(self) -> str:
        return "".join(self._output_parts)

    @staticmethod
    def _normalize_error_code(value: str) -> str:
        normalized = "".join(
            character
            for character in value.strip().lower()
            if character.isascii()
            and (character.isalnum() or character in {"_", "-", "."})
        )
        return normalized[:64] or "stream_failed"

    @staticmethod
    def _normalize_safe_message(value: str) -> str:
        normalized = " ".join(value.split())
        return (
            normalized[:REALTIME_TEXT_STREAM_MAX_SAFE_MESSAGE_CHARS]
            or "The streamed response failed."
        )
