# v2.1.0 V-1b deterministic character display state contract

Updated: 2026-07-24
Status: COMPLETED / ACCEPTED
Parent phase: V-1 CURRENT / NOT_COMPLETED
Completed small commit: V-1b — Deterministic presentation model and standalone widget
Current small commit: V-1c — HomeScreen extraction and integration
Current small commit: V-1c — HomeScreen extraction and integration (CURRENT / NOT_COMPLETED; NOT_STARTED)

## Purpose

```text
- Add an app-owned deterministic presentation model for the normal character display.
- Keep content and activity state independently representable.
- Add a standalone static character card without connecting HomeScreen yet.
- Cover the contract with model-only and widget-only Flutter tests.
- Preserve the accepted static assets, Backend contract, Motion Demo boundary, and release records.
```

V-1b does not call a provider, decode real audio, connect Live2D/VTube Studio, or alter
HomeScreen. It defines the presentation boundary that V-1c will connect.

## Change surface

```text
app/lib/models/character_display_presentation.dart
app/lib/widgets/character_display_card.dart
app/test/character_display_presentation_test.dart
app/test/character_display_card_test.dart
docs/v210_character_display_state_contract.md
scripts/check_v210_character_display_state.py
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_character_display_current_behavior_inventory.md
scripts/check_v210_character_display_current_behavior_inventory.py
```

## Content-state contract

```text
mood
  Used when a repository-backed character is available and no non-empty advice exists.

advice
  Used when a repository-backed character is available and a non-empty advice message exists.

fallback
  Used when character data is unavailable, the character has no repository asset,
  or advice source.engine is framework_fallback.
```

Deterministic precedence:

```text
1. character unavailable
2. repository character asset unavailable
3. framework_fallback advice source
4. non-empty advice
5. mood
```

The fallback state does not display provider exception text or the original fallback advice body.
It uses fixed app-owned normal-user copy.

## Activity-state contract

```text
idle
  No active character-display work. Stopped, completed, failed, and expired audio phases
  return to idle presentation.

loading
  Initial/advice work is active, or the accepted audio controller is in loading.

speaking
  The accepted audio controller is in playing.
```

Deterministic precedence:

```text
1. speaking
2. loading
3. idle
```

Speaking wins when app loading and audio playing are simultaneously reported.

## Safe normal-user copy

```text
mood title: <character>と今日の気分
advice title: <character>からのアドバイス
fallback labels: 代替表示 / 安全な代替アドバイス / 共通の静的表示
activity labels: 待機中 / 準備中 / 音声再生中
static baseline label: 静的表示
```

The standalone widget explicitly states that its fallback note does not represent Live2D or
VTube Studio execution. No raw audio URL, private path, provider exception, token, or health
payload is accepted as display input.

## Standalone widget boundary

`CharacterDisplayCard` owns only presentation rendering:

```text
- selected static character image;
- content-state and activity-state chips;
- title, message, and activity copy;
- CharacterPreset profile fields;
- static-baseline and fallback disclaimers;
- a generic missing-image placeholder for an actual asset load failure.
```

HomeScreen still owns all data loading, character selection, mood copy, advice creation, and
TTS control. V-1b does not import or instantiate the standalone widget from HomeScreen.
The repository fallback-image retry before the generic placeholder remains V-1c integration work.

## Focused test contract

```text
character_display_presentation_test.dart
- mood, advice, and empty-advice behavior;
- character, asset, and framework fallback precedence;
- safe fallback copy that does not expose provider text;
- speaking-over-loading precedence;
- app/audio loading and terminal-audio idle behavior.

character_display_card_test.dart
- static image and CharacterPreset profile rendering;
- mood and advice copy;
- loading and speaking activity widgets;
- fallback disclaimer and no Live2D/VTS execution claim.
```

Tests use only const/fake model values and repository assets. They do not use Backend, network,
credentials, Framework, TTS providers, health providers, motion adapters, or private evidence.

## Unchanged boundaries

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
app/assets/**
backend/**
v2.0.0 / v2.0.1 tags, releases, fixed ZIPs, and historical release records
```

## Acceptance boundary

V-1b acceptance passed on 2026-07-24:

```text
implementation commit: e1f8d6f
compileall / all check_v210_*.py / v2.0.x guards: passed
Backend pytest: 110 passed
focused presentation-model Flutter tests: 9 passed
focused character-card Flutter tests: 4 passed
full Flutter test: 97 passed
diff review / explicit operator approval: passed
HomeScreen integration: false
Backend runtime / Motion Demo / dependencies / assets changed: false
real provider or motion execution: false
release records changed: false
```

V-1b is `COMPLETED / ACCEPTED`. V-1c is `CURRENT / NOT_COMPLETED` and `NOT_STARTED`; parent V-1 remains current/not completed and R-1 remains planned.
