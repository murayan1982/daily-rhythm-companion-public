"""Validate the V-1a character display current behavior inventory.

This check is source-tree only. It freezes the pre-V-1 Flutter runtime, accepted
static assets, existing widget-test baseline, Motion Demo separation, and immutable
release records without loading credentials or executing providers.
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

V1A_FLUTTER_BASELINE_HASHES = {
    "app/lib/screens/home_screen.dart": "1fdd4e82338904a175112e5eb74386ea5797308aea71cde64161970fb42e44c1",
    "app/lib/models/character_preset.dart": "66896fa5ff7ffc2cf5e1497bfc3ce18ba555809ca73ebc60c655cd867075cf08",
    "app/lib/models/advice_response.dart": "99d26ce001213bafe44d917a459ae1491913af85cb33b897e0b81172f89046f7",
    "app/lib/models/advice_source.dart": "99ba85cb63901fe2ef3f2d2d7d7bd0ef38977eccad7277f53d937e11d17425fe",
    "app/lib/models/motion_demo.dart": "5e3fafa3fba66d92fe589d7b913bf350842b28d02218c3a54903d45c5f5fab89",
    "app/lib/services/voice_output_audio_player.dart": "3089e8423c5ec758c54684e55d100b300753b4e71e7553e6a72daff1865e388a",
    "app/lib/ui/character_asset_catalog.dart": "6e3ab31eb3ac2c1c97899c7fa64eb5d04c808932322feb240e2bf6ea5762df54",
    "app/test/widget_test.dart": "dd869daa9123dbdd98e11a43d00c4ec56f2238f54e12d3c02cbd5313d479db04",
    "app/pubspec.yaml": "78ea66a2c1c4f96deced1063bf9f00369e7507c415e87d769a556b392dec4756",
}

V1A_STATIC_ASSET_HASHES = {
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
    inventory = read("docs/v210_character_display_current_behavior_inventory.md")
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    home = read("app/lib/screens/home_screen.dart")
    character_model = read("app/lib/models/character_preset.dart")
    advice_source = read("app/lib/models/advice_source.dart")
    motion_model = read("app/lib/models/motion_demo.dart")
    player = read("app/lib/services/voice_output_audio_player.dart")
    catalog = read("app/lib/ui/character_asset_catalog.dart")
    widget_tests = read("app/test/widget_test.dart")
    pubspec = read("app/pubspec.yaml")

    for source, label in (
        (inventory, "inventory"),
        (checklist, "checklist"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
    ):
        require(source, "V-1a", f"{label} V-1a marker")
        require(source, "IMPLEMENTED / NOT_ACCEPTED", f"{label} V-1a state")
        require(source, "V-1b", f"{label} V-1b marker")
        require(source, "V-1c", f"{label} V-1c marker")
        require(source, "R-1", f"{label} R-1 marker")

    require(checklist, "V-1  CURRENT / NOT_COMPLETED", "parent V-1 state")
    require(checklist, "R-1  PLANNED", "R-1 planned state")
    require(inventory, "Status: IMPLEMENTED / NOT_ACCEPTED", "inventory state")
    require(inventory, "Runtime changed: false", "docs-only runtime marker")
    require(inventory, "Existing tests changed: false", "unchanged test marker")
    require(inventory, "content state: mood | advice | fallback", "planned content axis")
    require(inventory, "activity state: idle | loading | speaking", "planned activity axis")
    require(inventory, "No Live2D or VTube Studio connection", "motion exclusion")

    for marker in (
        "Widget _buildCharacterSection(BuildContext context)",
        "_characterAwareMoodChoiceCopy",
        "bool _isLoading = false;",
        "bool _isCreatingAdvice = false;",
        "AdviceResponse? _adviceResponse;",
        "VoiceOutputAudioPlayerController",
        "_buildMotionDemoSection(context)",
        "selected-character-image",
        "selected-character-fallback-image",
        "CharacterAssetCatalog.imageForCharacter",
        "image_not_supported_outlined",
    ):
        require(home, marker, "HomeScreen inventory marker")

    for marker in (
        "required this.characterId",
        "required this.displayName",
        "required this.description",
        "required this.personalityType",
        "required this.speakingStyle",
        "required this.adviceStyle",
    ):
        require(character_model, marker, "CharacterPreset field")

    require(advice_source, "case 'framework_fallback':", "framework fallback source")
    require(motion_model, "final bool motionSent;", "motion sent boundary")
    require(motion_model, "final bool vtsConnectionUsed;", "VTS connection boundary")

    for phase in ("idle", "loading", "playing", "stopped", "completed", "failed", "expired"):
        require(player, phase, f"voice playback phase {phase}")

    for marker in (
        "gentle_mina_demo.png",
        "cheerful_sora_demo.png",
        "cool_rei_demo.png",
        "character_fallback.png",
        "morning_room_soft.png",
        "night_room_calm.png",
    ):
        require(catalog + pubspec, marker, "static asset marker")

    for marker in (
        "Character choice updates daily loop and advice context",
        "Character-aware mood labels stay presentation-only while advice uses stable mood IDs",
        "Accepted visual assets are exposed in the Web UI",
        "Motion demo button submits lightweight avatar request",
        "framework_fallback",
    ):
        require(widget_tests, marker, "existing widget-test marker")

    for forbidden in (
        "Live2D execution: accepted",
        "VTube Studio execution: accepted",
        "real motion execution: true",
    ):
        forbid(inventory, forbidden, "unsupported execution claim")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(V1A_FLUTTER_BASELINE_HASHES, "V-1a Flutter baseline")
    assert_hashes(V1A_STATIC_ASSET_HASHES, "V-1a static asset baseline")

    for relative in (
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_character_display_current_behavior_inventory.md",
        "scripts/check_v210_character_display_current_behavior_inventory.py",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_character_display_inventory_status: implemented-not-accepted")
    print("v210_character_display_inventory_current_small_commit: V-1a")
    print("v210_character_display_inventory_parent_phase: V-1-current-not-completed")
    print("v210_character_display_inventory_home_screen_lines: 4195")
    print("v210_character_display_inventory_widget_test_lines: 2669")
    print("v210_character_display_inventory_character_assets: 3")
    print("v210_character_display_inventory_fallback_assets: 1")
    print("v210_character_display_inventory_flutter_runtime_changed: false")
    print("v210_character_display_inventory_existing_tests_changed: false")
    print("v210_character_display_inventory_assets_changed: false")
    print("v210_character_display_inventory_real_motion_execution: false")
    print("v210_character_display_inventory_release_records_changed: false")
    print("[v210-character-display-current-behavior-inventory-check] OK")


if __name__ == "__main__":
    main()
