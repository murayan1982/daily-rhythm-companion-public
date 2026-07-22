"""v2.0.0 Day83 final release readiness fixed-zip gate with accepted Web evidence.

This module defines the public-safe contract for final release readiness after one
fixed release zip has passed accepted Web evidence verification. It does not build
release zips, call providers, call Google Health, start the backend, run Flutter
Web, inspect raw screenshots, tag releases, push to GitHub, or use the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from backend.app.services.framework_v200_fixed_release_zip_with_web_evidence_verification import (
    V200FixedReleaseZipInspection,
    inspect_fixed_release_zip_as_is,
)


@dataclass(frozen=True)
class V200FinalReleaseReadinessFixedZipWithWebEvidenceContract:
    """Public-safe Day83 final release readiness contract."""

    status: str
    requirement_key: str
    requires_day80_accepted_manifest: bool
    requires_day81_final_readiness: bool
    requires_day82_fixed_zip_verification: bool
    inspects_zip_as_is: bool
    creates_or_rebuilds_zip: bool
    required_zip_entries: tuple[str, ...]
    required_absent_entries: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    next_focus: str


@dataclass(frozen=True)
class V200FinalReleaseReadinessFixedZipWithWebEvidenceValidation:
    """Validation result for private Day83 operator evidence."""

    status: str
    missing_markers: tuple[str, ...]
    public_safe: bool


def build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract() -> V200FinalReleaseReadinessFixedZipWithWebEvidenceContract:
    """Build the Day83 final readiness contract."""

    required_zip_entries = (
        "README.md",
        "roadmap.md",
        "LICENSE",
        "build_release.bat",
        "build_v200_final_fixed_release_zip_from_head.ps1",
        "docs/DRC_v200_goal_checklist_small_commit.md",
        "docs/v2_prerelease_requirements.md",
        "docs/v200_accepted_web_screenshot_evidence_enforcement.md",
        "docs/v200_real_llm_web_screenshot_evidence_capture.md",
        "docs/v200_real_tts_web_audio_screenshot_evidence_capture.md",
        "docs/v200_real_google_health_web_sleep_screenshot_evidence_capture.md",
        "docs/v200_web_image_display_screenshot_evidence_capture.md",
        "docs/v200_accepted_web_evidence_manifest_aggregate.md",
        "docs/v200_final_release_readiness_with_web_evidence.md",
        "docs/v200_fixed_release_zip_with_web_evidence_verification.md",
        "docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md",
        "docs/v200_final_release_artifact_record.md",
        "docs/v200_public_distribution_readiness.md",
        "backend/app/services/framework_v200_public_distribution_readiness.py",
        "scripts/smoke_framework_v200_public_distribution_readiness.py",
        "backend/app/services/framework_v200_final_release_artifact_record.py",
        "scripts/smoke_framework_v200_final_release_artifact_record.py",
        "docs/operator_evidence_templates/v200_accepted_web_screenshot_evidence_day73.example.json",
        "docs/operator_evidence_templates/v200_real_llm_web_screenshot_day76.example.json",
        "docs/operator_evidence_templates/v200_real_tts_web_audio_screenshot_day77.example.json",
        "docs/operator_evidence_templates/v200_real_google_health_web_sleep_screenshot_day78.example.json",
        "docs/operator_evidence_templates/v200_web_image_display_screenshot_day79.example.json",
        "docs/operator_evidence_templates/v200_accepted_web_evidence_manifest_day80.example.json",
        "docs/operator_evidence_templates/v200_final_release_readiness_with_web_evidence_day81.example.json",
        "docs/operator_evidence_templates/v200_fixed_release_zip_with_web_evidence_day82.example.json",
        "docs/operator_evidence_templates/v200_final_release_readiness_fixed_zip_with_web_evidence_day83.example.json",
        "backend/app/services/framework_v200_accepted_web_screenshot_evidence_enforcement.py",
        "backend/app/services/framework_v200_real_llm_web_screenshot_evidence.py",
        "backend/app/services/framework_v200_real_tts_web_audio_screenshot_evidence.py",
        "backend/app/services/framework_v200_real_google_health_web_sleep_screenshot_evidence.py",
        "backend/app/services/framework_v200_web_image_display_screenshot_evidence.py",
        "backend/app/services/framework_v200_accepted_web_evidence_manifest_aggregate.py",
        "backend/app/services/framework_v200_final_release_readiness_with_web_evidence.py",
        "backend/app/services/framework_v200_fixed_release_zip_with_web_evidence_verification.py",
        "backend/app/services/framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py",
        "scripts/smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py",
        "scripts/smoke_framework_v200_real_llm_web_screenshot_evidence.py",
        "scripts/smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py",
        "scripts/smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py",
        "scripts/smoke_framework_v200_web_image_display_screenshot_evidence.py",
        "scripts/smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py",
        "scripts/smoke_framework_v200_final_release_readiness_with_web_evidence.py",
        "scripts/smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py",
        "scripts/smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py",
        "backend/env_profiles/mock_safe.env",
        "backend/env_profiles/framework_local.env.example",
    )
    required_absent_entries = (
        "docs/internal/",
        "release/",
        "__pycache__/",
        ".git/",
        ".venv/",
        "repo_files/",
        "optional_replacements/",
        "operator_evidence/",
        "DRC_v200_Day",
        "DRC_v200_goal_checklist_small_commit_CommitC_ACCEPTED.md",
        "replacement_bundle",
        "next_thread_handoff",
        "private_operator_evidence/",
        "operator_evidence/private/",
        "raw_screenshot",
        "raw_audio",
        "raw_google_health_payload",
        "scripts/check_v200_accepted_web_screenshot_evidence_day73.py",
        "scripts/check_v200_web_execution_screenshot_collection_day74.py",
        "scripts/check_v200_private_web_evidence_manifest_day75.py",
        "scripts/check_v200_real_llm_web_screenshot_day76.py",
        "scripts/check_v200_real_tts_web_audio_screenshot_day77.py",
        "scripts/check_v200_real_google_health_web_sleep_screenshot_day78.py",
        "scripts/check_v200_web_image_display_screenshot_day79.py",
        "scripts/check_v200_accepted_web_evidence_manifest_day80.py",
        "scripts/check_v200_final_release_readiness_with_web_evidence_day81.py",
        "scripts/check_v200_fixed_release_zip_with_web_evidence_day82.py",
        "scripts/check_v200_final_release_readiness_fixed_zip_with_web_evidence_day83.py",
    )
    return V200FinalReleaseReadinessFixedZipWithWebEvidenceContract(
        status="final-release-ready-fixed-zip-with-accepted-web-evidence",
        requirement_key="v200_final_release_readiness_fixed_zip_with_web_evidence",
        requires_day80_accepted_manifest=True,
        requires_day81_final_readiness=True,
        requires_day82_fixed_zip_verification=True,
        inspects_zip_as_is=True,
        creates_or_rebuilds_zip=False,
        required_zip_entries=required_zip_entries,
        required_absent_entries=required_absent_entries,
        public_safe_omissions=(
            "raw_screenshots",
            "raw_prompts",
            "raw_provider_payloads",
            "raw_audio_files",
            "raw_google_health_payloads",
            "api_keys",
            "oauth_tokens",
            "authorization_headers",
            "private_absolute_paths",
            "raw_lan_ips",
            "private_evidence_stores",
            "replacement_bundles",
            "source_tree_day_check_scripts",
            "production_or_store_claims",
            "medical_claims",
        ),
        forbidden_success_states=(
            "day80_not_accepted",
            "day81_not_passed",
            "day82_not_passed",
            "release_zip_rebuilt_during_verification",
            "zip_not_inspected_as_is",
            "required_file_missing_from_zip",
            "day_check_script_included_in_zip",
            "api_only_success",
            "source_tree_only_success",
            "command_output_only_success",
            "web_ui_not_confirmed",
            "actual_backend_api_not_used",
            "screenshot_missing",
            "screenshot_reference_missing",
            "raw_screenshot_included",
            "raw_prompt_included",
            "raw_provider_payload_included",
            "raw_audio_included",
            "raw_google_health_payload_included",
            "api_key_included",
            "oauth_token_included",
            "authorization_header_included",
            "private_path_included",
            "raw_lan_ip_included",
            "private_evidence_store_included",
            "replacement_bundle_included",
            "production_claim",
            "app_store_claim",
            "medical_claim",
            "skipped",
            "unavailable",
            "fallback_only",
            "placeholder_only",
        ),
        next_focus="Commit, tag, and publish only after this fixed-zip readiness gate passes with accepted private Web evidence.",
    )


def inspect_v200_final_release_readiness_fixed_zip_with_web_evidence(
    release_zip_path: str | Path,
) -> V200FixedReleaseZipInspection:
    """Inspect the same fixed zip against the complete Day83 release surface."""

    contract = build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract()
    return inspect_fixed_release_zip_as_is(
        release_zip_path,
        required_zip_entries=contract.required_zip_entries,
        required_absent_entries=contract.required_absent_entries,
    )


def render_v200_final_release_readiness_fixed_zip_with_web_evidence_contract(
    contract: V200FinalReleaseReadinessFixedZipWithWebEvidenceContract,
) -> str:
    """Render the Day83 contract as deterministic text."""

    return "\n".join(
        [
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_status: {contract.status}",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_requirement_key: {contract.requirement_key}",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day80_accepted_manifest: {contract.requires_day80_accepted_manifest}",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day81_final_readiness: {contract.requires_day81_final_readiness}",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day82_fixed_zip_verification: {contract.requires_day82_fixed_zip_verification}",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_inspects_zip_as_is: {contract.inspects_zip_as_is}",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_creates_or_rebuilds_zip: {contract.creates_or_rebuilds_zip}",
            "v200_final_release_readiness_fixed_zip_with_web_evidence_required_zip_entries: " + ",".join(contract.required_zip_entries),
            "v200_final_release_readiness_fixed_zip_with_web_evidence_required_absent_entries: " + ",".join(contract.required_absent_entries),
            "v200_final_release_readiness_fixed_zip_with_web_evidence_public_safe_omissions: " + ",".join(contract.public_safe_omissions),
            "v200_final_release_readiness_fixed_zip_with_web_evidence_forbidden_success_states: " + ",".join(contract.forbidden_success_states),
            "v200_final_release_readiness_fixed_zip_with_web_evidence_default_provider_status: not-called",
            "v200_final_release_readiness_fixed_zip_with_web_evidence_default_backend_status: not-started",
            "v200_final_release_readiness_fixed_zip_with_web_evidence_default_browser_status: not-opened",
            "v200_final_release_readiness_fixed_zip_with_web_evidence_default_screenshot_status: not-inspected",
            "v200_final_release_readiness_fixed_zip_with_web_evidence_default_release_zip_status: not-created-or-rebuilt",
            f"v200_final_release_readiness_fixed_zip_with_web_evidence_next_focus: {contract.next_focus}",
        ]
    )


def validate_v200_final_release_readiness_fixed_zip_with_web_evidence(
    evidence: Mapping[str, object],
) -> V200FinalReleaseReadinessFixedZipWithWebEvidenceValidation:
    """Validate private marker evidence for Day83 final release readiness."""

    missing: list[str] = []
    if evidence.get("status") != "accepted":
        missing.append("status=accepted")
    if evidence.get("release_target") != "v2.0.0":
        missing.append("release_target=v2.0.0")
    if evidence.get("manifest_kind") != "final_release_readiness_fixed_zip_with_web_evidence":
        missing.append("manifest_kind=final_release_readiness_fixed_zip_with_web_evidence")
    for marker in (
        "day80_accepted_manifest_passed",
        "day81_final_readiness_passed",
        "day82_fixed_zip_verification_passed",
        "fixed_release_zip_path_recorded",
        "fixed_zip_inspected_as_is",
        "no_rebuild_during_day83_verification",
        "all_web_screenshot_evidence_accepted",
        "release_surface_public_safe",
        "operator_review_accepted",
    ):
        if evidence.get(marker) is not True:
            missing.append(marker)
    contract = build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract()
    public_safe = True
    for forbidden in contract.forbidden_success_states:
        if evidence.get(forbidden) is True:
            missing.append(f"forbidden:{forbidden}")
            public_safe = False
    for leak in (
        "raw_screenshots_included",
        "raw_prompts_included",
        "raw_provider_payloads_included",
        "raw_audio_included",
        "raw_google_health_payloads_included",
        "api_keys_included",
        "oauth_tokens_included",
        "authorization_headers_included",
        "private_paths_included",
        "raw_lan_ips_included",
    ):
        if evidence.get(leak) is True:
            missing.append(f"leak:{leak}")
            public_safe = False
    return V200FinalReleaseReadinessFixedZipWithWebEvidenceValidation(
        status="accepted" if not missing and public_safe else "rejected",
        missing_markers=tuple(missing),
        public_safe=public_safe,
    )
