#!/usr/bin/env python3
"""Credential-free RT-8d Android operator manifest transition runner."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable, Mapping, TextIO
import validate_v300_rt8_private_operator_manifest as validator

ROOT = Path(__file__).resolve().parents[1]
RT8C_ACCEPTANCE_SYNC_BASELINE = "b889ce884a928809125c473dcd2e8cd7a4c020ef"
PC_ACCEPTED_SOURCE_HEAD = "fa39065130a4a4689c2e54195f231a5e79c62a35"
MANIFEST_RELATIVE = Path("operator_evidence/v300_rt8_pc_android_realtime_acceptance.json")
EXPECTED_CONFIRMATIONS = tuple([f"PASS-ANDROID-{x}" for x in "ABCDEFGH"] + ["ACCEPT-ANDROID"])
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
GitOutput = Callable[[tuple[str, ...], Path], str]
GitOk = Callable[[tuple[str, ...], Path], bool]
ReplaceFunc = Callable[[object, object], None]

class OperatorError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)

@dataclass(frozen=True)
class TargetState:
    ignored: bool
    exists: bool
    symlink: bool
    tracked: bool

def _default_git_output(args: tuple[str, ...], root: Path) -> str:
    cp = subprocess.run(["git", *args], cwd=root, check=True, text=True,
        encoding="utf-8", errors="strict", stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return cp.stdout.strip()

def _default_git_ok(args: tuple[str, ...], root: Path) -> bool:
    return subprocess.run(["git", *args], cwd=root, check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

def _target(root: Path) -> Path:
    target = root / MANIFEST_RELATIVE
    try:
        target.parent.resolve().relative_to((root / "operator_evidence").resolve())
    except ValueError as exc:
        raise OperatorError("target_boundary_invalid") from exc
    if target.name != "v300_rt8_pc_android_realtime_acceptance.json":
        raise OperatorError("target_boundary_invalid")
    return target

def _default_target_probe(root: Path, git_ok: GitOk, git_output: GitOutput) -> TargetState:
    target = _target(root)
    return TargetState(
        ignored=git_ok(("check-ignore", "--quiet", "--", MANIFEST_RELATIVE.as_posix()), root),
        exists=os.path.lexists(target), symlink=target.is_symlink(),
        tracked=bool(git_output(("ls-files", "--cached", "--", MANIFEST_RELATIVE.as_posix()), root)),
    )

def preflight(expected_source_head: str, *, root: Path = ROOT,
    git_output: GitOutput = _default_git_output, git_ok: GitOk = _default_git_ok,
    target_probe: Callable[[Path, GitOk, GitOutput], TargetState] = _default_target_probe) -> str:
    if not SHA_RE.fullmatch(expected_source_head):
        raise OperatorError("expected_source_head_invalid")
    if expected_source_head == RT8C_ACCEPTANCE_SYNC_BASELINE:
        raise OperatorError("stage1_source_not_committed")
    branch = git_output(("branch", "--show-current"), root)
    head = git_output(("rev-parse", "HEAD"), root)
    origin = git_output(("rev-parse", "origin/main"), root)
    status = git_output(("status", "--porcelain"), root)
    if branch != "main": raise OperatorError("branch_not_main")
    if head != origin: raise OperatorError("origin_main_not_synchronized")
    if head != expected_source_head: raise OperatorError("expected_source_head_mismatch")
    if status: raise OperatorError("working_tree_not_clean")
    for commit, missing, ancestry in (
        (RT8C_ACCEPTANCE_SYNC_BASELINE, "rt8c_acceptance_commit_missing", "rt8c_acceptance_not_ancestor"),
        (PC_ACCEPTED_SOURCE_HEAD, "pc_candidate_commit_missing", "pc_candidate_not_ancestor"),
    ):
        if not git_ok(("cat-file", "-e", f"{commit}^{{commit}}"), root): raise OperatorError(missing)
        if not git_ok(("merge-base", "--is-ancestor", commit, head), root): raise OperatorError(ancestry)
    state = target_probe(root, git_ok, git_output)
    if not state.ignored: raise OperatorError("target_not_ignored")
    if not state.exists: raise OperatorError("target_missing")
    if state.symlink: raise OperatorError("target_is_symlink")
    if state.tracked: raise OperatorError("target_is_tracked")
    return head

def _load_pc_transition(expected_source_head: str, *, root: Path,
    git_output: GitOutput, git_ok: GitOk,
    target_probe: Callable[[Path, GitOk, GitOutput], TargetState]):
    head = preflight(expected_source_head, root=root, git_output=git_output,
        git_ok=git_ok, target_probe=target_probe)
    try:
        raw = _target(root).read_bytes()
        data = validator.load_json_bytes(raw)
        validator.validate_manifest_data(data, "pc-windows")
    except (OSError, validator.ValidationError) as exc:
        raise OperatorError("pc_transition_manifest_invalid") from exc
    if data.get("pc_windows_candidate_source_head") != PC_ACCEPTED_SOURCE_HEAD:
        raise OperatorError("pc_candidate_source_mismatch")
    if data.get("android_candidate_source_head") != validator.EXAMPLE_HEAD:
        raise OperatorError("android_placeholder_mismatch")
    aggregate = data.get("aggregate_cleanup")
    if not isinstance(aggregate, Mapping) or aggregate.get("status") != "not_run":
        raise OperatorError("aggregate_not_not_run")
    if not git_ok(("merge-base", "--is-ancestor", PC_ACCEPTED_SOURCE_HEAD, head), root):
        raise OperatorError("pc_candidate_not_ancestor")
    return head, raw, data

def _confirm(stdin: TextIO, stdout: TextIO) -> None:
    for i, expected in enumerate(EXPECTED_CONFIRMATIONS, 1):
        stdout.write(f"v300_rt8d_confirmation_{i}_required: {expected}\n"); stdout.flush()
        supplied = stdin.readline()
        if supplied == "" or supplied.strip() != expected:
            raise OperatorError("confirmation_rejected")

def _android_bytes(head: str) -> bytes:
    data = validator.expected_manifest_for_stage("android",
        pc_head=PC_ACCEPTED_SOURCE_HEAD, android_head=head)
    validator.validate_manifest_data(data, "android")
    raw = (json.dumps(data, indent=2, sort_keys=False) + "\n").encode()
    if len(raw) > validator.MAX_MANIFEST_BYTES: raise OperatorError("generated_manifest_too_large")
    return raw

def _atomic_replace(root: Path, original: bytes, new: bytes,
    replace_func: ReplaceFunc = os.replace) -> None:
    target = _target(root)
    temp = target.with_name(target.name + ".rt8d-transition.tmp")
    if os.path.lexists(temp): raise OperatorError("temporary_target_exists")
    try:
        with temp.open("xb") as f:
            f.write(new); f.flush(); os.fsync(f.fileno())
        if target.read_bytes() != original: raise OperatorError("target_changed_during_transition")
        replace_func(temp, target)
    finally:
        if os.path.lexists(temp): temp.unlink()

def run_operator(*, mode: str, expected_source_head: str | None = None,
    root: Path = ROOT, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr, git_output: GitOutput = _default_git_output,
    git_ok: GitOk = _default_git_ok,
    target_probe: Callable[[Path, GitOk, GitOutput], TargetState] = _default_target_probe,
    replace_func: ReplaceFunc = os.replace) -> int:
    try:
        if mode == "check_inert":
            for line in ("operator_mode: inert-check", "git_inspected: False",
                "private_manifest_read: False", "private_manifest_modified: False",
                "private_configuration_read: False", "android_adb_started: False",
                "backend_flutter_started: False", "microphone_stt_tts_playback_attempted: False",
                "provider_network_vts_attempted: False"):
                stdout.write("v300_rt8d_" + line + "\n")
            return 0
        if expected_source_head is None: raise OperatorError("expected_source_head_required")
        if mode == "preflight":
            preflight(expected_source_head, root=root, git_output=git_output,
                git_ok=git_ok, target_probe=target_probe)
            for line in ("operator_mode: preflight", "source_head_verified: True",
                "working_tree_clean: True", "pc_candidate_ancestor_verified: True",
                "target_exists_ignored_untracked: True", "private_manifest_read: False",
                "private_manifest_modified: False", "execution_attempted: False"):
                stdout.write("v300_rt8d_" + line + "\n")
            return 0
        head, original, _ = _load_pc_transition(expected_source_head, root=root,
            git_output=git_output, git_ok=git_ok, target_probe=target_probe)
        if mode == "check_pc_transition":
            for line in ("operator_mode: check-pc-transition",
                "previous_manifest_stage_pc_windows: True", "pc_candidate_source_verified: True",
                "pc_candidate_ancestor_verified: True", "android_placeholder_verified: True",
                "private_manifest_read: True", "private_manifest_modified: False",
                "execution_attempted: False"):
                stdout.write("v300_rt8d_" + line + "\n")
            return 0
        if mode != "record_android": raise OperatorError("unsupported_mode")
        _confirm(stdin, stdout)
        _atomic_replace(root, original, _android_bytes(head), replace_func)
        for line in ("operator_mode: record-android", "confirmation_count: 9",
            "previous_pc_section_preserved: True", "android_candidate_source_recorded: True",
            "private_manifest_transitioned: True", "private_manifest_backup_created: False",
            "private_manifest_content_printed: False", "private_configuration_read: False",
            "execution_performed_by_runner: False"):
            stdout.write("v300_rt8d_" + line + "\n")
        return 0
    except OperatorError as exc:
        stderr.write(f"v300_rt8d_operator_error: {exc.code}\n"); return 3
    except (OSError, subprocess.SubprocessError, validator.ValidationError):
        stderr.write("v300_rt8d_operator_error: bounded_operation_failed\n"); return 3

def parse_args(argv=None):
    p=argparse.ArgumentParser(); m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--check-inert", action="store_true"); m.add_argument("--preflight", action="store_true")
    m.add_argument("--check-pc-transition", action="store_true"); m.add_argument("--record-android", action="store_true")
    p.add_argument("--expected-source-head"); return p.parse_args(argv)
def main(argv=None):
    a=parse_args(argv)
    mode="check_inert" if a.check_inert else "preflight" if a.preflight else "check_pc_transition" if a.check_pc_transition else "record_android"
    return run_operator(mode=mode, expected_source_head=a.expected_source_head)
if __name__ == "__main__": raise SystemExit(main())
