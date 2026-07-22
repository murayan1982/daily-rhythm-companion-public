"""Day18 configured framework text chat local import preflight smoke.

Default behavior is safe and skip-friendly. The script only requires a real
framework checkout when --require-real-framework is passed and
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=1 is set.

This smoke imports the framework module and verifies public API visibility. It
does not create text chat sessions, send messages, or call provider APIs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import load_config
from app.services.framework_text_chat_preflight import FrameworkTextChatPreflightService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Configured framework text chat local import preflight smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help=(
            "Fail unless the configured framework checkout is available and "
            "create_text_chat_session is visible."
        ),
    )
    args = parser.parse_args()

    config = load_config()
    result = FrameworkTextChatPreflightService(config).run()

    if result.status == "skipped":
        if args.require_real_framework:
            raise SystemExit(
                "Configured framework preflight was required but skipped. "
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=1."
            )
        print("[smoke-framework-text-chat-configured-preflight] SKIPPED")
        print(result.message)
        return

    if result.status != "available":
        if args.require_real_framework:
            raise SystemExit(
                "Configured framework preflight was required but unavailable: "
                f"{result.message}"
            )
        print("[smoke-framework-text-chat-configured-preflight] UNAVAILABLE")
        print(result.message)
        return

    if not result.has_create_text_chat_session:
        raise SystemExit("create_text_chat_session was not visible after import")

    print("[smoke-framework-text-chat-configured-preflight] OK")
    print("module:", result.module_name)
    print("project_root_shape:", result.project_root_shape)
    print("has_create_text_chat_session:", result.has_create_text_chat_session)
    print("has_text_chat_session_class:", result.has_text_chat_session_class)
    print("No session was created and no provider call was made.")


if __name__ == "__main__":
    main()
