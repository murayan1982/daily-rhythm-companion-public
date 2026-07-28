"""Validate DRC v3.0.0 RT-3c4 fake FW public-session handoff.

The gate uses generated WAV bytes in a temporary DRC staging root and imports
only the configured FW v5.3.0 public package. It creates a public voice-input
session with ``FakeVoiceInputProviderAdapter``. It does not read a real audio
artifact, open a microphone, create a provider client, or execute real STT.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import AppConfig  # noqa: E402
from app.services.framework_voice_input_fake_handoff import (  # noqa: E402
    FrameworkVoiceInputFakeHandoffAdapter,
    FrameworkVoiceInputFakeHandoffError,
    FrameworkVoiceInputFakeHandoffRequest,
)
from app.services.voice_input_staging_store import VoiceInputStagingStore  # noqa: E402

SOURCE_COMMIT = "87ebbf1ad0722b4689311c4d7a2b8e982110efdc"
SOURCE_ARCHIVE_SHA256 = (
    "B3A44AE494F7CE0F19E4530CF615035DB3A6E049F96377EDD5000AA4B76FC75E"
)

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

PROTECTED_FILE_HASHES = {
    "backend/app/services/voice_input_staging_store.py": "84dd9febaacd185db4d9686cf4f9ffa68d3dd1ff8fbaad8172db49b21bc16659",
    "backend/app/config.py": "5bb4d4de13dc2979a59566c6d7cddfc6b7607cadc7e7b4f781218a9f2125f3ca",
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/.env.example": "874ad09f8dd37370c9ba423fdc676133e447efeaeecd6eb44a1a2c1a2d46a76a",
    "backend/requirements.txt": "e93eaa60004f5fcf0433ab170341da5fa2b1fdbe399fd4f96114ea1f3d7bb5d2",
    "backend/requirements-dev.txt": "8636f9ab1a075be9f3039e2a6471837259c4f36b625bcaf7a3d9a1edd2419c6d",
    "backend/app/version.py": "dfbbca8efedb35151eea62bb9f719abea41b97b722d19abbefb1a7f176cb205e",
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
    "app/pubspec.lock": "d9eed55039c9075b1b3744184ea3223f4ca030003e23be06852741024866b2eb",
    "app/lib/main.dart": "2513413c1e863e73b605c9110244596e109fdcfdd8ab2876c2cc60c531d30a2c",
    "app/lib/services/backend_voice_input_staging_consumer.dart": "8a779d9026115f49ce63db1616b9b46e2a2b4dcb72cb936b35953c3d2df186ea",
    "app/lib/services/microphone_capture_host_audio_handoff.dart": "0765b6d65f023ce8c9efee4b59fa45d29bd077c5acbe519e7c404ef94fb263fd",
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
            details.append("missing RT-3c4 paths:\n" + "\n".join(sorted(missing)))
        raise AssertionError("RT-3c4 source surface mismatch:\n" + "\n".join(details))


def assert_protected_surface() -> None:
    for relative, expected in PROTECTED_FILE_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing protected file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"RT-3c4 protected file changed: {relative}: {actual} != {expected}"
            )


def validate_backend_surface() -> None:
    service = read("backend/app/services/framework_voice_input_fake_handoff.py")
    api = read("backend/app/api/voice_input_demo.py")
    models = read("backend/app/models/voice_input_demo.py")
    service_tests = read("backend/tests/test_framework_voice_input_fake_handoff.py")
    api_tests = read("backend/tests/test_voice_input_fake_handoff_api.py")

    for needle, label in (
        ("class FrameworkVoiceInputFakeHandoffAdapter", "DRC adapter"),
        ("self._store.consume(", "single-use consume"),
        ("VoiceInputAudioFormat.wav(", "public WAV format"),
        ("VoiceInputAudioSource.from_file_path(", "public file source"),
        ("VoiceInputRequest(", "public request"),
        ("FakeVoiceInputProviderAdapter(", "explicit fake adapter"),
        ("create_voice_input_session(", "public session factory"),
        ("session.transcribe_audio_result(", "public session handoff"),
        ("session.close()", "session close"),
        ("real_stt_enabled=False", "real STT disabled"),
        ("allow_provider_execution=False", "provider execution disabled"),
        ("provider_execution_executed=False", "normalized provider non-execution"),
        ("stt_executed=False", "normalized real STT non-execution"),
    ):
        require(service, needle, label)

    for forbidden, label in (
        ("GuardedRealVoiceInputProviderAdapter", "guarded real adapter"),
        ("openai", "provider SDK"),
        ("google.cloud", "provider SDK"),
        ("speech_recognition", "STT SDK"),
    ):
        forbid(service.lower(), forbidden.lower(), label)

    require(
        api,
        '"/demo/voice-input/staging/{staging_id}/fake-handoff"',
        "guarded fake-handoff route",
    )
    require(api, "_require_staging_upload_enabled(config)", "existing route guards")
    require(api, "VoiceInputFakeHandoffResponse", "path-free API response")
    require(models, "class VoiceInputFakeHandoffRequest", "request model")
    require(models, "class VoiceInputFakeHandoffResponse", "response model")
    fake_response = models.split("class VoiceInputFakeHandoffResponse", 1)[1]
    forbid(fake_response, "staging_id: str", "response staging ID field")
    forbid(fake_response, "path: str", "response path field")

    for needle in (
        "test_fake_public_session_handoff_is_path_free_and_single_use",
        "test_fake_session_failure_closes_session_and_discards_artifact",
        "test_preflight_failure_preserves_artifact_for_retry",
        "test_unsafe_fake_result_is_rejected_and_artifact_is_discarded",
    ):
        require(service_tests, needle, f"service test {needle}")
    for needle in (
        "test_fake_handoff_returns_path_free_result_and_consumes_once",
        "test_fake_handoff_guard_failure_preserves_staged_artifact",
        "test_fake_handoff_framework_preflight_failure_preserves_artifact",
        "test_fake_handoff_callback_failure_is_safe_and_single_use",
    ):
        require(api_tests, needle, f"API test {needle}")


def validate_docs() -> None:
    docs = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "RT-3c4 doc": read("docs/v300_rt3c4_fake_fw_public_session_handoff.md"),
        "scripts README": read("scripts/README.md"),
    }
    for label, text in docs.items():
        require(text, "RT-3c4", f"{label} RT-3c4 marker")
        require(text, "COMPLETED / ACCEPTED", f"{label} accepted state")
        assert_no_sensitive_values(label, text)

    rt3c4 = docs["RT-3c4 doc"]
    require(rt3c4, SOURCE_COMMIT, "source commit")
    require(rt3c4, SOURCE_ARCHIVE_SHA256, "source archive hash")
    require(rt3c4, "FakeVoiceInputProviderAdapter used: yes", "fake adapter evidence")
    require(rt3c4, "FW session closed: yes", "session close evidence")
    require(rt3c4, "provider execution: no", "provider non-execution")
    require(rt3c4, "real STT execution: no", "real STT non-execution")


def generated_wav(payload_size: int = 24) -> bytes:
    return (
        b"RIFF"
        + (payload_size + 4).to_bytes(4, "little")
        + b"WAVE"
        + (b"\x00" * payload_size)
    )


def configured_framework_root() -> Path:
    configured = os.getenv("FRAMEWORK_ROOT") or os.getenv("FRAMEWORK_PROJECT_ROOT")
    if not configured:
        raise AssertionError("FRAMEWORK_ROOT/FRAMEWORK_PROJECT_ROOT is required for RT-3c4 gate.")
    root = Path(configured).expanduser().resolve()
    if not (root / "framework" / "__init__.py").is_file():
        raise AssertionError("Configured Framework root does not expose framework/__init__.py.")
    return root


def run_synthetic_public_handoff() -> None:
    framework_root = configured_framework_root()
    config = AppConfig(
        conversation_engine="framework",
        framework_project_root=str(framework_root),
        voice_input_demo_enabled=True,
        voice_input_adapter_mode="framework",
        voice_input_staging_ttl_seconds=300,
        voice_input_staging_max_count=8,
        voice_input_staging_max_bytes=1048576,
    )
    with TemporaryDirectory(prefix="drc_rt3c4_gate_") as temporary:
        store = VoiceInputStagingStore(root_dir=Path(temporary), config=config)
        staged = store.stage_chunks((generated_wav(),))
        result = FrameworkVoiceInputFakeHandoffAdapter(config, store).transcribe_staged_artifact(
            FrameworkVoiceInputFakeHandoffRequest(
                staging_id=staged.staging_id,
                language="ja-JP",
                duration_ms=4820,
            )
        )

        if result.status != "completed" or result.outcome != "completed":
            raise AssertionError("FW fake public handoff did not complete.")
        if result.adapter_name != "fake" or not result.fake_transcription_completed:
            raise AssertionError("FW fake adapter contract was not used.")
        if not result.session_closed or not result.staged_artifact_consumed:
            raise AssertionError("Session/staging cleanup contract did not complete.")
        if result.audio_read or result.microphone_accessed:
            raise AssertionError("Synthetic fake handoff unexpectedly accessed audio runtime.")
        if result.provider_execution_executed or result.stt_executed:
            raise AssertionError("Synthetic fake handoff unexpectedly executed provider/STT.")
        public_text = repr(result).lower()
        if staged.staging_id in public_text or str(temporary).lower() in public_text or ".wav" in public_text:
            raise AssertionError("Fake handoff result exposed private artifact data.")
        if store.artifact_count() != 0:
            raise AssertionError("Fake handoff left a staged artifact.")

        try:
            FrameworkVoiceInputFakeHandoffAdapter(config, store).transcribe_staged_artifact(
                FrameworkVoiceInputFakeHandoffRequest(staging_id=staged.staging_id)
            )
        except FrameworkVoiceInputFakeHandoffError as exc:
            if exc.code != "artifact_not_found":
                raise AssertionError(f"Unexpected second-use error: {exc.code}") from exc
        else:
            raise AssertionError("Single-use staged artifact was consumed twice.")


def main() -> None:
    assert_changed_surface()
    assert_protected_surface()
    validate_backend_surface()
    validate_docs()
    run_synthetic_public_handoff()

    print("v300_rt3c4_fake_fw_public_session_handoff_status: completed-accepted")
    print(f"v300_rt3c4_drc_source_commit: {SOURCE_COMMIT}")
    print(f"v300_rt3c4_drc_archive_sha256: {SOURCE_ARCHIVE_SHA256}")
    print("v300_rt3c4_framework_release: v5.3.0")
    print("v300_rt3c4_public_framework_imported: True")
    print("v300_rt3c4_public_file_audio_source_created: True")
    print("v300_rt3c4_public_voice_input_session_created: True")
    print("v300_rt3c4_fake_provider_adapter_used: True")
    print("v300_rt3c4_fake_transcript_completed: True")
    print("v300_rt3c4_public_result_path_free: True")
    print("v300_rt3c4_session_closed: True")
    print("v300_rt3c4_staged_artifact_single_use_cleanup: True")
    print("v300_rt3c4_preflight_failure_preserves_artifact: True")
    print("v300_rt3c4_real_microphone_audio_read: False")
    print("v300_rt3c4_provider_execution_executed: False")
    print("v300_rt3c4_real_stt_executed: False")
    print("v300_rt3_parent_status: current-blocked-real-provider-execution-not-implemented")
    print("v300_rt3c_parent_status: completed-accepted")
    print("v300_rt3c4_status: completed-accepted")
    print("v300_rt3c4_implementation: completed-accepted")
    print("v300_rt3d_authorization: blocked-framework-real-provider-execution-not-implemented")
    print("v300_rt3_real_acceptance: blocked-framework-real-provider-execution-not-implemented")


if __name__ == "__main__":
    main()
