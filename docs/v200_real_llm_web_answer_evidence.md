# v2.0.0 Day52: Real LLM Web answer evidence

Day52 prepares the public-safe evidence path for the first v2.0.0 pre-release requirement:

```text
v200_prerelease_requirement_real_llm_web_answer: required
```

The goal is to prove, before v2.0.0 release readiness, that Daily Rhythm Companion can use a real LLM API through the configured backend / AI Character Framework path and display a generated answer on Web.

Day52 itself is still mock-safe by default. The default source-tree check does not call providers, start the backend, start Flutter, open a browser, or create framework sessions.

## Evidence contract

The evidence contract is:

```text
v200_real_llm_web_answer_evidence_status: operator-evidence-contract-ready
v200_real_llm_web_answer_requirement_key: real_llm_web_answer
v200_real_llm_web_answer_operator_run_required: True
v200_real_llm_web_answer_mock_safe_default: True
v200_real_llm_web_answer_evidence_explicit_operator_opt_in: required
v200_real_llm_web_answer_evidence_actual_drc_backend_api: required
v200_real_llm_web_answer_evidence_framework_or_configured_backend_route: required
v200_real_llm_web_answer_evidence_web_ui_non_empty_answer: required
v200_real_llm_web_answer_evidence_public_safe_evidence: required
v200_real_llm_web_answer_default_provider_call_status: not-called
v200_real_llm_web_answer_default_backend_call_status: not-called
v200_real_llm_web_answer_default_browser_status: not-started
```

This means the source tree is ready to record the real LLM Web answer evidence, but the requirement is not closed until a configured operator run confirms the Web UI result.

## Mock-safe default check

Use this check during normal local development and CI-like verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_llm_web_answer_evidence.py

cd app
flutter test
cd ..
```

Expected marker:

```text
[v200-real-llm-web-answer-day52-check] OK
```

The check also reruns the v2.0.0 pre-release requirements check:

```powershell
python scripts\check_v200_prerelease_requirements.py
```

## Optional configured backend API probe

Only run this after starting the backend with a configured framework / real LLM environment.

Required explicit opt-in marker:

```text
DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE=1
```

The backend should be configured so that `/advice` uses the framework route.

Required backend mode marker:

```text
CONVERSATION_ENGINE=framework
```

The configured response should return:

```text
source.engine=framework
```

Operator-only example:

```powershell
$env:DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE="1"
$env:DRC_BACKEND_API_BASE_URL="http://127.0.0.1:8000"
python scripts\smoke_framework_v200_real_llm_web_answer_evidence.py --require-running-backend
```

The optional probe sends only a safe sample advice request shape to the DRC backend API. It prints only safe metadata such as status, source engine, and message length. It does not print the answer body or raw provider payload.

## Smartphone Web UI evidence checklist

The real v2.0.0 requirement is Web-visible, not API-only. After the backend probe passes, verify the smartphone Web UI manually:

```text
1. Start the backend with configured framework / real LLM settings.
2. Start or serve Flutter Web with DRC_BACKEND_API_BASE_URL pointing to the backend.
3. Open the app from the smartphone browser.
4. Confirm the UI shows the active backend API base URL.
5. Generate advice from the Web UI.
6. Confirm the visible result is a non-empty answer.
7. Confirm source metadata or visible status indicates the configured framework path, not mock or framework_fallback.
8. Record only public-safe evidence.
```

Public-safe evidence may include:

```text
- check command names and OK/SKIP/ERROR statuses
- source.engine value
- non-empty answer confirmation
- answer length or short category
- redacted timestamp/date
- redacted backend URL shape such as http://<PC_LAN_IP>:8000
```

Do not record or commit:

```text
- API keys
- OAuth tokens
- Authorization headers
- prompt bodies
- answer bodies
- raw provider payloads
- raw provider errors
- local absolute paths
- raw LAN IPs
- raw screenshots that reveal private values
```

## Completion boundary

Day52 does not claim that v2.0.0 requirement #1 is satisfied by itself.

Requirement #1 can be marked satisfied only after a configured operator run confirms both:

```text
- backend API returns a non-empty framework-sourced answer
- smartphone Web UI visibly displays the generated answer
```

Until then, the status remains:

```text
v200_real_llm_web_answer_evidence_status: operator-evidence-contract-ready
```
