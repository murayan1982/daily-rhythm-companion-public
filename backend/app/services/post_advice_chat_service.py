from __future__ import annotations

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


class PostAdviceChatService:
    """In-memory post-advice chat session service.

    The default path remains mock-safe and provider-free. When
    DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE is explicitly enabled, this service
    routes message replies through the framework text chat adapter boundary.
    Day32 lets that adapter return a real FW reply only when the separate
    DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE gate is explicitly enabled.
    """

    def __init__(
        self,
        *,
        config: AppConfig | None = None,
        framework_adapter: FrameworkPostAdviceChatAdapter | None = None,
    ) -> None:
        self._config = config or load_config()
        self._framework_adapter = framework_adapter or FrameworkPostAdviceChatAdapter(
            self._config
        )
        self._sessions: dict[str, ChatSessionResponse] = {}

    def create_session(
        self,
        request: ChatSessionCreateRequest,
    ) -> ChatSessionResponse:
        session_id = f"chat_{uuid4().hex[:12]}"
        source = self._build_source(request.context)

        messages = [
            ChatMessage(
                role="assistant",
                content=self._build_opening_message(request.context),
            )
        ]

        session = ChatSessionResponse(
            session_id=session_id,
            status="active",
            source=source,
            context=request.context,
            messages=messages,
        )
        self._sessions[session_id] = session

        if request.initial_user_message:
            reply_response = self.add_message(
                session_id=session_id,
                request=ChatMessageRequest(message=request.initial_user_message),
            )
            session = session.model_copy(
                update={
                    "messages": reply_response.messages,
                    "source": reply_response.source,
                }
            )
            self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> ChatSessionResponse | None:
        return self._sessions.get(session_id)

    def add_message(
        self,
        session_id: str,
        request: ChatMessageRequest,
    ) -> ChatMessageResponse | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None

        user_message = ChatMessage(role="user", content=request.message)

        if self._config.framework_text_chat_smoke_enabled:
            return self._add_framework_boundary_message(
                session=session,
                user_message=user_message,
            )

        return self._add_mock_message(session=session, user_message=user_message)

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
        return self._store_reply(session=session, user_message=user_message, reply=reply, source=source)

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
        self._sessions[session.session_id] = updated_session

        return ChatMessageResponse(
            session_id=session.session_id,
            reply=reply,
            source=source,
            messages=messages,
        )

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
