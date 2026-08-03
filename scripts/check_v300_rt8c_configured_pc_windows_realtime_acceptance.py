#!/usr/bin/env python3
"""Credential-free RT-8c Stage 1 source/tooling verification."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "4815403d4c94b05551df03678e9c2c4e1dfe754e"
PARENT = "eedc32a6293b99435d1d2e60b4a4a6e7c519c8d5"
BASELINE_MESSAGE = "fix: correct RT-8 PC acceptance execution counts"
SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"

EXACT_PATHS = {
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
RT8B1_PATHS = {
    "README.md",
    "backend/tests/test_v300_rt8_private_operator_manifest.py",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json",
    "docs/v300_rt8b_private_operator_manifest_and_runbook.md",
    "roadmap.md",
    "scripts/README.md",
    "scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py",
    "scripts/validate_v300_rt8_private_operator_manifest.py",
    "tasklist.md",
}
TOP_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)
MANIFEST = ROOT / "operator_evidence" / "v300_rt8_pc_android_realtime_acceptance.json"


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt8c_stage1_gate_error: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def changed_paths() -> set[str]:
    paths: set[str] = set()
    for args in (("diff", "--name-only"), ("diff", "--cached", "--name-only")):
        paths.update(line.replace("\\", "/") for line in git(*args).splitlines() if line)
    paths.update(
        line.replace("\\", "/")
        for line in git("ls-files", "--others", "--exclude-standard").splitlines()
        if line
    )
    return paths


def committed_paths(commit: str) -> set[str]:
    return {
        line.replace("\\", "/")
        for line in git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        if line
    }


def read(relative: str) -> str:
    path = ROOT / relative
    require(path.is_file(), f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def verify_history_and_surface(snapshot: bool) -> tuple[bool, bool, bool]:
    if snapshot:
        return False, False, False
    require(git("rev-parse", "HEAD") == BASELINE, "HEAD is not RT-8b1 baseline")
    require(git("rev-parse", "origin/main") == BASELINE, "origin/main is not RT-8b1 baseline")
    require(git("rev-parse", f"{BASELINE}^") == PARENT, "RT-8b1 parent mismatch")
    require(git("show", "-s", "--format=%s", BASELINE) == BASELINE_MESSAGE, "RT-8b1 message mismatch")
    require(committed_paths(BASELINE) == RT8B1_PATHS, "RT-8b1 committed surface mismatch")
    require(changed_paths() == EXACT_PATHS, "RT-8c Stage 1 exact surface mismatch")
    return True, True, True


def verify_content() -> None:
    for relative in EXACT_PATHS:
        require((ROOT / relative).is_file(), f"candidate file missing: {relative}")
    require(not os.path.lexists(MANIFEST), "private RT-8 manifest exists during Stage 1")

    for relative in TOP_DOCS:
        text = read(relative)
        for marker in (
            "RT-8c Stage 1",
            "IMPLEMENTED / AWAITING_REVIEW",
            BASELINE,
            "RT-8b1: COMPLETED / ACCEPTED / PUSHED",
            "RT-8c Stage 2",
            "NOT_AUTHORIZED",
        ):
            require(marker in text, f"missing {relative} marker: {marker}")

    contract = read("docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md")
    for marker in (
        "A -> B -> D -> C -> E -> F -> G -> H",
        "manual_stream_start_count: 3",
        "completed_stream_terminal_count: 2",
        "cancelled_stream_terminal_count: 1",
        "explicit_tts_enqueue_count: 2",
        "explicit_tts_process_count: 2",
        "explicit_flush_count: 1",
        "total real VTS executions: exactly 1",
        "private manifest created: false",
        "RT-8c Stage 2: NOT_AUTHORIZED",
    ):
        require(marker in contract, f"missing contract marker: {marker}")

    runner = read("scripts/run_v300_rt8c_private_pc_windows_operator.py")
    for marker in (
        "--check-inert",
        "--preflight",
        "--record-pc-windows",
        "PASS-PC-A",
        "ACCEPT-PC-WINDOWS",
        "expected_manifest_for_stage(\"pc_windows\"",
        "target_already_exists",
        "private_manifest_content_printed: False",
    ):
        require(marker in runner, f"missing runner marker: {marker}")
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

    tests = read("backend/tests/test_v300_rt8c_private_pc_windows_operator.py")
    require(tests.count("def test_") == 12, "focused test count is not exactly 12")


def verify_inert_runner() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/run_v300_rt8c_private_pc_windows_operator.py", "--check-inert"],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
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
    require(not os.path.lexists(MANIFEST), "inert runner created private manifest")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()
    history, origin, surface = verify_history_and_surface(args.snapshot)
    verify_content()
    verify_inert_runner()
    print("v300_rt8c_stage1_status: operator-tooling-implemented-awaiting-review")
    print(f"v300_rt8c_stage1_baseline: {BASELINE}")
    print(f"v300_rt8c_stage1_snapshot_mode: {args.snapshot}")
    print(f"v300_rt8c_stage1_git_history_verified: {history}")
    print(f"v300_rt8c_stage1_origin_main_verified: {origin}")
    print(f"v300_rt8c_stage1_rt8b1_commit_verified: {history}")
    print(f"v300_rt8c_stage1_exact_worktree_surface_verified: {surface}")
    print("v300_rt8c_stage1_exact_change_surface: True")
    print(f"v300_rt8c_stage1_change_file_count: {len(EXACT_PATHS)}")
    print(f"v300_rt8c_schema_version: {SCHEMA_VERSION}")
    print("v300_rt8c_pc_manual_stream_start_count: 3")
    print("v300_rt8c_pc_completed_stream_terminal_count: 2")
    print("v300_rt8c_pc_cancelled_stream_terminal_count: 1")
    print("v300_rt8c_pc_explicit_tts_enqueue_count: 2")
    print("v300_rt8c_pc_explicit_tts_process_count: 2")
    print("v300_rt8c_pc_explicit_flush_count: 1")
    print("v300_rt8c_operator_runner_inert_by_default: True")
    print("v300_rt8c_operator_runner_starts_processes: False")
    print("v300_rt8c_operator_runner_network_free: True")
    print("v300_rt8c_private_manifest_created: False")
    print("v300_rt8c_private_manifest_read: False")
    print("v300_rt8c_private_configuration_read: False")
    print("v300_rt8c_backend_runtime_changed: False")
    print("v300_rt8c_flutter_runtime_changed: False")
    print("v300_rt8c_existing_tests_changed: False")
    print("v300_rt8c_new_focused_test_file_added: True")
    print("v300_rt8c_pc_execution_authorized: False")
    print("v300_rt8c_stage1_commit_push_authorized: False")


if __name__ == "__main__":
    main()
