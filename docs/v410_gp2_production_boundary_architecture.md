# DRC v4.1.0 GP-2 Production Boundary Architecture

## Control metadata

```text
Task: DRC_V410_GP2_PRODUCTION_ENTRYPOINT_FOUNDATION_R1
Baseline: 14ef092cd643fbf02c3bdfde3fa702ed062c3ef3
Phase: GP-2
Implementation: APPROVED
Stage / commit / push: NOT_AUTHORIZED
```

GP0-D04 is `APPROVED`. The approved value is: Separate production entrypoint
and production-only composition with structural import, route, and Backend
reachability boundaries. Approval evidence: User selection recorded
2026-09-18.

## Entrypoint ownership

| Entrypoint | Ownership | Current role |
| --- | --- | --- |
| `lib/main_production.dart` | Production candidate | Starts only `ProductionApp`. |
| `lib/main.dart` | Existing mixed development/demo | Unchanged; still the Flutter default target. |
| `lib/main_rt2ec_operator.dart` | Operator | Unchanged and outside production composition. |

Because `main.dart` remains Flutter's default target, this control alone does
not make a default or Google Play build release-safe. GP-4 owns release wiring
and any later authorized `-t lib/main_production.dart` build.

## Production import boundary

`main_production.dart` may import only Flutter and
`production/production_app.dart`. Source under `lib/production/` may import only
Flutter and relative files within that directory. It must not import existing
screens, services, operators, widgets, UI helpers, mixed entrypoints, or raw
Backend clients. Compile-time visual switching is not used as a boundary.

## Production route allowlist

The current allowlist contains only `ProductionHomeScreen` as
`MaterialApp.home`. There are no named, developer, operator, demo, diagnostic,
or fallback routes. Route expansion requires a later bounded control.

## Non-product reachability prohibitions

Production composition must not reach `HomeScreen`, `HistoryScreen`, RT2EC,
demo/realtime/framework runtimes, raw diagnostics, or existing Backend service
code. Hiding controls in widgets or behind flags is insufficient because the
code and routes would remain reachable.

## Backend boundary

The production composition has no network or data-layer wiring. It performs no
Backend, health-provider, microphone, permission, voice, or motion call. A
production endpoint allowlist, HTTPS configuration, and artifact-level proof
remain for later GP-2/GP-4 controls.

## Control A implementation scope

This reversible control adds one production entrypoint, a production-only app
composition, a minimal accessible shell, focused boundary tests, and this
architecture record. It does not migrate the daily flow or edit existing mixed
and operator entrypoints.

## Focused verification

- `flutter analyze --no-pub`
- `flutter test --no-pub test/production_composition_boundary_test.dart`
- `flutter test --no-pub test/widget_test.dart`
- Static recursive import and forbidden-reference scans.

The focused test checks structure rather than treating visual hiding as proof.

## Rollback and stop conditions

Stop without staging or committing if the baseline changes, the eight-file
surface expands, an import crosses the allowlist, existing entrypoints change,
or any authorized verification fails. Rollback requires separate authorization;
this control does not use reset, checkout, or revert.

## Handoff to later controls

- GP-2: migrate approved product components, add Backend allowlists, and prove
  non-product exclusion from an artifact.
- GP-3: design and implement the core daily journey within this boundary.
- GP-4: configure Android identity/signing/release target and production entry
  wiring, then build only under separate authorization.
- GP-5: reconcile implemented data behavior with privacy, deletion, Data safety,
  and Health Apps declarations.

## Non-claims

This foundation is not a completed production UI, migrated core flow, Backend
publication, Android release configuration, signed AAB, Google Play build,
testing-track result, policy completion, or production-readiness claim. GP-2 as
a whole remains incomplete.

## Control B: text-core capability boundary

Control A was reviewed, accepted, committed, pushed, and closed at
`e0e7e8434e49f812735b9d4a510997ad0108d174`. GP2-S01 approves
`TEXT_CORE_PLUS_CHAT` for the bounded production scope.

Control B adds typed capability and symbolic Backend-operation definitions only
under `lib/production/`. The new sources preserve the Control A import boundary:
they do not import UI, network, platform, legacy model/service/widget, or
Backend client code. They contain no network client, URL, endpoint path, or
credential and perform no communication.

Core-candidate operations and health-pending operations have exactly one typed
disposition. Health-pending operations are excluded from the active core set.
Unknown and non-product operations have no representation and are denied by
default. The production Backend remains unwired because GP0-D03 and GP0-D08 are
unresolved.

This control does not migrate UI, select a provider, approve a URL, wire the
Backend, wire a release target, prove artifact exclusion, or complete GP-2.
