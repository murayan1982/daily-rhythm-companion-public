# Daily Rhythm Companion v4.1.0 Google Play Launch Tasklist

Updated: 2026-09-19

## Current state

```text
Development line: DRC v4.1.0
Primary target: Google Play
Planning task: DRC_V410_GOOGLE_PLAY_LAUNCH_PLANNING_R1
Planning R1: COMPLETED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED
Planning R1 commit: d7e39ad37667c6f3f104c2097f5ca54f9089df5c
Current task: DRC_V410_GP0_BACKEND_PRIVACY_DECISION_CONTROL_CORRECTIVE_R1
Current phase: GP-0 計画確定 / GP-5 prerequisite decision control
Implementation authorization: APPROVED
Commit / push authorization: NOT_AUTHORIZED
Baseline HEAD / origin/main / remote main: 45d6a543165321e30757808095a545b0d9bc9ec1
Current implementation surface: exact M3 A1 D0
Current state: CORRECTIVE_IMPLEMENTED / STATIC_VERIFIED / READY_FOR_REVIEW
```

This tasklist is the prioritized execution index for
`docs/v410_google_play_launch_roadmap.md`. An unchecked box means incomplete; it
does not grant authorization. Each implementation, build, signing operation,
Play Console action, and publication step requires its own approved scope.

Priority meaning:

- **P0:** irreversible decision or launch blocker; resolve before dependent
  product/release work.
- **P1:** required product, release, policy, or quality work; must pass before
  testing-track exit.
- **P2:** required store, testing, and release-readiness work.
- **P3:** production submission, public verification, and line closure.

## P0 — Identity, architecture, and production-boundary blockers

- [ ] **[GP-0] 正式application ID:** approve a permanent, unique Android
  application ID to replace `com.example.app`; record ownership and the
  no-change-after-first-Play-upload rule.
- [x] **[GP-0] 正式アプリ表示名:** approve the formal display name to replace
  `app`; define consistent spelling for Android, in-app UI, policy, support, and
  Google Play.
- [ ] **[GP-0] Backend公開方式:** approve hosting, HTTPS endpoint, environment
  separation, secrets management, availability, observability, maintenance,
  incident response, and operating ownership.
- [x] **[GP-0/GP-5] Backend/privacy decision evidence control:** inventory the
  source-confirmed current state, official policy evidence, unresolved D03/D08
  fields, questionnaire, and approval exit criteria without selecting values.
- [ ] **[GP-0] Google Play account requirement:** confirm account type, current
  target API requirement, production-access prerequisites, health-app review
  requirements, and the evidence that must be retained.
- [ ] **[GP-0] Signing ownership:** approve who controls the upload key, recovery
  material, Play App Signing account access, backup, and rotation.
- [ ] **[GP-0] Data inventory:** map microphone, sleep/health, chat, account,
  diagnostic, log, retention, sharing, protection, and deletion behavior across
  app and Backend.
- [ ] **[GP-0] Privacy/data ownership decision:** approve the accountable
  operator, contacts, data handling, processors, retention, deletion, and
  declaration ownership represented by GP0-D08.
- [x] **[GP-1] 現行UI棚卸し:** inventory every screen, route, action, state,
  permission, API call, and entry point; classify each as general-user,
  developer, operator, demo, diagnostic, or mixed-purpose.
- [x] **[GP-1] HomeScreen混在の分解設計:** map every mixed `HomeScreen` section
  to either the production journey, a separate non-production surface, or
  removal.
- [x] **[GP-2] Production entrypoint foundation:** add the separate production
  entrypoint, production-only composition, minimal shell, structural import
  boundary, and focused source/widget verification.
- [x] **[GP-2] Production text-core capability boundary:** record the approved
  text-core-plus-chat scope and add typed capability and symbolic operation
  boundaries without UI migration or Backend wiring.
- [ ] **[GP-2] developer/operator UIのproduction分離:** approve a structural
  boundary using dedicated entry points/routes/build variants so production
  cannot reach developer, operator, demo, or raw diagnostic UI.
- [ ] **[GP-2] Non-product Backend boundary:** ensure production startup and core
  journeys cannot call operator-only, demo, or diagnostic endpoints.
- [ ] **[GP-2] Core-flow migration:** move only approved general-user journeys
  into the production-only composition under a later bounded control.
- [ ] **[GP-2] Artifact exclusion proof:** prove developer, operator, demo, and
  diagnostic code and routes are absent or unreachable in the release artifact.
- [ ] **[GP-4] localhost依存除去:** replace the production default
  `http://127.0.0.1:8000` with approved release-safe HTTPS configuration and
  prove that no production path depends on localhost or a private LAN address.
- [ ] **[GP-5] Privacy/declaration reconciliation owner:** assign one accountable
  owner for consistency across implementation, Backend behavior, Privacy
  Policy, deletion, Data safety, Health Apps declarations, and store copy.

## P1 — Product experience, Android release, privacy, and quality

### Production user experience

- [ ] **[GP-3] 初回オンボーディング:** explain product value, setup sequence,
  optional features, privacy entry points, and a safe defer/skip path.
- [ ] **[GP-3] マイク・健康データ権限の事前説明:** present contextual,
  purpose-specific explanations before platform prompts; support deny, defer,
  revoke, retry, and settings recovery.
- [ ] **[GP-3] 設定画面:** provide permission and connection status, relevant
  preferences, privacy and support links, data-deletion guidance, and safe
  recovery actions without raw diagnostics.
- [ ] **[GP-3] Core daily flow:** refine check-in, sleep/health connection,
  advice, post-advice chat, voice, character, and history into a coherent
  general-user journey.
- [ ] **[GP-3] User-facing language:** replace raw exceptions, endpoint names,
  engine/mode terms, and operator details with actionable product copy.
- [ ] **[GP-3/GP-6] loading / empty / error / offline状態:** define and verify
  loading, empty, partial, error, timeout, offline, maintenance, retry, and
  recovery behavior for every core journey.

### Android release foundation

- [ ] **[GP-4] Apply formal identity:** apply the approved application ID and
  display name to the authorized Android/product surfaces and verify package
  consistency.
- [ ] **[GP-4] Android API 36以上:** configure and verify the approved target API
  with API 36 or higher as the current planning floor, subject to the current
  Play requirement at execution time.
- [ ] **[GP-4] release signing:** replace debug signing with a credential-safe
  release-signing flow; keep keystore and passwords outside Git and review
  artifacts.
- [ ] **[GP-4] Play App Signing:** enroll/configure under explicit authorization;
  document upload certificate, app-signing certificate, access roles, recovery,
  rotation, and verification.
- [ ] **[GP-4] Production environment configuration:** inject the approved HTTPS
  Backend and release-safe feature configuration without embedding secrets.
- [ ] **[GP-4] Version/build metadata:** under a later exact authorization, set
  the v4.1.0 version/build number consistently; do not change
  `app/pubspec.yaml` during Planning R1.
- [ ] **[GP-4] signed AAB:** produce exactly the authorized release AAB and record
  source commit, version, filename, size, SHA-256, package ID, signing identity,
  permissions, and build invocation.
- [ ] **[GP-4] Release artifact inspection:** prove no debug signing, localhost,
  private LAN address, credential, developer route, or unintended permission is
  present in the AAB.
- [ ] **[GP-4] Install/upgrade verification:** verify clean install, launch,
  package identity, Play signing compatibility, upgrade path, and safe data
  handling on physical Android devices.

### Privacy, Data safety, and Health Apps

- [ ] **[GP-5] Privacy Policy:** publish a stable public policy URL covering the
  formal app/operator identity, data categories, purposes, transmission,
  storage, sharing, protection, retention, user choices, deletion, and contact.
- [ ] **[GP-5] In-app privacy access:** link the Privacy Policy from onboarding
  and settings and verify it remains reachable before and after sign-in/setup.
- [ ] **[GP-5] データ削除方法:** implement and document an accessible deletion
  request or in-product deletion flow, Backend processing, completion timing,
  retained exceptions, and user confirmation.
- [ ] **[GP-5] Data safety declaration:** derive each answer from verified app and
  Backend behavior; reconcile collection, sharing, optionality, purpose,
  encryption, ephemerality, and deletion claims.
- [ ] **[GP-5] Health Apps declaration:** declare each health-data type, access,
  user benefit, purpose, permission, and handling accurately and minimally.
- [ ] **[GP-5] Permission minimization:** request only the microphone and health
  permissions used by current production features; remove speculative access.
- [ ] **[GP-5] Policy consistency review:** compare runtime behavior, network/data
  inventory, Privacy Policy, deletion process, Data safety, Health Apps forms,
  support copy, and store descriptions field by field.
- [ ] **[GP-5] Public-safe evidence:** confirm policy evidence contains no token,
  credential, real health value, personal identifier, private path, or LAN IP.

### Device, accessibility, and failure behavior

- [ ] **[GP-6] Physical Android matrix:** define and execute representative OS,
  device, screen, density, network, memory, fresh-install, and upgrade coverage.
- [ ] **[GP-6] TalkBack:** verify accessible names, roles, state announcements,
  traversal order, modal focus, live updates, controls, and error recovery.
- [ ] **[GP-6] 文字サイズ拡大:** verify approved large text/display scaling with
  reflow, no clipped critical content, and no blocked action.
- [ ] **[GP-6] 色コントラスト:** measure text, icons, controls, focus/selected
  states, disabled states, errors, and charts against the approved criteria.
- [ ] **[GP-6] 端末サイズ対応:** verify supported narrow/tall/large screens,
  densities, insets, keyboard, and orientation behavior where supported.
- [ ] **[GP-6] Touch and keyboard behavior:** verify target sizes, scroll reach,
  focus visibility, input validation, keyboard avoidance, and dismissal.
- [ ] **[GP-6] Permission abnormal paths:** test first denial, permanent denial,
  revocation, restricted device state, interrupted prompt, settings return, and
  partial capability.
- [ ] **[GP-6] Backend/network abnormal paths:** test offline, DNS/TLS failure,
  timeout, maintenance, malformed/partial response, expired auth, retry, and
  idempotency without exposing internals.
- [ ] **[GP-6] Lifecycle resilience:** test background/foreground transitions,
  process recreation, interrupted microphone/health operations, and safe resume.
- [ ] **[GP-6] Release-blocker closure:** fix and regression-test all blocking
  accessibility, device, crash, privacy, data-loss, and recovery defects.

## P2 — Store listing, testing tracks, and production readiness

### Google Play listing assets

- [ ] **[GP-7] Google Playアイコン:** create the final high-resolution icon,
  verify adaptive masking and legibility, and align it with in-app identity.
- [ ] **[GP-7] feature graphic:** create the final feature graphic with approved
  branding, legibility, rights, dimensions, format, and no unsupported claim.
- [ ] **[GP-7] 説明文:** prepare short/full descriptions, release notes,
  category/contact/support metadata, and localization-ready source copy.
- [ ] **[GP-7] Claim review:** remove unsupported medical, diagnostic, treatment,
  guaranteed-outcome, privacy, or feature claims.
- [ ] **[GP-7] スクリーンショット:** capture required device screenshots from
  production UI only, using fictional/sanitized content and no developer,
  operator, diagnostic, localhost, LAN, account, or health-data leakage.
- [ ] **[GP-7] Listing/build trace:** prove that every screenshot, label, and
  feature claim matches the exact candidate submitted for testing.
- [ ] **[GP-7] Listing preview review:** inspect the complete listing on phone and
  desktop views and verify links, cropping, order, and readability.

### Testing tracks

- [ ] **[GP-8] internal testing:** upload the exact authorized signed AAB to the
  internal track and preserve Play-side version, processing, signing, and tester
  availability evidence.
- [ ] **[GP-8] Play-delivered smoke:** install from the internal track and verify
  startup, onboarding, permissions, Backend, daily flow, settings, privacy,
  deletion guidance, offline/error behavior, and update.
- [ ] **[GP-8] Crash/ANR review:** inspect Play pre-launch and test telemetry;
  triage reproducibility, severity, owner, fix, and retest status.
- [ ] **[GP-8] Tester support:** provide safe tester instructions, feedback path,
  privacy notice, known limitations, and build identification.
- [ ] **[GP-8] personal account該当時の12 testers / 14 days closed testing:**
  verify applicability and, when required, complete at least 12 opted-in testers
  continuously for at least 14 days under the then-current Play rules.
- [ ] **[GP-8] Closed-test evidence:** retain public-safe tester-count, duration,
  participation, feedback-response, and production-access evidence without
  exposing tester identities.
- [ ] **[GP-8] Replacement-build control:** for every new AAB, repeat identity,
  digest, signing, declaration, listing, test, and regression reconciliation;
  never silently substitute an artifact.
- [ ] **[GP-8] Exit review:** confirm no blocking crash, ANR, policy mismatch,
  Backend dependency, privacy/deletion failure, accessibility defect, or core
  journey defect remains.
- [ ] **[GP-8] Freeze production candidate:** record the exact AAB and accepted
  source/evidence tuple proposed for GP-9; this does not authorize submission.

## P3 — Production submission and post-release closure

- [ ] **[GP-9] Final no-change reconciliation:** compare the frozen candidate,
  source, version, digest, signing, Backend, Privacy Policy, deletion method,
  Data safety, Health Apps declaration, permissions, listing, and support plan.
- [ ] **[GP-9] Production authorization:** obtain explicit authorization for the
  exact artifact, listing, declarations, release notes, rollout mode, and stop
  criteria.
- [ ] **[GP-9] production申請:** submit the authorized candidate and preserve
  public-safe Play review status, questions, responses, and decisions.
- [ ] **[GP-9] Review-response control:** do not alter artifacts, declarations,
  or claims ad hoc; route every required change through a new bounded corrective
  and repeat affected validation.
- [ ] **[GP-9] Rollout control:** apply the approved availability/rollout mode,
  monitoring window, halt criteria, incident ownership, and user communication.
- [ ] **[GP-9] 公開後smoke check:** from Google Play, verify listing visibility,
  clean install/update, startup, onboarding, permissions, Backend connectivity,
  daily core flow, settings, privacy/deletion links, and support contact.
- [ ] **[GP-9] Public artifact verification:** verify public version/package,
  Play signing identity, release date/status, and the accepted production tuple.
- [ ] **[GP-9] Post-release monitoring:** review crash/ANR, Backend health, policy
  messages, reviews, and support signals during the approved observation window.
- [ ] **[GP-9] v4.1.0 release record:** record final evidence and close v4.1.0 only
  after production and post-release verification are accepted.
- [ ] **[GP-9] v4.0.0 preservation check:** confirm the v4.0.0 tag, GitHub Release,
  published asset, fixed ZIP, digest, and public history remain unchanged.

## Planning R1 historical closure checklist

- [x] New development line is explicitly DRC v4.1.0.
- [x] Primary target is explicitly Google Play.
- [x] GP-0 through GP-9 are represented with prioritized executable tasks.
- [x] All supplied current blockers have destination tasks.
- [x] v4.0.0 immutable release objects are outside the implementation surface.
- [x] Planning R1 changes only the two new v4.1.0 planning documents.
- [x] Stage, commit, push, build, signing, upload, tag, and publication remain
  unauthorized.
- [x] User review and acceptance.
- [x] Separate commit authorization.
- [x] Separate push authorization.

These historical approvals closed Planning R1. GP-1, GP-2 Control A, and GP-2
Control B are accepted, committed, and pushed. Control B closed at
`45d6a543165321e30757808095a545b0d9bc9ec1`; GP-2 as a whole remains
incomplete.

## Current decision-control stop point

The Planning R1 stop point is historically complete; Planning R1 was committed,
pushed, and closed. GP-1 is accepted, committed, and pushed. GP-2 Control A
closed at `e0e7e8434e49f812735b9d4a510997ad0108d174`, and Control B closed at
`45d6a543165321e30757808095a545b0d9bc9ec1`. The current control documents
decision evidence only: GP0-D03 and GP0-D08 remain `NOT_DECIDED`; Backend
wiring, Privacy Policy publication, Data safety submission, and Health Apps
declaration remain incomplete and unauthorized. Stop after implementation,
static verification, and review handoff. Staging, commit, and push remain
`NOT_AUTHORIZED`.
