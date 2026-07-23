# v2.1.0 Fitbit current behavior inventory

Updated: 2026-07-23
Status: W-1 COMPLETED / ACCEPTED
Purpose: record the implementation that exists before v2.1.0 Fitbit changes

## Interpretation rule

```text
Implemented source boundary != configured real-use acceptance
Local token detection != live token validity
Authorization URL ready != connected
Normalized fixture success != real Fitbit sleep retrieval
Fallback/unavailable behavior != configured-provider success
```

This document records the inspected Public source. It does not contain credentials, tokens, authorization codes, OAuth state values, raw Fitbit payloads, exact private sleep values, private paths, LAN addresses, or operator screenshots.

## Provider classification

`backend/app/services/sleep_providers/factory.py` currently defines:

| Provider value | Current role | Accepted meaning |
| --- | --- | --- |
| `mock` | recommended default | credential-free deterministic app behavior |
| `wearable_stub` | recommended sample | deterministic wearable-shaped `SleepSummary` |
| `google_health` | recommended real provider | existing guarded Google Health path |
| `fitbit_stub` | deprecated alias | compatibility sample, not Fitbit execution |
| `fitbit` | legacy migration/reference provider | existing OAuth/token/API code path, not yet accepted as real daily-use Fitbit |

Provider selection is backend configuration through `SLEEP_PROVIDER`. The accepted W-1 Flutter UI does not provide a user-facing provider selector.

## Configuration boundary

`backend/app/config.py` exposes the retained Fitbit settings:

```text
FITBIT_CLIENT_ID
FITBIT_CLIENT_SECRET
FITBIT_REDIRECT_URI
FITBIT_DEV_SAVE_DUMMY_TOKEN
FITBIT_OAUTH_STATE_TTL_SECONDS (default 600)
FITBIT_ENABLE_REAL_TOKEN_EXCHANGE (default false)
```

The comments still classify Fitbit as a legacy migration/reference route. W-1 does not alter configuration ownership or move provider credentials into Flutter.

## API routes and response models

`backend/app/api/fitbit.py` retains:

```text
GET /fitbit/status   -> FitbitStatusResponse
GET /fitbit/connect  -> FitbitConnectResponse
GET /fitbit/callback -> FitbitCallbackResponse
```

`backend/app/models/fitbit.py` keeps the accepted response shapes:

```text
FitbitStatusResponse:
  connected, provider, message

FitbitConnectResponse:
  ready, connect_url, message

FitbitCallbackResponse:
  received_code, received_state, state_valid, state_expired,
  token_exchange_attempted, token_request_prepared,
  real_token_exchange_enabled, token_saved, message,
  error, error_description, token_exchange_error
```

W-1 does not add fields or change route behavior.

## Status semantics

`backend/app/services/fitbit_service.py:get_fitbit_status()` checks:

```text
- client ID, client secret, and redirect URI are configured;
- the local token store file exists;
- access_token-like and refresh_token-like fields are present.
```

When all are detected it returns `connected=true`, but its message states that this is local development token data and that real token validation is not implemented.

It does not currently check:

```text
- token expiry at status-read time;
- refresh success;
- live Fitbit authentication;
- sleep scope or permission acceptance;
- a successful Fitbit API response;
- a successful sleep-data normalization result.
```

Flutter therefore presents legacy `connected=true` as `ローカルトークン検出`, not `連携済み`.

## Connect and OAuth state boundary

`build_fitbit_connect_response()` requires client ID and redirect URI, creates a random OAuth state in the local state store, and builds a Fitbit authorization URL with the `sleep` scope.

`ready=true` means only:

```text
- required URL inputs were present;
- a local OAuth state was written;
- an authorization URL was generated.
```

It does not mean authorization, permission, token exchange, token refresh, API retrieval, or connection acceptance succeeded.

`FitbitOAuthStateStore` stores the latest state and creation timestamp, compares callback state with `secrets.compare_digest`, and applies a configured TTL. The current callback path does not consume/delete the state after a successful callback; later reconnect hardening may address lifecycle behavior.

## Callback and token-exchange boundary

`handle_fitbit_callback_stub()` currently:

```text
- returns a safe error response when Fitbit reports an OAuth error;
- rejects a missing/mismatched state;
- rejects an expired state;
- passes a valid code/state pair to exchange_fitbit_code_stub();
- exposes only status flags and safe error identifiers through the response model.
```

`backend/app/services/fitbit_token_exchange.py` includes real token-request and refresh code, but real authorization-code exchange is guarded by `FITBIT_ENABLE_REAL_TOKEN_EXCHANGE` and required configuration. Source presence alone is not W-5 acceptance.

The token store persists access/refresh token material under ignored local data. Public checks must use temporary stores or fakes and must not inspect an operator's real token file.

## Sleep request boundary

`backend/app/services/fitbit_sleep_service.py` currently:

```text
- loads the local token store;
- refreshes when token expiry indicates refresh is needed;
- builds the Fitbit sleep-by-date endpoint;
- creates a non-sensitive request preview;
- calls the bearer-auth Fitbit API client;
- keeps the raw response inside the service result;
- returns coarse safe error identifiers on no-token, refresh, or API failure.
```

The API endpoint shape is:

```text
https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json
```

`backend/app/services/fitbit_api_client.py` currently maps HTTP/network/JSON/shape failures to broad internal exceptions. It does not yet expose an app-facing distinction for:

```text
reconnect required
permission denied
scope missing
rate limited
provider unavailable
no sleep record for the selected date
```

Those distinctions are later W-2/W-3 work.

## Normalization boundary

`backend/app/services/fitbit_sleep_normalizer.py` currently:

```text
- validates that the raw response is a dictionary;
- selects the `isMainSleep=true` entry when available;
- falls back to the first dictionary sleep entry;
- derives total sleep minutes from `minutesAsleep` or summary totals;
- retains time-in-bed, efficiency, startTime, and endTime;
- returns a provider-neutral normalized result and safe message.
```

This proves a normalization implementation exists. It does not prove that a real Fitbit payload was retrieved or accepted.

## SleepSummary mapping gap

`backend/app/services/sleep_providers/fitbit.py` maps a successful normalized result into `SleepSummary` with:

```text
date
total_sleep_minutes
efficiency
source=fitbit
available=true
message
```

It currently leaves the following `SleepSummary` fields at defaults or `None`:

```text
sleep_start
sleep_end
quality_label
confidence
is_real_data (default false)
unavailable_reason
```

Therefore a successful Fitbit service path is not yet represented as confirmed real sleep data by the app-facing model. W-3 owns the accepted mapping and regression contract; W-1 only records the gap.

## Flutter presentation boundary

The inspected Flutter files preserve the M-7 conservative presentation:

```text
app/lib/models/fitbit_status.dart
- legacy Fitbit connected=true -> `ローカルトークン検出`
- legacy token wording explains that live validation/acceptance is incomplete

app/lib/models/fitbit_connect_response.dart
- authorization URL readiness is described as a compatibility URL
- it explicitly avoids connection-success wording

app/lib/models/sleep_summary.dart
- real-data presentation depends on is_real_data and source semantics

app/lib/screens/home_screen.dart
- loads sleep summary and Fitbit status in the health-data section
- can open the prepared external authorization URL
- uses `連携済み` only when the app determines real sleep data is present
- contains separate detailed Google Health connection/operator surfaces
- has no user-facing sleep-provider selector
```

W-4 owns unified provider selection/source labels and simplified normal-user Google Health UX while retaining explicitly labeled operator diagnostics.

## Existing regression boundary

The accepted v2.0.x tests remain unchanged in W-1:

```text
backend/tests/test_fitbit_current_state_contract.py
app/test/fitbit_current_state_contract_test.dart
```

They use temporary/fake inputs and deterministic presentation assertions. They do not call Fitbit or read an operator token store.

## Work assignment after W-1

```text
W-2: CURRENT / NOT_COMPLETED — token/status/reconnect state model and fake-response hardening
W-3: PLANNED — API error classification, SleepSummary real-data mapping, fixtures, tests
W-4: PLANNED — provider selection, source labels, normal-user health UX
W-5: PLANNED — explicit configured real OAuth/token/permission/sleep/UI operator acceptance
```

W-1 acceptance does not imply any W-2 through W-5 implementation or configured real Fitbit success.
