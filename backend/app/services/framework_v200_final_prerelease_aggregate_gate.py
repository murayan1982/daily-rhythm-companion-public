"""v2.0.0 Day70 final prerelease aggregate gate evidence acceptance.

This module validates marker-only evidence for the final prerelease aggregate
before building a v2.0.0 fixed release candidate. It deliberately avoids
release builds, release zip creation, release zip inspection, provider calls,
Google Health calls, backend calls, browser automation, screenshot inspection,
audio/image inspection, GitHub publication, and network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200FinalPrereleaseAggregateEvidenceItem:
    """One required Day70 final prerelease aggregate marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200FinalPrereleaseAggregateResult:
    """Public-safe Day70 final prerelease aggregate contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200FinalPrereleaseAggregateEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    release_zip_created_by_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200FinalPrereleaseAggregateValidation:
    """Validation result for a marker-only Day70 aggregate summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_final_prerelease_aggregate_contract() -> V200FinalPrereleaseAggregateResult:
    """Build the Day70 final prerelease aggregate evidence contract.

    The returned contract is static and credential-free. It is safe for normal
    local checks and public documentation because it contains no keys, tokens,
    provider payloads, screenshots, audio, health records, generated image
    metadata, private paths, or release artifacts.
    """

    required_markers = (
        "day52_to_day58_foundation_gates_passed",
        "day64_real_llm_web_answer_execution_accepted",
        "day65_real_tts_web_audio_execution_accepted",
        "day66_real_google_health_sleep_data_execution_accepted",
        "day67_image_asset_intake_accepted",
        "day68_web_image_display_execution_accepted",
        "day69_public_repo_final_sweep_accepted",
        "smartphone_web_evidence_reviewed",
        "api_level_evidence_reviewed",
        "fallback_skipped_unavailable_not_counted",
        "mock_safe_default_preserved",
        "credential_free_default_checks_preserved",
        "public_safe_marker_only_evidence_preserved",
        "release_zip_not_created_by_aggregate_check",
        "ready_to_build_one_fixed_v200_release_candidate",
    )
    return V200FinalPrereleaseAggregateResult(
        status="final-prerelease-aggregate-contract-ready",
        requirement_key="v200_final_prerelease_aggregate_gate",
        evidence_items=(
            V200FinalPrereleaseAggregateEvidenceItem(
                key="day52_to_day58_foundation_gates_passed",
                status="source-tree-required",
                description="The v2.0.0 foundation gates from Day52 through Day58 remain available and passing.",
            ),
            V200FinalPrereleaseAggregateEvidenceItem(
                key="day64_to_day68_real_execution_evidence_accepted",
                status="operator-required",
                description="Real LLM, TTS, Google Health, image intake, and Web image display evidence records have been accepted.",
            ),
            V200FinalPrereleaseAggregateEvidenceItem(
                key="day69_public_repo_final_sweep_accepted",
                status="operator-required",
                description="The public repository final sweep was accepted after reviewing the execution evidence records.",
            ),
            V200FinalPrereleaseAggregateEvidenceItem(
                key="fallback_skipped_unavailable_not_counted",
                status="operator-required",
                description="Skipped, unavailable, fallback-only, mock-only, and error states were not counted as real execution success.",
            ),
            V200FinalPrereleaseAggregateEvidenceItem(
                key="ready_to_build_one_fixed_v200_release_candidate",
                status="operator-required",
                description="The source tree is ready for one fixed v2.0.0 release candidate build, followed by fixed-zip verification.",
            ),
        ),
        required_operator_markers=required_markers,
        public_safe_omissions=(
            "api_keys",
            "oauth_tokens",
            "client_secrets",
            "authorization_headers",
            "raw_provider_payloads",
            "prompt_bodies",
            "answer_bodies",
            "raw_google_health_payloads",
            "raw_sleep_events",
            "precise_personal_sleep_timestamps",
            "generated_audio_artifacts",
            "raw_audio_urls",
            "raw_screenshots",
            "raw_lan_ips",
            "private_paths",
            "local_token_files",
            "browser_storage_dumps",
            "unreviewed_image_artifacts",
            "private_generated_prompts",
            "copyrighted_source_image_references",
            "release_zips",
            "release_build_outputs",
            "dev_handoff_notes",
            "replacement_bundles",
            "extracted_release_workdirs",
            "cache_folders",
            "production_or_store_claims",
            "medical_claims",
        ),
        forbidden_success_states=(
            "day64_not_accepted",
            "day65_not_accepted",
            "day66_not_accepted",
            "day67_not_accepted",
            "day68_not_accepted",
            "day69_not_accepted",
            "api_only_success",
            "web_ui_not_confirmed",
            "mock_only",
            "fallback_only",
            "skipped",
            "unavailable",
            "error",
            "raw_provider_payload",
            "raw_google_health_payload",
            "raw_audio",
            "raw_screenshot",
            "raw_lan_ip",
            "private_path",
            "api_key",
            "oauth_token",
            "release_zip_created_by_day70",
            "release_zip_verified_by_day70",
            "replacement_bundle_present",
            "extracted_workdir_present",
            "cache_folder_present",
            "production_claim",
            "app_store_claim",
            "medical_claim",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        release_zip_created_by_default=False,
        next_focus="Build one fixed v2.0.0 release candidate zip, then run fixed-zip verification without rebuilding.",
    )


def render_v200_final_prerelease_aggregate(result: V200FinalPrereleaseAggregateResult) -> str:
    """Render the final prerelease aggregate contract as deterministic text."""

    lines = [
        f"v200_final_prerelease_aggregate_gate_status: {result.status}",
        f"v200_final_prerelease_aggregate_gate_requirement_key: {result.requirement_key}",
        f"v200_final_prerelease_aggregate_gate_operator_run_required: {result.operator_run_required}",
        f"v200_final_prerelease_aggregate_gate_mock_safe_default: {result.mock_safe_default}",
        f"v200_final_prerelease_aggregate_gate_release_zip_created_by_default: {result.release_zip_created_by_default}",
        "v200_final_prerelease_aggregate_gate_default_external_network_status: not-called",
        "v200_final_prerelease_aggregate_gate_default_provider_status: not-called",
        "v200_final_prerelease_aggregate_gate_default_google_health_status: not-called",
        "v200_final_prerelease_aggregate_gate_default_browser_status: not-opened",
        "v200_final_prerelease_aggregate_gate_default_release_zip_status: not-created",
        f"v200_final_prerelease_aggregate_gate_next_focus: {result.next_focus}",
        "v200_final_prerelease_aggregate_gate_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_final_prerelease_aggregate_gate_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
        "v200_final_prerelease_aggregate_gate_forbidden_success_states: "
        + ",".join(result.forbidden_success_states),
    ]
    for item in result.evidence_items:
        lines.append(f"v200_final_prerelease_aggregate_gate_item_{item.key}: {item.status}")
    return "\n".join(lines)


def validate_v200_final_prerelease_aggregate_operator_evidence(
    evidence: Mapping[str, object],
) -> V200FinalPrereleaseAggregateValidation:
    """Validate a redacted marker-only Day70 aggregate evidence summary."""

    contract = build_v200_final_prerelease_aggregate_contract()
    accepted: list[str] = []
    missing: list[str] = []
    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    unsafe_boolean_fields = (
        "api_keys_included",
        "oauth_tokens_included",
        "client_secrets_included",
        "authorization_headers_included",
        "raw_provider_payloads_included",
        "prompt_bodies_included",
        "answer_bodies_included",
        "raw_google_health_payloads_included",
        "raw_sleep_events_included",
        "precise_personal_sleep_timestamps_included",
        "generated_audio_artifacts_included",
        "raw_audio_urls_included",
        "raw_screenshots_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "local_token_files_included",
        "browser_storage_dumps_included",
        "unreviewed_image_artifacts_included",
        "private_generated_prompts_included",
        "copyrighted_source_image_references_included",
        "release_zips_included",
        "release_build_outputs_included",
        "dev_handoff_notes_included",
        "replacement_bundles_included",
        "extracted_release_workdirs_included",
        "cache_folders_included",
        "production_or_store_claims_included",
        "medical_claims_included",
    )
    public_safe = all(evidence.get(field) is False for field in unsafe_boolean_fields)

    state = str(evidence.get("result_state", "final_prerelease_aggregate_passed"))
    forbidden_absent = state not in contract.forbidden_success_states
    status = "accepted" if not missing and public_safe and forbidden_absent else "rejected"

    return V200FinalPrereleaseAggregateValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_absent,
    )
