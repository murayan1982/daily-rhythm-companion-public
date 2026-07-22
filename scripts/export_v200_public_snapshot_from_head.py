"""Export one clean DRC v2.0.0 Public source snapshot from committed HEAD.

The exporter reads only the committed Git tree, applies the committed Public
export policy, validates the selected files strictly, and optionally writes the
snapshot to a new directory outside the Private repository. It never copies
.git metadata, initializes Git, builds a release zip, creates tags, publishes a
repository, reads ignored operator evidence, or accesses the network.
"""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_public_distribution_readiness import (  # noqa: E402
    inspect_v200_public_distribution_files,
    render_v200_public_distribution_inspection,
)
from backend.app.services.framework_v200_public_snapshot_export import (  # noqa: E402
    build_v200_public_snapshot_export_contract,
    render_v200_public_snapshot_export_contract,
    render_v200_public_snapshot_selection,
    select_v200_public_snapshot_files,
)


class ExportError(RuntimeError):
    pass


def _run_git(*args: str, stdout: int | None = subprocess.PIPE) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=stdout,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ExportError(f"git {' '.join(args)} failed: {detail}")
    return completed


def _repository_state(expected_head: str | None) -> tuple[str, str]:
    git_root = Path(_run_git("rev-parse", "--show-toplevel").stdout.decode().strip()).resolve()
    if git_root != ROOT.resolve():
        raise ExportError(f"repository root mismatch: script={ROOT} git={git_root}")

    dirty = _run_git("status", "--porcelain", "--untracked-files=all").stdout
    if dirty:
        raise ExportError("working tree contains tracked or non-ignored uncommitted files")

    head = _run_git("rev-parse", "HEAD").stdout.decode().strip()
    if expected_head and head.lower() != expected_head.strip().lower():
        raise ExportError(f"HEAD mismatch: expected={expected_head} actual={head}")

    branch = _run_git("branch", "--show-current").stdout.decode().strip() or "detached"
    return head, branch


def _committed_archive(head: str) -> tuple[dict[str, bytes], dict[str, int]]:
    archive = _run_git("archive", "--format=tar", head).stdout
    files: dict[str, bytes] = {}
    modes: dict[str, int] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as package:
            for member in package.getmembers():
                if member.isdir():
                    continue
                if not member.isfile():
                    raise ExportError(f"committed tree contains unsupported entry: {member.name}")
                pure = PurePosixPath(member.name.replace("\\", "/"))
                if pure.is_absolute() or ".." in pure.parts or not pure.parts:
                    raise ExportError(f"invalid committed path: {member.name}")
                normalized = "/".join(pure.parts)
                if normalized in files:
                    raise ExportError(f"duplicate committed path: {normalized}")
                extracted = package.extractfile(member)
                if extracted is None:
                    raise ExportError(f"unable to read committed entry: {normalized}")
                files[normalized] = extracted.read()
                modes[normalized] = member.mode
    except tarfile.TarError as exc:
        raise ExportError(f"unable to inspect committed archive: {exc}") from exc
    return files, modes


def _ensure_external_destination(destination: Path) -> Path:
    absolute = destination.expanduser().resolve(strict=False)
    root = ROOT.resolve()
    if absolute == root or root in absolute.parents:
        raise ExportError("output directory must be outside the Private repository")
    if absolute.exists():
        raise ExportError(f"output directory already exists: {absolute}")
    absolute.parent.mkdir(parents=True, exist_ok=True)
    return absolute


def _write_snapshot(
    destination: Path,
    selected_files: dict[str, bytes],
    modes: dict[str, int],
) -> None:
    destination.mkdir(parents=False, exist_ok=False)
    try:
        for relative, data in selected_files.items():
            pure = PurePosixPath(relative)
            target = destination.joinpath(*pure.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            if modes.get(relative, 0) & 0o111:
                target.chmod(target.stat().st_mode | 0o111)
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def _strict_directory_files(destination: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in destination.rglob("*"):
        relative = path.relative_to(destination)
        if path.is_symlink():
            raise ExportError(f"export contains a symbolic link: {relative.as_posix()}")
        if path.is_file():
            files[relative.as_posix()] = path.read_bytes()
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        help="New directory to create outside the Private repository.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate committed HEAD selection without writing files.",
    )
    parser.add_argument(
        "--expected-head",
        help="Optional exact committed HEAD expected by the operator.",
    )
    args = parser.parse_args()

    if args.validate_only and args.output_directory is not None:
        parser.error("--validate-only and --output-directory cannot be combined")
    if not args.validate_only and args.output_directory is None:
        parser.error("provide --output-directory or use --validate-only")

    contract = build_v200_public_snapshot_export_contract()
    print(render_v200_public_snapshot_export_contract(contract))

    destination: Path | None = None
    try:
        head, branch = _repository_state(args.expected_head)
        committed_files, modes = _committed_archive(head)
        selection = select_v200_public_snapshot_files(committed_files)
        print(render_v200_public_snapshot_selection(selection))
        if selection.status != "accepted":
            print("[export-v200-public-snapshot-from-head] REJECTED")
            return 1

        print(f"v200_public_snapshot_export_source_branch: {branch}")
        print(f"v200_public_snapshot_export_source_head: {head}")
        print("v200_public_snapshot_export_private_git_history_copied: False")
        print("v200_public_snapshot_export_ignored_files_read: False")

        if args.validate_only:
            print("v200_public_snapshot_export_write_status: not-written-validate-only")
            print("[export-v200-public-snapshot-from-head] OK")
            return 0

        destination = _ensure_external_destination(args.output_directory)
        selected = dict(selection.selected_files)
        selected_modes = {path: modes[path] for path in selected}
        _write_snapshot(destination, selected, selected_modes)

        written_files = _strict_directory_files(destination)
        if written_files != selected:
            raise ExportError("written snapshot differs from the validated committed selection")
        strict = inspect_v200_public_distribution_files(
            written_files,
            surface_kind="exported-public-source-directory-strict",
        )
        print(render_v200_public_distribution_inspection(strict))
        if strict.status != "accepted":
            raise ExportError("strict post-export Public-distribution validation failed")

        print(f"v200_public_snapshot_export_output_directory: {destination}")
        print(f"v200_public_snapshot_export_written_file_count: {len(written_files)}")
        print("v200_public_snapshot_export_git_repository_initialized: False")
        print("v200_public_snapshot_export_release_zip_created: False")
        print("v200_public_snapshot_export_tag_created: False")
        print("v200_public_snapshot_export_github_release_created: False")
        print("v200_public_snapshot_export_write_status: written-once-and-strictly-validated")
        print("[export-v200-public-snapshot-from-head] OK")
        return 0
    except (ExportError, OSError) as exc:
        if destination is not None and destination.exists():
            shutil.rmtree(destination, ignore_errors=True)
        print("[export-v200-public-snapshot-from-head] REJECTED")
        print(f"{exc.__class__.__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
