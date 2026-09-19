# Daily Rhythm Companion v4.1.0 Google Play Launch Roadmap

Updated: 2026-09-19

## Planning state

```text
Development line: DRC v4.1.0
Primary target: Google Play
Planning task: DRC_V410_GOOGLE_PLAY_LAUNCH_PLANNING_R1
Planning R1: COMPLETED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED
Planning R1 commit: d7e39ad37667c6f3f104c2097f5ca54f9089df5c
Current task: DRC_V410_GP2_PRODUCTION_JOURNEY_SHELL_CORRECTIVE_R1
Current phase: GP-2 一般ユーザーUIとdeveloper/operator UIの分離
Implementation authorization: APPROVED
Commit / push authorization: NOT_AUTHORIZED
Baseline HEAD / origin/main / remote main: 438b8e82c2fb66181289a0a5a60897993effe62f
Current implementation surface: exact M6 A4 D0
Current state: CORRECTIVE_IMPLEMENTED / STATIC_VERIFIED / ACCESSIBLE_STATUS_SEMANTICS / MARKDOWN_CHECKBOX_RESTORED / READY_FOR_REVIEW
```

This roadmap starts the DRC v4.1.0 development line. Its goal is an actual
Google Play launch, not only a locally runnable Android build. Work proceeds
through explicit phase gates covering product UI, production boundaries,
Android release configuration, privacy and health-data declarations, device
quality, store presentation, testing tracks, and production publication.

This R1 changes planning documents only. It does not authorize implementation,
builds, signing, uploads, testing-track operations, or publication for any later
phase.

## Immutable v4.0.0 boundary

DRC v4.0.0 is RELEASED / VERIFIED / CLOSED. The following release objects are
immutable and outside the v4.1.0 development surface:

- annotated tag `DRC_v4.0.0`;
- tag object `67600ee31c951efe34ab1c851f71c375b83c760b`;
- tag target `4b2920a5225fd5a6141ecf8ff4125615e2ec0ef2`;
- the published GitHub Release and its release history;
- `DailyRhythmCompanion_v4.0.0_20260908_173440.zip`;
- the 3,018,230-byte fixed ZIP with SHA-256
  `F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142`.

No v4.1.0 phase may rewrite, regenerate, replace, retag, or republish any of
these objects. v4.1.0 receives its own source, version, artifact, verification,
and publication history under later explicit authorization.

## Current launch blockers

| Area | Current state | Required v4.1.0 outcome |
| --- | --- | --- |
| Android identity | `applicationId` is `com.example.app` | A permanent, unique application ID is approved before the first Play upload. |
| Display identity | Android application label is `app` | The formal user-facing application name is approved and applied consistently. |
| Release signing | The release build uses debug signing | A credential-safe release-signing flow and Play App Signing ownership model are established. |
| Backend connectivity | The Flutter default is `http://127.0.0.1:8000` | Production builds use an approved reachable HTTPS Backend and contain no localhost dependency. |
| Product boundary | `HomeScreen` mixes user, developer, operator, demo, and diagnostic UI | Production exposes only the general-user experience; non-product controls are separated and unreachable. |

The blocker list is a starting inventory, not a complete policy or quality
assessment. GP-1 must expand it before product changes begin.

## Delivery principles

1. Every phase requires a bounded implementation surface, static and runtime
   evidence appropriate to that phase, review, and explicit acceptance.
2. A completed prerequisite does not implicitly authorize the next phase.
3. Store declarations, privacy documents, product behavior, Backend behavior,
   and retained data must describe the same system.
4. Production separation must be structural. Merely hiding a developer control
   visually is not sufficient if it remains reachable or callable.
5. Secrets, signing keys, private health data, private paths, LAN addresses,
   and raw operator evidence must never enter tracked source or store assets.
6. Google Play policy and console requirements must be reconfirmed at the phase
   that uses them because external requirements can change.
7. Version and build-number changes, release builds, Play Console actions, and
   publication each require their own later authorization.

## Phase dependency overview

| Phase | Name | Depends on | Primary gate |
| --- | --- | --- | --- |
| GP-0 | 計画確定 | v4.0.0 closed baseline | Scope, decisions, owners, evidence, and stop rules accepted |
| GP-1 | 現行UI棚卸し | GP-0 | Complete screen/state/data-flow inventory accepted |
| GP-2 | 一般ユーザーUIとdeveloper/operator UIの分離 | GP-1 | Production reachability boundary verified |
| GP-3 | コアユーザー導線のUI精査 | GP-1, GP-2 | Core journey and state handling accepted |
| GP-4 | Android release基盤 | GP-0 decisions; coordinate with GP-2 and GP-3 | Installable signed release AAB and production configuration verified |
| GP-5 | Privacy / Data safety / Health Apps対応 | GP-1; stable GP-2 through GP-4 behavior | App, Backend, policy, and declarations reconciled |
| GP-6 | Android実機・アクセシビリティ・異常系検証 | GP-2 through GP-5 | Device, accessibility, and failure evidence accepted |
| GP-7 | Google Play掲載素材作成 | Stable GP-3 UI; GP-5 policy wording | Complete policy-safe store listing set accepted |
| GP-8 | internal / closed testing | GP-4 through GP-7 | Required testing-track evidence and exit criteria accepted |
| GP-9 | production公開と公開後確認 | GP-8 | Production release and post-release checks completed |

## GP-0 計画確定

### 目的

Convert the Google Play launch goal into an approved, auditable sequence with
resolved ownership, irreversible decisions identified early, and explicit
authorization boundaries for every later phase.

### 依存関係

- DRC v4.0.0 is RELEASED / VERIFIED / CLOSED.
- Public `main` is synchronized at the recorded v4.1.0 planning baseline.
- This roadmap and the companion tasklist are reviewed together.

### 作業範囲

- Approve the v4.1.0 launch scope and phase order.
- Decide the formal application ID and application display name before they are
  implemented.
- Decide the production Backend publication and operations model, including
  HTTPS endpoint ownership, environments, observability, availability, and
  incident response.
- Decide how product, developer, operator, demo, and diagnostic surfaces are
  separated across build variants, entry points, routes, and Backend exposure.
- Establish the data inventory for account, microphone, sleep, health, chat,
  diagnostics, logs, retention, and deletion behavior.
- Confirm Play developer account type and determine whether the personal-account
  12-testers / 14-days closed-testing requirement applies.
- Define phase-specific review evidence, rollback/stop rules, and the authority
  required for source edits, builds, signing, uploads, and publication.
- Reconfirm current Google Play target API, health-app, privacy, and testing
  requirements before implementation is authorized.

### 完了条件

- No launch-critical decision remains implicit or ownerless.
- All current blockers have an approved destination state and owning phase.
- The roadmap, tasklist, evidence model, and authorization boundaries are
  reviewed and accepted.
- The next exact implementation surface is proposed separately; it is not
  activated by accepting this plan.

### 禁止事項

- Do not edit `app/pubspec.yaml`, Android settings, Flutter product source,
  Backend product source, existing `roadmap.md`, existing `tasklist.md`, or
  release checkers during this planning task.
- Do not create or expose credentials, signing material, Play Console IDs, or
  private operator evidence.
- Do not build, sign, upload, stage, commit, push, tag, or publish.

## GP-1 現行UI棚卸し

Implementation evidence is recorded in
docs/v410_gp1_current_ui_inventory.md and
docs/v410_gp1_production_separation_map.md. At creation, this read-only evidence
did not itself mean GP-1 acceptance or GP0-D04 approval. The inventory was later
reviewed, accepted, committed, and pushed as
14ef092cd643fbf02c3bdfde3fa702ed062c3ef3. GP0-D04 was separately APPROVED by
user decision on 2026-09-18. This history does not complete GP-2.

### 目的

Create a source-backed inventory of every user-visible screen, action, state,
permission request, diagnostic surface, and Backend dependency before deciding
what remains in the production product.

### 依存関係

- Planning R1 and the GP-0 inventory control are accepted as planning and
  evidence baselines; GP-0 as a whole is not complete or accepted.
- GP0-D01 is DEFERRED; GP0-D02 is APPROVED; GP0-D03 through GP0-D09,
  excluding D02, remain NOT_DECIDED; GP0-D10 remains PROPOSED.
- This read-only GP-1 inventory was performed under separate explicit
  authorization and does not approve any unresolved GP-0 decision.

### 作業範囲

- Map startup, home, daily check-in, sleep/health connection, advice, chat,
  voice, character, history, settings, recovery, and exit flows.
- Classify every control and message as general-user, developer, operator,
  demo, diagnostic, or mixed-purpose.
- Record loading, empty, success, partial, error, denied-permission, offline,
  expired-session, and Backend-unavailable states.
- Inventory routes, entry points, compile/runtime flags, API calls, configuration
  sources, logs, diagnostic details, and current localhost assumptions.
- Inventory microphone and health-data permission timing and existing
  pre-permission explanations.
- Capture accessibility and responsive-layout risks without using private user
  data in screenshots or evidence.

### 完了条件

- Every reachable production-candidate screen and action has an owner,
  classification, data dependency, and intended v4.1.0 disposition.
- Mixed-purpose `HomeScreen` content is decomposed into an accepted separation
  map for GP-2 and a core-journey map for GP-3.
- Missing loading, empty, error, offline, permission, accessibility, and device
  states are recorded as actionable gaps.
- Inventory evidence is reproducible and contains no secret or private data.

### 禁止事項

- Do not change product behavior while inventorying it.
- Do not treat a currently hidden control as safely separated without proving
  reachability and Backend boundaries.
- Do not copy tokens, private health values, local user paths, LAN addresses, or
  raw diagnostic payloads into tracked evidence.

## GP-2 一般ユーザーUIとdeveloper/operator UIの分離

GP0-D04 is APPROVED: use a separate production entrypoint and a
production-only composition with structural import, route, and Backend
reachability boundaries. Control A was reviewed, accepted, committed, pushed,
and closed at `e0e7e8434e49f812735b9d4a510997ad0108d174`. Control B was reviewed,
accepted, committed, pushed, and closed at
`45d6a543165321e30757808095a545b0d9bc9ec1`; it defines only the approved
text-core capability and symbolic Backend-operation boundaries. The Backend and
privacy decision control was reviewed, accepted, committed, pushed, and closed
at `438b8e82c2fb66181289a0a5a60897993effe62f`; GP0-D03 and GP0-D08 remain
`NOT_DECIDED`. Control C adds only a local, non-interactive journey shell for the
approved six-step scope. Backend wiring remains unauthorized. These controls do
not complete core-flow migration, release wiring, artifact exclusion proof, or
GP-2 as a whole.

### 目的

Make the production app a coherent general-user product and move developer,
operator, demo, and diagnostic capabilities behind explicit non-production
boundaries.

### 依存関係

- GP-1 inventory and classification are accepted.
- The separation architecture and exact implementation surface receive separate
  authorization.

### 作業範囲

- Define a production entry point and route graph containing only approved
  general-user journeys.
- Move developer/operator/demo/diagnostic panels to dedicated non-production
  targets, screens, routes, or build variants.
- Prevent production navigation, deep links, feature flags, and accidental
  gestures from reaching non-product UI.
- Prevent production startup and normal user actions from calling operator-only
  or diagnostic Backend endpoints.
- Replace developer-facing raw statuses and failure details with safe,
  actionable user messages while retaining private diagnostic observability in
  approved operator channels.
- Preserve bounded developer/operator capability for development and acceptance
  without shipping it as product UI.

### 完了条件

- Production builds expose no developer, operator, demo, or raw diagnostic
  controls through navigation, deep links, semantics, or ordinary interaction.
- Production network evidence shows no unintended calls to non-product
  endpoints during core journeys.
- Automated and manual tests cover both the production exclusion boundary and
  the separately authorized non-production entry point.
- General-user behavior needed for GP-3 remains functional.

### 禁止事項

- Do not rely only on `Visibility`, obscured widgets, secret taps, or labels to
  claim production separation.
- Do not embed secrets or operator authorization material in the client.
- Do not remove diagnostic capability without preserving an approved private
  operational path and support model.

## GP-3 コアユーザー導線のUI精査

### 目的

Turn the remaining product UI into a clear, calm, and recoverable journey from
first launch through daily use, health connection, advice, chat, and settings.

### 依存関係

- GP-1 journey inventory is accepted.
- GP-2 production boundary is implemented and verified, or its stable interface
  is accepted for coordinated work.

### 作業範囲

- Design first-run onboarding that explains the product value and lets users
  defer optional setup.
- Place microphone and health-data pre-permission explanations immediately
  before contextual permission requests.
- Refine the daily check-in, sleep-data connection, advice, chat, voice, history,
  and character experience into a minimal core flow.
- Add a settings screen for permissions, connection status, privacy links,
  data-deletion guidance, Backend/account state, and relevant preferences.
- Design explicit loading, empty, error, offline, retry, permission-denied, and
  partially available states.
- Establish responsive layouts, text-scaling expectations, accessible names,
  focus order, touch targets, and contrast tokens for GP-6 verification.

### 完了条件

- A new user can understand the app, complete or defer setup, and reach the
  first useful result without developer knowledge.
- Core journeys remain usable when optional microphone or health access is
  denied, revoked, or temporarily unavailable.
- Settings provide discoverable recovery, privacy, and deletion paths.
- All defined states have approved copy, interaction behavior, and testable
  acceptance criteria.

### 禁止事項

- Do not request sensitive permissions before a clear contextual explanation.
- Do not block unrelated app functions when an optional permission is denied.
- Do not expose implementation terms, raw exceptions, internal endpoint names,
  or diagnostic payloads to general users.

## GP-4 Android release基盤

### 目的

Create a reproducible, credential-safe Android release foundation capable of
producing the signed AAB that will be tested and later submitted to Google Play.

### 依存関係

- GP-0 identity, Backend, signing-ownership, and environment decisions are
  accepted.
- GP-2 production boundary and GP-3 release-facing identity/configuration needs
  are stable enough to avoid publishing a throwaway package identity.

### 作業範囲

- Apply the permanent application ID and formal display name consistently.
- Configure an Android API level meeting the approved Google Play requirement,
  with API 36 or higher as the current planning floor.
- Establish release signing without storing keys, passwords, or recoverable
  secrets in Git or review artifacts.
- Configure and document Play App Signing roles, upload-key custody, rotation,
  backup, and recovery responsibilities.
- Define release-safe environment injection for the approved HTTPS Backend and
  remove production dependence on localhost.
- Produce and verify a signed AAB under separate build authorization.
- Verify package identity, version/build metadata, signing certificate,
  permissions, release-only configuration, and install/upgrade behavior.
- Treat the eventual v4.1.0 version/build-number edit as a separately authorized
  release task; this planning R1 does not change it.

### 完了条件

- The release AAB uses the permanent identity, approved label, release signing,
  target API, and production Backend configuration.
- No debug signing, localhost dependency, private endpoint, or secret is present
  in the production artifact.
- Signing recovery and Play App Signing ownership are documented and reviewed.
- The exact AAB is reproducibly identified by filename, size, digest, source
  commit, version, and signing identity before any upload.

### 禁止事項

- Do not commit keystores, passwords, service credentials, local property files,
  or secret-bearing logs.
- Do not change the application ID after the first permanent Play application
  record or testing upload without an explicit replacement-app decision.
- Do not upload or publish an artifact merely because it builds successfully.

## GP-5 Privacy / Data safety / Health Apps対応

### 目的

Make product behavior, Backend processing, privacy disclosures, deletion
behavior, Play Data safety answers, and Health Apps declarations accurate and
mutually consistent.

### 依存関係

- GP-1 data-flow inventory is accepted.
- GP-2 through GP-4 have stable production behavior, configuration, identity,
  and permission requirements.
- Current Google Play policy and declaration forms are reconfirmed.

### 作業範囲

- Finalize a data map covering collection, transmission, storage, sharing,
  retention, protection, account association, optionality, and deletion.
- Publish an accessible Privacy Policy using the formal product and operator
  identity.
- Define and test a clear data-deletion request or in-product deletion method,
  including Backend completion and user-facing confirmation.
- Complete Data safety answers from verified behavior rather than assumptions.
- Complete required Health Apps declarations and justify each health-data type,
  purpose, permission, and user benefit.
- Minimize microphone and health permissions and align pre-permission copy,
  runtime prompts, settings, denial handling, and policy text.
- Define support contact, retention exceptions, deletion timing, and incident
  response language.

### 完了条件

- A field-by-field reconciliation matrix shows that app behavior, Backend
  behavior, Privacy Policy, deletion process, Data safety, and Health Apps
  declarations agree.
- Every sensitive permission and health-data use is necessary, explained,
  testable, and represented in the store submission.
- Privacy Policy and deletion instructions are reachable both in-app and at the
  required public locations.
- Policy review has no unsupported, incomplete, or contradictory claim.

### 禁止事項

- Do not claim that data is uncollected, unshared, encrypted, ephemeral, or
  deleted unless the end-to-end implementation proves it.
- Do not use real health data, personal identifiers, tokens, or private evidence
  in tracked documentation or store review materials.
- Do not request broader health or microphone access for possible future use.

## GP-6 Android実機・アクセシビリティ・異常系検証

### 目的

Prove that the production candidate remains understandable and recoverable on
representative Android hardware, assistive technology, layouts, and realistic
failure conditions.

### 依存関係

- GP-2 through GP-5 production behavior and declarations are stable.
- An authorized signed release candidate and controlled test Backend exist.

### 作業範囲

- Test representative Android versions, physical devices, screen sizes,
  orientations where supported, densities, memory/network conditions, and
  fresh-install/upgrade paths.
- Verify TalkBack labels, roles, announcements, traversal order, modal focus,
  dynamic updates, and actionable error recovery.
- Verify enlarged text, display scaling, reflow, clipping, truncation, touch
  targets, and color contrast.
- Exercise loading, empty, error, offline, timeout, partial-response, Backend
  maintenance, expired auth, permission denial/revocation, and interrupted
  microphone/health flows.
- Check startup, resume, background/foreground transitions, process recreation,
  and safe retry/idempotency behavior.
- Record public-safe evidence and triage severity, reproducibility, ownership,
  and release-blocking status.

### 完了条件

- The accepted device and Android-version matrix passes all release-blocking
  core journeys.
- TalkBack, text enlargement, contrast, and supported screen sizes meet the
  approved accessibility criteria.
- No loading, empty, error, or offline state traps the user or leaks internal
  details.
- All release-blocking defects are fixed and regression-tested; accepted
  residual risks are explicit.

### 禁止事項

- Do not treat emulator-only success as Android release acceptance.
- Do not disable accessibility services, permission denials, or network faults
  to obtain a passing result.
- Do not record private accounts, health values, credentials, or LAN details in
  screenshots, videos, logs, or handoffs.

## GP-7 Google Play掲載素材作成

### 目的

Create an accurate, cohesive store listing that represents the verified
production UI and gives reviewers and prospective users the information needed
to understand DRC.

### 依存関係

- GP-3 production UI and formal identity are visually stable.
- GP-5 policy language and public URLs are approved.
- Screenshot capture uses a production-safe build and sanitized data.

### 作業範囲

- Produce the Google Play app icon and verify adaptive/icon-mask behavior.
- Produce the feature graphic using the approved visual identity.
- Write short and full descriptions, release notes, category/contact metadata,
  and support wording without unsupported medical or health claims.
- Capture required phone and any supported device screenshots from production
  UI only, using fictional or sanitized content.
- Check asset dimensions, formats, localization readiness, legibility, rights,
  product-name consistency, and policy compliance.
- Maintain a listing-to-feature trace showing that every visual and claim exists
  in the candidate submitted for testing.

### 完了条件

- Icon, feature graphic, descriptions, screenshots, support/privacy links, and
  other required listing fields form a complete review set.
- No image or copy exposes developer/operator UI, private data, localhost/LAN
  details, debug status, or a feature absent from the submitted build.
- The final listing is reviewed on representative desktop and mobile Play views.

### 禁止事項

- Do not use real personal or health data in store assets.
- Do not claim diagnosis, treatment, guaranteed outcomes, or capabilities not
  supported by the verified product and approved policy position.
- Do not capture screenshots from a developer/operator/demo configuration.

## GP-8 internal / closed testing

### 目的

Validate the exact Play-distributed candidate through the required testing
tracks, collect actionable feedback, and satisfy any account-specific access
requirement before production application.

### 依存関係

- GP-4 through GP-7 are accepted.
- The exact signed AAB, listing, privacy declarations, tester plan, and support
  channel are approved for upload.
- Current Play Console eligibility and account-type requirements are confirmed.

### 作業範囲

- Upload the exact authorized AAB to internal testing first and verify Play-side
  processing, install, update, package identity, signing, and Backend access.
- Run internal smoke, permission, privacy-link, deletion-path, accessibility,
  offline, and crash checks on the Play-delivered build.
- If the developer account is subject to the personal-account rule, plan and
  complete closed testing with at least 12 opted-in testers continuously for at
  least 14 days, subject to the then-current console requirement.
- Manage tester instructions, consent, safe evidence, feedback triage, crash/
  ANR review, fixes, retests, and track promotion criteria.
- Reconcile every replacement AAB with source, version, digest, signing, test
  evidence, declarations, and store assets.

### 完了条件

- The Play-delivered candidate passes the approved internal-testing matrix.
- Required closed-testing duration, tester participation, feedback, and
  production-access evidence are complete when applicable.
- No unresolved release-blocking crash, ANR, policy mismatch, broken Backend
  dependency, privacy/deletion failure, or critical usability defect remains.
- The exact production candidate and its evidence are frozen for GP-9 review.

### 禁止事項

- Do not count sideloaded builds as Play testing-track evidence.
- Do not fabricate testers, opt-ins, activity, dates, feedback, or eligibility.
- Do not promote a different, unverified AAB or silently change declarations
  after testing.

## GP-9 production公開と公開後確認

### 目的

Submit the accepted candidate for production, respond to review without losing
traceability, and verify the public listing, installation, core service, and
support posture after release.

### 依存関係

- GP-8 exit criteria and any production-access requirement are accepted.
- The exact AAB, source commit, version, digest, signing identity, declarations,
  listing, release notes, rollout plan, monitoring, and rollback/stop decision
  are approved.
- Explicit production submission and publication authorization is received.

### 作業範囲

- Run final no-change reconciliation across artifact, source, Backend, policy,
  declarations, listing, support, and monitoring readiness.
- Submit the production application and preserve reviewer questions and answers
  as public-safe release evidence.
- Use the approved rollout mode and stop criteria; do not improvise artifact or
  declaration changes during review.
- After availability, verify listing visibility, install/update from Google
  Play, startup, onboarding, permissions, Backend connectivity, daily core flow,
  privacy/deletion links, and support contact.
- Monitor crash/ANR, Backend health, policy messages, reviews, and support signals
  during the agreed observation window.
- Record the immutable v4.1.0 release tuple and close the line only after the
  post-release smoke and evidence review pass.

### 完了条件

- Google Play production status, public listing, and exact released artifact are
  verified against the approved release tuple.
- Post-release smoke checks pass on a clean install and supported update path.
- Monitoring and support ownership are active; blocking incidents trigger the
  approved halt, rollback, or corrective path.
- v4.1.0 release records are complete, reviewed, and closed without modifying
  v4.0.0 history.

### 禁止事項

- Do not submit, roll out, halt, replace, or republish without the corresponding
  explicit authorization.
- Do not rebuild or swap the accepted artifact during publication.
- Do not alter the v4.0.0 tag, GitHub Release, asset, fixed ZIP, or public history.
- Do not declare completion before the public Play-delivered app passes the
  required post-release smoke checks.

## Planning R1 stop point

Planning R1 stops after creation and static review of this roadmap and
`docs/v410_google_play_launch_tasklist.md`. No later phase is implemented by this
change. Stage, commit, and push remain NOT_AUTHORIZED pending review.
