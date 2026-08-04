#!/usr/bin/env python3
"""RT-8d Stage 3 public Android acceptance-sync verification gate."""

from __future__ import annotations
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "b889ce884a928809125c473dcd2e8cd7a4c020ef"
COMMIT = "0e7fc6fc5922c293b8460fc816610d41c2a79e9a"
MESSAGE = "test/docs: add RT-8d Android operator tooling"
PC = "fa39065130a4a4689c2e54195f231a5e79c62a35"
SCHEMA = "drc.v3.rt8-platform-acceptance.2"
RUNNER = "scripts/run_v300_rt8d_private_android_operator.py"
TEST = "backend/tests/test_v300_rt8d_private_android_operator.py"
VALIDATOR = "scripts/validate_v300_rt8_private_operator_manifest.py"
CONTRACT = "docs/v300_rt8d_configured_android_realtime_acceptance.md"
MREL = "operator_evidence/v300_rt8_pc_android_realtime_acceptance.json"
MANIFEST = ROOT / MREL

IMPLEMENTATION = {
    "README.md", "roadmap.md", "tasklist.md", "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt8d_configured_android_realtime_acceptance.md",
    "scripts/check_v300_rt8d_configured_android_realtime_acceptance.py",
    RUNNER, TEST,
}
ACCEPTANCE = {
    "README.md", "roadmap.md", "tasklist.md", "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    CONTRACT,
    "scripts/check_v300_rt8d_configured_android_realtime_acceptance.py",
}
TOP = (
    "README.md", "roadmap.md", "tasklist.md", "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
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
    raise SystemExit("v300_rt8d_stage3_gate_error: " + message)

def req(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def git(*args: str) -> str:
    cp = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, text=True,
        encoding="utf-8", errors="surrogateescape",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if cp.returncode:
        fail(cp.stderr.strip() or "git command failed")
    return cp.stdout.strip()

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
    req(path.is_file(), "missing " + relative)
    return path.read_text(encoding="utf-8")

def markers(relative: str, *values: str) -> None:
    text = read(relative)
    for value in values:
        req(value in text, f"{relative} missing {value}")

def verify_history() -> tuple[set[str], set[str]]:
    req(git("branch", "--show-current") == "main", "branch")
    req(git("rev-parse", "HEAD") == COMMIT, "HEAD")
    req(git("rev-parse", "origin/main") == COMMIT, "origin")
    req(git("rev-parse", COMMIT + "^") == BASELINE, "parent")
    req(git("show", "-s", "--format=%s", COMMIT) == MESSAGE, "message")
    req(git_ok("cat-file", "-e", PC + "^{commit}"), "PC source missing")
    req(git_ok("merge-base", "--is-ancestor", PC, COMMIT), "PC ancestry")
    implementation = paths(git("diff", "--name-only", BASELINE + ".." + COMMIT))
    acceptance = changed()
    req(implementation == IMPLEMENTATION, "implementation surface " + repr(sorted(implementation)))
    req(acceptance == ACCEPTANCE, "acceptance surface " + repr(sorted(acceptance)))
    return implementation, acceptance

def verify_docs() -> None:
    for relative in TOP:
        markers(
            relative,
            "RT-8d configured Android smartphone realtime acceptance",
            "RT-8d: COMPLETED / ACCEPTED / PUSHED",
            "RT-8d Stage 2c: COMPLETED / PASS / ACCEPTED",
            "RT-8d Stage 2d: COMPLETED / PASS / ACCEPTED",
            "RT-8d Stage 2e: COMPLETED / PASS / ACCEPTED",
            "RT-8d Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW",
            "RT-8e exact contract review: READY",
            "RT-8e implementation: NOT_AUTHORIZED",
            "all accepted facts come only from the separately",
            COMMIT,
        )
    markers("README.md", "Current small commit: RT-8d Stage 3 Android acceptance sync")
    markers("roadmap.md", "Current small commit: RT-8d Stage 3 Android acceptance sync")
    markers("tasklist.md", "current small commit: RT-8d Stage 3 Android acceptance sync")
    markers(
        "docs/DRC_v300_goal_checklist_small_commit.md",
        "Current implementation step: RT-8d Stage 3 public-safe Android acceptance synchronization",
        "Next implementation action: verify exact seven-file RT-8d Stage 3 acceptance sync; commit/push and RT-8e remain NOT_AUTHORIZED",
    )
    markers(
        "roadmap.md",
        "Current implementation boundary: exact 7 public documentation/static-gate files",
    )
    markers(
        "README.md",
        "Historical v2.1.0 terminal marker retained for accepted v2.1.0 checks:\n\n```text\nCurrent small commit: none\n```",
    )
    markers("roadmap.md", "Current small commit: none (M-9 accepted; v2.0.1 released)")
    markers(
        "tasklist.md",
        "Current parent phase: RT-2 CURRENT / NOT_COMPLETED\nCurrent small commit: RT-2a CURRENT / NOT_COMPLETED",
    )
    markers(
        "scripts/README.md",
        "v2.0.1 RELEASED\nM-1 through M-9 COMPLETED / ACCEPTED\ncurrent small commit: none",
        "Current implementation state: `COMPLETED / ACCEPTED`. RT-2b is `CURRENT / NOT_COMPLETED; NOT_STARTED`.",
        "Current implementation state: `COMPLETED / ACCEPTED`. RT-2e is `CURRENT / NOT_COMPLETED; NOT_STARTED`.",
    )
    req(
        read("README.md").count("Current small commit: RT-8d Stage 3 Android acceptance sync") == 1,
        "README current marker count",
    )
    req(
        read("roadmap.md").count("Current small commit: RT-8d Stage 3 Android acceptance sync") == 2,
        "roadmap current marker count",
    )
    req(
        read("tasklist.md").count("current small commit: RT-8d Stage 3 Android acceptance sync") == 1,
        "tasklist current marker count",
    )
    req(
        read("scripts/README.md").count("current small commit: RT-8d Stage 3 Android acceptance sync") == 1,
        "scripts README current marker count",
    )
    markers(
        CONTRACT,
        "## Accepted state",
        "## Historical failed attempt and accepted fresh rerun",
        "The original configured Stage 2c attempt remains `FAILED / NOT_ACCEPTED`.",
        "private-manifest modification state remains `UNKNOWN`",
        "Only that fresh rerun supplies the accepted Control",
        "A -> B -> C -> D -> E -> F -> G -> H",
        "natural_voice_turn_count: 1",
        "silent_control_interruption_count: 0",
        "confirmed_user_speech_event_count: 1",
        "drc_local_interruption_count: 1",
        "pending_voice_output_after_interruption: 0",
        "recovery_voice_turn_count: 1",
        "manual_vts_apply_count: 1",
        "vts_commands_requested: 1",
        "vts_commands_applied: 1",
        "vts_commands_completed: 1",
        "Framework session created: true",
        "Framework session closed: true",
        "provider execution attempted: true",
        "network execution attempted: true",
        "Backend / Flutter real_motion_executed: false",
        "operator-visible physical motion confirmed: true",
        "operator-visible physical motion count: 1",
        "manifest stage: android",
        "manifest status: accepted",
        "fixed confirmation count: 9",
        "previous PC section preserved: true",
        "strict schema validation: PASS",
        "candidate Git-state validation: PASS",
        "PC candidate ancestry validation: PASS",
        "private manifest tracked: false",
        "private manifest committed: false",
        "private manifest pushed: false",
        "## Exact Stage 3 surface",
        "## Stage 3 stop rule",
    )

def verify_tools() -> None:
    for relative in (RUNNER, TEST, VALIDATOR):
        req(git_ok("diff", "--quiet", "HEAD", "--", relative), relative + " changed")
    runner = read(RUNNER)
    for value in (
        "--check-inert", "--preflight", "--check-pc-transition", "--record-android",
        "PASS-ANDROID-", "ACCEPT-ANDROID", 'expected_manifest_for_stage("android"',
        "os.replace", "private_manifest_content_printed: False",
    ):
        req(value in runner, "runner marker " + value)
    for forbidden in (
        "import requests", "import httpx", "import socket", "import adb",
        "import pyvts", "import websockets", "popen(", "start-process",
    ):
        req(forbidden not in runner.lower(), "runner forbidden " + forbidden)
    req(read(TEST).count("def test_") == 18, "focused test count")
    validator = read(VALIDATOR)
    for value in (
        'SCHEMA_VERSION = "drc.v3.rt8-platform-acceptance.2"',
        "validate_private_manifest_path", "validate_manifest_data", "verify_git_state",
        'choices=("pc-windows", "android", "aggregate")',
    ):
        req(value in validator, "validator marker " + value)

def verify_manifest_without_read() -> None:
    operator_root = (ROOT / "operator_evidence").resolve()
    try:
        MANIFEST.parent.resolve().relative_to(operator_root)
    except ValueError:
        fail("manifest boundary")
    req(os.path.lexists(MANIFEST), "manifest missing")
    req(MANIFEST.is_file() and not MANIFEST.is_symlink(), "manifest regular")
    req(git_ok("check-ignore", "--quiet", "--", MREL), "manifest ignored")
    req(git("ls-files", "--cached", "--", MREL) == "", "manifest tracked")

def verify_inert() -> None:
    before = MANIFEST.stat()
    cp = subprocess.run(
        [sys.executable, RUNNER, "--check-inert"], cwd=ROOT, check=False,
        text=True, encoding="utf-8", errors="strict",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    req(cp.returncode == 0 and cp.stderr == "", "inert runner")
    for value in (
        "operator_mode: inert-check", "private_manifest_read: False",
        "private_manifest_modified: False", "private_configuration_read: False",
        "android_adb_started: False", "backend_flutter_started: False",
        "microphone_stt_tts_playback_attempted: False",
        "provider_network_vts_attempted: False",
    ):
        req(value in cp.stdout, "inert marker " + value)
    after = MANIFEST.stat()
    req((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), "manifest metadata")

def verify_privacy() -> None:
    for relative in ACCEPTANCE:
        diff = git("diff", "--unified=0", "HEAD", "--", relative)
        added = "\n".join(
            line[1:] for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        for pattern in SENSITIVE:
            req(pattern.search(added) is None, "private-looking value in " + relative)

def main() -> None:
    implementation, acceptance = verify_history()
    verify_docs()
    verify_tools()
    verify_manifest_without_read()
    verify_inert()
    verify_privacy()
    print("v300_rt8d_status: completed-accepted-pushed")
    print("v300_rt8d_stage1_status: completed-accepted-pushed")
    print("v300_rt8d_stage2_status: completed-accepted")
    print("v300_rt8d_stage2a_status: completed-pass")
    print("v300_rt8d_stage2b_status: completed-pass")
    print("v300_rt8d_stage2c_status: completed-pass-accepted")
    print("v300_rt8d_stage2d_status: completed-pass-accepted")
    print("v300_rt8d_stage2e_status: completed-pass-accepted")
    print("v300_rt8d_stage3_status: implemented-awaiting-review")
    print("v300_rt8d_implementation_baseline:", BASELINE)
    print("v300_rt8d_implementation_commit:", COMMIT)
    print("v300_rt8d_schema_version:", SCHEMA)
    print("v300_rt8d_exact_implementation_surface:", implementation == IMPLEMENTATION)
    print("v300_rt8d_implementation_change_file_count:", len(implementation))
    print("v300_rt8d_exact_acceptance_sync_surface:", acceptance == ACCEPTANCE)
    print("v300_rt8d_acceptance_sync_change_file_count:", len(acceptance))
    print("v300_rt8d_original_stage2c_attempt_accepted: False")
    print("v300_rt8d_original_stage2c_manifest_modified: UNKNOWN")
    print("v300_rt8d_fresh_controls_a_h_rerun_accepted: True")
    print("v300_rt8d_controls_a_h_accepted: True")
    print("v300_rt8d_android_natural_voice_turn_count: 1")
    print("v300_rt8d_android_silent_control_interruption_count: 0")
    print("v300_rt8d_android_confirmed_user_speech_event_count: 1")
    print("v300_rt8d_android_drc_local_interruption_count: 1")
    print("v300_rt8d_android_pending_after_interruption: 0")
    print("v300_rt8d_android_recovery_voice_turn_count: 1")
    print("v300_rt8d_android_manual_vts_apply_count: 1")
    print("v300_rt8d_android_vts_commands_requested: 1")
    print("v300_rt8d_android_vts_commands_applied: 1")
    print("v300_rt8d_android_vts_commands_completed: 1")
    print("v300_rt8d_android_operator_visible_motion_count: 1")
    print("v300_rt8d_manifest_recording_accepted: True")
    print("v300_rt8d_strict_validation_accepted: True")
    print("v300_rt8d_private_manifest_exists: True")
    print("v300_rt8d_private_manifest_ignored: True")
    print("v300_rt8d_private_manifest_tracked: False")
    print("v300_rt8d_private_manifest_read: False")
    print("v300_rt8d_private_manifest_modified: False")
    print("v300_rt8d_private_values_printed: False")
    print("v300_rt8d_backend_runtime_changed: False")
    print("v300_rt8d_flutter_runtime_changed: False")
    print("v300_rt8d_existing_tests_changed: False")
    print("v300_rt8d_configured_execution_performed_by_gate: False")
    print("v300_rt8e_exact_contract_review_ready: True")
    print("v300_rt8e_authorized: False")
    print("v300_rt8d_stage3_commit_push_authorized: False")

if __name__ == "__main__":
    main()
