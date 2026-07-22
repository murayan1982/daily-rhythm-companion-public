# v2.0.0 Day66 real Google Health sleep data execution evidence

Day66 continues the v2.0.0 real execution evidence phase for the third completion requirement:

```text
real Google Health API: 実睡眠データが取得できること / real Google Health API sleep-data retrieval
```

Day55 prepared the public-safe evidence gate. Day66 adds the execution-evidence acceptance layer for a configured operator run that proves real Google Health API use, successful real sleep-data fetch, safe SleepSummary normalization, backend real-data response confirmation, and smartphone Web UI real-source confirmation.

Default checks are still mock-safe. They do not call Google Health APIs, read OAuth tokens, call the backend, open a browser, start Flutter, normalize real health payloads, inspect raw health data, write health-data artifacts, or create release artifacts.

## Status marker

```text
v200_real_google_health_sleep_data_execution_evidence_status: operator-execution-evidence-contract-ready
```

This means the Day66 execution evidence acceptance contract is ready. It does **not** mean the configured real Google Health run has already happened.

## Required configured-run evidence

A configured real Google Health run can satisfy this execution requirement only after all of the following marker-only evidence is confirmed:

```text
explicit_operator_opt_in_enabled
google_health_real_api_gate_enabled
oauth_connection_available
real_google_health_api_request_confirmed
real_sleep_data_fetch_succeeded
sleep_summary_normalized_to_public_contract
backend_sleep_summary_real_data_confirmed
smartphone_web_sleep_summary_real_source_confirmed
fallback_or_skip_not_counted
public_safe_evidence_recorded
```

The configured run must prove:

```text
- the real Google Health API path was explicitly enabled by the operator
- OAuth was available without exposing client secrets, tokens, authorization headers, or local token files
- the configured real Google Health API request path was used instead of mock, fixture, simulated, or fallback data
- real sleep data was fetched successfully
- the fetched data was normalized into the public SleepSummary contract
- the backend sleep summary path reported real-data source fields through safe public response fields
- the smartphone Web UI visibly confirmed the real sleep summary source or equivalent public-safe real-data indicator
- fallback, skipped, unavailable, failed, and error states were not counted as configured real execution success
- shared evidence stayed marker-only and public-safe
```

## Mock-safe source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py

cd app
flutter test
cd ..
```

Expected output includes:

```text
[v200-real-google-health-sleep-data-execution-day66-check] OK
```

## Default smoke renderer

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py
```

Expected marker:

```text
v200_real_google_health_sleep_data_execution_evidence_status: operator-execution-evidence-contract-ready
```

## Optional marker-only operator evidence validation

After a configured manual run, create a small redacted JSON file outside normal source control, or copy the reviewed template under `docs/operator_evidence_templates/` and keep only boolean markers.

Validate it with:

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py --operator-evidence-json .\operator_evidence\v200_real_google_health_sleep_data_day66.json
```

The accepted marker-only shape is:

```json
{
  "explicit_operator_opt_in_enabled": true,
  "google_health_real_api_gate_enabled": true,
  "oauth_connection_available": true,
  "real_google_health_api_request_confirmed": true,
  "real_sleep_data_fetch_succeeded": true,
  "sleep_summary_normalized_to_public_contract": true,
  "backend_sleep_summary_real_data_confirmed": true,
  "smartphone_web_sleep_summary_real_source_confirmed": true,
  "fallback_or_skip_not_counted": true,
  "public_safe_evidence_recorded": true
}
```

Do not add raw values to this JSON. It should contain booleans only.

## Public-safe evidence policy

Public evidence may include:

```text
- check names and OK/SKIP/ERROR statuses
- configured real Google Health API gate confirmation
- OAuth availability marker without token values
- real Google Health API request marker
- real sleep-data fetch success marker
- SleepSummary normalization marker
- backend real-data source marker
- smartphone Web UI real-source confirmation marker
- redacted backend URL shape such as http://<PC_LAN_IP>:8000
- redacted execution date
```

Public evidence must not include:

```text
- client secrets
- access tokens
- refresh tokens
- authorization headers
- raw Google Health payloads
- raw sleep events
- precise personal sleep timestamps
- raw LAN IPs
- private absolute paths
- raw screenshots
- browser storage dumps
- local token files
```

Health details should stay local and private. Public docs should record only coarse markers and redacted labels.

## States that are not success

The following states must be visible when they happen, but must not be counted as configured real Google Health execution success:

```text
mock_data
fixture_data
fallback_data
simulated_data
skipped
unavailable
oauth_missing
token_invalid
api_failed
normalization_failed
backend_not_called
web_ui_not_confirmed
error
```

## What Day66 does not complete

Day66 accepts only the third v2.0.0 real execution requirement when a configured operator evidence JSON validates successfully.

Day66 does not complete:

```text
- Web image display execution evidence
- public repo readiness final sweep
- v2.0.0 final aggregate gate
- fixed v2.0.0 release zip verification
```

Until the remaining requirements are accepted, v2.0.0 release readiness remains incomplete.
