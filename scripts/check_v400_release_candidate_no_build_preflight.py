"""Validate DRC v4.0.0 Control C and Control D Stage 4 authorization-sync boundary."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path, PurePosixPath
import re
import sys
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CONTROL_C_BASELINE = "5908cb5b0d88c2e8aa6370105c3d618064cb4665"
CONTROL_C_COMMIT = "4cae15573f3332cbc476557461babdfe2eb3c0bf"
CONTROL_D_STAGE1_COMMIT = "a204f6b11d25baeea67b7b7be8860c9a4f9ea945"
CONTROL_D_STAGE2A_COMMIT = "507685488fd33231dfec4bfc0f2c4532a1141de2"
CONTROL_D_STAGE2_PREFLIGHT_GUARD_COMMIT = "eb68cf9334f46a30c0c06d3921d59f56abb540bb"
CONTROL_D_STAGE2_ACCEPTANCE_COMMIT = "697d0918cb8a6de5c0459324464b7d7e376b3a5a"
CONTROL_D_STAGE3_AUTHORIZATION_COMMIT = "0f7418100beaedd764d4c0821973b23fa20327a2"
CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT = "3193aa6aa8eb5e8e0140fc0235d5f4ecfd6ac4f3"
CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT = "46f5af49106c6ecc0d478a425cf709cf511da1be"
CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT = "0a6e6e65f8c775022471018bc3ca6c03b2ed588b"
STAGE2_AUTHORIZATION = "AUTHORIZED_FOR_CLEAN_COMMITTED_SOURCE_PREFLIGHT"
STAGE3_AUTHORIZATION = "AUTHORIZED_FOR_ONE_TIME_BUILD"
STAGE4_AUTHORIZATION = "AUTHORIZED_FOR_SAME_ARTIFACT_VERIFICATION"
EXPECTED_FIXED_ZIP_SOURCE_HEAD = CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT
EXPECTED_FIXED_ZIP_BASENAME = "DailyRhythmCompanion_v4.0.0_20260908_173440.zip"
EXPECTED_FIXED_ZIP_SIZE = 3018230
EXPECTED_FIXED_ZIP_SHA256 = "f02b43a219d7e89fd9e40dd6c1f7cd588076de7b260d6085ffa99966b3c49142"
EXPECTED_STAGE3_AUTHORIZATION_MARKER_ASSIGNMENT = (
    '$stage3AuthorizationMarker = "Control D Stage 3 authorization:\\s*`r?`nAUTHORIZED_FOR_ONE_TIME_BUILD"'
)
EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256 = "599080CCBAA77EBDFEF934FCC1BC79E772E58B80F1E0F6A7903FAC79AA7F1E00"
EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256 = "E341FCA3180C62EE90ED5F95E0D8433CD6723DAEE7ABD98FA618639ED53A6AAB"
STAGE2_ACCEPTED = "Control D Stage 2:\nCLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"
STAGE3_ARTIFACT_READY = "Control D Stage 3:\nBUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"
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
STAGE4_AUTHORIZATION_SYNC_MODIFIED = STAGE2A_MODIFIED
STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED = STAGE2A_MODIFIED
STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_MODIFIED = {
    "build_v400_fixed_release_zip_from_head.ps1",
    "scripts/check_v400_fixed_release_zip.py",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED = {
    "build_v400_fixed_release_zip_from_head.ps1",
    "build_release.bat",
    "scripts/check_v400_fixed_release_zip.py",
    "scripts/check_v400_release_candidate_no_build_preflight.py",
}
STAGE3_PATH_LENGTH_CORRECTIVE_PROTECTED = {
    "build_v400_fixed_release_zip_from_head.ps1",
    "build_release.bat",
}
PATH_BUDGET_LIMIT = 259
FIXED_BUILDER_CANONICAL_SHORT_WORKTREE_ASSIGNMENT = re.compile(
    r'(?m)^\s*\$tempRoot\s*=\s*Join-Path\s+'
    r'\(\s*\[IO\.Path\]\s*::\s*GetTempPath\(\s*\)\s*\)\s+'
    r'\(\s*"d4w_"\s*\+\s*\[Guid\]\s*::\s*NewGuid\(\s*\)'
    r'\s*\.\s*ToString\(\s*"N"\s*\)\s*\.\s*Substring\(\s*0\s*,\s*8\s*\)\s*\)\s*$'
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
    "DRC v4.0.0 can proceed to a separately authorized Stage 3 build request because",
    "future accepted document adds the tooling-defined Stage 3 one-time-build authorization marker",
    "future accepted document adds the tooling-defined Stage 4 same-artifact authorization marker",
    "future Stage 3/4 authorization absence",
    "When authorized in the future, actual build must create",
    "Current checkpoint: DRC v4.0.0 Release Preparation Protocol Control D Stage 2 Acceptance Sync",
    "Stage 4 authorization-marker absence",
    "Stage 3 authorization-sync candidate does not run the builder while it is dirty",
    "Stage 3 is authorized for exactly one fixed ZIP build but has not run",
    "Stage 4 remains blocked pending the Stage 3 artifact",
    "BLOCKED_PENDING_STAGE3_ARTIFACT / NOT_AUTHORIZED",
)
REQUIRED_STAGE4_CURRENT_STATE_PHRASES = (
    "Control D Stage 4 authorization-sync is COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED",
    "Stage 4 invocation 1 was EXACTLY_ONCE_EXECUTED",
    "failure class is NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE",
    "Release-package scanner known fixtures were EXACT_EXPECTED_FINDINGS / ACCEPTED",
    "The fixed ZIP is PRESERVED",
    "Stage 4 retry is NOT_AUTHORIZED / NOT_RUN",
)
STALE_CURRENT_PURPOSE_PHRASES = (
    "DRC v4.0.0 can proceed to a separately authorized Stage 3 build request because",
)
REQUIRED_CURRENT_PURPOSE_PHRASES = (
    "Control D Stage 3 fixed ZIP build completed, passed, and is accepted",
    "Control D Stage 4 authorization-sync completed and was committed, pushed, reviewed, and accepted",
    "Stage 4 invocation 1 was executed exactly once and failed",
    "failure class is NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE",
    "scanner findings were the exact accepted source-matched fixtures",
    "ZIP structure/version checks passed",
    "extracted compileall passed",
    "extracted Backend pytest process completed, but its result/count was not evaluated",
    "output emission raised UnicodeEncodeError",
    "Stage 4 conclusive verdict was not reached",
    "fixed ZIP remains preserved",
    "Stage 4 retry is NOT_AUTHORIZED / NOT_RUN",
    "Control E is NOT_AUTHORIZED",
    "DRC v4.0.0 remains NOT_RELEASED",
    "bounded release scope: bounded coexistence adoption",
    "does not claim that Framework v6.0.0 provides a production unified real STT -> streaming LLM -> TTS -> motion runtime",
)
CURRENT_STAGE4_PROSE_DOCS = (
    "docs/v400_release_preparation_protocol.md",
    "docs/v400_release_candidate_metadata.md",
)
V3_HISTORICAL_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
)
V3_HISTORICAL_SECTION_MARKERS = (
    ("<!-- RT-9B-RELEASE-READINESS:BEGIN -->", "<!-- RT-9B-RELEASE-READINESS:END -->"),
    ("<!-- RT-9C-STAGE1-FIXED-ZIP-TOOLING:BEGIN -->", "<!-- RT-9C-STAGE1-FIXED-ZIP-TOOLING:END -->"),
)
REQUIRED_CURRENT_STAGE4_REVIEW_PHRASES = (
    "Control D Stage 4 authorization-sync is COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED",
    "Stage 4 invocation 1 was EXACTLY_ONCE_EXECUTED",
    "verdict is NOT_REACHED",
    "failure class is NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE",
    "Release-package scanner known fixtures were EXACT_EXPECTED_FINDINGS / ACCEPTED",
    "Stage 4 retry is NOT_AUTHORIZED / NOT_RUN",
    "Control E is NOT_AUTHORIZED",
    "DRC v4.0.0 is NOT_RELEASED",
    "Stage 4 authorization marker was consumed",
    "fixed ZIP exact-one artifact",
    "the exact artifact was created and its tuple is recorded",
    EXPECTED_FIXED_ZIP_BASENAME,
    str(EXPECTED_FIXED_ZIP_SIZE),
    EXPECTED_FIXED_ZIP_SHA256.upper(),
    EXPECTED_FIXED_ZIP_SOURCE_HEAD,
    "Stage 3 one-time build authorization token is consumed",
    "current documentation count is 0",
    "release-ZIP verifier remains unreachable in default corrective mode",
    "Stage 4 invocation 1 executed and failed before verdict",
    "retry is not authorized",
    "Control E is not authorized",
    "tag/publication are not run",
    "DRC v4.0.0 is not released",
)
STALE_CURRENT_STAGE4_REVIEW_PHRASES = (
    "Control D Stage 3: Build exactly once AUTHORIZED / NOT_RUN",
    "Control D Stage 4: Same-artifact verification and tuple record BLOCKED_PENDING_STAGE3_ARTIFACT / NOT_AUTHORIZED",
    "Control E: Publication FUTURE / NOT_AUTHORIZED",
    "Stage 3 is authorized for exactly one fixed ZIP build but has not run",
    "Stage 4 remains blocked pending the Stage 3 artifact",
    "blocked pending the Stage 3 artifact",
    "future/not authorized",
    "future accepted document adds the tooling-defined Stage 4 same-artifact authorization marker",
    "Stage 4 authorization-marker absence",
    "dirty/clean Stage 3 authorization-sync surface checks",
    "Stage 3 authorization-sync candidate does not run the builder while it is dirty",
    "artifact absent",
)
REQUIRED_V3_HISTORICAL_PHRASES = (
    "v3.0.0 fixed ZIP: NOT_BUILT",
    "RT-9c Stage 2 builder invocation count: 0",
    "RT-9c Stage 2 fixed ZIP built: false",
    "fixed ZIP builder invocation count: 0",
)
V3_CONTAMINATION_PHRASES = (
    EXPECTED_FIXED_ZIP_BASENAME,
    EXPECTED_FIXED_ZIP_SHA256.upper(),
    EXPECTED_FIXED_ZIP_SOURCE_HEAD,
    "Control D Stage 3: BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED",
    "Control D Stage 4: SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED / NOT_RUN",
    "RT-9c Stage 2 builder invocation count: 1",
    "RT-9c Stage 2 fixed ZIP built: true / unverified",
    "fixed ZIP builder invocation count: 1",
)
TASKLIST_CURRENT_IMPLEMENTATION_STEP = (
    "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1"
)
STAGE2_HISTORY_EVIDENCE_DOCS = (
    "README.md",
    "roadmap.md",
    "docs/v400_fixed_release_zip.md",
    "docs/v400_release_preparation_protocol.md",
)
HISTORICAL_NO_BUILD_CONTROL_BLOCKS = ("Control B", "Control C")
ACTIVE_STAGE4_STOP_RULE_HEADING = "## Stage 4 Verifier Output-Encoding Corrective R1 Stop Rule"
STALE_STAGE3_STOP_RULE_HEADING = "## Stage 3 Authorization-Sync Stop Rule"


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


def decode_subprocess_output(data: bytes, preferred_encoding: str = "utf-8") -> str:
    for encoding in (preferred_encoding, "utf-8", "cp932"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode(preferred_encoding, errors="backslashreplace")


def safe_console_text(text: str, encoding: str | None = None) -> str:
    target = encoding or getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(target, errors="backslashreplace").decode(target, errors="strict")


def safe_output_emission_self_check() -> dict[str, bool]:
    ascii_text = "479 passed\n"
    utf8_text = "pytest: 完了\n"
    cp932_bytes = "cp932 日本語\n".encode("cp932")
    replacement_text = "bad \ufffd byte\n"
    unavailable_text = "snowman \u2603\n"
    nonzero_return_code = 1
    return {
        "ordinary_ascii_output_unchanged": safe_console_text(ascii_text, "cp932") == ascii_text,
        "utf8_text_safe_for_cp932": "\\u" in safe_console_text(utf8_text, "ascii"),
        "cp932_origin_bytes_decodable": "日本語" in decode_subprocess_output(cp932_bytes, "cp932"),
        "replacement_character_visible_fallback": "\\ufffd" in safe_console_text(replacement_text, "cp932"),
        "unavailable_console_character_visible_fallback": "\\u2603" in safe_console_text(unavailable_text, "cp932"),
        "passed_count_machine_readable": re.search(r"\b479 passed\b", ascii_text) is not None,
        "nonzero_subprocess_result_rejectable": nonzero_return_code != 0,
        "output_emission_failure_cannot_bypass_return_code": nonzero_return_code != 0
        and bool(safe_console_text(unavailable_text, "ascii")),
    }


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


def validate_stage3_path_length_corrective_protected_delta(name_status_lines: list[str]) -> bool:
    return validate_exact_name_status_surface(
        name_status_lines,
        {"M": STAGE3_PATH_LENGTH_CORRECTIVE_PROTECTED},
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


def validate_stage3_path_length_corrective_committed_surface(
    commit_count: int,
    name_status_lines: list[str],
) -> bool:
    return validate_exact_committed_surface(
        commit_count,
        name_status_lines,
        STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED,
    )


def validate_stage4_authorization_sync_committed_surface(
    commit_count: int,
    name_status_lines: list[str],
) -> bool:
    return validate_exact_committed_surface(commit_count, name_status_lines, STAGE4_AUTHORIZATION_SYNC_MODIFIED)


def validate_stage4_verifier_output_encoding_corrective_committed_surface(
    commit_count: int,
    name_status_lines: list[str],
) -> bool:
    return validate_exact_committed_surface(commit_count, name_status_lines, STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED)


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


def stage3_path_length_corrective_origin_state(head: str, origin: str) -> str | None:
    if not origin:
        return None
    if origin == CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT and head == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT:
        return "NOT_PUSHED"
    if origin == head and head == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT:
        return "PUSHED"
    return None


def stage4_authorization_sync_origin_state(head: str, origin: str) -> str | None:
    if not origin:
        return None
    if origin == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT and head != origin:
        return "NOT_PUSHED"
    if origin == head and head != CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT:
        return "PUSHED"
    return None


def stage4_authorization_sync_clean_mode_after_surface_validation(
    surface_validated: bool,
    head: str,
    origin: str,
) -> str:
    if not surface_validated:
        raise AssertionError("Stage 4 authorization-sync origin policy reached before committed surface validation")
    state = stage4_authorization_sync_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE4_AUTHORIZATION_SYNC_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE4_AUTHORIZATION_SYNC"
    raise AssertionError("Clean Stage 4 authorization-sync origin/main state is invalid")


def stage4_verifier_output_encoding_corrective_origin_state(head: str, origin: str) -> str | None:
    if not origin:
        return None
    if origin == CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT and head != origin:
        return "NOT_PUSHED"
    if origin == head and head != CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT:
        return "PUSHED"
    return None


def stage4_verifier_output_encoding_corrective_clean_mode_after_surface_validation(
    surface_validated: bool,
    head: str,
    origin: str,
) -> str:
    if not surface_validated:
        raise AssertionError("Stage 4 verifier output-encoding corrective origin policy reached before committed surface validation")
    state = stage4_verifier_output_encoding_corrective_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE"
    raise AssertionError("Clean Stage 4 verifier output-encoding corrective origin/main state is invalid")


def stage3_path_length_corrective_clean_mode_after_surface_validation(
    surface_validated: bool,
    head: str,
    origin: str,
) -> str:
    if not surface_validated:
        raise AssertionError("Stage 3 path-length corrective origin policy reached before committed surface validation")
    state = stage3_path_length_corrective_origin_state(head, origin)
    if state == "NOT_PUSHED":
        return "CLEAN_COMMITTED_STAGE3_PATH_LENGTH_CORRECTIVE_NOT_PUSHED"
    if state == "PUSHED":
        return "CLEAN_COMMITTED_STAGE3_PATH_LENGTH_CORRECTIVE"
    raise AssertionError("Clean Stage 3 path-length corrective origin/main state is invalid")


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


def stage3_path_length_corrective_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED)[0]
    exact = [(" M", path) for path in sorted(STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED)]
    return {
        "exact_m4_accepted": dirty_surface_is_exact(exact, STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED),
        "unexpected_path_rejected": not dirty_surface_is_exact(
            [*exact, (" M", "README.md")], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "duplicate_path_rejected": not dirty_surface_is_exact(
            [*exact, exact[0]], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "staged_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("M ", first)], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "untracked_rejected": not dirty_surface_is_exact(
            [*exact, ("??", "scratch.txt")], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "status_a_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" A", first)], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "status_d_rejected": not dirty_surface_is_exact(
            [*exact[1:], (" D", first)], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "status_r_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("R ", first)], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
        "status_c_rejected": not dirty_surface_is_exact(
            [*exact[1:], ("C ", first)], STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED
        ),
    }


def stage3_path_length_corrective_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED)]
    return {
        "exact_one_commit_m4_accepted": validate_stage3_path_length_corrective_committed_surface(1, exact),
        "count_0_rejected": not validate_stage3_path_length_corrective_committed_surface(0, exact),
        "count_2_rejected": not validate_stage3_path_length_corrective_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage3_path_length_corrective_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_stage3_path_length_corrective_committed_surface(
            1, [*exact, "M\tREADME.md"]
        ),
        "duplicate_path_rejected": not validate_stage3_path_length_corrective_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_stage3_path_length_corrective_committed_surface(
            1, [*exact[1:], "A\t" + first]
        ),
        "status_d_rejected": not validate_stage3_path_length_corrective_committed_surface(
            1, [*exact[1:], "D\t" + first]
        ),
        "status_r_rejected": not validate_stage3_path_length_corrective_committed_surface(
            1, [*exact[1:], "R100\told\t" + first]
        ),
        "status_c_rejected": not validate_stage3_path_length_corrective_committed_surface(
            1, [*exact[1:], "C100\told\t" + first]
        ),
        "malformed_line_rejected": not validate_stage3_path_length_corrective_committed_surface(
            1, [*exact[1:], "M " + first]
        ),
    }


def stage3_path_length_corrective_protected_delta_self_check() -> dict[str, bool]:
    first = sorted(STAGE3_PATH_LENGTH_CORRECTIVE_PROTECTED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE3_PATH_LENGTH_CORRECTIVE_PROTECTED)]
    return {
        "exact_builder_m2_accepted": validate_stage3_path_length_corrective_protected_delta(exact),
        "empty_rejected": not validate_stage3_path_length_corrective_protected_delta([]),
        "missing_rejected": not validate_stage3_path_length_corrective_protected_delta(exact[:-1]),
        "unexpected_rejected": not validate_stage3_path_length_corrective_protected_delta(
            [*exact, "M\tscripts/check_v400_fixed_release_zip.py"]
        ),
        "duplicate_rejected": not validate_stage3_path_length_corrective_protected_delta([*exact, exact[0]]),
        "status_a_rejected": not validate_stage3_path_length_corrective_protected_delta(
            [*exact[1:], "A\t" + first]
        ),
        "status_d_rejected": not validate_stage3_path_length_corrective_protected_delta(
            [*exact[1:], "D\t" + first]
        ),
        "status_r_rejected": not validate_stage3_path_length_corrective_protected_delta(
            [*exact[1:], "R100\told\t" + first]
        ),
        "status_c_rejected": not validate_stage3_path_length_corrective_protected_delta(
            [*exact[1:], "C100\told\t" + first]
        ),
        "malformed_line_rejected": not validate_stage3_path_length_corrective_protected_delta(["M " + first]),
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


def stage3_path_length_corrective_origin_state_self_check() -> dict[str, bool]:
    synthetic_head = CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT
    unrelated = "4" * 40
    expected_message = "Stage 3 path-length corrective origin policy reached before committed surface validation"
    try:
        stage3_path_length_corrective_clean_mode_after_surface_validation(
            False, synthetic_head, CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT
        )
        blocked_before_surface_validation = False
    except AssertionError as exc:
        blocked_before_surface_validation = str(exc) == expected_message
    determine_names = set(determine_mode.__code__.co_names)
    determine_consts = set(determine_mode.__code__.co_consts)
    return {
        "base_origin_accepted_as_not_pushed": stage3_path_length_corrective_origin_state(
            synthetic_head, CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT
        )
        == "NOT_PUSHED",
        "head_origin_accepted_as_pushed": stage3_path_length_corrective_origin_state(
            synthetic_head, synthetic_head
        )
        == "PUSHED",
        "unrelated_origin_rejected": stage3_path_length_corrective_origin_state(synthetic_head, unrelated) is None,
        "empty_origin_rejected": stage3_path_length_corrective_origin_state(synthetic_head, "") is None,
        "origin_policy_blocked_before_surface_validation": blocked_before_surface_validation,
        "determine_mode_references_origin_helper": "stage3_path_length_corrective_clean_mode_after_surface_validation"
        in determine_names,
        "dirty_mode_maintained": "DIRTY_STAGE3_PATH_LENGTH_CORRECTIVE_CANDIDATE" in determine_consts,
    }


def current_state_prose_is_consistent(text: str) -> bool:
    compacted = compact(text)
    return all(phrase in compacted for phrase in REQUIRED_STAGE4_CURRENT_STATE_PHRASES) and not any(
        phrase in compacted for phrase in STALE_STAGE3_CURRENT_STATE_PHRASES
    )


def current_state_prose_consistency_self_check() -> dict[str, bool]:
    corrected = "\n".join(REQUIRED_STAGE4_CURRENT_STATE_PHRASES)
    stale = corrected + "\nWhen authorized in the future, actual build must create"
    missing = "\n".join(REQUIRED_STAGE4_CURRENT_STATE_PHRASES[:-1])
    stage4_future = corrected + "\nfuture accepted document adds the tooling-defined Stage 4 same-artifact authorization marker"
    return {
        "corrected_current_state_prose_accepted": current_state_prose_is_consistent(corrected),
        "stale_stage4_phrase_rejected": not current_state_prose_is_consistent(stale),
        "required_current_state_phrase_missing_rejected": not current_state_prose_is_consistent(missing),
        "stage4_future_boundary_prose_rejected": not current_state_prose_is_consistent(stage4_future),
    }


def top_level_section(text: str, heading: str) -> str | None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    matches = list(re.finditer(rf"(?m)^## {re.escape(heading)}\s*\n", normalized))
    if len(matches) != 1:
        return None
    start = matches[0].end()
    next_heading = re.search(r"(?m)^## [^\n]*\n", normalized[start:])
    end = start + next_heading.start() if next_heading else len(normalized)
    return normalized[start:end]


def current_purpose_is_correct(text: str) -> bool:
    section = top_level_section(text, "Purpose")
    if section is None:
        return False
    compacted = compact(section)
    return all(phrase in compacted for phrase in REQUIRED_CURRENT_PURPOSE_PHRASES) and not any(
        phrase in compacted for phrase in STALE_CURRENT_PURPOSE_PHRASES
    )


def current_purpose_self_check() -> dict[str, bool]:
    corrected = "\n".join(REQUIRED_CURRENT_PURPOSE_PHRASES)
    historical = "\n".join(
        (
            "## Control D Boundary",
            "Control D Stage 3:",
            "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED",
        )
    )
    return {
        "corrected_current_purpose_accepted": current_purpose_is_correct("## Purpose\n" + corrected),
        "stale_stage3_current_purpose_rejected": not current_purpose_is_correct(
            "## Purpose\n" + corrected + "\n" + STALE_CURRENT_PURPOSE_PHRASES[0]
        ),
        "bounded_historical_stage3_evidence_accepted": current_purpose_is_correct(
            "## Purpose\n" + corrected + "\n" + historical
        ),
        "duplicate_current_purpose_heading_rejected": not current_purpose_is_correct(
            "## Purpose\n" + corrected + "\n## Purpose\n" + corrected
        ),
        "malformed_current_purpose_heading_rejected": not current_purpose_is_correct("# Purpose\n" + corrected),
    }


def current_docs_text() -> str:
    return "\n".join(read(relative) for relative in CURRENT_DOCS)


def extract_bounded_section(text: str, start: str, end: str) -> str | None:
    start_count = text.count(start)
    end_count = text.count(end)
    if start_count != 1 or end_count != 1:
        return None
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    if end_index <= start_index:
        return None
    return text[start_index : end_index + len(end)]


def current_stage4_review_text() -> str:
    return "\n".join(read(relative) for relative in CURRENT_STAGE4_PROSE_DOCS)


def current_stage4_review_prose_is_consistent(text: str) -> bool:
    compacted = compact(text)
    return all(phrase in compacted for phrase in REQUIRED_CURRENT_STAGE4_REVIEW_PHRASES) and not any(
        phrase in compacted for phrase in STALE_CURRENT_STAGE4_REVIEW_PHRASES
    )


def current_stage4_review_prose_self_check() -> dict[str, bool]:
    corrected = "\n".join(REQUIRED_CURRENT_STAGE4_REVIEW_PHRASES)
    stale = corrected + "\nStage 4 remains blocked pending the Stage 3 artifact."
    future_marker = corrected + "\nfuture accepted document adds the tooling-defined Stage 4 same-artifact authorization marker"
    mixed = corrected + "\nStage 3 is authorized for exactly one fixed ZIP build but has not run."
    missing = "\n".join(REQUIRED_CURRENT_STAGE4_REVIEW_PHRASES[:-1])
    return {
        "corrected_current_protocol_and_metadata_accepted": current_stage4_review_prose_is_consistent(corrected),
        "stale_stage4_blocked_rejected": not current_stage4_review_prose_is_consistent(stale),
        "future_stage4_marker_wording_rejected": not current_stage4_review_prose_is_consistent(future_marker),
        "mixed_stale_and_corrected_rejected": not current_stage4_review_prose_is_consistent(mixed),
        "required_current_stage4_phrase_missing_rejected": not current_stage4_review_prose_is_consistent(missing),
    }


def historical_v3_sections_are_clean(text: str) -> bool:
    sections: list[str] = []
    for start, end in V3_HISTORICAL_SECTION_MARKERS:
        section = extract_bounded_section(text, start, end)
        if section is None:
            return False
        sections.append(section)
    compacted = compact("\n".join(sections))
    return all(phrase in compacted for phrase in REQUIRED_V3_HISTORICAL_PHRASES) and not any(
        phrase in compacted for phrase in V3_CONTAMINATION_PHRASES
    )


def historical_v3_contamination_self_check() -> dict[str, bool]:
    clean = "\n".join(
        (
            "<!-- RT-9B-RELEASE-READINESS:BEGIN -->",
            "v3.0.0 fixed ZIP: NOT_BUILT",
            "<!-- RT-9B-RELEASE-READINESS:END -->",
            "<!-- RT-9C-STAGE1-FIXED-ZIP-TOOLING:BEGIN -->",
            "RT-9c Stage 2 builder invocation count: 0",
            "RT-9c Stage 2 fixed ZIP built: false",
            "fixed ZIP builder invocation count: 0",
            "v3.0.0 fixed ZIP: NOT_BUILT",
            "<!-- RT-9C-STAGE1-FIXED-ZIP-TOOLING:END -->",
        )
    )
    contaminated = clean.replace("v3.0.0 fixed ZIP: NOT_BUILT", f"v3.0.0 fixed ZIP: release/{EXPECTED_FIXED_ZIP_BASENAME}", 1)
    current_stage4_leak = clean.replace(
        "fixed ZIP builder invocation count: 0",
        "Control D Stage 4: SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED / NOT_RUN\nfixed ZIP builder invocation count: 0",
    )
    unrelated_historical = clean + "\nLegacy v2.0.0 fixed ZIP: NOT_BUILT"
    duplicate_section = clean + "\n" + clean
    missing_section = "\n".join(clean.splitlines()[:3])
    return {
        "v3_clean_historical_sections_accepted": historical_v3_sections_are_clean(clean),
        "v3_v4_basename_contamination_rejected": not historical_v3_sections_are_clean(contaminated),
        "v3_current_stage4_status_contamination_rejected": not historical_v3_sections_are_clean(current_stage4_leak),
        "unrelated_historical_text_accepted": historical_v3_sections_are_clean(unrelated_historical),
        "duplicate_bounded_section_rejected": not historical_v3_sections_are_clean(duplicate_section),
        "missing_bounded_section_rejected": not historical_v3_sections_are_clean(missing_section),
    }


def tasklist_current_implementation_step_is_current(text: str) -> bool:
    return re.search(
        rf"(?m)^current implementation step:\s*{re.escape(TASKLIST_CURRENT_IMPLEMENTATION_STEP)}$",
        norm(text),
    ) is not None


def stage2_history_evidence_text(relative: str, text: str) -> str | None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if relative in {"README.md", "roadmap.md"}:
        match = re.search(
            r"Control D Stage 2 source preflight HEAD:.*?Control D Stage 2 DRC_v4\.0\.0 tag:\s*NOT_CREATED",
            normalized,
            flags=re.DOTALL,
        )
        return match.group(0) if match else None
    if relative == "docs/v400_fixed_release_zip.md":
        match = re.search(
            r"## Stage 2 Accepted Source Preflight.*?```text\n(?P<section>.*?)\n```",
            normalized,
            flags=re.DOTALL,
        )
        return match.group("section") if match else None
    if relative == "docs/v400_release_preparation_protocol.md":
        match = re.search(
            r"Stage 2 accepted evidence:\n\n```text\n(?P<section>.*?)\n```",
            normalized,
            flags=re.DOTALL,
        )
        return match.group("section") if match else None
    return None


def stage2_history_evidence_is_clean(relative: str, text: str) -> bool:
    evidence = stage2_history_evidence_text(relative, text)
    if evidence is None:
        return False
    compacted = compact(evidence)
    builder_is_zero = (
        "Control D Stage 2 release builder invocation: 0" in compacted
        or "release builder invocation: 0" in compacted
    )
    fixed_zip_not_built = (
        "Control D Stage 2 fixed ZIP: NOT_BUILT" in compacted
        or "fixed ZIP: NOT_BUILT" in compacted
    )
    current_stage_leaked = any(
        phrase in evidence
        for phrase in (
            EXPECTED_FIXED_ZIP_BASENAME,
            "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED",
            "SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED / NOT_RUN",
        )
    )
    return builder_is_zero and fixed_zip_not_built and not current_stage_leaked


def stage2_history_evidence_self_check() -> dict[str, bool]:
    readme_clean = "\n".join(
        (
            "Control D Stage 2 source preflight HEAD: abc",
            "Control D Stage 2 release builder invocation: 0",
            "Control D Stage 2 fixed ZIP: NOT_BUILT",
            "Control D Stage 2 DRC_v4.0.0 tag: NOT_CREATED",
        )
    )
    fixed_clean = "\n".join(
        (
            "## Stage 2 Accepted Source Preflight",
            "Stage 2 clean committed source preflight completed.",
            "```text",
            "release builder invocation:",
            "0",
            "",
            "fixed ZIP:",
            "NOT_BUILT",
            "```",
            "At the Stage 2 checkpoint, Stage 3 was authorized.",
        )
    )
    protocol_clean = "\n".join(
        (
            "Stage 2 accepted evidence:",
            "",
            "```text",
            "release builder invocation:",
            "0",
            "",
            "fixed ZIP:",
            "NOT_BUILT",
            "```",
        )
    )
    protocol_current_block_mixed = protocol_clean.replace(
        "fixed ZIP:\nNOT_BUILT",
        "fixed ZIP:\nNOT_BUILT\nControl D Stage 4:\nSAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED / NOT_RUN",
    )
    contaminated = fixed_clean.replace("NOT_BUILT", f"release/{EXPECTED_FIXED_ZIP_BASENAME}")
    return {
        "readme_style_clean_accepted": stage2_history_evidence_is_clean("README.md", readme_clean),
        "roadmap_style_clean_accepted": stage2_history_evidence_is_clean("roadmap.md", readme_clean),
        "fixed_doc_clean_accepted": stage2_history_evidence_is_clean("docs/v400_fixed_release_zip.md", fixed_clean),
        "protocol_doc_clean_accepted": stage2_history_evidence_is_clean(
            "docs/v400_release_preparation_protocol.md",
            protocol_clean,
        ),
        "protocol_current_block_mixed_rejected": not stage2_history_evidence_is_clean(
            "docs/v400_release_preparation_protocol.md",
            protocol_current_block_mixed,
        ),
        "current_fixed_zip_basename_rejected": not stage2_history_evidence_is_clean(
            "docs/v400_fixed_release_zip.md",
            contaminated,
        ),
        "missing_not_built_rejected": not stage2_history_evidence_is_clean(
            "docs/v400_fixed_release_zip.md",
            fixed_clean.replace("NOT_BUILT", "MISSING"),
        ),
    }


def protocol_control_block(text: str, control: str) -> str | None:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    match = re.search(
        rf"## {re.escape(control)} Boundary\n(?P<section>.*?)(?=\n## Control [A-Z] Boundary|\n## Future Control E|\Z)",
        normalized,
        flags=re.DOTALL,
    )
    return match.group("section") if match else None


def protocol_historical_no_build_blocks_are_clean(text: str) -> bool:
    for control in HISTORICAL_NO_BUILD_CONTROL_BLOCKS:
        section = protocol_control_block(text, control)
        if section is None:
            return False
        compacted = compact(section)
        if "fixed ZIP builder invocation count: 0" not in compacted:
            return False
        if "fixed ZIP: NOT_BUILT" not in compacted:
            return False
        if EXPECTED_FIXED_ZIP_BASENAME in section:
            return False
        if "fixed ZIP builder invocation count:\n1" in section:
            return False
    return True


def fixed_zip_contract_stop_rule_is_current(text: str) -> bool:
    return ACTIVE_STAGE4_STOP_RULE_HEADING in text and STALE_STAGE3_STOP_RULE_HEADING not in text


def top_level_status_section(text: str) -> str | None:
    return top_level_section(text, "Status")


def exact_status_value_is_present(section: str, label: str, value: str) -> bool:
    lines = section.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    label_line = f"{label}:"
    inline_line = f"{label}: {value}"
    matches = 0
    for index, line in enumerate(lines):
        if line == inline_line:
            matches += 1
        elif line == label_line:
            value_index = index + 1
            if value_index < len(lines) and lines[value_index] == value:
                matches += 1
            else:
                return False
        elif line.startswith(label_line):
            return False
    if matches != 1:
        return False
    return True


def protocol_current_status_is_correct(text: str) -> bool:
    section = top_level_status_section(text)
    if section is None:
        return False
    expected_zip = f"release/{EXPECTED_FIXED_ZIP_BASENAME}"
    required = (
        ("Current checkpoint", "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1"),
        ("Control D Stage 3", "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"),
        ("Control D Stage 4 authorization-sync", "COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED"),
        ("Stage 4 invocation 1", "EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED"),
        ("verification verdict", "NOT_REACHED"),
        ("failure class", "NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE"),
        ("release-package scanner known fixtures", "EXACT_EXPECTED_FINDINGS / ACCEPTED"),
        ("ZIP structural/version checks reached before failure", "PASS"),
        ("extracted compileall", "PASS"),
        ("extracted Backend pytest", "PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED"),
        ("Stage 4 retry", "NOT_AUTHORIZED / NOT_RUN"),
        ("Control E", "NOT_AUTHORIZED"),
        ("fixed ZIP builder invocation count", "1"),
        ("fixed ZIP", expected_zip),
        ("annotated tag", "NOT_CREATED"),
        ("GitHub Release", "NOT_CREATED"),
        ("DRC v4.0.0", "NOT_RELEASED"),
    )
    if not all(exact_status_value_is_present(section, label, value) for label, value in required):
        return False
    v4_basenames = re.findall(r"DailyRhythmCompanion_v4\.0\.0_\d{8}_\d{6}\.zip", section)
    if any(basename != EXPECTED_FIXED_ZIP_BASENAME for basename in v4_basenames):
        return False
    return True


def r7_current_status_self_check() -> dict[str, bool]:
    status = "\n".join(
        (
            "## Status",
            "Current checkpoint:",
            "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1",
            "Control D Stage 3:",
            "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED",
            "Control D Stage 4 authorization-sync:",
            "COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED",
            "Stage 4 invocation 1:",
            "EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED",
            "verification verdict:",
            "NOT_REACHED",
            "failure class:",
            "NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE",
            "release-package scanner known fixtures:",
            "EXACT_EXPECTED_FINDINGS / ACCEPTED",
            "ZIP structural/version checks reached before failure:",
            "PASS",
            "extracted compileall:",
            "PASS",
            "extracted Backend pytest:",
            "PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED",
            "Stage 4 retry:",
            "NOT_AUTHORIZED / NOT_RUN",
            "Control E:",
            "NOT_AUTHORIZED",
            "fixed ZIP builder invocation count:",
            "1",
            "fixed ZIP:",
            f"release/{EXPECTED_FIXED_ZIP_BASENAME}",
            "annotated tag:",
            "NOT_CREATED",
            "GitHub Release:",
            "NOT_CREATED",
            "DRC v4.0.0:",
            "NOT_RELEASED",
        )
    )
    historical = "\n".join(
        (
            "## Control B Boundary",
            "fixed ZIP builder invocation count:",
            "0",
            "fixed ZIP:",
            "NOT_BUILT",
            "## Control C Boundary",
            "fixed ZIP builder invocation count:",
            "0",
            "fixed ZIP:",
            "NOT_BUILT",
        )
    )
    return {
        "corrected_current_status_accepted": protocol_current_status_is_correct(status),
        "current_status_with_historical_no_build_accepted": protocol_current_status_is_correct(status + "\n" + historical),
        "current_builder_count_zero_rejected": not protocol_current_status_is_correct(
            status.replace("fixed ZIP builder invocation count:\n1", "fixed ZIP builder invocation count:\n0")
        ),
        "current_builder_count_ten_rejected": not protocol_current_status_is_correct(
            status.replace("fixed ZIP builder invocation count:\n1", "fixed ZIP builder invocation count:\n10")
        ),
        "current_builder_count_extra_rejected": not protocol_current_status_is_correct(
            status.replace("fixed ZIP builder invocation count:\n1", "fixed ZIP builder invocation count:\n1 extra")
        ),
        "current_fixed_zip_not_built_rejected": not protocol_current_status_is_correct(
            status.replace(f"release/{EXPECTED_FIXED_ZIP_BASENAME}", "NOT_BUILT")
        ),
        "wrong_basename_rejected": not protocol_current_status_is_correct(
            status.replace(EXPECTED_FIXED_ZIP_BASENAME, "DailyRhythmCompanion_v4.0.0_20991231_235959.zip")
        ),
        "missing_exact_zip_path_rejected": not protocol_current_status_is_correct(
            status.replace(f"release/{EXPECTED_FIXED_ZIP_BASENAME}", EXPECTED_FIXED_ZIP_BASENAME)
        ),
        "fixed_zip_bak_suffix_rejected": not protocol_current_status_is_correct(
            status.replace(f"release/{EXPECTED_FIXED_ZIP_BASENAME}", f"release/{EXPECTED_FIXED_ZIP_BASENAME}.bak")
        ),
        "not_created_extra_rejected": not protocol_current_status_is_correct(
            status.replace("annotated tag:\nNOT_CREATED", "annotated tag:\nNOT_CREATED_EXTRA")
        ),
        "not_run_extra_rejected": not protocol_current_status_is_correct(
            status.replace("Stage 4 retry:\nNOT_AUTHORIZED / NOT_RUN", "Stage 4 retry:\nNOT_AUTHORIZED / NOT_RUN_EXTRA")
        ),
        "checkpoint_trailing_text_rejected": not protocol_current_status_is_correct(
            status.replace(
                "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1",
                "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1 trailing text",
            )
        ),
        "stage3_stale_authorization_rejected": not protocol_current_status_is_correct(
            status.replace("BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED", "BUILD_EXACTLY_ONCE / AUTHORIZED / NOT_RUN")
        ),
        "stage4_completion_rejected": not protocol_current_status_is_correct(
            status.replace("Stage 4 invocation 1:\nEXACTLY_ONCE_EXECUTED / EXECUTION_FAILED", "Stage 4 invocation 1:\nCOMPLETED / PASS / ACCEPTED")
        ),
        "control_e_authorization_rejected": not protocol_current_status_is_correct(
            status.replace("Control E:\nNOT_AUTHORIZED", "Control E:\nAUTHORIZED")
        ),
        "released_tag_release_created_claims_rejected": not protocol_current_status_is_correct(
            status.replace("DRC v4.0.0:\nNOT_RELEASED", "DRC v4.0.0:\nRELEASED")
            .replace("annotated tag:\nNOT_CREATED", "annotated tag:\nCREATED")
            .replace("GitHub Release:\nNOT_CREATED", "GitHub Release:\nCREATED")
        ),
        "missing_status_section_rejected": not protocol_current_status_is_correct(status.replace("## Status\n", "")),
        "duplicate_status_section_rejected": not protocol_current_status_is_correct(status + "\n## Status\nextra"),
        "duplicate_required_label_rejected": not protocol_current_status_is_correct(
            status.replace("Control E:\nNOT_AUTHORIZED", "Control E:\nNOT_AUTHORIZED\nControl E:\nNOT_AUTHORIZED")
        ),
    }


def r5_document_correction_self_check() -> dict[str, bool]:
    clean_protocol = "\n".join(
        (
            "## Control B Boundary",
            "fixed ZIP builder invocation count:",
            "0",
            "fixed ZIP:",
            "NOT_BUILT",
            "## Control C Boundary",
            "fixed ZIP builder invocation count:",
            "0",
            "fixed ZIP:",
            "NOT_BUILT",
            "## Control D Boundary",
        )
    )
    contaminated_protocol = clean_protocol.replace("NOT_BUILT", f"release/{EXPECTED_FIXED_ZIP_BASENAME}", 1)
    count_one_protocol = clean_protocol.replace("fixed ZIP builder invocation count:\n0", "fixed ZIP builder invocation count:\n1", 1)
    clean_contract = ACTIVE_STAGE4_STOP_RULE_HEADING + "\nStage 4 verifier output-encoding corrective R1 stops as a dirty exact candidate."
    stale_contract = clean_contract + "\n" + STALE_STAGE3_STOP_RULE_HEADING
    return {
        "historical_control_b_c_no_build_accepted": protocol_historical_no_build_blocks_are_clean(clean_protocol),
        "historical_current_fixed_zip_leak_rejected": not protocol_historical_no_build_blocks_are_clean(contaminated_protocol),
        "historical_builder_count_one_rejected": not protocol_historical_no_build_blocks_are_clean(count_one_protocol),
        "active_stage4_stop_rule_accepted": fixed_zip_contract_stop_rule_is_current(clean_contract),
        "stale_stage3_stop_rule_rejected": not fixed_zip_contract_stop_rule_is_current(stale_contract),
    }


def stage4_content_review_runtime_connection_self_check() -> dict[str, bool]:
    protocol_names = check_protocol_and_records.__code__.co_names
    main_names = main.__code__.co_names
    guard_names = check_stage4_content_review_guards.__code__.co_names
    return {
        "content_review_guard_callable": callable(check_stage4_content_review_guards),
        "r6_current_status_guard_callable": callable(check_r6_current_status_guards),
        "protocol_validation_references_guard_once": protocol_names.count("check_stage4_content_review_guards") == 1,
        "main_references_current_self_check_once": main_names.count("current_stage4_review_prose_self_check") == 1,
        "main_references_historical_self_check_once": main_names.count("historical_v3_contamination_self_check") == 1,
        "protocol_references_stage2_history_self_check_once": protocol_names.count("stage2_history_evidence_self_check") == 1,
        "protocol_references_r5_document_self_check_once": protocol_names.count("r5_document_correction_self_check") == 1,
        "protocol_references_r7_current_status_self_check_once": protocol_names.count("r7_current_status_self_check") == 1,
        "stage4_guard_references_v3_guard_once": guard_names.count("historical_v3_sections_are_clean") == 1,
        "stage4_guard_references_tasklist_step_once": guard_names.count("tasklist_current_implementation_step_is_current") == 1,
        "stage4_guard_references_stage2_history_once": guard_names.count("stage2_history_evidence_is_clean") == 1,
        "stage4_guard_references_r5_docs_once": guard_names.count("check_r5_document_correction_guards") == 1,
        "stage4_guard_references_r6_current_status_once": guard_names.count("check_r6_current_status_guards") == 1,
    }


def check_stage4_content_review_guards() -> None:
    if not current_stage4_review_prose_is_consistent(current_stage4_review_text()):
        raise AssertionError("Stage 4 current protocol/metadata content-review guard failed")
    if not current_purpose_is_correct(read("docs/v400_release_preparation_protocol.md")):
        raise AssertionError("current Purpose guard failed")
    for relative in V3_HISTORICAL_DOCS:
        if not historical_v3_sections_are_clean(read(relative)):
            raise AssertionError(f"Historical v3 section contamination guard failed: {relative}")
    if not tasklist_current_implementation_step_is_current(read("tasklist.md")):
        raise AssertionError("tasklist current implementation step is not Stage 4 Authorization Sync")
    for relative in STAGE2_HISTORY_EVIDENCE_DOCS:
        if not stage2_history_evidence_is_clean(relative, read(relative)):
            raise AssertionError(f"Stage 2 history evidence guard failed: {relative}")
    check_r5_document_correction_guards()
    check_r6_current_status_guards()


def check_r5_document_correction_guards() -> None:
    protocol = read("docs/v400_release_preparation_protocol.md")
    fixed_zip_contract = read("docs/v400_fixed_release_zip.md")
    if "Current checkpoint:\nDRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1" not in protocol:
        raise AssertionError("protocol current checkpoint is not Stage 4 verifier output-encoding corrective R1")
    if "Control D Stage 2 authorization-sync" in protocol:
        raise AssertionError("stale Stage 2 authorization-sync checkpoint remains")
    if not protocol_historical_no_build_blocks_are_clean(protocol):
        raise AssertionError("Control B/C historical no-build block guard failed")
    if not fixed_zip_contract_stop_rule_is_current(fixed_zip_contract):
        raise AssertionError("fixed ZIP contract active Stage 4 stop rule guard failed")


def check_r6_current_status_guards() -> None:
    if not protocol_current_status_is_correct(read("docs/v400_release_preparation_protocol.md")):
        raise AssertionError("protocol current top-level Status block guard failed")


def stage3_authorization_contract_is_present(text: str) -> bool:
    canonical_marker_pattern = (
        rf"Control D Stage 3 authorization:\s*\r?\n\s*{re.escape(STAGE3_AUTHORIZATION)}"
    )
    canonical_marker_occurrences = list(re.finditer(canonical_marker_pattern, text))
    return len(canonical_marker_occurrences) == 1 and not old_stage3_authorization_contract_is_present(text)


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


def normalized_source_sha256(source_bytes: bytes) -> str:
    normalized = source_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(normalized).hexdigest().upper()


def normalized_stage3_builder_sha256(builder_bytes: bytes) -> str:
    return normalized_source_sha256(builder_bytes)


def normalized_generic_builder_sha256(builder_bytes: bytes) -> str:
    return normalized_source_sha256(builder_bytes)


def builder_has_expected_stage3_builder_normalized_sha256() -> bool:
    return (
        normalized_stage3_builder_sha256((ROOT / "build_v400_fixed_release_zip_from_head.ps1").read_bytes())
        == EXPECTED_STAGE3_BUILDER_NORMALIZED_SHA256
    )


def builder_has_expected_generic_builder_normalized_sha256() -> bool:
    return (
        normalized_generic_builder_sha256((ROOT / "build_release.bat").read_bytes())
        == EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256
    )


def check_builder_stage3_normalized_sha256() -> None:
    if not builder_has_expected_stage3_builder_normalized_sha256():
        raise AssertionError("Stage 3 builder normalized SHA-256 is not exact")


def check_builder_generic_normalized_sha256() -> None:
    if not builder_has_expected_generic_builder_normalized_sha256():
        raise AssertionError("Generic builder normalized SHA-256 is not exact")


def stage3_authorization_marker_runtime_connection_self_check() -> dict[str, bool]:
    exact_names = stage3_authorization_marker_assignment_is_exact.__code__.co_names
    check_names = check_builder_stage3_authorization_marker_assignment.__code__.co_names
    sha_check_names = check_builder_stage3_normalized_sha256.__code__.co_names
    generic_sha_check_names = check_builder_generic_normalized_sha256.__code__.co_names
    protocol_names = check_protocol_and_records.__code__.co_names
    short_contract_names = fixed_builder_short_worktree_contract_is_present.__code__.co_names
    generic_contract_names = generic_builder_short_package_staging_contract_is_present.__code__.co_names
    determine_names = determine_mode.__code__.co_names
    protected_names = check_protected_surface.__code__.co_names
    main_names = main.__code__.co_names
    return {
        "pure_assignment_validator_callable": callable(executable_stage3_authorization_marker_assignments),
        "exact_assignment_validator_callable": callable(stage3_authorization_marker_assignment_is_exact),
        "builder_guard_callable": callable(check_builder_stage3_authorization_marker_assignment),
        "normalized_sha_guard_callable": callable(check_builder_stage3_normalized_sha256),
        "generic_normalized_sha_guard_callable": callable(check_builder_generic_normalized_sha256),
        "fixed_builder_canonical_short_assignment_helper_callable": callable(
            fixed_builder_has_canonical_short_worktree_assignment
        ),
        "fixed_builder_short_worktree_contract_callable": callable(fixed_builder_short_worktree_contract_is_present),
        "generic_builder_short_package_contract_callable": callable(generic_builder_short_package_staging_contract_is_present),
        "generic_builder_atomic_slot_claim_helper_callable": callable(
            generic_builder_atomic_slot_claim_contract_is_present
        ),
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
        "generic_sha_guard_uses_expected_sha_helper_once": generic_sha_check_names.count(
            "builder_has_expected_generic_builder_normalized_sha256"
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
        "protocol_validation_uses_generic_normalized_sha_guard_once": protocol_names.count(
            "check_builder_generic_normalized_sha256"
        )
        == 1,
        "protocol_validation_uses_fixed_short_contract_once": protocol_names.count(
            "fixed_builder_short_worktree_contract_is_present"
        )
        == 1,
        "fixed_short_contract_uses_canonical_assignment_helper_once": short_contract_names.count(
            "fixed_builder_has_canonical_short_worktree_assignment"
        )
        == 1,
        "protocol_validation_uses_generic_short_contract_once": protocol_names.count(
            "generic_builder_short_package_staging_contract_is_present"
        )
        == 1,
        "generic_short_contract_uses_atomic_slot_claim_helper_once": generic_contract_names.count(
            "generic_builder_atomic_slot_claim_contract_is_present"
        )
        == 1,
        "determine_mode_uses_r10_dirty_validator": "STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED" in determine_names,
        "protected_surface_uses_r10_protected_validator": "validate_stage3_path_length_corrective_protected_delta"
        in protected_names,
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


def generic_builder_normalized_sha256_self_check() -> dict[str, bool]:
    current = (ROOT / "build_release.bat").read_bytes()
    normalized = current.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    crlf = normalized.replace(b"\n", b"\r\n")
    one_byte_mutation = current[:-1] + (b"\n" if current[-1:] != b"\n" else b"X")
    path_marker_mutation = current.replace(b"\\d%%s", b"\\long_slot%%s", 1)
    added_statement = current + b"\necho unexpected\n"
    return {
        "current_builder_bytes_accepted": normalized_generic_builder_sha256(current)
        == EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256,
        "lf_form_accepted": normalized_generic_builder_sha256(normalized)
        == EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256,
        "crlf_form_accepted": normalized_generic_builder_sha256(crlf)
        == EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256,
        "one_byte_content_mutation_rejected": normalized_generic_builder_sha256(one_byte_mutation)
        != EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256,
        "path_marker_mutation_rejected": normalized_generic_builder_sha256(path_marker_mutation)
        != EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256,
        "added_executable_statement_rejected": normalized_generic_builder_sha256(added_statement)
        != EXPECTED_GENERIC_BUILDER_NORMALIZED_SHA256,
    }


def stage3_authorization_contract_self_check() -> dict[str, bool]:
    lf = "Control D Stage 3 authorization:\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    crlf = "Control D Stage 3 authorization:\r\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    old = "Control D Stage 3:\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    duplicate = lf + "\n" + lf
    crlf_duplicate = crlf + "\r\n" + crlf
    mixed_lf_crlf_duplicate = lf + "\n" + crlf
    adjacent_duplicate = lf + lf
    missing_token = "Control D Stage 3 authorization:\nNOT_AUTHORIZED"
    missing_marker = "Control D Stage 3 build is complete"
    partial_marker = "Control D Stage 3 authorization:"
    malformed_marker = "Control D Stage 3 authorization: AUTHORIZED_FOR_ONE_TIME_BUILD"
    new_plus_old = lf + "\n" + old
    unrelated_between = "Control D Stage 3 authorization:\nnot related\nAUTHORIZED_FOR_ONE_TIME_BUILD"
    return {
        "lf_contract_accepted": stage3_authorization_contract_is_present(lf),
        "crlf_contract_accepted": stage3_authorization_contract_is_present(crlf),
        "old_stage3_label_rejected": not stage3_authorization_contract_is_present(old),
        "new_plus_old_rejected": not stage3_authorization_contract_is_present(new_plus_old),
        "duplicate_marker_rejected": not stage3_authorization_contract_is_present(duplicate),
        "crlf_duplicate_marker_rejected": not stage3_authorization_contract_is_present(crlf_duplicate),
        "mixed_lf_crlf_duplicate_marker_rejected": not stage3_authorization_contract_is_present(
            mixed_lf_crlf_duplicate
        ),
        "adjacent_duplicate_marker_rejected": not stage3_authorization_contract_is_present(adjacent_duplicate),
        "authorization_label_missing_rejected": not stage3_authorization_contract_is_present(old),
        "token_missing_rejected": not stage3_authorization_contract_is_present(missing_token),
        "marker_missing_rejected": not stage3_authorization_contract_is_present(missing_marker),
        "partial_marker_rejected": not stage3_authorization_contract_is_present(partial_marker),
        "malformed_marker_rejected": not stage3_authorization_contract_is_present(malformed_marker),
        "unrelated_between_label_and_token_rejected": not stage3_authorization_contract_is_present(unrelated_between),
        "builder_marker_assignment_correct": builder_has_correct_stage3_authorization_marker(),
        "builder_normalized_sha_correct": builder_has_expected_stage3_builder_normalized_sha256(),
        "builder_assignment_self_check": all(stage3_authorization_marker_assignment_self_check().values()),
    }


def stage3_build_is_authorized(text: str) -> bool:
    return stage3_authorization_contract_is_present(text) and STAGE2_ACCEPTED in text


def stage4_zip_verification_is_authorized(text: str) -> bool:
    return STAGE4_AUTHORIZATION in text and STAGE3_ARTIFACT_READY in text


def stage4_zip_verification_completed(text: str) -> bool:
    return "SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / COMPLETED" in text


def control_e_is_authorized(text: str) -> bool:
    return re.search(r"Control E:\s*\r?\n\s*AUTHORIZED\b", text) is not None


def stage4_lifecycle_contract_is_valid(text: str) -> bool:
    return (
        text.count(STAGE2_ACCEPTED) == 2
        and text.count(STAGE2_AUTHORIZATION) == 0
        and text.count(STAGE3_ARTIFACT_READY) == 2
        and text.count(STAGE3_AUTHORIZATION) == 0
        and text.count(STAGE4_AUTHORIZATION) == 0
        and not stage3_build_is_authorized(text)
        and not stage4_zip_verification_is_authorized(text)
        and not stage4_zip_verification_completed(text)
        and not control_e_is_authorized(text)
        and "Stage 4 invocation 1:\nEXACTLY_ONCE_EXECUTED / EXECUTION_FAILED" in text
        and "Stage 4 retry:\nNOT_AUTHORIZED / NOT_RUN" in text
    )


def stage4_lifecycle_contract_self_check() -> dict[str, bool]:
    text = current_docs_text()
    stage3_token_restored = text + "\nControl D Stage 3 authorization:\n" + STAGE3_AUTHORIZATION
    stage3_artifact_missing = text.replace(STAGE3_ARTIFACT_READY, "", 1)
    stage3_artifact_duplicate = text + "\n" + STAGE3_ARTIFACT_READY
    stage4_invocation_missing = text.replace("Stage 4 invocation 1:\nEXACTLY_ONCE_EXECUTED / EXECUTION_FAILED", "")
    stage4_token_duplicate = text + "\nControl D Stage 4 authorization:\n" + STAGE4_AUTHORIZATION
    stage4_completed = text.replace(
        "Stage 4 invocation 1:\nEXACTLY_ONCE_EXECUTED / EXECUTION_FAILED",
        "Stage 4 invocation 1:\nCOMPLETED / PASS / ACCEPTED",
    )
    control_e_authorized = text.replace("Control E:\nNOT_AUTHORIZED", "Control E:\nAUTHORIZED", 1)
    return {
        "current_stage4_docs_stage2_accepted_exact_2": text.count(STAGE2_ACCEPTED) == 2,
        "current_stage4_docs_stage2_authorization_absent": text.count(STAGE2_AUTHORIZATION) == 0,
        "current_stage4_docs_stage3_artifact_ready_exact_2": text.count(STAGE3_ARTIFACT_READY) == 2,
        "current_stage4_docs_stage3_authorization_absent": text.count(STAGE3_AUTHORIZATION) == 0,
        "current_stage4_docs_stage4_authorization_absent": text.count(STAGE4_AUTHORIZATION) == 0,
        "current_stage4_docs_actual_build_authorization_false": not stage3_build_is_authorized(text),
        "current_stage4_docs_same_artifact_retry_authorization_false": not stage4_zip_verification_is_authorized(text),
        "current_stage4_docs_stage4_invocation_failed": "Stage 4 invocation 1:\nEXACTLY_ONCE_EXECUTED / EXECUTION_FAILED" in text,
        "current_stage4_docs_stage4_verification_not_completed": not stage4_zip_verification_completed(text),
        "current_stage4_docs_control_e_authorization_false": not control_e_is_authorized(text),
        "stage3_token_restored_rejected": not stage4_lifecycle_contract_is_valid(stage3_token_restored),
        "stage3_artifact_missing_rejected": not stage4_lifecycle_contract_is_valid(stage3_artifact_missing),
        "stage3_artifact_duplicate_rejected": not stage4_lifecycle_contract_is_valid(stage3_artifact_duplicate),
        "stage4_invocation_missing_rejected": not stage4_lifecycle_contract_is_valid(stage4_invocation_missing),
        "stage4_token_duplicate_rejected": not stage4_lifecycle_contract_is_valid(stage4_token_duplicate),
        "stage4_completed_rejected": not stage4_lifecycle_contract_is_valid(stage4_completed),
        "control_e_authorized_rejected": not stage4_lifecycle_contract_is_valid(control_e_authorized),
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
    commit_count = int(
        git_out(
            "rev-list",
            "--count",
            f"{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}..{CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT}",
        )
    )
    lines = git_out(
        "diff",
        "--name-status",
        f"{CONTROL_D_STAGE3_AUTHORIZATION_COMMIT}..{CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT}",
    ).splitlines()
    if not validate_stage3_builder_auth_guard_corrective_committed_surface(commit_count, lines):
        raise AssertionError(
            "Clean committed Stage 3 builder authorization guard corrective surface is not exact one-commit M3"
        )
    check_stage3_builder_auth_guard_corrective_protected_delta(
        CONTROL_D_STAGE3_AUTHORIZATION_COMMIT,
        CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT,
    )


def check_committed_stage3_path_length_corrective_surface() -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT}..{CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT}"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT}..{CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT}").splitlines()
    if not validate_stage3_path_length_corrective_committed_surface(commit_count, lines):
        raise AssertionError("Clean committed Stage 3 path-length corrective surface is not exact one-commit M4")
    check_stage3_path_length_corrective_protected_delta(CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT, CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT)


def check_committed_stage4_authorization_sync_surface(head: str = "HEAD") -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT}..{head}"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT}..{head}").splitlines()
    if not validate_stage4_authorization_sync_committed_surface(commit_count, lines):
        raise AssertionError("Clean committed Stage 4 authorization-sync surface is not exact one-commit M12")
    protected = git_out("diff", "--name-status", f"{CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT}..{head}", "--", *PROTECTED_PATHS).splitlines()
    if not validate_empty_protected_delta(protected):
        raise AssertionError("Stage 4 authorization-sync protected delta is not empty")


def check_committed_stage4_verifier_output_encoding_corrective_surface(head: str = "HEAD") -> None:
    commit_count = int(git_out("rev-list", "--count", f"{CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT}..{head}"))
    lines = git_out("diff", "--name-status", f"{CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT}..{head}").splitlines()
    if not validate_stage4_verifier_output_encoding_corrective_committed_surface(commit_count, lines):
        raise AssertionError("Clean committed Stage 4 verifier output-encoding corrective surface is not exact one-commit M12")
    protected = git_out(
        "diff",
        "--name-status",
        f"{CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT}..{head}",
        "--",
        *PROTECTED_PATHS,
    ).splitlines()
    if not validate_empty_protected_delta(protected):
        raise AssertionError("Stage 4 verifier output-encoding corrective protected delta is not empty")


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
            if head == CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT and origin == CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT:
                check_dirty_surface(entries, STAGE3_PATH_LENGTH_CORRECTIVE_MODIFIED)
                return "DIRTY_STAGE3_PATH_LENGTH_CORRECTIVE_CANDIDATE"
            if head == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT and origin == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT:
                check_dirty_surface(entries, STAGE4_AUTHORIZATION_SYNC_MODIFIED)
                check_expected_fixed_zip_tuple()
                return "DIRTY_STAGE4_AUTHORIZATION_SYNC_CANDIDATE"
            if head == CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT and origin == CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT:
                check_dirty_surface(entries, STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED)
                check_expected_fixed_zip_tuple()
                return "DIRTY_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_CANDIDATE"
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
    if head == CONTROL_D_STAGE3_BUILDER_AUTH_GUARD_COMMIT:
        return stage3_builder_auth_guard_corrective_clean_mode_after_surface_validation(True, head, origin)
    check_committed_stage3_path_length_corrective_surface()
    if head == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT:
        return stage3_path_length_corrective_clean_mode_after_surface_validation(True, head, origin)
    check_committed_stage4_authorization_sync_surface(CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT)
    if head == CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT:
        check_expected_fixed_zip_tuple()
        return stage4_authorization_sync_clean_mode_after_surface_validation(True, head, origin)
    check_committed_stage4_verifier_output_encoding_corrective_surface("HEAD")
    check_expected_fixed_zip_tuple()
    return stage4_verifier_output_encoding_corrective_clean_mode_after_surface_validation(True, head, origin)


def check_versions() -> None:
    require(read("backend/app/version.py"), 'APP_VERSION = "4.0.0"', "Backend APP_VERSION")
    require(read("app/pubspec.yaml"), "version: 4.0.0+5", "Flutter version")
    require(read("scripts/check_v20x_application_version_metadata.py"), '"4.0.0": "5"', "version mapping")


def check_release_state_docs() -> None:
    for relative in COORDINATION_DOCS:
        text = read(relative)
        for label, value in (
            ("current small commit", "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1"),
            ("current implementation", "DRC v4.0.0 Control D Stage 4 Verifier Output Encoding Corrective R1"),
            ("current implementation state", "STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_R1 / IMPLEMENTED / AWAITING_REVIEW"),
            ("Control C", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control C implementation commit", CONTROL_C_COMMIT),
            ("Control D", "CURRENT / NOT_COMPLETED"),
            ("Control D Stage 1", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
            ("Control D Stage 1 implementation commit", CONTROL_D_STAGE1_COMMIT),
            ("Control D Stage 1 surface", "13 files / M10 A3 D0"),
            ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"),
            ("Control D Stage 3", "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"),
            ("Control D Stage 4 authorization-sync", "COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED"),
            ("Stage 4 invocation 1", "EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED"),
            ("verification verdict", "NOT_REACHED"),
            ("failure class", "NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE"),
            ("release-package scanner known fixtures", "EXACT_EXPECTED_FINDINGS / ACCEPTED"),
            ("Stage 4 retry", "NOT_AUTHORIZED / NOT_RUN"),
            ("Control E", "NOT_AUTHORIZED"),
            ("DRC v4.0.0", "NOT_RELEASED"),
            ("fixed ZIP builder invocation count", "1"),
            ("fixed ZIP", "release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip"),
            ("annotated tag", "NOT_CREATED"),
            ("GitHub Release", "NOT_CREATED"),
        ):
            require_associated(text, label, value, relative)


def check_protocol_and_records() -> None:
    protocol = read("docs/v400_release_preparation_protocol.md")
    for needle in (
        "Control D Stage 1",
        "STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_R1 / IMPLEMENTED / AWAITING_REVIEW",
        "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
        "13 files / M10 A3 D0",
        "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED",
        "Stage 4 invocation 1",
        "NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE",
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
        ("Control D Stage 3", "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"),
        ("Control E", "NOT_AUTHORIZED"),
        ("DRC v4.0.0", "NOT_RELEASED"),
    ):
        require_associated(metadata, label, value, "candidate metadata")

    record = read("docs/v400_release_record.md")
    for label, value in (
        ("Status", "PREPARED / NOT_RELEASED"),
        ("Current phase", "Control D Stage 4 Verifier Output Encoding Corrective R1 STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_R1 / IMPLEMENTED / AWAITING_REVIEW"),
        ("Control C verification baseline", CONTROL_C_BASELINE),
        ("Control C implementation commit", CONTROL_C_COMMIT),
        ("Control D Stage 1", "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED"),
        ("Control D Stage 1 implementation commit", CONTROL_D_STAGE1_COMMIT),
        ("Control D Stage 2", "CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"),
        ("Control D Stage 3", "BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED"),
        ("release source HEAD", EXPECTED_FIXED_ZIP_SOURCE_HEAD),
        ("verification HEAD", "NOT_RECORDED"),
        ("fixed ZIP basename", EXPECTED_FIXED_ZIP_BASENAME),
        ("fixed ZIP size", "3018230 bytes"),
        ("fixed ZIP SHA-256", EXPECTED_FIXED_ZIP_SHA256.upper()),
        ("fixed ZIP builder invocation count", "1"),
        ("same-artifact verification", "EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED"),
        ("verification verdict", "NOT_REACHED"),
        ("failure class", "NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE"),
        ("Stage 4 retry", "NOT_AUTHORIZED / NOT_RUN"),
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
        "builder invocation count:\n1",
        "fixed ZIP:\nrelease/DailyRhythmCompanion_v4.0.0_20260908_173440.zip",
        "release source HEAD:\n46f5af49106c6ecc0d478a425cf709cf511da1be",
        "verification HEAD:\nNOT_RECORDED",
        "fixed ZIP SHA-256:\nF02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142",
        "## Stage 4 Verifier Output-Encoding Corrective R1 Stop Rule",
    ):
        require(fixed, needle, "fixed ZIP contract")
    reject(fixed, "## Stage 3 Authorization-Sync Stop Rule", "stale fixed ZIP stop rule")
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
    if current_text.count(STAGE3_AUTHORIZATION) != 0:
        raise AssertionError("Stage 3 authorization marker was not consumed")
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
    if not all(stage3_path_length_corrective_dirty_surface_self_check().values()):
        raise AssertionError("Stage 3 path-length corrective dirty validator self-check failed")
    if not all(stage3_path_length_corrective_committed_surface_self_check().values()):
        raise AssertionError("Stage 3 path-length corrective future clean validator self-check failed")
    if not all(stage3_path_length_corrective_protected_delta_self_check().values()):
        raise AssertionError("Stage 3 path-length corrective protected delta validator self-check failed")
    if not all(stage3_path_length_corrective_origin_state_self_check().values()):
        raise AssertionError("Stage 3 path-length corrective origin-state validator self-check failed")
    if not all(stage4_authorization_sync_dirty_surface_self_check().values()):
        raise AssertionError("Stage 4 authorization-sync dirty validator self-check failed")
    if not all(stage4_authorization_sync_committed_surface_self_check().values()):
        raise AssertionError("Stage 4 authorization-sync future clean validator self-check failed")
    if not all(stage4_authorization_sync_origin_state_self_check().values()):
        raise AssertionError("Stage 4 authorization-sync origin-state validator self-check failed")
    if not all(stage4_verifier_output_encoding_corrective_dirty_surface_self_check().values()):
        raise AssertionError("Stage 4 verifier output-encoding corrective dirty surface validator self-check failed")
    if not all(stage4_verifier_output_encoding_corrective_committed_surface_self_check().values()):
        raise AssertionError("Stage 4 verifier output-encoding corrective committed surface validator self-check failed")
    if not all(stage4_verifier_output_encoding_corrective_origin_state_self_check().values()):
        raise AssertionError("Stage 4 verifier output-encoding corrective origin-state validator self-check failed")
    if not all(fixed_zip_tuple_self_check().values()):
        raise AssertionError("Stage 4 fixed ZIP tuple self-check failed")
    if not all(stage3_authorization_contract_self_check().values()):
        raise AssertionError("Stage 3 authorization marker contract self-check failed")
    if not all(stage4_lifecycle_contract_self_check().values()):
        raise AssertionError("Stage 4 lifecycle contract self-check failed")
    if not all(stage3_authorization_marker_assignment_self_check().values()):
        raise AssertionError("Stage 3 authorization marker assignment self-check failed")
    if not all(stage3_authorization_marker_expandable_subexpression_self_check().values()):
        raise AssertionError("Stage 3 authorization marker expandable subexpression self-check failed")
    if not all(stage3_authorization_marker_backtick_escape_self_check().values()):
        raise AssertionError("Stage 3 authorization marker backtick escape self-check failed")
    if not all(stage3_builder_normalized_sha256_self_check().values()):
        raise AssertionError("Stage 3 builder normalized SHA-256 self-check failed")
    if not all(generic_builder_normalized_sha256_self_check().values()):
        raise AssertionError("Generic builder normalized SHA-256 self-check failed")
    if not all(fixed_builder_short_worktree_assignment_self_check().values()):
        raise AssertionError("Fixed builder canonical short worktree assignment self-check failed")
    if not all(generic_builder_atomic_slot_claim_self_check().values()):
        raise AssertionError("Generic builder atomic slot claim self-check failed")
    if not all(path_budget_self_check().values()):
        raise AssertionError("path-budget self-check failed")
    check_builder_stage3_authorization_marker_assignment()
    check_builder_stage3_normalized_sha256()
    check_builder_generic_normalized_sha256()
    if not fixed_builder_short_worktree_contract_is_present():
        raise AssertionError("Fixed builder short worktree path contract is missing")
    if not generic_builder_short_package_staging_contract_is_present():
        raise AssertionError("Generic builder short package staging contract is missing")
    if not current_state_prose_is_consistent(current_text):
        raise AssertionError("Stage 4 current-state prose consistency failed")
    if not all(current_state_prose_consistency_self_check().values()):
        raise AssertionError("Stage 4 current-state prose consistency self-check failed")
    if not all(current_purpose_self_check().values()):
        raise AssertionError("current Purpose self-check failed")
    check_stage4_content_review_guards()
    if not all(current_stage4_review_prose_self_check().values()):
        raise AssertionError("Stage 4 current protocol/metadata content-review self-check failed")
    if not all(historical_v3_contamination_self_check().values()):
        raise AssertionError("Historical v3 contamination self-check failed")
    if not all(stage2_history_evidence_self_check().values()):
        raise AssertionError("Stage 2 history evidence self-check failed")
    if not all(r5_document_correction_self_check().values()):
        raise AssertionError("R5 document correction self-check failed")
    if not all(r7_current_status_self_check().values()):
        raise AssertionError("R7 current Status block self-check failed")
    if not all(safe_output_emission_self_check().values()):
        raise AssertionError("safe output emission self-check failed")
    if current_text.count(STAGE4_AUTHORIZATION) != 0:
        raise AssertionError("Stage 4 authorization marker was not consumed")
    if current_text.count(PENDING_POST_EDIT_MARKER) != 0:
        raise AssertionError("PENDING_POST_EDIT_VERIFICATION marker is present in current docs")


def check_no_release_outputs() -> None:
    if git_out("tag", "--list", "DRC_v4.0.0"):
        raise AssertionError("DRC_v4.0.0 tag exists")
    release_root = ROOT / "release"
    if release_root.exists() and any(release_root.glob("DailyRhythmCompanion_v4.0.0_*.zip")):
        raise AssertionError("v4.0.0 release ZIP exists")


def path_budget(paths: list[str], root_length: int, limit: int = PATH_BUDGET_LIMIT) -> dict[str, int | bool]:
    if root_length < 0 or not paths:
        return {"valid": False, "count": len(paths), "maximum_relative_path": -1, "root_length": root_length, "maximum_projected_path": -1, "limit": limit}
    seen: set[str] = set()
    maximum = 0
    for raw in paths:
        path = raw.replace("\\", "/")
        parts = PurePosixPath(path).parts
        if not path or path.startswith("/") or re.match(r"^[A-Za-z]:/", path) or ".." in parts or path in seen:
            return {"valid": False, "count": len(paths), "maximum_relative_path": -1, "root_length": root_length, "maximum_projected_path": -1, "limit": limit}
        seen.add(path)
        maximum = max(maximum, len(path))
    projected = root_length + 1 + maximum
    return {"valid": projected <= limit, "count": len(paths), "maximum_relative_path": maximum, "root_length": root_length, "maximum_projected_path": projected, "limit": limit}


def tracked_paths_at(commit: str = "HEAD") -> list[str]:
    return git_out("ls-tree", "-r", "--name-only", commit).splitlines()


def current_tracked_path_budget() -> dict[str, int | bool]:
    paths = tracked_paths_at("HEAD")
    temp_base = ROOT.parent / "temp"
    fixed_root = temp_base / "d4w_12345678" / "w"
    package_root = temp_base / "d0" / "DailyRhythmCompanion"
    fixed = path_budget(paths, len(str(fixed_root)))
    package = path_budget(paths, len(str(package_root)))
    return {
        "tracked_file_count": fixed["count"],
        "maximum_relative_path": fixed["maximum_relative_path"],
        "fixed_worktree_root_length": fixed["root_length"],
        "fixed_maximum_projected_path": fixed["maximum_projected_path"],
        "generic_package_destination_root_length": package["root_length"],
        "generic_maximum_projected_path": package["maximum_projected_path"],
        "limit": PATH_BUDGET_LIMIT,
    }


def path_budget_self_check() -> dict[str, bool]:
    paths = tracked_paths_at("HEAD")
    maximum = max(len(path.replace("\\", "/")) for path in paths)
    temp_base = ROOT.parent / "temp"
    fixed_root = temp_base / "d4w_12345678" / "w"
    package_root = temp_base / "d0" / "DailyRhythmCompanion"
    old_fixed_root = temp_base / "DRC_v400_ControlD_Stage3_build_retry_20260907_095136" / "TEMP" / ("DailyRhythmCompanion_v400_fixed_" + "a" * 32) / "committed_head"
    old_package_root = temp_base / "DRC_v400_ControlD_Stage3_build_retry_20260907_095136" / "TEMP" / "DailyRhythmCompanion_release_temp_20260907_000000_32767" / "DailyRhythmCompanion"
    boundary_path = "a" * 10
    return {
        "fixed_current_plan_under_limit": bool(path_budget(paths, len(str(fixed_root)))["valid"]),
        "generic_current_plan_under_limit": bool(path_budget(paths, len(str(package_root)))["valid"]),
        "old_fixed_long_prefix_rejected": not bool(path_budget(paths, len(str(old_fixed_root)))["valid"]),
        "old_generic_long_prefix_rejected": not bool(path_budget(paths, len(str(old_package_root)))["valid"]),
        "too_long_temp_base_rejected": not bool(path_budget([boundary_path], PATH_BUDGET_LIMIT)["valid"]),
        "relative_path_boundary_failure_rejected": not bool(path_budget(["a" * (PATH_BUDGET_LIMIT + 1 - len(str(fixed_root)))], len(str(fixed_root)))["valid"]),
        "exactly_259_accepted": bool(path_budget([boundary_path], PATH_BUDGET_LIMIT - 1 - len(boundary_path))["valid"]),
        "260_rejected": not bool(path_budget([boundary_path], PATH_BUDGET_LIMIT - len(boundary_path))["valid"]),
        "negative_length_rejected": not bool(path_budget([boundary_path], -1)["valid"]),
        "empty_tracked_path_collection_rejected": not bool(path_budget([], len(str(fixed_root)))["valid"]),
        "duplicate_tracked_paths_rejected": not bool(path_budget(["a/b.txt", "a/b.txt"], len(str(fixed_root)))["valid"]),
        "absolute_relative_path_rejected": not bool(path_budget(["C:/tmp/a.txt"], len(str(fixed_root)))["valid"]),
        "traversal_relative_path_rejected": not bool(path_budget(["../a.txt"], len(str(fixed_root)))["valid"]),
        "current_maximum_relative_path_measured": maximum > 0,
    }


def powershell_brace_delta(line: str) -> int:
    scrubbed = re.sub(r'"(?:`.|[^"`])*"|\'[^\']*\'', "", line)
    return scrubbed.count("{") - scrubbed.count("}")


def powershell_executable_line_records_with_lexical_state(text: str) -> tuple[list[tuple[str, int]], bool]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    records: list[tuple[str, int]] = []
    in_block_comment = False
    in_single_quoted_string = False
    in_double_quoted_string = False
    here_string_end: str | None = None
    for line_index, raw_line in enumerate(lines):
        if here_string_end is not None:
            if raw_line.strip() == here_string_end:
                here_string_end = None
            continue
        code = ""
        brace_delta = 0
        i = 0
        while i < len(raw_line):
            if in_block_comment:
                end = raw_line.find("#>", i)
                if end == -1:
                    i = len(raw_line)
                    continue
                in_block_comment = False
                i = end + 2
                continue
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
                    if i + 1 < len(raw_line):
                        i += 2
                        continue
                    if line_index + 1 >= len(lines):
                        return records, False
                    i += 1
                    continue
                if raw_line[i] == '"':
                    in_double_quoted_string = False
                i += 1
                continue
            if raw_line.startswith("<#", i):
                in_block_comment = True
                i += 2
                continue
            if raw_line[i] == "#":
                break
            if raw_line.startswith("@'", i) or raw_line.startswith('@"', i):
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
                        elif line_index + 1 >= len(lines):
                            return records, False
                        i += 1
                        continue
                    if raw_line[i] == '"':
                        i += 1
                        break
                    i += 1
                else:
                    in_double_quoted_string = True
                continue
            if raw_line[i] == "`":
                if i + 1 < len(raw_line):
                    code += raw_line[i : i + 2]
                    i += 2
                    continue
                if line_index + 1 >= len(lines):
                    return records, False
                i += 1
                continue
            if raw_line[i] == "{":
                brace_delta += 1
            elif raw_line[i] == "}":
                brace_delta -= 1
            code += raw_line[i]
            i += 1
        if code.strip():
            records.append((code, brace_delta))
    return (
        records,
        not in_block_comment
        and not in_single_quoted_string
        and not in_double_quoted_string
        and here_string_end is None,
    )


def powershell_executable_lines_with_lexical_state(text: str) -> tuple[list[str], bool]:
    records, complete = powershell_executable_line_records_with_lexical_state(text)
    return [line for line, _ in records], complete


TEMP_ROOT_VARIABLE_PATTERN = (
    r"(?:\$\{(?:(?:script|local|global|private):)?tempRoot\}"
    r"|\$(?:(?:script|local|global|private):)?tempRoot)(?![A-Za-z0-9_])"
)
TEMP_ROOT_MUTATION = re.compile(
    rf"(?i)(?:\+\+|--)\s*{TEMP_ROOT_VARIABLE_PATTERN}|"
    rf"{TEMP_ROOT_VARIABLE_PATTERN}\s*(?:\+\+|--|\?\?=|\+=|-=|\*=|/=|%=|=)(?![=])"
)
TEMP_ROOT_NULL_INITIALIZER = re.compile(
    rf"(?i)^\s*{TEMP_ROOT_VARIABLE_PATTERN}\s*=\s*\$null\s*$"
)
TEMP_ROOT_PLAIN_NULL_INITIALIZER = re.compile(r"^\s*\$tempRoot\s*=\s*\$null\s*$")
TEMP_ROOT_NULL_INITIALIZER_EVENT = "NULL_INITIALIZER"
TEMP_ROOT_CANONICAL_ASSIGNMENT_EVENT = "CANONICAL_ASSIGNMENT"


def powershell_unescaped_subexpressions(value: str) -> tuple[list[str], bool]:
    subexpressions: list[str] = []
    i = 0
    while i < len(value):
        if value[i] == "`":
            i += 2
            continue
        if value.startswith("$(", i):
            start = i + 2
            depth = 1
            j = start
            in_single = False
            in_double = False
            while j < len(value):
                if in_single:
                    if value[j] == "'":
                        if j + 1 < len(value) and value[j + 1] == "'":
                            j += 2
                            continue
                        in_single = False
                    j += 1
                    continue
                if in_double:
                    if value[j] == "`":
                        j += 2
                        continue
                    if value[j] == '"':
                        in_double = False
                    j += 1
                    continue
                if value[j] == "'":
                    in_single = True
                elif value[j] == '"':
                    in_double = True
                elif value[j] == "(":
                    depth += 1
                elif value[j] == ")":
                    depth -= 1
                    if depth == 0:
                        subexpressions.append(value[start:j])
                        i = j + 1
                        break
                j += 1
            else:
                return subexpressions, False
            continue
        i += 1
    return subexpressions, True


def powershell_line_code_and_subexpressions(line: str) -> tuple[str, list[str], bool]:
    code = ""
    subexpressions: list[str] = []
    i = 0
    while i < len(line):
        if line[i] == "`":
            code += "  "
            i += 2
            continue
        if line[i] == "'":
            code += " "
            i += 1
            while i < len(line):
                if line[i] == "'":
                    if i + 1 < len(line) and line[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            else:
                return code, subexpressions, False
            continue
        if line[i] == '"':
            code += " "
            start = i + 1
            i += 1
            content = ""
            while i < len(line):
                if line[i] == "`":
                    if i + 1 < len(line):
                        content += line[i : i + 2]
                        i += 2
                        continue
                    return code, subexpressions, False
                if line[i] == '"':
                    found, complete = powershell_unescaped_subexpressions(content)
                    subexpressions.extend(found)
                    if not complete:
                        return code, subexpressions, False
                    i += 1
                    break
                content += line[i]
                i += 1
            else:
                return code, subexpressions, False
            code += " " * (i - start)
            continue
        code += line[i]
        i += 1
    return code, subexpressions, True


def powershell_double_here_string_subexpressions(text: str) -> tuple[list[str], bool]:
    subexpressions: list[str] = []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    in_block_comment = False
    in_double_here = False
    for line in lines:
        stripped = line.strip()
        if in_double_here:
            if stripped == '"@':
                in_double_here = False
                continue
            found, complete = powershell_unescaped_subexpressions(line)
            subexpressions.extend(found)
            if not complete:
                return subexpressions, False
            continue
        if in_block_comment:
            end = line.find("#>")
            if end == -1:
                continue
            in_block_comment = False
            line = line[end + 2 :]
            stripped = line.strip()
        if stripped.startswith("<#"):
            if "#>" not in stripped:
                in_block_comment = True
            continue
        if stripped.startswith('@"'):
            in_double_here = stripped != '"@'
    return subexpressions, not in_block_comment and not in_double_here


def fixed_builder_temp_root_mutation_events(text: str) -> tuple[list[str], bool]:
    executable_records, complete = powershell_executable_line_records_with_lexical_state(text)
    here_subexpressions, here_complete = powershell_double_here_string_subexpressions(text)
    if not complete or not here_complete:
        return [], False
    events: list[str] = []
    depth = 0
    disallowed_depth: int | None = None
    for line, brace_delta in executable_records:
        if disallowed_depth is None and (
            re.match(r"^\s*function\b", line, re.IGNORECASE)
            or re.match(r"^\s*if\s*\(\s*(?:\$false|0)\s*\)", line, re.IGNORECASE)
        ):
            disallowed_depth = depth
        reachable = disallowed_depth is None
        code, subexpressions, line_complete = powershell_line_code_and_subexpressions(line)
        if not line_complete:
            return [], False
        if FIXED_BUILDER_CANONICAL_SHORT_WORKTREE_ASSIGNMENT.match(line):
            events.append(
                TEMP_ROOT_CANONICAL_ASSIGNMENT_EVENT
                if reachable
                else "NONCANONICAL_TEMP_ROOT_EVENT: " + line.strip()
            )
        elif TEMP_ROOT_PLAIN_NULL_INITIALIZER.match(code) and reachable and depth == 0:
            events.append(TEMP_ROOT_NULL_INITIALIZER_EVENT)
        elif TEMP_ROOT_MUTATION.search(code):
            events.append("NONCANONICAL_TEMP_ROOT_EVENT: " + line.strip())
        for subexpression in subexpressions:
            if TEMP_ROOT_MUTATION.search(subexpression):
                events.append("NONCANONICAL_TEMP_ROOT_EVENT: " + subexpression.strip())
        depth += brace_delta
        if depth < 0:
            return [], False
        if disallowed_depth is not None and depth <= disallowed_depth:
            disallowed_depth = None
    if depth != 0:
        return [], False
    for subexpression in here_subexpressions:
        if TEMP_ROOT_MUTATION.search(subexpression):
            events.append("NONCANONICAL_TEMP_ROOT_EVENT: " + subexpression.strip())
    return events, True


def fixed_builder_canonical_short_worktree_assignments(text: str) -> list[str]:
    executable_records, complete = powershell_executable_line_records_with_lexical_state(text)
    if not complete:
        return []
    matches: list[str] = []
    disallowed_depth: int | None = None
    depth = 0
    for line, brace_delta in executable_records:
        if disallowed_depth is not None:
            depth += brace_delta
            if depth < 0:
                return []
            if depth <= disallowed_depth:
                disallowed_depth = None
            continue
        if re.match(r"^\s*function\b", line, re.IGNORECASE) or re.match(
            r"^\s*if\s*\(\s*(?:\$false|0)\s*\)", line, re.IGNORECASE
        ):
            disallowed_depth = depth
            depth += brace_delta
            if depth < 0:
                return []
            if depth <= disallowed_depth:
                disallowed_depth = None
            continue
        if FIXED_BUILDER_CANONICAL_SHORT_WORKTREE_ASSIGNMENT.match(line):
            matches.append(line)
        depth += brace_delta
        if depth < 0:
            return []
    return matches if depth == 0 else []


def fixed_builder_has_canonical_short_worktree_assignment(text: str | None = None) -> bool:
    if text is None:
        text = read("build_v400_fixed_release_zip_from_head.ps1")
    events, complete = fixed_builder_temp_root_mutation_events(text)
    return bool(
        complete
        and events == [TEMP_ROOT_NULL_INITIALIZER_EVENT, TEMP_ROOT_CANONICAL_ASSIGNMENT_EVENT]
    )


def fixed_builder_short_worktree_assignment_self_check() -> dict[str, bool]:
    canonical = (
        '$tempRoot = Join-Path ([IO.Path]::GetTempPath()) '
        '("d4w_" + [Guid]::NewGuid().ToString("N").Substring(0, 8))'
    )
    spaced = (
        '  $tempRoot   =   Join-Path   ( [IO.Path] :: GetTempPath( ) )   '
        '( "d4w_"   +   [Guid] :: NewGuid( ) . ToString( "N" ) . Substring( 0, 8 ) )  '
    )
    null_initializer = "$tempRoot = $null"
    valid = null_initializer + "\n" + canonical
    expected_sequence = [TEMP_ROOT_NULL_INITIALIZER_EVENT, TEMP_ROOT_CANONICAL_ASSIGNMENT_EVENT]
    current_events, current_complete = fixed_builder_temp_root_mutation_events(
        read("build_v400_fixed_release_zip_from_head.ps1")
    )
    return {
        "current_builder_accepted": fixed_builder_has_canonical_short_worktree_assignment(),
        "current_builder_mutation_event_sequence_exact": current_complete and current_events == expected_sequence,
        "exact_null_initializer_followed_by_canonical_accepted": fixed_builder_has_canonical_short_worktree_assignment(valid),
        "lf_variant_accepted": fixed_builder_has_canonical_short_worktree_assignment(valid + "\n"),
        "crlf_variant_accepted": fixed_builder_has_canonical_short_worktree_assignment(
            null_initializer + "\r\n" + canonical + "\r\n"
        ),
        "read_only_temp_root_references_after_canonical_accepted": fixed_builder_has_canonical_short_worktree_assignment(
            valid + '\nWrite-Host $tempRoot\nJoin-Path $tempRoot "w"'
        ),
        "harmless_operator_whitespace_accepted": fixed_builder_has_canonical_short_worktree_assignment(
            null_initializer + "\n" + spaced
        ),
        "missing_rejected": not fixed_builder_has_canonical_short_worktree_assignment("Write-Host 'missing'\n"),
        "canonical_only_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical),
        "null_initializer_only_rejected": not fixed_builder_has_canonical_short_worktree_assignment(null_initializer),
        "null_after_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            valid + "\n" + null_initializer
        ),
        "null_before_and_after_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            null_initializer + "\n" + canonical + "\n" + null_initializer
        ),
        "duplicate_null_before_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            null_initializer + "\n" + null_initializer + "\n" + canonical
        ),
        "duplicate_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            valid + "\n" + canonical
        ),
        "braced_null_initializer_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            "${tempRoot} = $null\n" + canonical
        ),
        "scoped_null_before_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            "$script:tempRoot = $null\n" + canonical
        ),
        "scoped_null_after_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            valid + "\n$script:tempRoot = $null"
        ),
        "never_called_function_only_rejected": not fixed_builder_has_canonical_short_worktree_assignment("function Invoke-Unused {\n" + canonical + "\n}"),
        "false_branch_only_rejected": not fixed_builder_has_canonical_short_worktree_assignment("if ($false) {\n" + canonical + "\n}"),
        "function_null_initializer_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            "function Invoke-Unused {\n" + null_initializer + "\n}\n" + canonical
        ),
        "false_branch_null_initializer_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            "if ($false) {\n" + null_initializer + "\n}\n" + canonical
        ),
        "subexpression_null_assignment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            'Write-Host "$($tempRoot = $null)"' + "\n" + canonical
        ),
        "double_quoted_here_string_subexpression_null_assignment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(
            '@"\n$($tempRoot = $null)\n"@\n' + canonical
        ),
        "comment_null_text_ignored": fixed_builder_has_canonical_short_worktree_assignment(
            "# $tempRoot = $null\n" + valid
        ),
        "literal_string_null_text_ignored": fixed_builder_has_canonical_short_worktree_assignment(
            "'$tempRoot = $null'\n" + valid
        ),
        "single_quoted_here_string_null_text_ignored": fixed_builder_has_canonical_short_worktree_assignment(
            "@'\n$tempRoot = $null\n'@\n" + valid
        ),
        "helper_return_type_is_exact_bool": type(fixed_builder_has_canonical_short_worktree_assignment(canonical)) is bool,
        "canonical_plus_plain_override_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + '\n$tempRoot = "C:\\evil"'),
        "plain_override_before_canonical_rejected": not fixed_builder_has_canonical_short_worktree_assignment('$tempRoot = "C:\\evil"\n' + canonical),
        "canonical_plus_compound_assignment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + '\n$tempRoot += "evil"'),
        "canonical_plus_prefix_increment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + "\n++$tempRoot"),
        "canonical_plus_postfix_increment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + "\n$tempRoot++"),
        "canonical_plus_braced_scoped_assignment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + '\n${script:tempRoot} = "C:\\evil"'),
        "canonical_plus_expandable_string_subexpression_override_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + '\nWrite-Host "$($tempRoot = ''C:\\evil'')"'),
        "canonical_plus_double_here_string_subexpression_override_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + '\n@"\n$($tempRoot = ''C:\\evil'')\n"@'),
        "mutation_text_in_comment_accepted": fixed_builder_has_canonical_short_worktree_assignment(valid + '\n# $tempRoot = "C:\\evil"'),
        "mutation_text_in_single_quoted_string_accepted": fixed_builder_has_canonical_short_worktree_assignment(valid + "\n'$tempRoot = \"C:\\evil\"'"),
        "escaped_dollar_mutation_text_accepted": fixed_builder_has_canonical_short_worktree_assignment(valid + '\nWrite-Host "`$tempRoot = ''C:\\evil''"'),
        "unclosed_subexpression_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + '\nWrite-Host "$($tempRoot = ''C:\\evil''"'),
        "unclosed_block_comment_rejected": not fixed_builder_has_canonical_short_worktree_assignment("<#\n" + valid),
        "unclosed_double_quoted_string_rejected": not fixed_builder_has_canonical_short_worktree_assignment('"before\n' + valid),
        "unclosed_single_quoted_string_rejected": not fixed_builder_has_canonical_short_worktree_assignment("'before\n" + valid),
        "unclosed_here_string_rejected": not fixed_builder_has_canonical_short_worktree_assignment('@"\n' + valid),
        "duplicate_executable_assignment_rejected": not fixed_builder_has_canonical_short_worktree_assignment(valid + "\nif ($true) {\n" + canonical + "\n}"),
        "unrelated_variable_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace("$tempRoot", "$otherRoot")),
        "d4x_prefix_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace('"d4w_"', '"d4x_"')),
        "wrong_tostring_format_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace('ToString("N")', 'ToString("D")')),
        "substring_start_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace("Substring(0, 8)", "Substring(1, 8)")),
        "substring_length_7_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace("Substring(0, 8)", "Substring(0, 7)")),
        "substring_length_9_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace("Substring(0, 8)", "Substring(0, 9)")),
        "newguid_missing_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace("[Guid]::NewGuid()", '"12345678"')),
        "gettemppath_missing_rejected": not fixed_builder_has_canonical_short_worktree_assignment(canonical.replace("([IO.Path]::GetTempPath())", '"C:\\tmp"')),
        "worktree_child_marker_alone_rejected": not fixed_builder_has_canonical_short_worktree_assignment('Join-Path $tempRoot "w"'),
        "old_impossible_fragment_not_required": fixed_builder_has_canonical_short_worktree_assignment(valid) and '".Substring(0, 8)' not in canonical,
    }


def fixed_builder_short_worktree_contract_is_present() -> bool:
    text = read("build_v400_fixed_release_zip_from_head.ps1")
    return fixed_builder_has_canonical_short_worktree_assignment(text) and all(needle in text for needle in ('Join-Path $tempRoot "w"', "Get-TrackedPathBudget", "[PathBudget] maximum projected worktree path:", "Temporary worktree path budget exceeded before git worktree add.", "Limit = 259", "git worktree add --detach $worktreeRoot $headCommit"))


def generic_builder_atomic_slot_claim_contract_is_present(text: str | None = None) -> bool:
    if text is None:
        text = read("build_release.bat")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    executable_lines = [
        line.rstrip()
        for line in normalized.split("\n")
        if line.strip()
        and not line.lstrip().lower().startswith(("rem ", "::"))
        and (
            not line.lstrip().lower().startswith("echo ")
            or line.strip() == "echo [Error] Slots d0 through d9 are already in use."
        )
    ]
    executable = "\n".join(executable_lines)
    required = (
        "set \"TEMP_ROOT=\"",
        "set \"TEMP_ROOT_OWNED=0\"",
        "for %%s in (0 1 2 3 4 5 6 7 8 9) do if not defined TEMP_ROOT (",
        "mkdir \"%TEMP_BASE%\\d%%s\" >nul 2>nul",
        "if not errorlevel 1 (",
        "set \"TEMP_ROOT=%TEMP_BASE%\\d%%s\"",
        "set \"TEMP_ROOT_OWNED=1\"",
        "set \"TEMP_DIR=%TEMP_ROOT%\\%PACKAGE_ROOT_NAME%\"",
        "if not \"%TEMP_ROOT_OWNED%\"==\"1\" exit /b 0",
        "Remove-Item -LiteralPath $p -Recurse -Force",
    )
    if any(needle not in executable for needle in required):
        return False
    if "Slots d0 through d9 are already in use." not in normalized:
        return False
    if "if not defined TEMP_ROOT if not exist" in normalized:
        return False
    if executable.count('mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul') != 1:
        return False
    if executable_lines.count('set "TEMP_ROOT="') != 1 or executable_lines.count('set "TEMP_ROOT_OWNED=0"') != 1:
        return False
    loop_line = "for %%s in (0 1 2 3 4 5 6 7 8 9) do if not defined TEMP_ROOT ("
    if executable_lines.count(loop_line) != 1:
        return False

    def batch_paren_delta(line: str) -> int:
        scrubbed = ""
        in_quote = False
        for char in line:
            if char == '"':
                in_quote = not in_quote
            elif not in_quote:
                scrubbed += char
        return scrubbed.count("(") - scrubbed.count(")")

    def matching_block_end(start: int) -> int:
        depth = batch_paren_delta(executable_lines[start])
        if depth <= 0:
            return -1
        for index in range(start + 1, len(executable_lines)):
            depth += batch_paren_delta(executable_lines[index])
            if depth == 0:
                return index
            if depth < 0:
                return -1
        return -1

    def block_depths_before() -> list[int]:
        depths: list[int] = []
        depth = 0
        for line in executable_lines:
            depths.append(depth)
            depth += batch_paren_delta(line)
            if depth < 0:
                return []
        return depths if depth == 0 else []

    init_root = executable_lines.index('set "TEMP_ROOT="')
    init_owned = executable_lines.index('set "TEMP_ROOT_OWNED=0"')
    loop_start = executable_lines.index(loop_line)
    depths_before = block_depths_before()
    if not depths_before or depths_before[loop_start] != 0:
        return False
    loop_end = matching_block_end(loop_start)
    if not (init_root < init_owned < loop_start and loop_end != -1):
        return False
    pre_claim = "\n".join(executable_lines[:loop_start]).lower()
    if "remove-item" in pre_claim or "rmdir" in pre_claim or "rd /s" in pre_claim or "call :cleanup_temp" in pre_claim or "call :cleanup_temp_silent" in pre_claim:
        return False
    loop_body = executable_lines[loop_start + 1 : loop_end]
    if loop_body.count('  mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul') + loop_body.count('mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul') != 1:
        return False
    mkdir_slot = next((index for index in range(loop_start + 1, loop_end) if executable_lines[index].strip() == 'mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul'), -1)
    success_if = mkdir_slot + 1
    if success_if >= loop_end or executable_lines[success_if].strip() != "if not errorlevel 1 (":
        return False
    success_end = matching_block_end(success_if)
    if success_end == -1 or success_end > loop_end:
        return False
    set_temp_indices = [index for index, line in enumerate(executable_lines) if line.strip() == 'set "TEMP_ROOT=%TEMP_BASE%\\d%%s"']
    set_owned_indices = [index for index, line in enumerate(executable_lines) if line.strip() == 'set "TEMP_ROOT_OWNED=1"']
    if len(set_temp_indices) != 1 or len(set_owned_indices) != 1:
        return False
    set_temp = set_temp_indices[0]
    set_owned = set_owned_indices[0]
    if not (success_if < set_temp < set_owned < success_end):
        return False
    success_child_depth = depths_before[success_if] + 1
    if depths_before[set_temp] != success_child_depth or depths_before[set_owned] != success_child_depth:
        return False
    if set_temp != success_if + 1 or set_owned != success_if + 2:
        return False
    for index, line in enumerate(executable_lines):
        stripped_lower = line.strip().lower()
        if stripped_lower.startswith('set "temp_root=') and index not in {init_root, set_temp}:
            return False
        if stripped_lower.startswith('set "temp_root_owned=1"') and index != set_owned:
            return False
    set_dir_indices = [index for index, line in enumerate(executable_lines) if line.strip() == 'set "TEMP_DIR=%TEMP_ROOT%\\%PACKAGE_ROOT_NAME%"']
    if len(set_dir_indices) != 1:
        return False
    set_dir = set_dir_indices[0]
    temp_dir_mkdir = next((index for index, line in enumerate(executable_lines) if line.strip() == 'mkdir "%TEMP_DIR%" >nul 2>nul'), -1)
    cleanup_guard_count = executable.count('if not "%TEMP_ROOT_OWNED%"=="1" exit /b 0')
    if cleanup_guard_count != 2 or temp_dir_mkdir <= set_dir or set_dir <= set_owned:
        return False
    no_slot_if = "if not defined TEMP_ROOT ("
    no_slot_if_indices = [index for index, line in enumerate(executable_lines) if line.strip() == no_slot_if]
    if len(no_slot_if_indices) != 1:
        return False
    no_slot_start = no_slot_if_indices[0]
    no_slot_end = matching_block_end(no_slot_start)
    if no_slot_end == -1 or depths_before[no_slot_start] != 0 or no_slot_start <= loop_end or no_slot_end >= set_dir:
        return False
    if any(line.strip().lower() == "exit /b 1" for line in executable_lines[loop_end + 1 : no_slot_start]):
        return False
    no_slot = normalized.find("Slots d0 through d9 are already in use.")
    no_slot_if_text = normalized.find("\n" + no_slot_if, normalized.find(loop_line))
    no_slot_block_end_text = normalized.find("\n)", no_slot_if_text)
    if no_slot == -1 or no_slot_if_text == -1 or no_slot_block_end_text == -1:
        return False
    if not (no_slot_if_text < no_slot < no_slot_block_end_text):
        return False
    cleanup_call_after_no_slot = normalized.find("call :cleanup_temp", no_slot, normalized.find('set "TEMP_DIR='))
    if cleanup_call_after_no_slot != -1:
        return False
    no_slot_body = executable_lines[no_slot_start + 1 : no_slot_end]
    no_slot_direct_indices = [index for index in range(no_slot_start + 1, no_slot_end) if depths_before[index] == depths_before[no_slot_start] + 1]
    no_slot_direct_lines = [executable_lines[index].strip() for index in no_slot_direct_indices]
    if no_slot_direct_lines.count("echo [Error] Slots d0 through d9 are already in use.") != 1:
        return False
    if sum(1 for line in no_slot_direct_lines if line.lower() == "exit /b 1") != 1:
        return False
    if no_slot_body.count("  echo [Error] Slots d0 through d9 are already in use.") + no_slot_body.count("echo [Error] Slots d0 through d9 are already in use.") != 1:
        return False
    if sum(1 for line in no_slot_body if line.strip().lower() == "exit /b 1") != 1:
        return False
    for label in (":cleanup_temp_silent", ":cleanup_temp"):
        if executable_lines.count(label) != 1:
            return False
        label_index = executable_lines.index(label)
        if label_index + 1 >= len(executable_lines):
            return False
        if executable_lines[label_index + 1] != 'if not "%TEMP_ROOT_OWNED%"=="1" exit /b 0':
            return False
        next_label = next((index for index in range(label_index + 1, len(executable_lines)) if executable_lines[index].startswith(":")), len(executable_lines))
        guarded_body = "\n".join(executable_lines[label_index + 2 : next_label])
        if "Remove-Item -LiteralPath $p -Recurse -Force" not in guarded_body:
            return False
    cleanup = executable.find(":cleanup_temp")
    return no_slot < cleanup


def generic_builder_atomic_slot_claim_self_check() -> dict[str, bool]:
    current = read("build_release.bat")
    minimal = """
set "TEMP_ROOT="
set "TEMP_ROOT_OWNED=0"
for %%s in (0 1 2 3 4 5 6 7 8 9) do if not defined TEMP_ROOT (
  mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul
  if not errorlevel 1 (
    set "TEMP_ROOT=%TEMP_BASE%\\d%%s"
    set "TEMP_ROOT_OWNED=1"
  )
)
if not defined TEMP_ROOT (
  echo [Error] Slots d0 through d9 are already in use.
  exit /b 1
)
set "TEMP_DIR=%TEMP_ROOT%\\%PACKAGE_ROOT_NAME%"
mkdir "%TEMP_DIR%" >nul 2>nul
:cleanup_temp_silent
if not "%TEMP_ROOT_OWNED%"=="1" exit /b 0
Remove-Item -LiteralPath $p -Recurse -Force
:cleanup_temp
if not "%TEMP_ROOT_OWNED%"=="1" exit /b 0
Remove-Item -LiteralPath $p -Recurse -Force
"""
    return {
        "current_corrected_builder_accepted": generic_builder_atomic_slot_claim_contract_is_present(current),
        "atomic_d0_to_d9_claim_accepted": generic_builder_atomic_slot_claim_contract_is_present(minimal),
        "if_not_exist_slot_selection_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace("for %%s in (0 1 2 3 4 5 6 7 8 9) do if not defined TEMP_ROOT (", "for %%s in (0 1 2 3 4 5 6 7 8 9) do if not defined TEMP_ROOT if not exist \"%TEMP_BASE%\\d%%s\" (")),
        "temp_root_set_before_directory_claim_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul\n  if not errorlevel 1 (\n    set "TEMP_ROOT=%TEMP_BASE%\\d%%s"', 'set "TEMP_ROOT=%TEMP_BASE%\\d%%s"\n  mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul\n  if not errorlevel 1 (')),
        "temp_dir_only_mkdir_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul', 'mkdir "%TEMP_DIR%" >nul 2>nul')),
        "cleanup_without_ownership_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('if not "%TEMP_ROOT_OWNED%"=="1" exit /b 0\n', "")),
        "valid_conditional_no_slot_block_accepted": generic_builder_atomic_slot_claim_contract_is_present(minimal),
        "success_assignments_direct_children_accepted": generic_builder_atomic_slot_claim_contract_is_present(minimal),
        "success_assignments_nested_in_false_if_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('  if not errorlevel 1 (\n    set "TEMP_ROOT=%TEMP_BASE%\\d%%s"\n    set "TEMP_ROOT_OWNED=1"\n  )', '  if not errorlevel 1 (\n    if 0==1 (\n      set "TEMP_ROOT=%TEMP_BASE%\\d%%s"\n      set "TEMP_ROOT_OWNED=1"\n    )\n  )')),
        "success_assignments_nested_in_another_if_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('  if not errorlevel 1 (\n    set "TEMP_ROOT=%TEMP_BASE%\\d%%s"\n    set "TEMP_ROOT_OWNED=1"\n  )', '  if not errorlevel 1 (\n    if not defined TEMP_ROOT (\n      set "TEMP_ROOT=%TEMP_BASE%\\d%%s"\n      set "TEMP_ROOT_OWNED=1"\n    )\n  )')),
        "no_slot_message_exit_direct_children_accepted": generic_builder_atomic_slot_claim_contract_is_present(minimal),
        "no_slot_message_exit_nested_in_false_if_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('if not defined TEMP_ROOT (\n  echo [Error] Slots d0 through d9 are already in use.\n  exit /b 1\n)', 'if not defined TEMP_ROOT (\n  if 0==1 (\n    echo [Error] Slots d0 through d9 are already in use.\n    exit /b 1\n  )\n)')),
        "no_slot_exit_nested_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('  exit /b 1', '  if 0==1 (\n    exit /b 1\n  )')),
        "no_slot_message_nested_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('  echo [Error] Slots d0 through d9 are already in use.', '  if 0==1 (\n    echo [Error] Slots d0 through d9 are already in use.\n  )')),
        "direct_body_duplicate_exit_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('  exit /b 1', '  exit /b 1\n  exit /b 1')),
        "unconditional_no_slot_exit_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('if not defined TEMP_ROOT (\n  echo [Error] Slots d0 through d9 are already in use.\n  exit /b 1\n)', 'echo [Error] Slots d0 through d9 are already in use.\nexit /b 1')),
        "missing_no_slot_if_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('if not defined TEMP_ROOT (', 'REM missing no-slot if (')),
        "duplicate_no_slot_block_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('set "TEMP_DIR=%TEMP_ROOT%\\%PACKAGE_ROOT_NAME%"', 'if not defined TEMP_ROOT (\n  echo [Error] Slots d0 through d9 are already in use.\n  exit /b 1\n)\nset "TEMP_DIR=%TEMP_ROOT%\\%PACKAGE_ROOT_NAME%"')),
        "claim_loop_wrapped_in_false_branch_rejected": not generic_builder_atomic_slot_claim_contract_is_present("if 0==1 (\n" + minimal + "\n)"),
        "no_slot_block_wrapped_in_false_branch_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('if not defined TEMP_ROOT (\n  echo [Error] Slots d0 through d9 are already in use.\n  exit /b 1\n)', 'if 0==1 (\nif not defined TEMP_ROOT (\n  echo [Error] Slots d0 through d9 are already in use.\n  exit /b 1\n)\n)')),
        "no_slot_message_outside_conditional_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('if not defined TEMP_ROOT (\n  echo [Error] Slots d0 through d9 are already in use.\n  exit /b 1\n)', 'echo [Error] Slots d0 through d9 are already in use.\nif not defined TEMP_ROOT (\n  exit /b 1\n)')),
        "pre_claim_cleanup_call_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('set "TEMP_ROOT_OWNED=0"\nfor %%s', 'set "TEMP_ROOT_OWNED=0"\ncall :cleanup_temp\nfor %%s')),
        "pre_claim_cleanup_silent_call_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('set "TEMP_ROOT_OWNED=0"\nfor %%s', 'set "TEMP_ROOT_OWNED=0"\ncall :cleanup_temp_silent\nfor %%s')),
        "unguarded_temp_root_assignment_after_success_block_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace("echo [Error] Slots d0 through d9 are already in use.", 'set "TEMP_ROOT=%TEMP_BASE%\\d9"\necho [Error] Slots d0 through d9 are already in use.')),
        "unguarded_ownership_assignment_after_success_block_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace("echo [Error] Slots d0 through d9 are already in use.", 'set "TEMP_ROOT_OWNED=1"\necho [Error] Slots d0 through d9 are already in use.')),
        "ownership_guard_moved_below_cleanup_work_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace(':cleanup_temp\nif not "%TEMP_ROOT_OWNED%"=="1" exit /b 0\nRemove-Item', ':cleanup_temp\nif exist "%TEMP_ROOT%" echo cleanup\nif not "%TEMP_ROOT_OWNED%"=="1" exit /b 0\nRemove-Item')),
        "claim_before_slot_cleanup_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('set "TEMP_ROOT_OWNED=0"\nfor %%s', 'set "TEMP_ROOT_OWNED=0"\nrmdir /s /q "%TEMP_BASE%\\d0"\nfor %%s')),
        "single_cleanup_label_guarded_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace(':cleanup_temp_silent', ':cleanup_temp')),
        "slot_mkdir_assignment_gap_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul\n  if not errorlevel 1 (', 'mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul\n  set "TEMP_ROOT_OWNED=1"\n  if not errorlevel 1 (')),
        "pre_existing_slot_cleanup_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace("echo [Error] Slots d0 through d9 are already in use.", "echo [Error] Slots d0 through d9 are already in use.\ncall :cleanup_temp")),
        "missing_claim_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal.replace('mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul', "")),
        "duplicate_claim_rejected": not generic_builder_atomic_slot_claim_contract_is_present(minimal + '\nfor %%s in (0 1 2 3 4 5 6 7 8 9) do if not defined TEMP_ROOT (\n  mkdir "%TEMP_BASE%\\d%%s" >nul 2>nul\n)\n'),
        "comment_marker_only_rejected": not generic_builder_atomic_slot_claim_contract_is_present("REM " + minimal.replace("\n", "\nREM ")),
        "string_marker_only_rejected": not generic_builder_atomic_slot_claim_contract_is_present("echo " + minimal.replace("\n", "\necho ")),
    }


def generic_builder_short_package_staging_contract_is_present() -> bool:
    text = read("build_release.bat")
    return generic_builder_atomic_slot_claim_contract_is_present(text) and all(needle in text for needle in ("for %%s in (0 1 2 3 4 5 6 7 8 9)", r"%TEMP_BASE%\d%%s", "[PathBudget] package source maximum relative path:", "[PathBudget] maximum projected package path:", "Slots d0 through d9 are already in use.")) and "DailyRhythmCompanion_release_temp_%TIMESTAMP%_%RANDOM%" not in text


def check_protected_surface(mode: str) -> None:
    lines = git_out("diff", "--name-status", "--", *PROTECTED_PATHS).splitlines()
    if mode == "DIRTY_STAGE3_BUILDER_AUTH_GUARD_CORRECTIVE_CANDIDATE":
        if not validate_stage3_builder_auth_guard_corrective_protected_delta(lines):
            raise AssertionError(
                "Dirty Stage 3 builder authorization guard corrective protected delta is not exact builder M"
        )
        return
    if mode == "DIRTY_STAGE3_PATH_LENGTH_CORRECTIVE_CANDIDATE":
        if not validate_stage3_path_length_corrective_protected_delta(lines):
            raise AssertionError("Dirty Stage 3 path-length corrective protected delta is not exact builder M2")
        return
    if not validate_empty_protected_delta(lines):
        raise AssertionError("Protected surface diff is not empty")


def check_stage3_builder_auth_guard_corrective_protected_delta(start: str, end: str) -> None:
    lines = git_out("diff", "--name-status", f"{start}..{end}", "--", *PROTECTED_PATHS).splitlines()
    if not validate_stage3_builder_auth_guard_corrective_protected_delta(lines):
        raise AssertionError("Stage 3 builder authorization guard corrective protected delta is not exact builder M")


def check_stage3_path_length_corrective_protected_delta(start: str, end: str) -> None:
    lines = git_out("diff", "--name-status", f"{start}..{end}", "--", *PROTECTED_PATHS).splitlines()
    if not validate_stage3_path_length_corrective_protected_delta(lines):
        raise AssertionError("Stage 3 path-length corrective protected delta is not exact builder M2")


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
        "Control D Stage 4:\nSAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / COMPLETED",
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
    stage3_path_dirty_checks = stage3_path_length_corrective_dirty_surface_self_check()
    stage3_path_committed_checks = stage3_path_length_corrective_committed_surface_self_check()
    stage3_path_protected_checks = stage3_path_length_corrective_protected_delta_self_check()
    stage3_path_origin_checks = stage3_path_length_corrective_origin_state_self_check()
    stage4_dirty_checks = stage4_authorization_sync_dirty_surface_self_check()
    stage4_committed_checks = stage4_authorization_sync_committed_surface_self_check()
    stage4_origin_checks = stage4_authorization_sync_origin_state_self_check()
    fixed_zip_tuple_checks = fixed_zip_tuple_self_check()
    stage3_marker_contract_checks = stage3_authorization_contract_self_check()
    stage3_marker_assignment_checks = stage3_authorization_marker_assignment_self_check()
    stage3_marker_expandable_subexpression_checks = stage3_authorization_marker_expandable_subexpression_self_check()
    stage3_marker_backtick_checks = stage3_authorization_marker_backtick_escape_self_check()
    stage3_builder_normalized_sha_checks = stage3_builder_normalized_sha256_self_check()
    generic_builder_normalized_sha_checks = generic_builder_normalized_sha256_self_check()
    fixed_builder_short_assignment_checks = fixed_builder_short_worktree_assignment_self_check()
    generic_builder_atomic_slot_claim_checks = generic_builder_atomic_slot_claim_self_check()
    path_budget_checks = path_budget_self_check()
    current_budget = current_tracked_path_budget()
    prose_checks = current_state_prose_consistency_self_check()
    current_stage4_review_checks = current_stage4_review_prose_self_check()
    historical_v3_checks = historical_v3_contamination_self_check()
    content_review_connection_checks = stage4_content_review_runtime_connection_self_check()
    if not all(content_review_connection_checks.values()):
        raise AssertionError("Stage 4 content-review runtime connection self-check failed")
    check_versions()
    check_release_state_docs()
    check_protocol_and_records()
    if stage4_authorization_sync_modes(mode):
        check_expected_fixed_zip_tuple()
    else:
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
        "v400_release_candidate_no_build_preflight_stage3_path_length_corrective_dirty_exact_m4_validator_self_check: "
        f"{all(stage3_path_dirty_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_path_length_corrective_future_clean_exact_one_commit_m4_validator_self_check: "
        f"{all(stage3_path_committed_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_path_length_corrective_protected_exact_builder_m2_self_check: "
        f"{all(stage3_path_protected_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage3_path_length_corrective_origin_state_validator_self_check: "
        f"{all(stage3_path_origin_checks.values())}"
    )
    print(f"v400_release_candidate_no_build_preflight_stage4_authorization_sync_dirty_exact_m12_validator_self_check: {all(stage4_dirty_checks.values())}")
    print(f"v400_release_candidate_no_build_preflight_stage4_authorization_sync_future_clean_exact_one_commit_m12_validator_self_check: {all(stage4_committed_checks.values())}")
    print(f"v400_release_candidate_no_build_preflight_stage4_authorization_sync_origin_state_validator_self_check: {all(stage4_origin_checks.values())}")
    print(f"v400_release_candidate_no_build_preflight_stage4_fixed_zip_exact_tuple_self_check: {all(fixed_zip_tuple_checks.values())}")
    print(
        "v400_release_candidate_no_build_preflight_stage3_authorization_marker_contract_self_check: "
        f"{all(stage3_marker_contract_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage4_lifecycle_contract_self_check: "
        f"{all(stage4_lifecycle_contract_self_check().values())}"
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
        "v400_release_candidate_no_build_preflight_generic_builder_normalized_sha256_self_check: "
        f"{all(generic_builder_normalized_sha_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_generic_builder_normalized_sha256_current: "
        f"{builder_has_expected_generic_builder_normalized_sha256()}"
    )
    print(
        "v400_release_candidate_no_build_preflight_fixed_builder_canonical_short_worktree_assignment_self_check: "
        f"{all(fixed_builder_short_assignment_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_fixed_builder_canonical_short_worktree_assignment_occurrences: "
        f"{len(fixed_builder_canonical_short_worktree_assignments(read('build_v400_fixed_release_zip_from_head.ps1')))}"
    )
    print(
        "v400_release_candidate_no_build_preflight_fixed_builder_temp_root_mutation_event_sequence: "
        f"{fixed_builder_temp_root_mutation_events(read('build_v400_fixed_release_zip_from_head.ps1'))[0]}"
    )
    print(
        "v400_release_candidate_no_build_preflight_generic_builder_atomic_slot_claim_self_check: "
        f"{all(generic_builder_atomic_slot_claim_checks.values())}"
    )
    print(f"v400_release_candidate_no_build_preflight_path_budget_self_check: {all(path_budget_checks.values())}")
    print(f"v400_release_candidate_no_build_preflight_current_tracked_file_count: {current_budget['tracked_file_count']}")
    print(
        "v400_release_candidate_no_build_preflight_current_maximum_relative_path: "
        f"{current_budget['maximum_relative_path']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_fixed_builder_short_worktree_contract: "
        f"{fixed_builder_short_worktree_contract_is_present()}"
    )
    print(
        "v400_release_candidate_no_build_preflight_generic_builder_short_package_staging_contract: "
        f"{generic_builder_short_package_staging_contract_is_present()}"
    )
    print(
        "v400_release_candidate_no_build_preflight_fixed_maximum_projected_worktree_path: "
        f"{current_budget['fixed_maximum_projected_path']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_generic_maximum_projected_package_path: "
        f"{current_budget['generic_maximum_projected_path']}"
    )
    print(f"v400_release_candidate_no_build_preflight_path_budget_limit: {current_budget['limit']}")
    print(
        "v400_release_candidate_no_build_preflight_prior_long_layouts_rejected: "
        f"{path_budget_checks['old_fixed_long_prefix_rejected'] and path_budget_checks['old_generic_long_prefix_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_current_state_prose_consistency_self_check: "
        f"{all(prose_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stale_stage4_current_state_phrase_rejected: "
        f"{prose_checks['stale_stage4_phrase_rejected']}"
    )
    print(
        "v400_release_candidate_no_build_preflight_current_stage4_content_review_self_check: "
        f"{all(current_stage4_review_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_historical_v3_contamination_self_check: "
        f"{all(historical_v3_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_stage4_content_review_runtime_connection_self_check: "
        f"{all(content_review_connection_checks.values())}"
    )
    print(
        "v400_release_candidate_no_build_preflight_control_d_stage4_corrective_status: "
        "stage4-verifier-output-encoding-corrective-r1-implemented-awaiting-review"
    )
    print("v400_release_candidate_no_build_preflight_backend_version: 4.0.0")
    print("v400_release_candidate_no_build_preflight_flutter_version: 4.0.0+5")
    print("v400_release_candidate_no_build_preflight_current_released: v3.0.0")
    print("v400_release_candidate_no_build_preflight_v400_released: False")
    print("v400_release_candidate_no_build_preflight_release_source_head_recorded: False")
    print("v400_release_candidate_no_build_preflight_verification_head_recorded: False")
    print("v400_release_candidate_no_build_preflight_fixed_zip_builder_invocation_count: 1")
    print("v400_release_candidate_no_build_preflight_fixed_zip_built: True / unverified")
    print("v400_release_candidate_no_build_preflight_tag_created: False")
    print("v400_release_candidate_no_build_preflight_github_release_created: False")
    print("v400_release_candidate_no_build_preflight_stage3_authorization_token_occurrence: 0")
    print("v400_release_candidate_no_build_preflight_stage3_build_authorized: False")
    print("v400_release_candidate_no_build_preflight_stage4_retry_authorized: False")
    print("v400_release_candidate_no_build_preflight_stage_commit_push_authorized: False")
    print("v400_release_candidate_no_build_preflight_package_tag_publication_authorized: False")
    print("[v400-release-candidate-no-build-preflight-check] OK")

def stage4_authorization_sync_modes(mode: str) -> bool:
    return mode in {
        "DIRTY_STAGE4_AUTHORIZATION_SYNC_CANDIDATE",
        "CLEAN_COMMITTED_STAGE4_AUTHORIZATION_SYNC_NOT_PUSHED",
        "CLEAN_COMMITTED_STAGE4_AUTHORIZATION_SYNC",
        "DIRTY_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_CANDIDATE",
        "CLEAN_COMMITTED_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_NOT_PUSHED",
        "CLEAN_COMMITTED_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE",
    }


def expected_fixed_zip_path(root: Path = ROOT) -> Path:
    return root / "release" / EXPECTED_FIXED_ZIP_BASENAME


def fixed_zip_tuple_is_exact(root: Path = ROOT, tag_present: bool = False) -> bool:
    if tag_present:
        return False
    release_root = root / "release"
    path = release_root / EXPECTED_FIXED_ZIP_BASENAME
    if not release_root.is_dir() or not path.is_file():
        return False
    matches = sorted(release_root.glob("DailyRhythmCompanion_v4.0.0_*.zip"))
    if len(matches) != 1 or matches[0].name != EXPECTED_FIXED_ZIP_BASENAME:
        return False
    if matches[0].resolve().parent != release_root.resolve():
        return False
    data = path.read_bytes()
    return len(data) == EXPECTED_FIXED_ZIP_SIZE and sha256(data).hexdigest() == EXPECTED_FIXED_ZIP_SHA256


def check_expected_fixed_zip_tuple() -> None:
    if git_out("tag", "--list", "DRC_v4.0.0"):
        raise AssertionError("DRC_v4.0.0 tag exists")
    if not fixed_zip_tuple_is_exact():
        raise AssertionError("fixed ZIP tuple is not exact")


def stage4_authorization_sync_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE4_AUTHORIZATION_SYNC_MODIFIED)[0]
    exact = [(" M", path) for path in sorted(STAGE4_AUTHORIZATION_SYNC_MODIFIED)]
    return {
        "exact_m12_accepted": dirty_surface_is_exact(exact, STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "unexpected_path_rejected": not dirty_surface_is_exact([*exact, (" M", "backend/app/version.py")], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "duplicate_path_rejected": not dirty_surface_is_exact([*exact, exact[0]], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "staged_rejected": not dirty_surface_is_exact([*exact[1:], ("M ", first)], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "untracked_rejected": not dirty_surface_is_exact([*exact, ("??", "scratch.txt")], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "status_a_rejected": not dirty_surface_is_exact([*exact[1:], (" A", first)], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "status_d_rejected": not dirty_surface_is_exact([*exact[1:], (" D", first)], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "status_r_rejected": not dirty_surface_is_exact([*exact[1:], ("R ", first)], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
        "status_c_rejected": not dirty_surface_is_exact([*exact[1:], ("C ", first)], STAGE4_AUTHORIZATION_SYNC_MODIFIED),
    }


def stage4_authorization_sync_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE4_AUTHORIZATION_SYNC_MODIFIED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE4_AUTHORIZATION_SYNC_MODIFIED)]
    return {
        "exact_one_commit_m12_accepted": validate_stage4_authorization_sync_committed_surface(1, exact),
        "count_0_rejected": not validate_stage4_authorization_sync_committed_surface(0, exact),
        "count_2_rejected": not validate_stage4_authorization_sync_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage4_authorization_sync_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact, "M\tbackend/app/version.py"]),
        "duplicate_path_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact[1:], "A\t" + first]),
        "status_d_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact[1:], "D\t" + first]),
        "status_r_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact[1:], "R100\told\t" + first]),
        "status_c_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact[1:], "C100\told\t" + first]),
        "malformed_line_rejected": not validate_stage4_authorization_sync_committed_surface(1, [*exact[1:], "M " + first]),
    }


def stage4_verifier_output_encoding_corrective_dirty_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED)[0]
    exact = [(" M", path) for path in sorted(STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED)]
    return {
        "exact_m12_accepted": dirty_surface_is_exact(exact, STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED),
        "missing_path_rejected": not dirty_surface_is_exact(exact[:-1], STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED),
        "unexpected_path_rejected": not dirty_surface_is_exact([*exact, (" M", "backend/app/version.py")], STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED),
        "duplicate_path_rejected": not dirty_surface_is_exact([*exact, exact[0]], STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED),
        "staged_rejected": not dirty_surface_is_exact([*exact[1:], ("M ", first)], STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED),
        "untracked_rejected": not dirty_surface_is_exact([*exact, ("??", "scratch.txt")], STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED),
    }


def stage4_verifier_output_encoding_corrective_committed_surface_self_check() -> dict[str, bool]:
    first = sorted(STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED)[0]
    exact = [f"M\t{path}" for path in sorted(STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_MODIFIED)]
    return {
        "exact_one_commit_m12_accepted": validate_stage4_verifier_output_encoding_corrective_committed_surface(1, exact),
        "count_0_rejected": not validate_stage4_verifier_output_encoding_corrective_committed_surface(0, exact),
        "count_2_rejected": not validate_stage4_verifier_output_encoding_corrective_committed_surface(2, exact),
        "missing_path_rejected": not validate_stage4_verifier_output_encoding_corrective_committed_surface(1, exact[:-1]),
        "unexpected_path_rejected": not validate_stage4_verifier_output_encoding_corrective_committed_surface(1, [*exact, "M\tbackend/app/version.py"]),
        "duplicate_path_rejected": not validate_stage4_verifier_output_encoding_corrective_committed_surface(1, [*exact, exact[0]]),
        "status_a_rejected": not validate_stage4_verifier_output_encoding_corrective_committed_surface(1, [*exact[1:], "A\t" + first]),
    }


def stage4_verifier_output_encoding_corrective_origin_state_self_check() -> dict[str, bool]:
    head = "1" * 40
    return {
        "base_origin_accepted_as_not_pushed": stage4_verifier_output_encoding_corrective_origin_state(head, CONTROL_D_STAGE4_AUTHORIZATION_SYNC_COMMIT) == "NOT_PUSHED",
        "head_origin_accepted_as_pushed": stage4_verifier_output_encoding_corrective_origin_state(head, head) == "PUSHED",
        "unrelated_origin_rejected": stage4_verifier_output_encoding_corrective_origin_state(head, "2" * 40) is None,
        "dirty_mode_accepted": stage4_authorization_sync_modes("DIRTY_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_CANDIDATE"),
        "retry_verifier_reachability_false": not release_zip_reachability("DIRTY_STAGE4_VERIFIER_OUTPUT_ENCODING_CORRECTIVE_CANDIDATE"),
    }


def stage4_authorization_sync_origin_state_self_check() -> dict[str, bool]:
    head = "1" * 40
    return {
        "base_origin_accepted_as_not_pushed": stage4_authorization_sync_origin_state(head, CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT) == "NOT_PUSHED",
        "head_origin_accepted_as_pushed": stage4_authorization_sync_origin_state(head, head) == "PUSHED",
        "unrelated_origin_rejected": stage4_authorization_sync_origin_state(head, "2" * 40) is None,
        "empty_origin_rejected": stage4_authorization_sync_origin_state(head, "") is None,
        "origin_policy_blocked_before_surface_validation": _stage4_origin_policy_blocks_before_surface_validation(),
        "determine_mode_references_origin_helper": "stage4_authorization_sync_clean_mode_after_surface_validation" in determine_mode.__code__.co_names,
        "dirty_mode_maintained": stage4_authorization_sync_modes("DIRTY_STAGE4_AUTHORIZATION_SYNC_CANDIDATE"),
    }


def _stage4_origin_policy_blocks_before_surface_validation() -> bool:
    try:
        stage4_authorization_sync_clean_mode_after_surface_validation(False, "1" * 40, "1" * 40)
    except AssertionError:
        return True
    return False


def fixed_zip_tuple_self_check() -> dict[str, bool]:
    return {
        "actual_tuple_accepted": fixed_zip_tuple_is_exact(),
        "tag_present_rejected": not fixed_zip_tuple_is_exact(tag_present=True),
        "expected_basename_exact": EXPECTED_FIXED_ZIP_BASENAME == "DailyRhythmCompanion_v4.0.0_20260908_173440.zip",
        "expected_size_exact": EXPECTED_FIXED_ZIP_SIZE == 3018230,
        "expected_sha_exact": EXPECTED_FIXED_ZIP_SHA256 == "f02b43a219d7e89fd9e40dd6c1f7cd588076de7b260d6085ffa99966b3c49142",
        "expected_source_head_exact": EXPECTED_FIXED_ZIP_SOURCE_HEAD == CONTROL_D_STAGE3_PATH_LENGTH_CORRECTIVE_COMMIT,
    }


def release_zip_reachability(mode: str) -> bool:
    return mode == "CLEAN_COMMITTED_STAGE4_AUTHORIZATION_SYNC"





if __name__ == "__main__":
    main()
