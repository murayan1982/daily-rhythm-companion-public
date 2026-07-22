"""v2.0.0 Day67 image asset generation/intake evidence acceptance.

This module validates marker-only evidence for the image asset generation and
repository-safe intake phase. It deliberately avoids image-generation service
calls, image file creation, Flutter asset registration, browser automation,
screenshot inspection, local generation workspace reads, and release artifact
creation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200ImageAssetGenerationIntakeEvidenceItem:
    """One required Day67 image asset generation/intake evidence marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200ImageAssetGenerationIntakeEvidenceResult:
    """Public-safe Day67 image asset generation/intake evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200ImageAssetGenerationIntakeEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200ImageAssetGenerationIntakeEvidenceValidation:
    """Validation result for a marker-only Day67 evidence summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_image_asset_generation_intake_evidence_contract() -> V200ImageAssetGenerationIntakeEvidenceResult:
    """Build the Day67 image asset generation/intake evidence contract.

    The returned structure is static and source-tree safe. It must not call
    image-generation services, inspect local image work folders, create image
    files, register Flutter assets, call the backend, open a browser, inspect
    screenshots, or create release packages.
    """

    evidence_items = (
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="explicit_operator_opt_in_enabled",
            status="required",
            description="The operator intentionally enabled the configured image asset generation or sourcing workflow.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="image_asset_generation_review_completed",
            status="required",
            description="Generated or sourced image candidates were reviewed before repository intake.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="public_safe_asset_sources_confirmed",
            status="required",
            description="Selected assets are original or otherwise public-repository safe.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="required_asset_inventory_selected",
            status="required",
            description="The small v2.0.0 character/background/fallback asset inventory was selected intentionally.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="repository_safe_asset_paths_reserved",
            status="required",
            description="Stable app/assets/images paths were reserved without private paths or unsafe filenames.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="generated_asset_metadata_sanitized",
            status="required",
            description="Prompts, seeds, generator metadata, and source references were omitted or sanitized for public docs.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="third_party_or_copyrighted_sources_absent",
            status="required",
            description="Copyrighted characters, third-party character references, and trademarked designs were excluded.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="private_or_living_person_references_absent",
            status="required",
            description="Private photos, private user context, and living-person likeness references were excluded.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="raw_generation_workspace_excluded",
            status="required",
            description="Raw generation work folders and unreviewed intermediate outputs were not committed or documented.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="fallback_placeholder_strategy_confirmed",
            status="required",
            description="A repository-safe fallback image strategy exists before Web display verification.",
        ),
        V200ImageAssetGenerationIntakeEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description="Shared evidence is marker-only and omits screenshots, private paths, raw LAN IPs, prompts, and metadata.",
        ),
    )

    return V200ImageAssetGenerationIntakeEvidenceResult(
        status="operator-execution-evidence-contract-ready",
        requirement_key="image_asset_generation_repository_safe_intake",
        evidence_items=evidence_items,
        required_operator_markers=tuple(item.key for item in evidence_items),
        public_safe_omissions=(
            "raw_prompts_with_private_context",
            "raw_generation_metadata",
            "raw_seed_metadata",
            "unreviewed_intermediate_outputs",
            "local_generation_work_folders",
            "private_photos",
            "living_person_references",
            "copyrighted_source_references",
            "third_party_character_references",
            "private_paths",
            "raw_lan_ips",
            "raw_screenshots",
        ),
        forbidden_success_states=(
            "unreviewed_image_artifacts",
            "copyrighted_source_image",
            "third_party_character_reference",
            "private_photo",
            "living_person_reference",
            "trademarked_character",
            "private_prompt_context",
            "raw_generation_metadata",
            "raw_seed_metadata",
            "local_generation_work_folder",
            "committed_external_work_folder",
            "missing_rights_review",
            "unsafe_filename",
            "private_path",
            "raw_lan_ip",
            "raw_screenshot",
            "skipped",
            "unavailable",
            "fallback_only",
            "error",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="web-image-display-execution-evidence",
    )


def render_v200_image_asset_generation_intake_evidence(
    result: V200ImageAssetGenerationIntakeEvidenceResult,
) -> str:
    """Render public-safe Day67 image asset generation/intake markers."""

    lines = [
        "v200_image_asset_generation_intake_evidence_status: " + result.status,
        "v200_image_asset_generation_intake_requirement_key: " + result.requirement_key,
        "v200_image_asset_generation_intake_operator_run_required: " + str(result.operator_run_required),
        "v200_image_asset_generation_intake_mock_safe_default: " + str(result.mock_safe_default),
        "v200_image_asset_generation_intake_required_operator_markers: " + ",".join(result.required_operator_markers),
        "v200_image_asset_generation_intake_public_safe_omissions: " + ",".join(result.public_safe_omissions),
        "v200_image_asset_generation_intake_forbidden_success_states: " + ",".join(result.forbidden_success_states),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_image_asset_generation_intake_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_image_asset_generation_intake_default_image_generation_status: not-called",
            "v200_image_asset_generation_intake_default_image_file_status: not-created",
            "v200_image_asset_generation_intake_default_asset_manifest_status: not-modified",
            "v200_image_asset_generation_intake_default_backend_call_status: not-called",
            "v200_image_asset_generation_intake_default_browser_status: not-opened",
            "v200_image_asset_generation_intake_default_screenshot_status: not-inspected",
            "v200_image_asset_generation_intake_default_release_artifact_status: not-created",
            "v200_image_asset_generation_intake_public_evidence_body_policy: marker-only-no-raw-prompts-no-raw-images",
            "v200_image_asset_generation_intake_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_image_asset_generation_intake_operator_evidence(
    evidence: Mapping[str, object],
) -> V200ImageAssetGenerationIntakeEvidenceValidation:
    """Validate a redacted marker-only Day67 operator evidence summary."""

    contract = build_v200_image_asset_generation_intake_evidence_contract()
    accepted = []
    missing = []
    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    unsafe_boolean_fields = (
        "unreviewed_image_artifacts_included",
        "copyrighted_source_image_included",
        "third_party_character_reference_included",
        "private_photo_included",
        "living_person_reference_included",
        "trademarked_character_included",
        "private_prompt_context_included",
        "raw_generation_metadata_included",
        "raw_seed_metadata_included",
        "local_generation_work_folder_included",
        "committed_external_work_folder_included",
        "private_paths_included",
        "raw_lan_ips_included",
        "raw_screenshots_included",
    )
    public_safe = all(evidence.get(field) is False for field in unsafe_boolean_fields)

    state = str(evidence.get("result_state", "configured_success"))
    forbidden_absent = state not in contract.forbidden_success_states
    status = "accepted" if not missing and public_safe and forbidden_absent else "rejected"

    return V200ImageAssetGenerationIntakeEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_absent,
    )
