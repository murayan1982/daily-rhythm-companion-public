"""v2.0.0 Day80 accepted Web evidence manifest aggregate.

The default contract is marker-only and public-safe. It does not call providers,
call Google Health, start the Daily Rhythm Companion backend, run Flutter Web,
open browsers, inspect screenshot files, build releases, call GitHub, or use the
network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import re


@dataclass(frozen=True)
class V200AcceptedWebEvidenceManifestAggregateContract:
    """Public-safe contract for the Day80 accepted private manifest aggregate."""

    status: str
    required_top_level_true_markers: tuple[str, ...]
    required_top_level_false_markers: tuple[str, ...]
    required_evidence_items: tuple[str, ...]
    web_capability_items: tuple[str, ...]
    required_web_item_true_markers: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    screenshots_required: bool
    web_ui_execution_required: bool
    actual_drc_backend_api_required: bool
    api_only_counts_as_success: bool
    source_tree_only_counts_as_success: bool
    command_output_only_counts_as_success: bool
    ready_for_v200_release_when_accepted: bool


@dataclass(frozen=True)
class V200AcceptedWebEvidenceManifestAggregateValidation:
    """Validation result for one private Day80 accepted Web evidence manifest."""

    status: str
    missing_markers: tuple[str, ...]
    public_safe: bool
    screenshot_references_public_safe: bool
    required_items_accepted: bool
    forbidden_success_states_absent: bool


def build_v200_accepted_web_evidence_manifest_aggregate_contract() -> V200AcceptedWebEvidenceManifestAggregateContract:
    """Build the Day80 accepted Web evidence manifest aggregate contract."""

    return V200AcceptedWebEvidenceManifestAggregateContract(
        status="accepted-web-evidence-manifest-aggregate-validator-ready",
        required_top_level_true_markers=(
            "all_required_evidence_items_accepted",
            "actual_drc_backend_api_used_for_web_capabilities",
            "web_ui_execution_confirmed_for_web_capabilities",
            "web_execution_results_visible",
            "all_required_screenshots_captured",
            "all_screenshot_references_recorded",
            "screenshot_references_public_safe",
            "screenshots_private_storage_confirmed",
            "operator_review_accepted",
            "not_api_only",
            "not_source_tree_only",
            "not_command_output_only",
            "not_mock_only",
            "not_fallback",
            "not_skipped",
            "not_unavailable",
            "not_placeholder",
        ),
        required_top_level_false_markers=(
            "api_keys_included",
            "oauth_tokens_included",
            "authorization_headers_included",
            "raw_screenshot_files_included",
            "raw_prompts_included",
            "raw_provider_payloads_included",
            "raw_audio_files_included",
            "raw_google_health_payloads_included",
            "private_paths_included",
            "raw_lan_ips_included",
            "production_or_store_claims_included",
            "medical_claims_included",
        ),
        required_evidence_items=(
            "real_llm_web_answer",
            "real_tts_web_audio_output",
            "real_google_health_sleep_data",
            "web_image_display",
            "image_asset_intake_review",
            "public_repo_final_sweep_review",
            "final_aggregate_review",
        ),
        web_capability_items=(
            "real_llm_web_answer",
            "real_tts_web_audio_output",
            "real_google_health_sleep_data",
            "web_image_display",
        ),
        required_web_item_true_markers=(
            "actual_drc_backend_api_used",
            "web_ui_execution_confirmed",
            "web_execution_result_visible",
            "screenshot_captured",
            "screenshot_reference_recorded",
            "screenshot_private_storage_confirmed",
            "operator_review_accepted",
        ),
        forbidden_success_states=(
            "api_only_success",
            "source_tree_only_success",
            "command_output_only_success",
            "mock_only_success",
            "fallback_success",
            "skipped_success",
            "unavailable_success",
            "placeholder_success",
            "web_ui_not_confirmed",
            "actual_drc_backend_api_not_used",
            "screenshot_missing",
            "screenshot_reference_missing",
            "screenshot_not_reviewed",
            "raw_screenshot_committed",
            "raw_provider_payload_committed",
            "raw_audio_committed",
            "raw_health_data_committed",
            "private_path_exposed",
            "raw_lan_ip_exposed",
            "api_key_exposed",
            "oauth_token_exposed",
            "authorization_header_exposed",
            "medical_claim",
            "production_claim",
            "app_store_claim",
        ),
        public_safe_omissions=(
            "raw_screenshot_files",
            "raw_prompts",
            "raw_provider_payloads",
            "raw_audio_files",
            "raw_google_health_payloads",
            "api_keys",
            "oauth_tokens",
            "authorization_headers",
            "local_paths",
            "raw_lan_ips",
            "private_operator_files",
            "production_claims",
            "app_store_claims",
            "medical_claims",
        ),
        screenshots_required=True,
        web_ui_execution_required=True,
        actual_drc_backend_api_required=True,
        api_only_counts_as_success=False,
        source_tree_only_counts_as_success=False,
        command_output_only_counts_as_success=False,
        ready_for_v200_release_when_accepted=True,
    )


def render_v200_accepted_web_evidence_manifest_aggregate_contract(
    contract: V200AcceptedWebEvidenceManifestAggregateContract,
) -> str:
    """Render the Day80 contract as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_accepted_web_evidence_manifest_aggregate_status: {contract.status}",
            f"v200_accepted_web_evidence_manifest_aggregate_screenshots_required: {contract.screenshots_required}",
            f"v200_accepted_web_evidence_manifest_aggregate_web_ui_execution_required: {contract.web_ui_execution_required}",
            f"v200_accepted_web_evidence_manifest_aggregate_actual_drc_backend_api_required: {contract.actual_drc_backend_api_required}",
            f"v200_accepted_web_evidence_manifest_aggregate_api_only_counts_as_success: {contract.api_only_counts_as_success}",
            f"v200_accepted_web_evidence_manifest_aggregate_source_tree_only_counts_as_success: {contract.source_tree_only_counts_as_success}",
            f"v200_accepted_web_evidence_manifest_aggregate_command_output_only_counts_as_success: {contract.command_output_only_counts_as_success}",
            f"v200_accepted_web_evidence_manifest_aggregate_ready_for_v200_release_when_accepted: {contract.ready_for_v200_release_when_accepted}",
            "v200_accepted_web_evidence_manifest_aggregate_required_items: " + ",".join(contract.required_evidence_items),
            "v200_accepted_web_evidence_manifest_aggregate_web_capability_items: " + ",".join(contract.web_capability_items),
            "v200_accepted_web_evidence_manifest_aggregate_required_top_level_true_markers: "
            + ",".join(contract.required_top_level_true_markers),
            "v200_accepted_web_evidence_manifest_aggregate_required_top_level_false_markers: "
            + ",".join(contract.required_top_level_false_markers),
            "v200_accepted_web_evidence_manifest_aggregate_required_web_item_true_markers: "
            + ",".join(contract.required_web_item_true_markers),
            "v200_accepted_web_evidence_manifest_aggregate_forbidden_success_states: "
            + ",".join(contract.forbidden_success_states),
            "v200_accepted_web_evidence_manifest_aggregate_public_safe_omissions: "
            + ",".join(contract.public_safe_omissions),
            "v200_accepted_web_evidence_manifest_aggregate_default_provider_status: not-called",
            "v200_accepted_web_evidence_manifest_aggregate_default_backend_status: not-started",
            "v200_accepted_web_evidence_manifest_aggregate_default_browser_status: not-opened",
            "v200_accepted_web_evidence_manifest_aggregate_default_screenshot_status: not-inspected",
        ]
    )


def _is_public_safe_reference(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if not value.startswith("private-operator-evidence://"):
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


def validate_v200_accepted_web_evidence_manifest_aggregate(
    manifest: Mapping[str, object],
) -> V200AcceptedWebEvidenceManifestAggregateValidation:
    """Validate one private Day80 accepted Web evidence manifest."""

    contract = build_v200_accepted_web_evidence_manifest_aggregate_contract()
    missing: list[str] = []
    if manifest.get("status") != "accepted":
        missing.append("status=accepted")
    if manifest.get("release_target") != "v2.0.0":
        missing.append("release_target=v2.0.0")
    if manifest.get("manifest_kind") != "private_web_execution_evidence":
        missing.append("manifest_kind=private_web_execution_evidence")

    for marker in contract.required_top_level_true_markers:
        if manifest.get(marker) is not True:
            missing.append(marker)

    public_safe = True
    for marker in contract.required_top_level_false_markers:
        if manifest.get(marker) is not False:
            public_safe = False
            missing.append(marker + "=false")

    forbidden_absent = True
    for marker in contract.forbidden_success_states:
        if manifest.get(marker) is True:
            forbidden_absent = False
            missing.append(marker + "=false")

    web_evidence = manifest.get("web_evidence")
    if not isinstance(web_evidence, Mapping):
        missing.append("web_evidence")
        web_evidence = {}

    required_items_accepted = True
    screenshot_refs_public_safe = True

    for item_name in contract.required_evidence_items:
        item = web_evidence.get(item_name)
        if not isinstance(item, Mapping):
            required_items_accepted = False
            missing.append(f"web_evidence.{item_name}")
            continue
        if item.get("status") != "accepted":
            required_items_accepted = False
            missing.append(f"web_evidence.{item_name}.status=accepted")
        if item.get("capability") != item_name:
            required_items_accepted = False
            missing.append(f"web_evidence.{item_name}.capability={item_name}")
        if item.get("operator_review_accepted") is not True:
            required_items_accepted = False
            missing.append(f"web_evidence.{item_name}.operator_review_accepted")

        if item_name in contract.web_capability_items:
            for marker in contract.required_web_item_true_markers:
                if item.get(marker) is not True:
                    required_items_accepted = False
                    missing.append(f"web_evidence.{item_name}.{marker}")
            if not _is_public_safe_reference(item.get("screenshot_reference")):
                screenshot_refs_public_safe = False
                missing.append(f"web_evidence.{item_name}.screenshot_reference_public_safe")

    status = (
        "accepted"
        if not missing and public_safe and screenshot_refs_public_safe and required_items_accepted and forbidden_absent
        else "incomplete"
    )
    return V200AcceptedWebEvidenceManifestAggregateValidation(
        status=status,
        missing_markers=tuple(missing),
        public_safe=public_safe,
        screenshot_references_public_safe=screenshot_refs_public_safe,
        required_items_accepted=required_items_accepted,
        forbidden_success_states_absent=forbidden_absent,
    )


def render_v200_accepted_web_evidence_manifest_aggregate_validation(
    validation: V200AcceptedWebEvidenceManifestAggregateValidation,
) -> str:
    """Render Day80 aggregate validation as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_accepted_web_evidence_manifest_aggregate_validation_status: {validation.status}",
            "v200_accepted_web_evidence_manifest_aggregate_missing_markers: "
            + ",".join(validation.missing_markers),
            f"v200_accepted_web_evidence_manifest_aggregate_public_safe: {validation.public_safe}",
            f"v200_accepted_web_evidence_manifest_aggregate_screenshot_references_public_safe: {validation.screenshot_references_public_safe}",
            f"v200_accepted_web_evidence_manifest_aggregate_required_items_accepted: {validation.required_items_accepted}",
            f"v200_accepted_web_evidence_manifest_aggregate_forbidden_success_states_absent: {validation.forbidden_success_states_absent}",
        ]
    )
