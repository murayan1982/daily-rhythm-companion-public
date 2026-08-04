"""Credential-free tests for RT-8e private aggregate-cleanup tooling."""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_v300_rt8e_private_aggregate_cleanup as runner
import validate_v300_rt8_private_operator_manifest as validator

AGGREGATE_HEAD = "a" * 40


class FakeGit:
    def __init__(
        self,
        *,
        head: str = AGGREGATE_HEAD,
        status: str = "",
        missing: set[str] | None = None,
        nonancestors: set[str] | None = None,
    ) -> None:
        self.head = head
        self.status = status
        self.missing = missing or set()
        self.nonancestors = nonancestors or set()

    def output(self, args: tuple[str, ...], root: Path) -> str:
        del root
        values = {
            ("branch", "--show-current"): "main",
            ("rev-parse", "HEAD"): self.head,
            ("rev-parse", "origin/main"): self.head,
            ("status", "--porcelain"): self.status,
            ("ls-files", "--cached", "--", runner.MANIFEST_RELATIVE.as_posix()): "",
        }
        return values[args]

    def ok(self, args: tuple[str, ...], root: Path) -> bool:
        del root
        if args[0] == "cat-file":
            return args[2].removesuffix("^{commit}") not in self.missing
        if args[0] == "merge-base":
            return args[2] not in self.nonancestors
        return args[0] == "check-ignore"


def good_target(root: Path, git_ok, git_output) -> runner.TargetState:
    del root, git_ok, git_output
    return runner.TargetState(True, True, False, False, True, False)


def confirmations() -> io.StringIO:
    return io.StringIO("\n".join(runner.EXPECTED_CONFIRMATIONS) + "\n")


def write_android(root: Path, *, pc: str | None = None, android: str | None = None):
    target = root / runner.MANIFEST_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    data = validator.expected_manifest_for_stage(
        "android",
        pc_head=pc or runner.PC_ACCEPTED_SOURCE_HEAD,
        android_head=android or runner.ANDROID_ACCEPTED_SOURCE_HEAD,
    )
    target.write_text(json.dumps(data) + "\n", encoding="utf-8")
    return data


def test_inert_mode_performs_no_access_write_or_execution(tmp_path: Path) -> None:
    stdout = io.StringIO()
    assert runner.run_operator(
        mode="check_inert", root=tmp_path, stdout=stdout, stderr=io.StringIO()
    ) == 0
    rendered = stdout.getvalue()
    assert "private_manifest_read: False" in rendered
    assert "private_cleanup_performed: False" in rendered


def test_clean_committed_source_preflight_passes(tmp_path: Path) -> None:
    fake = FakeGit()
    assert runner.preflight(
        AGGREGATE_HEAD,
        root=tmp_path,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
    ) == AGGREGATE_HEAD


def test_wrong_expected_head_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    with pytest.raises(runner.OperatorError) as error:
        runner.preflight(
            "b" * 40,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=good_target,
        )
    assert error.value.code == "expected_source_head_mismatch"


def test_dirty_tree_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit(status=" M README.md")
    with pytest.raises(runner.OperatorError) as error:
        runner.preflight(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=good_target,
        )
    assert error.value.code == "working_tree_not_clean"


def test_rt8d_acceptance_sync_ancestry_is_required(tmp_path: Path) -> None:
    fake = FakeGit(nonancestors={runner.RT8D_ACCEPTANCE_SYNC_BASELINE})
    with pytest.raises(runner.OperatorError) as error:
        runner.preflight(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=good_target,
        )
    assert error.value.code == "rt8d_acceptance_sync_not_ancestor"


def test_pc_and_android_candidate_ancestry_is_required(tmp_path: Path) -> None:
    for commit, expected in (
        (runner.PC_ACCEPTED_SOURCE_HEAD, "pc_candidate_not_ancestor"),
        (runner.ANDROID_ACCEPTED_SOURCE_HEAD, "android_candidate_not_ancestor"),
    ):
        fake = FakeGit(nonancestors={commit})
        with pytest.raises(runner.OperatorError) as error:
            runner.preflight(
                AGGREGATE_HEAD,
                root=tmp_path,
                git_output=fake.output,
                git_ok=fake.ok,
                target_probe=good_target,
            )
        assert error.value.code == expected


def test_missing_manifest_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    state = lambda root, ok, output: runner.TargetState(True, False, False, False, False, False)
    with pytest.raises(runner.OperatorError) as error:
        runner.preflight(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=state,
        )
    assert error.value.code == "target_missing"


def test_nonignored_manifest_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    state = lambda root, ok, output: runner.TargetState(False, True, False, False, True, False)
    with pytest.raises(runner.OperatorError) as error:
        runner.preflight(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=state,
        )
    assert error.value.code == "target_not_ignored"


def test_symlink_tracked_or_nonregular_manifest_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    cases = (
        (runner.TargetState(True, True, True, False, True, False), "target_is_symlink"),
        (runner.TargetState(True, True, False, True, True, False), "target_is_tracked"),
        (runner.TargetState(True, True, False, False, False, False), "target_not_regular"),
        (runner.TargetState(True, True, False, False, True, True), "temporary_target_exists"),
    )
    for state_value, expected in cases:
        with pytest.raises(runner.OperatorError) as error:
            runner.preflight(
                AGGREGATE_HEAD,
                root=tmp_path,
                git_output=fake.output,
                git_ok=fake.ok,
                target_probe=lambda root, ok, output, value=state_value: value,
            )
        assert error.value.code == expected


def test_valid_android_transition_check_passes(tmp_path: Path) -> None:
    write_android(tmp_path)
    fake = FakeGit()
    head, raw, data = runner._load_android_transition(
        AGGREGATE_HEAD,
        root=tmp_path,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
    )
    assert head == AGGREGATE_HEAD
    assert raw
    assert data["stage"] == "android"


def test_wrong_previous_stage_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / runner.MANIFEST_RELATIVE
    target.parent.mkdir(parents=True)
    aggregate = validator.expected_manifest_for_stage(
        "aggregate",
        pc_head=runner.PC_ACCEPTED_SOURCE_HEAD,
        android_head=runner.ANDROID_ACCEPTED_SOURCE_HEAD,
    )
    target.write_text(json.dumps(aggregate), encoding="utf-8")
    fake = FakeGit()
    with pytest.raises(runner.OperatorError) as error:
        runner._load_android_transition(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=good_target,
        )
    assert error.value.code == "android_transition_manifest_invalid"


def test_wrong_pc_candidate_source_is_rejected(tmp_path: Path) -> None:
    write_android(tmp_path, pc="c" * 40)
    fake = FakeGit()
    with pytest.raises(runner.OperatorError) as error:
        runner._load_android_transition(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=good_target,
        )
    assert error.value.code == "pc_candidate_source_mismatch"


def test_wrong_android_candidate_source_is_rejected(tmp_path: Path) -> None:
    write_android(tmp_path, android="d" * 40)
    fake = FakeGit()
    with pytest.raises(runner.OperatorError) as error:
        runner._load_android_transition(
            AGGREGATE_HEAD,
            root=tmp_path,
            git_output=fake.output,
            git_ok=fake.ok,
            target_probe=good_target,
        )
    assert error.value.code == "android_candidate_source_mismatch"


def test_already_aggregate_manifest_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / runner.MANIFEST_RELATIVE
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps(
            validator.expected_manifest_for_stage(
                "aggregate",
                pc_head=runner.PC_ACCEPTED_SOURCE_HEAD,
                android_head=runner.ANDROID_ACCEPTED_SOURCE_HEAD,
            )
        ),
        encoding="utf-8",
    )
    fake = FakeGit()
    code = runner.run_operator(
        mode="record_aggregate",
        expected_source_head=AGGREGATE_HEAD,
        root=tmp_path,
        stdin=confirmations(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
    )
    assert code == 3


def test_wrong_confirmation_creates_no_update(tmp_path: Path) -> None:
    write_android(tmp_path)
    target = tmp_path / runner.MANIFEST_RELATIVE
    before = target.read_bytes()
    fake = FakeGit()
    code = runner.run_operator(
        mode="record_aggregate",
        expected_source_head=AGGREGATE_HEAD,
        root=tmp_path,
        stdin=io.StringIO("WRONG\n"),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
    )
    assert code == 3
    assert target.read_bytes() == before


def test_successful_transition_creates_exact_aggregate_manifest(tmp_path: Path) -> None:
    write_android(tmp_path)
    fake = FakeGit()
    assert runner.run_operator(
        mode="record_aggregate",
        expected_source_head=AGGREGATE_HEAD,
        root=tmp_path,
        stdin=confirmations(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
    ) == 0
    actual = json.loads((tmp_path / runner.MANIFEST_RELATIVE).read_text(encoding="utf-8"))
    expected = validator.expected_manifest_for_stage(
        "aggregate",
        pc_head=runner.PC_ACCEPTED_SOURCE_HEAD,
        android_head=runner.ANDROID_ACCEPTED_SOURCE_HEAD,
    )
    assert actual == expected


def test_pc_and_android_sections_remain_structurally_equal(tmp_path: Path) -> None:
    old = write_android(tmp_path)
    fake = FakeGit()
    assert runner.run_operator(
        mode="record_aggregate",
        expected_source_head=AGGREGATE_HEAD,
        root=tmp_path,
        stdin=confirmations(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
    ) == 0
    new = json.loads((tmp_path / runner.MANIFEST_RELATIVE).read_text(encoding="utf-8"))
    assert new["pc_windows"] == old["pc_windows"]
    assert new["android"] == old["android"]


def test_atomic_failure_preserves_original_and_output_leaks_no_private_data(tmp_path: Path) -> None:
    write_android(tmp_path)
    target = tmp_path / runner.MANIFEST_RELATIVE
    before = target.read_bytes()
    fake = FakeGit()

    def fail_replace(source, destination) -> None:
        del source, destination
        raise OSError("synthetic-private-detail")

    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        mode="record_aggregate",
        expected_source_head=AGGREGATE_HEAD,
        root=tmp_path,
        stdin=confirmations(),
        stdout=stdout,
        stderr=stderr,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=good_target,
        replace_func=fail_replace,
    )
    rendered = stdout.getvalue() + stderr.getvalue()
    assert code == 3
    assert target.read_bytes() == before
    assert not target.with_name(target.name + ".rt8e-transition.tmp").exists()
    assert str(tmp_path) not in rendered
    assert "synthetic-private-detail" not in rendered
    assert "schema_version" not in rendered
    assert "operator_evidence" not in rendered
