#!/usr/bin/env python3
"""DRC v4.0.0 Control D fixed-ZIP tooling gate.

Default mode validates the exact Stage 3 authorization-sync candidate or its
exact one-commit clean committed form without network, credentials, Flutter execution,
builder invocation, or artifact creation. ``--source-tree`` accepts the already
completed Stage 2 source preflight state, while ``--release-zip`` remains
blocked until a later authorization marker is committed.
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
CONTROL_D_STAGE1_COMMIT = "a204f6b11d25baeea67b7b7be8860c9a4f9ea945"
CONTROL_D_STAGE2A_COMMIT = "507685488fd33231dfec4bfc0f2c4532a1141de2"
CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT = "eb68cf9334f46a30c0c06d3921d59f56abb540bb"
CONTROL_D_STAGE2_ACCEPTANCE_COMMIT = "697d0918cb8a6de5c0459324464b7d7e376b3a5a"
CONTROL_D_STAGE3_AUTHORIZATION_COMMIT = "0f7418100beaedd764d4c0821973b23fa20327a2"
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
EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT = (
    '$stage3AuthorizationMarker = "Control D Stage 3 authorization:\\s*`r?`nAUTHORIZED_FOR_ONE_TIME_BUILD"'
)
EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256 = "13248D55299C57B5DD940091DB2B6738B5F7024DC3A2A3F238917E9F8315A330"
STAGE2_ACCEPTED = "Control D Stage 2:\nCLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"
STAGE3_ARTIFACT_READY = "Control D Stage 3:\nBUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"
STAGE2A_MODIFIED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_fixed_release_zip.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_record.md",
    "scripts/check_v400_fixed_release_zip.py",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
CORRECTIVE_SURFACE = {
    "scripts/check_v400_fixed_release_zip.py",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
EXPECTED_MODIFIED = STAGE2A_MODIFIED
EXPECTED_ADDED: set[str] = set()
STAGE2_ACCEPTANCE_SYNC_MODIFIED = STAGE2A_MODIFIED
STAGE3_AUTHORIZATION_SYNC_MODIFIED = STAGE2A_MODIFIED
STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED = {
    "build_v400_fixed_release_zip_from_head.ps1",
    "scripts/check_v400_fixed_release_zip.py",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
STAGE1_MODIFIED = {
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
STAGE1_ADDED = {
    "docs/v400_fixed_release_zip.md",
    "build_v400_fixed_release_zip_from_head.ps1",
    "scripts/check_v400_fixed_release_zip.py",
}
STAGE1_SURFACE = STAGE1_MODIFIED | STAGE1_ADDED
STAGE1_PROTECTED_DELTA = {
    "build_v400_fixed_release_zip_from_head.ps1",
}
STAGE1_EXPECTED_BY_STATUS = {
    "M": STAGE1_MODIFIED,
    "A": STAGE1_ADDED,
}
STAGE1_PROTECTED_EXPECTED_BY_STATUS = {
    "A": STAGE1_PROTECTED_DELTA,
}
STALE_STAGE3_CURRENT_STATE_PHRASES = (
    "future accepted document adds the tooling-defined Stage 3 one-time-build authorization marker",
    "future Stage 3/4 authorization absence",
    "When authorized in the future, actual build must create",
    "Current checkpoint: DRC v4.0.0 Release Preparation Protocol Control D Stage 2 Acceptance Sync",
)
REQUIRED_STAGE3_CURRENT_STATE_PHRASES = (
    "Stage 3 authorization-sync candidate does not run the builder while it is dirty, unreviewed, unaccepted, uncommitted, and unpushed.",
    "After Stage 3 authorization-sync is reviewed, accepted, committed, and pushed, the accepted marker authorizes only the fixed ZIP exact one-time build, and the builder still requires separate explicit user build approval.",
    "Stage 4 remains future and not authorized until a future accepted document adds the tooling-defined Stage 4 same-artifact authorization marker.",
)
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
    "build_v400_fixed_release_zip_from_head.ps1",
    "build_release.bat",
    "scripts/check_release_package.py",
    "release_notes/v4.0.0.md",
    "backend",
    "app",
    "release",
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
    current_doc_checks_required: bool
    source_tree_verification_required: bool
    release_zip_verification_required: bool
    authorization_boundary_check_required: bool


DEFAULT_MODE_POLICY = ModePolicy(
    name="default",
    artifact_policy="artifact-absent",
    current_doc_checks_required=True,
    source_tree_verification_required=False,
    release_zip_verification_required=False,
    authorization_boundary_check_required=True,
)
SOURCE_TREE_MODE_POLICY = ModePolicy(
    name="source-tree",
    artifact_policy="artifact-absent",
    current_doc_checks_required=False,
    source_tree_verification_required=True,
    release_zip_verification_required=False,
    authorization_boundary_check_required=False,
)
RELEASE_ZIP_MODE_POLICY = ModePolicy(
    name="release-zip",
    artifact_policy="exact-supplied-artifact",
    current_doc_checks_required=False,
    source_tree_verification_required=False,
    release_zip_verification_required=True,
    authorization_boundary_check_required=False,
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


def compact(text: str) -> str:
    return " ".join(norm(text).split())


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


def dirty_surface_is_exact(entries: list[tuple[str, str]], expected_modified: set[str]) -> bool:
    modified: set[str] = set()
    added: set[str] = set()
    deleted: set[str] = set()
    other: list[tuple[str, str]] = []
    for status, path in entries:
        if status == " M":
            if path in modified:
                other.append((status, path))
            modified.add(path)
        elif status == "??":
            if path in added:
                other.append((status, path))
            added.add(path)
        elif "D" in status:
            if path in deleted:
                other.append((status, path))
            deleted.add(path)
        else:
            other.append((status, path))
    return modified == expected_modified and added == EXPECTED_ADDED and not deleted and not other


def check_dirty_surface(entries: list[tuple[str, str]], expected_modified: set[str]) -> None:
    if not dirty_surface_is_exact(entries, expected_modified):
        modified_paths = sorted(path for status, path in entries if status == " M")
        added_paths = sorted(path for status, path in entries if status == "??")
        deleted_paths = sorted(path for status, path in entries if "D" in status)
        other = [(status, path) for status, path in entries if status not in {" M", "??"} and "D" not in status]
        die(
            "Unexpected dirty surface: "
            f"modified={modified_paths!r} added={added_paths!r} "
            f"deleted={deleted_paths!r} other={other!r}"
        )


def validate_exact_committed_surface(
    commit_count: int,
    name_status_lines: list[str],
    expected_modified: set[str],
) -> bool:
    if commit_count != 1:
        return False
    seen: set[str] = set()
    for line in name_status_lines:
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            return False
        status, path = parts
        normalized = path.replace("\\", "/")
        if status != "M":
            return False
        if normalized in seen:
            return False
        seen.add(normalized)
    return seen == expected_modified


def validate_stage2a_committed_surface(commit_count: int, name_status_lines: list[str]) -> bool:
    return validate_exact_committed_surface(commit_count, name_status_lines, STAGE2A_MODIFIED)


def validate_corrective_committed_surface(commit_count: int, name_status_lines: list[str]) -> bool:
    return validate_exact_committed_surface(commit_count, name_status_lines, CORRECTIVE_SURFACE)


def validate_acceptance_sync_committed_surface(commit_count: int, name_status_lines: list[str]) -> bool:
    return validate_exact_committed_surface(commit_count, name_status_lines, STAGE2_ACCEPTANCE_SYNC_MODIFIED)


def validate_stage3_authorization_sync_committed_surface(
    commit_count: int,
    name_status_lines: list[str],
) -> bool:
    return validate_exact_committed_surface(commit_count, name_status_lines, STAGE3_AUTHORIZATION_SYNC_MODIFIED)


def validate_stage3_builder_auth_guard_corrective_committed_surface(
    commit_count: int,
    name_status_lines: list[str],
) -> bool:
    return validate_exact_committed_surface(
        commit_count,
        name_status_lines,
        STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED,
    )


def acceptance_sync_origin_state(head: str, origin: str) -> str | None:
    if not origin:
        return None
    if origin == CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT and head != origin:
        return "NOT_PUSHED"
    if origin == head and head != CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT:
        return "PUSHED"
    return None


def acceptance_sync_clean_mode_after_surface_validation(surface_validated: bool, head: str, origin: str) -> str:
    if not surface_validated:
        die("Stage 2 acceptance-sync origin policy reached before committed surface validation")
    state = acceptance_sync_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE2_ACCEPTANCE_SYNC_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE2_ACCEPTANCE_SYNC"
    die("clean Stage 2 acceptance-sync origin/main state is invalid")


def stage3_authorization_sync_origin_state(head: str, origin: str) -> str | None:
    if not origin:
        return None
    if origin == CONTROL_D_STAGE2_ACCEPTANCE_COMMIT and head != origin:
        return "NOT_PUSHED"
    if origin == head and head != CONTROL_D_STAGE2_ACCEPTANCE_COMMIT:
        return "PUSHED"
    return None


def stage3_authorization_sync_clean_mode_after_surface_validation(
    surface_validated: bool,
    head: str,
    origin: str,
) -> str:
    if not surface_validated:
        die("Stage 3 authorization-sync origin policy reached before committed surface validation")
    state = stage3_authorization_sync_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE3_AUTHORIZATION_SYNC_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE3_AUTHORIZATION_SYNC"
    die("clean Stage 3 authorization-sync origin/main state is invalid")


def stage3_builder_auth_guard_corrective_origin_state(head: str, origin: str) -> str | None:
    if not origin:
        return None
    if origin == CONTROL_D_STAGE3_AUTHORIZATION_COMMIT and head != origin:
        return "NOT_PUSHED"
    if origin == head and head != CONTROL_D_STAGE3_AUTHORIZATION_COMMIT:
        return "PUSHED"
    return None


def stage3_builder_auth_guard_corrective_clean_mode_after_surface_validation(
    surface_validated: bool,
    head: str,
    origin: str,
) -> str:
    if not surface_validated:
        die("Stage 3 builder authorization guard corrective origin policy reached before committed surface validation")
    state = stage3_builder_auth_guard_corrective_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE"
    die("clean Stage 3 builder authorization guard corrective origin/main state is invalid")


def validate_exact_name_status_surface(
    name_status_lines: list[str],
    expected_by_status: dict[str, set[str]],
) -> bool:
    expected_paths = set().union(*expected_by_status.values())
    seen: set[str] = set()
    seen_by_status = {status: set() for status in expected_by_status}
    for line in name_status_lines:
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            return False
        status, path = parts
        normalized = path.replace("\\", "/")
        if status not in expected_by_status or normalized in seen:
            return False
        seen.add(normalized)
        seen_by_status[status].add(normalized)
    return seen == expected_paths and seen_by_status == expected_by_status


def validate_stage1_surface(name_status_lines: list[str]) -> bool:
    return validate_exact_name_status_surface(name_status_lines, STAGE1_EXPECTED_BY_STATUS)


def validate_stage1_protected_delta(name_status_lines: list[str]) -> bool:
    return validate_exact_name_status_surface(name_status_lines, STAGE1_PROTECTED_EXPECTED_BY_STATUS)


def validate_empty_protected_delta(name_status_lines: list[str]) -> bool:
    return not any(line for line in name_status_lines)


def validate_stage3_builder_auth_guard_corrective_protected_delta(name_status_lines: list[str]) -> bool:
    return validate_exact_name_status_surface(
        name_status_lines,
        {"M": {"build_v400_fixed_release_zip_from_head.ps1"}},
    )


def stage2a_committed_surface_self_check() -> dict[str, bool]:
    exact = [f"M\t{path}" for path in sorted(STAGE2A_MODIFIED)]
    missing = exact[:-1]
    unexpected = [*exact, "M\tbackend/app/version.py"]
    duplicate = [*exact, exact[0]]
    status_a = [*exact[1:], "A\tREADME.md"]
    status_d = [*exact[1:], "D\tREADME.md"]
    status_r = [*exact[1:], "R100\tREADME.md\tREADME.md"]
    status_c = [*exact[1:], "C100\tREADME.md\tREADME.md"]
    malformed = [*exact[1:], "M README.md"]
    return {
        "exact_one_commit_m12_accepted": validate_stage2a_committed_surface(1, exact),
        "count_0_rejected": not validate_stage2a_committed_surface(0, exact),
        "count_2_rejected": not validate_stage2a_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage2a_committed_surface(1, missing),
        "unexpected_path_rejected": not validate_stage2a_committed_surface(1, unexpected),
        "duplicate_path_rejected": not validate_stage2a_committed_surface(1, duplicate),
        "status_a_rejected": not validate_stage2a_committed_surface(1, status_a),
        "status_d_rejected": not validate_stage2a_committed_surface(1, status_d),
        "status_r_rejected": not validate_stage2a_committed_surface(1, status_r),
        "status_c_rejected": not validate_stage2a_committed_surface(1, status_c),
        "malformed_line_rejected": not validate_stage2a_committed_surface(1, malformed),
    }


def stage1_surface_self_check() -> dict[str, bool]:
    exact = [*[f"M\t{path}" for path in sorted(STAGE1_MODIFIED)], *[f"A\t{path}" for path in sorted(STAGE1_ADDED)]]
    first_modified = sorted(STAGE1_MODIFIED)[0]
    first_added = sorted(STAGE1_ADDED)[0]
    return {
        "exact_m10_a3_accepted": validate_stage1_surface(exact),
        "missing_path_rejected": not validate_stage1_surface(exact[:-1]),
        "unexpected_path_rejected": not validate_stage1_surface([*exact, "M\tbackend/app/version.py"]),
        "duplicate_path_rejected": not validate_stage1_surface([*exact, exact[0]]),
        "wrong_m_a_rejected": not validate_stage1_surface(
            [line for line in exact if line != "M\t" + first_modified and line != "A\t" + first_added]
            + ["A\t" + first_modified, "M\t" + first_added]
        ),
        "status_d_rejected": not validate_stage1_surface([*exact[1:], "D\t" + first_modified]),
        "status_r_rejected": not validate_stage1_surface([*exact[1:], "R100\told\t" + first_modified]),
        "status_c_rejected": not validate_stage1_surface([*exact[1:], "C100\told\t" + first_modified]),
        "malformed_line_rejected": not validate_stage1_surface([*exact[1:], "M " + first_modified]),
    }


def stage1_protected_delta_self_check() -> dict[str, bool]:
    exact = [f"A\t{path}" for path in sorted(STAGE1_PROTECTED_DELTA)]
    builder = sorted(STAGE1_PROTECTED_DELTA)[0]
    return {
        "exact_builder_a_accepted": validate_stage1_protected_delta(exact),
        "empty_rejected": not validate_stage1_protected_delta([]),
        "builder_m_rejected": not validate_stage1_protected_delta(["M\t" + builder]),
        "missing_rejected": not validate_stage1_protected_delta([]),
        "unexpected_protected_path_rejected": not validate_stage1_protected_delta([*exact, "A\tbuild_release.bat"]),
        "duplicate_rejected": not validate_stage1_protected_delta([*exact, exact[0]]),
        "status_d_rejected": not validate_stage1_protected_delta(["D\t" + builder]),
        "status_r_rejected": not validate_stage1_protected_delta(["R100\told\t" + builder]),
        "status_c_rejected": not validate_stage1_protected_delta(["C100\told\t" + builder]),
    }


def post_stage1_protected_delta_self_check() -> dict[str, bool]:
    return {
        "empty_accepted": validate_empty_protected_delta([]),
        "any_protected_change_rejected": not validate_empty_protected_delta(["M\tbuild_release.bat"]),
    }


def stage3_builder_auth_guard_corrective_protected_delta_self_check() -> dict[str, bool]:
    builder = "build_v400_fixed_release_zip_from_head.ps1"
    exact = ["M\t" + builder]
    return {
        "exact_builder_m_accepted": validate_stage3_builder_auth_guard_corrective_protected_delta(exact),
        "empty_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta([]),
        "builder_a_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta(["A\t" + builder]),
        "builder_d_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta(["D\t" + builder]),
        "builder_r_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta(
            ["R100\told\t" + builder]
        ),
        "builder_c_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta(
            ["C100\told\t" + builder]
        ),
        "extra_path_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta(
            [*exact, "M\tbuild_release.bat"]
        ),
        "malformed_line_rejected": not validate_stage3_builder_auth_guard_corrective_protected_delta(["M " + builder]),
    }


def corrective_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(CORRECTIVE_SURFACE)[0]
    exact = [(" M", path) for path in sorted(CORRECTIVE_SURFACE)]
    return {
        "exact_m2_accepted": dirty_surface_is_exact(exact, CORRECTIVE_SURFACE),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], CORRECTIVE_SURFACE),
        "unexpected_path_rejected": not dirty_surface_is_exact([*exact, (" M", "README.md")], CORRECTIVE_SURFACE),
        "duplicate_path_rejected": not dirty_surface_is_exact([*exact, exact[0]], CORRECTIVE_SURFACE),
        "staged_rejected": not dirty_surface_is_exact([*exact[1:], ("M ", first)], CORRECTIVE_SURFACE),
        "untracked_rejected": not dirty_surface_is_exact([*exact, ("??", "scratch.txt")], CORRECTIVE_SURFACE),
        "status_a_rejected": not dirty_surface_is_exact([*exact[1:], (" A", first)], CORRECTIVE_SURFACE),
        "status_d_rejected": not dirty_surface_is_exact([*exact[1:], (" D", first)], CORRECTIVE_SURFACE),
        "status_r_rejected": not dirty_surface_is_exact([*exact[1:], ("R ", first)], CORRECTIVE_SURFACE),
        "status_c_rejected": not dirty_surface_is_exact([*exact[1:], ("C ", first)], CORRECTIVE_SURFACE),
    }


def corrective_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(CORRECTIVE_SURFACE)[0]
    exact = [f"M\t{path}" for path in sorted(CORRECTIVE_SURFACE)]
    return {
        "exact_one_commit_m2_accepted": validate_corrective_committed_surface(1, exact),
        "count_0_rejected": not validate_corrective_committed_surface(0, exact),
        "count_2_rejected": not validate_corrective_committed_surface(2, exact),
        "missing_path_rejected": not validate_corrective_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_corrective_committed_surface(1, [*exact, "M\tREADME.md"]),
        "duplicate_path_rejected": not validate_corrective_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "A\t" + first]),
        "status_d_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "D\t" + first]),
        "status_r_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "R100\told\t" + first]),
        "status_c_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "C100\told\t" + first]),
        "malformed_line_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "M " + first]),
    }


def acceptance_sync_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE2_ACCEPTANCE_SYNC_MODIFIED)[0]
    exact = [(" M", path) for path in sorted(STAGE2_ACCEPTANCE_SYNC_MODIFIED)]
    return {
        "exact_m12_accepted": dirty_surface_is_exact(exact, STAGE2_ACCEPTANCE_SYNC_MODIFIED),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], STAGE2_ACCEPTANCE_SYNC_MODIFIED),
        "unexpected_path_rejected": not dirty_surface_is_exact(
            [*exact, (" M", "backend/app/version.py")], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
        "duplicate_path_rejected": not dirty_surface_is_exact([*exact, exact[0]], STAGE2_ACCEPTANCE_SYNC_MODIFIED),
        "staged_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("M ", first)], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
        "untracked_rejected": not dirty_surface_is_exact(
            [*exact, ("??", "scratch.txt")], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
        "status_a_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" A", first)], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
        "status_d_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" D", first)], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
        "status_r_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("R ", first)], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
        "status_c_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("C ", first)], STAGE2_ACCEPTANCE_SYNC_MODIFIED
        ),
    }


def acceptance_sync_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE2_ACCEPTANCE_SYNC_MODIFIED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE2_ACCEPTANCE_SYNC_MODIFIED)]
    return {
        "exact_one_commit_m12_accepted": validate_acceptance_sync_committed_surface(1, exact),
        "count_0_rejected": not validate_acceptance_sync_committed_surface(0, exact),
        "count_2_rejected": not validate_acceptance_sync_committed_surface(2, exact),
        "missing_path_rejected": not validate_acceptance_sync_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_acceptance_sync_committed_surface(
            1, [*exact, "M\tbackend/app/version.py"]
        ),
        "duplicate_path_rejected": not validate_acceptance_sync_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_acceptance_sync_committed_surface(1, [*exact[1:], "A\t" + first]),
        "status_d_rejected": not validate_acceptance_sync_committed_surface(1, [*exact[1:], "D\t" + first]),
        "status_r_rejected": not validate_acceptance_sync_committed_surface(1, [*exact[1:], "R100\told\t" + first]),
        "status_c_rejected": not validate_acceptance_sync_committed_surface(1, [*exact[1:], "C100\told\t" + first]),
        "malformed_line_rejected": not validate_acceptance_sync_committed_surface(1, [*exact[1:], "M " + first]),
    }


def stage3_authorization_sync_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_AUTHORIZATION_SYNC_MODIFIED)[0]
    exact = [(" M", path) for path in sorted(STAGE3_AUTHORIZATION_SYNC_MODIFIED)]
    return {
        "exact_m12_accepted": dirty_surface_is_exact(exact, STAGE3_AUTHORIZATION_SYNC_MODIFIED),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], STAGE3_AUTHORIZATION_SYNC_MODIFIED),
        "unexpected_path_rejected": not dirty_surface_is_exact(
            [*exact, (" M", "backend/app/version.py")], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
        "duplicate_path_rejected": not dirty_surface_is_exact([*exact, exact[0]], STAGE3_AUTHORIZATION_SYNC_MODIFIED),
        "staged_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("M ", first)], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
        "untracked_rejected": not dirty_surface_is_exact(
            [*exact, ("??", "scratch.txt")], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
        "status_a_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" A", first)], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
        "status_d_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" D", first)], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
        "status_r_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("R ", first)], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
        "status_c_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("C ", first)], STAGE3_AUTHORIZATION_SYNC_MODIFIED
        ),
    }


def stage3_authorization_sync_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_AUTHORIZATION_SYNC_MODIFIED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE3_AUTHORIZATION_SYNC_MODIFIED)]
    return {
        "exact_one_commit_m12_accepted": validate_stage3_authorization_sync_committed_surface(1, exact),
        "count_0_rejected": not validate_stage3_authorization_sync_committed_surface(0, exact),
        "count_2_rejected": not validate_stage3_authorization_sync_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage3_authorization_sync_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_stage3_authorization_sync_committed_surface(
            1, [*exact, "M\tbackend/app/version.py"]
        ),
        "duplicate_path_rejected": not validate_stage3_authorization_sync_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_stage3_authorization_sync_committed_surface(1, [*exact[1:], "A\t" + first]),
        "status_d_rejected": not validate_stage3_authorization_sync_committed_surface(1, [*exact[1:], "D\t" + first]),
        "status_r_rejected": not validate_stage3_authorization_sync_committed_surface(
            1, [*exact[1:], "R100\told\t" + first]
        ),
        "status_c_rejected": not validate_stage3_authorization_sync_committed_surface(
            1, [*exact[1:], "C100\told\t" + first]
        ),
        "malformed_line_rejected": not validate_stage3_authorization_sync_committed_surface(
            1, [*exact[1:], "M " + first]
        ),
    }


def stage3_builder_auth_guard_corrective_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED)[0]
    exact = [(" M", path) for path in sorted(STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED)]
    return {
        "exact_m3_accepted": dirty_surface_is_exact(exact, STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED),
        "missing_path_rejected": not dirty_surface_is_exact(
            exact[:-1], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "unexpected_path_rejected": not dirty_surface_is_exact(
            [*exact, (" M", "README.md")], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "duplicate_path_rejected": not dirty_surface_is_exact(
            [*exact, exact[0]], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "staged_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("M ", first)], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "untracked_rejected": not dirty_surface_is_exact(
            [*exact, ("??", "scratch.txt")], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "status_a_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" A", first)], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "status_d_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" D", first)], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "status_r_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("R ", first)], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
        "status_c_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("C ", first)], STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED
        ),
    }


def stage3_builder_auth_guard_corrective_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED)]
    return {
        "exact_one_commit_m3_accepted": validate_stage3_builder_auth_guard_corrective_committed_surface(1, exact),
        "count_0_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(0, exact),
        "count_2_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact, "M\tREADME.md"]
        ),
        "duplicate_path_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact, exact[0]]
        ),
        "status_a_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact[1:], "A\t" + first]
        ),
        "status_d_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact[1:], "D\t" + first]
        ),
        "status_r_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact[1:], "R100\told\t" + first]
        ),
        "status_c_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact[1:], "C100\told\t" + first]
        ),
        "malformed_line_rejected": not validate_stage3_builder_auth_guard_corrective_committed_surface(
            1, [*exact[1:], "M " + first]
        ),
    }


def acceptance_sync_origin_state_self_check() -> dict[str, bool]:
    synthetic_head = "f" * 40
    unrelated = "1" * 40
    try:
        acceptance_sync_clean_mode_after_surface_validation(False, synthetic_head, CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT)
        blocked_before_surface_validation = False
    except AssertionError:
        blocked_before_surface_validation = True
    determine_names = set(determine_mode.__code__.co_names)
    determine_consts = set(determine_mode.__code__.co_consts)
    return {
        "base_origin_accepted_as_not_pushed": acceptance_sync_origin_state(
            synthetic_head, CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT
        )
        == "NOT_PUSHED",
        "head_origin_accepted_as_pushed": acceptance_sync_origin_state(synthetic_head, synthetic_head) == "PUSHED",
        "unrelated_origin_rejected": acceptance_sync_origin_state(synthetic_head, unrelated) is None,
        "empty_origin_rejected": acceptance_sync_origin_state(synthetic_head, "") is None,
        "origin_policy_blocked_before_surface_validation": blocked_before_surface_validation,
        "determine_mode_references_origin_helper": "acceptance_sync_clean_mode_after_surface_validation"
        in determine_names,
        "dirty_mode_maintained": "DIRTY_STAGE2_ACCEPTANCE_SYNC_CANDIDATE" in determine_consts,
    }


def stage3_authorization_sync_origin_state_self_check() -> dict[str, bool]:
    synthetic_head = "e" * 40
    unrelated = "2" * 40
    expected_message = "Stage 3 authorization-sync origin policy reached before committed surface validation"
    try:
        stage3_authorization_sync_clean_mode_after_surface_validation(
            False, synthetic_head, CONTROL_D_STAGE2_ACCEPTANCE_COMMIT
        )
        blocked_before_surface_validation = False
    except AssertionError as exc:
        blocked_before_surface_validation = str(exc) == expected_message
    determine_names = set(determine_mode.__code__.co_names)
    determine_consts = set(determine_mode.__code__.co_consts)
    return {
        "base_origin_accepted_as_not_pushed": stage3_authorization_sync_origin_state(
            synthetic_head, CONTROL_D_STAGE2_ACCEPTANCE_COMMIT
        )
        == "NOT_PUSHED",
        "head_origin_accepted_as_pushed": stage3_authorization_sync_origin_state(
            synthetic_head, synthetic_head
        )
        == "PUSHED",
        "unrelated_origin_rejected": stage3_authorization_sync_origin_state(synthetic_head, unrelated) is None,
        "empty_origin_rejected": stage3_authorization_sync_origin_state(synthetic_head, "") is None,
        "origin_policy_blocked_before_surface_validation": blocked_before_surface_validation,
        "determine_mode_references_origin_helper": "stage3_authorization_sync_clean_mode_after_surface_validation"
        in determine_names,
        "dirty_mode_maintained": "DIRTY_STAGE3_AUTHORIZATION_SYNC_CANDIDATE" in determine_consts,
    }


def stage3_builder_auth_guard_corrective_origin_state_self_check() -> dict[str, bool]:
    synthetic_head = "d" * 40
    unrelated = "3" * 40
    expected_message = "Stage 3 builder authorization guard corrective origin policy reached before committed surface validation"
    try:
        stage3_builder_auth_guard_corrective_clean_mode_after_surface_validation(
            False, synthetic_head, CONTROL_D_STAGE3_AUTHORIZATION_COMMIT
        )
        blocked_before_surface_validation = False
    except AssertionError as exc:
        blocked_before_surface_validation = str(exc) == expected_message
    determine_names = set(determine_mode.__code__.co_names)
    determine_consts = set(determine_mode.__code__.co_consts)
    return {
        "base_origin_accepted_as_not_pushed": stage3_builder_auth_guard_corrective_origin_state(
            synthetic_head, CONTROL_D_STAGE3_AUTHORIZATION_COMMIT
        )
        == "NOT_PUSHED",
        "head_origin_accepted_as_pushed": stage3_builder_auth_guard_corrective_origin_state(
            synthetic_head, synthetic_head
        )
        == "PUSHED",
        "unrelated_origin_rejected": stage3_builder_auth_guard_corrective_origin_state(
            synthetic_head, unrelated
        )
        is None,
        "empty_origin_rejected": stage3_builder_auth_guard_corrective_origin_state(synthetic_head, "") is None,
        "origin_policy_blocked_before_surface_validation": blocked_before_surface_validation,
        "determine_mode_references_origin_helper": "stage3_builder_auth_guard_corrective_clean_mode_after_surface_validation"
        in determine_names,
        "dirty_mode_maintained": "DIRTY_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_CANDIDATE" in determine_consts,
    }


def current_state_prose_is_consistent(text: str) -> bool:
    compacted = compact(text)
    return all(phrase in compacted for phrase in REQUIRED_STAGE3_CURRENT_STATE_PHRASES) and not any(
        phrase in compacted for phrase in STALE_STAGE3_CURRENT_STATE_PHRASES
    )


def current_state_prose_consistency_self_check() -> dict[str, bool]:
    corrected = "\n".join(REQUIRED_STAGE3_CURRENT_STATE_PHRASES)
    stale = corrected + "\nfuture Stage 3/4 authorization absence"
    missing = "\n".join(REQUIRED_STAGE3_CURRENT_STATE_PHRASES[:-1])
    stage4_future = corrected + "\nfuture accepted document adds the tooling-defined Stage 4 same-artifact authorization marker"
    return {
        "corrected_current_state_prose_accepted": current_state_prose_is_consistent(corrected),
        "stale_stage3_phrase_rejected": not current_state_prose_is_consistent(stale),
        "required_current_state_phrase_missing_rejected": not current_state_prose_is_consistent(missing),
        "stage4_future_boundary_prose_accepted": current_state_prose_is_consistent(stage4_future),
    }


def stage3_authorization_contract_is_present(text: str) -> bool:
    return (
        re.search(
        rf"Control D Stage 3 authorization:\s*\r?\n\s*{re.escape(STAGE3_AUTHORIZATION)}",
        text,
        )
        is not None
        and not old_stage3_authorization_contract_is_present(text)
    )


def old_stage3_authorization_contract_is_present(text: str) -> bool:
    return re.search(
        rf"Control D Stage 3:\s*\r?\n\s*{re.escape(STAGE3_AUTHORIZATION)}",
        text,
    ) is not None


def executable_stage3_authorization_marker_assignments(builder_text: str) -> tuple[list[str], bool]:
    assignments: list[str] = []
    in_block_comment = False
    here_string_end: str | None = None
    in_single_quoted_string = False
    in_double_quoted_string = False
    brace_depth = 0
    parenthesis_depth = 0
    invalid_nesting = False

    def variable_event_at(line: str, start: int, top_level: bool) -> tuple[str | None, int]:
        mutation_prefix = ""
        variable_start = start
        if line.startswith("++", start) or line.startswith("--", start):
            mutation_prefix = line[start : start + 2]
            variable_start = start + 2
        if variable_start >= len(line) or line[variable_start] != "$":
            return None, start

        variable_end = variable_start
        canonical_unscoped = False
        if line.startswith("${", variable_start):
            close = line.find("}", variable_start + 2)
            if close == -1:
                return None, start
            variable_content = line[variable_start + 2 : close]
            if ":" in variable_content:
                _, variable_name = variable_content.split(":", 1)
            else:
                variable_name = variable_content
            variable_end = close + 1
        else:
            match = re.match(r"\$((?:[A-Za-z_][A-Za-z0-9_]*):)?([A-Za-z_][A-Za-z0-9_]*)", line[variable_start:])
            if match is None:
                return None, start
            scope = match.group(1) or ""
            variable_name = match.group(2)
            variable_end = variable_start + match.end()
            canonical_unscoped = scope == "" and variable_name == "stage3AuthorizationMarker"

        if variable_name.lower() != "stage3authorizationmarker":
            return None, start

        operator_start = variable_end
        while operator_start < len(line) and line[operator_start].isspace():
            operator_start += 1
        operator = ""
        if mutation_prefix:
            operator = mutation_prefix
        elif line.startswith("??=", operator_start):
            operator = "??="
        elif operator_start < len(line) and line[operator_start : operator_start + 2] in {
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "++",
            "--",
        }:
            operator = line[operator_start : operator_start + 2]
        elif operator_start < len(line) and line[operator_start] == "=":
            operator = "="
        if not operator:
            return None, variable_end

        statement_end = len(line)
        scan_i = operator_start + len(operator)
        while scan_i < len(line):
            if line[scan_i] == "`":
                end = scan_i
                while end < len(line) and line[end] == "`":
                    end += 1
                if (end - scan_i) % 2 == 0:
                    scan_i = end
                elif end < len(line):
                    scan_i = end + 1
                else:
                    scan_i = end
                continue
            if line[scan_i] in {";", "}"}:
                statement_end = scan_i
                break
            scan_i += 1
        event_text = line[variable_start:statement_end].strip()
        if operator == "=" and canonical_unscoped and top_level:
            return event_text, variable_end
        return "NONCANONICAL_STAGE3_AUTHORIZATION_MARKER_EVENT: " + line[start:statement_end].strip(), variable_end

    lines = builder_text.splitlines()

    def backtick_escape_end(line: str, start: int, line_index: int) -> tuple[int, bool, bool]:
        if start >= len(line) or line[start] != "`":
            return start, False, True
        end = start
        while end < len(line) and line[end] == "`":
            end += 1
        count = end - start
        if count % 2 == 0:
            return end, True, True
        if end < len(line):
            return end + 1, True, True
        return end, True, line_index + 1 < len(lines)

    def subexpression_at(line_index: int, start: int) -> tuple[str, int, int, bool]:
        content: list[str] = []
        current_line_index = line_index
        i = start
        depth = 1
        sub_in_block_comment = False
        sub_in_single_quoted_string = False
        sub_in_double_quoted_string = False

        while current_line_index < len(lines):
            line = lines[current_line_index]
            if current_line_index != line_index:
                content.append("\n")
                i = 0
            while i < len(line):
                if sub_in_block_comment:
                    end = line.find("#>", i)
                    if end == -1:
                        content.append(line[i:])
                        i = len(line)
                        continue
                    content.append(line[i : end + 2])
                    i = end + 2
                    sub_in_block_comment = False
                    continue
                if sub_in_single_quoted_string:
                    content.append(line[i])
                    if line[i] == "'":
                        if i + 1 < len(line) and line[i + 1] == "'":
                            i += 1
                            content.append(line[i])
                        else:
                            sub_in_single_quoted_string = False
                    i += 1
                    continue
                if sub_in_double_quoted_string:
                    content.append(line[i])
                    if line[i] == "`":
                        if i + 1 < len(line):
                            i += 1
                            content.append(line[i])
                        i += 1
                        continue
                    if line[i] == '"':
                        sub_in_double_quoted_string = False
                    i += 1
                    continue
                if line.startswith("<#", i):
                    content.append("<#")
                    sub_in_block_comment = True
                    i += 2
                    continue
                if line[i] == "#":
                    content.append(line[i:])
                    i = len(line)
                    continue
                if line[i] == "'":
                    content.append(line[i])
                    sub_in_single_quoted_string = True
                    i += 1
                    continue
                if line[i] == '"':
                    content.append(line[i])
                    sub_in_double_quoted_string = True
                    i += 1
                    continue
                next_i, consumed_escape, escape_complete = backtick_escape_end(line, i, current_line_index)
                if consumed_escape:
                    content.append(line[i:next_i])
                    if not escape_complete:
                        return "".join(content), current_line_index, next_i, False
                    i = next_i
                    continue
                if line[i] == "(":
                    depth += 1
                elif line[i] == ")":
                    depth -= 1
                    if depth == 0:
                        return "".join(content), current_line_index, i + 1, True
                content.append(line[i])
                i += 1
            current_line_index += 1
        return "".join(content), current_line_index, 0, False

    def add_expandable_subexpression_events() -> bool:
        complete = True
        scan_in_block_comment = False
        scan_in_single_quoted_string = False
        scan_in_double_quoted_string = False
        scan_here_string_end: str | None = None
        line_index = 0

        while line_index < len(lines):
            raw_line = lines[line_index]
            if scan_here_string_end is not None:
                if raw_line.strip() == scan_here_string_end:
                    scan_here_string_end = None
                    line_index += 1
                    continue
                if scan_here_string_end == '"@':
                    i = 0
                    while i < len(raw_line):
                        next_i, consumed_escape, escape_complete = backtick_escape_end(raw_line, i, line_index)
                        if consumed_escape:
                            if not escape_complete:
                                complete = False
                                return complete
                            i = next_i
                            continue
                        if raw_line.startswith("$(", i):
                            subexpr, end_line, end_i, subexpr_complete = subexpression_at(line_index, i + 2)
                            if not subexpr_complete:
                                complete = False
                                return complete
                            sub_assignments, sub_complete = executable_stage3_authorization_marker_assignments(subexpr)
                            complete = complete and sub_complete
                            for event in sub_assignments:
                                if event.startswith("NONCANONICAL_STAGE3_AUTHORIZATION_MARKER_EVENT: "):
                                    assignments.append(event)
                                else:
                                    assignments.append("NONCANONICAL_STAGE3_AUTHORIZATION_MARKER_EVENT: " + event)
                            if end_line == line_index:
                                i = end_i
                            else:
                                break
                            continue
                        i += 1
                line_index += 1
                continue

            i = 0
            while i < len(raw_line):
                if scan_in_single_quoted_string:
                    if raw_line[i] == "'":
                        if i + 1 < len(raw_line) and raw_line[i + 1] == "'":
                            i += 2
                            continue
                        scan_in_single_quoted_string = False
                    i += 1
                    continue
                if scan_in_double_quoted_string:
                    next_i, consumed_escape, escape_complete = backtick_escape_end(raw_line, i, line_index)
                    if consumed_escape:
                        if not escape_complete:
                            complete = False
                            return complete
                        i = next_i
                        continue
                    if raw_line.startswith("$(", i):
                        subexpr, end_line, end_i, subexpr_complete = subexpression_at(line_index, i + 2)
                        if not subexpr_complete:
                            complete = False
                            return complete
                        sub_assignments, sub_complete = executable_stage3_authorization_marker_assignments(subexpr)
                        complete = complete and sub_complete
                        for event in sub_assignments:
                            if event.startswith("NONCANONICAL_STAGE3_AUTHORIZATION_MARKER_EVENT: "):
                                assignments.append(event)
                            else:
                                assignments.append("NONCANONICAL_STAGE3_AUTHORIZATION_MARKER_EVENT: " + event)
                        if end_line == line_index:
                            i = end_i
                        else:
                            i = len(raw_line)
                        continue
                    if raw_line[i] == '"':
                        scan_in_double_quoted_string = False
                    i += 1
                    continue
                if scan_in_block_comment:
                    end = raw_line.find("#>", i)
                    if end == -1:
                        i = len(raw_line)
                        continue
                    i = end + 2
                    scan_in_block_comment = False
                    continue
                if raw_line.startswith("<#", i):
                    scan_in_block_comment = True
                    i += 2
                    continue
                if raw_line[i] == "#":
                    break
                if raw_line.startswith("@'", i):
                    scan_here_string_end = "'@"
                    break
                if raw_line.startswith('@"', i):
                    scan_here_string_end = '"@'
                    break
                if raw_line[i] == "'":
                    scan_in_single_quoted_string = True
                    i += 1
                    continue
                if raw_line[i] == '"':
                    scan_in_double_quoted_string = True
                    i += 1
                    continue
                next_i, consumed_escape, escape_complete = backtick_escape_end(raw_line, i, line_index)
                if consumed_escape:
                    if not escape_complete:
                        complete = False
                        return complete
                    i = next_i
                    continue
                i += 1
            line_index += 1

        return (
            complete
            and not scan_in_block_comment
            and scan_here_string_end is None
            and not scan_in_single_quoted_string
            and not scan_in_double_quoted_string
        )

    expandable_subexpressions_complete = add_expandable_subexpression_events()

    for line_index, raw_line in enumerate(lines):
        if here_string_end is not None:
            if raw_line.strip() == here_string_end:
                here_string_end = None
            continue

        code = ""
        i = 0
        while i < len(raw_line):
            if in_single_quoted_string:
                if raw_line[i] == "'":
                    if i + 1 < len(raw_line) and raw_line[i + 1] == "'":
                        i += 2
                        continue
                    in_single_quoted_string = False
                i += 1
                continue
            if in_double_quoted_string:
                if raw_line[i] == "`":
                    i += 2
                    continue
                if raw_line[i] == '"':
                    in_double_quoted_string = False
                i += 1
                continue
            if in_block_comment:
                end = raw_line.find("#>", i)
                if end == -1:
                    i = len(raw_line)
                    continue
                i = end + 2
                in_block_comment = False
                continue
            next_i, consumed_escape, escape_complete = backtick_escape_end(raw_line, i, line_index)
            if consumed_escape:
                if not escape_complete:
                    invalid_nesting = True
                    break
                code += raw_line[i:next_i]
                i = next_i
                continue
            event, next_i = variable_event_at(raw_line, i, brace_depth == 0 and parenthesis_depth == 0)
            if event is not None:
                assignments.append(event)
                i = next_i
                continue
            if raw_line.startswith("${", i):
                close = raw_line.find("}", i + 2)
                if close == -1:
                    invalid_nesting = True
                    break
                code += raw_line[i : close + 1]
                i = close + 1
                continue
            if raw_line.startswith("<#", i):
                in_block_comment = True
                i += 2
                continue
            if raw_line[i] == "#":
                break
            if raw_line.startswith("@'", i) or raw_line.startswith('@"', i):
                code += raw_line[i : i + 2]
                here_string_end = "'@" if raw_line.startswith("@'", i) else '"@'
                break
            if raw_line[i] == "'":
                code += raw_line[i]
                i += 1
                while i < len(raw_line):
                    code += raw_line[i]
                    if raw_line[i] == "'":
                        if i + 1 < len(raw_line) and raw_line[i + 1] == "'":
                            i += 1
                            code += raw_line[i]
                        else:
                            i += 1
                            break
                    i += 1
                else:
                    in_single_quoted_string = True
                continue
            if raw_line[i] == '"':
                code += raw_line[i]
                i += 1
                while i < len(raw_line):
                    code += raw_line[i]
                    if raw_line[i] == "`":
                        if i + 1 < len(raw_line):
                            i += 1
                            code += raw_line[i]
                        i += 1
                        continue
                    if raw_line[i] == '"':
                        i += 1
                        break
                    i += 1
                else:
                    in_double_quoted_string = True
                continue
            if raw_line[i] == "{":
                brace_depth += 1
            elif raw_line[i] == "}":
                if brace_depth == 0:
                    invalid_nesting = True
                else:
                    brace_depth -= 1
            elif raw_line[i] == "(":
                parenthesis_depth += 1
            elif raw_line[i] == ")":
                if parenthesis_depth == 0:
                    invalid_nesting = True
                else:
                    parenthesis_depth -= 1
            code += raw_line[i]
            i += 1
    return (
        assignments,
        not in_block_comment
        and here_string_end is None
        and not in_single_quoted_string
        and not in_double_quoted_string
        and brace_depth == 0
        and parenthesis_depth == 0
        and not invalid_nesting
        and expandable_subexpressions_complete,
    )


def stage3_authorization_marker_assignments(builder_text: str) -> list[str]:
    assignments, complete = executable_stage3_authorization_marker_assignments(builder_text)
    return assignments if complete else []


def stage3_authorization_marker_assignment_is_exact(builder_text: str) -> bool:
    assignments, complete = executable_stage3_authorization_marker_assignments(builder_text)
    return complete and assignments == [
        EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT
    ]


def check_builder_stage3_authorization_marker_assignment(text: str) -> None:
    if not stage3_authorization_marker_assignment_is_exact(text):
        die("Stage 3 authorization marker assignment is not exact")


def builder_has_correct_stage3_authorization_marker() -> bool:
    return stage3_authorization_marker_assignment_is_exact(read("build_v400_fixed_release_zip_from_head.ps1"))


def normalized_stage3_builder_sha256(builder_bytes: bytes) -> str:
    normalized = builder_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(normalized).hexdigest().upper()


def builder_has_expected_stage3_builder_normalized_sha256() -> bool:
    return (
        normalized_stage3_builder_sha256((ROOT / "build_v400_fixed_release_zip_from_head.ps1").read_bytes())
        == EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256
    )


def check_builder_stage3_normalized_sha256() -> None:
    if not builder_has_expected_stage3_builder_normalized_sha256():
        die("Stage 3 builder normalized SHA-256 is not exact")


def stage3_authorization_marker_runtime_connection_self_check() -> dict[str, bool]:
    exact_names = stage3_authorization_marker_assignment_is_exact.__code__.co_names
    check_names = check_builder_stage3_authorization_marker_assignment.__code__.co_names
    sha_check_names = check_builder_stage3_normalized_sha256.__code__.co_names
    check_builder_names = check_builder.__code__.co_names
    main_names = main.__code__.co_names
    return {
        "pure_assignment_validator_callable": callable(executable_stage3_authorization_marker_assignments),
        "exact_assignment_validator_callable": callable(stage3_authorization_marker_assignment_is_exact),
        "builder_guard_callable": callable(check_builder_stage3_authorization_marker_assignment),
        "normalized_sha_guard_callable": callable(check_builder_stage3_normalized_sha256),
        "check_builder_callable": callable(check_builder),
        "main_callable": callable(main),
        "exact_validator_uses_pure_helper_once": exact_names.count(
            "executable_stage3_authorization_marker_assignments"
        )
        == 1,
        "builder_guard_uses_exact_validator_once": check_names.count("stage3_authorization_marker_assignment_is_exact")
        == 1,
        "normalized_sha_guard_uses_expected_sha_helper_once": sha_check_names.count(
            "builder_has_expected_stage3_builder_normalized_sha256"
        )
        == 1,
        "check_builder_uses_builder_guard_once": check_builder_names.count(
            "check_builder_stage3_authorization_marker_assignment"
        )
        == 1,
        "check_builder_uses_normalized_sha_guard_once": check_builder_names.count("check_builder_stage3_normalized_sha256")
        == 1,
        "main_default_path_uses_check_builder_once": main_names.count("check_builder") == 1,
    }


def stage3_authorization_marker_assignment_self_check() -> dict[str, bool]:
    new = EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT
    old = '$stage3AuthorizationMarker = "Control D Stage 3:\\s*`r?`nAUTHORIZED_FOR_ONE_TIME_BUILD"'
    wrong = '$stage3AuthorizationMarker = "Control D Stage 3 authorization:\\s*`r?`nNOT_AUTHORIZED"'
    unrelated = '"Control D Stage 3 authorization:" + "AUTHORIZED_FOR_ONE_TIME_BUILD"'
    block_old = "<#\n" + old + "\n#>\n" + new
    here_old_single = "@'\n" + old + "\n'@\n" + new
    here_old_double = '@"\n' + old + '\n"@\n' + new
    same_line_block_old = "<# " + old + " #> " + new
    multiline_single_new = "'\n" + new + "\n'"
    multiline_double_new = '"\n' + new + '\n"'
    quoted_markers = "'<# #> # @'' @\"" + "\n'\n" + new
    unrelated_string_before_new = "'unrelated\nstring'\n" + new
    unrelated_string_after_new = new + "\n'unrelated\nstring'"
    closing_single_then_new = "'ignored\n' " + new
    closing_double_then_new = '"ignored' + "\n" + '" ' + new
    readonly_reference = new + "\nif ($authorizationText -notmatch $stage3AuthorizationMarker) { throw 'blocked' }"
    target_like_variables = (
        '$stage3AuthorizationMarkerBackup = "unrelated"\n'
        '$myStage3AuthorizationMarker = "unrelated"\n'
        + new
    )
    line_comment_assignment = "# if ($true) { " + wrong + " }\n" + new
    block_comment_assignment = "<# if ($true) { " + wrong + " } #>\n" + new
    here_string_assignment = "@'\nif ($true) { " + wrong + " }\n'@\n" + new
    multiline_string_assignment = "'\nif ($true) { " + wrong + " }\n'\n" + new
    nested_canonical = "if ($false) {\n" + new + "\n}"
    script_block_canonical = "& {\n" + new + "\n}"
    function_canonical = "function Set-Marker {\n" + new + "\n}"
    parentheses_canonical = "(\n" + new + "\n)"
    unrelated_function_before = "function Get-Unrelated {\nWrite-Output ok\n}\n" + new
    unrelated_function_after = new + "\nfunction Get-Unrelated {\nWrite-Output ok\n}"
    unrelated_braced_reference = "${unrelated}\n" + new
    comment_nesting = "# { ( ) }\n" + new
    block_comment_nesting = "<# { ( ) } #>\n" + new
    here_string_nesting = "@'\n{ ( ) }\n'@\n" + new
    normal_string_nesting = "'\n{ ( ) }\n'\n" + new
    quoted_scoped_readonly = new + "\n'$SCRIPT:Stage3AuthorizationMarker = \"wrong\"'"
    return {
        "exact_new_assignment_accepted": stage3_authorization_marker_assignment_is_exact(new),
        "old_only_rejected": not stage3_authorization_marker_assignment_is_exact(old),
        "new_plus_old_rejected": not stage3_authorization_marker_assignment_is_exact(new + "\n" + old),
        "duplicate_new_rejected": not stage3_authorization_marker_assignment_is_exact(new + "\n" + new),
        "missing_assignment_rejected": not stage3_authorization_marker_assignment_is_exact(""),
        "wrong_token_rejected": not stage3_authorization_marker_assignment_is_exact(wrong),
        "unrelated_label_token_text_rejected": not stage3_authorization_marker_assignment_is_exact(unrelated),
        "commented_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact("# " + old + "\n" + new),
        "commented_new_only_rejected": not stage3_authorization_marker_assignment_is_exact("# " + new),
        "block_commented_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(block_old),
        "single_quoted_here_string_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(
            here_old_single
        ),
        "double_quoted_here_string_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(
            here_old_double
        ),
        "same_line_block_comment_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(
            same_line_block_old
        ),
        "block_commented_new_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            "<#\n" + new + "\n#>"
        ),
        "same_line_block_commented_new_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            "<# " + new + " #>"
        ),
        "single_quoted_here_string_new_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            "@'\n" + new + "\n'@"
        ),
        "double_quoted_here_string_new_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '@"\n' + new + '\n"@'
        ),
        "unclosed_block_comment_rejected": not stage3_authorization_marker_assignment_is_exact("<#\n" + new),
        "unclosed_single_quoted_here_string_rejected": not stage3_authorization_marker_assignment_is_exact(
            "@'\n" + new
        ),
        "unclosed_double_quoted_here_string_rejected": not stage3_authorization_marker_assignment_is_exact(
            '@"\n' + new
        ),
        "multiline_normal_single_quoted_string_new_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            multiline_single_new
        ),
        "multiline_normal_double_quoted_string_new_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            multiline_double_new
        ),
        "unclosed_normal_single_quoted_string_rejected": not stage3_authorization_marker_assignment_is_exact(
            "'\n" + new
        ),
        "unclosed_normal_double_quoted_string_rejected": not stage3_authorization_marker_assignment_is_exact(
            '"\n' + new
        ),
        "normal_quoted_string_new_without_executable_assignment_rejected": not stage3_authorization_marker_assignment_is_exact(
            "'" + new + "'"
        ),
        "multiline_normal_single_quoted_string_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(
            "'\n" + old + "\n'\n" + new
        ),
        "multiline_normal_double_quoted_string_old_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(
            '"\n' + old + '\n"\n' + new
        ),
        "normal_quoted_string_markers_plus_exact_new_accepted": stage3_authorization_marker_assignment_is_exact(
            quoted_markers
        ),
        "complete_multiline_unrelated_string_before_new_accepted": stage3_authorization_marker_assignment_is_exact(
            unrelated_string_before_new
        ),
        "complete_multiline_unrelated_string_after_new_accepted": stage3_authorization_marker_assignment_is_exact(
            unrelated_string_after_new
        ),
        "closing_single_quote_same_line_then_new_accepted": stage3_authorization_marker_assignment_is_exact(
            closing_single_then_new
        ),
        "closing_double_quote_same_line_then_new_accepted": stage3_authorization_marker_assignment_is_exact(
            closing_double_then_new
        ),
        "runtime_connection_self_check": all(stage3_authorization_marker_runtime_connection_self_check().values()),
        "canonical_new_plus_wrong_after_semicolon_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "; " + wrong
        ),
        "canonical_new_plus_duplicate_after_semicolon_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "; " + new
        ),
        "canonical_new_plus_wrong_inside_if_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "\nif ($true) { " + wrong + " }"
        ),
        "canonical_new_plus_wrong_inside_script_block_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "\n& { " + wrong + " }"
        ),
        "canonical_new_plus_wrong_inside_parentheses_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "\n(" + wrong + ")"
        ),
        "alternate_case_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '$Stage3AuthorizationMarker = "wrong"'
        ),
        "canonical_new_plus_alternate_case_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n$STAGE3AUTHORIZATIONMARKER = "wrong"'
        ),
        "braced_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '${stage3AuthorizationMarker} = "wrong"'
        ),
        "canonical_new_plus_braced_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n${stage3AuthorizationMarker} = "wrong"'
        ),
        "script_scoped_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '$script:stage3AuthorizationMarker = "wrong"'
        ),
        "canonical_new_plus_script_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n$script:stage3AuthorizationMarker = "wrong"'
        ),
        "local_scoped_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '$local:stage3AuthorizationMarker = "wrong"'
        ),
        "canonical_new_plus_compound_assignment_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "\n" + "$stage3AuthorizationMarker += 'wrong'"
        ),
        "canonical_new_plus_increment_decrement_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "\n" + "$stage3AuthorizationMarker++\n--$stage3AuthorizationMarker"
        ),
        "wrong_inline_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            'if ($true) { $stage3AuthorizationMarker = "wrong" }'
        ),
        "canonical_assignment_plus_later_readonly_reference_accepted": stage3_authorization_marker_assignment_is_exact(
            readonly_reference
        ),
        "target_like_prefix_suffix_variable_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            target_like_variables
        ),
        "target_assignment_text_inside_line_comment_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            line_comment_assignment
        ),
        "target_assignment_text_inside_block_comment_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            block_comment_assignment
        ),
        "target_assignment_text_inside_here_string_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            here_string_assignment
        ),
        "target_assignment_text_inside_multiline_string_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            multiline_string_assignment
        ),
        "canonical_plus_upper_script_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n$SCRIPT:Stage3AuthorizationMarker = "wrong"'
        ),
        "canonical_plus_mixed_script_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n$ScRiPt:Stage3AuthorizationMarker = "wrong"'
        ),
        "canonical_plus_upper_local_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n$LOCAL:Stage3AuthorizationMarker = "wrong"'
        ),
        "canonical_plus_braced_script_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n${script:stage3AuthorizationMarker} = "wrong"'
        ),
        "canonical_plus_braced_upper_script_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n${SCRIPT:Stage3AuthorizationMarker} = "wrong"'
        ),
        "canonical_plus_braced_local_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n${local:Stage3AuthorizationMarker} = "wrong"'
        ),
        "canonical_plus_braced_global_scoped_wrong_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n${GLOBAL:Stage3AuthorizationMarker} = "wrong"'
        ),
        "scoped_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '$private:stage3AuthorizationMarker = "wrong"'
        ),
        "braced_scoped_assignment_only_rejected": not stage3_authorization_marker_assignment_is_exact(
            '${SCRIPT:Stage3AuthorizationMarker} = "wrong"'
        ),
        "canonical_assignment_only_inside_if_rejected": not stage3_authorization_marker_assignment_is_exact(
            nested_canonical
        ),
        "canonical_assignment_only_inside_script_block_rejected": not stage3_authorization_marker_assignment_is_exact(
            script_block_canonical
        ),
        "canonical_assignment_only_inside_function_rejected": not stage3_authorization_marker_assignment_is_exact(
            function_canonical
        ),
        "canonical_assignment_only_inside_multiline_parentheses_rejected": not stage3_authorization_marker_assignment_is_exact(
            parentheses_canonical
        ),
        "canonical_top_level_plus_nested_canonical_duplicate_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + "\n" + nested_canonical
        ),
        "canonical_top_level_plus_nested_wrong_assignment_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\nif ($false) {\n$stage3AuthorizationMarker = "wrong"\n}'
        ),
        "unmatched_opening_brace_rejected": not stage3_authorization_marker_assignment_is_exact("{\n" + new),
        "unmatched_closing_brace_rejected": not stage3_authorization_marker_assignment_is_exact(new + "\n}"),
        "unmatched_opening_parenthesis_rejected": not stage3_authorization_marker_assignment_is_exact("(\n" + new),
        "unmatched_closing_parenthesis_rejected": not stage3_authorization_marker_assignment_is_exact(new + "\n)"),
        "top_level_canonical_assignment_only_accepted": stage3_authorization_marker_assignment_is_exact(new),
        "complete_unrelated_function_followed_by_top_level_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            unrelated_function_before
        ),
        "top_level_canonical_followed_by_complete_unrelated_function_accepted": stage3_authorization_marker_assignment_is_exact(
            unrelated_function_after
        ),
        "unrelated_braced_reference_followed_by_top_level_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            unrelated_braced_reference
        ),
        "braces_parentheses_inside_line_comment_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            comment_nesting
        ),
        "braces_parentheses_inside_block_comment_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            block_comment_nesting
        ),
        "braces_parentheses_inside_here_string_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            here_string_nesting
        ),
        "braces_parentheses_inside_normal_multiline_string_plus_canonical_accepted": stage3_authorization_marker_assignment_is_exact(
            normal_string_nesting
        ),
        "canonical_plus_readonly_scoped_looking_text_inside_string_accepted": stage3_authorization_marker_assignment_is_exact(
            quoted_scoped_readonly
        ),
        "canonical_plus_ordinary_readonly_target_reference_accepted": stage3_authorization_marker_assignment_is_exact(
            readonly_reference
        ),
    }


def stage3_authorization_marker_expandable_subexpression_self_check() -> dict[str, bool]:
    new = EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT
    wrong = '$stage3AuthorizationMarker = "wrong"'
    unclosed_assignments, unclosed_complete = executable_stage3_authorization_marker_assignments(
        new + '\n"$($stage3AuthorizationMarker = "wrong"'
    )
    return {
        "one_line_double_quoted_subexpression_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$($stage3AuthorizationMarker = \'wrong\')"'
        ),
        "multiline_double_quoted_subexpression_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(\n$stage3AuthorizationMarker = \'wrong\'\n)"'
        ),
        "double_quoted_here_string_subexpression_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n@"\n$($stage3AuthorizationMarker = \'wrong\')\n"@'
        ),
        "nested_subexpression_target_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$($($stage3AuthorizationMarker = \'wrong\'))"'
        ),
        "scoped_braced_case_variant_subexpression_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(${SCRIPT:Stage3AuthorizationMarker} = \'wrong\')"'
        ),
        "compound_and_increment_subexpression_mutations_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$($stage3AuthorizationMarker += \'wrong\'; ++$stage3AuthorizationMarker; $stage3AuthorizationMarker--)"'
        ),
        "readonly_target_reference_in_subexpression_accepted": stage3_authorization_marker_assignment_is_exact(
            new + '\n"$($stage3AuthorizationMarker)"'
        ),
        "escaped_subexpression_text_accepted": stage3_authorization_marker_assignment_is_exact(
            new + '\n"`$($stage3AuthorizationMarker = \'wrong\')"'
        ),
        "single_quoted_string_subexpression_text_accepted": stage3_authorization_marker_assignment_is_exact(
            new + "\n'$($stage3AuthorizationMarker = \"wrong\")'"
        ),
        "single_quoted_here_string_subexpression_text_accepted": stage3_authorization_marker_assignment_is_exact(
            new + "\n@'\n$($stage3AuthorizationMarker = \"wrong\")\n'@"
        ),
        "unclosed_subexpression_in_expandable_string_rejected_as_incomplete": (
            bool(unclosed_assignments) and not unclosed_complete
        ),
        "comments_and_quoted_strings_inside_subexpression_preserved": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(# comment\n\'$stage3AuthorizationMarker = \"ignored\"\'\n' + wrong + '\n)"'
        ),
    }


def stage3_authorization_marker_backtick_escape_self_check() -> dict[str, bool]:
    new = EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT
    wrong = "$stage3AuthorizationMarker = 'wrong'"
    terminal_assignments, terminal_complete = executable_stage3_authorization_marker_assignments(
        new + '\n"$(Write-Output foo`'
    )
    return {
        "escaped_closing_parenthesis_subexpression_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output foo`); ' + wrong + ')"'
        ),
        "here_string_escaped_closing_parenthesis_subexpression_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n@"\n$(Write-Output foo`); ' + wrong + ')\n"@'
        ),
        "escaped_opening_parenthesis_does_not_change_depth": stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output foo`(ignored))"'
        ),
        "escaped_quote_does_not_change_string_state": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output `"; ' + wrong + ')"'
        ),
        "escaped_hash_does_not_start_comment": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output `#; ' + wrong + ')"'
        ),
        "escaped_dollar_does_not_start_target_event_or_subexpression": stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(`$stage3AuthorizationMarker = \'wrong\')"'
        ),
        "double_backtick_then_closing_parenthesis_is_structural": stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output ``); ' + wrong + ')"'
        ),
        "triple_backtick_then_closing_parenthesis_is_escaped": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output ```); ' + wrong + ')"'
        ),
        "backtick_line_continuation_then_target_mutation_rejected": not stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output foo`\n' + wrong + ')"'
        ),
        "readonly_target_reference_after_escaped_closing_parenthesis_accepted": stage3_authorization_marker_assignment_is_exact(
            new + '\n"$(Write-Output foo`); $stage3AuthorizationMarker)"'
        ),
        "terminal_incomplete_backtick_fails_closed": bool(terminal_assignments) and not terminal_complete,
    }


def stage3_builder_normalized_sha256_self_check() -> dict[str, bool]:
    current = (ROOT / "build_v400_fixed_release_zip_from_head.ps1").read_bytes()
    normalized = current.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf = normalized.replace(b"\n", b"\r\n")
    one_byte_mutation = current[:-1] + (b"\n" if current[-1:] != b"\n" else b"X")
    marker_mutation = current.replace(
        b"Control D Stage 3 authorization:",
        b"Control D Stage 3 authorization mutation:",
        1,
    )
    added_statement = current + b"\nWrite-Output 'unexpected'\n"
    return {
        "current_builder_bytes_accepted": normalized_stage3_builder_sha256(current)
        == EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256,
        "lf_form_accepted": normalized_stage3_builder_sha256(normalized) == EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256,
        "crlf_form_accepted": normalized_stage3_builder_sha256(crlf) == EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256,
        "one_byte_content_mutation_rejected": normalized_stage3_builder_sha256(one_byte_mutation)
        != EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256,
        "marker_mutation_rejected": normalized_stage3_builder_sha256(marker_mutation)
        != EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256,
        "added_executable_statement_rejected": normalized_stage3_builder_sha256(added_statement)
        != EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256,
    }


def stage3_authorization_contract_self_check() -> dict[str, bool]:
    lf = "Control D Stage 3 authorization:\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    crlf = "Control D Stage 3 authorization:\r\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    old = "Control D Stage 3:\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    missing_token = "Control D Stage 3 authorization:\nNOT_AUTHORIZED"
    new_plus_old = lf + "\n" + old
    unrelated_between = "Control D Stage 3 authorization:\nnot related\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    return {
        "lf_contract_accepted": stage3_authorization_contract_is_present(lf),
        "crlf_contract_accepted": stage3_authorization_contract_is_present(crlf),
        "current_docs_contract_accepted": stage3_authorization_contract_is_present(current_docs_text()),
        "old_stage3_label_rejected": not stage3_authorization_contract_is_present(old),
        "new_plus_old_rejected": not stage3_authorization_contract_is_present(new_plus_old),
        "authorization_label_missing_rejected": not stage3_authorization_contract_is_present(old),
        "token_missing_rejected": not stage3_authorization_contract_is_present(missing_token),
        "unrelated_between_label_and_token_rejected": not stage3_authorization_contract_is_present(unrelated_between),
        "builder_marker_assignment_correct": builder_has_correct_stage3_authorization_marker(),
        "builder_normalized_sha_correct": builder_has_expected_stage3_builder_normalized_sha256(),
        "builder_assignment_self_check": all(stage3_authorization_marker_assignment_self_check().values()),
    }


def check_committed_stage2a_surface() -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE1_COMMIT}..{CONTROL_D_STAGE2A_COMMIT}"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE1_COMMIT}..{CONTROL_D_STAGE2A_COMMIT}").splitlines()
    if not validate_stage2a_committed_surface(commit_count, lines):
        die("Clean committed Stage 2-A surface is not exact one-commit M12")
    check_protected_delta_empty(CONTROL_D_STAGE1_COMMIT, CONTROL_D_STAGE2A_COMMIT)


def check_committed_corrective_surface() -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE2A_COMMIT}..{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE2A_COMMIT}..{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}").splitlines()
    if not validate_corrective_committed_surface(commit_count, lines):
        die("Clean committed corrective surface is not exact one-commit M2")
    check_protected_delta_empty(CONTROL_D_STAGE2A_COMMIT, CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT)


def check_committed_stage2_acceptance_sync_surface() -> None:
    commit_count = int(
        git_out("rev-list", "--count", f"{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}..{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}")
    )
    lines = git_out(
        "diff", "--name-status", f"{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}..{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}"
    ).splitlines()
    if not validate_acceptance_sync_committed_surface(commit_count, lines):
        die("Clean committed Stage 2 acceptance-sync surface is not exact one-commit M12")
    check_protected_delta_empty(CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT, CONTROL_D_STAGE2_ACCEPTANCE_COMMIT)


def check_committed_stage3_authorization_sync_surface() -> None:
    commit_count = int(
        git_out("rev-list", "--count", f"{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}..{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}")
    )
    lines = git_out(
        "diff",
        "--name-status",
        f"{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}..{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}",
    ).splitlines()
    if not validate_stage3_authorization_sync_committed_surface(commit_count, lines):
        die("Clean committed Stage 3 authorization-sync surface is not exact one-commit M12")
    check_protected_delta_empty(CONTROL_D_STAGE2_ACCEPTANCE_COMMIT, CONTROL_D_STAGE3_AUTHORIZATION_COMMIT)


def check_committed_stage3_builder_auth_guard_corrective_surface() -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}..HEAD"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}..HEAD").splitlines()
    if not validate_stage3_builder_auth_guard_corrective_committed_surface(commit_count, lines):
        die("Clean committed Stage 3 builder authorization guard corrective surface is not exact one-commit M3")
    check_stage3_builder_auth_guard_corrective_protected_delta(CONTROL_D_STAGE3_AUTHORIZATION_COMMIT, "HEAD")


def clean_committed_source_guard_plan():
    return (
        check_committed_stage1_surface,
        check_committed_stage2a_surface,
        check_committed_corrective_surface,
        check_committed_stage2_acceptance_sync_surface,
        check_committed_stage3_authorization_sync_surface,
        check_committed_stage3_builder_auth_guard_corrective_surface,
    )


def check_clean_committed_source_guards() -> None:
    subprocess.run(["git", "merge-base", "--is-ancestor", CONTROL_D_STAGE2A_COMMIT, "HEAD"], cwd=ROOT, check=True)
    for guard in clean_committed_source_guard_plan():
        guard()


def clean_committed_source_guard_plan_self_check() -> dict[str, bool]:
    plan = clean_committed_source_guard_plan()
    names = [guard.__name__ for guard in plan]
    expected = [
        "check_committed_stage1_surface",
        "check_committed_stage2a_surface",
        "check_committed_corrective_surface",
        "check_committed_stage2_acceptance_sync_surface",
        "check_committed_stage3_authorization_sync_surface",
        "check_committed_stage3_builder_auth_guard_corrective_surface",
    ]
    code_names = set(verify_clean_source_tree.__code__.co_names)
    return {
        "exact_order": names == expected,
        "guard_count_exact_6": len(plan) == 6,
        "all_callable": all(callable(guard) for guard in plan),
        "no_duplicate_guards": len(set(names)) == len(names),
        "source_tree_runtime_uses_shared_guard_plan": "check_clean_committed_source_guards" in code_names,
    }


def determine_mode() -> str:
    if git_out("branch", "--show-current") != "main":
        die("branch must be main")
    check_committed_stage2a_surface()
    check_committed_corrective_surface()
    check_committed_stage2_acceptance_sync_surface()
    entries = status_entries()
    if entries:
        head = git_out("rev-parse", "HEAD")
        origin = git_out("rev-parse", "origin/main")
        if head == CONTROL_D_STAGE1_COMMIT and origin == CONTROL_D_STAGE1_COMMIT:
            check_dirty_surface(entries, STAGE2A_MODIFIED)
            return "DIRTY_STAGE2A_CANDIDATE"
        if head == CONTROL_D_STAGE2A_COMMIT and origin == CONTROL_D_STAGE2A_COMMIT:
            check_dirty_surface(entries, CORRECTIVE_SURFACE)
            return "DIRTY_STAGE2_PREFLIGHT_GUARD_CORRECTIVE_CANDIDATE"
        if head != CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT:
            if head == CONTROL_D_STAGE2_ACCEPTANCE_COMMIT and origin == CONTROL_D_STAGE2_ACCEPTANCE_COMMIT:
                check_dirty_surface(entries, STAGE3_AUTHORIZATION_SYNC_MODIFIED)
                return "DIRTY_STAGE3_AUTHORIZATION_SYNC_CANDIDATE"
            if head == CONTROL_D_STAGE3_AUTHORIZATION_COMMIT and origin == CONTROL_D_STAGE3_AUTHORIZATION_COMMIT:
                check_dirty_surface(entries, STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED)
                return "DIRTY_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_CANDIDATE"
            die("dirty candidate HEAD mismatch")
        if origin != CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT:
            die("dirty candidate origin/main mismatch")
        check_dirty_surface(entries, STAGE2_ACCEPTANCE_SYNC_MODIFIED)
        return "DIRTY_STAGE2_ACCEPTANCE_SYNC_CANDIDATE"
    subprocess.run(["git", "merge-base", "--is-ancestor", CONTROL_D_STAGE2_ACCEPTANCE_COMMIT, "HEAD"], cwd=ROOT, check=True)
    if git_out("rev-parse", "HEAD") == CONTROL_D_STAGE2A_COMMIT:
        return "CLEAN_COMMITTED_TOOLING"
    if git_out("rev-parse", "HEAD") == CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT:
        return "CLEAN_COMMITTED_STAGE2_PREFLIGHT_GUARD_CORRECTIVE"
    if git_out("rev-parse", "HEAD") == CONTROL_D_STAGE2_ACCEPTANCE_COMMIT:
        head = git_out("rev-parse", "HEAD")
        origin = git_out("rev-parse", "origin/main")
        return acceptance_sync_clean_mode_after_surface_validation(True, head, origin)
    head = git_out("rev-parse", "HEAD")
    origin = git_out("rev-parse", "origin/main")
    if head == CONTROL_D_STAGE3_AUTHORIZATION_COMMIT:
        check_committed_stage3_authorization_sync_surface()
        return stage3_authorization_sync_clean_mode_after_surface_validation(True, head, origin)
    check_committed_stage3_authorization_sync_surface()
    check_committed_stage3_builder_auth_guard_corrective_surface()
    return stage3_builder_auth_guard_corrective_clean_mode_after_surface_validation(True, head, origin)


def check_versions() -> None:
    require(read("backend/app/version.py"), 'APP_VERSION = "4.0.0"', "Backend version")
    require(read("app/pubspec.yaml"), "version: 4.0.0+5", "Flutter version")
    require(read("scripts/check_v20x_application_version_metadata.py"), '"4.0.0": "5"', "version mapping")


def check_current_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current small commit", "DRC v4.0.0 Release Preparation Protocol Control D Stage 3 Authorization"),
            ("current implementation", "DRC v4.0.0 Release Preparation Protocol Control D Stage 3 Authorization"),
            ("current implementation state", "STAGE3_AUTHORIZATION_SYNC / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control C implementation commit", BASELINE),
            ("Control D", "CURRENT / NOT_COMPLETED"),
            ("Control D Stage 1", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control D Stage 1 implementation commit", CONTROL_D_STAGE1_COMMIT),
            ("Control D Stage 1 surface", "13 files / M10 A3 D0"),
            ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"),
            ("Control D Stage 3", "BUILD_EXACTLY_ONCE / AUTHORIZED / NOT_RUN"),
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
        "Stage 1 implemented",
        "build_v400_fixed_release_zip_from_head.ps1",
        "scripts/check_v400_fixed_release_zip.py",
        "13 files / M10 A3 D0",
        "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED",
        "AUTHORIZED_FOR_ONE_TIME_BUILD",
    ):
        require(protocol, needle, "protocol")

    contract = read("docs/v400_fixed_release_zip.md")
    for needle in (
        "credential-free, provider-free, private-evidence-free",
        "builder invocation count:\n0",
        "fixed ZIP:\nNOT_BUILT",
        "release source HEAD:\nNOT_RECORDED",
        "verification HEAD:\nNOT_RECORDED",
        "fixed ZIP SHA-256:\nNOT_RECORDED",
        "AI Character Framework is not bundled.",
        "## Stage 3 Authorization-Sync Stop Rule",
    ):
        require(contract, needle, "fixed ZIP contract")
    if current_docs_text().count(STAGE2_ACCEPTED) != 2:
        die("Stage 2 accepted marker occurrence is not exact 2")
    if current_docs_text().count(STAGE2_AUTHORIZATION) != 0:
        die("Stage 2 authorization marker was not consumed")
    if current_docs_text().count(STAGE3_AUTHORIZATION) != 2:
        die("Stage 3 authorization marker occurrence is not exact 2")
    require(protocol, STAGE3_AUTHORIZATION, "Stage 3 protocol authorization token")
    require(contract, STAGE3_AUTHORIZATION, "Stage 3 fixed ZIP authorization token")
    for token in (STAGE4_AUTHORIZATION,):
        reject(protocol, token, "future documentation authorization token")
        reject(contract, token, "future documentation authorization token")

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
        "Control D Stage 3 authorization:",
        "AUTHORIZED_FOR_ONE_TIME_BUILD",
        "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED",
        "git worktree add --detach",
        "build_release.bat release",
        "$buildInvocationCount++",
        "verification_status: not-run",
        "next_action: verify-this-same-zip-without-rebuilding",
    ):
        require(text, needle, "builder")
    check_builder_stage3_authorization_marker_assignment(text)
    check_builder_stage3_normalized_sha256()


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


def check_protected_surface(mode: str) -> None:
    lines = git_out("diff", "--name-status", "--", *PROTECTED_PATHS).splitlines()
    if mode == "DIRTY_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_CANDIDATE":
        if not validate_stage3_builder_auth_guard_corrective_protected_delta(lines):
            die("Dirty Stage 3 builder authorization guard corrective protected delta is not exact builder M")
        return
    if not validate_empty_protected_delta(lines):
        die("Protected product/build/release surface diff is not empty")


def check_committed_stage1_surface() -> None:
    lines = git_out("diff", "--name-status", f"{BASELINE}..{CONTROL_D_STAGE1_COMMIT}").splitlines()
    if not validate_stage1_surface(lines):
        die("Committed Stage 1 surface is not exact M10 A3")
    protected = git_out("diff", "--name-status", f"{BASELINE}..{CONTROL_D_STAGE1_COMMIT}", "--", *PROTECTED_PATHS)
    if not validate_stage1_protected_delta(protected.splitlines()):
        die("Committed Stage 1 protected delta is not exact builder A")


def check_protected_delta_empty(start: str, end: str) -> None:
    lines = git_out("diff", "--name-status", f"{start}..{end}", "--", *PROTECTED_PATHS).splitlines()
    if not validate_empty_protected_delta(lines):
        die("Post-Stage 1 protected product/build/release surface diff is not empty")


def check_stage3_builder_auth_guard_corrective_protected_delta(start: str, end: str) -> None:
    lines = git_out("diff", "--name-status", f"{start}..{end}", "--", *PROTECTED_PATHS).splitlines()
    if not validate_stage3_builder_auth_guard_corrective_protected_delta(lines):
        die("Stage 3 builder authorization guard corrective protected delta is not exact builder M")


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
    return stage3_authorization_contract_is_present(text) and STAGE2_ACCEPTED in text


def docs_have_stage4_authorization() -> bool:
    text = current_docs_text()
    return STAGE4_AUTHORIZATION in text and STAGE3_ARTIFACT_READY in text


def stage2_is_authorized_or_accepted(text: str) -> bool:
    return STAGE2_AUTHORIZATION in text or STAGE2_ACCEPTED in text


def stage3_build_is_authorized(text: str) -> bool:
    return stage3_authorization_contract_is_present(text) and STAGE2_ACCEPTED in text


def stage4_zip_verification_is_authorized(text: str) -> bool:
    return STAGE4_AUTHORIZATION in text and STAGE3_ARTIFACT_READY in text


def check_stage2a_authorization_boundary() -> None:
    current_text = current_docs_text()
    if current_text.count(STAGE2_ACCEPTED) != 2:
        die("Stage 2 accepted marker occurrence is not exact 2")
    if current_text.count(STAGE2_AUTHORIZATION) != 0:
        die("Stage 2 authorization marker was not consumed")
    if not docs_have_stage2_authorization():
        die("Stage 2 authorization is missing from current docs")
    if current_text.count(STAGE3_AUTHORIZATION) != 2:
        die("Stage 3 authorization marker occurrence is not exact 2")
    if not docs_have_stage3_authorization():
        die("Stage 3 authorization is missing from current docs")
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
    if not default_policy.current_doc_checks_required or not default_policy.authorization_boundary_check_required:
        die("default mode policy missing Stage 2-A checks")
    if source_policy.current_doc_checks_required or source_policy.authorization_boundary_check_required:
        die("source-tree mode policy should not apply Stage 2 acceptance current-doc checks")
    if release_policy.current_doc_checks_required or release_policy.authorization_boundary_check_required:
        die("release-zip mode policy should not apply Stage 2 acceptance current-doc checks")
    if current_text.count(STAGE2_ACCEPTED) != 2:
        die("Stage 2 accepted marker occurrence is not exact 2")
    if current_text.count(STAGE2_AUTHORIZATION) != 0:
        die("Stage 2 authorization marker was not consumed")
    if not stage2_is_authorized_or_accepted(current_text):
        die("current docs do not authorize Stage 2")
    if current_text.count(STAGE3_AUTHORIZATION) != 2:
        die("Stage 3 authorization marker occurrence is not exact 2")
    if not stage3_build_is_authorized(current_text):
        die("current docs do not authorize Stage 3")
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
    if not all(stage1_surface_self_check().values()):
        die("Stage 1 surface validator self-check failed")
    if not all(stage1_protected_delta_self_check().values()):
        die("Stage 1 protected delta validator self-check failed")
    if not all(post_stage1_protected_delta_self_check().values()):
        die("post-Stage 1 protected delta validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_protected_delta_self_check().values()):
        die("Stage 3 builder authorization guard corrective protected delta validator self-check failed")
    if not all(stage2a_committed_surface_self_check().values()):
        die("Stage 2-A committed surface validator self-check failed")
    if not all(corrective_dirty_surface_self_check().values()):
        die("corrective dirty surface validator self-check failed")
    if not all(corrective_committed_surface_self_check().values()):
        die("corrective committed surface validator self-check failed")
    if not all(acceptance_sync_dirty_surface_self_check().values()):
        die("Stage 2 acceptance-sync dirty surface validator self-check failed")
    if not all(acceptance_sync_committed_surface_self_check().values()):
        die("Stage 2 acceptance-sync committed surface validator self-check failed")
    if not all(acceptance_sync_origin_state_self_check().values()):
        die("Stage 2 acceptance-sync origin-state validator self-check failed")
    if not all(stage3_authorization_sync_dirty_surface_self_check().values()):
        die("Stage 3 authorization-sync dirty surface validator self-check failed")
    if not all(stage3_authorization_sync_committed_surface_self_check().values()):
        die("Stage 3 authorization-sync committed surface validator self-check failed")
    if not all(stage3_authorization_sync_origin_state_self_check().values()):
        die("Stage 3 authorization-sync origin-state validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_dirty_surface_self_check().values()):
        die("Stage 3 builder authorization guard corrective dirty surface validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_committed_surface_self_check().values()):
        die("Stage 3 builder authorization guard corrective committed surface validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_origin_state_self_check().values()):
        die("Stage 3 builder authorization guard corrective origin-state validator self-check failed")
    if not all(stage3_authorization_contract_self_check().values()):
        die("Stage 3 authorization marker contract self-check failed")
    if not all(stage3_authorization_marker_assignment_self_check().values()):
        die("Stage 3 authorization marker assignment self-check failed")
    if not all(stage3_authorization_marker_expandable_subexpression_self_check().values()):
        die("Stage 3 authorization marker expandable subexpression self-check failed")
    if not all(stage3_authorization_marker_backtick_escape_self_check().values()):
        die("Stage 3 authorization marker backtick escape self-check failed")
    if not all(stage3_builder_normalized_sha256_self_check().values()):
        die("Stage 3 builder normalized SHA-256 self-check failed")
    if not current_state_prose_is_consistent(current_text):
        die("Stage 3 current-state prose consistency failed")
    if not all(current_state_prose_consistency_self_check().values()):
        die("Stage 3 current-state prose consistency self-check failed")
    if not all(clean_committed_source_guard_plan_self_check().values()):
        die("clean committed source guard plan self-check failed")
    if flutter_test_command("flutter") != ["flutter", "test", "--no-pub", "--reporter", "expanded"]:
        die("shared Flutter test command missing expanded reporter")
    if not repository_source_tree_uses_shared_flutter_test_command():
        die("repository source-tree path does not use shared Flutter test command")
    if not temporary_extraction_uses_shared_flutter_test_command():
        die("temporary extraction path does not use shared Flutter test command")


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


def flutter_test_command(command: str) -> list[str]:
    return [command, "test", "--no-pub", "--reporter", "expanded"]


def repository_source_tree_uses_shared_flutter_test_command() -> bool:
    return flutter_test_command("flutter")[1:] == ["test", "--no-pub", "--reporter", "expanded"]


def temporary_extraction_uses_shared_flutter_test_command() -> bool:
    return flutter_test_command("flutter")[1:] == ["test", "--no-pub", "--reporter", "expanded"]


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
    check_clean_committed_source_guards()
    run_checked([sys.executable, "-m", "compileall", "-q", "backend", "scripts"])
    out = run_checked([sys.executable, "-m", "pytest", "-q", "backend/tests"])
    if not re.search(rf"\b{EXPECTED_BACKEND_TESTS} passed\b", out):
        die("Backend full count mismatch")
    if with_flutter:
        command = require_absolute_flutter_command(flutter_command)
        check_flutter_identity(command)
        prepare_flutter_dependencies(ROOT / "app", command, temporary_extraction=False)
        run_checked([command, "analyze", "--no-pub"], ROOT / "app")
        out = run_checked(flutter_test_command(command), ROOT / "app")
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
        out = run_checked(flutter_test_command(command), source / "app")
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
    if policy.current_doc_checks_required:
        check_current_docs()
    if policy.artifact_policy == "artifact-absent":
        check_release_outputs_absent()
    if policy.name == "default":
        check_protected_surface(mode)
        check_source_only_hygiene()
        check_no_contradictions()
    if policy.authorization_boundary_check_required:
        check_stage2a_authorization_boundary()
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
        stage1_surface_checks = stage1_surface_self_check()
        stage1_protected_checks = stage1_protected_delta_self_check()
        post_stage1_protected_checks = post_stage1_protected_delta_self_check()
        stage3_builder_protected_checks = stage3_builder_auth_guard_corrective_protected_delta_self_check()
        stage2a_surface_checks = stage2a_committed_surface_self_check()
        corrective_dirty_checks = corrective_dirty_surface_self_check()
        corrective_committed_checks = corrective_committed_surface_self_check()
        acceptance_sync_dirty_checks = acceptance_sync_dirty_surface_self_check()
        acceptance_sync_committed_checks = acceptance_sync_committed_surface_self_check()
        acceptance_sync_origin_checks = acceptance_sync_origin_state_self_check()
        stage3_dirty_checks = stage3_authorization_sync_dirty_surface_self_check()
        stage3_committed_checks = stage3_authorization_sync_committed_surface_self_check()
        stage3_origin_checks = stage3_authorization_sync_origin_state_self_check()
        stage3_builder_dirty_checks = stage3_builder_auth_guard_corrective_dirty_surface_self_check()
        stage3_builder_committed_checks = stage3_builder_auth_guard_corrective_committed_surface_self_check()
        stage3_builder_origin_checks = stage3_builder_auth_guard_corrective_origin_state_self_check()
        stage3_marker_contract_checks = stage3_authorization_contract_self_check()
        stage3_marker_assignment_checks = stage3_authorization_marker_assignment_self_check()
        stage3_marker_expandable_subexpression_checks = stage3_authorization_marker_expandable_subexpression_self_check()
        stage3_marker_backtick_checks = stage3_authorization_marker_backtick_escape_self_check()
        stage3_builder_normalized_sha_checks = stage3_builder_normalized_sha256_self_check()
        prose_checks = current_state_prose_consistency_self_check()
        clean_guard_plan_checks = clean_committed_source_guard_plan_self_check()
        flutter_plan_checks = {
            "repository_with_package_config": flutter_dependency_plan(False, True) == "use-existing-package-config",
            "repository_without_package_config": flutter_dependency_plan(False, False) == "reject-missing-package-config",
            "temporary_with_package_config": flutter_dependency_plan(True, True) == "use-existing-package-config",
            "temporary_without_package_config": flutter_dependency_plan(True, False) == "pub-get-offline",
        }
        print("v400_fixed_release_zip_tooling_status: stage3-authorization-sync-implemented-awaiting-review")
        print(
            "v400_fixed_release_zip_exact_stage1_surface: "
            f"{stage1_surface_checks['exact_m10_a3_accepted']}"
        )
        print("v400_fixed_release_zip_stage1_change_file_count: 13")
        print(f"v400_fixed_release_zip_stage1_implementation_commit: {CONTROL_D_STAGE1_COMMIT}")
        print(
            "v400_fixed_release_zip_stage1_protected_exact_builder_a: "
            f"{stage1_protected_checks['exact_builder_a_accepted']}"
        )
        print(
            "v400_fixed_release_zip_post_stage1_protected_delta_empty: "
            f"{post_stage1_protected_checks['empty_accepted']}"
        )
        print(
            "v400_stage3_builder_auth_guard_corrective_protected_exact_builder_m_self_check: "
            f"{all(stage3_builder_protected_checks.values())}"
        )
        print("v400_fixed_release_zip_exact_stage2a_surface: True")
        print("v400_fixed_release_zip_stage2a_change_file_count: 12")
        print(f"v400_stage2a_dirty_m12_validator_self_check: {all(stage2a_surface_checks.values())}")
        print(
            "v400_stage2a_clean_exact_one_commit_validator_self_check: "
            f"{all(stage2a_surface_checks.values())}"
        )
        print(
            "v400_stage2a_clean_exact_m12_validator_self_check: "
            f"{stage2a_surface_checks['exact_one_commit_m12_accepted']}"
        )
        print(
            "v400_corrective_dirty_exact_m2_validator_self_check: "
            f"{all(corrective_dirty_checks.values())}"
        )
        print(
            "v400_corrective_clean_exact_one_commit_m2_validator_self_check: "
            f"{all(corrective_committed_checks.values())}"
        )
        print(
            "v400_stage2_acceptance_sync_dirty_exact_m12_validator_self_check: "
            f"{all(acceptance_sync_dirty_checks.values())}"
        )
        print(
            "v400_stage2_acceptance_sync_future_clean_exact_one_commit_m12_validator_self_check: "
            f"{all(acceptance_sync_committed_checks.values())}"
        )
        print(
            "v400_stage2_acceptance_sync_origin_state_validator_self_check: "
            f"{all(acceptance_sync_origin_checks.values())}"
        )
        print(
            "v400_stage2_acceptance_sync_origin_base_not_pushed_self_check: "
            f"{acceptance_sync_origin_checks['base_origin_accepted_as_not_pushed']}"
        )
        print(
            "v400_stage2_acceptance_sync_origin_head_pushed_self_check: "
            f"{acceptance_sync_origin_checks['head_origin_accepted_as_pushed']}"
        )
        print(
            "v400_stage2_acceptance_sync_origin_unrelated_rejected_self_check: "
            f"{acceptance_sync_origin_checks['unrelated_origin_rejected']}"
        )
        print(
            "v400_stage2_acceptance_sync_origin_empty_rejected_self_check: "
            f"{acceptance_sync_origin_checks['empty_origin_rejected']}"
        )
        print(
            "v400_stage2_acceptance_sync_origin_policy_after_surface_guard_self_check: "
            f"{acceptance_sync_origin_checks['origin_policy_blocked_before_surface_validation']}"
        )
        print(
            "v400_stage2_acceptance_sync_determine_mode_uses_origin_helper: "
            f"{acceptance_sync_origin_checks['determine_mode_references_origin_helper']}"
        )
        print(
            "v400_stage2_acceptance_sync_dirty_mode_maintained: "
            f"{acceptance_sync_origin_checks['dirty_mode_maintained']}"
        )
        print(
            "v400_stage3_authorization_sync_dirty_exact_m12_validator_self_check: "
            f"{all(stage3_dirty_checks.values())}"
        )
        print(
            "v400_stage3_authorization_sync_future_clean_exact_one_commit_m12_validator_self_check: "
            f"{all(stage3_committed_checks.values())}"
        )
        print(
            "v400_stage3_authorization_sync_origin_state_validator_self_check: "
            f"{all(stage3_origin_checks.values())}"
        )
        print(
            "v400_stage3_authorization_sync_origin_base_not_pushed_self_check: "
            f"{stage3_origin_checks['base_origin_accepted_as_not_pushed']}"
        )
        print(
            "v400_stage3_authorization_sync_origin_head_pushed_self_check: "
            f"{stage3_origin_checks['head_origin_accepted_as_pushed']}"
        )
        print(
            "v400_stage3_authorization_sync_origin_unrelated_rejected_self_check: "
            f"{stage3_origin_checks['unrelated_origin_rejected']}"
        )
        print(
            "v400_stage3_authorization_sync_origin_empty_rejected_self_check: "
            f"{stage3_origin_checks['empty_origin_rejected']}"
        )
        print(
            "v400_stage3_authorization_sync_origin_policy_after_surface_guard_self_check: "
            f"{stage3_origin_checks['origin_policy_blocked_before_surface_validation']}"
        )
        print(
            "v400_stage3_authorization_sync_determine_mode_uses_origin_helper: "
            f"{stage3_origin_checks['determine_mode_references_origin_helper']}"
        )
        print(
            "v400_stage3_authorization_sync_dirty_mode_maintained: "
            f"{stage3_origin_checks['dirty_mode_maintained']}"
        )
        print(
            "v400_stage3_builder_auth_guard_corrective_dirty_exact_m3_validator_self_check: "
            f"{all(stage3_builder_dirty_checks.values())}"
        )
        print(
            "v400_stage3_builder_auth_guard_corrective_future_clean_exact_one_commit_m3_validator_self_check: "
            f"{all(stage3_builder_committed_checks.values())}"
        )
        print(
            "v400_stage3_builder_auth_guard_corrective_origin_state_validator_self_check: "
            f"{all(stage3_builder_origin_checks.values())}"
        )
        print(
            "v400_stage3_authorization_marker_contract_self_check: "
            f"{all(stage3_marker_contract_checks.values())}"
        )
        print(
            "v400_stage3_authorization_marker_lf_crlf_self_check: "
            f"{stage3_marker_contract_checks['lf_contract_accepted'] and stage3_marker_contract_checks['crlf_contract_accepted']}"
        )
        print(
            "v400_stage3_authorization_marker_old_label_rejected_self_check: "
            f"{stage3_marker_contract_checks['old_stage3_label_rejected']}"
        )
        print(
            "v400_stage3_authorization_marker_builder_assignment_self_check: "
            f"{stage3_marker_contract_checks['builder_marker_assignment_correct']}"
        )
        print(
            "v400_stage3_authorization_marker_assignment_r7_self_check_count: "
            f"{len(stage3_marker_assignment_checks)}"
        )
        print(
            "v400_stage3_authorization_marker_assignment_r7_self_check: "
            f"{all(stage3_marker_assignment_checks.values())}"
        )
        print(
            "v400_stage3_authorization_marker_expandable_subexpression_r8_self_check_count: "
            f"{len(stage3_marker_expandable_subexpression_checks)}"
        )
        print(
            "v400_stage3_authorization_marker_expandable_subexpression_r8_self_check: "
            f"{all(stage3_marker_expandable_subexpression_checks.values())}"
        )
        print(
            "v400_stage3_authorization_marker_backtick_escape_r9_self_check_count: "
            f"{len(stage3_marker_backtick_checks)}"
        )
        print(
            "v400_stage3_authorization_marker_backtick_escape_r9_self_check: "
            f"{all(stage3_marker_backtick_checks.values())}"
        )
        print(
            "v400_stage3_builder_normalized_sha256_self_check_count: "
            f"{len(stage3_builder_normalized_sha_checks)}"
        )
        print(
            "v400_stage3_builder_normalized_sha256_self_check: "
            f"{all(stage3_builder_normalized_sha_checks.values())}"
        )
        print(
            "v400_stage3_builder_normalized_sha256_current: "
            f"{builder_has_expected_stage3_builder_normalized_sha256()}"
        )
        print(
            "v400_current_state_prose_consistency_self_check: "
            f"{all(prose_checks.values())}"
        )
        print(
            "v400_stale_stage3_current_state_phrase_rejected: "
            f"{prose_checks['stale_stage3_phrase_rejected']}"
        )
        print(
            "v400_source_tree_path_reaches_clean_committed_guard: "
            f"{all(clean_guard_plan_checks.values())}"
        )
        print(
            "v400_clean_committed_source_guard_plan_count_exact_5: "
            "False"
        )
        print(
            "v400_clean_committed_source_guard_plan_count_exact_6: "
            f"{clean_guard_plan_checks['guard_count_exact_6']}"
        )
        print("v400_fixed_release_zip_builder_invocation_count: 0")
        print("v400_fixed_release_zip_built: False")
        print("v400_control_d_stage2_accepted: True")
        print("v400_control_d_stage2_authorization_token_occurrence: 0")
        print("v400_control_d_stage2_executed: True")
        print("v400_control_d_stage2_acceptance_sync_commit: 697d0918cb8a6de5c0459324464b7d7e376b3a5a")
        print("v400_control_d_stage3_authorization_token_occurrence: 2")
        print("v400_control_d_stage3_authorized: True")
        print("v400_control_d_stage3_build_status: authorized-not-run")
        print("v400_control_d_stage4_authorized: False")
        print("v400_default_mode_uses_artifact_absent_policy: True")
        print("v400_source_tree_mode_uses_artifact_absent_policy: True")
        print("v400_release_zip_mode_uses_exact_supplied_artifact_policy: True")
        print("v400_release_zip_mode_does_not_call_absent_artifact_gate: True")
        print("v400_current_docs_stage2_accepted: True")
        print("v400_stage2_accepted_marker_occurrence: 2")
        print("v400_current_docs_stage3_authorization: True")
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
        print("v400_shared_expanded_flutter_test_command: True")
        print("v400_repository_source_tree_uses_shared_flutter_test_command: True")
        print("v400_temporary_extraction_uses_shared_flutter_test_command: True")
        print("v400_arbitrary_product_change_after_expected_source_head_rejected: True")
    print("v400_release_verifier_consumes_expected_source_head: True")
    print("v400_release_verifier_consumes_flutter_build_arguments: True")
    print("v400_release_mode_not_blocked_by_absent_artifact_gate: True")
    print("v400_control_e_authorized: False")
    print("[v400-fixed-release-zip-check] OK")


if __name__ == "__main__":
    main()
