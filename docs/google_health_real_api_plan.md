# Google Health Real API Integration Plan

## Purpose

This document defines the implementation boundary for connecting Daily Rhythm Companion to a real Google-side health/sleep data source.

As of the v0.24.0 release, Daily Rhythm Companion has validated the current Google Health real sleep path with the minimal `googlehealth.sleep.readonly` scope. The app can fetch Google Health sleep dataPoints, normalize them into `SleepSummary`, display real sleep data in Flutter, and reflect that summary in advice generation.

v0.25.0 keeps the real request boundary guarded while focusing on OAuth/setup cleanup:

- OAuth readiness
- token storage and reset
- reauthorization workflow
- minimal sleep-scope guidance
- safe preview vs guarded real request checks
- release wording / public claims

## Current State

Implemented today:

- `GET /google-health/status`
- `GET /google-health/diagnostics`
- `GET /google-health/self-check`
- `GET /google-health/connect`
- `GET /google-health/callback`
- OAuth credentials loading from `credentials.json`
- OAuth state generation and validation
- guarded token exchange boundary
- local token storage boundary
- token expiry detection and guarded refresh boundary
- Google Health API client request boundary
- Google Health session boundary connecting refresh and API request preparation
- `SLEEP_PROVIDER=google_health` guarded sleep source/provider boundary
- `/sleep/summary` safe responses for `needs_auth`, refresh-required, API-disabled, unsafe-config, and unavailable states
- runtime guard that blocks real API requests when placeholder endpoint settings are still configured
- configurable Google Health sleep API path and API timeout values
- non-sensitive diagnostics endpoint that classifies local setup gates
- non-sensitive self-check endpoint that runs the guarded source/session/API-client smoke path
- v0.22.0 verified endpoint/path gate for `https://health.googleapis.com/v4` and `/users/me/dataTypes/sleep/dataPoints`
- v0.22.0 request preview for the Google Health `sleep` dataPoints list shape
- v0.22.0 guarded first real HTTP smoke path with explicit local opt-in
- v0.22.0 safe provider error category mapping, including `provider_error_category=permission_denied` for the current 403 boundary
- v0.23.0 Day1 scope-check endpoint that compares configured OAuth scopes and stored token scopes without refreshing tokens or sending Google Health API requests

Validated as of v0.24.0:

- provider approval/scope state allowed sleep data retrieval with the minimal sleep scope
- the configured sleep scope and stored token included `googlehealth.sleep.readonly`
- a real account returned HTTP 200 for sleep dataPoints
- Google Health raw sleep intervals were normalized into `SleepSummary`
- Flutter and advice generation used the normalized real sleep summary

Still intentionally limited:

- real API requests remain disabled by default
- token reset and reauthorization are local developer workflows
- raw health payloads should not be stored or exposed unnecessarily
- future versions should improve user-facing connection UX

## v0.23.0 Day1 Scope Troubleshooting Boundary

`GET /google-health/scope-check` compares the configured OAuth scopes with the locally stored token scope. It is designed to help investigate the current `403 permission_denied` result before retrying real sleep requests.

The check is intentionally non-requesting:

- does not perform OAuth
- does not refresh tokens
- does not call Google Health
- does not expose token values, refresh tokens, client secrets, or Authorization headers

Expected local flow:

1. Confirm the official Google Health sleep read scope.
2. Set `GOOGLE_HEALTH_REQUIRED_SLEEP_SCOPE`.
3. Include the same scope in `GOOGLE_HEALTH_OAUTH_SCOPES`.
4. Reconnect/re-authorize so the stored token is minted with the new scope.
5. Run `scripts/smoke_google_health_scope_check.py --require-scope-ready`.

Only after the scope check is ready should another guarded real request be considered. Real request flags must still default to OFF.

## Release Wording Rule

After v0.24.0, user-facing docs may claim the current Google Health sleep dataPoints flow has been validated for the local MVP path. Keep the wording scoped and safety-aware:

```txt
Google Health real sleep dataPoints retrieval has been validated for the current minimal sleep-scope path.
Real API requests remain guarded and disabled by default for normal development.
```

Do not overstate the integration as a full production auth experience until:

1. token refresh and reauthorization behavior are documented for normal users,
2. user-facing reconnect states exist in the app,
3. no-data, permission, expired-token, and provider-error cases are consistently displayed,
4. raw health data is not stored or exposed unnecessarily,
5. the release package excludes credentials, token files, and local data.

## Proposed Backend Boundary

Recommended file layout:

```txt
backend/app/services/
  google_health_api_client.py          # HTTP boundary for the Google-side API
  google_health_session.py             # Coordinates token refresh and API client use
  google_health_sleep_source.py        # App-facing sleep summary boundary
  google_health_token_refresh.py       # Refresh expired access tokens
  google_health_token_store.py         # Local token storage boundary

backend/app/services/sleep_providers/
  google_health.py                     # SleepProvider implementation for /sleep/summary

Future real-payload work may add:

backend/app/services/
  google_health_sleep_normalizer.py    # Convert provider response into SleepSummary fields
```

Do not let `/sleep/summary` call OAuth/token exchange logic directly. The provider should only depend on a token reader/refresh boundary and a sleep API client boundary.

## Proposed Flow

```txt
Flutter UI
  -> GET /sleep/summary
    -> sleep_summary_service.get_sleep_summary(config)
      -> create_sleep_provider(config)
        -> GoogleHealthSleepProvider
          -> token store loads local token metadata
          -> refresh boundary refreshes token if needed
          -> API client fetches sleep records for target date
          -> normalizer converts response to SleepSummary
```

When token data is missing, expired without refresh support, or sleep data is unavailable, return a graceful unavailable summary instead of raising a generic 500.

Recommended unavailable response shape:

```json
{
  "date": "YYYY-MM-DD",
  "total_sleep_minutes": 0,
  "efficiency": null,
  "deep_sleep_minutes": null,
  "rem_sleep_minutes": null,
  "awake_minutes": null,
  "source": "google_health",
  "available": false,
  "message": "Google Health sleep data is not available yet. Connect health data or try again later."
}
```

## Provider Naming

Keep current release-facing provider recommendations until the real API works:

```env
SLEEP_PROVIDER=mock
```

or:

```env
SLEEP_PROVIDER=wearable_stub
```

Available guarded integration boundary:

```env
SLEEP_PROVIDER=google_health
```

This mode is acceptable for local boundary testing because real refresh and real API calls are disabled by default. Do not describe it as completed real sleep-data retrieval until actual endpoint/scope validation succeeds.

## Token Handling Rules

Token values are sensitive.

Rules:

- never print `access_token`, `refresh_token`, `id_token`, or authorization code
- never return raw token values from API responses
- never include token files in release packages
- keep token files under `backend/local_data/`
- keep `credentials.json` local only
- prefer explicit status/error codes for missing or expired tokens

## Refresh Boundary

Before the sleep provider is enabled, define a refresh boundary with stable outcomes:

```txt
valid_access_token
missing_token
expired_without_refresh_token
refresh_disabled
refresh_failed
refreshed
```

The sleep provider can then handle these outcomes without knowing OAuth details.

## Normalization Boundary

The normalizer should accept provider-specific sleep records and return the app's stable `SleepSummary` model.

Rules:

- keep provider-specific response shapes outside API responses
- make `available=false` explicit when no usable sleep data exists
- keep `source="google_health"`
- map unknown stage values safely instead of failing
- prefer deterministic behavior for tests

## Error Handling

Expected non-fatal cases should return unavailable sleep summaries:

- credentials not configured
- token file missing
- token expired and refresh unavailable
- no sleep records for selected date
- provider API returns an empty successful response

Fatal/internal cases may raise and become API errors:

- malformed local token file
- unexpected provider response shape after a successful HTTP call
- local file permission errors

## Test Plan

Before enabling `SLEEP_PROVIDER=google_health`, add tests or smoke scripts for:

- token store loads saved tokens without exposing values
- expired token detection
- refresh request preview or guarded refresh request
- sleep normalizer with full sleep data
- sleep normalizer with missing optional fields
- sleep normalizer with empty records
- provider returns unavailable summary when token is missing
- `/sleep/summary` returns `source="google_health"` only when explicitly configured

## Implementation Steps

### Completed in v0.18.0

- token read / expiry / refresh boundary
- API client request boundary
- session boundary connecting refresh and API client behavior
- Google Health sleep source/provider boundary
- `/sleep/summary` provider boundary checks
- release-facing wording that keeps real API claims guarded

### Completed in v0.19.0 Day1

- add Google Health runtime guard for real API request settings
- block outbound API calls when `GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1` but `GOOGLE_HEALTH_API_BASE_URL` is still the placeholder
- move sleep API path and API timeout into environment-backed config
- expose non-sensitive guard status through `GET /google-health/status`

### Completed in v0.19.0 Day2

- add `GET /google-health/diagnostics` as a local setup self-check endpoint
- classify Google Health setup states without exposing credentials, tokens, authorization codes, or raw health data
- include safe token metadata such as stored/expired/refresh-available booleans only
- add diagnostics smoke check for mock mode, missing credentials, missing auth, API disabled, API blocked, and ready-for-real-API states

### Completed in v0.19.0 Day3

- add `GET /google-health/self-check` to run the guarded Google Health source/session/API-client smoke path
- return safe session/request metadata only; never return tokens, Authorization headers, client secrets, or raw health payloads
- confirm API-disabled and unsafe-config paths do not attempt HTTP
- add self-check smoke script for mock, missing credentials, missing auth, API-disabled, and API-blocked states

### Completed in v0.19.0 Day4

- add `scripts/check_v019_release_readiness.py` as a pre-release aggregator for the Google Health guarded real-API path
- verify required v0.19.0 files, safe `.env.example` defaults, guarded README wording, diagnostics/self-check docs, and Python compile health
- run the existing Google Health boundary, runtime guard, diagnostics, and self-check scripts from one release-readiness command

### Next implementation step

- use diagnostics and self-check output to verify local setup gates before enabling real API flags
- confirm the actual Google-side sleep endpoint and required scopes
- run real token exchange / refresh with a local test account
- add payload normalizer after observing the real response shape
- keep raw provider payloads out of app-facing API responses
- update app README if needed
- update Gumroad / BOOTH only after real sleep summary retrieval is confirmed

## Release Gate

Do not update Gumroad / BOOTH messaging for Google Health until all of these are true:

- real OAuth token exchange confirmed
- real or documented token refresh behavior confirmed
- real sleep summary fetch confirmed
- `/sleep/summary` returns a useful real-data or unavailable response
- release package check passes
- Google Health boundary check passes


## v0.22.0 safety additions

- Keep `GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0` by default.
- Keep `GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0` until the endpoint and OAuth scope are checked against official provider documentation.
- Keep `GOOGLE_HEALTH_REAL_API_OPT_IN=0` until endpoint/scope verification and the token refresh check are complete.
- Use `GET /google-health/token-refresh-check` to verify the refresh boundary without requesting sleep API data.
- Only the narrow final real-request smoke should set all three real API gates to `1` locally.

## v0.22.0 Day3 verified-endpoint gate

Day3 verifies the local configuration state immediately after the operator has confirmed the official endpoint and OAuth scope, but before any real sleep API request is allowed.

Local `.env` target for this gate:

```env
SLEEP_PROVIDER=google_health
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=1
GOOGLE_HEALTH_API_BASE_URL=<official verified base URL>
GOOGLE_HEALTH_SLEEP_API_PATH=<official verified sleep summary path>
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=1
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
```

Expected `GET /google-health/preflight` API gate fields:

```txt
endpoint_verified=True
api_base_url_placeholder=False
real_api_requests_enabled=False
real_api_opt_in=False
real_api_requests_allowed=False
ready_for_real_api_request=False
```

Expected `GET /google-health/self-check` fields:

```txt
diagnostics_status=api_disabled
real_http_attempted=False
safe_to_use_sleep_summary=False
```

Run the Day3 smoke after restarting the backend:

```powershell
python scripts\smoke_google_health_verified_endpoint_gate.py --base-url http://127.0.0.1:8000
```

This gate intentionally proves that endpoint/scope verification metadata can be set without accidentally sending a real Google Health sleep API request. The first real request must remain a separate, narrow smoke that explicitly sets both `GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1` and `GOOGLE_HEALTH_REAL_API_OPT_IN=1` locally.

## v0.22.0 Day4 sleep dataPoints request preview

Day4 adds a preview-only request shape for the Google Health `sleep` data type
through the `users.dataTypes.dataPoints.list` style endpoint.

Locally verified candidate values:

```env
GOOGLE_HEALTH_API_BASE_URL=https://health.googleapis.com/v4
GOOGLE_HEALTH_SLEEP_API_PATH=/users/me/dataTypes/sleep/dataPoints
GOOGLE_HEALTH_SLEEP_FILTER_QUERY_PARAM=filter
```

The default real-request gates remain disabled:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
```

With these values, `/google-health/self-check` should prepare a request preview
for the configured sleep dataPoints endpoint and the Google Health `filter` query
parameter, while keeping `real_http_attempted=false` and returning `api_disabled`
until a later explicit first-real-request smoke.

Day4 still does not normalize raw Google Health sleep payloads. The response
payload may contain personal health data, so the self-check keeps returning only
safe status and request preview metadata.

## v0.22.0 Day5: guarded first real sleep request smoke

Day5 adds a separate real-request smoke script for the first narrow Google Health
sleep `dataPoints.list` request.

The real request still requires both layers of opt-in:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
```

and the operator must also run the smoke with:

```powershell
python scripts\smoke_google_health_real_sleep_request.py --base-url http://127.0.0.1:8000 --allow-real-request
```

The smoke verifies that the request reached the HTTP boundary while keeping the
self-check response safe. It does not require a successful sleep payload yet;
non-2xx provider responses are acceptable during endpoint/scope/query
verification as long as the request was not blocked by the local guard and a
provider HTTP status was captured.

After the smoke, return the runtime flags to safe defaults:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
```

## v0.22.0 Day6: provider error boundary classification

Day6 keeps the real Google Health response payload behind the API-client
boundary while exposing only safe troubleshooting metadata through
`/google-health/self-check`.

When Google Health returns a non-2xx response, the backend now keeps the raw
provider JSON inside the internal API-client result/logging boundary and maps it
to safe fields such as:

```txt
status_code=403
error=http_error
provider_error_category=permission_denied
```

The self-check response must still not expose raw provider payload fields such
as `data`, `response`, `raw_payload`, `payload`, or `provider_response`.

For local troubleshooting only, enable the same Day5 real request gates and run:

```powershell
python scripts\smoke_google_health_provider_error_boundary.py --base-url http://127.0.0.1:8000 --allow-real-request
```

Then return the runtime flags to safe defaults:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
```

A 401/403 result is still not considered real sleep-data success. It is only a
useful boundary signal that the app reached Google Health and classified the
provider-side auth/scope/project error without leaking the raw response to app
APIs.

## v0.22.0 Day7: permission_denied troubleshooting checklist

Day7 does not try to hide or "fix" a Google Health `403` locally. A `403`
means the app reached the provider HTTP boundary, but Google rejected the
request. The backend should continue to return a safe unavailable result while
operators inspect provider configuration.

Current expected boundary signal:

```txt
status_code=403
error=http_error
provider_error_category=permission_denied
source_status=unavailable
real_http_attempted=True
safe_to_use_sleep_summary=False
```

The common causes to check are:

1. Google Health API is not enabled for the Google Cloud project used by the
   OAuth client.
2. The OAuth consent screen does not include the required Google Health sleep
   read scope.
3. The local token was issued before the sleep scope was added, so the user must
   reconnect/re-authorize and mint a new refresh token.
4. The Google account is not configured as an allowed test user, or the app is
   not approved for the requested sensitive/restricted scope.
5. The OAuth client ID/secret in `credentials.json` belongs to a different
   project than the project where the Health API and consent screen were
   configured.
6. The request path or query parameter names are still slightly wrong even
   though the base URL is correct.

Use the Day7 smoke only during a narrow troubleshooting run with the Day5 real
request gates enabled:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
```

```powershell
python scripts\smoke_google_health_permission_denied_troubleshooting.py --base-url http://127.0.0.1:8000 --allow-real-request
```

After the smoke, return the runtime flags to safe defaults:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
```

A passing Day7 smoke still does **not** mean real sleep retrieval works. It only
means the app can classify the current provider-side rejection and present a
safe, concrete troubleshooting checklist without exposing raw provider payloads
through app APIs.


## v0.23.0 Day2 scope-check refinement

Day2 refines the v0.23.0 scope readiness check after the first real permission retest.

Observed result:

```txt
GOOGLE_HEALTH_REQUIRED_SLEEP_SCOPE=https://www.googleapis.com/auth/fitness.sleep.read
OAuth reconnect succeeded
token includes fitness.sleep.read
Google Health real sleep request still returns 403 permission_denied
```

The scope-check endpoint now separates the required sleep-read scope from optional identity scopes. Missing `email` / `profile` metadata in the stored token scope field no longer blocks `ready_for_permission_retest` when the required sleep-read scope is present.

Expected ready state:

```txt
missing_required_scopes_in_token=[]
ready_for_permission_retest=True
reconnect_recommended=False
```

A persistent `403 permission_denied` after this state should be investigated as a Google Health API project access, OAuth consent approval, test-user, restricted-scope, or endpoint/query issue rather than a simple missing sleep-read token scope.

## v0.23.0 Day3 permission retest readiness

v0.23.0 Day3 adds a local readiness endpoint before repeating a guarded real request after `403 permission_denied`.

```txt
GET /google-health/permission-retest-readiness
```

This endpoint does not call Google Health API. It combines the v0.23 scope-check result with local operator confirmations for the non-code checks most likely to affect `403`:

- Google Health API enabled in the same Google Cloud project as `credentials.json`
- OAuth consent screen includes the configured sleep read scope
- signed-in account is a test user or the app is approved for the requested scope
- endpoint/path/query parameters still match the official Google Health docs

The manual confirmation flags are intentionally separate from the real request gates:

```env
GOOGLE_HEALTH_CLOUD_API_ENABLED_CONFIRMED=0
GOOGLE_HEALTH_OAUTH_CONSENT_SLEEP_SCOPE_CONFIRMED=0
GOOGLE_HEALTH_OAUTH_TEST_USER_CONFIRMED=0
GOOGLE_HEALTH_ENDPOINT_QUERY_CONFIRMED=0
```

Even when all are set to `1`, real API calls remain disabled unless the v0.22 runtime gates are also explicitly enabled:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=1
GOOGLE_HEALTH_REAL_API_OPT_IN=1
```

This keeps the permission-denied investigation explicit and prevents accidental real health-data requests.


## v0.23.0 Day4 historical sleep filter query correction

v0.23.0 Day4 corrects the sleep `dataPoints.list` query shape after checking the official Google Health reference. The endpoint/path remains the same:

```env
GOOGLE_HEALTH_API_BASE_URL=https://health.googleapis.com/v4
GOOGLE_HEALTH_SLEEP_API_PATH=/users/me/dataTypes/sleep/dataPoints
```

At that checkpoint, the date range moved from separate `startTime` / `endTime` query parameters to a single `filter` query parameter using `sleep.interval.end_time`. The v2.0.0 E-2 correction below supersedes that UTC-date choice for current DRC execution:

```txt
filter=sleep.interval.end_time >= "2026-05-05T00:00:00Z" AND sleep.interval.end_time < "2026-05-06T00:00:00Z"
```

The local configuration is therefore:

```env
GOOGLE_HEALTH_SLEEP_FILTER_QUERY_PARAM=filter
GOOGLE_HEALTH_ENDPOINT_QUERY_CONFIRMED=1
```

At that checkpoint, the preview smoke expected only the `filter` query key and verified a UTC sleep end-time range. Current v2.0.0 execution instead follows the E-2 civil end-date contract below. Real requests remain behind the same explicit opt-in gates:

```env
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
```

Run the preview smoke after restarting the backend:

```powershell
python scripts\smoke_google_health_sleep_request_preview.py --base-url http://127.0.0.1:8000
```

Only after the preview shows the `filter` query shape should the guarded real request smoke be repeated with temporary local opt-in.

## v2.0.0 Commit E-2 sleep normalization and civil-date query correction

Commit E-2 prepares the current v2.0.0 real-evidence path without performing or accepting a real Google Health run.

The current Google Health v4 sleep list contract supports the sleep-specific civil end-date field. DRC now selects sleep sessions that ended on the user's target civil date:

```txt
filter=sleep.interval.civil_end_time >= "2026-05-05" AND sleep.interval.civil_end_time < "2026-05-06"
```

This avoids treating UTC midnight as the user's day boundary for sleep that ends in the local morning.

Google Health sleep data points may include output-only summary metrics. DRC normalization now uses these provider values when present:

```text
sleep.summary.minutesAsleep
sleep.summary.minutesAwake
sleep.summary.stagesSummary[type=DEEP]
sleep.summary.stagesSummary[type=REM]
```

The observed session interval remains required for the app-facing start/end range and for safety caps. Interval duration is only a fallback when usable provider summary metrics are unavailable. Raw Google Health payloads and precise personal evidence remain outside public logs and commits.

Commit E-2 does not call Google Health, read local OAuth tokens, start the backend or Web UI, inspect screenshots, accept `real_google_health_sleep_data`, populate the accepted private evidence manifest, build the final fixed zip, or create the v2.0.0 tag.
