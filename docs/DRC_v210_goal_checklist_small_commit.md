# Daily Rhythm Companion v2.1.0 goal checklist — small commits

Updated: 2026-07-25
Status: IN_PROGRESS
Current small commit: R-1e — explicit approval, publication, and post-publication verification
Current small-commit state: CURRENT / NOT_COMPLETED
Current implementation state: NOT_STARTED
Parent R-1 state: CURRENT / NOT_COMPLETED
W-1 state: COMPLETED / ACCEPTED
W-2 state: COMPLETED / ACCEPTED
W-3 state: COMPLETED / ACCEPTED
W-4 state: COMPLETED / ACCEPTED
W-5 state: COMPLETED / ACCEPTED
Current released version: v2.0.1
Current source candidate metadata: Backend 2.1.0 / Flutter 2.1.0+3 (NOT_RELEASED)

## Source-of-truth rule

This file is the authoritative detailed implementation source of truth for v2.1.0. W-1 established and accepted it after verification, diff review, and operator approval passed. `tasklist.md` is the concise operator index and `roadmap.md` defines the version direction.

Completed release and maintenance records remain immutable historical evidence:

```text
v2.0.0 checklist: docs/DRC_v200_goal_checklist_small_commit.md
v2.0.0 release notes: release_notes/v2.0.0.md
v2.0.x checklist: docs/DRC_v20x_maintenance_checklist.md
v2.0.1 release record: docs/v201_patch_release_record.md
v2.0.1 release notes: release_notes/v2.0.1.md
annotated tags: DRC_v2.0.0 and DRC_v2.0.1
```

They are not edited or reused as v2.1.0 completion records.

## Progress rule

```text
- At most one small commit is CURRENT at a time.
- A phase remains NOT_COMPLETED until its implementation, focused checks,
  aggregate checks, diff review, and operator approval pass.
- Later phases remain PLANNED and must not be marked complete early.
- Existing source code does not prove configured real-provider acceptance.
- Local token presence does not prove live token validity.
- OAuth URL preparation does not prove connection success.
- Mock-safe verification does not substitute for explicit real operator verification.
- API-only evidence does not substitute for required smartphone Web evidence.
```

## Immutable release baseline

```text
v2.0.0 status: RELEASED
v2.0.1 status: RELEASED
v2.0.1 source HEAD: 3e4c9f6186ef7195045a445307e14f412924bc26
v2.0.1 fixed ZIP: DailyRhythmCompanion_20260723_143447.zip
v2.0.1 fixed ZIP SHA-256: ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1
v2.0.1 post-publication SHA-256 re-verification: completed
```

W-1 and all later v2.1.0 work use new commits. They do not rewrite either release tag, replace either release asset, rebuild the v2.0.1 fixed ZIP, or alter the publication records.

## v2.1.0 goal

```text
Turn the accepted v2.0.0 demo paths into a clearer repeatable daily-use loop,
with Fitbit real-use completion as the main new capability.
```

## Phase queue

```text
W-1  COMPLETED / ACCEPTED   Fitbit current behavior inventory and contract
W-2  COMPLETED / ACCEPTED   Fitbit token/status/reconnect hardening
W-3  COMPLETED / ACCEPTED   Fitbit real sleep normalization and API regression tests
W-4  COMPLETED / ACCEPTED   Sleep-provider selection, source-label UI, and simplified
                              Google Health user UX with retained operator diagnostics
W-5  COMPLETED / ACCEPTED   Wearable migration correction and configured Google Health verification
  W-5a  COMPLETED / ACCEPTED   Fitbit real operator contract and preflight
  W-5b1  COMPLETED / ACCEPTED   Google Health API migration audit and legacy Fitbit execution retirement
  W-5b2  COMPLETED / ACCEPTED   Configured Google Health API operator verification
C-1  COMPLETED / ACCEPTED     Post-advice chat lifecycle and UI-state hardening
  C-1a  COMPLETED / ACCEPTED     Current behavior inventory and implementation contract
  C-1b  COMPLETED / ACCEPTED     Backend lifecycle outcomes, bounded turns, and tests
  C-1c  COMPLETED / ACCEPTED     Flutter lifecycle state, recovery UI, and C-1 acceptance
T-1  COMPLETED / ACCEPTED  Flutter in-app TTS player and artifact-expiry handling
  T-1a  COMPLETED / ACCEPTED     Current TTS/audio handoff inventory and implementation contract
  T-1b  COMPLETED / ACCEPTED  Flutter in-app player abstraction, states, and mock-safe tests
  T-1c  COMPLETED / ACCEPTED                 Home UI integration, expired-artifact recovery, and T-1 acceptance
V-1  COMPLETED / ACCEPTED                  Character display extraction and deterministic state presentation
  V-1a  COMPLETED / ACCEPTED                     Current behavior inventory and implementation contract
  V-1b  COMPLETED / ACCEPTED                       Deterministic presentation model and standalone widget
  V-1c  COMPLETED / ACCEPTED                     HomeScreen extraction and integration
R-1  CURRENT / NOT_COMPLETED                  v2.1.0 aggregate readiness, smartphone Web evidence,
                              fixed-ZIP verification, approval, and release preparation
  R-1a  COMPLETED / ACCEPTED                     Release/readiness current behavior inventory
  R-1b  COMPLETED / ACCEPTED                     Aggregate source-tree/test gate and v2.1.0 candidate metadata
  R-1c  COMPLETED / ACCEPTED                     Final smartphone Web evidence aggregate
  R-1d  COMPLETED / ACCEPTED                     One-time fixed ZIP build and same-artifact verification
  R-1e  CURRENT / NOT_COMPLETED                    Explicit approval, publication, and post-publication verification
         NOT_STARTED
```

W-1 through W-5, C-1, T-1, V-1, and R-1a through R-1d are completed and accepted. The final exact-candidate PC/smartphone Web aggregate and the unchanged fixed-ZIP tuple are accepted. R-1e is current/not completed and not started.

---

# W-1 — Fitbit current behavior inventory and contract

Status: COMPLETED / ACCEPTED

Commit title:

```text
docs/test: establish v2.1.0 Fitbit current behavior inventory
```

## Purpose

```text
- Read and record the existing Fitbit backend and Flutter implementation before changes.
- Establish this checklist as the authoritative v2.1.0 source of truth through W-1 acceptance.
- Preserve the accepted v2.0.x behavior and publication records.
- Separate source availability, local configuration, local token-like data,
  authorization readiness, mock-safe verification, and configured real success.
- Assign later implementation responsibilities without advancing their completion state.
```

## Inspected current implementation

The detailed inventory is `docs/v210_fitbit_current_behavior_inventory.md` and covers:

```text
backend/app/config.py
backend/app/api/fitbit.py
backend/app/api/sleep.py
backend/app/models/fitbit.py
backend/app/models/sleep.py
backend/app/services/fitbit_service.py
backend/app/services/fitbit_oauth_state_store.py
backend/app/services/fitbit_token_exchange.py
backend/app/services/fitbit_token_store.py
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_http_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/factory.py
backend/app/services/sleep_providers/fitbit.py
backend/tests/test_fitbit_current_state_contract.py
app/lib/models/fitbit_status.dart
app/lib/models/fitbit_connect_response.dart
app/lib/models/sleep_summary.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
app/test/fitbit_current_state_contract_test.dart
```

## W-1 change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_current_behavior_inventory.md
scripts/check_v210_fitbit_current_behavior_inventory.py
```

## Explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
backend/.env.example
backend/env_profiles/**
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
docs/DRC_v20x_maintenance_checklist.md
docs/v20x_patch_release.md
docs/v201_patch_release_record.md
release_notes/v2.0.1.md
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
scripts/check_v20x_patch_release.py
release ZIPs, tags, GitHub Releases, and publication records
```

## Current contract fixed by W-1

```text
- SLEEP_PROVIDER=mock is the credential-free default.
- wearable_stub is the recommended deterministic wearable-shaped sample.
- fitbit_stub remains a deprecated compatibility alias.
- fitbit remains the legacy migration/reference real-code path until later work accepts it.
- /fitbit/status connected=true means configured client fields and local access/refresh
  token-like fields were detected; it is not live token validation.
- /fitbit/connect ready=true means a connect URL and OAuth state were prepared;
  it is not connection, permission, or sleep-data success.
- /fitbit/callback validates state and can reach guarded token exchange, but no
  configured real Fitbit acceptance is inherited from source presence.
- FITBIT_ENABLE_REAL_TOKEN_EXCHANGE is an explicit guard for the real token path.
- token refresh and sleep-by-date request code exist, but live success is W-5 work.
- raw Fitbit responses remain internal to services and are not returned by /sleep/summary.
- the normalizer can retain start/end values, while the legacy Fitbit SleepSummary
  mapping currently omits sleep_start, sleep_end, quality_label, confidence, and
  is_real_data=true.
- Flutter preserves conservative local-token and authorization-ready wording.
- Flutter has no user-facing sleep-provider selector in the accepted W-1 baseline.
```

## Accepted completion record

W-1 was accepted on 2026-07-23 after all of the following passed:

```text
- This checklist and the detailed inventory agreed with the inspected code.
- Before acceptance synchronization, README, roadmap, tasklist, and scripts README
  identified W-1 as CURRENT / NOT_COMPLETED.
- W-2 through W-5, C-1, T-1, V-1, and R-1 remained PLANNED during W-1 execution.
- The W-1 source-tree check confirmed the inspected runtime, Flutter, and existing-test
  files matched the pre-change normalized-hash baseline.
- The W-1 source-tree check confirmed v2.0.0/v2.0.1 publication records, release
  builders, and patch-release validator matched their pre-change normalized hashes.
- No credential, token, authorization code, OAuth state value, raw Fitbit payload,
  private path, LAN address, raw screenshot, or exact private sleep value was added.
- python -m compileall -q backend scripts passed.
- python scripts/check_v210_fitbit_current_behavior_inventory.py passed.
- python -m pytest -q backend/tests passed: 38 tests.
- flutter test passed from app/: 43 tests.
- The operator reviewed the seven-file change and approved W-1 acceptance synchronization.
```

W-1 changed no tests, so no test-count increase was required. The accepted baseline remains 38 backend tests and 43 Flutter tests. W-1 performed no configured real Fitbit execution and did not satisfy any W-2 through R-1 completion requirement.

## Mock-safe boundary

W-1 source-tree verification may:

```text
- read Public source and documentation files;
- compare normalized file hashes;
- inspect stable source markers;
- run compileall;
- run the existing credential-free backend and Flutter test suites.
```

W-1 source-tree verification must not:

```text
- load backend/.env or backend/local_data credentials;
- create or modify backend/local_data;
- call Fitbit, Google Health, Framework, LLM, TTS, STT, or motion providers;
- open an OAuth browser;
- exchange or refresh a real token;
- retrieve real sleep data;
- build or inspect a new release ZIP;
- create or change a tag or GitHub Release.
```

## Real operator boundary

Configured real Fitbit verification is deferred to W-5 and must remain explicit opt-in. W-5 will require a separately accepted operator contract for:

```text
- real OAuth authorization and callback;
- real token exchange and refresh;
- intended scope and permission confirmation;
- real Fitbit sleep retrieval and normalized SleepSummary confirmation;
- selected provider/source presentation in the actual Flutter Web UI;
- reconnect and permission-failure behavior;
- public-safe acceptance markers without private evidence in the repository.
```

Source-tree success, fake HTTP responses, token-file shape checks, or an authorization URL do not satisfy W-5.

---

# W-2 — Fitbit token/status/reconnect hardening

Status: COMPLETED / ACCEPTED

Commit title:

```text
feat/test: harden Fitbit token status and reconnect states
```

Detailed contract: `docs/v210_fitbit_token_status_reconnect.md`

## Purpose

```text
- Add provider-neutral connection_state and verified fields without removing
  connected/provider/message compatibility fields.
- Classify local token presence, expiry, refresh need, reconnect need, permission
  denial, malformed storage, and authorization readiness without external calls.
- Consume matching OAuth state once before token exchange and reject replay.
- Add deterministic temporary-store and fake-HTTP regression coverage.
- Keep live OAuth, live token validity, permission, sleep retrieval, and UI evidence
  deferred to W-5.
```

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/app/models/fitbit.py
backend/app/services/fitbit_service.py
backend/app/services/fitbit_token_store.py
backend/app/services/fitbit_oauth_state_store.py
backend/app/services/fitbit_token_exchange.py
backend/tests/test_fitbit_token_status_reconnect.py
app/lib/models/fitbit_status.dart
app/lib/models/fitbit_connect_response.dart
app/test/fitbit_token_status_reconnect_test.dart
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_token_status_reconnect.md
scripts/check_v210_fitbit_current_behavior_inventory.py
scripts/check_v210_fitbit_token_status_reconnect.py
```

## Explicit non-change surface

```text
Fitbit API routes and SleepSummary models
Fitbit sleep API/error/normalization/provider implementation
Flutter home screen, API client, provider selection, and sleep summary model
existing M-7 backend and Flutter regression tests
version metadata
v2.0.0/v2.0.1 release records, builders, tags, GitHub Releases, and fixed ZIPs
```

## Accepted implementation state

```text
- W-2 implementation and focused mock-safe tests are accepted.
- Normal /fitbit/status performs no HTTP or token refresh.
- connected remains a backward-compatible legacy bool; verified remains false.
- connected connection_state is reserved for W-5 and is not emitted by W-2 status.
- W-3 is CURRENT / NOT_COMPLETED; W-4 through R-1 remain PLANNED.
```

## Completion conditions

```text
- old and new Fitbit response shapes remain parseable;
- token values, authorization codes, OAuth state values, and Authorization headers
  are absent from app-facing responses and logs;
- expired/near-expiry/missing-expiry token states fail closed;
- matching OAuth state is one-time and replay is rejected;
- access_denied is distinguishable from malformed/error state;
- fake refresh success and failure pass without network access;
- compileall, W-1/W-2 checks, v2.0.x guards, full backend pytest, and Flutter test pass;
- W-3 through R-1 remain incomplete;
- operator diff review and explicit approval are received.
```

Accepted verification on 2026-07-23:

```text
compileall: passed
W-1/W-2 source-tree checks: passed
v2.0.x compatibility and historical guards: passed
backend pytest: 57 passed
Flutter test: 50 passed
diff review and operator approval: passed
real operator execution: false
release records changed: false
```

## Mock-safe / real operator boundary

W-2 may use temporary token/state files, fixed time, fake HTTP responses, public-safe
placeholder strings, source-tree checks, backend pytest, and Flutter tests.

W-2 does not open OAuth, exchange or refresh real tokens, call Fitbit sleep APIs,
verify permission/scope, retrieve real sleep values, or collect smartphone Web evidence.
Configured real acceptance remains W-5.

---

# W-3 — Fitbit real sleep normalization and API regression tests

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

Commit title candidate:

```text
fix/test: harden Fitbit sleep normalization and API states
```

Implemented boundary:

```text
- Classify 401, permission, scope, rate-limit, provider-outage, network,
  invalid-response, and generic HTTP failures through allow-listed codes.
- Keep provider error messages, raw payloads, tokens, and Authorization headers
  outside app-facing responses and exception text.
- Require a positive usable sleep duration before normalization succeeds.
- Prefer the main sleep entry and retain summary.totalMinutesAsleep fallback.
- Map sleep_start, sleep_end, quality_label, confidence, is_real_data, and
  unavailable_reason into SleepSummary.
- Add deterministic fake-HTTP, synthetic-normalization, provider, and API tests.
- Keep configured real Fitbit execution and smartphone Web acceptance in W-5.
```

Changed runtime and test files:

```text
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/fitbit.py
backend/tests/test_fitbit_real_sleep_normalization.py
```

Changed contract and verification files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_real_sleep_normalization.md
scripts/check_v210_fitbit_current_behavior_inventory.py
scripts/check_v210_fitbit_real_sleep_normalization.py
```

Explicitly unchanged:

```text
backend/app/api/fitbit.py
backend/app/api/sleep.py
backend/app/models/fitbit.py
backend/app/models/sleep.py
backend/app/config.py
backend/app/services/fitbit_service.py
backend/app/services/fitbit_token_store.py
backend/app/services/fitbit_oauth_state_store.py
backend/app/services/fitbit_token_exchange.py
backend/app/services/sleep_providers/factory.py
backend/tests/test_fitbit_current_state_contract.py
backend/tests/test_fitbit_token_status_reconnect.py
app/lib/**
app/test/**
app/pubspec.yaml
version metadata
v2.0.0 / v2.0.1 tags, Releases, fixed ZIPs, and publication records
```

Completion gate:

```text
- compileall passes;
- W-1, W-2, and W-3 source-tree checks pass;
- v2.0.x Fitbit and maintenance guards pass;
- full backend pytest passes;
- full Flutter test passes;
- no private Fitbit values or raw payload fixture is committed;
- diff review passes;
- operator approval is received.
```

The detailed contract is `docs/v210_fitbit_real_sleep_normalization.md`.

Acceptance result:

```text
- compileall passed;
- W-1, W-2, and W-3 source-tree checks passed;
- v2.0.x Fitbit and maintenance guards passed;
- full backend pytest passed: 84 tests;
- full Flutter test passed: 50 tests;
- no private Fitbit values or raw payload fixture was committed;
- diff review passed;
- operator approval was received;
- real Fitbit operator execution was not performed;
- v2.0.0 / v2.0.1 publication records remained unchanged.
```

W-3 was completed and accepted on 2026-07-23. This acceptance validates the mock-safe Fitbit sleep normalization/API contract; configured real Fitbit acceptance remains W-5.

---

# W-4 — Sleep-provider selection and source-label UI

Status: COMPLETED / ACCEPTED

## W-4 implementation split

```text
W-4a  COMPLETED / ACCEPTED   Read-only sleep-provider selection status contract
W-4b  COMPLETED / ACCEPTED   Flutter provider/source-label UI and simplified
                                Google Health user UX with retained diagnostics
```

W-4a state: COMPLETED / ACCEPTED
W-4b state: COMPLETED / ACCEPTED

## W-4a purpose

```text
- Expose the backend-owned SLEEP_PROVIDER selection through a read-only API.
- Separate configured provider metadata from SleepSummary.source and real/demo state.
- Keep provider credentials, OAuth, token refresh, and sleep retrieval outside the route.
- Preserve the accepted W-3 Fitbit API, normalization, and SleepSummary contract.
- Prepare the later Flutter UI without completing W-4 or W-5.
```

Detailed contract: `docs/v210_sleep_provider_selection_source_labels.md`

## W-4a change surface

```text
backend/app/main.py
backend/app/api/sleep_provider_selection.py
backend/app/models/sleep_provider_selection.py
backend/app/services/sleep_provider_selection_service.py
backend/tests/test_sleep_provider_selection_contract.py
docs/v210_sleep_provider_selection_source_labels.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_sleep_provider_selection_source_labels.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

## W-4a explicit non-change surface

```text
backend/app/api/sleep.py
backend/app/models/sleep.py
backend/app/services/sleep_providers/factory.py
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/fitbit.py
backend/tests/test_fitbit_real_sleep_normalization.py
app/lib/**
app/test/**
app/pubspec.yaml
Fitbit and Google Health OAuth/token/runtime services
version metadata
v2.0.0 / v2.0.1 release records, tags, GitHub Releases, and fixed ZIPs
```

## W-4a completion conditions

```text
- GET /sleep/providers reports configured provider metadata without provider execution.
- mock, wearable_stub, google_health, fitbit_stub, and fitbit remain distinct.
- fitbit_stub remains a deprecated alias of wearable_stub.
- fitbit remains legacy_real_provider and requires W-5 real operator verification.
- unknown configuration is reported conservatively as unsupported.
- existing /sleep/summary and accepted W-3 runtime files remain unchanged.
- compileall, W-1/W-2/W-3 checks, W-4a check, v2.0.x guards, full backend
  pytest, full Flutter test, diff review, and operator approval pass.
```

## W-4a accepted verification

```text
implementation commit: 1619b0b
compileall: passed
W-1/W-2/W-3/W-4a checks: passed
v2.0.x compatibility and maintenance guards: passed
focused backend pytest: 8 passed
full backend pytest: 92 passed
Flutter test: 50 passed
diff review: passed
operator approval: passed
real operator execution: false
release records changed: false
```

W-4a was completed and accepted on 2026-07-23. At W-4a acceptance time,
W-4 remained CURRENT / NOT_COMPLETED and W-4b became the next small commit.

## W-4b purpose

```text
- Consume accepted GET /sleep/providers metadata in Flutter.
- Show configured provider separately from SleepSummary.source and data kind.
- Keep mock / wearable samples credential-free and avoid irrelevant Fitbit status calls.
- Simplify the normal Google Health user surface.
- Retain Google Health state details, actions, diagnostics, preflight, and self-check
  under Advanced Demo Tools.
- Keep configured real Fitbit acceptance and smartphone Web evidence in W-5.
```

Detailed contract: `docs/v210_flutter_sleep_provider_source_ui.md`

## W-4b change surface

```text
app/lib/models/sleep_provider_selection.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
app/test/sleep_provider_selection_test.dart
app/test/widget_test.dart
docs/v210_flutter_sleep_provider_source_ui.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_sleep_provider_selection_source_labels.py
scripts/check_v210_flutter_sleep_provider_source_ui.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

## W-4b explicit non-change surface

```text
backend/app/**
backend/tests/**
app/pubspec.yaml
Fitbit and Google Health OAuth/token/sleep runtime
post-advice chat, voice, motion, and character runtime
version metadata
v2.0.0 / v2.0.1 release records, tags, GitHub Releases, and fixed ZIPs
```

## W-4b implementation boundary

```text
- Add Flutter models for the read-only provider metadata response.
- Load /sleep/providers without making the daily loop depend on provider metadata success.
- Query /fitbit/status only when configured_provider=fitbit.
- Add a normal Sleep Data Source card with configured provider, actual source,
  data kind, availability, and provider-specific concise guidance.
- Keep the normal Google Health card free of state-stage, raw action groups,
  developer fields, diagnostics, preflight, and self-check details.
- Keep the detailed Google Health connection/operator surfaces below Advanced Demo Tools.
- Keep Fitbit UI wording explicitly pending W-5 real operator acceptance.
```

## W-4b mock-safe verification boundary

```text
- deterministic model parsing;
- fake BackendApiClient widget tests for mock, Google Health, and Fitbit states;
- no external HTTP, OAuth browser, real token, real provider API, or private evidence;
- full backend pytest remains unchanged and must pass;
- full Flutter test is required for acceptance.
```

## W-4b accepted verification

```text
implementation commit: 1fbea58
compileall: passed
W-1/W-2/W-3/W-4a/W-4b checks: passed
v2.0.x compatibility and maintenance guards: passed
focused Flutter provider model tests: 4 passed
focused Flutter widget tests: 35 passed
full backend pytest: 92 passed
full Flutter test: 57 passed
diff review: passed
operator approval: passed
real operator execution: false
release records changed: false
```

W-4b and parent phase W-4 were completed and accepted on 2026-07-23. This
acceptance covers the mock-safe provider/source-label UI and Google Health UX
boundary only. Real Fitbit OAuth, token/permission validation, live sleep retrieval,
and smartphone Web real-provider evidence remain unperformed W-5 work.

---

# W-5 — Wearable migration correction and configured Google Health verification

Status: COMPLETED / ACCEPTED

## W-5 split

```text
W-5a   COMPLETED / ACCEPTED   Historical Fitbit operator contract and preflight; no real execution
W-5b1  COMPLETED / ACCEPTED   Google Health API migration audit and legacy Fitbit execution retirement
W-5b2  COMPLETED / ACCEPTED   Configured Google Health API operator verification for Fitbit-origin sleep and smartphone Web evidence
```

## W-5a accepted historical record

W-5a was completed and accepted on 2026-07-24 at implementation commit `7f84980`. It established a public-safe preflight and operator boundary but performed no OAuth or provider request. After the official migration direction was rechecked, its legacy real-execution direction was superseded. The accepted history remains; new legacy Fitbit execution is now blocked.

## W-5b1 purpose

```text
- Record the official Google Health API migration direction.
- Audit the existing google_health v4 endpoint, scope, filter, and sleep schema.
- Add mock-safe Google Health v4 contract tests.
- Fix Flutter parsing from available_providers to the backend provider_options field.
- Relabel fitbit as a legacy migration reference and remove normal-user legacy OAuth actions.
- Hard-stop the legacy Fitbit runner and execution smoke.
- Keep real Google Health OAuth/API and smartphone Web evidence in W-5b2.
```

Detailed contract: `docs/v210_google_health_migration_audit.md`

## W-5b1 accepted verification

```text
implementation commit: 081cfdd
compileall: passed
W-1 through W-5b1 checks: passed
v2.0.x compatibility and maintenance guards: passed
Google Health v4 focused tests: 8 passed
provider selection + migration focused tests: 16 passed
full backend pytest: 100 passed
full Flutter test: 57 passed
diff review: passed
operator approval: passed
legacy Fitbit network request: false
real Google Health operator execution: false
release records changed: false
```

W-5b1 was completed and accepted on 2026-07-24. This acceptance covers the mock-safe migration correction, legacy Fitbit execution retirement, Google Health v4 contract guard, and Flutter provider parsing correction only. W-5b2 owns configured Google OAuth, real Google Health API sleep retrieval, Fitbit-origin data confirmation when available, and smartphone Web evidence.

## W-5b1 change surface

```text
backend/app/services/sleep_provider_selection_service.py
backend/env_profiles/fitbit_real_operator.env.example
backend/scripts/run_fitbit_real_operator.ps1
backend/tests/test_sleep_provider_selection_contract.py
backend/tests/test_google_health_v4_migration_contract.py
app/lib/models/sleep_provider_selection.dart
app/lib/screens/home_screen.dart
app/test/sleep_provider_selection_test.dart
app/test/widget_test.dart
docs/v210_google_health_migration_audit.md
scripts/check_v210_google_health_migration_audit.py
scripts/smoke_v210_fitbit_real_operator_execution.py
README.md
roadmap.md
tasklist.md
scripts/README.md
existing v2.1.0 check scripts
```

## W-5b1 mock-safe boundary

```text
- no OAuth browser, credential read, token exchange/refresh, or provider network request;
- synthetic public-safe Google Health v4 payloads only;
- legacy Fitbit execution entry points must return non-zero before network;
- no exact private sleep values, raw payloads, private paths, or screenshots;
- W-5b2 and C-1 onward remain not completed.
```

## W-5b2 accepted configured execution

Status: COMPLETED / ACCEPTED

Detailed record: `docs/v210_google_health_real_operator_verification.md`

```text
- ignored operator env, credentials, and token files were present and Git-ignored;
- public-safe env preflight, actual-run checkpoint, and launcher ValidateOnly passed;
- the stored token required refresh and the guarded refresh path succeeded;
- post-refresh preflight reported ready_for_real_api;
- the explicit real Google Health v4 request returned HTTP 200;
- backend /sleep/summary returned available real Google Health data with positive duration;
- PC and smartphone Flutter Web both showed Google Health / 実データ / 取得済み;
- normalized SleepSummary was visible on both form factors;
- reviewed screenshots remain outside Git and exact private sleep values are not recorded;
- current UI/API source is Google Health; the operator confirmed the displayed sleep was measured by a Fitbit Versa 2;
- no device identifier, exact private sleep value, raw payload, or screenshot is recorded;
- W-5b2 and parent W-5 are COMPLETED / ACCEPTED.
```

Public-safe source-tree guard:

```powershell
python scripts\check_v210_google_health_real_operator_verification.py
```

Accepted verification:

```text
execution-record commit: ed50d9e
operator env / ValidateOnly: passed
token refresh: succeeded
real Google Health HTTP status: 200
normalized backend summary: confirmed real data
PC Web display: passed
smartphone Web display: passed
Fitbit-origin device model: operator-confirmed Fitbit Versa 2
W-1 through W-5b2 checks: passed
v2.0.x guards: passed
backend pytest: 100 passed
Flutter test: 57 passed
diff review / operator approval: passed
raw screenshot committed: false
release records changed: false
```

W-5b2 and parent W-5 were completed and accepted on 2026-07-24. C-1 is now CURRENT / NOT_COMPLETED. T-1, V-1, and R-1 remain PLANNED.

---

# C-1 — Post-advice chat lifecycle and UI-state hardening

Status: COMPLETED / ACCEPTED

Small-commit split:

```text
C-1a  COMPLETED / ACCEPTED     Current behavior inventory and implementation contract
C-1b  COMPLETED / ACCEPTED     Backend lifecycle outcomes, bounded turns, and mock-safe tests
C-1c  COMPLETED / ACCEPTED     Flutter lifecycle state, recovery UI, and aggregate C-1 acceptance
```

Parent boundary:

```text
- Preserve the accepted 30-minute idle TTL, 100-session capacity, and LRU behavior
  unless a later accepted contract intentionally changes them.
- Add bounded chat turns and clearer expired, unavailable, blocked, fallback,
  active, sending, skipped, and restart states.
- Separate normal-user copy from optional developer/operator diagnostics.
- Reuse released AI Character Framework public text-session APIs only.
- Keep T-1, V-1, and R-1 planned until separately implemented and accepted.
```

## C-1a — Current behavior inventory and implementation contract

Status: COMPLETED / ACCEPTED

Detailed inventory: `docs/v210_post_advice_chat_current_behavior_inventory.md`

Purpose:

```text
- inspect the accepted Backend chat API/model/service and Framework adapter boundary;
- inspect Flutter chat models, BackendApiClient, HomeScreen state, and widget tests;
- record the lifecycle and recovery gaps before runtime changes;
- pin inspected runtime/test files using normalized source hashes;
- define the C-1b/C-1c small-commit responsibilities.
```

C-1a change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_post_advice_chat_current_behavior_inventory.md
scripts/check_v210_post_advice_chat_current_behavior_inventory.py
existing v2.1.0 check scripts current-state synchronization
```

Explicit non-change surface:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
backend/.env.example
released v2.0.0/v2.0.1 records, ZIPs, tags, and GitHub Releases
```

C-1a fixed findings:

```text
- accepted defaults are 1800-second idle TTL and 100 sessions;
- successful get/message refreshes recency and capacity eviction is LRU;
- sessions have no bounded-turn limit;
- expired, evicted, and unknown sessions share one HTTP 404 detail;
- Framework outcome status is represented indirectly through source.mode/reply copy;
- Flutter uses booleans plus a generic error string rather than a structured lifecycle state;
- message failure leaves a stale local session, so direct restart is not available;
- normal-user copy and operator diagnostics are mixed in the chat card.
```

Mock-safe gate:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_post_advice_chat_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

C-1a acceptance record:

```text
- implementation commit: a4263ca
- compileall / C-1a source-tree check: passed
- W-1 through W-5 checks / v2.0.x guards: passed
- backend pytest: 100 passed
- Flutter test: 57 passed
- diff review / operator approval: passed
- Backend runtime changed: false
- Flutter runtime changed: false
- existing tests changed: false
- real Framework/LLM execution: false
- release records changed: false
```

C-1a was completed and accepted on 2026-07-24. C-1b, C-1c, and parent C-1 were subsequently completed and accepted. T-1 is CURRENT / NOT_COMPLETED.
C-1a performed no real Framework/LLM execution by itself.

## C-1b — Backend lifecycle outcomes, bounded turns, and mock-safe tests

Status: COMPLETED / ACCEPTED

Detailed contract: `docs/v210_post_advice_chat_backend_lifecycle.md`

Implementation boundary:

```text
- preserve POST_ADVICE_CHAT_TTL_SECONDS=1800;
- preserve POST_ADVICE_CHAT_MAX_SESSIONS=100 and LRU eviction;
- add POST_ADVICE_CHAT_MAX_TURNS=8;
- add ChatLifecycle, ChatOutcome, and ChatSessionProblem;
- distinguish session_expired, session_evicted, and session_not_found;
- return structured HTTP 409 turn_limit_reached after the final allowed response;
- keep terminal-reason metadata bounded without retaining removed message bodies;
- map mock/configured/fallback/unavailable/blocked/skipped outcomes;
- use deterministic clocks and fake adapters only in normal tests;
- leave all Flutter runtime/tests unchanged for C-1c.
```

C-1b change surface:

```text
backend/app/config.py
backend/app/models/chat.py
backend/app/services/post_advice_chat_service.py
backend/app/api/chat.py
backend/.env.example
backend/env_profiles/mock_safe.env
backend/tests/test_temporary_lifecycle_config.py
backend/tests/test_post_advice_chat_lifecycle.py
backend/tests/test_post_advice_chat_outcomes.py
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_post_advice_chat_current_behavior_inventory.md
docs/v210_post_advice_chat_backend_lifecycle.md
scripts/check_v210_post_advice_chat_current_behavior_inventory.py
scripts/check_v210_post_advice_chat_backend_lifecycle.py
```

Explicit non-change surface:

```text
backend/app/services/framework_text_chat_adapter.py
backend/app/services/framework_text_chat_drc_live_reply.py
app/lib/**
app/test/**
T-1 / V-1 / R-1 runtime
released v2.0.0/v2.0.1 records, ZIPs, tags, and GitHub Releases
```

C-1b acceptance record:

```text
- implementation commit: 3055995
- python -m compileall -q backend scripts: passed
- C-1a / C-1b source-tree checks: passed
- W-1 through W-5 checks / v2.0.x guards: passed
- focused C-1b Backend tests: 17 passed
- backend pytest: 110 passed
- Flutter test: 57 passed
- diff review / operator approval: passed
- Backend runtime changed: true
- Backend tests changed: true
- Flutter runtime changed: false
- Flutter tests changed: false
- real Framework/LLM execution: false
- release records changed: false
```

C-1b was completed and accepted on 2026-07-24. C-1c and parent C-1 were subsequently completed and accepted; T-1 is CURRENT / NOT_COMPLETED.


## C-1c — Flutter lifecycle state, recovery UI, and aggregate C-1 acceptance

Status: COMPLETED / ACCEPTED

Detailed contract: `docs/v210_post_advice_chat_flutter_lifecycle.md`

Implementation boundary:

```text
- add Flutter ChatLifecycle, ChatOutcome, ChatSessionProblem, and typed API exception models;
- parse the accepted C-1b lifecycle/outcome/problem payloads while keeping old payloads readable;
- show active/turn-limit and mock/configured/fallback/unavailable/blocked/skipped user states;
- show turn count / limit and disable message sending when the lifecycle or outcome is terminal;
- clear stale local sessions after structured expired/evicted/not-found/turn-limit failures;
- offer a direct new-conversation action after restartable terminal states;
- keep technical source/session/code metadata in a separate developer-details section;
- use fake BackendApiClient implementations only in normal Flutter tests;
- leave Backend runtime/tests, T-1, V-1, R-1, and release records unchanged.
```

C-1c change surface:

```text
app/lib/models/chat.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
app/test/post_advice_chat_lifecycle_test.dart
app/test/post_advice_chat_lifecycle_widget_test.dart
docs/v210_post_advice_chat_flutter_lifecycle.md
scripts/check_v210_post_advice_chat_flutter_lifecycle.py
scripts/check_v210_post_advice_chat_current_behavior_inventory.py
scripts/check_v210_post_advice_chat_backend_lifecycle.py
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
```

Explicit non-change surface:

```text
backend/app/**
backend/tests/**
backend/.env.example
backend/env_profiles/**
AI Character Framework checkout/provider/runtime
T-1 / V-1 / R-1 runtime
released v2.0.0/v2.0.1 records, ZIPs, tags, and GitHub Releases
```

Acceptance record:

```text
- implementation commit: c856374
- python -m compileall -q backend scripts: passed
- C-1a / C-1b / C-1c source-tree checks: passed
- W-1 through W-5 checks / v2.0.x guards: passed
- focused C-1c Flutter tests: 7 passed
- backend pytest: 110 passed
- Flutter test: 64 passed
- diff review / operator approval: passed
- Backend runtime changed by C-1c: false
- Flutter runtime changed by C-1c: true
- real Framework/LLM execution: false
- release records changed: false
```

C-1c and parent C-1 were completed and accepted on 2026-07-24. T-1 is CURRENT / NOT_COMPLETED; V-1 and R-1 remain PLANNED.

---

# T-1 — Flutter in-app TTS player and artifact-expiry handling

Status: COMPLETED / ACCEPTED

Small-commit split:

```text
T-1a  COMPLETED / ACCEPTED     Current TTS/audio handoff inventory and implementation contract
T-1b  COMPLETED / ACCEPTED  Flutter in-app player abstraction, states, and mock-safe tests
T-1c  COMPLETED / ACCEPTED                 Home UI integration, expired-artifact recovery, and T-1 acceptance
```

Parent boundary:

```text
- Add in-app play, stop, replay, loading, completion, failure, and expired states.
- Preserve DRC-owned opaque MP3 URLs and accepted artifact retention/cleanup rules.
- Do not expose Framework-managed paths or provider payloads.
- Keep V-1 and R-1 planned until separately implemented and accepted.
```

## T-1a — Current TTS/audio handoff inventory and implementation contract

Status: COMPLETED / ACCEPTED

Detailed inventory: `docs/v210_tts_player_current_behavior_inventory.md`

Purpose:

```text
- inspect the accepted Backend artifact store/audio route and Flutter voice-output flow;
- record the current external URL launch behavior and missing in-app player state;
- preserve the accepted 86400-second TTL, 100-artifact cap, opaque MP3 URL, no-store, and nosniff boundaries;
- pin the pre-T-1 runtime/test files using normalized hashes;
- assign T-1b/T-1c responsibilities without changing runtime, dependencies, or tests.
```

T-1a change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_tts_player_current_behavior_inventory.md
scripts/check_v210_tts_player_current_behavior_inventory.py
existing v2.1.0 check scripts current-state synchronization
```

Explicit non-change surface:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
AI Character Framework checkout/provider/runtime
V-1 / R-1 runtime
released v2.0.0/v2.0.1 records, ZIPs, tags, and GitHub Releases
```

T-1a completion conditions:

```text
- inventory/check agree with the accepted source tree;
- pre-T-1 runtime/test hashes remain unchanged;
- compileall, all accepted v2.1.0 checks, v2.0.x guards, backend pytest, and Flutter test pass;
- no real TTS request, audio download/playback, browser launch, private artifact read, or release work occurs;
- diff review and operator approval pass.
```

T-1a acceptance record:

```text
- implementation commit: 0b06378
- python -m compileall -q backend scripts: passed
- W-1 through W-5, C-1, and T-1a source-tree checks: passed
- v2.0.x compatibility and maintenance guards: passed
- backend pytest: 110 passed
- Flutter test: 64 passed
- diff review / operator approval: passed
- Backend runtime changed: false
- Flutter runtime changed: false
- dependencies changed: false
- existing tests changed: false
- real Framework/TTS execution: false
- release records changed: false
```

T-1a was completed and accepted on 2026-07-24. T-1b was subsequently completed and accepted at implementation commit `161e624`. T-1c and parent T-1 are now COMPLETED / ACCEPTED; V-1 is CURRENT / NOT_COMPLETED.

## T-1b — Flutter player abstraction, states, and mock-safe tests

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

Detailed contract: `docs/v210_tts_player_controller.md`

Implementation boundary:

```text
- add an app-owned VoiceOutputAudioEngine interface;
- add VoiceOutputPlaybackPhase and immutable VoiceOutputPlaybackState;
- add VoiceOutputAudioPlayerController with play, stop, replay, reset, expiry, and disposal;
- accept only http/https sources and keep raw URIs out of user-facing state;
- invalidate stale asynchronous load/play completions after reset/replacement/disposal;
- add fake-engine focused tests for lifecycle, failure, expiry, and disposal;
- add no concrete audio plugin and do not integrate HomeScreen in T-1b;
- leave Backend runtime/tests, V-1, R-1, and release records unchanged.
```

T-1b change surface:

```text
app/lib/services/voice_output_audio_player.dart
app/test/voice_output_audio_player_test.dart
docs/v210_tts_player_controller.md
docs/v210_tts_player_current_behavior_inventory.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_tts_player_controller.py
scripts/check_v210_tts_player_current_behavior_inventory.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

Explicit non-change surface:

```text
backend/app/**
backend/tests/**
app/lib/screens/home_screen.dart
app/lib/models/voice_output_demo.dart
app/lib/services/backend_api_client.dart
app/test/widget_test.dart
app/pubspec.yaml
app/pubspec.lock
AI Character Framework/provider runtime
private audio and operator evidence
V-1 / R-1 runtime
released v2.0.0/v2.0.1 records, ZIPs, tags, and GitHub Releases
```

T-1b implementation verification target:

```text
- python -m compileall -q backend scripts;
- T-1a and T-1b source-tree checks;
- focused app/test/voice_output_audio_player_test.dart;
- full backend pytest and full Flutter test;
- no real audio download/decode/playback or Framework/TTS execution;
- diff review and operator approval before acceptance synchronization.
```

T-1b acceptance record:

```text
- implementation commit: 161e624
- python -m compileall -q backend scripts: passed
- T-1a / T-1b source-tree checks: passed
- all accepted v2.1.0 checks and v2.0.x guards: passed
- focused Flutter player-controller tests: 10 passed
- backend pytest: 110 passed
- Flutter test: 74 passed
- diff review / operator approval / push: passed
- Backend runtime changed: false
- HomeScreen integration changed: false
- dependencies changed: false
- real Framework/TTS execution: false
- release records changed: false
```

T-1b was completed and accepted on 2026-07-24. T-1c and parent T-1 are now COMPLETED / ACCEPTED; V-1 is CURRENT / NOT_COMPLETED.

## T-1c — Home UI integration, expired-artifact recovery, and T-1 acceptance

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

Detailed contract: `docs/v210_tts_player_home_integration.md`

Implementation boundary:

```text
- add audioplayers ^6.7.1 behind the accepted VoiceOutputAudioEngine interface;
- use HTTP MP3 loading with 404/410 -> expired classification;
- integrate one controller into HomeScreen lifetime and dispose it safely;
- replace external URL launch with in-app play, stop, replay, and regenerate controls;
- keep raw URLs and technical codes outside normal user copy;
- add fake-driver engine tests and fake-engine widget tests;
- update Windows CMake policy baseline for the selected plugin and Visual Studio 2026;
- leave Backend runtime/tests, Framework/TTS providers, V-1, R-1, and release records unchanged.
```

T-1c change surface:

```text
app/pubspec.yaml
app/pubspec.lock
app/android/app/src/main/java/io/flutter/plugins/GeneratedPluginRegistrant.java
app/ios/Runner/GeneratedPluginRegistrant.m
app/linux/flutter/generated_plugin_registrant.cc
app/linux/flutter/generated_plugins.cmake
app/macos/Flutter/GeneratedPluginRegistrant.swift
app/windows/flutter/generated_plugin_registrant.cc
app/windows/flutter/generated_plugins.cmake
app/windows/CMakeLists.txt
app/lib/services/audioplayers_voice_output_audio_engine.dart
app/lib/screens/home_screen.dart
app/test/audioplayers_voice_output_audio_engine_test.dart
app/test/voice_output_audio_player_widget_test.dart
app/test/widget_test.dart
docs/v210_tts_player_home_integration.md
docs/v210_tts_player_controller.md
docs/v210_tts_player_current_behavior_inventory.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_tts_player_home_integration.py
scripts/check_v210_tts_player_controller.py
scripts/check_v210_tts_player_current_behavior_inventory.py
README.md
roadmap.md
tasklist.md
scripts/README.md
existing v2.1.0 checks that previously pinned app/pubspec.yaml
```

Implementation verification target:

```text
- flutter pub get;
- compileall and all v2.1.0 source-tree checks;
- focused T-1b controller, T-1c engine, and T-1c widget tests;
- full backend pytest, full Flutter test, Flutter Web build, and Windows build;
- no real Framework/TTS execution in normal automated tests;
- diff review, audible PC/smartphone Web review, and operator approval before acceptance synchronization.
```

T-1c acceptance record:

```text
- implementation commit: 4d3d5d5
- desktop plugin registrant follow-up: 9771f76
- python -m compileall -q backend scripts: passed
- T-1a / T-1b / T-1c source-tree checks: passed
- all accepted v2.1.0 checks and v2.0.x guards: passed
- focused Flutter player tests: 20 passed
- backend pytest: 110 passed
- Flutter test: 84 passed
- Flutter Web build: passed
- Flutter Windows build: passed
- PC Web audible playback / stop / replay / completion: passed
- smartphone Web audible playback / stop / replay / completion: passed
- missing-artifact HTTP mapping to expired: passed
- PC and smartphone regenerate recovery: passed
- raw audio URL / private path hidden from normal UI: passed
- real Framework/TTS execution: true
- Backend runtime changed: false
- release records changed: false
- diff review / operator approval: passed
```

T-1c and parent T-1 were completed and accepted on 2026-07-24.
V-1 is COMPLETED / ACCEPTED and R-1 is CURRENT / NOT_COMPLETED (NOT_STARTED).

---

# V-1 — Character display extraction and deterministic states

Status: COMPLETED / ACCEPTED

Implementation split:

```text
V-1a  COMPLETED / ACCEPTED         Current behavior inventory and implementation contract
V-1b  COMPLETED / ACCEPTED         Deterministic presentation model and standalone widget
V-1c  COMPLETED / ACCEPTED       HomeScreen extraction and integration
```

## V-1a — Current behavior inventory and implementation contract

Status: COMPLETED / ACCEPTED

Commit title:

```text
docs/test: establish V-1 character display inventory
```

Purpose:

```text
- Read the current HomeScreen, character models/assets, Motion Demo boundary, and widget tests.
- Record the current mood/advice/loading/speaking/fallback presentation gaps.
- Freeze the static repository-safe asset and pre-V-1 Flutter/test baseline with normalized hashes.
- Separate normal character presentation from Motion Demo simulation/discovery.
- Assign V-1b and V-1c without changing runtime or advancing R-1.
```

Changed files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_character_display_current_behavior_inventory.md
scripts/check_v210_character_display_current_behavior_inventory.py
```

Unchanged boundaries:

```text
app/lib/**
app/test/**
app/pubspec.yaml
app/assets/**
backend/**
release notes / release records / fixed-ZIP builders / tags / GitHub Releases
```

Detailed inventory: `docs/v210_character_display_current_behavior_inventory.md`.

V-1a acceptance record:

```text
- implementation commit: 1602b2f
- python -m compileall -q backend scripts: passed
- V-1a source-tree check: passed
- all check_v210_*.py: passed
- v2.0.x compatibility and maintenance guards: passed
- Backend pytest: 110 passed
- Flutter test: 84 passed
- git diff --check: no real error
- diff review confirmed docs/test-only scope
- operator approval: explicit
- Flutter runtime changed: false
- Backend runtime changed: false
- existing tests changed: false
- dependencies/assets changed: false
- real LLM/TTS/health/motion execution: false
- release records changed: false
```

V-1a, V-1b, V-1c, and parent V-1 were completed and accepted on 2026-07-24. R-1 is CURRENT / NOT_COMPLETED; R-1c is IMPLEMENTED / NOT_ACCEPTED.

## V-1b — Deterministic presentation model and standalone widget

Status: COMPLETED / ACCEPTED

Implemented boundary:

```text
- Add CharacterDisplayPresentation content states mood / advice / fallback.
- Resolve fallback as character unavailable → asset unavailable → framework fallback.
- Resolve normal content as non-empty advice → mood.
- Add activity states idle / loading / speaking with speaking → loading → idle precedence.
- Add CharacterDisplayCard for static image, state chips, copy, and CharacterPreset profile.
- Add nine model tests and four widget tests using only const/fake inputs.
- Keep HomeScreen, Backend, Motion Demo, dependencies, static assets, and release records unchanged.
```

Detailed contract: `docs/v210_character_display_state_contract.md`.

V-1b acceptance record:

```text
- implementation commit: e1f8d6f
- python -m compileall -q backend scripts: passed
- all check_v210_*.py: passed
- v2.0.x compatibility and maintenance guards: passed
- Backend pytest: 110 passed
- focused presentation-model Flutter tests: 9 passed
- focused character-card Flutter tests: 4 passed
- full Flutter test: 97 passed
- git diff --check: no real error
- diff review: passed
- operator approval: explicit
- HomeScreen integration: false
- Backend runtime changed: false
- Motion Demo / dependencies / assets changed: false
- real LLM/TTS/health/motion execution: false
- release records changed: false
```

V-1b and V-1c were completed and accepted on 2026-07-24. Parent V-1 is also COMPLETED / ACCEPTED; R-1 is CURRENT / NOT_COMPLETED; R-1c is IMPLEMENTED / NOT_ACCEPTED.

## V-1c — HomeScreen extraction and integration

Status: COMPLETED / ACCEPTED
Current implementation state: COMPLETED / ACCEPTED

Implemented boundary:

```text
- Connect the accepted standalone widget from HomeScreen.
- Keep HomeScreen data loading, selection callback, advice creation, and TTS control ownership.
- Connect mood/advice/loading/speaking/fallback inputs deterministically.
- Retry the repository-safe fallback asset before a generic missing-image placeholder.
- Add five focused HomeScreen integration tests and one additional fallback-image card test.
- Preserve existing character selection, profile, asset, advice, and TTS regressions.
- Do not claim Live2D/VTS execution or advance R-1.
```

Detailed contract: `docs/v210_character_display_home_integration.md`.

V-1c acceptance record:

```text
- implementation commit: 995145d
- python -m compileall -q backend scripts: passed
- all check_v210_*.py: passed
- v2.0.x compatibility / maintenance guards: passed
- backend pytest: 110 passed
- focused presentation-model Flutter tests: 9 passed
- focused character-card Flutter tests: 5 passed
- focused HomeScreen integration Flutter tests: 5 passed
- full Flutter test: 103 passed
- Flutter Web build: passed
- Flutter Windows build: passed
- existing character-choice regressions: passed
- repository fallback-image retry: passed
- Backend runtime changed: false
- Motion Demo / dependencies / static assets changed: false
- real provider or motion execution: false
- release records changed: false
- diff review / explicit operator approval: passed
```

V-1c and parent V-1 were completed and accepted on 2026-07-24. R-1 is CURRENT / NOT_COMPLETED; R-1c is IMPLEMENTED / NOT_ACCEPTED.

---

# R-1 — v2.1.0 readiness and release preparation

Status: CURRENT / NOT_COMPLETED

Small-commit split:

```text
R-1a  COMPLETED / ACCEPTED   Release/readiness current behavior inventory
R-1b  COMPLETED / ACCEPTED   Aggregate source-tree/test gate and v2.1.0 candidate metadata
R-1c  COMPLETED / ACCEPTED     Final smartphone Web evidence aggregate
R-1d  COMPLETED / ACCEPTED     One-time fixed ZIP build and same-artifact verification
R-1e  CURRENT / NOT_COMPLETED  Explicit approval, publication, and post-publication verification
      NOT_STARTED
```

## R-1a — Release/readiness current behavior inventory

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED

Commit title:

```text
docs/test: establish R-1 release readiness inventory
```

Purpose:

```text
- Inventory the current generic package builder, ZIP hygiene checker, historical v2.0.1 one-time builder/verifier, version metadata, release records, and Git exclusion boundary.
- Record the accepted 110 Backend / 103 Flutter test baseline and prior PC/smartphone Web evidence without importing raw screenshots or private values.
- Identify the missing v2.1.0 aggregate gate, candidate metadata, final smartphone evidence aggregate, fixed-ZIP builder/verifier, release record, and release notes.
- Split later R-1 work into R-1b through R-1e before any version bump, fixed ZIP, tag, or GitHub Release work.
```

Changed files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_readiness_current_behavior_inventory.md
scripts/check_v210_release_readiness_current_behavior_inventory.py
```

Unchanged boundaries:

```text
backend/**
app/**
build_release.bat
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
scripts/check_release_package.py
scripts/check_v20x_maintenance_readiness.py
scripts/check_v20x_patch_release.py
docs/DRC_v200_goal_checklist_small_commit.md
docs/DRC_v20x_maintenance_checklist.md
docs/v20x_patch_release.md
docs/v201_patch_release_record.md
release_notes/v2.0.0.md
release_notes/v2.0.1.md
release/**
annotated tags / GitHub Releases
```

Detailed inventory: `docs/v210_release_readiness_current_behavior_inventory.md`.

R-1a acceptance record:

```text
- accepted on: 2026-07-25
- implementation commit: dbc84db
- python -m compileall -q backend scripts: passed
- scripts/check_v210_release_readiness_current_behavior_inventory.py: passed
- all check_v210_*.py: 18 / 18 passed
- v2.0.x compatibility and maintenance guards: passed
- Backend pytest: 110 passed
- Flutter test: 103 passed
- git diff --check: passed
- diff review: docs/test-only scope confirmed
- release artifact / tag / GitHub Release action: none
- explicit operator approval: received
```

R-1a and R-1b are COMPLETED / ACCEPTED. R-1c is CURRENT / NOT_COMPLETED and IMPLEMENTED / NOT_ACCEPTED. R-1 completion requirements must not be imported into R-1a. R-1a did not update version metadata, implement the aggregate release gate, create final smartphone Web evidence, build a fixed ZIP, create `DRC_v2.1.0`, or publish a GitHub Release.


## R-1b — Aggregate source-tree/test gate and v2.1.0 candidate metadata

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED
Completed small commit: R-1b
Current small commit: R-1e

Implementation commit:

```text
72dd42c  build/test: add R-1b candidate readiness gate
```

Purpose:

```text
- Advance active Backend/Flutter source metadata to 2.1.0 / 2.1.0+3 without claiming publication.
- Add one credential-free aggregate gate over all 18 accepted v2.1.0 child checks and Backend pytest.
- Require the full 103-test Flutter suite plus Web and Windows builds for R-1b acceptance.
- Prepare public-safe v2.1.0 candidate release notes and an intentionally unfilled release record.
- Preserve release/, backend/local_data, generic packaging, and immutable v2.0.0/v2.0.1 records.
```

Changed files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_readiness_current_behavior_inventory.md
docs/v210_release_readiness.md
docs/v210_release_record.md
release_notes/v2.1.0.md
scripts/check_v210_release_readiness_current_behavior_inventory.py
scripts/check_v210_release_readiness.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v210_character_display_current_behavior_inventory.py
scripts/check_v210_character_display_state.py
scripts/check_v210_character_display_home_integration.py
backend/app/version.py
app/pubspec.yaml
```

Required implementation gate:

```powershell
python scripts\check_v210_release_readiness.py --with-flutter --with-builds
git diff --check
```

Acceptance record:

```text
- accepted on: 2026-07-25
- implementation commit: 72dd42c
- all accepted v2.1.0 child checks: 18 / 18 passed
- v2.0.x maintenance/compatibility aggregate: passed
- Backend pytest: 110 passed
- Flutter test: 103 passed
- Flutter Web build: passed
- Flutter Windows build: passed
- backend/local_data and release unchanged: confirmed
- candidate notes/release record private-value review: passed
- fixed ZIP / DRC_v2.1.0 tag / GitHub Release: absent
- git diff --check and diff review: passed
- explicit operator approval: received
```

Deferred boundaries:

```text
R-1c final integrated smartphone Web evidence aggregate
R-1d one-time committed-source fixed ZIP and same-artifact verification
R-1e explicit approval, annotated tag, GitHub Release, and published SHA-256 verification
```

R-1b is COMPLETED / ACCEPTED. R-1c is CURRENT / NOT_COMPLETED and IMPLEMENTED / NOT_ACCEPTED. The accepted R-1b gate remains artifact-free and publication-free; R-1c owns the final integrated smartphone Web evidence aggregate.

## R-1c — Final PC/smartphone Web evidence aggregate

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED
Completed small commit: R-1c
Current small commit: R-1e
Parent R-1: CURRENT / NOT_COMPLETED

Purpose:

```text
- Require the exact clean official-main candidate source for final evidence.
- Aggregate Google Health sleep, daily advice, post-advice chat, in-app TTS,
  deterministic character display, and the final integrated daily loop.
- Require actual DRC Backend plus PC and smartphone Flutter Web execution.
- Validate an ignored private manifest without reading raw screenshots/audio/health data.
- Keep fixed ZIP, tag, GitHub Release, and publication work in R-1d/R-1e.
```

Implementation files:

```text
docs/v210_final_smartphone_web_evidence.md
docs/operator_evidence_templates/v210_final_smartphone_web_evidence_r1c.example.json
scripts/check_v210_final_smartphone_web_evidence.py
```

Accepted private manifest destination:

```text
operator_evidence/v210_final_smartphone_web_evidence_r1c.json
```

Acceptance record:

```text
accepted on: 2026-07-25
implementation commit: 1e922e6
accepted candidate source HEAD: 1e922e68685dadfc1008f1119d0ce492584e8f19
private manifest validation: passed
required evidence items: 6 / 6 accepted
actual DRC Backend API used: true
final PC Web aggregate: COMPLETED / ACCEPTED
final smartphone Web aggregate: COMPLETED / ACCEPTED
public-safe opaque screenshot references: recorded
raw/private evidence committed: false
fixed ZIP built: false
tag created: false
GitHub Release created: false
```

Acceptance-sync verification before commit:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_final_smartphone_web_evidence.py
python scripts\check_v210_final_smartphone_web_evidence.py `
  --manifest-json .\operator_evidence\v210_final_smartphone_web_evidence_r1c.json
python scripts\check_v210_release_readiness.py --with-flutter --with-builds
git diff --check
```

R-1c is `COMPLETED / ACCEPTED`.
R-1d is `CURRENT / NOT_COMPLETED` and `IMPLEMENTED / NOT_ACCEPTED`; R-1e remains `PLANNED`.


## Historical R-1d implementation state — One-time fixed ZIP build and same-artifact verification

Status: CURRENT / NOT_COMPLETED
Implementation state: IMPLEMENTED / NOT_ACCEPTED
Current small commit: R-1e
Parent R-1: CURRENT / NOT_COMPLETED

Implementation files:

```text
build_v210_fixed_release_zip_from_head.ps1
scripts/check_v210_fixed_release_zip.py
```

Implementation contract:

```text
- clean synchronized official Public main
- HEAD == origin/main
- immutable annotated DRC_v2.0.0 and DRC_v2.0.1 tags
- DRC_v2.1.0 absent
- no existing DailyRhythmCompanion_v2.1.0_*.zip
- one detached committed-HEAD worktree
- build_release.bat release invoked exactly once
- one versioned fixed ZIP moved into ignored release/
- source HEAD / basename / size / SHA-256 printed outside the ZIP
- builder supports Windows PowerShell 5.1 without requiring pwsh
- -PreflightOnly runs the strict source/test/build gate with build invocation count 0
- builder stops before verification, tag, or GitHub Release
- verifier accepts only an explicitly supplied exact ZIP
- verifier never rebuilds and confirms the same file remains unchanged
```

Implementation verification before commit:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fixed_release_zip.py
python scripts\check_v210_release_readiness_current_behavior_inventory.py
python scripts\check_v210_final_smartphone_web_evidence.py
python scripts\check_v210_release_readiness.py --with-flutter --with-builds
git diff --check
```

Stop rule:

```text
Do not run build_v210_fixed_release_zip_from_head.ps1 in the implementation commit.
Do not build or verify the fixed ZIP.
Do not create DRC_v2.1.0.
Do not publish a GitHub Release.
```

R-1d remains `CURRENT / NOT_COMPLETED` and `IMPLEMENTED / NOT_ACCEPTED`.
R-1e remains `PLANNED`.

T-1c Visual Studio 18 compatibility correction:

```text
- Flutter 3.41.7 / audioplayers 6.7.1 dependency resolution: passed
- windows/flutter/CMakeLists.txt scaffold restoration: operator-local generated file
- MSVC 14.5x experimental coroutine deprecation bridge: implemented
- Windows build re-verification: required before commit
- T-1c final accepted state: COMPLETED / ACCEPTED
```
- Windows Flutter scaffold CMakeLists is tracked; only its ephemeral directory stays ignored.

## R-1d acceptance record

Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED
Completed small commit: R-1d
Current small commit: R-1e
Parent R-1: CURRENT / NOT_COMPLETED

```text
implementation commits: 42e93f1, 377d98d, 6e7af31
accepted release source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
fixed ZIP basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
fixed ZIP size bytes: 1747337
fixed ZIP SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
preflight-only gate: passed with build invocation count 0
accepted-candidate builder invocation count: 1
release-package hygiene: passed
ZIP CRC and single-package-root verification: passed
Backend pytest from extracted ZIP: 110 passed
Flutter test from extracted ZIP: 103 passed
Flutter Web build from extracted ZIP: passed
Flutter Windows build from extracted ZIP: passed
same-artifact verification without rebuilding: passed
verifier builder invocation: false
DRC_v2.1.0 tag created: false
GitHub Release created: false
```

A superseded pre-fix candidate was rejected before publication and is not part of the accepted tuple. R-1d is `COMPLETED / ACCEPTED`; R-1e is `CURRENT / NOT_COMPLETED` and `NOT_STARTED`.
