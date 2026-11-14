# DRC v4.1.0 GP-2 Strict Product Artifact Exclusion Contract

## Control metadata

```text
Task: DRC_V410_GP2_PRODUCT_DEPENDENCY_BOUNDARY_ARCHITECTURE_DECISION_R1
Baseline HEAD / origin/main / remote main: 5ae9a8370330f1970238feb3b4c93aad59a29b4e
Phase: GP-2
Surface: exact M5 A0 D0
State: ARCHITECTURE_APPROVED / DOCUMENTED / ARTIFACT_PROOF_BLOCKED / READY_FOR_REVIEW
Documentation implementation: APPROVED
Product / Android / pubspec implementation: NOT_AUTHORIZED
Build / stage / commit / push: NOT_AUTHORIZED
Artifact proof: NOT_EXECUTED / BLOCKED
```

## Approved strict policy

The strict exclusion contract was introduced at
`5ae9a8370330f1970238feb3b4c93aad59a29b4e`. This update records the approved
dependency-boundary architecture.

GP2-S03 is `APPROVED` with value
`STRICT_PRODUCT_ONLY_ANDROID_ARTIFACT`. Approval evidence is the user's
2026-11-14 selection of the strict product-only recommendation.

The GitHub Android Public Beta and later final public candidates must exclude
developer/operator/demo/diagnostic Dart graphs, non-product entrypoints, legacy
mixed `HomeScreen` and `HistoryScreen`, non-product Backend/service/operator/
widget code, unused microphone permission, unused audio/recording/operator
native plugins, unapproved demo/diagnostic assets, localhost/private-LAN
dependencies, and developer/operator configuration and identifiers. Excluding
only non-product UI is insufficient.

## Source-level evidence already accepted

- `lib/main_production.dart` starts only `ProductionApp`.
- `lib/production/` imports Flutter and relative production files only.
- The production composition boundary test rejects non-product route/import
  reachability.
- The production core-scope boundary test preserves the typed production
  capability and Backend-operation boundary.
- `lib/main.dart` is a non-product compatibility shim,
  `lib/main_non_product.dart` is the mixed development composition, and
  `lib/main_rt2ec_operator.dart` is an operator entrypoint.
- The default Flutter target is therefore not yet the production release
  target.

This evidence establishes a source graph boundary. It is not compiled Android
artifact proof.

## Current artifact inputs

### Android manifest and Gradle

- The shared main manifest declares `android.permission.RECORD_AUDIO`.
- The application label is `app`; no product-only permission manifest exists.
- The namespace and application ID are `com.example.app`.
- The release build type uses debug signing.
- No production flavor or production release source set is implemented.

### Declared dependencies

| Dependency | Static classification | Artifact claim |
| --- | --- | --- |
| `audioplayers` | Android native-plugin candidate | Exclusion not proved |
| `http` | Pure Dart HTTP library | Reachability/exclusion not proved at artifact level |
| `permission_handler` | Android native-plugin candidate | Exclusion not proved |
| `path_provider` | Android native-plugin candidate | Exclusion not proved |
| `record` | Android native-plugin candidate | Exclusion not proved |
| `url_launcher` | Android native-plugin candidate | Exclusion not proved |
| `cupertino_icons` | Dart/Flutter asset package; no Android plugin registration expected | Inclusion/exclusion not inspected |

The compiled inventory must verify the absence of excluded declared
dependencies and native plugins.

### Declared assets

The shared pubspec bundles three character `*_demo.png` files, two background
images, and a placeholder image. Their product approval and actual production
usage are not confirmed, and their absence from a product artifact is not
proved.

## Blocker inventory A-G

- **BLOCKER-A:** The only existing Flutter app root is `app/`, whose default
  target `lib/main.dart` delegates to the non-product composition. The approved
  public app and its target have yet to be implemented.
- **BLOCKER-B:** `RECORD_AUDIO` exists in the shared main manifest.
- **BLOCKER-C:** Native-plugin candidates are declared in the shared pubspec.
- **BLOCKER-D:** Demo/legacy assets are bundle inputs in the shared pubspec.
- **BLOCKER-E:** Formal application ID, display name application, and release
  signing are unfinished GP-4 publication blockers.
- **BLOCKER-F:** No compiled APK/AAB or analyze-size evidence has been created.
- **BLOCKER-G:** Resolved at the decision level. GP2-S04 approves Option A.
  The approved design awaits implementation.

BLOCKER-A through BLOCKER-D directly prevent artifact-exclusion proof.

## Strict acceptance criteria

A later artifact proof must:

1. Generate a release-mode Android artifact from `app_public/` with explicit
   production target `lib/main.dart`.
2. Prove the artifact's unique production execution entrypoint.
3. Show no non-product Dart library in AOT size analysis.
4. Show developer/operator/demo/diagnostic routes, symbols, and copy are
   unreachable.
5. Show no unused microphone permission in the merged manifest.
6. Show no unused native plugin in the generated registrant or artifact
   inventory.
7. Show no unapproved demo/diagnostic asset in the Flutter asset manifest.
8. Show no localhost/private-LAN endpoint or configuration.
9. Confirm application ID, label, version, and signing evidence under GP-4.
10. Preserve the APK manifest, plugin inventory, asset inventory, and
    analyze-size report.
11. Record artifact filename, byte size, and SHA-256.
12. Clearly distinguish a proof artifact from a public APK.
13. Repeat the proof on the exact final signed candidate. Record which APK
    and shipped ABIs the AOT evidence covers. If a separate analysis build
    is used, record the relationship between its AOT output and the output
    shipped in the candidate.

## Evidence commands planned for a later build

Subject to separate authorization, later evidence may use a Flutter release
build with the approved production target and `--analyze-size`, merged and
packaged Android manifest inspection, generated plugin registrant inspection,
Flutter asset manifest inspection, APK inventory, and SHA-256 calculation.

No such command was run by this control, and no artifact result is recorded as
passing.

## Architecture alternatives

### A. Separate public Flutter application boundary

Use a product-only pubspec and Android manifest/configuration in `app_public/`,
sharing the production UI through `packages/drc_production/`. The user approved
this option as GP2-S04 on 2026-11-14.

### B. Move non-product tooling out of the current app

Restructure the current app as the public product and migrate legacy/operator
tooling to another app. This is `ALTERNATIVE / NOT_APPROVED` and has a larger
migration surface.

### C. Android flavor only

A flavor can separate a Dart target and Android manifest and scope Flutter
assets by flavor. The shared pubspec still needs an independent plugin
dependency and registration boundary. This is
`INSUFFICIENT_AS_STANDALONE_SOLUTION`.

## Approved architecture

GP2-S04 approves `SEPARATE_PUBLIC_FLUTTER_APPLICATION_BOUNDARY`. See
[Control G](v410_gp2_production_boundary_architecture.md#control-g-public-flutter-application-boundary)
for directory and dependency ownership, migration, rollback, and GP-2/GP-4
verification responsibilities.

## Remaining work

- Implement the approved boundary under a separate GP-2 implementation control.
- Complete the still-open GP-2 migration and exclusion gates.
- Complete GP-4 application identity, label, signing, and release-target wiring.
- Authorize and execute compiled artifact evidence on a proof candidate and
  again on the final public candidate.
- Keep D03 approved only for the active local-only beta, D08 `NOT_DECIDED`, and
  D11 `APPROVED` unless separately changed by the user.

## Stop boundary

This decision control ends at review of the five-document diff. Product,
Backend, Android, pubspec, README, and test changes, builds, Git writes, and
release operations are outside this control.
