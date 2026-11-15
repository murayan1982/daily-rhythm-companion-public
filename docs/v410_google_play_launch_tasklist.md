# Daily Rhythm Companion v4.1.0 Distribution Tasklist

Updated: 2026-11-15

```text
Active track: GitHub Android Public Beta
Deferred track: Google Play / NOT_CANCELLED
Current task: DRC_V410_GP3_LOCAL_JOURNEY_RESUME_RESET_R1
Baseline: 77c9888d61599e01b5c4fa5e4b692f0fd342e735
Surface: exact M2 A0 D0
State: IMPLEMENTED / STATIC_VERIFIED / GP3_IN_PROGRESS / READY_FOR_REVIEW
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
- [x] Active Public Beta Mood acknowledgement decision: mood-specific copy, invariant across Character choices
- [x] Active Public Beta three-step Core-flow: Mood → Character → local advice
- [x] Mood and Character accepted in either order; advice appears and updates after both selections
- [x] Sleep, optional text chat, and history cards excluded from the active Public Beta main screen
- [x] Shared package analyze PASS and all 29 shared tests PASS
- [x] `app_public/` analyze PASS and startup test PASS
- [x] App product-boundary suite: 31 tests PASS
- [x] Review and accept the active Beta GP-2 three-step implementation (`3ac56a19197179e7370da173a56382c0fb7b9747`; no blocking findings)
- [ ] Long-term `TEXT_CORE_PLUS_CHAT` capability completion beyond the active Beta screen
- [x] Strict product-only artifact exclusion policy selected
- [x] Source-level production graph boundary preserved
- [x] Current Android/pubspec/asset blockers inventoried
- [x] Artifact exclusion acceptance contract defined
- [x] Product dependency-boundary architecture decision (GP2-S04, Option A; BLOCKER-G resolved at the decision level)
- [x] Extract `packages/drc_production/` and verify behavior and source boundaries with the existing preview and regression suites (`2e0c038e9737ec711aeb6173f524f4390c122432`)
- [x] Add `app_public/` and verify the product-only dependency, entrypoint, Android manifest, and asset inputs (`ed2454da9277b425e62a72c8b29357ad0780b49b`)
- [x] Product-only Android ARM64 release-mode proof artifact build (unsigned and undistributed)
- [x] Merged and packaged manifest exclusion proof for the proof APK
- [x] Plugin registrant, DEX, and native-library inventory proof for the proof APK
- [x] Flutter asset manifest and APK entry exclusion proof for the proof APK
- [x] AOT analyze-size exclusion proof for the proof APK
- [x] GP-2 private proof-artifact exclusion evidence captured
- [x] GP-3 initial guidance consolidates local-processing and no-save notices above the three-step flow
- [x] Advice guidance identifies both missing selections or the single remaining selection without "準備中"
- [x] Ready advice Semantics includes selected Mood, selected Character, and advice body
- [x] Widget Semantics verification for the refined three-step states (shared package analyze PASS and 30 tests PASS; public app analyze PASS and startup test PASS; product-boundary 31 tests PASS)
- [x] In-app About guidance states that advice is produced on-device from Mood and Character and that selections are not saved
- [x] About entry exposes its name to Semantics and returns to the same journey instance without losing current selections or advice
- [x] About route widget verification for navigation, state retention, narrow width, and 2.0 text scaling (shared package analyze PASS and 33 tests PASS; public app analyze PASS and startup test PASS; product-boundary 31 tests PASS)
- [x] Flutter widget lifecycle verification for same-instance pause/resume retention and fresh-instance reset (shared package analyze PASS and 34 tests PASS; public app startup test PASS; product-boundary 31 tests PASS)
- [x] Lifecycle widget-test scope is local UI state only; the active Beta has no permission request or Backend connection exercised by this check
- [ ] GP-6 Android-device verification for background resume, process restart, airplane mode, and TalkBack
- [ ] Android device TalkBack verification
- [ ] Settings, support, and remaining GP-3 user-journey refinement

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

GP2-S04 records `SEPARATE_PUBLIC_FLUTTER_APPLICATION_BOUNDARY`. The shared
package extraction is complete at `2e0c038e9737ec711aeb6173f524f4390c122432`,
and `app_public/` is complete at
`ed2454da9277b425e62a72c8b29357ad0780b49b`. An unsigned, undistributed ARM64
release-mode proof APK was built from that exact source as `app-release.apk`:
15,073,506 bytes, SHA-256
`672DCCD462ACAD49ECD891482353B1EF0212E33512D9868A1E9C383AF60F4BAC`.
Manifest, plugin/DEX/native-library, Flutter asset, and AOT exclusion evidence
was captured for this proof APK. Formal identity, display name, version,
distribution signing, and repetition against the exact final signed APK remain
GP-4 gates. The active Beta three-step Core-flow and mood-specific,
Character-invariant Mood responses were accepted at
`3ac56a19197179e7370da173a56382c0fb7b9747` after final review found no
blocking findings. The current GitHub Android Public Beta GP-2 scope is complete.
Sleep/health connection, optional text chat, history, and the broader
`TEXT_CORE_PLUS_CHAT` range remain future work. GP-3 refinement remains open,
and GP-4 must repeat exclusion proof on the exact final signed APK.
