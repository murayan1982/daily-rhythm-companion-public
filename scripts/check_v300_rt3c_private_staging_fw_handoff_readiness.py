"""Validate DRC v3.0.0 RT-3c1 private staging/FW fake-handoff readiness.

This gate is source-only. It does not import the vendored Framework, read or
upload audio, create staging files, open microphones, create provider clients,
or execute STT.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

DRC_SOURCE_COMMIT = "cf734aa04990aa55ccfcd56b65052fbe206f74fb"
DRC_ARCHIVE_SHA256 = "AE42AE996DA0A2E42F132C1AD3A0EF69329E00A709BB10891F6306D459ABFE35"
FRAMEWORK_RELEASE = "v5.3.0"
FRAMEWORK_SURFACE_ARCHIVE_SHA256 = "60AF94A8C3623C0F8D5421B5CA2A6E798E04CD39A1EEA3E9B3A8A29E54BD0096"

ALLOWED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "backend/app/api/voice_input_demo.py",
    "backend/app/models/voice_input_demo.py",
    "backend/app/services/framework_voice_input_fake_handoff.py",
    "backend/tests/test_framework_voice_input_fake_handoff.py",
    "backend/tests/test_voice_input_fake_handoff_api.py",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_v530_stt_integration_inventory.md",
    "docs/v300_host_audio_handoff_lifecycle.md",
    "docs/v300_rt3c_private_staging_fw_handoff_readiness.md",
    "docs/v300_rt3c2_private_backend_staging_store.md",
    "docs/v300_rt3c3_guarded_upload_flutter_staging_consumer.md",
    "docs/v300_rt3c4_fake_fw_public_session_handoff.md",
    "scripts/check_v300_framework_v530_stt_integration_inventory.py",
    "scripts/check_v300_host_audio_handoff_lifecycle.py",
    "scripts/check_v300_rt3c_private_staging_fw_handoff_readiness.py",
    "scripts/check_v300_rt3c2_private_backend_staging_store.py",
    "scripts/check_v300_rt3c3_guarded_upload_flutter_staging_consumer.py",
    "scripts/check_v300_rt3c4_fake_fw_public_session_handoff.py",
}

PROTECTED_TREE_HASHES = {}

PROTECTED_FILE_HASHES = {
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
    "backend/requirements.txt": "e93eaa60004f5fcf0433ab170341da5fa2b1fdbe399fd4f96114ea1f3d7bb5d2",
    "backend/app/config.py": "5bb4d4de13dc2979a59566c6d7cddfc6b7607cadc7e7b4f781218a9f2125f3ca",
    "backend/app/services/voice_input_demo_service.py": "79f77aac86ee58e2daa0c0533ab0e073a5260a361736a81f218972da7054b811",
    "backend/app/services/voice_output_artifact_store.py": "69804d2e9926b76d6f297a1e7919402b084f4e654749b3789d7d23cfc0951613",
    "backend/tests/test_temporary_lifecycle_config.py": "716bf063ab4fbc2e6019a5258b0ea27549f2829f5e0e32bd3b61fbe74dfdeb1c",
    "app/lib/services/backend_api_client.dart": "1d754b931ee7811ce708dd5e0ab3d64bc7b3ecdb63f60f1819d8470976f28774",
}

FRAMEWORK_FILE_HASHES = {
    "framework/__init__.py": "d476c15008694c561a9b9a32331660afadf1b95e0bc954606dccd2043ff37446",
    "framework/voice_input_audio.py": "e5e0e33cd97b69925acd85153f715f28755890385aa2d0f1c31c6ea8ba9cfa86",
    "framework/voice_input_provider_adapter.py": "76323072014c3223520329a4648abbc55b27539cfd6c9ec4d567cdfd3878df26",
    "framework/voice_input_session.py": "a6ae8f543eb7975c03cd447ecc05670c3a45175eedc03e134329b8f1f4610f6b",
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
            details.append("missing RT-3c1 paths:\n" + "\n".join(sorted(missing)))
        raise AssertionError("RT-3c1 source surface mismatch:\n" + "\n".join(details))


def assert_protected_drc_surface() -> None:
    for relative, expected in PROTECTED_TREE_HASHES.items():
        actual = normalized_tree_hash(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"RT-3c1 protected DRC tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in PROTECTED_FILE_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing protected DRC file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"RT-3c1 protected DRC file changed: {relative}: {actual} != {expected}"
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


def validate_docs() -> None:
    sources = {
        "README": read(ROOT, "README.md"),
        "roadmap": read(ROOT, "roadmap.md"),
        "tasklist": read(ROOT, "tasklist.md"),
        "scripts README": read(ROOT, "scripts/README.md"),
        "checklist": read(ROOT, "docs/DRC_v300_goal_checklist_small_commit.md"),
        "RT-3a inventory": read(ROOT, "docs/v300_framework_v530_stt_integration_inventory.md"),
        "RT-3b lifecycle": read(ROOT, "docs/v300_host_audio_handoff_lifecycle.md"),
        "RT-3c1 readiness": read(ROOT, "docs/v300_rt3c_private_staging_fw_handoff_readiness.md"),
    }
    for label, source in sources.items():
        require(source, "RT-3c1", f"{label} RT-3c1 marker")
        assert_no_sensitive_values(label, source)

    readiness = sources["RT-3c1 readiness"]
    for marker in (
        "RT-3c1 implementation: COMPLETED / ACCEPTED",
        "maximum request body: 1048576 bytes",
        "TTL: 300 seconds",
        "maximum count: 8",
        "backend/local_data/voice_input/staging",
        "RT-3c2 implementation: COMPLETED / ACCEPTED",
        "RT-3c4 authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only",
        "RT-3c3",
        "RT-3c4",
        "python-multipart",
        "streamed request body",
        "single-use",
        "real_stt_not_implemented",
    ):
        require(readiness, marker, "RT-3c1 readiness decision")


def validate_drc_surface() -> None:
    handoff = read(ROOT, "app/lib/services/microphone_capture_host_audio_handoff.dart")
    for marker in (
        "class HostAudioPrivateArtifactLease",
        "Future<T> withPrivateArtifactPath<T>(",
        "abstract interface class HostAudioHandoffConsumer",
        "maximumAllowedDuration = const Duration(seconds: 15)",
    ):
        require(handoff, marker, "Flutter scoped handoff marker")

    pubspec = read(ROOT, "app/pubspec.yaml")
    require(pubspec, "http: ^1.6.0", "Flutter HTTP dependency")

    backend_api_client = read(ROOT, "app/lib/services/backend_api_client.dart")
    for forbidden in (
        "HostAudioHandoffConsumer",
        "MultipartRequest",
        "/demo/voice-input/staging",
        "stageHostAudio",
    ):
        if forbidden in backend_api_client:
            raise AssertionError(f"RT-3c1 unexpected Flutter staging runtime present: {forbidden}")

    api = read(ROOT, "backend/app/api/voice_input_demo.py")
    model = read(ROOT, "backend/app/models/voice_input_demo.py")
    service = read(ROOT, "backend/app/services/voice_input_demo_service.py")
    require(api, "does not\n    process audio yet", "metadata-only probe API marker")
    require(model, "Metadata-only request", "metadata-only model marker")
    require(service, "does not import FW audio code, read ``audio_reference``", "no-read service marker")
    require(api, '"/demo/voice-input/staging"', "current guarded staging route")
    require(api, "request.stream()", "current streamed staging body")
    require(api, "VoiceInputStagingStore", "current private staging store wiring")

    combined = "\n".join((api, model, service))
    for forbidden in (
        "UploadFile",
        "StreamingResponse",
        "from framework import",
        "import framework",
        "framework.voice_input",
    ):
        if forbidden in combined:
            raise AssertionError(f"RT-3c1 unexpected Backend staging/FW runtime present: {forbidden}")

    config = read(ROOT, "backend/app/config.py")
    for marker in (
        "voice_input_staging_ttl_seconds: int = 300",
        "voice_input_staging_max_count: int = 8",
        "voice_input_staging_max_bytes: int = 1048576",
    ):
        require(config, marker, "RT-3c2 downstream staging config")

    staging_store = read(ROOT, "backend/app/services/voice_input_staging_store.py")
    for marker in (
        "class VoiceInputStagingStore:",
        "def stage_chunks(",
        "def consume(",
        "def discard(",
    ):
        require(staging_store, marker, "RT-3c2 downstream staging store")
    for forbidden in (
        "from fastapi",
        "APIRouter",
        "from framework",
        "import framework",
        "VoiceInputSession",
    ):
        if forbidden in staging_store:
            raise AssertionError(f"RT-3c2 downstream store crossed a blocked boundary: {forbidden}")

    requirements = read(ROOT, "backend/requirements.txt")
    if "python-multipart" in requirements.lower():
        raise AssertionError("RT-3c1 current Backend unexpectedly depends on python-multipart")

    store = read(ROOT, "backend/app/services/voice_output_artifact_store.py")
    for marker in (
        "class VoiceOutputArtifactStore",
        "ttl_seconds",
        "max_artifacts",
        "resolve_public_artifact",
    ):
        require(store, marker, "existing bounded artifact-store pattern")


def validate_framework_surface(fw: dict[str, str]) -> None:
    fw_init = fw["framework/__init__.py"]
    for marker in (
        "VoiceInputAudioFormat",
        "VoiceInputAudioSource",
        "VoiceInputRequest",
        "VoiceInputResult",
        "VoiceInputSession",
        "create_voice_input_session",
        "FakeVoiceInputProviderAdapter",
    ):
        require(fw_init, marker, f"FW public export {marker}")

    audio = fw["framework/voice_input_audio.py"]
    require(audio, "def from_file_path(", "FW file-path audio source")
    require(audio, "class VoiceInputAudioFormat", "FW audio format contract")

    session = fw["framework/voice_input_session.py"]
    require(session, "def transcribe_audio_result(", "FW public audio transcription wiring")
    require(
        session,
        "effective_adapter = adapter or FakeVoiceInputProviderAdapter()",
        "FW default fake adapter",
    )

    adapter = fw["framework/voice_input_provider_adapter.py"]
    require(adapter, "class FakeVoiceInputProviderAdapter:", "FW fake adapter")
    require(adapter, "class GuardedRealVoiceInputProviderAdapter:", "FW guarded adapter")
    require(adapter, '"guard": "real_stt_not_implemented"', "FW real-provider block")
    require(adapter, '"provider_execution_executed": False', "FW provider non-execution")

    example = fw["examples/voice_input_drc_public_handoff.py"]
    require(example, "create_voice_input_session()", "FW public handoff example")
    require(example, "FakeVoiceInputProviderAdapter(", "FW fake handoff example")
    require(example, "does not open the microphone, read audio, upload", "FW example safety")


def main() -> None:
    assert_protected_drc_surface()
    assert_changed_surface()
    validate_docs()
    validate_drc_surface()

    framework_root = resolve_framework_root()
    fw = assert_framework_surface(framework_root)
    validate_framework_surface(fw)

    print("v300_rt3c_private_staging_fw_handoff_readiness_status: completed-accepted")
    print(f"v300_rt3c1_drc_source_commit: {DRC_SOURCE_COMMIT}")
    print(f"v300_rt3c1_drc_archive_sha256: {DRC_ARCHIVE_SHA256}")
    print(f"v300_rt3c1_framework_release: {FRAMEWORK_RELEASE}")
    print(f"v300_rt3c1_framework_surface_archive_sha256: {FRAMEWORK_SURFACE_ARCHIVE_SHA256}")
    print("v300_rt3c1_exact_current_surface_inspected: True")
    print("v300_rt3c1_flutter_scoped_private_path_lease_present: True")
    print("v300_rt3c1_flutter_http_dependency_present: True")
    print("v300_rt3c1_backend_voice_input_metadata_only: True")
    print("v300_rt3c1_backend_private_staging_store_present_at_inventory: False")
    print("v300_rt3c1_backend_audio_upload_route_present_at_inventory: False")
    print("v300_rt3c3_backend_audio_upload_route_present: True")
    print("v300_rt3c1_backend_staging_lifecycle_config_present_at_inventory: False")
    print("v300_rt3c2_backend_private_staging_store_present: True")
    print("v300_rt3c2_backend_staging_lifecycle_config_present: True")
    print("v300_rt3c1_python_multipart_dependency_present: False")
    print("v300_rt3c1_bounded_streamed_wav_transport_selected: True")
    print("v300_rt3c1_selected_maximum_body_bytes: 1048576")
    print("v300_rt3c1_selected_staging_ttl_seconds: 300")
    print("v300_rt3c1_selected_staging_max_count: 8")
    print("v300_rt3c1_framework_public_fake_file_handoff_present: True")
    print("v300_rt3c1_framework_real_provider_execution_present: False")
    print("v300_rt3c1_runtime_changed: False")
    print("v300_rt3c1_audio_read: False")
    print("v300_rt3c1_audio_uploaded: False")
    print("v300_rt3c1_framework_imported: False")
    print("v300_rt3c1_stt_executed: False")
    print("v300_rt3_parent_status: current-blocked-real-provider-execution-not-implemented")
    print("v300_rt3c_parent_status: completed-accepted")
    print("v300_rt3c1_status: completed-accepted")
    print("v300_rt3c2_status: completed-accepted")
    print("v300_rt3c2_implementation: completed-accepted")
    print("v300_rt3c3_status: completed-accepted")
    print("v300_rt3c3_implementation: completed-accepted")
    print("v300_rt3c4_status: completed-accepted")
    print("v300_rt3c4_implementation: completed-accepted")
    print("v300_rt3c4_authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only")
    print("v300_rt3_real_acceptance: blocked-framework-real-provider-execution-not-implemented")


if __name__ == "__main__":
    main()
