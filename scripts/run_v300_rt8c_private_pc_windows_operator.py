#!/usr/bin/env python3
"""Credential-free RT-8c PC Windows operator manifest recorder.

The default-safe ``--check-inert`` mode performs no Git inspection, private
manifest access, private configuration access, process startup, HTTP request,
provider call, TTS/playback action, VTube Studio action, or device operation.

``--preflight`` inspects only local Git metadata and the fixed ignored target
state. ``--record-pc-windows`` additionally accepts only nine fixed confirmation
tokens and creates one strict RT-8 schema-v2 PC manifest. It does not execute
Controls A-H itself and never prints a manifest path, manifest content, private
value, or operator-entered text.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable, TextIO

import validate_v300_rt8_private_operator_manifest as validator

ROOT = Path(__file__).resolve().parents[1]
RT8B1_BASELINE = "4815403d4c94b05551df03678e9c2c4e1dfe754e"
MANIFEST_RELATIVE = Path(
    "operator_evidence/v300_rt8_pc_android_realtime_acceptance.json"
)
EXPECTED_CONFIRMATIONS = (
    "PASS-PC-A",
    "PASS-PC-B",
    "PASS-PC-C",
    "PASS-PC-D",
    "PASS-PC-E",
    "PASS-PC-F",
    "PASS-PC-G",
    "PASS-PC-H",
    "ACCEPT-PC-WINDOWS",
)
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")

GitOutput = Callable[[tuple[str, ...], Path], str]
GitOk = Callable[[tuple[str, ...], Path], bool]


class OperatorError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class TargetState:
    ignored: bool
    exists: bool
    symlink: bool


def _default_git_output(args: tuple[str, ...], root: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout.strip()


def _default_git_ok(args: tuple[str, ...], root: Path) -> bool:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def _default_target_probe(root: Path, git_ok: GitOk) -> TargetState:
    target = root / MANIFEST_RELATIVE
    return TargetState(
        ignored=git_ok(("check-ignore", "--quiet", "--", MANIFEST_RELATIVE.as_posix()), root),
        exists=os.path.lexists(target),
        symlink=target.is_symlink(),
    )


def _validate_fixed_target_boundary(root: Path) -> Path:
    target = root / MANIFEST_RELATIVE
    operator_root = (root / "operator_evidence").resolve()
    resolved_parent = target.parent.resolve()
    try:
        resolved_parent.relative_to(operator_root)
    except ValueError as exc:
        raise OperatorError("target_boundary_invalid") from exc
    if target.name != "v300_rt8_pc_android_realtime_acceptance.json":
        raise OperatorError("target_boundary_invalid")
    return target


def preflight(
    expected_source_head: str,
    *,
    root: Path = ROOT,
    git_output: GitOutput = _default_git_output,
    git_ok: GitOk = _default_git_ok,
    target_probe: Callable[[Path, GitOk], TargetState] = _default_target_probe,
) -> str:
    if not SHA_RE.fullmatch(expected_source_head):
        raise OperatorError("expected_source_head_invalid")
    if expected_source_head == RT8B1_BASELINE:
        raise OperatorError("stage1_source_not_committed")

    branch = git_output(("branch", "--show-current"), root)
    head = git_output(("rev-parse", "HEAD"), root)
    origin_main = git_output(("rev-parse", "origin/main"), root)
    status = git_output(("status", "--porcelain"), root)

    if branch != "main":
        raise OperatorError("branch_not_main")
    if head != origin_main:
        raise OperatorError("origin_main_not_synchronized")
    if head != expected_source_head:
        raise OperatorError("expected_source_head_mismatch")
    if status:
        raise OperatorError("working_tree_not_clean")
    if not git_ok(("cat-file", "-e", f"{RT8B1_BASELINE}^{{commit}}"), root):
        raise OperatorError("rt8b1_commit_missing")
    if not git_ok(("merge-base", "--is-ancestor", RT8B1_BASELINE, head), root):
        raise OperatorError("rt8b1_not_ancestor")

    _validate_fixed_target_boundary(root)
    state = target_probe(root, git_ok)
    if not state.ignored:
        raise OperatorError("target_not_ignored")
    if state.symlink:
        raise OperatorError("target_is_symlink")
    if state.exists:
        raise OperatorError("target_already_exists")
    return head


def _read_confirmations(stdin: TextIO, stdout: TextIO) -> None:
    for index, expected in enumerate(EXPECTED_CONFIRMATIONS, start=1):
        stdout.write(f"v300_rt8c_confirmation_{index}_required: {expected}\n")
        stdout.flush()
        supplied = stdin.readline()
        if supplied == "" or supplied.strip() != expected:
            raise OperatorError("confirmation_rejected")


def _manifest_bytes(source_head: str) -> bytes:
    data = validator.expected_manifest_for_stage("pc_windows", pc_head=source_head)
    validator.validate_manifest_data(data, "pc-windows")
    raw = (json.dumps(data, indent=2, sort_keys=False) + "\n").encode("utf-8")
    if len(raw) > validator.MAX_MANIFEST_BYTES:
        raise OperatorError("generated_manifest_too_large")
    return raw


def _write_new_manifest(root: Path, raw: bytes) -> None:
    target = _validate_fixed_target_boundary(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise OperatorError("target_already_exists") from exc


def run_operator(
    *,
    mode: str,
    expected_source_head: str | None = None,
    root: Path = ROOT,
    stdin: TextIO = sys.stdin,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
    git_output: GitOutput = _default_git_output,
    git_ok: GitOk = _default_git_ok,
    target_probe: Callable[[Path, GitOk], TargetState] = _default_target_probe,
) -> int:
    try:
        if mode == "check_inert":
            stdout.write("v300_rt8c_operator_mode: inert-check\n")
            stdout.write("v300_rt8c_private_manifest_created: False\n")
            stdout.write("v300_rt8c_private_manifest_read: False\n")
            stdout.write("v300_rt8c_private_configuration_read: False\n")
            stdout.write("v300_rt8c_backend_started: False\n")
            stdout.write("v300_rt8c_flutter_started: False\n")
            stdout.write("v300_rt8c_http_attempted: False\n")
            stdout.write("v300_rt8c_provider_execution_attempted: False\n")
            stdout.write("v300_rt8c_network_execution_attempted: False\n")
            stdout.write("v300_rt8c_tts_playback_vts_attempted: False\n")
            return 0

        if expected_source_head is None:
            raise OperatorError("expected_source_head_required")
        head = preflight(
            expected_source_head,
            root=root,
            git_output=git_output,
            git_ok=git_ok,
            target_probe=target_probe,
        )
        if mode == "preflight":
            stdout.write("v300_rt8c_operator_mode: preflight\n")
            stdout.write("v300_rt8c_source_head_verified: True\n")
            stdout.write("v300_rt8c_working_tree_clean: True\n")
            stdout.write("v300_rt8c_target_ignored: True\n")
            stdout.write("v300_rt8c_private_manifest_created: False\n")
            stdout.write("v300_rt8c_private_manifest_read: False\n")
            stdout.write("v300_rt8c_execution_attempted: False\n")
            return 0
        if mode != "record_pc_windows":
            raise OperatorError("unsupported_mode")

        _read_confirmations(stdin, stdout)
        raw = _manifest_bytes(head)
        _write_new_manifest(root, raw)
        stdout.write("v300_rt8c_operator_mode: record-pc-windows\n")
        stdout.write("v300_rt8c_confirmation_count: 9\n")
        stdout.write("v300_rt8c_private_manifest_created: True\n")
        stdout.write("v300_rt8c_private_manifest_overwritten: False\n")
        stdout.write("v300_rt8c_private_manifest_content_printed: False\n")
        stdout.write("v300_rt8c_private_configuration_read: False\n")
        stdout.write("v300_rt8c_execution_performed_by_runner: False\n")
        return 0
    except OperatorError as exc:
        stderr.write(f"v300_rt8c_operator_error: {exc.code}\n")
        return 3
    except (OSError, subprocess.SubprocessError, validator.ValidationError):
        stderr.write("v300_rt8c_operator_error: bounded_operation_failed\n")
        return 3


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-inert", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--record-pc-windows", action="store_true")
    parser.add_argument("--expected-source-head")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.check_inert:
        mode = "check_inert"
    elif args.preflight:
        mode = "preflight"
    else:
        mode = "record_pc_windows"
    return run_operator(mode=mode, expected_source_head=args.expected_source_head)


if __name__ == "__main__":
    raise SystemExit(main())
