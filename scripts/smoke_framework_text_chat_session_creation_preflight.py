r"""Day20 smoke for framework text chat session creation preflight.

Default mode uses a Temporary fake framework module and verifies that
create_text_chat_session can be called without ask/ask_stream/provider calls.

Strict mode can be used by an operator with a configured real framework checkout:

    python scripts\smoke_framework_text_chat_session_creation_preflight.py --require-real-framework

This script must not send chat messages or call provider APIs.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig, load_config
from app.services.framework_text_chat_session_preflight import (
    FrameworkTextChatSessionPreflightService,
)


def _fake_config(*, session_preflight_enabled: bool, project_root: str | None) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root=project_root,
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_preflight_enabled=True,
        framework_text_chat_session_preflight_enabled=session_preflight_enabled,
    )


def _run_fake_framework_smoke() -> None:
    skipped = FrameworkTextChatSessionPreflightService(
        _fake_config(session_preflight_enabled=False, project_root=None)
    ).run()
    if skipped.status != "skipped":
        raise AssertionError(f"Expected skipped, got {skipped.status!r}")

    unavailable = FrameworkTextChatSessionPreflightService(
        _fake_config(session_preflight_enabled=True, project_root=None)
    ).run()
    if unavailable.status != "unavailable":
        raise AssertionError(f"Expected unavailable, got {unavailable.status!r}")

    previous_framework = sys.modules.pop("framework", None)
    try:
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
                        "class FakeTextChatSession:",
                        "    def get_session_info(self):",
                        "        return TextChatSessionInfo()",
                        "    def ask(self, *args, **kwargs):",
                        "        raise AssertionError('ask must not be called')",
                        "    def ask_stream(self, *args, **kwargs):",
                        "        raise AssertionError('ask_stream must not be called')",
                        "",
                        "def create_text_chat_session(*args, **kwargs):",
                        "    return FakeTextChatSession()",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            result = FrameworkTextChatSessionPreflightService(
                _fake_config(session_preflight_enabled=True, project_root=str(root))
            ).run()
    finally:
        sys.modules.pop("framework", None)
        if previous_framework is not None:
            sys.modules["framework"] = previous_framework

    if result.status != "created":
        raise AssertionError(f"Expected created, got {result.status!r}: {result.message}")
    if not result.session_created:
        raise AssertionError("Expected session_created=True")
    if not result.has_session_info:
        raise AssertionError("Expected session info to be visible")
    if "No ask, ask_stream, or provider call was made." not in result.message:
        raise AssertionError("Expected no-provider-call safety note")

    print("[smoke-framework-text-chat-session-creation-preflight] OK")


def _run_real_framework_smoke() -> None:
    config = load_config()
    result = FrameworkTextChatSessionPreflightService(config).run()

    if result.status != "created":
        raise SystemExit(
            "Configured framework session creation preflight did not create a session: "
            f"{result.status}: {result.message}"
        )
    if not result.session_created:
        raise SystemExit("session_created was false")
    if not result.has_session_info:
        raise SystemExit("session info was not visible")

    print("[smoke-framework-text-chat-session-creation-configured] OK")
    print("module:", result.module_name)
    print("project_root_shape:", result.project_root_shape)
    print("session_created:", result.session_created)
    print("has_session_info:", result.has_session_info)
    print("session_info_shape:", result.session_info_shape)
    print("No ask, ask_stream, or provider call was made.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat session creation preflight smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Use the configured real framework checkout instead of the fake framework smoke.",
    )
    args = parser.parse_args()

    if args.require_real_framework:
        if os.getenv("DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1 "
                "before running the strict session creation preflight."
            )
        _run_real_framework_smoke()
        return

    _run_fake_framework_smoke()


if __name__ == "__main__":
    main()
