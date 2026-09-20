# DRC v4.1.0 GP-2 Non-product Entrypoint Boundary

## Task metadata

```text
Task: DRC_V410_GP2_NON_PRODUCT_ENTRYPOINT_SEPARATION_R1
Baseline HEAD / origin/main / remote main: 719508fe1f7299744b5a717e9e1837f499032ab6
Phase: GP-2
Implementation: APPROVED
Stage / commit / push: NOT_AUTHORIZED
Current implementation surface: exact M6 A3 D0
Current state: IMPLEMENTED / STATIC_VERIFIED / READY_FOR_REVIEW
```

Control D separates the default mixed development composition from the production candidate by moving the existing default app body into a dedicated non-product entrypoint and leaving `main.dart` as a compatibility shim.

## Entrypoint ownership matrix

| Entrypoint | Ownership | Contract |
| --- | --- | --- |
| `lib/main_production.dart` | Production candidate | Starts only `ProductionApp`; release wiring remains GP-4 work. |
| `lib/main.dart` | Default non-product compatibility shim | Re-exports `DailyRhythmCompanionApp` and delegates to `main_non_product.main()`. It is not the Google Play release target. |
| `lib/main_non_product.dart` | Mixed development/demo/diagnostic composition | Byte-preserved copy of the baseline default composition with `HomeScreen`, runtime factories, and `BackendApiClient`. |
| `lib/main_rt2ec_operator.dart` | Operator-only composition | Preserved as a standalone non-product operator target outside the production graph. |

## Production route allowlist

The production candidate remains `MaterialApp.home = ProductionHomeScreen`. Named `routes` are empty and `onGenerateRoute` / `onUnknownRoute` are null. Route expansion requires a later bounded control.

## Production graph exclusion contract

`main_production.dart` and `lib/production/` must not reference `main.dart`, `main_non_product.dart`, `main_rt2ec_operator.dart`, `DailyRhythmCompanionApp`, `HomeScreen`, developer/operator/demo/diagnostic source, mixed services, widgets, operators, or raw Backend clients. Source hiding, visual hiding, and feature flags are not accepted as production-boundary proof.

## Preserved developer/operator capability

The default Flutter target continues to launch the existing non-product mixed app through the shim. Existing tests that import `package:app/main.dart` can still resolve `DailyRhythmCompanionApp`. The RT2EC operator entrypoint remains separate and is not folded into production.

## Verification commands

```text
flutter analyze --no-pub
flutter test --no-pub test/non_product_entrypoint_boundary_test.dart
flutter test --no-pub test/production_composition_boundary_test.dart
flutter test --no-pub test/production_core_scope_boundary_test.dart
flutter test --no-pub test/production_journey_shell_test.dart
flutter test --no-pub test/widget_test.dart
flutter test --no-pub test/main_realtime_text_stream_wiring_widget_test.dart test/main_realtime_terminal_voice_output_wiring_widget_test.dart test/main_integrated_voice_turn_wiring_widget_test.dart test/main_character_motion_presentation_wiring_widget_test.dart test/main_framework_vts_motion_wiring_widget_test.dart test/framework_v600_realtime_session_main_composition_test.dart
```

## Rollback and stop conditions

Stop without staging or committing if the baseline changes, the surface differs from exact M6 A3 D0, production imports cross the allowlist, protected product files change unexpectedly, D03/D08 are changed from `NOT_DECIDED`, Backend wiring appears, or verification fails. Rollback requires separate authorization.

## Non-claims

- Default `main.dart` is not the Google Play release target.
- GP-4 must wire `main_production.dart` for any release build.
- Artifact exclusion proof is not complete.
- The non-product Backend boundary is not complete.
- The production Backend is unwired.
- GP0-D03 and GP0-D08 remain `NOT_DECIDED`.
- GP-2 as a whole is not complete.
