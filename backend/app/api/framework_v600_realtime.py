from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.responses import JSONResponse

from app.models.framework_v600_realtime import (
    FrameworkV600DiagnosticsSnapshot,
    FrameworkV600InterruptResult,
    FrameworkV600OpenResult,
    FrameworkV600TurnResult,
)
from app.models.framework_v600_realtime_api import (
    FrameworkV600RealtimeApiProblem,
    FrameworkV600RealtimeInterruptRequest,
    FrameworkV600RealtimeTurnRequest,
)
from app.services.framework_v600_realtime_api_registry import (
    FrameworkV600RealtimeApiError,
    FrameworkV600RealtimeApiRegistry,
)

class FrameworkV600SafeValidationRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], object]:
        original_route_handler = super().get_route_handler()

        async def safe_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError:
                problem = FrameworkV600RealtimeApiProblem(
                    code="request_validation_failed",
                    message="Request validation failed.",
                    retryable=False,
                )
                return JSONResponse(
                    status_code=422,
                    content={"detail": problem.model_dump()},
                )

        return safe_route_handler


router = APIRouter(
    prefix="/realtime/framework-v6/provider-free",
    tags=["framework-v6-provider-free-realtime"],
    route_class=FrameworkV600SafeValidationRoute,
)

_registry = FrameworkV600RealtimeApiRegistry()


def get_framework_v600_realtime_registry() -> FrameworkV600RealtimeApiRegistry:
    return _registry


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    response_model=FrameworkV600OpenResult,
)
def create_framework_v600_realtime_session(
    registry: FrameworkV600RealtimeApiRegistry = Depends(get_framework_v600_realtime_registry),
) -> FrameworkV600OpenResult:
    try:
        return registry.create_session()
    except FrameworkV600RealtimeApiError as error:
        _raise_problem(error)


@router.post(
    "/sessions/{session_id}/turns",
    response_model=FrameworkV600TurnResult,
)
async def run_framework_v600_realtime_turn(
    session_id: str,
    request: FrameworkV600RealtimeTurnRequest,
    registry: FrameworkV600RealtimeApiRegistry = Depends(get_framework_v600_realtime_registry),
) -> FrameworkV600TurnResult:
    try:
        return await registry.run_turn(session_id=session_id, input_text=request.input_text)
    except FrameworkV600RealtimeApiError as error:
        _raise_problem(error)


@router.post(
    "/sessions/{session_id}/interrupt",
    response_model=FrameworkV600InterruptResult,
)
def interrupt_framework_v600_realtime_session(
    session_id: str,
    request: FrameworkV600RealtimeInterruptRequest,
    registry: FrameworkV600RealtimeApiRegistry = Depends(get_framework_v600_realtime_registry),
) -> FrameworkV600InterruptResult:
    try:
        return registry.interrupt(
            session_id=session_id,
            scope=request.scope,
            reason=request.reason,
        )
    except FrameworkV600RealtimeApiError as error:
        _raise_problem(error)


@router.get(
    "/sessions/{session_id}/diagnostics",
    response_model=FrameworkV600DiagnosticsSnapshot,
)
def get_framework_v600_realtime_diagnostics(
    session_id: str,
    registry: FrameworkV600RealtimeApiRegistry = Depends(get_framework_v600_realtime_registry),
) -> FrameworkV600DiagnosticsSnapshot:
    try:
        return registry.diagnostics(session_id=session_id)
    except FrameworkV600RealtimeApiError as error:
        _raise_problem(error)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def close_framework_v600_realtime_session(
    session_id: str,
    registry: FrameworkV600RealtimeApiRegistry = Depends(get_framework_v600_realtime_registry),
) -> Response:
    registry.close_session(session_id=session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _raise_problem(error: FrameworkV600RealtimeApiError) -> None:
    raise HTTPException(
        status_code=error.status_code,
        detail=error.problem.model_dump(),
    )
