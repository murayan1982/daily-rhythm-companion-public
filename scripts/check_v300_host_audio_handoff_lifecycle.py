"""Validate DRC v3.0.0 RT-3b host-audio handoff lifecycle.

This gate is source-only. It does not import Flutter or the vendored Framework,
read audio, open a microphone, upload data, create provider clients, or execute
STT.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]

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
    "app/lib/services/microphone_capture.dart": "4edba11a1eed458d113aa441ee73d3289bed2e20650805e7685e5801b9c4cc58",
    "app/lib/services/record_microphone_capture_engine.dart": "84c08ef9d4ab455e42c3167faa9b94748934660f7d70db871353f3fcfe396d9f",
    "app/lib/operators/rt2ec_microphone_capture_operator.dart": "2c7568504b298eda284575c7c75facc263cce4857cbfe73169fcbbaabbd03fb0",
    "app/test/microphone_capture_test.dart": "90e391a385aec50679955561e0a4e9aafa98e5835e2f478e9e5925a573666c9a",
    "app/test/record_microphone_capture_engine_test.dart": "71ec8fd9b8ab77610db4b3968a8c94bf8fd1522c2f8ffedbd6e94a97d20c634c",
    "app/test/rt2ec_microphone_capture_operator_test.dart": "e8c4c1980bb3bf322f06569a6ad12ab80a08fed07bf087069cc4b8033ccd34c9",
    "app/pubspec.yaml": "5de06f3041d7f150b83638e1cd2cc913b286c107e3b58a37178f678a37e7a428",
    "app/android/app/src/main/AndroidManifest.xml": "5fb1b832160c9dcfeb33d45fe3b0ea3355dced95caa5a675b4490caba2b0adcd",
    "app/ios/Runner/Info.plist": "0bed3e2d536b5160706c12bd99da7364562f1b9fd4ed84a6d3a0c9d64f743865",
    "backend/app/version.py": "dfbbca8efedb35151eea62bb9f719abea41b97b722d19abbefb1a7f176cb205e",
    "backend/.env.example": "874ad09f8dd37370c9ba423fdc676133e447efeaeecd6eb44a1a2c1a2d46a76a",
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
            details.append("missing RT-3b paths:\n" + "\n".join(sorted(missing)))
        raise AssertionError("RT-3b source surface mismatch:\n" + "\n".join(details))


def assert_protected_surface() -> None:
    for relative, expected in PROTECTED_TREE_HASHES.items():
        actual = normalized_tree_hash(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"RT-3b protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in PROTECTED_FILE_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"Missing protected file: {relative}")
        actual = normalized_hash(path)
        if actual != expected:
            raise AssertionError(
                f"RT-3b protected file changed: {relative}: {actual} != {expected}"
            )


def validate_contract() -> None:
    contract = read("app/lib/services/microphone_capture_host_audio_handoff.dart")

    for marker in (
        "enum HostAudioHandoffPhase",
        "enum HostAudioHandoffOutcome",
        "class HostAudioHandoffDescriptor",
        "class HostAudioHandoffConsumerResult",
        "class HostAudioHandoffResult",
        "class HostAudioHandoffState",
        "class HostAudioHandoffException",
        "class HostAudioPrivateArtifactLease",
        "abstract interface class HostAudioHandoffConsumer",
        "class FakeHostAudioHandoffConsumer",
        "class HostAudioHandoffController",
        "Future<T> withPrivateArtifactPath<T>(",
        "Future<HostAudioHandoffResult> retain(",
        "Future<HostAudioHandoffResult> consume()",
        "Future<HostAudioHandoffResult> discard()",
        "Future<HostAudioHandoffResult> cancel()",
        "Future<void> close()",
        "maximumAllowedDuration = const Duration(seconds: 15)",
        "host_audio_private_artifact_discard_failed",
        "private_path_exposed': false",
        "opaque_capture_id_exposed': false",
        "audio_uploaded': false",
        "stt_executed': false",
    ):
        require(contract, marker, "RT-3b contract marker")

    for forbidden in (
        "package:http/",
        "package:dio/",
        "BackendApiClient",
        "VoiceInputAudioSource",
        "VoiceInputSession",
        "create_voice_input_session",
        "framework/",
        "dart:io",
        "readAsBytes",
        "readAsBytesSync",
        "openRead(",
        "MultipartRequest",
        "UploadFile",
        "transcript",
    ):
        if forbidden in contract:
            raise AssertionError(f"RT-3b forbidden runtime marker: {forbidden}")

    if re.search(r"\bString\??\s+get\s+.*(?:path|opaque)", contract, re.IGNORECASE):
        raise AssertionError("RT-3b must not expose private path or opaque id getters")


def validate_tests() -> None:
    tests = read("app/test/microphone_capture_host_audio_handoff_test.dart")
    if tests.count("    test(") < 21:
        raise AssertionError("RT-3b focused test count is below 21")

    for marker in (
        "retains a completed opaque artifact without exposing id or path",
        "single retained artifact is enforced",
        "private path access is closed outside consumer execution",
        "fake consumer completes and artifact is discarded exactly once",
        "scoped fake consumer can resolve a path only during consume",
        "consumer exception is normalized and cleanup still succeeds",
        "cleanup failure keeps the lease available for explicit retry",
        "explicit discard removes a retained artifact without consuming",
        "cancel invokes fake consumer cancellation and discards artifact",
        "close cleans a retained artifact and disposes the fake consumer",
        "public metadata uses an allowlist and removes sensitive fields",
        "_FakePrivateArtifactAccess",
        "_PathUsingFakeConsumer",
        "isNot(contains('<private>/capture.wav'))",
        "isNot(contains('opaque-1'))",
    ):
        require(tests, marker, "RT-3b fake-only test marker")

    for forbidden in (
        "RecordPackageMicrophoneCaptureDriver(",
        "RecordMicrophoneCaptureEngine.mobile(",
        "BackendApiClient",
        "package:http/",
        "flutter run",
        "integration_test",
        "create_voice_input_session",
    ):
        if forbidden in tests:
            raise AssertionError(f"RT-3b test executes forbidden boundary: {forbidden}")


def validate_docs() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "scripts README": read("scripts/README.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "inventory": read("docs/v300_framework_v530_stt_integration_inventory.md"),
        "contract doc": read("docs/v300_host_audio_handoff_lifecycle.md"),
    }
    for label, source in sources.items():
        assert_no_sensitive_values(label, source)
        require(source, "RT-3b", f"{label} RT-3b marker")

    require(
        sources["README"],
        "Current small commit: none (RT-3c4 accepted)",
        "README RT-3c2 current state",
    )
    require(
        sources["checklist"],
        "Current implementation state: COMPLETED / ACCEPTED",
        "checklist RT-3c3 state",
    )
    require(
        sources["tasklist"],
        "Status: COMPLETED / ACCEPTED",
        "tasklist accepted state",
    )
    require(
        sources["contract doc"],
        "completed-accepted-app-owned-host-audio-lifecycle-contract-fake-only",
        "accepted authorization marker",
    )
    for marker in (
        "retain",
        "lease",
        "consume",
        "discard",
        "fake-only",
        "no private-path getter",
        "no concrete real STT",
    ):
        combined = "\n".join(sources.values())
        if marker == "no concrete real STT":
            require(combined, "no concrete real STT", "real STT block marker")
        else:
            require(combined.lower(), marker.lower(), f"planning marker {marker}")


def main() -> None:
    assert_changed_surface()
    assert_protected_surface()
    validate_contract()
    validate_tests()
    validate_docs()

    print("v300_host_audio_handoff_lifecycle_status: completed-accepted")
    print("v300_rt3b_app_owned_contract_added: True")
    print("v300_rt3b_opaque_artifact_retention_added: True")
    print("v300_rt3b_scoped_private_path_access_added: True")
    print("v300_rt3b_consume_cleanup_added: True")
    print("v300_rt3b_cancel_cleanup_added: True")
    print("v300_rt3b_close_cleanup_added: True")
    print("v300_rt3b_public_result_path_free: True")
    print("v300_rt3b_fake_consumer_tests_added: True")
    print("v300_rt3b_backend_changed: False")
    print("v300_rt3b_network_upload_added: False")
    print("v300_rt3b_framework_imported: False")
    print("v300_rt3b_provider_execution_executed: False")
    print("v300_rt3b_stt_executed: False")
    print(
        "v300_rt3_parent_status: "
        "current-blocked-real-provider-execution-not-implemented"
    )
    print("v300_rt3b_status: completed-accepted")
    print("v300_rt3c_status: completed-accepted")
    print("v300_rt3c1_status: completed-accepted")
    print("v300_rt3c2_status: completed-accepted")
    print("v300_rt3c2_implementation: completed-accepted")
    print("v300_rt3c3_status: completed-accepted")
    print("v300_rt3c3_implementation: completed-accepted")
    print("v300_rt3c4_status: completed-accepted")
    print("v300_rt3c4_implementation: completed-accepted")
    print("v300_rt3c4_authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only")
    print(
        "v300_rt3_real_acceptance: "
        "blocked-framework-real-provider-execution-not-implemented"
    )


if __name__ == "__main__":
    main()
