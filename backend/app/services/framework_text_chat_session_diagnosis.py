from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import importlib
import inspect
import os
import re
from typing import Any

from app.config import AppConfig
from app.services.framework_text_chat_import_setup import (
    framework_text_chat_import_context,
    framework_text_chat_import_layout_summary,
)
from app.services.framework_text_chat_provider_env_diagnosis import (
    classify_framework_text_chat_session_failure,
)


@dataclass(frozen=True)
class FrameworkTextChatSessionDiagnosisAttempt:
    """Public-safe result for one session creation diagnosis attempt."""

    attempt_name: str
    status: str
    cwd_shape: str
    exception_type: str | None
    safe_message: str
    session_created: bool
    has_session_info: bool
    failure_kind: str = "none"


@dataclass(frozen=True)
class FrameworkTextChatSessionDiagnosisResult:
    """Public-safe diagnosis result for framework session creation."""

    status: str
    module_name: str
    project_root_shape: str | None
    likely_cwd_dependency: bool
    attempts: list[FrameworkTextChatSessionDiagnosisAttempt]


class FrameworkTextChatSessionDiagnosisService:
    """Diagnose framework text chat session creation without sending messages.

    Day21 may call create_text_chat_session in controlled attempts. It must not
    call ask, ask_stream, provider APIs, STT/TTS, or Live2D/VTS runtime paths.

    Day24 keeps the configured framework import layout active for the whole
    session-creation attempt. This prevents a false ``ModuleNotFoundError`` when
    the public facade performs lazy top-level imports after ``import framework``.

    Day25 classifies failures such as ``provider-env-missing`` without
    exposing provider credential values.
    """

    def __init__(self, config: AppConfig, *, module_name: str = "framework") -> None:
        self._config = config
        self._module_name = module_name

    def run(self) -> FrameworkTextChatSessionDiagnosisResult:
        project_root = self._framework_project_root()
        if project_root is None:
            return FrameworkTextChatSessionDiagnosisResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape=None,
                likely_cwd_dependency=False,
                attempts=[
                    FrameworkTextChatSessionDiagnosisAttempt(
                        attempt_name="configured-root-missing",
                        status="unavailable",
                        cwd_shape="<current-working-directory>",
                        exception_type=None,
                        safe_message=(
                            "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured."
                        ),
                        session_created=False,
                        has_session_info=False,
                    )
                ],
            )

        if not project_root.exists():
            return FrameworkTextChatSessionDiagnosisResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                likely_cwd_dependency=False,
                attempts=[
                    FrameworkTextChatSessionDiagnosisAttempt(
                        attempt_name="configured-root-missing",
                        status="unavailable",
                        cwd_shape="<current-working-directory>",
                        exception_type=None,
                        safe_message="Configured framework project root does not exist.",
                        session_created=False,
                        has_session_info=False,
                    )
                ],
            )

        try:
            with framework_text_chat_import_context(project_root):
                module = importlib.import_module(self._module_name)
                create_session = getattr(module, "create_text_chat_session", None)
                if not callable(create_session):
                    return FrameworkTextChatSessionDiagnosisResult(
                        status="unavailable",
                        module_name=self._module_name,
                        project_root_shape="<configured-framework-root>",
                        likely_cwd_dependency=False,
                        attempts=[
                            FrameworkTextChatSessionDiagnosisAttempt(
                                attempt_name="public-api-visible",
                                status="unavailable",
                                cwd_shape="<current-working-directory>",
                                exception_type=None,
                                safe_message="create_text_chat_session is not available.",
                                session_created=False,
                                has_session_info=False,
                            )
                        ],
                    )

                attempts = [
                    self._attempt_create_session(
                        create_session,
                        attempt_name="current-cwd",
                        cwd=None,
                        project_root=project_root,
                    ),
                    self._attempt_create_session(
                        create_session,
                        attempt_name="framework-root-cwd",
                        cwd=project_root,
                        project_root=project_root,
                    ),
                ]
        except Exception as exc:  # pragma: no cover - operator checkout dependent.
            return FrameworkTextChatSessionDiagnosisResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                likely_cwd_dependency=False,
                attempts=[
                    _error_attempt(
                        attempt_name="import-framework",
                        cwd_shape="<current-working-directory>",
                        exc=exc,
                        project_root=project_root,
                    )
                ],
            )

        any_created = any(attempt.session_created for attempt in attempts)
        current_failed = attempts[0].status == "error"
        root_created = attempts[1].session_created
        likely_cwd_dependency = current_failed and root_created

        if any_created:
            status = "created"
        elif all(attempt.status == "error" for attempt in attempts):
            status = "error"
        else:
            status = "unavailable"

        return FrameworkTextChatSessionDiagnosisResult(
            status=status,
            module_name=self._module_name,
            project_root_shape="<configured-framework-root>",
            likely_cwd_dependency=likely_cwd_dependency,
            attempts=attempts,
        )

    def _attempt_create_session(
        self,
        create_session: Any,
        *,
        attempt_name: str,
        cwd: Path | None,
        project_root: Path,
    ) -> FrameworkTextChatSessionDiagnosisAttempt:
        cwd_shape = (
            "<configured-framework-root>"
            if cwd is not None
            else "<current-working-directory>"
        )
        try:
            with _temporary_cwd(cwd):
                session = self._create_session(create_session, project_root=project_root)
        except Exception as exc:  # pragma: no cover - operator checkout dependent.
            return _error_attempt(
                attempt_name=attempt_name,
                cwd_shape=cwd_shape,
                exc=exc,
                project_root=project_root,
            )

        has_info = _has_session_info(session)
        return FrameworkTextChatSessionDiagnosisAttempt(
            attempt_name=attempt_name,
            status="created",
            cwd_shape=cwd_shape,
            exception_type=None,
            safe_message=(
                "Session was created with import layout "
                f"{framework_text_chat_import_layout_summary(project_root)}. "
                "No ask, ask_stream, or provider call was made."
            ),
            session_created=True,
            has_session_info=has_info,
        )

    def _create_session(self, create_session: Any, *, project_root: Path) -> Any:
        signature = inspect.signature(create_session)
        kwargs: dict[str, Any] = {}

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

        has_var_keyword = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )
        if has_var_keyword:
            kwargs = {
                "preset": self._config.framework_preset,
                "character": self._config.framework_character,
                "project_root": str(project_root),
            }
        else:
            for name in signature.parameters:
                value = candidate_values.get(name)
                if value is not None:
                    kwargs[name] = value

        return create_session(**kwargs)

    def _framework_project_root(self) -> Path | None:
        configured = self._config.framework_project_root or getattr(
            self._config,
            "framework_root",
            None,
        )
        if not configured:
            return None
        return Path(configured)


def _error_attempt(
    *,
    attempt_name: str,
    cwd_shape: str,
    exc: Exception,
    project_root: Path,
) -> FrameworkTextChatSessionDiagnosisAttempt:
    safe_message = _sanitize_message(str(exc), project_root)
    exception_type = type(exc).__name__
    return FrameworkTextChatSessionDiagnosisAttempt(
        attempt_name=attempt_name,
        status="error",
        cwd_shape=cwd_shape,
        exception_type=exception_type,
        safe_message=safe_message,
        session_created=False,
        has_session_info=False,
        failure_kind=classify_framework_text_chat_session_failure(
            exception_type=exception_type,
            safe_message=safe_message,
        ),
    )


def _has_session_info(session: Any) -> bool:
    if hasattr(session, "get_session_info") and callable(session.get_session_info):
        info = session.get_session_info()
        return info is not None
    if hasattr(session, "session_info"):
        return getattr(session, "session_info") is not None
    if hasattr(session, "info"):
        return getattr(session, "info") is not None
    return session is not None


def _sanitize_message(message: str, project_root: Path) -> str:
    if not message:
        return "<empty-error-message>"

    safe = message.replace(str(project_root), "<configured-framework-root>")
    safe = safe.replace(str(project_root).replace("\\", "/"), "<configured-framework-root>")
    safe = re.sub(r"[A-Za-z]:[\\/][^\s:'\"]+", "<private-path>", safe)
    safe = re.sub(r"/(?:Users|home|mnt|tmp)/[^\s:'\"]+", "<private-path>", safe)
    safe = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "<redacted-api-key>", safe)
    safe = re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "<redacted-api-key>", safe)
    safe = re.sub(r"xai-[A-Za-z0-9_\-]{12,}", "<redacted-api-key>", safe)
    safe = " ".join(safe.split())
    return safe[:240]


@contextmanager
def _temporary_cwd(path: Path | None):
    if path is None:
        yield
        return

    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)
