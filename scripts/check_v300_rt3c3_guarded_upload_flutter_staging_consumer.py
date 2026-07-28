"""Validate DRC v3.0.0 RT-3c3 guarded upload and Flutter staging consumer.

This gate inspects the exact RT-3c3 source surface and runs a generated-WAV
Backend staging smoke in a temporary directory. It does not read a microphone
artifact, contact a running Backend, import the vendored Framework, create a
provider client, or execute STT.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api import voice_input_demo  # noqa: E402
from app.config import AppConfig  # noqa: E402
from app.services.voice_input_staging_store import VoiceInputStagingStore  # noqa: E402

SOURCE_COMMIT = "6f97014715c8e198ae639420f7cf9334d9a61029"
SOURCE_ARCHIVE_SHA256 = (
    "93DC227CEACF640709695F758A0E73DEBDF63749FE4418F071CDBEC69E07AD42"
)

ALLOWED_CHANGED_PATHS = {
    "README.md",
    "roadmap.md",
    "tasklist.md",
    "scripts/README.md",
    "backend/app/api/voice_input_demo.py",
    "backend/app/models/voice_input_demo.py",
    "backend/app/services/voice_input_staging_store.py",
    "backend/tests/test_voice_input_staging_upload_api.py",
    "app/lib/services/microphone_capture_host_audio_handoff.dart",
    "app/lib/services/backend_voice_input_staging_consumer.dart",
    "app/test/backend_voice_input_staging_consumer_test.dart",
    "docs/DRC_v300_goal_checklist_small_commit.md",
    "docs/v300_framework_v530_stt_integration_inventory.md",
    "docs/v300_host_audio_handoff_lifecycle.md",
    "docs/v300_rt3c_private_staging_fw_handoff_readiness.md",
    "docs/v300_rt3c2_private_backend_staging_store.md",
    "docs/v300_rt3c3_guarded_upload_flutter_staging_consumer.md",
    "scripts/check_v300_framework_v530_stt_integration_inventory.py",
    "scripts/check_v300_host_audio_handoff_lifecycle.py",
    "scripts/check_v300_rt3c_private_staging_fw_handoff_readiness.py",
    "scripts/check_v300_rt3c2_private_backend_staging_store.py",
    "scripts/check_v300_rt3c3_guarded_upload_flutter_staging_consumer.py",
}

PROTECTED_FILE_HASHES = {
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/app/config.py": "5bb4d4de13dc2979a59566c6d7cddfc6b7607cadc7e7b4f781218a9f2125f3ca",
    "backend/.env.example": "874ad09f8dd37370c9ba423fdc676133e447efeaeecd6eb44a1a2c1a2d46a76a",
    "backend/requirements.txt": "e93eaa60004f5fcf0433ab170341da5fa2b1fdbe399fd4f96114ea1f3d7bb5d2",
    "backend/requirements-dev.txt": "8636f9ab1a075be9f3039e2a6471837259c4f36b625bcaf7a3d9a1edd2419c6d",
    "backend/app/version.py": "dfbbca8efedb35151eea62bb9f719abea41b97b722d19abbefb1a7f176cb205e",
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
    "app/pubspec.lock": "d9eed55039c9075b1b3744184ea3223f4ca030003e23be06852741024866b2eb",
    "app/lib/main.dart": "2513413c1e863e73b605c9110244596e109fdcfdd8ab2876c2cc60c531d30a2c",
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


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


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
            details.append("missing RT-3c3 paths:\n" + "\n".join(sorted(missing)))
        raise AssertionError("RT-3c3 source surface mismatch:\n" + "\n".join(details))


def assert_protected_surface() -> None:
    for relative, expected in PROTECTED_FILE_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing protected file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"RT-3c3 protected file changed: {relative}: {actual} != {expected}"
            )


def validate_backend_route() -> None:
    api = read("backend/app/api/voice_input_demo.py")
    models = read("backend/app/models/voice_input_demo.py")
    store = read("backend/app/services/voice_input_staging_store.py")
    tests = read("backend/tests/test_voice_input_staging_upload_api.py")

    for needle, label in (
        ('"/demo/voice-input/staging"', "guarded staging route"),
        ("request.stream()", "streamed request body"),
        ("_require_staging_upload_enabled(config)", "explicit upload guards"),
        ('media_type != "audio/wav"', "WAV media guard"),
        ('"x-drc-sample-rate-hz"', "sample-rate header"),
        ('"x-drc-channel-count"', "channel header"),
        ('"x-drc-duration-ms"', "duration header"),
        ("config.voice_input_staging_max_bytes", "configured body bound"),
        ("VoiceInputStagingUploadResponse", "path-free upload response"),
        ("VoiceInputStagingProblem", "safe problem response"),
    ):
        require(api, needle, label)

    require(models, "class VoiceInputStagingUploadResponse", "upload response model")
    require(models, "class VoiceInputStagingProblem", "problem model")
    require(store, "async def stage_async_chunks(", "async streamed store input")
    require(store, 'partial_path = self._staging_dir / f".{staging_id}.part"', "private partial")
    require(store, "async for chunk in chunks:", "incremental chunk loop")
    require(store, "if next_size > self._max_bytes:", "streamed byte bound")
    require(store, "partial_path.replace(final_path)", "private finalization")
    require(store, "self._unlink(partial_path)", "partial cleanup")

    forbid(api, "UploadFile", "multipart UploadFile")
    forbid(api, "File(", "multipart File dependency")
    forbid(api, "multipart/form-data", "multipart media type")
    forbid(api, "from framework", "Framework import")
    forbid(api, "import framework", "Framework import")
    forbid(store, "from framework", "Framework import")
    forbid(store, "import framework", "Framework import")

    for needle in (
        "test_staging_upload_streams_wav_and_returns_path_free_metadata",
        "test_staging_upload_is_guarded_by_explicit_voice_input_enablement",
        "test_staging_upload_requires_framework_engine",
        "test_staging_upload_requires_framework_adapter_mode",
        "test_staging_upload_rejects_non_wav_media_type",
        "test_staging_upload_rejects_missing_safe_audio_metadata",
        "test_staging_upload_rejects_wrong_sample_rate_and_channel_count",
        "test_staging_upload_rejects_duration_over_fifteen_seconds",
        "test_staging_upload_rejects_declared_or_streamed_body_over_limit",
        "test_staging_upload_rejects_invalid_wav_without_leaving_partial",
    ):
        require(tests, needle, f"Backend test {needle}")


def validate_flutter_consumer() -> None:
    consumer = read("app/lib/services/backend_voice_input_staging_consumer.dart")
    handoff = read("app/lib/services/microphone_capture_host_audio_handoff.dart")
    tests = read("app/test/backend_voice_input_staging_consumer_test.dart")

    for needle, label in (
        ("class BackendVoiceInputStagedArtifact", "path-free staged handle"),
        ("class BackendVoiceInputStagingConsumer implements HostAudioHandoffConsumer", "consumer"),
        ("lease.withPrivateArtifactPath", "scoped path access"),
        ("FileSystemEntity.type(", "symlink-safe entity check"),
        ("followLinks: false", "symlink guard"),
        ("http.StreamedRequest('POST', _endpoint)", "streamed HTTP request"),
        ("file.openRead()", "streamed file read"),
        ("takeStagedArtifact()", "single handle transfer"),
        ("backend_staging_artifact_pending", "pending handle guard"),
        ("maximumResponseBytes", "bounded response"),
        ("'audio_uploaded': true", "safe upload metadata"),
    ):
        require(consumer, needle, label)

    for forbidden, label in (
        ("readAsBytes", "whole-file read"),
        ("package:framework", "Framework package import"),
        ("VoiceInputSession", "Framework session use"),
        ("opaqueCaptureId':", "capture ID request field"),
    ):
        forbid(consumer, forbidden, label)

    require(handoff, "'audio_uploaded'", "safe upload metadata allowlist")
    require(handoff, "'backend_staging_created'", "staging-created metadata allowlist")
    require(handoff, "'backend_staging_id_available'", "staging handle metadata allowlist")
    require(handoff, "safeConsumerMetadata['audio_uploaded'] == true", "consumer result propagation")
    require(handoff, "'stt_executed': false", "handoff STT non-execution")

    for needle in (
        "streams scoped WAV bytes and keeps path out of request metadata",
        "takeStagedArtifact transfers the path-free handle once",
        "rejects local artifact above the client byte bound before sending",
        "normalizes Backend problem without exposing the response message",
        "marks server failure retryable while local source is still discarded",
        "rejects malformed success response as a safe contract failure",
        "does not allow a second upload while a staging handle is pending",
        "dispose fast-fails future consume and remains idempotent",
    ):
        require(tests, needle, f"Flutter test {needle}")


def validate_docs() -> None:
    docs = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "RT-3c3 doc": read("docs/v300_rt3c3_guarded_upload_flutter_staging_consumer.md"),
        "scripts README": read("scripts/README.md"),
    }
    for label, text in docs.items():
        require(text, "RT-3c3", f"{label} RT-3c3 marker")
        require(text, "COMPLETED / ACCEPTED", f"{label} accepted state")
        assert_no_sensitive_values(label, text)

    rt3c3 = docs["RT-3c3 doc"]
    require(rt3c3, SOURCE_COMMIT, "source commit")
    require(rt3c3, SOURCE_ARCHIVE_SHA256, "source archive hash")
    require(rt3c3, "real operator audio uploaded: no", "honest operator-audio status")
    require(rt3c3, "Framework imported: no", "Framework non-import")
    require(rt3c3, "provider execution: no", "provider non-execution")
    require(rt3c3, "transcription/STT execution: no", "STT non-execution")
    require(rt3c3, "RT-3c4: CURRENT / NOT_COMPLETED", "RT-3c4 current state")
    require(rt3c3, "RT-3c4 implementation: NOT_STARTED", "RT-3c4 not-started state")
    require(rt3c3, "RT-3c4 authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only", "RT-3c4 authorization")


def generated_wav(payload_size: int = 24) -> bytes:
    return (
        b"RIFF"
        + (payload_size + 4).to_bytes(4, "little")
        + b"WAVE"
        + (b"\x00" * payload_size)
    )


def run_synthetic_backend_smoke() -> None:
    config = AppConfig(
        conversation_engine="framework",
        voice_input_demo_enabled=True,
        voice_input_adapter_mode="framework",
        voice_input_staging_ttl_seconds=300,
        voice_input_staging_max_count=8,
        voice_input_staging_max_bytes=1048576,
    )
    with TemporaryDirectory(prefix="drc_rt3c3_gate_") as temporary:
        store = VoiceInputStagingStore(root_dir=Path(temporary), config=config)
        app = FastAPI()
        app.include_router(voice_input_demo.router)
        body = generated_wav()
        headers = {
            "Content-Type": "audio/wav",
            "X-DRC-Audio-Format": "wav",
            "X-DRC-Sample-Rate-Hz": "16000",
            "X-DRC-Channel-Count": "1",
            "X-DRC-Duration-Ms": "3000",
        }
        with (
            patch.object(voice_input_demo, "load_config", return_value=config),
            patch.object(
                voice_input_demo,
                "_create_voice_input_staging_store",
                return_value=store,
            ),
            TestClient(app) as client,
        ):
            response = client.post(
                "/demo/voice-input/staging",
                content=body,
                headers=headers,
            )

        if response.status_code != 201:
            raise AssertionError(f"Synthetic staging failed: {response.status_code}")
        payload = response.json()
        staging_id = payload.get("staging_id")
        if not isinstance(staging_id, str) or re.fullmatch(r"[0-9a-f]{32}", staging_id) is None:
            raise AssertionError("Synthetic staging did not return an opaque ID.")
        if payload.get("byte_count") != len(body):
            raise AssertionError("Synthetic staging byte count mismatch.")
        public_text = repr(payload).lower()
        if str(temporary).lower() in public_text or ".wav" in public_text or "riff" in public_text:
            raise AssertionError("Synthetic response exposed private artifact data.")
        if not store.has_artifact(staging_id):
            raise AssertionError("Synthetic staged artifact is missing.")
        if not store.discard(staging_id):
            raise AssertionError("Synthetic staged artifact cleanup failed.")
        if store.artifact_count() != 0:
            raise AssertionError("Synthetic staging cleanup left an artifact.")


def main() -> None:
    assert_changed_surface()
    assert_protected_surface()
    validate_backend_route()
    validate_flutter_consumer()
    validate_docs()
    run_synthetic_backend_smoke()

    print("v300_rt3c3_guarded_upload_flutter_staging_consumer_status: completed-accepted")
    print(f"v300_rt3c3_drc_source_commit: {SOURCE_COMMIT}")
    print(f"v300_rt3c3_drc_archive_sha256: {SOURCE_ARCHIVE_SHA256}")
    print("v300_rt3c3_guarded_upload_route_added: True")
    print("v300_rt3c3_streamed_request_body_added: True")
    print("v300_rt3c3_multipart_dependency_added: False")
    print("v300_rt3c3_flutter_scoped_consumer_added: True")
    print("v300_rt3c3_private_path_exposed: False")
    print("v300_rt3c3_path_free_staging_handle_added: True")
    print("v300_rt3c3_synthetic_upload_smoke_passed: True")
    print("v300_rt3c3_real_microphone_audio_read: False")
    print("v300_rt3c3_operator_audio_uploaded: False")
    print("v300_rt3c3_framework_imported: False")
    print("v300_rt3c3_voice_input_session_created: False")
    print("v300_rt3c3_provider_execution_executed: False")
    print("v300_rt3c3_stt_executed: False")
    print("v300_rt3_parent_status: current-blocked-real-provider-execution-not-implemented")
    print("v300_rt3c_parent_status: current-pending-rt3c4-implementation")
    print("v300_rt3c3_status: completed-accepted")
    print("v300_rt3c3_implementation: completed-accepted")
    print("v300_rt3c4_status: current-not-completed")
    print("v300_rt3c4_implementation: not-started")
    print("v300_rt3c4_authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only")
    print("v300_rt3_real_acceptance: blocked-framework-real-provider-execution-not-implemented")


if __name__ == "__main__":
    main()
