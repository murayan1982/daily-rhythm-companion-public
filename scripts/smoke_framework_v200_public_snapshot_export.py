"""Smoke-check the Public-P3 committed clean-snapshot export contract."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_public_distribution_readiness import (  # noqa: E402
    inspect_v200_public_distribution_files,
)
from backend.app.services.framework_v200_public_snapshot_export import (  # noqa: E402
    build_v200_public_snapshot_export_contract,
    render_v200_public_snapshot_export_contract,
    render_v200_public_snapshot_selection,
    select_v200_public_snapshot_files,
)


def _working_files() -> dict[str, bytes]:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError("git ls-files failed")
    files: dict[str, bytes] = {}
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8")
        path = ROOT / relative
        if path.is_file():
            files[relative.replace("\\", "/")] = path.read_bytes()
    return files


def main() -> int:
    contract = build_v200_public_snapshot_export_contract()
    print(render_v200_public_snapshot_export_contract(contract))

    required_true = (
        contract.requires_clean_worktree,
        contract.requires_committed_head,
        contract.excludes_private_git_history,
        contract.excludes_private_only_files,
        contract.strict_post_export_validation_required,
    )
    forbidden_true = (
        contract.creates_git_repository,
        contract.creates_release_zip,
        contract.creates_or_moves_tags,
        contract.publishes_github_release,
    )
    if not all(required_true) or any(forbidden_true):
        print("[smoke-framework-v200-public-snapshot-export] ERROR")
        print("static export contract is inconsistent")
        return 1

    files = _working_files()
    selection = select_v200_public_snapshot_files(files)
    print(render_v200_public_snapshot_selection(selection))
    if selection.status != "accepted":
        print("[smoke-framework-v200-public-snapshot-export] ERROR")
        print("current Public export view was rejected")
        return 1

    required_export_files = (
        "backend/app/services/framework_v200_public_snapshot_export.py",
        "docs/v200_public_snapshot_export.md",
        "scripts/export_v200_public_snapshot_from_head.py",
        "scripts/smoke_framework_v200_public_snapshot_export.py",
    )
    if any(path not in selection.selected_files for path in required_export_files):
        print("[smoke-framework-v200-public-snapshot-export] ERROR")
        print("Public-P3 files are missing from the selected snapshot")
        return 1

    synthetic = dict(files)
    synthetic["docs/internal/private_history_probe.md"] = b"private-only"
    synthetic["private_export_probe.patch"] = b"diff --git a/a b/a"
    synthetic_selection = select_v200_public_snapshot_files(synthetic)
    if (
        "docs/internal/private_history_probe.md" not in synthetic_selection.excluded_paths
        or "private_export_probe.patch" not in synthetic_selection.excluded_paths
        or synthetic_selection.status != "accepted"
    ):
        print("[smoke-framework-v200-public-snapshot-export] ERROR")
        print("Private-only exclusion case failed")
        return 1

    strict_unfiltered = inspect_v200_public_distribution_files(
        synthetic,
        surface_kind="negative-unfiltered-private-source",
    )
    if strict_unfiltered.status == "accepted":
        print("[smoke-framework-v200-public-snapshot-export] ERROR")
        print("strict unfiltered negative case was not rejected")
        return 1

    missing = dict(selection.selected_files)
    missing.pop("README.md", None)
    missing_result = inspect_v200_public_distribution_files(
        missing,
        surface_kind="negative-export-missing-required",
    )
    if missing_result.status == "accepted":
        print("[smoke-framework-v200-public-snapshot-export] ERROR")
        print("missing required file negative case was not rejected")
        return 1

    print("v200_public_snapshot_export_source_positive_case: accepted")
    print(
        "v200_public_snapshot_export_source_negative_cases: "
        "unfiltered-private-source,missing-required-file"
    )
    print("v200_public_snapshot_export_writes_files: False")
    print("v200_public_snapshot_export_reads_ignored_files: False")
    print("v200_public_snapshot_export_creates_git_repository: False")
    print("[smoke-framework-v200-public-snapshot-export] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
