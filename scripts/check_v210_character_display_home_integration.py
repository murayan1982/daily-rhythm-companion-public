"""Validate the V-1c HomeScreen character display integration boundary.

This check is source-tree only. It verifies deterministic HomeScreen wiring,
repository-safe fallback handling, focused fake/widget tests, unchanged Backend,
static assets, dependencies, Motion Demo boundary, and immutable release records.
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

UNCHANGED_RUNTIME_HASHES = {
    "app/lib/models/character_display_presentation.dart": "6a5f0df8ea609dc541bce14283f310dc734d99911c972550397c8ea0466403c2",
    "app/lib/models/character_preset.dart": "66896fa5ff7ffc2cf5e1497bfc3ce18ba555809ca73ebc60c655cd867075cf08",
    "app/lib/models/advice_response.dart": "99d26ce001213bafe44d917a459ae1491913af85cb33b897e0b81172f89046f7",
    "app/lib/models/advice_source.dart": "99ba85cb63901fe2ef3f2d2d7d7bd0ef38977eccad7277f53d937e11d17425fe",
    "app/lib/models/motion_demo.dart": "5e3fafa3fba66d92fe589d7b913bf350842b28d02218c3a54903d45c5f5fab89",
    "app/lib/services/voice_output_audio_player.dart": "3089e8423c5ec758c54684e55d100b300753b4e71e7553e6a72daff1865e388a",
    "app/pubspec.yaml": "78ea66a2c1c4f96deced1063bf9f00369e7507c415e87d769a556b392dec4756",
    "backend/app/main.py": "6ead9b1570b1453d7029496db3b554156b0e6752b1cb2369053e9341a81d3c27",
    "backend/app/api/advice.py": "ecf21509449e67f0c6c0209b762fad9e6c2dc2c10e2ffea7d18e36b446ae83c1",
    "backend/app/api/voice_output_demo.py": "ecb030e97b95f0825485108660c916530146cbcc5d5742f04916f686df14b0f7",
}

STATIC_ASSET_HASHES = {
    "app/assets/images/characters/gentle_mina_demo.png": "7f6a7b9d071c7a6897a4e66aaf81a92c6ef0b78c63c8d6a0ea7c22b13d59ac72",
    "app/assets/images/characters/cheerful_sora_demo.png": "2f0ad34642252d17851ce437e484d31ab5ee960e539a55d09f0ad87e4474627b",
    "app/assets/images/characters/cool_rei_demo.png": "932fd68c601b21577895a2cbf7569368a03b0561914d78f2cd8ef92fabf00b91",
    "app/assets/images/backgrounds/morning_room_soft.png": "f0b158b32affbc085f2650eb852407aad193a4bcaa5fb23a6417ca4999085ea7",
    "app/assets/images/backgrounds/night_room_calm.png": "46d01e2b5f9a8a1683a15d0fe648a2d6e60bd3144cb112418cff1f53015c47af",
    "app/assets/images/placeholders/character_fallback.png": "3e37a8318aa344d928b4c811edb796c643f39086a5a2204f2cb872084ee7d601",
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
    home = read("app/lib/screens/home_screen.dart")
    model = read("app/lib/models/character_display_presentation.dart")
    widget = read("app/lib/widgets/character_display_card.dart")
    catalog = read("app/lib/ui/character_asset_catalog.dart")
    model_tests = read("app/test/character_display_presentation_test.dart")
    card_tests = read("app/test/character_display_card_test.dart")
    integration_tests = read("app/test/character_display_home_integration_test.dart")
    legacy_widget_tests = read("app/test/widget_test.dart")
    contract = read("docs/v210_character_display_home_integration.md")
    state_contract = read("docs/v210_character_display_state_contract.md")
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    inventory = read("docs/v210_character_display_current_behavior_inventory.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")

    for source, label in (
        (contract, "contract"),
        (state_contract, "state contract"),
        (checklist, "checklist"),
        (inventory, "inventory"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
    ):
        require(source, "V-1c", f"{label} V-1c marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} accepted state")
        require(source, "V-1", f"{label} parent marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} parent accepted state")
        require(source, "R-1", f"{label} R-1 marker")
        require(source, "CURRENT / NOT_COMPLETED", f"{label} R-1 current state")

    require(checklist, "V-1b  COMPLETED / ACCEPTED", "accepted V-1b state")
    require(checklist, "V-1c  COMPLETED / ACCEPTED", "accepted V-1c state")
    require(checklist, "Current implementation state: NOT_STARTED", "R-1 implementation marker")
    require(checklist, "R-1  CURRENT / NOT_COMPLETED", "R-1 current state")

    for marker in (
        "import '../models/character_display_presentation.dart';",
        "import '../widgets/character_display_card.dart';",
        "CharacterDisplayPresentation.resolve(",
        "CharacterDisplayCard(",
        "moodLabel: _formatMoodLabel(_selectedMood)",
        "moodSupportMessage: _formatMoodSupportMessage(_selectedMood)",
        "advice: _adviceResponse",
        "_isLoading ||",
        "_isCreatingAdvice ||",
        "_isSubmittingVoiceOutputDemo",
        "playbackPhase: _voiceOutputAudioPlayerController.state.phase",
        "CharacterAssetCatalog.hasCharacterAsset",
        "character-options-loading",
        "_buildMotionDemoSection(context)",
    ):
        require(home, marker, "HomeScreen integration marker")

    for marker in (
        "static bool hasCharacterAsset",
        "characterImages.containsKey(characterId)",
        "return characterImages[characterId] ?? fallbackCharacter",
    ):
        require(catalog, marker, "asset-catalog marker")

    for marker in (
        "fallbackImageAssetPath = CharacterAssetCatalog.fallbackCharacter",
        "selected-character-fallback-image",
        "character-display-missing-image",
        "character-display-name",
        "character-display-personality",
        "character-display-speaking",
        "character-display-advice-style",
        "character-display-profile-note",
    ):
        require(widget, marker, "character-card integration marker")

    fallback_position = widget.index("selected-character-fallback-image")
    generic_position = widget.index("character-display-missing-image")
    if fallback_position >= generic_position:
        raise AssertionError("Repository fallback image must precede generic placeholder")

    for marker in (
        "HomeScreen shows deterministic loading before mood state",
        "mood and advice loading resolve into advice presentation",
        "framework fallback uses safe copy inside character card",
        "in-app audio playback drives speaking presentation",
        "unknown character ID uses repository fallback presentation",
    ):
        require(integration_tests, marker, "focused HomeScreen integration test")

    require(
        card_tests,
        "retries the repository fallback image before generic placeholder",
        "fallback retry widget test",
    )
    for marker in (
        "Character choice updates daily loop and advice context",
        "of: find.byKey(const Key('character-display-card'))",
        "matching: find.textContaining('ソラです。')",
        "of: find.byKey(const Key('character-display-name'))",
        "matching: find.text('ミナ')",
        "matching: find.text('ソラ')",
        "matching: find.text('レイ')",
        "matching: find.textContaining('mood=tired')",
        "matching: find.textContaining('character=cool_rei')",
    ):
        require(legacy_widget_tests, marker, "targeted legacy character test")

    for brittle_marker in (
        "expect(find.textContaining('mood=tired'), findsOneWidget)",
        "expect(find.textContaining('character=cool_rei'), findsOneWidget)",
        "find.text('Name: ミナ')",
        "find.text('Name: ソラ')",
        "find.text('Name: レイ')",
    ):
        forbid(legacy_widget_tests, brittle_marker, "pre-extraction combined detail finder")
    require(model_tests, "speaking wins over simultaneous loading", "accepted model precedence test")

    for marker in (
        "initial loading -> resolved mood state",
        "mood change -> advice loading -> advice state",
        "in-app audio playback -> speaking state",
        "full Flutter tests: 103",
        "Backend data loading and error handling",
        "Advanced Motion Demo",
    ):
        require(contract, marker, "V-1c contract marker")

    for marker in (
        "implementation commit: 995145d",
        "Backend pytest: 110 passed",
        "full Flutter test: 103 passed",
        "Flutter Web / Windows builds: passed",
        "diff review / explicit operator approval: passed",
    ):
        require(contract, marker, "V-1c acceptance marker")

    for forbidden in (
        "Live2D execution: accepted",
        "VTube Studio execution: accepted",
        "real motion execution: true",
        "R-1  COMPLETED",
    ):
        forbid(contract + checklist + inventory, forbidden, "premature completion/execution claim")

    forbid(home + widget + model, "WebSocket", "motion runtime connection")
    forbid(home + widget + model, "dart:math", "random presentation state")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(UNCHANGED_RUNTIME_HASHES, "V-1c unchanged runtime boundary")
    assert_hashes(STATIC_ASSET_HASHES, "V-1c static asset baseline")

    for relative in (
        "app/lib/screens/home_screen.dart",
        "app/lib/ui/character_asset_catalog.dart",
        "app/lib/widgets/character_display_card.dart",
        "app/test/widget_test.dart",
        "app/test/character_display_card_test.dart",
        "app/test/character_display_home_integration_test.dart",
        "docs/v210_character_display_home_integration.md",
        "docs/v210_character_display_state_contract.md",
        "docs/v210_character_display_current_behavior_inventory.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "scripts/check_v210_character_display_current_behavior_inventory.py",
        "scripts/check_v210_character_display_state.py",
        "scripts/check_v210_character_display_home_integration.py",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_character_display_home_integration_status: completed-accepted")
    print("v210_character_display_home_integration_completed_small_commit: V-1c")
    print("v210_character_display_home_integration_current_small_commit: R-1")
    print("v210_character_display_home_integration_parent_phase: V-1-completed-accepted")
    print("v210_character_display_home_integration_content_states: mood,advice,fallback")
    print("v210_character_display_home_integration_activity_states: idle,loading,speaking")
    print("v210_character_display_home_integration_focused_model_tests: 9")
    print("v210_character_display_home_integration_focused_card_tests: 5")
    print("v210_character_display_home_integration_focused_home_tests: 5")
    print("v210_character_display_home_integration_expected_flutter_tests: 103")
    print("v210_character_display_home_integration_backend_runtime_changed: false")
    print("v210_character_display_home_integration_assets_changed: false")
    print("v210_character_display_home_integration_real_motion_execution: false")
    print("v210_character_display_home_integration_release_records_changed: false")
    print("[v210-character-display-home-integration-check] OK")


if __name__ == "__main__":
    main()
