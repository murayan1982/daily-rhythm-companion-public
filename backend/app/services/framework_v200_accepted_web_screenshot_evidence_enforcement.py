"""v2.0.0 Day73 accepted Web screenshot evidence enforcement contract.

This module validates public-safe, marker-only evidence that the v2.0.0
real-execution requirements were confirmed through the Web UI with screenshot
confirmation. It deliberately does not call providers, Google Health, backend
APIs, browsers, Flutter, audio playback, image inspection, release builders,
release zips, GitHub, or the network in default mode.

Raw screenshots remain operator evidence and must not be committed. Public
records should store only redacted screenshot references or screenshot manifest
markers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import re


@dataclass(frozen=True)
class V200WebScreenshotCapability:
    """One capability that requires Web execution screenshot evidence."""

    key: str
    label: str
    requires_screenshot: bool
    extra_required_markers: tuple[str, ...]


@dataclass(frozen=True)
class V200AcceptedWebScreenshotEvidenceContract:
    """Public-safe Day73 accepted Web screenshot evidence enforcement contract."""

    status: str
    requirement_key: str
    web_capabilities: tuple[V200WebScreenshotCapability, ...]
    non_web_review_items: tuple[str, ...]
    required_common_markers: tuple[str, ...]
    required_screenshot_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    web_execution_required_for_v200_completion: bool
    screenshot_required_for_web_execution: bool
    api_only_counts_as_success: bool
    source_tree_only_counts_as_success: bool
    next_focus: str


@dataclass(frozen=True)
class V200AcceptedWebScreenshotEvidenceValidation:
    """Validation result for Day73 accepted Web screenshot evidence."""

    status: str
    accepted_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool
    screenshot_references_public_safe: bool


def build_v200_accepted_web_screenshot_evidence_contract() -> V200AcceptedWebScreenshotEvidenceContract:
    """Build the Day73 enforcement contract."""

    common_markers = (
        "status",
        "actual_drc_backend_api_used",
        "web_ui_execution_confirmed",
        "web_execution_result_visible",
        "operator_review_accepted",
        "not_api_only",
        "not_source_tree_only",
        "not_mock_only",
        "not_fallback",
        "not_skipped",
        "not_unavailable",
        "not_placeholder",
    )
    screenshot_markers = (
        "screenshot_captured",
        "screenshot_reference_recorded",
        "screenshot_public_safe_redaction_confirmed",
    )
    return V200AcceptedWebScreenshotEvidenceContract(
        status="accepted-web-screenshot-evidence-enforcement-ready",
        requirement_key="v200_accepted_web_screenshot_evidence_enforcement",
        web_capabilities=(
            V200WebScreenshotCapability(
                key="real_llm_web_answer",
                label="real LLM Web answer generation",
                requires_screenshot=True,
                extra_required_markers=("real_provider_response_confirmed",),
            ),
            V200WebScreenshotCapability(
                key="real_tts_web_audio_output",
                label="real TTS Web audio output",
                requires_screenshot=True,
                extra_required_markers=("real_provider_audio_synthesis_confirmed", "audible_playback_confirmed"),
            ),
            V200WebScreenshotCapability(
                key="real_google_health_sleep_data",
                label="real Google Health sleep data retrieval",
                requires_screenshot=True,
                extra_required_markers=("real_sleep_data_source_confirmed", "sleep_summary_normalized_confirmed"),
            ),
            V200WebScreenshotCapability(
                key="web_image_display",
                label="Web image display",
                requires_screenshot=True,
                extra_required_markers=("repository_safe_asset_displayed", "displayed_asset_identity_confirmed"),
            ),
        ),
        non_web_review_items=(
            "image_asset_intake_accepted",
            "public_repo_final_sweep_accepted",
            "final_aggregate_review_accepted",
            "all_web_screenshot_evidence_reviewed",
        ),
        required_common_markers=common_markers,
        required_screenshot_markers=screenshot_markers,
        public_safe_omissions=(
            "api_keys",
            "oauth_tokens",
            "authorization_headers",
            "raw_prompts",
            "raw_answers",
            "raw_provider_payloads",
            "raw_google_health_payloads",
            "raw_sleep_events",
            "raw_audio",
            "raw_screenshot_files",
            "raw_lan_ips",
            "private_paths",
            "production_claims",
            "app_store_claims",
            "medical_claims",
        ),
        forbidden_success_states=(
            "api_only_success",
            "source_tree_only_success",
            "web_ui_not_confirmed",
            "screenshot_missing",
            "screenshot_reference_missing",
            "screenshot_not_reviewed",
            "raw_screenshot_committed",
            "actual_drc_backend_api_not_used",
            "mock_only",
            "fallback_only",
            "skipped",
            "unavailable",
            "placeholder",
            "error",
            "raw_prompt",
            "raw_answer",
            "raw_provider_payload",
            "raw_google_health_payload",
            "raw_sleep_events",
            "raw_audio",
            "raw_lan_ip",
            "private_path",
            "api_key",
            "oauth_token",
            "production_claim",
            "app_store_claim",
            "medical_claim",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        web_execution_required_for_v200_completion=True,
        screenshot_required_for_web_execution=True,
        api_only_counts_as_success=False,
        source_tree_only_counts_as_success=False,
        next_focus="Collect accepted Web UI screenshot evidence before rebuilding any v2.0.0 release candidate zip.",
    )


def render_v200_accepted_web_screenshot_evidence_contract(
    contract: V200AcceptedWebScreenshotEvidenceContract,
) -> str:
    """Render the Day73 contract as deterministic text."""

    lines = [
        f"v200_accepted_web_screenshot_evidence_status: {contract.status}",
        f"v200_accepted_web_screenshot_evidence_requirement_key: {contract.requirement_key}",
        "v200_accepted_web_screenshot_evidence_operator_run_required: "
        f"{contract.operator_run_required}",
        f"v200_accepted_web_screenshot_evidence_mock_safe_default: {contract.mock_safe_default}",
        "v200_accepted_web_screenshot_evidence_web_execution_required_for_v200_completion: "
        f"{contract.web_execution_required_for_v200_completion}",
        "v200_accepted_web_screenshot_evidence_screenshot_required_for_web_execution: "
        f"{contract.screenshot_required_for_web_execution}",
        "v200_accepted_web_screenshot_evidence_api_only_counts_as_success: "
        f"{contract.api_only_counts_as_success}",
        "v200_accepted_web_screenshot_evidence_source_tree_only_counts_as_success: "
        f"{contract.source_tree_only_counts_as_success}",
        "v200_accepted_web_screenshot_evidence_default_external_network_status: not-called",
        "v200_accepted_web_screenshot_evidence_default_provider_status: not-called",
        "v200_accepted_web_screenshot_evidence_default_google_health_status: not-called",
        "v200_accepted_web_screenshot_evidence_default_backend_status: not-started",
        "v200_accepted_web_screenshot_evidence_default_browser_status: not-opened",
        "v200_accepted_web_screenshot_evidence_default_screenshot_status: not-inspected",
        f"v200_accepted_web_screenshot_evidence_next_focus: {contract.next_focus}",
        "v200_accepted_web_screenshot_evidence_required_common_markers: "
        + ",".join(contract.required_common_markers),
        "v200_accepted_web_screenshot_evidence_required_screenshot_markers: "
        + ",".join(contract.required_screenshot_markers),
        "v200_accepted_web_screenshot_evidence_non_web_review_items: "
        + ",".join(contract.non_web_review_items),
        "v200_accepted_web_screenshot_evidence_public_safe_omissions: "
        + ",".join(contract.public_safe_omissions),
        "v200_accepted_web_screenshot_evidence_forbidden_success_states: "
        + ",".join(contract.forbidden_success_states),
    ]
    for capability in contract.web_capabilities:
        extra = ",".join(capability.extra_required_markers)
        lines.append(
            "v200_accepted_web_screenshot_evidence_capability_"
            f"{capability.key}: screenshot_required={capability.requires_screenshot};extra={extra}"
        )
    return "\n".join(lines)


def _is_public_safe_reference(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    unsafe_patterns = (
        r"[A-Za-z]:\\",
        r"/Users/",
        r"/home/[^/]+/",
        r"E:\\work\\",
        r"C:\\Users\\",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
    )
    return not any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in unsafe_patterns)


def _unsafe_public_flags_absent(evidence: Mapping[str, object]) -> bool:
    unsafe_boolean_fields = (
        "api_keys_included",
        "oauth_tokens_included",
        "authorization_headers_included",
        "raw_prompts_included",
        "raw_answers_included",
        "raw_provider_payloads_included",
        "raw_google_health_payloads_included",
        "raw_sleep_events_included",
        "raw_audio_included",
        "raw_screenshot_files_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "production_or_store_claims_included",
        "medical_claims_included",
    )
    return all(evidence.get(field) is not True for field in unsafe_boolean_fields)


def validate_v200_accepted_web_screenshot_evidence(
    evidence: Mapping[str, object],
) -> V200AcceptedWebScreenshotEvidenceValidation:
    """Validate public-safe Day73 operator evidence."""

    contract = build_v200_accepted_web_screenshot_evidence_contract()
    accepted: list[str] = []
    missing_capabilities: list[str] = []
    missing_markers: list[str] = []
    screenshot_references_public_safe = True

    capabilities = evidence.get("capabilities")
    if not isinstance(capabilities, Mapping):
        capabilities = {}

    for capability in contract.web_capabilities:
        item = capabilities.get(capability.key)
        if not isinstance(item, Mapping):
            missing_capabilities.append(capability.key)
            missing_markers.append(f"{capability.key}.capability_present")
            continue

        required = list(contract.required_common_markers)
        if capability.requires_screenshot:
            required.extend(contract.required_screenshot_markers)
        required.extend(capability.extra_required_markers)

        capability_missing = []
        for marker in required:
            if marker == "status":
                if item.get("status") != "accepted":
                    capability_missing.append(f"{capability.key}.status=accepted")
            elif item.get(marker) is not True:
                capability_missing.append(f"{capability.key}.{marker}")

        screenshot_reference = item.get("screenshot_reference")
        if capability.requires_screenshot and not _is_public_safe_reference(screenshot_reference):
            screenshot_references_public_safe = False
            capability_missing.append(f"{capability.key}.screenshot_reference_public_safe")

        if capability_missing:
            missing_capabilities.append(capability.key)
            missing_markers.extend(capability_missing)
        else:
            accepted.append(capability.key)

    for marker in contract.non_web_review_items:
        if evidence.get(marker) is not True:
            missing_markers.append(marker)

    public_safe = _unsafe_public_flags_absent(evidence)
    forbidden_success_states_absent = all(
        evidence.get(state) is not True for state in contract.forbidden_success_states
    )
    status = (
        "accepted"
        if not missing_capabilities
        and not missing_markers
        and public_safe
        and forbidden_success_states_absent
        and screenshot_references_public_safe
        else "incomplete"
    )
    return V200AcceptedWebScreenshotEvidenceValidation(
        status=status,
        accepted_capabilities=tuple(accepted),
        missing_capabilities=tuple(missing_capabilities),
        missing_markers=tuple(missing_markers),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_success_states_absent,
        screenshot_references_public_safe=screenshot_references_public_safe,
    )


def render_v200_accepted_web_screenshot_evidence_validation(
    validation: V200AcceptedWebScreenshotEvidenceValidation,
) -> str:
    """Render Day73 operator evidence validation as deterministic text."""

    return "\n".join(
        [
            "v200_accepted_web_screenshot_evidence_validation_status: "
            f"{validation.status}",
            "v200_accepted_web_screenshot_evidence_accepted_capabilities: "
            + ",".join(validation.accepted_capabilities),
            "v200_accepted_web_screenshot_evidence_missing_capabilities: "
            + ",".join(validation.missing_capabilities),
            "v200_accepted_web_screenshot_evidence_missing_markers: "
            + ",".join(validation.missing_markers),
            "v200_accepted_web_screenshot_evidence_public_safe: "
            f"{validation.public_safe}",
            "v200_accepted_web_screenshot_evidence_forbidden_success_states_absent: "
            f"{validation.forbidden_success_states_absent}",
            "v200_accepted_web_screenshot_evidence_screenshot_references_public_safe: "
            f"{validation.screenshot_references_public_safe}",
            "v200_accepted_web_screenshot_evidence_requirement_satisfied: "
            f"{validation.status == 'accepted'}",
        ]
    )
