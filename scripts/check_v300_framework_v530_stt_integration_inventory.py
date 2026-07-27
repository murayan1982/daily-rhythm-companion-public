"""Validate RT-3a Framework v5.3.0 STT integration inventory.

This gate is source-only. It does not import the vendored framework, load a
private dotenv file, read credentials, read/upload audio, open a microphone,
create provider clients, or execute STT.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DRC_SOURCE_COMMIT = "c7a6afd85f29fe07564ded02a76fa645b2fb9a69"
FRAMEWORK_RELEASE = "v5.3.0"
DRC_ARCHIVE_SHA256 = "5432DE388BD4AE13CDD2663839DBBE628C7BC319D821E2C845500A3F920AF786"
FRAMEWORK_SURFACE_ARCHIVE_SHA256 = "60AF94A8C3623C0F8D5421B5CA2A6E798E04CD39A1EEA3E9B3A8A29E54BD0096"

ALLOWED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_v530_stt_integration_inventory.md",
    "scripts/check_v300_framework_v530_stt_integration_inventory.py",
}

PROTECTED_TREE_HASHES = {
    "backend/app": "e46df81c20a3843b249cb66757c75a2324ff05c54adf2549b65de22ce2efcec1",
    "backend/tests": "c62f2351de017fd7812571c66232c6dbff293539e52b72a8bc06a8f5aa0044ae",
    "app/lib": "eea487551ce299a728aa25f4dbf1ef1cfbadf1e530d7e9cea5cd1249fe7dcde9",
    "app/test": "969a89030060b8934f6a5a82e27fae0caae0fb2811507c4975cf33f0f7a2e836",
}

PROTECTED_FILE_HASHES = {
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
    "app/android/app/src/main/AndroidManifest.xml": "5fb1b832160c9dcfeb33d45fe3b0ea3355dced95caa5a675b4490caba2b0adcd",
    "app/ios/Runner/Info.plist": "0bed3e2d536b5160706c12bd99da7364562f1b9fd4ed84a6d3a0c9d64f743865",
    "backend/app/version.py": "dfbbca8efedb35151eea62bb9f719abea41b97b722d19abbefb1a7f176cb205e",
    "backend/.env.example": "c6936adcf1af839f6b5ed3c596395baa2a16eca5104a3015f9a392787234d45a",
}

FRAMEWORK_FILE_HASHES = {
    "framework/__init__.py": "d476c15008694c561a9b9a32331660afadf1b95e0bc954606dccd2043ff37446",
    "framework/voice_input.py": "13e4c5a9dcf4ed3382d67cea43f5e36f2c63660e6170cda36e4bf2e5efe07684",
    "framework/voice_input_audio.py": "e5e0e33cd97b69925acd85153f715f28755890385aa2d0f1c31c6ea8ba9cfa86",
    "framework/voice_input_provider_adapter.py": "76323072014c3223520329a4648abbc55b27539cfd6c9ec4d567cdfd3878df26",
    "framework/voice_input_session.py": "a6ae8f543eb7975c03cd447ecc05670c3a45175eedc03e134329b8f1f4610f6b",
    "docs/v530_release_readiness_gate.md": "2838270221f2ec9b2b8e3ec157850be90d6635e54d086b7c35f6a5dc2c5620d8",
    "docs/v530_drc_public_handoff_verification.md": "0a55c2e88ece09e2c1633e2929020170c98a0c1d0d230b5c58d6fe383395b7dd",
    "examples/voice_input_drc_public_handoff.py": "c80411fb66c07df877ef02edc341bb607cd9d2a08d330e2fc14539113167363a",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:\\Users\\[^<\r\n]+",
    r"192\.168\.\d{1,3}\.\d{1,3}",
)


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_hash(path: Path) -> str:
    return sha256(normalized_bytes(path)).hexdigest()


def normalized_tree_hash(path: Path) -> str:
    if not path.is_dir():
        raise AssertionError(f"Missing protected directory: {path.relative_to(ROOT).as_posix()}")
    digest = sha256()
    candidates = [
        item
        for item in path.rglob("*")
        if item.is_file()
        and "__pycache__" not in item.parts
        and item.suffix.lower() not in {".pyc", ".pyo"}
    ]
    for item in sorted(candidates):
        digest.update(item.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(normalized_bytes(item))
        digest.update(b"\0")
    return digest.hexdigest()


def read(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def assert_no_sensitive_values(label: str, text: str) -> None:
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {label}: {pattern}")


def resolve_framework_root() -> Path:
    raw = (os.getenv("FRAMEWORK_ROOT") or os.getenv("FRAMEWORK_PROJECT_ROOT") or "").strip()
    if not raw:
        raise AssertionError(
            "FRAMEWORK_ROOT is not set in the current operator shell. "
            "Set it to the vendored AI Character Framework v5.3.0 root."
        )
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise AssertionError("Configured FRAMEWORK_ROOT does not exist.")
    return root


def assert_protected_drc_surface() -> None:
    for relative, expected in PROTECTED_TREE_HASHES.items():
        actual = normalized_tree_hash(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"RT-3a protected DRC tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in PROTECTED_FILE_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing protected DRC file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"RT-3a protected DRC file changed: {relative}: {actual} != {expected}"
            )


def assert_framework_surface(framework_root: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    for relative, expected in FRAMEWORK_FILE_HASHES.items():
        path = framework_root / relative
        if not path.is_file():
            raise AssertionError(f"Missing FW v5.3.0 surface file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"FW v5.3.0 surface mismatch: {relative}: {actual} != {expected}"
            )
        texts[relative] = path.read_text(encoding="utf-8")
    return texts


def changed_paths() -> set[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return set()

    paths: set[str] = set()
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        path_text = raw_line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.add(path_text.replace("\\", "/"))
    return paths


def assert_changed_surface() -> None:
    paths = changed_paths()
    if not paths:
        return
    unexpected = paths - ALLOWED_CHANGED_PATHS
    missing = ALLOWED_CHANGED_PATHS - paths
    if unexpected or missing:
        details: list[str] = []
        if unexpected:
            details.append("unexpected paths:\n" + "\n".join(sorted(unexpected)))
        if missing:
            details.append("missing RT-3a paths:\n" + "\n".join(sorted(missing)))
        raise AssertionError("RT-3a source surface mismatch:\n" + "\n".join(details))


def main() -> None:
    assert_protected_drc_surface()
    assert_changed_surface()

    framework_root = resolve_framework_root()
    fw = assert_framework_surface(framework_root)

    inventory = read(ROOT, "docs/v300_framework_v530_stt_integration_inventory.md")
    checklist = read(ROOT, "docs/DRC_v300_goal_checklist_small_commit.md")
    readme = read(ROOT, "README.md")
    roadmap = read(ROOT, "roadmap.md")
    tasklist = read(ROOT, "tasklist.md")
    scripts_readme = read(ROOT, "scripts/README.md")

    planning_sources = {
        "inventory": inventory,
        "checklist": checklist,
        "README": readme,
        "roadmap": roadmap,
        "tasklist": tasklist,
        "scripts README": scripts_readme,
    }
    for label, source in planning_sources.items():
        require(source, "RT-3a", f"{label} RT-3a marker")
        require(source, "v5.3.0", f"{label} FW release marker")
        assert_no_sensitive_values(label, source)

    require(inventory, "RT-3a: COMPLETED / ACCEPTED", "inventory accepted state")
    require(
        checklist,
        "Current implementation state: NOT_STARTED",
        "checklist RT-3b state",
    )
    require(
        checklist,
        "RT-3b: CURRENT / NOT_COMPLETED",
        "RT-3b current marker",
    )
    require(
        inventory,
        "authorized-app-owned-host-audio-lifecycle-contract-fake-only",
        "RT-3b future authorization",
    )
    require(
        inventory,
        "FW v5.3.0 actual provider execution: absent",
        "honest provider execution finding",
    )
    require(
        inventory,
        "DRC voice-input audio upload/staging: absent",
        "DRC upload/staging finding",
    )

    fw_init = fw["framework/__init__.py"]
    for symbol in (
        "VoiceInputAudioSource",
        "VoiceInputAudioFormat",
        "VoiceInputRequest",
        "VoiceInputResult",
        "VoiceInputSession",
        "create_voice_input_session",
        "FakeVoiceInputProviderAdapter",
        "GuardedRealVoiceInputProviderAdapter",
    ):
        require(fw_init, symbol, f"FW public export {symbol}")

    fw_session = fw["framework/voice_input_session.py"]
    require(fw_session, "def transcribe_audio_result(", "FW transcribe session method")
    require(fw_session, "def listen_audio_result(", "FW listen-audio alias")
    require(
        fw_session,
        "effective_adapter = adapter or FakeVoiceInputProviderAdapter()",
        "FW default fake adapter wiring",
    )

    fw_adapter = fw["framework/voice_input_provider_adapter.py"]
    require(fw_adapter, 'class FakeVoiceInputProviderAdapter:', "FW fake adapter")
    require(
        fw_adapter,
        'class GuardedRealVoiceInputProviderAdapter:',
        "FW guarded real adapter",
    )
    require(fw_adapter, '"guard": "real_stt_not_implemented"', "FW real STT missing guard")
    require(fw_adapter, '"provider_execution_executed": False', "FW provider non-execution")
    require(fw_adapter, '"audio_read": False', "FW audio non-read")
    require(
        fw_adapter,
        'available=False',
        "FW guarded adapter remains unavailable",
    )

    release_gate = fw["docs/v530_release_readiness_gate.md"]
    require(
        release_gate,
        "v530_public_real_stt_execution_present: False",
        "FW release honest real STT status",
    )
    require(
        release_gate,
        "v530_drc_rt3_status: blocked-pending-real-provider-execution",
        "FW release DRC block status",
    )

    drc_engine = read(ROOT, "app/lib/services/record_microphone_capture_engine.dart")
    require(
        drc_engine,
        "abstract interface class RecordMicrophoneCapturePrivateArtifactAccess",
        "DRC private artifact access",
    )
    require(
        drc_engine,
        "String? resolvePrivateArtifactPath(String opaqueCaptureId);",
        "DRC private path resolver",
    )
    require(
        drc_engine,
        "Future<bool> discardPrivateArtifact(String opaqueCaptureId);",
        "DRC private artifact discard",
    )

    operator = read(ROOT, "app/lib/operators/rt2ec_microphone_capture_operator.dart")
    require(
        operator,
        ".discardPrivateArtifact(",
        "DRC operator immediate discard",
    )
    require(
        operator,
        "録音を停止し、private artifactを削除しました。",
        "DRC operator discard evidence",
    )

    model = read(ROOT, "backend/app/models/voice_input_demo.py")
    api = read(ROOT, "backend/app/api/voice_input_demo.py")
    require(model, "Metadata-only request", "DRC metadata-only request contract")
    require(api, "process audio yet", "DRC audio processing block")
    for forbidden in ("UploadFile", "File(", "multipart/form-data"):
        if forbidden in api or forbidden in model:
            raise AssertionError(f"Unexpected DRC voice-input upload boundary present: {forbidden}")

    print("v300_framework_v530_stt_integration_inventory_status: completed-accepted")
    print(f"v300_drc_source_commit: {DRC_SOURCE_COMMIT}")
    print(f"v300_framework_release: {FRAMEWORK_RELEASE}")
    print(f"v300_drc_archive_sha256: {DRC_ARCHIVE_SHA256}")
    print(f"v300_framework_surface_archive_sha256: {FRAMEWORK_SURFACE_ARCHIVE_SHA256}")
    print("v300_framework_public_host_audio_contract_present: True")
    print("v300_framework_public_voice_input_session_wiring_present: True")
    print("v300_framework_fake_adapter_present: True")
    print("v300_framework_guarded_real_adapter_present: True")
    print("v300_framework_real_provider_execution_present: False")
    print("v300_framework_guarded_adapter_available_after_guard: False")
    print("v300_drc_capture_private_artifact_boundary_present: True")
    print("v300_drc_operator_auto_discard_present: True")
    print("v300_drc_backend_audio_upload_boundary_present: False")
    print("v300_drc_voice_input_endpoint_metadata_only: True")
    print("v300_drc_runtime_changed: False")
    print("v300_provider_execution_executed: False")
    print("v300_audio_uploaded: False")
    print("v300_stt_executed: False")
    print(
        "v300_rt3_parent_status: "
        "current-blocked-real-provider-execution-not-implemented"
    )
    print("v300_rt3a_status: completed-accepted")
    print("v300_rt3b_status: current-not-completed")
    print(
        "v300_rt3b_authorization: "
        "authorized-app-owned-host-audio-lifecycle-contract-fake-only"
    )
    print(
        "v300_rt3_real_acceptance: "
        "blocked-framework-real-provider-execution-not-implemented"
    )


if __name__ == "__main__":
    main()
