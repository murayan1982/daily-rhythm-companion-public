"""Smoke check for the v2.0.0 immutable final release artifact record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.framework_v200_final_release_artifact_record import (  # noqa: E402
    build_v200_final_release_artifact_record_contract,
    render_v200_final_release_artifact_record_contract,
    validate_v200_final_release_artifact_record,
)
from backend.app.services.framework_v200_final_release_readiness_fixed_zip_with_web_evidence import (  # noqa: E402
    build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract,
    inspect_v200_final_release_readiness_fixed_zip_with_web_evidence,
)
from backend.app.services.framework_v200_fixed_release_zip_with_web_evidence_verification import (  # noqa: E402
    V200FixedReleaseZipInspection,
    build_v200_fixed_release_zip_with_web_evidence_contract,
    render_v200_fixed_release_zip_inspection,
)


SYNTHETIC_HEAD = "0123456789abcdef0123456789abcdef01234567"
SYNTHETIC_HASH = "89abcdef0123456789abcdef0123456789abcdef0123456789abcdef01234567"


def _accepted_record() -> dict[str, object]:
    return {
        "status": "accepted",
        "release_target": "v2.0.0",
        "record_kind": "final_release_artifact_record",
        "repository_topology": "clean_history_public_snapshot",
        "public_repository": "murayan1982/daily-rhythm-companion-public",
        "source_head": SYNTHETIC_HEAD,
        "main_head": SYNTHETIC_HEAD,
        "public_root_commit_count": 1,
        "tag_name": "DRC_v2.0.0",
        "tag_target_head": SYNTHETIC_HEAD,
        "tag_object_type": "annotated",
        "release_zip_name": "DailyRhythmCompanion_20260721_190000.zip",
        "release_zip_size_bytes": 1234567,
        "release_zip_sha256": SYNTHETIC_HASH,
        "day80_accepted_manifest_passed": True,
        "day82_fixed_zip_verification_passed": True,
        "day83_final_release_readiness_passed": True,
        "fixed_zip_inspected_as_is": True,
        "public_main_matches_source_head": True,
        "clean_history_public_root_verified": True,
        "annotated_tag_targets_source_head": True,
        "github_release_same_fixed_zip_required": True,
        "operator_review_accepted": True,
        "fixed_zip_rebuilt_after_verification": False,
        "source_changed_after_fixed_zip_build": False,
        "private_git_history_included": False,
        "private_evidence_included": False,
        "raw_screenshots_included": False,
        "raw_audio_included": False,
        "raw_health_data_included": False,
        "raw_provider_payloads_included": False,
        "api_keys_included": False,
        "oauth_tokens_included": False,
        "authorization_headers_included": False,
        "private_paths_included": False,
        "raw_lan_ips_included": False,
    }


def _synthetic_inspection() -> V200FixedReleaseZipInspection:
    return V200FixedReleaseZipInspection(
        status="accepted",
        release_zip_name="DailyRhythmCompanion_20260721_190000.zip",
        package_root="DailyRhythmCompanion",
        entry_count=638,
        file_size_bytes=1234567,
        sha256=SYNTHETIC_HASH,
        crc_ok=True,
        unchanged_during_inspection=True,
        missing_entries=(),
        forbidden_entries=(),
        invalid_entries=(),
    )


def _check_public_release_sequence_docs() -> bool:
    required_snippets = {
        ROOT / "README.md": (
            '--evidence-json "<private-Day82-marker-json>"',
            '--evidence-json "<private-Day83-marker-json>"',
            'build_v200_final_fixed_release_zip_from_head.ps1 -ManifestPath $manifest',
        ),
        ROOT / "docs" / "v200_fixed_release_zip_with_web_evidence_verification.md": (
            "Public main HEAD == origin/main == fixed ZIP source_head == annotated tag target",
            "--inspect-zip-only",
            "<private-Day82-marker-json>",
        ),
        ROOT / "docs" / "v200_final_release_readiness_fixed_zip_with_web_evidence.md": (
            "matching Public `main` and `origin/main`",
            "legacy `develop_head` fields are rejected",
            "<private-Day83-marker-json>",
        ),
        ROOT / "docs" / "v200_public_repository_migration.md": (
            "explicit `ManifestPath` to the accepted Day80 manifest outside the Public repository",
            "Public-P6 follow-up 3",
        ),
        ROOT / "docs" / "DRC_v200_goal_checklist_small_commit.md": (
            "builder_repository_local_private_manifest_dependency: removed",
            "builder_external_day80_manifest_preflight: required-outside-public-repository",
            "Public-P6 pre-build follow-up 3",
        ),
        ROOT / "scripts" / "README.md": (
            "Public-P4 supersedes that historical topology",
            "Public main HEAD == origin/main",
            '<private-Day82-marker-json>',
            '<private-Day83-marker-json>',
            '--inspect-zip-only',
        ),
    }
    forbidden_active_snippets = {
        ROOT / "docs" / "v200_fixed_release_zip_with_web_evidence_verification.md": (
            "After G-7 is committed and `main` and `develop` point to the same HEAD",
        ),
        ROOT / "docs" / "v200_final_release_readiness_fixed_zip_with_web_evidence.md": (
            "matching `main` and `develop` refs",
        ),
        ROOT / "scripts" / "README.md": (
            "After G-7 is committed and `main`/`develop` are aligned",
        ),
    }

    errors: list[str] = []
    for path, snippets in required_snippets.items():
        if not path.is_file():
            errors.append(f"missing-file:{path.relative_to(ROOT).as_posix()}")
            continue
        body = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in body:
                errors.append(f"missing-snippet:{path.relative_to(ROOT).as_posix()}:{snippet}")
    for path, snippets in forbidden_active_snippets.items():
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet in body:
                errors.append(f"obsolete-active-snippet:{path.relative_to(ROOT).as_posix()}:{snippet}")

    if errors:
        print("[smoke-framework-v200-final-release-artifact-record] ERROR")
        for error in errors:
            print(error)
        return False

    print("v200_final_release_artifact_record_public_release_sequence_docs: synchronized")
    return True


def _run_source_tree_contract_checks() -> bool:
    if not _check_public_release_sequence_docs():
        return False

    day82 = build_v200_fixed_release_zip_with_web_evidence_contract()
    day83 = build_v200_final_release_readiness_fixed_zip_with_web_evidence_contract()
    required_entries = {
        "docs/v200_final_release_artifact_record.md",
        "backend/app/services/framework_v200_final_release_artifact_record.py",
        "scripts/smoke_framework_v200_final_release_artifact_record.py",
    }
    missing_day82 = sorted(required_entries - set(day82.required_zip_entries))
    missing_day83 = sorted(required_entries - set(day83.required_zip_entries))
    if missing_day82 or missing_day83:
        print("[smoke-framework-v200-final-release-artifact-record] ERROR")
        if missing_day82:
            print("Day82 missing artifact-record entries: " + ",".join(missing_day82))
        if missing_day83:
            print("Day83 missing artifact-record entries: " + ",".join(missing_day83))
        return False

    accepted = _accepted_record()
    inspection = _synthetic_inspection()
    result = validate_v200_final_release_artifact_record(accepted, inspection=inspection)
    if result.status != "accepted":
        print("[smoke-framework-v200-final-release-artifact-record] ERROR")
        print("synthetic accepted record was rejected: " + ",".join(result.missing_markers))
        return False

    negative_cases: list[tuple[str, dict[str, object]]] = []

    hash_mismatch = dict(accepted)
    hash_mismatch["release_zip_sha256"] = "0" * 64
    negative_cases.append(("hash-mismatch", hash_mismatch))

    public_main_mismatch = dict(accepted)
    public_main_mismatch["main_head"] = "f" * 40
    negative_cases.append(("public-main-mismatch", public_main_mismatch))

    topology_mismatch = dict(accepted)
    topology_mismatch["repository_topology"] = "same_repository_main_develop"
    negative_cases.append(("topology-mismatch", topology_mismatch))

    private_history = dict(accepted)
    private_history["private_git_history_included"] = True
    negative_cases.append(("private-history", private_history))

    multiple_roots = dict(accepted)
    multiple_roots["public_root_commit_count"] = 2
    negative_cases.append(("multiple-roots", multiple_roots))

    legacy_develop = dict(accepted)
    legacy_develop["develop_head"] = SYNTHETIC_HEAD
    negative_cases.append(("legacy-develop-field", legacy_develop))

    lightweight_tag = dict(accepted)
    lightweight_tag["tag_object_type"] = "lightweight"
    negative_cases.append(("lightweight-tag", lightweight_tag))

    private_path = dict(accepted)
    private_path["private_paths_included"] = True
    negative_cases.append(("private-path", private_path))

    post_build_source_commit = dict(accepted)
    post_build_source_commit["source_changed_after_fixed_zip_build"] = True
    negative_cases.append(("post-build-source-commit", post_build_source_commit))

    for name, candidate in negative_cases:
        negative_result = validate_v200_final_release_artifact_record(candidate, inspection=inspection)
        if negative_result.status != "rejected":
            print("[smoke-framework-v200-final-release-artifact-record] ERROR")
            print(f"negative case unexpectedly accepted: {name}")
            return False

    print("v200_final_release_artifact_record_source_tree_positive_case: accepted")
    print(
        "v200_final_release_artifact_record_source_tree_negative_cases: "
        + ",".join(name for name, _ in negative_cases)
    )
    print("v200_final_release_artifact_record_repository_topology: clean-history-public-snapshot")
    print("v200_final_release_artifact_record_day82_day83_release_surface: synchronized")
    return True


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
        help="Final fixed zip to inspect directly. Required with --record-json.",
    )
    parser.add_argument(
        "--record-json",
        help="Public-safe final artifact record JSON. Required with --release-zip.",
    )
    args = parser.parse_args()

    contract = build_v200_final_release_artifact_record_contract()
    print(render_v200_final_release_artifact_record_contract(contract))

    if not _run_source_tree_contract_checks():
        return 1

    if bool(args.release_zip) != bool(args.record_json):
        print("[smoke-framework-v200-final-release-artifact-record] REJECTED")
        print("--release-zip and --record-json must be supplied together")
        return 1

    if args.release_zip and args.record_json:
        release_zip = Path(args.release_zip)
        if not _run_release_package_check(release_zip):
            print("[smoke-framework-v200-final-release-artifact-record] REJECTED")
            print("release package hygiene check failed")
            return 1
        inspection = inspect_v200_final_release_readiness_fixed_zip_with_web_evidence(release_zip)
        print(render_v200_fixed_release_zip_inspection(inspection))
        try:
            record = json.loads(args.record_json)
        except json.JSONDecodeError as exc:
            print("[smoke-framework-v200-final-release-artifact-record] REJECTED")
            print(f"record JSON could not be parsed: {exc.__class__.__name__}")
            return 1
        if not isinstance(record, dict):
            print("[smoke-framework-v200-final-release-artifact-record] REJECTED")
            print("record JSON must be an object")
            return 1
        result = validate_v200_final_release_artifact_record(record, inspection=inspection)
        print(f"v200_final_release_artifact_record_validation_status: {result.status}")
        print(f"v200_final_release_artifact_record_public_safe: {result.public_safe}")
        print(
            "v200_final_release_artifact_record_artifact_matches_inspection: "
            f"{result.artifact_matches_inspection}"
        )
        if result.status != "accepted":
            print("[smoke-framework-v200-final-release-artifact-record] REJECTED")
            for marker in result.missing_markers:
                print(f"missing: {marker}")
            return 1

    print("[smoke-framework-v200-final-release-artifact-record] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
