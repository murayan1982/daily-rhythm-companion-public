from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import importlib
import sys

from app.config import AppConfig


@dataclass(frozen=True)
class FrameworkTextChatPreflightResult:
    """Public-safe result for framework text chat local import preflight."""

    status: str
    module_name: str
    project_root_shape: str | None
    has_create_text_chat_session: bool
    has_text_chat_session_class: bool
    message: str


class FrameworkTextChatPreflightService:
    """Preflight boundary for configured framework text chat local import.

    The preflight may import the framework package to confirm public API
    availability, but it must not create sessions, send messages, or call
    provider-backed runtime paths.
    """

    def __init__(self, config: AppConfig, *, module_name: str = "framework") -> None:
        self._config = config
        self._module_name = module_name

    def run(self) -> FrameworkTextChatPreflightResult:
        if not self._config.framework_text_chat_preflight_enabled:
            return FrameworkTextChatPreflightResult(
                status="skipped",
                module_name=self._module_name,
                project_root_shape=self._project_root_shape(),
                has_create_text_chat_session=False,
                has_text_chat_session_class=False,
                message=(
                    "Framework text chat local import preflight skipped because "
                    "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT is off."
                ),
            )

        project_root = self._framework_project_root()
        if project_root is None:
            return FrameworkTextChatPreflightResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape=None,
                has_create_text_chat_session=False,
                has_text_chat_session_class=False,
                message=(
                    "Framework text chat preflight is enabled, but FRAMEWORK_ROOT "
                    "or FRAMEWORK_PROJECT_ROOT is not configured."
                ),
            )

        if not project_root.exists():
            return FrameworkTextChatPreflightResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                has_create_text_chat_session=False,
                has_text_chat_session_class=False,
                message="Configured framework project root does not exist.",
            )

        try:
            with _temporary_sys_path(project_root):
                module = importlib.import_module(self._module_name)
        except Exception as exc:  # pragma: no cover - message is checked by smoke.
            return FrameworkTextChatPreflightResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                has_create_text_chat_session=False,
                has_text_chat_session_class=False,
                message=f"Framework module import failed safely: {type(exc).__name__}",
            )

        has_create = callable(getattr(module, "create_text_chat_session", None))
        has_session_class = hasattr(module, "TextChatSessionInfo") or hasattr(
            module, "TextChatSession"
        )

        if not has_create:
            return FrameworkTextChatPreflightResult(
                status="unavailable",
                module_name=self._module_name,
                project_root_shape="<configured-framework-root>",
                has_create_text_chat_session=False,
                has_text_chat_session_class=has_session_class,
                message="Framework module imported but create_text_chat_session is not available.",
            )

        return FrameworkTextChatPreflightResult(
            status="available",
            module_name=self._module_name,
            project_root_shape="<configured-framework-root>",
            has_create_text_chat_session=True,
            has_text_chat_session_class=has_session_class,
            message=(
                "Framework module imported and create_text_chat_session is visible. "
                "No session was created and no provider call was made."
            ),
        )

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


@contextmanager
def _temporary_sys_path(path: Path):
    path_text = str(path)
    added = False
    if path_text not in sys.path:
        sys.path.insert(0, path_text)
        added = True
    try:
        yield
    finally:
        if added:
            try:
                sys.path.remove(path_text)
            except ValueError:
                pass
