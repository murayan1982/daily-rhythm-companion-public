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
| `app/lib/main_production.dart` | Production preview and current source-level candidate | Starts only `ProductionApp`. After extraction this remains the local preview. |
| `lib/main.dart` | Non-product compatibility shim | Default Flutter target; delegates to `main_non_product.dart` and is not release-safe. |
| `lib/main_non_product.dart` | Mixed development/demo/diagnostic | Owns the prior `HomeScreen` composition, runtime factories, and default development behavior. |
| `lib/main_rt2ec_operator.dart` | Operator | Preserved outside production composition. |

The default target of `app/` is the non-product shim. The approved future
public release target is defined in
[Control G](#control-g-public-flutter-application-boundary).

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

## Control C: local-only production journey shell

Control A closed at `e0e7e8434e49f812735b9d4a510997ad0108d174` and Control B closed at
`45d6a543165321e30757808095a545b0d9bc9ec1`. The Backend/privacy decision
control closed at `438b8e82c2fb66181289a0a5a60897993effe62f` without deciding GP0-D03
or GP0-D08.

Control C adds a typed local journey model and a presentation component entirely
under `lib/production/`. The model maps exactly six approved capabilities in
order: sleep/health preparation, mood check-in, character selection, daily
advice, optional text chat, and history. Imports remain inside the production
directory except for Flutter itself.

The shell adds no route, interactive control, network client, permission or
platform access. It does not select or contact a health provider. The health
step remains decision-pending, the production Backend remains unwired, and the
release target remains unwired. The static cards provide ordered semantics,
scrolling, flexible height, narrow-width support, and enlarged-text support.

Control C does not complete core-flow migration, broader production separation,
Backend allowlisting, artifact exclusion proof, release wiring, GP-2, or GP-3.
Any expansion beyond this local shell requires a later bounded authorization.

## Control D: non-product entrypoint separation

Control D moves the existing mixed default composition into `lib/main_non_product.dart` byte-for-byte from the baseline `main.dart` blob and replaces `lib/main.dart` with a minimal compatibility shim. The shim exists for default development startup and existing test imports only; it is not a Google Play release target.

Production ownership remains with `lib/main_production.dart` and `lib/production/`. The production route allowlist remains `ProductionHomeScreen` only, with empty named routes and null route generators. The production graph must not reference `main.dart`, `main_non_product.dart`, `main_rt2ec_operator.dart`, `DailyRhythmCompanionApp`, `HomeScreen`, developer/operator/demo/diagnostic source, or mixed Backend/service/operator/widget code.

The RT2EC operator entrypoint remains an independent non-product operator target. This control does not wire Android release targets, prove artifact exclusion, complete the non-product Backend boundary, select a production Backend, or complete GP-2.

Protected product boundaries remain unchanged for `main_production.dart`, `lib/production/`, production journey tests, Backend source, Android configuration, `pubspec.yaml`, services, operators, widgets, HistoryScreen, HomeScreen, production journey behavior, and v4.0.0 release objects.
## Control E: non-product Backend boundary

Control E adds a typed, deny-by-default access decision around the existing
symbolic `ProductionBackendOperation` set. Only the exact 11 core candidates
resolve to `allowCoreCandidate`. The three health-pending operations resolve to
`denyHealthPendingDecision`; unknown objects and non-product method or route
names resolve to `denyUnknown`.

Non-product operations are not represented in the production enum. The
production graph does not reach `BackendApiClient`, legacy services, transport
clients, endpoints, routes, URLs, platform APIs, or permissions. This control
does not add Backend wiring or make an allow decision equivalent to network or
release authorization. Any future production adapter must pass its symbolic
operation through this access decision before communication.

Artifact exclusion proof, core-flow migration, production environment and
release wiring remain later controls. GP0-D03 and GP0-D08 remain
`NOT_DECIDED`; health operations remain inactive and the production Backend
remains unwired.

## Control F: strict product artifact exclusion contract

The accepted production import and route boundary is source-level proof. It
shows that `main_production.dart` and `lib/production/` do not reach the mixed,
developer, operator, demo, diagnostic, or legacy Backend graph. It does not
prove what a compiled Android APK or AAB contains.

GP2-S03 approves `STRICT_PRODUCT_ONLY_ANDROID_ARTIFACT`. A qualifying public
candidate must exclude unapproved non-product Dart code, permissions, native
plugins, assets, localhost/private-LAN configuration, and developer/operator
identifiers. The current app cannot yet demonstrate that result: the default
target is the non-product compatibility shim; the shared manifest declares
`RECORD_AUDIO`; the shared pubspec declares native-plugin candidates and
demo/background/placeholder assets; Android identity and signing are unfinished;
and no compiled artifact evidence exists. Control F recorded the recommendation
for a separate public Flutter application. Its approval is recorded below.

## Control G: public Flutter application boundary

GP2-S04 is `APPROVED` with value
`SEPARATE_PUBLIC_FLUTTER_APPLICATION_BOUNDARY`. The user approved Option A on
2026-11-14. Baseline is `5ae9a8370330f1970238feb3b4c93aad59a29b4e`.
Documentation scope is five existing files. Implementation and builds require
separate authorization.

### Directory and dependency ownership

| Path | Ownership and dependency rules |
| --- | --- |
| `app_public/` | Public Flutter application. Owns its pubspec, lockfile, approved assets, Android resources, manifest overlays, Gradle configuration, version metadata, and public startup. Runtime dependencies start with Flutter and the local `drc_production` package. |
| `packages/drc_production/` | Single source for `ProductionApp`, the journey UI and models, deterministic advice, and symbolic capability/Backend-operation policy. Runtime dependencies are limited to Flutter and package-internal code for this migration. Public startup imports `package:drc_production/production_app.dart`. |
| `app/` | Owns developer/demo/operator composition, tooling dependencies, demo assets, and existing default/operator entrypoints. `app/lib/main_production.dart` is a local preview of the shared package after extraction. |

Both apps depend on `drc_production` through explicit local path dependencies.
The public app and shared package have no direct or transitive dependency on
`app/`, its generated files, its assets, or its Backend/Framework runtime.
Product startup is `app_public/lib/main.dart` and starts only `ProductionApp`.
Run public builds from `app_public/` with explicit target `lib/main.dart`.
Permissions and assets come from that application's build inputs and their
resolved dependencies. Demo assets and microphone permission remain outside
those inputs.

The shared code preserves the three-choice Mood check-in, three Character
choices, nine deterministic advice messages, and fresh-journey Mood reset.
The active beta stays local-only under D03 and the approved ephemeral Mood
policy GP2-S02.

### Android ownership and phase handoff

GP-2 owns the structural split, the product-only Android manifest and
dependency inputs, the public target, and exclusion evidence on a private
release-mode proof APK. The later proof build control specifies its temporary
identity and signing inputs. Keep proof output out of distribution.

GP-4 applies the permanent application ID and namespace, the approved
`Daily Rhythm Companion` display name, version/build metadata, and release
signing configuration in the public app. Signing material remains outside
source control. GP-4 wires the exact public release build command and repeats
the exclusion inspection on the final signed candidate, recording its filename,
byte size, APK SHA-256, and signing certificate SHA-256.

### Migration and rollback

1. Extract `app/lib/production/` into `packages/drc_production/` and update
   the preview to import the package. Move or adapt the production regression
   suites and source guards as one reviewable change so each guard still
   inspects the files it constrains. Preserve the existing non-product
   entrypoint checks and development widget tests under `app/`.
2. Add the Android public app with a minimal pubspec, explicit production
   startup, product-owned Android inputs, and approved assets only. Check the
   resolved dependency graph and any generated registrant for excluded packages.
3. Under separate build authorization, produce and inspect the private proof
   APK using the strict artifact contract. Review the proof before GP-4 uses
   the new boundary for the final signed candidate.

Before release wiring, roll back by removing the public app and its
dependencies, then reverting the package extraction, preview changes, and
test relocations together. If GP-4 has wired a candidate, withdraw that
candidate from publication first. Preserve published package identity and
signing continuity once a public APK exists. The v4.0.0 release remains outside
this rollback.

### Verification strategy

- At each migration step, analyze the affected Flutter roots and run their
  focused tests. Rerun the preview, developer/compatibility, and operator
  boundary checks under `app/`.
- Preserve production behavior assertions for journey, Mood, Character, local
  advice, composition, and core scope, including the exact advice matrix,
  fresh-instance reset, and deny-by-default Backend operations.
- Assert that the public target boots the single product composition, the
  shared package stays inside its import boundary, and the resolved public
  dependency graph excludes the existing `app/` and its development plugins.
- Inspect the proof artifact's merged and packaged manifest, plugin registrant
  and shipped native inventory, Flutter asset manifest and APK entries, AOT
  report, and packaged endpoint/configuration inventory. Record SDK/build
  inputs, target, ABI, filename, byte size, and SHA-256. GP-4 records equivalent
  evidence for the final signed APK. Follow the
  [strict artifact exclusion contract](v410_gp2_strict_product_artifact_exclusion_contract.md).

BLOCKER-G is resolved at the decision level. BLOCKER-A through BLOCKER-F remain
open. Artifact proof is `NOT_EXECUTED / BLOCKED` and GP-2 remains incomplete.
