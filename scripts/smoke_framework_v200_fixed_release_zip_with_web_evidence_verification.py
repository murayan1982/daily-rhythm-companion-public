"""Smoke check for v2.0.0 Day82 fixed release zip with accepted Web evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_fixed_release_zip_with_web_evidence_verification import (  # noqa: E402
    build_v200_fixed_release_zip_with_web_evidence_contract,
    inspect_v200_fixed_release_zip_with_web_evidence,
    render_v200_fixed_release_zip_inspection,
    render_v200_fixed_release_zip_with_web_evidence_contract,
    validate_v200_fixed_release_zip_with_web_evidence,
)


def _write_synthetic_zip(
    path: Path,
    *,
    omit: str | None = None,
    extras: tuple[str, ...] = (),
) -> None:
    contract = build_v200_fixed_release_zip_with_web_evidence_contract()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for relative in contract.required_zip_entries:
            if relative == omit:
                continue
            package.writestr(f"DailyRhythmCompanion/{relative}", "")
        for name in extras:
            package.writestr(name, "")


def _run_source_tree_inspection_checks() -> bool:
    with tempfile.TemporaryDirectory(prefix="drc_v200_day82_") as temp_dir:
        temp = Path(temp_dir)

        accepted_zip = temp / "accepted.zip"
        _write_synthetic_zip(accepted_zip)
        accepted = inspect_v200_fixed_release_zip_with_web_evidence(accepted_zip)
        if accepted.status != "accepted":
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print(render_v200_fixed_release_zip_inspection(accepted))
            return False

        missing_zip = temp / "missing.zip"
        _write_synthetic_zip(missing_zip, omit="README.md")
        missing = inspect_v200_fixed_release_zip_with_web_evidence(missing_zip)
        if missing.status == "accepted" or "README.md" not in missing.missing_entries:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("negative missing-required-entry case was not rejected")
            return False

        forbidden_zip = temp / "forbidden.zip"
        _write_synthetic_zip(
            forbidden_zip,
            extras=("DailyRhythmCompanion/operator_evidence/private_manifest.json",),
        )
        forbidden = inspect_v200_fixed_release_zip_with_web_evidence(forbidden_zip)
        if forbidden.status == "accepted" or not forbidden.forbidden_entries:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("negative private-evidence-entry case was not rejected")
            return False

        worktree_git_zip = temp / "worktree-git-file.zip"
        _write_synthetic_zip(
            worktree_git_zip,
            extras=("DailyRhythmCompanion/.git",),
        )
        worktree_git = inspect_v200_fixed_release_zip_with_web_evidence(worktree_git_zip)
        if worktree_git.status == "accepted" or not worktree_git.forbidden_entries:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("negative worktree .git file case was not rejected")
            return False

        extra_root_zip = temp / "extra-root.zip"
        _write_synthetic_zip(extra_root_zip, extras=("UnexpectedRoot/README.md",))
        extra_root = inspect_v200_fixed_release_zip_with_web_evidence(extra_root_zip)
        if extra_root.status == "accepted" or not any(
            marker.startswith("package-root:") for marker in extra_root.invalid_entries
        ):
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("negative extra-package-root case was not rejected")
            return False

    print("v200_fixed_release_zip_source_tree_positive_case: accepted")
    print(
        "v200_fixed_release_zip_source_tree_negative_cases: "
        "missing-required-entry,private-evidence-entry,worktree-git-file,extra-package-root"
    )
    return True



def _run_committed_head_builder_contract_checks() -> bool:
    required_snippets = {
        ROOT / "build_v200_final_fixed_release_zip_from_head.ps1": (
            "git status --porcelain --untracked-files=all",
            '$tagOutput = @(& git tag --list "DRC_v2.0.0")',
            '$existingTags = @($tagOutput | Where-Object { $_ })',
            'if ($existingTags.Count -gt 0)',
            "smoke_framework_v200_public_distribution_readiness.py",
            "smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py",
            "smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py",
            "git\" \"worktree\" \"add\" \"--detach",
            "build_release.bat release",
            "v200_final_fixed_release_zip_build_invocation_count",
            "Get-FileHash",
            "verification_status: not-run",
        ),
        ROOT / "build_release.bat": (
            "DENYLIST_PACKAGE_BUILDER_HARDENING=v9-committed-head-worktree-git-file",
            '".git" ^',
            "$filePatterns = @('.git'",
        ),
        ROOT / "scripts" / "check_release_package.py": (
            'BLOCKED_BASENAMES = {',
            '".git",',
            'BLOCKED_PARTS = {',
        ),
    }
    for path, snippets in required_snippets.items():
        if not path.exists():
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print(f"missing committed-HEAD builder contract file: {path.relative_to(ROOT)}")
            return False
        text = path.read_text(encoding="utf-8")
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print(
                f"{path.relative_to(ROOT)} is missing builder hardening markers: "
                + ",".join(missing)
            )
            return False
    print("v200_fixed_release_zip_committed_head_builder_contract: ready")
    print("v200_fixed_release_zip_worktree_git_file_exclusion_contract: ready")
    return True

def _run_public_distribution_check(release_zip: Path) -> bool:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "smoke_framework_v200_public_distribution_readiness.py"),
        "--release-zip",
        str(release_zip),
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode == 0


def _run_release_package_check(release_zip: Path) -> bool:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "check_release_package.py"),
        str(release_zip),
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release-zip",
        help="Optional fixed release zip path to inspect directly without rebuilding.",
    )
    parser.add_argument(
        "--evidence-json",
        help="Optional private Day82 marker JSON. It is accepted only with --release-zip.",
    )
    args = parser.parse_args()

    contract = build_v200_fixed_release_zip_with_web_evidence_contract()
    print(render_v200_fixed_release_zip_with_web_evidence_contract(contract))

    if not _run_source_tree_inspection_checks():
        return 1
    if not _run_committed_head_builder_contract_checks():
        return 1

    if args.evidence_json and not args.release_zip:
        print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
        print("marker-only Day82 validation is not allowed; --release-zip is required")
        return 1

    if args.release_zip:
        release_zip = Path(args.release_zip)
        if not _run_release_package_check(release_zip):
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
            print("release package hygiene check failed")
            return 1

        if not _run_public_distribution_check(release_zip):
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
            print("Public distribution readiness check failed")
            return 1

        inspection = inspect_v200_fixed_release_zip_with_web_evidence(release_zip)
        print(render_v200_fixed_release_zip_inspection(inspection))
        if inspection.status != "accepted":
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
            return 1

    if args.evidence_json:
        try:
            evidence = json.loads(args.evidence_json)
        except json.JSONDecodeError as exc:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
            print(f"Day82 evidence JSON could not be parsed: {exc.__class__.__name__}")
            return 1
        result = validate_v200_fixed_release_zip_with_web_evidence(evidence)
        if result.status != "accepted":
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
            for marker in result.missing_markers:
                print(f"missing: {marker}")
            return 1

    print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
