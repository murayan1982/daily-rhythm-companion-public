# DRC v4.1.0 GP-1 Production Separation Map

## Control boundary

This is PROPOSED inventory evidence for GP-2 and GP-3. It does not approve
GP0-D04, change reachability, or authorize product implementation.

## HomeScreen decomposition map

| Current surface | Current class | Proposed disposition | Reason/evidence | Next control |
| --- | --- | --- | --- | --- |
| Daily loop, character, sleep, mood, advice | GENERAL_USER/MIXED | PRODUCTION_CANDIDATE | Core sequence in home_screen.dart:907-4737 | GP-3 refine states/copy. |
| Chat and History | GENERAL_USER/MIXED | REQUIRES_SPLIT | User flow includes developer details. | GP-2 remove diagnostics; GP-3 refine. |
| Backend/API status and demo context | DIAGNOSTIC | NON_PRODUCT_CANDIDATE | URL, engine, mode, capability shown. | GP-2 make unreachable. |
| Visual asset preview | MIXED | REQUIRES_DECISION | Product images and review diagnostics coexist. | GP0-D04/GP-2 decide. |
| Demo status and voice/motion demos | DEMO | NON_PRODUCT_CANDIDATE | Explicit demo endpoints/manual requests. | GP-2 isolate app and Backend. |
| Realtime/framework/manual voice | DEVELOPER | NON_PRODUCT_CANDIDATE | Manual lifecycle/diagnostic controls. | GP-2 isolate structurally. |
| Fitbit/Google Health user guidance | MIXED | REQUIRES_SPLIT | Useful journey plus raw provider details. | GP-2 split; GP-3 design setup/settings. |
| Google Health developer checks | DIAGNOSTIC | NON_PRODUCT_CANDIDATE | Diagnostics/preflight/self-check. | GP-2 non-product only. |
| RT2EC capture app | OPERATOR | NON_PRODUCT_CANDIDATE | Separate default-off operator entry. | GP-2 prove artifact exclusion. |

## Production candidates

Startup branding, core check-in, character, sleep summary, mood, advice,
optional chat, history, and reduced health guidance are candidates only.
Final journeys and language require GP-3.

## Developer and operator candidates

Backend URL/status, capability matrices, manual streams/sessions, voice/motion
demo requests, technical codes/session IDs, provider checks, and RT2EC capture
are non-product candidates. Visual hiding is insufficient.

## Demo and diagnostic candidates

Demo API controls, asset review, engine/mode fields, realtime diagnostics,
Google Health checks, and raw status rows should be unreachable from production.
Whether they remain in separate tooling is REQUIRES_DECISION.

## Mixed-purpose UI

Daily-loop status, chat, visual assets, audio, Fitbit, and Google Health combine
product value with technical evidence. They require component/route separation
and safe product models, not a production-ready claim.

## Current route, entry-point, and build configuration

- Normal: main.dart to MaterialApp.home to HomeScreen.
- Route: two MaterialPageRoute pushes to HistoryScreen.
- Operator: main_rt2ec_operator.dart, compile-time gated, default-off.
- Optional service flags default false, but advanced Home sections remain.
- Product/non-product flavors, route allowlists, and artifact reachability tests
  are NOT_IMPLEMENTED.

## Backend reachability

Home startup reaches core, demo-status, and Google Health diagnostic APIs.
Advanced controls reach demo, realtime, framework, Fitbit, and health endpoints
through one base URL. The default is loopback HTTP. No verified production
endpoint allowlist or separated non-product Backend exists.

## GP-2 separation candidates

1. Define a production composition with approved user routes only.
2. Move operator/demo/diagnostic tools to separate entry points or packages and
   prove absence/unreachability in production artifacts.
3. Split mixed widgets/models so product UI cannot expose raw URLs, modes,
   technical codes, session IDs, or provider diagnostics.
4. Enforce Backend endpoint allowlists and release-safe configuration.
5. Add static, artifact, and navigation tests for production exclusion.

These are proposals, not the GP0-D04 decision.

## GP-3 general-user journey candidates

1. Onboarding and optional health/voice setup with defer paths.
2. Sleep status to mood to character to advice.
3. Optional chat/voice followed by save/history confirmation.
4. Settings for connection/permission, privacy, deletion, and support.
5. Actionable loading, empty, partial, offline, timeout, denial, and recovery
   without implementation terminology.

## Security, privacy, and accessibility risks

- Raw endpoint/configuration and diagnostic identifiers are visible.
- Mixed Backend reachability broadens production exposure.
- Dense single-page content lacks verified semantics, focus, announcement,
  scaling, contrast, and device evidence.
- Startup fan-out can fail partially; offline/timeout modeling is inconsistent.
- Microphone/health behavior is not reconciled with privacy, deletion,
  Data safety, or Health Apps declarations.

## Source evidence

- app/lib/main.dart:15-108
- app/lib/main_rt2ec_operator.dart:8-34
- app/lib/screens/home_screen.dart:874-5510
- app/lib/screens/history_screen.dart:11-284
- app/lib/services/backend_api_client.dart:20-520
- app/android/app/src/main/AndroidManifest.xml:1-36
- app/android/app/build.gradle.kts:1-46

## Unresolved decisions

- GP0-D04 remains NOT_DECIDED; no separation architecture is approved.
- GP0-D01 is DEFERRED and must be re-decided before GP-4.
- D03 and D05-D09 remain NOT_DECIDED; D10 remains PROPOSED.
- Daily Rhythm Companion is approved as display name, but Android source
  implementation is not authorized; Japanese store localization is separate.
- Production Backend, permissions, policy ownership, signing, target API,
  version/build, Play testing, and publication remain unresolved.
