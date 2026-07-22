"""Smoke check for Day16 post-advice framework text chat unavailable state.

This script does not call AI Character Framework. It instantiates the
post-advice chat service with DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE-style
configuration and verifies the safe unavailable state.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig
from app.models.chat import ChatMessageRequest, ChatSessionCreateRequest, PostAdviceChatContext
from app.models.character import CharacterContext
from app.services.post_advice_chat_service import PostAdviceChatService


def main() -> None:
    config = AppConfig(
        conversation_engine="framework",
        framework_project_root=None,
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_smoke_enabled=True,
    )
    service = PostAdviceChatService(config=config)

    character = CharacterContext(
        character_id="default",
        display_name="Default",
        personality_type="friendly",
        speaking_style="casual",
        advice_style="light",
    )
    context = PostAdviceChatContext(
        character=character,
        advice_message="今日は小さく整えていきましょう。",
        mood="normal",
        advice_basis="mock-safe day16 check",
    )

    session = service.create_session(ChatSessionCreateRequest(context=context))
    if session.source.engine != "framework":
        raise AssertionError(f"Expected framework source, got {session.source.engine!r}")
    if session.source.mode != "framework_text_chat_boundary":
        raise AssertionError(f"Expected framework_text_chat_boundary, got {session.source.mode!r}")

    response = service.add_message(
        session.session_id,
        ChatMessageRequest(message="FWチャットの状態を確認したい"),
    )
    if response is None:
        raise AssertionError("Expected chat response")

    if response.source.engine != "framework":
        raise AssertionError(f"Expected framework response source, got {response.source.engine!r}")
    if response.source.mode != "framework_text_chat_unavailable":
        raise AssertionError(
            f"Expected framework_text_chat_unavailable, got {response.source.mode!r}"
        )
    if "FWテキストチャットは有効化されています" not in response.reply.content:
        raise AssertionError("Expected safe unavailable framework text chat message")
    if "FRAMEWORK_ROOT" not in response.reply.content:
        raise AssertionError("Expected missing framework root guidance")

    print("[smoke-post-advice-framework-text-chat-unavailable] OK")


if __name__ == "__main__":
    main()
