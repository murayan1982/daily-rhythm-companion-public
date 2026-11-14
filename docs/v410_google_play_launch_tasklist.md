# Daily Rhythm Companion v4.1.0 Distribution Tasklist

Updated: 2026-11-14

```text
Active track: GitHub Android Public Beta
Deferred track: Google Play / NOT_CANCELLED
Current task: DRC_V410_GP2_PRODUCT_DEPENDENCY_BOUNDARY_ARCHITECTURE_DECISION_R1
Baseline: 5ae9a8370330f1970238feb3b4c93aad59a29b4e
Surface: exact M5 A0 D0
State: ARCHITECTURE_APPROVED / DOCUMENTED / ARTIFACT_PROOF_BLOCKED / READY_FOR_REVIEW
Stage / commit / push: NOT_AUTHORIZED
```

Each unchecked line is an individual gate and requires separate authorization.

## Completed history and README checklist

- [x] Planning R1 closed at `d7e39ad37667c6f3f104c2097f5ca54f9089df5c`.
- [x] GP-1 accepted inventory remains recorded.
- [x] GP-2 accepted production entrypoint and text-core boundaries remain recorded.
- [x] D03 approves the active GitHub beta local-only/no-remote-Backend mode; D08 remains `NOT_DECIDED`.
- [x] GP0-D11 approves GitHub Android Public Beta first and Google Play later.
- [x] README is the general-user landing page.
- [x] README says `DEVELOPMENT / NOT_YET_RELEASED`.
- [x] README says installable public APK `NOT_AVAILABLE`.
- [x] README says Google Play `DEFERRED / NOT_CANCELLED`.
- [x] README preserves AI Character Framework attribution.
- [x] README legacy body, 28 markers, user marker pair, and details pair remain preserved.

## GP-2 Core-flow migration

- [x] GP-2 local three-choice mood check-in migration
- [x] Production-only typed mood model
- [x] Accessible mutually-exclusive mood selection
- [x] Initial Mood Check-in slice introduced no Backend/persistence/advice wiring
- [x] GP-2 local three-character selection migration
- [x] Production-only typed character model
- [x] Accessible mutually-exclusive character selection
- [x] Existing stable character IDs and selection copy preserved
- [x] Initial Character Selection slice introduced no Backend/persistence/advice/FW routing
- [x] GP-2 local deterministic advice migration
- [x] Exact 3 moods × 3 characters advice matrix
- [x] Local mood-and-character-to-advice wiring
- [x] No remote Backend / persistence / AI / Framework routing
- [x] Mood / Character copy matches immediate local-advice reflection
- [x] Selection persistence remains unavailable and is stated separately
- [x] Mood persistence decision: not included in the v4.1.0 GitHub beta; Mood selection remains ephemeral
- [x] Fresh `ProductionJourneyOverview` instance resets Mood to unselected
- [x] Product source unchanged and no persistence dependency added
- [x] D08 remains `NOT_DECIDED`
- [ ] Character-aware mood copy decision
- [ ] Remaining Core-flow migration
- [x] Strict product-only artifact exclusion policy selected
- [x] Source-level production graph boundary preserved
- [x] Current Android/pubspec/asset blockers inventoried
- [x] Artifact exclusion acceptance contract defined
- [x] Product dependency-boundary architecture decision (GP2-S04, Option A; BLOCKER-G resolved at the decision level)
- [ ] Extract `packages/drc_production/` and verify behavior and source boundaries with the existing preview and regression suites
- [ ] Add `app_public/` and verify the product-only dependency, entrypoint, Android manifest, and asset inputs
- [ ] Product-only Android artifact build
- [ ] Merged manifest exclusion proof
- [ ] Plugin registrant/artifact inventory proof
- [ ] Asset manifest exclusion proof
- [ ] AOT analyze-size exclusion proof
- [ ] GP-2 artifact exclusion proof
- [ ] GP-3 user-journey refinement

## P0 — release foundation and blocking decisions

- [ ] Formal application ID
- [ ] Formal application display name applied to Android
- [ ] Release signing
- [ ] Signing key owner/custody/backup/recovery
- [ ] Release build wiring from `app_public/` with explicit target `lib/main.dart`
- [ ] versionName/versionCode
- [x] v4.1.0 GitHub beta Backend mode: local-only / no remote Backend
- [ ] localhost/private-LAN release dependency exclusion proof
- [x] D03 active-track decision closure
- [ ] D08 decision closure
- [ ] Privacy Policy
- [ ] Public data deletion method
- [ ] Signed release APK
- [ ] APK SHA-256
- [ ] Signing certificate SHA-256
- [ ] Repeat GP2-S03 exclusion proof on the final signed APK and record the exact APK SHA-256
- [ ] Clean install
- [ ] Manual update
- [ ] Android developer verification
- [ ] Package registration
- [ ] GitHub publication authorization

## P1 — general-user journey, safety, and quality

- [ ] First-run onboarding
- [ ] Microphone permission pre-explanation
- [ ] Health-data permission pre-explanation
- [ ] Settings screen
- [ ] Support/contact
- [ ] TalkBack
- [ ] Text enlargement
- [ ] Color contrast
- [ ] Device-size support
- [ ] Loading state
- [ ] Empty state
- [ ] Error state
- [ ] Offline state
- [ ] Permission denial/revocation
- [ ] Backend/network failure
- [ ] Lifecycle recovery
- [ ] Developer/operator UI exclusion

## P2 / GP-7 — publication materials and preparation

- [ ] README download journey
- [ ] APK install guide
- [ ] Unknown-app explanation
- [ ] Screenshots
- [ ] Release notes
- [ ] Known limitations
- [ ] APK filename/size/SHA-256
- [ ] Signing certificate information
- [ ] Update guide
- [ ] Uninstall guide
- [ ] Deletion guide

## GP-8 — GitHub Android Public Beta testing

- [ ] Physical-device beta matrix
- [ ] Download-to-install journey
- [ ] Clean-install beta test
- [ ] Manual-update beta test
- [ ] Signing continuity
- [ ] Permission-denial beta test
- [ ] Offline/error beta test
- [ ] TalkBack/accessibility beta test
- [ ] Feedback collection
- [ ] Crash/regression review
- [ ] Release-blocker closure
- [ ] GP-9 candidate freeze

GP-8 does not create or publish a tag, GitHub Release, or asset.

## GP-9 — GitHub Release publication

- [ ] Approved tag
- [ ] GitHub Release
- [ ] Signed APK upload
- [ ] Checksum publication
- [ ] Public asset re-download verification
- [ ] Public download smoke check
- [ ] Public clean-install smoke check
- [ ] Public update smoke check
- [ ] Monitoring
- [ ] Release closeout

## Deferred Google Play Track — NOT_CANCELLED

- [ ] Play developer account/testing applicability
- [ ] Play App Signing
- [ ] Signed AAB
- [ ] Play target API at reactivation
- [ ] Data safety declaration
- [ ] Health Apps declaration
- [ ] Google Play icon
- [ ] Feature graphic
- [ ] Play short/full descriptions
- [ ] Play screenshots
- [ ] Internal testing
- [ ] Closed testing
- [ ] Applicable 12 testers / 14 days
- [ ] Production application
- [ ] Play publication smoke check

All Play items remain `DEFERRED / NOT_CANCELLED`. GitHub beta completion does
not check any Play item.

## Product dependency-boundary decision R1

GP2-S04 records `SEPARATE_PUBLIC_FLUTTER_APPLICATION_BOUNDARY`. BLOCKER-A
through BLOCKER-F remain open. Artifact proof is `NOT_EXECUTED / BLOCKED`;
GP-2 and GP-3 are incomplete. See the
[migration and verification sequence](v410_gp2_production_boundary_architecture.md#control-g-public-flutter-application-boundary)
for the next separately authorized implementation slice.
