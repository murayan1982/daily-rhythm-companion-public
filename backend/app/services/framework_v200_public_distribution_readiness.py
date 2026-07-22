"""Public-distribution readiness checks for Daily Rhythm Companion v2.0.0.

The checks operate on an already selected public source surface. They do not
publish a repository, create tags, build a zip, call providers, read ignored
operator evidence, or access the network.
"""

from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import json
from pathlib import PurePosixPath
import re
from typing import Mapping


PUBLIC_DESCRIPTION = (
    "A lightweight daily rhythm companion and public demo application "
    "for AI Character Framework."
)


@dataclass(frozen=True)
class V200PublicDistributionReadinessContract:
    """Static Public-P2 source/package contract."""

    status: str
    requirement_key: str
    required_files: tuple[str, ...]
    forbidden_exact_paths: tuple[str, ...]
    forbidden_path_prefixes: tuple[str, ...]
    forbidden_path_segments: tuple[str, ...]
    forbidden_suffixes: tuple[str, ...]
    public_safe_omissions: tuple[str, ...]
    public_export_excluded_exact_paths: tuple[str, ...]
    public_export_excluded_path_prefixes: tuple[str, ...]
    public_export_excluded_patterns: tuple[str, ...]
    public_export_excluded_suffixes: tuple[str, ...]
    deferred_cleanup_groups: tuple[str, ...]
    next_focus: str


@dataclass(frozen=True)
class V200PublicDistributionInspection:
    """Inspection result for a tracked source surface or fixed zip."""

    status: str
    surface_kind: str
    inspected_file_count: int
    required_files_present: bool
    metadata_aligned: bool
    public_safe: bool
    missing_files: tuple[str, ...]
    forbidden_files: tuple[str, ...]
    metadata_errors: tuple[str, ...]
    sensitive_content_findings: tuple[str, ...]
    deferred_cleanup_groups: tuple[str, ...]


REQUIRED_FILES = (
    "LICENSE",
    "README.md",
    "roadmap.md",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "app/web/index.html",
    "app/web/manifest.json",
    "backend/.env.example",
    "backend/env_profiles/mock_safe.env",
    "docs/DRC_v200_goal_checklist_small_commit.md",
    "docs/quickstart_local.md",
    "docs/quickstart_smartphone_web.md",
    "docs/v200_final_release_artifact_record.md",
    "docs/v200_public_distribution_readiness.md",
    "docs/v200_public_repository_migration.md",
    "docs/v200_public_snapshot_file_retention.md",
    "release_notes/v2.0.0.md",
    "scripts/check_release_package.py",
    "scripts/smoke_framework_v200_public_distribution_readiness.py",
    "backend/app/services/framework_v200_public_distribution_readiness.py",
    "backend/app/services/framework_v200_public_snapshot_export.py",
    "docs/v200_public_snapshot_export.md",
    "scripts/export_v200_public_snapshot_from_head.py",
    "scripts/smoke_framework_v200_public_snapshot_export.py",
    "build_release.bat",
    "build_v200_final_fixed_release_zip_from_head.ps1",
)


GENERATED_FLUTTER_REGISTRANT_PATHS = (
    "app/android/app/src/main/java/io/flutter/plugins/GeneratedPluginRegistrant.java",
    "app/ios/Runner/GeneratedPluginRegistrant.h",
    "app/ios/Runner/GeneratedPluginRegistrant.m",
    "app/linux/flutter/generated_plugin_registrant.cc",
    "app/linux/flutter/generated_plugin_registrant.h",
    "app/linux/flutter/generated_plugins.cmake",
    "app/windows/flutter/generated_plugin_registrant.cc",
    "app/windows/flutter/generated_plugin_registrant.h",
    "app/windows/flutter/generated_plugins.cmake",
)

FORBIDDEN_EXACT_PATHS = (
    "DRC_v200_goal_checklist_small_commit.md",
    "docs/archive/README.md",
    "scripts/archive/README.md",
    "scripts/check_env_profile_v041.py",
    "scripts/cleanup_scripts_v030_day5.py",
    "docs/v0.30.0_release_notes.md",
    "docs/v1100_release_foundation.md",
    "scripts/check_v025_release_readiness.py",
    "scripts/check_v030_framework_integration_foundation.py",
    "docs/release_notes_v1.9.0.md",
    "backend/app/services/framework_v190_release_readiness.py",
    "backend/app/services/framework_v190_release_package_candidate.py",
    "backend/app/services/framework_v190_fixed_release_zip_evidence.py",
    "backend/app/services/framework_v190_release_finalization.py",
    "docs/framework_v190_release_readiness.md",
    "docs/framework_v190_release_package_candidate.md",
    "docs/framework_v190_fixed_release_zip_evidence.md",
    "docs/framework_v190_release_finalization.md",
    "docs/release_cleanup_policy.md",
    "scripts/smoke_framework_v190_release_readiness.py",
    "scripts/smoke_framework_v190_release_package_candidate.py",
    "scripts/smoke_framework_v190_fixed_release_zip_evidence.py",
    "scripts/smoke_framework_v190_release_finalization.py",
    "scripts/check_v190_release_package_candidate.py",
    "scripts/check_v190_release_surface_cleanup.py",
    "scripts/cleanup_v190_release_dev_artifacts.py",
    "backend/app/services/public_repo_v200_readiness.py",
    "backend/app/services/v200_release_requirements_final_gate.py",
    "backend/app/services/framework_v200_fixed_release_candidate_zip_verification.py",
    "backend/app/services/framework_v200_final_release_readiness.py",
    "docs/v200_public_repo_readiness.md",
    "docs/v200_release_requirements_final_gate.md",
    "docs/v200_fixed_release_candidate_zip_verification.md",
    "docs/v200_final_release_readiness.md",
    "scripts/smoke_v200_public_repo_readiness.py",
    "scripts/smoke_v200_release_requirements_final_gate.py",
    "scripts/smoke_framework_v200_fixed_release_candidate_zip_verification.py",
    "scripts/smoke_framework_v200_final_release_readiness.py",
    "docs/operator_evidence_templates/v200_fixed_release_candidate_zip_day71.example.json",
    "docs/operator_evidence_templates/v200_final_release_readiness_day72.example.json",
    "backend/app/services/framework_v200_real_tts_web_audio_actual_run_checkpoint.py",
    "backend/app/services/framework_v200_real_tts_web_audio_evidence_authoring_handoff.py",
    "backend/app/services/framework_v200_real_tts_web_audio_local_preflight_checkpoint.py",
    "backend/app/services/framework_v200_real_tts_web_audio_operator_runbook.py",
    "backend/app/services/framework_v200_real_tts_web_audio_preflight.py",
    "backend/app/services/framework_v200_real_tts_web_audio_preflight_execution_handoff.py",
    "backend/app/services/framework_v200_real_tts_web_audio_run_validation_flow.py",
    "docs/v200_real_tts_web_audio_operator_runbook.md",
    "scripts/smoke_framework_v200_real_tts_web_audio_actual_run_checkpoint.py",
    "scripts/smoke_framework_v200_real_tts_web_audio_evidence_authoring_handoff.py",
    "scripts/smoke_framework_v200_real_tts_web_audio_local_preflight_checkpoint.py",
    "scripts/smoke_framework_v200_real_tts_web_audio_operator_runbook.py",
    "scripts/smoke_framework_v200_real_tts_web_audio_preflight.py",
    "scripts/smoke_framework_v200_real_tts_web_audio_preflight_execution_handoff.py",
    "scripts/smoke_framework_v200_real_tts_web_audio_run_validation_flow.py",
    "backend/app/services/framework_v200_web_execution_screenshot_collection.py",
    "backend/app/services/framework_v200_private_web_evidence_manifest_validation.py",
    "docs/v200_web_execution_screenshot_evidence_collection.md",
    "docs/v200_private_web_evidence_manifest_validation.md",
    "scripts/smoke_framework_v200_web_execution_screenshot_collection.py",
    "scripts/smoke_framework_v200_private_web_evidence_manifest_validation.py",
    "scripts/check_v200_web_execution_screenshot_collection_day74.py",
    "scripts/check_v200_private_web_evidence_manifest_day75.py",
    "docs/operator_evidence_templates/v200_web_execution_screenshot_collection_day74.example.json",
    "docs/operator_evidence_templates/v200_private_web_evidence_manifest_day75.example.json",
    *GENERATED_FLUTTER_REGISTRANT_PATHS,
)

FORBIDDEN_PATH_PREFIXES = (
    ".git/",
    ".venv/",
    "release/",
    "docs/internal/",
    "operator_evidence/",
    "private_operator_evidence/",
    "repo_files/",
    "optional_replacements/",
    "_local/",
    ".release_build/",
    "app/build/",
    "app/.dart_tool/",
    "backend/local_data/",
)

FORBIDDEN_PATH_SEGMENTS = (
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
)

FORBIDDEN_SUFFIXES = (
    ".patch",
    ".diff",
    ".bak",
    ".tmp",
    ".log",
    ".zip",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".pyc",
    ".pyo",
)


# Private-repository files that are intentionally omitted from the clean Public
# source snapshot. Source mode validates this export view rather than pretending
# that the full Private development repository is itself the Public repository.
PUBLIC_EXPORT_EXCLUDED_EXACT_PATHS = (
    "DailyRhythmCompanion_handoff_v0_15_0.md",
    "release_final_check_v0_16_0_day4.md",
    "release_package_check_result_v0_16_0_day3.md",
    "public_release_checklist.md",
    "DRC_v190_Day22_handoff.md",
    "DRC_v190_next_thread_prompt.md",
    "DRC_v200_goal_checklist_small_commit_CommitC_ACCEPTED.md",
    "README_B0_APPLY.md",
    "PATCH_SUMMARY.md",
    "VERIFICATION_SUMMARY.txt",
    "IMPLEMENTATION_NOTES.txt",
    "LOCAL_VALIDATION_RESULT.txt",
    "README_LOCAL_ONLY.txt",
)

PUBLIC_EXPORT_EXCLUDED_PATH_PREFIXES = (
    "docs/internal/",
    "operator_evidence/",
    "private_operator_evidence/",
    "repo_files/",
    "optional_replacements/",
    "_local/",
    ".release_build/",
    "release/",
    "app/build/",
    "app/.dart_tool/",
    "backend/local_data/",
)

PUBLIC_EXPORT_EXCLUDED_PATTERNS = (
    "CHANGE_SUMMARY*",
    "day*_validation.txt",
    "DAY*.md",
    "DOC_UPDATE_BUNDLE*.md",
    "README_v*_day*.md",
    "scripts/check_v*_day*.py",
    "scripts/check_env_profile_v*_day*.py",
    "scripts/check_v190_smartphone_web_fw_demo_day*.py",
    "*handoff*.md",
    "*next_thread_prompt*.md",
)

PUBLIC_EXPORT_EXCLUDED_SUFFIXES = (
    ".patch",
    ".diff",
    ".bak",
    ".tmp",
    ".log",
    ".zip",
    ".sqlite",
    ".sqlite3",
    ".db",
)

SENSITIVE_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "private-windows-user-path",
        re.compile(r"\b[A-Za-z]:[\\/]Users[\\/][^\\/\r\n]+", re.IGNORECASE),
    ),
    (
        "private-lan-ip",
        re.compile(
            r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[0-1])\.\d+\.\d+)\b"
        ),
    ),
)

TEXT_SUFFIXES = {
    ".bat", ".css", ".dart", ".env", ".gradle", ".html", ".json",
    ".kt", ".kts", ".md", ".plist", ".properties", ".ps1", ".py",
    ".swift", ".toml", ".txt", ".xcconfig", ".xml", ".yaml", ".yml",
}

SAFE_SECRET_PLACEHOLDERS = {
    "", "0", "false", "none", "null", "disabled", "placeholder",
    "replace_me", "replace-me", "changeme", "change-me", "example",
}

SENSITIVE_ENV_KEY_FRAGMENTS = (
    "API_KEY", "CLIENT_SECRET", "PRIVATE_KEY", "PASSWORD", "SECRET",
    "ACCESS_TOKEN", "REFRESH_TOKEN", "AUTHORIZATION",
)


def build_v200_public_distribution_readiness_contract() -> V200PublicDistributionReadinessContract:
    """Build the Public-P2 contract without inspecting files."""

    return V200PublicDistributionReadinessContract(
        status="public-distribution-validator-ready",
        requirement_key="v200_public_distribution_readiness",
        required_files=REQUIRED_FILES,
        forbidden_exact_paths=FORBIDDEN_EXACT_PATHS,
        forbidden_path_prefixes=FORBIDDEN_PATH_PREFIXES,
        forbidden_path_segments=FORBIDDEN_PATH_SEGMENTS,
        forbidden_suffixes=FORBIDDEN_SUFFIXES,
        public_safe_omissions=(
            "private_git_history", "private_refs_and_tags", "operator_evidence",
            "raw_screenshots", "raw_audio", "raw_health_data",
            "raw_provider_payloads", "api_keys", "oauth_tokens",
            "authorization_headers", "private_absolute_paths", "raw_lan_ips",
            "local_env_files", "build_cache_output",
            "patch_diff_temp_backup_files", "superseded_private_candidate_zip",
            "untracked_flutter_generated_registrants",
        ),
        public_export_excluded_exact_paths=PUBLIC_EXPORT_EXCLUDED_EXACT_PATHS,
        public_export_excluded_path_prefixes=PUBLIC_EXPORT_EXCLUDED_PATH_PREFIXES,
        public_export_excluded_patterns=PUBLIC_EXPORT_EXCLUDED_PATTERNS,
        public_export_excluded_suffixes=PUBLIC_EXPORT_EXCLUDED_SUFFIXES,
        deferred_cleanup_groups=(),
        next_focus=(
            "Resolve final Public pre-build gate issues, commit and push the final Public source, "
            "verify a clean Public main, freeze source, build one fixed ZIP, and run Day81, "
            "Day82, and Day83 against that same artifact."
        ),
    )


def _normalize_path(path: str) -> str:
    normalized = str(PurePosixPath(path.replace("\\", "/")))
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_v200_private_repository_export_excluded(path: str) -> bool:
    """Return True when a Private-repository path is omitted from Public export."""

    normalized = _normalize_path(path)
    lower = normalized.lower()
    if normalized in PUBLIC_EXPORT_EXCLUDED_EXACT_PATHS:
        return True
    if any(lower.startswith(prefix.lower()) for prefix in PUBLIC_EXPORT_EXCLUDED_PATH_PREFIXES):
        return True
    if any(lower.endswith(suffix.lower()) for suffix in PUBLIC_EXPORT_EXCLUDED_SUFFIXES):
        return True
    return any(
        fnmatch.fnmatch(normalized.lower(), pattern.lower())
        for pattern in PUBLIC_EXPORT_EXCLUDED_PATTERNS
    )


def _is_text_path(path: str) -> bool:
    pure = PurePosixPath(path)
    lower_name = pure.name.lower()
    return (
        pure.suffix.lower() in TEXT_SUFFIXES
        or pure.name in {".gitignore", "gradlew", "LICENSE"}
        or lower_name.endswith(".env")
        or ".env." in lower_name
    )


def _decode_text(path: str, data: bytes, errors: list[str]) -> str | None:
    if not _is_text_path(path):
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        errors.append(f"{path}:not-valid-utf8")
        return None


def _is_safe_placeholder(value: str) -> bool:
    normalized = value.strip().strip('"').strip("'")
    lower = normalized.lower()
    return (
        lower in SAFE_SECRET_PLACEHOLDERS
        or (normalized.startswith("<") and normalized.endswith(">"))
        or (normalized.startswith("${") and normalized.endswith("}"))
        or (normalized.startswith("%") and normalized.endswith("%"))
        or (bool(normalized) and set(normalized) <= {"*"})
        or lower.startswith("your_")
        or lower.startswith("your-")
    )


def _scan_env_assignments(path: str, text: str, findings: list[str]) -> None:
    lower_name = PurePosixPath(path).name.lower()
    if not (lower_name.endswith(".env") or ".env." in lower_name):
        return

    assignment = re.compile(
        r"^\s*(?:export\s+|\$env:)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$"
    )
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        match = assignment.match(raw_line)
        if not match:
            continue
        key, raw_value = match.groups()
        upper_key = key.upper()
        if not any(fragment in upper_key for fragment in SENSITIVE_ENV_KEY_FRAGMENTS):
            continue
        value = raw_value.split(" #", 1)[0].strip()
        if not _is_safe_placeholder(value):
            findings.append(f"{path}:{line_number}:non-placeholder-sensitive-assignment:{key}")


def _scan_sensitive_content(path: str, text: str, findings: list[str]) -> None:
    sanitized = (
        text.replace("http://<PC_LAN_IP>:8000", "")
        .replace("http://<PC_LAN_IP>:18080", "")
        .replace("<PC_LAN_IP>", "")
    )
    for label, pattern in SENSITIVE_PATTERNS:
        if pattern.search(sanitized):
            findings.append(f"{path}:{label}")
    _scan_env_assignments(path, text, findings)


def _metadata_errors(files: Mapping[str, bytes], text_cache: Mapping[str, str]) -> list[str]:
    errors: list[str] = []

    pubspec = text_cache.get("app/pubspec.yaml", "")
    if "version: 2.0.0+1" not in pubspec:
        errors.append("app/pubspec.yaml:version-must-be-2.0.0+1")
    if 'description: "Flutter frontend for Daily Rhythm Companion."' not in pubspec:
        errors.append("app/pubspec.yaml:description-not-aligned")

    manifest_text = text_cache.get("app/web/manifest.json", "")
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        manifest = None
        errors.append("app/web/manifest.json:invalid-json")
    if isinstance(manifest, dict):
        if manifest.get("name") != "Daily Rhythm Companion":
            errors.append("app/web/manifest.json:name-not-aligned")
        if manifest.get("short_name") != "DRC":
            errors.append("app/web/manifest.json:short-name-not-aligned")
        if manifest.get("description") != PUBLIC_DESCRIPTION:
            errors.append("app/web/manifest.json:description-not-aligned")

    index = text_cache.get("app/web/index.html", "")
    for marker, error in (
        ("<title>Daily Rhythm Companion</title>", "app/web/index.html:title-not-aligned"),
        ('content="Daily Rhythm Companion"', "app/web/index.html:apple-title-not-aligned"),
        (f'<meta name="description" content="{PUBLIC_DESCRIPTION}">', "app/web/index.html:description-not-aligned"),
    ):
        if marker not in index:
            errors.append(error)

    readme = text_cache.get("README.md", "")
    for marker, error in (
        ("Current target: v2.0.0 clean-history Public repository preparation (**NOT RELEASED**)", "README.md:public-preparation-status-missing"),
        ("docs/DRC_v200_goal_checklist_small_commit.md", "README.md:checklist-source-missing"),
        ("The superseded Private candidate zip and Private tag are not Public release assets.", "README.md:private-candidate-boundary-missing"),
    ):
        if marker not in readme:
            errors.append(error)

    checklist = text_cache.get("docs/DRC_v200_goal_checklist_small_commit.md", "")
    if "Status: **NOT RELEASED**" not in checklist:
        errors.append("docs/DRC_v200_goal_checklist_small_commit.md:status-not-safe")
    if "This checklist is the source of truth" not in checklist:
        errors.append("docs/DRC_v200_goal_checklist_small_commit.md:not-source-of-truth")

    migration = text_cache.get("docs/v200_public_repository_migration.md", "")
    if "Status: **IN PROGRESS**" not in migration:
        errors.append("docs/v200_public_repository_migration.md:status-not-in-progress")
    if "public_release_use: superseded-do-not-publish" not in migration:
        errors.append("docs/v200_public_repository_migration.md:old-zip-boundary-missing")

    release_notes = text_cache.get("release_notes/v2.0.0.md", "")
    if "Release type: clean-history Public demo source release" not in release_notes:
        errors.append("release_notes/v2.0.0.md:release-type-missing")
    if "Its presence does not by itself mean that the GitHub Release has been published." not in release_notes:
        errors.append("release_notes/v2.0.0.md:publication-boundary-missing")

    if "MIT License" not in text_cache.get("LICENSE", ""):
        errors.append("LICENSE:not-mit-license")
    if "DRC_v200_goal_checklist_small_commit.md" in files:
        errors.append("root-duplicate-checklist-present")

    return errors


def inspect_v200_public_distribution_files(
    files: Mapping[str, bytes], *, surface_kind: str
) -> V200PublicDistributionInspection:
    """Inspect normalized repository-relative file bytes."""

    normalized_files = {_normalize_path(path): data for path, data in files.items()}
    names = set(normalized_files)

    missing = sorted(path for path in REQUIRED_FILES if path not in names)
    forbidden_exact_paths_lower = {path.lower() for path in FORBIDDEN_EXACT_PATHS}
    forbidden: list[str] = []
    for path in sorted(names):
        lower = path.lower()
        if lower in forbidden_exact_paths_lower:
            forbidden.append(path)
            continue
        if any(lower.startswith(prefix.lower()) for prefix in FORBIDDEN_PATH_PREFIXES):
            forbidden.append(path)
            continue
        path_segments = {part.lower() for part in PurePosixPath(path).parts}
        if any(segment.lower() in path_segments for segment in FORBIDDEN_PATH_SEGMENTS):
            forbidden.append(path)
            continue
        if any(lower.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            forbidden.append(path)
            continue
        basename = PurePosixPath(path).name.lower()
        if basename == ".env" or (
            basename.startswith(".env.")
            and basename not in {".env.example", ".env.sample", ".env.template"}
        ):
            forbidden.append(path)

    text_errors: list[str] = []
    text_cache: dict[str, str] = {}
    sensitive_findings: list[str] = []
    for path, data in normalized_files.items():
        text = _decode_text(path, data, text_errors)
        if text is None:
            continue
        text_cache[path] = text
        _scan_sensitive_content(path, text, sensitive_findings)

    metadata = _metadata_errors(normalized_files, text_cache)
    metadata.extend(text_errors)

    status = "accepted" if not missing and not forbidden and not metadata and not sensitive_findings else "rejected"
    contract = build_v200_public_distribution_readiness_contract()
    return V200PublicDistributionInspection(
        status=status,
        surface_kind=surface_kind,
        inspected_file_count=len(normalized_files),
        required_files_present=not missing,
        metadata_aligned=not metadata,
        public_safe=not forbidden and not sensitive_findings,
        missing_files=tuple(missing),
        forbidden_files=tuple(forbidden),
        metadata_errors=tuple(metadata),
        sensitive_content_findings=tuple(sorted(set(sensitive_findings))),
        deferred_cleanup_groups=contract.deferred_cleanup_groups,
    )


def render_v200_public_distribution_readiness_contract(contract: V200PublicDistributionReadinessContract) -> str:
    return "\n".join((
        f"v200_public_distribution_readiness_status: {contract.status}",
        f"v200_public_distribution_readiness_requirement_key: {contract.requirement_key}",
        "v200_public_distribution_readiness_required_files: " + ",".join(contract.required_files),
        "v200_public_distribution_readiness_forbidden_exact_paths: " + ",".join(contract.forbidden_exact_paths),
        "v200_public_distribution_readiness_forbidden_path_prefixes: " + ",".join(contract.forbidden_path_prefixes),
        "v200_public_distribution_readiness_forbidden_path_segments: " + ",".join(contract.forbidden_path_segments),
        "v200_public_distribution_readiness_forbidden_suffixes: " + ",".join(contract.forbidden_suffixes),
        "v200_public_distribution_readiness_public_safe_omissions: " + ",".join(contract.public_safe_omissions),
        "v200_public_distribution_readiness_public_export_excluded_exact_paths: " + ",".join(contract.public_export_excluded_exact_paths),
        "v200_public_distribution_readiness_public_export_excluded_path_prefixes: " + ",".join(contract.public_export_excluded_path_prefixes),
        "v200_public_distribution_readiness_public_export_excluded_patterns: " + ",".join(contract.public_export_excluded_patterns),
        "v200_public_distribution_readiness_public_export_excluded_suffixes: " + ",".join(contract.public_export_excluded_suffixes),
        "v200_public_distribution_readiness_deferred_cleanup_groups: " + ",".join(contract.deferred_cleanup_groups),
        "v200_public_distribution_readiness_creates_zip: False",
        "v200_public_distribution_readiness_publishes_repository: False",
        "v200_public_distribution_readiness_creates_or_moves_tags: False",
        f"v200_public_distribution_readiness_next_focus: {contract.next_focus}",
    ))


def render_v200_public_distribution_inspection(inspection: V200PublicDistributionInspection) -> str:
    return "\n".join((
        f"v200_public_distribution_inspection_status: {inspection.status}",
        f"v200_public_distribution_inspection_surface_kind: {inspection.surface_kind}",
        f"v200_public_distribution_inspection_file_count: {inspection.inspected_file_count}",
        f"v200_public_distribution_inspection_required_files_present: {inspection.required_files_present}",
        f"v200_public_distribution_inspection_metadata_aligned: {inspection.metadata_aligned}",
        f"v200_public_distribution_inspection_public_safe: {inspection.public_safe}",
        "v200_public_distribution_inspection_missing_files: " + ",".join(inspection.missing_files),
        "v200_public_distribution_inspection_forbidden_files: " + ",".join(inspection.forbidden_files),
        "v200_public_distribution_inspection_metadata_errors: " + ",".join(inspection.metadata_errors),
        "v200_public_distribution_inspection_sensitive_content_findings: " + ",".join(inspection.sensitive_content_findings),
        "v200_public_distribution_inspection_deferred_cleanup_groups: " + ",".join(inspection.deferred_cleanup_groups),
    ))
