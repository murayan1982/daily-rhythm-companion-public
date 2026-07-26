"""Validate the RT-0a v3.0.0 realtime current behavior inventory.

This gate is credential-free and source-tree-only. It verifies that the RT-0a
planning documents agree with the inspected v2.1.0 implementation while
protecting Backend/Flutter runtime, existing tests, platform metadata, version
metadata, and immutable release records from change.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

TREE_HASHES = {
    "backend/app": "132cad8af5c960af8a1bbe8e29b566eb55effa0f00069a6ee72282fc4328f662",
    "backend/tests": "ea6f1444ef37a46c357849afa38d729120d66bef13199d63e9421ca810aab814",
    "app/lib": "2cdc0fb035e6082ac918ba59bc8b4e66219632e37f180cb31abcfd524adc0b2c",
    "app/test": "6fa480f5c17a0588d16bfcd4ac200fa7ff3d257138b7309cc4554edb9bc411de",
    "release_notes": "709652f31c775a9d48bb28b88acc765ee330fb0c40ae4ce611be8b6d0ea78ac5",
}

FILE_HASHES = {
    "app/pubspec.yaml": "baa60adac069f8543cf122e3e1c34179c6712ae5ca3c021e0369bb35f7d83bbd",
    "app/android/app/src/main/AndroidManifest.xml": "9e26a5f2b6e049418386f34ba1e460ce66e23a927b6d19bf339987ebf7a7f36d",
    "app/ios/Runner/Info.plist": "2bc30e544d40a83db2e2022bc690e5fcef62c591afe105087fa260f42115c556",
    "backend/.env.example": "c6936adcf1af839f6b5ed3c596395baa2a16eca5104a3015f9a392787234d45a",
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/DRC_v210_goal_checklist_small_commit.md": "a953165821c38b2671affcdbb0bc427233dabf5c00320d7c7f19ee939a688018",
    "docs/v210_release_record.md": "de7e83b9cd9d21bbd61805a0a09c0039c90b7a85ce9f25512e760fd0bcb562a1",
    "build_v210_fixed_release_zip_from_head.ps1": "434011e1ed8680a1619db845c8eda9d462d78956ed0d1d1e734c06f18c6d2f6d",
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
    candidates = (candidate for candidate in base.rglob("*") if candidate.is_file())
    for path in sorted(
        candidate
        for candidate in candidates
        if "__pycache__" not in candidate.parts
        and candidate.suffix.lower() not in {".pyc", ".pyo"}
    ):
        name = path.relative_to(ROOT).as_posix().encode("utf-8")
        digest.update(name)
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
                f"RT-0a protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-0a protected file changed: {relative}: {actual} != {expected}"
            )


def main() -> None:
    inventory = read("docs/v300_realtime_current_behavior_inventory.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    planning_sources = {
        "inventory": inventory,
        "checklist": checklist,
        "README": readme,
        "roadmap": roadmap,
        "tasklist": tasklist,
        "scripts README": scripts_readme,
    }
    for label, source in planning_sources.items():
        require(source, "RT-0a", f"{label} RT-0a marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} RT-0a accepted state")
        require(source, "RT-0b", f"{label} RT-0b marker")
        require(source, "CURRENT / NOT_COMPLETED", f"{label} RT-0b active state")
        require(source, "NOT_STARTED", f"{label} RT-0b implementation state")

    require(checklist, "RT-0c  PLANNED", "RT-0c planned state")
    require(checklist, "RT-0a implementation did not start RT-0b", "small-commit stop rule")
    require(inventory, "Acceptance date: 2026-07-26", "RT-0a acceptance date")
    require(inventory, "Backend pytest: 110 passed", "RT-0a Backend acceptance result")
    require(inventory, "Flutter test: 103 passed", "RT-0a Flutter acceptance result")
    require(inventory, "diff review / explicit operator approval: passed", "RT-0a approval result")
    require(inventory, "Runtime changed: false", "runtime non-change marker")
    require(inventory, "Existing tests changed: false", "test non-change marker")
    require(inventory, "RT-1 implementation authorization: BLOCKED_PENDING_RT-0b_AND_RT-0c", "RT-1 block marker")
    require(tasklist, "## RT-0 — v3.0.0 prerequisite and current behavior review", "active RT-0 section")
    forbid(tasklist, "## R-1 — v2.1.0 aggregate readiness and release preparation\n\nStatus: CURRENT / NOT_COMPLETED", "stale R-1 current marker")
    require(tasklist, "Status: COMPLETED / ACCEPTED", "historical R-1 completed state")

    voice_service = read("backend/app/services/voice_input_demo_service.py")
    voice_model = read("backend/app/models/voice_input_demo.py")
    voice_api = read("backend/app/api/voice_input_demo.py")
    motion_service = read("backend/app/services/motion_demo_service.py")
    motion_model = read("backend/app/models/motion_demo.py")
    motion_probe = read("backend/app/services/motion_boundary_probe.py")
    main_app = read("backend/app/main.py")
    text_live = read("backend/app/services/framework_text_chat_drc_live_reply.py")
    text_import = read("backend/app/services/framework_text_chat_import_setup.py")
    voice_adapter = read("backend/app/services/framework_voice_output_adapter.py")
    backend_client = read("app/lib/services/backend_api_client.dart")
    presentation = read("app/lib/models/character_display_presentation.dart")
    player = read("app/lib/services/voice_output_audio_player.dart")
    pubspec = read("app/pubspec.yaml")
    android_manifest = read("app/android/app/src/main/AndroidManifest.xml")
    ios_plist = read("app/ios/Runner/Info.plist")

    for marker in (
        "accepted=False",
        'request_state="not_started"',
        "transcript=None",
        "does not import",
        "open microphones",
        "speech recognition",
        "realtime sessions",
    ):
        require(voice_service, marker, "voice-input guarded boundary")
    require(voice_model, "audio_reference", "metadata-only audio reference field")
    require(voice_api, "does not\n    process audio yet", "voice-input API placeholder statement")

    for marker in (
        "accepted=False",
        'request_state="not_started"',
        "motion_sent=False",
        "vts_connection_used=False",
        "VTube Studio WebSocket",
    ):
        require(motion_service + motion_model + motion_probe, marker, "motion guarded boundary")

    require(text_live, "return ask(prompt)", "full-response Framework ask path")
    require(text_live, "with _temporary_cwd(project_root):", "temporary CWD workaround")
    require(text_import, "sys.path", "Framework text import path workaround")
    require(voice_adapter, "sys.path.insert", "Framework voice import path workaround")
    require(voice_adapter, "sys.modules", "Framework voice module cache workaround")
    require(voice_adapter, "importlib.invalidate_caches", "Framework voice cache invalidation")

    for forbidden_transport in ("WebSocket", "StreamingResponse", "UploadFile", "EventSource"):
        forbid(main_app + backend_client, forbidden_transport, "wired realtime transport")
    for marker in ("/demo/voice-input", "/demo/voice-output", "/demo/motion"):
        require(backend_client, marker, "HTTP demo route")
    require(backend_client, "http.post", "HTTP request/response client")

    for state in ("idle", "loading", "speaking"):
        require(presentation, state, f"character activity state {state}")
    for absent_state in ("listening", "transcribing", "interrupted", "reconnecting"):
        forbid(presentation, absent_state, f"unimplemented realtime presentation state {absent_state}")

    for phase in ("idle", "loading", "playing", "stopped", "completed", "failed", "expired"):
        require(player, phase, f"voice playback phase {phase}")
    require(player, "await _engine.stop();", "local audio stop")
    forbid(player, "barge", "barge-in implementation")

    for dependency in ("record:", "permission_handler:", "flutter_sound:", "speech_to_text:"):
        forbid(pubspec, dependency, "microphone dependency")
    forbid(android_manifest, "android.permission.RECORD_AUDIO", "Android microphone permission")
    forbid(ios_plist, "NSMicrophoneUsageDescription", "iOS microphone usage description")

    require(read("backend/app/version.py"), 'APP_VERSION = "2.1.0"', "Backend version baseline")
    require(pubspec, "version: 2.1.0+3", "Flutter version baseline")

    for relative, source in (
        ("docs/v300_realtime_current_behavior_inventory.md", inventory),
        ("docs/DRC_v300_goal_checklist_small_commit.md", checklist),
        ("README.md", readme),
        ("roadmap.md", roadmap),
        ("tasklist.md", tasklist),
        ("scripts/README.md", scripts_readme),
    ):
        assert_no_sensitive_values(relative, source)

    assert_hashes()

    print("v300_realtime_current_behavior_inventory_status: completed-accepted")
    print("v300_rt0a_runtime_changed: False")
    print("v300_rt0a_existing_tests_changed: False")
    print("v300_rt0a_microphone_used: False")
    print("v300_rt0a_realtime_session_started: False")
    print("v300_rt1_authorization: blocked-pending-rt0b-and-rt0c")


if __name__ == "__main__":
    main()
