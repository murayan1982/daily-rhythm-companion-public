from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Callable
from uuid import uuid4

from app.config import AppConfig, load_config
from app.models.chat import (
    ChatLifecycle,
    ChatMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatOutcome,
    ChatSessionCreateRequest,
    ChatSessionProblem,
    ChatSessionResponse,
    ChatSource,
    PostAdviceChatContext,
)
from app.services.framework_text_chat_adapter import (
    FrameworkPostAdviceChatAdapter,
    FrameworkTextChatResult,
)


CHAT_PROBLEM_EXPIRED = "session_expired"
CHAT_PROBLEM_EVICTED = "session_evicted"
CHAT_PROBLEM_NOT_FOUND = "session_not_found"
CHAT_PROBLEM_TURN_LIMIT = "turn_limit_reached"


@dataclass(frozen=True)
class _StoredChatSession:
    session: ChatSessionResponse
    last_used_at: float
    sequence: int


@dataclass(frozen=True)
class _StoredTerminalSession:
    problem: ChatSessionProblem
    sequence: int


@dataclass(frozen=True)
class ChatSessionLookupResult:
    session: ChatSessionResponse | None
    problem: ChatSessionProblem | None = None


@dataclass(frozen=True)
class ChatMessageOperationResult:
    response: ChatMessageResponse | None
    problem: ChatSessionProblem | None = None


class PostAdviceChatService:
    """Bounded in-memory post-advice chat session service.

    The default path remains mock-safe and provider-free. Sessions expire after
    an idle TTL, the least-recently-used session is evicted when capacity is
    reached, and user turns are bounded. A small bounded terminal-reason cache
    lets the API distinguish expired, evicted, unknown, and turn-limit states
    without retaining user message bodies after a session is removed.
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
        self._max_turns = max(1, self._config.post_advice_chat_max_turns)
        self._sessions: dict[str, _StoredChatSession] = {}
        self._terminal_sessions: dict[str, _StoredTerminalSession] = {}
        self._sequence = 0
        self._terminal_sequence = 0
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
            lifecycle = self._build_lifecycle(turn_count=0)
            session = ChatSessionResponse(
                session_id=session_id,
                status=lifecycle.state,
                source=source,
                context=request.context,
                messages=[
                    ChatMessage(
                        role="assistant",
                        content=self._build_opening_message(request.context),
                    )
                ],
                lifecycle=lifecycle,
                outcome=self._build_initial_outcome(source),
            )
            self._store_session_locked(session, current_time)

            if request.initial_user_message:
                operation = self._add_message_result_locked(
                    session_id=session_id,
                    request=ChatMessageRequest(message=request.initial_user_message),
                )
                if operation.response is not None:
                    stored = self._sessions.get(session_id)
                    if stored is not None:
                        session = stored.session

            return session

    def get_session(self, session_id: str) -> ChatSessionResponse | None:
        """Backward-compatible convenience wrapper returning only active state."""

        return self.get_session_result(session_id).session

    def get_session_result(self, session_id: str) -> ChatSessionLookupResult:
        with self._lock:
            current_time = self._now()
            self._cleanup_expired_locked(current_time)
            stored = self._sessions.get(session_id)
            if stored is None:
                return ChatSessionLookupResult(
                    session=None,
                    problem=self._problem_for_missing_session_locked(session_id),
                )

            self._store_session_locked(stored.session, current_time)
            return ChatSessionLookupResult(session=stored.session)

    def add_message(
        self,
        session_id: str,
        request: ChatMessageRequest,
    ) -> ChatMessageResponse | None:
        """Backward-compatible wrapper returning None for terminal operations."""

        return self.add_message_result(session_id, request).response

    def add_message_result(
        self,
        session_id: str,
        request: ChatMessageRequest,
    ) -> ChatMessageOperationResult:
        with self._lock:
            return self._add_message_result_locked(session_id=session_id, request=request)

    def _add_message_result_locked(
        self,
        *,
        session_id: str,
        request: ChatMessageRequest,
    ) -> ChatMessageOperationResult:
        current_time = self._now()
        self._cleanup_expired_locked(current_time)
        stored = self._sessions.get(session_id)
        if stored is None:
            return ChatMessageOperationResult(
                response=None,
                problem=self._problem_for_missing_session_locked(session_id),
            )

        session = stored.session
        if session.lifecycle.turn_count >= self._max_turns:
            return ChatMessageOperationResult(
                response=None,
                problem=self._build_problem(CHAT_PROBLEM_TURN_LIMIT),
            )

        user_message = ChatMessage(role="user", content=request.message)

        if self._config.framework_text_chat_smoke_enabled:
            response = self._add_framework_boundary_message(
                session=session,
                user_message=user_message,
            )
        else:
            response = self._add_mock_message(session=session, user_message=user_message)

        return ChatMessageOperationResult(response=response)

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
            outcome=ChatOutcome(
                kind="mock",
                can_continue=True,
                can_restart=False,
                user_message="デモ用の安全な応答を表示しています。",
                technical_code="mock",
            ),
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
            outcome=self._build_framework_outcome(result),
        )

    def _store_reply(
        self,
        *,
        session: ChatSessionResponse,
        user_message: ChatMessage,
        reply: ChatMessage,
        source: ChatSource,
        outcome: ChatOutcome,
    ) -> ChatMessageResponse:
        messages = [*session.messages, user_message, reply]
        lifecycle = self._build_lifecycle(turn_count=session.lifecycle.turn_count + 1)
        updated_session = session.model_copy(
            update={
                "status": lifecycle.state,
                "messages": messages,
                "source": source,
                "lifecycle": lifecycle,
                "outcome": outcome,
            }
        )
        self._store_session_locked(updated_session, self._now())

        return ChatMessageResponse(
            session_id=session.session_id,
            reply=reply,
            source=source,
            messages=messages,
            lifecycle=lifecycle,
            outcome=outcome,
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
        self._terminal_sessions.pop(session.session_id, None)

    def _cleanup_expired_locked(self, current_time: float) -> int:
        expired_ids = [
            session_id
            for session_id, stored in self._sessions.items()
            if current_time - stored.last_used_at >= self._ttl_seconds
        ]
        for session_id in expired_ids:
            self._sessions.pop(session_id, None)
            self._remember_terminal_locked(session_id, CHAT_PROBLEM_EXPIRED)
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
            self._remember_terminal_locked(oldest_session_id, CHAT_PROBLEM_EVICTED)

    def _remember_terminal_locked(self, session_id: str, code: str) -> None:
        self._terminal_sequence += 1
        self._terminal_sessions[session_id] = _StoredTerminalSession(
            problem=self._build_problem(code),
            sequence=self._terminal_sequence,
        )
        while len(self._terminal_sessions) > self._max_sessions:
            oldest = min(
                self._terminal_sessions,
                key=lambda item: self._terminal_sessions[item].sequence,
            )
            self._terminal_sessions.pop(oldest, None)

    def _problem_for_missing_session_locked(self, session_id: str) -> ChatSessionProblem:
        terminal = self._terminal_sessions.get(session_id)
        if terminal is not None:
            return terminal.problem
        return self._build_problem(CHAT_PROBLEM_NOT_FOUND)

    def _build_problem(self, code: str) -> ChatSessionProblem:
        if code == CHAT_PROBLEM_EXPIRED:
            return ChatSessionProblem(
                code=code,
                message="Chat session not found",
                user_message=(
                    "この会話は時間が空いたため終了しました。"
                    "新しい会話を始めてください。"
                ),
            )
        if code == CHAT_PROBLEM_EVICTED:
            return ChatSessionProblem(
                code=code,
                message="Chat session not found",
                user_message=(
                    "この会話は利用上限により終了しました。"
                    "新しい会話を始めてください。"
                ),
            )
        if code == CHAT_PROBLEM_TURN_LIMIT:
            return ChatSessionProblem(
                code=code,
                message="Chat turn limit reached",
                user_message=(
                    "この会話は上限まで進みました。"
                    "続ける場合は新しい会話を始めてください。"
                ),
            )
        return ChatSessionProblem(
            code=CHAT_PROBLEM_NOT_FOUND,
            message="Chat session not found",
            user_message=(
                "この会話を見つけられませんでした。"
                "新しい会話を始めてください。"
            ),
        )

    def _build_lifecycle(self, *, turn_count: int) -> ChatLifecycle:
        limit_reached = turn_count >= self._max_turns
        return ChatLifecycle(
            state="turn_limit_reached" if limit_reached else "active",
            turn_count=turn_count,
            turn_limit=self._max_turns,
            can_send_message=not limit_reached,
            can_restart=limit_reached,
        )

    def _build_initial_outcome(self, source: ChatSource) -> ChatOutcome:
        if source.engine == "mock":
            return ChatOutcome(
                kind="mock",
                can_continue=True,
                can_restart=False,
                user_message="デモ用の安全な会話を開始しました。",
                technical_code="mock",
            )
        return ChatOutcome(
            kind="pending",
            can_continue=True,
            can_restart=False,
            user_message="会話を開始しました。",
            technical_code="framework_text_chat_boundary",
        )

    def _build_framework_outcome(self, result: FrameworkTextChatResult) -> ChatOutcome:
        status = result.status.strip().lower()
        if result.is_configured_success:
            return ChatOutcome(
                kind="configured",
                can_continue=True,
                can_restart=False,
                user_message="設定済みAIから返答しました。",
                technical_code=status,
            )
        if status == "skipped":
            return ChatOutcome(
                kind="skipped",
                can_continue=False,
                can_restart=True,
                user_message="AIチャットは現在オフです。新しい会話は後から始められます。",
                technical_code=status,
            )
        if (
            "unavailable" in status
            or "root-missing" in status
            or "public-api-missing" in status
        ):
            return ChatOutcome(
                kind="unavailable",
                can_continue=False,
                can_restart=True,
                user_message=(
                    "現在AIチャットを利用できません。"
                    "時間をおいて新しい会話を始めてください。"
                ),
                technical_code=status,
            )
        if "blocked" in status:
            return ChatOutcome(
                kind="blocked",
                can_continue=False,
                can_restart=True,
                user_message=(
                    "現在このチャットは利用できません。"
                    "設定確認後に新しい会話を始めてください。"
                ),
                technical_code=status,
            )
        return ChatOutcome(
            kind="fallback",
            can_continue=True,
            can_restart=False,
            user_message=(
                "AI応答を利用できなかったため、"
                "安全な代替応答を表示しています。"
            ),
            technical_code=status or "unknown",
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
