#!/usr/bin/env python3
"""RT-8e Stage 3 public-safe RT-8 acceptance synchronization gate."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "25c003405fe1a59f3ca7e8a8a6788698ad30bf6d"
RT8D = "84839efd6e381cb5a2c45022a7e8f7d9eafcb5df"
PC = "fa39065130a4a4689c2e54195f231a5e79c62a35"
ANDROID = "0e7fc6fc5922c293b8460fc816610d41c2a79e9a"
SCHEMA = "drc.v3.rt8-platform-acceptance.2"
CONTRACT = "docs/v300_rt8e_aggregate_cleanup_and_rt8_acceptance.md"
GATE = "scripts/check_v300_rt8e_aggregate_cleanup_and_acceptance.py"
RUNNER = "scripts/run_v300_rt8e_private_aggregate_cleanup.py"
TEST = "backend/tests/test_v300_rt8e_private_aggregate_cleanup.py"
VALIDATOR = "scripts/validate_v300_rt8_private_operator_manifest.py"

ACCEPTANCE = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    CONTRACT,
    GATE,
}

TOP = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)

UNCHANGED = (
    RUNNER,
    TEST,
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
    "backend/tests/",
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
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]"),
    re.compile(r"(?i)\b[a-z]:\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


def fail(message: str) -> None:
    raise SystemExit("v300_rt8e_stage3_gate_error: " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, text=True,
        encoding="utf-8", errors="surrogateescape",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        fail(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()


def git_ok(*args: str) -> bool:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def paths(value: str) -> set[str]:
    return {line.strip().replace("\\", "/") for line in value.splitlines() if line.strip()}


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
    for commit, label in ((RT8D, "RT-8d"), (PC, "PC"), (ANDROID, "Android")):
        require(git_ok("cat-file", "-e", commit + "^{commit}"), label + " source missing")
        require(git_ok("merge-base", "--is-ancestor", commit, BASELINE), label + " ancestry")
    surface = changed()
    require(surface == ACCEPTANCE, "acceptance surface " + repr(sorted(surface)))
    for relative in surface:
        require(not relative.startswith(PROTECTED_PREFIXES), "protected path changed " + relative)
    return surface


def verify_docs() -> None:
    common = (
        "RT-8: COMPLETED / ACCEPTED",
        "RT-8e: COMPLETED / ACCEPTED / PUSHED",
        "RT-8e Stage 1: COMPLETED / ACCEPTED / PUSHED",
        "RT-8e Stage 1 commit: 25c003405fe1a59f3ca7e8a8a6788698ad30bf6d",
        "RT-8e Stage 2: COMPLETED / PASS / ACCEPTED",
        "RT-8e Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW",
        "RT-8e Stage 3 surface: exact 7 documentation/static-gate files",
        "RT-9: READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
        "v3.0.0: NOT_RELEASED",
    )
    for relative in TOP:
        markers(relative, *common)

    markers("README.md",
        "Current small commit: RT-8e Stage 3 RT-8 acceptance sync",
        "Current implementation: RT-8e Stage 3 public-safe RT-8 acceptance synchronization.",
        "Current implementation baseline: `25c003405fe1a59f3ca7e8a8a6788698ad30bf6d`",
        "Current realtime phase: RT-8 (**COMPLETED / ACCEPTED**)",
    )
    markers("roadmap.md",
        "Current small commit: RT-8e Stage 3 RT-8 acceptance sync",
        "Status: RT-8 COMPLETED / ACCEPTED",
        "Current implementation boundary: exact 7 public documentation/static-gate files",
    )
    markers("tasklist.md",
        "current parent phase: RT-8 COMPLETED / ACCEPTED",
        "current small commit: RT-8e Stage 3 RT-8 acceptance sync",
        "current implementation step: RT-8e Stage 3 public-safe RT-8 acceptance synchronization",
    )
    markers("scripts/README.md", "current small commit: RT-8e Stage 3 RT-8 acceptance sync")
    markers("docs/DRC_v300_goal_checklist_small_commit.md",
        "Current parent phase: RT-8 COMPLETED / ACCEPTED",
        "Current small commit: RT-8e Stage 3 RT-8 acceptance sync",
        "Next implementation action: verify exact seven-file RT-8e Stage 3 acceptance-sync candidate; commit/push and RT-9 implementation remain NOT_AUTHORIZED",
    )

    markers(CONTRACT,
        "## Current Stage 3 acceptance-sync candidate state",
        "## Stage 1 accepted implementation",
        "implementation commit: 25c003405fe1a59f3ca7e8a8a6788698ad30bf6d",
        "focused Backend tests: 18 passed",
        "Backend full regression: 417 passed, 1 existing warning",
        "Flutter full regression: 500 passed",
        "## Stage 2 accepted checks and transition",
        "PASS-AGGREGATE-A",
        "PASS-AGGREGATE-H",
        "ACCEPT-RT8-AGGREGATE",
        "manifest stage: aggregate",
        "manifest status: accepted",
        "private manifest committed: false",
        "private manifest pushed: false",
        "## Stage 2 non-execution boundary",
        "## Exact Stage 3 surface",
        "## Stage 3 public privacy boundary",
        "private manifest read by Stage 3 gate: false",
        "## Protected and unchanged",
        "## Stage 3 verification",
        "## Stage 3 stop rule",
    )


def verify_unchanged_tooling() -> None:
    for relative in UNCHANGED:
        require(git_ok("diff", "--quiet", "HEAD", "--", relative), relative + " changed")
    require(read(TEST).count("def test_") == 18, "focused test count")
    runner = read(RUNNER)
    for value in (
        'RT8D_ACCEPTANCE_SYNC_BASELINE = "84839efd6e381cb5a2c45022a7e8f7d9eafcb5df"',
        'PC_ACCEPTED_SOURCE_HEAD = "fa39065130a4a4689c2e54195f231a5e79c62a35"',
        'ANDROID_ACCEPTED_SOURCE_HEAD = "0e7fc6fc5922c293b8460fc816610d41c2a79e9a"',
        "--record-aggregate",
        "PASS-AGGREGATE-",
        "ACCEPT-RT8-AGGREGATE",
        "private_manifest_content_printed: False",
        "cleanup_performed_by_runner: False",
        "rt9_implementation_authorized: False",
    ):
        require(value in runner, "runner marker " + value)
    validator = read(VALIDATOR)
    for value in (
        'SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"',
        "AGGREGATE_BOOLEAN_KEYS",
        "expected_manifest_for_stage",
        'choices=("pc-windows", "android", "aggregate")',
    ):
        require(value in validator, "validator marker " + value)


def verify_privacy(surface: set[str]) -> None:
    for relative in surface:
        diff = git("diff", "--unified=0", "HEAD", "--", relative)
        added = "\n".join(
            line[1:] for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        for pattern in SENSITIVE:
            require(pattern.search(added) is None, "private-looking value in " + relative)


def main() -> None:
    surface = verify_history_and_surface()
    verify_docs()
    verify_unchanged_tooling()
    verify_privacy(surface)
    print("v300_rt8_status: completed-accepted")
    print("v300_rt8e_status: completed-accepted-pushed")
    print("v300_rt8e_stage1_status: completed-accepted-pushed")
    print("v300_rt8e_stage2_status: completed-pass-accepted")
    print("v300_rt8e_stage3_status: implemented-awaiting-review")
    print("v300_rt8e_stage1_commit:", BASELINE)
    print("v300_rt8e_stage3_baseline:", BASELINE)
    print("v300_rt8e_schema_version:", SCHEMA)
    print("v300_rt8e_exact_acceptance_surface:", surface == ACCEPTANCE)
    print("v300_rt8e_acceptance_change_file_count:", len(surface))
    print("v300_rt8e_private_manifest_read: False")
    print("v300_rt8e_private_manifest_modified: False")
    print("v300_rt8e_private_cleanup_performed: False")
    print("v300_rt8e_configured_execution_performed: False")
    print("v300_rt8e_backend_runtime_changed: False")
    print("v300_rt8e_flutter_runtime_changed: False")
    print("v300_rt8e_existing_tests_changed: False")
    print("v300_rt8e_runner_changed: False")
    print("v300_rt8e_validator_changed: False")
    print("v300_rt8e_commit_push_authorized: False")
    print("v300_rt9_ready_for_exact_contract_review: True")
    print("v300_rt9_authorized: False")
    print("v300_release_ready: False")


if __name__ == "__main__":
    main()
