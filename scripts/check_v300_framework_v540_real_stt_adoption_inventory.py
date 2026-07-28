# Validate DRC v3.0.0 RT-3d1 FW v5.4.0 adoption inventory.

from __future__ import annotations

from pathlib import Path
import hashlib
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DRC_HEAD = "7b1d0154079dc38cce41b3a813df07a0053815e4"
FW_HEAD = "d313eb6acb643103fe25988720ebee5976a04f78"
ZIP_SHA256 = "3acebbc250d575df86cde710d07b962158b266fc6dc969e49c3fbce2e3d6c65d"

EXPECTED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_v540_real_stt_adoption_inventory.md",
    "scripts/check_v300_framework_v540_real_stt_adoption_inventory.py",
}

FW_GATES = (
    "scripts/smoke_v540_provider_execution_configuration_status.py",
    "scripts/smoke_v540_openai_adapter_client_injection_contract.py",
    "scripts/smoke_v540_openai_fake_execution_boundary.py",
    "scripts/smoke_v540_openai_real_provider_runtime.py",
    "scripts/smoke_v540_openai_private_real_provider_operator_acceptance.py",
)


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args), cwd=cwd, check=True, text=True, capture_output=capture
    )
    return completed.stdout.rstrip("\r\n") if capture else ""


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def changed_paths() -> set[str]:
    output = run(
        "git", "status", "--porcelain", "--untracked-files=all", capture=True
    )
    paths: set[str] = set()
    for line in output.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def framework_root() -> Path:
    value = os.environ.get("FRAMEWORK_ROOT", "").strip()
    return Path(value) if value else Path(
        r"E:\work\deverop\AI-Character-Framework\Development"
    )


def framework_python(root: Path) -> Path:
    candidate = root / ".venv" / "Scripts" / "python.exe"
    return candidate if candidate.is_file() else Path(sys.executable)


def verify_public_surface(root: Path, python: Path) -> None:
    source = """
import inspect
import framework

required = (
    "OpenAIVoiceInputProviderAdapter",
    "VoiceInputProviderExecutionConfig",
    "VoiceInputAudioSource",
    "VoiceInputSession",
    "create_voice_input_session",
)
missing = [name for name in required if not hasattr(framework, name)]
assert not missing, missing
adapter = inspect.signature(framework.OpenAIVoiceInputProviderAdapter)
config = inspect.signature(framework.VoiceInputProviderExecutionConfig)
session = inspect.signature(framework.create_voice_input_session)
assert {"execution_config", "model", "client", "client_factory"} <= set(adapter.parameters)
assert {"allow_provider_execution", "credentials_available"} <= set(config.parameters)
assert {"real_stt_enabled", "credential_env"} <= set(session.parameters)
print("public_surface_ok")
"""
    output = run(str(python), "-c", source, cwd=root, capture=True)
    if output.strip() != "public_surface_ok":
        raise AssertionError(f"Unexpected FW public surface result: {output!r}")


def main() -> None:
    if changed_paths() != EXPECTED_PATHS:
        raise AssertionError(f"RT-3d1 changed surface mismatch: {sorted(changed_paths())}")
    if run("git", "rev-parse", "HEAD", capture=True) != DRC_HEAD:
        raise AssertionError("Unexpected DRC baseline HEAD.")

    root = framework_root()
    python = framework_python(root)
    if run("git", "rev-parse", "HEAD", cwd=root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW HEAD.")
    if run("git", "rev-list", "-n", "1", "v5.4.0", cwd=root, capture=True) != FW_HEAD:
        raise AssertionError("Unexpected FW v5.4.0 tag target.")
    if run(
        "git", "status", "--porcelain", "--untracked-files=all",
        cwd=root, capture=True
    ):
        raise AssertionError("FW working tree is not clean.")

    zip_path = root / "release" / "ai-character-framework_v5.4.0.zip"
    sidecar = root / "release" / "ai-character-framework_v5.4.0.zip.sha256"
    if sha256(zip_path) != ZIP_SHA256:
        raise AssertionError("FW ZIP SHA-256 mismatch.")
    if sidecar.read_text(encoding="utf-8").split()[0].lower() != ZIP_SHA256:
        raise AssertionError("FW sidecar SHA-256 mismatch.")

    verify_public_surface(root, python)
    for gate in FW_GATES:
        run(str(python), gate, cwd=root)

    sources = {
        "inventory": read("docs/v300_framework_v540_real_stt_adoption_inventory.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
    }
    for label, text in sources.items():
        require(text, "RT-3d1", f"{label} RT-3d1 marker")
        require(text, "v5.4.0", f"{label} FW version")
        require(
            text,
            "BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING",
            f"{label} block marker",
        )

    require(
        sources["inventory"],
        "RT-3d1: COMPLETED / ACCEPTED",
        "accepted RT-3d1 state",
    )
    require(
        sources["inventory"],
        "explicit operator approval: RECEIVED",
        "operator approval record",
    )
    require(
        sources["inventory"],
        "Additional Framework development requirement discovered by RT-3d1: False",
        "FW requirement result",
    )
    require(
        sources["checklist"],
        "Current small commit: none (RT-3d1 accepted; RT-3d2 next)",
        "active checklist state",
    )

    print("v300_framework_v540_real_stt_adoption_inventory_status: completed-accepted")
    print("v300_framework_release: v5.4.0")
    print(f"v300_framework_tag_commit: {FW_HEAD}")
    print(f"v300_framework_release_zip_sha256: {ZIP_SHA256}")
    print("v300_framework_public_openai_adapter_present: True")
    print("v300_framework_execution_config_present: True")
    print("v300_framework_import_provider_safe: True")
    print("v300_framework_private_real_provider_acceptance_recorded: True")
    print("v300_new_framework_requirement_identified: False")
    print("v300_drc_runtime_changed: False")
    print("v300_audio_read: False")
    print("v300_microphone_accessed: False")
    print("v300_provider_execution_executed: False")
    print("v300_rt3d_status: blocked-drc-v540-wiring-and-operator-acceptance-pending")
    print("v300_rt3d1_operator_approval: accepted")
    print("v300_rt3d2_authorization: authorized-not-started")
    print("[OK] RT-3d1 FW v5.4.0 adoption inventory is completed and accepted")


if __name__ == "__main__":
    main()
