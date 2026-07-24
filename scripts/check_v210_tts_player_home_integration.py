"""Validate the T-1c Flutter in-app TTS player integration.

This source-tree check does not call a running Backend, Framework, TTS provider,
or platform decoder. Audible PC/smartphone Web acceptance remains separate.
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

UNCHANGED_BACKEND_HASHES = {
    "backend/app/config.py": "ebe022db586ffbaaa6a37db2f43cddca218c4e1e91cee782ffd7b6c8e607d4a5",
    "backend/app/services/voice_output_artifact_store.py": "69804d2e9926b76d6f297a1e7919402b084f4e654749b3789d7d23cfc0951613",
    "backend/app/api/voice_output_demo.py": "ecb030e97b95f0825485108660c916530146cbcc5d5742f04916f686df14b0f7",
    "backend/app/models/voice_output_demo.py": "9e00e559d5815e5f8c37a0fedcd077385e62ed0fb4b67596df6f14a2cb7dfd11",
    "backend/tests/test_voice_output_artifact_store.py": "c0d103d7b25830f8752aa9a0238bb5495b2895aad6afd9682eec8064168b659f",
    "app/lib/services/voice_output_audio_player.dart": "3089e8423c5ec758c54684e55d100b300753b4e71e7553e6a72daff1865e388a",
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
    contract = read("docs/v210_tts_player_home_integration.md")
    inventory = read("docs/v210_tts_player_current_behavior_inventory.md")
    controller_contract = read("docs/v210_tts_player_controller.md")
    engine = read("app/lib/services/audioplayers_voice_output_audio_engine.dart")
    home = read("app/lib/screens/home_screen.dart")
    engine_tests = read("app/test/audioplayers_voice_output_audio_engine_test.dart")
    widget_tests = read("app/test/voice_output_audio_player_widget_test.dart")
    existing_widget_tests = read("app/test/widget_test.dart")
    pubspec = read("app/pubspec.yaml")
    windows_cmake = read("app/windows/CMakeLists.txt")
    windows_flutter_cmake = read("app/windows/flutter/CMakeLists.txt")
    root_gitignore = read(".gitignore")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    for source, label in (
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
    ):
        require(source, "T-1c", f"{label} T-1c marker")

    require(checklist, "Current small commit: V-1", "current small commit")
    require(checklist, "T-1b  COMPLETED / ACCEPTED", "T-1b accepted state")
    require(checklist, "T-1c  COMPLETED / ACCEPTED", "T-1c queue state")
    require(checklist, "Status: COMPLETED / ACCEPTED", "T-1c acceptance status")
    require(checklist, "V-1  CURRENT / NOT_COMPLETED", "V-1 current state")
    require(checklist, "R-1  PLANNED", "R-1 state")
    require(contract, "Status: COMPLETED / ACCEPTED", "detailed contract status")
    require(contract, "Parent phase: T-1 COMPLETED / ACCEPTED", "parent state")
    require(inventory, "T-1c acceptance follow-up", "inventory follow-up")
    require(controller_contract, "T-1c acceptance follow-up", "controller follow-up")
    require(scripts_readme, "check_v210_tts_player_home_integration.py", "T-1c check command")
    require(contract, "implementation commit: 4d3d5d5", "T-1c implementation commit")
    require(contract, "desktop plugin registrant follow-up: 9771f76", "plugin registrant follow-up")
    require(contract, "PC Web audible playback / stop / replay / completion: passed", "PC audible evidence")
    require(contract, "smartphone Web audible playback / stop / replay / completion: passed", "smartphone audible evidence")
    require(contract, "missing-artifact HTTP mapping to expired: passed", "expired mapping evidence")
    require(contract, "PC and smartphone regenerate recovery: passed", "regenerate recovery evidence")
    require(contract, "real Framework/TTS execution: true", "real TTS execution evidence")

    require(pubspec, "audioplayers: ^6.7.1", "audio dependency")
    require(windows_cmake, "cmake_minimum_required(VERSION 3.15)", "Windows CMake minimum")
    require(windows_cmake, "cmake_policy(VERSION 3.15...3.25)", "Windows CMake policy")
    require(windows_cmake, "_SILENCE_EXPERIMENTAL_COROUTINE_DEPRECATION_WARNINGS", "Visual Studio 18 coroutine compatibility")
    require(windows_flutter_cmake, "Flutter", "Windows Flutter scaffold")
    require(root_gitignore, "/flutter/", "root-scoped Flutter SDK ignore")
    if "\nflutter/\n" in root_gitignore:
        raise AssertionError("Unscoped flutter/ ignore would hide app/windows/flutter")

    for marker in (
        "class AudioplayersVoiceOutputAudioEngine implements VoiceOutputAudioEngine",
        "abstract interface class VoiceOutputPlatformAudioDriver",
        "http.Client",
        "response.statusCode == 404 || response.statusCode == 410",
        "audio_artifact_not_found",
        "unsupported_audio_content_type",
        "empty_audio_artifact",
        "audio_platform_playback_failed",
        "setSourceBytes",
        "PlayerMode.mediaPlayer",
        "ReleaseMode.stop",
    ):
        require(engine, marker, "concrete engine marker")

    for marker in (
        "final VoiceOutputAudioEngine? voiceOutputAudioEngine",
        "AudioplayersVoiceOutputAudioEngine()",
        "VoiceOutputAudioPlayerController",
        "voice-output-in-app-player",
        "voice-output-play-button",
        "voice-output-stop-button",
        "voice-output-replay-button",
        "voice-output-regenerate-button",
        "アプリ内音声プレイヤー",
        "音声を作り直す",
        "開発者向け再生詳細",
        "await _voiceOutputAudioPlayerController.reset()",
        "_voiceOutputAudioPlayerController.dispose()",
    ):
        require(home, marker, "HomeScreen integration marker")
    forbid(home, "_openVoiceOutputAudioUrl", "legacy external voice-output helper")
    forbid(home, "音声を開いて再生確認する", "legacy external playback button")

    for marker in (
        "HTTP 404 becomes an expired artifact failure",
        "HTTP 410 becomes an expired artifact failure",
        "loads MP3 bytes and drives play stop seek",
        "forwards playing and completion events",
        "platform not-found error is mapped to expired",
        "_FakePlatformAudioDriver",
    ):
        require(engine_tests, marker, "engine test marker")

    for marker in (
        "in-app player supports play stop and replay",
        "completion exposes replay without printing the source URL",
        "expired artifact offers direct regeneration",
        "_FakeVoiceOutputAudioEngine",
        "opaque-test-id",
    ):
        require(widget_tests, marker, "widget test marker")

    require(existing_widget_tests, "Playback candidate: playable in-app URL handoff", "updated existing widget regression")
    require(existing_widget_tests, "アプリ内音声プレイヤー", "existing widget in-app marker")

    for forbidden in (
        "backend/local_data",
        "credentials.json",
        "create_voice_output_session(",
    ):
        if forbidden in engine_tests + widget_tests:
            raise AssertionError(f"T-1c focused tests are not mock-safe: {forbidden}")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(UNCHANGED_BACKEND_HASHES, "T-1c unchanged boundary")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_tts_player_current_behavior_inventory.md",
        "docs/v210_tts_player_controller.md",
        "docs/v210_tts_player_home_integration.md",
        "app/lib/services/audioplayers_voice_output_audio_engine.dart",
        "app/lib/screens/home_screen.dart",
        "app/test/audioplayers_voice_output_audio_engine_test.dart",
        "app/test/voice_output_audio_player_widget_test.dart",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_tts_player_home_integration_status: completed-accepted")
    print("v210_tts_player_home_integration_current_small_commit: V-1")
    print("v210_tts_player_home_integration_parent_phase: T-1-completed-accepted")
    print("v210_tts_player_home_integration_audio_dependency: audioplayers-6.7.1")
    print("v210_tts_player_home_integration_in_app_controls: true")
    print("v210_tts_player_home_integration_http_expiry_mapping: true")
    print("v210_tts_player_home_integration_windows_cmake_315: true")
    print("v210_tts_player_home_integration_windows_vs18_coroutine_bridge: true")
    print("v210_tts_player_home_integration_windows_scaffold_tracked: true")
    print("v210_tts_player_home_integration_backend_runtime_changed: false")
    print("v210_tts_player_home_integration_flutter_runtime_changed: true")
    print("v210_tts_player_home_integration_real_tts_execution: true")
    print("v210_tts_player_home_integration_audible_acceptance: true")
    print("v210_tts_player_home_integration_release_records_changed: false")
    print("[v210-tts-player-home-integration-check] OK")


if __name__ == "__main__":
    main()
