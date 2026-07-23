# Daily Rhythm Companion v2.1.0 goal checklist — small commits

Updated: 2026-07-23
Status: IN_PROGRESS
Current small commit: W-3 — Fitbit real sleep normalization and API regression tests
Current small-commit state: CURRENT / NOT_COMPLETED
W-1 state: COMPLETED / ACCEPTED
W-2 state: COMPLETED / ACCEPTED
Current released version: v2.0.1

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
W-3  CURRENT / NOT_COMPLETED  Fitbit real sleep normalization and API regression tests
W-4  PLANNED                  Sleep-provider selection, source-label UI, and simplified
                              Google Health user UX with retained operator diagnostics
W-5  PLANNED                  Configured real Fitbit operator verification
C-1  PLANNED                  Post-advice chat lifecycle and UI-state hardening
T-1  PLANNED                  Flutter in-app TTS player and artifact-expiry handling
V-1  PLANNED                  Character display extraction and deterministic state presentation
R-1  PLANNED                  v2.1.0 aggregate readiness, smartphone Web evidence,
                              fixed-ZIP verification, approval, and release preparation
```

W-1 and W-2 are completed and accepted. W-3 is current but not completed; W-4 through R-1 remain planned.

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

Status: CURRENT / NOT_COMPLETED
Implementation state: IMPLEMENTED / VERIFICATION_PENDING

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
W-3 remains NOT_COMPLETED until the complete gate and approval pass.

---

# W-4 — Sleep-provider selection and source-label UI

Status: PLANNED

Planned boundary:

```text
- Present the configured sleep provider and app-facing data source consistently.
- Add a clear selection/configuration UX without making credentials client-owned.
- Simplify normal Google Health connection UX while retaining operator diagnostics
  in an advanced or explicitly labeled surface.
- Preserve mock-safe operation and conservative health wording.
```

---

# W-5 — Configured real Fitbit operator verification

Status: PLANNED

Planned boundary:

```text
- Execute the accepted real Fitbit path only through explicit operator opt-in.
- Validate OAuth, refresh, permissions, real sleep retrieval, normalization,
  source labels, and smartphone Web presentation.
- Keep tokens, codes, raw payloads, raw screenshots, exact private sleep values,
  private paths, and LAN addresses outside Public commits and release artifacts.
```

---

# C-1 — Post-advice chat lifecycle and UI-state hardening

Status: PLANNED

Planned boundary:

```text
- Preserve the accepted 30-minute idle TTL, 100-session capacity, and LRU behavior
  unless a later accepted contract intentionally changes them.
- Add bounded turn limits and clearer expired/unavailable/fallback UI states.
- Reuse released AI Character Framework public text-session APIs only.
```

---

# T-1 — Flutter in-app TTS player and artifact-expiry handling

Status: PLANNED

Planned boundary:

```text
- Add in-app play, stop, replay, loading, completion, failure, and expired states.
- Preserve DRC-owned opaque MP3 URLs and accepted artifact retention/cleanup rules.
- Do not expose Framework-managed paths or provider payloads.
```

---

# V-1 — Character display extraction and deterministic states

Status: PLANNED

Planned boundary:

```text
- Extract character display from the large home screen.
- Add deterministic advice, mood, loading, speaking, and fallback presentation.
- Keep static repository-safe assets and do not claim Live2D/VTS execution.
```

---

# R-1 — v2.1.0 readiness and release preparation

Status: PLANNED

Planned boundary:

```text
- Add the aggregate source-tree and test gate only after prior phases are accepted.
- Require separately accepted smartphone Web evidence where specified.
- Freeze one committed source state before building a fixed ZIP.
- Build the fixed ZIP once and verify the same artifact without rebuilding.
- Require explicit final approval before tag and GitHub Release publication.
```

R-1 completion requirements must not be imported into W-1 or any earlier phase.
