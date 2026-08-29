#!/usr/bin/env python3
"""DRC v4.0.0 release preparation protocol static gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "7ff8e34037808f6c002b1644201e856c1e0187f2"
EXPECTED_MODIFIED = (
    "README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "roadmap.md",
    "scripts/README.md",
    "tasklist.md",
)
EXPECTED_ADDED = (
    "docs/v400_release_preparation_protocol.md",
    "scripts/check_v400_release_preparation_protocol.py",
)
EXPECTED_FILES = tuple(sorted((*EXPECTED_MODIFIED, *EXPECTED_ADDED)))
CANONICAL_DOCS = (
    *EXPECTED_MODIFIED,
    "docs/v400_release_preparation_protocol.md",
)
PROTECTED_PATHS = (
    "app",
    "backend",
    "tests",
    "release",
    "release_notes",
    ".gitignore",
    "pubspec.yaml",
    "pubspec.lock",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "requirements.txt",
    "requirements-dev.txt",
    "build_release.bat",
    "build_v200_final_fixed_release_zip_from_head.ps1",
    "build_v201_fixed_release_zip_from_head.ps1",
    "build_v210_fixed_release_zip_from_head.ps1",
    "build_v300_fixed_release_zip_from_head.ps1",
    "docs/v400_framework_v600_readiness_acceptance.md",
    "docs/v400_aggregate_readiness_reassessment.md",
    "docs/v400_provider_free_realtime_configured_local_backend_acceptance.md",
    "docs/v300_release_record.md",
    "docs/v300_rt9_release_readiness.md",
    "docs/v300_rt9_fixed_release_zip.md",
)
REQUIRED_ASSOCIATIONS = (
    ("Current checkpoint", "DRC v4.0.0 Release Preparation Protocol"),
    ("Current small commit", "DRC v4.0.0 Release Preparation Protocol"),
    ("Current implementation", "DRC v4.0.0 Release Preparation Protocol"),
    ("Current implementation state", "IMPLEMENTED / AWAITING_REVIEW"),
    ("protocol baseline", EXPECTED_BASELINE),
    ("implementation commit", "none"),
    ("current released version", "v3.0.0 RELEASED / ACCEPTED"),
    (
        "DRC-V4 Aggregate Readiness Reassessment",
        "COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
    ),
    ("reassessment commit", EXPECTED_BASELINE),
    ("DRC-V4 bounded coexistence readiness", "READY_FOR_RELEASE_PREPARATION"),
    ("DRC-V4 aggregate", "READY_FOR_RELEASE_PREPARATION"),
    ("DRC v4.0.0", "NOT_RELEASED"),
    (
        "Framework v6.0.0 framework-level readiness",
        "PARTIAL_READY / HISTORICAL_AND_STILL_TRUE",
    ),
    ("existing v3 real runtime", "PRESERVED / RELEASED / ACCEPTED"),
    ("existing v3 replacement", "NO"),
    ("/realtime/text replacement", "NO"),
    ("real unified FW runtime", "NOT_AVAILABLE / NOT_CLAIMED"),
    ("real unified FW runtime release blocker", "NO"),
    ("Control B", "FUTURE / NOT_AUTHORIZED"),
    ("Control C", "FUTURE / NOT_AUTHORIZED"),
    ("Control D", "FUTURE / NOT_AUTHORIZED"),
    ("Control E", "FUTURE / NOT_AUTHORIZED"),
    ("fixed ZIP builder invocation count", "0"),
    ("fixed ZIP", "NOT_BUILT"),
    ("annotated tag", "NOT_CREATED"),
    ("GitHub Release", "NOT_CREATED"),
    ("stage", "NOT_AUTHORIZED / NOT_RUN"),
    ("commit", "NOT_AUTHORIZED / NOT_RUN"),
    ("push", "NOT_AUTHORIZED / NOT_RUN"),
    ("package", "NOT_AUTHORIZED / NOT_RUN"),
    ("tag", "NOT_AUTHORIZED / NOT_RUN"),
    ("publication", "NOT_AUTHORIZED / NOT_RUN"),
)
PROTOCOL_REQUIRED_TEXT = (
    "Control A:",
    "Release inventory / preparation protocol",
    "Control B:",
    "Candidate metadata / release-record preparation",
    "Control C:",
    "Release Candidate verification / no-build preflight",
    "Control D:",
    "Fixed source ZIP / same-artifact acceptance",
    "Control E:",
    "Publication",
    "completion or acceptance of one control does not authorize the next control",
    "implementation approval != stage approval",
    "stage/commit approval != push approval",
    "commit/push approval != package approval",
    "package approval != tag approval",
    "tag approval != publication approval",
    "must not silently continue to be used",
    "artifact is treated as invalidated",
    "release source HEAD",
    "verification HEAD",
    "artifact SHA-256",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"(?im)^\s*DRC v4\.0\.0:\s*RELEASED"),
    re.compile(r"(?im)^\s*v4\.0\.0\s+RELEASED"),
    re.compile(r"(?im)^\s*real unified FW runtime:\s*AVAILABLE"),
    re.compile(r"(?im)^\s*existing v3 replacement:(?!(?:[^\S\r\n]*|[^\S\r\n]*\r?\n\s*)NO\b)"),
    re.compile(r"(?im)^\s*/realtime/text replacement:(?!(?:[^\S\r\n]*|[^\S\r\n]*\r?\n\s*)NO\b)"),
    re.compile(r"(?im)^\s*fixed ZIP:(?!(?:[^\S\r\n]*|[^\S\r\n]*\r?\n\s*)NOT_BUILT\b)"),
    re.compile(r"(?im)^\s*GitHub Release:(?!(?:[^\S\r\n]*|[^\S\r\n]*\r?\n\s*)NOT_CREATED\b)"),
    re.compile(r"(?im)^\s*annotated tag:(?!(?:[^\S\r\n]*|[^\S\r\n]*\r?\n\s*)NOT_CREATED\b)"),
)


class GateError(RuntimeError):
    pass


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and completed.returncode:
        raise GateError(completed.stderr.strip() or completed.stdout.strip())
    return completed


def git_out(*args: str) -> str:
    return git(*args).stdout


def git_success(*args: str) -> bool:
    return git(*args, check=False).returncode == 0


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GateError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def association_pattern(label: str, value: str) -> re.Pattern[str]:
    escaped_label = re.escape(label)
    escaped_value = re.escape(value)
    return re.compile(
        rf"(?im)^\s*(?:Status:\s*)?(?:current\s+)?{escaped_label}\s*:?\s*"
        rf"(?:\r?\n\s*){{0,2}}`?{escaped_value}`?\s*$"
    )


def require_association(relative: str, label: str, value: str) -> None:
    text = read(relative)
    if association_pattern(label, value).search(text):
        return
    if label == "current released version":
        emphasized = re.compile(
            r"(?im)^\s*current\ released\ version\s*:\s*"
            r"`?v3\.0\.0`?\s*\(?\*{0,2}RELEASED / ACCEPTED\*{0,2}\)?\s*$"
        )
        if emphasized.search(text):
            return
    if label == "Current released version":
        emphasized = re.compile(
            r"(?im)^\s*Current\ released\ version\s*:\s*"
            r"`?v3\.0\.0`?\s*\(?\*{0,2}RELEASED / ACCEPTED\*{0,2}\)?\s*$"
        )
        if emphasized.search(text):
            return
    raise GateError(f"missing semantic association in {relative}: {label} -> {value}")


def current_state_region(relative: str) -> str:
    text = read(relative)
    if relative == "README.md":
        return text.split("\nLast accepted release control:", 1)[0]
    if relative == "roadmap.md":
        return text.split("\nHistorical v2.1.0 terminal marker:", 1)[0]
    fence_start = text.find("```text")
    if fence_start == -1:
        return "\n".join(text.splitlines()[:140])
    fence_end = text.find("```", fence_start + len("```text"))
    if fence_end == -1:
        return "\n".join(text.splitlines()[:140])
    return text[:fence_end]


def status_entries() -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    for line in git_out("status", "--short", "--untracked-files=all").splitlines():
        entries.append((line[:2], line[3:].strip().replace("\\", "/")))
    return tuple(sorted(entries, key=lambda item: item[1]))


def require_branch_main() -> None:
    if git_out("branch", "--show-current").strip() != "main":
        raise GateError("unexpected branch")


def check_dirty_candidate_surface(entries: tuple[tuple[str, str], ...]) -> None:
    actual = tuple(path for _, path in entries)
    if actual != EXPECTED_FILES:
        raise GateError(f"exact dirty surface mismatch: {actual}")
    modified = tuple(sorted(path for status, path in entries if status == " M"))
    added = tuple(sorted(path for status, path in entries if status == "??"))
    deleted = tuple(path for status, path in entries if "D" in status)
    if modified != tuple(sorted(EXPECTED_MODIFIED)):
        raise GateError(f"modified mismatch: {modified}")
    if added != tuple(sorted(EXPECTED_ADDED)):
        raise GateError(f"added mismatch: {added}")
    if deleted:
        raise GateError(f"delete not authorized: {deleted}")


def determine_source_state() -> str:
    require_branch_main()
    entries = status_entries()
    if entries:
        if git_out("rev-parse", "HEAD").strip() != EXPECTED_BASELINE:
            raise GateError("unexpected dirty-candidate HEAD")
        if git_out("rev-parse", "origin/main").strip() != EXPECTED_BASELINE:
            raise GateError("unexpected dirty-candidate origin/main")
        check_dirty_candidate_surface(entries)
        return "DIRTY_CANDIDATE"

    if not git_success("cat-file", "-e", EXPECTED_BASELINE + "^{commit}"):
        raise GateError("expected baseline commit is missing")
    if not git_success("merge-base", "--is-ancestor", EXPECTED_BASELINE, "HEAD"):
        raise GateError("clean HEAD does not descend from expected baseline")
    return "CLEAN_COMMITTED_STATIC"


def check_protected() -> None:
    completed = git("diff", "--exit-code", "--", *PROTECTED_PATHS, check=False)
    if completed.returncode:
        raise GateError("protected surface diff is not empty")
    changed_checkers = [
        path
        for path in git_out("diff", "--name-only", "--", "scripts/check_*.py").splitlines()
        if path.replace("\\", "/") != "scripts/check_v400_release_preparation_protocol.py"
    ]
    if changed_checkers:
        raise GateError(f"existing checker changed: {tuple(changed_checkers)}")


def check_docs() -> None:
    for relative in CANONICAL_DOCS:
        for label, value in REQUIRED_ASSOCIATIONS:
            if label == "Current checkpoint" and relative != "docs/v400_release_preparation_protocol.md":
                continue
            require_association(relative, label, value)
        text = current_state_region(relative)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                raise GateError(f"forbidden claim in {relative}: {pattern.pattern}")
    protocol = read("docs/v400_release_preparation_protocol.md")
    for marker in PROTOCOL_REQUIRED_TEXT:
        if marker not in protocol:
            raise GateError(f"protocol missing marker: {marker}")


def check_no_release_artifacts() -> None:
    if git_out("tag", "--list", "DRC_v4.0.0").strip():
        raise GateError("DRC_v4.0.0 tag exists")
    release_root = ROOT / "release"
    if release_root.exists() and any(release_root.glob("*v4.0.0*.zip")):
        raise GateError("v4.0.0 release ZIP exists")


def main() -> int:
    try:
        source_state = determine_source_state()
        check_protected()
        check_docs()
        check_no_release_artifacts()
    except GateError as exc:
        print(f"DRC v4.0.0 Release Preparation Protocol gate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC v4.0.0 Release Preparation Protocol gate: PASS")
    print(f"source-state mode: {source_state}")
    print(f"baseline: {EXPECTED_BASELINE}")
    print("exact surface: 7 files / M5 A2 D0")
    print("current released version: v3.0.0 RELEASED / ACCEPTED")
    print("DRC-V4 aggregate: READY_FOR_RELEASE_PREPARATION")
    print("DRC v4.0.0: NOT_RELEASED")
    print("fixed ZIP builder invocation count: 0")
    print("fixed ZIP: NOT_BUILT")
    print("stage / commit / push / package / tag / publication: NOT_AUTHORIZED / NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
