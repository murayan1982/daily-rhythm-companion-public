from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.models.realtime_text_stream_transport import (
    RealtimeTextStreamCancelResponse,
    RealtimeTextStreamCreateRequest,
    RealtimeTextStreamCreateResponse,
)
from app.config import load_config
from app.services.framework_realtime_text_stream_adapter import (
    FrameworkRealtimeTextStreamAdapter,
)
from app.services.realtime_text_stream_transport import (
    RealtimeTextStreamTransportError,
    RealtimeTextStreamTransportRegistry,
)

router = APIRouter(prefix="/realtime/text", tags=["realtime-text"])


def _create_stream_registry() -> RealtimeTextStreamTransportRegistry:
    config = load_config()
    producer = (
        FrameworkRealtimeTextStreamAdapter(config)
        if config.realtime_text_stream_framework_enabled
        else None
    )
    return RealtimeTextStreamTransportRegistry(config=config, producer=producer)


_stream_registry = _create_stream_registry()


@router.post(
    "/sessions",
    response_model=RealtimeTextStreamCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_realtime_text_session(
    request: RealtimeTextStreamCreateRequest,
) -> RealtimeTextStreamCreateResponse:
    """Create one bounded provider-free stream session and active turn."""

    try:
        started = _stream_registry.create_session(input_text=request.input_text)
    except RealtimeTextStreamTransportError as exc:
        _raise_transport_problem(exc)
    if started.turn is None:
        raise AssertionError("accepted stream start is missing its turn")

    session_id = started.session.session_id
    return RealtimeTextStreamCreateResponse(
        session=started.session,
        turn=started.turn,
        events_path=f"/realtime/text/sessions/{session_id}/events",
        cancel_path=f"/realtime/text/sessions/{session_id}/cancel",
        idle_ttl_seconds=_stream_registry.settings.idle_ttl_seconds,
        max_duration_seconds=_stream_registry.settings.max_duration_seconds,
        max_pending_events=_stream_registry.settings.max_pending_events,
        max_event_bytes=_stream_registry.settings.max_event_bytes,
    )


@router.get("/sessions/{session_id}/events")
def stream_realtime_text_events(
    session_id: str,
    request: Request,
) -> StreamingResponse:
    """Attach the single SSE consumer and stream normalized RT-4 events."""

    try:
        _stream_registry.acquire_consumer(session_id)
    except RealtimeTextStreamTransportError as exc:
        _raise_transport_problem(exc)

    return StreamingResponse(
        _iter_realtime_text_events(request=request, session_id=session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post(
    "/sessions/{session_id}/cancel",
    response_model=RealtimeTextStreamCancelResponse,
)
def cancel_realtime_text_session(session_id: str) -> RealtimeTextStreamCancelResponse:
    """Request and terminalize cooperative cancellation at the DRC boundary."""

    try:
        operation = _stream_registry.request_cancel(session_id)
    except RealtimeTextStreamTransportError as exc:
        _raise_transport_problem(exc)

    result = operation.final_result
    return RealtimeTextStreamCancelResponse(
        accepted=result.accepted,
        session_id=result.session.session_id,
        turn_id=result.turn.turn_id if result.turn is not None else None,
        state=result.session.state,
        terminal=result.event is not None and result.event.terminal is not None,
        safe_message=(result.event.safe_message if result.event is not None else ""),
    )


async def _iter_realtime_text_events(
    *,
    request: Request,
    session_id: str,
) -> AsyncIterator[str]:
    terminal_seen = False
    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                _stream_registry.enforce_timeouts(session_id)
                event = await _stream_registry.next_event(session_id)
            except RealtimeTextStreamTransportError:
                break
            if event is None:
                continue
            yield _stream_registry.serialize_sse(event)
            if event.terminal is not None:
                terminal_seen = True
                break
    finally:
        _stream_registry.release_consumer(
            session_id,
            terminal_seen=terminal_seen,
        )


def _raise_transport_problem(exc: RealtimeTextStreamTransportError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail=exc.problem.model_dump(),
    ) from exc
