from __future__ import annotations

from contextlib import contextmanager
import importlib
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Any, Iterator

from app.config import AppConfig
from app.engines.base import ConversationEngine
from app.engines.character_mapping import (
    FrameworkCharacterMapping,
    resolve_framework_character_mapping,
)
from app.engines.errors import FrameworkEngineError
from app.models.advice import AdviceRequest, AdviceResponse, AdviceSource
from app.services.advice_prompt_builder import build_advice_prompt


class FrameworkConversationEngine(ConversationEngine):
    """
    Conversation engine backed by the AI Character Framework public facade.

    The framework package is imported dynamically from FRAMEWORK_ROOT or the
    compatibility alias FRAMEWORK_PROJECT_ROOT so DRC can keep framework
    integration optional. The adapter intentionally depends on the public
    ``framework`` import boundary rather than framework internals.
    """

    def __init__(self, config: AppConfig):
        self._config = config
        self._session_cache: dict[str, Any] = {}

    def create_advice(self, request: AdviceRequest) -> AdviceResponse:
        """Create app-facing advice through the framework text session."""

        character_mapping = self._resolve_framework_character_mapping(
            request.character.character_id
        )
        session = self._get_or_create_session(character_mapping.framework_character)
        prompt = build_advice_prompt(request)
        message = self._ask_session(session=session, prompt=prompt)

        return AdviceResponse(
            message=message,
            character_name=request.character.display_name,
            source=AdviceSource(
                engine="framework",
                drc_character_id=request.character.character_id,
                drc_character_name=request.character.display_name,
                framework_preset=self._config.framework_preset,
                framework_character=character_mapping.framework_character,
                framework_character_source=(
                    character_mapping.framework_character_source
                ),
            ),
        )

    def _ask_session(self, *, session: Any, prompt: str) -> str:
        """
        Call ``session.ask`` and normalize the public response to non-empty text.

        AI Character Framework's app-facing text session is expected to support
        ``session.ask(text)``. DRC stores and displays an ``AdviceResponse`` text
        field, so an empty or non-text-like response is treated as a framework
        engine failure and can fall back through the /advice boundary.
        """

        if not hasattr(session, "ask") or not callable(session.ask):
            raise FrameworkEngineError(
                "AI Character Framework text session does not expose ask(text)."
            )

        framework_root = self._resolve_framework_root()

        try:
            with self._temporary_cwd(framework_root):
                message = session.ask(prompt)
        except Exception as exc:
            raise FrameworkEngineError(
                "AI Character Framework session.ask() failed."
            ) from exc

        normalized_message = self._normalize_message(message)
        if not normalized_message:
            raise FrameworkEngineError(
                "AI Character Framework session.ask() returned an empty response."
            )

        return normalized_message

    def _normalize_message(self, message: Any) -> str:
        """Convert the framework response into the text expected by AdviceResponse."""

        if isinstance(message, str):
            return message.strip()

        for attr_name in ("message", "text", "content"):
            attr_value = getattr(message, attr_name, None)
            if isinstance(attr_value, str) and attr_value.strip():
                return attr_value.strip()

        if message is None:
            return ""

        return str(message).strip()

    def _get_or_create_session(self, framework_character_name: str) -> Any:
        if framework_character_name in self._session_cache:
            return self._session_cache[framework_character_name]

        framework_root = self._resolve_framework_root()
        create_text_chat_session = self._load_framework_facade(framework_root)

        if self._config.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = self._config.gemini_api_key
            os.environ["GOOGLE_API_KEY"] = self._config.gemini_api_key

        if self._config.xai_api_key:
            os.environ["XAI_API_KEY"] = self._config.xai_api_key

        try:
            with self._temporary_cwd(framework_root):
                session = create_text_chat_session(
                    preset=self._config.framework_preset,
                    character_name=framework_character_name,
                )
        except Exception as exc:
            raise FrameworkEngineError(
                "Failed to create AI Character Framework text chat session."
            ) from exc

        self._session_cache[framework_character_name] = session
        return session

    def _load_framework_facade(self, framework_root: Path) -> Any:
        adapter_mode = self._config.framework_adapter_mode.strip().lower()
        if adapter_mode != "local_import":
            raise FrameworkEngineError(
                f"Unsupported FRAMEWORK_ADAPTER_MODE: {self._config.framework_adapter_mode}"
            )

        framework_root_str = str(framework_root)
        if framework_root_str not in sys.path:
            sys.path.insert(0, framework_root_str)

        self._clear_stale_framework_modules(framework_root)
        importlib.invalidate_caches()

        try:
            framework_module = import_module("framework")
            self._assert_framework_module_from_root(
                framework_module=framework_module,
                framework_root=framework_root,
            )
            create_text_chat_session = getattr(
                framework_module,
                "create_text_chat_session",
            )
        except FrameworkEngineError:
            raise
        except Exception as exc:
            raise FrameworkEngineError(
                "Failed to import framework.create_text_chat_session."
            ) from exc

        if not callable(create_text_chat_session):
            raise FrameworkEngineError(
                "framework.create_text_chat_session is not callable."
            )

        return create_text_chat_session

    def _clear_stale_framework_modules(self, framework_root: Path) -> None:
        """Drop a cached ``framework`` package when it came from another root."""

        framework_module = sys.modules.get("framework")
        if framework_module is None:
            return

        module_path = self._module_file_path(framework_module)
        if module_path is not None and self._is_relative_to(module_path, framework_root):
            return

        for module_name in list(sys.modules):
            if module_name == "framework" or module_name.startswith("framework."):
                sys.modules.pop(module_name, None)

    def _assert_framework_module_from_root(
        self,
        *,
        framework_module: Any,
        framework_root: Path,
    ) -> None:
        """Make sure local_import resolved the intended FRAMEWORK_ROOT package."""

        module_path = self._module_file_path(framework_module)
        if module_path is None:
            raise FrameworkEngineError(
                "Imported framework package has no __file__; cannot verify FRAMEWORK_ROOT."
            )

        if not self._is_relative_to(module_path, framework_root):
            raise FrameworkEngineError(
                "Imported framework package did not come from FRAMEWORK_ROOT: "
                f"{module_path}"
            )

    def _module_file_path(self, module: Any) -> Path | None:
        module_file = getattr(module, "__file__", None)
        if not module_file:
            return None

        try:
            return Path(module_file).resolve()
        except OSError:
            return None

    def _is_relative_to(self, path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def _resolve_framework_root(self) -> Path:
        root = self._config.framework_project_root

        if not root:
            raise FrameworkEngineError(
                "FRAMEWORK_ROOT or FRAMEWORK_PROJECT_ROOT is not configured."
            )

        framework_root = Path(root).expanduser().resolve()

        if not framework_root.exists():
            raise FrameworkEngineError(
                f"FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT does not exist: {framework_root}"
            )

        facade_path = framework_root / "framework" / "facade.py"
        package_init_path = framework_root / "framework" / "__init__.py"
        if not facade_path.exists() and not package_init_path.exists():
            raise FrameworkEngineError(
                f"framework/facade.py was not found under: {framework_root}"
            )

        return framework_root

    def _resolve_framework_character_mapping(
        self,
        character_id: str,
    ) -> FrameworkCharacterMapping:
        """
        Resolve framework character selection with v0.32 source metadata.

        An explicit FRAMEWORK_CHARACTER value remains a local/demo override;
        otherwise DRC uses the shared mapping table from character_mapping.py.
        """

        return resolve_framework_character_mapping(
            character_id,
            configured_character=self._config.framework_character,
        )

    def _resolve_framework_character_name(self, character_id: str) -> str:
        """
        Backward-compatible helper for older checks that only need the name.
        """

        return self._resolve_framework_character_mapping(
            character_id
        ).framework_character

    @contextmanager
    def _temporary_cwd(self, path: Path) -> Iterator[None]:
        """Temporarily use FRAMEWORK_ROOT as CWD for current FW config loading."""

        previous_cwd = Path.cwd()
        try:
            os.chdir(path)
            yield
        finally:
            os.chdir(previous_cwd)
