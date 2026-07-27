"""Validate DRC v3.0.0 RT-3c2 private Backend staging store.

This mock-safe gate inspects the exact RT-3c2 source surface and runs a synthetic
private-store lifecycle smoke. It does not start FastAPI, read a real microphone
artifact, upload audio, import the vendored Framework, create a provider client,
or execute STT.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.voice_input_staging_store import VoiceInputStagingStore  # noqa: E402


SOURCE_COMMIT = "c61eeb2616a3ed5b3c411a3a6b55750ed9d786d2"
SOURCE_ARCHIVE_SHA256 = (
    "BFBA6724FAA02E5D060F90F49DEAE80C45156DBA83F7372FB9CC791E99D17191"
)

ALLOWED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "backend/.env.example",
    "backend/app/config.py",
    "backend/app/services/voice_input_staging_store.py",
    "backend/tests/test_temporary_lifecycle_config.py",
    "backend/tests/test_voice_input_staging_store.py",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_v530_stt_integration_inventory.md",
    "docs/v300_host_audio_handoff_lifecycle.md",
    "docs/v300_rt3c_private_staging_fw_handoff_readiness.md",
    "docs/v300_rt3c2_private_backend_staging_store.md",
    "scripts/check_v300_framework_v530_stt_integration_inventory.py",
    "scripts/check_v300_host_audio_handoff_lifecycle.py",
    "scripts/check_v300_rt3c_private_staging_fw_handoff_readiness.py",
    "scripts/check_v300_rt3c2_private_backend_staging_store.py",
}

PROTECTED_TREE_HASHES = {
    "app/lib": "15c81e30712b6980aca085ceed11f31e97da40c70223197a41396b0ff123a857",
    "app/test": "1d9d3124880d918ff1f52ec0abc35b01b6a7417824bae16c159cb6efff2b75d2",
}

PROTECTED_FILE_HASHES = {
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/app/api/voice_input_demo.py": "3737e92544d2e3d53a98c7bef8f79f2b6894808168b6745a766573eb29a021d2",
    "backend/requirements.txt": "e93eaa60004f5fcf0433ab170341da5fa2b1fdbe399fd4f96114ea1f3d7bb5d2",
    "backend/requirements-dev.txt": "8636f9ab1a075be9f3039e2a6471837259c4f36b625bcaf7a3d9a1edd2419c6d",
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
    "app/android/app/src/main/AndroidManifest.xml": "5fb1b832160c9dcfeb33d45fe3b0ea3355dced95caa5a675b4490caba2b0adcd",
    "app/ios/Runner/Info.plist": "0bed3e2d536b5160706c12bd99da7364562f1b9fd4ed84a6d3a0c9d64f743865",
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


def read(relative: str) -> str:
    path = ROOT / relative
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
            details.append("missing RT-3c2 paths:\n" + "\n".join(sorted(missing)))
        raise AssertionError("RT-3c2 source surface mismatch:\n" + "\n".join(details))


def assert_protected_surface() -> None:
    for relative, expected in PROTECTED_TREE_HASHES.items():
        actual = normalized_tree_hash(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"RT-3c2 protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in PROTECTED_FILE_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing protected file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"RT-3c2 protected file changed: {relative}: {actual} != {expected}"
            )


def validate_config() -> None:
    config = read("backend/app/config.py")
    env_example = read("backend/.env.example")
    tests = read("backend/tests/test_temporary_lifecycle_config.py")

    for marker in (
        "voice_input_staging_ttl_seconds: int = 300",
        "voice_input_staging_max_count: int = 8",
        "voice_input_staging_max_bytes: int = 1048576",
        '"VOICE_INPUT_STAGING_TTL_SECONDS",\n            300,',
        '"VOICE_INPUT_STAGING_MAX_COUNT",\n            8,',
        '"VOICE_INPUT_STAGING_MAX_BYTES",\n            1048576,',
    ):
        require(config, marker, "RT-3c2 config marker")

    for marker in (
        "VOICE_INPUT_STAGING_TTL_SECONDS=300",
        "VOICE_INPUT_STAGING_MAX_COUNT=8",
        "VOICE_INPUT_STAGING_MAX_BYTES=1048576",
        "No public file-serving route is added",
    ):
        require(env_example, marker, "RT-3c2 env example marker")

    for marker in (
        "config.voice_input_staging_ttl_seconds == 300",
        "config.voice_input_staging_max_count == 8",
        "config.voice_input_staging_max_bytes == 1048576",
        "config.voice_input_staging_ttl_seconds == 30",
        "config.voice_input_staging_max_count == 4",
        "config.voice_input_staging_max_bytes == 2048",
    ):
        require(tests, marker, "RT-3c2 config test marker")


def validate_store() -> None:
    store = read("backend/app/services/voice_input_staging_store.py")

    for marker in (
        "class StagedVoiceInputArtifact:",
        "class VoiceInputStagingCleanupResult:",
        "class VoiceInputStagingError(RuntimeError):",
        "class VoiceInputStagingStore:",
        'backend_root / "local_data" / "voice_input"',
        'self._staging_dir = self._root_dir / "staging"',
        "def stage_chunks(",
        "def consume(",
        "def discard(",
        "def has_artifact(",
        "def artifact_count(",
        "def cleanup(",
        're.compile(r"^[0-9a-f]{32}$")',
        '"artifact_too_large"',
        '"invalid_wav_header"',
        'header[:4] != b"RIFF"',
        'header[8:12] != b"WAVE"',
        "protected_paths=(final_path,)",
        '"cleanup_failed"',
        "if candidate_ref.is_symlink():",
    ):
        require(store, marker, "RT-3c2 store marker")

    for forbidden in (
        "from fastapi",
        "import fastapi",
        "APIRouter",
        "UploadFile",
        "Request",
        "python_multipart",
        "multipart",
        "framework.",
        "from framework",
        "import framework",
        "VoiceInputAudioSource",
        "VoiceInputSession",
        "create_voice_input_session",
        "FakeVoiceInputProviderAdapter",
        "GuardedRealVoiceInputProviderAdapter",
        "transcribe",
        "provider_execution",
    ):
        if forbidden in store:
            raise AssertionError(f"RT-3c2 forbidden store marker: {forbidden}")


def validate_tests() -> None:
    tests = read("backend/tests/test_voice_input_staging_store.py")
    if tests.count("def test_") < 10:
        raise AssertionError("RT-3c2 focused store test count is below 10")

    for marker in (
        "test_stage_returns_path_free_opaque_metadata_and_scoped_consume",
        "test_application_octet_stream_is_normalized_to_safe_wav_metadata",
        "test_stage_rejects_unsupported_format_media_type_and_invalid_header",
        "test_stage_rejects_empty_invalid_chunk_and_oversized_body_without_leftovers",
        "test_invalid_chunk_type_is_rejected_when_within_size_limit",
        "test_stage_cleans_partial_when_chunk_iterable_raises",
        "test_capacity_cleanup_removes_oldest_without_exceeding_bound",
        "test_expiry_cleanup_and_expired_consume_are_bounded",
        "test_consume_is_single_use_and_cleans_up_after_consumer_exception",
        "test_explicit_discard_and_malformed_ids_do_not_expose_or_escape_paths",
        "test_cleanup_removes_expired_partial_file_but_preserves_unmanaged_and_symlink",
        'assert "path" not in staged.__dict__',
        "assert not store.has_artifact(staged.staging_id)",
    ):
        require(tests, marker, "RT-3c2 test marker")

    for forbidden in (
        "TestClient",
        "client.post",
        "package:http",
        "FRAMEWORK_ROOT",
        "create_voice_input_session",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
    ):
        if forbidden in tests:
            raise AssertionError(f"RT-3c2 test executes forbidden boundary: {forbidden}")


def validate_docs() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "FW inventory": read("docs/v300_framework_v530_stt_integration_inventory.md"),
        "host handoff": read("docs/v300_host_audio_handoff_lifecycle.md"),
        "RT-3c readiness": read("docs/v300_rt3c_private_staging_fw_handoff_readiness.md"),
        "RT-3c2 doc": read("docs/v300_rt3c2_private_backend_staging_store.md"),
    }
    combined = "\n".join(sources.values())
    for label, source in sources.items():
        assert_no_sensitive_values(label, source)
        require(source, "RT-3c2", f"{label} RT-3c2 marker")

    for marker in (
        "RT-3c2 implementation: COMPLETED / ACCEPTED",
        "authorized-bounded-private-backend-staging-store-and-lifecycle-only",
        "VOICE_INPUT_STAGING_TTL_SECONDS=300",
        "VOICE_INPUT_STAGING_MAX_COUNT=8",
        "VOICE_INPUT_STAGING_MAX_BYTES=1048576",
        "backend/local_data/voice_input/staging",
        "RT-3c3: CURRENT / NOT_COMPLETED",
        "RT-3c3 authorization: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only",
        "127 passed",
        "192",
        "No FastAPI upload route",
        "does not add a FastAPI upload route",
        "does not import Framework",
    ):
        require(combined, marker, "RT-3c2 planning marker")


def run_synthetic_store_smoke() -> None:
    synthetic_wav = b"RIFF" + (b"\x00" * 4) + b"WAVE" + b"synthetic-only"
    with TemporaryDirectory(prefix="drc-rt3c2-") as temporary_root:
        store = VoiceInputStagingStore(
            Path(temporary_root) / "voice_input",
            ttl_seconds=300,
            max_artifacts=8,
            max_bytes=1048576,
        )
        staged = store.stage_chunks((synthetic_wav[:5], synthetic_wav[5:]))
        if set(staged.__dict__) != {
            "staging_id",
            "audio_format",
            "media_type",
            "byte_count",
        }:
            raise AssertionError("RT-3c2 metadata contains an unexpected field")
        if not store.has_artifact(staged.staging_id):
            raise AssertionError("RT-3c2 synthetic artifact was not retained")

        def consume(path: Path, metadata: object) -> str:
            if not path.is_file() or path.suffix.lower() != ".wav":
                raise AssertionError("RT-3c2 scoped path is not a managed WAV")
            if metadata != staged:
                raise AssertionError("RT-3c2 scoped metadata changed")
            return "synthetic-consumed"

        result = store.consume(staged.staging_id, consume)
        if result != "synthetic-consumed":
            raise AssertionError("RT-3c2 synthetic consume result mismatch")
        if store.has_artifact(staged.staging_id) or store.artifact_count() != 0:
            raise AssertionError("RT-3c2 synthetic artifact was not single-use")


def main() -> None:
    assert_changed_surface()
    assert_protected_surface()
    validate_config()
    validate_store()
    validate_tests()
    validate_docs()
    run_synthetic_store_smoke()

    print("v300_rt3c2_private_backend_staging_store_status: completed-accepted")
    print(f"v300_rt3c2_drc_source_commit: {SOURCE_COMMIT}")
    print(f"v300_rt3c2_drc_archive_sha256: {SOURCE_ARCHIVE_SHA256}")
    print("v300_rt3c2_config_defaults_added: True")
    print("v300_rt3c2_private_store_added: True")
    print("v300_rt3c2_private_root_ignored: True")
    print("v300_rt3c2_opaque_id_added: True")
    print("v300_rt3c2_path_free_metadata: True")
    print("v300_rt3c2_bounded_chunk_staging_added: True")
    print("v300_rt3c2_maximum_body_bytes: 1048576")
    print("v300_rt3c2_staging_ttl_seconds: 300")
    print("v300_rt3c2_staging_max_count: 8")
    print("v300_rt3c2_single_use_consume_added: True")
    print("v300_rt3c2_explicit_discard_added: True")
    print("v300_rt3c2_cleanup_lifecycle_added: True")
    print("v300_rt3c2_synthetic_store_smoke_passed: True")
    print("v300_rt3c2_real_audio_read: False")
    print("v300_rt3c2_audio_uploaded: False")
    print("v300_rt3c2_upload_route_added: False")
    print("v300_rt3c2_flutter_changed: False")
    print("v300_rt3c2_framework_imported: False")
    print("v300_rt3c2_provider_execution_executed: False")
    print("v300_rt3c2_stt_executed: False")
    print(
        "v300_rt3_parent_status: "
        "current-blocked-real-provider-execution-not-implemented"
    )
    print("v300_rt3c_parent_status: current-pending-rt3c3-implementation")
    print("v300_rt3c2_status: completed-accepted")
    print("v300_rt3c2_implementation: completed-accepted")
    print("v300_rt3c3_status: current-not-completed")
    print("v300_rt3c3_implementation: not-started")
    print("v300_rt3c3_authorization: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only")
    print("v300_rt3c4_authorization: blocked-pending-rt3c3-acceptance")
    print(
        "v300_rt3_real_acceptance: "
        "blocked-framework-real-provider-execution-not-implemented"
    )


if __name__ == "__main__":
    main()
