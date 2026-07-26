"""Validate the RT-0b released Framework public-contract readiness review.

This gate is credential-free and source-tree-only. It does not clone/import AI
Character Framework, call GitHub, read private env files, call a provider, open
a microphone, or start a realtime session. It verifies the accepted RT-0a DRC
baseline remains unchanged and that the RT-0b documents record the reviewed
v5.0.0 public snapshot, readiness matrix, integration feedback, and blocking
decision consistently.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

FRAMEWORK_RELEASE = "v5.0.0"
FRAMEWORK_COMMIT = "6494da306015c4f714f869b43e773ba51a2478a2"

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
    "docs/v300_realtime_current_behavior_inventory.md": "6a84df2b6172e5ac06dec448d11e26b2f29abba72b702d2793dfda7e4d49495d",
    "scripts/check_v300_realtime_current_behavior_inventory.py": "38430a816b053a118b2e6f2db8db2cb05364f7b037dbb3e425a28a57f39a185e",
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
                f"RT-0b protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-0b protected file changed: {relative}: {actual} != {expected}"
            )


def main() -> None:
    readiness = read("docs/v300_framework_realtime_contract_readiness.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    planning_sources = {
        "readiness": readiness,
        "checklist": checklist,
        "README": readme,
        "roadmap": roadmap,
        "tasklist": tasklist,
        "scripts README": scripts_readme,
    }
    for label, source in planning_sources.items():
        require(source, "RT-0b", f"{label} RT-0b marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} accepted RT-0b state")
        require(source, "RT-0c", f"{label} RT-0c marker")
        require(source, "BLOCKED_FRAMEWORK_UPDATE_REQUIRED", f"{label} Framework block decision")
        assert_no_sensitive_values(label, source)

    require(checklist, "RT-0a  COMPLETED / ACCEPTED", "accepted RT-0a state")
    require(checklist, "RT-0c  CURRENT / NOT_COMPLETED", "current RT-0c state")
    require(checklist, "NOT_STARTED", "RT-0c implementation state")
    require(checklist, "RT-1 through RT-9 remain blocked", "post-RT-0b block rule")
    require(tasklist, "RT-1 authorization: BLOCKED pending RT-0c and a released Framework update", "tasklist RT-1 block")
    require(roadmap, "RT-1   BLOCKED", "roadmap RT-1 blocked state")

    require(readiness, f"Released line: {FRAMEWORK_RELEASE}", "Framework release")
    require(readiness, f"Inspected public-source commit: {FRAMEWORK_COMMIT}", "Framework commit")
    for public_symbol in (
        "create_text_chat_session",
        "create_voice_output_session",
        "TextChatSession",
        "VoiceOutputSession",
        "VoiceOutputRequest",
        "VoiceOutputResult",
    ):
        require(readiness, public_symbol, f"released public symbol {public_symbol}")

    for absent_symbol in (
        "create_voice_input_session",
        "create_realtime_session",
        "create_motion_session",
        "RealtimeCapabilities",
    ):
        require(readiness, absent_symbol, f"missing public symbol record {absent_symbol}")

    for classification in (
        "READY_CURRENT_USE",
        "PARTIAL_BLOCKING",
        "MISSING_BLOCKING",
        "DEFECT_BLOCKING",
    ):
        require(readiness, classification, f"readiness classification {classification}")

    for required_gap in (
        "Voice-input / STT session",
        "Unified realtime session",
        "Provider-level cancellation",
        "TTS queue / cancel / flush",
        "Motion-event / VTS adapter",
        "Installable SDK import",
        "Session close/dispose",
    ):
        require(readiness, required_gap, f"required readiness row {required_gap}")

    require(readiness, "README example: session.speak", "public docs method example")
    require(readiness, "implementation: VoiceOutputSession.create_output", "implemented method")
    require(readiness, "pyproject.toml: absent", "pyproject absence record")
    require(readiness, "setup.py: absent", "setup.py absence record")
    require(readiness, "setup.cfg: absent", "setup.cfg absence record")

    for feedback_id in range(1, 13):
        require(readiness, f"FW-F{feedback_id}", f"Framework feedback FW-F{feedback_id}")

    require(readiness, "RT-1 implementation authorization: BLOCKED_PENDING_RT-0c_AND_RELEASED_FW_UPDATE", "RT-1 authorization marker")
    require(readiness, "DRC runtime changed: false", "DRC runtime non-change")
    require(readiness, "Framework runtime changed: false", "Framework runtime non-change")
    require(readiness, "Real provider execution: false", "provider non-execution")
    require(readiness, "Acceptance date: 2026-07-26", "RT-0b acceptance date")
    require(readiness, "Backend pytest: 110 passed", "RT-0b Backend acceptance result")
    require(readiness, "Flutter test: 103 passed", "RT-0b Flutter acceptance result")
    require(readiness, "explicit operator approval: received", "RT-0b operator approval")

    text_live = read("backend/app/services/framework_text_chat_drc_live_reply.py")
    text_import = read("backend/app/services/framework_text_chat_import_setup.py")
    voice_adapter = read("backend/app/services/framework_voice_output_adapter.py")

    require(text_live, "with _temporary_cwd(project_root):", "temporary CWD workaround")
    require(text_live, "inspect.signature(create_session)", "factory signature inspection")
    require(text_import, "sys.path", "text import path workaround")
    require(voice_adapter, "sys.path.insert", "voice import path workaround")
    require(voice_adapter, "sys.modules", "voice module cache workaround")
    require(voice_adapter, "importlib.invalidate_caches", "voice cache invalidation")
    require(voice_adapter, '"create_output"', "current FW voice-output method")

    pubspec = read("app/pubspec.yaml")
    for forbidden_runtime_marker in (
        "speech_to_text:",
        "permission_handler:",
        "flutter_sound:",
    ):
        forbid(pubspec, forbidden_runtime_marker, "new microphone dependency")

    assert_hashes()

    print("v300_framework_realtime_contract_readiness_status: completed-accepted")
    print(f"v300_framework_release_snapshot: {FRAMEWORK_RELEASE}@{FRAMEWORK_COMMIT}")
    print("v300_framework_public_readiness: blocked-framework-update-required")
    print("v300_framework_required_contracts_ready: False")
    print("v300_rt0b_drc_runtime_changed: False")
    print("v300_rt0b_existing_tests_changed: False")
    print("v300_rt0b_framework_runtime_changed: False")
    print("v300_rt0b_real_provider_execution: False")
    print("v300_rt1_authorization: blocked-pending-rt0c-and-released-fw-update")


if __name__ == "__main__":
    main()
