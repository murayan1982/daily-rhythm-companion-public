# Daily Rhythm Companion v4.1.0 Distribution Tasklist

Updated: 2026-11-13

```text
Active track: GitHub Android Public Beta
Deferred track: Google Play / NOT_CANCELLED
Current task: DRC_V410_GITHUB_ANDROID_PUBLIC_BETA_REPLAN_CORRECTIVE_R2
Baseline: 0514d9780f9853e15cd8a109af5d1e09f36b4d89
Surface: exact M4 A1 D0
State: CORRECTIVE_IMPLEMENTED / STATIC_VERIFIED / READY_FOR_RE_REVIEW
Stage / commit / push: NOT_AUTHORIZED
```

Each unchecked line is an individual gate and requires separate authorization.

## Completed history and README checklist

- [x] Planning R1 closed at `d7e39ad37667c6f3f104c2097f5ca54f9089df5c`.
- [x] GP-1 accepted inventory remains recorded.
- [x] GP-2 accepted production entrypoint and text-core boundaries remain recorded.
- [x] Backend/privacy evidence control preserves D03/D08 as `NOT_DECIDED`.
- [x] GP0-D11 approves GitHub Android Public Beta first and Google Play later.
- [x] README is the general-user landing page.
- [x] README says `DEVELOPMENT / NOT_YET_RELEASED`.
- [x] README says installable public APK `NOT_AVAILABLE`.
- [x] README says Google Play `DEFERRED / NOT_CANCELLED`.
- [x] README preserves AI Character Framework attribution.
- [x] README legacy body, 28 markers, user marker pair, and details pair remain preserved.

## P0 — release foundation and blocking decisions

- [ ] Formal application ID
- [ ] Formal application display name applied to Android
- [ ] Release signing
- [ ] Signing key owner/custody/backup/recovery
- [ ] `main_production.dart` release wiring
- [ ] versionName/versionCode
- [ ] Production Backend mode
- [ ] Localhost/private-LAN dependency removal
- [ ] D03 decision closure
- [ ] D08 decision closure
- [ ] Privacy Policy
- [ ] Public data deletion method
- [ ] Signed release APK
- [ ] APK SHA-256
- [ ] Signing certificate SHA-256
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

## Corrective R2 verification

- [x] GP-0 through GP-9 identifier contract restored.
- [x] GP-8 is pre-publication Public Beta testing.
- [x] GP-9 is GitHub Release publication and post-release verification.
- [x] Google Play is outside GP numbering in a separate deferred section.
- [x] README accepted candidate remains unchanged.
- [x] Product, Backend, Android, and pubspec source remain unchanged.
- [x] Stage, commit, push, build, test, signing, tag, Release, asset, and Console operations remain unauthorized.

## Corrective R2 stop point

Stop after static verification and a new handoff. No unchecked item is
authorized by this documentation corrective.
