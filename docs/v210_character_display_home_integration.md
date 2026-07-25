# v2.1.0 V-1c HomeScreen character display integration

Updated: 2026-07-25
Status: COMPLETED / ACCEPTED
Completed small commit: V-1c — HomeScreen extraction and integration
Parent phase: V-1 — COMPLETED / ACCEPTED
Current small commit: none — v2.1.0 RELEASED / ACCEPTED

## Purpose

V-1c connects the accepted V-1b deterministic character presentation boundary to the existing
HomeScreen without adding a Live2D/VTube Studio runtime, changing Backend behavior, or replacing
the repository-safe static assets.

The integration keeps HomeScreen ownership of data loading, character selection, advice creation,
and TTS controls. `CharacterDisplayPresentation` resolves the visible state and
`CharacterDisplayCard` renders the normal static character surface.

## Changed Flutter boundary

```text
app/lib/screens/home_screen.dart
app/lib/ui/character_asset_catalog.dart
app/lib/widgets/character_display_card.dart
app/test/widget_test.dart
app/test/character_display_card_test.dart
app/test/character_display_home_integration_test.dart
```

No dependency or asset file is added or replaced.

## Deterministic HomeScreen inputs

HomeScreen passes these existing values into the accepted V-1b resolver:

```text
character:
  _selectedCharacter

mood:
  _formatMoodLabel(_selectedMood)
  _formatMoodSupportMessage(_selectedMood)

advice:
  _adviceResponse

loading:
  _isLoading
  OR _isCreatingAdvice
  OR _isSubmittingVoiceOutputDemo

speaking:
  _voiceOutputAudioPlayerController.state.phase == playing

repository asset availability:
  CharacterAssetCatalog.hasCharacterAsset(characterId)
```

The accepted V-1b precedence remains unchanged:

```text
content:
  character unavailable
  -> repository asset unavailable
  -> framework fallback
  -> non-empty advice
  -> mood

activity:
  speaking
  -> loading
  -> idle
```

No random, timer-driven, provider-driven, or motion-adapter state selection is added.

## Static image fallback

Known character IDs continue to use the existing repository character images.
Unknown IDs use the existing repository fallback image and resolve to the deterministic
`assetUnavailable` content state.

If a selected image fails to load at runtime, `CharacterDisplayCard` retries
`assets/images/placeholders/character_fallback.png`. Only if that repository fallback also fails
does the generic `image_not_supported_outlined` placeholder appear.

The six accepted image files and `app/pubspec.yaml` registration remain unchanged.

## Existing UI ownership

The following remain owned by HomeScreen:

```text
- Backend data loading and error handling
- character candidate list and selection callback
- mood selection
- advice request lifecycle
- voice-output request and playback controller lifecycle
- Advanced Motion Demo simulator and request boundary
```

The extracted card owns only the normal static presentation surface:

```text
- selected repository-safe image
- mood / advice / fallback content chip and copy
- idle / loading / speaking activity chip and copy
- CharacterPreset profile fields
- explicit static-display and no-Live2D/VTS wording
```

## Focused mock-safe tests

`app/test/character_display_home_integration_test.dart` adds five credential-free widget tests:

```text
1. initial loading -> resolved mood state
2. mood change -> advice loading -> advice state
3. framework_fallback -> safe card copy
4. in-app audio playback -> speaking state
5. unknown character ID -> repository fallback state/image
```

`app/test/character_display_card_test.dart` adds one focused fallback-image retry test.
The existing character-choice test is updated to use the extracted card's stable detail keys while
preserving the accepted selection, asset, profile, and advice-flow assertions.

Expected Flutter counts after V-1c implementation:

```text
presentation-model focused tests: 9
character-card focused tests: 5
HomeScreen integration focused tests: 5
full Flutter tests: 103
```

These tests use only fake Backend clients, fake audio engines, deterministic fixtures, and bundled
assets. They do not call a real provider, decode real audio, access credentials, or connect a motion
adapter.

## Explicit exclusions

V-1c does not:

```text
- connect Live2D or VTube Studio;
- alter the Advanced Motion Demo contract;
- add or replace character/background assets;
- change Flutter dependencies or platform plugin registration;
- change Backend routes, models, services, or tests;
- execute real LLM, TTS, health, or motion providers;
- change v2.0.0/v2.0.1 release records, tags, GitHub Releases, or fixed ZIPs;
- complete R-1 or perform release publication work.
```

## Verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_character_display_current_behavior_inventory.py
python scripts\check_v210_character_display_state.py
python scripts\check_v210_character_display_home_integration.py
python -m pytest -q backend/tests

cd app
flutter test test/character_display_presentation_test.dart
flutter test test/character_display_card_test.dart
flutter test test/character_display_home_integration_test.dart
flutter test
flutter build web
flutter build windows
cd ..

git diff --check
```

V-1c acceptance passed on 2026-07-24:

```text
implementation commit: 995145d
all check_v210_*.py / v2.0.x guards: passed
Backend pytest: 110 passed
focused presentation-model tests: 9 passed
focused character-card tests: 5 passed
focused HomeScreen integration tests: 5 passed
full Flutter test: 103 passed
Flutter Web / Windows builds: passed
existing character-choice regressions: passed
repository fallback-image retry: passed
diff review / explicit operator approval: passed
Backend / Motion Demo / dependencies / static assets changed: false
real provider or motion execution: false
release records changed: false
```

V-1c, parent V-1, R-1e, and parent R-1 are `COMPLETED / ACCEPTED`; v2.1.0 is released.
