"""Validate RT-1b DRC Backend realtime models and Framework normalization.

This gate is credential-free, provider-free, network-free, microphone-free, and
Framework-import-free. It validates DRC-owned models with local fake objects
only and protects routes, Flutter, platform permissions, version metadata, and
immutable release records from change.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TREE_HASHES = {
    "backend/app/api": "b6fe025d120f53ce4e5905ba5a978ff91abf7ed02eb6ac14a51645571ec4940a",
    "app/lib": "2cdc0fb035e6082ac918ba59bc8b4e66219632e37f180cb31abcfd524adc0b2c",
    "app/test": "6fa480f5c17a0588d16bfcd4ac200fa7ff3d257138b7309cc4554edb9bc411de",
    "release_notes": "709652f31c775a9d48bb28b88acc765ee330fb0c40ae4ce611be8b6d0ea78ac5",
}

FILE_HASHES = {
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/app/config.py": "ebe022db586ffbaaa6a37db2f43cddca218c4e1e91cee782ffd7b6c8e607d4a5",
    "backend/app/version.py": "dfbbca8efedb35151eea62bb9f719abea41b97b722d19abbefb1a7f176cb205e",
    "backend/.env.example": "c6936adcf1af839f6b5ed3c596395baa2a16eca5104a3015f9a392787234d45a",
    "app/pubspec.yaml": "baa60adac069f8543cf122e3e1c34179c6712ae5ca3c021e0369bb35f7d83bbd",
    "app/android/app/src/main/AndroidManifest.xml": "9e26a5f2b6e049418386f34ba1e460ce66e23a927b6d19bf339987ebf7a7f36d",
    "app/ios/Runner/Info.plist": "2bc30e544d40a83db2e2022bc690e5fcef62c591afe105087fa260f42115c556",
}

SENSITIVE_PATTERNS = (
    r"sk-[A-Za-z0-9_\-]{12,}",
    r"xai-[A-Za-z0-9_\-]{12,}",
    r"AIza[0-9A-Za-z_\-]{20,}",
    r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
    r"[A-Za-z]:\\Users\\[^<\r\n]+",
    r"192\.168\.\d{1,3}\.\d{1,3}",
)


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def normalized_hash(relative: str) -> str:
    return sha256(normalized_bytes(ROOT / relative)).hexdigest()


def normalized_tree_hash(relative: str) -> str:
    base = ROOT / relative
    if not base.is_dir():
        raise AssertionError(f"Missing required directory: {relative}")
    digest = sha256()
    for path in sorted(
        candidate
        for candidate in base.rglob("*")
        if candidate.is_file()
        and "__pycache__" not in candidate.parts
        and candidate.suffix.lower() not in {".pyc", ".pyo"}
    ):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(normalized_bytes(path))
        digest.update(b"\0")
    return digest.hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def assert_hashes() -> None:
    for relative, expected in TREE_HASHES.items():
        actual = normalized_tree_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-1b protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-1b protected file changed: {relative}: {actual} != {expected}"
            )


def assert_source_contract() -> None:
    model = read("backend/app/models/realtime.py")
    normalizer = read("backend/app/services/framework_realtime_normalizer.py")
    tests = read("backend/tests/test_framework_realtime_normalizer.py")
    doc = read("docs/v300_backend_realtime_normalization.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    for symbol in (
        "class RealtimeState",
        "class RealtimeEventType",
        "class RealtimeCapabilityStatus",
        "class RealtimeCapabilities",
        "class RealtimeEvent",
        "class RealtimeSessionSnapshot",
    ):
        require(model, symbol, f"DRC model {symbol}")

    for marker in (
        "class FrameworkRealtimeContractNormalizer",
        "def normalize_event",
        "def normalize_capabilities",
        "def normalize_session",
        "Session-specific v5.2.0 metadata takes precedence",
        "_sanitize_mapping",
        "RealtimeEventType.UNKNOWN",
    ):
        require(normalizer, marker, f"normalizer marker {marker}")

    for forbidden_import in ("import framework", "from framework"):
        forbid(model, forbidden_import, "Framework model import")
        forbid(normalizer, forbidden_import, "Framework normalizer import")

    for forbidden_runtime in (
        "FastAPI",
        "APIRouter",
        "WebSocket",
        "StreamingResponse",
        "UploadFile",
        "microphone",
        "speech_recognition",
        "sounddevice",
    ):
        forbid(model + normalizer, forbidden_runtime, "RT-1b runtime wiring")

    require(tests, "test_session_specific_v520_info_overrides_stale_global_snapshot", "stale snapshot regression")
    require(tests, "test_public_metadata_redacts_sensitive_keys_and_opaque_objects", "metadata safety regression")
    require(tests, "test_normalizer_module_does_not_require_framework_package", "Framework-free regression")

    sources = {
        "doc": doc,
        "checklist": checklist,
        "README": readme,
        "roadmap": roadmap,
        "tasklist": tasklist,
        "scripts README": scripts_readme,
    }
    for label, source in sources.items():
        require(source, "RT-1b", f"{label} RT-1b marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} accepted state")
        assert_no_sensitive_values(label, source)

    for marker in (
        "public_contract_released",
        "mock_contract_available",
        "real_runtime_supported",
        "real_runtime_configured",
        "real_runtime_available",
        "Framework import: false",
        "API route added: false",
        "microphone used: false",
        "realtime runtime started: false",
    ):
        require(doc + checklist, marker, f"RT-1b boundary {marker}")


def assert_runtime_contract() -> None:
    framework_before = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }

    from app.models.realtime import RealtimeEventType, RealtimeState
    from app.services.framework_realtime_normalizer import (
        FrameworkRealtimeContractNormalizer,
    )

    normalizer = FrameworkRealtimeContractNormalizer()
    realtime_info = SimpleNamespace(
        session_type="realtime",
        session_id="rt1b-session",
        state="idle",
        supports_run_turn=True,
        supports_interrupt=True,
        supports_output_flush=True,
        supports_barge_in_policy=True,
        real_runtime_enabled=False,
        hard_cancel_supported=False,
        tts_queue_flush_supported=False,
        public_metadata={"boundary": "realtime"},
    )
    event = normalizer.normalize_event(
        {
            "type": "realtime.turn.started",
            "state": "listening",
            "turn_id": "rt1b-turn",
            "session_id": "rt1b-session",
            "public_metadata": {"api_key": "must-redact", "safe": "ok"},
        }
    )
    capabilities = normalizer.normalize_capabilities(realtime_info=realtime_info)
    session = normalizer.normalize_session(realtime_info, capabilities=capabilities)

    if event.event_type is not RealtimeEventType.TURN_STARTED:
        raise AssertionError("RT-1b event type normalization failed")
    if event.state is not RealtimeState.LISTENING:
        raise AssertionError("RT-1b state normalization failed")
    if event.public_metadata.get("api_key") != "<redacted>":
        raise AssertionError("RT-1b metadata redaction failed")
    if not capabilities.realtime.public_contract_released:
        raise AssertionError("RT-1b realtime public contract was not recognized")
    if capabilities.realtime.real_runtime_available:
        raise AssertionError("RT-1b incorrectly marked real realtime runtime available")
    if session.session_id != "rt1b-session" or session.is_closed:
        raise AssertionError("RT-1b session normalization failed")

    framework_after = {
        name for name in sys.modules if name == "framework" or name.startswith("framework.")
    }
    if framework_after != framework_before:
        raise AssertionError("RT-1b imported AI Character Framework unexpectedly")


def main() -> None:
    assert_source_contract()
    assert_runtime_contract()
    assert_hashes()

    print("v300_backend_realtime_normalization_status: completed-accepted")
    print("v300_rt1b_backend_models_added: True")
    print("v300_rt1b_framework_imported: False")
    print("v300_rt1b_api_route_added: False")
    print("v300_rt1b_microphone_used: False")
    print("v300_rt1b_provider_execution: False")
    print("v300_rt1b_realtime_runtime_started: False")
    print("v300_rt1_parent_status: completed-accepted")
    print("v300_rt2_authorization: authorized-guarded-capture-planning-only")


if __name__ == "__main__":
    main()
