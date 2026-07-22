from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib
import inspect
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
class FrameworkTextChatSessionPreflightResult:
    """Public-safe result for framework text chat session creation preflight."""

    status: str
    module_name: str
    project_root_shape: str | None
    session_created: bool
    has_session_info: bool
    session_info_shape: str | None
    message: str
    failure_kind: str = "none"


class FrameworkTextChatSessionPreflightService:
    """Preflight boundary for creating a framework text chat session.

    Day20 may call create_text_chat_session, but must not call ask, ask_stream,
    provider APIs, STT/TTS, or Live2D/VTS runtime paths. Day24 keeps the
    configured FW sys.path layout active through session creation so lazy
    top-level imports such as registry are diagnosed at the correct site.
    """

    def __init__(self, config: AppConfig, *, module_name: str = "framework") -> None:
        self._config = config
        self._module_name = module_name

    def run(self) -> FrameworkTextChatSessionPreflightResult:
        if not self._config.framework_text_chat_session_preflight_enabled:
            return FrameworkTextChatSessionPreflightResult(
                status="skipped",
                module_name=self._module_name,
                project_root_shape=self._project_root_shape(),
                session_created=False,
                has_session_info=False,
                session_info_shape=None,
                message=(
                    "Framework text chat session preflight skipped because "
                    "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT is off."
                ),
            )

        project_root = self._framework_project_root()
        if project_root is None:
            return FrameworkTextChatSessionPreflightResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape=None,
                session_created=False,
                has_session_info=False,
                session_info_shape=None,
                message=(
                    "Framework text chat session preflight is enabled, but "
                    "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured."
                ),
            )

        if not project_root.exists():
            return FrameworkTextChatSessionPreflightResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                session_created=False,
                has_session_info=False,
                session_info_shape=None,
                message="Configured framework project root does not exist.",
            )

        try:
            with framework_text_chat_import_context(project_root):
                module = importlib.import_module(self._module_name)
                create_session = getattr(module, "create_text_chat_session", None)
                if not callable(create_session):
                    return FrameworkTextChatSessionPreflightResult(
                        status="unavailable",
                        module_name=self._module_name,
                        project_root_shape="<configured-framework-root>",
                        session_created=False,
                        has_session_info=False,
                        session_info_shape=None,
                        message="create_text_chat_session is not available.",
                    )
                session = self._create_session(create_session)
        except Exception as exc:  # pragma: no cover - depends on operator checkout.
            exception_type = type(exc).__name__
            safe_message = str(exc)[:240]
            failure_kind = classify_framework_text_chat_session_failure(
                exception_type=exception_type,
                safe_message=safe_message,
            )
            extra = (
                " Provider environment appears missing; values are never exposed."
                if failure_kind == "provider-env-missing"
                else ""
            )
            return FrameworkTextChatSessionPreflightResult(
                status="error",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                session_created=False,
                has_session_info=False,
                session_info_shape=None,
                message=(
                    f"create_text_chat_session failed safely after Day24 import setup: {exception_type}."
                    f"{extra}"
                ),
                failure_kind=failure_kind,
            )

        has_session_info = self._has_session_info(session)
        return FrameworkTextChatSessionPreflightResult(
            status="created",
            module_name=self._module_name,
            project_root_shape="<configured-framework-root>",
            session_created=True,
            has_session_info=has_session_info,
            session_info_shape="<session-info>" if has_session_info else None,
            message=(
                "Framework text chat session was created for preflight with "
                f"import layout {framework_text_chat_import_layout_summary(project_root)}. "
                "No ask, ask_stream, or provider call was made."
            ),
        )

    def _create_session(self, create_session: Any) -> Any:
        """Call create_text_chat_session with conservative public kwargs.

        The fake-framework smoke accepts no arguments. Real framework versions
        may accept public configuration kwargs, so this function only supplies
        kwargs that are present in the callable signature.
        """

        signature = inspect.signature(create_session)
        kwargs: dict[str, Any] = {}

        candidate_values = {
            "preset": self._config.framework_preset,
            "preset_name": self._config.framework_preset,
            "preset_id": self._config.framework_preset,
            "character": self._config.framework_character,
            "character_name": self._config.framework_character,
            "character_id": self._config.framework_character,
            "project_root": str(self._framework_project_root())
            if self._framework_project_root()
            else None,
            "framework_project_root": str(self._framework_project_root())
            if self._framework_project_root()
            else None,
        }

        has_var_keyword = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )
        if has_var_keyword:
            kwargs = {
                key: value
                for key, value in candidate_values.items()
                if value is not None and key in {"preset", "character", "project_root"}
            }
        else:
            for name in signature.parameters:
                value = candidate_values.get(name)
                if value is not None:
                    kwargs[name] = value

        return create_session(**kwargs)

    def _has_session_info(self, session: Any) -> bool:
        if hasattr(session, "get_session_info") and callable(session.get_session_info):
            info = session.get_session_info()
            return info is not None
        if hasattr(session, "session_info"):
            return getattr(session, "session_info") is not None
        if hasattr(session, "info"):
            return getattr(session, "info") is not None
        return session is not None

    def _framework_project_root(self) -> Path | None:
        configured = self._config.framework_project_root or getattr(
            self._config,
            "framework_root",
            None,
        )
        if not configured:
            return None
        return Path(configured)

    def _project_root_shape(self) -> str | None:
        return "<configured-framework-root>" if self._framework_project_root() else None
