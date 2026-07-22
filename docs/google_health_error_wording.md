# Google Health Unavailable and Error Wording Guide

## Purpose

This guide defines safe, understandable wording for Google Health unavailable, authorization, reconnect, fallback, and configured-skip states.

The goal is to make the app/backend state clear without exposing secrets, raw provider details, or medical claims.

This guide is for:

```text
- app UI wording
- backend response labels
- capability/status summaries
- operator-facing check output
- public docs
```

The normal development default remains mock-safe.

---

## Wording principles

Use wording that is:

```text
- calm
- short
- actionable
- source-aware
- non-medical
- non-diagnostic
- safe for public logs and screenshots
```

Avoid wording that is:

```text
- alarming
- judgmental
- diagnostic
- overly technical for the app UI
- misleading about mock vs real data
- exposing provider internals or raw payloads
```

---

## Required public state labels

Use these state labels consistently:

```text
not_configured
authorization_required
connected
reconnect_required
unavailable
fallback_to_mock
configured_skip
```

These labels are safe categories.
They must not include token values, client secrets, authorization codes, raw provider payloads, or private paths.

---

## State wording matrix

### not_configured

Use when the Google Health provider is not set up or explicit opt-in gates are disabled.

User-facing wording:

```text
Google Health is not configured.
```

Operator-facing wording:

```text
Google Health is not configured. Review setup/OAuth guidance before enabling the configured path.
```

Safe next action:

```text
Use mock mode, or review docs/google_health_setup_oauth.md.
```

Do not say:

```text
Google Health failed.
Your health data is broken.
```

---

### authorization_required

Use when configuration exists, but authorization has not been completed.

User-facing wording:

```text
Authorization is required.
```

Operator-facing wording:

```text
Authorization is required. Complete the local/demo Google authorization flow.
```

Safe next action:

```text
Start the authorization flow with the intended test account.
```

Do not say:

```text
Your account is invalid.
Your sleep data cannot be trusted.
```

---

### connected

Use when authorization is available and the configured provider path can be attempted.

User-facing wording:

```text
Google Health is connected.
```

Operator-facing wording:

```text
Google Health is connected. Verify that app-facing sleep summary output is normalized and minimal.
```

Safe next action:

```text
Fetch the app-facing sleep summary and confirm the source label.
```

Do not say:

```text
Your sleep health is good.
Your sleep is diagnosed.
```

---

### reconnect_required

Use when prior authorization cannot be reused safely.

User-facing wording:

```text
Reconnect is required.
```

Operator-facing wording:

```text
Reconnect is required. Reset local/demo authorization state and complete authorization again.
```

Safe next action:

```text
Review docs/google_health_reconnect_reset.md.
```

Do not say:

```text
Your Google account is unsafe.
Your health connection is permanently broken.
```

---

### unavailable

Use when the configured provider path cannot currently fetch or normalize data.

User-facing wording:

```text
Google Health data is unavailable.
```

Operator-facing wording:

```text
Google Health data is unavailable. Check status details, endpoint verification, and provider data availability.
```

Safe next action:

```text
Check configured verification guidance, then fall back to mock mode if needed.
```

Do not say:

```text
You did not sleep enough.
You have a health problem.
The provider returned this raw payload: ...
```

---

### fallback_to_mock

Use when the app/backend intentionally uses mock data because real data is disabled or unavailable.

User-facing wording:

```text
Real data is unavailable, so mock data is being used.
```

Operator-facing wording:

```text
Real data is unavailable or disabled, so mock data is being used. Confirm source label is mock.
```

Safe next action:

```text
Continue with mock-safe testing, or configure the real/demo path intentionally.
```

Do not say:

```text
This is your actual sleep data.
Google Health source: real
```

---

### configured_skip

Use for configured-only checks when explicit opt-in gates are missing.

Check output wording:

```text
[v120-day4-configured-skip] Google Health configured verification requires explicit opt-in gates
```

User/operator-facing wording:

```text
Configured Google Health verification was skipped because explicit opt-in gates are not enabled.
```

Safe next action:

```text
Enable configured gates only in a private local/demo environment when intentionally verifying real data.
```

Do not say:

```text
Configured verification failed.
Real API verification is required for normal development.
```

---

## Source label rules

Always keep source labels clear.

Allowed source labels:

```text
mock
google_health
fallback
unavailable
```

Rules:

```text
- mock data must be labeled mock.
- Google Health-backed normalized data must be labeled google_health.
- fallback behavior must clearly say fallback or mock.
- unavailable states must not pretend to have real sleep data.
- history/trend data must not be presented as today's sleep.
```

---

## Safe reason categories

Backend/operator details may use safe reason categories.

Examples:

```text
missing_client_config
missing_redirect_config
state_mismatch
authorization_denied
authorization_code_missing
token_exchange_disabled
token_exchange_failed
token_refresh_disabled
token_refresh_failed
token_revoked_or_expired
scope_missing
real_api_disabled
endpoint_not_verified
api_request_failed
sleep_data_unavailable
provider_response_unusable
configured_gates_missing
```

These categories are safe only if they do not include secret values or raw payload fragments.

---

## Forbidden output

Never expose:

```text
- access tokens
- refresh tokens
- client secrets
- authorization codes
- raw Google Health payloads
- local token files
- private absolute paths
- provider debug dumps
```

Do not include those values in:

```text
- app UI
- API responses
- normal logs
- check output
- public docs
- release packages
```

---

## Health wording safety

Google Health sleep data must remain informational.

Avoid:

```text
- diagnosis
- treatment advice
- medical guarantees
- alarmist claims
- presenting trends as today's sleep
- claiming causation from a single sleep summary
```

Prefer:

```text
- "Here is the available sleep summary."
- "This looks like mock data."
- "Real data is unavailable."
- "You may want to take it easy today."
- "Consider checking your routine if this pattern continues."
```

---

## Example response snippets

Safe API/UI-style snippets:

```text
status: authorization_required
message: Authorization is required.
source: unavailable
```

```text
status: fallback_to_mock
message: Real data is unavailable, so mock data is being used.
source: mock
```

```text
status: connected
message: Google Health is connected.
source: google_health
```

Safe operator/check-style snippet:

```text
[v120-day4-configured-skip] Google Health configured verification requires explicit opt-in gates
```

---

## Day5 status

This guide is the v1.2.0 Day5 unavailable/error wording baseline.

Expected check output:

```text
[v120-google-health-error-wording-day5-check] OK
```
