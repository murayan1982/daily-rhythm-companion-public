# DRC v2.1.0 W-5 Fitbit real operator runbook

Updated: 2026-07-23

## Status

```text
W-5a: IMPLEMENTED / NOT_ACCEPTED
W-5b: PLANNED
parent W-5: CURRENT / NOT_COMPLETED
real operator execution: NOT_PERFORMED
smartphone Web verification: NOT_PERFORMED
```

W-5a prepares the public-safe operator contract. It does not perform OAuth,
token exchange/refresh, Fitbit sleep retrieval, or smartphone Web acceptance.
Those remain W-5b operator work.

## Safety boundary

Never commit, paste into shared logs, or add to a release artifact:

```text
Fitbit client secret
access token or refresh token
authorization code or OAuth state
full connect/callback URL
raw Fitbit response or provider error payload
exact private sleep date, duration, start/end time
private env path, private absolute path, or LAN address
raw screenshot or browser history
operator_evidence contents
```

Public output may contain only key names, allow-listed states, boolean markers,
and generic success/failure classifications.

## 1. Source-tree gate

Run without a private env file:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v210_fitbit_real_operator_preflight.py
python scripts\smoke_v210_fitbit_real_operator_preflight.py --check-example
python scripts\check_v210_fitbit_real_operator_contract.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

These commands do not contact Fitbit.

## 2. Create the ignored dedicated env file

```powershell
Copy-Item `
  .\backend\env_profiles\fitbit_real_operator.env.example `
  .\backend\env_profiles\fitbit_real_operator.local.env
```

Fill only the dedicated Fitbit configuration in the `.local.env` file. The
registered Fitbit application callback must match:

```text
http://127.0.0.1:8000/fitbit/callback
```

A different local host/port is allowed only when the Fitbit application and the
private env file use the exact same callback URL.

The dedicated profile must retain:

```text
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=fitbit
FITBIT_ENABLE_REAL_TOKEN_EXCHANGE=1
FITBIT_DEV_SAVE_DUMMY_TOKEN=0
```

Do not add token values, authorization codes, OAuth state, Framework/LLM keys,
Google Health credentials, or TTS provider secrets.

## 3. Validate the private profile without starting the backend

```powershell
python scripts\smoke_v210_fitbit_real_operator_preflight.py `
  --env-file .\backend\env_profiles\fitbit_real_operator.local.env

powershell -ExecutionPolicy Bypass -File `
  .\backend\scripts\run_fitbit_real_operator.ps1 `
  -EnvFile .\backend\env_profiles\fitbit_real_operator.local.env `
  -ValidateOnly
```

Expected public-safe markers include:

```text
v210_fitbit_real_operator_preflight_env_file_status: accepted
v210_fitbit_real_operator_preflight_env_file_public_safe: True
[fitbit-operator-run] operator_env_validation=accepted
[fitbit-operator-run] backend_dotenv_override=disabled
[fitbit-operator-run] validate_only=True
[fitbit-operator-run] backend_start=not-started
```

`token_file_exists=False` is valid before the first OAuth flow.

## 4. Start the configured backend

Use a private terminal:

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\backend\scripts\run_fitbit_real_operator.ps1 `
  -EnvFile .\backend\env_profiles\fitbit_real_operator.local.env
```

Do not redirect the complete terminal output to a committed file.

## 5. Complete OAuth locally

Use the Flutter Fitbit connect action or open the local `/fitbit/connect`
response in a private browser session. Do not publish or screenshot the full
connect URL because it contains OAuth state.

Complete Fitbit authorization with the sleep scope. The browser should return
to the configured DRC `/fitbit/callback` endpoint. The callback response may be
reviewed locally, but authorization data and browser history stay private.

After callback completion, `/fitbit/status` should no longer be
`unconfigured` or `authorization_ready`. A local token file may now exist under
`backend/local_data`; that file remains ignored and private.

## 6. Run the explicit real backend smoke

From a second private terminal:

```powershell
python scripts\smoke_v210_fitbit_real_operator_execution.py `
  --base-url http://127.0.0.1:8000 `
  --allow-real-request
```

The command intentionally fails without `--allow-real-request`.

Required safe markers for an API-success checkpoint:

```text
provider_selection_fitbit: True
sleep_source_fitbit: True
sleep_available: True
sleep_is_real_data: True
positive_duration: True
sleep_window_present: True
raw_payload_exposed: False
smartphone_web_required: True
smartphone_web_verified: False
```

The script never prints the target date, duration, sleep timestamps, token
values, raw response, full base URL, or provider payload.

An API-success checkpoint does not complete W-5. Smartphone Web evidence is
still required.

## 7. Verify the actual Flutter Web presentation

Start Flutter Web against the same configured backend. Keep the actual LAN
address local-only when using a smartphone.

The normal `Sleep Data Source` card must visibly show the equivalent of:

```text
configured provider: Fitbit
actual source: Fitbit
data kind: 実データ
availability: 取得済み
```

The displayed normalized sleep summary must be usable without exposing raw
Fitbit data. Do not include the OAuth URL, callback URL, token data, exact sleep
values, private path, or LAN address in a public screenshot.

Store any raw screenshot only under ignored `operator_evidence/` or another
private location. W-5b will define and validate the minimal public-safe marker
record after the actual run.

## 8. Failure classification

```text
unconfigured / authorization_ready
  -> verify the dedicated env and complete OAuth

refresh_required / refresh failure / reconnect_required
  -> repeat OAuth; do not paste token files or callback URLs

permission_denied / scope_missing
  -> confirm Fitbit sleep permission and reauthorize

rate_limited
  -> stop repeated calls and retry later

provider_unavailable / request failure
  -> preserve only the allow-listed error category

no_sleep_data
  -> retry a date known privately to contain Fitbit sleep data; do not publish it

invalid_response
  -> retain no raw payload; review locally and report only the safe category
```

## Completion boundary

W-5a may be accepted after source-tree checks, full backend/Flutter tests, diff
review, and operator approval. W-5 remains `CURRENT / NOT_COMPLETED`.

W-5b requires all of the following before W-5 can be accepted:

```text
explicit private env validation
real OAuth callback and token save/refresh path
real Fitbit sleep request
W-3 normalization into SleepSummary
W-4 provider/source/data-kind display
smartphone Web visual confirmation
private evidence kept outside Git
public-safe marker review
```

C-1 and later phases remain planned.
