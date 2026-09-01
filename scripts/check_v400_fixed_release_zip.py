#!/usr/bin/env python3
"""DRC v4.0.0 Control D fixed-ZIP tooling gate.

Default mode validates the exact Stage 1 tooling candidate without network,
credentials, Flutter execution, builder invocation, or artifact creation.
Future ``--source-tree`` and ``--release-zip`` modes are wired for the accepted
contract, but the artifact path remains blocked until a later authorization
marker is committed.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from hashlib import sha256
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "4cae15573f3332cbc476557461babdfe2eb3c0bf"
EXPECTED_BACKEND_VERSION = "4.0.0"
EXPECTED_FLUTTER_VERSION = "4.0.0+5"
EXPECTED_BACKEND_TESTS = 479
EXPECTED_FLUTTER_TESTS = 570
EXPECTED_TAG = "DRC_v4.0.0"
OFFICIAL_ORIGIN = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)"
    r"murayan1982/daily-rhythm-companion-public(?:\.git)?$"
)
ZIP_PATTERN = re.compile(r"^DailyRhythmCompanion_v4\.0\.0_\d{8}_\d{6}\.zip$")
STAGE2_AUTHORIZATION = "AUTHORIZED_FOR_CLEAN_COMMITTED_SOURCE_PREFLIGHT"
STAGE3_AUTHORIZATION = "AUTHORIZED_FOR_ONE_TIME_BUILD"
STAGE4_AUTHORIZATION = "AUTHORIZED_FOR_SAME_ARTIFACT_VERIFICATION"
STAGE2_ACCEPTED = "Control D Stage 2:\nCLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"
STAGE3_ARTIFACT_READY = "Control D Stage 3:\nBUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"
EXPECTED_MODIFIED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_record.md",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
EXPECTED_ADDED = {
    "docs/v400_fixed_release_zip.md",
    "build_v400_fixed_release_zip_from_head.ps1",
    "scripts/check_v400_fixed_release_zip.py",
}
STAGE1_SURFACE = EXPECTED_MODIFIED | EXPECTED_ADDED
COORDINATION_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
)
CURRENT_DOCS = (
    *COORDINATION_DOCS,
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_release_record.md",
    "docs/v400_fixed_release_zip.md",
)
PROTECTED_PATHS = (
    "build_release.bat",
    "scripts/check_release_package.py",
    "release_notes/v4.0.0.md",
    "backend",
    "app",
)
PRIVATE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)\b[a-z]:\\users\\"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[0-1])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)
FORBIDDEN_PACKAGE_NAMES = {
    ".env",
    "credentials.json",
    "google_health_tokens.json",
    "fitbit_tokens.json",
    "token.json",
}
FORBIDDEN_PACKAGE_PARTS = {
    ".git",
    "release",
    "build",
    "operator_evidence",
    "local_data",
    "vendor",
}
EXPECTED_FLUTTER_IDENTITY = {
    "frameworkVersion": "3.41.7",
    "channel": "stable",
    "frameworkRevision": "cc0734ac716fbb8b90f3f9db8020958b1553afa7",
    "dartSdkVersion": "3.11.5",
}
REQUIRED_PACKAGE_FILES = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "scripts/check_release_package.py",
    "scripts/check_v400_fixed_release_zip.py",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_fixed_release_zip.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_record.md",
    "release_notes/v4.0.0.md",
    "backend/app/version.py",
    "app/pubspec.yaml",
    "backend/tests/test_v300_rt8_private_operator_manifest.py",
    "scripts/check_v300_rt4f4_configured_local_stream_acceptance.py",
}
KNOWN_RELEASE_SCAN_FIXTURES = {
    "backend/tests/test_v300_rt8_private_operator_manifest.py": (
        "private Windows user path",
        b"test_sensitive_looking_values_are_rejected",
    ),
    "scripts/check_v300_rt4f4_configured_local_stream_acceptance.py": (
        "private LAN IP literal",
        b"assert_scanner_self_checks",
    ),
}


@dataclass(frozen=True)
class ModePolicy:
    name: str
    artifact_policy: str
    stage1_current_doc_checks_required: bool
    source_tree_verification_required: bool
    release_zip_verification_required: bool
    blocked_authorization_check_required: bool


DEFAULT_MODE_POLICY = ModePolicy(
    name="default",
    artifact_policy="artifact-absent",
    stage1_current_doc_checks_required=True,
    source_tree_verification_required=False,
    release_zip_verification_required=False,
    blocked_authorization_check_required=True,
)
SOURCE_TREE_MODE_POLICY = ModePolicy(
    name="source-tree",
    artifact_policy="artifact-absent",
    stage1_current_doc_checks_required=False,
    source_tree_verification_required=True,
    release_zip_verification_required=False,
    blocked_authorization_check_required=False,
)
RELEASE_ZIP_MODE_POLICY = ModePolicy(
    name="release-zip",
    artifact_policy="exact-supplied-artifact",
    stage1_current_doc_checks_required=False,
    source_tree_verification_required=False,
    release_zip_verification_required=True,
    blocked_authorization_check_required=False,
)


def die(message: str) -> None:
    raise AssertionError(message)


def git_out(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        die(completed.stderr.strip() or "git failed: " + " ".join(args))
    return completed.stdout.strip()


def read(relative: str, root: Path = ROOT) -> str:
    path = root / relative
    if not path.is_file():
        die(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("`", "").replace("*", "")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        die(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        die(f"Unexpected {label}: {needle!r}")


def require_associated(text: str, label: str, value: str, scope: str) -> None:
    pattern = rf"{re.escape(label)}\s*:?\s*\n?\s*{re.escape(value)}"
    if not re.search(pattern, norm(text), flags=re.IGNORECASE):
        die(f"Missing associated {scope}: {label} -> {value}")


def status_entries() -> list[tuple[str, str]]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    entries: list[tuple[str, str]] = []
    for part in raw.decode("utf-8").split("\0"):
        if part:
            entries.append((part[:2], part[3:].replace("\\", "/")))
    return entries


def check_dirty_surface(entries: list[tuple[str, str]]) -> None:
    modified: set[str] = set()
    added: set[str] = set()
    deleted: set[str] = set()
    other: list[tuple[str, str]] = []
    for status, path in entries:
        if status == " M":
            modified.add(path)
        elif status == "??":
            added.add(path)
        elif "D" in status:
            deleted.add(path)
        else:
            other.append((status, path))
    if modified != EXPECTED_MODIFIED:
        die(f"Unexpected modified surface: {sorted(modified)}")
    if added != EXPECTED_ADDED:
        die(f"Unexpected added surface: {sorted(added)}")
    if deleted:
        die(f"Unexpected deleted files: {sorted(deleted)}")
    if other:
        die(f"Unexpected status entries: {other!r}")


def determine_mode() -> str:
    if git_out("branch", "--show-current") != "main":
        die("branch must be main")
    entries = status_entries()
    if entries:
        if git_out("rev-parse", "HEAD") != BASELINE:
            die("dirty candidate HEAD mismatch")
        if git_out("rev-parse", "origin/main") != BASELINE:
            die("dirty candidate origin/main mismatch")
        check_dirty_surface(entries)
        return "DIRTY_STAGE1_CANDIDATE"
    subprocess.run(["git", "merge-base", "--is-ancestor", BASELINE, "HEAD"], cwd=ROOT, check=True)
    return "CLEAN_COMMITTED_TOOLING"


def check_versions() -> None:
    require(read("backend/app/version.py"), 'APP_VERSION = "4.0.0"', "Backend version")
    require(read("app/pubspec.yaml"), "version: 4.0.0+5", "Flutter version")
    require(read("scripts/check_v20x_application_version_metadata.py"), '"4.0.0": "5"', "version mapping")


def check_stage1_current_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current small commit", "DRC v4.0.0 Release Preparation Protocol Control D Stage 1"),
            ("current implementation", "DRC v4.0.0 Release Preparation Protocol Control D Stage 1"),
            ("current implementation state", "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control C implementation commit", BASELINE),
            ("Control D Stage 1 baseline", BASELINE),
            ("Control D", "CURRENT / NOT_COMPLETED"),
            ("Control D Stage 1", "FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED"),
            ("Control D Stage 3", "BUILD_EXACTLY_ONCE / BLOCKED_PENDING_STAGE2_ACCEPTANCE / NOT_AUTHORIZED"),
            ("Control D Stage 4", "SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / BLOCKED_PENDING_STAGE3_ARTIFACT / NOT_AUTHORIZED"),
            ("Control E", "FUTURE / NOT_AUTHORIZED"),
            ("DRC v4.0.0", "NOT_RELEASED"),
            ("fixed ZIP builder invocation count", "0"),
            ("fixed ZIP", "NOT_BUILT"),
            ("annotated tag", "NOT_CREATED"),
            ("GitHub Release", "NOT_CREATED"),
        ):
            require_associated(text, label, value, relative)

    protocol = read("docs/v400_release_preparation_protocol.md")
    for needle in (
        "## Control D Boundary",
        "Stage 1 implements",
        "build_v400_fixed_release_zip_from_head.ps1",
        "scripts/check_v400_fixed_release_zip.py",
        "13 files / M10 A3 D0",
    ):
        require(protocol, needle, "protocol")

    contract = read("docs/v400_fixed_release_zip.md")
    for needle in (
        "credential-free, provider-free, private-evidence-free",
        "builder invocation count:\n0",
        "fixed ZIP basename:\nNOT_BUILT",
        "release source HEAD:\nNOT_RECORDED",
        "verification HEAD:\nNOT_RECORDED",
        "fixed ZIP SHA-256:\nNOT_RECORDED",
        "AI Character Framework is not bundled.",
        "## Stage 1 Stop Rule",
    ):
        require(contract, needle, "fixed ZIP contract")
    for token in (STAGE2_AUTHORIZATION, STAGE3_AUTHORIZATION, STAGE4_AUTHORIZATION):
        reject(protocol, token, "current documentation authorization token")
        reject(contract, token, "current documentation authorization token")

    record = read("docs/v400_release_record.md")
    for label, value in (
        ("Status", "PREPARED / NOT_RELEASED"),
        ("release source HEAD", "NOT_RECORDED"),
        ("verification HEAD", "NOT_RECORDED"),
        ("fixed ZIP basename", "NOT_BUILT"),
        ("fixed ZIP size", "NOT_RECORDED"),
        ("fixed ZIP SHA-256", "NOT_RECORDED"),
        ("fixed ZIP builder invocation count", "0"),
        ("same-artifact verification", "NOT_COMPLETED"),
        ("explicit final operator approval", "NOT_RECEIVED"),
        ("annotated tag publication", "NOT_CREATED"),
        ("GitHub Release publication", "NOT_CREATED"),
    ):
        require_associated(record, label, value, "release record")


def check_builder() -> None:
    text = read("build_v400_fixed_release_zip_from_head.ps1")
    for needle in (
        "[string]$OutputDirectory = \"release\"",
        "[string]$PythonCommand = \"python\"",
        "[string]$FlutterCommand",
        "[switch]$PreflightOnly",
        "Assert-AbsoluteFlutterCommand",
        "DRC_v2.0.0",
        "DRC_v2.0.1",
        "DRC_v2.1.0",
        "DRC_v3.0.0",
        "DRC_v4.0.0",
        "DailyRhythmCompanion_v4.0.0_*.zip",
        "scripts\\check_v400_fixed_release_zip.py",
        "--flutter-command",
        "v400_fixed_release_zip_preflight_build_invocation_count: $buildInvocationCount",
        "Control D Stage 3:",
        "AUTHORIZED_FOR_ONE_TIME_BUILD",
        "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED",
        "git worktree add --detach",
        "build_release.bat release",
        "$buildInvocationCount++",
        "verification_status: not-run",
        "next_action: verify-this-same-zip-without-rebuilding",
    ):
        require(text, needle, "builder")


def check_no_release_outputs() -> None:
    check_release_outputs_absent()


def fixed_zip_paths() -> list[Path]:
    release_root = ROOT / "release"
    if not release_root.exists():
        return []
    return sorted(release_root.glob("DailyRhythmCompanion_v4.0.0_*.zip"))


def check_release_outputs_absent() -> None:
    if git_out("tag", "--list", EXPECTED_TAG):
        die("DRC_v4.0.0 tag exists")
    if fixed_zip_paths():
        die("v4.0.0 fixed ZIP exists")


def check_release_outputs_for_zip(path: Path) -> None:
    if git_out("tag", "--list", EXPECTED_TAG):
        die("DRC_v4.0.0 tag exists")
    release_root = (ROOT / "release").resolve()
    if path.resolve().parent != release_root:
        die("--release-zip must be under repository release/")
    zips = [candidate.resolve() for candidate in fixed_zip_paths()]
    if len(zips) != 1 or zips[0] != path.resolve():
        die("--release-zip requires exactly one matching v4 fixed ZIP in release/")


def check_release_mode_worktree_state(path: Path) -> None:
    allowed = path.resolve().relative_to(ROOT.resolve()).as_posix()
    staged = git_out("diff", "--cached", "--name-status")
    if staged:
        die("--release-zip requires empty Git index")
    entries = status_entries()
    unexpected: list[tuple[str, str]] = []
    for status, entry_path in entries:
        if entry_path == allowed and status == "??":
            continue
        unexpected.append((status, entry_path))
    if unexpected:
        die(f"--release-zip unexpected working tree state: {unexpected!r}")


def check_protected_surface() -> None:
    completed = subprocess.run(
        ["git", "diff", "--exit-code", "--", *PROTECTED_PATHS],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        die("Protected product/build/release surface diff is not empty")


def check_committed_stage1_surface() -> None:
    changed = {
        path.replace("\\", "/")
        for path in git_out("diff", "--name-only", f"{BASELINE}..HEAD").splitlines()
        if path
    }
    if changed and changed != STAGE1_SURFACE:
        die(f"Unexpected committed Stage 1 surface: {sorted(changed)}")
    protected = subprocess.run(
        ["git", "diff", "--exit-code", f"{BASELINE}..HEAD", "--", *PROTECTED_PATHS],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if protected.returncode:
        die("Committed protected product/build/release surface diff is not empty")


ALLOWED_POST_SOURCE_HEAD_SURFACE = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_record.md",
    "docs/v400_fixed_release_zip.md",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
    "scripts/check_v400_fixed_release_zip.py",
}


def validate_post_source_head_surface(
    changed_paths: list[str],
    deleted_paths: list[str],
    rename_or_copy_paths: list[str],
    commit_count: int,
) -> bool:
    if commit_count == 0:
        return not changed_paths and not deleted_paths and not rename_or_copy_paths
    if commit_count > 2:
        return False
    if deleted_paths or rename_or_copy_paths:
        return False
    changed = {path.replace("\\", "/") for path in changed_paths}
    return bool(changed) and changed <= ALLOWED_POST_SOURCE_HEAD_SURFACE


def check_post_source_head_surface(expected_head: str, verification_head: str) -> None:
    commit_count = int(git_out("rev-list", "--count", f"{expected_head}..{verification_head}"))
    name_status = git_out("diff", "--name-status", f"{expected_head}..{verification_head}").splitlines()
    changed: list[str] = []
    deleted: list[str] = []
    rename_or_copy: list[str] = []
    for line in name_status:
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith("D"):
            deleted.append(parts[-1])
        elif status.startswith(("R", "C")):
            rename_or_copy.append(parts[-1])
        else:
            changed.append(parts[-1])
    if not validate_post_source_head_surface(changed, deleted, rename_or_copy, commit_count):
        die("post-source HEAD surface invalidates the fixed ZIP artifact")


def check_source_only_hygiene() -> None:
    tracked = git_out("ls-files").splitlines()
    for relative in tracked:
        path = Path(relative.replace("\\", "/"))
        parts = set(path.parts)
        lower_name = path.name.lower()
        if lower_name in FORBIDDEN_PACKAGE_NAMES:
            die(f"Forbidden tracked package member: {relative}")
        if lower_name.endswith(".zip"):
            die(f"Forbidden tracked ZIP: {relative}")
        if parts & FORBIDDEN_PACKAGE_PARTS:
            die(f"Forbidden tracked package path: {relative}")

    for relative in sorted(EXPECTED_MODIFIED):
        diff = subprocess.check_output(["git", "diff", "--", relative], cwd=ROOT, text=True, errors="replace")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(diff):
                die(f"Private-looking value in candidate diff: {relative}")
    for relative in sorted(EXPECTED_ADDED):
        text = read(relative)
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                die(f"Private-looking value in candidate file: {relative}")


def check_no_contradictions() -> None:
    text = "\n".join(read(relative) for relative in CURRENT_DOCS)
    for needle in (
        "v4.0.0 RELEASED",
        "fixed ZIP: BUILT",
        "annotated tag: CREATED",
        "GitHub Release: CREATED",
        "Control E: AUTHORIZED",
        "fixed ZIP builder invocation count:\n1",
        STAGE2_AUTHORIZATION,
        STAGE3_AUTHORIZATION,
        STAGE4_AUTHORIZATION,
    ):
        reject(text, needle, "current-state contradiction")


def current_docs_text() -> str:
    return "\n".join(read(relative) for relative in CURRENT_DOCS)


def docs_have_stage2_authorization() -> bool:
    text = current_docs_text()
    return STAGE2_AUTHORIZATION in text or STAGE2_ACCEPTED in text


def docs_have_stage3_authorization() -> bool:
    text = current_docs_text()
    return STAGE3_AUTHORIZATION in text and STAGE2_ACCEPTED in text


def docs_have_stage4_authorization() -> bool:
    text = current_docs_text()
    return STAGE4_AUTHORIZATION in text and STAGE3_ARTIFACT_READY in text


def stage2_is_authorized_or_accepted(text: str) -> bool:
    return STAGE2_AUTHORIZATION in text or STAGE2_ACCEPTED in text


def stage3_build_is_authorized(text: str) -> bool:
    return STAGE3_AUTHORIZATION in text and STAGE2_ACCEPTED in text


def stage4_zip_verification_is_authorized(text: str) -> bool:
    return STAGE4_AUTHORIZATION in text and STAGE3_ARTIFACT_READY in text


def check_stage1_blocked_authorizations() -> None:
    if docs_have_stage2_authorization():
        die("Stage 2 is unexpectedly authorized by current docs")
    if docs_have_stage3_authorization():
        die("Stage 3 is unexpectedly authorized by current docs")
    if docs_have_stage4_authorization():
        die("Stage 4 is unexpectedly authorized by current docs")


def check_static_corrective_assertions() -> None:
    current_text = current_docs_text()
    default_policy = mode_policy(False, None)
    source_policy = mode_policy(True, None)
    release_policy = mode_policy(False, Path("release/DailyRhythmCompanion_v4.0.0_20991231_235959.zip"))
    if default_policy.artifact_policy != "artifact-absent":
        die("default mode artifact policy mismatch")
    if source_policy.artifact_policy != "artifact-absent":
        die("source-tree mode artifact policy mismatch")
    if release_policy.artifact_policy != "exact-supplied-artifact":
        die("release-zip mode artifact policy mismatch")
    if not release_zip_skips_absent_artifact_gate(release_policy):
        die("release-zip mode must not use absent-artifact gate")
    if not default_policy.stage1_current_doc_checks_required or not default_policy.blocked_authorization_check_required:
        die("default mode policy missing Stage 1 checks")
    if source_policy.stage1_current_doc_checks_required or source_policy.blocked_authorization_check_required:
        die("source-tree mode policy should not apply Stage 1 current-doc checks")
    if release_policy.stage1_current_doc_checks_required or release_policy.blocked_authorization_check_required:
        die("release-zip mode policy should not apply Stage 1 current-doc checks")
    if stage2_is_authorized_or_accepted(current_text):
        die("current docs unexpectedly authorize Stage 2")
    if stage3_build_is_authorized(current_text):
        die("current docs unexpectedly authorize Stage 3")
    if stage4_zip_verification_is_authorized(current_text):
        die("current docs unexpectedly authorize Stage 4")
    synthetic_stage3 = current_text + "\n" + STAGE2_ACCEPTED + "\n" + STAGE3_AUTHORIZATION
    synthetic_stage4 = current_text + "\n" + STAGE3_ARTIFACT_READY + "\n" + STAGE4_AUTHORIZATION
    if not stage3_build_is_authorized(synthetic_stage3):
        die("synthetic Stage 3 docs cannot reach source-tree/build policy")
    if not stage4_zip_verification_is_authorized(synthetic_stage4):
        die("synthetic Stage 4 docs cannot reach release-zip policy")
    if len(KNOWN_RELEASE_SCAN_FIXTURES) != 2:
        die("known scanner fixture count mismatch")
    if not all(scanner_result_self_check().values()):
        die("scanner result helper self-check failed")
    if not all(fixture_payload_self_check().values()):
        die("fixture payload helper self-check failed")
    if not all(zip_version_identity_self_check().values()):
        die("ZIP version identity self-check failed")
    if flutter_dependency_plan(False, True) != "use-existing-package-config":
        die("repository package config plan mismatch")
    if flutter_dependency_plan(False, False) != "reject-missing-package-config":
        die("repository missing package config must reject")
    if flutter_dependency_plan(True, True) != "use-existing-package-config":
        die("temporary package config plan mismatch")
    if flutter_dependency_plan(True, False) != "pub-get-offline":
        die("temporary missing package config must use offline pub get")
    if not source_diff_guard_rejects_arbitrary_product_change():
        die("source diff guard does not reject arbitrary product change")


def mode_policy(source_tree: bool, release_zip: Path | None) -> ModePolicy:
    if source_tree and release_zip is not None:
        die("--source-tree and --release-zip are mutually exclusive")
    if source_tree:
        return SOURCE_TREE_MODE_POLICY
    if release_zip is not None:
        return RELEASE_ZIP_MODE_POLICY
    return DEFAULT_MODE_POLICY


def release_zip_skips_absent_artifact_gate(policy: ModePolicy) -> bool:
    return policy.artifact_policy == "exact-supplied-artifact"


def flutter_dependency_plan(temporary_extraction: bool, package_config_exists: bool) -> str:
    if package_config_exists:
        return "use-existing-package-config"
    if temporary_extraction:
        return "pub-get-offline"
    return "reject-missing-package-config"


def source_diff_guard_rejects_arbitrary_product_change() -> bool:
    return not validate_post_source_head_surface(["backend/app/version.py"], [], [], 1)


def normalized_source_bytes(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_source_bytes_equal(packaged: bytes, source_blob: bytes) -> bool:
    return normalized_source_bytes(packaged) == normalized_source_bytes(source_blob)


def fixture_payload_is_valid(packaged: bytes, source_blob: bytes, marker: bytes) -> bool:
    return normalized_source_bytes_equal(packaged, source_blob) and marker in packaged


def expected_scanner_findings() -> set[str]:
    return {
        f"- DailyRhythmCompanion/{rel} (text file contains sensitive-looking value: {reason})"
        for rel, (reason, _) in KNOWN_RELEASE_SCAN_FIXTURES.items()
    }


def scanner_findings_are_exact(lines: list[str]) -> bool:
    expected = expected_scanner_findings()
    return (
        len(lines) == 1 + len(expected)
        and lines[0] == "[release-package-check] NG"
        and len(set(lines[1:])) == len(expected)
        and set(lines[1:]) == expected
    )


def scanner_result_is_exact(returncode: int, lines: list[str]) -> bool:
    return returncode == 1 and scanner_findings_are_exact(lines)


def scanner_result_self_check() -> dict[str, bool]:
    expected = sorted(expected_scanner_findings())
    return {
        "known_fixtures_required_file_membership": set(KNOWN_RELEASE_SCAN_FIXTURES).issubset(REQUIRED_PACKAGE_FILES),
        "exit_0_rejected": not scanner_result_is_exact(0, ["[release-package-check] OK"]),
        "exit_2_rejected": not scanner_result_is_exact(2, ["[release-package-check] NG", *expected]),
        "exact_2_accepted": scanner_result_is_exact(1, ["[release-package-check] NG", *expected]),
        "duplicate_rejected": not scanner_result_is_exact(1, ["[release-package-check] NG", expected[0], expected[0]]),
        "missing_rejected": not scanner_result_is_exact(1, ["[release-package-check] NG", expected[0]]),
        "unexpected_rejected": not scanner_result_is_exact(
            1,
            ["[release-package-check] NG", *expected, "- DailyRhythmCompanion/extra.txt (unexpected)"],
        ),
    }


def fixture_payload_self_check() -> dict[str, bool]:
    source = b"line one\nmarker\nline three\n"
    return {
        "lf_source_crlf_packaged_accepted": fixture_payload_is_valid(b"line one\r\nmarker\r\nline three\r\n", source, b"marker"),
        "standalone_cr_normalized_accepted": fixture_payload_is_valid(b"line one\rmarker\rline three\r", source, b"marker"),
        "content_mismatch_rejected": not fixture_payload_is_valid(b"line one\nmarker\nchanged\n", source, b"marker"),
        "marker_missing_rejected": not fixture_payload_is_valid(source, source, b"missing-marker"),
        "marker_present_accepted": fixture_payload_is_valid(source, source, b"marker"),
    }


def backend_version_is_valid(data: bytes) -> bool:
    text = normalized_source_bytes(data).decode("utf-8", errors="replace")
    matches = re.findall(r'^APP_VERSION\s*=\s*"([^"]+)"\s*$', text, flags=re.MULTILINE)
    return matches == [EXPECTED_BACKEND_VERSION]


def flutter_version_is_valid(data: bytes) -> bool:
    text = normalized_source_bytes(data).decode("utf-8", errors="replace")
    matches = re.findall(r"^version:\s*([^\s]+)\s*$", text, flags=re.MULTILINE)
    return matches == [EXPECTED_FLUTTER_VERSION]


def source_matched_version_is_valid(packaged: bytes, source_blob: bytes, version_validator) -> bool:
    return normalized_source_bytes_equal(packaged, source_blob) and version_validator(packaged)


def zip_version_identity_self_check() -> dict[str, bool]:
    backend_good = b'APP_VERSION = "4.0.0"\n'
    backend_bad = b'APP_VERSION = "4.0.1"\n'
    backend_duplicate = b'APP_VERSION = "4.0.0"\nAPP_VERSION = "4.0.0"\n'
    flutter_good = b"name: app\nversion: 4.0.0+5\n"
    flutter_bad = b"name: app\nversion: 4.0.0+6\n"
    flutter_duplicate = b"name: app\nversion: 4.0.0+5\nversion: 4.0.0+5\n"
    return {
        "backend_4_0_0_source_matched_accepted": source_matched_version_is_valid(backend_good, backend_good, backend_version_is_valid),
        "backend_wrong_version_rejected": not source_matched_version_is_valid(backend_bad, backend_bad, backend_version_is_valid),
        "backend_source_mismatch_rejected": not source_matched_version_is_valid(backend_good, backend_bad, backend_version_is_valid),
        "backend_duplicate_declaration_rejected": not source_matched_version_is_valid(
            backend_duplicate,
            backend_duplicate,
            backend_version_is_valid,
        ),
        "flutter_4_0_0_plus_5_source_matched_accepted": source_matched_version_is_valid(
            flutter_good,
            flutter_good,
            flutter_version_is_valid,
        ),
        "flutter_wrong_version_rejected": not source_matched_version_is_valid(flutter_bad, flutter_bad, flutter_version_is_valid),
        "flutter_source_mismatch_rejected": not source_matched_version_is_valid(flutter_good, flutter_bad, flutter_version_is_valid),
        "flutter_duplicate_declaration_rejected": not source_matched_version_is_valid(
            flutter_duplicate,
            flutter_duplicate,
            flutter_version_is_valid,
        ),
    }


def run_checked(cmd: list[str], cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(completed.stdout, end="")
    if completed.returncode:
        die("command failed: " + " ".join(cmd))
    return completed.stdout


def require_absolute_flutter_command(command: str | None) -> str:
    if not command:
        die("--flutter-command is required with --with-flutter")
    path = Path(command)
    if not path.is_absolute():
        die("--flutter-command must be absolute")
    if path.name.lower() in {"flutter", "flutter.bat", "flutter.cmd"} and not re.search(r"[\\/]", command):
        die("bare flutter is forbidden")
    if not path.is_file():
        die("--flutter-command does not exist")
    return str(path)


def check_flutter_identity(command: str) -> None:
    completed = subprocess.run(
        [command, "--version", "--machine"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        die("flutter --version --machine failed")
    data = json.loads(completed.stdout)
    for key, value in EXPECTED_FLUTTER_IDENTITY.items():
        if data.get(key) != value:
            die(f"Unexpected Flutter identity {key}: {data.get(key)!r}")


def prepare_flutter_dependencies(app_dir: Path, command: str, temporary_extraction: bool) -> None:
    package_config = app_dir / ".dart_tool" / "package_config.json"
    plan = flutter_dependency_plan(temporary_extraction, package_config.is_file())
    if plan == "reject-missing-package-config":
        die("Flutter package_config.json is missing in repository source tree")
    if plan == "pub-get-offline":
        run_checked([command, "pub", "get", "--offline"], app_dir)
        if not package_config.is_file():
            die("extracted Flutter package_config.json was not prepared")


def verify_clean_source_tree(with_flutter: bool, with_builds: bool, flutter_command: str | None) -> None:
    if not docs_have_stage2_authorization():
        die("--source-tree is blocked until Control D Stage 2 authorization or accepted state.")
    if git_out("status", "--porcelain", "--untracked-files=all"):
        die("--source-tree requires clean working tree")
    if git_out("branch", "--show-current") != "main":
        die("--source-tree requires main")
    if git_out("rev-parse", "HEAD") != git_out("rev-parse", "origin/main"):
        die("--source-tree requires HEAD == origin/main")
    if not OFFICIAL_ORIGIN.fullmatch(git_out("remote", "get-url", "origin")):
        die("official origin required")
    if not Path("docs/v400_fixed_release_zip.md").is_file():
        die("Control D Stage 1 must be accepted before Stage 2")
    check_no_release_outputs()
    check_committed_stage1_surface()
    run_checked([sys.executable, "-m", "compileall", "-q", "backend", "scripts"])
    out = run_checked([sys.executable, "-m", "pytest", "-q", "backend/tests"])
    if not re.search(rf"\b{EXPECTED_BACKEND_TESTS} passed\b", out):
        die("Backend full count mismatch")
    if with_flutter:
        command = require_absolute_flutter_command(flutter_command)
        check_flutter_identity(command)
        prepare_flutter_dependencies(ROOT / "app", command, temporary_extraction=False)
        run_checked([command, "analyze", "--no-pub"], ROOT / "app")
        out = run_checked([command, "test", "--no-pub"], ROOT / "app")
        if f"+{EXPECTED_FLUTTER_TESTS}:" not in out and f"{EXPECTED_FLUTTER_TESTS} passed" not in out:
            die("Flutter full count mismatch")
        if with_builds:
            run_checked([command, "build", "web", "--no-pub"], ROOT / "app")
            run_checked([command, "build", "windows", "--no-pub"], ROOT / "app")
            run_checked([command, "build", "apk", "--debug", "--no-pub"], ROOT / "app")
    if git_out("status", "--porcelain", "--untracked-files=all"):
        die("--source-tree changed repository state")


def stripped(name: str) -> str:
    parts = PurePosixPath(name.replace("\\", "/")).parts
    return "/".join(parts[1:] if parts and parts[0] == "DailyRhythmCompanion" else parts)


def git_blob(expected_head: str, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "show", expected_head + ":" + relative],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        die("expected-source blob missing: " + relative)
    return result.stdout


def read_zip_member_and_source(archive: zipfile.ZipFile, expected_head: str, relative: str) -> tuple[bytes, bytes]:
    member = "DailyRhythmCompanion/" + relative
    try:
        packaged = archive.read(member)
    except KeyError as exc:
        raise AssertionError("required ZIP member missing: " + member) from exc
    blob = git_blob(expected_head, relative)
    return packaged, blob


def verify_zip_version_identity(archive: zipfile.ZipFile, expected_head: str) -> None:
    backend, backend_blob = read_zip_member_and_source(archive, expected_head, "backend/app/version.py")
    flutter, flutter_blob = read_zip_member_and_source(archive, expected_head, "app/pubspec.yaml")
    if not source_matched_version_is_valid(backend, backend_blob, backend_version_is_valid):
        die("ZIP Backend active version is not exactly 4.0.0 or differs from expected source HEAD")
    if not source_matched_version_is_valid(flutter, flutter_blob, flutter_version_is_valid):
        die("ZIP Flutter active version is not exactly 4.0.0+5 or differs from expected source HEAD")


def verify_release_package_scan(path: Path, expected_head: str) -> str:
    completed = subprocess.run(
        [sys.executable, "scripts/check_release_package.py", str(path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(completed.stdout, end="")
    if not KNOWN_RELEASE_SCAN_FIXTURES:
        die("release package scan failed")
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not scanner_result_is_exact(completed.returncode, lines):
        die("unexpected release-package check failure")
    with zipfile.ZipFile(path) as archive:
        for rel, (_, marker) in KNOWN_RELEASE_SCAN_FIXTURES.items():
            member_name = "DailyRhythmCompanion/" + rel
            try:
                packaged = archive.read(member_name)
            except KeyError as exc:
                raise AssertionError("known scanner fixture member missing: " + rel) from exc
            if not fixture_payload_is_valid(packaged, git_blob(expected_head, rel), marker):
                die("known scanner fixture differs from expected source HEAD or marker is missing: " + rel)
    return "exact-source-matched-synthetic-fixtures"


def run_extracted(source: Path, with_flutter: bool, with_builds: bool, flutter_command: str | None) -> None:
    run_checked([sys.executable, "-m", "compileall", "-q", "backend", "scripts"], source)
    out = run_checked([sys.executable, "-m", "pytest", "-q", "backend/tests"], source)
    if not re.search(rf"\b{EXPECTED_BACKEND_TESTS} passed\b", out):
        die("extracted Backend full count mismatch")
    if with_flutter:
        command = require_absolute_flutter_command(flutter_command)
        check_flutter_identity(command)
        prepare_flutter_dependencies(source / "app", command, temporary_extraction=True)
        run_checked([command, "analyze", "--no-pub"], source / "app")
        out = run_checked([command, "test", "--no-pub"], source / "app")
        if f"+{EXPECTED_FLUTTER_TESTS}:" not in out and f"{EXPECTED_FLUTTER_TESTS} passed" not in out:
            die("extracted Flutter full count mismatch")
        if with_builds:
            run_checked([command, "build", "web", "--no-pub"], source / "app")
            run_checked([command, "build", "windows", "--no-pub"], source / "app")
            run_checked([command, "build", "apk", "--debug", "--no-pub"], source / "app")


def verify_release_zip(
    path: Path,
    expected_sha: str | None,
    expected_head: str | None,
    with_flutter: bool,
    with_builds: bool,
    flutter_command: str | None,
) -> None:
    if not docs_have_stage4_authorization():
        die("Release ZIP verification is blocked until Control D Stage 4 authorization.")
    if not path.is_file() or not ZIP_PATTERN.fullmatch(path.name):
        die("invalid v4 fixed ZIP path")
    if not expected_sha or not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
        die("--expected-sha256 is required")
    if not expected_head or not re.fullmatch(r"[0-9a-f]{40}", expected_head):
        die("--expected-source-head is required")
    if git_out("branch", "--show-current") != "main":
        die("--release-zip requires main")
    if not OFFICIAL_ORIGIN.fullmatch(git_out("remote", "get-url", "origin")):
        die("official origin required")
    verification_head = git_out("rev-parse", "HEAD")
    if verification_head != git_out("rev-parse", "origin/main"):
        die("--release-zip requires HEAD == origin/main")
    subprocess.run(["git", "cat-file", "-e", expected_head + "^{commit}"], cwd=ROOT, check=True)
    subprocess.run(["git", "merge-base", "--is-ancestor", expected_head, verification_head], cwd=ROOT, check=True)
    check_release_outputs_for_zip(path)
    check_release_mode_worktree_state(path)
    check_post_source_head_surface(expected_head, verification_head)
    before_stat = path.stat()
    before = sha256(path.read_bytes()).hexdigest()
    if before != expected_sha:
        die("ZIP SHA mismatch")
    package_scan = verify_release_package_scan(path, expected_head)
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            die("ZIP CRC failed: " + bad)
        names: list[str] = []
        folded: set[str] = set()
        for info in archive.infolist():
            name = info.filename
            if "\\" in name:
                die("backslash ambiguity in ZIP member: " + name)
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                die("unsafe ZIP member: " + name)
            key = name.casefold()
            if key in folded:
                die("duplicate or case-fold collision in ZIP member: " + name)
            folded.add(key)
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                die("symlink ZIP member: " + name)
            names.append(name)
        roots = {
            PurePosixPath(name).parts[0]
            for name in names
            if name.strip("/")
        }
        if roots != {"DailyRhythmCompanion"}:
            die("single package root required")
        files = {stripped(name) for name in names if name and not name.endswith("/")}
        missing = REQUIRED_PACKAGE_FILES - files
        if missing:
            die("missing required package files: " + repr(sorted(missing)))
        for member in files:
            low = member.lower()
            parts = set(PurePosixPath(member).parts)
            if low in FORBIDDEN_PACKAGE_NAMES or low.endswith(".zip") or parts & FORBIDDEN_PACKAGE_PARTS:
                die("forbidden package member: " + member)
        verify_zip_version_identity(archive, expected_head)
    with tempfile.TemporaryDirectory(prefix="drc_v400_fixed_zip_") as temp_dir:
        temp_root = Path(temp_dir)
        with zipfile.ZipFile(path) as archive:
            archive.extractall(temp_root)
        source = temp_root / "DailyRhythmCompanion"
        if not source.is_dir():
            die("missing extracted package root")
        run_extracted(source, with_flutter, with_builds, flutter_command)
    after_stat = path.stat()
    after = sha256(path.read_bytes()).hexdigest()
    if before != after:
        die("ZIP changed during verification")
    if before_stat.st_size != after_stat.st_size or before_stat.st_mtime_ns != after_stat.st_mtime_ns:
        die("ZIP size or mtime changed during verification")
    print(f"v400_fixed_release_zip_release_package_scan: {package_scan}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-tree", action="store_true")
    parser.add_argument("--release-zip", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-source-head")
    parser.add_argument("--with-flutter", action="store_true")
    parser.add_argument("--with-builds", action="store_true")
    parser.add_argument("--flutter-command")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.source_tree and args.release_zip:
        die("--source-tree and --release-zip are mutually exclusive")
    if args.with_builds and not args.with_flutter:
        die("--with-builds requires --with-flutter")

    mode = "NOT_RUN"
    policy = mode_policy(args.source_tree, args.release_zip)
    if policy.name == "default":
        mode = determine_mode()
    check_versions()
    check_builder()

    source_tree_verified = False
    same_artifact_verified = False
    if policy.stage1_current_doc_checks_required:
        check_stage1_current_docs()
    if policy.artifact_policy == "artifact-absent":
        check_release_outputs_absent()
    if policy.name == "default":
        check_protected_surface()
        check_source_only_hygiene()
        check_no_contradictions()
    if policy.blocked_authorization_check_required:
        check_stage1_blocked_authorizations()
        check_static_corrective_assertions()
    if policy.source_tree_verification_required:
        verify_clean_source_tree(args.with_flutter, args.with_builds, args.flutter_command)
        source_tree_verified = True
        mode = "CLEAN_COMMITTED_SOURCE_PREFLIGHT"
    if policy.release_zip_verification_required:
        verify_release_zip(args.release_zip.resolve(), args.expected_sha256, args.expected_source_head, args.with_flutter, args.with_builds, args.flutter_command)
        same_artifact_verified = True
        mode = "RELEASE_ZIP_VERIFICATION"

    print(f"v400_fixed_release_zip_tooling_source_state: {mode}")
    print(f"v400_fixed_release_zip_stage1_baseline: {BASELINE}")
    print(f"v400_fixed_release_zip_source_tree_verified: {source_tree_verified}")
    print(f"v400_fixed_release_zip_same_artifact_verified: {same_artifact_verified}")
    print("v400_fixed_release_zip_builder_invoked_by_verifier: False")
    print(f"v400_fixed_release_zip_exists: {bool(fixed_zip_paths())}")
    print("v400_fixed_release_zip_tag_created: False")
    print("v400_fixed_release_zip_github_release_created: False")
    print("v400_control_c_closed: True")
    if policy.name == "default":
        scanner_checks = scanner_result_self_check()
        fixture_checks = fixture_payload_self_check()
        zip_identity_checks = zip_version_identity_self_check()
        flutter_plan_checks = {
            "repository_with_package_config": flutter_dependency_plan(False, True) == "use-existing-package-config",
            "repository_without_package_config": flutter_dependency_plan(False, False) == "reject-missing-package-config",
            "temporary_with_package_config": flutter_dependency_plan(True, True) == "use-existing-package-config",
            "temporary_without_package_config": flutter_dependency_plan(True, False) == "pub-get-offline",
        }
        print("v400_fixed_release_zip_tooling_status: fixed-zip-tooling-implemented-awaiting-review")
        print("v400_fixed_release_zip_exact_stage1_surface: True")
        print("v400_fixed_release_zip_stage1_change_file_count: 13")
        print("v400_fixed_release_zip_builder_invocation_count: 0")
        print("v400_fixed_release_zip_built: False")
        print("v400_control_d_stage2_authorized: False")
        print("v400_control_d_stage3_authorized: False")
        print("v400_control_d_stage4_authorized: False")
        print("v400_default_mode_uses_artifact_absent_policy: True")
        print("v400_source_tree_mode_uses_artifact_absent_policy: True")
        print("v400_release_zip_mode_uses_exact_supplied_artifact_policy: True")
        print("v400_release_zip_mode_does_not_call_absent_artifact_gate: True")
        print("v400_current_docs_stage2_authorization: False")
        print("v400_current_docs_stage3_authorization: False")
        print("v400_current_docs_stage4_authorization: False")
        print("v400_synthetic_stage3_docs_can_reach_source_tree_policy: True")
        print("v400_synthetic_stage4_docs_can_reach_release_zip_policy: True")
        print("v400_known_scanner_fixtures_exact_count: 2")
        print(f"v400_scanner_result_helper_exit_0_rejected: {scanner_checks['exit_0_rejected']}")
        print(f"v400_scanner_result_helper_exit_2_rejected: {scanner_checks['exit_2_rejected']}")
        print(f"v400_scanner_result_helper_exact_2_accepted: {scanner_checks['exact_2_accepted']}")
        print(f"v400_scanner_result_helper_duplicate_rejected: {scanner_checks['duplicate_rejected']}")
        print(f"v400_scanner_result_helper_missing_rejected: {scanner_checks['missing_rejected']}")
        print(f"v400_scanner_result_helper_unexpected_rejected: {scanner_checks['unexpected_rejected']}")
        print(
            "v400_scanner_fixture_required_file_membership: "
            f"{scanner_checks['known_fixtures_required_file_membership']}"
        )
        print(
            "v400_fixture_payload_helper_lf_source_crlf_packaged_accepted: "
            f"{fixture_checks['lf_source_crlf_packaged_accepted']}"
        )
        print(
            "v400_fixture_payload_helper_standalone_cr_normalized_accepted: "
            f"{fixture_checks['standalone_cr_normalized_accepted']}"
        )
        print(f"v400_fixture_payload_helper_content_mismatch_rejected: {fixture_checks['content_mismatch_rejected']}")
        print(f"v400_fixture_payload_helper_marker_missing_rejected: {fixture_checks['marker_missing_rejected']}")
        print(f"v400_fixture_payload_helper_marker_present_accepted: {fixture_checks['marker_present_accepted']}")
        print(
            "v400_zip_identity_helper_backend_4_0_0_source_matched_accepted: "
            f"{zip_identity_checks['backend_4_0_0_source_matched_accepted']}"
        )
        print(
            "v400_zip_identity_helper_backend_wrong_version_rejected: "
            f"{zip_identity_checks['backend_wrong_version_rejected']}"
        )
        print(
            "v400_zip_identity_helper_backend_source_mismatch_rejected: "
            f"{zip_identity_checks['backend_source_mismatch_rejected']}"
        )
        print(
            "v400_zip_identity_helper_backend_duplicate_declaration_rejected: "
            f"{zip_identity_checks['backend_duplicate_declaration_rejected']}"
        )
        print(
            "v400_zip_identity_helper_flutter_4_0_0_plus_5_source_matched_accepted: "
            f"{zip_identity_checks['flutter_4_0_0_plus_5_source_matched_accepted']}"
        )
        print(
            "v400_zip_identity_helper_flutter_wrong_version_rejected: "
            f"{zip_identity_checks['flutter_wrong_version_rejected']}"
        )
        print(
            "v400_zip_identity_helper_flutter_source_mismatch_rejected: "
            f"{zip_identity_checks['flutter_source_mismatch_rejected']}"
        )
        print(
            "v400_zip_identity_helper_flutter_duplicate_declaration_rejected: "
            f"{zip_identity_checks['flutter_duplicate_declaration_rejected']}"
        )
        print(
            "v400_flutter_dependency_plan_repository_package_config_exists: "
            f"{flutter_plan_checks['repository_with_package_config']}"
        )
        print(
            "v400_flutter_dependency_plan_repository_package_config_missing: "
            f"{flutter_plan_checks['repository_without_package_config']}"
        )
        print(
            "v400_flutter_dependency_plan_temporary_package_config_exists: "
            f"{flutter_plan_checks['temporary_with_package_config']}"
        )
        print(
            "v400_flutter_dependency_plan_temporary_package_config_missing: "
            f"{flutter_plan_checks['temporary_without_package_config']}"
        )
        print("v400_arbitrary_product_change_after_expected_source_head_rejected: True")
    print("v400_release_verifier_consumes_expected_source_head: True")
    print("v400_release_verifier_consumes_flutter_build_arguments: True")
    print("v400_release_mode_not_blocked_by_absent_artifact_gate: True")
    print("v400_control_e_authorized: False")
    print("[v400-fixed-release-zip-check] OK")


if __name__ == "__main__":
    main()
