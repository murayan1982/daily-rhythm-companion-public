# Google Health Onboarding Readiness Checklist

## Purpose

This checklist summarizes the v1.2.0 Google Health real-use onboarding readiness baseline.

v1.2.0 focuses on making the guarded configured local/demo path clearer and safer.

It does not claim production hosted consumer-service readiness.

---

## Scope

v1.2.0 Google Health onboarding covers:

```text
- planning baseline
- setup/OAuth guidance
- reconnect/reset guidance
- configured verification checklist
- unavailable/error wording
- non-exposure sweep
- aggregate readiness gate
```

The normal default remains mock-safe.

```text
mock-safe mode → no credentials → no accidental real API calls
```

---

## Required public docs

The v1.2.0 onboarding baseline expects these public docs:

```text
docs/google_health_real_api_opt_in.md
docs/google_health_setup_oauth.md
docs/google_health_reconnect_reset.md
docs/google_health_configured_verification.md
docs/google_health_error_wording.md
docs/google_health_non_exposure_checklist.md
docs/google_health_onboarding_readiness.md
```

---

## Required internal guardrail docs

The v1.2.0 onboarding baseline expects these internal guardrail docs:

```text
docs/internal/v120_google_health_onboarding_day1.md
docs/internal/v120_google_health_setup_day2.md
docs/internal/v120_google_health_reconnect_reset_day3.md
docs/internal/v120_google_health_configured_verification_day4.md
docs/internal/v120_google_health_error_wording_day5.md
docs/internal/v120_google_health_non_exposure_day6.md
docs/internal/v120_google_health_onboarding_readiness_day7.md
```

---

## Required checks

The v1.2.0 onboarding baseline expects these checks:

```text
scripts/check_v120_google_health_onboarding_day1.py
scripts/check_v120_google_health_setup_day2.py
scripts/check_v120_google_health_reconnect_reset_day3.py
scripts/check_v120_google_health_configured_verification_day4.py
scripts/check_v120_google_health_error_wording_day5.py
scripts/check_v120_google_health_non_exposure_day6.py
scripts/check_v120_google_health_onboarding_readiness_day7.py
```

---

## Aggregate check command

Run the aggregate readiness check from the project root:

```powershell
python scripts\check_v120_google_health_onboarding_readiness_day7.py
```

Expected output includes:

```text
[v120-google-health-onboarding-day1-check] OK
[v120-google-health-setup-day2-check] OK
[v120-google-health-reconnect-reset-day3-check] OK
[v120-google-health-configured-verification-day4-check] OK
[v120-google-health-error-wording-day5-check] OK
[v120-google-health-non-exposure-day6-check] OK
[v120-google-health-onboarding-readiness-day7-check] OK
```

---

## Optional configured environment check

The aggregate check can also pass through configured environment validation:

```powershell
python scripts\check_v120_google_health_onboarding_readiness_day7.py --configured-env
```

In a mock-safe environment, this should skip configured verification without failing:

```text
[v120-day4-configured-skip] Google Health configured verification requires explicit opt-in gates
[v120-google-health-onboarding-readiness-day7-check] OK
```

If explicit opt-in gates are intentionally enabled in a private configured environment, the aggregate check may report:

```text
[v120-day4-configured-env] explicit opt-in gates enabled
[v120-google-health-onboarding-readiness-day7-check] OK
```

The aggregate check still must not perform real Google Health API calls.

---

## Explicit opt-in gates

Configured real/demo verification requires all of these gates:

```text
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1
```

The committed mock-safe profile must keep them disabled:

```text
SLEEP_PROVIDER=mock
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

---

## Readiness criteria

v1.2.0 Google Health onboarding readiness means:

```text
- setup/OAuth guidance exists
- reconnect/reset guidance exists
- configured verification guidance exists
- unavailable/error wording guidance exists
- non-exposure sweep exists
- aggregate readiness check exists
- mock-safe profile keeps real API gates disabled
- configured-only checks skip safely unless explicit opt-in gates are enabled
- no real API calls happen during normal readiness checks
- docs/checks do not expose token, secret, authorization-code, raw-payload, local-token-file, or private-path values
- wording remains non-medical and non-diagnostic
```

---

## Non-claims

v1.2.0 does not claim:

```text
- production hosted consumer-service readiness
- App Store / Google Play release readiness
- production-grade Google Health onboarding
- long-term commitment to Google Fit REST as a platform
- automatic real health-data access without explicit opt-in
- medical diagnosis or treatment advice
```

---

## Day7 status

This checklist is the v1.2.0 Day7 aggregate readiness baseline.

Expected check output:

```text
[v120-google-health-onboarding-readiness-day7-check] OK
```
