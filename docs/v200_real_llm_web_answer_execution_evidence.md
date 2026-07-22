# v2.0.0 Day64: Real LLM Web answer execution evidence

Day64 starts the real execution evidence phase for the first v2.0.0 completion requirement:

```text
real LLM API: Web上で回答が生成できること / real LLM API Web answer generation
```

Day52 prepared the public-safe evidence gate. Day64 does **not** replace that gate. It adds a marker-only acceptance layer for a configured operator run that has already confirmed both the DRC backend API response and the smartphone Web UI visible result.

## Completion boundary

The Day64 real LLM requirement can be accepted only when all of the following are true:

```text
v200_real_llm_web_answer_execution_evidence_status: operator-execution-evidence-contract-ready
v200_real_llm_web_answer_execution_requirement_key: real_llm_web_answer
v200_real_llm_web_answer_execution_operator_run_required: True
v200_real_llm_web_answer_execution_mock_safe_default: True
```

The actual accepted operator evidence must confirm:

```text
explicit_operator_opt_in_enabled
backend_advice_api_called
configured_framework_route_used
source_engine_framework_confirmed
message_non_empty_confirmed
smartphone_web_ui_visible_answer_confirmed
fallback_or_skip_not_counted
public_safe_evidence_recorded
```

`source.engine=framework` is required. `mock`, `framework_fallback`, `skipped`, `unavailable`, and `error` are useful states to display, but they must not be counted as real execution success.

## Mock-safe source-tree check

Use this check during normal local development and CI-like verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_llm_web_answer_execution_evidence.py

cd app
flutter test
cd ..
```

Expected marker:

```text
[v200-real-llm-web-answer-execution-day64-check] OK
```

The default check does not call providers, start a backend, open a browser, create AI Character Framework sessions, call `ask`, call `/advice`, or inspect raw screenshots. It verifies the Day64 evidence contract and validates the public-safe example marker file only.

## Configured operator run outline

Run this only in a private local/demo environment with real LLM credentials configured through private environment variables.

1. Start the backend with the configured framework / real LLM route.
2. Confirm the backend uses the actual DRC `/advice` API path.
3. Run the existing Day52 optional backend probe, or manually call `/advice` with a safe request shape.
4. Confirm the response message is non-empty.
5. Confirm `source.engine` is exactly `framework`.
6. Start or serve Flutter Web with the phone-accessible backend base URL.
7. Open the Web UI from the smartphone browser.
8. Generate advice from the Web UI.
9. Confirm the visible Web answer is non-empty and the configured framework path is visible or otherwise confirmed.
10. Record only marker-only public-safe evidence.

Optional backend probe example:

```powershell
$env:DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE="1"
$env:DRC_BACKEND_API_BASE_URL="http://127.0.0.1:8000"
python scripts\smoke_framework_v200_real_llm_web_answer_evidence.py --require-running-backend
```

The optional backend probe still does not print the answer body or raw provider payload. Smartphone Web UI confirmation remains required after the API probe.

## Marker-only evidence JSON

After the configured operator run, create a small redacted JSON file outside normal source control, or copy the template under `docs/operator_evidence_templates/` and keep only boolean markers.

Validate it with:

```powershell
python scripts\smoke_framework_v200_real_llm_web_answer_execution_evidence.py --operator-evidence-json .\operator_evidence\200_real_llm_web_answer_day64.json
```

The accepted marker-only shape is:

```json
{
  "explicit_operator_opt_in_enabled": true,
  "backend_advice_api_called": true,
  "configured_framework_route_used": true,
  "source_engine_framework_confirmed": true,
  "message_non_empty_confirmed": true,
  "smartphone_web_ui_visible_answer_confirmed": true,
  "fallback_or_skip_not_counted": true,
  "public_safe_evidence_recorded": true
}
```

Do not add raw values to this JSON. It should contain booleans only.

## Public-safe evidence policy

Public evidence may include:

```text
- check names and OK/SKIP/ERROR statuses
- source.engine=framework confirmation
- non-empty message confirmation
- approximate answer length bucket, if needed
- redacted backend URL shape such as http://<PC_LAN_IP>:8000
- redacted execution date
```

Public evidence must not include:

```text
- API keys
- OAuth tokens
- Authorization headers
- raw prompt bodies
- answer bodies
- raw provider payloads
- raw provider errors that include private payloads
- raw LAN IPs
- private absolute paths
- raw screenshots
- browser storage dumps
```

## What Day64 does not complete

Day64 accepts only the first v2.0.0 real execution requirement when a configured operator evidence JSON validates successfully.

Day64 does not complete:

```text
- real TTS Web audio output evidence
- real Google Health sleep data evidence
- Web image display execution evidence
- public repo readiness final sweep
- v2.0.0 final aggregate gate
- fixed v2.0.0 release zip verification
```

Until the remaining requirements are accepted, v2.0.0 release readiness remains incomplete.
