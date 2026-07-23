# Fitbit Integration Plan


> v2.0.x maintenance note (2026-07-23): this document contains historical implementation chronology. The active Fitbit status contract is `docs/v20x_fitbit_current_state_contract.md`. Retained Fitbit OAuth/token/read code is a legacy migration/reference boundary and has not completed configured real-use operator acceptance.

## Purpose

Daily Rhythm Companion will use sleep data as one of the main context sources for daily advice generation.

The first implementation should keep Fitbit integration behind the backend so that the Flutter app does not directly depend on Fitbit APIs or token handling.

## Current Status

As of v0.15.0, the backend provides sleep summaries through a provider boundary and exposes OAuth readiness endpoints for both the legacy Fitbit route and the new Google Health readiness route. The Flutter app can display sleep summary availability, handle unavailable sleep data as a normal app state, and generate advice without pretending unavailable wearable sleep data is known.

The legacy Fitbit Web API route is no longer treated as the planned public integration path because new legacy Fitbit application registration is not available through the old Fitbit developer flow. The existing Fitbit provider should be considered a migration reference and should be removed or clearly deprecated before public release.

The backend can receive OAuth callback parameters, validate OAuth `state` values, prepare token request previews, and run guarded token exchange boundaries when explicitly enabled. The backend also includes token expiration metadata, refresh checks before Fitbit sleep API requests, Google OAuth credentials loading from `credentials.json`, Google OAuth URL generation, Google callback/state validation, and a guarded Google token exchange boundary. Sleep data API integration through the new Google Health/wearable provider is not implemented yet because the new sleep data API details, scopes, and response shape are not confirmed. v0.15.0 adds `wearable_stub` as the recommended wearable-shaped sample provider and keeps `fitbit_stub` as a deprecated compatibility alias.

Implemented providers:

```txt
mock
wearable_stub
fitbit_stub  # deprecated compatibility alias
fitbit       # legacy migration/reference provider
```

The active provider is selected with:

```env
SLEEP_PROVIDER=mock
```

or:

```env
SLEEP_PROVIDER=wearable_stub
```

`fitbit_stub` is still accepted as a deprecated compatibility alias for older local configuration, but new local configuration should use `wearable_stub`.

The legacy `fitbit` provider is kept as a migration/reference boundary only and is not the planned public integration path.

Current Fitbit OAuth/token status:

```txt
GET /fitbit/connect
  -> generates OAuth state
  -> stores state under backend/local_data/
  -> returns Fitbit authorization URL when config is available

GET /fitbit/callback?code=...&state=...
  -> validates OAuth state
  -> prepares token exchange request parts
  -> skips real token exchange by default

FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=1
  -> enables guarded real HTTP token exchange
  -> normalizes successful token responses
  -> stores token data locally under backend/local_data/

Token refresh boundary
  -> stores expires_at with token data
  -> checks whether access token is expired or near expiration
  -> prepares refresh-token request parts
  -> skips real refresh HTTP POST by default
  -> refreshes token data only when real token exchange is explicitly enabled
```

Current Fitbit sleep status:

```txt
SLEEP_PROVIDER=fitbit
  -> loads local Fitbit token data
  -> calls the Fitbit sleep/date API through backend service boundaries
  -> normalizes summary-level sleep values
  -> returns the app-facing SleepSummary shape
```

If local Fitbit token data does not exist or the Fitbit API request fails, `/sleep/summary` returns a safe unavailable summary with `available=false` and a message instead of exposing raw Fitbit payloads or token values.

Sensitive values such as Fitbit client secrets, authorization codes, access tokens, refresh tokens, Authorization header values, and raw Fitbit sleep payloads must not be returned from API responses or printed to logs.

`backend/local_data/` is local-only development data and must not be committed or included in release packages.

## v0.12.0 Fitbit Sleep API Read Boundary Status

As of v0.12.0, the backend includes a Fitbit-backed sleep provider that can be selected with:

```env
SLEEP_PROVIDER=fitbit
```

This provider is wired into the existing endpoint:

```txt
GET /sleep/summary
```

The Fitbit sleep flow is:

```txt
/sleep/summary
  -> sleep_summary_service
  -> FitbitSleepProvider
  -> FitbitTokenStore.load_tokens()
  -> Fitbit sleep/date API request boundary
  -> Fitbit sleep response normalizer
  -> app-facing SleepSummary
```

The Fitbit API client boundary is isolated in:

```txt
backend/app/services/fitbit_api_client.py
```

The Fitbit sleep read service is isolated in:

```txt
backend/app/services/fitbit_sleep_service.py
```

The Fitbit sleep response normalizer is isolated in:

```txt
backend/app/services/fitbit_sleep_normalizer.py
```

The Fitbit-backed sleep provider is isolated in:

```txt
backend/app/services/sleep_providers/fitbit.py
```

The app-facing `SleepSummary` shape now includes availability metadata:

```txt
source
available
message
```

When Fitbit sleep data is unavailable, the API should return a safe app-facing response such as:

```json
{
  "date": "2026-05-03",
  "total_sleep_minutes": 0,
  "efficiency": null,
  "deep_sleep_minutes": null,
  "rem_sleep_minutes": null,
  "awake_minutes": null,
  "source": "fitbit",
  "available": false,
  "message": "Fitbit sleep data could not be fetched because no local token exists."
}
```

The Flutter app displays this as an unavailable sleep state instead of treating `0` minutes as a real sleep measurement.

The advice prompt builder also checks `available=false` and instructs the character not to pretend exact sleep duration is known.

Raw Fitbit sleep payloads and token values should remain inside backend service boundaries.

Token refresh, production token storage, and historical sleep charts remain out of scope for v0.12.0.

## v0.13.0 Token Refresh Boundary Status

As of v0.13.0, the backend includes a Fitbit token refresh boundary.

Token data stored under local development storage now includes an expiration timestamp:

```txt
expires_at
```

Token data is stored under:

```txt
backend/local_data/fitbit_tokens.json
```

This file is local development data and must not be committed or included in release packages.

The token store can now check whether the current access token is expired or should be refreshed soon:

```txt
StoredFitbitTokens.is_access_token_expired()
StoredFitbitTokens.should_refresh_access_token()
```

The default refresh margin is 5 minutes before expiration.

The refresh request boundary prepares internal request parts for the Fitbit token endpoint:

```txt
POST https://api.fitbit.com/oauth2/token
```

Refresh request shape:

```txt
grant_type=refresh_token
refresh_token=<stored refresh token>
```

The refresh token value is internal only. Non-sensitive previews may report whether a refresh token exists, but must not expose the token value.

Real refresh exchange remains guarded by:

```env
FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=0
```

When this flag is disabled, the backend can prepare a refresh request preview but skips real HTTP POST.

When explicitly enabled, the backend can run the guarded refresh-token exchange path:

```txt
stored refresh token
  -> build internal refresh request parts
  -> build non-sensitive refresh request preview
  -> optionally call the Fitbit token endpoint
  -> normalize successful token response data
  -> store refreshed token data locally
```

The Fitbit sleep read service now checks token expiration before calling the sleep API:

```txt
SLEEP_PROVIDER=fitbit
  -> load local Fitbit token data
  -> check expires_at
  -> refresh token when expired or near expiration
  -> call Fitbit sleep/date API only after refresh succeeds or is not needed
```

If refresh is needed but fails, `/sleep/summary` returns a safe unavailable summary with `available=false` instead of calling Fitbit with an expired access token.

External refresh/token exchange error codes are intentionally stable and non-sensitive:

```txt
config_incomplete
no_refresh_token
http_request_failed
invalid_token_response
```

Sensitive values such as refresh tokens, access tokens, Fitbit client secrets, and Authorization header values must not be returned from API responses or printed to logs.

Real token refresh should only be tested with valid Fitbit OAuth credentials and locally stored real token data.

## v0.14.0 Google Health OAuth Readiness and Legacy Fitbit Deprecation Prep

As of v0.14.0, the backend includes Google Health OAuth readiness boundaries.

The legacy Fitbit Web API route is no longer treated as the planned public integration path. New legacy Fitbit application registration is not available through the old Fitbit developer flow, so the existing Fitbit provider should be considered a migration reference and not a public production integration target.

The new OAuth readiness route is separated from legacy Fitbit settings.

Google Health OAuth readiness uses:

```env
GOOGLE_HEALTH_CREDENTIALS_FILE=credentials.json
GOOGLE_HEALTH_REDIRECT_URI=http://127.0.0.1:8000/google-health/callback
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
```

The credentials file is expected to use the Google OAuth `web` client format:

```txt
web.client_id
web.client_secret
web.auth_uri
web.token_uri
web.redirect_uris
```

`credentials.json` may contain client secrets and must not be committed or included in release packages.

The backend now exposes:

```txt
GET /google-health/status
GET /google-health/connect
GET /google-health/callback
```

Current Google Health OAuth readiness flow:

```txt
GET /google-health/connect
  -> load credentials.json
  -> generate OAuth state
  -> build Google OAuth authorization URL
  -> return connect URL

GET /google-health/callback?code=...&state=...
  -> receive callback parameters
  -> validate OAuth state
  -> prepare token request preview
  -> optionally run guarded token exchange when explicitly enabled
```

Real Google token exchange remains disabled by default:

```env
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
```

When enabled, the backend can POST to the Google token endpoint and store normalized token data locally under:

```txt
backend/local_data/google_health_tokens.json
```

This file is local development data and must not be committed or included in release packages.

Sensitive values such as Google client secrets, authorization codes, access tokens, refresh tokens, and raw Authorization headers must not be returned from API responses or printed to logs.

Sleep data API integration is still out of scope for v0.14.0 because the new wearable/Google Health sleep data API details, scopes, and response format are not confirmed yet.

Current implementation status:

```txt
Google OAuth credentials loader: implemented
Google OAuth connect URL builder: implemented
Google OAuth callback/state validation: implemented
Google token request preview: implemented
Guarded Google token exchange boundary: implemented
Google sleep data API integration: not implemented
/sleep/summary Google Health provider: not implemented
```

Future direction:

```txt
mock
wearable_stub
google_health
```

The legacy `fitbit` provider should be removed or clearly deprecated before public release to avoid implying that new users can connect Fitbit through the legacy Web API path.


## v0.15.0 MVP UX Polish and Wearable Stub Provider

As of v0.15.0, the app improves the MVP experience when sleep data is unavailable and reduces Fitbit-specific wording in the user-facing UI.

The recommended local sleep providers are now:

```txt
mock
wearable_stub
```

`wearable_stub` returns deterministic wearable-shaped sleep data without calling any real wearable, Fitbit, Google Health, or health API.

`fitbit_stub` remains available as a deprecated compatibility alias for older local configuration, but new configuration should use:

```env
SLEEP_PROVIDER=wearable_stub
```

The Flutter app now presents health data connection wording more generically instead of implying that Fitbit real API integration is available.

Current user-facing direction:

```txt
Health Data Status
  -> shows health/wearable connection readiness

Sleep Summary
  -> shows source, availability, and friendly unavailable messages

Advice
  -> can still be generated when sleep data is unavailable
  -> does not pretend exact sleep duration is known
```

Unavailable sleep data is treated as a normal app state, not only as a technical error.

Example behavior:

```txt
Sleep data unavailable
  -> display a gentle message
  -> allow mood-based advice generation
  -> avoid inventing sleep duration or sleep quality
```

The Day4 provider rename introduces:

```txt
SLEEP_PROVIDER=wearable_stub
  -> recommended wearable-shaped sample provider

SLEEP_PROVIDER=fitbit_stub
  -> deprecated compatibility alias for older local configs
```

Legacy Fitbit Web API integration remains a migration/reference boundary only and should be removed or clearly deprecated before public release.


## v0.4.0 OAuth Stub Status

As of v0.4.0, the backend includes Fitbit OAuth stub endpoints:

```txt
GET /fitbit/status
GET /fitbit/connect
GET /fitbit/callback
```

The backend also defines a local token store placeholder:

```txt
backend/local_data/fitbit_tokens.json
```

This file is not committed to Git. In v0.4.0, it is only used to test the future token storage boundary.

Current behavior:

```txt
/fitbit/status
  -> checks Fitbit config placeholders
  -> checks local token store placeholder
  -> returns connected=false or connected=true without real token validation
```

Real OAuth code exchange, token refresh, and Fitbit API calls are still planned for a later version.

### Current Flow

```text
Flutter App
  ↓
GET /sleep/summary
  ↓
FastAPI Backend
  ↓
sleep_summary_service
  ↓
configured SleepProvider
  ↓
SleepSummary
```

### Mock Provider

The `mock` provider returns deterministic local development data.

Example response:

```json
{
  "date": "2026-04-28",
  "total_sleep_minutes": 372,
  "efficiency": 86,
  "deep_sleep_minutes": 52,
  "rem_sleep_minutes": 78,
  "awake_minutes": 31
}
```

### Legacy Fitbit Stub Provider

`fitbit_stub` is kept as a deprecated compatibility alias.
For current sample usage, prefer `wearable_stub`.

It returns deterministic Fitbit-shaped sample data so the API, Flutter UI, and future Fitbit integration boundary can be tested safely.

Example response:

```json
{
  "date": "2026-04-28",
  "total_sleep_minutes": 398,
  "efficiency": 89,
  "deep_sleep_minutes": 64,
  "rem_sleep_minutes": 92,
  "awake_minutes": 27
}
```

## Next Planned Step

The next planned step is to replace the stub internals with Fitbit OAuth/config boundaries while keeping the `/sleep/summary` API stable.

Planned progression:

```text
mock
  ↓
fitbit_stub
  ↓
Fitbit OAuth/config boundary
  ↓
real Fitbit API client
```

## Target Direction

The target direction is to replace the current stub sleep summary provider with a Fitbit-backed provider.

Target flow:

```text
Flutter App
  ↓
GET /sleep/summary
  ↓
FastAPI Backend
  ↓
sleep_summary_service
  ↓
FitbitSleepProvider
  ↓
Fitbit Web API
  ↓
SleepSummary
```

The Flutter app should continue to use the same `/sleep/summary` API even after Fitbit integration is added.

## Responsibility Split

### Flutter App

The Flutter app should be responsible for:

- Displaying sleep summary data
- Displaying character presets
- Letting the user select a character
- Letting the user select their current mood
- Sending selected character, sleep summary, and mood to `/advice`

The Flutter app should not be responsible for:

- Holding Fitbit API secrets
- Managing Fitbit refresh tokens
- Calling Fitbit APIs directly
- Knowing Fitbit-specific response formats

### FastAPI Backend

The backend should be responsible for:

- Selecting the configured sleep provider
- Fitbit OAuth flow
- Fitbit access token / refresh token handling
- Calling Fitbit Web API
- Converting Fitbit sleep data into `SleepSummary`
- Providing `/sleep/summary` to the Flutter app
- Passing normalized sleep summary data into the advice flow

## API Shape

### Existing API

```text
GET /sleep/summary
```

Current response model:

```json
{
  "date": "2026-04-28",
  "total_sleep_minutes": 372,
  "efficiency": 86,
  "deep_sleep_minutes": 52,
  "rem_sleep_minutes": 78,
  "awake_minutes": 31
}
```

This API should remain stable as much as possible.

## Backend Design

### Current Service Shape

```text
services/
  sleep_summary_service.py
  sleep_providers/
    base.py
    factory.py
    mock.py
    fitbit_stub.py
```

Current responsibilities:

```text
sleep_summary_service
→ App-level service used by API routes.
→ Returns normalized SleepSummary from the configured provider.

SleepProvider
→ Provider interface for sleep summary sources.

MockSleepProvider
→ Returns deterministic local development data.

FitbitStubSleepProvider
→ Returns deterministic Fitbit-shaped stub data.
→ Does not call the real Fitbit API yet.
```

Current flow:

```text
api/sleep.py
  ↓
load_config()
  ↓
sleep_summary_service.get_sleep_summary(config)
  ↓
create_sleep_provider(config)
  ↓
configured SleepProvider
  ↓
SleepSummary
```

Unsupported provider values should return a clear client-facing error.

Example:

```env
SLEEP_PROVIDER=unknown
```

Expected API behavior:

```text
400 Bad Request
```

Example response:

```json
{
  "detail": "Unsupported sleep provider: unknown"
}
```

### Future Service Shape

Possible future split:

```text
services/
  sleep_summary_service.py
  sleep_providers/
    base.py
    factory.py
    mock.py
    fitbit_stub.py
    fitbit.py
  fitbit_oauth_service.py
  fitbit_token_store.py
```

Possible responsibilities:

```text
SleepSummaryService
→ App-level service used by API routes.
→ Returns normalized SleepSummary.

FitbitOAuthService
→ Handles Fitbit OAuth URL generation, callback handling, and token refresh.

FitbitTokenStore
→ Stores and retrieves Fitbit access/refresh tokens for local development.

FitbitSleepProvider
→ Calls Fitbit sleep APIs and converts raw Fitbit responses into SleepSummary.
```

Possible future flow:

```text
api/sleep.py
  ↓
SleepSummaryService.get_sleep_summary(config)
  ↓
FitbitSleepProvider.get_sleep_summary()
  ↓
Fitbit Web API
  ↓
SleepSummary
```

## v0.8.0 Callback and Token Exchange Stub Status

As of v0.8.0, the backend can receive Fitbit OAuth callback query parameters:

```txt
code
state
error
error_description
```

Current callback behavior:

```txt
GET /fitbit/callback
  -> no authorization data received

GET /fitbit/callback?code=...&state=...
  -> authorization code received
  -> token exchange stub reached

GET /fitbit/callback?error=...
  -> authorization error received
```

The token exchange service is still a stub.

Current token exchange behavior:

```txt
authorization code
  -> Fitbit token exchange stub
  -> no real Fitbit token endpoint call
```

For local development only, the backend can save dummy token data when enabled:

```env
FITBIT_DEV_SAVE_DUMMY_TOKEN=1
```

When enabled, a callback with `code` writes dummy token data to:

```txt
backend/local_data/fitbit_tokens.json
```

This allows the app to test the future connected-state flow:

```txt
callback with code
  -> dummy token saved
  -> /fitbit/status returns connected=true
```

This does not represent a real Fitbit connection.

Before release, local dummy token data must be removed and the development flag should be disabled:

```env
FITBIT_DEV_SAVE_DUMMY_TOKEN=0
```

## v0.9.0 OAuth State Validation Status

As of v0.9.0, the backend generates, stores, validates, and expires Fitbit OAuth `state` values.

Current connect behavior:

```txt
GET /fitbit/connect
  -> generate OAuth state
  -> save state under backend/local_data/
  -> include state in Fitbit authorization URL
```

Current callback behavior:

```txt
GET /fitbit/callback?code=...&state=...
  -> validate returned state against saved state
  -> check state expiration
  -> proceed to token exchange stub only when state is valid and not expired
```

State mismatch behavior:

```txt
state_valid=false
state_expired=false
error=invalid_state
token_exchange_attempted=false
```

State expiration behavior:

```txt
state_valid=false
state_expired=true
error=invalid_state_expired
token_exchange_attempted=false
```

The state lifetime is configured with:

```env
FITBIT_OAUTH_STATE_TTL_SECONDS=600
```

The OAuth state file is local development data and must not be committed or included in release packages.

## v0.10.0 Token Exchange Request Boundary Status

As of v0.10.0, the backend prepares the future Fitbit token exchange request boundary after a valid OAuth callback.

Current behavior:

```txt
GET /fitbit/callback?code=...&state=...
  -> validate OAuth state
  -> check OAuth state expiration
  -> prepare token exchange request parts
  -> skip real HTTP POST by default
```

The token exchange request boundary prepares internal request parts for the future Fitbit token endpoint:

```txt
POST https://api.fitbit.com/oauth2/token
```

Planned request shape:

```txt
grant_type=authorization_code
code=<authorization code>
redirect_uri=<FITBIT_REDIRECT_URI>
```

The future real request will use HTTP Basic authentication with Fitbit client credentials.

Sensitive values such as `FITBIT_CLIENT_SECRET`, authorization codes, and Authorization header values must not be returned from API responses or printed to logs.

Real token exchange remains guarded by:

```env
FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=0
```

When this flag is disabled, the backend prepares a non-sensitive request preview and skips real HTTP POST.

## v0.11.0 Real Token Exchange Boundary Status

As of v0.11.0, the backend includes a guarded real Fitbit token exchange path.

Real token exchange remains disabled by default:

```env
FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=0
```

When explicitly enabled, the backend can POST the prepared token request to the Fitbit token endpoint:

```txt
POST https://api.fitbit.com/oauth2/token
```

The HTTP boundary is isolated in:

```txt
backend/app/services/fitbit_http_client.py
```

The token exchange service is responsible for:

```txt
authorization code
  -> build internal token request parts
  -> build non-sensitive request preview
  -> optionally call the real Fitbit token endpoint
  -> normalize successful token response data
  -> store token data locally
```

Successful real token responses are normalized before local storage.

Expected normalized fields:

```txt
access_token
refresh_token
token_type
expires_in
scope
user_id
```

Token data is stored under:

```txt
backend/local_data/fitbit_tokens.json
```

This file is local development data and must not be committed or included in release packages.

The API response does not expose token values. It only reports high-level status fields such as:

```txt
token_exchange_attempted
token_request_prepared
real_token_exchange_enabled
token_saved
token_exchange_error
```

External token exchange error codes are intentionally stable and non-sensitive:

```txt
config_incomplete
http_request_failed
invalid_token_response
```

Real token exchange should only be tested with valid Fitbit OAuth credentials and a valid callback `code`/`state` pair.

## OAuth Flow Draft

The exact Fitbit OAuth implementation should be checked against the latest Fitbit developer documentation before implementation.

Expected high-level flow:

```text
1. User starts Fitbit connection from Flutter app.
2. Flutter app opens backend Fitbit connect URL.
3. Backend redirects user to Fitbit OAuth authorization page.
4. User approves requested scopes.
5. Fitbit redirects back to backend callback URL.
6. Backend exchanges authorization code for access token and refresh token.
7. Backend stores tokens securely.
8. Flutter app can call /sleep/summary.
9. Backend refreshes Fitbit token when needed.
```

Possible backend endpoints:

```text
GET /fitbit/connect
GET /fitbit/callback
GET /fitbit/status
POST /fitbit/disconnect
```

These endpoint names are tentative.

## Required Fitbit Data

The app initially needs only a normalized sleep summary.

Desired fields:

```text
date
total_sleep_minutes
efficiency
deep_sleep_minutes
rem_sleep_minutes
awake_minutes
```

Optional future fields:

```text
sleep_score
time_in_bed_minutes
start_time
end_time
data_source
sync_status
```

## SleepSummary Mapping

The backend should convert Fitbit raw sleep data into the app-level `SleepSummary` model.

Current model:

```python
class SleepSummary(BaseModel):
    date: str
    total_sleep_minutes: int
    efficiency: int | None = None
    deep_sleep_minutes: int | None = None
    rem_sleep_minutes: int | None = None
    awake_minutes: int | None = None
```

Mapping policy should prefer normalized app fields over leaking Fitbit-specific field names into Flutter.

## Token Storage Policy

For local development, token storage can start simple.

Possible local development options:

```text
Option A:
- Store tokens in a local JSON file
- Simple for development
- Not suitable for production

Option B:
- Store tokens in SQLite
- Better for local backend testing
- Still simple

Option C:
- Store tokens in PostgreSQL or managed DB
- Better for production
```

Production should not store Fitbit tokens in Flutter.

Production token storage should be backend-side only.

## Security Notes

Do not put Fitbit client secrets in the Flutter app.

Do not commit `.env` files.

Backend environment variables may include:

```env
FITBIT_CLIENT_ID=
FITBIT_CLIENT_SECRET=
FITBIT_REDIRECT_URI=
```

`backend/.env.example` should include empty placeholder values only.

## Out of Scope for First Fitbit Implementation

The first Fitbit implementation should not include:

- Apple Health support
- Health Connect support
- Multiple wearable providers
- Complex historical sleep charts
- Medical diagnosis or treatment claims
- Advanced recommendation logic
- Paid plan enforcement

## First Implementation Plan

### Step 1: Keep Stable Sleep Summary API

Current state:

```text
GET /sleep/summary
→ configured SleepProvider
→ normalized SleepSummary
```

### Step 2: Add Fitbit Configuration Placeholders

Add backend config placeholders:

```text
FITBIT_CLIENT_ID
FITBIT_CLIENT_SECRET
FITBIT_REDIRECT_URI
```

### Step 3: Add Fitbit OAuth Draft Endpoints

Add minimal endpoints:

```text
GET /fitbit/connect
GET /fitbit/callback
GET /fitbit/status
```

At first, these can return stub responses or redirect URLs.

### Step 4: Add Token Storage for Local Development

Start with local development storage only.

Possible simple file:

```text
backend/local_data/fitbit_tokens.json
```

This file must be ignored by Git.

### Step 5: Add Fitbit Sleep Provider

Add:

```text
services/sleep_providers/fitbit.py
```

It should return normalized `SleepSummary`, not raw Fitbit data.

### Step 6: Replace Fitbit Stub Internals

Keep API unchanged:

```text
GET /sleep/summary
```

Change internals:

```text
FitbitStubSleepProvider
↓
FitbitSleepProvider
```

## Sleep Data Unavailable Flow

In a future version, the app should handle cases where sleep data cannot be fetched.

Examples:

```txt
- Fitbit is not connected
- Fitbit token is expired
- Fitbit API request fails
- Sleep data for the target date does not exist
- The selected sleep provider is temporarily unavailable
```

The app should not treat this only as a technical error.

Because Daily Rhythm Companion is a character-driven app, the character should gently acknowledge that sleep data is unavailable and still provide lightweight advice based on the user's mood.

Example character response:

```txt
ごめんね、今日は睡眠状態が確認できなかったみたい……。
でも、今の気分をもとに、無理しすぎない過ごし方を一緒に考えるね。
```

### Future Backend Direction

The current `AdviceRequest` requires a sleep summary.

Current shape:

```python
class AdviceRequest(BaseModel):
    character: CharacterContext
    sleep: SleepSummary
    mood: str
```

A future version may allow advice generation without sleep data.

Possible future shape:

```python
class AdviceRequest(BaseModel):
    character: CharacterContext
    sleep: SleepSummary | None = None
    mood: str
    sleep_status: str = "available"
```

Possible `sleep_status` values:

```txt
available
unavailable
not_connected
fetch_failed
no_data
```

### Future Prompt Behavior

When sleep data is unavailable, the advice prompt should include instructions such as:

```txt
Sleep data is not available today.
The character should gently acknowledge this in Japanese.
Do not blame the user.
Do not mention technical implementation details.
Provide light, mood-based advice instead.
```

The response should avoid implying that sleep data was actually measured.

Good example:

```txt
今日は睡眠データが確認できなかったみたい。
今の気分をもとに、少し軽めの一日にしていこうね。
```

Bad example:

```txt
昨夜は6時間眠れたようですね。
```

### Future Provider Direction

A future version may add an unavailable stub provider for testing this flow.

Example:

```env
SLEEP_PROVIDER=unavailable_stub
```

Expected behavior:

```txt
GET /sleep/summary
  -> sleep data unavailable
```

The exact API shape is still undecided.

Possible options:

```txt
Option A:
- /sleep/summary returns an error such as 503
- Flutter handles the unavailable state separately

Option B:
- /sleep/summary returns a response with availability metadata
- Flutter and /advice can use the same normalized response shape
```

For now, this is only a design note. The actual implementation should be decided after the Fitbit connect flow becomes more concrete.

## Design Principle

Flutter should depend on app-level APIs, not Fitbit APIs.

Backend should hide Fitbit-specific details behind service boundaries.

The app should be able to switch from:

```text
MockSleepProvider
```

to:

```text
FitbitStubSleepProvider
```

to:

```text
FitbitSleepProvider
```

without changing the Flutter screen contract.