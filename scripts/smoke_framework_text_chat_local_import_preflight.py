"""Day17 smoke for framework text chat local import preflight.

This smoke uses a Temporary fake framework module to verify import/preflight
mechanics. It does not call the real AI Character Framework and does not create
text chat sessions.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig
from app.services.framework_text_chat_preflight import FrameworkTextChatPreflightService


def _config(
    *,
    preflight_enabled: bool,
    project_root: str | None,
) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=project_root,
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_preflight_enabled=preflight_enabled,
    )


def main() -> None:
    skipped = FrameworkTextChatPreflightService(
        _config(preflight_enabled=False, project_root=None)
    ).run()
    if skipped.status != "skipped":
        raise AssertionError(f"Expected skipped, got {skipped.status!r}")

    unavailable = FrameworkTextChatPreflightService(
        _config(preflight_enabled=True, project_root=None)
    ).run()
    if unavailable.status != "unavailable":
        raise AssertionError(f"Expected unavailable, got {unavailable.status!r}")
    if "FRAMEWORK_ROOT" not in unavailable.message:
        raise AssertionError("Expected safe missing FRAMEWORK_ROOT guidance")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        framework_dir = root / "framework"
        framework_dir.mkdir()
        (framework_dir / "__init__.py").write_text(
            "\n".join(
                [
                    "class TextChatSessionInfo:",
                    "    pass",
                    "",
                    "def create_text_chat_session(*args, **kwargs):",
                    "    raise AssertionError('preflight must not create sessions')",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        available = FrameworkTextChatPreflightService(
            _config(preflight_enabled=True, project_root=str(root))
        ).run()

    if available.status != "available":
        raise AssertionError(f"Expected available, got {available.status!r}: {available.message}")
    if not available.has_create_text_chat_session:
        raise AssertionError("Expected create_text_chat_session to be visible")
    if not available.has_text_chat_session_class:
        raise AssertionError("Expected text chat session metadata class to be visible")
    if available.project_root_shape != "<configured-framework-root>":
        raise AssertionError("Expected public-safe project root shape")
    if "No session was created" not in available.message:
        raise AssertionError("Expected no-session-created safety note")

    print("[smoke-framework-text-chat-local-import-preflight] OK")


if __name__ == "__main__":
    main()
