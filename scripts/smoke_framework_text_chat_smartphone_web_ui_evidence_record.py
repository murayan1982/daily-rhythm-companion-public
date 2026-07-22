r"""Day34 smoke for recording v1.9.0 smartphone Web UI live FW reply evidence.

Default mode is source-tree only. It does not start Flutter, open a browser,
import AI Character Framework, create a framework session, call ask/ask_stream,
or call providers. It verifies that Day33 manual smartphone Web UI evidence can
be represented as a public-safe v1.9.0 record.

Manual recording mode accepts booleans from an operator-run smartphone Web check:

    python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence_record.py ^
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
)
from app.services.framework_text_chat_smartphone_web_ui_evidence_record import (
    SmartphoneWebUiLiveReplyEvidenceRecordInput,
    evaluate_smartphone_web_ui_live_reply_evidence_record,
    render_smartphone_web_ui_live_reply_evidence_record,
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
                "Public-safe smartphone Web UI record contained forbidden pattern: "
                + pattern
            )


def _build_record_input(
    *,
    backend_status_ok: bool,
    api_base_url_visible: bool,
    advice_result_visible: bool,
    post_advice_chat_visible: bool,
    chat_source_visible: bool,
    live_reply_visible: bool,
    response_non_empty: bool,
    body_hidden: bool,
    source_mode: str,
    evidence_mode: str,
) -> SmartphoneWebUiLiveReplyEvidenceRecordInput:
    evidence_result = evaluate_smartphone_web_ui_live_reply_evidence(
        SmartphoneWebUiLiveReplyEvidenceInput(
            backend_status_ok=backend_status_ok,
            api_base_url_visible=api_base_url_visible,
            advice_result_visible=advice_result_visible,
            post_advice_chat_visible=post_advice_chat_visible,
            chat_source_visible=chat_source_visible,
            live_reply_visible=live_reply_visible,
            response_non_empty=response_non_empty,
            response_body_hidden_in_evidence=body_hidden,
            source_mode=source_mode,
            evidence_mode=evidence_mode,
        )
    )
    return SmartphoneWebUiLiveReplyEvidenceRecordInput(
        evidence_status=evidence_result.status,
        evidence_mode=evidence_result.evidence_mode,
        source_mode=evidence_result.source_mode,
        source_mode_matches=evidence_result.source_mode_matches,
        backend_status_ok=evidence_result.backend_status_ok,
        api_base_url_visible=evidence_result.api_base_url_visible,
        advice_result_visible=evidence_result.advice_result_visible,
        post_advice_chat_visible=evidence_result.post_advice_chat_visible,
        chat_source_visible=evidence_result.chat_source_visible,
        live_reply_visible=evidence_result.live_reply_visible,
        response_non_empty=evidence_result.response_non_empty,
        body_hidden_in_evidence=evidence_result.response_body_hidden_in_evidence,
    )


def _render_and_validate(record_input: SmartphoneWebUiLiveReplyEvidenceRecordInput) -> str:
    record = evaluate_smartphone_web_ui_live_reply_evidence_record(record_input)
    rendered = "\n".join(render_smartphone_web_ui_live_reply_evidence_record(record))
    _assert_public_safe(rendered)
    return rendered


def _run_source_tree_smoke() -> None:
    rendered = _render_and_validate(
        _build_record_input(
            backend_status_ok=True,
            api_base_url_visible=True,
            advice_result_visible=True,
            post_advice_chat_visible=True,
            chat_source_visible=True,
            live_reply_visible=True,
            response_non_empty=True,
            body_hidden=True,
            source_mode=EXPECTED_LIVE_SOURCE_MODE,
            evidence_mode="source-tree-synthetic-smartphone-web-ui-record",
        )
    )
    required = [
        "v190_smartphone_web_ui_live_reply_record_status: recorded",
        "v190_smartphone_web_ui_live_reply_record_from_evidence_status: verified",
        "v190_smartphone_web_ui_live_reply_record_source_mode: framework_text_chat_live_message",
        "v190_smartphone_web_ui_live_reply_record_source_mode_matches: True",
        "v190_smartphone_web_ui_backend_status_ok: True",
        "v190_smartphone_web_ui_response_non_empty: True",
        "v190_smartphone_web_ui_body_hidden_in_evidence: True",
        "v190_smartphone_web_ui_live_reply_record_next_step: prepare-v190-fw40-demo-evidence-summary",
    ]
    for needle in required:
        if needle not in rendered:
            raise AssertionError(f"Missing source-tree record marker: {needle}")
    print("[smoke-framework-text-chat-smartphone-web-ui-evidence-record] OK")


def _run_manual_recording(args: argparse.Namespace) -> None:
    rendered = _render_and_validate(
        _build_record_input(
            backend_status_ok=args.backend_status_ok,
            api_base_url_visible=args.api_base_url_visible,
            advice_result_visible=args.advice_result_visible,
            post_advice_chat_visible=args.post_advice_chat_visible,
            chat_source_visible=args.chat_source_visible,
            live_reply_visible=args.live_reply_visible,
            response_non_empty=args.response_non_empty,
            body_hidden=args.body_hidden,
            source_mode=args.source_mode,
            evidence_mode="manual-smartphone-web-ui-record",
        )
    )
    print("[smoke-framework-text-chat-smartphone-web-ui-evidence-record-configured] RESULT")
    print(rendered)
    print(
        "v1.9.0 smartphone Web UI live-reply record was rendered without prompt "
        "bodies, response bodies, provider payloads, API key values, private paths, "
        "or raw LAN IPs."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-manual-ui-evidence", action="store_true")
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
