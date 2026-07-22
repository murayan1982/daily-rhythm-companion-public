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
    V200FixedReleaseZipInspection,
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


def _accepted_evidence(inspection: V200FixedReleaseZipInspection) -> dict[str, object]:
    return {
        "status": "accepted",
        "release_target": "v2.0.0",
        "manifest_kind": "fixed_release_zip_with_web_evidence_verification",
        "fixed_release_zip_path": f"release/{inspection.release_zip_name}",
        "fixed_release_zip_name": inspection.release_zip_name,
        "fixed_release_zip_size_bytes": inspection.file_size_bytes,
        "fixed_release_zip_sha256": inspection.sha256,
        "day81_final_readiness_passed": True,
        "release_zip_built_once_from_final_committed_public_source": True,
        "release_zip_built_once_before_day82": True,
        "same_fixed_zip_used_for_day81_and_day82": True,
        "fixed_release_zip_path_recorded": True,
        "release_package_check_passed": True,
        "day82_zip_inspected_as_is": True,
        "required_web_evidence_release_surface_present": True,
        "source_tree_day_checks_absent_from_zip": True,
        "private_evidence_artifacts_absent_from_zip": True,
        "no_rebuild_during_verification": True,
        "operator_review_accepted": True,
        "raw_screenshots_included": False,
        "raw_prompts_included": False,
        "raw_provider_payloads_included": False,
        "raw_audio_included": False,
        "raw_google_health_payloads_included": False,
        "api_keys_included": False,
        "oauth_tokens_included": False,
        "authorization_headers_included": False,
        "private_paths_included": False,
        "raw_lan_ips_included": False,
    }


def _resolve_execution_mode(
    *,
    release_zip: str | None,
    evidence_json: str | None,
    inspect_zip_only: bool,
) -> tuple[str | None, str | None]:
    """Resolve a mode without allowing ZIP-only acceptance."""

    if inspect_zip_only:
        if release_zip is None:
            return None, "--inspect-zip-only requires --release-zip"
        if evidence_json is not None:
            return None, "--inspect-zip-only cannot be combined with --evidence-json"
        return "inspection-only", None

    if evidence_json is not None:
        if release_zip is None:
            return None, "marker-only Day82 validation is not allowed; --release-zip is required"
        return "acceptance", None

    if release_zip is not None:
        return (
            None,
            "--release-zip alone is inspection input, not Day82 acceptance; "
            "add --inspect-zip-only or --evidence-json",
        )

    return "source-tree-contract", None


def _run_execution_mode_contract_checks() -> bool:
    cases = (
        ((None, None, False), "source-tree-contract", None),
        (("candidate.zip", None, True), "inspection-only", None),
        (("candidate.zip", "{}", False), "acceptance", None),
        (("candidate.zip", None, False), None, "--release-zip alone"),
        ((None, "{}", False), None, "marker-only Day82"),
        ((None, None, True), None, "--inspect-zip-only requires"),
        (("candidate.zip", "{}", True), None, "cannot be combined"),
    )
    for (release_zip, evidence_json, inspect_only), expected_mode, expected_error in cases:
        mode, error = _resolve_execution_mode(
            release_zip=release_zip,
            evidence_json=evidence_json,
            inspect_zip_only=inspect_only,
        )
        if mode != expected_mode:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print(f"unexpected execution mode: {mode!r} != {expected_mode!r}")
            return False
        if expected_error is None:
            if error is not None:
                print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
                print(f"unexpected execution-mode error: {error}")
                return False
        elif error is None or expected_error not in error:
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print(f"missing execution-mode rejection marker: {expected_error}")
            return False

    print("v200_fixed_release_zip_execution_modes: source-tree-contract,inspection-only,acceptance")
    print("v200_fixed_release_zip_zip_only_acceptance_allowed: False")
    return True


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

        accepted_evidence = _accepted_evidence(accepted)
        accepted_validation = validate_v200_fixed_release_zip_with_web_evidence(
            accepted_evidence,
            inspection=accepted,
        )
        if accepted_validation.status != "accepted":
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("synthetic evidence-backed Day82 acceptance was rejected")
            print("missing: " + ",".join(accepted_validation.missing_markers))
            return False

        mismatched_evidence = dict(accepted_evidence)
        mismatched_evidence["fixed_release_zip_sha256"] = "0" * 64
        mismatched_validation = validate_v200_fixed_release_zip_with_web_evidence(
            mismatched_evidence,
            inspection=accepted,
        )
        if (
            mismatched_validation.status == "accepted"
            or "fixed_release_zip_sha256=inspected-zip-sha256"
            not in mismatched_validation.missing_markers
        ):
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("negative mismatched-evidence case was not rejected")
            return False

        legacy_sequence_evidence = dict(accepted_evidence)
        legacy_sequence_evidence.pop("release_zip_built_once_from_final_committed_public_source")
        legacy_sequence_evidence.pop("release_zip_built_once_before_day82")
        legacy_sequence_evidence["release_zip_built_once_after_day81"] = True
        legacy_sequence_validation = validate_v200_fixed_release_zip_with_web_evidence(
            legacy_sequence_evidence,
            inspection=accepted,
        )
        if legacy_sequence_validation.status == "accepted":
            print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] ERROR")
            print("legacy circular Day82 build marker was still accepted")
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
        "mismatched-evidence,legacy-circular-build-marker,missing-required-entry,"
        "private-evidence-entry,worktree-git-file,extra-package-root"
    )
    return True


def _run_committed_head_builder_contract_checks() -> bool:
    required_snippets = {
        ROOT / "build_v200_final_fixed_release_zip_from_head.ps1": (
            "git status --porcelain --untracked-files=all",
            '$tagOutput = @(& git tag --list "DRC_v2.0.0")',
            '$existingTags = @($tagOutput | Where-Object { $_ })',
            "if ($existingTags.Count -gt 0)",
            "smoke_framework_v200_public_distribution_readiness.py",
            "smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py",
            "smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py",
            'git\" \"worktree\" \"add\" \"--detach',
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
            "BLOCKED_BASENAMES = {",
            '".git",',
            "BLOCKED_PARTS = {",
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
        help="Fixed release zip path for inspection-only or evidence-backed acceptance.",
    )
    parser.add_argument(
        "--evidence-json",
        help="Private Day82 marker JSON required for Day82 acceptance with --release-zip.",
    )
    parser.add_argument(
        "--inspect-zip-only",
        action="store_true",
        help="Inspect --release-zip without claiming Day82 acceptance.",
    )
    args = parser.parse_args()

    contract = build_v200_fixed_release_zip_with_web_evidence_contract()
    print(render_v200_fixed_release_zip_with_web_evidence_contract(contract))

    if not _run_execution_mode_contract_checks():
        return 1
    if not _run_source_tree_inspection_checks():
        return 1
    if not _run_committed_head_builder_contract_checks():
        return 1

    mode, mode_error = _resolve_execution_mode(
        release_zip=args.release_zip,
        evidence_json=args.evidence_json,
        inspect_zip_only=args.inspect_zip_only,
    )
    if mode_error is not None:
        print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
        print(mode_error)
        return 1

    print(f"v200_fixed_release_zip_execution_mode: {mode}")
    if mode == "source-tree-contract":
        print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] OK")
        print("v200_fixed_release_zip_acceptance_status: not-run-source-tree-contract-only")
        return 0

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

    if mode == "inspection-only":
        print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] INSPECTION_ONLY")
        print("v200_fixed_release_zip_acceptance_status: not-run-evidence-required")
        return 0

    try:
        evidence = json.loads(args.evidence_json)
    except json.JSONDecodeError as exc:
        print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
        print(f"Day82 evidence JSON could not be parsed: {exc.__class__.__name__}")
        return 1

    result = validate_v200_fixed_release_zip_with_web_evidence(
        evidence,
        inspection=inspection,
    )
    if result.status != "accepted":
        print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] REJECTED")
        for marker in result.missing_markers:
            print(f"missing: {marker}")
        return 1

    print("v200_fixed_release_zip_acceptance_status: accepted-evidence-backed")
    print("[smoke-framework-v200-fixed-release-zip-with-web-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
