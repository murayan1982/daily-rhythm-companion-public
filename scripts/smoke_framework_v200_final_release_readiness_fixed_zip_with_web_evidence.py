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
    build_v200_fixed_release_zip_with_web_evidence_contract,
    render_v200_fixed_release_zip_inspection,
)


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

    print("v200_final_release_readiness_fixed_zip_day82_contract_preserved: True")
    print("v200_final_release_readiness_fixed_zip_day83_release_surface_contract: ready")
    print("v200_final_release_readiness_fixed_zip_artifact_record_contract: ready")
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
        help="Optional fixed release zip path to re-inspect directly without rebuilding.",
    )
    parser.add_argument(
        "--evidence-json",
        help="Optional private Day83 marker JSON. It is accepted only with --release-zip.",
    )
    args = parser.parse_args()

    contract = build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract()
    print(render_v200_final_release_readiness_fixed_zip_with_web_evidence_contract(contract))

    if not _run_source_tree_contract_checks():
        return 1

    if args.evidence_json and not args.release_zip:
        print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
        print("marker-only Day83 validation is not allowed; --release-zip is required")
        return 1

    if args.release_zip:
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

    if args.evidence_json:
        try:
            evidence = json.loads(args.evidence_json)
        except json.JSONDecodeError as exc:
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
            print(f"Day83 evidence JSON could not be parsed: {exc.__class__.__name__}")
            return 1
        result = validate_v200_final_release_readiness_fixed_zip_with_web_evidence(evidence)
        if result.status != "accepted":
            print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] REJECTED")
            for marker in result.missing_markers:
                print(f"missing: {marker}")
            return 1

    print("[smoke-framework-v200-final-release-readiness-fixed-zip-with-web-evidence] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
