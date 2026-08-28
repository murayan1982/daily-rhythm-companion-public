#!/usr/bin/env python3
"""DRC-V4-5 provider-free FW v6 Flutter UI readiness static gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "cf82518cd0b96a752ad92151bb3d706a88b9147c"
EXPECTED_FILES = (
    "README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_provider_free_realtime_flutter_ui_readiness.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v400_provider_free_realtime_flutter_ui_readiness.py",
    "tasklist.md",
)
EXPECTED_MODIFIED = (
    "README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "roadmap.md",
    "scripts/README.md",
    "tasklist.md",
)
EXPECTED_UNTRACKED = (
    "docs/v400_provider_free_realtime_flutter_ui_readiness.md",
    "scripts/check_v400_provider_free_realtime_flutter_ui_readiness.py",
)
PROTECTED_FILES = (
    "app/lib/main.dart",
    "app/lib/screens/home_screen.dart",
    "app/lib/models/framework_v600_realtime_session.dart",
    "app/lib/services/framework_v600_realtime_session_client.dart",
    "app/lib/services/framework_v600_realtime_session_controller.dart",
    "app/test/framework_v600_realtime_session_model_test.dart",
    "app/test/framework_v600_realtime_session_client_test.dart",
    "app/test/framework_v600_realtime_session_controller_test.dart",
    "scripts/check_v400_provider_free_realtime_flutter_session_client.py",
)
CURRENT_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
)
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
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
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append((status, path.replace("\\", "/")))
    return tuple(sorted(entries, key=lambda item: item[1]))


def check_baseline() -> None:
    if git_out("branch", "--show-current").strip() != "main":
        raise GateError("unexpected branch")
    if git_out("rev-parse", "HEAD").strip() != EXPECTED_BASELINE:
        raise GateError("unexpected baseline HEAD")
    if git_out("rev-parse", "origin/main").strip() != EXPECTED_BASELINE:
        raise GateError("unexpected origin/main")


def check_surface() -> None:
    entries = status_entries()
    actual = tuple(path for _, path in entries)
    expected = tuple(sorted(EXPECTED_FILES))
    if actual != expected:
        raise GateError(f"exact seven-file surface mismatch: expected={expected}, actual={actual}")
    modified = tuple(sorted(path for status, path in entries if status == " M"))
    untracked = tuple(sorted(path for status, path in entries if status == "??"))
    deleted = tuple(path for status, path in entries if "D" in status)
    if modified != tuple(sorted(EXPECTED_MODIFIED)):
        raise GateError(f"modified-file mismatch: {modified}")
    if untracked != tuple(sorted(EXPECTED_UNTRACKED)):
        raise GateError(f"untracked-file mismatch: {untracked}")
    if deleted:
        raise GateError(f"deleted files are not authorized: {deleted}")


def check_protected_diff() -> None:
    for scope in ("app", "backend"):
        completed = git("diff", "--exit-code", "--", scope, check=False)
        if completed.returncode:
            raise GateError(f"protected {scope}/ diff is not empty")
    completed = git("diff", "--exit-code", "--", *PROTECTED_FILES, check=False)
    if completed.returncode:
        raise GateError("protected implementation/test/checker diff is not empty")


def check_source_inventory() -> None:
    main = read("app/lib/main.dart")
    home = read("app/lib/screens/home_screen.dart")
    for marker in (
        "DailyRhythmCompanionApp",
        "HomeScreen",
        "buildControllerFactory",
        "buildBindingFactory",
    ):
        if marker not in main:
            raise GateError(f"missing main.dart composition marker: {marker}")
    for marker in ("class HomeScreen", "HomeScreen({"):
        if marker not in home:
            raise GateError(f"missing HomeScreen marker: {marker}")
    if "Controller Function()?" not in home:
        raise GateError("missing HomeScreen controller factory seam")
    if "BindingFactory?" not in home:
        raise GateError("missing HomeScreen binding factory seam")


def require_markers(relative: str, markers: tuple[str, ...]) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            raise GateError(f"missing marker in {relative}: {marker}")


def check_docs() -> None:
    readiness_markers = (
        "DRC-V4-5 IMPLEMENTED / AWAITING_REVIEW",
        EXPECTED_BASELINE,
        "HomeScreen wiring:\nNOT_IMPLEMENTED",
        "main.dart wiring:\nNOT_IMPLEMENTED",
        "configured runtime wiring:\nNOT_IMPLEMENTED",
        "automatic startup network:\nNO",
        "automatic startup session open:\nNOT_AUTHORIZED",
        "provider execution:\nOUT_OF_SCOPE",
        "real unified FW runtime:\nNOT_AVAILABLE / NOT_CLAIMED",
        "DRC-V4 aggregate:\nPARTIAL_READY",
        "DRC-V4-6 Control A",
        "DRC-V4-6 Control B",
        "DRC-V4-6 Control C",
        "existing v3 realtime replacement:\nNOT_AUTHORIZED",
        "V4-4 Flutter model/client/controller:\nREADY / ACCEPTED",
        "V4-3 Backend provider-free HTTP API:\nREADY / ACCEPTED",
        "HomeScreen dependency-injection seam:\nREADY_FOR_EXACT_IMPLEMENTATION_REVIEW",
        "main.dart configured-runtime composition seam:\nREADY_FOR_EXACT_IMPLEMENTATION_REVIEW",
        "configured provider-free FW-v6 runtime:\nNOT_IMPLEMENTED",
        "HomeScreen provider-free FW-v6 session UI:\nNOT_IMPLEMENTED",
        "main.dart provider-free FW-v6 composition:\nNOT_IMPLEMENTED",
        "replacement of existing v3 realtime flow:\nNOT_AUTHORIZED",
    )
    require_markers("docs/v400_provider_free_realtime_flutter_ui_readiness.md", readiness_markers)
    for doc in CURRENT_DOCS:
        require_markers(
            doc,
            (
                "DRC-V4-5",
                "IMPLEMENTED / AWAITING_REVIEW",
                EXPECTED_BASELINE,
                "commit / push: NOT_AUTHORIZED",
                "DRC-V4-4: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
                "DRC-V4-4 implementation commit",
                "a05d62447e85be28d674201853d0667aef11e2ae",
                "DRC-V4-4 final acceptance-sync commit",
                "cf82518cd0b96a752ad92151bb3d706a88b9147c",
                "DRC-V4 aggregate: PARTIAL_READY",
                "HomeScreen dependency-injection seam",
                "main.dart configured-runtime composition seam",
                "configured provider-free FW-v6 runtime",
                "NOT_IMPLEMENTED",
                "NOT_AUTHORIZED",
            ),
        )


def check_no_shortcuts() -> None:
    forbidden_paths = (
        "app/lib/services/configured_framework_v600_realtime_runtime.dart",
        "app/lib/services/framework_v600_realtime_home_screen_binding.dart",
    )
    for relative in forbidden_paths:
        if (ROOT / relative).exists():
            raise GateError(f"unauthorized implementation shortcut exists: {relative}")


def check_privacy() -> None:
    diff = git_out("diff", "--", *EXPECTED_FILES)
    untracked_text = "\n".join(read(path) for path in EXPECTED_UNTRACKED)
    added_lines = "\n".join(
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    text = "\n".join((added_lines, untracked_text))
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            raise GateError(f"privacy marker matched in V4-5 candidate additions: {pattern.pattern}")


def main() -> int:
    try:
        check_baseline()
        check_surface()
        check_protected_diff()
        check_source_inventory()
        check_docs()
        check_no_shortcuts()
        check_privacy()
    except GateError as exc:
        print(f"DRC-V4-5 readiness gate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC-V4-5 readiness gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
