# Validate DRC v3.0.0 RT-3d2c guarded real-executor assembly contract.

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DRC_HEAD = "daf4eb058fb1137f60e637ffe7c621abbe85f261"
EXPECTED_FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"

EXPECTED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_rt3d2c_guarded_real_executor_assembly_contract.md",
    "scripts/check_v300_rt3d2c_guarded_real_executor_assembly_contract.py",
    "backend/app/services/framework_voice_input_openai_real_executor_assembly.py",
    "backend/tests/test_framework_voice_input_openai_real_executor_assembly.py",
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


def reject(text: str, marker: str, label: str) -> None:
    if marker in text:
        raise AssertionError(f"Forbidden {label}: {marker!r}")


def framework_root() -> Path:
    configured = os.environ.get("FRAMEWORK_ROOT", "").strip()
    return (
        Path(configured)
        if configured
        else Path(r"E:\work\deverop\AI-Character-Framework\Development")
    )


def framework_python(root: Path) -> Path:
    candidate = root / ".venv" / "Scripts" / "python.exe"
    return candidate if candidate.is_file() else Path(sys.executable)


def verify_fw_public_real_assembly_contract(root: Path, python: Path) -> None:
    source = """
import sys
import framework

required = (
    "resolve_voice_input_provider_execution_config",
    "OpenAIVoiceInputPrivateCredential",
    "OpenAIVoiceInputRealProviderPolicy",
    "OpenAIVoiceInputRuntimeMode",
    "OpenAIVoiceInputRealClientFactory",
    "OpenAIVoiceInputProviderAdapter",
    "OpenAIVoiceInputRealProviderExecutor",
)
missing = [name for name in required if not hasattr(framework, name)]
assert not missing, missing
assert "openai" not in sys.modules
assert callable(framework.resolve_voice_input_provider_execution_config)
assert callable(framework.OpenAIVoiceInputRealClientFactory)
assert callable(framework.OpenAIVoiceInputRealProviderExecutor)
print("fw_public_real_assembly_contract: True")
print("fw_openai_sdk_imported_by_public_contract_check: False")
"""
    output = run(str(python), "-c", source, cwd=root, capture=True)
    for marker in (
        "fw_public_real_assembly_contract: True",
        "fw_openai_sdk_imported_by_public_contract_check: False",
    ):
        if marker not in output:
            raise AssertionError(f"Missing FW public-contract marker: {marker}")


def main() -> None:
    if run("git", "rev-parse", "HEAD", capture=True) != EXPECTED_DRC_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")
    if changed_paths() != EXPECTED_CHANGED_PATHS:
        raise AssertionError("RT-3d2c changed surface mismatch.")

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

    verify_fw_public_real_assembly_contract(fw, framework_python(fw))

    files = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "RT-3d2c doc": read(
            "docs/v300_rt3d2c_guarded_real_executor_assembly_contract.md"
        ),
        "service": read(
            "backend/app/services/"
            "framework_voice_input_openai_real_executor_assembly.py"
        ),
        "tests": read(
            "backend/tests/"
            "test_framework_voice_input_openai_real_executor_assembly.py"
        ),
    }

    for label in (
        "README",
        "roadmap",
        "tasklist",
        "scripts README",
        "checklist",
        "RT-3d2c doc",
    ):
        require(files[label], "RT-3d2c", f"{label} RT-3d2c marker")
        require(
            files[label],
            "BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING",
            f"{label} parent block",
        )

    require(
        files["README"],
        "Current small commit: RT-3d2c (**IMPLEMENTED / NOT_ACCEPTED**)",
        "README implementation state",
    )
    require(
        files["checklist"],
        "RT-3d2c  IMPLEMENTED / NOT_ACCEPTED",
        "checklist implementation state",
    )
    require(
        files["RT-3d2c doc"],
        "RT-3d2c: IMPLEMENTED / NOT_ACCEPTED",
        "RT-3d2c document state",
    )
    require(
        files["RT-3d2c doc"],
        "Additional Framework development requirement discovered by RT-3d2c: False",
        "Framework requirement result",
    )

    service = files["service"]
    tests = files["tests"]

    required_service_markers = (
        "FrameworkVoiceInputOpenAIRealExecutorAssemblyRequest",
        "FrameworkVoiceInputOpenAIRealExecutorAssembly",
        "FrameworkVoiceInputOpenAIRealExecutorAssembler",
        "resolve_voice_input_provider_execution_config",
        "OpenAIVoiceInputPrivateCredential",
        "OpenAIVoiceInputRealProviderPolicy",
        "OpenAIVoiceInputRuntimeMode.REAL",
        "OpenAIVoiceInputRealClientFactory",
        "OpenAIVoiceInputProviderAdapter",
        "OpenAIVoiceInputRealProviderExecutor",
        "private_credential_builder(credential_type)",
        "operator_handoff_only=True",
        "explicit_opt_in_complete=True",
        "credential_object_injected=True",
        "credential_value_read_by_drc=False",
        "provider_sdk_imported=False",
        "provider_client_created=False",
        "network_request_executed=False",
        "real_provider_execution_executed=False",
        "audio_read=False",
        "microphone_accessed=False",
        "private_path_exposed=False",
        "raw_audio_exposed=False",
        "provider_payload_exposed=False",
    )
    for marker in required_service_markers:
        require(service, marker, f"service contract {marker}")

    forbidden_service_markers = (
        "import openai",
        "from openai",
        "OPENAI_API_KEY",
        "os.environ",
        "executor.execute(",
        "client_factory()",
        "VoiceInputStagingStore",
        "VoiceInputAudioSource(",
        "read_bytes(",
    )
    for marker in forbidden_service_markers:
        reject(service, marker, "RT-3d2c service runtime marker")

    opt_in_call = service.index("self._require_explicit_operator_opt_in(request)")
    root_call = service.index("framework_root = self._resolve_framework_root()")
    context_call = service.index("with self._public_api_context_factory(framework_root)")
    contract_call = service.index("module = self._require_real_executor_contract(public_api)")
    credential_call = service.index("private_credential_builder(credential_type)")
    factory_call = service.index("module.OpenAIVoiceInputRealClientFactory(")
    executor_call = service.index("module.OpenAIVoiceInputRealProviderExecutor(")

    if not (
        opt_in_call
        < root_call
        < context_call
        < contract_call
        < credential_call
        < factory_call
        < executor_call
    ):
        raise AssertionError("RT-3d2c guard/assembly ordering mismatch.")

    if tests.count("def test_") != 5:
        raise AssertionError("RT-3d2c focused test count mismatch.")
    for marker in (
        "state.client_factory_calls == 0",
        "state.executor_calls == 0",
        "credential builder must not run",
        "private_operator_handoff_required",
        "real_executor_opt_in_incomplete",
        "public_openai_real_executor_contract_missing",
        "private_credential_object_invalid",
        '"staging_id" not in result.__dict__',
        '"transcript" not in result.__dict__',
    ):
        require(tests, marker, f"focused test contract {marker}")

    print("v300_rt3d2c_guarded_real_executor_assembly_status: implemented-not-accepted")
    print("v300_framework_release: v5.4.0")
    print(f"v300_framework_tag_commit: {EXPECTED_FW_HEAD}")
    print("v300_fw_root_public_exports_only: True")
    print("v300_operator_opt_in_before_framework_import: True")
    print("v300_credential_builder_after_public_contract: True")
    print("v300_private_credential_object_injected: True")
    print("v300_credential_value_read_by_drc: False")
    print("v300_provider_sdk_imported: False")
    print("v300_provider_client_factory_invoked: False")
    print("v300_provider_client_created: False")
    print("v300_executor_execute_called: False")
    print("v300_network_request_executed: False")
    print("v300_staging_consumed: False")
    print("v300_audio_read: False")
    print("v300_microphone_accessed: False")
    print("v300_private_path_exposed: False")
    print("v300_raw_audio_exposed: False")
    print("v300_provider_payload_exposed: False")
    print("v300_transcript_exposed: False")
    print("v300_real_provider_execution_executed: False")
    print("v300_new_framework_requirement_identified: False")
    print("v300_rt3d3_authorization: blocked-pending-rt3d2c-acceptance")
    print("v300_rt3d_status: blocked-drc-v540-wiring-and-operator-acceptance-pending")
    print("[OK] RT-3d2c guarded real-executor assembly contract is implementation-ready")


if __name__ == "__main__":
    main()
