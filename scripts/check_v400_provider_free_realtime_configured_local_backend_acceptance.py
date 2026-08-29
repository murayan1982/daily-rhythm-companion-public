#!/usr/bin/env python3
"""DRC-V4-6 Aggregate Acceptance Protocol static candidate gate."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BASELINE = "13127ac93054840caeff5ec12698ae82f36bb514"
EXPECTED_MODIFIED = (
    "README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "roadmap.md",
    "scripts/README.md",
    "tasklist.md",
)
EXPECTED_ADDED = (
    "docs/v400_provider_free_realtime_configured_local_backend_acceptance.md",
    "scripts/check_v400_provider_free_realtime_configured_local_backend_acceptance.py",
)
EXPECTED_FILES = tuple(sorted((*EXPECTED_MODIFIED, *EXPECTED_ADDED)))
PROTECTED_PATHS = (
    "app",
    "backend",
    "docs/v400_provider_free_realtime_flutter_ui_readiness.md",
    "docs/v400_provider_free_realtime_flutter_configured_runtime.md",
    "docs/v400_provider_free_realtime_flutter_home_screen.md",
    "docs/v400_provider_free_realtime_flutter_main_composition.md",
    "scripts/check_v400_provider_free_realtime_flutter_configured_runtime.py",
    "scripts/check_v400_provider_free_realtime_flutter_home_screen.py",
    "scripts/check_v400_provider_free_realtime_flutter_main_composition.py",
    "pubspec.yaml",
    "pubspec.lock",
    "app/pubspec.yaml",
    "app/pubspec.lock",
)
CANONICAL_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v400_goal_checklist_small_commit.md",
    "docs/v400_provider_free_realtime_configured_local_backend_acceptance.md",
)
EXPECTED_CONTROL_C_IMPLEMENTATION_COMMIT = (
    "8c807507e930b546f562acad97f52a6ba652b35f"
)
SEMANTIC_ASSOCIATIONS = (
    ("DRC-V4-6 Control A", r".*\bCLOSED\b"),
    ("DRC-V4-6 Control B", r".*\bCLOSED\b"),
    ("DRC-V4-6 Control C", r".*\bCLOSED\b"),
    (
        "DRC-V4-6 Control C implementation commit",
        re.escape(EXPECTED_CONTROL_C_IMPLEMENTATION_COMMIT),
    ),
    (
        "DRC-V4-6 Control C final acceptance-sync commit",
        re.escape(EXPECTED_BASELINE),
    ),
    (
        "DRC-V4-6 Aggregate Acceptance Protocol",
        re.escape("IMPLEMENTED / AWAITING_REVIEW"),
    ),
    ("protocol baseline", re.escape(EXPECTED_BASELINE)),
    ("protocol implementation commit", r"none"),
    ("operator acceptance", re.escape("NOT_AUTHORIZED / NOT_RUN")),
    ("stage", re.escape("NOT_AUTHORIZED / NOT_RUN")),
    ("commit", re.escape("NOT_AUTHORIZED / NOT_RUN")),
    ("push", re.escape("NOT_AUTHORIZED / NOT_RUN")),
    ("DRC-V4-6 aggregate", re.escape("PARTIAL_READY / NOT_COMPLETED")),
    ("DRC-V4 aggregate", re.escape("PARTIAL_READY / NOT_COMPLETED")),
)
PROTOCOL_DOC_MARKERS = (
    "provider-free configured local Backend session acceptance",
    "This is not real provider acceptance.",
    "backend\\run_dev.bat",
    "ai-character-framework",
    "required version:\n6.0.0",
    "DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION=true",
    "DRC_BACKEND_API_BASE_URL=http://127.0.0.1:8000",
    "/realtime/framework-v6/provider-free/sessions/{sessionId}/turns",
    '{"input_text":"<exact operator input>"}',
    "automatic FW-v6 Backend request:\n0",
    "automatic FW-v6 session open:\n0",
    "provider network:\nNO",
    "provider execution:\nNO",
    "real unified FW runtime:\nNOT_AVAILABLE / NOT_CLAIMED",
)
FORBIDDEN_PATTERNS = (
    re.compile(r"DRC-V4-6 aggregate:\s*(?:COMPLETED|CLOSED)", re.IGNORECASE),
    re.compile(r"DRC-V4 aggregate:\s*(?:COMPLETED|CLOSED)", re.IGNORECASE),
    re.compile(r"v4\.0\.0\s+RELEASED", re.IGNORECASE),
    re.compile(r"real unified FW runtime:\s*AVAILABLE", re.IGNORECASE),
    re.compile(r"real STT enabled in aggregate protocol", re.IGNORECASE),
    re.compile(r"real LLM provider enabled", re.IGNORECASE),
    re.compile(r"real TTS enabled", re.IGNORECASE),
    re.compile(r"VTS/motion enabled", re.IGNORECASE),
    re.compile(r"existing v3 replacement completed", re.IGNORECASE),
    re.compile(r"/realtime/text replaced", re.IGNORECASE),
    re.compile(r"operator acceptance:\s*PASS", re.IGNORECASE),
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


def label_value_pattern(label: str, value_pattern: str) -> re.Pattern[str]:
    escaped_label = re.escape(label)
    return re.compile(
        rf"(?im)^\s*(?:Status:\s*)?{escaped_label}\s*:?\s*"
        rf"(?:\r?\n\s*){{0,2}}`?{value_pattern}`?\s*$"
    )


def require_association(relative: str, label: str, value_pattern: str) -> None:
    text = read(relative)
    if not label_value_pattern(label, value_pattern).search(text):
        raise GateError(f"missing semantic association in {relative}: {label} -> {value_pattern}")


def check_docs() -> None:
    for relative in CANONICAL_DOCS:
        for label, value_pattern in SEMANTIC_ASSOCIATIONS:
            require_association(relative, label, value_pattern)
    require_markers(
        "docs/v400_provider_free_realtime_configured_local_backend_acceptance.md",
        PROTOCOL_DOC_MARKERS,
    )


def check_forbidden_claims() -> None:
    for relative in CANONICAL_DOCS:
        text = read(relative)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                raise GateError(f"forbidden claim in {relative}: {pattern.pattern}")


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
        check_docs()
        check_forbidden_claims()
        check_privacy()
    except GateError as exc:
        print(f"DRC-V4-6 Aggregate Acceptance Protocol gate: FAIL: {exc}", file=sys.stderr)
        return 1
    print("DRC-V4-6 Aggregate Acceptance Protocol gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
