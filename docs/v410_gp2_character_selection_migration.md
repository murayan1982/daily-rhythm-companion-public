# DRC v4.1.0 GP-2 Character Selection Migration R1

## Control metadata

```text
Task: DRC_V410_GP2_CHARACTER_SELECTION_MIGRATION_R1
Baseline: 7bb18d1fc8438d702afd440655bcf84fd6907774
Branch: main
Surface: exact M6 A4 D0
Implementation and required analyze/test: APPROVED
Stage / commit / push: NOT_AUTHORIZED
```

## Approved scope

This second Core-flow slice adds only a production-local character selection
for journey step 3. Initial state is unselected and selection is held only in
widget state.

## Existing stable character catalog

The read-only source documents remain `character_experience_inventory.md`,
`character_selection_ux_copy.md`, and `character_advice_tone_matrix.md`.
The catalog is exactly `gentle_mina / ミナ`, `cheerful_sora / ソラ`, and
`cool_rei / レイ`, in that order. Their accepted headline, tagline, tone
label, and selection summary are preserved exactly.

## Production typed model

`production_character.dart` is pure Dart. It defines exactly three enum
values, immutable options, stable IDs and copy fields, an ordered const list,
and a total fail-closed enum lookup. It imports no Flutter, Backend, service,
legacy model, Framework/provider type, URL, storage, or platform API.

## Local-only state boundary

Sleep remains `decisionPending`; mood and character are
`localSelectionAvailable`; advice, optional text chat, and history remain
`planned`. Character selection is not restored or persisted.

## UI and accessibility contract

The step exposes `3. キャラクターを選択`, exactly three mutually exclusive
ChoiceChips, all three selection-copy sets, explicit unselected/selected text,
unique option semantics, and selected semantics. Re-selecting the active option
does not clear it or invoke the callback. Narrow 320x568 and 2.0 text scale
must not overflow.

## Source and import boundary

New source is under `app/lib/production/` and imports only Flutter and
contained production files. It cannot reach legacy screens/models/services/
operators, non-product entrypoints, Backend clients, dart:io, HTTP/URL/
endpoints, platform channels, persistence/storage, voice/realtime/motion,
developer/operator UI, or raw diagnostics.

## Verification commands

Run from `app/`:

```text
flutter analyze --no-pub
flutter test --no-pub test/production_character_selection_test.dart
flutter test --no-pub test/production_mood_check_in_test.dart
flutter test --no-pub test/production_journey_shell_test.dart
flutter test --no-pub test/production_composition_boundary_test.dart
flutter test --no-pub test/production_core_scope_boundary_test.dart
flutter test --no-pub test/widget_test.dart
```

## Explicit non-claims

There is no Backend character fetch/communication, persistence, DailyRecord,
selection restoration, mood-to-advice or character-aware copy/advice,
Framework routing, provider/model selection, Framework asset, health/sleep,
permission, navigation, analytics, release-artifact proof, or public APK
readiness. D03/D08 remain `NOT_DECIDED`; D11 remains `APPROVED`.

## Remaining GP-2 / GP-3 work

Persistence, restoration, advice integration, character-aware behavior,
remaining Core-flow migration, artifact exclusion proof, onboarding, settings,
permission copy, and complete loading/empty/error/offline refinement remain
open. This slice completes neither GP-2 nor GP-3.

## Stop boundary

Stop after required verification and review handoff. Do not stage, commit,
push, build, sign, operate tags/Releases/assets or Console, run Backend,
external providers, Framework runtime, pytest, builder, or release verifier.
