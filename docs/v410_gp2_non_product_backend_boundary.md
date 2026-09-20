# DRC v4.1.0 GP-2 Non-product Backend Boundary

Task: `DRC_V410_GP2_NON_PRODUCT_BACKEND_BOUNDARY_R1`

Baseline: `eb9e27e6d470252e2543de17d4a168d68fdecfbc`

Implementation surface: exact M6 A2 D0.

## Access-decision contract

`ProductionBackendOperation` remains an exact 14-value symbolic candidate set,
not an endpoint allowlist. `ProductionBackendAccessDecision` is deny by default:

- `allowCoreCandidate` applies only to the 11 core candidates below;
- `denyHealthPendingDecision` applies to the three unresolved health operations;
- `denyUnknown` applies to strings, arbitrary objects, unregistered operations,
  and every legacy non-product method or route name.

`allowCoreCandidate` does not authorize communication, implementation, or
release wiring. Any future production Backend adapter must pass every operation
through `productionBackendAccessDecisionFor` before attempting transport.

### Core candidates

- `loadCharacters`
- `loadSleepSummary`
- `loadSleepProviderSelection`
- `createAdvice`
- `createTextChatSession`
- `sendTextChatMessage`
- `loadHistory`
- `loadRecentSleepTrend`
- `loadWeeklySleepSummary`
- `loadWeeklyRhythmReport`
- `loadMonthlyRhythmReport`

### Health pending

- `loadFitbitConnectionStatus`
- `startFitbitConnection`
- `loadGoogleHealthConnectionGuidance`

These operations are explicitly denied pending later decisions; they are not
classified as unknown.

## Non-product inventory

Legacy health status, demo status, Google Health diagnostics/self-check/
preflight, voice input/output demo, motion demo, realtime, framework lifecycle,
and raw `/health` operations remain in non-product source. They are deliberately
unrepresentable as `ProductionBackendOperation` values and resolve to
`denyUnknown` when their method names or route strings reach the access policy.

The production graph consists of `lib/main_production.dart` and
`lib/production/**/*.dart`. It excludes `BackendApiClient`, legacy services,
models, screens, widgets, operators, transport clients, endpoint and route
literals, URLs, private hosts, and platform or permission access.

## Verification

```text
flutter analyze --no-pub
flutter test --no-pub test/production_backend_reachability_boundary_test.dart
flutter test --no-pub test/production_core_scope_boundary_test.dart
flutter test --no-pub test/production_composition_boundary_test.dart
flutter test --no-pub test/production_journey_shell_test.dart
flutter test --no-pub test/non_product_entrypoint_boundary_test.dart
flutter test --no-pub test/widget_test.dart
git diff --check
```

Stop and roll back this candidate if a production source gains a non-product
symbol, route, import, transport, URL, host, platform dependency, or if any
operation outside the 11 core candidates becomes allowed.

## Handoff and non-claims

Later controls still own core-flow migration, artifact exclusion proof,
production Backend adapter and environment configuration, Android release
wiring, and release verification. The production Backend remains unwired; its
provider, URL, and host are undecided. GP0-D03 and GP0-D08 remain
`NOT_DECIDED`. Health operations remain inactive. Backend source is unchanged,
artifact exclusion is not yet proved, and GP-2 as a whole is incomplete.
