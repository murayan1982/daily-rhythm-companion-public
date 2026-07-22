# Google Health Non-Exposure Checklist

## Purpose

This checklist defines the v1.2.0 Google Health non-exposure sweep.

It is intended to keep public Google Health docs, v1.2.0 internal planning docs, and v1.2.0 validation scripts free of accidentally committed sensitive values.

The normal default remains mock-safe.

```text
mock-safe mode → no credentials → no accidental real API calls
```

Day6 does not perform real Google Health API calls.

---

## What must never be exposed

Do not expose real values for:

```text
- access tokens
- refresh tokens
- client secrets
- authorization codes
- API keys
- raw Google Health payloads
- local token files
- private absolute paths
- provider debug dumps
```

This applies to:

```text
- app UI
- API responses
- normal logs
- check output
- public docs
- internal planning docs that may be shared
- release packages
```

---

## Safe things to document

These are safe to document when they are placeholders, categories, or labels:

```text
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS
GOOGLE_HEALTH_REAL_API_OPT_IN
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED
```

Safe state labels:

```text
not_configured
authorization_required
connected
reconnect_required
unavailable
fallback_to_mock
configured_skip
```

Safe source labels:

```text
mock
google_health
fallback
unavailable
```

Safe reason categories:

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

---

## Source-tree sweep targets

Day6 source-tree sweep should inspect the current Google Health onboarding docs and v1.2.0 validation checks.

Core docs:

```text
roadmap.md
docs/google_health_real_api_opt_in.md
docs/google_health_setup_oauth.md
docs/google_health_reconnect_reset.md
docs/google_health_configured_verification.md
docs/google_health_error_wording.md
docs/google_health_non_exposure_checklist.md
```

Internal v1.2.0 docs:

```text
docs/internal/v120_google_health_onboarding_day1.md
docs/internal/v120_google_health_setup_day2.md
docs/internal/v120_google_health_reconnect_reset_day3.md
docs/internal/v120_google_health_configured_verification_day4.md
docs/internal/v120_google_health_error_wording_day5.md
docs/internal/v120_google_health_non_exposure_day6.md
```

v1.2.0 checks:

```text
scripts/check_v120_google_health_onboarding_day1.py
scripts/check_v120_google_health_setup_day2.py
scripts/check_v120_google_health_reconnect_reset_day3.py
scripts/check_v120_google_health_configured_verification_day4.py
scripts/check_v120_google_health_error_wording_day5.py
scripts/check_v120_google_health_non_exposure_day6.py
```

---

## Forbidden value patterns

The Day6 check should reject likely real values such as:

```text
- Bearer token literals
- Google OAuth access token prefixes
- Google API key literals
- OpenAI-style secret keys accidentally pasted nearby
- refresh-token-looking values
- private Windows absolute paths under user/work/dev/temp locations
- PEM private key blocks
```

The check should not reject safe placeholder names or policy text such as "access tokens must not be exposed."

---

## Mock-safe profile expectation

The committed mock-safe profile must keep Google Health real API gates disabled:

```text
SLEEP_PROVIDER=mock
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

---

## Operator rule

If a real value is needed for configured local/demo testing:

```text
- keep it in a private local environment
- keep it out of committed files
- keep it out of check output
- keep it out of issue comments and public screenshots
- rotate/revoke it if it was accidentally exposed
```

Do not place real values into docs or check fixtures.

---

## Day6 status

This checklist is the v1.2.0 Day6 non-exposure sweep baseline.

Expected check output:

```text
[v120-google-health-non-exposure-day6-check] OK
```
