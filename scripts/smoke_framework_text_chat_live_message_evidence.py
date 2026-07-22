r"""Day31 smoke for public-safe live text-chat message evidence.

Default mode is source-tree only. It verifies the evidence renderer with fake
Day30 smoke results and does not import AI Character Framework or call providers.

Optional local mode may run the Day30 strict smoke once and then render the
public-safe evidence shape:

    python scripts\smoke_framework_text_chat_live_message_evidence.py --require-real-framework

Local mode requires the existing Day30 gates. It may make one bounded
``session.ask`` call through the Day30 smoke service. Prompt and response bodies
are hidden.
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

from app.config import load_config
from app.services.framework_text_chat_live_message_evidence import (
    FrameworkTextChatLiveMessageEvidenceService,
    fake_responded_live_message_smoke_result,
    render_live_message_evidence,
)
from app.services.framework_text_chat_live_message_smoke import (
    DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT,
    LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
    FrameworkTextChatLiveMessageSmokeResult,
    FrameworkTextChatLiveMessageSmokeService,
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
                f"Public-safe evidence output contained forbidden pattern: {pattern}"
            )


def _run_source_tree_smoke() -> None:
    service = FrameworkTextChatLiveMessageEvidenceService()
    verified = service.from_smoke_result(fake_responded_live_message_smoke_result())

    blocked = service.from_smoke_result(
        FrameworkTextChatLiveMessageSmokeResult(
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
    )

    rendered = "\n---\n".join(
        [render_live_message_evidence(verified), render_live_message_evidence(blocked)]
    )
    for needle in [
        "live_text_chat_message_evidence_status: verified",
        "live_text_chat_message_evidence_smoke_status: responded",
        "live_text_chat_message_evidence_gate_status: ready",
        "live_text_chat_message_evidence_provider_call_attempted: True",
        "live_text_chat_message_evidence_response_received: True",
        "live_text_chat_message_evidence_response_text_length_present: True",
        "live_text_chat_message_evidence_response_non_empty: True",
        "live_text_chat_message_evidence_next_step: wire-live-text-chat-response-through-drc-adapter",
        "live_text_chat_message_evidence_status: not-verified",
    ]:
        if needle not in rendered:
            raise AssertionError(f"Missing expected live-message evidence line: {needle}")
    if DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT in rendered:
        raise AssertionError("Rendered evidence must not print the prompt body")
    if "こんにちは" in rendered:
        raise AssertionError("Rendered evidence must not print a response body")
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-live-message-evidence] OK")


def _run_real_evidence(prompt: str) -> None:
    config = load_config()
    smoke_result = FrameworkTextChatLiveMessageSmokeService(config).run(prompt=prompt)
    evidence = FrameworkTextChatLiveMessageEvidenceService().from_smoke_result(
        smoke_result
    )
    rendered = render_live_message_evidence(evidence)
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-live-message-evidence-configured] RESULT")
    print(rendered)
    if evidence.status == "verified":
        print(
            "One bounded session.ask call was made by the Day30 smoke path. "
            "Prompt and response bodies were hidden."
        )
    else:
        print(
            "Live-message evidence was not verified. Provider response body was not printed."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat live-message evidence smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Run evidence rendering after the explicitly gated local live-message smoke.",
    )
    parser.add_argument(
        "--message",
        default=DEFAULT_LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT,
        help=(
            "Optional bounded message for local evidence smoke. The body is sent only "
            "in --require-real-framework mode and is never printed."
        ),
    )
    args = parser.parse_args()

    if args.require_real_framework:
        if os.getenv("DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1 "
                "before running strict live-message evidence."
            )
        if os.getenv("DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1 before running "
                "strict live-message evidence."
            )
        _run_real_evidence(args.message)
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
