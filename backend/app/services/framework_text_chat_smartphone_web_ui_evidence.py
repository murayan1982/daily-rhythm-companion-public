from __future__ import annotations

from dataclasses import dataclass


EXPECTED_LIVE_SOURCE_MODE = "framework_text_chat_live_message"


@dataclass(frozen=True)
class SmartphoneWebUiLiveReplyEvidenceInput:
    """Public-safe manual evidence flags for the smartphone Web live FW reply path.

    This input intentionally records booleans and source labels only. It must not
    carry raw prompt bodies, response bodies, API key values, provider payloads,
    private absolute paths, or raw LAN IP addresses.
    """

    backend_status_ok: bool
    api_base_url_visible: bool
    advice_result_visible: bool
    post_advice_chat_visible: bool
    chat_source_visible: bool
    live_reply_visible: bool
    response_non_empty: bool
    response_body_hidden_in_evidence: bool
    source_mode: str = EXPECTED_LIVE_SOURCE_MODE
    evidence_mode: str = "manual-smartphone-web-ui"


@dataclass(frozen=True)
class SmartphoneWebUiLiveReplyEvidenceResult:
    """Rendered public-safe evidence for smartphone Web UI verification."""

    status: str
    evidence_mode: str
    source_mode: str
    source_mode_matches: bool
    backend_status_ok: bool
    api_base_url_visible: bool
    advice_result_visible: bool
    post_advice_chat_visible: bool
    chat_source_visible: bool
    live_reply_visible: bool
    response_non_empty: bool
    response_body_hidden_in_evidence: bool
    safe_summary: str
    next_step: str


def evaluate_smartphone_web_ui_live_reply_evidence(
    evidence: SmartphoneWebUiLiveReplyEvidenceInput,
) -> SmartphoneWebUiLiveReplyEvidenceResult:
    """Evaluate smartphone Web UI evidence without exposing UI text bodies."""

    source_mode_matches = evidence.source_mode == EXPECTED_LIVE_SOURCE_MODE
    required_flags = (
        evidence.backend_status_ok,
        evidence.api_base_url_visible,
        evidence.advice_result_visible,
        evidence.post_advice_chat_visible,
        evidence.chat_source_visible,
        evidence.live_reply_visible,
        evidence.response_non_empty,
        evidence.response_body_hidden_in_evidence,
        source_mode_matches,
    )
    verified = all(required_flags)
    status = "verified" if verified else "incomplete"
    next_step = (
        "record-v190-live-text-chat-smartphone-web-ui-evidence"
        if verified
        else "complete-smartphone-web-ui-live-reply-checklist"
    )
    safe_summary = (
        "Smartphone Web UI evidence verifies that the DRC post-advice chat UI "
        "can display a live FW text-chat reply through the actual backend API. "
        "Only public-safe booleans and source labels are recorded."
        if verified
        else "Smartphone Web UI evidence is incomplete; rerun the manual checklist."
    )

    return SmartphoneWebUiLiveReplyEvidenceResult(
        status=status,
        evidence_mode=evidence.evidence_mode,
        source_mode=evidence.source_mode,
        source_mode_matches=source_mode_matches,
        backend_status_ok=evidence.backend_status_ok,
        api_base_url_visible=evidence.api_base_url_visible,
        advice_result_visible=evidence.advice_result_visible,
        post_advice_chat_visible=evidence.post_advice_chat_visible,
        chat_source_visible=evidence.chat_source_visible,
        live_reply_visible=evidence.live_reply_visible,
        response_non_empty=evidence.response_non_empty,
        response_body_hidden_in_evidence=evidence.response_body_hidden_in_evidence,
        safe_summary=safe_summary,
        next_step=next_step,
    )


def render_smartphone_web_ui_live_reply_evidence(
    result: SmartphoneWebUiLiveReplyEvidenceResult,
) -> list[str]:
    """Render public-safe evidence lines for scripts and docs.

    Do not add prompt text, response text, provider payloads, raw URLs, secrets,
    absolute local paths, or raw exception messages to this output.
    """

    return [
        "smartphone_web_ui_live_reply_evidence_status: " + result.status,
        "smartphone_web_ui_live_reply_evidence_mode: " + result.evidence_mode,
        "smartphone_web_ui_live_reply_source_mode: " + result.source_mode,
        "smartphone_web_ui_live_reply_source_mode_matches: "
        + str(result.source_mode_matches),
        "smartphone_web_ui_backend_status_ok: " + str(result.backend_status_ok),
        "smartphone_web_ui_api_base_url_visible: " + str(result.api_base_url_visible),
        "smartphone_web_ui_advice_result_visible: " + str(result.advice_result_visible),
        "smartphone_web_ui_post_advice_chat_visible: "
        + str(result.post_advice_chat_visible),
        "smartphone_web_ui_chat_source_visible: " + str(result.chat_source_visible),
        "smartphone_web_ui_live_reply_visible: " + str(result.live_reply_visible),
        "smartphone_web_ui_response_non_empty: " + str(result.response_non_empty),
        "smartphone_web_ui_body_hidden_in_evidence: "
        + str(result.response_body_hidden_in_evidence),
        "smartphone_web_ui_next_step: " + result.next_step,
        "smartphone_web_ui_safe_summary: " + result.safe_summary,
    ]
