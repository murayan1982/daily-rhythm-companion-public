"""Validate the RT-0c Framework v5.1.0 reassessment and DRC stop decision.

This gate is credential-free and source-tree-only. It does not import or clone
AI Character Framework, call GitHub, read private env files, call a provider,
open a microphone, or start a realtime session. It protects the accepted RT-0a
and RT-0b records and verifies the separately recorded v5.1.0 reassessment.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_RELEASE = "v5.1.0"
FRAMEWORK_TAG_COMMIT = "b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f"
FRAMEWORK_RELEASE_NOTE_COMMIT = "c08c7539e2109a3a9a77be1c54a02f6e3bf06c30"
FIXED_ZIP_SHA256 = "137f9f85602957b068881d8d26e34570bafa8e000c4a624fc19871b313612545"

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
    "backend/app/version.py": "dfbbca8efedb35151eea62bb9f719abea41b97b722d19abbefb1a7f176cb205e",
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/DRC_v210_goal_checklist_small_commit.md": "a953165821c38b2671affcdbb0bc427233dabf5c00320d7c7f19ee939a688018",
    "docs/v210_release_record.md": "de7e83b9cd9d21bbd61805a0a09c0039c90b7a85ce9f25512e760fd0bcb562a1",
    "build_v210_fixed_release_zip_from_head.ps1": "434011e1ed8680a1619db845c8eda9d462d78956ed0d1d1e734c06f18c6d2f6d",
    "docs/v300_realtime_current_behavior_inventory.md": "6a84df2b6172e5ac06dec448d11e26b2f29abba72b702d2793dfda7e4d49495d",
    "scripts/check_v300_realtime_current_behavior_inventory.py": "38430a816b053a118b2e6f2db8db2cb05364f7b037dbb3e425a28a57f39a185e",
    "docs/v300_framework_realtime_contract_readiness.md": "cf560a7664fdf1089254e22bfda8833b37038b261a655a7b10c8ffbd966770e3",
    "scripts/check_v300_framework_realtime_contract_readiness.py": "41623918be4c17f8d17265cb1516abf6392c15b0eb0a2691d3aa1385cfef82ee",
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


def assert_no_sensitive_values(relative: str, text: str) -> None:
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def assert_hashes() -> None:
    for relative, expected in TREE_HASHES.items():
        actual = normalized_tree_hash(relative)
        if actual != expected:
            raise AssertionError(f"RT-0c protected tree changed: {relative}: {actual} != {expected}")
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(f"RT-0c protected file changed: {relative}: {actual} != {expected}")


def main() -> None:
    reassessment = read("docs/v300_framework_v510_reassessment.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    planning_sources = {
        "reassessment": reassessment,
        "checklist": checklist,
        "README": readme,
        "roadmap": roadmap,
        "tasklist": tasklist,
        "scripts README": scripts_readme,
    }
    for label, source in planning_sources.items():
        require(source, "RT-0c", f"{label} RT-0c marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} accepted state")
        require(source, "v5.1.0", f"{label} Framework release")
        require(source, "BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING", f"{label} realtime block decision")
        assert_no_sensitive_values(label, source)

    require(reassessment, "Parent phase: RT-0 COMPLETED / ACCEPTED", "accepted RT-0 parent state")
    require(reassessment, "Small commit: RT-0c COMPLETED / ACCEPTED", "accepted RT-0c small commit state")
    require(reassessment, "Implementation state: COMPLETED / ACCEPTED", "accepted RT-0c implementation state")
    require(checklist, "Current parent phase: RT-0 COMPLETED / ACCEPTED", "accepted checklist parent state")
    require(checklist, "Current small commit: none", "no active small commit after RT-0c")
    require(checklist, "Completed small commit: RT-0c COMPLETED / ACCEPTED", "accepted RT-0c checklist state")
    require(checklist, "RT-0a  COMPLETED / ACCEPTED", "accepted RT-0a state")
    require(checklist, "RT-0b  COMPLETED / ACCEPTED", "accepted RT-0b state")
    require(checklist, "Historical RT-0b decision: BLOCKED_FRAMEWORK_UPDATE_REQUIRED", "historical RT-0b decision")
    require(checklist, "RT-1 through RT-5 remain blocked", "RT-1 through RT-5 block")
    require(checklist, "RT-6 through RT-7 remain", "RT-6 through RT-7 block")

    require(reassessment, f"Released tag: {FRAMEWORK_RELEASE}", "released Framework tag")
    require(reassessment, f"Tag commit: {FRAMEWORK_TAG_COMMIT}", "Framework tag commit")
    require(reassessment, f"Post-tag release-note commit: {FRAMEWORK_RELEASE_NOTE_COMMIT}", "release-note commit")
    require(reassessment, f"Fixed release ZIP SHA-256: {FIXED_ZIP_SHA256}", "fixed ZIP hash")

    for public_symbol in (
        "TextChatResult",
        "ask_result()",
        "CapabilityStatus",
        "FrameworkCapabilities",
        "get_capabilities",
        "VoiceOutputSession.speak()",
        "VoiceArtifactRef",
        "close()",
        "dispose()",
    ):
        require(reassessment, public_symbol, f"v5.1 public contract {public_symbol}")

    for feedback_id in range(1, 13):
        require(reassessment, f"FW-F{feedback_id}", f"Framework feedback FW-F{feedback_id}")

    for marker in (
        "RESOLVED_V510: FW-F4, FW-F5, FW-F7, FW-F8",
        "PARTIAL_V510: FW-F1, FW-F2, FW-F3, FW-F6",
        "MISSING_REALTIME_BLOCKER: FW-F9, FW-F10, FW-F11, FW-F12",
        "does not publish a wheel",
        "transition absolute imports",
        "TextChatSessionInfo.supports_close",
        "public_boundary_missing",
    ):
        require(reassessment, marker, f"reassessment finding {marker}")

    for missing_contract in (
        "create_voice_input_session",
        "create_realtime_session",
        "create_motion_session",
        "Hard cancellation / TTS queue / flush / barge-in",
    ):
        require(reassessment, missing_contract, f"missing realtime contract {missing_contract}")

    require(reassessment, "DRC runtime changed: false", "DRC runtime non-change")
    require(reassessment, "Framework runtime changed: false", "Framework runtime non-change")
    require(reassessment, "Real provider execution: false", "provider non-execution")

    assert_hashes()

    print("v300_framework_v510_reassessment_status: completed-accepted")
    print(f"v300_framework_release_snapshot: {FRAMEWORK_RELEASE}@{FRAMEWORK_TAG_COMMIT}")
    print("v300_framework_host_app_foundation: substantially-ready-with-transition-gaps")
    print("v300_framework_realtime_prerequisites_ready: False")
    print("v300_framework_feedback_resolved: FW-F4,FW-F5,FW-F7,FW-F8")
    print("v300_framework_feedback_partial: FW-F1,FW-F2,FW-F3,FW-F6")
    print("v300_framework_feedback_missing: FW-F9,FW-F10,FW-F11,FW-F12")
    print("v300_rt0c_drc_runtime_changed: False")
    print("v300_rt0c_existing_tests_changed: False")
    print("v300_rt0c_framework_runtime_changed: False")
    print("v300_rt0c_real_provider_execution: False")
    print("v300_rt1_authorization: blocked-pending-released-voice-input-realtime-cancel-contracts")
    print("v300_rt6_authorization: blocked-pending-released-motion-contract")


if __name__ == "__main__":
    main()
