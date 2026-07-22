# Google Health Reconnect and Reset Guide

## Purpose

This guide explains how a configured local/demo operator should recover from Google Health authorization and data-access problems.

The default remains mock-safe.

```text
mock-safe mode → no Google credentials → no accidental real API calls
```

This guide does not add production hosted health-service behavior.
It documents safe recovery expectations for the guarded local/demo path.

---

## Operator rule

When the real-data path is confusing, unsafe, or unavailable, return to mock-safe mode first.

```text
SLEEP_PROVIDER=mock
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

Then re-enable configured real/demo gates only when intentionally testing that path.

---

## Recovery state model

Use a small, understandable state model for app/backend behavior.

```text
not_configured
authorization_required
connected
reconnect_required
unavailable
fallback_to_mock
```

More detailed backend reasons may be logged or surfaced safely as non-secret categories:

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
```

Do not expose access tokens, refresh tokens, client secrets, authorization codes, or raw provider payloads in these states.

---

## State meanings and operator actions

### not_configured

Meaning:

```text
Google Health real-use configuration is missing or disabled.
```

Likely causes:

```text
- SLEEP_PROVIDER is still mock.
- OAuth client values are missing.
- redirect URI/config is missing.
- explicit opt-in gates are disabled.
```

Operator action:

```text
- Keep mock-safe mode if real data is not needed.
- If running the configured path, review docs/google_health_setup_oauth.md.
- Confirm private local env values are loaded.
- Confirm explicit opt-in gates are enabled only for the configured run.
```

User-facing wording:

```text
Google Health is not configured.
```

---

### authorization_required

Meaning:

```text
Configuration exists, but the operator has not completed authorization yet.
```

Likely causes:

```text
- no valid stored authorization
- first-time setup
- authorization was reset intentionally
```

Operator action:

```text
- Start the local/demo authorization flow.
- Use the intended Google test account.
- Confirm requested scopes.
- Do not paste authorization codes or tokens into public logs.
```

User-facing wording:

```text
Authorization is required.
```

---

### connected

Meaning:

```text
The configured path has enough valid authorization state to attempt normalized sleep-data access.
```

Operator action:

```text
- Verify the app-facing sleep summary endpoint returns normalized, minimal fields.
- Confirm source labels are clear.
- Confirm no tokens, secrets, raw payloads, or local machine paths are exposed.
```

User-facing wording:

```text
Google Health is connected.
```

---

### reconnect_required

Meaning:

```text
The previous authorization cannot be used safely anymore.
```

Likely causes:

```text
- access token expired and refresh failed
- refresh token revoked
- scopes changed
- operator removed app access from Google account
- client configuration changed
- provider reports authorization failure
```

Operator action:

```text
- Reset local stored authorization for the demo environment.
- Re-run the authorization flow.
- Confirm the same redirect URI and OAuth client configuration are being used.
- If reconnect still fails, return to mock-safe mode.
```

User-facing wording:

```text
Reconnect is required.
```

---

### unavailable

Meaning:

```text
The provider path is configured, but data cannot currently be fetched or normalized.
```

Likely causes:

```text
- provider API request failed
- endpoint is not verified for real requests
- expected sleep data is absent
- provider response cannot be normalized safely
- optional dependency/runtime is unavailable
```

Operator action:

```text
- Check capability/status output.
- Confirm real API gates are intentionally enabled.
- Confirm endpoint verification flag is enabled only after the operator has verified the endpoint.
- Confirm the provider account actually has sleep data for the requested range.
- Return to mock-safe mode if the configured path is not needed.
```

User-facing wording:

```text
Google Health data is unavailable.
```

---

### fallback_to_mock

Meaning:

```text
The app/backend intentionally uses mock data because real data is unavailable or disabled.
```

Operator action:

```text
- Confirm the UI/API labels the source as mock.
- Do not present mock data as real Google Health data.
```

User-facing wording:

```text
Real data is unavailable, so mock data is being used.
```

---

## Reset guidance

A reset should remove only local/demo authorization state.

Safe reset expectations:

```text
- clear local stored demo tokens/authorization state
- keep committed mock-safe profile unchanged
- do not print token values before deleting them
- do not include raw token files in release packages
- re-run mock-safe checks after reset
```

Unsafe reset behavior:

```text
- committing token files
- sharing authorization codes in issue comments
- deleting unrelated project files
- logging raw provider payloads while debugging
- leaving real API gates enabled after the test
```

---

## Recommended reconnect/reset sequence

```text
1. Stop the backend/app.
2. Return to mock-safe env values.
3. Clear local/demo authorization state without printing secret values.
4. Run mock-safe checks.
5. Review docs/google_health_setup_oauth.md.
6. Re-enable configured real/demo gates in a private local env only if needed.
7. Restart backend/app.
8. Complete authorization again.
9. Confirm status is connected or authorization_required/reconnect_required with safe wording.
10. Fetch normalized sleep summary only after connected.
11. Confirm source labels and non-exposure behavior.
12. Return to mock-safe mode after the configured run.
```

---

## Non-exposure requirements

Never expose:

```text
- access tokens
- refresh tokens
- client secrets
- authorization codes
- raw Google Health payloads
- local token files
- private absolute paths
```

Safe output may include:

```text
- connection state
- safe reason category
- source label
- normalized SleepSummary-like fields
- skipped/check explanation
```

---

## Day3 status

This guide is the v1.2.0 Day3 reconnect/reset guidance baseline.

Expected check output:

```text
[v120-google-health-reconnect-reset-day3-check] OK
```
