from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import Event, Thread
import importlib
import inspect
import os
import re
from typing import Any, Protocol

from app.config import AppConfig
from app.services.framework_text_chat_import_setup import (
    framework_text_chat_import_context,
)


class RealtimeTextStreamProducerCallbacks(Protocol):
    def publish_chunk(self, *, session_id: str, turn_id: str, text: str) -> Any:
        """Publish one bounded DRC stream chunk."""

    def complete_session(self, *, session_id: str, turn_id: str) -> Any:
        """Complete one DRC stream turn."""

    def fail_session(
        self,
        *,
        session_id: str,
        turn_id: str,
        public_error_code: str,
        safe_message: str,
        retryable: bool,
    ) -> Any:
        """Fail one DRC stream turn with public-safe details."""


@dataclass(frozen=True)
class FrameworkRealtimeTextStreamStart:
    """Public-safe metadata for one adapter start request."""

    accepted: bool
    status: str
    provider_call_attempted: bool = False
    safe_message: str = ""


class FrameworkRealtimeTextStreamHandle:
    """Cooperative handle for a root-public FW text stream."""

    def __init__(self) -> None:
        self._cancel_requested = Event()
        self._session: Any | None = None

    @property
    def cancel_requested(self) -> bool:
        return self._cancel_requested.is_set()

    def bind_session(self, session: Any) -> None:
        self._session = session

    def request_interrupt(self) -> bool:
        self._cancel_requested.set()
        session = self._session
        interrupt = getattr(session, "interrupt", None) if session is not None else None
        if not callable(interrupt):
            return False
        interrupt()
        return True


class FrameworkRealtimeTextStreamAdapter:
    """Run RT-4d text streaming through FW root public text-chat APIs only."""

    def __init__(self, config: AppConfig, *, module_name: str = "framework") -> None:
        self._config = config
        self._module_name = module_name

    def start_stream(
        self,
        *,
        session_id: str,
        turn_id: str,
        input_text: str,
        callbacks: RealtimeTextStreamProducerCallbacks,
    ) -> tuple[FrameworkRealtimeTextStreamStart, FrameworkRealtimeTextStreamHandle | None]:
        project_root = self._framework_project_root()
        if project_root is None or not project_root.exists():
            return (
                FrameworkRealtimeTextStreamStart(
                    accepted=False,
                    status="blocked-framework-root-missing",
                    safe_message="Configured framework project root is missing.",
                ),
                None,
            )

        handle = FrameworkRealtimeTextStreamHandle()
        worker = Thread(
            target=self._run_stream,
            kwargs={
                "project_root": project_root,
                "session_id": session_id,
                "turn_id": turn_id,
                "input_text": input_text,
                "callbacks": callbacks,
                "handle": handle,
            },
            daemon=True,
            name="drc-rt4d-fw-text-stream",
        )
        worker.start()
        return (
            FrameworkRealtimeTextStreamStart(
                accepted=True,
                status="started",
                provider_call_attempted=True,
                safe_message="FW text stream started through root public APIs.",
            ),
            handle,
        )

    def _run_stream(
        self,
        *,
        project_root: Path,
        session_id: str,
        turn_id: str,
        input_text: str,
        callbacks: RealtimeTextStreamProducerCallbacks,
        handle: FrameworkRealtimeTextStreamHandle,
    ) -> None:
        session: Any | None = None
        try:
            with framework_text_chat_import_context(project_root):
                module = importlib.import_module(self._module_name)
                create_session = getattr(module, "create_text_chat_session", None)
                if not callable(create_session):
                    raise RuntimeError("create_text_chat_session is not available.")

                with _temporary_cwd(project_root):
                    session = self._create_session(create_session, project_root=project_root)
                    handle.bind_session(session)
                    ask_stream = getattr(session, "ask_stream", None)
                    if not callable(ask_stream):
                        raise RuntimeError(
                            "Framework text chat session does not expose ask_stream(text)."
                        )
                    for item in ask_stream(input_text):
                        if handle.cancel_requested:
                            break
                        text = _extract_chunk_text(item)
                        if not text:
                            continue
                        result = callbacks.publish_chunk(
                            session_id=session_id,
                            turn_id=turn_id,
                            text=text,
                        )
                        if not getattr(result, "accepted", False):
                            break
                    if handle.cancel_requested:
                        return
                    callbacks.complete_session(session_id=session_id, turn_id=turn_id)
        except Exception as exc:  # pragma: no cover - real FW failures are local.
            callbacks.fail_session(
                session_id=session_id,
                turn_id=turn_id,
                public_error_code="framework_text_stream_failed",
                safe_message=_sanitize_message(str(exc), project_root),
                retryable=True,
            )
        finally:
            _close_session(session)

    def _create_session(self, create_session: Any, *, project_root: Path) -> Any:
        signature = inspect.signature(create_session)
        candidate_values = {
            "preset": self._config.framework_preset,
            "preset_name": self._config.framework_preset,
            "preset_id": self._config.framework_preset,
            "character": self._config.framework_character,
            "character_name": self._config.framework_character,
            "character_id": self._config.framework_character,
            "project_root": str(project_root),
            "framework_project_root": str(project_root),
        }
        if any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        ):
            return create_session(
                preset=self._config.framework_preset,
                character=self._config.framework_character,
                project_root=str(project_root),
            )
        kwargs = {
            name: value
            for name, value in candidate_values.items()
            if name in signature.parameters
        }
        return create_session(**kwargs)

    def _framework_project_root(self) -> Path | None:
        configured = self._config.framework_project_root
        if not configured:
            return None
        return Path(configured).expanduser().resolve()


def _extract_chunk_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    for attr_name in ("text", "content", "message", "delta"):
        value = getattr(item, attr_name, None)
        if isinstance(value, str):
            return value
    if isinstance(item, dict):
        for key in ("text", "content", "message", "delta"):
            value = item.get(key)
            if isinstance(value, str):
                return value
    return ""


def _close_session(session: Any | None) -> None:
    if session is None:
        return
    for method_name in ("close", "dispose"):
        method = getattr(session, method_name, None)
        if callable(method):
            method()
            return


def _sanitize_message(message: str, project_root: Path) -> str:
    if not message:
        return "The framework text stream failed."
    safe = message.replace(str(project_root), "<configured-framework-root>")
    safe = safe.replace(str(project_root).replace("\\", "/"), "<configured-framework-root>")
    safe = re.sub(r"[A-Za-z]:[\\/][^\s:'\"]+", "<private-path>", safe)
    safe = re.sub(r"/(?:Users|home|mnt|tmp)/[^\s:'\"]+", "<private-path>", safe)
    safe = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "<redacted-api-key>", safe)
    safe = re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "<redacted-api-key>", safe)
    safe = re.sub(r"xai-[A-Za-z0-9_\-]{12,}", "<redacted-api-key>", safe)
    safe = " ".join(safe.split())
    return safe[:240] or "The framework text stream failed."


@contextmanager
def _temporary_cwd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)
