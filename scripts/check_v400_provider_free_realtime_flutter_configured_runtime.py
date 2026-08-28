#!/usr/bin/env python3
"""DRC-V4-6 Control A configured Flutter runtime static gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "26a4222eec724a7517f2e812dfe4bd039c5b511d"
EXPECTED_FILES = (
    "README.md",
    "app/lib/services/configured_framework_v600_realtime_session_runtime.dart",
    "app/test/configured_framework_v600_realtime_session_runtime_test.dart",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_provider_free_realtime_flutter_configured_runtime.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v400_provider_free_realtime_flutter_configured_runtime.py",
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
    "app/lib/services/configured_framework_v600_realtime_session_runtime.dart",
    "app/test/configured_framework_v600_realtime_session_runtime_test.dart",
    "docs/v400_provider_free_realtime_flutter_configured_runtime.md",
    "scripts/check_v400_provider_free_realtime_flutter_configured_runtime.py",
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
    "docs/v400_provider_free_realtime_flutter_ui_readiness.md",
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
        raise GateError(f"exact nine-file surface mismatch: expected={expected}, actual={actual}")
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
    completed = git("diff", "--exit-code", "--", "backend", check=False)
    if completed.returncode:
        raise GateError("protected backend/ diff is not empty")
    completed = git("diff", "--exit-code", "--", *PROTECTED_FILES, check=False)
    if completed.returncode:
        raise GateError("protected V4-4/V4-5 boundary diff is not empty")


def require_markers(relative: str, markers: tuple[str, ...]) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            raise GateError(f"missing marker in {relative}: {marker}")


def check_runtime_source() -> None:
    runtime = read("app/lib/services/configured_framework_v600_realtime_session_runtime.dart")
    tests = read("app/test/configured_framework_v600_realtime_session_runtime_test.dart")
    for marker in (
        "ConfiguredFrameworkV600RealtimeSessionRuntime",
        "typedef FrameworkV600RealtimeSessionHttpClientFactory",
        "http.Client Function()",
        "http.Client.new",
        "factory ConfiguredFrameworkV600RealtimeSessionRuntime.fromEnvironment",
        "BackendApiClient apiClient = const BackendApiClient()",
        "DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION",
        "defaultValue: false",
        "baseUrl: apiClient.baseUrl",
        "FrameworkV600RealtimeSessionController Function()? buildControllerFactory()",
        "baseUrl.trim()",
        "_isValidBaseUrl(configuredBaseUrl)",
        "final httpClient = _httpClientFactory()",
        "FrameworkV600RealtimeSessionClient(",
        "baseUrl: configuredBaseUrl",
        "client: httpClient",
        "FrameworkV600RealtimeSessionController(client: sessionClient)",
        "uri.scheme != 'http' && uri.scheme != 'https'",
        "uri.host.isEmpty || uri.hasFragment || uri.userInfo.isNotEmpty",
    ):
        if marker not in runtime:
            raise GateError(f"missing runtime marker: {marker}")
    for forbidden in (
        ".open(",
        "createSession()",
        "runTurn(",
        "interrupt(",
        "diagnostics(",
        "closeSession(",
        "dart:io",
        "microphone",
        "Voice",
        "Tts",
        "VTube",
        "provider_sdk",
    ):
        if forbidden in runtime:
            raise GateError(f"forbidden runtime marker present: {forbidden}")
    for marker in (
        "disabled runtime returns null factory",
        "enabled valid http URL returns factory",
        "enabled valid https URL returns factory",
        "invalid base URLs return null",
        "runtime construction is lazy",
        "buildControllerFactory lookup is lazy",
        "factory invocation creates independent ownership",
        "newly created controller is idle",
        "controller dispose closes owned HTTP client without DELETE",
        "explicit open uses trimmed base URL and preserves path prefix",
        "/api/realtime/framework-v6/provider-free/sessions",
        "sendCalls, 0",
        "closeCalls, 1",
    ):
        if marker not in tests:
            raise GateError(f"missing focused test marker: {marker}")


def check_docs() -> None:
    require_markers(
        "docs/v400_provider_free_realtime_flutter_configured_runtime.md",
        (
            "DRC-V4-6 Control A IMPLEMENTED / AWAITING_REVIEW",
            EXPECTED_BASELINE,
            "implementation commit:\nnone",
            "commit:\nNOT_AUTHORIZED",
            "push:\nNOT_AUTHORIZED",
            "configured FW-v6 runtime/factory:\nIMPLEMENTED",
            "HomeScreen FW-v6 UI:\nNOT_IMPLEMENTED",
            "main.dart FW-v6 composition:\nNOT_IMPLEMENTED",
            "automatic startup network:\nNO",
            "automatic startup session open:\nNO",
            "provider execution:\nNO",
            "existing v3 runtime replacement:\nNO",
            "real unified FW runtime:\nNOT_AVAILABLE / NOT_CLAIMED",
            "DRC-V4 aggregate:\nPARTIAL_READY",
            "Backend HTTP capability: YES",
            "Control A automatic startup network: NO",
            "verification network: NO / fake transport only",
            "provider network: NO",
            "external provider execution: NO",
            "DRC-V4-6 Control B:\nPROPOSED / NOT_AUTHORIZED",
            "DRC-V4-6 Control C:\nPROPOSED / NOT_AUTHORIZED",
            "DRC-V4-6 aggregate:\nPARTIAL_READY / NOT_COMPLETED",
            "DRC-V4-5:\nCOMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
            "implementation commit:\n838ab047bb7a7e96f26f3c6ab436a1b9241c2c0e",
            "final acceptance-sync commit:\n26a4222eec724a7517f2e812dfe4bd039c5b511d",
        ),
    )
    for doc in CURRENT_DOCS:
        require_markers(
            doc,
            (
                "DRC-V4-6 Control A",
                "IMPLEMENTED / AWAITING_REVIEW",
                EXPECTED_BASELINE,
                "commit / push: NOT_AUTHORIZED",
                "configured FW-v6 runtime/factory",
                "IMPLEMENTED",
                "HomeScreen FW-v6 UI",
                "NOT_IMPLEMENTED",
                "main.dart FW-v6 composition",
                "NOT_IMPLEMENTED",
                "automatic startup network",
                "NO",
                "provider execution",
                "NO",
                "real unified FW runtime",
                "NOT_AVAILABLE / NOT_CLAIMED",
                "DRC-V4 aggregate: PARTIAL_READY",
                "DRC-V4-6 Control B",
                "PROPOSED / NOT_AUTHORIZED",
                "DRC-V4-6 Control C",
                "PROPOSED / NOT_AUTHORIZED",
                "DRC-V4-5",
                "COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED",
                "838ab047bb7a7e96f26f3c6ab436a1b9241c2c0e",
                "26a4222eec724a7517f2e812dfe4bd039c5b511d",
            ),
        )


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
            raise GateError(f"privacy marker matched in V4-6A candidate additions: {pattern.pattern}")


def main() -> int:
    try:
        check_baseline()
        check_surface()
        check_protected_diff()
        check_runtime_source()
        check_docs()
        check_privacy()
    except GateError as exc:
        print(f"DRC-V4-6 Control A gate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC-V4-6 Control A gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
