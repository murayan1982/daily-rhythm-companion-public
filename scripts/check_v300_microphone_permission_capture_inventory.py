"""Validate RT-2a microphone permission/capture inventory and split.

This source-tree gate is credential-free, network-free, Framework-import-free,
provider-free, permission-free, microphone-free, capture-free, and STT-free.
It protects Backend/Flutter runtime and tests, platform permission metadata,
versions, dependencies, and immutable release records.
"""
from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

TREE_HASHES = {
    "backend/app": "e46df81c20a3843b249cb66757c75a2324ff05c54adf2549b65de22ce2efcec1",
    "backend/tests": "c62f2351de017fd7812571c66232c6dbff293539e52b72a8bc06a8f5aa0044ae",
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
                f"RT-2a protected tree changed: {relative}: {actual} != {expected}"
            )
    for relative, expected in FILE_HASHES.items():
        actual = normalized_hash(relative)
        if actual != expected:
            raise AssertionError(
                f"RT-2a protected file changed: {relative}: {actual} != {expected}"
            )


def assert_current_surface() -> None:
    pubspec = read("app/pubspec.yaml")
    android_manifest = read("app/android/app/src/main/AndroidManifest.xml")
    ios_plist = read("app/ios/Runner/Info.plist")
    home = read("app/lib/screens/home_screen.dart")
    api_client = read("app/lib/services/backend_api_client.dart")
    backend_route = read("backend/app/api/voice_input_demo.py")
    backend_model = read("backend/app/models/voice_input_demo.py")
    backend_service = read("backend/app/services/voice_input_demo_service.py")

    for package_name in (
        "permission_handler:",
        "record:",
        "flutter_sound:",
        "speech_to_text:",
        "mic_stream:",
        "audio_waveforms:",
    ):
        forbid(pubspec, package_name, "microphone/permission dependency")

    forbid(android_manifest, "android.permission.RECORD_AUDIO", "Android microphone permission")
    forbid(ios_plist, "NSMicrophoneUsageDescription", "iOS microphone usage description")

    require(
        home,
        "録音やマイク権限はまだ使わず、backend の voice input demo request contract だけを確認します。",
        "metadata-only Flutter voice-input explanation",
    )
    require(home, "_submitVoiceInputDemoRequest", "Flutter metadata request handler")
    require(api_client, "submitVoiceInputDemoRequest", "Flutter Backend request method")
    forbid(api_client, "MultipartRequest", "audio multipart upload")

    require(backend_route, "Accept a metadata-only voice input demo request", "metadata-only Backend route")
    require(backend_route, "It does not", "Backend no-audio route explanation")
    require(backend_model, "transcript", "voice-input transcript field")
    require(backend_service, "no audio was processed", "voice-input no-audio result")

    combined = "\n".join((backend_route, backend_model, backend_service))
    for forbidden_runtime in (
        "UploadFile",
        "File(",
        "speech_recognition",
        "sounddevice",
        "pyaudio",
        "MediaRecorder",
        "getUserMedia",
    ):
        forbid(combined, forbidden_runtime, "voice-input capture/STT runtime")


def assert_planning_contract() -> None:
    sources = {
        "README": read("README.md"),
        "roadmap": read("roadmap.md"),
        "tasklist": read("tasklist.md"),
        "checklist": read("docs/DRC_v300_goal_checklist_small_commit.md"),
        "scripts README": read("scripts/README.md"),
        "inventory": read("docs/v300_microphone_permission_capture_inventory.md"),
    }

    for label, source in sources.items():
        require(source, "RT-2a", f"{label} RT-2a marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} accepted state")
        assert_no_sensitive_values(label, source)

    combined = "\n".join(sources.values())
    for marker in (
        "RT-2b",
        "RT-2c",
        "RT-2d",
        "RT-2e",
        "explicit user action",
        "no raw audio persistence by default",
        "no STT execution",
        "Microphone dependency added: false",
        "Android RECORD_AUDIO added: false",
        "iOS microphone usage added: false",
        "Audio captured: false",
    ):
        require(combined, marker, f"RT-2a planning marker {marker}")

    gate = read("scripts/check_v300_microphone_permission_capture_inventory.py")
    tree = ast.parse(gate)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "framework" or alias.name.startswith("framework."):
                    raise AssertionError("RT-2a gate imports Framework")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "framework" or module.startswith("framework."):
                raise AssertionError("RT-2a gate imports Framework")
        elif isinstance(node, ast.Call):
            target = node.func
            call_name = ""
            if isinstance(target, ast.Name):
                call_name = target.id
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                call_name = f"{target.value.id}.{target.attr}"
            if call_name in {
                "subprocess.run",
                "requests.get",
                "httpx.get",
                "sounddevice.rec",
                "speech_recognition.Recognizer",
            }:
                raise AssertionError(f"RT-2a gate runtime call: {call_name}")


def main() -> None:
    assert_hashes()
    assert_current_surface()
    assert_planning_contract()

    print("v300_microphone_permission_capture_inventory_status: completed-accepted")
    print("v300_rt2a_backend_runtime_changed: False")
    print("v300_rt2a_flutter_runtime_changed: False")
    print("v300_rt2a_existing_tests_changed: False")
    print("v300_rt2a_microphone_dependency_added: False")
    print("v300_rt2a_android_record_audio_added: False")
    print("v300_rt2a_ios_microphone_usage_added: False")
    print("v300_rt2a_microphone_accessed: False")
    print("v300_rt2a_audio_captured: False")
    print("v300_rt2_parent_status: current-pending-rt2b-implementation")
    print("v300_rt2b_authorization: authorized-permission-contract-and-fake-gateway-only")


if __name__ == "__main__":
    main()
