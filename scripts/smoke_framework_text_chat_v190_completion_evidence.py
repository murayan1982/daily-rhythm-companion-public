"""Day35 smoke for v1.9.0 FW text-chat smartphone Web completion evidence.

This is a source-tree evidence renderer. It does not start Flutter, open a
browser, import AI Character Framework, create sessions, call ask/ask_stream, or
call providers. It combines the public-safe evidence chain already established
by Day28 through Day34.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_text_chat_v190_completion_evidence import (
    EXPECTED_SOURCE_MODE,
    FrameworkTextChatV190CompletionInput,
    evaluate_framework_text_chat_v190_completion,
    render_framework_text_chat_v190_completion,
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
                "Public-safe v1.9.0 completion evidence contained forbidden pattern: "
                + pattern
            )


def _build_completed_evidence() -> FrameworkTextChatV190CompletionInput:
    return FrameworkTextChatV190CompletionInput(
        session_creation_verified=True,
        live_message_verified=True,
        drc_adapter_live_reply_verified=True,
        smartphone_web_ui_live_reply_recorded=True,
        actual_backend_api_used=True,
        source_mode=EXPECTED_SOURCE_MODE,
        response_non_empty=True,
        body_hidden_in_evidence=True,
        prompt_body_hidden_in_evidence=True,
    )


def main() -> None:
    result = evaluate_framework_text_chat_v190_completion(_build_completed_evidence())
    rendered = "\n".join(render_framework_text_chat_v190_completion(result))
    _assert_public_safe(rendered)
    if result.status != "completed":
        raise AssertionError("Expected completed v1.9.0 FW text-chat smartphone Web evidence")
    if result.next_step != "prepare-v190-release-readiness-checkpoint":
        raise AssertionError("Unexpected Day35 next step: " + result.next_step)
    if EXPECTED_SOURCE_MODE not in rendered:
        raise AssertionError("Missing expected live source mode")

    print("[smoke-framework-text-chat-v190-completion-evidence] OK")


if __name__ == "__main__":
    main()
