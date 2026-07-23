from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Callable
from uuid import uuid4

from app.config import AppConfig, load_config
from app.models.chat import (
    ChatMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    ChatSource,
    PostAdviceChatContext,
)
from app.services.framework_text_chat_adapter import FrameworkPostAdviceChatAdapter


@dataclass(frozen=True)
class _StoredChatSession:
    session: ChatSessionResponse
    last_used_at: float
    sequence: int


class PostAdviceChatService:
    """Bounded in-memory post-advice chat session service.

    The default path remains mock-safe and provider-free. Sessions expire after
    an idle TTL and the least-recently-used session is evicted when capacity is
    reached. The existing API response models remain unchanged.
    """

    def __init__(
        self,
        *,
        config: AppConfig | None = None,
        framework_adapter: FrameworkPostAdviceChatAdapter | None = None,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._config = config or load_config()
        self._framework_adapter = framework_adapter or FrameworkPostAdviceChatAdapter(
            self._config
        )
        self._now = now or monotonic
        self._ttl_seconds = max(1, self._config.post_advice_chat_ttl_seconds)
        self._max_sessions = max(1, self._config.post_advice_chat_max_sessions)
        self._sessions: dict[str, _StoredChatSession] = {}
        self._sequence = 0
        self._lock = RLock()

    def create_session(
        self,
        request: ChatSessionCreateRequest,
    ) -> ChatSessionResponse:
        with self._lock:
            current_time = self._now()
            self._cleanup_expired_locked(current_time)
            self._evict_for_new_session_locked()

            session_id = f"chat_{uuid4().hex[:12]}"
            source = self._build_source(request.context)
            session = ChatSessionResponse(
                session_id=session_id,
                status="active",
                source=source,
                context=request.context,
                messages=[
                    ChatMessage(
                        role="assistant",
                        content=self._build_opening_message(request.context),
                    )
                ],
            )
            self._store_session_locked(session, current_time)

            if request.initial_user_message:
                reply_response = self.add_message(
                    session_id=session_id,
                    request=ChatMessageRequest(message=request.initial_user_message),
                )
                if reply_response is not None:
                    session = session.model_copy(
                        update={
                            "messages": reply_response.messages,
                            "source": reply_response.source,
                        }
                    )
                    self._store_session_locked(session, self._now())

            return session

    def get_session(self, session_id: str) -> ChatSessionResponse | None:
        with self._lock:
            current_time = self._now()
            self._cleanup_expired_locked(current_time)
            stored = self._sessions.get(session_id)
            if stored is None:
                return None

            self._store_session_locked(stored.session, current_time)
            return stored.session

    def add_message(
        self,
        session_id: str,
        request: ChatMessageRequest,
    ) -> ChatMessageResponse | None:
        with self._lock:
            current_time = self._now()
            self._cleanup_expired_locked(current_time)
            stored = self._sessions.get(session_id)
            if stored is None:
                return None

            session = stored.session
            user_message = ChatMessage(role="user", content=request.message)

            if self._config.framework_text_chat_smoke_enabled:
                return self._add_framework_boundary_message(
                    session=session,
                    user_message=user_message,
                )

            return self._add_mock_message(session=session, user_message=user_message)

    def cleanup(self) -> int:
        """Remove expired sessions and return the number removed."""

        with self._lock:
            return self._cleanup_expired_locked(self._now())

    @property
    def session_count(self) -> int:
        with self._lock:
            self._cleanup_expired_locked(self._now())
            return len(self._sessions)

    def _add_mock_message(
        self,
        *,
        session: ChatSessionResponse,
        user_message: ChatMessage,
    ) -> ChatMessageResponse:
        reply = ChatMessage(
            role="assistant",
            content=self._build_reply(
                context=session.context,
                user_message=user_message.content,
            ),
        )
        source = self._build_mock_source(session.context)
        return self._store_reply(
            session=session,
            user_message=user_message,
            reply=reply,
            source=source,
        )

    def _add_framework_boundary_message(
        self,
        *,
        session: ChatSessionResponse,
        user_message: ChatMessage,
    ) -> ChatMessageResponse:
        result = self._framework_adapter.reply(
            context=session.context,
            prior_messages=session.messages,
            user_message=user_message.content,
        )
        reply = ChatMessage(role="assistant", content=result.reply_text)
        return self._store_reply(
            session=session,
            user_message=user_message,
            reply=reply,
            source=result.source,
        )

    def _store_reply(
        self,
        *,
        session: ChatSessionResponse,
        user_message: ChatMessage,
        reply: ChatMessage,
        source: ChatSource,
    ) -> ChatMessageResponse:
        messages = [*session.messages, user_message, reply]
        updated_session = session.model_copy(
            update={"messages": messages, "source": source}
        )
        self._store_session_locked(updated_session, self._now())

        return ChatMessageResponse(
            session_id=session.session_id,
            reply=reply,
            source=source,
            messages=messages,
        )

    def _store_session_locked(
        self,
        session: ChatSessionResponse,
        last_used_at: float,
    ) -> None:
        self._sequence += 1
        self._sessions[session.session_id] = _StoredChatSession(
            session=session,
            last_used_at=last_used_at,
            sequence=self._sequence,
        )

    def _cleanup_expired_locked(self, current_time: float) -> int:
        expired_ids = [
            session_id
            for session_id, stored in self._sessions.items()
            if current_time - stored.last_used_at
            >= self._ttl_seconds
        ]
        for session_id in expired_ids:
            self._sessions.pop(session_id, None)
        return len(expired_ids)

    def _evict_for_new_session_locked(self) -> None:
        while len(self._sessions) >= self._max_sessions:
            oldest_session_id = min(
                self._sessions,
                key=lambda session_id: (
                    self._sessions[session_id].last_used_at,
                    self._sessions[session_id].sequence,
                    session_id,
                ),
            )
            self._sessions.pop(oldest_session_id, None)

    def _build_source(self, context: PostAdviceChatContext) -> ChatSource:
        if self._config.framework_text_chat_smoke_enabled:
            return ChatSource(
                engine="framework",
                mode="framework_text_chat_boundary",
                drc_character_id=context.character.character_id,
                drc_character_name=context.character.display_name,
                framework_preset=self._config.framework_preset,
                framework_character=self._config.framework_character,
                framework_character_source="configured_env",
            )

        return self._build_mock_source(context)

    def _build_mock_source(self, context: PostAdviceChatContext) -> ChatSource:
        return ChatSource(
            engine="mock",
            mode="post_advice_chat",
            drc_character_id=context.character.character_id,
            drc_character_name=context.character.display_name,
        )

    def _build_opening_message(self, context: PostAdviceChatContext) -> str:
        character_name = context.character.display_name

        if self._config.framework_text_chat_smoke_enabled:
            if self._config.framework_text_chat_live_message_enabled:
                return (
                    f"{character_name}です。FWテキストチャットlive message gateが"
                    "有効化されています。実FW応答はローカルstrict確認として扱います。"
                )
            return (
                f"{character_name}です。FWテキストチャット境界は有効化されています。"
                "実メッセージ送信gateはoffなので、安全な未接続表示にしています。"
            )

        return (
            f"{character_name}です。さっきのアドバイスについて、"
            "もう少し話したいことがあれば聞かせてね。"
            "無理に続けなくても大丈夫だよ。"
        )

    def _build_reply(
        self,
        context: PostAdviceChatContext,
        user_message: str,
    ) -> str:
        character_name = context.character.display_name
        advice_hint = _shorten(context.advice_message, limit=44)
        user_hint = _shorten(user_message, limit=36)

        return (
            f"{character_name}です。『{user_hint}』って感じなんだね。"
            f"さっきの提案（{advice_hint}）をベースにするなら、"
            "まずは小さく一つだけ試して、しんどければ今日は休む方向で大丈夫。"
        )


def _shorten(value: str, *, limit: int) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1]}…"
