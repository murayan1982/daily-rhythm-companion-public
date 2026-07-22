r"""Day33 smoke for smartphone Web UI live FW reply evidence.

Default mode is source-tree only and does not start Flutter, open a browser,
import AI Character Framework, or call providers. It validates the public-safe
shape used to record manual smartphone Web UI evidence.

Manual recording mode accepts booleans from an operator-run smartphone Web check:

    python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence.py ^
      --record-manual-ui-evidence ^
      --backend-status-ok ^
      --api-base-url-visible ^
      --advice-result-visible ^
      --post-advice-chat-visible ^
      --chat-source-visible ^
      --live-reply-visible ^
      --response-non-empty ^
      --body-hidden

The script never accepts or prints prompt bodies, response bodies, provider
payloads, API key values, private paths, or raw LAN IP addresses.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.framework_text_chat_smartphone_web_ui_evidence import (
    EXPECTED_LIVE_SOURCE_MODE,
    SmartphoneWebUiLiveReplyEvidenceInput,
    evaluate_smartphone_web_ui_live_reply_evidence,
    render_smartphone_web_ui_live_reply_evidence,
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
                "Public-safe smartphone Web UI evidence contained forbidden pattern: "
                + pattern
            )


def _sample_verified_input(*, evidence_mode: str) -> SmartphoneWebUiLiveReplyEvidenceInput:
    return SmartphoneWebUiLiveReplyEvidenceInput(
        backend_status_ok=True,
        api_base_url_visible=True,
        advice_result_visible=True,
        post_advice_chat_visible=True,
        chat_source_visible=True,
        live_reply_visible=True,
        response_non_empty=True,
        response_body_hidden_in_evidence=True,
        source_mode=EXPECTED_LIVE_SOURCE_MODE,
        evidence_mode=evidence_mode,
    )


def _render_and_validate(evidence: SmartphoneWebUiLiveReplyEvidenceInput) -> str:
    result = evaluate_smartphone_web_ui_live_reply_evidence(evidence)
    rendered = "\n".join(render_smartphone_web_ui_live_reply_evidence(result))
    _assert_public_safe(rendered)
    return rendered


def _run_source_tree_smoke() -> None:
    rendered = _render_and_validate(
        _sample_verified_input(evidence_mode="source-tree-synthetic-ui-evidence")
    )
    required = [
        "smartphone_web_ui_live_reply_evidence_status: verified",
        "smartphone_web_ui_live_reply_source_mode: framework_text_chat_live_message",
        "smartphone_web_ui_backend_status_ok: True",
        "smartphone_web_ui_api_base_url_visible: True",
        "smartphone_web_ui_chat_source_visible: True",
        "smartphone_web_ui_response_non_empty: True",
        "smartphone_web_ui_body_hidden_in_evidence: True",
        "smartphone_web_ui_next_step: record-v190-live-text-chat-smartphone-web-ui-evidence",
    ]
    for needle in required:
        if needle not in rendered:
            raise AssertionError(f"Missing source-tree evidence marker: {needle}")
    print("[smoke-framework-text-chat-smartphone-web-ui-evidence] OK")


def _run_manual_recording(args: argparse.Namespace) -> None:
    evidence = SmartphoneWebUiLiveReplyEvidenceInput(
        backend_status_ok=args.backend_status_ok,
        api_base_url_visible=args.api_base_url_visible,
        advice_result_visible=args.advice_result_visible,
        post_advice_chat_visible=args.post_advice_chat_visible,
        chat_source_visible=args.chat_source_visible,
        live_reply_visible=args.live_reply_visible,
        response_non_empty=args.response_non_empty,
        response_body_hidden_in_evidence=args.body_hidden,
        source_mode=args.source_mode,
        evidence_mode="manual-smartphone-web-ui",
    )
    rendered = _render_and_validate(evidence)
    print("[smoke-framework-text-chat-smartphone-web-ui-evidence-configured] RESULT")
    print(rendered)
    print(
        "Smartphone Web UI evidence was rendered without prompt bodies, response "
        "bodies, provider payloads, API key values, private paths, or raw LAN IPs."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render public-safe smartphone Web UI live FW reply evidence."
    )
    parser.add_argument(
        "--record-manual-ui-evidence",
        action="store_true",
        help="Render evidence from operator-confirmed smartphone Web UI checks.",
    )
    parser.add_argument("--backend-status-ok", action="store_true")
    parser.add_argument("--api-base-url-visible", action="store_true")
    parser.add_argument("--advice-result-visible", action="store_true")
    parser.add_argument("--post-advice-chat-visible", action="store_true")
    parser.add_argument("--chat-source-visible", action="store_true")
    parser.add_argument("--live-reply-visible", action="store_true")
    parser.add_argument("--response-non-empty", action="store_true")
    parser.add_argument("--body-hidden", action="store_true")
    parser.add_argument("--source-mode", default=EXPECTED_LIVE_SOURCE_MODE)
    args = parser.parse_args()

    if args.record_manual_ui_evidence:
        _run_manual_recording(args)
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
