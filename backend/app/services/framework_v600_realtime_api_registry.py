from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from typing import Protocol

from app.models.framework_v600_realtime import (
    FrameworkV600DiagnosticsSnapshot,
    FrameworkV600InterruptResult,
    FrameworkV600OpenResult,
    FrameworkV600TurnResult,
)
from app.models.framework_v600_realtime_api import FrameworkV600RealtimeApiProblem
from app.services.framework_v600_realtime_session_adapter import (
    FrameworkV600RealtimeSessionAdapter,
)

MAX_SESSIONS = 8


class FrameworkV600RealtimeApiAdapter(Protocol):
    def open(self) -> FrameworkV600OpenResult:
        ...

    async def run_turn(self, *, input_text: str) -> FrameworkV600TurnResult:
        ...

    def interrupt(self, *, scope: str, reason: str) -> FrameworkV600InterruptResult:
        ...

    def diagnostics_snapshot(self) -> FrameworkV600DiagnosticsSnapshot | None:
        ...

    def close(self) -> FrameworkV600OpenResult:
        ...


class FrameworkV600RealtimeApiError(RuntimeError):
    def __init__(self, status_code: int, problem: FrameworkV600RealtimeApiProblem) -> None:
        super().__init__(problem.code)
        self.status_code = status_code
        self.problem = problem


AdapterFactory = Callable[[], FrameworkV600RealtimeApiAdapter]


def default_framework_v600_realtime_adapter_factory() -> FrameworkV600RealtimeApiAdapter:
    return FrameworkV600RealtimeSessionAdapter()


class FrameworkV600RealtimeApiRegistry:
    """Bounded process-local registry for provider-free FW v6 sessions."""

    def __init__(
        self,
        *,
        adapter_factory: AdapterFactory = default_framework_v600_realtime_adapter_factory,
    ) -> None:
        self._adapter_factory = adapter_factory
        self._sessions: dict[str, FrameworkV600RealtimeApiAdapter] = {}
        self._lock = RLock()

    def create_session(self) -> FrameworkV600OpenResult:
        with self._lock:
            if len(self._sessions) >= MAX_SESSIONS:
                raise _capacity_error()

        try:
            adapter = self._adapter_factory()
            result = adapter.open()
        except Exception:
            raise _unavailable_error()
        if not result.available or result.session_id is None:
            raise FrameworkV600RealtimeApiError(
                503,
                FrameworkV600RealtimeApiProblem(
                    code=result.public_error_code or "framework_v600_realtime_unavailable",
                    message=result.safe_message or "FW v6 provider-free realtime is unavailable.",
                    retryable=result.retryable,
                ),
            )

        with self._lock:
            if len(self._sessions) >= MAX_SESSIONS:
                adapter.close()
                raise _capacity_error()
            self._sessions[result.session_id] = adapter
        return result

    async def run_turn(self, *, session_id: str, input_text: str) -> FrameworkV600TurnResult:
        adapter = self._lookup(session_id)
        try:
            return await adapter.run_turn(input_text=input_text)
        except Exception:
            raise _unavailable_error()

    def interrupt(
        self,
        *,
        session_id: str,
        scope: str,
        reason: str,
    ) -> FrameworkV600InterruptResult:
        adapter = self._lookup(session_id)
        try:
            return adapter.interrupt(scope=scope, reason=reason)
        except Exception:
            raise _unavailable_error()

    def diagnostics(self, *, session_id: str) -> FrameworkV600DiagnosticsSnapshot:
        adapter = self._lookup(session_id)
        try:
            snapshot = adapter.diagnostics_snapshot()
        except Exception:
            raise FrameworkV600RealtimeApiError(
                503,
                FrameworkV600RealtimeApiProblem(
                    code="diagnostics_unavailable",
                    message="FW v6 provider-free diagnostics are unavailable.",
                    retryable=True,
                ),
            )
        if snapshot is None:
            raise FrameworkV600RealtimeApiError(
                503,
                FrameworkV600RealtimeApiProblem(
                    code="diagnostics_unavailable",
                    message="FW v6 provider-free diagnostics are unavailable.",
                    retryable=True,
                ),
            )
        return snapshot

    def close_session(self, *, session_id: str) -> None:
        with self._lock:
            adapter = self._sessions.pop(session_id, None)
        if adapter is not None:
            adapter.close()

    def _lookup(self, session_id: str) -> FrameworkV600RealtimeApiAdapter:
        with self._lock:
            adapter = self._sessions.get(session_id)
        if adapter is None:
            raise FrameworkV600RealtimeApiError(
                404,
                FrameworkV600RealtimeApiProblem(
                    code="session_not_found",
                    message="FW v6 provider-free session was not found.",
                    retryable=False,
                ),
            )
        return adapter


def _capacity_error() -> FrameworkV600RealtimeApiError:
    return FrameworkV600RealtimeApiError(
        429,
        FrameworkV600RealtimeApiProblem(
            code="session_capacity_reached",
            message="FW v6 provider-free session capacity has been reached.",
            retryable=True,
        ),
    )


def _unavailable_error() -> FrameworkV600RealtimeApiError:
    return FrameworkV600RealtimeApiError(
        503,
        FrameworkV600RealtimeApiProblem(
            code="framework_v600_realtime_unavailable",
            message="FW v6 provider-free realtime is unavailable.",
            retryable=True,
        ),
    )
