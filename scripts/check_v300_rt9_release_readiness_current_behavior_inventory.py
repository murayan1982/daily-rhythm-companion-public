#!/usr/bin/env python3
"""RT-9a release/security current-behavior inventory candidate gate."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "4c3b724a0c42e0d078c876c02b07a04d4c71e24d"
EXPECTED_BACKEND_VERSION = "2.1.0"
EXPECTED_FLUTTER_VERSION = "2.1.0+3"
HISTORICAL_V300_CHECK_COUNT = 62
INVENTORY = "docs/v300_rt9_release_readiness_current_behavior_inventory.md"
GATE = "scripts/check_v300_rt9_release_readiness_current_behavior_inventory.py"

SURFACE = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    INVENTORY,
    GATE,
}

TOP = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)

PROTECTED_EXACT = (
    ".gitignore",
    "build_release.bat",
    "scripts/check_release_package.py",
    "build_v200_final_fixed_release_zip_from_head.ps1",
    "build_v201_fixed_release_zip_from_head.ps1",
    "build_v210_fixed_release_zip_from_head.ps1",
    "scripts/check_v20x_patch_release.py",
    "scripts/check_v210_release_readiness.py",
    "scripts/check_v210_fixed_release_zip.py",
    "docs/v210_release_record.md",
    "release_notes/v2.0.0.md",
    "release_notes/v2.0.1.md",
    "release_notes/v2.1.0.md",
    "backend/app/version.py",
    "app/pubspec.yaml",
)

PROTECTED_PREFIXES = (
    "backend/app/",
    "backend/tests/",
    "app/",
    "vendor/",
    "release/",
    "operator_evidence/",
    "backend/local_data/",
)

ABSENT_V300_RELEASE_FILES = (
    "docs/v300_rt9_release_readiness.md",
    "docs/v300_release_record.md",
    "release_notes/v3.0.0.md",
    "scripts/check_v300_rt9_release_readiness.py",
    "build_v300_fixed_release_zip_from_head.ps1",
    "scripts/check_v300_fixed_release_zip.py",
)

SENSITIVE = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\(?:users|work|home)\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


def fail(message: str) -> None:
    raise SystemExit("v300_rt9a_gate_error: " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode:
        fail(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def git_ok(*args: str) -> bool:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def paths(value: str) -> set[str]:
    return {
        line.strip().replace("\\", "/")
        for line in value.splitlines()
        if line.strip()
    }


def changed() -> set[str]:
    result = paths(git("diff", "--name-only"))
    result |= paths(git("diff", "--cached", "--name-only"))
    result |= paths(git("ls-files", "--others", "--exclude-standard"))
    return result


def read(relative: str) -> str:
    path = ROOT / relative
    require(path.is_file(), "missing " + relative)
    return path.read_text(encoding="utf-8")


def markers(relative: str, *values: str) -> None:
    text = read(relative)
    for value in values:
        require(value in text, f"{relative} missing {value}")


def verify_history_and_surface() -> set[str]:
    require(git("branch", "--show-current") == "main", "branch")
    require(git("rev-parse", "HEAD") == BASELINE, "HEAD")
    require(git("rev-parse", "origin/main") == BASELINE, "origin/main")
    require(git_ok("cat-file", "-e", BASELINE + "^{commit}"), "baseline missing")
    surface = changed()
    require(surface == SURFACE, "surface " + repr(sorted(surface)))
    for relative in surface:
        require(
            not relative.startswith(PROTECTED_PREFIXES),
            "protected path changed " + relative,
        )
    return surface


def verify_docs() -> None:
    common = (
        "RT-8: COMPLETED / ACCEPTED",
        "RT-8e: COMPLETED / ACCEPTED / PUSHED",
        "RT-8e Stage 3: COMPLETED / ACCEPTED / PUSHED",
        "RT-8e Stage 3 acceptance-sync commit: 4c3b724a0c42e0d078c876c02b07a04d4c71e24d",
        "RT-9: CURRENT / NOT_COMPLETED",
        "RT-9a: IMPLEMENTED / AWAITING_REVIEW",
        "RT-9a baseline: 4c3b724a0c42e0d078c876c02b07a04d4c71e24d",
        "RT-9a surface: exact 7 documentation/static-gate files",
        "RT-9b: BLOCKED_PENDING_RT9A_ACCEPTANCE / NOT_AUTHORIZED",
        "RT-9c: BLOCKED_PENDING_RT9B_ACCEPTANCE / NOT_AUTHORIZED",
        "RT-9d: BLOCKED_PENDING_RT9C_ACCEPTANCE / NOT_AUTHORIZED",
        "RT-9e: BLOCKED_PENDING_RT9D_ACCEPTANCE / NOT_AUTHORIZED",
        "v3.0.0: NOT_RELEASED",
        "v3.0.0 fixed ZIP: NOT_BUILT",
        "DRC_v3.0.0 annotated tag: NOT_CREATED",
        "GitHub Release: NOT_CREATED",
    )
    for relative in TOP:
        markers(relative, *common)

    markers(
        "README.md",
        "Current small commit: RT-9a release/security inventory",
        "Current implementation: RT-9a release/security current-behavior inventory and exact split.",
        "Current implementation baseline: `4c3b724a0c42e0d078c876c02b07a04d4c71e24d`",
        "Current realtime phase: RT-9 (**CURRENT / NOT_COMPLETED**)",
    )
    markers(
        "roadmap.md",
        "Current small commit: RT-9a release/security inventory",
    )
    markers(
        "tasklist.md",
        "current parent phase: RT-9 CURRENT / NOT_COMPLETED",
        "current small commit: RT-9a release/security inventory",
        "current implementation step: RT-9a release/security current-behavior inventory and exact split",
    )
    markers(
        "scripts/README.md",
        "current small commit: RT-9a release/security inventory",
    )
    markers(
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "Current parent phase: RT-9 CURRENT / NOT_COMPLETED",
        "Current small commit: RT-9a release/security inventory",
        "Next implementation action: verify exact seven-file RT-9a inventory candidate; RT-9b through RT-9e, version changes, fixed ZIP, tag, and publication remain NOT_AUTHORIZED",
    )

    markers(
        INVENTORY,
        "# Daily Rhythm Companion v3.0.0 RT-9 release-readiness current behavior inventory",
        "## Current source and test baseline",
        "Backend APP_VERSION: 2.1.0",
        "Flutter package version: 2.1.0+3",
        "Backend full regression baseline: 417 passed, 1 existing warning",
        "Flutter full regression baseline: 500 passed",
        "v300 check scripts before RT-9a: 62",
        "v300 check scripts including RT-9a gate: 63",
        "## Current release tooling inventory",
        "## v300 gate classification boundary",
        "## Package and private-data boundary",
        "## Accepted exact RT-9 split",
        "RT-9a  release/security current-behavior inventory and exact split",
        "RT-9b  v3.0.0 candidate metadata and aggregate source/test/build readiness",
        "RT-9c  one-time fixed-ZIP builder/verifier implementation and no-build preflight",
        "RT-9d  fixed ZIP build-once, same-artifact verification, and tuple record",
        "RT-9e  explicit approval, annotated tag/GitHub Release, and post-publication verification",
        "Backend APP_VERSION: 3.0.0",
        "Flutter package version: 3.0.0+4",
        "## Required non-claims",
        "## RT-9a exact implementation surface",
        "## Protected and unchanged",
        "## RT-9a verification",
        "## RT-9a stop rule",
    )


def verify_current_source_facts() -> None:
    markers("backend/app/version.py", f'APP_VERSION = "{EXPECTED_BACKEND_VERSION}"')
    markers("app/pubspec.yaml", f"version: {EXPECTED_FLUTTER_VERSION}")

    checks = sorted((ROOT / "scripts").glob("check_v300_*.py"))
    historical = [path for path in checks if path.name != Path(GATE).name]
    require(len(historical) == HISTORICAL_V300_CHECK_COUNT, "historical gate count")
    require(len(checks) == HISTORICAL_V300_CHECK_COUNT + 1, "gate count including RT-9a")

    for relative in ABSENT_V300_RELEASE_FILES:
        require(not (ROOT / relative).exists(), "early v300 release file " + relative)

    gitignore = read(".gitignore")
    for value in (
        "vendor/ai-character-framework-*/",
        "operator_evidence/",
        "release/",
        "backend/local_data/",
    ):
        require(value in gitignore, ".gitignore marker " + value)

    builder = read("build_release.bat")
    for value in (
        '"%ROOT_DIR%release"',
        '"%ROOT_DIR%vendor"',
        '"%ROOT_DIR%backend\\local_data"',
        '"%ROOT_DIR%operator_evidence"',
        '"*.zip"',
    ):
        require(value in builder, "package denylist marker " + value)

    for relative in PROTECTED_EXACT:
        require(git_ok("diff", "--quiet", "HEAD", "--", relative), relative + " changed")


def verify_privacy(surface: set[str]) -> None:
    for relative in surface:
        diff = git("diff", "--unified=0", "HEAD", "--", relative)
        added = "\n".join(
            line[1:]
            for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        for pattern in SENSITIVE:
            require(pattern.search(added) is None, "private-looking value in " + relative)


def main() -> None:
    surface = verify_history_and_surface()
    verify_docs()
    verify_current_source_facts()
    verify_privacy(surface)

    print("v300_rt9_status: current-not-completed")
    print("v300_rt9a_status: implemented-awaiting-review")
    print("v300_rt9a_baseline:", BASELINE)
    print("v300_rt9a_exact_implementation_surface:", surface == SURFACE)
    print("v300_rt9a_implementation_change_file_count:", len(surface))
    print("v300_rt9a_historical_v300_gate_count:", HISTORICAL_V300_CHECK_COUNT)
    print("v300_rt9a_backend_version_metadata:", EXPECTED_BACKEND_VERSION)
    print("v300_rt9a_flutter_version_metadata:", EXPECTED_FLUTTER_VERSION)
    print("v300_rt9a_backend_runtime_changed: False")
    print("v300_rt9a_flutter_runtime_changed: False")
    print("v300_rt9a_existing_tests_changed: False")
    print("v300_rt9a_version_metadata_changed: False")
    print("v300_rt9a_historical_release_tooling_changed: False")
    print("v300_rt9a_historical_release_records_changed: False")
    print("v300_rt9a_private_manifest_read: False")
    print("v300_rt9a_private_manifest_modified: False")
    print("v300_rt9a_provider_network_configured_execution: False")
    print("v300_rt9a_release_zip_built: False")
    print("v300_rt9a_tag_created: False")
    print("v300_rt9a_github_release_created: False")
    print("v300_rt9a_commit_push_authorized: False")
    print("v300_rt9b_authorized: False")
    print("v300_release_ready: False")


if __name__ == "__main__":
    main()
