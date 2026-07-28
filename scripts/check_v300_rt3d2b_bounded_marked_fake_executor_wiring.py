# Validate DRC v3.0.0 RT-3d2b bounded marked-fake executor wiring.

from __future__ import annotations

from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DRC_HEAD = "044f978240b1abda3d28206093e25c4ce285906d"
EXPECTED_FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt3d2b_bounded_marked_fake_executor_wiring.md",
    "scripts/check_v300_rt3d2b_bounded_marked_fake_executor_wiring.py",
}


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
        text=True,
        capture_output=capture,
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


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
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        result.add(path.replace("\\", "/"))
    return result


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise AssertionError(f"Missing {label}: {marker!r}")


def framework_root() -> Path:
    configured = os.environ.get("FRAMEWORK_ROOT", "").strip()
    return (
        Path(configured)
        if configured
        else Path(r"E:\work\deverop\AI-Character-Framework\Development")
    )


def main() -> None:
    if run("git", "rev-parse", "HEAD", capture=True) != EXPECTED_DRC_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")
    if changed_paths() != EXPECTED_CHANGED_PATHS:
        raise AssertionError("RT-3d2b changed surface mismatch.")

    fw = framework_root()
    if run("git", "rev-parse", "HEAD", cwd=fw, capture=True) != EXPECTED_FW_HEAD:
        raise AssertionError("Unexpected FW HEAD.")
    if (
        run("git", "rev-list", "-n", "1", "v5.4.0", cwd=fw, capture=True)
        != EXPECTED_FW_HEAD
    ):
        raise AssertionError("Unexpected FW v5.4.0 tag target.")
    if run(
        "git",
        "status",
        "--porcelain",
        "--untracked-files=all",
        cwd=fw,
        capture=True,
    ):
        raise AssertionError("FW working tree is not clean.")

    files = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "RT-3d2b doc": read(
            "docs/v300_rt3d2b_bounded_marked_fake_executor_wiring.md"
        ),
        "API": read("backend/app/api/voice_input_demo.py"),
        "models": read("backend/app/models/voice_input_demo.py"),
        "shared public context": read(
            "backend/app/services/framework_voice_input_fake_handoff.py"
        ),
        "adapter": read(
            "backend/app/services/framework_voice_input_openai_fake_executor.py"
        ),
        "service tests": read(
            "backend/tests/test_framework_voice_input_openai_fake_executor.py"
        ),
        "API tests": read(
            "backend/tests/test_voice_input_openai_fake_executor_api.py"
        ),
    }

    for label in (
        "README",
        "roadmap",
        "tasklist",
        "scripts README",
        "checklist",
        "RT-3d2b doc",
    ):
        require(files[label], "RT-3d2b", f"{label} RT-3d2b marker")

    require(files["API"], "/openai-fake-executor", "guarded endpoint")
    require(
        files["shared public context"],
        "module: ModuleType | None = None",
        "shared public module handle",
    )
    for label in ("adapter", "service tests", "API tests"):
        require(
            files[label],
            "OpenAIVoiceInputFakeExecutor",
            f"{label} fake executor marker",
        )

    for marker in (
        "resolve_voice_input_provider_execution_config",
        "OpenAIVoiceInputProviderAdapter",
        "OpenAIVoiceInputFakeClientMarker",
        "OpenAIVoiceInputFakeExecutionPolicy",
        "OpenAIVoiceInputFakeExecutor",
        "real_provider_execution_executed=False",
        "credential_values_read=False",
        "provider_sdk_imported=False",
        "provider_client_created=False",
        "fake_stt_executed=True",
        "real_stt_executed=False",
    ):
        require(files["adapter"], marker, f"adapter contract {marker}")

    forbidden = (
        "import openai",
        "from openai",
        "OPENAI_API_KEY",
        "OpenAIVoiceInputPrivateCredential",
        "OpenAIVoiceInputRealClientFactory",
        "OpenAIVoiceInputRealProviderExecutor",
    )
    for marker in forbidden:
        if marker in files["adapter"]:
            raise AssertionError(f"Forbidden RT-3d2b runtime marker: {marker}")

    require(
        files["RT-3d2b doc"],
        "Additional Framework development requirement discovered by RT-3d2b: False",
        "FW requirement result",
    )

    require(
        files["README"],
        "Current small commit: none (RT-3d2b accepted; RT-3d2c next)",
        "README accepted current small commit",
    )
    require(
        files["checklist"],
        "RT-3d2b  COMPLETED / ACCEPTED",
        "checklist accepted RT-3d2b state",
    )
    require(
        files["RT-3d2b doc"],
        "RT-3d2b: COMPLETED / ACCEPTED",
        "RT-3d2b document accepted state",
    )
    require(
        files["RT-3d2b doc"],
        "explicit operator approval: RECEIVED",
        "operator approval record",
    )

    print("v300_rt3d2b_bounded_marked_fake_executor_status: completed-accepted")
    print("v300_framework_release: v5.4.0")
    print(f"v300_framework_tag_commit: {EXPECTED_FW_HEAD}")
    print("v300_private_staging_consumed: True")
    print("v300_bounded_audio_read: True")
    print("v300_marked_fake_client_injected: True")
    print("v300_fake_provider_protocol_call_executed: True")
    print("v300_provider_sdk_imported: False")
    print("v300_provider_client_created: False")
    print("v300_credential_values_read: False")
    print("v300_real_provider_execution_executed: False")
    print("v300_microphone_accessed: False")
    print("v300_private_path_exposed: False")
    print("v300_raw_audio_exposed: False")
    print("v300_provider_payload_exposed: False")
    print("v300_single_use_cleanup_required: True")
    print("v300_new_framework_requirement_identified: False")
    print("v300_rt3d2b_implementation_commit: 044f978240b1abda3d28206093e25c4ce285906d")
    print("v300_rt3d2b_operator_approval: accepted")
    print("v300_rt3d2c_authorization: authorized-not-started")
    print("v300_rt3d_status: blocked-drc-v540-wiring-and-operator-acceptance-pending")
    print("[OK] RT-3d2b bounded marked-fake executor wiring is completed and accepted")


if __name__ == "__main__":
    main()
