# v2.1.0 W-2 Fitbit token/status/reconnect contract

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED

## Purpose

W-2 hardens the legacy Fitbit migration/reference path without claiming configured real Fitbit success. It adds a conservative app-facing lifecycle model, one-time OAuth state consumption, deterministic token-expiry classification, and mock-safe refresh-boundary tests.

W-2 does not validate a token against Fitbit, retrieve real sleep data, prove permissions, or satisfy W-5.

## App-facing connection states

```text
unconfigured
  Required Fitbit OAuth settings are not available.

authorization_ready
  A connect/reconnect URL can be prepared, but no usable local token is present.

token_present_unverified
  Local access-token data exists and does not currently require refresh.
  Live validity, scope, permission, and Fitbit API success remain unverified.

connected
  Reserved for separately accepted configured real verification.
  Normal W-2 status inspection does not emit this state.

refresh_required
  The access token is missing, expired, near expiry, or has no valid expiry,
  and a refresh token is available. Status inspection does not perform refresh.

reconnect_required
  The local access token cannot be safely continued without a new OAuth flow,
  or callback state is invalid/expired/consumed.

permission_blocked
  A matching OAuth callback returned access_denied.

unavailable
  Compatibility fallback for older or unknown responses.

error
  Local token data could not be parsed safely or guarded token exchange failed.
```

## Backward compatibility

The existing `/fitbit/status` fields remain:

```text
connected
provider
message
```

W-2 adds:

```text
connection_state
verified
```

The legacy `connected` boolean remains `true` when readable local token data contains both access-token and refresh-token fields. This preserves the old route shape, but `verified=false` and `connection_state` are authoritative for new UI wording. `connected=true` alone still does not mean live Fitbit validation.

The existing `/fitbit/connect` and `/fitbit/callback` response fields remain, with the same new `connection_state` and `verified` fields added.

## Token status rules

`FitbitTokenStore.get_status()` returns only non-sensitive metadata:

```text
file exists / readable
access token present
refresh token present
source marker
expiration known
expired
refresh required
 development dummy marker
```

It never returns token values.

Classification uses a fixed five-minute refresh margin. Missing or invalid expiry metadata fails closed into `refresh_required` when a refresh token exists, otherwise `reconnect_required` when the access token cannot safely continue.

A development dummy token remains `token_present_unverified` and is explicitly described as non-real.

## OAuth state lifecycle

A Fitbit OAuth state is now one-time data:

```text
- matching and unexpired callback: state is deleted before token exchange;
- matching but expired callback: state is deleted and reconnect is required;
- mismatched callback: saved state is retained, callback is rejected;
- matching access_denied callback: state is consumed and permission_blocked is returned;
- replay after consumption: invalid state / reconnect required.
```

This does not make the callback or token exchange real-use accepted.

## Refresh test boundary

`refresh_fitbit_access_token()` and the guarded code-exchange implementation accept injected temporary token stores and fake HTTP functions for tests. Fake success verifies normalized storage and non-sensitive result metadata. Fake failure verifies safe error classification.

Normal `/fitbit/status` does not call the refresh function or any network endpoint.

## Flutter presentation

`FitbitStatus` and `FitbitConnectResponse` parse both old and W-2 responses.

Legacy old-response fallback remains conservative:

```text
connected=true + provider=fitbit -> token_present_unverified
configured wording -> authorization_ready
not configured wording -> unconfigured
```

New display states include:

```text
authorization_ready       認証準備済み
token_present_unverified  ローカルトークン検出
refresh_required          トークン更新が必要
reconnect_required        再接続が必要
permission_blocked        認証未許可
error                     状態確認エラー
```

`connected` is displayed as `連携済み` for the legacy Fitbit route only when `verified=true`. W-2 does not set `verified=true`.

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/app/models/fitbit.py
backend/app/services/fitbit_service.py
backend/app/services/fitbit_token_store.py
backend/app/services/fitbit_oauth_state_store.py
backend/app/services/fitbit_token_exchange.py
backend/tests/test_fitbit_token_status_reconnect.py
app/lib/models/fitbit_status.dart
app/lib/models/fitbit_connect_response.dart
app/test/fitbit_token_status_reconnect_test.dart
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_fitbit_token_status_reconnect.md
scripts/check_v210_fitbit_current_behavior_inventory.py
scripts/check_v210_fitbit_token_status_reconnect.py
```

## Explicit non-change surface

```text
backend/app/api/fitbit.py
backend/app/api/sleep.py
backend/app/models/sleep.py
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_http_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/fitbit.py
backend/app/services/sleep_providers/factory.py
backend/tests/test_fitbit_current_state_contract.py
app/lib/screens/home_screen.dart
app/lib/services/backend_api_client.dart
app/lib/models/sleep_summary.dart
app/test/fitbit_current_state_contract_test.dart
app/test/widget_test.dart
app/pubspec.yaml
version metadata
v2.0.0/v2.0.1 release records, tags, GitHub Releases, and fixed ZIPs
```

Sleep API error classification, `SleepSummary.is_real_data`, normalized start/end mapping, provider selection UI, and configured real verification remain W-3 through W-5 work.

## Mock-safe verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests/test_fitbit_current_state_contract.py
python -m pytest -q backend/tests/test_fitbit_token_status_reconnect.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

W-2 verification uses only temporary token/state files, fixed time, fake HTTP responses, public-safe placeholder strings, source inspection, backend pytest, and Flutter tests.

## Real operator boundary

W-2 must not:

```text
- open a Fitbit OAuth browser;
- use a real authorization code, access token, or refresh token;
- perform a real token exchange or refresh;
- call the Fitbit sleep API;
- confirm live scopes or permissions;
- retrieve real sleep values;
- collect smartphone Web evidence;
- add private screenshots, payloads, paths, URLs, or operator evidence to Public source.
```

Configured real acceptance remains W-5 and cannot be completed from fake HTTP success or local token classification.

## Accepted verification

W-2 was accepted on 2026-07-23 after the following passed:

```text
compileall
W-1 and W-2 source-tree checks
v2.0.x compatibility and historical guards
backend pytest: 57 passed
Flutter test: 50 passed
diff review and explicit operator approval
```

No real OAuth, real token exchange/refresh, Fitbit API request, private payload, smartphone Web evidence, release ZIP, tag, or GitHub Release was created or used for W-2 acceptance. W-3 is the next CURRENT / NOT_COMPLETED small commit.
