"""v2.0.0 real LLM Web answer evidence checkpoint.

This module records the public-safe evidence contract for the first v2.0.0
pre-release gate. It does not call a provider, start a browser, call the
backend, create framework sessions, or persist prompt / response bodies.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V200RealLlmWebAnswerEvidence:
    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200RealLlmWebAnswerEvidenceResult:
    status: str
    requirement_key: str
    evidence_items: tuple[V200RealLlmWebAnswerEvidence, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


def build_v200_real_llm_web_answer_evidence() -> V200RealLlmWebAnswerEvidenceResult:
    evidence_items = (
        V200RealLlmWebAnswerEvidence(
            key="explicit_operator_opt_in",
            status="required",
            description=(
                "Real LLM execution must require an explicit operator opt-in "
                "and must not happen during normal mock-safe checks."
            ),
        ),
        V200RealLlmWebAnswerEvidence(
            key="actual_drc_backend_api",
            status="required",
            description=(
                "The Web UI must request an answer through the actual Daily "
                "Rhythm Companion backend API, not a fixture-only path."
            ),
        ),
        V200RealLlmWebAnswerEvidence(
            key="framework_or_configured_backend_route",
            status="required",
            description=(
                "The backend route must use the configured framework / LLM "
                "integration path and surface source metadata."
            ),
        ),
        V200RealLlmWebAnswerEvidence(
            key="web_ui_non_empty_answer",
            status="required",
            description=(
                "The smartphone Web UI must visibly display a non-empty answer."
            ),
        ),
        V200RealLlmWebAnswerEvidence(
            key="public_safe_evidence",
            status="required",
            description=(
                "Evidence must not commit prompt bodies, answer bodies, raw "
                "provider payloads, API keys, local paths, LAN IPs, or raw screenshots."
            ),
        ),
    )

    return V200RealLlmWebAnswerEvidenceResult(
        status="operator-evidence-contract-ready",
        requirement_key="real_llm_web_answer",
        evidence_items=evidence_items,
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="run-configured-real-llm-web-answer-operator-check",
    )


def render_v200_real_llm_web_answer_evidence(
    result: V200RealLlmWebAnswerEvidenceResult,
) -> str:
    lines = [
        "v200_real_llm_web_answer_evidence_status: " + result.status,
        "v200_real_llm_web_answer_requirement_key: " + result.requirement_key,
        "v200_real_llm_web_answer_operator_run_required: "
        + str(result.operator_run_required),
        "v200_real_llm_web_answer_mock_safe_default: "
        + str(result.mock_safe_default),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_real_llm_web_answer_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_real_llm_web_answer_default_provider_call_status: not-called",
            "v200_real_llm_web_answer_default_backend_call_status: not-called",
            "v200_real_llm_web_answer_default_browser_status: not-started",
            "v200_real_llm_web_answer_public_safe_body_policy: no-prompt-or-answer-body",
            "v200_real_llm_web_answer_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)
