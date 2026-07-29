from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

DRC_HEAD = "cc5a970ed22e372fd41f08470d9526f7ee589f73"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"
EXPECTED = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt3d3_private_real_stt_operator_boundary.md",
    "scripts/check_v300_rt3d3_private_real_stt_operator_boundary.py",
    "backend/app/services/framework_voice_input_openai_real_operator.py",
    "backend/tests/test_framework_voice_input_openai_real_operator.py",
}


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
    ).stdout.rstrip("\r\n")


def changed_paths(repo: Path) -> set[str]:
    result: set[str] = set()
    for line in run(
        "git", "status", "--porcelain", "--untracked-files=all", cwd=repo
    ).splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        result.add(path.replace("\\", "/"))
    return result


def require(text: str, marker: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing marker: {marker}")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    if run("git", "rev-parse", "HEAD", cwd=repo) != DRC_HEAD:
        raise AssertionError("Unexpected DRC HEAD")
    if run("git", "rev-parse", "origin/main", cwd=repo) != DRC_HEAD:
        raise AssertionError("Unexpected DRC origin/main")
    if changed_paths(repo) != EXPECTED:
        raise AssertionError("RT-3d3 nine-file surface mismatch")

    fw = Path(os.environ["FRAMEWORK_ROOT"]).resolve()
    if run("git", "rev-parse", "HEAD", cwd=fw) != FW_HEAD:
        raise AssertionError("Unexpected FW HEAD")
    if run("git", "rev-list", "-n", "1", "v5.4.0", cwd=fw) != FW_HEAD:
        raise AssertionError("Unexpected FW tag")
    if run("git", "status", "--porcelain", "--untracked-files=all", cwd=fw):
        raise AssertionError("FW working tree is not clean")

    documents = (
        repo / "README.md",
        repo / "roadmap.md",
        repo / "tasklist.md",
        repo / "scripts/README.md",
        repo / "docs/DRC_v300_goal_checklist_small_commit.md",
        repo / "docs/v300_rt3d3_private_real_stt_operator_boundary.md",
    )
    markers = (
        "REAL_OPERATOR_EXECUTION_COMPLETED",
        "ACCEPTANCE_CANDIDATE",
        "Transport response status: 200",
        "Transcript nonempty: True",
        "Expected phrase match: True",
        "Staged artifact cleanup complete: True",
        "Provider payload exposed: False",
        "Private path exposed: False",
        "Raw audio exposed: False",
        "Transcript exposed: False",
        "Private operator evidence committed: False",
        "Explicit operator approval: PENDING",
        "Implementation commit: PENDING",
    )
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            require(text, marker)

    service = (
        repo / "backend/app/services/framework_voice_input_openai_real_operator.py"
    ).read_text(encoding="utf-8")

    # This source-only gate verifies the DRC/FW execution boundary. The
    # successful staged-artifact cleanup marker is an operator-run result
    # recorded in the public-safe documents above; it is not a service field.
    for marker in (
        "FrameworkVoiceInputOpenAIRealOperator",
        "FrameworkVoiceInputOpenAIRealExecutorAssembler",
        "private_credential_builder",
        "staging_store",
        "executor.execute",
    ):
        require(service, marker)

    for forbidden in (
        "import openai",
        "from openai",
        "OPENAI_API_KEY",
        "os.environ",
        "httpx.",
        "requests.",
        "urllib.",
    ):
        if forbidden in service:
            raise AssertionError(f"Forbidden service marker: {forbidden}")

    tests = (
        repo / "backend/tests/test_framework_voice_input_openai_real_operator.py"
    ).read_text(encoding="utf-8")
    if len(re.findall(r"(?m)^def test_", tests)) != 5:
        raise AssertionError("Focused RT-3d3 test count is not five")

    # Redaction contracts may be expressed in the operator service or its
    # focused tests. Do not require invented runtime-result field names.
    for marker in (
        "provider_payload_exposed",
        "private_path_exposed",
        "raw_audio_exposed",
        "transcript_exposed",
    ):
        if marker not in service and marker not in tests:
            raise AssertionError(
                f"Missing operator redaction contract marker: {marker}"
            )

    print("[OK] RT-3d3 post-execution public-safe synchronization gate passed")
    print(
        "v300_rt3d3_private_real_stt_operator_boundary_status: "
        "real-operator-execution-completed-acceptance-candidate"
    )
    print("v300_rt3d3_changed_surface: exact-nine-files")
    print("v300_rt3d3_fw_baseline: clean-v5.4.0")
    print("v300_rt3d3_cleanup_validation_source: public-safe-operator-result")
    print("v300_rt3d3_invented_service_cleanup_field_required: False")
    print("v300_rt3d3_private_evidence_committed: False")
    print("v300_rt3d3_explicit_operator_approval: pending")
    print("v300_rt3d3_implementation_commit: pending")
    print("v300_rt3d3_provider_execution_executed_by_gate: False")
    print("v300_rt3d3_credential_read_by_gate: False")
    print("v300_rt3d3_audio_read_by_gate: False")


if __name__ == "__main__":
    main()
