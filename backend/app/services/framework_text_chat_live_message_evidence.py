from __future__ import annotations

from dataclasses import dataclass

from app.services.framework_text_chat_live_message_smoke import (
    LIVE_TEXT_CHAT_MESSAGE_SMOKE_PROMPT_SHAPE,
    FrameworkTextChatLiveMessageSmokeResult,
)


@dataclass(frozen=True)
class FrameworkTextChatLiveMessageEvidence:
    """Public-safe evidence extracted from a live text-chat message smoke.

    The evidence intentionally keeps only gate status, booleans, shapes, and
    response metadata. It must not contain prompt bodies, response bodies,
    provider payloads, request headers, token counts, API key values, private
    paths, or raw exceptions.
    """

    status: str
    smoke_status: str
    gate_status: str
    gate_enabled: bool
    session_created: bool
    has_session_info: bool
    prompt_shape: str
    provider_call_attempted: bool
    response_received: bool
    response_type: str | None
    response_text_length_present: bool
    response_non_empty: bool
    failure_kind: str
    safe_summary: str
    next_step: str


class FrameworkTextChatLiveMessageEvidenceService:
    """Convert Day30 live-message smoke output into public-safe evidence."""

    def from_smoke_result(
        self,
        result: FrameworkTextChatLiveMessageSmokeResult,
    ) -> FrameworkTextChatLiveMessageEvidence:
        """Create public-safe live-message evidence from a smoke result.

        This method does not call ``ask``, ``ask_stream``, framework providers,
        STT, TTS, Live2D/VTS, or health APIs. The caller owns whether a smoke
        result came from source-tree fake data or an explicitly gated local run.
        """

        response_text_length_present = result.response_text_length is not None

        if result.status == "responded" and result.response_non_empty:
            return FrameworkTextChatLiveMessageEvidence(
                status="verified",
                smoke_status=result.status,
                gate_status=result.gate_status,
                gate_enabled=result.gate_enabled,
                session_created=result.session_created,
                has_session_info=result.has_session_info,
                prompt_shape=result.prompt_shape,
                provider_call_attempted=result.provider_call_attempted,
                response_received=result.response_received,
                response_type=result.response_type,
                response_text_length_present=response_text_length_present,
                response_non_empty=result.response_non_empty,
                failure_kind=result.failure_kind,
                safe_summary=(
                    "Framework text chat live-message path is public-safe verified: "
                    "one bounded session.ask call returned a non-empty response. "
                    "Prompt and response bodies are hidden."
                ),
                next_step="wire-live-text-chat-response-through-drc-adapter",
            )

        return FrameworkTextChatLiveMessageEvidence(
            status="not-verified",
            smoke_status=result.status,
            gate_status=result.gate_status,
            gate_enabled=result.gate_enabled,
            session_created=result.session_created,
            has_session_info=result.has_session_info,
            prompt_shape=result.prompt_shape,
            provider_call_attempted=result.provider_call_attempted,
            response_received=result.response_received,
            response_type=result.response_type,
            response_text_length_present=response_text_length_present,
            response_non_empty=result.response_non_empty,
            failure_kind=result.failure_kind,
            safe_summary=(
                "Framework text chat live-message evidence is not verified yet. "
                "Keep the explicit local gate and inspect the public-safe smoke status."
            ),
            next_step=result.next_step,
        )


def render_live_message_evidence(
    evidence: FrameworkTextChatLiveMessageEvidence,
) -> str:
    """Render public-safe live-message evidence lines for logs and docs."""

    lines = [
        "live_text_chat_message_evidence_status: " + evidence.status,
        "live_text_chat_message_evidence_smoke_status: " + evidence.smoke_status,
        "live_text_chat_message_evidence_gate_status: " + evidence.gate_status,
        "live_text_chat_message_evidence_gate_enabled: "
        + str(evidence.gate_enabled),
        "live_text_chat_message_evidence_session_created: "
        + str(evidence.session_created),
        "live_text_chat_message_evidence_has_session_info: "
        + str(evidence.has_session_info),
        "live_text_chat_message_evidence_prompt_shape: " + evidence.prompt_shape,
        "live_text_chat_message_evidence_provider_call_attempted: "
        + str(evidence.provider_call_attempted),
        "live_text_chat_message_evidence_response_received: "
        + str(evidence.response_received),
        "live_text_chat_message_evidence_response_type: "
        + str(evidence.response_type),
        "live_text_chat_message_evidence_response_text_length_present: "
        + str(evidence.response_text_length_present),
        "live_text_chat_message_evidence_response_non_empty: "
        + str(evidence.response_non_empty),
        "live_text_chat_message_evidence_failure_kind: " + evidence.failure_kind,
        "live_text_chat_message_evidence_next_step: " + evidence.next_step,
        "live_text_chat_message_evidence_safe_summary: " + evidence.safe_summary,
    ]
    return "\n".join(lines)


def fake_responded_live_message_smoke_result() -> FrameworkTextChatLiveMessageSmokeResult:
    """Return a source-tree-only responded smoke shape without provider calls."""

    return FrameworkTextChatLiveMessageSmokeResult(
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
