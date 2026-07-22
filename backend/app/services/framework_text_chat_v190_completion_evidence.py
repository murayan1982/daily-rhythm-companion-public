from __future__ import annotations

from dataclasses import dataclass


EXPECTED_SOURCE_MODE = "framework_text_chat_live_message"


@dataclass(frozen=True)
class FrameworkTextChatV190CompletionInput:
    """Public-safe v1.9.0 FW text-chat smartphone Web completion evidence.

    This shape intentionally stores booleans, source labels, and status markers
    only. It must never store prompt bodies, response bodies, provider payloads,
    API key values, authorization headers, private paths, raw LAN IPs, or raw
    provider error payloads.
    """

    session_creation_verified: bool
    live_message_verified: bool
    drc_adapter_live_reply_verified: bool
    smartphone_web_ui_live_reply_recorded: bool
    actual_backend_api_used: bool
    source_mode: str
    response_non_empty: bool
    body_hidden_in_evidence: bool
    prompt_body_hidden_in_evidence: bool


@dataclass(frozen=True)
class FrameworkTextChatV190CompletionResult:
    """Rendered v1.9.0 text-chat smartphone Web completion result."""

    status: str
    source_mode: str
    source_mode_matches: bool
    session_creation_verified: bool
    live_message_verified: bool
    drc_adapter_live_reply_verified: bool
    smartphone_web_ui_live_reply_recorded: bool
    actual_backend_api_used: bool
    response_non_empty: bool
    body_hidden_in_evidence: bool
    prompt_body_hidden_in_evidence: bool
    safe_summary: str
    next_step: str


def evaluate_framework_text_chat_v190_completion(
    evidence: FrameworkTextChatV190CompletionInput,
) -> FrameworkTextChatV190CompletionResult:
    """Evaluate whether the v1.9.0 FW text-chat smartphone Web path is complete."""

    source_mode_matches = evidence.source_mode == EXPECTED_SOURCE_MODE
    complete = all(
        (
            evidence.session_creation_verified,
            evidence.live_message_verified,
            evidence.drc_adapter_live_reply_verified,
            evidence.smartphone_web_ui_live_reply_recorded,
            evidence.actual_backend_api_used,
            source_mode_matches,
            evidence.response_non_empty,
            evidence.body_hidden_in_evidence,
            evidence.prompt_body_hidden_in_evidence,
        )
    )
    status = "completed" if complete else "incomplete"
    next_step = (
        "prepare-v190-release-readiness-checkpoint"
        if complete
        else "complete-v190-fw40-text-chat-smartphone-web-evidence"
    )
    safe_summary = (
        "v1.9.0 FW4.0.0 text-chat smartphone Web path is complete: session "
        "creation, one bounded live message, DRC adapter/API routing, and "
        "smartphone Web UI display were verified while evidence stayed public-safe."
        if complete
        else "v1.9.0 FW4.0.0 text-chat smartphone Web path is incomplete; finish the public-safe evidence chain."
    )
    return FrameworkTextChatV190CompletionResult(
        status=status,
        source_mode=evidence.source_mode,
        source_mode_matches=source_mode_matches,
        session_creation_verified=evidence.session_creation_verified,
        live_message_verified=evidence.live_message_verified,
        drc_adapter_live_reply_verified=evidence.drc_adapter_live_reply_verified,
        smartphone_web_ui_live_reply_recorded=evidence.smartphone_web_ui_live_reply_recorded,
        actual_backend_api_used=evidence.actual_backend_api_used,
        response_non_empty=evidence.response_non_empty,
        body_hidden_in_evidence=evidence.body_hidden_in_evidence,
        prompt_body_hidden_in_evidence=evidence.prompt_body_hidden_in_evidence,
        safe_summary=safe_summary,
        next_step=next_step,
    )


def render_framework_text_chat_v190_completion(
    result: FrameworkTextChatV190CompletionResult,
) -> list[str]:
    """Render public-safe v1.9.0 text-chat smartphone Web completion lines."""

    return [
        "v190_fw40_text_chat_smartphone_web_completion_status: " + result.status,
        "v190_fw40_text_chat_smartphone_web_source_mode: " + result.source_mode,
        "v190_fw40_text_chat_smartphone_web_source_mode_matches: "
        + str(result.source_mode_matches),
        "v190_fw40_text_chat_session_creation_verified: "
        + str(result.session_creation_verified),
        "v190_fw40_text_chat_live_message_verified: "
        + str(result.live_message_verified),
        "v190_fw40_text_chat_drc_adapter_live_reply_verified: "
        + str(result.drc_adapter_live_reply_verified),
        "v190_fw40_text_chat_smartphone_web_ui_live_reply_recorded: "
        + str(result.smartphone_web_ui_live_reply_recorded),
        "v190_fw40_text_chat_actual_backend_api_used: "
        + str(result.actual_backend_api_used),
        "v190_fw40_text_chat_response_non_empty: "
        + str(result.response_non_empty),
        "v190_fw40_text_chat_prompt_body_hidden_in_evidence: "
        + str(result.prompt_body_hidden_in_evidence),
        "v190_fw40_text_chat_response_body_hidden_in_evidence: "
        + str(result.body_hidden_in_evidence),
        "v190_fw40_text_chat_smartphone_web_next_step: " + result.next_step,
        "v190_fw40_text_chat_smartphone_web_safe_summary: " + result.safe_summary,
    ]
