"""Validate the T-1b Flutter audio-player abstraction and state contract.

This check is source-tree only. It does not load private audio, launch a browser,
call Framework/TTS providers, or execute a platform audio decoder.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_RELEASE_HASHES = {
    "docs/DRC_v200_goal_checklist_small_commit.md": "4c043837986c626c6fc44e4f84f73b019b2c8c21da7531a3f029554006b7eb63",
    "release_notes/v2.0.0.md": "d2e13041ae51b9fef330a01a0d9124ccbfb6fb0850a0c2a29966baf96be3417b",
    "docs/DRC_v20x_maintenance_checklist.md": "02e6e2e49a54a5c1360ee5d95d6bed2314ab42aec5dce911f3ed72867c4d46f2",
    "docs/v20x_patch_release.md": "eb6ae9770a4611a463ddb227a1dd8ce8816ee310cddaed327a02404a34a7935d",
    "docs/v201_patch_release_record.md": "9b724a6c5c7ffffdb3e699ad010ff75148ec4549b6cf2d940b44e62e161140bd",
    "release_notes/v2.0.1.md": "1e90c85e51ef848b64bddaa73f1f40c659457935e30831027310ea95fc94656b",
    "build_v200_final_fixed_release_zip_from_head.ps1": "4a4439341b0ad00d56b50038993631fcb48fb417cd0f0648dc3abc5e72d3b360",
    "build_v201_fixed_release_zip_from_head.ps1": "89d3fe3e39484b36272d9c8ec8499276ffe305ec844a87cca5d90fef8931ab1b",
    "scripts/check_v20x_patch_release.py": "e4eefc408abcbccc2651c1113ae8264269cce1d77525067173e0a06a7ef685cf",
}

UNCHANGED_T1B_HASHES = {
    "backend/app/config.py": "ebe022db586ffbaaa6a37db2f43cddca218c4e1e91cee782ffd7b6c8e607d4a5",
    "backend/app/services/voice_output_artifact_store.py": "69804d2e9926b76d6f297a1e7919402b084f4e654749b3789d7d23cfc0951613",
    "backend/app/api/voice_output_demo.py": "ecb030e97b95f0825485108660c916530146cbcc5d5742f04916f686df14b0f7",
    "backend/app/models/voice_output_demo.py": "9e00e559d5815e5f8c37a0fedcd077385e62ed0fb4b67596df6f14a2cb7dfd11",
    "backend/tests/test_voice_output_artifact_store.py": "c0d103d7b25830f8752aa9a0238bb5495b2895aad6afd9682eec8064168b659f",
    "app/lib/models/voice_output_demo.dart": "e31f376e93d4c0dabdf543279314be234bf2a78bb7383ab2f0d28f161074673f",
    "app/lib/services/backend_api_client.dart": "1d754b931ee7811ce708dd5e0ab3d64bc7b3ecdb63f60f1819d8470976f28774",
    "app/lib/screens/home_screen.dart": "85a791716bfb2996b964148a74ab3c7ae33fd1d2be51c7d11006968f7dddfc1c",
    "app/test/widget_test.dart": "175eec29a41f1cd1731137eeb74444c4e11c02ec6e7494385eb7ca322a2fcfb1",
    "app/pubspec.yaml": "fe4921649f69a5c9a7fe9dc4caad7d41f796cdb1b6adcd8687974a89cec85f86",
}


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"Missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def normalized_hash(relative: str) -> str:
    data = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"Missing {label}: {needle!r}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"Unexpected {label}: {needle!r}")


def assert_hashes(expected: dict[str, str], label: str) -> None:
    for relative, digest in expected.items():
        actual = normalized_hash(relative)
        if actual != digest:
            raise AssertionError(f"{label} changed: {relative}: {actual} != {digest}")


def assert_no_sensitive_values(relative: str, text: str) -> None:
    patterns = (
        r"sk-[A-Za-z0-9_\-]{12,}",
        r"xai-[A-Za-z0-9_\-]{12,}",
        r"AIza[0-9A-Za-z_\-]{20,}",
        r"Bearer\s+[A-Za-z0-9_\-.]{16,}",
        r"[A-Za-z]:\\Users\\[^<\r\n]+",
        r"192\.168\.\d{1,3}\.\d{1,3}",
    )
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            raise AssertionError(f"Sensitive-looking value in {relative}: {pattern}")


def main() -> None:
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    contract = read("docs/v210_tts_player_controller.md")
    inventory = read("docs/v210_tts_player_current_behavior_inventory.md")
    controller = read("app/lib/services/voice_output_audio_player.dart")
    tests = read("app/test/voice_output_audio_player_test.dart")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    pubspec = read("app/pubspec.yaml")

    for text, label in (
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
    ):
        require(text, "T-1b", f"{label} T-1b marker")
        require(text, "T-1c", f"{label} T-1c marker")

    require(checklist, "Current small commit: T-1b", "checklist current small commit")
    require(checklist, "T-1b  CURRENT / NOT_COMPLETED", "T-1b state")
    require(checklist, "Implementation state: IMPLEMENTED / NOT_ACCEPTED", "T-1b implementation state")
    require(checklist, "T-1c  PLANNED", "T-1c state")
    require(checklist, "V-1  PLANNED", "V-1 state")
    require(checklist, "R-1  PLANNED", "R-1 state")
    require(contract, "Status: IMPLEMENTED / NOT_ACCEPTED", "contract status")
    require(contract, "VoiceOutputAudioEngine", "engine abstraction")
    require(contract, "VoiceOutputAudioPlayerController", "controller contract")
    require(inventory, "T-1b implementation added", "inventory follow-up")
    require(scripts_readme, "check_v210_tts_player_controller.py", "T-1b command")

    for marker in (
        "enum VoiceOutputPlaybackPhase",
        "idle,",
        "loading,",
        "playing,",
        "stopped,",
        "completed,",
        "failed,",
        "expired,",
        "abstract interface class VoiceOutputAudioEngine",
        "class VoiceOutputAudioPlayerController extends ChangeNotifier",
        "Future<void> play(Uri source)",
        "Future<void> stop()",
        "Future<void> replay()",
        "Future<void> markExpired",
        "Future<void> reset()",
        "source.scheme == 'http' || source.scheme == 'https'",
        "unsupported_audio_uri",
        "audio_artifact_expired",
        "unawaited(_engine.dispose())",
    ):
        require(controller, marker, "controller marker")

    for marker in (
        "play exposes loading before becoming playing",
        "stop produces a replayable stopped state",
        "completion event produces replay-ready state",
        "replay seeks to the beginning and starts again",
        "expired engine failure clears the source and blocks replay",
        "ordinary engine failure stays retryable without exposing URL",
        "unsupported URI fails before the engine sees it",
        "reset invalidates a pending load result",
        "dispose closes the engine",
        "_FakeVoiceOutputAudioEngine",
    ):
        require(tests, marker, "focused test marker")

    forbid(controller, "package:just_audio", "concrete audio dependency")
    forbid(controller, "package:audioplayers", "concrete audio dependency")
    forbid(controller, "launchUrl", "external URL launch")
    forbid(controller, "audioUrl", "raw response URL field")
    for package_name in ("audioplayers:", "just_audio:", "assets_audio_player:"):
        forbid(pubspec, package_name, "T-1b audio dependency")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(UNCHANGED_T1B_HASHES, "T-1b explicit non-change surface")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_tts_player_current_behavior_inventory.md",
        "docs/v210_tts_player_controller.md",
        "app/lib/services/voice_output_audio_player.dart",
        "app/test/voice_output_audio_player_test.dart",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_tts_player_controller_status: implemented-not-accepted")
    print("v210_tts_player_controller_current_small_commit: T-1b")
    print("v210_tts_player_controller_parent_phase: T-1-current-not-completed")
    print("v210_tts_player_controller_state_model: true")
    print("v210_tts_player_controller_engine_abstraction: true")
    print("v210_tts_player_controller_stop_replay: true")
    print("v210_tts_player_controller_expired_state: true")
    print("v210_tts_player_controller_stale_operation_guard: true")
    print("v210_tts_player_controller_home_integration: false")
    print("v210_tts_player_controller_dependency_changed: false")
    print("v210_tts_player_controller_backend_runtime_changed: false")
    print("v210_tts_player_controller_real_tts_execution: false")
    print("v210_tts_player_controller_release_records_changed: false")
    print("[v210-tts-player-controller-check] OK")


if __name__ == "__main__":
    main()
