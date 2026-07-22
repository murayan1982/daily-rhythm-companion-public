"""v2.0.0 Day82 fixed release zip verification with accepted Web evidence.

This module defines the public-safe contract for inspecting one fixed release zip
as-is after the accepted Web evidence enforcement path is in place. It does not
build release zips, call providers, call Google Health, start the backend, run
Flutter Web, inspect raw screenshots, tag releases, or use the network.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
from typing import Mapping
import zipfile


@dataclass(frozen=True)
class V200FixedReleaseZipWithWebEvidenceContract:
    """Public-safe Day82 release zip verification contract."""

    status: str
    requirement_key: str
    requires_day81_final_readiness: bool
    requires_evidence_with_release_zip_for_acceptance: bool
    allows_inspection_only_mode: bool
    inspects_zip_as_is: bool
    creates_or_rebuilds_zip: bool
    required_zip_entries: tuple[str, ...]
    required_absent_entries: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    forbidden_success_states: tuple[str, ...]
    next_focus: str


@dataclass(frozen=True)
class V200FixedReleaseZipInspection:
    """Direct inspection result for one fixed release zip."""

    status: str
    release_zip_name: str
    package_root: str
    entry_count: int
    file_size_bytes: int
    sha256: str
    crc_ok: bool
    unchanged_during_inspection: bool
    missing_entries: tuple[str, ...]
    forbidden_entries: tuple[str, ...]
    invalid_entries: tuple[str, ...]


@dataclass(frozen=True)
class V200FixedReleaseZipWithWebEvidenceValidation:
    """Validation result for private Day82 operator evidence."""

    status: str
    missing_markers: tuple[str, ...]
    public_safe: bool


def build_v200_fixed_release_zip_with_web_evidence_contract() -> V200FixedReleaseZipWithWebEvidenceContract:
    """Build the Day82 fixed-zip verification contract."""

    required_zip_entries = (
        "README.md",
        "roadmap.md",
        "LICENSE",
        "build_release.bat",
        "build_v200_final_fixed_release_zip_from_head.ps1",
        "docs/DRC_v200_goal_checklist_small_commit.md",
        "docs/v2_prerelease_requirements.md",
        "docs/v200_accepted_web_screenshot_evidence_enforcement.md",
        "docs/v200_real_llm_web_screenshot_evidence_capture.md",
        "docs/v200_real_tts_web_audio_screenshot_evidence_capture.md",
        "docs/v200_real_google_health_web_sleep_screenshot_evidence_capture.md",
        "docs/v200_web_image_display_screenshot_evidence_capture.md",
        "docs/v200_accepted_web_evidence_manifest_aggregate.md",
        "docs/v200_final_release_readiness_with_web_evidence.md",
        "docs/v200_fixed_release_zip_with_web_evidence_verification.md",
        "docs/v200_final_release_artifact_record.md",
        "docs/v200_public_distribution_readiness.md",
        "backend/app/services/framework_v200_public_distribution_readiness.py",
        "scripts/smoke_framework_v200_public_distribution_readiness.py",
        "backend/app/services/framework_v200_final_release_artifact_record.py",
        "scripts/smoke_framework_v200_final_release_artifact_record.py",
        "docs/operator_evidence_templates/v200_accepted_web_screenshot_evidence_day73.example.json",
        "docs/operator_evidence_templates/v200_real_llm_web_screenshot_day76.example.json",
        "docs/operator_evidence_templates/v200_real_tts_web_audio_screenshot_day77.example.json",
        "docs/operator_evidence_templates/v200_real_google_health_web_sleep_screenshot_day78.example.json",
        "docs/operator_evidence_templates/v200_web_image_display_screenshot_day79.example.json",
        "docs/operator_evidence_templates/v200_accepted_web_evidence_manifest_day80.example.json",
        "docs/operator_evidence_templates/v200_final_release_readiness_with_web_evidence_day81.example.json",
        "docs/operator_evidence_templates/v200_fixed_release_zip_with_web_evidence_day82.example.json",
        "backend/app/services/framework_v200_accepted_web_screenshot_evidence_enforcement.py",
        "backend/app/services/framework_v200_real_llm_web_screenshot_evidence.py",
        "backend/app/services/framework_v200_real_tts_web_audio_screenshot_evidence.py",
        "backend/app/services/framework_v200_real_google_health_web_sleep_screenshot_evidence.py",
        "backend/app/services/framework_v200_web_image_display_screenshot_evidence.py",
        "backend/app/services/framework_v200_accepted_web_evidence_manifest_aggregate.py",
        "backend/app/services/framework_v200_final_release_readiness_with_web_evidence.py",
        "backend/app/services/framework_v200_fixed_release_zip_with_web_evidence_verification.py",
        "scripts/smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py",
        "scripts/smoke_framework_v200_real_llm_web_screenshot_evidence.py",
        "scripts/smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py",
        "scripts/smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py",
        "scripts/smoke_framework_v200_web_image_display_screenshot_evidence.py",
        "scripts/smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py",
        "scripts/smoke_framework_v200_final_release_readiness_with_web_evidence.py",
        "scripts/smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py",
        "backend/env_profiles/mock_safe.env",
        "backend/env_profiles/framework_local.env.example",
    )
    required_absent_entries = (
        "docs/internal/",
        "release/",
        "__pycache__/",
        ".git/",
        ".venv/",
        "repo_files/",
        "optional_replacements/",
        "operator_evidence/",
        "private_operator_evidence/",
        "operator_evidence/private/",
        "DRC_v200_Day",
        "DRC_v200_goal_checklist_small_commit_CommitC_ACCEPTED.md",
        "replacement_bundle",
        "next_thread_handoff",
        "raw_screenshot",
        "raw_audio",
        "raw_google_health_payload",
        "scripts/check_v200_accepted_web_screenshot_evidence_day73.py",
        "scripts/check_v200_web_execution_screenshot_collection_day74.py",
        "scripts/check_v200_private_web_evidence_manifest_day75.py",
        "scripts/check_v200_real_llm_web_screenshot_day76.py",
        "scripts/check_v200_real_tts_web_audio_screenshot_day77.py",
        "scripts/check_v200_real_google_health_web_sleep_screenshot_day78.py",
        "scripts/check_v200_web_image_display_screenshot_day79.py",
        "scripts/check_v200_accepted_web_evidence_manifest_day80.py",
        "scripts/check_v200_final_release_readiness_with_web_evidence_day81.py",
        "scripts/check_v200_fixed_release_zip_with_web_evidence_day82.py",
    )
    return V200FixedReleaseZipWithWebEvidenceContract(
        status="fixed-release-zip-with-accepted-web-evidence-verification-ready",
        requirement_key="v200_fixed_release_zip_with_web_evidence",
        requires_day81_final_readiness=True,
        requires_evidence_with_release_zip_for_acceptance=True,
        allows_inspection_only_mode=True,
        inspects_zip_as_is=True,
        creates_or_rebuilds_zip=False,
        required_zip_entries=required_zip_entries,
        required_absent_entries=required_absent_entries,
        public_safe_omissions=(
            "raw_screenshots",
            "raw_prompts",
            "raw_provider_payloads",
            "raw_audio_files",
            "raw_google_health_payloads",
            "api_keys",
            "oauth_tokens",
            "authorization_headers",
            "private_absolute_paths",
            "raw_lan_ips",
            "private_evidence_stores",
            "replacement_bundles",
            "source_tree_day_check_scripts",
            "production_or_store_claims",
            "medical_claims",
        ),
        forbidden_success_states=(
            "day81_not_passed",
            "release_zip_not_built_from_final_committed_public_source",
            "different_zip_used_for_day81_and_day82",
            "release_zip_rebuilt_during_verification",
            "zip_not_inspected_as_is",
            "required_file_missing_from_zip",
            "day_check_script_included_in_zip",
            "raw_screenshot_included",
            "raw_prompt_included",
            "raw_provider_payload_included",
            "raw_audio_included",
            "raw_google_health_payload_included",
            "api_key_included",
            "oauth_token_included",
            "authorization_header_included",
            "private_path_included",
            "raw_lan_ip_included",
            "private_evidence_store_included",
            "replacement_bundle_included",
            "production_claim",
            "app_store_claim",
            "medical_claim",
            "skipped",
            "unavailable",
            "fallback_only",
            "placeholder_only",
        ),
        next_focus="Run final release readiness against the same fixed zip without rebuilding.",
    )


def render_v200_fixed_release_zip_with_web_evidence_contract(
    contract: V200FixedReleaseZipWithWebEvidenceContract,
) -> str:
    """Render the Day82 contract as deterministic text."""

    return "\n".join(
        [
            f"v200_fixed_release_zip_with_web_evidence_status: {contract.status}",
            f"v200_fixed_release_zip_with_web_evidence_requirement_key: {contract.requirement_key}",
            f"v200_fixed_release_zip_with_web_evidence_requires_day81_final_readiness: {contract.requires_day81_final_readiness}",
            "v200_fixed_release_zip_with_web_evidence_requires_evidence_with_release_zip_for_acceptance: "
            f"{contract.requires_evidence_with_release_zip_for_acceptance}",
            "v200_fixed_release_zip_with_web_evidence_allows_inspection_only_mode: "
            f"{contract.allows_inspection_only_mode}",
            f"v200_fixed_release_zip_with_web_evidence_inspects_zip_as_is: {contract.inspects_zip_as_is}",
            f"v200_fixed_release_zip_with_web_evidence_creates_or_rebuilds_zip: {contract.creates_or_rebuilds_zip}",
            "v200_fixed_release_zip_with_web_evidence_required_zip_entries: " + ",".join(contract.required_zip_entries),
            "v200_fixed_release_zip_with_web_evidence_required_absent_entries: " + ",".join(contract.required_absent_entries),
            "v200_fixed_release_zip_with_web_evidence_public_safe_omissions: " + ",".join(contract.public_safe_omissions),
            "v200_fixed_release_zip_with_web_evidence_forbidden_success_states: " + ",".join(contract.forbidden_success_states),
            "v200_fixed_release_zip_with_web_evidence_default_provider_status: not-called",
            "v200_fixed_release_zip_with_web_evidence_default_backend_status: not-started",
            "v200_fixed_release_zip_with_web_evidence_default_browser_status: not-opened",
            "v200_fixed_release_zip_with_web_evidence_default_screenshot_status: not-inspected",
            "v200_fixed_release_zip_with_web_evidence_default_release_zip_status: not-created-or-rebuilt",
            f"v200_fixed_release_zip_with_web_evidence_next_focus: {contract.next_focus}",
        ]
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_zip_name(name: str) -> tuple[str | None, str | None]:
    normalized = name.replace("\\", "/").strip("/")
    if not normalized:
        return None, None
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or any(":" in part for part in path.parts):
        return None, f"unsafe-path:{normalized}"
    return "/".join(path.parts), None


def _matches_absent_rule(relative_name: str, rule: str) -> bool:
    relative_lower = relative_name.lower()
    rule_lower = rule.replace("\\", "/").lower()
    if rule_lower.endswith("/"):
        prefix = rule_lower.rstrip("/")
        return relative_lower == prefix or relative_lower.startswith(prefix + "/")
    if "/" in rule_lower:
        return relative_lower == rule_lower
    return rule_lower in relative_lower


def inspect_v200_fixed_release_zip_with_web_evidence(
    release_zip_path: str | Path,
) -> V200FixedReleaseZipInspection:
    """Inspect one Day82 fixed release zip directly without rebuilding it."""

    contract = build_v200_fixed_release_zip_with_web_evidence_contract()
    return inspect_fixed_release_zip_as_is(
        release_zip_path,
        required_zip_entries=contract.required_zip_entries,
        required_absent_entries=contract.required_absent_entries,
    )


def inspect_fixed_release_zip_as_is(
    release_zip_path: str | Path,
    *,
    required_zip_entries: tuple[str, ...],
    required_absent_entries: tuple[str, ...],
) -> V200FixedReleaseZipInspection:
    """Inspect one fixed release zip against the supplied public contract."""

    path = Path(release_zip_path)
    missing_entries: list[str] = []
    forbidden_entries: list[str] = []
    invalid_entries: list[str] = []
    package_root = ""
    entry_count = 0
    file_size_bytes = 0
    file_size_after = 0
    mtime_ns_before = 0
    mtime_ns_after = 0
    sha256_before = ""
    sha256_after = ""
    crc_ok = False

    if not path.exists() or not path.is_file():
        invalid_entries.append("release-zip-missing")
    elif path.suffix.lower() != ".zip":
        invalid_entries.append("release-zip-extension")
    else:
        stat_before = path.stat()
        file_size_bytes = stat_before.st_size
        mtime_ns_before = stat_before.st_mtime_ns
        if file_size_bytes <= 0:
            invalid_entries.append("release-zip-empty")
        else:
            sha256_before = _sha256(path)
            try:
                with zipfile.ZipFile(path) as package:
                    bad_crc_entry = package.testzip()
                    crc_ok = bad_crc_entry is None
                    if bad_crc_entry is not None:
                        invalid_entries.append(f"crc:{bad_crc_entry}")

                    normalized_entries: list[str] = []
                    seen_casefolded: set[str] = set()
                    roots: set[str] = set()
                    for info in package.infolist():
                        normalized, error = _normalize_zip_name(info.filename)
                        if error:
                            invalid_entries.append(error)
                            continue
                        if normalized is None:
                            continue
                        casefolded = normalized.casefold()
                        if casefolded in seen_casefolded:
                            invalid_entries.append(f"duplicate-entry:{normalized}")
                            continue
                        seen_casefolded.add(casefolded)
                        normalized_entries.append(normalized)
                        roots.add(normalized.split("/", 1)[0])

                    entry_count = len(normalized_entries)
                    if roots != {"DailyRhythmCompanion"}:
                        invalid_entries.append(
                            "package-root:" + (",".join(sorted(roots)) if roots else "missing")
                        )
                    else:
                        package_root = "DailyRhythmCompanion"

                    relative_entries: set[str] = set()
                    if package_root:
                        root_prefix = package_root + "/"
                        for normalized in normalized_entries:
                            if normalized == package_root:
                                continue
                            if not normalized.startswith(root_prefix):
                                invalid_entries.append(f"outside-package-root:{normalized}")
                                continue
                            relative = normalized[len(root_prefix) :].strip("/")
                            if relative:
                                relative_entries.add(relative)

                    missing_entries.extend(
                        entry
                        for entry in required_zip_entries
                        if entry not in relative_entries
                    )
                    for relative in sorted(relative_entries):
                        for rule in required_absent_entries:
                            if _matches_absent_rule(relative, rule):
                                forbidden_entries.append(f"{relative} ({rule})")
                                break
            except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
                invalid_entries.append(f"zip-open:{exc.__class__.__name__}")

            if path.exists() and path.is_file():
                stat_after = path.stat()
                file_size_after = stat_after.st_size
                mtime_ns_after = stat_after.st_mtime_ns
                sha256_after = _sha256(path)

    unchanged = (
        bool(sha256_before)
        and sha256_before == sha256_after
        and file_size_bytes == file_size_after
        and mtime_ns_before == mtime_ns_after
    )
    if sha256_before and not unchanged:
        invalid_entries.append("release-zip-changed-during-inspection")

    status = (
        "accepted"
        if not missing_entries
        and not forbidden_entries
        and not invalid_entries
        and crc_ok
        and unchanged
        else "rejected"
    )
    return V200FixedReleaseZipInspection(
        status=status,
        release_zip_name=path.name,
        package_root=package_root,
        entry_count=entry_count,
        file_size_bytes=file_size_bytes,
        sha256=sha256_after or sha256_before,
        crc_ok=crc_ok,
        unchanged_during_inspection=unchanged,
        missing_entries=tuple(missing_entries),
        forbidden_entries=tuple(forbidden_entries),
        invalid_entries=tuple(invalid_entries),
    )


def render_v200_fixed_release_zip_inspection(
    inspection: V200FixedReleaseZipInspection,
) -> str:
    """Render direct zip inspection results without exposing private paths."""

    return "\n".join(
        [
            f"v200_fixed_release_zip_inspection_status: {inspection.status}",
            f"v200_fixed_release_zip_name: {inspection.release_zip_name}",
            f"v200_fixed_release_zip_package_root: {inspection.package_root}",
            f"v200_fixed_release_zip_entry_count: {inspection.entry_count}",
            f"v200_fixed_release_zip_file_size_bytes: {inspection.file_size_bytes}",
            f"v200_fixed_release_zip_sha256: {inspection.sha256}",
            f"v200_fixed_release_zip_crc_ok: {inspection.crc_ok}",
            f"v200_fixed_release_zip_unchanged_during_inspection: {inspection.unchanged_during_inspection}",
            "v200_fixed_release_zip_missing_entries: " + ",".join(inspection.missing_entries),
            "v200_fixed_release_zip_forbidden_entries: " + ",".join(inspection.forbidden_entries),
            "v200_fixed_release_zip_invalid_entries: " + ",".join(inspection.invalid_entries),
        ]
    )


def validate_v200_fixed_release_zip_with_web_evidence(
    evidence: Mapping[str, object],
    *,
    inspection: V200FixedReleaseZipInspection | None = None,
) -> V200FixedReleaseZipWithWebEvidenceValidation:
    """Validate private Day82 evidence and bind it to the inspected fixed zip."""

    missing: list[str] = []
    if evidence.get("status") != "accepted":
        missing.append("status=accepted")
    if evidence.get("release_target") != "v2.0.0":
        missing.append("release_target=v2.0.0")
    if evidence.get("manifest_kind") != "fixed_release_zip_with_web_evidence_verification":
        missing.append("manifest_kind=fixed_release_zip_with_web_evidence_verification")
    for marker in (
        "day81_final_readiness_passed",
        "release_zip_built_once_from_final_committed_public_source",
        "release_zip_built_once_before_day82",
        "same_fixed_zip_used_for_day81_and_day82",
        "fixed_release_zip_path_recorded",
        "release_package_check_passed",
        "day82_zip_inspected_as_is",
        "required_web_evidence_release_surface_present",
        "source_tree_day_checks_absent_from_zip",
        "private_evidence_artifacts_absent_from_zip",
        "no_rebuild_during_verification",
        "operator_review_accepted",
    ):
        if evidence.get(marker) is not True:
            missing.append(marker)

    if "release_zip_built_once_after_day81" in evidence:
        missing.append("obsolete:release_zip_built_once_after_day81")

    if inspection is None or inspection.status != "accepted":
        missing.append("fixed_zip_inspection=accepted")
    else:
        recorded_path = evidence.get("fixed_release_zip_path")
        if not isinstance(recorded_path, str) or not recorded_path.strip():
            missing.append("fixed_release_zip_path=recorded")
        else:
            recorded_name = recorded_path.replace("\\", "/").rstrip("/").split("/")[-1]
            if recorded_name != inspection.release_zip_name:
                missing.append("fixed_release_zip_path=inspected-zip-name")
        if evidence.get("fixed_release_zip_name") != inspection.release_zip_name:
            missing.append("fixed_release_zip_name=inspected-zip-name")
        if evidence.get("fixed_release_zip_size_bytes") != inspection.file_size_bytes:
            missing.append("fixed_release_zip_size_bytes=inspected-zip-size")
        if evidence.get("fixed_release_zip_sha256") != inspection.sha256:
            missing.append("fixed_release_zip_sha256=inspected-zip-sha256")

    contract = build_v200_fixed_release_zip_with_web_evidence_contract()
    public_safe = True
    for forbidden in contract.forbidden_success_states:
        if evidence.get(forbidden) is True:
            missing.append(f"forbidden:{forbidden}")
            public_safe = False
    for leak in (
        "raw_screenshots_included",
        "raw_prompts_included",
        "raw_provider_payloads_included",
        "raw_audio_included",
        "raw_google_health_payloads_included",
        "api_keys_included",
        "oauth_tokens_included",
        "authorization_headers_included",
        "private_paths_included",
        "raw_lan_ips_included",
    ):
        if evidence.get(leak) is True:
            missing.append(f"leak:{leak}")
            public_safe = False
    return V200FixedReleaseZipWithWebEvidenceValidation(
        status="accepted" if not missing and public_safe else "rejected",
        missing_markers=tuple(missing),
        public_safe=public_safe,
    )
