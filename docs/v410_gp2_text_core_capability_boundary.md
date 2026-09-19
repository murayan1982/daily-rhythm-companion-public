# DRC v4.1.0 GP-2 Text-Core Capability Boundary

Task: `DRC_V410_GP2_TEXT_CORE_CAPABILITY_BOUNDARY_CORRECTIVE_R1`

Baseline: `e0e7e8434e49f812735b9d4a510997ad0108d174`

## Scope decision

GP2-S01 is `APPROVED` with value `TEXT_CORE_PLUS_CHAT`. Approval evidence is
the user selection recorded on 2026-09-19. This control records a scope and
typed boundary; it does not authorize transport, provider, or release wiring.

| Capability | Production disposition |
| --- | --- |
| Sleep / health connection | Included; external health work is pending D03/D08 |
| Mood check-in | Included |
| Character selection | Included |
| Daily advice | Included |
| Optional text chat | Included |
| History | Included |
| Microphone and voice input | Excluded |
| Voice output | Excluded |
| Realtime controls | Excluded |
| Motion controls | Excluded |
| Demo tools | Excluded |
| Developer/operator controls | Excluded |
| Raw diagnostics | Excluded |
| Framework lifecycle controls | Excluded |

## Classification vocabulary

- `CORE_CANDIDATE`: approved text-core candidate represented by the symbolic
  production operation boundary.
- `HEALTH_PENDING_DECISION`: health connection candidate blocked from the active
  core set until GP0-D03 and GP0-D08 are approved.
- `NON_PRODUCT_DENIED`: known non-product behavior with no production symbol.
- `BACKEND_ONLY_CALLBACK`: provider redirect target; never an app-originated
  production allowlist operation.
- `UNKNOWN_DENIED`: not approved or not represented; denied by default.

## Flutter BackendApiClient public network-operation inventory

| Public method | Classification | Symbolic production operation |
| --- | --- | --- |
| `fetchHealthStatus` | UNKNOWN_DENIED | None; `/health` usage requires a later decision |
| `fetchDemoStatus` | NON_PRODUCT_DENIED | None |
| `fetchCharacters` | CORE_CANDIDATE | `loadCharacters` |
| `fetchSleepSummary` | CORE_CANDIDATE | `loadSleepSummary` |
| `fetchSleepProviderSelectionStatus` | CORE_CANDIDATE | `loadSleepProviderSelection` |
| `fetchDailyRecords` | CORE_CANDIDATE | `loadHistory` |
| `fetchRecentSleepTrend` | CORE_CANDIDATE | `loadRecentSleepTrend` |
| `fetchWeeklySleepSummary` | CORE_CANDIDATE | `loadWeeklySleepSummary` |
| `fetchRhythmReport` with weekly period | CORE_CANDIDATE | `loadWeeklyRhythmReport` |
| `fetchRhythmReport` with monthly period | CORE_CANDIDATE | `loadMonthlyRhythmReport` |
| `fetchFitbitStatus` | HEALTH_PENDING_DECISION | `loadFitbitConnectionStatus` |
| `fetchFitbitConnect` | HEALTH_PENDING_DECISION | `startFitbitConnection` |
| `fetchGoogleHealthConnectionUx` | HEALTH_PENDING_DECISION | `loadGoogleHealthConnectionGuidance` |
| `fetchGoogleHealthDiagnostics` | NON_PRODUCT_DENIED | None |
| `fetchGoogleHealthSelfCheck` | NON_PRODUCT_DENIED | None |
| `fetchGoogleHealthPreflight` | NON_PRODUCT_DENIED | None |
| `submitVoiceInputDemoRequest` | NON_PRODUCT_DENIED | None |
| `submitVoiceOutputDemoRequest` | NON_PRODUCT_DENIED | None |
| `submitMotionDemoRequest` | NON_PRODUCT_DENIED | None |
| `createPostAdviceChatSession` | CORE_CANDIDATE | `createTextChatSession` |
| `sendPostAdviceChatMessage` | CORE_CANDIDATE | `sendTextChatMessage` |
| `createAdvice` | CORE_CANDIDATE | `createAdvice` |

The client's public configuration fields, constructor, localhost hint, and
health formatting helper are not network operations and are not imported into
the production boundary.

## Backend route inventory

| Method and route | Classification | Notes |
| --- | --- | --- |
| `GET /health` | UNKNOWN_DENIED | Service health route, not a product UI endpoint; later use decision required |
| `GET /characters` | CORE_CANDIDATE | Character selection |
| `GET /sleep/summary` | CORE_CANDIDATE | Sleep summary |
| `GET /sleep/providers` | CORE_CANDIDATE | Provider-selection status only; no provider selected here |
| `POST /advice` | CORE_CANDIDATE | Daily advice |
| `POST /chat/sessions` | CORE_CANDIDATE | Optional text-chat creation |
| `POST /chat/sessions/{session_id}/messages` | CORE_CANDIDATE | Optional text-chat message |
| `GET /chat/sessions/{session_id}` | UNKNOWN_DENIED | Existing route without an approved production symbol |
| `GET /daily-records` | CORE_CANDIDATE | History list |
| `GET /daily-records/recent-sleep-trend` | CORE_CANDIDATE | Recent trend |
| `GET /daily-records/weekly-summary` | CORE_CANDIDATE | Weekly sleep summary |
| `GET /daily-records/rhythm-report` | CORE_CANDIDATE | Weekly/monthly report selected symbolically |
| `POST /daily-records` | UNKNOWN_DENIED | Existing Backend write without a direct approved app operation |
| `GET /daily-records/{date}` | UNKNOWN_DENIED | Existing route without an approved production symbol |
| `GET /fitbit/status` | HEALTH_PENDING_DECISION | Inactive until D03/D08 decisions |
| `GET /fitbit/connect` | HEALTH_PENDING_DECISION | Inactive until D03/D08 decisions |
| `GET /fitbit/callback` | BACKEND_ONLY_CALLBACK | Never app-originated allowlist traffic |
| `GET /google-health/status` | HEALTH_PENDING_DECISION | Candidate only; no active symbol in this control |
| `GET /google-health/connect` | HEALTH_PENDING_DECISION | Candidate only; no active symbol in this control |
| `GET /google-health/connection-ux` | HEALTH_PENDING_DECISION | Maps to connection guidance symbol |
| `GET /google-health/callback` | BACKEND_ONLY_CALLBACK | Never app-originated allowlist traffic |
| `GET /google-health/diagnostics` | NON_PRODUCT_DENIED | Diagnostic surface |
| `GET /google-health/self-check` | NON_PRODUCT_DENIED | Operator self-check |
| `GET /google-health/preflight` | NON_PRODUCT_DENIED | Operator preflight |
| `GET /google-health/token-refresh-check` | NON_PRODUCT_DENIED | Operator check |
| `GET /google-health/scope-check` | NON_PRODUCT_DENIED | Operator check |
| `GET /google-health/permission-retest-readiness` | NON_PRODUCT_DENIED | Operator check |
| `GET /google-health/project-access-readiness` | NON_PRODUCT_DENIED | Operator check |
| `GET /google-health/codelab-exercise-check` | NON_PRODUCT_DENIED | Operator check |
| `GET /google-health/connection-checklist` | NON_PRODUCT_DENIED | Operator checklist |
| `GET /demo/status` | NON_PRODUCT_DENIED | Demo surface |
| `GET /demo/voice-input/status` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/voice-input` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/voice-input/staging` | NON_PRODUCT_DENIED | Demo/operator surface |
| `POST /demo/voice-input/staging/{staging_id}/fake-handoff` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/voice-input/staging/{staging_id}/openai-fake-executor` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/voice-input/transcript` | NON_PRODUCT_DENIED | Demo/operator surface |
| `GET /demo/voice-output/status` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/voice-output` | NON_PRODUCT_DENIED | Demo surface |
| `GET /demo/voice-output/audio/{artifact_id}` | NON_PRODUCT_DENIED | Demo artifact surface |
| `GET /demo/motion/status` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/motion` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/character-motion/presentation` | NON_PRODUCT_DENIED | Demo surface |
| `POST /demo/character-motion/vts/presentation` | NON_PRODUCT_DENIED | Operator adapter surface |
| `POST /realtime/text/sessions` | NON_PRODUCT_DENIED | Realtime surface |
| `GET /realtime/text/sessions/{session_id}/events` | NON_PRODUCT_DENIED | Realtime surface |
| `POST /realtime/text/sessions/{session_id}/cancel` | NON_PRODUCT_DENIED | Realtime surface |
| `POST /realtime/framework-v6/provider-free/sessions` | NON_PRODUCT_DENIED | Framework lifecycle surface |
| `POST /realtime/framework-v6/provider-free/sessions/{session_id}/turns` | NON_PRODUCT_DENIED | Framework lifecycle surface |
| `POST /realtime/framework-v6/provider-free/sessions/{session_id}/interrupt` | NON_PRODUCT_DENIED | Framework lifecycle surface |
| `GET /realtime/framework-v6/provider-free/sessions/{session_id}/diagnostics` | NON_PRODUCT_DENIED | Diagnostic surface |
| `DELETE /realtime/framework-v6/provider-free/sessions/{session_id}` | NON_PRODUCT_DENIED | Framework lifecycle surface |

Any operation or route not listed as an active `CORE_CANDIDATE` symbol is denied
by default. Route classification is evidence, not a wired URL allowlist.

## Decision and implementation boundary

Fitbit and Google Health remain production-scope candidates, but GP0-D03
Backend publication and GP0-D08 privacy/data ownership are `NOT_DECIDED`.
Privacy Policy, Data safety, Health Apps declarations, consent, retention,
deletion, and operational ownership must agree before health connectivity can
be activated. This control performs no provider selection, approves no URL or
endpoint, adds no credential, and wires no Backend client.

The production Backend remains unwired. UI migration, release wiring, and
artifact exclusion proof remain incomplete, so GP-2 is not complete.

## Next control proposal

Propose a separately authorized control that resolves the production operation
allowlist contract after D03/D08 decisions, then wires only approved core
operations behind user-safe states. Health operations remain inactive unless a
later decision and privacy review explicitly authorize them.
