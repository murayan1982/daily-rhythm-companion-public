# v2.0.0 real Google Health sleep data operator runbook

This runbook prepares the private configured Google Health sleep-data Web run for
`real_google_health_sleep_data`.

Current public status:

```text
real_google_health_sleep_data: ACCEPTED
operator_evidence_acceptance_status: ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

E-3 added the source-tree safe local env preflight. E-4 recorded the
public-safe accepted marker observed from the actual ignored operator env. E-5
added the source-tree safe actual backend/Web run checkpoint and guarded launcher.
E-6 recorded the launcher `-ValidateOnly` success. E-7 records the public-safe
outcome of the actual reauthorization, Google Health HTTP request, and normalized
backend `/sleep/summary`. E-8 records the completed PC and smartphone Web display
plus ignored private screenshot checkpoint. E-9 synchronizes the accepted result
after Day55, Day66, and Day78 marker-only validation completed successfully.

## 1. Source-tree verification

Run before using any private env file:

```powershell
python -m compileall -q backend scripts
python scripts\check_google_health_api_client_boundary.py
python scripts\check_google_health_session_boundary.py
python scripts\check_google_health_sleep_parser.py
python scripts\check_google_health_sleep_source_boundary.py
python scripts\check_google_health_runtime_guard.py
python scripts\check_google_health_diagnostics.py
python scripts\check_google_health_self_check.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py
```

The default preflight is credential-free and network-free.

## 2. Create the ignored operator env file

Create a dedicated Google Health profile instead of reusing a broad framework,
LLM, or TTS env file:

```powershell
Copy-Item `
  .\backend\env_profiles\google_health_real_api_guarded.env.example `
  .\backend\env_profiles\google_health_real_api_operator.local.env
```

The destination is ignored by `.gitignore` through `*.local.env` and
`backend/env_profiles/*.local.env`.

Fill private/local values only in:

```text
backend/env_profiles/google_health_real_api_operator.local.env
```

Required private configuration includes a local credentials-file reference and
the registered OAuth redirect URI. Do not paste OAuth access tokens, refresh
tokens, authorization headers, raw Google Health payloads, raw sleep data, LAN
IPs, or private screenshots into this file.

The Google Health evidence profile intentionally keeps:

```text
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=google_health
```

Do not add `FRAMEWORK_ROOT`, `FRAMEWORK_PROJECT_ROOT`, LLM API keys, or TTS
provider secrets to this dedicated file. The user's normal framework location
remains a separate local setting and is not required for the Google Health sleep
evidence run.

## 3. Validate the private env markers

Run:

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py `
  --env-file .\backend\env_profiles\google_health_real_api_operator.local.env
```

Expected public-safe marker:

```text
v200_real_google_health_sleep_data_preflight_env_file_validation_status: accepted
```

The script prints key names and marker status only. It does not print env values
or the supplied path.

Recommended project-access markers may remain listed as missing until the local
operator has manually confirmed the matching OAuth client, Cloud API enablement,
Data Access scope, Audience/test-user configuration, and current endpoint/query
contract. They are diagnostics and do not replace the actual real API/Web run.

## 4. E-4 actual local preflight checkpoint

The actual ignored local operator env preflight completed with these public-safe
results:

```text
v200_real_google_health_sleep_data_preflight_env_file_validation_status: accepted
v200_real_google_health_sleep_data_preflight_env_file_missing_or_invalid_keys:
v200_real_google_health_sleep_data_preflight_env_file_forbidden_keys_present:
v200_real_google_health_sleep_data_preflight_env_file_public_safe: True
credentials_file_exists=True
token_file_exists=True
operator_env_git_status=ignored
```

Only these marker names, empty-status results, and boolean presence checks are
recorded publicly. Do not commit the raw local command transcript, operator env,
credential file, token file, OAuth values, client ID, credential contents, private
paths, LAN IPs, raw health payloads, raw sleep data, or screenshots.

The local env preflight gate is passed, but the requirement is not accepted.

The later configured execution must still confirm all of the following:

```text
- existing OAuth/token availability without exposing values
- actual Google Health API request
- real sleep-data fetch success
- E-2 SleepSummary normalization
- actual DRC backend /sleep/summary response with Google Health source
- smartphone Web UI visible real-source result
- private screenshot capture and reference
- Day55, Day66, and Day78 marker-only validation
```

Until the later real backend/Web run, evidence authoring, and marker validation steps are completed and reviewed:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
v2.0.0: NOT_RELEASED
```

## 5. E-5 actual configured backend/Web run checkpoint

Run the source-tree checkpoint before any private network execution:

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py
```

Expected marker:

```text
v200_real_google_health_actual_run_checkpoint_status: real-google-health-sleep-data-actual-run-checkpoint-ready
```

This source-tree command does not read the private operator env, credentials, or
OAuth tokens and does not start the backend or browser.

### 5.1 Validate the backend launcher without starting the API

The E-5 launcher reruns the E-3 preflight, loads only the dedicated validated
operator env into its own process, sets `DRC_SKIP_BACKEND_DOTENV=1`, and checks
credential/token file presence without displaying values.

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\backend\scripts\run_google_health_real_api_operator.ps1 `
  -EnvFile .\backend\env_profiles\google_health_real_api_operator.local.env `
  -ValidateOnly
```

Expected public-safe launcher markers include:

```text
[google-health-operator-run] operator_env_validation=accepted
[google-health-operator-run] backend_dotenv_override=disabled
[google-health-operator-run] credentials_file_exists=True
[google-health-operator-run] token_file_exists=True
[google-health-operator-run] validate_only=True
[google-health-operator-run] backend_start=not-started
```

The `loaded_key_names` marker may show env key names only. It must never show env
values.

### 5.2 Start the actual DRC backend

Use the first private local terminal:

```powershell
powershell -ExecutionPolicy Bypass -File `
  .\backend\scripts\run_google_health_real_api_operator.ps1 `
  -EnvFile .\backend\env_profiles\google_health_real_api_operator.local.env
```

Do not redirect raw backend logs into committed files. The launcher intentionally
disables `backend/.env` loading so the validated operator profile cannot be
silently replaced by unrelated local settings.

### 5.3 Run the guarded real API and backend summary check

After the backend is ready, use a second private local terminal:

```powershell
python scripts\smoke_google_health_real_sleep_request.py `
  --base-url http://127.0.0.1:8000 `
  --allow-real-request
```

The smoke requires explicit consent and confirms the Google Health HTTP boundary
plus the actual normalized DRC `/sleep/summary` response. Required public-safe
markers are:

```text
real_http_attempted=True
safe_to_use_sleep_summary=True
backend_sleep_summary_source=google_health
backend_sleep_summary_available=True
backend_sleep_summary_is_real_data=True
backend_sleep_summary_positive_duration=True
```

Do not treat provider errors, missing data, mock/fallback data, or API-only output
as accepted evidence. Do not publish the target date, precise sleep timestamps,
raw sleep duration, raw provider response, tokens, or authorization headers.

### 5.4 Start Flutter Web against the actual backend

Use a third private local terminal:

```powershell
cd app
flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 `
  --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
cd ..
```

Keep the actual LAN IP local-only. The Web UI must visibly show:

```text
data_source_label=Google Health
data_kind_label=実データ
availability_label=取得済み
normalized_sleep_summary_visible=True
```

The actual DRC backend API, Web UI result, and private screenshot are all required.
A terminal-only or API-only success does not satisfy the requirement.

### 5.5 Later private evidence destinations

E-5 prepares, but does not create or accept, these local-only marker files:

```text
operator_evidence/200_real_google_health_sleep_data_day55.json
operator_evidence/v200_real_google_health_sleep_data_day66.json
operator_evidence/v200_real_google_health_web_sleep_screenshot_day78.json
```

Later validation commands are:

```powershell
python scripts\smoke_v200_real_google_health_sleep_data_evidence.py `
  --operator-evidence-json .\operator_evidence\200_real_google_health_sleep_data_day55.json

python scripts\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py `
  --operator-evidence-json .\operator_evidence\v200_real_google_health_sleep_data_day66.json

python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py `
  --evidence-json .\operator_evidence\v200_real_google_health_web_sleep_screenshot_day78.json
```

Until the actual private run, screenshot review, and all three marker validators
are accepted:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

## 6. E-6 actual launcher validation checkpoint

The actual ignored operator env was passed to the E-5 launcher in `-ValidateOnly`
mode. Only public-safe markers were recorded:

```text
[google-health-operator-run] operator_env_validation=accepted
[google-health-operator-run] backend_dotenv_override=disabled
[google-health-operator-run] credentials_file_exists=True
[google-health-operator-run] token_file_exists=True
[google-health-operator-run] loaded_key_names=<key names only>
[google-health-operator-run] validate_only=True
[google-health-operator-run] backend_start=not-started
validate_exit_code=0
operator_env_git_status=ignored
```

The raw command output, env values, credential contents, OAuth token values,
client IDs, and private paths are not committed. The `loaded_key_names` marker is
allowed because it contains names only and no values.

This checkpoint confirms that the guarded launcher is ready for the actual
private backend run. It does not confirm a Google Health API response, a
normalized `/sleep/summary`, Web UI display, screenshot review, or accepted
evidence.

Next private steps:

1. Start the actual backend with the same launcher without `-ValidateOnly`.
2. Run `scripts/smoke_google_health_real_sleep_request.py --allow-real-request`.
3. Confirm the required public-safe backend summary markers.
4. Start Flutter Web against the actual backend and confirm the visible Google
   Health real-data labels.
5. Capture and keep the screenshot private, then author and validate the Day55,
   Day66, and Day78 marker-only evidence files.

Until all of those steps are completed and reviewed:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

## 7. E-7 actual backend/API and normalized sleep summary checkpoint

The actual configured backend was started with the validated ignored operator
profile. The previously stored OAuth authorization returned `invalid_grant`, so
the old token was retained locally as a private backup and the operator completed
a fresh authorization using the current OAuth client. Only public-safe status
markers are recorded here:

```text
oauth_state_valid=True
oauth_token_exchange_attempted=True
oauth_token_saved=True
token_stored=True
required_sleep_scope_in_token=True
reconnect_recommended=False
google_health_http_status=200
google_health_source_status=ok
real_http_attempted=True
safe_to_use_sleep_summary=True
backend_sleep_summary_source=google_health
backend_sleep_summary_available=True
backend_sleep_summary_is_real_data=True
backend_sleep_summary_positive_duration=True
provider_error_summary=None
real_request_smoke_status=OK
real_request_exit_code=0
```

This checkpoint confirms all of the following:

- The actual DRC backend used the dedicated operator profile.
- The configured Google Health OAuth path was reauthorized successfully.
- The required sleep read-only scope was present.
- Google Health returned a successful real HTTP response.
- The result was normalized through the DRC `/sleep/summary` surface.
- The normalized summary was available, labeled as real Google Health data, and
  contained a positive duration.

Do not commit or publish the target date, exact sleep duration, precise sleep
timestamps, raw Google Health response, raw sleep events, access/refresh tokens,
client credentials, authorization headers, private paths, LAN IPs, or raw backend
logs.

E-7 is still not Web evidence. The next private steps are:

1. Keep the actual backend running with the validated operator profile.
2. Start Flutter Web using the implemented `DRC_BACKEND_API_BASE_URL` define.
3. Confirm the visible source label is `Google Health`.
4. Confirm the UI identifies the result as `実データ` and `取得済み`.
5. Confirm the normalized sleep summary is visible.
6. Capture a private screenshot without committing it.
7. Author and validate the Day55, Day66, and Day78 marker-only evidence files.

Until the actual Web UI result, screenshot review, and marker evidence are
accepted:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

## 8. E-8 actual PC/smartphone Web and private screenshot checkpoint

The actual backend remained configured through the validated ignored Google
Health operator profile. The PC Web UI and smartphone Web UI both reached that
backend and visibly showed the real normalized sleep result. Only public-safe
markers are recorded here:

```text
actual_drc_backend_api_status: confirmed
pc_web_ui_confirmed: True
smartphone_web_ui_confirmed: True
data_source_google_health_visible: True
real_data_label_visible: True
availability_acquired_visible: True
normalized_sleep_summary_visible: True
error_or_fallback_visible: False
private_screenshot_captured: True
private_screenshot_stored_under_ignored_path: True
private_screenshot_git_ignore_confirmed: True
```

The smartphone check used a release Web build served over the private LAN rather
than relying on the desktop Chrome debug-service session:

```powershell
cd app
flutter build web --release `
  --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
python -m http.server 8080 --bind 0.0.0.0 --directory .\build\web
```

Keep `<PC_LAN_IP>` local-only. Do not commit or paste the screenshot bytes, exact
sleep values, dates, timestamps, OAuth values, credentials, raw health payloads,
private paths, or raw backend/Web logs. The screenshot must remain under the
ignored local evidence area.

E-8 completes the visible PC/smartphone Web and private screenshot capture
checkpoint only. It does not yet record the public-safe screenshot reference in
private operator evidence and does not author or validate:

```text
operator_evidence/200_real_google_health_sleep_data_day55.json
operator_evidence/v200_real_google_health_sleep_data_day66.json
operator_evidence/v200_real_google_health_web_sleep_screenshot_day78.json
```

Until all three marker-only evidence files are authored, validated, and reviewed:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

## 9. E-9 public-safe acceptance synchronization

The ignored Day55, Day66, and Day78 operator evidence files were authored only
after the actual Google Health backend, PC Web UI, smartphone Web UI, and private
screenshot checks had completed. Each validator accepted its marker-only evidence:

```text
day55_evidence_status: accepted
day55_public_safe: True
day55_missing_markers: none
day66_execution_evidence_status: accepted
day66_public_safe: True
day66_forbidden_success_states_absent: True
day66_requirement_satisfied: True
day66_missing_markers: none
day78_screenshot_evidence_status: accepted
day78_public_safe: True
day78_screenshot_reference_public_safe: True
day78_forbidden_success_states_absent: True
day78_missing_markers: none
combined_acceptance_status: accepted
combined_requirement_satisfied: True
```

Public-safe source-tree verification for this synchronization:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_acceptance_sync.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py
```

The acceptance-sync checks read committed documentation markers only. They do not
read `operator_evidence/`, call Google Health, read OAuth tokens, start backend or
Web processes, inspect screenshot bytes, or create release artifacts.

```text
commit_scope: Commit E-9 only
implementation_status: real-google-health-sleep-data-acceptance-public-safe-synchronized
accepted_requirement_key: real_google_health_sleep_data
actual_drc_backend_api_status: confirmed
pc_web_ui_status: confirmed
smartphone_web_ui_status: confirmed
day55_evidence_status: accepted
day55_public_safe: True
day66_execution_evidence_status: accepted
day66_public_safe: True
day66_forbidden_success_states_absent: True
day66_requirement_satisfied: True
day78_screenshot_evidence_status: accepted
day78_public_safe: True
day78_screenshot_reference_public_safe: True
day78_forbidden_success_states_absent: True
combined_acceptance_status: accepted
combined_requirement_satisfied: True
operator_evidence_acceptance_status: ACCEPTED
private_evidence_policy: raw screenshots, raw Google Health payloads, raw sleep values, precise timestamps, OAuth values, credentials, authorization headers, LAN IPs, private paths, and operator evidence files remain uncommitted
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_completion_status: NOT_RELEASED
real_google_health_sleep_data: ACCEPTED
```

E-9 closes only `real_google_health_sleep_data`. The next unresolved work is the
Day69 public repository final sweep and the accepted private Web evidence manifest.
The final fixed zip, tag, and v2.0.0 release remain incomplete.
