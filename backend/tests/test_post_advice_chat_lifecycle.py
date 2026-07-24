"""Mock-safe lifecycle regression tests for post-advice chat sessions."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import chat
from app.config import AppConfig
from app.models.character import CharacterContext
from app.models.chat import ChatMessageRequest, ChatSessionCreateRequest, PostAdviceChatContext
from app.services.post_advice_chat_service import PostAdviceChatService


@dataclass
class MutableClock:
    value: float = 1000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _request(*, initial_user_message: str | None = None) -> ChatSessionCreateRequest:
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
            mood="normal",
            advice_basis="sleep+mood+character+mock",
        ),
        initial_user_message=initial_user_message,
    )


def _service(
    clock: MutableClock,
    *,
    ttl_seconds: int = 10,
    max_sessions: int = 2,
    max_turns: int = 8,
) -> PostAdviceChatService:
    return PostAdviceChatService(
        config=AppConfig(
            post_advice_chat_ttl_seconds=ttl_seconds,
            post_advice_chat_max_sessions=max_sessions,
            post_advice_chat_max_turns=max_turns,
        ),
        now=clock,
    )


def _test_client(monkeypatch, service: PostAdviceChatService) -> TestClient:
    monkeypatch.setattr(chat, "_chat_service", service)
    test_app = FastAPI()
    test_app.include_router(chat.router)
    return TestClient(test_app)


def test_session_expires_after_idle_ttl_and_successful_get_refreshes_it() -> None:
    clock = MutableClock()
    service = _service(clock)
    session = service.create_session(_request())

    clock.advance(9)
    assert service.get_session(session.session_id) is not None

    clock.advance(9)
    assert service.get_session(session.session_id) is not None

    clock.advance(10)
    assert service.get_session(session.session_id) is None
    assert service.session_count == 0


def test_successful_message_refreshes_session_idle_ttl() -> None:
    clock = MutableClock()
    service = _service(clock)
    session = service.create_session(_request())

    clock.advance(9)
    response = service.add_message(
        session.session_id,
        ChatMessageRequest(message="少し休んでもいい？"),
    )
    assert response is not None
    assert response.session_id == session.session_id

    clock.advance(9)
    assert service.get_session(session.session_id) is not None


def test_capacity_evicts_least_recently_used_session() -> None:
    clock = MutableClock()
    service = _service(clock, max_sessions=2)

    first = service.create_session(_request())
    clock.advance(1)
    second = service.create_session(_request())
    clock.advance(1)
    assert service.get_session(first.session_id) is not None
    clock.advance(1)
    third = service.create_session(_request())

    assert service.get_session(first.session_id) is not None
    assert service.get_session(second.session_id) is None
    assert service.get_session(third.session_id) is not None
    assert service.session_count == 2


def test_cleanup_and_api_keep_existing_not_found_contract(monkeypatch) -> None:
    clock = MutableClock()
    service = _service(clock, ttl_seconds=5)
    session = service.create_session(_request(initial_user_message="もう少し話したい"))
    assert len(session.messages) == 3

    clock.advance(5)
    assert service.cleanup() == 1

    with _test_client(monkeypatch, service) as client:
        get_response = client.get(f"/chat/sessions/{session.session_id}")
        message_response = client.post(
            f"/chat/sessions/{session.session_id}/messages",
            json={"message": "まだいる？"},
        )

    expected_detail = {
        "code": "session_expired",
        "message": "Chat session not found",
        "user_message": "この会話は時間が空いたため終了しました。新しい会話を始めてください。",
        "can_restart": True,
    }
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": expected_detail}
    assert message_response.status_code == 404
    assert message_response.json() == {"detail": expected_detail}


def test_api_distinguishes_evicted_and_unknown_sessions(monkeypatch) -> None:
    clock = MutableClock()
    service = _service(clock, max_sessions=1)
    evicted = service.create_session(_request())
    service.create_session(_request())

    with _test_client(monkeypatch, service) as client:
        evicted_response = client.get(f"/chat/sessions/{evicted.session_id}")
        unknown_response = client.get("/chat/sessions/chat_unknown")

    assert evicted_response.status_code == 404
    assert evicted_response.json()["detail"]["code"] == "session_evicted"
    assert unknown_response.status_code == 404
    assert unknown_response.json()["detail"]["code"] == "session_not_found"
    assert evicted_response.json()["detail"]["can_restart"] is True
    assert unknown_response.json()["detail"]["can_restart"] is True


def test_turn_limit_counts_user_turns_and_returns_restartable_conflict(monkeypatch) -> None:
    clock = MutableClock()
    service = _service(clock, max_turns=2)
    session = service.create_session(_request(initial_user_message="最初の質問"))

    assert session.lifecycle.turn_count == 1
    assert session.lifecycle.turn_limit == 2
    assert session.lifecycle.state == "active"
    assert session.lifecycle.can_send_message is True

    second = service.add_message(
        session.session_id,
        ChatMessageRequest(message="もう一つだけ"),
    )
    assert second is not None
    assert second.lifecycle.turn_count == 2
    assert second.lifecycle.state == "turn_limit_reached"
    assert second.lifecycle.can_send_message is False
    assert second.lifecycle.can_restart is True

    with _test_client(monkeypatch, service) as client:
        limited_response = client.post(
            f"/chat/sessions/{session.session_id}/messages",
            json={"message": "上限後の送信"},
        )
        get_response = client.get(f"/chat/sessions/{session.session_id}")

    assert limited_response.status_code == 409
    assert limited_response.json()["detail"]["code"] == "turn_limit_reached"
    assert limited_response.json()["detail"]["can_restart"] is True
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "turn_limit_reached"
    assert get_response.json()["lifecycle"]["can_send_message"] is False


def test_terminal_reason_cache_is_bounded_by_session_capacity() -> None:
    clock = MutableClock()
    service = _service(clock, max_sessions=2)

    first = service.create_session(_request())
    second = service.create_session(_request())
    third = service.create_session(_request())
    fourth = service.create_session(_request())

    assert service.get_session(first.session_id) is None
    assert service.get_session(second.session_id) is None
    assert service.get_session(third.session_id) is not None
    assert service.get_session(fourth.session_id) is not None
    assert len(service._terminal_sessions) <= 2
