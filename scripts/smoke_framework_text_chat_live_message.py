r"""Day30 smoke for one explicitly gated live FW text-chat message.

Default mode is source-tree only. It verifies the public-safe result renderer,
placeholder-secret guard, and fake response summarization without importing AI
Character Framework or calling ask/ask_stream.

Optional local mode may send exactly one bounded text message through FW4.0.0:

    python scripts\smoke_framework_text_chat_live_message.py --require-real-framework

Local mode requires all of these operator-controlled gates:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<local framework checkout>
```
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
from app.services.framework_text_chat_live_message_smoke import (
    DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT,
    LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
    FrameworkTextChatLiveMessageSmokeResult,
    FrameworkTextChatLiveMessageSmokeService,
    _looks_like_placeholder_secret,
    _response_summary,
    render_live_message_smoke,
)


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


def _assert_public_safe(text: str) -> None:
    forbidden_patterns = [
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
        r"Authorization:\s*Bearer",
        r"[A-Za-z]:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Public-safe output contained forbidden pattern: {pattern}")


def _fake_config() -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root="<configured-framework-root>",
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_preflight_enabled=True,
        framework_text_chat_session_preflight_enabled=True,
        framework_text_chat_live_message_enabled=True,
    )


def _run_source_tree_smoke() -> None:
    if not _looks_like_placeholder_secret("<local-secret-value>"):
        raise AssertionError("placeholder-looking provider env value was not detected")
    if not _looks_like_placeholder_secret("replace-me"):
        raise AssertionError("replace-me provider env value was not detected")
    if _looks_like_placeholder_secret("not-a-placeholder-but-not-a-real-key"):
        raise AssertionError("ordinary non-placeholder value was incorrectly blocked")

    fake_summary = _response_summary(_FakeResponse("こんにちは。"))
    if fake_summary["type"] != "_FakeResponse":
        raise AssertionError("fake response type summary mismatch")
    if not fake_summary["non_empty"]:
        raise AssertionError("fake response should be treated as non-empty")
    if fake_summary["text_length"] <= 0:
        raise AssertionError("fake response text length should be positive")

    blocked = FrameworkTextChatLiveMessageSmokeResult(
        status="blocked",
        gate_status="blocked",
        gate_enabled=False,
        session_created=True,
        has_session_info=True,
        prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
        provider_call_attempted=False,
        response_received=False,
        response_type=None,
        response_text_length=None,
        response_non_empty=False,
        exception_type=None,
        failure_kind="gate-not-ready",
        safe_message="Live text-chat message execution is blocked by default.",
        next_step="enable-explicit-live-text-chat-message-gate-locally",
    )
    responded = FrameworkTextChatLiveMessageSmokeResult(
        status="responded",
        gate_status="ready",
        gate_enabled=True,
        session_created=True,
        has_session_info=True,
        prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
        provider_call_attempted=True,
        response_received=True,
        response_type="str",
        response_text_length=8,
        response_non_empty=True,
        exception_type=None,
        failure_kind="none",
        safe_message=(
            "Live text-chat message smoke completed with one bounded "
            "session.ask call. Prompt and response bodies are hidden."
        ),
        next_step="record-live-text-chat-message-evidence",
    )
    placeholder_blocked = FrameworkTextChatLiveMessageSmokeResult(
        status="blocked-provider-env-placeholder",
        gate_status="ready",
        gate_enabled=True,
        session_created=True,
        has_session_info=True,
        prompt_shape=LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
        provider_call_attempted=False,
        response_received=False,
        response_type=None,
        response_text_length=None,
        response_non_empty=False,
        exception_type=None,
        failure_kind="provider-env-placeholder",
        safe_message="A configured provider env value looks like a placeholder.",
        next_step="replace-placeholder-provider-env-locally",
    )

    rendered = "\n---\n".join(
        [
            render_live_message_smoke(blocked),
            render_live_message_smoke(responded),
            render_live_message_smoke(placeholder_blocked),
        ]
    )
    for needle in [
        "live_text_chat_message_smoke_status: blocked",
        "live_text_chat_message_smoke_status: responded",
        "live_text_chat_message_smoke_status: blocked-provider-env-placeholder",
        "live_text_chat_message_smoke_prompt_shape: <bounded-live-text-chat-smoke-prompt>",
        "live_text_chat_message_smoke_provider_call_attempted: True",
        "live_text_chat_message_smoke_response_received: True",
        "live_text_chat_message_smoke_response_non_empty: True",
        "live_text_chat_message_smoke_next_step: record-live-text-chat-message-evidence",
    ]:
        if needle not in rendered:
            raise AssertionError(f"Missing expected live message smoke render line: {needle}")
    if DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT in rendered:
        raise AssertionError("Rendered smoke output must not print the prompt body")
    _assert_public_safe(rendered)

    # Instantiate the service so source-tree checks catch import/config regressions.
    service = FrameworkTextChatLiveMessageSmokeService(_fake_config())
    if service is None:
        raise AssertionError("service instantiation failed")

    print("[smoke-framework-text-chat-live-message] OK")


def _run_real_live_message(prompt: str) -> None:
    config = load_config()
    service = FrameworkTextChatLiveMessageSmokeService(config)
    result = service.run(prompt=prompt)
    rendered = render_live_message_smoke(result)
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-live-message-configured] RESULT")
    print(rendered)
    if result.status == "responded":
        print(
            "One bounded session.ask call was made. Prompt and response bodies were hidden."
        )
    else:
        print(
            "No live provider response body was printed. Provider call may have been skipped or failed safely as shown above."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat live-message smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Run the explicitly gated local live-message smoke.",
    )
    parser.add_argument(
        "--message",
        default=DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT,
        help=(
            "Optional bounded message for local smoke. The body is sent only in "
            "--require-real-framework mode and is never printed."
        ),
    )
    args = parser.parse_args()

    if args.require_real_framework:
        if os.getenv("DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1 "
                "before running strict live-message smoke."
            )
        if os.getenv("DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1 before running "
                "the live-message smoke."
            )
        _run_real_live_message(args.message)
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
