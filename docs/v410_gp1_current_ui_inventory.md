# DRC v4.1.0 GP-1 Current UI Inventory

## 1. Control metadata

Task: DRC_V410_GP1_CURRENT_UI_INVENTORY_R1
Corrective task: DRC_V410_GP1_CURRENT_UI_INVENTORY_CORRECTIVE_R1
Phase: GP-1
Baseline: 60d3fc76c45e153a0c31ce9c9ce8e2fd78c48ca2
Method: read-only static source inspection
Runtime verification: NOT_VERIFIED
GP-1 review / acceptance: NOT_PERFORMED
GP0-D04 decision: NOT_DECIDED

This records current behavior; it does not approve production architecture,
release readiness, policy declarations, or product-source edits.

## 2. Inspected sources

- app/lib/main.dart, main_rt2ec_operator.dart, screens/, widgets/, services/,
  models/, Android manifest/build.gradle, pubspec.yaml, and app/test/
- app/lib/state/: NOT_FOUND
- Backend route/service/test names were used only as static evidence.

No Flutter, Backend, Android, or test execution was performed.

## 3. Startup entry points

| Entry | Behavior | Classification | Evidence | Open gap |
| --- | --- | --- | --- | --- |
| main.dart | BackendApiClient and optional runtimes; MaterialApp.home is HomeScreen. | MIXED | main.dart:15-108 | Production composition not separated. |
| main_rt2ec_operator.dart | Microphone operator UI; DRC_RT2EC_OPERATOR defaults false. | OPERATOR | main_rt2ec_operator.dart:8-34 | Artifact isolation NOT_VERIFIED. |

Named routes/onGenerateRoute and settings, onboarding, sign-in, or exit screens
are NOT_IMPLEMENTED.

## 4. Screen, route, dialog, and sheet inventory

| ID | Surface | Entry | Primary user | Actions | Data dependency | Permission dependency | Backend dependency | Current states | Classification | Evidence | Open gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UI-01 | Home shell | Startup | Mixed | Scroll, History, reload | All home models | Indirect voice/health | Yes | loading/partial/success/error | MIXED | home_screen.dart:5373-5510 | All classes share one surface. |
| UI-02 | Loop overview/status | Home | General/diagnostic | Inspect/recover | health/character/advice | None direct | Yes | checking/ready/incomplete/error | MIXED | :907-1200 | Raw Backend/engine state visible. |
| UI-03 | Character/assets | Home | General/demo | Select/inspect | catalog | None | Yes | loading/empty/selected/missing | MIXED | :4231-4469 | Asset diagnostics mixed in. |
| UI-04 | Sleep source/summary | Home | General | Inspect/connect | provider/health | Provider auth | Yes | loading/available/partial/error | MIXED | :3192-3455,:4163-4229 | Ownership unclear. |
| UI-05 | Mood/advice | Home | General | Select/create | mood/sleep/character | None | Yes | ready/creating/success/error | GENERAL_USER | :4471-4737 | Offline/timeout not distinct. |
| UI-06 | Post-advice chat | After advice | General/developer | Start/skip/send/restart | chat | None | Yes | idle/active/terminal/error | MIXED | :4739-4957 | Developer details visible. |
| UI-07 | Record completion | After advice | General | Open History | advice | None | Yes | hidden/complete | GENERAL_USER | :4959-5062 | Persistence needs runtime proof. |
| UI-08 | HistoryScreen | Push | General | Back/retry | records/reports | None | Yes | loading/empty/content/error | GENERAL_USER | history_screen.dart:11-284 | No delete/offline cache. |
| UI-09 | Demo status | Advanced | Developer/demo | Refresh | capability | None | Yes | loading/content/error | DEMO | home_screen.dart:1307-1399 | Normal Home reachability. |
| UI-10 | Realtime text | Advanced | Developer | Start/cancel/handoff | stream/input | None | Configured | unconfigured/active/terminal/failed | DEVELOPER | :1401-1717 | Product need NOT_VERIFIED. |
| UI-11 | Framework v6 | Advanced | Developer/operator | Open/send/interrupt/diagnose/close | session | None | Configured | unconfigured/open/active/error | DIAGNOSTIC | :1719-1967 | Diagnostics product-reachable. |
| UI-12 | Terminal voice | Advanced | Developer | Opt-in/enqueue/process/flush | queue/audio | Playback | Configured | ready/queued/playing/failed | DEVELOPER | :1969-2245 | Technical state visible. |
| UI-13 | Integrated voice | Advanced | Operator | Opt-in/start/stop | voice/transcript | RECORD_AUDIO | Configured | ready/capture/process/error | OPERATOR | :2247-2402 | Pre-explanation NOT_IMPLEMENTED. |
| UI-14 | Voice demos | Advanced | Demo | Submit/play/stop/replay | demo/artifact | Input demo metadata-only | Yes | idle/submitting/playback/error | DEMO | :2426-2749,:5168-5324 | Demo APIs product-reachable. |
| UI-15 | Motion/demo | Advanced | Developer/demo | Select/apply/reset/submit | motion | None | Configured | unconfigured/ready/success/error | DEMO | :2751-3190 | Implementations overlap. |
| UI-16 | Fitbit | Conditional | User/operator | Inspect/connect/open URL | OAuth/status | External consent | Yes | disconnected/ready/connected/error | MIXED | :3343-3455,:5342-5371 | Return flow NOT_VERIFIED. |
| UI-17 | Google Health | Advanced | User/operator | Refresh/inspect | UX/checks | Provider scopes | Yes | loading/connected/blocked/error | MIXED | :3492-4130 | User/raw checks coexist. |
| UI-18 | RT2EC capture | Separate entry | Operator | Acknowledge/permission/start/stop/cancel | capture | RECORD_AUDIO | No core API | disabled/denied/recording/error | OPERATOR | operator source | Distribution isolation NOT_VERIFIED. |

No showDialog or showModalBottomSheet call was found in app/lib.

## 5. Transitions and back behavior

Home pushes History with MaterialPageRoute from the app bar and record handoff;
default back returns Home. Other content is conditional in one scroll. Deep
links, guarded exit, nested navigation, modal focus, and state restoration are
NOT_IMPLEMENTED or NOT_VERIFIED.

## 6. HomeScreen functional decomposition

The first band has Backend state, loop/status/demo context, character/assets,
sleep, mood, advice, chat, record handoff, and completion. After a divider,
Advanced Demo Tools exposes capability, realtime, voice, motion, Fitbit, and
Google Health diagnostics. This visual grouping is not a reachability boundary.

## 7. User actions

General candidates: character/mood selection, advice, optional chat, history,
health connection, retry, audio playback. Diagnostics, manual stream/session
lifecycle, demos, motion controls, and capture are non-product candidates.
Account, privacy, deletion, support, onboarding, settings, and sign-out actions
are NOT_IMPLEMENTED.

## 8. State coverage

Loading/generic error, empty records, unavailable sleep, unconfigured runtime,
permission denial variants, expired audio, terminal chat, and retry exist in
selected flows. Distinct offline, DNS/TLS, timeout, maintenance, auth expiry,
and process-restoration product states are NOT_IMPLEMENTED or NOT_VERIFIED.

## 9. Permissions and pre-explanations

Android declares RECORD_AUDIO. RT2EC checks/requests it and distinguishes
denied, permanently denied, restricted, and unsupported. Home can capture via
configured bindings, but contextual product explanation/settings recovery are
NOT_IMPLEMENTED. No Android health permission was found; health uses
Backend/provider OAuth.

## 10. Microphone, health, sleep, Fitbit, and Google Health

- Microphone: default-off operator entry plus optional Home binding; device
  behavior NOT_VERIFIED.
- Sleep: startup loads summary/provider; unavailable sleep has mood fallback.
- Fitbit: conditional status; connect launches an external URL.
- Google Health: user UX and diagnostics/preflight/self-check load at startup.
- Authorization, token retention/revocation, and real provider behavior are
  NOT_VERIFIED.

## 11. Backend and localhost reachability

BackendApiClient uses DRC_BACKEND_API_BASE_URL, default
http://127.0.0.1:8000. Startup
calls health, characters, sleep, demo status, and Google Health UX/check APIs.
User flows call advice/chat/records/provider APIs; advanced controls call
demo/realtime/framework APIs. Production HTTPS/deployment is
NOT_IMPLEMENTED/NOT_VERIFIED.

## 12. Configuration and feature flags

Realtime text, character/VTS motion, integrated voice, voice output, framework
v6, and RT2EC use compile-time flags defaulting false. Advanced Home UI still
renders unconfigured states. Release-variant enforcement is NOT_VERIFIED.

## 13. Diagnostics, logs, and developer information

Home shows base URL, Backend status, engine/mode/capabilities, technical codes,
session IDs, provider diagnostics, and configuration. Complete redaction is
NOT_VERIFIED. Production logging, telemetry, and consent design were not found.

## 14. Accessibility and responsive static risks

Material controls, labels, scrolling, max width 760, and adjustResize are
positive static signals. Risks: one long card, dense rows, mixed language,
expanded developer detail, and no verified live-region/semantics/focus plan.
TalkBack, large text, contrast, targets, keyboard, insets, rotation, and devices
are NOT_VERIFIED.

## 15. Source evidence and test coverage

Test names cover daily-loop recovery, mood/character, chat, demos,
sleep/health, History, optional wiring, safe errors, microphone denial, and
audio lifecycle. Tests were not run. No production-exclusion test was found.

## 16. NOT_VERIFIED and NOT_IMPLEMENTED register

NOT_IMPLEMENTED: onboarding, settings, privacy/deletion/support, structural
separation, named routing, production HTTPS default.
NOT_VERIFIED: release reachability, real permissions/provider consent,
offline/timeout, accessibility/device matrix, Backend deployment, Play Console,
signed AAB, and production readiness.

## 17. Handoff gaps

- GP-2: enforce entry/route/build/Backend boundaries and remove production
  reachability to developer/operator/demo/diagnostic surfaces.
- GP-3: define onboarding, settings, permission explanations, core flow, user
  language, and loading/empty/error/offline recovery.
- GP-5: reconcile microphone/health/chat/diagnostics, retention/deletion,
  policy, Data safety, and Health Apps claims.
- GP-6: execute device accessibility, permission, lifecycle, network, and
  failure testing; this inventory does not claim those checks passed.
