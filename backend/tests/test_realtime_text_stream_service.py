from __future__ import annotations

import pytest

from app.models.realtime_text_stream import (
    RealtimeTextStreamCallbackReason,
    RealtimeTextStreamEventType,
    RealtimeTextStreamState,
    RealtimeTextStreamTerminalOutcome,
)
from app.services.realtime_text_stream_service import RealtimeTextStreamService


def _ids(*values: str):
    iterator = iter(values)
    return lambda: next(iterator)


def test_configured_limits_cannot_weaken_public_model_bounds() -> None:
    with pytest.raises(ValueError, match="max_chunk_chars"):
        RealtimeTextStreamService(max_chunk_chars=513)
    with pytest.raises(ValueError, match="max_output_chars"):
        RealtimeTextStreamService(max_output_chars=4097)


def test_start_turn_exposes_provider_neutral_soft_cancel_capability() -> None:
    service = RealtimeTextStreamService(
        session_id="session-1",
        id_factory=_ids("turn-1"),
    )

    result = service.start_turn()

    assert result.accepted is True
    assert result.reason is RealtimeTextStreamCallbackReason.ACCEPTED
    assert result.event is not None
    assert result.event.event_type is RealtimeTextStreamEventType.STREAM_STARTED
    assert result.event.sequence == 1
    assert result.event.state is RealtimeTextStreamState.STREAMING
    assert result.session.active_turn_id == "turn-1"
    assert result.session.cancel_mode == "cooperative"
    assert result.session.hard_cancel_supported is False


def test_second_turn_cannot_replace_an_active_turn() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")

    rejected = service.start_turn(turn_id="turn-2")

    assert rejected.accepted is False
    assert rejected.reason is RealtimeTextStreamCallbackReason.ACTIVE_TURN
    assert rejected.session.active_turn_id == "turn-1"
    assert rejected.session.last_sequence == 1


def test_chunks_are_bounded_and_sequences_are_monotonic() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    started = service.start_turn(turn_id="turn-1")
    first = service.append_chunk(turn_id="turn-1", text="こん")
    second = service.append_chunk(turn_id="turn-1", text="にちは")
    completed = service.complete(turn_id="turn-1")

    assert [
        started.event.sequence,
        first.event.sequence,
        second.event.sequence,
        completed.event.sequence,
    ] == [1, 2, 3, 4]
    assert first.event.chunk is not None
    assert first.event.chunk.text == "こん"
    assert first.event.chunk.output_char_count == 2
    assert second.event.chunk is not None
    assert second.event.chunk.output_char_count == 5
    assert completed.event.terminal is not None
    assert completed.event.terminal.outcome is RealtimeTextStreamTerminalOutcome.COMPLETED
    assert completed.event.terminal.final_text == "こんにちは"
    assert completed.event.terminal.output_char_count == 5
    assert completed.session.active_turn_id is None


def test_cancel_request_rejects_late_chunks_and_finishes_cancelled() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")
    service.append_chunk(turn_id="turn-1", text="partial")

    requested = service.request_cancel(turn_id="turn-1")
    late = service.append_chunk(turn_id="turn-1", text="late")
    cancelled = service.cancel(turn_id="turn-1")

    assert requested.event is not None
    assert requested.event.event_type is RealtimeTextStreamEventType.CANCEL_REQUESTED
    assert requested.event.sequence == 3
    assert requested.session.state is RealtimeTextStreamState.CANCEL_REQUESTED
    assert late.accepted is False
    assert late.reason is RealtimeTextStreamCallbackReason.CANCEL_REQUESTED
    assert late.session.last_sequence == 3
    assert cancelled.event is not None
    assert cancelled.event.sequence == 4
    assert cancelled.event.terminal is not None
    assert cancelled.event.terminal.outcome is RealtimeTextStreamTerminalOutcome.CANCELLED
    assert cancelled.event.terminal.final_text == "partial"
    assert cancelled.session.hard_cancel_supported is False


def test_complete_after_cancel_request_resolves_to_cancelled() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")
    service.request_cancel(turn_id="turn-1")

    terminal = service.complete(turn_id="turn-1")

    assert terminal.event is not None
    assert terminal.event.event_type is RealtimeTextStreamEventType.STREAM_CANCELLED
    assert terminal.event.terminal is not None
    assert terminal.event.terminal.outcome is RealtimeTextStreamTerminalOutcome.CANCELLED


def test_oversized_chunk_fails_without_storing_unbounded_text() -> None:
    service = RealtimeTextStreamService(
        session_id="session-1",
        max_chunk_chars=4,
        max_output_chars=20,
    )
    service.start_turn(turn_id="turn-1")

    failed = service.append_chunk(turn_id="turn-1", text="12345")

    assert failed.event is not None
    assert failed.event.event_type is RealtimeTextStreamEventType.STREAM_FAILED
    assert failed.event.terminal is not None
    assert failed.event.terminal.outcome is RealtimeTextStreamTerminalOutcome.FAILED
    assert failed.event.terminal.public_error_code == "chunk_limit_exceeded"
    assert failed.event.terminal.final_text == ""
    assert failed.event.terminal.output_char_count == 0


def test_output_limit_fails_before_overflowing_aggregate() -> None:
    service = RealtimeTextStreamService(
        session_id="session-1",
        max_chunk_chars=8,
        max_output_chars=5,
    )
    service.start_turn(turn_id="turn-1")
    service.append_chunk(turn_id="turn-1", text="abc")

    failed = service.append_chunk(turn_id="turn-1", text="def")

    assert failed.event is not None
    assert failed.event.terminal is not None
    assert failed.event.terminal.public_error_code == "output_limit_exceeded"
    assert failed.event.terminal.final_text == "abc"
    assert failed.event.terminal.output_char_count == 3


def test_callback_after_terminal_is_rejected_as_stale() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")
    completed = service.complete(turn_id="turn-1")

    stale = service.append_chunk(turn_id="turn-1", text="late")

    assert stale.accepted is False
    assert stale.reason is RealtimeTextStreamCallbackReason.STALE_TURN
    assert completed.event is not None
    assert stale.session.last_sequence == completed.event.sequence


def test_old_turn_callback_is_rejected_after_a_new_turn_starts() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-old")
    service.complete(turn_id="turn-old")
    service.start_turn(turn_id="turn-new")

    stale = service.append_chunk(turn_id="turn-old", text="late")
    current = service.append_chunk(turn_id="turn-new", text="ok")

    assert stale.accepted is False
    assert stale.reason is RealtimeTextStreamCallbackReason.STALE_TURN
    assert stale.session.last_sequence == 3
    assert current.accepted is True
    assert current.event is not None
    assert current.event.sequence == 4
    assert current.event.chunk is not None
    assert current.event.chunk.text == "ok"


def test_failure_normalizes_public_code_and_safe_message() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")

    failed = service.fail(
        turn_id="turn-1",
        public_error_code=" Provider Error! ",
        safe_message="  Temporary\nstream failure.  ",
        retryable=True,
    )

    assert failed.event is not None
    assert failed.event.terminal is not None
    assert failed.event.terminal.public_error_code == "providererror"
    assert failed.event.terminal.safe_message == "Temporary stream failure."
    assert failed.event.terminal.retryable is True


def test_close_terminalizes_active_turn_and_rejects_future_callbacks() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")
    service.append_chunk(turn_id="turn-1", text="partial")

    closed = service.close(turn_id="turn-1")
    late = service.append_chunk(turn_id="turn-1", text="late")

    assert closed.event is not None
    assert closed.event.event_type is RealtimeTextStreamEventType.STREAM_CLOSED
    assert closed.event.terminal is not None
    assert closed.event.terminal.outcome is RealtimeTextStreamTerminalOutcome.CLOSED
    assert closed.event.terminal.final_text == "partial"
    assert closed.session.is_closed is True
    assert closed.session.active_turn_id is None
    assert late.accepted is False
    assert late.reason is RealtimeTextStreamCallbackReason.SESSION_CLOSED
    assert late.session.last_sequence == closed.event.sequence


def test_empty_chunk_is_rejected_without_advancing_sequence() -> None:
    service = RealtimeTextStreamService(session_id="session-1")
    service.start_turn(turn_id="turn-1")

    empty = service.append_chunk(turn_id="turn-1", text="")

    assert empty.accepted is False
    assert empty.reason is RealtimeTextStreamCallbackReason.EMPTY_CHUNK
    assert empty.session.last_sequence == 1
    assert empty.turn is not None
    assert empty.turn.chunk_count == 0
    assert empty.turn.output_char_count == 0
