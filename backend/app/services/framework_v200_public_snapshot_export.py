"""Clean-history Public snapshot export contract for DRC v2.0.0.

This module selects the committed files that are allowed to cross the boundary
from the existing Private development repository into the new Public source
snapshot. It does not read Git history, write files, create repositories, build
release archives, create tags, or access the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from backend.app.services.framework_v200_public_distribution_readiness import (
    V200PublicDistributionInspection,
    inspect_v200_public_distribution_files,
    is_v200_private_repository_export_excluded,
)


@dataclass(frozen=True)
class V200PublicSnapshotExportContract:
    """Static Public-P3 export boundary."""

    status: str
    requirement_key: str
    source_kind: str
    requires_clean_worktree: bool
    requires_committed_head: bool
    excludes_private_git_history: bool
    excludes_private_only_files: bool
    strict_post_export_validation_required: bool
    creates_git_repository: bool
    creates_release_zip: bool
    creates_or_moves_tags: bool
    publishes_github_release: bool
    next_focus: str


@dataclass(frozen=True)
class V200PublicSnapshotSelection:
    """Selected committed files and the strict Public inspection result."""

    status: str
    selected_files: Mapping[str, bytes]
    excluded_paths: tuple[str, ...]
    inspection: V200PublicDistributionInspection


def build_v200_public_snapshot_export_contract() -> V200PublicSnapshotExportContract:
    return V200PublicSnapshotExportContract(
        status="committed-public-snapshot-export-ready",
        requirement_key="v200_public_snapshot_export",
        source_kind="committed-private-repository-head",
        requires_clean_worktree=True,
        requires_committed_head=True,
        excludes_private_git_history=True,
        excludes_private_only_files=True,
        strict_post_export_validation_required=True,
        creates_git_repository=False,
        creates_release_zip=False,
        creates_or_moves_tags=False,
        publishes_github_release=False,
        next_focus=(
            "Commit Public-P3, validate the committed HEAD export, then write one "
            "clean snapshot outside the Private repository before Public Git init."
        ),
    )


def select_v200_public_snapshot_files(
    files: Mapping[str, bytes],
) -> V200PublicSnapshotSelection:
    """Apply the committed Private-to-Public export policy and inspect strictly."""

    selected: dict[str, bytes] = {}
    excluded: list[str] = []
    for path, data in sorted(files.items()):
        normalized = path.replace("\\", "/")
        while normalized.startswith("./"):
            normalized = normalized[2:]
        if is_v200_private_repository_export_excluded(normalized):
            excluded.append(normalized)
            continue
        selected[normalized] = data

    inspection = inspect_v200_public_distribution_files(
        selected,
        surface_kind="committed-public-snapshot-selection-strict",
    )
    return V200PublicSnapshotSelection(
        status="accepted" if inspection.status == "accepted" else "rejected",
        selected_files=selected,
        excluded_paths=tuple(sorted(excluded)),
        inspection=inspection,
    )


def render_v200_public_snapshot_export_contract(
    contract: V200PublicSnapshotExportContract,
) -> str:
    return "\n".join((
        f"v200_public_snapshot_export_status: {contract.status}",
        f"v200_public_snapshot_export_requirement_key: {contract.requirement_key}",
        f"v200_public_snapshot_export_source_kind: {contract.source_kind}",
        f"v200_public_snapshot_export_requires_clean_worktree: {contract.requires_clean_worktree}",
        f"v200_public_snapshot_export_requires_committed_head: {contract.requires_committed_head}",
        f"v200_public_snapshot_export_excludes_private_git_history: {contract.excludes_private_git_history}",
        f"v200_public_snapshot_export_excludes_private_only_files: {contract.excludes_private_only_files}",
        f"v200_public_snapshot_export_strict_post_export_validation_required: {contract.strict_post_export_validation_required}",
        f"v200_public_snapshot_export_creates_git_repository: {contract.creates_git_repository}",
        f"v200_public_snapshot_export_creates_release_zip: {contract.creates_release_zip}",
        f"v200_public_snapshot_export_creates_or_moves_tags: {contract.creates_or_moves_tags}",
        f"v200_public_snapshot_export_publishes_github_release: {contract.publishes_github_release}",
        f"v200_public_snapshot_export_next_focus: {contract.next_focus}",
    ))


def render_v200_public_snapshot_selection(
    selection: V200PublicSnapshotSelection,
) -> str:
    inspection = selection.inspection
    return "\n".join((
        f"v200_public_snapshot_selection_status: {selection.status}",
        f"v200_public_snapshot_selection_selected_file_count: {len(selection.selected_files)}",
        f"v200_public_snapshot_selection_excluded_private_only_count: {len(selection.excluded_paths)}",
        f"v200_public_snapshot_selection_required_files_present: {inspection.required_files_present}",
        f"v200_public_snapshot_selection_metadata_aligned: {inspection.metadata_aligned}",
        f"v200_public_snapshot_selection_public_safe: {inspection.public_safe}",
        "v200_public_snapshot_selection_missing_files: " + ",".join(inspection.missing_files),
        "v200_public_snapshot_selection_forbidden_files: " + ",".join(inspection.forbidden_files),
        "v200_public_snapshot_selection_metadata_errors: " + ",".join(inspection.metadata_errors),
        "v200_public_snapshot_selection_sensitive_content_findings: " + ",".join(inspection.sensitive_content_findings),
    ))
