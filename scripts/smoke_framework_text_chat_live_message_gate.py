r"""Day29 smoke for the explicit live text-chat message gate.

Default mode uses public-safe fake evidence and verifies the gate shape without
importing AI Character Framework or calling ask/ask_stream.

Optional local mode evaluates the gate after strict session-created evidence is
available. It still does not execute a message:

    python scripts\smoke_framework_text_chat_live_message_gate.py --require-real-framework
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

from app.config import AppConfig, load_config
from app.services.framework_text_chat_live_message_gate import (
    LIVE_TEXT_CHAT_MESSAGE_GATE_ENV,
    FrameworkTextChatLiveMessageGateService,
    render_live_message_gate,
)
from app.services.framework_text_chat_session_created_evidence import (
    FrameworkTextChatSessionCreatedEvidence,
    FrameworkTextChatSessionCreatedEvidenceService,
)
from app.services.framework_text_chat_session_diagnosis import (
    FrameworkTextChatSessionDiagnosisService,
)


def _fake_config(*, live_message_enabled: bool) -> AppConfig:
    return AppConfig(
        conversation_engine="framework",
        framework_project_root="<configured-framework-root>",
        framework_preset="text_chat",
        framework_character="default",
        framework_adapter_mode="local_import",
        framework_text_chat_smoke_enabled=True,
        framework_text_chat_preflight_enabled=True,
        framework_text_chat_session_preflight_enabled=True,
        framework_text_chat_live_message_enabled=live_message_enabled,
    )


def _created_evidence() -> FrameworkTextChatSessionCreatedEvidence:
    return FrameworkTextChatSessionCreatedEvidence(
        status="created",
        likely_cwd_dependency=True,
        created_attempt_name="framework-root-cwd",
        created_attempt_cwd_shape="<configured-framework-root>",
        current_cwd_failure_kind="unknown",
        current_cwd_exception_type="FacadeConfigError",
        session_created=True,
        has_session_info=True,
        safe_summary=(
            "Framework text chat session creation is public-safe verified. "
            "No ask, ask_stream, or provider API call was made."
        ),
        next_step="design-explicit-live-text-chat-message-gate",
    )


def _not_ready_evidence() -> FrameworkTextChatSessionCreatedEvidence:
    return FrameworkTextChatSessionCreatedEvidence(
        status="blocked",
        likely_cwd_dependency=False,
        created_attempt_name=None,
        created_attempt_cwd_shape=None,
        current_cwd_failure_kind="provider-env-missing",
        current_cwd_exception_type="OSError",
        session_created=False,
        has_session_info=False,
        safe_summary="Session-created evidence is not ready.",
        next_step="verify-session-created-evidence",
    )


def _assert_public_safe(rendered: str) -> None:
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
        if re.search(pattern, rendered, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value found in gate output: {pattern}")


def _run_source_tree_smoke() -> None:
    created = _created_evidence()
    blocked = FrameworkTextChatLiveMessageGateService(
        _fake_config(live_message_enabled=False)
    ).evaluate(created)
    ready = FrameworkTextChatLiveMessageGateService(
        _fake_config(live_message_enabled=True)
    ).evaluate(created)
    not_ready = FrameworkTextChatLiveMessageGateService(
        _fake_config(live_message_enabled=True)
    ).evaluate(_not_ready_evidence())

    blocked_rendered = render_live_message_gate(blocked)
    ready_rendered = render_live_message_gate(ready)
    not_ready_rendered = render_live_message_gate(not_ready)
    all_rendered = "\n".join([blocked_rendered, ready_rendered, not_ready_rendered])

    if blocked.status != "blocked":
        raise AssertionError(f"Expected blocked default gate, got {blocked.status!r}")
    if blocked.gate_enabled:
        raise AssertionError("Default live message gate must be disabled")
    if ready.status != "ready" or not ready.gate_enabled:
        raise AssertionError("Explicit live message gate did not become ready")
    if not_ready.status != "session-not-ready":
        raise AssertionError("Session-not-ready evidence must block the live gate")
    for needle in [
        "live_text_chat_message_gate_status: blocked",
        "live_text_chat_message_gate_status: ready",
        "live_text_chat_message_gate_status: session-not-ready",
        LIVE_TEXT_CHAT_MESSAGE_GATE_ENV,
        "run-explicit-live-text-chat-message-smoke",
    ]:
        if needle not in all_rendered:
            raise AssertionError(f"Missing expected rendered gate line: {needle}")
    for forbidden in [".ask(", ".ask_stream(", "provider response", "Authorization:"]:
        if forbidden in all_rendered:
            raise AssertionError(f"Gate output must not imply runtime execution: {forbidden}")
    _assert_public_safe(all_rendered)

    print("[smoke-framework-text-chat-live-message-gate] OK")


def _run_real_gate() -> None:
    config = load_config()
    diagnosis = FrameworkTextChatSessionDiagnosisService(config).run()
    evidence = FrameworkTextChatSessionCreatedEvidenceService().from_diagnosis(
        diagnosis
    )
    gate = FrameworkTextChatLiveMessageGateService(config).evaluate(evidence)
    rendered = render_live_message_gate(gate)
    _assert_public_safe(rendered)

    print("[smoke-framework-text-chat-live-message-gate-configured] RESULT")
    print(rendered)
    print("No ask, ask_stream, or provider call was made by this gate evaluator.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Framework text chat live-message gate smoke."
    )
    parser.add_argument(
        "--require-real-framework",
        action="store_true",
        help="Evaluate the gate after configured real framework session evidence.",
    )
    args = parser.parse_args()

    if args.require_real_framework:
        if os.getenv("DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT") != "1":
            raise SystemExit(
                "Set DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1 "
                "before running strict live-message gate evidence."
            )
        _run_real_gate()
        return

    _run_source_tree_smoke()


if __name__ == "__main__":
    main()
