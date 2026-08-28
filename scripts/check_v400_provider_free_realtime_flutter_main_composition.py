#!/usr/bin/env python3
"""DRC-V4-6 Control C main.dart FW-v6 composition static gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "3ef11c87d8e12393ab6dbe8f3308ffe9a1ca6f43"
EXPECTED_MODIFIED = (
    "README.md",
    "app/lib/main.dart",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "roadmap.md",
    "scripts/README.md",
    "tasklist.md",
)
EXPECTED_ADDED = (
    "app/test/framework_v600_realtime_session_main_composition_test.dart",
    "docs/v400_provider_free_realtime_flutter_main_composition.md",
    "scripts/check_v400_provider_free_realtime_flutter_main_composition.py",
)
EXPECTED_FILES = tuple(sorted((*EXPECTED_MODIFIED, *EXPECTED_ADDED)))
PROTECTED_PATHS = (
    "app/lib/screens/home_screen.dart",
    "app/lib/services/configured_framework_v600_realtime_session_runtime.dart",
    "app/lib/services/framework_v600_realtime_session_controller.dart",
    "app/lib/services/framework_v600_realtime_session_client.dart",
    "app/lib/models/framework_v600_realtime_session.dart",
    "app/test/configured_framework_v600_realtime_session_runtime_test.dart",
    "app/test/framework_v600_realtime_session_home_screen_widget_test.dart",
    "backend",
    "app/pubspec.yaml",
    "app/pubspec.lock",
)
MAIN_REQUIRED = (
    "import 'services/configured_framework_v600_realtime_session_runtime.dart';",
    "import 'services/framework_v600_realtime_session_controller.dart';",
    "final configuredFrameworkV600RealtimeSessionRuntime =",
    "ConfiguredFrameworkV600RealtimeSessionRuntime.fromEnvironment",
    "apiClient: apiClient",
    ".buildControllerFactory()",
    "this.frameworkV600RealtimeSessionControllerFactory",
    "final FrameworkV600RealtimeSessionController Function()?",
    "frameworkV600RealtimeSessionControllerFactory:",
)
MAIN_FORBIDDEN = (
    "DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION",
    "FrameworkV600RealtimeSessionClient(",
    "http.Client(",
    "controller.open(",
    "controller.runTurn(",
    "controller.interrupt(",
    "controller.diagnostics(",
    "controller.close(",
    "frameworkV600RealtimeSessionControllerFactory.call(",
)
TEST_REQUIRED = (
    "default app leaves FW-v6 session unconfigured",
    "configured factory composition is lazy",
    "pump build and settle do not activate FW-v6 factory",
    "explicit Open activates factory and create-session once",
    "dispose before Open does not create FW-v6 request or DELETE",
    "framework-v600-realtime-open-button",
    "/realtime/framework-v6/provider-free/sessions",
)
DOC_REQUIRED = (
    "DRC-V4-6 Control C IMPLEMENTED / AWAITING_REVIEW",
    EXPECTED_BASELINE,
    "implementation commit:\nnone",
    "commit:\nNOT_AUTHORIZED",
    "push:\nNOT_AUTHORIZED",
    "exact surface:\n9 files / M6 A3 D0",
    "Control A:\nconfigured runtime/factory",
    "Control B:\nHomeScreen explicit manual UI",
    "Control C:\nmain.dart default-off composition",
    "main.dart FW-v6 composition:\nIMPLEMENTED / AWAITING_REVIEW",
    "FW-v6 automatic startup network:\nNO",
    "FW-v6 automatic session open:\nNO",
    "explicit Open Session Backend HTTP:\nYES",
    "provider execution:\nNO",
    "real unified FW runtime:\nNOT_AVAILABLE / NOT_CLAIMED",
)
CURRENT_DOC_MARKERS = (
    "DRC-V4-6 Control B:",
    "COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
    "DRC-V4-6 Control B implementation commit",
    "3f9d38107f0306e023c127e68ce657cc4bd90b18",
    "DRC-V4-6 Control B final acceptance-sync commit",
    "3ef11c87d8e12393ab6dbe8f3308ffe9a1ca6f43",
    "DRC-V4-6 Control C:",
    "IMPLEMENTED / AWAITING_REVIEW",
    "DRC-V4-6 Control C implementation baseline",
    "DRC-V4-6 Control C implementation commit: none",
    "DRC-V4-6 Control C commit / push: NOT_AUTHORIZED",
    "DRC-V4-6 aggregate: PARTIAL_READY / NOT_COMPLETED",
)
PRIVACY_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{4,}"
    ),
    re.compile(r"(?i)\b[a-z]:\\(?:users|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(
        r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"
    ),
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


def require_markers(relative: str, markers: tuple[str, ...]) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            raise GateError(f"missing marker in {relative}: {marker}")


def check_main() -> None:
    text = read("app/lib/main.dart")
    for marker in MAIN_REQUIRED:
        if marker not in text:
            raise GateError(f"missing main.dart marker: {marker}")
    for marker in MAIN_FORBIDDEN:
        if marker in text:
            raise GateError(f"forbidden main.dart marker: {marker}")


def check_docs() -> None:
    require_markers(
        "docs/v400_provider_free_realtime_flutter_main_composition.md",
        DOC_REQUIRED,
    )
    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v400_goal_checklist_small_commit.md",
    ):
        require_markers(relative, CURRENT_DOC_MARKERS)


def check_tests() -> None:
    require_markers(
        "app/test/framework_v600_realtime_session_main_composition_test.dart",
        TEST_REQUIRED,
    )


def check_privacy() -> None:
    diff_text = git_out("diff", "--", *EXPECTED_MODIFIED)
    added_text = "\n".join(read(path) for path in EXPECTED_ADDED)
    candidate = "\n".join(
        line[1:]
        for line in diff_text.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    candidate = f"{candidate}\n{added_text}"
    for pattern in PRIVACY_PATTERNS:
        if pattern.search(candidate):
            raise GateError(f"privacy pattern matched: {pattern.pattern}")


def main() -> int:
    try:
        check_baseline()
        check_surface()
        check_protected()
        check_main()
        check_tests()
        check_docs()
        check_privacy()
    except GateError as exc:
        print(f"DRC-V4-6 Control C gate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC-V4-6 Control C gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
