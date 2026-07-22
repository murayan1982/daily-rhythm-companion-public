# Google Health Setup and OAuth Guide

## Purpose

This guide is for a configured local/demo operator who wants to verify the Daily Rhythm Companion real health-data path safely.

The normal development default remains mock-safe.

```text
Default path:
mock sleep data → local backend/app checks → no Google credentials required
```

The configured path is opt-in only.

```text
Configured path:
operator-controlled Google health data source → guarded backend path → normalized SleepSummary-like response
```

This guide does not make Daily Rhythm Companion a production hosted consumer health service.

---

## Naming note

Daily Rhythm Companion uses "Google Health" as the project-facing health integration boundary.

Some current implementation or reference material may still involve Google Fit REST API concepts.

As of this guide, Google Fit APIs are deprecated and scheduled for end of service in late 2026. Treat the current configured path as a guarded local/demo integration path, not a long-term production platform commitment.

Future milestones should decide whether the project continues with the existing configured demo path, migrates Android-side data access toward Health Connect, or keeps Google Health as an abstract provider boundary with multiple possible implementations.

---

## Required operator mindset

Before enabling a real-data path, confirm all of the following:

```text
- You are using a local/demo environment that you control.
- You understand which Google account is being authorized.
- You understand which scopes are being requested.
- You can revoke access if needed.
- You will not paste tokens, authorization codes, client secrets, or raw payloads into public logs or issues.
- You can return to mock-safe mode at any time.
```

---

## High-level setup sequence

Use this as the public first-read setup map.

```text
1. Keep mock-safe green first.
2. Review docs/google_health_real_api_opt_in.md.
3. Prepare the Google-side project and OAuth consent configuration.
4. Create the OAuth client needed by the local/demo flow.
5. Configure local environment variables outside committed source files.
6. Enable explicit opt-in gates only for the configured test run.
7. Start the backend/app.
8. Complete the authorization flow.
9. Verify capability/status output.
10. Verify normalized sleep summary output.
11. Return to mock-safe mode after the test.
```

Do not start with real-data configuration.
Always prove the mock path works first.

---

## Google-side preparation checklist

The exact Google API Console / Google Cloud Console UI may change over time, so treat this as a checklist rather than a click-by-click promise.

```text
- Choose or create a Google Cloud project for this local/demo test.
- Confirm the relevant fitness/health API capability for the current implementation path.
- Configure the OAuth consent screen.
- Keep the app in an appropriate testing state for local/demo use.
- Add only the test users needed for the configured run.
- Request the minimum scopes needed by the current sleep-data path.
- Create an OAuth client appropriate for the current local/demo flow.
- Register redirect URIs/origins required by the backend flow.
```

Use official Google documentation as the source of truth for OAuth requirements and policy changes.

Reference starting points:

```text
https://developers.google.com/identity/protocols/oauth2
https://developers.google.com/identity/protocols/oauth2/web-server
https://developers.google.com/identity/protocols/oauth2/native-app
https://developers.google.com/fit/rest
https://developer.android.com/health-and-fitness/health-connect/migration/fit
```

---

## Local configuration checklist

Keep real credentials out of committed files.

Recommended pattern:

```text
- Keep backend/env_profiles/mock_safe.env unchanged as the safe baseline.
- Put local real/demo values in a private local env file that is ignored by git.
- Do not commit client secrets, refresh tokens, access tokens, authorization codes, or raw API responses.
- Prefer short test sessions.
- Restore mock-safe mode after the configured run.
```

The mock-safe profile should keep real Google Health gates disabled:

```text
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

A configured real/demo run may require enabling explicit gates in a private local environment:

```text
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1
```

Only enable those gates when you intentionally run the configured path.

---

## OAuth flow expectations

The local/demo flow should be understandable to the operator.

Expected safe behavior:

```text
- The app/backend can explain that authorization is required.
- The operator is sent through a Google authorization screen, not asked to paste passwords.
- The backend validates returned state before token exchange.
- The backend does not expose tokens in API responses.
- The backend does not log raw tokens or raw Google payloads.
- The app/backend can explain reconnect-required or unavailable states.
```

Unsafe behavior:

```text
- Real API call happens while mock-safe flags are disabled.
- Token or client secret appears in a response body.
- Token or client secret appears in normal logs.
- Raw Google payload is shown to the app UI.
- Authorization state mismatch is ignored.
- The app gives medical or diagnostic advice based on sleep data.
```

---

## Verification sequence

After configuration, verify in this order:

```text
1. Run mock-safe checks.
2. Run the setup guidance check.
3. Start the backend with private configured environment values.
4. Confirm capability/status output explains the configured state.
5. Complete OAuth authorization.
6. Confirm the backend reports a connected or authorized state.
7. Fetch sleep summary through the app-facing endpoint.
8. Confirm the response is normalized and minimal.
9. Confirm no token, secret, raw payload, or machine path appears in output.
10. Return to mock-safe configuration.
11. Re-run mock-safe checks.
```

---

## Expected user-facing language

Use calm source/status wording.

Good examples:

```text
- Google Health is not configured.
- Authorization is required.
- Reconnect is required.
- Real data is unavailable, so mock data is being used.
- Sleep summary source: mock
- Sleep summary source: google_health
```

Avoid:

```text
- diagnostic wording
- medical conclusions
- guarantees about sleep improvement
- presenting old history as today's sleep
- exposing technical secrets or raw payloads
```

---

## Day2 status

This guide is the v1.2.0 Day2 setup/OAuth guidance baseline.

Expected check output:

```text
[v120-google-health-setup-day2-check] OK
```
