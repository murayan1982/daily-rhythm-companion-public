# v2.1.0 V-1a character display current behavior inventory

Updated: 2026-07-24
Status: COMPLETED / ACCEPTED
Parent phase: V-1 CURRENT / NOT_COMPLETED
Completed small commit: V-1a — Character display current behavior inventory and implementation contract
Current small commit: V-1b — Deterministic presentation model and standalone widget
Current implementation state: IMPLEMENTED / NOT_ACCEPTED

## Purpose

```text
- Read the current Flutter character display implementation before changing it.
- Freeze the accepted static-asset and existing widget-test baseline.
- Separate the normal daily-loop character display from the Advanced Motion Demo boundary.
- Record exactly how mood, advice, loading, speaking, and fallback state are represented today.
- Assign V-1b and V-1c responsibilities without starting their runtime changes.
- Keep R-1 PLANNED and preserve the v2.0.0/v2.0.1 release records.
```

V-1a is documentation and source-tree validation only. It does not change Flutter runtime,
Backend runtime, existing tests, dependencies, assets, configured providers, or release records.

## Inspected files

```text
app/lib/screens/home_screen.dart
app/lib/models/character_preset.dart
app/lib/models/advice_response.dart
app/lib/models/advice_source.dart
app/lib/models/motion_demo.dart
app/lib/services/voice_output_audio_player.dart
app/lib/ui/character_asset_catalog.dart
app/test/widget_test.dart
app/pubspec.yaml
app/assets/images/characters/gentle_mina_demo.png
app/assets/images/characters/cheerful_sora_demo.png
app/assets/images/characters/cool_rei_demo.png
app/assets/images/backgrounds/morning_room_soft.png
app/assets/images/backgrounds/night_room_calm.png
app/assets/images/placeholders/character_fallback.png
```

## Current HomeScreen ownership

`app/lib/screens/home_screen.dart` is currently 4,195 lines. The same StatefulWidget owns:

```text
- initial Backend, character, sleep, and provider-status loading;
- selected character and selected mood state;
- character-aware mood copy;
- advice creation and advice result state;
- post-advice chat state;
- TTS generation and in-app playback state;
- static character/background/fallback asset previews;
- the Advanced Motion Demo simulator and guarded request UI;
- history and daily-loop completion presentation.
```

The current character display is the private `_buildCharacterSection()` method inside
`HomeScreen`. No standalone normal-loop character display widget or presentation model exists.

## Character model contract

`CharacterPreset` contains only the accepted stable fields:

```text
characterId
displayName
description
personalityType
speakingStyle
adviceStyle
```

V-1 does not require provider-specific fields, animation fields, Live2D parameters, VTube Studio
parameters, or a new Backend response model.

## Static repository-safe asset baseline

`CharacterAssetCatalog` resolves three known character IDs and one fallback image:

```text
gentle_mina  -> assets/images/characters/gentle_mina_demo.png
cheerful_sora -> assets/images/characters/cheerful_sora_demo.png
cool_rei     -> assets/images/characters/cool_rei_demo.png
unknown ID   -> assets/images/placeholders/character_fallback.png
```

Accepted asset inventory:

```text
characters/gentle_mina_demo.png       1024 x 1024
characters/cheerful_sora_demo.png     1024 x 1024
characters/cool_rei_demo.png          1024 x 1024
backgrounds/morning_room_soft.png      1920 x 1080
backgrounds/night_room_calm.png        1920 x 1080
placeholders/character_fallback.png    1024 x 1024
```

Each character has one static image. There are no repository assets for per-character mood,
advice, loading, or speaking expression variants. V-1 therefore keeps the accepted static images
and expresses deterministic state through app-owned presentation, not through claimed animation or
unverified generated assets.

## Current state presentation

### Mood

```text
- `_selectedMood` uses the stable IDs energetic, normal, and tired.
- `_characterAwareMoodChoiceCopy` changes labels/support copy by selected character.
- Mood is shown in the Mood section and readiness summaries.
- Mood does not currently change the selected-character card state or image treatment.
```

### Advice

```text
- `_adviceResponse` is cleared while a new advice request starts.
- Advice content is shown later in `_buildAdviceSection()`.
- `AdviceSource.engine` can distinguish mock, framework, and framework_fallback.
- Advice result/fallback does not currently change the selected-character card state.
```

### Loading

```text
- `_isLoading` controls initial-page progress and the character-section loading spinner.
- `_isCreatingAdvice` controls the advice button and a separate LinearProgressIndicator.
- voice playback has its own loading state in VoiceOutputPlaybackState.
- No single character-display loading presentation combines these accepted activity states.
```

### Speaking

```text
- VoiceOutputPlaybackState has idle, loading, playing, stopped, completed, failed, and expired.
- The in-app player displays playing as an audio-player state.
- Playing does not currently produce a speaking state in the normal character display.
```

### Fallback

```text
- Unknown character IDs resolve to CharacterAssetCatalog.fallbackCharacter.
- An actual Image.asset load failure currently falls through to a generic grey
  image_not_supported placeholder rather than retrying the repository fallback asset.
- framework_fallback is visible in advice source/debug presentation, but there is no unified
  normal character-display fallback state.
- Raw audio URLs and private paths remain hidden from normal UI and are outside V-1.
```

## Motion Demo separation

The Advanced Motion Demo is a separate guarded developer/demo surface. It contains manual
motion/expression selections and a lightweight emoji simulator, including states such as idle,
happy, thinking, supportive, and speaking.

```text
- Motion Demo request presence does not prove motion adapter execution.
- `motionSent` and `vtsConnectionUsed` remain explicit provider-neutral fields.
- The accepted normal character display must not reuse discovery or simulator output as a claim
  of Live2D or VTube Studio execution.
- V-1 does not connect a real motion adapter and does not change the Motion Demo API/model.
```

## Existing widget-test baseline

`app/test/widget_test.dart` is currently 2,669 lines and includes coverage for:

```text
- character selection changing selected name/profile and static image asset;
- selected character and stable mood IDs reaching advice creation;
- character-aware mood labels remaining presentation-only;
- the accepted background and fallback assets appearing in Web UI;
- framework_fallback advice through an unavailable-sleep fake;
- the Advanced Motion Demo remaining unavailable/not configured and motion not sent.
```

Missing focused V-1 coverage:

```text
- a pure deterministic character-display presentation resolver;
- standalone character-display widget states;
- advice versus mood content precedence;
- loading and speaking activity precedence;
- framework_fallback normal-user presentation;
- unknown-character and asset-load fallback behavior;
- focused HomeScreen integration after extraction.
```

## Normalized source-tree hashes frozen by V-1a

```text
app/lib/screens/home_screen.dart
  1fdd4e82338904a175112e5eb74386ea5797308aea71cde64161970fb42e44c1
app/lib/models/character_preset.dart
  66896fa5ff7ffc2cf5e1497bfc3ce18ba555809ca73ebc60c655cd867075cf08
app/lib/models/advice_response.dart
  99d26ce001213bafe44d917a459ae1491913af85cb33b897e0b81172f89046f7
app/lib/models/advice_source.dart
  99ba85cb63901fe2ef3f2d2d7d7bd0ef38977eccad7277f53d937e11d17425fe
app/lib/models/motion_demo.dart
  5e3fafa3fba66d92fe589d7b913bf350842b28d02218c3a54903d45c5f5fab89
app/lib/services/voice_output_audio_player.dart
  3089e8423c5ec758c54684e55d100b300753b4e71e7553e6a72daff1865e388a
app/lib/ui/character_asset_catalog.dart
  6e3ab31eb3ac2c1c97899c7fa64eb5d04c808932322feb240e2bf6ea5762df54
app/test/widget_test.dart
  dd869daa9123dbdd98e11a43d00c4ec56f2238f54e12d3c02cbd5313d479db04
app/pubspec.yaml
  78ea66a2c1c4f96deced1063bf9f00369e7507c415e87d769a556b392dec4756
```

Static asset hashes:

```text
app/assets/images/characters/gentle_mina_demo.png
  7f6a7b9d071c7a6897a4e66aaf81a92c6ef0b78c63c8d6a0ea7c22b13d59ac72
app/assets/images/characters/cheerful_sora_demo.png
  2f0ad34642252d17851ce437e484d31ab5ee960e539a55d09f0ad87e4474627b
app/assets/images/characters/cool_rei_demo.png
  932fd68c601b21577895a2cbf7569368a03b0561914d78f2cd8ef92fabf00b91
app/assets/images/backgrounds/morning_room_soft.png
  f0b158b32affbc085f2650eb852407aad193a4bcaa5fb23a6417ca4999085ea7
app/assets/images/backgrounds/night_room_calm.png
  46d01e2b5f9a8a1683a15d0fe648a2d6e60bd3144cb112418cff1f53015c47af
app/assets/images/placeholders/character_fallback.png
  3e37a8318aa344d928b4c811edb796c643f39086a5a2204f2cb872084ee7d601
```

These hashes prove that V-1a itself is docs/test-only. Later accepted V-1b/V-1c changes are
allowed to update only their explicitly assigned Flutter files and tests; the V-1a historical check
must then be synchronized without weakening the static-asset, release-record, or Motion Demo guards.

## V-1a acceptance record

```text
implementation commit: 1602b2f
compileall: passed
all check_v210_*.py: passed
v2.0.x compatibility / maintenance guards: passed
Backend pytest: 110 passed
Flutter test: 84 passed
git diff --check: no real error
diff review: docs/test-only scope confirmed
operator approval: explicit
Flutter runtime changed: false
Backend runtime changed: false
existing tests changed: false
dependencies/assets changed: false
real provider or motion execution: false
release records changed: false
```

V-1a was completed and accepted on 2026-07-24. Parent V-1 remains CURRENT / NOT_COMPLETED.
V-1b is CURRENT / NOT_COMPLETED; V-1c and R-1 remain PLANNED.

## V-1 implementation split

### V-1a — Current behavior inventory and implementation contract

```text
Status: COMPLETED / ACCEPTED
Runtime changed: false
Existing tests changed: false
Dependencies/assets changed: false
Real provider or motion execution: false
```

Acceptance passed after the source-tree check, all accepted v2.1.0 checks, v2.0.x guards,
110 Backend tests, 84 Flutter tests, diff review, and explicit operator approval.

### V-1b — Deterministic presentation model and standalone widget

```text
Status: CURRENT / NOT_COMPLETED
Implementation state: IMPLEMENTED / NOT_ACCEPTED
- Add an app-owned deterministic presentation model.
- Keep content state and activity state independently representable.
- Cover mood, advice, fallback, idle, loading, and speaking with fake/model-only tests.
- Add a standalone character-display widget without connecting HomeScreen yet.
- Do not change Backend, provider APIs, Motion Demo, assets, or release records.
```

Planned state direction:

```text
content state: mood | advice | fallback
activity state: idle | loading | speaking
```

Exact precedence and user-facing copy are frozen in `docs/v210_character_display_state_contract.md`. The implementation adds `CharacterDisplayPresentation`, `CharacterDisplayCard`, nine model tests, and four widget tests without connecting HomeScreen.

### V-1c — HomeScreen extraction and integration

```text
Status: PLANNED
- Replace the private HomeScreen character-card rendering with the accepted standalone widget.
- Keep HomeScreen ownership of data loading, selection callbacks, advice creation, and TTS control.
- Connect accepted mood/advice/loading/speaking/fallback inputs deterministically.
- Preserve existing widget keys and behavior where practical.
- Retry the repository-safe fallback asset before using a generic missing-image placeholder.
- Add focused HomeScreen integration tests.
- Do not change Backend runtime, Motion Demo execution, dependencies/assets, or release records.
```

V-1 and V-1c are not completed from V-1a acceptance. A separate acceptance sync is required
after focused tests, aggregate tests, builds required by the accepted contract, diff review, and
operator approval pass.

## Explicit exclusions

```text
- No new character image generation or asset replacement.
- No animation timing or random expression selection.
- No Live2D or VTube Studio connection.
- No motion API/model/runtime change.
- No Backend response-model change.
- No real LLM, TTS, health-provider, or motion request.
- No private env, token, raw health payload, exact sleep value, audio, screenshot, LAN IP,
  private path, or operator evidence.
- No v2.0.0/v2.0.1 tag, GitHub Release, fixed ZIP, or historical release-record change.
- No R-1 completion or release preparation.
```

## V-1a verification command

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_character_display_current_behavior_inventory.py

# Then run all accepted check_v210_*.py and the v2.0.x compatibility guards.
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

Normal verification remains credential-free, provider-free, network-free, decoder-free, and
motion-adapter-free.
