"""Validate RT-1a Framework v5.2.0 public-contract adoption planning.

This check is credential-free and source-tree-only. It does not import AI
Character Framework, call GitHub, read private env files, call providers, open a
microphone, start audio playback, or connect to motion runtimes.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_RELEASE = "v5.2.0"
FRAMEWORK_TAG_COMMIT = "c2e247064987c94bf735a359700f0462439b8286"

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
    "docs/v300_realtime_current_behavior_inventory.md": "6a84df2b6172e5ac06dec448d11e26b2f29abba72b702d2793dfda7e4d49495d",
    "scripts/check_v300_realtime_current_behavior_inventory.py": "38430a816b053a118b2e6f2db8db2cb05364f7b037dbb3e425a28a57f39a185e",
    "docs/v300_framework_realtime_contract_readiness.md": "cf560a7664fdf1089254e22bfda8833b37038b261a655a7b10c8ffbd966770e3",
    "scripts/check_v300_framework_realtime_contract_readiness.py": "41623918be4c17f8d17265cb1516abf6392c15b0eb0a2691d3aa1385cfef82ee",
    "docs/v300_framework_v510_reassessment.md": "61c63d61a4996628947eae3268669e083eb8d1158fcdec9622426412d6a842bc",
    "scripts/check_v300_framework_v510_reassessment.py": "e477580fd9db1bc37d1c88e307c3733792225ec436e351330210aa226ed99427",
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
    for path in sorted(candidate for candidate in base.rglob("*") if candidate.is_file() and "__pycache__" not in candidate.parts and candidate.suffix.lower() not in {".pyc", ".pyo"}):
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
            raise AssertionError(f"RT-1a protected tree changed: {relative}: {actual} != {expected}")
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(f"RT-1a protected file changed: {relative}: {actual} != {expected}")

def main() -> None:
    adoption = read("docs/v300_framework_v520_contract_adoption.md")
    checklist = read("docs/DRC_v300_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    sources = {
        "adoption": adoption,
        "checklist": checklist,
        "README": readme,
        "roadmap": roadmap,
        "tasklist": tasklist,
        "scripts README": scripts_readme,
    }
    for label, source in sources.items():
        require(source, "RT-1a", f"{label} RT-1a marker")
        require(source, "v5.2.0", f"{label} Framework release")
        require(source, "RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED", f"{label} authorization decision")
        assert_no_sensitive_values(label, source)

    require(adoption, "Implementation state: COMPLETED / ACCEPTED", "RT-1a implementation state")
    require(checklist, "Current parent phase: RT-1 CURRENT / NOT_COMPLETED", "checklist parent phase")
    require(checklist, "Current small commit: RT-1b CURRENT / NOT_COMPLETED", "checklist current small commit")
    require(checklist, "Current implementation state: NOT_STARTED", "checklist implementation state")
    require(checklist, "Completed small commit: RT-1a COMPLETED / ACCEPTED", "accepted RT-1a marker")
    require(checklist, "RT-0c  COMPLETED / ACCEPTED", "accepted RT-0c history")

    require(adoption, f"Released tag: {FRAMEWORK_RELEASE}", "Framework released tag")
    require(adoption, f"Tag commit: {FRAMEWORK_TAG_COMMIT}", "Framework tag commit")

    for symbol in (
        "create_voice_input_session()",
        "VoiceInputSession",
        "create_realtime_session()",
        "RealtimeSession",
        "InterruptRequest",
        "TTSQueueState",
        "BargeInPolicy",
        "create_motion_session()",
        "MotionSession",
    ):
        require(adoption, symbol, f"v5.2 public symbol {symbol}")

    for marker in (
        "real STT execution: NOT_IMPLEMENTED",
        "incremental transcript events: NOT_IMPLEMENTED",
        "provider-level hard cancellation: NOT_IMPLEMENTED",
        "real TTS queue flush/playback stop: NOT_IMPLEMENTED",
        "real Live2D/VTS adapter execution: NOT_IMPLEMENTED",
        "v5.1.capabilities",
        "public_boundary_missing",
        "event ID, sequence number, or timestamp",
        "RT-1: AUTHORIZED / CURRENT",
        "RT-3: BLOCKED_REAL_STT_NOT_IMPLEMENTED",
        "RT-4: BLOCKED_REAL_STREAMING_CANCEL_NOT_IMPLEMENTED",
        "RT-5: BLOCKED_REAL_OUTPUT_CONTROL_NOT_IMPLEMENTED",
        "RT-6: PLANNED_AFTER_RT1",
        "RT-7: BLOCKED_REAL_MOTION_ADAPTER_NOT_IMPLEMENTED",
    ):
        require(adoption, marker, f"RT-1a finding {marker}")

    require(adoption, "DRC runtime changed: false", "DRC runtime non-change")
    require(adoption, "Existing tests changed: false", "test non-change")
    require(adoption, "Real provider execution: false", "provider non-execution")
    require(adoption, "Microphone access: false", "microphone non-access")
    require(adoption, "Realtime runtime started: false", "realtime non-execution")
    require(adoption, "Backend pytest through .venv: 110 passed", "Backend acceptance evidence")
    require(adoption, "Flutter tests: 103 passed", "Flutter acceptance evidence")
    require(adoption, "diff review / explicit operator approval: passed", "operator acceptance evidence")

    assert_hashes()

    print("v300_framework_v520_contract_adoption_status: completed-accepted")
    print(f"v300_framework_release_snapshot: {FRAMEWORK_RELEASE}@{FRAMEWORK_TAG_COMMIT}")
    print("v300_framework_public_contracts_released: True")
    print("v300_framework_real_runtime_ready: False")
    print("v300_rt1a_drc_runtime_changed: False")
    print("v300_rt1a_existing_tests_changed: False")
    print("v300_rt1a_framework_runtime_changed: False")
    print("v300_rt1a_real_provider_execution: False")
    print("v300_rt1_authorization: authorized-mock-contract-only")
    print("v300_rt3_authorization: blocked-real-stt-not-implemented")
    print("v300_rt4_authorization: blocked-real-streaming-cancel-not-implemented")
    print("v300_rt5_authorization: blocked-real-output-control-not-implemented")
    print("v300_rt6_authorization: planned-after-rt1-mock-motion-contract-available")
    print("v300_rt7_authorization: blocked-real-motion-adapter-not-implemented")

if __name__ == "__main__":
    main()
