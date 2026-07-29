from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_COMMIT = "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
EXPECTED_FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_ACCEPTANCE_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt3d3_private_real_stt_operator_boundary.md",
    "scripts/check_v300_rt3d3_private_real_stt_operator_boundary.py",
}


def run(
    *args: str,
    cwd: Path = ROOT,
    capture: bool = False,
) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def changed_paths() -> set[str]:
    output = run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        capture=True,
    )
    result: set[str] = set()
    for line in output.splitlines():
        if not line:
            continue
        if len(line) < 4:
            raise AssertionError("Unexpected git status output.")
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        result.add(path.replace("\\", "/"))
    return result


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing {label}: {marker}")


def forbid(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"Forbidden {label}: {marker}")


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    matches = [index for index, line in enumerate(lines) if line == heading]
    if len(matches) != 1:
        raise AssertionError(
            f"Section heading {heading!r} count was {len(matches)}"
        )

    start = matches[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def validate_repository_mode() -> str:
    head = run("git", "rev-parse", "HEAD", capture=True)
    paths = changed_paths()

    if paths:
        if head != IMPLEMENTATION_COMMIT:
            raise AssertionError(
                "Uncommitted acceptance surface requires the implementation HEAD."
            )
        if paths != EXPECTED_ACCEPTANCE_PATHS:
            raise AssertionError(
                "RT-3d3 acceptance-only surface is not the exact seven files."
            )
        return "acceptance-working-tree"

    subprocess.run(
        (
            "git",
            "merge-base",
            "--is-ancestor",
            IMPLEMENTATION_COMMIT,
            head,
        ),
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if head == IMPLEMENTATION_COMMIT:
        raise AssertionError(
            "Clean implementation HEAD does not contain the acceptance-only state."
        )
    return "accepted-clean-tree"


def main() -> None:
    validation_mode = validate_repository_mode()

    fw_value = os.environ.get("FRAMEWORK_ROOT", "").strip()
    if not fw_value:
        raise AssertionError("FRAMEWORK_ROOT is required.")

    fw = Path(fw_value).resolve()
    if (
        run("git", "rev-parse", "HEAD", cwd=fw, capture=True)
        != EXPECTED_FW_HEAD
    ):
        raise AssertionError("Unexpected FW HEAD.")
    if (
        run("git", "rev-list", "-n", "1", "v5.4.0", cwd=fw, capture=True)
        != EXPECTED_FW_HEAD
    ):
        raise AssertionError("Unexpected FW v5.4.0 tag.")
    if run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        cwd=fw,
        capture=True,
    ):
        raise AssertionError("FW working tree is not clean.")

    docs = {
        "README": (ROOT / "README.md").read_text(encoding="utf-8"),
        "roadmap": (ROOT / "roadmap.md").read_text(encoding="utf-8"),
        "tasklist": (ROOT / "tasklist.md").read_text(encoding="utf-8"),
        "scripts README": (ROOT / "scripts/README.md").read_text(
            encoding="utf-8"
        ),
        "checklist": (
            ROOT / "docs/DRC_v300_goal_checklist_small_commit.md"
        ).read_text(encoding="utf-8"),
        "boundary": (
            ROOT / "docs/v300_rt3d3_private_real_stt_operator_boundary.md"
        ).read_text(encoding="utf-8"),
    }

    common_markers = (
        "RT-3d3",
        "COMPLETED / ACCEPTED",
        (
            "Implementation commit: "
            "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
        ),
        "Explicit operator approval: ACCEPTED",
        "Private operator evidence committed: False",
    )
    for label, text in docs.items():
        for marker in common_markers:
            require(text, marker, f"{label} accepted marker")

    readme_current = "\n".join(docs["README"].splitlines()[:100])
    for marker in (
        "Current small commit: none (RT-3d3 accepted; RT-4 next)",
        "Completed small commit: RT-3d3 (**COMPLETED / ACCEPTED**)",
        "Next realtime phase: RT-4 (**NEXT / NOT_STARTED**)",
        (
            "Next realtime action: define the RT-4 streaming/cancel "
            "small-commit boundary (**NOT_STARTED**)"
        ),
        "RT-3  COMPLETED / ACCEPTED",
        "RT-3d  COMPLETED / ACCEPTED",
        "RT-3d2  COMPLETED / ACCEPTED",
        "RT-3d3  COMPLETED / ACCEPTED",
    ):
        require(readme_current, marker, "README current accepted state")

    for marker in (
        "ACCEPTANCE_CANDIDATE",
        "COMMIT_PENDING",
        "PENDING_APPROVAL",
        "PENDING OPERATOR OPT-IN",
    ):
        forbid(readme_current, marker, "README stale current state")

    readme_checkpoint = section(
        docs["README"],
        "## v3.0.0 RT-3d3 real operator execution checkpoint",
    )
    for marker in (
        "RT-3d3: COMPLETED / ACCEPTED",
        "RT-3d2: COMPLETED / ACCEPTED",
        "RT-3d: COMPLETED / ACCEPTED",
        "Explicit operator approval: ACCEPTED",
        (
            "Implementation commit: "
            "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
        ),
        "The accepted run used",
    ):
        require(readme_checkpoint, marker, "README RT-3d3 checkpoint")
    for marker in ("candidate", "PENDING"):
        forbid(readme_checkpoint, marker, "README stale checkpoint state")

    checklist_current = "\n".join(docs["checklist"].splitlines()[:30])
    for marker in (
        (
            "Current parent phase: RT-3 COMPLETED / ACCEPTED; "
            "RT-4 NEXT / NOT_STARTED"
        ),
        "Current implementation state: COMPLETED / ACCEPTED",
        "Completed small commit: RT-3d3 COMPLETED / ACCEPTED",
    ):
        require(checklist_current, marker, "checklist current accepted state")

    checklist_section = section(
        docs["checklist"],
        "## RT-3d3 - private real-STT operator boundary",
    )
    for marker in (
        "RT-3d3  COMPLETED / ACCEPTED",
        "RT-3d2  COMPLETED / ACCEPTED",
        "RT-3d   COMPLETED / ACCEPTED",
        "RT-3d3 accepted: True",
        "Explicit operator approval: ACCEPTED",
        (
            "Implementation commit: "
            "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
        ),
    ):
        require(checklist_section, marker, "checklist RT-3d3 accepted state")
    for marker in ("acceptance candidate", "PENDING"):
        forbid(checklist_section, marker, "checklist stale RT-3d3 state")

    boundary_prefix = "\n".join(docs["boundary"].splitlines()[:45])
    for marker in (
        "RT-3d3: COMPLETED / ACCEPTED",
        "RT-3d2: COMPLETED / ACCEPTED",
        "RT-3d: COMPLETED / ACCEPTED",
        "Private operator acceptance: ACCEPTED",
        "Explicit operator approval: ACCEPTED",
        (
            "Implementation commit: "
            "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
        ),
    ):
        require(boundary_prefix, marker, "boundary accepted state")
    for marker in ("acceptance candidate", "PENDING"):
        forbid(boundary_prefix, marker, "boundary stale accepted state")

    for label, heading in (
        ("roadmap", "## RT-3d3 real operator execution checkpoint"),
        ("tasklist", "## RT-3d3 real operator execution checkpoint"),
        ("scripts README", "## RT-3d3 real operator execution checkpoint"),
    ):
        checkpoint = section(docs[label], heading)
        for marker in (
            "RT-3d3: COMPLETED / ACCEPTED",
            "RT-3d2: COMPLETED / ACCEPTED",
            "RT-3d: COMPLETED / ACCEPTED",
            "Explicit operator approval: ACCEPTED",
            (
                "Implementation commit: "
                "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
            ),
        ):
            require(checkpoint, marker, f"{label} accepted checkpoint")
        for marker in ("ACCEPTANCE_CANDIDATE", "PENDING_APPROVAL"):
            forbid(checkpoint, marker, f"{label} stale checkpoint")

    service = (
        ROOT
        / "backend/app/services/framework_voice_input_openai_real_operator.py"
    ).read_text(encoding="utf-8")
    tests = (
        ROOT
        / "backend/tests/test_framework_voice_input_openai_real_operator.py"
    ).read_text(encoding="utf-8")

    for marker in (
        "FrameworkVoiceInputOpenAIRealOperator",
        "FrameworkVoiceInputOpenAIRealExecutorAssembler",
        "private_credential_builder",
        "staging_store",
        "executor.execute",
    ):
        require(service, marker, "committed operator boundary")

    for marker in (
        "import openai",
        "from openai",
        "OPENAI_API_KEY",
        "httpx.",
        "requests.",
        "urllib.",
    ):
        forbid(service, marker, "direct provider/network bypass")

    if len(re.findall(r"(?m)^def test_", tests)) != 5:
        raise AssertionError("Focused RT-3d3 test count is not five.")

    print("[OK] RT-3d3 acceptance gate passed")
    print(f"v300_rt3d3_acceptance_validation_mode: {validation_mode}")
    print("v300_rt3d3_acceptance_status: completed-accepted")
    print("v300_rt3d2_status: completed-accepted")
    print("v300_rt3d_status: completed-accepted")
    print("v300_rt3_status: completed-accepted")
    print(
        "v300_rt3d3_implementation_commit: "
        "5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c"
    )
    print("v300_rt3d3_operator_approval: accepted")
    print("v300_rt4_status: next-not-started")
    print("v300_rt3d3_private_evidence_committed: False")
    print("v300_rt3d3_provider_execution_executed_by_gate: False")
    print("v300_rt3d3_credential_read_by_gate: False")
    print("v300_rt3d3_audio_read_by_gate: False")
    print("v300_rt3d3_commit_performed_by_gate: False")
    print("v300_rt3d3_push_performed_by_gate: False")


if __name__ == "__main__":
    main()
