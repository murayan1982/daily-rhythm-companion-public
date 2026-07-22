"""v2.0.0 immutable final release artifact record contract.

This module defines a public-safe record that binds the clean-history Public
repository source, one fixed release zip, the annotated tag, and GitHub Release
metadata. It never creates a zip, edits source files, creates refs, publishes a
release, reads private operator evidence, or uses the network.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

from backend.app.services.framework_v200_fixed_release_zip_with_web_evidence_verification import (
    V200FixedReleaseZipInspection,
)


_FULL_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_FULL_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SAFE_ZIP_NAME_RE = re.compile(r"^DailyRhythmCompanion_[0-9]{8}_[0-9]{6}\.zip$")

_PUBLIC_REPOSITORY_TOPOLOGY = "clean_history_public_snapshot"
_PUBLIC_REPOSITORY = "murayan1982/daily-rhythm-companion-public"


@dataclass(frozen=True)
class V200FinalReleaseArtifactRecordContract:
    """Public-safe immutable final artifact record contract."""

    status: str
    requirement_key: str
    release_target: str
    tag_name: str
    repository_topology: str
    public_repository: str
    record_locations: tuple[str, ...]
    required_public_fields: tuple[str, ...]
    required_true_markers: tuple[str, ...]
    required_false_markers: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    next_focus: str


@dataclass(frozen=True)
class V200FinalReleaseArtifactRecordValidation:
    """Validation result for one immutable artifact record."""

    status: str
    missing_markers: tuple[str, ...]
    public_safe: bool
    artifact_matches_inspection: bool


def build_v200_final_release_artifact_record_contract() -> V200FinalReleaseArtifactRecordContract:
    """Build the clean-history Public artifact-record contract."""

    return V200FinalReleaseArtifactRecordContract(
        status="immutable-final-release-artifact-record-ready",
        requirement_key="v200_final_release_artifact_record",
        release_target="v2.0.0",
        tag_name="DRC_v2.0.0",
        repository_topology=_PUBLIC_REPOSITORY_TOPOLOGY,
        public_repository=_PUBLIC_REPOSITORY,
        record_locations=(
            "annotated-git-tag-message",
            "github-release-body",
        ),
        required_public_fields=(
            "status",
            "release_target",
            "record_kind",
            "repository_topology",
            "public_repository",
            "source_head",
            "main_head",
            "public_root_commit_count",
            "tag_name",
            "tag_target_head",
            "tag_object_type",
            "release_zip_name",
            "release_zip_size_bytes",
            "release_zip_sha256",
        ),
        required_true_markers=(
            "day80_accepted_manifest_passed",
            "day82_fixed_zip_verification_passed",
            "day83_final_release_readiness_passed",
            "fixed_zip_inspected_as_is",
            "public_main_matches_source_head",
            "clean_history_public_root_verified",
            "annotated_tag_targets_source_head",
            "github_release_same_fixed_zip_required",
            "operator_review_accepted",
        ),
        required_false_markers=(
            "fixed_zip_rebuilt_after_verification",
            "source_changed_after_fixed_zip_build",
            "private_git_history_included",
            "private_evidence_included",
            "raw_screenshots_included",
            "raw_audio_included",
            "raw_health_data_included",
            "raw_provider_payloads_included",
            "api_keys_included",
            "oauth_tokens_included",
            "authorization_headers_included",
            "private_paths_included",
            "raw_lan_ips_included",
        ),
        forbidden_success_states=(
            "source_head_not_committed",
            "private_repository_release_source",
            "public_main_head_mismatch",
            "multiple_public_root_commits",
            "private_git_history_present",
            "lightweight_tag",
            "tag_target_mismatch",
            "release_zip_not_inspected",
            "release_zip_rebuilt",
            "release_zip_hash_mismatch",
            "release_zip_size_mismatch",
            "release_zip_name_mismatch",
            "github_release_asset_mismatch",
            "post_build_source_commit",
            "private_evidence_in_release_metadata",
            "skipped",
            "unavailable",
            "placeholder_only",
        ),
        public_safe_omissions=(
            "private_repository_commit_ids",
            "private_git_history",
            "raw_screenshots",
            "raw_audio",
            "raw_health_data",
            "raw_prompts",
            "raw_provider_payloads",
            "api_keys",
            "oauth_tokens",
            "authorization_headers",
            "private_absolute_paths",
            "raw_lan_ips",
            "private_operator_evidence",
        ),
        next_focus=(
            "Build one fixed zip from clean Public main, verify the same artifact, "
            "validate this record, then create the annotated tag and GitHub Release "
            "without changing source or rebuilding the zip."
        ),
    )


def render_v200_final_release_artifact_record_contract(
    contract: V200FinalReleaseArtifactRecordContract,
) -> str:
    """Render the contract as deterministic public-safe text."""

    return "\n".join(
        [
            f"v200_final_release_artifact_record_status: {contract.status}",
            f"v200_final_release_artifact_record_requirement_key: {contract.requirement_key}",
            f"v200_final_release_artifact_record_release_target: {contract.release_target}",
            f"v200_final_release_artifact_record_tag_name: {contract.tag_name}",
            f"v200_final_release_artifact_record_repository_topology: {contract.repository_topology}",
            f"v200_final_release_artifact_record_public_repository: {contract.public_repository}",
            "v200_final_release_artifact_record_locations: " + ",".join(contract.record_locations),
            "v200_final_release_artifact_record_required_public_fields: "
            + ",".join(contract.required_public_fields),
            "v200_final_release_artifact_record_required_true_markers: "
            + ",".join(contract.required_true_markers),
            "v200_final_release_artifact_record_required_false_markers: "
            + ",".join(contract.required_false_markers),
            "v200_final_release_artifact_record_forbidden_success_states: "
            + ",".join(contract.forbidden_success_states),
            "v200_final_release_artifact_record_public_safe_omissions: "
            + ",".join(contract.public_safe_omissions),
            "v200_final_release_artifact_record_creates_or_rebuilds_zip: False",
            "v200_final_release_artifact_record_creates_or_moves_git_refs: False",
            "v200_final_release_artifact_record_publishes_github_release: False",
            f"v200_final_release_artifact_record_next_focus: {contract.next_focus}",
        ]
    )


def _is_full_git_sha(value: object) -> bool:
    return isinstance(value, str) and _FULL_GIT_SHA_RE.fullmatch(value) is not None


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and _FULL_SHA256_RE.fullmatch(value) is not None


def validate_v200_final_release_artifact_record(
    record: Mapping[str, object],
    *,
    inspection: V200FixedReleaseZipInspection | None = None,
) -> V200FinalReleaseArtifactRecordValidation:
    """Validate one public-safe record and optionally bind it to a direct zip inspection."""

    contract = build_v200_final_release_artifact_record_contract()
    missing: list[str] = []
    public_safe = True
    artifact_matches_inspection = inspection is not None

    for field in contract.required_public_fields:
        if field not in record:
            missing.append(f"field:{field}")

    if record.get("status") != "accepted":
        missing.append("status=accepted")
    if record.get("release_target") != contract.release_target:
        missing.append(f"release_target={contract.release_target}")
    if record.get("record_kind") != "final_release_artifact_record":
        missing.append("record_kind=final_release_artifact_record")
    if record.get("repository_topology") != contract.repository_topology:
        missing.append(f"repository_topology={contract.repository_topology}")
    if record.get("public_repository") != contract.public_repository:
        missing.append(f"public_repository={contract.public_repository}")
    if record.get("tag_name") != contract.tag_name:
        missing.append(f"tag_name={contract.tag_name}")
    if record.get("tag_object_type") != "annotated":
        missing.append("tag_object_type=annotated")

    source_head = record.get("source_head")
    main_head = record.get("main_head")
    tag_target_head = record.get("tag_target_head")
    for field_name, value in (
        ("source_head", source_head),
        ("main_head", main_head),
        ("tag_target_head", tag_target_head),
    ):
        if not _is_full_git_sha(value):
            missing.append(f"{field_name}=full-40-char-lowercase-sha")

    if _is_full_git_sha(source_head):
        if main_head != source_head:
            missing.append("main_head=source_head")
        if tag_target_head != source_head:
            missing.append("tag_target_head=source_head")

    public_root_commit_count = record.get("public_root_commit_count")
    if (
        isinstance(public_root_commit_count, bool)
        or not isinstance(public_root_commit_count, int)
        or public_root_commit_count != 1
    ):
        missing.append("public_root_commit_count=1")

    zip_name = record.get("release_zip_name")
    if not isinstance(zip_name, str) or _SAFE_ZIP_NAME_RE.fullmatch(zip_name) is None:
        missing.append("release_zip_name=public-safe-basename")
    zip_size = record.get("release_zip_size_bytes")
    if isinstance(zip_size, bool) or not isinstance(zip_size, int) or zip_size <= 0:
        missing.append("release_zip_size_bytes=positive-int")
    zip_sha256 = record.get("release_zip_sha256")
    if not _is_sha256(zip_sha256):
        missing.append("release_zip_sha256=64-char-lowercase-sha256")

    for marker in contract.required_true_markers:
        if record.get(marker) is not True:
            missing.append(marker)
    for marker in contract.required_false_markers:
        if record.get(marker) is not False:
            missing.append(f"{marker}=False")
            if marker in {
                "private_git_history_included",
                "private_evidence_included",
                "raw_screenshots_included",
                "raw_audio_included",
                "raw_health_data_included",
                "raw_provider_payloads_included",
                "api_keys_included",
                "oauth_tokens_included",
                "authorization_headers_included",
                "private_paths_included",
                "raw_lan_ips_included",
            }:
                public_safe = False
    for forbidden in contract.forbidden_success_states:
        if record.get(forbidden) is True:
            missing.append(f"forbidden:{forbidden}")
            public_safe = False

    if "develop_head" in record:
        missing.append("field:develop_head=not-allowed-in-clean-public-record")
        public_safe = False
    if "main_and_develop_match_source_head" in record:
        missing.append("field:main_and_develop_match_source_head=obsolete")
        public_safe = False

    if inspection is not None:
        if inspection.status != "accepted":
            missing.append("inspection_status=accepted")
            artifact_matches_inspection = False
        if zip_name != inspection.release_zip_name:
            missing.append("release_zip_name=inspection.release_zip_name")
            artifact_matches_inspection = False
        if zip_size != inspection.file_size_bytes:
            missing.append("release_zip_size_bytes=inspection.file_size_bytes")
            artifact_matches_inspection = False
        if zip_sha256 != inspection.sha256:
            missing.append("release_zip_sha256=inspection.sha256")
            artifact_matches_inspection = False
        if not inspection.crc_ok:
            missing.append("inspection_crc_ok=True")
            artifact_matches_inspection = False
        if not inspection.unchanged_during_inspection:
            missing.append("inspection_unchanged=True")
            artifact_matches_inspection = False
        if inspection.missing_entries or inspection.forbidden_entries or inspection.invalid_entries:
            missing.append("inspection_entries=public-safe")
            artifact_matches_inspection = False
    else:
        missing.append("direct_release_zip_inspection_required")
        artifact_matches_inspection = False

    return V200FinalReleaseArtifactRecordValidation(
        status="accepted" if not missing and public_safe and artifact_matches_inspection else "rejected",
        missing_markers=tuple(missing),
        public_safe=public_safe,
        artifact_matches_inspection=artifact_matches_inspection,
    )
