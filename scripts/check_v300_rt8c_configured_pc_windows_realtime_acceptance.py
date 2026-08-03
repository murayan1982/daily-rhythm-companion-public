#!/usr/bin/env python3
"""Historical RT-8c implementation and Stage 3 acceptance-sync gate.

The gate is credential-free and network-free. It verifies the accepted exact
nine-file Stage 1 implementation history, the current exact seven-file public
acceptance synchronization, unchanged operator tooling/tests, and the fixed
ignored manifest state without reading manifest content. It starts no runtime
and performs no configured execution.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_BASELINE = "4815403d4c94b05551df03678e9c2c4e1dfe754e"
IMPLEMENTATION_COMMIT = "fa39065130a4a4689c2e54195f231a5e79c62a35"
IMPLEMENTATION_MESSAGE = "test/docs: add RT-8c PC Windows operator tooling"
SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"

IMPLEMENTATION_EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md",
    "scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py",
    "scripts/run_v300_rt8c_private_pc_windows_operator.py",
    "backend/tests/test_v300_rt8c_private_pc_windows_operator.py",
}

ACCEPTANCE_SYNC_EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md",
    "scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py",
}

TOP_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)

RUNNER = "scripts/run_v300_rt8c_private_pc_windows_operator.py"
FOCUSED_TEST = "backend/tests/test_v300_rt8c_private_pc_windows_operator.py"
MANIFEST_RELATIVE = "operator_evidence/v300_rt8_pc_android_realtime_acceptance.json"
MANIFEST = ROOT / MANIFEST_RELATIVE

SENSITIVE_PATTERNS = (
    re.compile(r"(?i)sk-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)xai-[a-z0-9_-]{12,}"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|refresh[_-]?token|"
        r"client[_-]?secret)\s*[:=]\s*[^\s`]+"
    ),
    re.compile(r"(?i)\b[a-z]:\\"),
    re.compile(r"/(?:home|users)/[^/\s]+/"),
    re.compile(r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
)


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt8c_stage3_gate_error: {message}")


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
    if completed.returncode != 0:
        fail(completed.stderr.strip() or f"git command failed: {' '.join(args)}")
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


def normalized_paths(value: str) -> set[str]:
    return {
        line.strip().replace("\\", "/")
        for line in value.splitlines()
        if line.strip()
    }


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for args in (("diff", "--name-only"), ("diff", "--cached", "--name-only")):
        paths.update(normalized_paths(git(*args)))
    paths.update(
        normalized_paths(git("ls-files", "--others", "--exclude-standard"))
    )
    return paths


def read(relative: str) -> str:
    path = ROOT / relative
    require(path.is_file(), f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require_text(relative: str, *markers: str) -> None:
    text = read(relative)
    for marker in markers:
        require(marker in text, f"{relative} missing marker: {marker}")


def verify_history_and_surface() -> tuple[set[str], set[str]]:
    require(git("branch", "--show-current") == "main", "branch is not main")
    require(git("rev-parse", "HEAD") == IMPLEMENTATION_COMMIT, "HEAD is not RT-8c implementation commit")
    require(git("rev-parse", "origin/main") == IMPLEMENTATION_COMMIT, "origin/main is not RT-8c implementation commit")
    require(git("rev-parse", f"{IMPLEMENTATION_COMMIT}^") == IMPLEMENTATION_BASELINE, "RT-8c implementation parent mismatch")
    require(git("show", "-s", "--format=%s", IMPLEMENTATION_COMMIT) == IMPLEMENTATION_MESSAGE, "RT-8c implementation message mismatch")

    implementation_actual = normalized_paths(
        git("diff", "--name-only", f"{IMPLEMENTATION_BASELINE}..{IMPLEMENTATION_COMMIT}")
    )
    require(
        implementation_actual == IMPLEMENTATION_EXPECTED,
        f"implementation surface mismatch: {sorted(implementation_actual)}",
    )

    acceptance_actual = changed_paths()
    require(
        acceptance_actual == ACCEPTANCE_SYNC_EXPECTED,
        f"acceptance-sync surface mismatch: {sorted(acceptance_actual)}",
    )
    return implementation_actual, acceptance_actual


def verify_public_acceptance_content() -> None:
    for relative in TOP_DOCS:
        require_text(
            relative,
            "RT-8c configured PC Windows realtime acceptance",
            "RT-8c: COMPLETED / ACCEPTED / PUSHED",
            "RT-8c Stage 2 Controls A-H: COMPLETED / ACCEPTED",
            "RT-8c Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW",
            "RT-8d exact contract review: READY",
            "RT-8d implementation: NOT_AUTHORIZED",
            IMPLEMENTATION_COMMIT,
        )

    require_text(
        "README.md",
        "Current small commit: RT-8c Stage 3 PC Windows acceptance sync",
        "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
        "RT-8c Stage 1  COMPLETED / ACCEPTED / PUSHED",
        "RT-8d  READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED",
    )
    require_text(
        "roadmap.md",
        "Current small commit: RT-8c Stage 3 PC Windows acceptance sync",
    )
    require_text(
        "tasklist.md",
        "current small commit: RT-8c Stage 3 PC Windows acceptance sync",
        "current implementation state: COMPLETED / ACCEPTED / PUSHED",
    )
    require_text(
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "Current small commit: RT-8c Stage 3 PC Windows acceptance sync",
        "Current implementation state: COMPLETED / ACCEPTED / PUSHED",
    )

    contract = "docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md"
    for marker in (
        "## Accepted state",
        "A -> B -> D -> C -> E -> F -> G -> H",
        "manual_stream_start_count: 3",
        "completed_stream_terminal_count: 2",
        "cancelled_stream_terminal_count: 1",
        "cooperative_cancel_request_count: 1",
        "explicit_tts_enqueue_count: 2",
        "explicit_tts_process_count: 2",
        "explicit_flush_count: 1",
        "pending_after_flush: 0",
        "app_owned_motion_presentation_count: 1",
        "manual_vts_apply_count: 1",
        "vts_commands_requested: 1",
        "vts_commands_applied: 1",
        "vts_commands_completed: 1",
        "Backend / Flutter real_motion_executed: false",
        "operator-visible physical motion confirmed: true",
        "manifest stage: pc-windows",
        "manifest status: accepted",
        "strict schema validation: PASS",
        "candidate Git-state validation: PASS",
        "private manifest tracked: false",
        "private manifest committed: false",
        "private manifest pushed: false",
        "Android microphone/STT/voice-turn/soft-barge-in acceptance remains owned by",
        "Stage 3 surface",
        "Stage 3 stop rule",
    ):
        require_text(contract, marker)


def verify_unchanged_tooling() -> None:
    require(git_ok("diff", "--quiet", "HEAD", "--", RUNNER), "operator runner changed")
    require(git_ok("diff", "--quiet", "HEAD", "--", FOCUSED_TEST), "focused operator tests changed")

    runner = read(RUNNER)
    for marker in (
        "--check-inert",
        "--preflight",
        "--record-pc-windows",
        "PASS-PC-A",
        "ACCEPT-PC-WINDOWS",
        'expected_manifest_for_stage("pc_windows"',
        "target_already_exists",
        "private_manifest_content_printed: False",
    ):
        require(marker in runner, f"runner marker missing: {marker}")

    lowered = runner.lower()
    for forbidden in (
        "import socket",
        "import requests",
        "import httpx",
        "from urllib",
        "import urllib",
        "import websockets",
        "import pyvts",
        "popen(",
        "start-process",
    ):
        require(forbidden not in lowered, f"runner contains execution dependency: {forbidden}")

    tests = read(FOCUSED_TEST)
    require(tests.count("def test_") == 12, "focused test count is not exactly 12")


def verify_private_manifest_state_without_read() -> None:
    operator_root = (ROOT / "operator_evidence").resolve()
    resolved_parent = MANIFEST.parent.resolve()
    try:
        resolved_parent.relative_to(operator_root)
    except ValueError:
        fail("private manifest parent escaped operator_evidence")

    require(os.path.lexists(MANIFEST), "private manifest does not exist")
    require(not MANIFEST.is_symlink(), "private manifest is a symlink")
    require(MANIFEST.is_file(), "private manifest is not a regular file")
    require(
        git_ok("check-ignore", "--quiet", "--", MANIFEST_RELATIVE),
        "private manifest is not Git ignored",
    )
    require(
        git("ls-files", "--cached", "--", MANIFEST_RELATIVE) == "",
        "private manifest is Git tracked",
    )


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
    require(completed.returncode == 0, "inert runner failed")
    require(completed.stderr == "", "inert runner wrote stderr")
    for marker in (
        "private_manifest_created: False",
        "private_manifest_read: False",
        "private_configuration_read: False",
        "backend_started: False",
        "flutter_started: False",
        "http_attempted: False",
        "provider_execution_attempted: False",
        "network_execution_attempted: False",
        "tts_playback_vts_attempted: False",
    ):
        require(marker in completed.stdout, f"inert marker missing: {marker}")
    require(os.path.lexists(MANIFEST), "inert runner removed private manifest")


def verify_changed_content_privacy() -> None:
    for relative in ACCEPTANCE_SYNC_EXPECTED:
        diff = git("diff", "--unified=0", "HEAD", "--", relative)
        added = "\n".join(
            line[1:]
            for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        for pattern in SENSITIVE_PATTERNS:
            require(
                pattern.search(added) is None,
                f"private-looking added value detected in {relative}",
            )


def main() -> None:
    implementation_actual, acceptance_actual = verify_history_and_surface()
    verify_public_acceptance_content()
    verify_unchanged_tooling()
    verify_private_manifest_state_without_read()
    verify_inert_runner()
    verify_changed_content_privacy()

    print("v300_rt8c_status: completed-accepted-pushed")
    print("v300_rt8c_stage1_status: completed-accepted-pushed")
    print("v300_rt8c_stage2_status: completed-accepted")
    print("v300_rt8c_stage3_status: implemented-awaiting-review")
    print("v300_rt8c_implementation_baseline:", IMPLEMENTATION_BASELINE)
    print("v300_rt8c_implementation_commit:", IMPLEMENTATION_COMMIT)
    print("v300_rt8c_schema_version:", SCHEMA_VERSION)
    print("v300_rt8c_exact_implementation_surface:", implementation_actual == IMPLEMENTATION_EXPECTED)
    print("v300_rt8c_implementation_change_file_count:", len(implementation_actual))
    print("v300_rt8c_exact_acceptance_sync_surface:", acceptance_actual == ACCEPTANCE_SYNC_EXPECTED)
    print("v300_rt8c_acceptance_sync_change_file_count:", len(acceptance_actual))
    print("v300_rt8c_controls_a_h_accepted: True")
    print("v300_rt8c_pc_manual_stream_start_count: 3")
    print("v300_rt8c_pc_completed_stream_terminal_count: 2")
    print("v300_rt8c_pc_cancelled_stream_terminal_count: 1")
    print("v300_rt8c_pc_cooperative_cancel_request_count: 1")
    print("v300_rt8c_pc_explicit_tts_enqueue_count: 2")
    print("v300_rt8c_pc_explicit_tts_process_count: 2")
    print("v300_rt8c_pc_explicit_flush_count: 1")
    print("v300_rt8c_pc_pending_after_flush: 0")
    print("v300_rt8c_pc_app_owned_motion_presentation_count: 1")
    print("v300_rt8c_pc_manual_vts_apply_count: 1")
    print("v300_rt8c_manifest_recording_accepted: True")
    print("v300_rt8c_strict_validation_accepted: True")
    print("v300_rt8c_private_manifest_exists: True")
    print("v300_rt8c_private_manifest_ignored: True")
    print("v300_rt8c_private_manifest_tracked: False")
    print("v300_rt8c_private_manifest_read: False")
    print("v300_rt8c_private_values_printed: False")
    print("v300_rt8c_backend_runtime_changed: False")
    print("v300_rt8c_flutter_runtime_changed: False")
    print("v300_rt8c_existing_tests_changed: False")
    print("v300_rt8c_configured_execution_performed_by_gate: False")
    print("v300_rt8d_exact_contract_review_ready: True")
    print("v300_rt8d_authorized: False")
    print("v300_rt8c_stage3_commit_push_authorized: False")


if __name__ == "__main__":
    main()
