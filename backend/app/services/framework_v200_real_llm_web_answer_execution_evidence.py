"""v2.0.0 Day64 real LLM Web answer execution evidence acceptance.

This module validates marker-only evidence for the first v2.0.0 real execution
requirement. It deliberately avoids provider SDK imports, backend calls,
browser automation, framework session creation, prompt inspection, answer-body
logging, screenshot parsing, and release artifact creation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200RealLlmWebAnswerExecutionEvidenceItem:
    """One required Day64 execution evidence marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealLlmWebAnswerExecutionEvidenceResult:
    """Public-safe Day64 execution evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200RealLlmWebAnswerExecutionEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200RealLlmWebAnswerExecutionEvidenceValidation:
    """Validation result for a marker-only Day64 evidence summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_real_llm_web_answer_execution_evidence_contract() -> V200RealLlmWebAnswerExecutionEvidenceResult:
    """Build the Day64 real LLM execution evidence contract.

    The returned structure is static and source-tree safe. It must not call a
    provider, DRC backend, browser, AI Character Framework, Flutter, or release
    packaging command.
    """

    evidence_items = (
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "A prepared operator must explicitly enable the real LLM run; "
                "normal checks must remain credential-free."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="backend_advice_api_called",
            status="required",
            description=(
                "The configured run must call the actual Daily Rhythm "
                "Companion /advice backend API path."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="configured_framework_route_used",
            status="required",
            description=(
                "The backend route must use the configured framework / real "
                "LLM integration path rather than mock-only logic."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="source_engine_framework_confirmed",
            status="required",
            description=(
                "The operator must confirm source.engine is exactly framework."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="message_non_empty_confirmed",
            status="required",
            description=(
                "The operator must confirm the returned advice message is "
                "non-empty without publishing the answer body."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="smartphone_web_ui_visible_answer_confirmed",
            status="required",
            description=(
                "The operator must confirm the smartphone Web UI visibly "
                "displays the generated answer."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="fallback_or_skip_not_counted",
            status="required",
            description=(
                "Fallback, skipped, unavailable, and error states must be "
                "visible when they occur but must not count as success."
            ),
        ),
        V200RealLlmWebAnswerExecutionEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description=(
                "Shared evidence must be marker-only and omit secrets, raw "
                "prompts, answer bodies, provider payloads, LAN IPs, private "
                "paths, browser storage, and screenshots."
            ),
        ),
    )

    return V200RealLlmWebAnswerExecutionEvidenceResult(
        status="operator-execution-evidence-contract-ready",
        requirement_key="real_llm_web_answer",
        evidence_items=evidence_items,
        required_operator_markers=(
            "explicit_operator_opt_in_enabled",
            "backend_advice_api_called",
            "configured_framework_route_used",
            "source_engine_framework_confirmed",
            "message_non_empty_confirmed",
            "smartphone_web_ui_visible_answer_confirmed",
            "fallback_or_skip_not_counted",
            "public_safe_evidence_recorded",
        ),
        public_safe_omissions=(
            "api_keys",
            "oauth_tokens",
            "authorization_headers",
            "raw_prompt_bodies",
            "answer_bodies",
            "raw_provider_payloads",
            "raw_provider_errors_with_private_payloads",
            "raw_lan_ips",
            "private_paths",
            "raw_screenshots",
            "browser_storage_dumps",
        ),
        forbidden_success_states=(
            "mock_counted_as_success",
            "framework_fallback_counted_as_success",
            "fallback_counted_as_success",
            "skipped_counted_as_success",
            "unavailable_counted_as_success",
            "error_counted_as_success",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="real-tts-web-audio-output-execution-evidence",
    )


def render_v200_real_llm_web_answer_execution_evidence(
    result: V200RealLlmWebAnswerExecutionEvidenceResult,
) -> str:
    """Render public-safe Day64 execution evidence markers."""

    lines = [
        "v200_real_llm_web_answer_execution_evidence_status: " + result.status,
        "v200_real_llm_web_answer_execution_requirement_key: " + result.requirement_key,
        "v200_real_llm_web_answer_execution_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_llm_web_answer_execution_mock_safe_default: "
        + str(result.mock_safe_default),
        "v200_real_llm_web_answer_execution_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_real_llm_web_answer_execution_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
        "v200_real_llm_web_answer_execution_forbidden_success_states: "
        + ",".join(result.forbidden_success_states),
    ]

    for item in result.evidence_items:
        lines.append(
            f"v200_real_llm_web_answer_execution_evidence_{item.key}: {item.status}"
        )

    lines.extend(
        [
            "v200_real_llm_web_answer_execution_default_provider_call_status: not-called",
            "v200_real_llm_web_answer_execution_default_backend_status: not-started",
            "v200_real_llm_web_answer_execution_default_browser_status: not-opened",
            "v200_real_llm_web_answer_execution_default_framework_session_status: not-created",
            "v200_real_llm_web_answer_execution_default_answer_body_status: not-recorded",
            "v200_real_llm_web_answer_execution_default_screenshot_status: not-recorded",
            "v200_real_llm_web_answer_execution_public_evidence_body_policy: marker-only-no-prompt-no-answer-body",
            "v200_real_llm_web_answer_execution_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_real_llm_web_answer_execution_operator_evidence(
    evidence: Mapping[str, object],
) -> V200RealLlmWebAnswerExecutionEvidenceValidation:
    """Validate marker-only Day64 operator evidence.

    This helper checks booleans only. It must not be pointed at raw screenshots,
    provider payloads, prompt logs, answer logs, browser storage dumps, token
    files, generated artifacts, or release work folders.
    """

    contract = build_v200_real_llm_web_answer_execution_evidence_contract()
    accepted: list[str] = []
    missing: list[str] = []

    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    forbidden_publication_flags = (
        "api_keys_included",
        "oauth_tokens_included",
        "authorization_headers_included",
        "raw_prompt_body_included",
        "answer_body_included",
        "raw_provider_payloads_included",
        "raw_provider_errors_with_private_payloads_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "raw_screenshots_included",
        "browser_storage_dumps_included",
    )
    public_safe = not any(evidence.get(flag) is True for flag in forbidden_publication_flags)
    forbidden_success_states_absent = not any(
        evidence.get(flag) is True for flag in contract.forbidden_success_states
    )

    status = (
        "accepted"
        if not missing and public_safe and forbidden_success_states_absent
        else "incomplete-or-unsafe"
    )

    return V200RealLlmWebAnswerExecutionEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_success_states_absent,
    )
