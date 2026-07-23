# v2.1.0 W-5b2 — Configured Google Health API operator verification

Status: COMPLETED / ACCEPTED

Execution date: 2026-07-24
Acceptance date: 2026-07-24
Execution-record commit: `ed50d9e`

## Purpose

W-5b2 verified the configured Google Health API path with an ignored local
operator environment, stored Google OAuth credentials and token state, an
explicit real HTTP opt-in, the normalized backend `SleepSummary`, and actual PC
and smartphone Flutter Web presentation.

This accepted record contains public-safe boolean and classification markers
only. It contains no credential value, token value, authorization code, raw
Google Health payload, exact private sleep value, private path, LAN address, or
raw screenshot.

## Accepted execution boundary

```text
- existing ignored operator env, credentials, and token files were reused;
- the operator env preflight and launcher ValidateOnly checks passed;
- no new OAuth browser or authorization-code exchange was required in this run;
- the stored access token required refresh and the guarded refresh path succeeded;
- the operator explicitly allowed the real Google Health request;
- the actual backend and Flutter Web were used;
- PC and smartphone screenshots were reviewed but remain outside Git;
- the operator independently confirmed that the displayed sleep was measured by
  a Fitbit Versa 2 and delivered through the Google Health API path;
- no serial number, account identifier, exact private sleep value, or screenshot
  was published;
- release artifacts, tags, GitHub Releases, and publication records were unchanged.
```

## Public-safe accepted result

```text
operator_env_validation=accepted
operator_private_files_git_ignored=True
credentials_file_exists=True
token_file_exists=True
actual_run_checkpoint=passed
backend_started=True
initial_preflight_status=needs_token_refresh
ready_for_token_refresh=True
token_stored=True
has_refresh_token=True
access_token_expired_before_refresh=True
refresh_recommended_before_refresh=True
real_api_requests_allowed=True
token_refresh_succeeded=True
post_refresh_preflight_status=ready_for_real_api
ready_for_real_api_request=True
refresh_recommended_after_refresh=False
real_http_attempted=True
google_health_http_status=200
google_health_source_status=ok
safe_to_use_sleep_summary=True
backend_sleep_summary_source=google_health
backend_sleep_summary_available=True
backend_sleep_summary_is_real_data=True
backend_sleep_summary_positive_duration=True
provider_error_summary=None
pc_web_display=True
smartphone_web_display=True
data_source_label=Google Health
data_kind_label=実データ
availability_label=取得済み
normalized_sleep_summary_visible=True
pc_web_screenshot_reviewed=True
smartphone_web_screenshot_reviewed=True
raw_screenshot_committed=False
fitbit_origin_provenance=operator-confirmed
fitbit_origin_device_model=Fitbit Versa 2
backend_pytest=100 passed
flutter_test=57 passed
diff_review=passed
operator_approval=passed
release_records_changed=False
```

## Provenance note

The configured provider and UI source are confirmed as `google_health` / Google
Health. Separately, the operator confirmed that the accepted displayed sleep was
measured by a Fitbit Versa 2. This is a device-model provenance confirmation, not
a claim that the API exposes a device-provenance field. No device identifier,
account information, raw provider payload, or private sleep value is recorded.

## Evidence handling

The reviewed PC and smartphone images contain personal health details. They must
not be added to Git, a release ZIP, issue, pull request, or public documentation.
Only the marker names and boolean/classification results above are Public-safe.

## Accepted verification

W-5b2 acceptance was synchronized after all of the following passed:

```text
- execution-record commit: ed50d9e
- operator env preflight and launcher ValidateOnly: passed
- guarded stored-token refresh: succeeded
- real Google Health API request: HTTP 200 / source status ok
- normalized backend SleepSummary: available real data with positive duration
- PC Flutter Web display: passed
- smartphone Flutter Web display: passed
- Fitbit-origin device model: operator-confirmed Fitbit Versa 2
- W-1 through W-5b2 source-tree checks: passed
- v2.0.x compatibility and maintenance guards: passed
- full backend pytest: 100 passed
- full Flutter test: 57 passed
- diff review and operator approval: passed
- raw screenshot committed: false
- release records changed: false
```

W-5b2 and parent W-5 are `COMPLETED / ACCEPTED`. C-1 is now `CURRENT /
NOT_COMPLETED`; T-1, V-1, and R-1 remain planned. No release-readiness or release
completion state is advanced by this acceptance.
