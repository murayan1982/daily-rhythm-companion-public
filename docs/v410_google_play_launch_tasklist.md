# Daily Rhythm Companion v4.1.0 Distribution Tasklist

Updated: 2026-11-20

```text
Active track: GitHub Android Public Beta
Deferred track: Google Play / NOT_CANCELLED
Current task: GP-4 clean-install and manual-update evidence
Baseline: e873444f76948c0239e38f807933f8baa03ec524
Surface: exact M2 A0 D0
State: GP4_SIGNED_CANDIDATE_INSPECTED / DEVICE_CLEAN_INSTALL_PASSED / MANUAL_UPDATE_PASSED / SIGNING_CONTINUITY_VERIFIED / GP5_PENDING / GP6_PENDING
Stage / commit / push: authorized for this two-document update to origin/main
```

Each unchecked line is an individual gate and requires separate authorization.

## Completed history and README checklist

- [x] Planning R1 closed at `d7e39ad37667c6f3f104c2097f5ca54f9089df5c`.
- [x] GP-1 accepted inventory remains recorded.
- [x] GP-2 accepted production entrypoint and text-core boundaries remain recorded.
- [x] D03 approves the active GitHub beta local-only/no-remote-Backend mode; D08 is approved for the active GitHub Android Public Beta.
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
- [x] D08 is approved for the active GitHub Android Public Beta
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
- [x] Active-Beta GP-3 implementation and Flutter-widget evidence set is complete; no local GP-3 implementation item remains
- [x] Current GitHub Android Public Beta GP-3 scope accepted after final review found no blocking findings
- [ ] GP-5 formal Privacy Policy and support/contact completion under an approved D08 decision
- [ ] GP-6 Android-device verification for background resume, process restart, airplane mode, and TalkBack

## P0 — release foundation and blocking decisions

- [x] Formal application ID
- [x] Formal application display name applied to Android
- [x] Release signing configuration and signed-candidate verification
- [x] Signing key owner/custody/backup/recovery evidence (user-reported 2026-11-15; no secret recorded)
- [x] Release build wiring from `app_public/` with explicit target `lib/main.dart`
- [x] versionName/versionCode
- [x] v4.1.0 GitHub beta Backend mode: local-only / no remote Backend
- [x] localhost/private-LAN release dependency exclusion proof for the inspected signed ARM64 candidate
- [x] D03 active-track decision closure
- [x] D08 decision approved for the active GitHub Android Public Beta
- [x] Privacy Policy and support contact published in [PRIVACY.md](../PRIVACY.md)
- [ ] Public data deletion method
- [x] Signed ARM64 candidate APK created and kept private
- [x] APK SHA-256 recorded for the inspected candidate
- [x] Signing certificate SHA-256 verified
- [x] Repeat GP2-S03 exclusion proof on the inspected signed APK and record the exact APK SHA-256
- [x] Clean install, first launch, and advice display on A301OP (API 34, arm64-v8a) with the inspected versionCode=6 candidate
- [x] GP-4 manual update via `adb install -r` on A301OP (API 34, arm64-v8a), including device version checks, launch, and advice display
- [x] GP-4 signing continuity verified for the `versionCode=5` to `versionCode=6` update
- [ ] Android developer verification
- [ ] Package registration
- [ ] GitHub publication authorization

## P1 — general-user journey, safety, and quality

- [x] Active-Beta first-run guidance is provided in-screen; no separate onboarding route is required
- [x] Microphone permission pre-explanation is not applicable: the active Beta requests no microphone permission
- [x] Health-data permission pre-explanation is not applicable: the active Beta requests no health-data permission
- [x] Separate Settings screen is not part of the active Beta; About provides the approved on-device/no-save explanation
- [ ] GP-5 formal Privacy Policy and support/contact path
- [ ] GP-6 physical-device TalkBack verification
- [x] Flutter widget verification at 2.0 text scaling
- [ ] GP-6 physical-device color-contrast verification
- [x] Flutter widget verification at narrow viewport; representative physical-device sizes remain GP-6
- [x] Loading state is not applicable: the active Beta performs no asynchronous load
- [x] Selection-waiting guidance covers the active local journey; no data-backed empty state exists
- [x] Backend/error state is not applicable: deterministic local advice has no Backend or fallible remote operation
- [x] Offline behavior has no product network dependency; airplane-mode verification remains GP-6 and is not claimed complete
- [x] Permission denial/revocation is not applicable: the active Beta requests no runtime permission
- [x] Backend/network failure is not applicable: the active Beta makes no Backend connection
- [x] Flutter widget lifecycle pause/resume and fresh-instance reset verification; physical-device recovery and process restart remain GP-6
- [x] Developer/operator UI exclusion remains covered by the accepted product-boundary suite

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
distribution signing, and repetition against the signed ARM64 candidate were
completed later under GP-4 and are recorded below. The active Beta three-step
Core-flow and mood-specific,
Character-invariant Mood responses were accepted at
`3ac56a19197179e7370da173a56382c0fb7b9747` after final review found no
blocking findings. The current GitHub Android Public Beta GP-2 scope is complete.
Sleep/health connection, optional text chat, history, and the broader
`TEXT_CORE_PLUS_CHAT` range remain future work. The active-Beta GP-3 evidence set
is complete, final review found no blocking findings, and the current GitHub
Android Public Beta GP-3 scope is accepted. GP-5 privacy/support and GP-6
physical-device gates remain open. GP-4 must repeat exclusion proof on the APK
selected for publication if it does not match the inspected candidate hash.

GP-4 candidate execution occurred on 2026-11-15; this documentation update is
dated 2026-11-20. The private candidate is
`DRC_v4.1.0_arm64_signed_candidate.apk`, source
`ffa7745a02cc289f44b8a3db960a1389e33cd1b6`, 15,081,786 bytes, APK SHA-256
`A50D6987B8E059A49FFF1FB340A7081293617DE9EE784E3304547BA17FDCE373`,
and certificate SHA-256
`27:1F:75:FE:3B:19:8B:AC:A9:4F:31:AE:2B:65:8C:7B:FC:99:88:1A:2C:C3:5C:68:FE:89:38:0B:FE:CF:8C:E5`.
It verifies as the signed ARM64 release candidate for
`io.github.murayan1982.dailyrhythmcompanion`, label
`Daily Rhythm Companion`, version `4.1.0` / `6`, and SDK `24` / `36` / `36`.
Manifest, plugin, DEX/native, asset, AOT, and product connection-setting
exclusion checks passed for this exact APK. The user reported signing-key
generation, encrypted-backup restoration with the same certificate SHA-256,
and matching release `signingReport` on 2026-11-15. The user reported that
clean installation, first launch, and advice display passed on an A301OP
(API 34, arm64-v8a) with the exact versionCode=6 APK identified above.

The user reported that `adb install -r` succeeded on the A301OP (API 34,
arm64-v8a), updating from the verification-only APK (`versionCode=5`) to the
saved candidate (`versionCode=6`) identified by the APK SHA-256 above. Both
APKs had the application ID and signing-certificate SHA-256 recorded above.
The installed `versionCode` was confirmed on the device before (5) and after
(6) the update. Launch and advice display passed after the update. GP-4
manual update and signing-continuity verification are complete.

Android package registration, representative-device compatibility verification,
D08/GP-5, and publication remain incomplete.
Publication must use an APK matching the recorded APK SHA-256 or repeat the
complete candidate inspection.
