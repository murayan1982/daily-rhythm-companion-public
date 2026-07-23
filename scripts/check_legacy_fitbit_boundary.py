"""Check that legacy Fitbit wording does not leak into public-facing paths.

This script intentionally allows the legacy Fitbit implementation itself.
Daily Rhythm Companion keeps that code as a compatibility migration/reference
boundary after the v2.0.0 Google Health acceptance. Real Fitbit completion and
any later removal decision remain explicit v2.1.0 work.

Run from the repository root:

    python scripts/check_legacy_fitbit_boundary.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    phrase: str
    line: str


BLOCKED_PUBLIC_PHRASES = (
    "Fitbit connection status",
    "Fitbit connect stub button",
    "Fitbit connect button",
    "Fitbit setup",
    "Fitbit Stub Provider",
    "mock / fitbit_stub / fitbit providers",
)

# Historical notes, release logs, policy docs, and this checker are internal.
# They may quote old wording as examples, so they are not treated as public UI
# or user-facing setup text.
ALLOWED_INTERNAL_BASENAMES = {
    "DailyRhythmCompanion_handoff_v0_15_0.md",
    "release_final_check_v0_16_0_day4.md",
    "release_package_check_result_v0_16_0_day3.md",
    "public_release_checklist.md",
    "release_package_policy.md",
    "legacy_fitbit_cleanup_plan.md",
    "check_legacy_fitbit_boundary.py",
}

# Legacy implementation/reference areas are allowed to mention Fitbit directly.
# The check is meant to catch accidental public-facing wording, not delete the
# migration/reference implementation before the replacement provider is ready.
ALLOWED_LEGACY_PATHS = {
    "backend/app/api/fitbit.py",
    "backend/app/models/fitbit.py",
    "backend/app/services/sleep_providers/fitbit.py",
    "backend/app/services/sleep_providers/fitbit_stub.py",
    "docs/fitbit_integration_plan.md",
    "docs/v20x_fitbit_current_state_contract.md",
}

ALLOWED_LEGACY_PREFIXES = (
    "backend/app/services/fitbit_",
)

SEARCH_SUFFIXES = {".md", ".py", ".dart", ".env", ".example", ".txt"}
SKIPPED_DIR_PARTS = {
    ".git",
    ".dart_tool",
    ".venv",
    "build",
    "release",
    "vendor",
    "__pycache__",
}


def as_posix(path: Path) -> str:
    return path.as_posix()


def should_skip_path(path: Path) -> bool:
    path_text = as_posix(path)

    if any(part in SKIPPED_DIR_PARTS for part in path.parts):
        return True
    if path.name in ALLOWED_INTERNAL_BASENAMES:
        return True
    if path_text in ALLOWED_LEGACY_PATHS:
        return True
    if any(path_text.startswith(prefix) for prefix in ALLOWED_LEGACY_PREFIXES):
        return True
    if path.suffix not in SEARCH_SUFFIXES and not path.name.endswith(".env.example"):
        return True
    return False


def iter_project_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def is_allowed_context(phrase: str, line: str) -> bool:
    # The new, explicit legacy heading is allowed. The old unqualified heading
    # "### Fitbit Stub Provider" is still blocked.
    if phrase == "Fitbit Stub Provider" and "Legacy Fitbit Stub Provider" in line:
        return True
    return False


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")

    for line_number, line in enumerate(text.splitlines(), start=1):
        for phrase in BLOCKED_PUBLIC_PHRASES:
            if phrase in line and not is_allowed_context(phrase, line):
                findings.append(
                    Finding(
                        path=path,
                        line_number=line_number,
                        phrase=phrase,
                        line=line.strip(),
                    )
                )

    return findings


def main() -> int:
    root = Path.cwd()
    findings: list[Finding] = []

    for path in iter_project_files(root):
        relative_path = path.relative_to(root)
        if should_skip_path(relative_path):
            continue
        findings.extend(scan_file(path))

    if findings:
        print("[legacy-fitbit-boundary-check] NG")
        for finding in findings:
            relative_path = finding.path.relative_to(root)
            print(
                f"- {relative_path}:{finding.line_number}: "
                f"{finding.phrase} | {finding.line}"
            )
        return 1

    print("[legacy-fitbit-boundary-check] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
