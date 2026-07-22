from __future__ import annotations

from dataclasses import dataclass

from app.services.framework_text_chat_session_diagnosis import (
    FrameworkTextChatSessionDiagnosisAttempt,
    FrameworkTextChatSessionDiagnosisResult,
)


@dataclass(frozen=True)
class FrameworkTextChatSessionCreatedEvidence:
    """Public-safe evidence extracted from a session creation diagnosis.

    This boundary intentionally carries only shapes, statuses, and booleans.
    It must not include provider payloads, prompts, responses, or secret values.
    """

    status: str
    likely_cwd_dependency: bool
    created_attempt_name: str | None
    created_attempt_cwd_shape: str | None
    current_cwd_failure_kind: str | None
    current_cwd_exception_type: str | None
    session_created: bool
    has_session_info: bool
    safe_summary: str
    next_step: str


class FrameworkTextChatSessionCreatedEvidenceService:
    """Create a compact public-safe summary after strict session diagnosis.

    Day28 uses this after the operator has confirmed local provider env readiness
    and strict session diagnosis reaches ``status: created``. It does not import
    the framework, create a session, call ask/ask_stream, or call provider APIs.
    """

    def from_diagnosis(
        self,
        result: FrameworkTextChatSessionDiagnosisResult,
    ) -> FrameworkTextChatSessionCreatedEvidence:
        current_attempt = _find_attempt(result, "current-cwd")
        created_attempt = _first_created_attempt(result)

        if created_attempt is None:
            return FrameworkTextChatSessionCreatedEvidence(
                status=result.status,
                likely_cwd_dependency=result.likely_cwd_dependency,
                created_attempt_name=None,
                created_attempt_cwd_shape=None,
                current_cwd_failure_kind=current_attempt.failure_kind
                if current_attempt
                else None,
                current_cwd_exception_type=current_attempt.exception_type
                if current_attempt
                else None,
                session_created=False,
                has_session_info=False,
                safe_summary=(
                    "Framework text chat session was not created. Keep the current "
                    "diagnosis path and inspect the next public-safe failure kind."
                ),
                next_step="continue-session-diagnosis",
            )

        return FrameworkTextChatSessionCreatedEvidence(
            status="created",
            likely_cwd_dependency=result.likely_cwd_dependency,
            created_attempt_name=created_attempt.attempt_name,
            created_attempt_cwd_shape=created_attempt.cwd_shape,
            current_cwd_failure_kind=current_attempt.failure_kind
            if current_attempt
            else None,
            current_cwd_exception_type=current_attempt.exception_type
            if current_attempt
            else None,
            session_created=True,
            has_session_info=created_attempt.has_session_info,
            safe_summary=(
                "Framework text chat session creation is now public-safe verified. "
                "The successful path is session creation only; no ask, ask_stream, "
                "provider API, STT, TTS, or Live2D/VTS call was made."
            ),
            next_step="design-explicit-live-text-chat-message-gate",
        )


def render_session_created_evidence(
    evidence: FrameworkTextChatSessionCreatedEvidence,
) -> str:
    """Render public-safe evidence lines for logs and docs."""

    lines = [
        "session_created_evidence_status: " + evidence.status,
        "session_created_evidence_likely_cwd_dependency: "
        + str(evidence.likely_cwd_dependency),
        "session_created_evidence_created_attempt: "
        + str(evidence.created_attempt_name),
        "session_created_evidence_created_cwd_shape: "
        + str(evidence.created_attempt_cwd_shape),
        "session_created_evidence_current_cwd_exception_type: "
        + str(evidence.current_cwd_exception_type),
        "session_created_evidence_current_cwd_failure_kind: "
        + str(evidence.current_cwd_failure_kind),
        "session_created_evidence_session_created: "
        + str(evidence.session_created),
        "session_created_evidence_has_session_info: "
        + str(evidence.has_session_info),
        "session_created_evidence_next_step: " + evidence.next_step,
        "session_created_evidence_safe_summary: " + evidence.safe_summary,
    ]
    return "\n".join(lines)


def _find_attempt(
    result: FrameworkTextChatSessionDiagnosisResult,
    attempt_name: str,
) -> FrameworkTextChatSessionDiagnosisAttempt | None:
    for attempt in result.attempts:
        if attempt.attempt_name == attempt_name:
            return attempt
    return None


def _first_created_attempt(
    result: FrameworkTextChatSessionDiagnosisResult,
) -> FrameworkTextChatSessionDiagnosisAttempt | None:
    for attempt in result.attempts:
        if attempt.session_created:
            return attempt
    return None
