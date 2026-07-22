from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol

from app.config import AppConfig
from app.models.chat import ChatMessage, ChatSource, PostAdviceChatContext
from app.services.framework_text_chat_drc_live_reply import (
    FrameworkTextChatDrcLiveReplyResult,
    FrameworkTextChatDrcLiveReplyService,
)


@dataclass(frozen=True)
class FrameworkTextChatResult:
    """Safe result returned by the framework text chat adapter boundary.

    The adapter keeps framework metadata explicit so the post-advice chat service
    can surface skipped, unavailable, blocked, fallback, and configured-success
    states without confusing them with mock chat replies.
    """

    status: str
    reply_text: str
    source: ChatSource
    is_configured_success: bool = False


class _LiveReplyService(Protocol):
    def reply(self, *, prompt: str) -> FrameworkTextChatDrcLiveReplyResult:
        """Return a DRC-facing live FW text-chat reply."""


class FrameworkPostAdviceChatAdapter:
    """Boundary for configured AI Character Framework post-advice text chat.

    The default path stays non-executing unless both app-level gates are enabled:
    ``DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1`` selects the framework
    boundary from the DRC chat service, and
    ``DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1`` allows one live ``session.ask``
    call through the DRC adapter. Source-tree checks inject a fake live service
    and remain provider-free.
    """

    def __init__(
        self,
        config: AppConfig,
        *,
        live_reply_service: _LiveReplyService | None = None,
    ) -> None:
        self._config = config
        self._live_reply_service = live_reply_service or FrameworkTextChatDrcLiveReplyService(
            config
        )

    def reply(
        self,
        *,
        context: PostAdviceChatContext,
        prior_messages: list[ChatMessage],
        user_message: str,
    ) -> FrameworkTextChatResult:
        """Return a framework-boundary reply for post-advice chat."""

        source = self._build_source(context)

        if not self._config.framework_text_chat_smoke_enabled:
            return FrameworkTextChatResult(
                status="skipped",
                reply_text=(
                    "FWテキストチャット確認は明示opt-inがoffのためスキップしています。"
                    "現在はmock-safeチャットで確認できます。"
                ),
                source=source.model_copy(update={"mode": "framework_text_chat_skipped"}),
            )

        if not self._config.framework_project_root:
            return FrameworkTextChatResult(
                status="unavailable",
                reply_text=(
                    "FWテキストチャットは有効化されていますが、FRAMEWORK_ROOT または "
                    "FRAMEWORK_PROJECT_ROOT が未設定のため実行できません。"
                ),
                source=source.model_copy(
                    update={"mode": "framework_text_chat_unavailable"}
                ),
            )

        if not self._config.framework_text_chat_live_message_enabled:
            return FrameworkTextChatResult(
                status="blocked-live-message-gate",
                reply_text=(
                    "FWテキストチャット境界は有効ですが、実メッセージ送信gateがoffです。"
                    "ローカルstrict確認時だけ DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1 "
                    "を有効にしてください。"
                ),
                source=source.model_copy(
                    update={"mode": "framework_text_chat_live_message_blocked"}
                ),
            )

        prompt = self._build_live_reply_prompt(
            context=context,
            prior_messages=prior_messages,
            user_message=user_message,
        )
        live_result = self._live_reply_service.reply(prompt=prompt)
        if live_result.status == "responded" and live_result.response_non_empty:
            return FrameworkTextChatResult(
                status="responded",
                reply_text=live_result.reply_text,
                source=source.model_copy(update={"mode": "framework_text_chat_live_message"}),
                is_configured_success=True,
            )

        return FrameworkTextChatResult(
            status=live_result.status,
            reply_text=live_result.reply_text,
            source=source.model_copy(
                update={"mode": _safe_source_mode(live_result.status)}
            ),
            is_configured_success=False,
        )

    def _build_source(self, context: PostAdviceChatContext) -> ChatSource:
        return ChatSource(
            engine="framework",
            mode="framework_text_chat_boundary",
            drc_character_id=context.character.character_id,
            drc_character_name=context.character.display_name,
            framework_preset=self._config.framework_preset,
            framework_character=self._config.framework_character,
            framework_character_source="configured_env",
        )

    def _build_live_reply_prompt(
        self,
        *,
        context: PostAdviceChatContext,
        prior_messages: list[ChatMessage],
        user_message: str,
    ) -> str:
        """Build the bounded DRC prompt passed to FW text chat.

        The prompt body may contain local user context and must never be printed
        by smoke/evidence renderers. It is intentionally short so the first live
        adapter/API path stays cheap and easy to inspect.
        """

        recent_turns = _summarize_recent_messages(prior_messages, limit=3)
        return "\n".join(
            [
                "Daily Rhythm Companion のpost-advice chatです。",
                "以下の条件で、日本語で短く自然に返答してください。",
                "医療断定は避け、睡眠や気分については一般的でやさしい表現にしてください。",
                f"character_name: {context.character.display_name}",
                f"speaking_style: {_shorten(context.character.speaking_style, limit=80)}",
                f"advice_style: {_shorten(context.character.advice_style, limit=80)}",
                f"mood: {_shorten(context.mood or 'unknown', limit=32)}",
                f"advice_message: {_shorten(context.advice_message, limit=180)}",
                f"recent_chat: {recent_turns}",
                f"user_message: {_shorten(user_message, limit=240)}",
                "返答は1〜3文。ユーザーの発言を受け止めて、必要なら小さな次の一歩だけ提案してください。",
            ]
        )


def _summarize_recent_messages(messages: list[ChatMessage], *, limit: int) -> str:
    selected = messages[-limit:]
    if not selected:
        return "<none>"
    parts = [f"{message.role}: {_shorten(message.content, limit=80)}" for message in selected]
    return " / ".join(parts)


def _shorten(value: str, *, limit: int) -> str:
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1]}…"


def _safe_source_mode(status: str) -> str:
    safe_status = re.sub(r"[^a-z0-9_\-]+", "-", status.strip().lower())
    safe_status = safe_status.strip("-") or "unknown"
    return "framework_text_chat_live_message_" + safe_status
