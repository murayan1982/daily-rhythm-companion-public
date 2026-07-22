"""Smoke check for v2.0.0 Day83 final release readiness fixed zip with Web evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_final_release_readiness_fixed_zip_with_web_evidence import (  # noqa: E402
    build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract,
    inspect_v200_final_release_readiness_fixed_zip_with_web_evidence,
    render_v200_final_release_readiness_fixed_zip_with_web_evidence_contract,
    validate_v200_final_release_readiness_fixed_zip_with_web_evidence,
)
from backend.app.services.framework_v200_fixed_release_zip_with_web_evidence_verification import (  # noqa: E402
    V200FixedReleaseZipInspection,
    build_v200_fixed_release_zip_with_web_evidence_contract,
    render_v200_fixed_release_zip_inspection,
)


def _accepted_evidence(inspection: V200FixedReleaseZipInspection) -> dict[str, object]:
    return {
        "status": "accepted",
        "release_target": "v2.0.0",
        "manifest_kind": "final_release_readiness_fixed_zip_with_web_evidence",
        "fixed_release_zip_path": f"release/{inspection.release_zip_name}",
        "fixed_release_zip_name": inspection.release_zip_name,
        "fixed_release_zip_size_bytes": inspection.file_size_bytes,
        "fixed_release_zip_sha256": inspection.sha256,
        "day82_verified_release_zip_sha256": inspection.sha256,
        "day80_accepted_manifest_passed": True,
        "day81_final_readiness_passed": True,
        "day82_fixed_zip_verification_passed": True,
        "fixed_release_zip_path_recorded": True,
        "fixed_zip_inspected_as_is": True,
        "same_fixed_zip_used_for_day81_day82_day83": True,
        "no_rebuild_during_day83_verification": True,
        "all_web_screenshot_evidence_accepted": True,
        "release_surface_public_safe": True,
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
    """Resolve a mode without allowing ZIP-only Day83 readiness."""

    if inspect_zip_only:
        if release_zip is None:
            return None, "--inspect-zip-only requires --release-zip"
        if evidence_json is not None:
            return None, "--inspect-zip-only cannot be combined with --evidence-json"
        return "inspection-only", None

    if evidence_json is not None:
        if release_zip is None:
            return None, "marker-only Day83 validation is not allowed; --release-zip is required"
        return "acceptance", None

    if release_zip is not None:
        return (
            None,
            "--release-zip alone is inspection input, not Day83 readiness; "
            "add --inspect-zip-only or --evidence-json",
        )

    return "source-tree-contract", None


def _run_execution_mode_contract_checks() -> bool:
    cases = (
        ((None, None, False), "source-tree-contract", None),
        (("candidate.zip", None, True), "inspection-only", None),
        (("candidate.zip", "{}", False), "acceptance", None),
        (("candidate.zip", None, False), None, "--release-zip alone"),
        ((None, "{}", False), None, "marker-only Day83"),
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
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
            print(f"unexpected execution mode: {mode!r} != {expected_mode!r}")
            return False
        if expected_error is None:
            if error is not None:
                print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
                print(f"unexpected execution-mode error: {error}")
                return False
        elif error is None or expected_error not in error:
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
            print(f"missing execution-mode rejection marker: {expected_error}")
            return False

    print("v200_final_release_readiness_fixed_zip_execution_modes: source-tree-contract,inspection-only,acceptance")
    print("v200_final_release_readiness_fixed_zip_zip_only_acceptance_allowed: False")
    return True


def _run_source_tree_contract_checks() -> bool:
    day82 = build_v200_fixed_release_zip_with_web_evidence_contract()
    day83 = build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract()

    missing_day82_entries = sorted(set(day82.required_zip_entries) - set(day83.required_zip_entries))
    missing_day82_absences = sorted(set(day82.required_absent_entries) - set(day83.required_absent_entries))
    if missing_day82_entries or missing_day82_absences:
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
        if missing_day82_entries:
            print("Day83 lost Day82 required entries: " + ",".join(missing_day82_entries))
        if missing_day82_absences:
            print("Day83 lost Day82 forbidden entries: " + ",".join(missing_day82_absences))
        return False

    required_day83_only = {
        "docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md",
        "docs/operator_evidence_templates/v200_final_release_readiness_fixed_zip_with_web_evidence_day83.example.json",
        "backend/app/services/framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py",
        "scripts/smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py",
    }
    missing_day83_only = sorted(required_day83_only - set(day83.required_zip_entries))
    if missing_day83_only:
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
        print("Day83 final-only release entries are missing: " + ",".join(missing_day83_only))
        return False

    required_g7_entries = {
        "docs/v200_final_release_artifact_record.md",
        "backend/app/services/framework_v200_final_release_artifact_record.py",
        "scripts/smoke_framework_v200_final_release_artifact_record.py",
    }
    missing_g7_entries = sorted(required_g7_entries - set(day83.required_zip_entries))
    if missing_g7_entries:
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
        print("Day83 immutable artifact-record entries are missing: " + ",".join(missing_g7_entries))
        return False

    # Reuse a synthetic Day82-shaped inspection to verify the Day83 evidence binding.
    from tempfile import TemporaryDirectory
    import zipfile

    with TemporaryDirectory(prefix="drc_v200_day83_") as temp_dir:
        candidate = Path(temp_dir) / "accepted.zip"
        with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for relative in day83.required_zip_entries:
                package.writestr(f"DailyRhythmCompanion/{relative}", "")
        inspection = inspect_v200_final_release_readiness_fixed_zip_with_web_evidence(candidate)
        if inspection.status != "accepted":
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
            print("synthetic Day83 release surface was rejected")
            return False

        accepted = _accepted_evidence(inspection)
        validation = validate_v200_final_release_readiness_fixed_zip_with_web_evidence(
            accepted,
            inspection=inspection,
        )
        if validation.status != "accepted":
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
            print("synthetic evidence-backed Day83 readiness was rejected")
            print("missing: " + ",".join(validation.missing_markers))
            return False

        mismatch = dict(accepted)
        mismatch["day82_verified_release_zip_sha256"] = "0" * 64
        mismatch_validation = validate_v200_final_release_readiness_fixed_zip_with_web_evidence(
            mismatch,
            inspection=inspection,
        )
        if (
            mismatch_validation.status == "accepted"
            or "day82_verified_release_zip_sha256=inspected-zip-sha256"
            not in mismatch_validation.missing_markers
        ):
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] ERROR")
            print("negative different-Day82-zip evidence case was not rejected")
            return False

    print("v200_final_release_readiness_fixed_zip_day82_contract_preserved: True")
    print("v200_final_release_readiness_fixed_zip_day83_release_surface_contract: ready")
    print("v200_final_release_readiness_fixed_zip_artifact_record_contract: ready")
    print("v200_final_release_readiness_fixed_zip_same_artifact_evidence_binding: ready")
    return True


def _run_public_distribution_check(release_zip: Path) -> bool:
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "smoke_framework_v200_public_distribution_readiness.py"),
            "--release-zip",
            str(release_zip),
        ],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode == 0


def _run_release_package_check(release_zip: Path) -> bool:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_release_package.py"), str(release_zip)],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release-zip",
        help="Fixed release zip path for inspection-only or evidence-backed readiness.",
    )
    parser.add_argument(
        "--evidence-json",
        help="Private Day83 marker JSON required for Day83 readiness with --release-zip.",
    )
    parser.add_argument(
        "--inspect-zip-only",
        action="store_true",
        help="Inspect --release-zip without claiming Day83 readiness.",
    )
    args = parser.parse_args()

    contract = build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract()
    print(render_v200_final_release_readiness_fixed_zip_with_web_evidence_contract(contract))

    if not _run_execution_mode_contract_checks():
        return 1
    if not _run_source_tree_contract_checks():
        return 1

    mode, mode_error = _resolve_execution_mode(
        release_zip=args.release_zip,
        evidence_json=args.evidence_json,
        inspect_zip_only=args.inspect_zip_only,
    )
    if mode_error is not None:
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        print(mode_error)
        return 1

    print(f"v200_final_release_readiness_fixed_zip_execution_mode: {mode}")
    if mode == "source-tree-contract":
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] OK")
        print("v200_final_release_readiness_fixed_zip_acceptance_status: not-run-source-tree-contract-only")
        return 0

    release_zip = Path(args.release_zip)
    if not _run_release_package_check(release_zip):
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        print("release package hygiene check failed")
        return 1

    if not _run_public_distribution_check(release_zip):
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        print("Public distribution readiness check failed")
        return 1

    inspection = inspect_v200_final_release_readiness_fixed_zip_with_web_evidence(release_zip)
    print(render_v200_fixed_release_zip_inspection(inspection))
    if inspection.status != "accepted":
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        return 1

    if mode == "inspection-only":
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] INSPECTION_ONLY")
        print("v200_final_release_readiness_fixed_zip_acceptance_status: not-run-evidence-required")
        return 0

    try:
        evidence = json.loads(args.evidence_json)
    except json.JSONDecodeError as exc:
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        print(f"Day83 evidence JSON could not be parsed: {exc.__class__.__name__}")
        return 1

    result = validate_v200_final_release_readiness_fixed_zip_with_web_evidence(
        evidence,
        inspection=inspection,
    )
    if result.status != "accepted":
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        for marker in result.missing_markers:
            print(f"missing: {marker}")
        return 1

    print("v200_final_release_readiness_fixed_zip_acceptance_status: accepted-evidence-backed")
    print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
