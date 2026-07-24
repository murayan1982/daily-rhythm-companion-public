"""Provider-neutral post-advice chat outcome regression tests."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.config import AppConfig
from app.models.character import CharacterContext
from app.models.chat import ChatMessageRequest, ChatSessionCreateRequest, ChatSource, PostAdviceChatContext
from app.services.framework_text_chat_adapter import FrameworkTextChatResult
from app.services.post_advice_chat_service import PostAdviceChatService


@dataclass
class FakeFrameworkAdapter:
    result: FrameworkTextChatResult

    def reply(self, **_kwargs) -> FrameworkTextChatResult:
        return self.result


def _request() -> ChatSessionCreateRequest:
    return ChatSessionCreateRequest(
        context=PostAdviceChatContext(
            character=CharacterContext(
                character_id="gentle_mina",
                display_name="ミナ",
                personality_type="gentle",
                speaking_style="casual",
                advice_style="rest_focused",
            ),
            advice_message="今日は小さく一つだけ試して、疲れたら休みましょう。",
        )
    )


def _result(status: str, *, configured: bool = False) -> FrameworkTextChatResult:
    return FrameworkTextChatResult(
        status=status,
        reply_text="安全なテスト応答です。",
        source=ChatSource(
            engine="framework",
            mode="framework_text_chat_test",
            drc_character_id="gentle_mina",
            drc_character_name="ミナ",
        ),
        is_configured_success=configured,
    )


@pytest.mark.parametrize(
    ("status", "configured", "expected_kind", "can_continue", "can_restart"),
    (
        ("responded", True, "configured", True, False),
        ("skipped", False, "skipped", False, True),
        ("unavailable", False, "unavailable", False, True),
        ("blocked-live-message-gate", False, "blocked", False, True),
        ("blocked-framework-root-missing", False, "unavailable", False, True),
        ("error-empty-response", False, "fallback", True, False),
    ),
)
def test_framework_results_map_to_provider_neutral_outcomes(
    status: str,
    configured: bool,
    expected_kind: str,
    can_continue: bool,
    can_restart: bool,
) -> None:
    service = PostAdviceChatService(
        config=AppConfig(
            framework_text_chat_smoke_enabled=True,
            post_advice_chat_max_turns=8,
        ),
        framework_adapter=FakeFrameworkAdapter(_result(status, configured=configured)),
    )
    session = service.create_session(_request())
    response = service.add_message(
        session.session_id,
        ChatMessageRequest(message="少し話したい"),
    )

    assert response is not None
    assert response.outcome.kind == expected_kind
    assert response.outcome.can_continue is can_continue
    assert response.outcome.can_restart is can_restart
    assert response.outcome.technical_code == status
    assert "FRAMEWORK_" not in response.outcome.user_message
    assert "DRC_FW40" not in response.outcome.user_message


def test_mock_outcome_is_structured_and_turn_metadata_is_present() -> None:
    service = PostAdviceChatService(config=AppConfig(post_advice_chat_max_turns=3))
    session = service.create_session(_request())
    response = service.add_message(
        session.session_id,
        ChatMessageRequest(message="少し話したい"),
    )

    assert session.outcome.kind == "mock"
    assert response is not None
    assert response.outcome.kind == "mock"
    assert response.lifecycle.turn_count == 1
    assert response.lifecycle.turn_limit == 3
    assert response.lifecycle.can_send_message is True
