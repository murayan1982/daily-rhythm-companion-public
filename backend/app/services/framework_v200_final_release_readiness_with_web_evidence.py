"""v2.0.0 Day81 final release readiness with accepted Web evidence.

The default contract is public-safe and marker-only. It does not call providers,
call Google Health, start the Daily Rhythm Companion backend, run Flutter Web,
open browsers, inspect screenshots, build release packages, tag releases, call
GitHub, or use the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import re

from backend.app.services.framework_v200_accepted_web_evidence_manifest_aggregate import (
    validate_v200_accepted_web_evidence_manifest_aggregate,
)


@dataclass(frozen=True)
class V200FinalReleaseReadinessWithWebEvidenceContract:
    """Public-safe contract for Day81 final release readiness."""

    status: str
    fixed_release_zip_required: bool
    accepted_day80_manifest_required: bool
    web_ui_execution_required: bool
    screenshots_required: bool
    actual_drc_backend_api_required: bool
    tag_allowed_without_accepted_manifest: bool
    release_allowed_without_accepted_manifest: bool
    api_only_counts_as_success: bool
    source_tree_only_counts_as_success: bool
    command_output_only_counts_as_success: bool
    required_manifest_items: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]


@dataclass(frozen=True)
class V200FinalReleaseReadinessWithWebEvidenceValidation:
    """Validation result for Day81 final release readiness."""

    status: str
    missing_markers: tuple[str, ...]
    fixed_release_zip_present: bool
    accepted_day80_manifest: bool
    public_safe: bool
    tag_allowed: bool
    release_allowed: bool


def build_v200_final_release_readiness_with_web_evidence_contract() -> V200FinalReleaseReadinessWithWebEvidenceContract:
    """Build the Day81 final readiness contract."""

    return V200FinalReleaseReadinessWithWebEvidenceContract(
        status="final-release-readiness-with-accepted-web-evidence-validator-ready",
        fixed_release_zip_required=True,
        accepted_day80_manifest_required=True,
        web_ui_execution_required=True,
        screenshots_required=True,
        actual_drc_backend_api_required=True,
        tag_allowed_without_accepted_manifest=False,
        release_allowed_without_accepted_manifest=False,
        api_only_counts_as_success=False,
        source_tree_only_counts_as_success=False,
        command_output_only_counts_as_success=False,
        required_manifest_items=(
            "real_llm_web_answer",
            "real_tts_web_audio_output",
            "real_google_health_sleep_data",
            "web_image_display",
            "image_asset_intake_review",
            "public_repo_final_sweep_review",
            "final_aggregate_review",
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
            "private_absolute_paths",
            "raw_lan_ips",
        ),
    )


def render_v200_final_release_readiness_with_web_evidence_contract(
    contract: V200FinalReleaseReadinessWithWebEvidenceContract,
) -> str:
    """Render the Day81 contract as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_final_release_readiness_with_web_evidence_status: {contract.status}",
            f"v200_final_release_readiness_requires_fixed_release_zip: {contract.fixed_release_zip_required}",
            f"v200_final_release_readiness_requires_day80_accepted_manifest: {contract.accepted_day80_manifest_required}",
            f"v200_final_release_readiness_web_ui_execution_required: {contract.web_ui_execution_required}",
            f"v200_final_release_readiness_screenshots_required: {contract.screenshots_required}",
            f"v200_final_release_readiness_actual_drc_backend_api_required: {contract.actual_drc_backend_api_required}",
            f"v200_final_release_readiness_tag_allowed_without_accepted_manifest: {contract.tag_allowed_without_accepted_manifest}",
            f"v200_final_release_readiness_release_allowed_without_accepted_manifest: {contract.release_allowed_without_accepted_manifest}",
            f"v200_final_release_readiness_api_only_counts_as_success: {contract.api_only_counts_as_success}",
            f"v200_final_release_readiness_source_tree_only_counts_as_success: {contract.source_tree_only_counts_as_success}",
            f"v200_final_release_readiness_command_output_only_counts_as_success: {contract.command_output_only_counts_as_success}",
            "v200_final_release_readiness_required_manifest_items: " + ",".join(contract.required_manifest_items),
            "v200_final_release_readiness_forbidden_success_states: " + ",".join(contract.forbidden_success_states),
            "v200_final_release_readiness_public_safe_omissions: " + ",".join(contract.public_safe_omissions),
            "v200_final_release_readiness_default_provider_status: not-called",
            "v200_final_release_readiness_default_backend_status: not-started",
            "v200_final_release_readiness_default_browser_status: not-opened",
            "v200_final_release_readiness_default_screenshot_status: not-inspected",
            "v200_final_release_readiness_default_release_zip_status: not-created-or-rebuilt",
        ]
    )


def _public_safe_reference(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if not value.startswith("private-operator-evidence://"):
        return False
    unsafe = (
        r"[A-Za-z]:\\",
        r"/Users/",
        r"/home/[^/]+/",
        r"192\.168\.\d+\.\d+",
        r"10\.\d+\.\d+\.\d+",
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+",
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"Bearer\s+[A-Za-z0-9_\-\.]{12,}",
    )
    return not any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in unsafe)


def validate_v200_final_release_readiness_with_web_evidence(
    final_evidence: Mapping[str, object],
    day80_manifest: Mapping[str, object],
    release_zip_path: str | Path | None = None,
) -> V200FinalReleaseReadinessWithWebEvidenceValidation:
    """Validate final readiness using a Day80 accepted private manifest."""

    missing: list[str] = []
    fixed_zip_present = True
    if release_zip_path is not None:
        fixed_zip_present = Path(release_zip_path).exists()
        if not fixed_zip_present:
            missing.append("fixed_release_zip_exists")

    if final_evidence.get("status") != "accepted":
        missing.append("status=accepted")
    if final_evidence.get("release_target") != "v2.0.0":
        missing.append("release_target=v2.0.0")
    if final_evidence.get("manifest_kind") != "final_release_readiness_with_web_evidence":
        missing.append("manifest_kind=final_release_readiness_with_web_evidence")
    if final_evidence.get("fixed_release_zip_verified") is not True:
        missing.append("fixed_release_zip_verified")
    if final_evidence.get("day80_manifest_status") != "accepted":
        missing.append("day80_manifest_status=accepted")
    if final_evidence.get("tag_allowed") is not True:
        missing.append("tag_allowed=true")
    if final_evidence.get("release_allowed") is not True:
        missing.append("release_allowed=true")

    reference = final_evidence.get("accepted_day80_manifest_reference")
    public_safe = _public_safe_reference(reference)
    if not public_safe:
        missing.append("accepted_day80_manifest_reference_public_safe")

    contract = build_v200_final_release_readiness_with_web_evidence_contract()
    for forbidden in contract.forbidden_success_states:
        if final_evidence.get(forbidden) is True:
            missing.append(f"forbidden:{forbidden}")
            public_safe = False

    day80_validation = validate_v200_accepted_web_evidence_manifest_aggregate(day80_manifest)
    accepted_day80_manifest = day80_validation.status == "accepted"
    if not accepted_day80_manifest:
        missing.append("day80_manifest_accepted")
        missing.extend(f"day80:{marker}" for marker in day80_validation.missing_markers)

    status = "accepted" if not missing and fixed_zip_present and accepted_day80_manifest and public_safe else "rejected"
    return V200FinalReleaseReadinessWithWebEvidenceValidation(
        status=status,
        missing_markers=tuple(missing),
        fixed_release_zip_present=fixed_zip_present,
        accepted_day80_manifest=accepted_day80_manifest,
        public_safe=public_safe and day80_validation.public_safe and day80_validation.screenshot_references_public_safe,
        tag_allowed=status == "accepted",
        release_allowed=status == "accepted",
    )


def render_v200_final_release_readiness_with_web_evidence_validation(
    validation: V200FinalReleaseReadinessWithWebEvidenceValidation,
) -> str:
    """Render a validation result without exposing private evidence content."""

    return "\n".join(
        [
            f"v200_final_release_readiness_with_web_evidence_validation_status: {validation.status}",
            f"v200_final_release_readiness_fixed_release_zip_present: {validation.fixed_release_zip_present}",
            f"v200_final_release_readiness_day80_manifest_accepted: {validation.accepted_day80_manifest}",
            f"v200_final_release_readiness_public_safe: {validation.public_safe}",
            f"v200_final_release_readiness_tag_allowed: {validation.tag_allowed}",
            f"v200_final_release_readiness_release_allowed: {validation.release_allowed}",
            "v200_final_release_readiness_missing_markers: " + ",".join(validation.missing_markers),
        ]
    )
