#!/usr/bin/env python3
"""DRC-V4-6 Control B HomeScreen manual FW-v6 UI static gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "9bba7db5ed20abf6a0ffa1444fa37b340f3189cd"
EXPECTED_MODIFIED = (
    "README.md",
    "app/lib/screens/home_screen.dart",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "roadmap.md",
    "scripts/README.md",
    "tasklist.md",
)
EXPECTED_ADDED = (
    "app/test/framework_v600_realtime_session_home_screen_widget_test.dart",
    "docs/v400_provider_free_realtime_flutter_home_screen.md",
    "scripts/check_v400_provider_free_realtime_flutter_home_screen.py",
)
EXPECTED_FILES = tuple(sorted((*EXPECTED_MODIFIED, *EXPECTED_ADDED)))
PROTECTED_PATHS = (
    "app/lib/main.dart",
    "backend",
    "app/lib/services/configured_framework_v600_realtime_session_runtime.dart",
    "app/lib/services/framework_v600_realtime_session_controller.dart",
    "app/lib/services/framework_v600_realtime_session_client.dart",
    "app/lib/models/framework_v600_realtime_session.dart",
    "app/test/configured_framework_v600_realtime_session_runtime_test.dart",
    "app/test/framework_v600_realtime_session_controller_test.dart",
    "app/test/framework_v600_realtime_session_client_test.dart",
    "docs/v400_provider_free_realtime_flutter_configured_runtime.md",
    "docs/v400_provider_free_realtime_flutter_ui_readiness.md",
    "scripts/check_v400_provider_free_realtime_flutter_configured_runtime.py",
)
HOME_REQUIRED = (
    "frameworkV600RealtimeSessionControllerFactory",
    "FrameworkV600RealtimeSessionController",
    "framework-v600-realtime-configuration",
    "framework-v600-realtime-phase",
    "framework-v600-realtime-session-id",
    "framework-v600-realtime-input",
    "framework-v600-realtime-open-button",
    "framework-v600-realtime-send-button",
    "framework-v600-realtime-interrupt-button",
    "framework-v600-realtime-diagnostics-button",
    "framework-v600-realtime-close-button",
    "framework-v600-realtime-turn-outcome",
    "framework-v600-realtime-turn-safe-message",
    "framework-v600-realtime-interrupt-outcome",
    "framework-v600-realtime-diagnostics-state",
    "framework-v600-realtime-diagnostics-phase",
    "framework-v600-realtime-problem-code",
    "framework-v600-realtime-problem-message",
)
HOME_FORBIDDEN = (
    "ConfiguredFrameworkV600RealtimeSessionRuntime",
    "fromEnvironment(",
    "bool.fromEnvironment",
    "DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION",
)
NEW_INTEGRATION_FORBIDDEN = (
    "provider_sdk",
    "OpenAI(",
    "microphone_permission",
    "SpeechToText",
    "TextToSpeech",
    "AudioPlayer(",
    "VTubeStudio",
    "MotionSession",
)
WIDGET_TEST_REQUIRED = (
    "unconfigured HomeScreen",
    "configured HomeScreen pump only",
    "explicit Open tap invokes factory exactly once",
    "explicit Open sends session create POST exactly once",
    "Send disabled before ready",
    "blank input cannot send",
    "ready explicit Send posts a turn exactly once",
    "explicit Interrupt posts once and only after tap",
    "explicit Diagnostics gets once and only after tap",
    "explicit Close deletes once with no hidden extra DELETE",
    "dispose before Open calls no factory",
    "dispose after Open without explicit Close sends no hidden DELETE",
    "after explicit Close next explicit Open creates fresh controller",
    "safe UI projection excludes raw exception JSON and private payload",
    "/realtime/framework-v6/provider-free/sessions",
    "/turns",
    "/interrupt",
    "/diagnostics",
    "DELETE",
)
DOC_REQUIRED = (
    "DRC-V4-6 Control B IMPLEMENTED / AWAITING_REVIEW",
    EXPECTED_BASELINE,
    "implementation commit:\nnone",
    "commit:\nNOT_AUTHORIZED",
    "push:\nNOT_AUTHORIZED",
    "exact surface 9 files",
    "M6 / A3 / D0",
    "Control A:\nCLOSED",
    "Control B:\nIMPLEMENTED / AWAITING_REVIEW",
    "Control C:\nPROPOSED / NOT_AUTHORIZED",
    "main.dart changes:\n0",
    "Backend changes:\n0",
    "automatic startup network:\nNO",
    "automatic session open:\nNO",
    "explicit user action Backend HTTP:\nYES",
    "provider network:\nNO",
    "external provider execution:\nNO",
    "existing v3 replacement:\nNO",
    "/realtime/text replacement:\nNO",
    "real unified FW runtime:\nNOT_AVAILABLE / NOT_CLAIMED",
)
README_FORBIDDEN_STALE = (
    "DRC-V4-6 Control A final acceptance sync: IMPLEMENTED / AWAITING_REVIEW",
    "DRC-V4-6 Control A final acceptance-sync commit: none",
    "DRC-V4-6 Control A acceptance-sync commit / push: NOT_AUTHORIZED",
)
README_CONTROL_A_CLOSED_REQUIRED = (
    "DRC-V4-6 Control A: CLOSED",
    EXPECTED_BASELINE,
)
PRIVACY_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{4,}"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"(?i)raw\s+audio"),
    re.compile(r"(?i)transcript\s+dump"),
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
        path = line[3:].strip().replace("\\", "/")
        entries.append((status, path))
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


def added_lines(relative: str) -> str:
    completed = git("diff", "--", relative)
    return "\n".join(
        line[1:]
        for line in completed.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def check_home_screen() -> None:
    require_markers("app/lib/screens/home_screen.dart", HOME_REQUIRED)
    text = read("app/lib/screens/home_screen.dart")
    for marker in HOME_FORBIDDEN:
        if marker in text:
            raise GateError(f"forbidden HomeScreen marker: {marker}")
    home_added = added_lines("app/lib/screens/home_screen.dart")
    for marker in NEW_INTEGRATION_FORBIDDEN:
        if marker in home_added:
            raise GateError(f"forbidden new integration marker: {marker}")


def check_widget_test() -> None:
    require_markers(
        "app/test/framework_v600_realtime_session_home_screen_widget_test.dart",
        WIDGET_TEST_REQUIRED,
    )


def check_docs() -> None:
    require_markers("docs/v400_provider_free_realtime_flutter_home_screen.md", DOC_REQUIRED)
    readme = read("README.md")
    for marker in README_FORBIDDEN_STALE:
        if marker in readme:
            raise GateError(f"stale Control A README marker present: {marker}")
    for marker in README_CONTROL_A_CLOSED_REQUIRED:
        if marker not in readme:
            raise GateError(f"missing Control A closed README marker: {marker}")
    current_doc_markers = (
        "DRC-V4-6 Control B",
        "IMPLEMENTED / AWAITING_REVIEW",
        EXPECTED_BASELINE,
        "Control C",
        "PROPOSED / NOT_AUTHORIZED",
        "PARTIAL_READY / NOT_COMPLETED",
        "commit / push: NOT_AUTHORIZED",
    )
    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v400_goal_checklist_small_commit.md",
    ):
        require_markers(relative, current_doc_markers)


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
        check_home_screen()
        check_widget_test()
        check_docs()
        check_privacy()
    except GateError as exc:
        print(f"DRC-V4-6 Control B gate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC-V4-6 Control B gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
