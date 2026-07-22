r"""Day32 smoke for routing a live FW text-chat response through the DRC adapter.

Default mode is source-tree only. It injects a fake live-reply service, exercises
``FrameworkPostAdviceChatAdapter`` and ``PostAdviceChatService``, and does not
import AI Character Framework or call providers.

Optional strict local mode routes one DRC post-advice chat message through the
real adapter/API service path:

    python scripts\smoke_framework_text_chat_drc_adapter_live_reply.py --require-real-framework

Strict mode requires all explicit local gates and may make one bounded
``session.ask`` call through the DRC adapter. The DRC app response body is not
printed by this smoke.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppConfig, load_config
from app.models.character import CharacterContext
from app.models.chat import (
    ChatMessage,
    ChatMessageRequest,
    ChatSessionCreateRequest,
    PostAdviceChatContext,
)
from app.services.framework_text_chat_adapter import FrameworkPostAdviceChatAdapter
from app.services.framework_text_chat_drc_live_reply import (
    FrameworkTextChatDrcLiveReplyResult,
    render_drc_live_reply_result,
)
from app.services.post_advice_chat_service import PostAdviceChatService


FAKE_ADAPTER_REPLY = "<hidden-fake-fw-adapter-reply>"
DEFAULT_DRC_LIVE_ADAPTER_MESSAGE = "さっきのアドバイスを、もう少しだけ噛み砕いて。"


class FakeLiveReplyService:
    """Provider-free fake for source-tree adapter/API wiring checks."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def reply(self, *, prompt: str) -> FrameworkTextChatDrcLiveReplyResult:
        self.prompts.append(prompt)
        return FrameworkTextChatDrcLiveReplyResult(
            status="responded",
            reply_text=FAKE_ADAPTER_REPLY,
            provider_call_attempted=True,
            response_received=True,
            response_type="str",
            response_text_length=len(FAKE_ADAPTER_REPLY),
            response_non_empty=True,
            exception_type=None,
            failure_kind="none",
            safe_message="Fake live reply reached the DRC adapter.",
            next_step="verify-live-fw-response-through-drc-chat-api",
        )


def _sample_context() -> PostAdviceChatContext:
    return PostAdviceChatContext(
        character=CharacterContext(
            character_id="gentle_mina",
            display_name="ミナ",
            personality_type="gentle",
            speaking_style="やさしく、短めに、押しつけない口調",
            advice_style="小さな一歩に分けて提案する",
        ),
        advice_message="今日は寝る前のスマホ時間を少し短くして、無理なく休む準備をしましょう。",
        mood="tired",
        advice_basis="mock-safe source-tree check",
    )


def _assert_public_safe(text: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        r"Authorization:\s*Bearer",
        r"refresh_token\s*[:=]\s*['\"][^'\"]+",
        r"access_token\s*[:=]\s*['\"][^'\"]+",
        r"client_secret\s*[:=]\s*['\"][^'\"]+",
        r"[A-Za-z]:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(
                f"Public-safe DRC adapter output contained forbidden pattern: {pattern}"
            )


def _run_source_tree_smoke() -> None:
    fake_live = FakeLiveReplyService()
    config = AppConfig(
        framework_project_root="<fake-framework-root>",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_live_message_enabled=True,
    )
    adapter = FrameworkPostAdviceChatAdapter(
        config,
        live_reply_service=fake_live,
    )

    adapter_result = adapter.reply(
        context=_sample_context(),
        prior_messages=[ChatMessage(role="assistant", content="最初の案内です。")],
        user_message=DEFAULT_DRC_LIVE_ADAPTER_MESSAGE,
    )
    if adapter_result.status != "responded":
        raise AssertionError("Adapter did not return responded status")
    if not adapter_result.is_configured_success:
        raise AssertionError("Adapter did not mark configured success")
    if adapter_result.reply_text != FAKE_ADAPTER_REPLY:
        raise AssertionError("Adapter did not route the fake FW reply text")
    if adapter_result.source.mode != "framework_text_chat_live_message":
        raise AssertionError("Adapter source mode did not mark live message path")
    if not fake_live.prompts or DEFAULT_DRC_LIVE_ADAPTER_MESSAGE not in fake_live.prompts[0]:
        raise AssertionError("Adapter did not build a DRC live-reply prompt")

    blocked_fake_live = FakeLiveReplyService()
    blocked_config = AppConfig(
        framework_project_root="<fake-framework-root>",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_live_message_enabled=False,
    )
    blocked_adapter = FrameworkPostAdviceChatAdapter(
        blocked_config,
        live_reply_service=blocked_fake_live,
    )
    blocked_result = blocked_adapter.reply(
        context=_sample_context(),
        prior_messages=[],
        user_message=DEFAULT_DRC_LIVE_ADAPTER_MESSAGE,
    )
    if blocked_result.status != "blocked-live-message-gate":
        raise AssertionError("Adapter did not block when live-message gate is off")
    if blocked_fake_live.prompts:
        raise AssertionError("Adapter called live service while gate was off")

    service = PostAdviceChatService(config=config, framework_adapter=adapter)
    session = service.create_session(ChatSessionCreateRequest(context=_sample_context()))
    response = service.add_message(
        session.session_id,
        ChatMessageRequest(message=DEFAULT_DRC_LIVE_ADAPTER_MESSAGE),
    )
    if response is None:
        raise AssertionError("PostAdviceChatService returned no response")
    if response.source.mode != "framework_text_chat_live_message":
        raise AssertionError("DRC chat service did not preserve live FW source mode")
    if response.reply.content != FAKE_ADAPTER_REPLY:
        raise AssertionError("DRC chat service did not route the adapter reply")

    rendered = "\n".join(
        [
            "drc_adapter_live_reply_status: " + adapter_result.status,
            "drc_adapter_live_reply_source_mode: " + adapter_result.source.mode,
            "drc_adapter_live_reply_configured_success: "
            + str(adapter_result.is_configured_success),
            "drc_adapter_live_reply_prompt_captured: " + str(bool(fake_live.prompts)),
            "drc_adapter_live_reply_reply_text_present: "
            + str(bool(adapter_result.reply_text.strip())),
            "drc_chat_api_live_reply_source_mode: " + response.source.mode,
            "drc_chat_api_live_reply_message_count: " + str(len(response.messages)),
            "drc_chat_api_live_reply_body_hidden: True",
        ]
    )
    if FAKE_ADAPTER_REPLY in rendered:
        raise AssertionError("Source-tree smoke must not print the fake reply body")
    if DEFAULT_DRC_LIVE_ADAPTER_MESSAGE in rendered:
        raise AssertionError("Source-tree smoke must not print the prompt body")
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-drc-adapter-live-reply] OK")


def _run_real_adapter_smoke(message: str) -> None:
    config = load_config()
    service = PostAdviceChatService(config=config)
    session = service.create_session(ChatSessionCreateRequest(context=_sample_context()))
    response = service.add_message(
        session.session_id,
        ChatMessageRequest(message=message),
    )
    if response is None:
        raise AssertionError("PostAdviceChatService returned no response")

    rendered = "\n".join(
        [
            "drc_adapter_live_reply_status: "
            + ("responded" if response.reply.content.strip() else "error-empty-response"),
            "drc_adapter_live_reply_source_mode: " + response.source.mode,
            "drc_adapter_live_reply_response_received: "
            + str(bool(response.reply.content.strip())),
            "drc_adapter_live_reply_response_text_length_present: "
            + str(response.reply.content is not None),
            "drc_adapter_live_reply_response_non_empty: "
            + str(bool(response.reply.content.strip())),
            "drc_chat_api_live_reply_session_id_present: " + str(bool(response.session_id)),
            "drc_chat_api_live_reply_message_count: " + str(len(response.messages)),
            "drc_chat_api_live_reply_body_hidden: True",
            "drc_adapter_live_reply_next_step: verify-live-fw-response-through-smartphone-web-ui",
        ]
    )
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-drc-adapter-live-reply-configured] RESULT")
    print(rendered)
    print(
        "One DRC post-advice chat message was routed through the framework adapter. "
        "Prompt and response bodies were hidden by this smoke."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat DRC adapter live-reply smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Route one DRC chat message through the real FW adapter path.",
    )
    parser.add_argument(
        "--message",
        default=DEFAULT_DRC_LIVE_ADAPTER_MESSAGE,
        help=(
            "Optional bounded DRC chat message for strict local adapter smoke. "
            "The body is sent only in --require-real-framework mode and is never printed."
        ),
    )
    args = parser.parse_args()

    if args.require_real_framework:
        required_flags = {
            "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE": "1",
            "DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT": "1",
            "DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE": "1",
        }
        for name, expected in required_flags.items():
            if os.getenv(name) != expected:
                raise SystemExit(
                    f"Set {name}={expected} before running strict DRC adapter live reply."
                )
        _run_real_adapter_smoke(args.message)
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
