#!/usr/bin/env python3
"""Credential-free RT-8e aggregate-cleanup manifest transition runner."""

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
RT8D_ACCEPTANCE_SYNC_BASELINE = "84839efd6e381cb5a2c45022a7e8f7d9eafcb5df"
PC_ACCEPTED_SOURCE_HEAD = "fa39065130a4a4689c2e54195f231a5e79c62a35"
ANDROID_ACCEPTED_SOURCE_HEAD = "0e7fc6fc5922c293b8460fc816610d41c2a79e9a"
MANIFEST_RELATIVE = Path("operator_evidence/v300_rt8_pc_android_realtime_acceptance.json")
EXPECTED_CONFIRMATIONS = tuple(
    [f"PASS-AGGREGATE-{letter}" for letter in "ABCDEFGH"]
    + ["ACCEPT-RT8-AGGREGATE"]
)
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
    regular: bool
    temporary_exists: bool


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
    return (
        subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def _target(root: Path) -> Path:
    target = root / MANIFEST_RELATIVE
    operator_root = (root / "operator_evidence").resolve()
    try:
        target.parent.resolve().relative_to(operator_root)
    except ValueError as exc:
        raise OperatorError("target_boundary_invalid") from exc
    if target.name != "v300_rt8_pc_android_realtime_acceptance.json":
        raise OperatorError("target_boundary_invalid")
    return target


def _temporary_target(root: Path) -> Path:
    target = _target(root)
    return target.with_name(target.name + ".rt8e-transition.tmp")


def _default_target_probe(
    root: Path,
    git_ok: GitOk,
    git_output: GitOutput,
) -> TargetState:
    target = _target(root)
    temporary = _temporary_target(root)
    return TargetState(
        ignored=git_ok(
            ("check-ignore", "--quiet", "--", MANIFEST_RELATIVE.as_posix()), root
        ),
        exists=os.path.lexists(target),
        symlink=target.is_symlink(),
        tracked=bool(
            git_output(
                ("ls-files", "--cached", "--", MANIFEST_RELATIVE.as_posix()), root
            )
        ),
        regular=target.is_file(),
        temporary_exists=os.path.lexists(temporary),
    )


def preflight(
    expected_source_head: str,
    *,
    root: Path = ROOT,
    git_output: GitOutput = _default_git_output,
    git_ok: GitOk = _default_git_ok,
    target_probe: Callable[[Path, GitOk, GitOutput], TargetState] = _default_target_probe,
) -> str:
    if not SHA_RE.fullmatch(expected_source_head):
        raise OperatorError("expected_source_head_invalid")
    if expected_source_head == RT8D_ACCEPTANCE_SYNC_BASELINE:
        raise OperatorError("stage1_source_not_committed")

    branch = git_output(("branch", "--show-current"), root)
    head = git_output(("rev-parse", "HEAD"), root)
    origin = git_output(("rev-parse", "origin/main"), root)
    status = git_output(("status", "--porcelain"), root)

    if branch != "main":
        raise OperatorError("branch_not_main")
    if head != origin:
        raise OperatorError("origin_main_not_synchronized")
    if head != expected_source_head:
        raise OperatorError("expected_source_head_mismatch")
    if status:
        raise OperatorError("working_tree_not_clean")

    required_commits = (
        (
            RT8D_ACCEPTANCE_SYNC_BASELINE,
            "rt8d_acceptance_sync_commit_missing",
            "rt8d_acceptance_sync_not_ancestor",
        ),
        (
            PC_ACCEPTED_SOURCE_HEAD,
            "pc_candidate_commit_missing",
            "pc_candidate_not_ancestor",
        ),
        (
            ANDROID_ACCEPTED_SOURCE_HEAD,
            "android_candidate_commit_missing",
            "android_candidate_not_ancestor",
        ),
    )
    for commit, missing_code, ancestry_code in required_commits:
        if not git_ok(("cat-file", "-e", f"{commit}^{{commit}}"), root):
            raise OperatorError(missing_code)
        if not git_ok(("merge-base", "--is-ancestor", commit, head), root):
            raise OperatorError(ancestry_code)

    state = target_probe(root, git_ok, git_output)
    if not state.ignored:
        raise OperatorError("target_not_ignored")
    if not state.exists:
        raise OperatorError("target_missing")
    if state.symlink:
        raise OperatorError("target_is_symlink")
    if state.tracked:
        raise OperatorError("target_is_tracked")
    if not state.regular:
        raise OperatorError("target_not_regular")
    if state.temporary_exists:
        raise OperatorError("temporary_target_exists")
    return head


def _load_android_transition(
    expected_source_head: str,
    *,
    root: Path,
    git_output: GitOutput,
    git_ok: GitOk,
    target_probe: Callable[[Path, GitOk, GitOutput], TargetState],
) -> tuple[str, bytes, Mapping[str, object]]:
    head = preflight(
        expected_source_head,
        root=root,
        git_output=git_output,
        git_ok=git_ok,
        target_probe=target_probe,
    )
    try:
        raw = _target(root).read_bytes()
        data = validator.load_json_bytes(raw)
        validator.validate_manifest_data(data, "android")
    except (OSError, validator.ValidationError) as exc:
        raise OperatorError("android_transition_manifest_invalid") from exc

    if data.get("pc_windows_candidate_source_head") != PC_ACCEPTED_SOURCE_HEAD:
        raise OperatorError("pc_candidate_source_mismatch")
    if data.get("android_candidate_source_head") != ANDROID_ACCEPTED_SOURCE_HEAD:
        raise OperatorError("android_candidate_source_mismatch")

    aggregate = data.get("aggregate_cleanup")
    if not isinstance(aggregate, Mapping) or aggregate.get("status") != "not_run":
        raise OperatorError("aggregate_not_not_run")

    for commit, code in (
        (PC_ACCEPTED_SOURCE_HEAD, "pc_candidate_not_ancestor"),
        (ANDROID_ACCEPTED_SOURCE_HEAD, "android_candidate_not_ancestor"),
    ):
        if not git_ok(("merge-base", "--is-ancestor", commit, head), root):
            raise OperatorError(code)

    return head, raw, data


def _confirm(stdin: TextIO, stdout: TextIO) -> None:
    for index, expected in enumerate(EXPECTED_CONFIRMATIONS, 1):
        stdout.write(f"v300_rt8e_confirmation_{index}_required: {expected}\n")
        stdout.flush()
        supplied = stdin.readline()
        if supplied == "" or supplied.strip() != expected:
            raise OperatorError("confirmation_rejected")


def _aggregate_bytes() -> bytes:
    data = validator.expected_manifest_for_stage(
        "aggregate",
        pc_head=PC_ACCEPTED_SOURCE_HEAD,
        android_head=ANDROID_ACCEPTED_SOURCE_HEAD,
    )
    validator.validate_manifest_data(data, "aggregate")
    raw = (json.dumps(data, indent=2, sort_keys=False) + "\n").encode("utf-8")
    if len(raw) > validator.MAX_MANIFEST_BYTES:
        raise OperatorError("generated_manifest_too_large")
    return raw


def _atomic_replace(
    root: Path,
    original: bytes,
    new: bytes,
    replace_func: ReplaceFunc = os.replace,
) -> None:
    target = _target(root)
    temporary = _temporary_target(root)
    if os.path.lexists(temporary):
        raise OperatorError("temporary_target_exists")
    try:
        with temporary.open("xb") as handle:
            handle.write(new)
            handle.flush()
            os.fsync(handle.fileno())
        if target.read_bytes() != original:
            raise OperatorError("target_changed_during_transition")
        replace_func(temporary, target)
    finally:
        if os.path.lexists(temporary):
            temporary.unlink()


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
    target_probe: Callable[[Path, GitOk, GitOutput], TargetState] = _default_target_probe,
    replace_func: ReplaceFunc = os.replace,
) -> int:
    try:
        if mode == "check_inert":
            for line in (
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
                stdout.write("v300_rt8e_" + line + "\n")
            return 0

        if expected_source_head is None:
            raise OperatorError("expected_source_head_required")

        if mode == "preflight":
            preflight(
                expected_source_head,
                root=root,
                git_output=git_output,
                git_ok=git_ok,
                target_probe=target_probe,
            )
            for line in (
                "operator_mode: preflight",
                "source_head_verified: True",
                "working_tree_clean: True",
                "rt8d_acceptance_sync_ancestor_verified: True",
                "pc_candidate_ancestor_verified: True",
                "android_candidate_ancestor_verified: True",
                "target_exists_ignored_untracked_regular: True",
                "temporary_target_absent: True",
                "private_manifest_read: False",
                "private_manifest_modified: False",
                "execution_attempted: False",
            ):
                stdout.write("v300_rt8e_" + line + "\n")
            return 0

        _, original, previous = _load_android_transition(
            expected_source_head,
            root=root,
            git_output=git_output,
            git_ok=git_ok,
            target_probe=target_probe,
        )

        if mode == "check_android_transition":
            for line in (
                "operator_mode: check-android-transition",
                "previous_manifest_stage_android: True",
                "pc_candidate_source_verified: True",
                "android_candidate_source_verified: True",
                "both_candidate_ancestors_verified: True",
                "aggregate_not_run_verified: True",
                "private_manifest_read: True",
                "private_manifest_modified: False",
                "execution_attempted: False",
            ):
                stdout.write("v300_rt8e_" + line + "\n")
            return 0

        if mode != "record_aggregate":
            raise OperatorError("unsupported_mode")

        _confirm(stdin, stdout)
        new = _aggregate_bytes()
        expected_previous = validator.expected_manifest_for_stage(
            "android",
            pc_head=PC_ACCEPTED_SOURCE_HEAD,
            android_head=ANDROID_ACCEPTED_SOURCE_HEAD,
        )
        if previous != expected_previous:
            raise OperatorError("android_transition_manifest_invalid")
        _atomic_replace(root, original, new, replace_func)
        for line in (
            "operator_mode: record-aggregate",
            "confirmation_count: 9",
            "previous_pc_section_preserved: True",
            "previous_android_section_preserved: True",
            "aggregate_cleanup_recorded: True",
            "private_manifest_transitioned: True",
            "private_manifest_backup_created: False",
            "private_manifest_content_printed: False",
            "private_configuration_read: False",
            "cleanup_performed_by_runner: False",
            "execution_performed_by_runner: False",
            "rt9_implementation_authorized: False",
        ):
            stdout.write("v300_rt8e_" + line + "\n")
        return 0
    except OperatorError as exc:
        stderr.write(f"v300_rt8e_operator_error: {exc.code}\n")
        return 3
    except (OSError, subprocess.SubprocessError, validator.ValidationError):
        stderr.write("v300_rt8e_operator_error: bounded_operation_failed\n")
        return 3


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check-inert", action="store_true")
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--check-android-transition", action="store_true")
    modes.add_argument("--record-aggregate", action="store_true")
    parser.add_argument("--expected-source-head")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.check_inert:
        mode = "check_inert"
    elif args.preflight:
        mode = "preflight"
    elif args.check_android_transition:
        mode = "check_android_transition"
    else:
        mode = "record_aggregate"
    return run_operator(mode=mode, expected_source_head=args.expected_source_head)


if __name__ == "__main__":
    raise SystemExit(main())
