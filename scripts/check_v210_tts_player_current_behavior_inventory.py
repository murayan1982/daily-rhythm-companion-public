"""Validate the T-1a TTS player current behavior inventory.

This check is source-tree only. It freezes the accepted pre-T-1 Backend artifact
and Flutter voice-output baseline without reading private audio, calling providers,
launching URLs, changing dependencies, or modifying release records.
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

T1A_BASELINE_HASHES = {
    "backend/app/config.py": "ebe022db586ffbaaa6a37db2f43cddca218c4e1e91cee782ffd7b6c8e607d4a5",
    "backend/app/services/voice_output_artifact_store.py": "69804d2e9926b76d6f297a1e7919402b084f4e654749b3789d7d23cfc0951613",
    "backend/app/api/voice_output_demo.py": "ecb030e97b95f0825485108660c916530146cbcc5d5742f04916f686df14b0f7",
    "backend/app/models/voice_output_demo.py": "9e00e559d5815e5f8c37a0fedcd077385e62ed0fb4b67596df6f14a2cb7dfd11",
    "backend/tests/test_voice_output_artifact_store.py": "c0d103d7b25830f8752aa9a0238bb5495b2895aad6afd9682eec8064168b659f",
    "app/lib/models/voice_output_demo.dart": "e31f376e93d4c0dabdf543279314be234bf2a78bb7383ab2f0d28f161074673f",
    "app/lib/services/backend_api_client.dart": "1d754b931ee7811ce708dd5e0ab3d64bc7b3ecdb63f60f1819d8470976f28774",
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
    inventory = read("docs/v210_tts_player_current_behavior_inventory.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    require(checklist, "Current small commit: T-1c", "checklist current small commit")
    require(checklist, "T-1  CURRENT / NOT_COMPLETED", "parent T-1 state")
    require(checklist, "T-1a  COMPLETED / ACCEPTED", "T-1a state")
    require(checklist, "T-1b  COMPLETED / ACCEPTED", "T-1b state")
    require(checklist, "T-1c  CURRENT / NOT_COMPLETED", "T-1c state")
    require(checklist, "C-1  COMPLETED / ACCEPTED", "C-1 accepted state")
    require(checklist, "V-1  PLANNED", "V-1 state")
    require(checklist, "R-1  PLANNED", "R-1 state")
    require(readme, "Current small commit: T-1c", "README current small commit")
    require(roadmap, "Current small commit: T-1c", "roadmap current small commit")
    require(tasklist, "current small commit: T-1c CURRENT / NOT_COMPLETED", "tasklist current state")
    require(scripts_readme, "check_v210_tts_player_current_behavior_inventory.py", "scripts command")

    for marker in (
        "Status: T-1a COMPLETED / ACCEPTED",
        "VOICE_OUTPUT_ARTIFACT_TTL_SECONDS=86400",
        "VOICE_OUTPUT_ARTIFACT_MAX_COUNT=100",
        "/demo/voice-output/audio/{artifact_id}",
        "LaunchMode.externalApplication",
        "no dedicated audio-player package",
        "T-1b  COMPLETED / ACCEPTED",
        "T-1c  CURRENT / NOT_COMPLETED",
        "T-1b added and accepted",
    ):
        require(inventory, marker, "T-1a inventory marker")

    config = read("backend/app/config.py")
    store = read("backend/app/services/voice_output_artifact_store.py")
    api = read("backend/app/api/voice_output_demo.py")
    flutter_model = read("app/lib/models/voice_output_demo.dart")
    flutter_client = read("app/lib/services/backend_api_client.dart")
    home = read("app/lib/screens/home_screen.dart")
    pubspec = read("app/pubspec.yaml")
    widget_tests = read("app/test/widget_test.dart")
    player_controller = read("app/lib/services/voice_output_audio_player.dart")

    require(config, "voice_output_artifact_ttl_seconds: int = 86400", "accepted artifact TTL")
    require(config, "voice_output_artifact_max_count: int = 100", "accepted artifact cap")
    require(store, 'audio_url=f"/demo/voice-output/audio/{artifact_id}"', "opaque audio URL")
    require(store, '"mp3": "audio/mpeg"', "MP3 media type")
    require(store, "current_time - modified_at >= self._ttl_seconds", "TTL cleanup")
    require(api, '"Cache-Control": "no-store"', "no-store header")
    require(api, '"X-Content-Type-Options": "nosniff"', "nosniff header")
    require(api, 'detail="Voice output audio artifact was not found."', "generic audio 404")
    require(flutter_model, "final String? audioUrl;", "Flutter audio URL field")
    require(flutter_model, "final String audioPlaybackStatus;", "response playback metadata")
    require(flutter_client, "Future<VoiceOutputDemoRequestResponse> submitVoiceOutputDemoRequest", "voice request client")
    forbid(flutter_client, "fetchVoiceOutputAudio", "audio fetch helper")
    require(inventory, "T-1c implementation follow-up", "T-1c inventory follow-up")
    require(home, "アプリ内音声プレイヤー", "in-app player UI")
    require(home, "voice-output-regenerate-button", "expired regeneration action")
    require(pubspec, "audioplayers: ^6.7.1", "T-1c audio dependency")
    require(widget_tests, "Voice output demo shows playback handoff when audio is ready", "playback visibility test")
    require(widget_tests, "Playback candidate: playable in-app URL handoff", "updated in-app widget regression")
    require(widget_tests, "Voice output demo keeps legacy audio URL non-playable", "legacy non-playable test")
    require(player_controller, "class VoiceOutputAudioPlayerController extends ChangeNotifier", "T-1b controller follow-up")
    read("app/lib/services/audioplayers_voice_output_audio_engine.dart")
    read("app/test/voice_output_audio_player_widget_test.dart")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(T1A_BASELINE_HASHES, "T-1a pre-runtime baseline")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_tts_player_current_behavior_inventory.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_tts_player_inventory_status: completed-accepted")
    print("v210_tts_player_inventory_current_small_commit: T-1c")
    print("v210_tts_player_inventory_parent_phase: T-1-current-not-completed")
    print("v210_tts_player_inventory_backend_artifact_ttl_seconds: 86400")
    print("v210_tts_player_inventory_backend_artifact_max_count: 100")
    print("v210_tts_player_inventory_current_playback_mode: in-app-audio-player")
    print("v210_tts_player_inventory_in_app_player_present: true")
    print("v210_tts_player_inventory_expired_state_present: true")
    print("v210_tts_player_inventory_t1b_controller_started: true")
    print("v210_tts_player_inventory_runtime_changed: true")
    print("v210_tts_player_inventory_existing_tests_changed: true")
    print("v210_tts_player_inventory_real_tts_execution: false")
    print("v210_tts_player_inventory_release_records_changed: false")
    print("[v210-tts-player-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
