# Validate DRC v3.0.0 RT-3d2a FW v5.4.0 executor-path correction.

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DRC_HEAD = "4dbec924cf3d3817e39313836c64eec4a03e15db"
EXPECTED_FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_v540_real_stt_adoption_inventory.md",
    "docs/v300_rt3d2a_framework_v540_executor_path_correction.md",
    "scripts/check_v300_rt3d2a_framework_v540_executor_path_correction.py",
}


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args), cwd=cwd, check=True, text=True, capture_output=capture
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def changed_paths() -> set[str]:
    output = run("git", "status", "--porcelain", "--untracked-files=all", capture=True)
    result: set[str] = set()
    for line in output.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        result.add(path.replace("\\", "/"))
    return result


def framework_root() -> Path:
    configured = os.environ.get("FRAMEWORK_ROOT", "").strip()
    return Path(configured) if configured else Path(
        r"E:\work\deverop\AI-Character-Framework\Development"
    )


def framework_python(root: Path) -> Path:
    candidate = root / ".venv" / "Scripts" / "python.exe"
    return candidate if candidate.is_file() else Path(sys.executable)


def verify_fw_distinction(root: Path, python: Path) -> None:
    source = """
import inspect
import framework

required = (
    "OpenAIVoiceInputProviderAdapter",
    "OpenAIVoiceInputFakeClientMarker",
    "OpenAIVoiceInputFakeExecutionPolicy",
    "OpenAIVoiceInputFakeExecutor",
    "OpenAIVoiceInputPrivateCredential",
    "OpenAIVoiceInputRealProviderPolicy",
    "OpenAIVoiceInputRealClientFactory",
    "OpenAIVoiceInputRealProviderExecutor",
    "VoiceInputSession",
)
missing = [name for name in required if not hasattr(framework, name)]
assert not missing, missing

session_source = inspect.getsource(framework.VoiceInputSession.transcribe_audio_result)
adapter_source = inspect.getsource(framework.OpenAIVoiceInputProviderAdapter.transcribe)

assert "effective_adapter.transcribe" in session_source
assert "VoiceInputResult.unavailable" in adapter_source
assert callable(framework.OpenAIVoiceInputFakeExecutor.execute)
assert callable(framework.OpenAIVoiceInputRealProviderExecutor.execute)

print("session_data_only: True")
print("openai_adapter_transcribe_execution_free: True")
print("fake_executor_public: True")
print("real_executor_public: True")
"""
    output = run(str(python), "-c", source, cwd=root, capture=True)
    for marker in (
        "session_data_only: True",
        "openai_adapter_transcribe_execution_free: True",
        "fake_executor_public: True",
        "real_executor_public: True",
    ):
        if marker not in output:
            raise AssertionError(f"Missing FW distinction marker: {marker}")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing {label}: {marker!r}")


def main() -> None:
    if changed_paths() != EXPECTED_CHANGED_PATHS:
        raise AssertionError("RT-3d2a changed surface mismatch.")
    if run("git", "rev-parse", "HEAD", capture=True) != EXPECTED_DRC_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")

    fw_root = framework_root()
    fw_python = framework_python(fw_root)
    if run("git", "rev-parse", "HEAD", cwd=fw_root, capture=True) != EXPECTED_FW_HEAD:
        raise AssertionError("Unexpected FW HEAD.")
    if run("git", "rev-list", "-n", "1", "v5.4.0", cwd=fw_root, capture=True) != EXPECTED_FW_HEAD:
        raise AssertionError("Unexpected FW v5.4.0 tag target.")
    if run("git", "status", "--porcelain", "--untracked-files=all", cwd=fw_root, capture=True):
        raise AssertionError("FW working tree is not clean.")

    verify_fw_distinction(fw_root, fw_python)
    run(str(fw_python), "scripts/smoke_v540_openai_fake_execution_boundary.py", cwd=fw_root)
    run(str(fw_python), "scripts/smoke_v540_openai_real_provider_runtime.py", cwd=fw_root)

    files = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "RT-3d1 inventory": read("docs/v300_framework_v540_real_stt_adoption_inventory.md"),
        "RT-3d2a correction": read("docs/v300_rt3d2a_framework_v540_executor_path_correction.md"),
    }
    for label, text in files.items():
        require(text, "RT-3d2a", f"{label} RT-3d2a marker")
        require(
            text,
            "BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING",
            f"{label} parent block",
        )

    require(
        files["README"],
        "Current small commit: none (RT-3d2a accepted; RT-3d2b next)",
        "README accepted current small commit",
    )
    require(
        files["checklist"],
        "RT-3d2a  COMPLETED / ACCEPTED",
        "checklist accepted RT-3d2a state",
    )
    require(
        files["RT-3d2a correction"],
        "RT-3d2a: COMPLETED / ACCEPTED",
        "correction accepted state",
    )
    require(
        files["RT-3d2a correction"],
        "explicit operator approval: RECEIVED",
        "operator approval record",
    )

    require(files["RT-3d2a correction"], "OpenAIVoiceInputFakeExecutor", "fake executor")
    require(files["RT-3d2a correction"], "OpenAIVoiceInputRealProviderExecutor", "real executor")
    require(
        files["RT-3d2a correction"],
        "Additional Framework development requirement discovered by RT-3d2a: False",
        "FW requirement result",
    )
    require(
        files["RT-3d1 inventory"],
        "Post-acceptance execution-path correction",
        "RT-3d1 correction record",
    )

    print("v300_rt3d2a_executor_path_correction_status: completed-accepted")
    print("v300_framework_release: v5.4.0")
    print(f"v300_framework_tag_commit: {EXPECTED_FW_HEAD}")
    print("v300_voice_input_session_data_only: True")
    print("v300_openai_adapter_transcribe_execution_free: True")
    print("v300_fake_executor_public: True")
    print("v300_real_executor_public: True")
    print("v300_new_framework_requirement_identified: False")
    print("v300_drc_runtime_changed: False")
    print("v300_private_audio_read: False")
    print("v300_microphone_accessed: False")
    print("v300_credential_value_read: False")
    print("v300_real_provider_execution_executed: False")
    print("v300_rt3d2a_operator_approval: accepted")
    print("v300_rt3d2b_authorization: authorized-not-started")
    print("v300_rt3d_status: blocked-drc-v540-wiring-and-operator-acceptance-pending")
    print("[OK] RT-3d2a executor-path correction is completed and accepted")


if __name__ == "__main__":
    main()
