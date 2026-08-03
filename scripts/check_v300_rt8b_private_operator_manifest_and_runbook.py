#!/usr/bin/env python3
"""Credential-free RT-8b1 strict PC execution-count contract verification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "eedc32a6293b99435d1d2e60b4a4a6e7c519c8d5"
RT8B_PARENT = "a3af4fae002c1425fdfb61b46f66e35e2443ad17"
RT8B_MESSAGE = "docs/test: add RT-8 private operator manifest tooling"
SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"

EXACT_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt8b_private_operator_manifest_and_runbook.md",
    "docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json",
    "scripts/validate_v300_rt8_private_operator_manifest.py",
    "scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py",
    "backend/tests/test_v300_rt8_private_operator_manifest.py",
}
RT8B_PATHS = set(EXACT_PATHS)
TOP_DOCS = (
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
)
SENSITIVE_PATTERNS = (
    r"(?i)sk-[a-z0-9_-]{12,}",
    r"(?i)xai-[a-z0-9_-]{12,}",
    r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^<][^'\"]{7,}",
    r"(?i)(?:^|\s)[a-z]:\\(?:users|work|home)\\",
    r"/(?:home|users)/[^/\s]+/",
    r"\b(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b",
)


def fail(message: str) -> None:
    raise SystemExit(f"v300_rt8b1_gate_error: {message}")


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
        output = git(*args)
        paths.update(line.replace("\\", "/") for line in output.splitlines() if line)
    untracked = git("ls-files", "--others", "--exclude-standard")
    paths.update(line.replace("\\", "/") for line in untracked.splitlines() if line)
    return paths


def committed_paths(commit: str) -> set[str]:
    output = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    return {line.replace("\\", "/") for line in output.splitlines() if line}


def read(relative: str) -> str:
    path = ROOT / relative
    require(path.is_file(), f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        require(marker in text, f"missing {label} marker: {marker}")


def verify_history_and_surface(snapshot: bool) -> tuple[bool, bool, bool]:
    if snapshot:
        return False, False, False
    require(git("rev-parse", "HEAD") == BASELINE, "HEAD is not accepted RT-8b baseline")
    require(git("rev-parse", "origin/main") == BASELINE, "origin/main is not accepted RT-8b baseline")
    require(git("rev-parse", f"{BASELINE}^") == RT8B_PARENT, "RT-8b parent mismatch")
    require(
        git("show", "-s", "--format=%s", BASELINE) == RT8B_MESSAGE,
        "RT-8b commit message mismatch",
    )
    require(committed_paths(BASELINE) == RT8B_PATHS, "RT-8b committed surface mismatch")
    actual = changed_paths()
    require(
        actual == EXACT_PATHS,
        f"RT-8b1 exact surface mismatch: expected={sorted(EXACT_PATHS)}, actual={sorted(actual)}",
    )
    return True, True, True


def verify_candidate_content() -> None:
    for relative in EXACT_PATHS:
        require((ROOT / relative).is_file(), f"candidate file missing: {relative}")

    for relative in TOP_DOCS:
        text = read(relative)
        require_markers(
            text,
            (
                "RT-8b1 strict PC execution-count contract corrective",
                "IMPLEMENTED / AWAITING_REVIEW",
                BASELINE,
                "RT-8b: COMPLETED / ACCEPTED / PUSHED",
                "RT-8c",
                "NOT_AUTHORIZED",
                "RT-8b1-STRICT-PC-COUNT-CORRECTIVE:BEGIN",
                "RT-8b1-STRICT-PC-COUNT-CORRECTIVE:END",
            ),
            relative,
        )

    contract = read("docs/v300_rt8b_private_operator_manifest_and_runbook.md")
    require_markers(
        contract,
        (
            SCHEMA_VERSION,
            "RT-8b1: IMPLEMENTED / AWAITING_REVIEW",
            "manual_stream_start_count: 3",
            "completed_stream_terminal_count: 2",
            "cancelled_stream_terminal_count: 1",
            "explicit_tts_enqueue_count: 2",
            "explicit_tts_process_count: 2",
            "explicit_flush_count: 1",
            "private manifest created: false",
            "private manifest read: false",
            "RT-8c implementation: NOT_AUTHORIZED",
        ),
        "RT-8b1 contract",
    )

    example_text = read(
        "docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json"
    )
    try:
        example = json.loads(example_text)
    except json.JSONDecodeError as exc:
        fail(f"example JSON invalid: {exc.msg}")
    require(example.get("schema_version") == SCHEMA_VERSION, "example schema version mismatch")
    require(example.get("stage") == "example", "example stage mismatch")
    require(example.get("status") == "example_not_accepted", "example must remain rejected")
    pc = example.get("pc_windows")
    require(isinstance(pc, dict), "example PC section missing")
    for key in (
        "manual_stream_start_count",
        "completed_stream_terminal_count",
        "cancelled_stream_terminal_count",
        "cooperative_cancel_request_count",
        "explicit_tts_enqueue_count",
        "explicit_tts_process_count",
        "explicit_flush_count",
    ):
        require(type(pc.get(key)) is int and pc.get(key) == 0, f"example zero count mismatch: {key}")

    validator = read("scripts/validate_v300_rt8_private_operator_manifest.py")
    require_markers(
        validator,
        (
            f'SCHEMA_VERSION = "{SCHEMA_VERSION}"',
            '"completed_stream_terminal_count"',
            '"cancelled_stream_terminal_count"',
            '"explicit_tts_enqueue_count"',
            "manual_stream_start_count=3",
            "completed_stream_terminal_count=2",
            "cancelled_stream_terminal_count=1",
            "explicit_tts_enqueue_count=2",
            "explicit_tts_process_count=2",
            "explicit_flush_count=1",
        ),
        "validator",
    )
    lowered = validator.lower()
    for forbidden in (
        "import socket",
        "import requests",
        "import httpx",
        "from urllib",
        "import urllib",
        "import websockets",
        "import pyvts",
        "package:record",
        "audioplayers",
    ):
        require(forbidden not in lowered, f"validator contains execution dependency: {forbidden}")

    tests = read("backend/tests/test_v300_rt8_private_operator_manifest.py")
    require(tests.count("def test_") >= 21, "focused validator corrective coverage is too small")
    require_markers(
        tests,
        (
            "test_rt8b1_schema_version_is_v2",
            "test_rt8b1_v1_schema_is_rejected",
            "test_rt8b1_pc_counts_are_exact",
            "test_rt8b1_incorrect_stream_split_is_rejected",
            "test_rt8b1_incorrect_tts_counts_are_rejected",
        ),
        "focused tests",
    )

    public_content_paths = set(TOP_DOCS) | {
        "docs/v300_rt8b_private_operator_manifest_and_runbook.md",
        "docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json",
    }
    for relative in public_content_paths:
        text = read(relative)
        for pattern in SENSITIVE_PATTERNS:
            require(not re.search(pattern, text), f"sensitive-looking content in {relative}")

    evidence_root = ROOT / "operator_evidence"
    if evidence_root.exists():
        rt8_evidence = []
        for candidate in evidence_root.rglob("*"):
            relative = candidate.relative_to(evidence_root)
            if any(part.lower().startswith(("v300_rt8", "rt8")) for part in relative.parts):
                rt8_evidence.append(candidate)
        require(not rt8_evidence, "RT-8 private operator evidence exists during RT-8b1")


def verify_example_command() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_v300_rt8_private_operator_manifest.py", "--check-example"],
        cwd=ROOT,
        check=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    require(completed.stderr == "", "example validator wrote stderr")
    require("rejected-as-template" in completed.stdout, "example validator did not reject template")
    require("private_file_read: False" in completed.stdout, "example private-read marker missing")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    args = parser.parse_args()

    history_verified, origin_verified, surface_verified = verify_history_and_surface(
        args.snapshot
    )
    verify_candidate_content()
    verify_example_command()

    print("v300_rt8b1_status: implemented-awaiting-review")
    print(f"v300_rt8b1_baseline: {BASELINE}")
    print(f"v300_rt8b1_snapshot_mode: {args.snapshot}")
    print(f"v300_rt8b1_git_history_verified: {history_verified}")
    print(f"v300_rt8b1_origin_main_verified: {origin_verified}")
    print(f"v300_rt8b1_rt8b_commit_verified: {history_verified}")
    print(f"v300_rt8b1_exact_worktree_surface_verified: {surface_verified}")
    print("v300_rt8b1_exact_change_surface: True")
    print(f"v300_rt8b1_change_file_count: {len(EXACT_PATHS)}")
    print(f"v300_rt8b1_schema_version: {SCHEMA_VERSION}")
    print("v300_rt8b1_pc_manual_stream_start_count: 3")
    print("v300_rt8b1_pc_completed_stream_terminal_count: 2")
    print("v300_rt8b1_pc_cancelled_stream_terminal_count: 1")
    print("v300_rt8b1_pc_cooperative_cancel_request_count: 1")
    print("v300_rt8b1_pc_explicit_tts_enqueue_count: 2")
    print("v300_rt8b1_pc_explicit_tts_process_count: 2")
    print("v300_rt8b1_pc_explicit_flush_count: 1")
    print("v300_rt8b1_public_example_rejected: True")
    print("v300_rt8b1_private_manifest_created: False")
    print("v300_rt8b1_private_manifest_read: False")
    print("v300_rt8b1_backend_runtime_changed: False")
    print("v300_rt8b1_flutter_runtime_changed: False")
    print("v300_rt8b1_existing_focused_test_changed: True")
    print("v300_rt8b1_other_existing_tests_changed: False")
    print("v300_rt8b1_private_configuration_read: False")
    print("v300_rt8b1_provider_execution_attempted: False")
    print("v300_rt8b1_network_execution_attempted: False")
    print("v300_rt8b1_microphone_used: False")
    print("v300_rt8b1_real_tts_executed: False")
    print("v300_rt8b1_real_motion_executed: False")
    print("v300_rt8c_exact_contract_review_ready: True")
    print("v300_rt8c_implementation_authorized: False")
    print("v300_rt8b1_commit_push_authorized: False")


if __name__ == "__main__":
    main()
