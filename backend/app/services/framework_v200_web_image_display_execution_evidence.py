"""v2.0.0 Day68 Web image display execution evidence acceptance.

This module validates marker-only evidence for the Web image display execution
phase. It deliberately avoids image generation, image file inspection, Flutter
Web builds, backend calls, browser automation, screenshot inspection, LAN URL
recording, and release artifact creation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class V200WebImageDisplayExecutionEvidenceItem:
    """One required Day68 Web image display execution evidence marker."""

    key: str
    status: str
    description: str


@dataclass(frozen=True)
class V200WebImageDisplayExecutionEvidenceResult:
    """Public-safe Day68 Web image display execution evidence contract."""

    status: str
    requirement_key: str
    evidence_items: tuple[V200WebImageDisplayExecutionEvidenceItem, ...]
    required_operator_markers: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    operator_run_required: bool
    mock_safe_default: bool
    next_focus: str


@dataclass(frozen=True)
class V200WebImageDisplayExecutionEvidenceValidation:
    """Validation result for a marker-only Day68 evidence summary."""

    status: str
    accepted_markers: tuple[str, ...]
    missing_markers: tuple[str, ...]
    public_safe: bool
    forbidden_success_states_absent: bool


def build_v200_web_image_display_execution_evidence_contract() -> V200WebImageDisplayExecutionEvidenceResult:
    """Build the Day68 Web image display execution evidence contract.

    The returned structure is static and source-tree safe. It must not generate
    images, inspect image files, run Flutter, start backend services, open a
    browser, inspect screenshots, record LAN URLs, or create release packages.
    """

    evidence_items = (
        V200WebImageDisplayExecutionEvidenceItem(
            key="explicit_operator_opt_in_enabled",
            status="required",
            description="The operator intentionally enabled the configured Web image display verification workflow.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="day67_asset_intake_evidence_accepted",
            status="required",
            description="The selected image assets or placeholders already passed the Day67 repository-safe intake review.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="public_safe_assets_available_in_app_tree",
            status="required",
            description="The app tree contains only reviewed public-safe image assets or placeholders at stable asset paths.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="flutter_asset_manifest_registration_confirmed",
            status="required",
            description="Flutter asset registration was confirmed through the app asset manifest.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="flutter_web_runtime_display_confirmed",
            status="required",
            description="Flutter Web displayed the intended image surface during the configured run.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="smartphone_web_display_confirmed",
            status="required",
            description="A smartphone browser displayed the intended image surface through the actual DRC Web UI.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="actual_app_route_used",
            status="required",
            description="The confirmation used the real app route/screen rather than an isolated static image preview.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="missing_image_fallback_confirmed",
            status="required",
            description="The missing-image or unavailable-image fallback was confirmed to be visible and non-crashing.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="release_package_asset_inclusion_ready",
            status="required",
            description="The selected public-safe asset paths are ready for later fixed release package inclusion verification.",
        ),
        V200WebImageDisplayExecutionEvidenceItem(
            key="public_safe_evidence_recorded",
            status="required",
            description="Shared evidence is marker-only and omits screenshots, private paths, raw LAN IPs, prompts, and metadata.",
        ),
    )

    return V200WebImageDisplayExecutionEvidenceResult(
        status="operator-execution-evidence-contract-ready",
        requirement_key="web_image_display_execution",
        evidence_items=evidence_items,
        required_operator_markers=tuple(item.key for item in evidence_items),
        public_safe_omissions=(
            "raw_screenshots",
            "raw_lan_ips",
            "private_paths",
            "local_browser_storage",
            "raw_image_generation_prompts",
            "raw_generation_metadata",
            "raw_seed_metadata",
            "unreviewed_intermediate_outputs",
            "local_image_work_folders",
            "copyrighted_source_references",
            "third_party_character_references",
            "private_photos",
            "living_person_references",
        ),
        forbidden_success_states=(
            "day67_not_accepted",
            "unreviewed_asset",
            "missing_asset_manifest_registration",
            "flutter_web_not_confirmed",
            "smartphone_web_not_confirmed",
            "static_file_preview_only",
            "screenshot_only_without_ui_confirmation",
            "missing_image_fallback_not_confirmed",
            "release_asset_inclusion_unknown",
            "raw_screenshot",
            "raw_lan_ip",
            "private_path",
            "private_prompt_context",
            "raw_generation_metadata",
            "copyrighted_source_image",
            "third_party_character_reference",
            "private_photo",
            "living_person_reference",
            "skipped",
            "unavailable",
            "fallback_only",
            "error",
        ),
        operator_run_required=True,
        mock_safe_default=True,
        next_focus="public-repo-readiness-final-sweep",
    )


def render_v200_web_image_display_execution_evidence(
    result: V200WebImageDisplayExecutionEvidenceResult,
) -> str:
    """Render public-safe Day68 Web image display execution markers."""

    lines = [
        "v200_web_image_display_execution_evidence_status: " + result.status,
        "v200_web_image_display_execution_requirement_key: " + result.requirement_key,
        "v200_web_image_display_execution_operator_run_required: " + str(result.operator_run_required),
        "v200_web_image_display_execution_mock_safe_default: " + str(result.mock_safe_default),
        "v200_web_image_display_execution_required_operator_markers: " + ",".join(result.required_operator_markers),
        "v200_web_image_display_execution_public_safe_omissions: " + ",".join(result.public_safe_omissions),
        "v200_web_image_display_execution_forbidden_success_states: " + ",".join(result.forbidden_success_states),
    ]

    for item in result.evidence_items:
        lines.append(f"v200_web_image_display_execution_evidence_{item.key}: {item.status}")

    lines.extend(
        [
            "v200_web_image_display_execution_default_image_generation_status: not-called",
            "v200_web_image_display_execution_default_image_file_inspection_status: not-run",
            "v200_web_image_display_execution_default_flutter_web_build_status: not-run",
            "v200_web_image_display_execution_default_backend_call_status: not-called",
            "v200_web_image_display_execution_default_browser_status: not-opened",
            "v200_web_image_display_execution_default_screenshot_status: not-inspected",
            "v200_web_image_display_execution_default_release_artifact_status: not-created",
            "v200_web_image_display_execution_public_evidence_body_policy: marker-only-no-raw-screenshots-no-raw-lan-ips",
            "v200_web_image_display_execution_next_focus: " + result.next_focus,
        ]
    )

    return "\n".join(lines)


def validate_v200_web_image_display_execution_operator_evidence(
    evidence: Mapping[str, object],
) -> V200WebImageDisplayExecutionEvidenceValidation:
    """Validate a redacted marker-only Day68 operator evidence summary."""

    contract = build_v200_web_image_display_execution_evidence_contract()
    accepted = []
    missing = []
    for marker in contract.required_operator_markers:
        if evidence.get(marker) is True:
            accepted.append(marker)
        else:
            missing.append(marker)

    unsafe_boolean_fields = (
        "raw_screenshots_included",
        "raw_lan_ips_included",
        "private_paths_included",
        "local_browser_storage_included",
        "raw_image_generation_prompts_included",
        "raw_generation_metadata_included",
        "raw_seed_metadata_included",
        "unreviewed_intermediate_outputs_included",
        "local_image_work_folders_included",
        "copyrighted_source_references_included",
        "third_party_character_references_included",
        "private_photos_included",
        "living_person_references_included",
    )
    public_safe = all(evidence.get(field) is False for field in unsafe_boolean_fields)

    state = str(evidence.get("result_state", "configured_success"))
    forbidden_absent = state not in contract.forbidden_success_states
    status = "accepted" if not missing and public_safe and forbidden_absent else "rejected"

    return V200WebImageDisplayExecutionEvidenceValidation(
        status=status,
        accepted_markers=tuple(accepted),
        missing_markers=tuple(missing),
        public_safe=public_safe,
        forbidden_success_states_absent=forbidden_absent,
    )
