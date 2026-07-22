# Google Health Configured Verification Checklist

## Purpose

This checklist defines how a configured local/demo operator should verify the Google Health real-data path safely.

The normal development path remains mock-safe.

```text
mock-safe mode → no credentials → no accidental real API calls
```

Day4 does not make real API calls from the validation script by default.
It documents the configured verification sequence and adds a safe environment-gate check.

---

## Verification modes

Use three separate modes.

### 1. Source-tree documentation check

Purpose:

```text
Confirm the onboarding, setup, reconnect/reset, and configured verification docs exist and preserve mock-safe policy.
```

This mode is safe for normal local development and CI-style checks.

Expected command:

```powershell
python scripts\check_v120_google_health_configured_verification_day4.py
```

Expected output:

```text
[v120-google-health-configured-verification-day4-check] OK
```

### 2. Configured environment gate check

Purpose:

```text
Confirm whether the current process environment is intentionally configured for a real/demo Google Health verification run.
```

Expected command:

```powershell
python scripts\check_v120_google_health_configured_verification_day4.py --configured-env
```

If the required explicit opt-in gates are not all enabled, the check must skip instead of failing normal mock-safe development.

Expected skip output:

```text
[v120-day4-configured-skip] Google Health configured verification requires explicit opt-in gates
[v120-google-health-configured-verification-day4-check] OK
```

If all explicit gates are enabled, the check may report that the configured environment gate is enabled, but it still must not print tokens, secrets, or raw payloads.

Expected configured-gate output:

```text
[v120-day4-configured-env] explicit opt-in gates enabled
[v120-google-health-configured-verification-day4-check] OK
```

### 3. Manual configured real-data verification

Purpose:

```text
Let the operator manually verify that the app-facing path can return normalized sleep summary data from the configured provider.
```

This mode may involve real provider access, but only after the operator intentionally enables the private configured environment.

The Day4 validation script does not perform this real-data request.

---

## Required explicit opt-in gates

A configured real/demo verification run must require all of these gates to be enabled in a private local environment:

```text
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1
```

The committed mock-safe profile must keep those gates disabled:

```text
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

---

## Manual configured verification sequence

Run this sequence only in a local/demo environment controlled by the operator.

```text
1. Confirm mock-safe checks pass.
2. Review docs/google_health_setup_oauth.md.
3. Review docs/google_health_reconnect_reset.md.
4. Load private local configured environment values.
5. Confirm all explicit opt-in gates are enabled intentionally.
6. Confirm endpoint verification is enabled only after the operator has verified the endpoint target.
7. Start the backend/app.
8. Complete or reuse Google authorization.
9. Confirm status/capability output uses safe state wording.
10. Fetch the app-facing sleep summary through the normal app/backend path.
11. Confirm the response is normalized and minimal.
12. Confirm source label is clear.
13. Confirm no token, secret, authorization code, raw payload, local token file, or private path appears in output.
14. Return to mock-safe mode after the test.
15. Re-run mock-safe checks.
```

---

## Expected app-facing response properties

A configured real-data response should be normalized before it reaches the app UI.

Expected safe properties:

```text
- app-facing response is SleepSummary-like
- source label is clear, for example google_health
- date/range is understandable
- sleep duration fields are normalized
- unavailable or fallback states are explicit
- old history is not presented as today's sleep
- wording remains non-medical and conservative
```

Forbidden properties:

```text
- access token
- refresh token
- client secret
- authorization code
- raw Google Health payload
- local token file path
- private absolute path
- diagnostic or medical conclusion
```

---

## Expected status labels

The configured path should use understandable status labels.

```text
not_configured
authorization_required
connected
reconnect_required
unavailable
fallback_to_mock
```

Safe reason categories may include:

```text
missing_client_config
state_mismatch
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
```

These are categories, not raw provider payload dumps.

---

## Skip policy

Configured verification must skip when explicit opt-in gates are not all enabled.

Skip is correct when:

```text
- normal mock-safe development is running
- credentials are absent
- optional Google configuration is absent
- real API gates are disabled
- endpoint verification is disabled
```

Skip is not a release failure when the milestone only requires mock-safe documentation and guard checks.

---

## Non-exposure policy

Never print or persist these values during configured verification:

```text
- access tokens
- refresh tokens
- client secrets
- authorization codes
- raw Google Health payloads
- local token files
- private absolute paths
```

This includes:

```text
- API responses
- app UI
- normal logs
- check output
- docs
- release packages
```

---

## Day4 status

This checklist is the v1.2.0 Day4 configured verification baseline.

Expected check output:

```text
[v120-google-health-configured-verification-day4-check] OK
```
