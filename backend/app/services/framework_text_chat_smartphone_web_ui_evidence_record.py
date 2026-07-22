from __future__ import annotations

from dataclasses import dataclass


EXPECTED_EVIDENCE_STATUS = "verified"
EXPECTED_LIVE_SOURCE_MODE = "framework_text_chat_live_message"


@dataclass(frozen=True)
class SmartphoneWebUiLiveReplyEvidenceRecordInput:
    """Public-safe input for the v1.9.0 smartphone Web UI evidence record.

    The record intentionally stores booleans, source labels, and shape/status
    fields only. It must not store prompt bodies, response bodies, provider
    payloads, API key values, authorization headers, private paths, or raw LAN IPs.
    """

    evidence_status: str
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
    body_hidden_in_evidence: bool


@dataclass(frozen=True)
class SmartphoneWebUiLiveReplyEvidenceRecordResult:
    """Rendered v1.9.0 public-safe smartphone Web UI evidence record."""

    status: str
    evidence_status: str
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
    body_hidden_in_evidence: bool
    safe_summary: str
    next_step: str


def evaluate_smartphone_web_ui_live_reply_evidence_record(
    evidence: SmartphoneWebUiLiveReplyEvidenceRecordInput,
) -> SmartphoneWebUiLiveReplyEvidenceRecordResult:
    """Evaluate whether the smartphone Web UI evidence is ready to record."""

    source_mode_matches = (
        evidence.source_mode_matches and evidence.source_mode == EXPECTED_LIVE_SOURCE_MODE
    )
    required_flags = (
        evidence.evidence_status == EXPECTED_EVIDENCE_STATUS,
        source_mode_matches,
        evidence.backend_status_ok,
        evidence.api_base_url_visible,
        evidence.advice_result_visible,
        evidence.post_advice_chat_visible,
        evidence.chat_source_visible,
        evidence.live_reply_visible,
        evidence.response_non_empty,
        evidence.body_hidden_in_evidence,
    )
    recorded = all(required_flags)
    status = "recorded" if recorded else "incomplete"
    next_step = (
        "prepare-v190-fw40-demo-evidence-summary"
        if recorded
        else "complete-v190-smartphone-web-ui-evidence-record"
    )
    safe_summary = (
        "v1.9.0 smartphone Web UI evidence is recorded: the DRC post-advice "
        "chat UI displayed a non-empty live FW text-chat reply through the "
        "actual backend API, while only public-safe booleans and labels are stored."
        if recorded
        else "v1.9.0 smartphone Web UI evidence is incomplete; rerun the public-safe checklist."
    )

    return SmartphoneWebUiLiveReplyEvidenceRecordResult(
        status=status,
        evidence_status=evidence.evidence_status,
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
        body_hidden_in_evidence=evidence.body_hidden_in_evidence,
        safe_summary=safe_summary,
        next_step=next_step,
    )


def render_smartphone_web_ui_live_reply_evidence_record(
    result: SmartphoneWebUiLiveReplyEvidenceRecordResult,
) -> list[str]:
    """Render public-safe evidence record lines.

    Do not add prompt text, response text, provider payloads, raw URLs, secrets,
    absolute local paths, or raw exception/provider messages to this output.
    """

    return [
        "v190_smartphone_web_ui_live_reply_record_status: " + result.status,
        "v190_smartphone_web_ui_live_reply_record_from_evidence_status: "
        + result.evidence_status,
        "v190_smartphone_web_ui_live_reply_record_evidence_mode: "
        + result.evidence_mode,
        "v190_smartphone_web_ui_live_reply_record_source_mode: "
        + result.source_mode,
        "v190_smartphone_web_ui_live_reply_record_source_mode_matches: "
        + str(result.source_mode_matches),
        "v190_smartphone_web_ui_backend_status_ok: "
        + str(result.backend_status_ok),
        "v190_smartphone_web_ui_api_base_url_visible: "
        + str(result.api_base_url_visible),
        "v190_smartphone_web_ui_advice_result_visible: "
        + str(result.advice_result_visible),
        "v190_smartphone_web_ui_post_advice_chat_visible: "
        + str(result.post_advice_chat_visible),
        "v190_smartphone_web_ui_chat_source_visible: "
        + str(result.chat_source_visible),
        "v190_smartphone_web_ui_live_reply_visible: "
        + str(result.live_reply_visible),
        "v190_smartphone_web_ui_response_non_empty: "
        + str(result.response_non_empty),
        "v190_smartphone_web_ui_body_hidden_in_evidence: "
        + str(result.body_hidden_in_evidence),
        "v190_smartphone_web_ui_live_reply_record_next_step: "
        + result.next_step,
        "v190_smartphone_web_ui_live_reply_record_safe_summary: "
        + result.safe_summary,
    ]
