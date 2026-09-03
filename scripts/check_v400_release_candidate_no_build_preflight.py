"""Validate DRC v4.0.0 Control C and Control D Stage 3 authorization-sync boundary."""

from __future__ import annotations

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
STAGE2_AUTHORIZATION = "AUTHORIZED_FOR_CLEAN_COMMITTED_SOURCE_PREFLIGHT"
STAGE3_AUTHORIZATION = "AUTHORIZED_FOR_ONE_TIME_BUILD"
STAGE4_AUTHORIZATION = "AUTHORIZED_FOR_SAME_ARTIFACT_VERIFICATION"
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
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}..HEAD"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE2_ACCEPTANCE_COMMIT}..HEAD").splitlines()
    if not validate_stage3_authorization_sync_committed_surface(commit_count, lines):
        raise AssertionError("Clean committed Stage 3 authorization-sync surface is not exact one-commit M12")


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
    check_committed_stage3_authorization_sync_surface()
    head = git_out("rev-parse", "HEAD")
    origin = git_out("rev-parse", "origin/main")
    return stage3_authorization_sync_clean_mode_after_surface_validation(True, head, origin)


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
    current_text = "\n".join(read(relative) for relative in CURRENT_DOCS)
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


def check_protected_surface() -> None:
    completed = subprocess.run(
        ["git", "diff", "--exit-code", "--", *PROTECTED_PATHS],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        raise AssertionError("Protected surface diff is not empty")


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
    acceptance_sync_dirty_checks = acceptance_sync_dirty_surface_self_check()
    acceptance_sync_committed_checks = acceptance_sync_committed_surface_self_check()
    acceptance_sync_origin_checks = acceptance_sync_origin_state_self_check()
    stage3_dirty_checks = stage3_authorization_sync_dirty_surface_self_check()
    stage3_committed_checks = stage3_authorization_sync_committed_surface_self_check()
    stage3_origin_checks = stage3_authorization_sync_origin_state_self_check()
    prose_checks = current_state_prose_consistency_self_check()
    check_versions()
    check_release_state_docs()
    check_protocol_and_records()
    check_no_release_outputs()
    check_protected_surface()
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
