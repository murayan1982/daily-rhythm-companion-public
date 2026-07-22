from __future__ import annotations

from dataclasses import dataclass

from app.config import AppConfig
from app.services.framework_text_chat_session_created_evidence import (
    FrameworkTextChatSessionCreatedEvidence,
)


LIVE_TEXT_CHAT_MESSAGE_GATE_ENV = "DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE"


@dataclass(frozen=True)
class FrameworkTextChatLiveMessageGateResult:
    """Public-safe readiness result for the future live message execution gate.

    Day29 only evaluates whether the operator has explicitly opened the gate for
    a later live message smoke. It does not call ``ask``, ``ask_stream``, or any
    provider API.
    """

    status: str
    gate_env_name: str
    gate_enabled: bool
    session_created_evidence_status: str
    session_created: bool
    has_session_info: bool
    safe_message: str
    next_step: str


class FrameworkTextChatLiveMessageGateService:
    """Evaluate the explicit live text-chat message gate without execution."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def evaluate(
        self,
        evidence: FrameworkTextChatSessionCreatedEvidence,
    ) -> FrameworkTextChatLiveMessageGateResult:
        """Return a public-safe gate decision for a later live message smoke.

        The gate intentionally depends on two conditions:
        - session-created evidence must already be verified; and
        - DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE must be explicitly enabled.

        This function performs no framework imports and no runtime calls.
        """

        gate_enabled = bool(
            getattr(self._config, "framework_text_chat_live_message_enabled", False)
        )
        session_ready = evidence.status == "created" and evidence.session_created

        if not session_ready:
            return FrameworkTextChatLiveMessageGateResult(
                status="session-not-ready",
                gate_env_name=LIVE_TEXT_CHAT_MESSAGE_GATE_ENV,
                gate_enabled=gate_enabled,
                session_created_evidence_status=evidence.status,
                session_created=evidence.session_created,
                has_session_info=evidence.has_session_info,
                safe_message=(
                    "Live text-chat message execution remains blocked because "
                    "session-created evidence is not verified yet."
                ),
                next_step="verify-session-created-evidence",
            )

        if not gate_enabled:
            return FrameworkTextChatLiveMessageGateResult(
                status="blocked",
                gate_env_name=LIVE_TEXT_CHAT_MESSAGE_GATE_ENV,
                gate_enabled=False,
                session_created_evidence_status=evidence.status,
                session_created=evidence.session_created,
                has_session_info=evidence.has_session_info,
                safe_message=(
                    "Live text-chat message execution is blocked by default. "
                    "Enable DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1 only for a "
                    "local operator live-message smoke."
                ),
                next_step="enable-explicit-live-text-chat-message-gate-locally",
            )

        return FrameworkTextChatLiveMessageGateResult(
            status="ready",
            gate_env_name=LIVE_TEXT_CHAT_MESSAGE_GATE_ENV,
            gate_enabled=True,
            session_created_evidence_status=evidence.status,
            session_created=evidence.session_created,
            has_session_info=evidence.has_session_info,
            safe_message=(
                "Live text-chat message execution gate is explicitly enabled. "
                "The next step may run a separate local live-message smoke that "
                "sends one bounded message."
            ),
            next_step="run-explicit-live-text-chat-message-smoke",
        )


def render_live_message_gate(
    result: FrameworkTextChatLiveMessageGateResult,
) -> str:
    """Render public-safe gate lines for logs and documentation."""

    lines = [
        "live_text_chat_message_gate_status: " + result.status,
        "live_text_chat_message_gate_env_name: " + result.gate_env_name,
        "live_text_chat_message_gate_enabled: " + str(result.gate_enabled),
        "live_text_chat_message_gate_session_created_evidence_status: "
        + result.session_created_evidence_status,
        "live_text_chat_message_gate_session_created: "
        + str(result.session_created),
        "live_text_chat_message_gate_has_session_info: "
        + str(result.has_session_info),
        "live_text_chat_message_gate_next_step: " + result.next_step,
        "live_text_chat_message_gate_safe_message: " + result.safe_message,
    ]
    return "\n".join(lines)
