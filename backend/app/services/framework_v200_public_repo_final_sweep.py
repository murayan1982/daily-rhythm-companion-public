"""v2.0.0 Day69 public repository final sweep evidence acceptance.

This module validates marker-only evidence for the public repository final sweep.
It deliberately avoids GitHub publishing, release builds, release zip creation,
provider calls, Google Health calls, backend calls, browser automation,
screenshot inspection, image generation, audio generation, and network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200PublicRepoFinalSweepEvidenceItem:
    """One required Day69 public repository final sweep marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200PublicRepoFinalSweepResult:
    """Public-safe Day69 final sweep evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200PublicRepoFinalSweepEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200PublicRepoFinalSweepValidation:
    """Validation result for a marker-only Day69 final sweep summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_public_repo_final_sweep_contract() -> V200PublicRepoFinalSweepResult:
    """Build the Day69 public repository final sweep evidence contract.

    The returned contract is intentionally static and credential-free. It is
    safe for normal local checks and public documentation because it contains no
    provider configuration, paths, evidence payloads, screenshots, audio, image
    binaries, or release artifacts.
    """

    required_markers = (
        "day57_public_repo_readiness_review_accepted",
        "day64_real_llm_execution_evidence_reviewed",
        "day65_real_tts_execution_evidence_reviewed",
        "day66_real_google_health_execution_evidence_reviewed",
        "day67_image_asset_intake_evidence_reviewed",
        "day68_web_image_display_evidence_reviewed",
        "license_scope_confirmed",
        "public_positioning_claims_reviewed",
        "public_docs_secret_hygiene_final_scan_completed",
        "release_surface_local_artifacts_absent",
        "raw_evidence_material_excluded",
        "mock_safe_default_preserved",
        "public_safe_evidence_recorded",
    )
    return V200PublicRepoFinalSweepResult(
        status="public-repo-final-sweep-contract-ready",
        requirement_key="public_repo_final_sweep",
        evidence_items=(
            V200PublicRepoFinalSweepEvidenceItem(
                key="day57_public_repo_readiness_review_accepted",
                status="operator-required",
                description="Day57 public repo readiness evidence review has been accepted.",
            ),
            V200PublicRepoFinalSweepEvidenceItem(
                key="day64_to_day68_execution_evidence_reviewed",
                status="operator-required",
                description="Day64 through Day68 real execution evidence records have been reviewed as public-safe marker-only evidence.",
            ),
            V200PublicRepoFinalSweepEvidenceItem(
                key="public_docs_secret_hygiene_final_scan_completed",
                status="operator-required",
                description="README, roadmap, public docs, scripts index, and release surface were checked for public-safety regressions.",
            ),
            V200PublicRepoFinalSweepEvidenceItem(
                key="release_surface_local_artifacts_absent",
                status="operator-required",
                description="Local handoff notes, helper bundles, extracted work folders, caches, and private artifacts are absent from the release surface.",
            ),
            V200PublicRepoFinalSweepEvidenceItem(
                key="mock_safe_default_preserved",
                status="operator-required",
                description="Mock-safe and credential-free default operation remains intact after the execution evidence additions.",
            ),
        ),
        required_operator_markers=required_markers,
        public_safe_omissions=(
            "api_keys",
            "oauth_tokens",
            "client_secrets",
            "authorization_headers",
            "raw_provider_payloads",
            "raw_google_health_payloads",
            "raw_sleep_events",
            "precise_personal_sleep_timestamps",
            "generated_audio_artifacts",
            "raw_screenshots",
            "raw_lan_ips",
            "private_paths",
            "local_token_files",
            "browser_storage_dumps",
            "unreviewed_image_artifacts",
            "private_generated_prompts",
            "copyrighted_source_image_references",
            "dev_handoff_notes",
            "replacement_bundles",
            "extracted_release_workdirs",
            "cache_folders",
            "production_or_store_claims",
            "medical_claims",
        ),
        forbidden_success_states=(
            "day57_not_accepted",
            "day64_not_accepted",
            "day65_not_accepted",
            "day66_not_accepted",
            "day67_not_accepted",
            "day68_not_accepted",
            "unreviewed_evidence",
            "raw_provider_payload",
            "raw_google_health_payload",
            "raw_audio",
            "raw_screenshot",
            "raw_lan_ip",
            "private_path",
            "api_key",
            "oauth_token",
            "local_token_file",
            "replacement_bundle_present",
            "extracted_workdir_present",
            "cache_folder_present",
            "production_claim",
            "app_store_claim",
            "medical_claim",
            "skipped",
            "unavailable",
            "fallback_only",
            "error",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="Day70 v2.0.0 final prerelease aggregate gate",
    )


def render_v200_public_repo_final_sweep(result: V200PublicRepoFinalSweepResult) -> str:
    """Render the final sweep contract as deterministic public-safe text."""

    lines = [
        f"v200_public_repo_final_sweep_status: {result.status}",
        f"v200_public_repo_final_sweep_requirement_key: {result.requirement_key}",
        f"v200_public_repo_final_sweep_operator_run_required: {result.operator_run_required}",
        f"v200_public_repo_final_sweep_mock_safe_default: {result.mock_safe_default}",
        "v200_public_repo_final_sweep_default_publish_status: not-run",
        "v200_public_repo_final_sweep_default_release_build_status: not-run",
        "v200_public_repo_final_sweep_default_external_network_status: not-called",
        f"v200_public_repo_final_sweep_next_focus: {result.next_focus}",
        "v200_public_repo_final_sweep_required_operator_markers: "
        + ",".join(result.required_operator_markers),
        "v200_public_repo_final_sweep_public_safe_omissions: "
        + ",".join(result.public_safe_omissions),
        "v200_public_repo_final_sweep_forbidden_success_states: "
        + ",".join(result.forbidden_success_states),
    ]
    for item in result.evidence_items:
        lines.append(f"v200_public_repo_final_sweep_item_{item.key}: {item.status}")
    return "\n".join(lines)


def validate_v200_public_repo_final_sweep_operator_evidence(
    evidence: Mapping[str, object],
) -> V200PublicRepoFinalSweepValidation:
    """Validate a redacted marker-only Day69 operator evidence summary."""

    contract = build_v200_public_repo_final_sweep_contract()
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
        "raw_google_health_payloads_included",
        "raw_sleep_events_included",
        "precise_personal_sleep_timestamps_included",
        "generated_audio_artifacts_included",
        "raw_screenshots_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "local_token_files_included",
        "browser_storage_dumps_included",
        "unreviewed_image_artifacts_included",
        "private_generated_prompts_included",
        "copyrighted_source_image_references_included",
        "dev_handoff_notes_included",
        "replacement_bundles_included",
        "extracted_release_workdirs_included",
        "cache_folders_included",
        "production_or_store_claims_included",
        "medical_claims_included",
    )
    public_safe = all(evidence.get(field) is False for field in unsafe_boolean_fields)

    state = str(evidence.get("result_state", "public_repo_final_sweep_passed"))
    forbidden_absent = state not in contract.forbidden_success_states
    status = "accepted" if not missing and public_safe and forbidden_absent else "rejected"

    return V200PublicRepoFinalSweepValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_absent,
    )
