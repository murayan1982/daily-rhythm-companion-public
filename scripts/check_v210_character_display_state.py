"""Validate the V-1b deterministic character display state boundary.

This check is source-tree only. It preserves the accepted V-1b presentation model and focused tests while allowing separately checked V-1c HomeScreen/card/catalog integration. Static assets, unchanged Backend/Motion boundaries, and immutable release records remain guarded without executing providers.
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

UNCHANGED_V1B_HASHES = {
    "app/lib/models/character_preset.dart": "66896fa5ff7ffc2cf5e1497bfc3ce18ba555809ca73ebc60c655cd867075cf08",
    "app/lib/models/advice_response.dart": "99d26ce001213bafe44d917a459ae1491913af85cb33b897e0b81172f89046f7",
    "app/lib/models/advice_source.dart": "99ba85cb63901fe2ef3f2d2d7d7bd0ef38977eccad7277f53d937e11d17425fe",
    "app/lib/models/motion_demo.dart": "5e3fafa3fba66d92fe589d7b913bf350842b28d02218c3a54903d45c5f5fab89",
    "app/lib/services/voice_output_audio_player.dart": "3089e8423c5ec758c54684e55d100b300753b4e71e7553e6a72daff1865e388a",
    "app/pubspec.yaml": "baa60adac069f8543cf122e3e1c34179c6712ae5ca3c021e0369bb35f7d83bbd",
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
    model = read("app/lib/models/character_display_presentation.dart")
    widget = read("app/lib/widgets/character_display_card.dart")
    model_tests = read("app/test/character_display_presentation_test.dart")
    widget_tests = read("app/test/character_display_card_test.dart")
    contract = read("docs/v210_character_display_state_contract.md")
    checklist = read("docs/DRC_v210_goal_checklist_small_commit.md")
    inventory = read("docs/v210_character_display_current_behavior_inventory.md")
    readme = read("README.md")
    roadmap = read("roadmap.md")
    tasklist = read("tasklist.md")
    scripts_readme = read("scripts/README.md")
    home = read("app/lib/screens/home_screen.dart")
    integration_tests = read("app/test/character_display_home_integration_test.dart")
    home_contract = read("docs/v210_character_display_home_integration.md")

    for source, label in (
        (contract, "contract"),
        (checklist, "checklist"),
        (inventory, "inventory"),
        (readme, "README"),
        (roadmap, "roadmap"),
        (tasklist, "tasklist"),
        (scripts_readme, "scripts README"),
    ):
        require(source, "V-1b", f"{label} V-1b marker")
        require(source, "COMPLETED / ACCEPTED", f"{label} accepted state")
        require(source, "V-1c", f"{label} V-1c marker")
        require(source, "R-1", f"{label} R-1 marker")

    require(checklist, "V-1  COMPLETED / ACCEPTED", "parent V-1 state")
    require(checklist, "V-1b  COMPLETED / ACCEPTED", "accepted V-1b state")
    require(checklist, "V-1c  COMPLETED / ACCEPTED", "accepted V-1c state")
    require(checklist, "Current implementation state: IMPLEMENTED / NOT_ACCEPTED", "R-1c implementation state")
    require(checklist, "Current small commit: R-1c", "R-1c current small commit")
    require(checklist, "R-1  CURRENT / NOT_COMPLETED", "R-1 current state")

    for marker in (
        "enum CharacterDisplayContentState",
        "mood,",
        "advice,",
        "fallback,",
        "enum CharacterDisplayActivityState",
        "idle,",
        "loading,",
        "speaking,",
        "enum CharacterDisplayFallbackReason",
        "factory CharacterDisplayPresentation.resolve",
        "CharacterDisplayFallbackReason.characterUnavailable",
        "CharacterDisplayFallbackReason.assetUnavailable",
        "CharacterDisplayFallbackReason.frameworkFallback",
        "VoiceOutputPlaybackPhase.playing",
        "VoiceOutputPlaybackPhase.loading",
        "AI応答を利用できなかったため",
    ):
        require(model, marker, "presentation-model marker")

    speaking_position = model.index("if (playbackPhase == VoiceOutputPlaybackPhase.playing)")
    loading_position = model.index("if (isLoading || playbackPhase == VoiceOutputPlaybackPhase.loading)")
    if speaking_position >= loading_position:
        raise AssertionError("Speaking precedence must appear before loading precedence")

    character_position = model.index("if (character == null)")
    asset_position = model.index("if (!hasRepositoryCharacterAsset)")
    framework_position = model.index("if (advice?.source?.engine.trim() == 'framework_fallback')")
    if not character_position < asset_position < framework_position:
        raise AssertionError("Fallback precedence must be character, asset, framework")

    for marker in (
        "class CharacterDisplayCard extends StatelessWidget",
        "character-display-card",
        "selected-character-image",
        "character-display-content-state",
        "character-display-activity-state",
        "character-display-static-baseline",
        "character-display-fallback-note",
        "Live2D / VTube Studio",
        "image_not_supported_outlined",
    ):
        require(widget, marker, "standalone-widget marker")

    for marker in (
        "uses mood content before advice exists",
        "uses non-empty advice ahead of mood content",
        "framework fallback uses safe app copy instead of provider text",
        "missing character wins before other content",
        "missing repository asset produces asset fallback",
        "speaking wins over simultaneous loading",
        "terminal playback phases return to idle presentation",
    ):
        require(model_tests, marker, "model-test marker")

    for marker in (
        "renders mood state with static character profile",
        "renders advice content without changing profile ownership",
        "shows deterministic loading and speaking activity",
        "fallback presentation uses safe static-runtime wording",
        "retries the repository fallback image before generic placeholder",
    ):
        require(widget_tests, marker, "widget-test marker")

    require(contract, "1. character unavailable", "content precedence")
    require(contract, "1. speaking", "activity precedence")
    require(contract, "HomeScreen still owns all data loading", "HomeScreen ownership")
    require(contract, "V-1c implements repository fallback-image retry", "V-1c handoff")
    require(contract, "implementation commit: e1f8d6f", "accepted implementation commit")
    require(contract, "Backend pytest: 110 passed", "accepted Backend count")
    require(contract, "full Flutter test: 97 passed", "accepted Flutter count")

    require(home, "CharacterDisplayCard(", "V-1c HomeScreen widget integration")
    require(home, "CharacterDisplayPresentation.resolve(", "V-1c HomeScreen model integration")
    require(integration_tests, "in-app audio playback drives speaking presentation", "V-1c speaking test")
    require(home_contract, "COMPLETED / ACCEPTED", "V-1c contract state")
    forbid(model + widget, "dart:math", "random state selection")
    forbid(model + widget, "Timer(", "timer-driven animation")
    forbid(model + widget, "WebSocket", "motion runtime connection")

    assert_hashes(PROTECTED_RELEASE_HASHES, "Protected release record")
    assert_hashes(UNCHANGED_V1B_HASHES, "V-1b unchanged baseline")
    assert_hashes(STATIC_ASSET_HASHES, "V-1b static asset baseline")

    for relative in (
        "app/lib/models/character_display_presentation.dart",
        "app/lib/widgets/character_display_card.dart",
        "app/test/character_display_presentation_test.dart",
        "app/test/character_display_card_test.dart",
        "docs/v210_character_display_state_contract.md",
        "README.md",
        "roadmap.md",
        "tasklist.md",
        "scripts/README.md",
        "docs/DRC_v210_goal_checklist_small_commit.md",
        "docs/v210_character_display_current_behavior_inventory.md",
        "scripts/check_v210_character_display_current_behavior_inventory.py",
        "scripts/check_v210_character_display_state.py",
        "app/lib/screens/home_screen.dart",
        "app/lib/ui/character_asset_catalog.dart",
        "app/test/widget_test.dart",
        "app/test/character_display_home_integration_test.dart",
        "docs/v210_character_display_home_integration.md",
    ):
        assert_no_sensitive_values(relative, read(relative))

    print("v210_character_display_state_status: completed-accepted")
    print("v210_character_display_state_completed_small_commit: V-1b")
    print("v210_character_display_state_current_small_commit: R-1")
    print("v210_character_display_state_parent_phase: V-1-completed-accepted")
    print("v210_character_display_state_content_states: mood,advice,fallback")
    print("v210_character_display_state_activity_states: idle,loading,speaking")
    print("v210_character_display_state_focused_model_tests: 9")
    print("v210_character_display_state_focused_widget_tests: 4")
    print("v210_character_display_state_home_integration: true")
    print("v210_character_display_state_v1c_runtime_started: true")
    print("v210_character_display_state_current_card_tests: 5")
    print("v210_character_display_state_backend_runtime_changed: false")
    print("v210_character_display_state_assets_changed: false")
    print("v210_character_display_state_real_motion_execution: false")
    print("v210_character_display_state_release_records_changed: false")
    print("[v210-character-display-state-check] OK")


if __name__ == "__main__":
    main()
