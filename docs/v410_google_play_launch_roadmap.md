# Daily Rhythm Companion v4.1.0 Distribution Roadmap

Updated: 2026-11-14

```text
Development line: DRC v4.1.0
Primary target: GitHub Releases Android Public Beta first; Google Play later
Current task: DRC_V410_GP2_EPHEMERAL_MOOD_POLICY_CORRECTIVE_R2
Baseline HEAD / origin/main / remote main: c10db09a0ce1e8acd8960df65032fd97c3f73de8
Surface: exact M4 A1 D0
State: CORRECTIVE_IMPLEMENTED / STATIC_VERIFIED / GP2_INCOMPLETE / READY_FOR_REVIEW
Stage / commit / push: NOT_AUTHORIZED
```

GitHub Android Public Beta is the active distribution track. Google Play is a
separate `DEFERRED / NOT_CANCELLED` track outside the GP-0 through GP-9 phase
numbering. This bounded Control authorizes only the exact five-path GP-2
ephemeral Mood policy test/documentation surface (`M4 A1 D0`).

## Immutable v4.0.0 boundary

The annotated tag `DRC_v4.0.0`, tag object
`67600ee31c951efe34ab1c851f71c375b83c760b`, target
`4b2920a5225fd5a6141ecf8ff4125615e2ec0ef2`, existing Release, and fixed
3,018,230-byte ZIP with SHA-256
`F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142`
remain immutable. The historical ZIP is not an Android APK.

## GP-0 — 計画・decision確定

### 目的
Resolve the decisions and authorization boundaries required for a safe direct
Android beta without silently deciding provider, legal, or publication values.

### 依存関係
The v4.0.0 baseline is closed. D02, D04, GP2-S01, and D11 are approved. D03 is
approved only for the active v4.1.0 GitHub beta local-only/no-remote-Backend
mode; D01, D05-D09 are `NOT_DECIDED`; D10 is `PROPOSED`.

### 作業範囲
Approve application ID, release-signing ownership, version sequence, supported
Android policy, Backend mode, privacy/data/deletion/support ownership, developer
verification/package registration plan, evidence, stop, and rollback controls.

### 完了条件
Every required value and owner is explicit, evidence-backed, and separately
authorized before implementation or publication.

### 禁止事項
Do not infer decisions, expose credentials/private evidence, or authorize
source, build, signing, tag, Release, asset, Console, stage, commit, or push.

## GP-1 — 現行UI棚卸し

### 目的
Maintain the accepted inventory of screens, routes, controls, states, data
flows, permissions, Backend dependencies, and non-product surfaces.

### 依存関係
The accepted inventory commit is
`14ef092cd643fbf02c3bdfde3fa702ed062c3ef3`.

### 作業範囲
Carry forward classifications for general-user, developer, operator, demo, and
diagnostic UI plus loading, empty, error, offline, permission, and lifecycle
states.

### 完了条件
The accepted inventory remains authoritative and traceable to later work.

### 禁止事項
Do not rewrite accepted evidence or claim that inventory acceptance completes
GP-2, product migration, release verification, or publication.

## GP-2 — 一般ユーザーUIとdeveloper/operator UIの分離

### 目的
Preserve the structural production/non-product boundary and deny-by-default
Backend operation boundary.

### 依存関係
Control A closed at `e0e7e8434e49f812735b9d4a510997ad0108d174`;
Control B at `45d6a543165321e30757808095a545b0d9bc9ec1`; later bounded
controls preserve the accepted architecture.

### 作業範囲
Maintain separate production/non-product entrypoints, text-core capability
scope, journey shell, and deny-by-default symbolic Backend decisions.
The first Core-flow slice migrates a local-only, three-choice mood check-in
with an initially unselected, accessible, mutually exclusive selection.
The second slice migrates a local-only, initially unselected choice among the
three stable characters and preserves their accepted selection copy. The third
slice maps the ephemeral mood and character selections to exactly nine fixed,
local messages without network, persistence, AI generation, or Framework
routing. Mood and Character user-facing copy now states that each selection is
reflected immediately in this screen's local message while persistence remains
unavailable. Cloud Backend work is `DEFERRED / NOT_CANCELLED`; persistence, health,
character-aware mood copy, the remaining Core-flow migration, and release-
artifact exclusion proof remain incomplete. D03 is approved only for this
active local-only beta mode, and D08 remains `NOT_DECIDED`. These slices do not
claim GP-2 or GP-3 completion.

For the active v4.1.0 GitHub beta, Mood selection is intentionally not
persisted. It exists only in the current `ProductionJourneyOverview` instance
and returns to unselected when a fresh instance is created. This is an approved
product policy, not an omitted implementation. D08 as a whole remains
`NOT_DECIDED`; no new Character persistence decision is made.

### 完了条件
Completed portions stay byte/evidence compatible, while remaining migration
and artifact proof are explicitly open and separately authorized.

### 禁止事項
Do not claim GP-2 complete, wire a Backend, expose non-product UI, or treat
visual hiding as structural exclusion.

## GP-3 — コアユーザー導線・UI精査

### 目的
Complete a calm general-user daily journey with understandable recovery paths.

### 依存関係
GP-1 inventory and stable GP-2 production boundaries.

### 作業範囲
Complete onboarding, daily journey, settings, permission pre-explanations, and
loading, empty, error, offline, denied/revoked, and lifecycle-recovery states.

### 完了条件
A user can understand, use, defer optional setup, recover, and access privacy
and support paths without developer knowledge.

### 禁止事項
Do not request sensitive access without context, block unrelated features when
optional access is denied, or expose raw implementation diagnostics.

## GP-4 — Android signed APK release基盤

### 目的
Produce a reproducible, signed, installable direct-distribution APK candidate.

### 依存関係
Approved D01, D03 beta mode, D06, D07 active policy, D09, stable GP-2/GP-3,
and an exact implementation/build authorization.

### 作業範囲
Apply formal application ID and display name; wire Android release startup to
`main_production.dart`; establish self-managed release signing with owner,
custody, backup, and recovery; set versionName/versionCode and supported
Android/API policy; establish production Backend mode; remove localhost/private
LAN dependencies; plan developer verification/package registration; produce a
signed APK and record filename, size, SHA-256, signing-certificate SHA-256,
clean install, and manual update evidence.

### 完了条件
The exact APK tuple is reproducible and accepted; release entrypoint, package,
version, certificate, install, update, configuration, and secret exclusion are
verified.

### 禁止事項
Do not commit keys/passwords, use debug signing, publish an artifact, or claim
success from build completion alone.

## GP-5 — Privacy / data / health対応

### 目的
Make user disclosures and support paths match actual app and Backend behavior.

### 依存関係
Stable product behavior plus approved D03/D08 ownership and evidence.

### 作業範囲
Publish Privacy Policy and support/contact; complete data inventory,
microphone and health permission pre-explanations, retention/deletion behavior,
public deletion method, health provider/ownership/consent, and app/Backend/
policy reconciliation.

### 完了条件
Every sensitive flow, purpose, optionality, retention, deletion, contact, and
provider claim is accurate, reachable, and testable.

### 禁止事項
Do not invent provider, operator, legal conclusion, retention period, deletion
SLA, policy URL, or support contact.

## GP-6 — Android実機・アクセシビリティ・異常系検証

### 目的
Verify release-candidate quality on representative physical devices.

### 依存関係
Accepted GP-4 APK candidate and stable GP-5 user-facing behavior.

### 作業範囲
Cover supported Android versions, physical devices, TalkBack, text enlargement,
contrast, device sizes, loading, empty, error, offline, permission denial/
revocation, Backend/network failure, lifecycle recovery, clean install, manual
update, and non-product exclusion.

### 完了条件
The matrix has no unresolved release blocker, credential/private endpoint,
non-product reachability, or unsupported accessibility claim.

### 禁止事項
Do not use private health/user data in evidence or proceed with an unresolved
release-blocking crash, integrity, privacy, or accessibility failure.

## GP-7 — GitHub Release掲載素材・公開準備

### 目的
Prepare a truthful, user-first publication package without publishing it.

### 依存関係
Accepted GP-4 through GP-6 evidence.

### 作業範囲
Finalize user-first README, APK install guide, unknown-app explanation, release
notes, screenshots, Privacy Policy/support links, artifact metadata, update/
uninstall/deletion guides, beta status, known limitations, and AI Character
Framework attribution.

### 完了条件
All material references the exact accepted APK and contains no fictional URL,
unsupported claim, private path/IP, credential, or v4.0.0 mutation.

### 禁止事項
Do not create a tag, GitHub Release, or asset; do not expose a download link
before public artifact verification.

## GP-8 — GitHub Android Public Beta testing

### 目的
Test the frozen candidate before any public tag, Release, or asset operation.

### 依存関係
An exact signed APK candidate and accepted GP-7 materials.

### 作業範囲
Use multiple physical devices for download-to-install journey, clean install,
manual update, signing continuity, previous-public-build update where
applicable, permission denial, offline/error, accessibility, feedback
collection, crash/regression review, release-blocker closure, and GP-9
candidate freeze.

### 完了条件
The exact candidate and materials are frozen, blockers are closed, signing and
update continuity are accepted, and GP-9 publication is separately proposed.

### 禁止事項
Do not create or publish a tag, GitHub Release, checksum, or asset in GP-8.

## GP-9 — GitHub Release production公開と公開後確認

### 目的
Publish and verify the exact accepted GitHub Android Public Beta under explicit
authorization.

### 依存関係
GP-8 candidate freeze, approved tag/release/asset tuple, rollback plan, and
explicit publication authorization.

### 作業範囲
Create the approved tag and GitHub Release; upload the signed APK and checksum;
publish release notes and Privacy Policy/support/install/update links; perform
public re-download, artifact metadata, clean-install, and update smoke checks;
observe/monitor; execute rollback/withdrawal if needed; record v4.1.0 release.

### 完了条件
Public tag, Release, asset, checksum, metadata, smoke checks, observation, and
release record match the accepted tuple while v4.0.0 remains unchanged.

### 禁止事項
Do not retry, replace, force, or expand publication beyond exact authority.
Stop on integrity/signing/privacy mismatch or failed public smoke verification.

## Deferred Google Play Track — NOT_CANCELLED

Google Play is not GP-9 and has no GP phase number in this plan. Its unchecked
work includes developer account/testing applicability, Play App Signing,
signed AAB, then-current target API, Data safety, Health Apps declaration,
listing icon/feature graphic/descriptions/screenshots, internal and closed
testing, any applicable 12-testers/14-days requirement, production application,
and Play publication smoke checks.

Reactivation requires a new baseline, then-current official evidence, explicit
decisions, and separate build/upload/testing/publication authority. GitHub beta
completion cannot mark Play work complete.

## Ephemeral Mood Policy R1 verification

The focused journey regression verifies initial unselected state, materializes
the local advice by selecting Mood and Character within one widget instance,
disposes that State, and verifies reset to unselected with no restored advice
in a fresh instance. Character selection is test setup, not a new Character
persistence decision. Product source and dependencies remain unchanged. Existing Mood,
Character, local-advice, boundary, and widget suites remain accepted.

## Ephemeral Mood Policy R1 stop point

README remains frozen at its accepted SHA-256. Backend source, Android
configuration, and `pubspec.yaml` remain unchanged. Changes are limited to the
exact five-path GP-2 ephemeral Mood policy surface, `M4 A1 D0`, recorded by
this Control. Stop after required verification and a new review handoff.
Stage, commit, push, build, signing, tag, Release, asset, Console, and hosting
operations remain `NOT_AUTHORIZED`.
