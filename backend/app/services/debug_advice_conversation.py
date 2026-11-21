from collections import OrderedDict
from dataclasses import dataclass, field
from secrets import token_urlsafe
from threading import Lock
from time import monotonic
from typing import Callable

from app.models.chat import ChatMessage


@dataclass(frozen=True)
class _Advice:
    character_id: str
    message: str


@dataclass(frozen=True)
class ConversationReply:
    message: str
    expression_tag: str
    voice_ref: str | None


@dataclass
class _Conversation:
    advice: _Advice
    expires_at: float
    turns: list[tuple[str, ConversationReply]] = field(default_factory=list)
    pending: bool = False


class ConversationUnavailable(Exception):
    pass


class ConversationTurnConflict(Exception):
    pass


class DebugAdviceConversationStore:
    """Short-lived advice anchors and bounded, process-local conversation history."""

    def __init__(self, *, ttl: int, capacity: int, turn_limit: int) -> None:
        self._ttl = ttl
        self._capacity = capacity
        self.turn_limit = turn_limit
        self._lock = Lock()
        self._advice: OrderedDict[str, tuple[float, _Advice]] = OrderedDict()
        self._sessions: OrderedDict[str, _Conversation] = OrderedDict()

    def _cleanup(self, now: float) -> None:
        for ref, (expires, _) in tuple(self._advice.items()):
            if expires <= now:
                del self._advice[ref]
        for ref, session in tuple(self._sessions.items()):
            if session.expires_at <= now:
                del self._sessions[ref]

    def remember_advice(self, character_id: str, message: str) -> str:
        with self._lock:
            now = monotonic()
            self._cleanup(now)
            if len(self._advice) >= self._capacity:
                self._advice.popitem(last=False)
            ref = token_urlsafe(24)
            self._advice[ref] = (now + 300, _Advice(character_id, message))
            return ref

    def start(self, advice_ref: str) -> str:
        with self._lock:
            now = monotonic()
            self._cleanup(now)
            entry = self._advice.get(advice_ref)
            if entry is None:
                raise ConversationUnavailable
            if len(self._sessions) >= self._capacity:
                self._sessions.popitem(last=False)
            ref = token_urlsafe(24)
            self._sessions[ref] = _Conversation(entry[1], now + self._ttl)
            return ref

    def end(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def reply(
        self,
        session_id: str,
        turn: int,
        question: str,
        generate: Callable[[str, str, list[ChatMessage]], ConversationReply],
    ) -> ConversationReply:
        with self._lock:
            self._cleanup(monotonic())
            session = self._sessions.get(session_id)
            if session is None:
                raise ConversationUnavailable
            if turn <= len(session.turns):
                previous, reply = session.turns[turn - 1]
                if previous == question:
                    return reply
                raise ConversationTurnConflict
            if session.pending or turn != len(session.turns) + 1 or turn > self.turn_limit:
                raise ConversationTurnConflict
            messages = []
            for previous, reply in session.turns:
                messages.extend((
                    ChatMessage(role="user", content=previous),
                    ChatMessage(role="assistant", content=reply.message),
                ))
            messages.append(ChatMessage(role="user", content=question))
            session.pending = True
            session.expires_at = monotonic() + self._ttl
            self._sessions.move_to_end(session_id)

        try:
            result = generate(session.advice.character_id, session.advice.message, messages)
            with self._lock:
                self._cleanup(monotonic())
                if self._sessions.get(session_id) is not session:
                    raise ConversationUnavailable
                session.turns.append((question, result))
                session.expires_at = monotonic() + self._ttl
                return result
        finally:
            with self._lock:
                session.pending = False

    def resolve_voice(self, session_id: str, voice_ref: str) -> tuple[str, str] | None:
        with self._lock:
            self._cleanup(monotonic())
            session = self._sessions.get(session_id)
            if session is None:
                return None
            for _, reply in session.turns:
                if reply.voice_ref == voice_ref:
                    return session.advice.character_id, reply.message
            return None
