"""Inspect the v2.0.0 Public distribution source surface or one fixed zip.

Default source mode inspects the clean Public export view of the Private
repository. Tracked Private-only history such as docs/internal, old patch/diff
files, and day-by-day source checks is omitted from that view.
--source-directory inspects an exported Public directory strictly without those
Private-source exclusions. Zip mode opens the supplied artifact as-is and never
rebuilds it.
"""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_public_distribution_readiness import (  # noqa: E402
    GENERATED_FLUTTER_REGISTRANT_PATHS,
    build_v200_public_distribution_readiness_contract,
    inspect_v200_public_distribution_files,
    is_v200_private_repository_export_excluded,
    render_v200_public_distribution_inspection,
    render_v200_public_distribution_readiness_contract,
)


def _source_files() -> tuple[dict[str, bytes], tuple[str, ...]]:
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
    excluded: list[str] = []
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8")
        normalized = relative.replace("\\", "/")
        if is_v200_private_repository_export_excluded(normalized):
            excluded.append(normalized)
            continue
        path = ROOT / relative
        if path.is_file():
            files[normalized] = path.read_bytes()
    return files, tuple(sorted(excluded))


def _zip_files(release_zip: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(release_zip) as package:
        bad_member = package.testzip()
        if bad_member is not None:
            raise RuntimeError(f"zip CRC failed at {bad_member}")

        roots: set[str] = set()
        members = [member for member in package.infolist() if not member.is_dir()]
        for member in members:
            pure = PurePosixPath(member.filename.replace("\\", "/"))
            if pure.parts:
                roots.add(pure.parts[0])
        if len(roots) != 1:
            raise RuntimeError("release zip must contain exactly one package root")

        package_root = next(iter(roots))
        if not package_root.startswith("DailyRhythmCompanion"):
            raise RuntimeError("unexpected package root")

        for member in members:
            pure = PurePosixPath(member.filename.replace("\\", "/"))
            if pure.parts[0] != package_root or len(pure.parts) < 2:
                raise RuntimeError("invalid package member path")
            relative = "/".join(pure.parts[1:])
            if relative in files:
                raise RuntimeError(f"duplicate normalized entry: {relative}")
            files[relative] = package.read(member)
    return files


def _directory_files(source_directory: Path) -> dict[str, bytes]:
    root = source_directory.expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError(f"source directory does not exist: {root}")

    files: dict[str, bytes] = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == ".git":
            continue
        if path.is_symlink():
            raise RuntimeError(f"source directory contains a symbolic link: {relative.as_posix()}")
        if path.is_file():
            normalized = relative.as_posix()
            if normalized in files:
                raise RuntimeError(f"duplicate normalized path: {normalized}")
            files[normalized] = path.read_bytes()
    return files



def _run_contract_self_checks(files: dict[str, bytes], *, surface_kind: str) -> bool:
    missing = dict(files)
    missing.pop("README.md", None)
    missing_result = inspect_v200_public_distribution_files(
        missing, surface_kind=surface_kind + "-negative-missing"
    )
    if missing_result.status == "accepted" or "README.md" not in missing_result.missing_files:
        print("[smoke-framework-v200-public-distribution-readiness] ERROR")
        print("negative missing-file case was not rejected")
        return False

    duplicate = dict(files)
    duplicate["DRC_v200_goal_checklist_small_commit.md"] = b"duplicate"
    duplicate_result = inspect_v200_public_distribution_files(
        duplicate, surface_kind=surface_kind + "-negative-duplicate"
    )
    if (
        duplicate_result.status == "accepted"
        or "DRC_v200_goal_checklist_small_commit.md" not in duplicate_result.forbidden_files
    ):
        print("[smoke-framework-v200-public-distribution-readiness] ERROR")
        print("negative obsolete-duplicate case was not rejected")
        return False

    metadata = dict(files)
    metadata["app/pubspec.yaml"] = metadata["app/pubspec.yaml"].replace(
        b"version: 2.0.0+1", b"version: 1.0.0+1"
    )
    metadata_result = inspect_v200_public_distribution_files(
        metadata, surface_kind=surface_kind + "-negative-metadata"
    )
    if metadata_result.status == "accepted" or not metadata_result.metadata_errors:
        print("[smoke-framework-v200-public-distribution-readiness] ERROR")
        print("negative version-metadata case was not rejected")
        return False

    sensitive = dict(files)
    sensitive["docs/private_path_probe.md"] = b"C:\\Users\\private-user\\secret.txt"
    sensitive_result = inspect_v200_public_distribution_files(
        sensitive, surface_kind=surface_kind + "-negative-sensitive"
    )
    if sensitive_result.status == "accepted" or not sensitive_result.sensitive_content_findings:
        print("[smoke-framework-v200-public-distribution-readiness] ERROR")
        print("negative private-path case was not rejected")
        return False

    generated = dict(files)
    generated["backend/app/__pycache__/probe.cpython-312.pyc"] = b"compiled-cache"
    generated["app/.dart_tool/package_config.json"] = b"{}"
    for generated_path in GENERATED_FLUTTER_REGISTRANT_PATHS:
        generated[generated_path] = b"generated Flutter plugin registration output"
    generated_result = inspect_v200_public_distribution_files(
        generated, surface_kind=surface_kind + "-negative-generated-cache"
    )
    expected_generated = {
        "backend/app/__pycache__/probe.cpython-312.pyc",
        "app/.dart_tool/package_config.json",
        *GENERATED_FLUTTER_REGISTRANT_PATHS,
    }
    if (
        generated_result.status == "accepted"
        or not expected_generated.issubset(set(generated_result.forbidden_files))
    ):
        print("[smoke-framework-v200-public-distribution-readiness] ERROR")
        print("negative generated-cache/registrant case was not rejected")
        return False

    print("v200_public_distribution_source_positive_case: accepted")
    print(
        "v200_public_distribution_source_negative_cases: "
        "missing-required-file,obsolete-duplicate,version-metadata,private-path,"
        "generated-cache,flutter-generated-registrants"
    )
    return True

def _run_release_package_hygiene(release_zip: Path) -> bool:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_release_package.py"), str(release_zip)],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode == 0


def _run_generated_registrant_zip_negative_check() -> bool:
    with tempfile.TemporaryDirectory(prefix="drc-v200-generated-registrant-") as temp_dir:
        probe_zip = Path(temp_dir) / "DailyRhythmCompanion_generated_probe.zip"
        with zipfile.ZipFile(probe_zip, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for generated_path in GENERATED_FLUTTER_REGISTRANT_PATHS:
                package.writestr(
                    f"DailyRhythmCompanion_generated_probe/{generated_path}",
                    b"generated Flutter plugin registration output",
                )

        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_release_package.py"), str(probe_zip)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output = completed.stdout.replace("\\", "/").lower()
        missing_reports = [
            path for path in GENERATED_FLUTTER_REGISTRANT_PATHS
            if path.lower() not in output
        ]
        if completed.returncode == 0 or missing_reports:
            print("[smoke-framework-v200-public-distribution-readiness] ERROR")
            print("release-package checker did not reject every generated registrant path")
            if missing_reports:
                print("missing generated registrant rejection reports: " + ",".join(missing_reports))
            return False

    print("v200_public_distribution_generated_registrant_zip_negative_case: rejected")
    return True


def _check_next_focus_regression(next_focus: str) -> bool:
    required_markers = (
        "final Public pre-build gate issues",
        "commit and push the final Public source",
        "clean Public main",
        "freeze source",
        "build one fixed ZIP",
        "Day81",
        "Day82",
        "Day83",
        "same artifact",
    )
    if "Public-P3" in next_focus or any(marker not in next_focus for marker in required_markers):
        print("[smoke-framework-v200-public-distribution-readiness] ERROR")
        print("next focus is not aligned with the final Public pre-build/release sequence")
        return False
    print("v200_public_distribution_next_focus_regression: current-final-public-sequence")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--release-zip",
        type=Path,
        help="Optional fixed zip to inspect as-is.",
    )
    source_group.add_argument(
        "--source-directory",
        type=Path,
        help=(
            "Optional exported Public source directory to inspect strictly without "
            "Private-repository source exclusions."
        ),
    )
    args = parser.parse_args()

    contract = build_v200_public_distribution_readiness_contract()
    print(render_v200_public_distribution_readiness_contract(contract))
    if not _check_next_focus_regression(contract.next_focus):
        return 1
    if not _run_generated_registrant_zip_negative_check():
        return 1

    try:
        if args.release_zip is not None:
            if not _run_release_package_hygiene(args.release_zip):
                print("[smoke-framework-v200-public-distribution-readiness] REJECTED")
                print("release package hygiene check failed")
                return 1
            files = _zip_files(args.release_zip)
            surface_kind = "fixed-release-zip-as-is"
        elif args.source_directory is not None:
            files = _directory_files(args.source_directory)
            surface_kind = "exported-public-source-directory-strict"
            print(
                "v200_public_distribution_source_export_excluded_private_only: False"
            )
        else:
            files, excluded = _source_files()
            surface_kind = "private-repository-public-export-view"
            print(
                "v200_public_distribution_source_export_excluded_private_only_count: "
                f"{len(excluded)}"
            )
            print(
                "v200_public_distribution_source_export_excluded_private_only: True"
            )
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        print("[smoke-framework-v200-public-distribution-readiness] REJECTED")
        print(f"inspection setup failed: {exc.__class__.__name__}: {exc}")
        return 1

    inspection = inspect_v200_public_distribution_files(files, surface_kind=surface_kind)
    print(render_v200_public_distribution_inspection(inspection))
    if inspection.status != "accepted":
        print("[smoke-framework-v200-public-distribution-readiness] REJECTED")
        return 1
    if not _run_contract_self_checks(files, surface_kind=surface_kind):
        return 1

    print("[smoke-framework-v200-public-distribution-readiness] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
