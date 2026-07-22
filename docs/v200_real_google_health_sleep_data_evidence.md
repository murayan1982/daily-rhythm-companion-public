# v2.0.0 Day55 real Google Health sleep data evidence

Day55 prepares the public-safe evidence contract for the v2.0.0 pre-release requirement:

```text
Google Health実APIを使用して、実睡眠データが取得できること / real Google Health API sleep-data retrieval
```

Default checks are still mock-safe. They do not call Google Health APIs, read OAuth tokens, call the backend, open a browser, start Flutter, normalize real health payloads, or create health-data artifacts.

## Status marker

```text
v200_real_google_health_sleep_evidence_status: operator-evidence-contract-ready
```

This means the evidence contract is ready. It does **not** mean the real Google Health sleep-data requirement is satisfied yet.

## Required configured-run evidence

A configured real Google Health run can satisfy this gate only after all of the following are confirmed:

```text
- explicit_operator_opt_in_enabled
- google_health_real_api_gate_enabled
- oauth_connection_available
- real_sleep_data_fetch_succeeded
- sleep_summary_normalized_to_public_contract
- backend_sleep_summary_real_data_confirmed
- public_safe_evidence_recorded
```

The configured run should prove:

```text
- the real Google Health API path was explicitly enabled by the operator
- the OAuth connection was available without exposing tokens or authorization headers
- real sleep data was fetched from Google Health
- the fetched data was normalized into the public SleepSummary contract
- the backend sleep summary path reported the result through safe real-data fields
- shared evidence is marker-based and public-safe
```

## Public safety policy

Do not record or commit:

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

Public evidence should use only coarse markers, redacted labels, and safe booleans. Health details should stay local and private.

## Mock-safe source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_real_google_health_sleep_data_evidence.py

cd app
flutter test
cd ..
```

Expected output includes:

```text
[v200-prerelease-requirements-check] OK
[v200-real-llm-web-answer-day52-check] OK
[v200-real-tts-provider-gate-day53-check] OK
[v200-real-tts-web-audio-output-day54-check] OK
[v200-real-google-health-sleep-data-day55-check] OK
```

## Default smoke renderer

```powershell
python scripts\smoke_v200_real_google_health_sleep_data_evidence.py
```

Expected marker:

```text
v200_real_google_health_sleep_evidence_status: operator-evidence-contract-ready
```

## Optional redacted operator evidence validation

After a configured manual run, an operator may create a small **local-only** redacted JSON summary. Do not commit the file unless it has been reviewed for public safety.

Example shape:

```json
{
  "explicit_operator_opt_in_enabled": true,
  "google_health_real_api_gate_enabled": true,
  "oauth_connection_available": true,
  "real_sleep_data_fetch_succeeded": true,
  "sleep_summary_normalized_to_public_contract": true,
  "backend_sleep_summary_real_data_confirmed": true,
  "public_safe_evidence_recorded": true,
  "client_secrets_included": false,
  "access_tokens_included": false,
  "refresh_tokens_included": false,
  "authorization_headers_included": false,
  "raw_google_health_payloads_included": false,
  "raw_sleep_events_included": false,
  "precise_personal_sleep_timestamps_included": false,
  "raw_lan_ips_included": false,
  "private_paths_included": false,
  "raw_screenshots_included": false
}
```

Validation command:

```powershell
python scripts\smoke_v200_real_google_health_sleep_data_evidence.py --operator-evidence-json .\operator_evidence.json
```

This validation does not call Google Health, read tokens, call the backend, or parse raw health payloads. It only checks that a marker-only summary has all required booleans and does not claim unsafe publication.

## Requirement status

Day55 keeps the v2.0.0 real Google Health sleep-data requirement pending until a configured operator run confirms real API retrieval and safe SleepSummary normalization. The source-tree check only confirms that the evidence contract, safety policy, and previous Day52-Day54 gates remain intact.
