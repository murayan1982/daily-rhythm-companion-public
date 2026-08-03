"""Credential-free tests for the inert-by-default RT-8c PC runner."""

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

import run_v300_rt8c_private_pc_windows_operator as runner
import validate_v300_rt8_private_operator_manifest as validator

STAGE1_SHA = "a" * 40


class FakeGit:
    def __init__(self, *, head: str = STAGE1_SHA, status: str = "") -> None:
        self.head = head
        self.status = status

    def output(self, args: tuple[str, ...], root: Path) -> str:
        del root
        table = {
            ("branch", "--show-current"): "main",
            ("rev-parse", "HEAD"): self.head,
            ("rev-parse", "origin/main"): self.head,
            ("status", "--porcelain"): self.status,
        }
        return table[args]

    def ok(self, args: tuple[str, ...], root: Path) -> bool:
        del root
        return args[0] in {"cat-file", "merge-base", "check-ignore"}


def clean_target(root: Path, git_ok: runner.GitOk) -> runner.TargetState:
    del root, git_ok
    return runner.TargetState(ignored=True, exists=False, symlink=False)


def confirmations() -> io.StringIO:
    return io.StringIO("\n".join(runner.EXPECTED_CONFIRMATIONS) + "\n")


def test_inert_mode_performs_no_write_read_or_execution(tmp_path: Path) -> None:
    stdout = io.StringIO()
    code = runner.run_operator(mode="check_inert", root=tmp_path, stdout=stdout, stderr=io.StringIO())
    assert code == 0
    assert not (tmp_path / runner.MANIFEST_RELATIVE).exists()
    output = stdout.getvalue()
    assert "private_manifest_created: False" in output
    assert "private_manifest_read: False" in output
    assert "execution_attempted: False" in output


def test_preflight_accepts_clean_synthetic_main_state(tmp_path: Path) -> None:
    fake = FakeGit()
    stdout = io.StringIO()
    code = runner.run_operator(
        mode="preflight",
        expected_source_head=STAGE1_SHA,
        root=tmp_path,
        stdout=stdout,
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 0
    assert "source_head_verified: True" in stdout.getvalue()


def test_wrong_expected_head_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    stderr = io.StringIO()
    code = runner.run_operator(
        mode="preflight",
        expected_source_head="b" * 40,
        root=tmp_path,
        stdout=io.StringIO(),
        stderr=stderr,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 3
    assert stderr.getvalue() == "v300_rt8c_operator_error: expected_source_head_mismatch\n"


def test_dirty_tracked_tree_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit(status=" M README.md")
    stderr = io.StringIO()
    code = runner.run_operator(
        mode="preflight",
        expected_source_head=STAGE1_SHA,
        root=tmp_path,
        stdout=io.StringIO(),
        stderr=stderr,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 3
    assert "working_tree_not_clean" in stderr.getvalue()


def test_target_is_fixed_inside_operator_evidence(tmp_path: Path) -> None:
    target = runner._validate_fixed_target_boundary(tmp_path)
    assert target.relative_to(tmp_path).as_posix() == runner.MANIFEST_RELATIVE.as_posix()
    assert target.parent.name == "operator_evidence"


def test_nonignored_target_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    state = lambda root, git_ok: runner.TargetState(False, False, False)
    with pytest.raises(runner.OperatorError) as exc:
        runner.preflight(STAGE1_SHA, root=tmp_path, git_output=fake.output, git_ok=fake.ok, target_probe=state)
    assert exc.value.code == "target_not_ignored"


def test_existing_target_is_rejected_without_reading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeGit()
    target = tmp_path / runner.MANIFEST_RELATIVE
    target.parent.mkdir()
    target.write_bytes(b"private-bytes-must-not-be-read")
    monkeypatch.setattr(Path, "read_bytes", lambda self: (_ for _ in ()).throw(AssertionError("read forbidden")))
    state = lambda root, git_ok: runner.TargetState(True, True, False)
    with pytest.raises(runner.OperatorError) as exc:
        runner.preflight(STAGE1_SHA, root=tmp_path, git_output=fake.output, git_ok=fake.ok, target_probe=state)
    assert exc.value.code == "target_already_exists"


def test_symlink_target_is_rejected(tmp_path: Path) -> None:
    fake = FakeGit()
    state = lambda root, git_ok: runner.TargetState(True, True, True)
    with pytest.raises(runner.OperatorError) as exc:
        runner.preflight(STAGE1_SHA, root=tmp_path, git_output=fake.output, git_ok=fake.ok, target_probe=state)
    assert exc.value.code == "target_is_symlink"


def test_incorrect_confirmation_creates_no_file(tmp_path: Path) -> None:
    fake = FakeGit()
    stderr = io.StringIO()
    code = runner.run_operator(
        mode="record_pc_windows",
        expected_source_head=STAGE1_SHA,
        root=tmp_path,
        stdin=io.StringIO("WRONG\n"),
        stdout=io.StringIO(),
        stderr=stderr,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 3
    assert not (tmp_path / runner.MANIFEST_RELATIVE).exists()
    assert stderr.getvalue() == "v300_rt8c_operator_error: confirmation_rejected\n"


def test_successful_confirmation_writes_exact_pc_manifest(tmp_path: Path) -> None:
    fake = FakeGit()
    code = runner.run_operator(
        mode="record_pc_windows",
        expected_source_head=STAGE1_SHA,
        root=tmp_path,
        stdin=confirmations(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 0
    data = json.loads((tmp_path / runner.MANIFEST_RELATIVE).read_text(encoding="utf-8"))
    assert data == validator.expected_manifest_for_stage("pc_windows", pc_head=STAGE1_SHA)


def test_generated_manifest_passes_strict_schema_v2(tmp_path: Path) -> None:
    fake = FakeGit()
    code = runner.run_operator(
        mode="record_pc_windows",
        expected_source_head=STAGE1_SHA,
        root=tmp_path,
        stdin=confirmations(),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 0
    raw = (tmp_path / runner.MANIFEST_RELATIVE).read_bytes()
    data = validator.load_json_bytes(raw)
    validator.validate_manifest_data(data, "pc-windows")
    assert data["schema_version"] == "drc.v3.rt8-platform-acceptance.2"


def test_output_never_echoes_private_input_path_or_manifest_content(tmp_path: Path) -> None:
    fake = FakeGit()
    private_input = r"C:\\Users\\private\\secret-token-value"
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = runner.run_operator(
        mode="record_pc_windows",
        expected_source_head=STAGE1_SHA,
        root=tmp_path,
        stdin=io.StringIO(private_input + "\n"),
        stdout=stdout,
        stderr=stderr,
        git_output=fake.output,
        git_ok=fake.ok,
        target_probe=clean_target,
    )
    assert code == 3
    rendered = stdout.getvalue() + stderr.getvalue()
    assert private_input not in rendered
    assert str(tmp_path) not in rendered
    assert "operator_evidence" not in rendered
    assert "schema_version" not in rendered
