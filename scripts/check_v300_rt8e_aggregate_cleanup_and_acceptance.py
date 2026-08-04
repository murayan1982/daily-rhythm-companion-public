#!/usr/bin/env python3
"""RT-8e Stage 1 aggregate-cleanup tooling candidate gate."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "84839efd6e381cb5a2c45022a7e8f7d9eafcb5df"
PC = "fa39065130a4a4689c2e54195f231a5e79c62a35"
ANDROID = "0e7fc6fc5922c293b8460fc816610d41c2a79e9a"
SCHEMA = "drc.v3.rt8-platform-acceptance.2"
CONTRACT = "docs/v300_rt8e_aggregate_cleanup_and_rt8_acceptance.md"
GATE = "scripts/check_v300_rt8e_aggregate_cleanup_and_acceptance.py"
RUNNER = "scripts/run_v300_rt8e_private_aggregate_cleanup.py"
TEST = "backend/tests/test_v300_rt8e_private_aggregate_cleanup.py"
VALIDATOR = "scripts/validate_v300_rt8_private_operator_manifest.py"

IMPLEMENTATION = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    CONTRACT,
    GATE,
    RUNNER,
    TEST,
}

TOP = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)

UNCHANGED = (
    VALIDATOR,
    "scripts/run_v300_rt8c_private_pc_windows_operator.py",
    "scripts/run_v300_rt8d_private_android_operator.py",
    "backend/tests/test_v300_rt8_private_operator_manifest.py",
    "backend/tests/test_v300_rt8c_private_pc_windows_operator.py",
    "backend/tests/test_v300_rt8d_private_android_operator.py",
    "docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json",
    ".gitignore",
)

PROTECTED_PREFIXES = (
    "backend/app/",
    "app/",
    "vendor/",
    "release/",
    "release_notes/",
    "backend/env_profiles/",
    "operator_evidence/",
)

SENSITIVE = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"
    ),
    re.compile(r"(?i)\b[a-z]:\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(
        r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"
    ),
)


def fail(message: str) -> None:
    raise SystemExit("v300_rt8e_stage1_gate_error: " + message)


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
    return (
        subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


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
    require(git_ok("cat-file", "-e", PC + "^{commit}"), "PC source missing")
    require(git_ok("cat-file", "-e", ANDROID + "^{commit}"), "Android source missing")
    require(git_ok("merge-base", "--is-ancestor", PC, BASELINE), "PC ancestry")
    require(
        git_ok("merge-base", "--is-ancestor", ANDROID, BASELINE),
        "Android ancestry",
    )
    surface = changed()
    require(surface == IMPLEMENTATION, "implementation surface " + repr(sorted(surface)))
    for relative in surface:
        require(
            not relative.startswith(PROTECTED_PREFIXES),
            "protected path changed " + relative,
        )
    return surface


def verify_docs() -> None:
    common = (
        "RT-8d: COMPLETED / ACCEPTED / PUSHED",
        "RT-8d Stage 3: COMPLETED / ACCEPTED / PUSHED",
        "RT-8e: CURRENT / NOT_COMPLETED",
        "RT-8e Stage 1: IMPLEMENTED / AWAITING_REVIEW",
        "RT-8e Stage 1 baseline: 84839efd6e381cb5a2c45022a7e8f7d9eafcb5df",
        "RT-8e Stage 1 surface: exact 9 files",
        "RT-8e Stage 2: BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED",
        "RT-8e Stage 3: BLOCKED_PENDING_AGGREGATE_ACCEPTANCE / NOT_AUTHORIZED",
        "RT-9: BLOCKED_PENDING_RT8 / NOT_AUTHORIZED",
    )
    for relative in TOP:
        markers(relative, *common)

    markers(
        "README.md",
        "Current small commit: RT-8e Stage 1 aggregate cleanup tooling",
        "Current implementation: RT-8e Stage 1 credential-free aggregate-transition tooling.",
        "Current implementation baseline: `84839efd6e381cb5a2c45022a7e8f7d9eafcb5df`",
    )
    markers(
        "roadmap.md",
        "Current small commit: RT-8e Stage 1 aggregate cleanup tooling",
        "Current implementation boundary: exact 9 documentation/static-gate/operator-test files",
    )
    markers(
        "tasklist.md",
        "current small commit: RT-8e Stage 1 aggregate cleanup tooling",
        "current implementation step: RT-8e Stage 1 credential-free aggregate-transition tooling",
    )
    markers(
        "scripts/README.md",
        "current small commit: RT-8e Stage 1 aggregate cleanup tooling",
        "current implementation state: IMPLEMENTED / AWAITING_REVIEW",
    )
    markers(
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "Current small commit: RT-8e Stage 1 aggregate cleanup tooling",
        "Current implementation step: RT-8e Stage 1 credential-free aggregate-transition tooling",
        "Next implementation action: verify exact nine-file RT-8e Stage 1 candidate; private aggregate transition, Stage 3, commit, and push remain NOT_AUTHORIZED",
    )

    markers(
        CONTRACT,
        "## Current Stage 1 candidate state",
        "## Accepted exact split",
        "## Stage 1 exact surface",
        "## Stage 1 runner modes",
        "--check-inert",
        "--preflight",
        "--check-android-transition",
        "--record-aggregate",
        "PASS-AGGREGATE-A",
        "PASS-AGGREGATE-H",
        "ACCEPT-RT8-AGGREGATE",
        "## Aggregate manifest result",
        "rt9_implementation_authorized: false",
        "## Exact focused-test contract",
        "18. atomic failure preserves the original and leaks no private data",
        "## Stage 2 bounded sequence",
        "## Stage 2 prohibited execution",
        "## Stage 3 future public-safe surface",
        "## Protected and unchanged",
        "## Stage 1 stop rule",
    )


def verify_tooling() -> None:
    runner = read(RUNNER)
    for value in (
        'RT8D_ACCEPTANCE_SYNC_BASELINE = "84839efd6e381cb5a2c45022a7e8f7d9eafcb5df"',
        'PC_ACCEPTED_SOURCE_HEAD = "fa39065130a4a4689c2e54195f231a5e79c62a35"',
        'ANDROID_ACCEPTED_SOURCE_HEAD = "0e7fc6fc5922c293b8460fc816610d41c2a79e9a"',
        "--check-inert",
        "--preflight",
        "--check-android-transition",
        "--record-aggregate",
        "PASS-AGGREGATE-",
        "ACCEPT-RT8-AGGREGATE",
        'expected_manifest_for_stage(\n        "aggregate"',
        "os.replace",
        "target_changed_during_transition",
        "private_manifest_content_printed: False",
        "cleanup_performed_by_runner: False",
        "rt9_implementation_authorized: False",
    ):
        require(value in runner, "runner marker " + value)

    lowered = runner.lower()
    for forbidden in (
        "import requests",
        "import httpx",
        "import socket",
        "import adb",
        "import pyvts",
        "import websockets",
        "popen(",
        "start-process",
    ):
        require(forbidden not in lowered, "runner forbidden " + forbidden)

    require(read(TEST).count("def test_") == 18, "focused test count")
    require(git_ok("diff", "--quiet", "HEAD", "--", VALIDATOR), "validator changed")
    for relative in UNCHANGED[1:]:
        require(git_ok("diff", "--quiet", "HEAD", "--", relative), relative + " changed")

    validator = read(VALIDATOR)
    for value in (
        'SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"',
        "AGGREGATE_BOOLEAN_KEYS",
        "expected_manifest_for_stage",
        'choices=("pc-windows", "android", "aggregate")',
    ):
        require(value in validator, "validator marker " + value)


def verify_inert_runner() -> None:
    completed = subprocess.run(
        [sys.executable, RUNNER, "--check-inert"],
        cwd=ROOT,
        check=False,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(completed.returncode == 0, "inert runner return code")
    require(completed.stderr == "", "inert runner stderr")
    for value in (
        "operator_mode: inert-check",
        "git_inspected: False",
        "private_manifest_read: False",
        "private_manifest_modified: False",
        "private_configuration_read: False",
        "backend_flutter_process_accessed: False",
        "microphone_stt_tts_playback_attempted: False",
        "provider_network_vts_attempted: False",
        "private_cleanup_performed: False",
    ):
        require(value in completed.stdout, "inert marker " + value)


def verify_privacy(surface: set[str]) -> None:
    for relative in surface:
        if not (ROOT / relative).is_file():
            continue
        diff = git("diff", "--unified=0", "HEAD", "--", relative)
        if relative in paths(git("ls-files", "--others", "--exclude-standard")):
            added = read(relative)
        else:
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
    verify_tooling()
    verify_inert_runner()
    verify_privacy(surface)
    print("v300_rt8e_status: current-not-completed")
    print("v300_rt8e_stage1_status: implemented-awaiting-review")
    print("v300_rt8e_stage2_status: blocked-pending-stage1-acceptance-not-authorized")
    print("v300_rt8e_stage3_status: blocked-pending-aggregate-acceptance-not-authorized")
    print("v300_rt8e_implementation_baseline:", BASELINE)
    print("v300_rt8e_schema_version:", SCHEMA)
    print("v300_rt8e_exact_implementation_surface:", surface == IMPLEMENTATION)
    print("v300_rt8e_implementation_change_file_count:", len(surface))
    print("v300_rt8e_focused_test_count: 18")
    print("v300_rt8e_private_manifest_read: False")
    print("v300_rt8e_private_manifest_modified: False")
    print("v300_rt8e_private_cleanup_performed: False")
    print("v300_rt8e_configured_execution_performed: False")
    print("v300_rt8e_backend_runtime_changed: False")
    print("v300_rt8e_flutter_runtime_changed: False")
    print("v300_rt8e_existing_tests_changed: False")
    print("v300_rt8e_validator_changed: False")
    print("v300_rt8e_commit_push_authorized: False")
    print("v300_rt9_authorized: False")
    print("v300_release_ready: False")


if __name__ == "__main__":
    main()
