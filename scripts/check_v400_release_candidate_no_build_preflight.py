"""Validate DRC v4.0.0 Control C and Control D Stage 3 authorization-sync boundary."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL_C_BASELINE = "5908cb5b0d88c2e8aa6370105c3d618064cb4665"
CONTROL_C_COMMIT = "4cae15573f3332cbc476557461babdfe2eb3c0bf"
CONTROL_D_STAGE1_COMMIT = "a204f6b11d25baeea67b7b7be8860c9a4f9ea945"
CONTROL_D_STAGE2A_COMMIT = "507685488fd33231dfec4bfc0f2c4532a1141de2"
CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT = "eb68cf9334f46a30c0c06d3921d59f56abb540bb"
CONTROL_D_STAGE2_ACCEPTANCE_COMMIT = "697d0918cb8a6de5c0459324464b7d7e376b3a5a"
CONTROL_D_STAGE3_AUTHORIZATION_COMMIT = "0f7418100beaedd764d4c0821973b23fa20327a2"
STAGE2_AUTHORIZATION = "AUTHORIZED_FOR_CLEAN_COMMITTED_SOURCE_PREFLIGHT"
STAGE3_AUTHORIZATION = "AUTHORIZED_FOR_ONE_TIME_BUILD"
STAGE4_AUTHORIZATION = "AUTHORIZED_FOR_SAME_ARTIFACT_VERIFICATION"
EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT = (
    '$stage3AuthorizationMarker = "Control D Stage 3 authorization:\\s*`r?`nAUTHORIZED_FOR_ONE_TIME_BUILD"'
)
EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256 = "13248D55299C57B5DD940091DB2B6738B5F7024DC3A2A3F238917E9F8315A330"
STAGE2_ACCEPTED = "Control D Stage 2:\nCLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"
STAGE2A_MODIFIED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_fixed_release_zip.md",
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_candidate_metadata.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_release_record.md",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
    "scripts/check_v400_fixed_release_zip.py",
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
    "docs/v400_release_record.md",
    "docs/v400_release_candidate_no_build_preflight.md",
    "docs/v400_fixed_release_zip.md",
)
PROTECTED_PATHS = (
    "backend/app/version.py",
    "app/pubspec.yaml",
    "scripts/check_v20x_application_version_metadata.py",
    "scripts/check_v400_release_candidate_metadata.py",
    "release_notes/v4.0.0.md",
    "backend/tests",
    "app/test",
    "app/pubspec.lock",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
    "backend/requirements-framework.txt",
    "build_release.bat",
    "build_v300_fixed_release_zip_from_head.ps1",
    "scripts/check_v300_fixed_release_zip.py",
    "build_v400_fixed_release_zip_from_head.ps1",
    "release",
)
PRIVATE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)\b[a-z]:\\users\\"),
    re.compile(r"\b(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[0-1])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)
FORBIDDEN_PACKAGE_NAMES = {".env", "credentials.json", "token.json"}
FORBIDDEN_PACKAGE_PARTS = {".git", "release", "build", "operator_evidence", "local_data", "vendor"}
PENDING_POST_EDIT_MARKER = "PENDING_POST_EDIT_" + "VERIFICATION"
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


def git_out(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("`", "").replace("*", "")


def compact(text: str) -> str:
    return " ".join(norm(text).split())


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def reject(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def require_associated(text: str, label: str, value: str, scope: str) -> None:
    pattern = rf"{re.escape(label)}\s*:?\s*\n?\s*{re.escape(value)}"
    if not re.search(pattern, norm(text), flags=re.IGNORECASE):
        raise AssertionError(f"Missing associated {scope}: {label} -> {value}")


def status_entries() -> list[tuple[str, str]]:
    raw = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    return [
        (part[:2], part[3:].replace("\\", "/"))
        for part in raw.decode("utf-8").split("\0")
        if part
    ]


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
        raise AssertionError(
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


def validate_empty_protected_delta(name_status_lines: list[str]) -> bool:
    return not any(line for line in name_status_lines)


def validate_stage3_builder_auth_guard_corrective_protected_delta(name_status_lines: list[str]) -> bool:
    return validate_exact_name_status_surface(
        name_status_lines,
        {"M": {"build_v400_fixed_release_zip_from_head.ps1"}},
    )


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
        raise AssertionError("Stage 2 acceptance-sync origin policy reached before committed surface validation")
    state = acceptance_sync_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE2_ACCEPTANCE_SYNC_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE2_ACCEPTANCE_SYNC"
    raise AssertionError("Clean Stage 2 acceptance-sync origin/main state is invalid")


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
        raise AssertionError("Stage 3 authorization-sync origin policy reached before committed surface validation")
    state = stage3_authorization_sync_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE3_AUTHORIZATION_SYNC_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE3_AUTHORIZATION_SYNC"
    raise AssertionError("Clean Stage 3 authorization-sync origin/main state is invalid")


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
        raise AssertionError(
            "Stage 3 builder authorization guard corrective origin policy reached before committed surface validation"
        )
    state = stage3_builder_auth_guard_corrective_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE"
    raise AssertionError("Clean Stage 3 builder authorization guard corrective origin/main state is invalid")


def stage2a_committed_surface_self_check() -> dict[str, bool]:
    exact = [f"M\t{path}" for path in sorted(EXPECTED_MODIFIED)]
    return {
        "exact_one_commit_m12_accepted": validate_stage2a_committed_surface(1, exact),
        "count_0_rejected": not validate_stage2a_committed_surface(0, exact),
        "count_2_rejected": not validate_stage2a_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage2a_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_stage2a_committed_surface(1, [*exact, "M\tbackend/app/version.py"]),
        "duplicate_path_rejected": not validate_stage2a_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_stage2a_committed_surface(1, [*exact[1:], "A\tREADME.md"]),
        "status_d_rejected": not validate_stage2a_committed_surface(1, [*exact[1:], "D\tREADME.md"]),
        "status_r_rejected": not validate_stage2a_committed_surface(1, [*exact[1:], "R100\tREADME.md\tREADME.md"]),
        "status_c_rejected": not validate_stage2a_committed_surface(1, [*exact[1:], "C100\tREADME.md\tREADME.md"]),
        "malformed_line_rejected": not validate_stage2a_committed_surface(1, [*exact[1:], "M README.md"]),
    }


def corrective_dirty_surface_self_check() -> dict[str, bool]:
    exact = [(" M", path) for path in sorted(CORRECTIVE_SURFACE)]
    return {
        "exact_m2_accepted": dirty_surface_is_exact(exact, CORRECTIVE_SURFACE),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], CORRECTIVE_SURFACE),
        "unexpected_path_rejected": not dirty_surface_is_exact([*exact, (" M", "README.md")], CORRECTIVE_SURFACE),
        "duplicate_path_rejected": not dirty_surface_is_exact([*exact, exact[0]], CORRECTIVE_SURFACE),
        "staged_rejected": not dirty_surface_is_exact([*exact[1:], ("M ", sorted(CORRECTIVE_SURFACE)[0])], CORRECTIVE_SURFACE),
        "untracked_rejected": not dirty_surface_is_exact([*exact, ("??", "scratch.txt")], CORRECTIVE_SURFACE),
        "status_a_rejected": not dirty_surface_is_exact([*exact[1:], (" A", sorted(CORRECTIVE_SURFACE)[0])], CORRECTIVE_SURFACE),
        "status_d_rejected": not dirty_surface_is_exact([*exact[1:], (" D", sorted(CORRECTIVE_SURFACE)[0])], CORRECTIVE_SURFACE),
        "status_r_rejected": not dirty_surface_is_exact([*exact[1:], ("R ", sorted(CORRECTIVE_SURFACE)[0])], CORRECTIVE_SURFACE),
        "status_c_rejected": not dirty_surface_is_exact([*exact[1:], ("C ", sorted(CORRECTIVE_SURFACE)[0])], CORRECTIVE_SURFACE),
    }


def corrective_committed_surface_self_check() -> dict[str, bool]:
    exact = [f"M\t{path}" for path in sorted(CORRECTIVE_SURFACE)]
    return {
        "exact_one_commit_m2_accepted": validate_corrective_committed_surface(1, exact),
        "count_0_rejected": not validate_corrective_committed_surface(0, exact),
        "count_2_rejected": not validate_corrective_committed_surface(2, exact),
        "missing_path_rejected": not validate_corrective_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_corrective_committed_surface(1, [*exact, "M\tREADME.md"]),
        "duplicate_path_rejected": not validate_corrective_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "A\t" + sorted(CORRECTIVE_SURFACE)[0]]),
        "status_d_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "D\t" + sorted(CORRECTIVE_SURFACE)[0]]),
        "status_r_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "R100\told\t" + sorted(CORRECTIVE_SURFACE)[0]]),
        "status_c_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "C100\told\t" + sorted(CORRECTIVE_SURFACE)[0]]),
        "malformed_line_rejected": not validate_corrective_committed_surface(1, [*exact[1:], "M " + sorted(CORRECTIVE_SURFACE)[0]]),
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
    try:
        stage3_authorization_sync_clean_mode_after_surface_validation(
            False, synthetic_head, CONTROL_D_STAGE2_ACCEPTANCE_COMMIT
        )
        blocked_before_surface_validation = False
    except AssertionError:
        blocked_before_surface_validation = True
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
    stale = corrected + "\nWhen authorized in the future, actual build must create"
    missing = "\n".join(REQUIRED_STAGE3_CURRENT_STATE_PHRASES[:-1])
    stage4_future = corrected + "\nfuture accepted document adds the tooling-defined Stage 4 same-artifact authorization marker"
    return {
        "corrected_current_state_prose_accepted": current_state_prose_is_consistent(corrected),
        "stale_stage3_phrase_rejected": not current_state_prose_is_consistent(stale),
        "required_current_state_phrase_missing_rejected": not current_state_prose_is_consistent(missing),
        "stage4_future_boundary_prose_accepted": current_state_prose_is_consistent(stage4_future),
    }


def current_docs_text() -> str:
    return "\n".join(read(relative) for relative in CURRENT_DOCS)


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


def check_builder_stage3_authorization_marker_assignment() -> None:
    if not stage3_authorization_marker_assignment_is_exact(read("build_v400_fixed_release_zip_from_head.ps1")):
        raise AssertionError("Stage 3 authorization marker assignment is not exact")


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
        raise AssertionError("Stage 3 builder normalized SHA-256 is not exact")


def stage3_authorization_marker_runtime_connection_self_check() -> dict[str, bool]:
    exact_names = stage3_authorization_marker_assignment_is_exact.__code__.co_names
    check_names = check_builder_stage3_authorization_marker_assignment.__code__.co_names
    sha_check_names = check_builder_stage3_normalized_sha256.__code__.co_names
    protocol_names = check_protocol_and_records.__code__.co_names
    main_names = main.__code__.co_names
    return {
        "pure_assignment_validator_callable": callable(executable_stage3_authorization_marker_assignments),
        "exact_assignment_validator_callable": callable(stage3_authorization_marker_assignment_is_exact),
        "builder_guard_callable": callable(check_builder_stage3_authorization_marker_assignment),
        "normalized_sha_guard_callable": callable(check_builder_stage3_normalized_sha256),
        "protocol_validation_callable": callable(check_protocol_and_records),
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
        "protocol_validation_uses_builder_guard_once": protocol_names.count(
            "check_builder_stage3_authorization_marker_assignment"
        )
        == 1,
        "protocol_validation_uses_normalized_sha_guard_once": protocol_names.count(
            "check_builder_stage3_normalized_sha256"
        )
        == 1,
        "main_default_path_uses_protocol_validation_once": main_names.count("check_protocol_and_records") == 1,
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
        raise AssertionError("Clean committed Stage 2-A surface is not exact one-commit M12")


def check_committed_corrective_surface() -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE2A_COMMIT}..{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE2A_COMMIT}..{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}").splitlines()
    if not validate_corrective_committed_surface(commit_count, lines):
        raise AssertionError("Clean committed corrective surface is not exact one-commit M2")


def check_committed_stage2_acceptance_sync_surface() -> None:
    commit_count = int(
        git_out("rev-list", "--count", f"{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}..{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}")
    )
    lines = git_out(
        "diff", "--name-status", f"{CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT}..{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}"
    ).splitlines()
    if not validate_acceptance_sync_committed_surface(commit_count, lines):
        raise AssertionError("Clean committed Stage 2 acceptance-sync surface is not exact one-commit M12")


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
        raise AssertionError("Clean committed Stage 3 authorization-sync surface is not exact one-commit M12")


def check_committed_stage3_builder_auth_guard_corrective_surface() -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}..HEAD"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}..HEAD").splitlines()
    if not validate_stage3_builder_auth_guard_corrective_committed_surface(commit_count, lines):
        raise AssertionError(
            "Clean committed Stage 3 builder authorization guard corrective surface is not exact one-commit M3"
        )
    check_stage3_builder_auth_guard_corrective_protected_delta(CONTROL_D_STAGE3_AUTHORIZATION_COMMIT, "HEAD")


def determine_mode() -> str:
    if git_out("branch", "--show-current") != "main":
        raise AssertionError("Unexpected branch")
    check_committed_stage2a_surface()
    check_committed_corrective_surface()
    check_committed_stage2_acceptance_sync_surface()
    entries = status_entries()
    if entries:
        head = git_out("rev-parse", "HEAD")
        origin = git_out("rev-parse", "origin/main")
        if head == CONTROL_D_STAGE1_COMMIT and origin == CONTROL_D_STAGE1_COMMIT:
            check_dirty_surface(entries, STAGE2A_MODIFIED)
            return "DIRTY_CONTROL_D_STAGE2A_CANDIDATE"
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
            raise AssertionError("Dirty candidate HEAD mismatch")
        if origin != CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT:
            raise AssertionError("Dirty candidate origin/main mismatch")
        check_dirty_surface(entries, STAGE2_ACCEPTANCE_SYNC_MODIFIED)
        return "DIRTY_STAGE2_ACCEPTANCE_SYNC_CANDIDATE"
    subprocess.run(["git", "merge-base", "--is-ancestor", CONTROL_D_STAGE2_ACCEPTANCE_COMMIT, "HEAD"], cwd=ROOT, check=True)
    if git_out("rev-parse", "HEAD") == CONTROL_D_STAGE2A_COMMIT:
        return "CLEAN_COMMITTED_STATIC"
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
    require(read("backend/app/version.py"), 'APP_VERSION = "4.0.0"', "Backend APP_VERSION")
    require(read("app/pubspec.yaml"), "version: 4.0.0+5", "Flutter version")
    require(read("scripts/check_v20x_application_version_metadata.py"), '"4.0.0": "5"', "version mapping")


def check_release_state_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current small commit", "DRC v4.0.0 Release Preparation Protocol Control D Stage 3 Authorization"),
            ("current implementation", "DRC v4.0.0 Release Preparation Protocol Control D Stage 3 Authorization"),
            ("current implementation state", "STAGE3_AUTHORIZATION_SYNC / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control C implementation commit", CONTROL_C_COMMIT),
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


def check_protocol_and_records() -> None:
    protocol = read("docs/v400_release_preparation_protocol.md")
    for needle in (
        "Control D Stage 1",
        "STAGE3_AUTHORIZATION_SYNC / IMPLEMENTED / AWAITING_REVIEW",
        "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
        "13 files / M10 A3 D0",
        "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED",
        "AUTHORIZED_FOR_ONE_TIME_BUILD",
        "build_v400_fixed_release_zip_from_head.ps1",
        "scripts/check_v400_fixed_release_zip.py",
    ):
        require(protocol, needle, "protocol")

    metadata = read("docs/v400_release_candidate_metadata.md")
    for label, value in (
        ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("Control D", "CURRENT / NOT_COMPLETED"),
        ("Control D Stage 1", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control D Stage 1 implementation commit", CONTROL_D_STAGE1_COMMIT),
        ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"),
        ("Control D Stage 3", "BUILD_EXACTLY_ONCE / AUTHORIZED / NOT_RUN"),
        ("Control E", "FUTURE / NOT_AUTHORIZED"),
        ("DRC v4.0.0", "NOT_RELEASED"),
    ):
        require_associated(metadata, label, value, "candidate metadata")

    record = read("docs/v400_release_record.md")
    for label, value in (
        ("Status", "PREPARED / NOT_RELEASED"),
        ("Current phase", "Control D Stage 3 Authorization STAGE3_AUTHORIZATION_SYNC / IMPLEMENTED / AWAITING_REVIEW"),
        ("Control C verification baseline", CONTROL_C_BASELINE),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("Control D Stage 1", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control D Stage 1 implementation commit", CONTROL_D_STAGE1_COMMIT),
        ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"),
        ("Control D Stage 3", "BUILD_EXACTLY_ONCE / AUTHORIZED / NOT_RUN"),
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

    preflight = read("docs/v400_release_candidate_no_build_preflight.md")
    for label, value in (
        ("Status", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("Control D Stage 1", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control D Stage 1 implementation commit", CONTROL_D_STAGE1_COMMIT),
        ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"),
        ("Python compileall", "PASS / exit 0"),
        ("Control C dedicated checker", "PASS / OK"),
        ("application version metadata checker", "PASS / OK"),
        ("source-only package hygiene", "PASS"),
        ("privacy boundary", "PASS"),
        ("git diff --check", "PASS / exit 0 / LF-to-CRLF warnings only"),
        ("release builder invocation", "NO"),
        ("release artifact creation", "NO"),
        ("Flutter release build", "NO"),
        ("provider execution", "NO"),
        ("credentials", "NO"),
        ("network", "NO"),
        ("repository stage", "NO"),
        ("commit", "NO"),
        ("push", "NO"),
        ("tag", "NO"),
        ("publication", "NO"),
        ("Backend FW-v6 focused", "62 PASS"),
        ("Backend v3 realtime preservation", "29 PASS"),
        ("Backend full", "479 PASS"),
        ("Flutter analyze", "PASS / No issues found"),
        ("Flutter FW-v6 focused corrective", "70 PASS / exit 0"),
        ("Flutter v3 realtime preservation", "328 PASS / exit 0"),
        ("Flutter full", "570 PASS"),
    ):
        require_associated(preflight, label, value, "preflight")
    for needle in (
        "Backend FW-v6 provider-free focused tests:\n62 PASS / ACCEPTED",
        "Backend v3 realtime preservation focused tests:\n29 PASS / ACCEPTED",
        "Backend full tests:\n479 PASS / ACCEPTED",
        "Flutter FW-v6 provider-free focused tests:\n70 PASS / corrective rerun exit 0",
        "Flutter v3 realtime preservation focused tests:\n328 PASS / exit 0",
        "Flutter full tests:\n570 PASS / exit 0",
        "source-only release-package hygiene:\nPASS",
    ):
        require(preflight, needle, "Control C historical guard")
    if preflight.count(PENDING_POST_EDIT_MARKER) != 0:
        raise AssertionError("PENDING_POST_EDIT_VERIFICATION marker is present")

    fixed = read("docs/v400_fixed_release_zip.md")
    for needle in (
        "credential-free, provider-free, private-evidence-free",
        "builder invocation count:\n0",
        "fixed ZIP:\nNOT_BUILT",
        "release source HEAD:\nNOT_RECORDED",
        "verification HEAD:\nNOT_RECORDED",
        "fixed ZIP SHA-256:\nNOT_RECORDED",
        "## Stage 3 Authorization-Sync Stop Rule",
    ):
        require(fixed, needle, "fixed ZIP contract")
    current_text = current_docs_text()
    if current_text.count(STAGE2_ACCEPTED) != 2:
        raise AssertionError("Stage 2 accepted marker occurrence is not exact 2")
    if current_text.count(STAGE2_AUTHORIZATION) != 0:
        raise AssertionError("Stage 2 authorization marker was not consumed")
    if not all(stage2a_committed_surface_self_check().values()):
        raise AssertionError("Stage 2-A committed surface validator self-check failed")
    if not all(corrective_dirty_surface_self_check().values()):
        raise AssertionError("corrective dirty surface validator self-check failed")
    if not all(corrective_committed_surface_self_check().values()):
        raise AssertionError("corrective committed surface validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_protected_delta_self_check().values()):
        raise AssertionError("Stage 3 builder authorization guard corrective protected delta validator self-check failed")
    if not all(acceptance_sync_dirty_surface_self_check().values()):
        raise AssertionError("Stage 2 acceptance-sync dirty validator self-check failed")
    if not all(acceptance_sync_committed_surface_self_check().values()):
        raise AssertionError("Stage 2 acceptance-sync future clean validator self-check failed")
    if not all(acceptance_sync_origin_state_self_check().values()):
        raise AssertionError("Stage 2 acceptance-sync origin-state validator self-check failed")
    if current_text.count(STAGE3_AUTHORIZATION) != 2:
        raise AssertionError("Stage 3 authorization marker occurrence is not exact 2")
    if not all(stage3_authorization_sync_dirty_surface_self_check().values()):
        raise AssertionError("Stage 3 authorization-sync dirty validator self-check failed")
    if not all(stage3_authorization_sync_committed_surface_self_check().values()):
        raise AssertionError("Stage 3 authorization-sync future clean validator self-check failed")
    if not all(stage3_authorization_sync_origin_state_self_check().values()):
        raise AssertionError("Stage 3 authorization-sync origin-state validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_dirty_surface_self_check().values()):
        raise AssertionError("Stage 3 builder authorization guard corrective dirty validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_committed_surface_self_check().values()):
        raise AssertionError("Stage 3 builder authorization guard corrective future clean validator self-check failed")
    if not all(stage3_builder_auth_guard_corrective_origin_state_self_check().values()):
        raise AssertionError("Stage 3 builder authorization guard corrective origin-state validator self-check failed")
    if not all(stage3_authorization_contract_self_check().values()):
        raise AssertionError("Stage 3 authorization marker contract self-check failed")
    if not all(stage3_authorization_marker_assignment_self_check().values()):
        raise AssertionError("Stage 3 authorization marker assignment self-check failed")
    if not all(stage3_authorization_marker_expandable_subexpression_self_check().values()):
        raise AssertionError("Stage 3 authorization marker expandable subexpression self-check failed")
    if not all(stage3_authorization_marker_backtick_escape_self_check().values()):
        raise AssertionError("Stage 3 authorization marker backtick escape self-check failed")
    if not all(stage3_builder_normalized_sha256_self_check().values()):
        raise AssertionError("Stage 3 builder normalized SHA-256 self-check failed")
    check_builder_stage3_authorization_marker_assignment()
    check_builder_stage3_normalized_sha256()
    if not current_state_prose_is_consistent(current_text):
        raise AssertionError("Stage 3 current-state prose consistency failed")
    if not all(current_state_prose_consistency_self_check().values()):
        raise AssertionError("Stage 3 current-state prose consistency self-check failed")
    reject(current_text, STAGE4_AUTHORIZATION, "future authorization marker")
    if current_text.count(PENDING_POST_EDIT_MARKER) != 0:
        raise AssertionError("PENDING_POST_EDIT_VERIFICATION marker is present in current docs")


def check_no_release_outputs() -> None:
    if git_out("tag", "--list", "DRC_v4.0.0"):
        raise AssertionError("DRC_v4.0.0 tag exists")
    release_root = ROOT / "release"
    if release_root.exists() and any(release_root.glob("DailyRhythmCompanion_v4.0.0_*.zip")):
        raise AssertionError("v4.0.0 release ZIP exists")


def check_protected_surface(mode: str) -> None:
    lines = git_out("diff", "--name-status", "--", *PROTECTED_PATHS).splitlines()
    if mode == "DIRTY_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_CANDIDATE":
        if not validate_stage3_builder_auth_guard_corrective_protected_delta(lines):
            raise AssertionError(
                "Dirty Stage 3 builder authorization guard corrective protected delta is not exact builder M"
            )
        return
    if not validate_empty_protected_delta(lines):
        raise AssertionError("Protected surface diff is not empty")


def check_stage3_builder_auth_guard_corrective_protected_delta(start: str, end: str) -> None:
    lines = git_out("diff", "--name-status", f"{start}..{end}", "--", *PROTECTED_PATHS).splitlines()
    if not validate_stage3_builder_auth_guard_corrective_protected_delta(lines):
        raise AssertionError("Stage 3 builder authorization guard corrective protected delta is not exact builder M")


def check_source_only_package_hygiene() -> None:
    for relative in git_out("ls-files").splitlines():
        normalized = relative.replace("\\", "/")
        path = Path(normalized)
        parts = set(path.parts)
        lower_name = path.name.lower()
        if lower_name in FORBIDDEN_PACKAGE_NAMES:
            raise AssertionError(f"Forbidden tracked package member: {normalized}")
        if lower_name.endswith(".zip"):
            raise AssertionError(f"Forbidden tracked ZIP: {normalized}")
        if parts & FORBIDDEN_PACKAGE_PARTS:
            raise AssertionError(f"Forbidden tracked package path: {normalized}")

    for relative in sorted(EXPECTED_MODIFIED):
        text = subprocess.check_output(["git", "diff", "--", relative], cwd=ROOT, text=True, errors="replace")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Private-looking value in candidate diff: {relative}")
    for relative in sorted(EXPECTED_ADDED):
        text = read(relative)
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                raise AssertionError(f"Private-looking value in candidate file: {relative}")


def reject_current_state_contradictions() -> None:
    current_text = "\n".join(read(relative) for relative in CURRENT_DOCS)
    for needle in (
        "v4.0.0 RELEASED",
        "fixed ZIP: BUILT",
        "fixed release ZIP: BUILT",
        "annotated tag: CREATED",
        "GitHub Release: CREATED",
        "Control E: AUTHORIZED",
        "Control D Stage 4:\nSAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED",
        "existing v3 replacement: YES",
        "/realtime/text replacement: YES",
        "real unified FW runtime: AVAILABLE",
    ):
        reject(current_text, needle, "current-state contradiction")


def main() -> None:
    mode = determine_mode()
    stage2a_surface_checks = stage2a_committed_surface_self_check()
    corrective_dirty_checks = corrective_dirty_surface_self_check()
    corrective_committed_checks = corrective_committed_surface_self_check()
    stage3_builder_protected_checks = stage3_builder_auth_guard_corrective_protected_delta_self_check()
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
    check_versions()
    check_release_state_docs()
    check_protocol_and_records()
    check_no_release_outputs()
    check_protected_surface(mode)
    check_source_only_package_hygiene()
    reject_current_state_contradictions()

    print(f"v400_release_candidate_no_build_preflight_source_state: {mode}")
    print("v400_release_candidate_no_build_preflight_control_c_status: completed-verified-reviewed-accepted-committed-pushed-closed")
    print(f"v400_release_candidate_no_build_preflight_control_c_implementation_commit: {CONTROL_C_COMMIT}")
    print("v400_release_candidate_no_build_preflight_control_d_stage1_status: completed-verified-reviewed-accepted-committed-pushed-closed")
    print(f"v400_release_candidate_no_build_preflight_control_d_stage1_implementation_commit: {CONTROL_D_STAGE1_COMMIT}")
    print("v400_release_candidate_no_build_preflight_control_d_stage2_status: clean-committed-source-preflight-completed-pass-accepted")
    print("v400_release_candidate_no_build_preflight_control_d_stage2_acceptance_sync_commit: 697d0918cb8a6de5c0459324464b7d7e376b3a5a")
    print("v400_release_candidate_no_build_preflight_stage2_accepted_marker_occurrence: 2")
    print("v400_release_candidate_no_build_preflight_stage2_authorization_token_occurrence: 0")
    print(
        "v400_release_candidate_no_build_preflight_stage2a_dirty_m12_validator_self_check: "
        f"{all(stage2a_surface_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2a_clean_exact_one_commit_validator_self_check: "
        f"{all(stage2a_surface_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2a_clean_exact_m12_validator_self_check: "
        f"{stage2a_surface_checks['exact_one_commit_m12_accepted']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_corrective_dirty_exact_m2_validator_self_check: "
        f"{all(corrective_dirty_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_corrective_clean_exact_one_commit_m2_validator_self_check: "
        f"{all(corrective_committed_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_auth_guard_corrective_protected_exact_builder_m_self_check: "
        f"{all(stage3_builder_protected_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_dirty_m12_validator_self_check: "
        f"{all(acceptance_sync_dirty_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_future_clean_m12_validator_self_check: "
        f"{all(acceptance_sync_committed_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_origin_state_validator_self_check: "
        f"{all(acceptance_sync_origin_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_origin_base_not_pushed_self_check: "
        f"{acceptance_sync_origin_checks['base_origin_accepted_as_not_pushed']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_origin_head_pushed_self_check: "
        f"{acceptance_sync_origin_checks['head_origin_accepted_as_pushed']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_origin_unrelated_rejected_self_check: "
        f"{acceptance_sync_origin_checks['unrelated_origin_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_origin_empty_rejected_self_check: "
        f"{acceptance_sync_origin_checks['empty_origin_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_origin_policy_after_surface_guard_self_check: "
        f"{acceptance_sync_origin_checks['origin_policy_blocked_before_surface_validation']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_determine_mode_uses_origin_helper: "
        f"{acceptance_sync_origin_checks['determine_mode_references_origin_helper']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage2_acceptance_sync_dirty_mode_maintained: "
        f"{acceptance_sync_origin_checks['dirty_mode_maintained']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_dirty_m12_validator_self_check: "
        f"{all(stage3_dirty_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_future_clean_exact_one_commit_m12_validator_self_check: "
        f"{all(stage3_committed_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_origin_state_validator_self_check: "
        f"{all(stage3_origin_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_origin_base_not_pushed_self_check: "
        f"{stage3_origin_checks['base_origin_accepted_as_not_pushed']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_origin_head_pushed_self_check: "
        f"{stage3_origin_checks['head_origin_accepted_as_pushed']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_origin_unrelated_rejected_self_check: "
        f"{stage3_origin_checks['unrelated_origin_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_origin_empty_rejected_self_check: "
        f"{stage3_origin_checks['empty_origin_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_origin_policy_after_surface_guard_self_check: "
        f"{stage3_origin_checks['origin_policy_blocked_before_surface_validation']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_determine_mode_uses_origin_helper: "
        f"{stage3_origin_checks['determine_mode_references_origin_helper']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_sync_dirty_mode_maintained: "
        f"{stage3_origin_checks['dirty_mode_maintained']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_auth_guard_corrective_dirty_exact_m3_validator_self_check: "
        f"{all(stage3_builder_dirty_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_auth_guard_corrective_future_clean_exact_one_commit_m3_validator_self_check: "
        f"{all(stage3_builder_committed_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_auth_guard_corrective_origin_state_validator_self_check: "
        f"{all(stage3_builder_origin_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_contract_self_check: "
        f"{all(stage3_marker_contract_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_lf_crlf_self_check: "
        f"{stage3_marker_contract_checks['lf_contract_accepted'] and stage3_marker_contract_checks['crlf_contract_accepted']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_old_label_rejected_self_check: "
        f"{stage3_marker_contract_checks['old_stage3_label_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_builder_assignment_self_check: "
        f"{stage3_marker_contract_checks['builder_marker_assignment_correct']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_assignment_r7_self_check_count: "
        f"{len(stage3_marker_assignment_checks)}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_assignment_r7_self_check: "
        f"{all(stage3_marker_assignment_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_expandable_subexpression_r8_self_check_count: "
        f"{len(stage3_marker_expandable_subexpression_checks)}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_expandable_subexpression_r8_self_check: "
        f"{all(stage3_marker_expandable_subexpression_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_backtick_escape_r9_self_check_count: "
        f"{len(stage3_marker_backtick_checks)}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_backtick_escape_r9_self_check: "
        f"{all(stage3_marker_backtick_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_normalized_sha256_self_check_count: "
        f"{len(stage3_builder_normalized_sha_checks)}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_normalized_sha256_self_check: "
        f"{all(stage3_builder_normalized_sha_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_builder_normalized_sha256_current: "
        f"{builder_has_expected_stage3_builder_normalized_sha256()}"
    )
    print(
        "v400_release_candidate_no_build_preflight_current_state_prose_consistency_self_check: "
        f"{all(prose_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stale_stage3_current_state_phrase_rejected: "
        f"{prose_checks['stale_stage3_phrase_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_control_d_stage3_authorization_sync_status: "
        "stage3-authorization-sync-implemented-awaiting-review"
    )
    print("v400_release_candidate_no_build_preflight_backend_version: 4.0.0")
    print("v400_release_candidate_no_build_preflight_flutter_version: 4.0.0+5")
    print("v400_release_candidate_no_build_preflight_current_released: v3.0.0")
    print("v400_release_candidate_no_build_preflight_v400_released: False")
    print("v400_release_candidate_no_build_preflight_release_source_head_recorded: False")
    print("v400_release_candidate_no_build_preflight_verification_head_recorded: False")
    print("v400_release_candidate_no_build_preflight_fixed_zip_builder_invocation_count: 0")
    print("v400_release_candidate_no_build_preflight_fixed_zip_built: False")
    print("v400_release_candidate_no_build_preflight_tag_created: False")
    print("v400_release_candidate_no_build_preflight_github_release_created: False")
    print("v400_release_candidate_no_build_preflight_stage3_authorization_token_occurrence: 2")
    print("v400_release_candidate_no_build_preflight_stage3_build_authorized: True")
    print("v400_release_candidate_no_build_preflight_stage4_authorized: False")
    print("v400_release_candidate_no_build_preflight_stage_commit_push_authorized: False")
    print("v400_release_candidate_no_build_preflight_package_tag_publication_authorized: False")
    print("[v400-release-candidate-no-build-preflight-check] OK")


if __name__ == "__main__":
    main()
