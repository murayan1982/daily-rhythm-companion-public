# DRC v4.1.0 GitHub Android Public Beta Replan

## 1. Control metadata

```text
Task: DRC_V410_GITHUB_ANDROID_PUBLIC_BETA_REPLAN_CORRECTIVE_R2
Baseline: 0514d9780f9853e15cd8a109af5d1e09f36b4d89
Development line: DRC v4.1.0
Distribution sequence: GitHub Android Public Beta first / Google Play later
Implementation: APPROVED_FOR_DOCUMENTATION_CORRECTIVE_ONLY
Stage / commit / push: NOT_AUTHORIZED
Surface: exact M4 A1 D0
```

## 2. Decision and scope

GP0-D11 approves GitHub Releases as the first planned Android Public Beta
channel and README as the primary general-user landing page. Google Play is
`DEFERRED / NOT_CANCELLED`. This control changes documentation only. It does
not authorize source changes, build, signing, tag, Release, asset, Console,
stage, commit, or push operations.

## 3. Current public state

- Android Public Beta: `DEVELOPMENT / NOT_YET_RELEASED`.
- Installable public APK: `NOT_AVAILABLE`.
- Production Backend: `UNWIRED`.
- Health provider/behavior: `PENDING_DECISION`.
- GP0-D03 and GP0-D08: `NOT_DECIDED`.
- Public Privacy Policy and support URLs: `NOT_AVAILABLE`.
- v4.0.0 Release: immutable history, not an Android APK release.

No URL, signing identity, contact, policy, or artifact tuple is invented.

## Why GitHub Public Beta first

- The public repository and user-first README can provide one transparent
  landing point for general Android users.
- Direct-distribution testing can produce install, update, accessibility,
  support, and feedback evidence before a Play submission.
- This sequence does not cancel Google Play.
- Direct distribution cannot omit signing, privacy, security, support, or
  developer-verification responsibilities.
- GitHub distribution is not evidence that Google Play requirements are met.

## Current blockers

| Blocker | Current state |
| --- | --- |
| Application ID | D01 `NOT_DECIDED`; observed value is not accepted for public release |
| Android label | D02 approved, but Android application is not yet updated |
| Release signing | D06 `NOT_DECIDED`; release signing and custody absent |
| Version | D09 `NOT_DECIDED`; public-beta sequence absent |
| Release entrypoint wiring | `main_production.dart` is not wired as the Android release entrypoint |
| Backend mode | D03 `NOT_DECIDED`; production Backend remains unwired |
| Privacy/deletion/support | D08 `NOT_DECIDED`; public URLs and owners absent |
| APK artifact | No signed installable public APK or accepted tuple exists |
| Developer verification/package registration | Applicability and registration plan not accepted |
| Device/accessibility evidence | Physical-device, update, and accessibility matrix not accepted |

## Work carried forward

- GP-1 accepted inventory.
- Separate production entrypoint.
- Production/non-product structural separation.
- Text-core capability boundary.
- Six-step production journey shell.
- Deny-by-default symbolic Backend operation boundary.
- GP-2 core-flow migration and release-artifact exclusion proof remain
  incomplete.
- Production Backend remains unwired.

## Active versus deferred mapping

| Active GitHub track | Separate Deferred Google Play Track |
| --- | --- |
| GP-4 signed APK foundation and direct-distribution signing | Play App Signing and signed AAB |
| GP-5 public privacy/deletion/support readiness | Data safety and Health Apps declarations |
| GP-6 device/accessibility/install/update verification | Play-specific device/Console evidence |
| GP-7 README, guides, screenshots, notes, and metadata | Play icon, feature graphic, descriptions, and screenshots |
| GP-8 pre-publication Public Beta testing and freeze | Internal/closed testing and any applicable tester-duration gate |
| GP-9 GitHub Release publication and observation | Production application, rollout, and Play smoke check |

## 4. User-first README contract

The accepted README places one marked user-facing block after
`# Daily Rhythm Companion`. It explains the goal, non-release status,
six-step journey, AI Character Framework attribution, future safe source,
prerequisites, developer references, and license.

The prior body remains byte-for-byte inside one collapsed legacy record, with
its HTML markers unchanged. Historical claims there do not override current
status. Corrective R2 preserves README SHA-256:
`B11DF9A47F95D60A1FD5973A6D185C8157ECBDFAF0656E86CED925C629E7CAB7`.

## 5. Product and framework boundary

DRC uses the AI Character Framework development foundation:
https://github.com/murayan1982/ai-character-framework

DRC remains an independent general-user application goal. Beta users must not
configure the Framework development environment. Developer, operator, demo,
realtime, raw-diagnostic, and framework-lifecycle controls remain outside the
intended product journey. No production Backend wiring is introduced.

## 6. Active-track dependency model

The path is GP-0 decision closure; GP-1 through GP-3 boundary/journey stability;
GP-4 signed APK foundation; GP-5 privacy/support/guidance; GP-6 device and flow
verification; GP-7 preparation; GP-8 pre-publication Public Beta testing and
candidate freeze; and GP-9 GitHub Release publication and observation. Each
gate needs separate bounded authority. Google Play is a separate deferred track
outside GP-0 through GP-9.

## 7. APK identity, signing, and reproducibility

Before distribution, approve application ID, release version/code, signing
owner, custody/recovery, and certificate evidence. Build a release-signed APK
only under separate authorization. Never place keys, passwords, keystores, or
recoverable secrets in Git or review artifacts.

The accepted tuple binds filename, byte size, SHA-256, source commit,
application ID, version name/code, signing-certificate fingerprint, build
environment, and authorized invocation. Android requires signed APKs. Update
acceptance depends on application ID, certificate continuity (or valid rotation
proof), and version code.

## 8. Direct-install safety guidance

The future guide must name the exact GitHub Release, explain per-source
unknown-app opt-in, exact APK choice and SHA-256 verification, and warn against
mirrors/forwarded copies. It must not ask users to broadly disable protections.
It covers install, first launch, permissions, update, uninstall/reinstall, data
effects, and support recovery without promising unverified migration/backup.

## 9. Privacy, permissions, and support gate

Before publication, provide stable Privacy Policy and support URLs. Reconcile
actual app/Backend behavior with collection, transmission, storage, retention,
deletion, microphone, optional health, chat/advice, diagnostics, and denial.
While D03/D08 remain unresolved, do not claim a production Backend, provider,
legal conclusion, retention period, deletion SLA, or health integration.

## 10. Verification matrix

Later authorized testing covers public-source download/digest; unknown-source
opt-in/install; first launch and six steps; optional denial/revocation; offline,
empty, loading, partial, and failure states; accessibility; signed update;
uninstall/reinstall; non-product exclusion; and absence of credentials,
localhost, and private-LAN dependencies. Evidence must be privacy-safe.

## 11. GitHub Release preparation

GitHub Releases package tag-based deployable iterations with notes and binary
assets. A future beta needs a new v4.1.0 tag, notes, accepted APK, checksum,
privacy/support links, guides, limitations, and rollback instructions.
Generated source ZIP/TAR archives are not the verified APK. README may link a
download only after the exact public Release, asset, and digest are verified.

## 12. GP-8 testing, GP-9 publication, observation, and rollback

GP-8 tests the frozen signed APK on multiple physical devices, including
download-to-install, clean install, manual update, signing continuity,
permission denial, offline/error, accessibility, feedback, and regression
review. GP-8 closes blockers and freezes the GP-9 candidate, but creates no tag,
GitHub Release, or asset.

GP-9 tag/Release/asset actions require exact explicit authority and invocation
limits. After publication, download and reverify the public tuple, smoke-check
clean install/update, and observe crash, security, integrity, support, and
critical-usability signals. Integrity/signing mismatch, credential exposure,
privacy mismatch, or release-blocking failure requires stopping. Retry or
replacement is never implicit.

## 13. Deferred Google Play track

Google Play remains planned but inactive. Reactivation must reconfirm account
and testing eligibility, target API, Play App Signing, AAB identity, Data
safety, Health Apps declarations, listing, policy URLs, test tracks, and
rollout. Direct-distribution evidence does not automatically satisfy Play
gates. A new baseline and authorization chain are required.

## 14. Official source record

Accessed: 2026-11-13.

1. Android Developers, "Alternative distribution options"
   https://developer.android.com/distribute/marketing-tools/alternative-distribution
   - Android supports marketplace, website, and direct distribution.
   - Direct installs require user opt-in for the relevant unknown app source.
2. Android Developers, "Sign your app"
   https://developer.android.com/studio/publish/app-signing
   - APKs must be digitally signed before installation or update.
   - Non-Play APK distribution requires controlled key management.
3. Android Developers, "How app updates work"
   https://developer.android.com/google/play/app-updates
   - Updates depend on application ID, certificate continuity, and version code.
   - An incompatible replacement can require uninstall and erase app data.
4. Android Developers, "Android developer verification"
   https://developer.android.com/developer-verification/guides
   - Direct distributors must assess current identity and package-registration
     obligations and choose the applicable distribution model.
5. Android Developers, "Frequently asked questions"
   https://developer.android.com/developer-verification/guides/faq
   - Verification/install behavior varies by distribution and device context;
     requirements must be reconfirmed before release.
6. GitHub Docs, "About releases"
   https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
   - Releases are tag-based iterations with notes and binary assets; generated
     source archives are distinct from an uploaded APK.

These are planning inputs, not proof that any account, package, artifact, or
publication requirement is completed.

## 15. Static verification and stop boundary

Verify exact M4 A1 D0 at the required baseline; empty index; only the replan
document untracked; accepted README SHA and legacy bytes/markers; UTF-8 without
BOM, LF-only, EOF `0A`; `git diff --check`; no private Windows user path,
private LAN IP, or credential; no fictional release object; unchanged product
and Backend source; preserved v4.0.0 tuple; and a new exact-five-entry external
review handoff.

Stop after handoff creation. Stage, commit, push, build, signing, tag, Release,
asset, Play Console, and hosting operations remain `NOT_AUTHORIZED`.
