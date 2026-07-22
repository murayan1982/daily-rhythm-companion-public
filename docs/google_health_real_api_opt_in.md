# Google Health real API explicit opt-in

Daily Rhythm Companion keeps Google Health real API access disabled by default.

The v1.0 goal is not polished production onboarding. The v1.0 goal is a documented, guarded, explicit opt-in path that can be verified in a configured local/demo environment.

## Safe default

Normal development should use:

```env
SLEEP_PROVIDER=mock
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

In this state:

- real Google Health HTTP requests must not run
- `/demo/status` can report capability state
- `/sleep/summary` should use mock or safe fallback behavior
- no token, secret, raw payload, or local file path should be exposed

## Explicit opt-in principle

Use this rule:

```txt
Safe default + documented explicit opt-in.
Guarded does not mean unimplemented.
```

Real API execution should require all relevant operator-controlled gates, not just a single accidental environment variable.

## Configured verification environment

A configured local/demo environment may set values like:

```env
SLEEP_PROVIDER=google_health
GOOGLE_HEALTH_CREDENTIALS_FILE=<local-credentials-file>
GOOGLE_HEALTH_REDIRECT_URI=<configured-redirect-uri>
GOOGLE_HEALTH_OAUTH_SCOPES=https://www.googleapis.com/auth/googlehealth.sleep.readonly
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=1
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1
```

Only use real values in local `.env` or a local secret manager. Do not commit them.

## v1.0 verification checklist

Before v1.0 final release readiness, verify or document the blocker reason for:

```txt
1. Google Health setup docs exist.
2. Safe default keeps real requests disabled.
3. Explicit opt-in flags are required before real requests.
4. Endpoint and scope readiness are documented.
5. Real sleep data can be fetched in a configured environment, or blocker reason is documented.
6. Real sleep data can be normalized into the SleepSummary contract, or blocker reason is documented.
7. /sleep/summary can return Google Health-backed SleepSummary when configured, or blocker reason is documented.
8. Failure states return safe unavailable/fallback responses.
9. App-facing responses do not expose tokens, secrets, raw payloads, local file paths, Authorization headers, or local machine paths.
10. Release package and public repo do not include local credentials, token files, local_data, cache, or build artifacts.
```

## Flutter app responsibility

The Flutter app should display backend-provided state and guidance. It should not perform Google Health OAuth, token refresh, provider HTTP requests, or raw credential handling directly.

## Post-v1.0 scope

Post-v1.0 work can improve:

- polished real-use onboarding
- better reconnect/reset UX
- safer guided real-data testing
- clearer end-user setup instructions
- production hosting and credential storage
