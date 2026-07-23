# v2.1.0 W-3 — Fitbit real sleep normalization and API regression contract

Updated: 2026-07-23
Status: IMPLEMENTED / VERIFICATION_PENDING
Active small commit: W-3 — CURRENT / NOT_COMPLETED

## Purpose

W-3 completes the mock-safe backend contract between the existing Fitbit
sleep-by-date path and the app-facing `SleepSummary` model.

It does not execute configured real Fitbit OAuth, token refresh, permission
checks, sleep retrieval, or smartphone Web acceptance. Those remain W-5 work.

## Implemented boundary

```text
Fitbit HTTP response
→ allow-listed API error code
→ safe Fitbit sleep result
→ deterministic normalizer
→ app-facing SleepSummary
```

The API boundary classifies:

```text
401       reconnect_required
403       permission_denied or scope_missing
429       rate_limited
5xx       provider_unavailable
network   provider_unavailable
invalid successful response  invalid_response
other 4xx fitbit_sleep_api_request_failed
```

Only an allow-listed code and optional HTTP status remain in the internal
exception. Provider messages, raw error payloads, access tokens, and
Authorization headers are not copied into app-facing messages.

## Accepted normalization semantics

A successful normalized Fitbit result requires a positive usable sleep duration.
The normalizer:

```text
- prefers the entry with isMainSleep=true;
- otherwise uses the first object sleep entry;
- falls back to summary.totalMinutesAsleep when needed;
- maps startTime and endTime when the selected entry supplies them;
- maps efficiency only when it is an integer from 0 through 100;
- uses the same good/fair/short duration labels as Google Health;
- sets confidence=high for a complete main-sleep entry;
- sets confidence=medium for a summary-level or incomplete-entry fallback;
- sets is_real_data=true only after successful provider-shaped normalization.
```

`is_real_data=true` describes the response semantics of a successful real-provider
path. A synthetic fixture that tests this mapping is not configured real Fitbit
evidence.

No-data and unavailable responses use:

```text
available=false
total_sleep_minutes=0
quality_label=unavailable
confidence=none
is_real_data=false
unavailable_reason=<allow-listed reason>
```

Allow-listed reasons include:

```text
not_connected
reconnect_required
permission_denied
scope_missing
rate_limited
provider_unavailable
no_sleep_data
invalid_response
fitbit_sleep_api_request_failed
```

## Mock-safe regression boundary

Normal W-3 tests may use:

```text
- synthetic public-safe Fitbit-shaped dictionaries;
- injected fake HTTP GET functions;
- temporary token files;
- fixed dates and non-private placeholder values;
- FastAPI TestClient;
- source-tree checks and normal backend pytest.
```

Normal W-3 tests must not use:

```text
- backend/.env real values;
- backend/local_data operator tokens;
- an OAuth browser or authorization code;
- real token exchange or refresh;
- a Fitbit network request;
- copied private raw Fitbit payloads;
- exact personal sleep values;
- raw screenshots, private paths, or LAN URLs.
```

## Changed runtime and test files

```text
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/fitbit.py
backend/tests/test_fitbit_real_sleep_normalization.py
```

The API route, `SleepSummary` model, provider factory, configuration, Fitbit
OAuth/status implementation, and Flutter runtime do not change in W-3.

## Verification gate

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v210_fitbit_real_sleep_normalization.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

W-3 remains `CURRENT / NOT_COMPLETED` until focused checks, aggregate checks,
Flutter tests, diff review, and operator approval pass.

## Explicit W-4 / W-5 boundary

W-3 does not add or accept:

```text
- sleep-provider selection UI;
- unified source-label UI;
- simplified Google Health normal-user UX;
- real Fitbit OAuth, token exchange, or refresh evidence;
- real scope/permission evidence;
- configured real sleep retrieval;
- smartphone Web evidence;
- a release ZIP, tag, GitHub Release, or publication record.
```

Configured real acceptance remains W-5.
