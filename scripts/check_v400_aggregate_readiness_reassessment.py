#!/usr/bin/env python3
"""DRC-V4 aggregate readiness reassessment static candidate gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "3f28c62aa193b404ccc9cc6111d756bbd7580b3f"
EXPECTED_MODIFIED = (
    "README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "roadmap.md",
    "scripts/README.md",
    "tasklist.md",
)
EXPECTED_ADDED = (
    "docs/v400_aggregate_readiness_reassessment.md",
    "scripts/check_v400_aggregate_readiness_reassessment.py",
)
EXPECTED_FILES = tuple(sorted((*EXPECTED_MODIFIED, *EXPECTED_ADDED)))
CANONICAL_DOCS = (
    *EXPECTED_MODIFIED,
    "docs/v400_aggregate_readiness_reassessment.md",
)
CANONICAL_FIVE = EXPECTED_MODIFIED
PROTECTED_PATHS = (
    "app",
    "backend",
    "tests",
    "release_notes",
    ".gitignore",
    "docs/v400_framework_v600_readiness_acceptance.md",
    "docs/v400_provider_free_realtime_session_adapter.md",
    "docs/v400_provider_free_realtime_backend_api.md",
    "docs/v400_provider_free_realtime_flutter_session_client.md",
    "docs/v400_provider_free_realtime_flutter_ui_readiness.md",
    "docs/v400_provider_free_realtime_flutter_configured_runtime.md",
    "docs/v400_provider_free_realtime_flutter_home_screen.md",
    "docs/v400_provider_free_realtime_flutter_main_composition.md",
    "docs/v400_provider_free_realtime_configured_local_backend_acceptance.md",
    "pubspec.yaml",
    "pubspec.lock",
    "app/pubspec.yaml",
    "app/pubspec.lock",
    "requirements.txt",
    "requirements-dev.txt",
)
REQUIRED_ASSOCIATIONS = (
    ("Current small commit", "DRC-V4 Aggregate Readiness Reassessment - post V4-6"),
    ("Current implementation", "DRC-V4 Aggregate Readiness Reassessment - post V4-6"),
    ("Current implementation state", "IMPLEMENTED / AWAITING_REVIEW"),
    ("implementation baseline", EXPECTED_BASELINE),
    ("implementation commit", "none"),
    ("stage", "NOT_AUTHORIZED / NOT_RUN"),
    ("commit", "NOT_AUTHORIZED / NOT_RUN"),
    ("push", "NOT_AUTHORIZED / NOT_RUN"),
    ("release", "NOT_AUTHORIZED / NOT_RUN"),
    (
        "DRC-V4-6 aggregate",
        "COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
    ),
    (
        "Framework v6.0.0 framework-level readiness",
        "PARTIAL_READY / HISTORICAL_AND_STILL_TRUE",
    ),
    ("DRC-V4 bounded coexistence readiness", "READY_FOR_RELEASE_PREPARATION"),
    ("DRC-V4 aggregate", "READY_FOR_RELEASE_PREPARATION"),
    ("DRC v4.0.0", "NOT_RELEASED"),
    ("existing v3 real runtime", "PRESERVED / RELEASED / ACCEPTED"),
    ("existing v3 replacement", "NO"),
    ("/realtime/text replacement", "NO"),
    ("real unified FW runtime", "NOT_AVAILABLE / NOT_CLAIMED"),
    (
        "real unified FW runtime required for DRC v4.0.0 release",
        "NO / NOT_A_RELEASE_BLOCKER",
    ),
    ("automatic FW-v6 startup network", "NO"),
    ("automatic FW-v6 session open", "NO"),
    ("provider execution", "NO"),
)
REASSESSMENT_ONLY_ASSOCIATIONS = (
    ("existing accepted v3 real runtime", "PRESERVED"),
    ("existing v3 realtime text flow", "PRESERVED"),
    ("existing v3 voice/STT/LLM/TTS/playback behavior", "PRESERVED"),
    (
        "existing FW v5.5.0 motion/VTube Studio integration",
        "PRESERVED where already accepted",
    ),
    ("FW-v6 provider-free path", "IMPLEMENTED / ACCEPTED"),
    ("default-off", "YES"),
    ("explicit user action required", "YES"),
    ("explicit local Backend HTTP", "YES"),
    ("microphone", "NO"),
    ("STT", "NO"),
    ("real LLM provider", "NO"),
    ("TTS", "NO"),
    ("audio playback", "NO"),
    ("VTube Studio", "NO"),
    ("motion", "NO"),
)
FORBIDDEN_PATTERNS = (
    re.compile(r"DRC v4\.0\.0:\s*RELEASED", re.IGNORECASE),
    re.compile(r"DRC-V4 aggregate:\s*(?:COMPLETED|CLOSED)", re.IGNORECASE),
    re.compile(r"^(?!.*\b(?:not|does not|Do NOT)\b).*DRC-V4-7", re.IGNORECASE | re.MULTILINE),
    re.compile(r"real unified FW runtime:\s*AVAILABLE", re.IGNORECASE),
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


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise GateError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def status_entries() -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    for line in git_out("status", "--short", "--untracked-files=normal").splitlines():
        entries.append((line[:2], line[3:].strip().replace("\\", "/")))
    return tuple(sorted(entries, key=lambda item: item[1]))


def association_pattern(label: str, value: str) -> re.Pattern[str]:
    escaped_label = re.escape(label)
    escaped_value = re.escape(value)
    return re.compile(
        rf"(?im)^\s*(?:Status:\s*)?(?:current\s+)?{escaped_label}\s*:?\s*"
        rf"(?:\r?\n\s*){{0,2}}`?{escaped_value}`?\s*$"
    )


def require_association(relative: str, label: str, value: str) -> None:
    if not association_pattern(label, value).search(read(relative)):
        raise GateError(f"missing semantic association in {relative}: {label} -> {value}")


def current_state_region(relative: str) -> str:
    text = read(relative)
    if relative == "README.md":
        marker = "\nDRC-V4-6 Control B final acceptance sync marker summary:"
        return text.split(marker, 1)[0]
    if relative == "roadmap.md":
        marker = "\nHistorical v2.1.0 terminal marker:"
        return text.split(marker, 1)[0]
    fence_start = text.find("```text")
    if fence_start == -1:
        return "\n".join(text.splitlines()[:120])
    fence_end = text.find("```", fence_start + len("```text"))
    if fence_end == -1:
        return "\n".join(text.splitlines()[:120])
    return text[:fence_end]


def check_current_state_drc_v4_aggregate(relative: str) -> None:
    region = current_state_region(relative)
    ready_pattern = association_pattern("DRC-V4 aggregate", "READY_FOR_RELEASE_PREPARATION")
    obsolete_pattern = association_pattern("DRC-V4 aggregate", "PARTIAL_READY / NOT_COMPLETED")
    ready_count = len(ready_pattern.findall(region))
    obsolete_count = len(obsolete_pattern.findall(region))
    if ready_count != 1:
        raise GateError(
            f"current-state DRC-V4 aggregate association count in {relative}: {ready_count}"
        )
    if obsolete_count:
        raise GateError(f"obsolete current-state DRC-V4 aggregate in {relative}")


def check_baseline() -> None:
    if git_out("branch", "--show-current").strip() != "main":
        raise GateError("unexpected branch")
    if git_out("rev-parse", "HEAD").strip() != EXPECTED_BASELINE:
        raise GateError("unexpected HEAD")
    if git_out("rev-parse", "origin/main").strip() != EXPECTED_BASELINE:
        raise GateError("unexpected origin/main")


def check_surface() -> None:
    entries = status_entries()
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


def check_protected() -> None:
    completed = git("diff", "--exit-code", "--", *PROTECTED_PATHS, check=False)
    if completed.returncode:
        raise GateError("protected surface diff is not empty")
    changed_checkers = [
        path
        for path in git_out("diff", "--name-only", "--", "scripts/check_*.py").splitlines()
        if path.replace("\\", "/") != "scripts/check_v400_aggregate_readiness_reassessment.py"
    ]
    if changed_checkers:
        raise GateError(f"existing checker changed: {tuple(changed_checkers)}")


def check_docs() -> None:
    for relative in CANONICAL_FIVE:
        check_current_state_drc_v4_aggregate(relative)
    for relative in CANONICAL_DOCS:
        for label, value in REQUIRED_ASSOCIATIONS:
            require_association(relative, label, value)
        text = read(relative)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                raise GateError(f"forbidden claim in {relative}: {pattern.pattern}")
    for label, value in REASSESSMENT_ONLY_ASSOCIATIONS:
        require_association("docs/v400_aggregate_readiness_reassessment.md", label, value)


def check_historical_v4_1() -> None:
    text = read("docs/v400_framework_v600_readiness_acceptance.md")
    if "Required aggregate decision: **PARTIAL_READY**" not in text:
        raise GateError("historical V4-1 aggregate decision missing")
    if "production real unified" not in text:
        raise GateError("historical V4-1 production unified non-claim missing")
    if "NOT_CLAIMED / NOT_AVAILABLE" not in text:
        raise GateError("historical V4-1 real unified runtime non-claim missing")


def main() -> int:
    try:
        check_baseline()
        check_surface()
        check_protected()
        check_docs()
        check_historical_v4_1()
    except GateError as exc:
        print(f"DRC-V4 Aggregate Readiness Reassessment candidate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC-V4 Aggregate Readiness Reassessment candidate: PASS")
    print(f"baseline: {EXPECTED_BASELINE}")
    print("exact surface: 7 files / M5 A2 D0")
    print("Framework v6.0.0 readiness: PARTIAL_READY / PRESERVED")
    print("DRC-V4 bounded coexistence readiness: READY_FOR_RELEASE_PREPARATION")
    print("DRC v4.0.0 release: NOT_RELEASED")
    print("v3 real runtime: PRESERVED")
    print("real unified FW runtime: NOT_AVAILABLE / NOT_CLAIMED")
    print("protected runtime: PASS")
    print("dependencies: UNCHANGED")
    print("stage / commit / push / release: NOT_AUTHORIZED / NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
