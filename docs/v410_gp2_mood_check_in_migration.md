# DRC v4.1.0 GP-2 Mood Check-in Migration R1

## Control metadata

```text
Task: DRC_V410_GP2_MOOD_CHECK_IN_MIGRATION_R1
Baseline: 3962a4757f918461382a935625a8b990f960df0e
Branch: main
Surface: exact M6 A4 D0
Implementation: APPROVED
Relevant analyze/test: AUTHORIZED
Stage / commit / push: NOT_AUTHORIZED
```

## Approved scope

This first Core-flow migration slice moves only the existing three-choice mood
selection into the production-only graph. It provides local UI state for
`energetic / ☀️ / 元気`, `normal / 🌿 / ふつう`, and
`tired / 😪 / だるい`. Initial state is unselected.

## Legacy behavior source

The behavior is derived from the non-product HomeScreen's private mood choice.
Production code neither imports nor modifies that implementation or any legacy
screen, model, widget, service, or operator source.

## Production typed model

`production_mood.dart` is pure Dart. It defines the three-value enum,
immutable option records, exact code/emoji/label/support-message mapping, and a
fail-closed enum-to-option lookup. It imports no Flutter, Backend, service, or
legacy model.

## Local-only state boundary

`localSelectionAvailable` applies only to the mood step. Sleep remains
`decisionPending`; the other four steps remain `planned`. Selection is
held only in the widget and is not persisted or transmitted.

## UI and accessibility contract

The mood item alone renders three mutually exclusive ChoiceChips in a Wrap.
The group exposes `2. 気分を記録`; each option exposes its label and selected
state. The UI shows explicit selected/unselected text, support copy after
selection, and a permanent notice that saving and advice integration are in
preparation. Narrow 320x568 and 2.0 text-scale layouts must not overflow.

## Source and import boundary

Production source stays inside `app/lib/production/` and may import only
Flutter and contained relative production files. It has no reachability to
screens, services, legacy models/widgets/operators, non-product entrypoints,
Backend clients, dart:io, HTTP/URL/endpoints, platform channels, persistence,
or storage. Existing recursive directive guards are unchanged.

## Verification commands

Run from `app/`:

```text
flutter analyze --no-pub
flutter test --no-pub test/production_mood_check_in_test.dart
flutter test --no-pub test/production_journey_shell_test.dart
flutter test --no-pub test/production_composition_boundary_test.dart
flutter test --no-pub test/production_core_scope_boundary_test.dart
flutter test --no-pub test/widget_test.dart
```

## Explicit non-claims

This control implements no Backend communication, persistence, DailyRecord,
advice generation, character-aware copy, health/sleep integration, permission,
navigation, platform API, analytics, or production Backend wiring. D03 and D08
remain `NOT_DECIDED`; D11 remains `APPROVED`.

## Remaining GP-2 and GP-3 work

Mood persistence, mood-to-advice wiring, character-aware copy, remaining
Core-flow migration, release-artifact exclusion proof, onboarding, settings,
permission copy, and complete loading/empty/error/offline refinement remain
open. This slice completes neither GP-2 nor GP-3.

## Stop boundary

Stop after authorized static analysis/tests and review handoff. Do not stage,
commit, push, build, sign, operate tags/Releases/assets or Console, run Backend
pytest, builder, or release verification.
