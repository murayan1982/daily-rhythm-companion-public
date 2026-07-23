# v2.1.0 W-5b2 — Configured Google Health API operator verification

Status: EXECUTED / NOT_ACCEPTED

Execution date: 2026-07-24

## Purpose

W-5b2 verifies the configured Google Health API path with an ignored local
operator environment, stored Google OAuth credentials and token state, an
explicit real HTTP opt-in, the normalized backend `SleepSummary`, and actual PC
and smartphone Flutter Web presentation.

This record contains public-safe boolean and classification markers only. It
contains no credential value, token value, authorization code, raw Google Health
payload, exact private sleep value, private path, LAN address, or raw screenshot.

## Execution boundary

```text
- existing ignored operator env, credentials, and token files were reused;
- the operator env preflight and launcher ValidateOnly checks passed;
- no new OAuth browser or authorization-code exchange was required in this run;
- the stored access token required refresh and the guarded refresh path succeeded;
- the operator explicitly allowed the real Google Health request;
- the actual backend and Flutter Web were used;
- screenshots were reviewed but remain outside Git;
- release artifacts, tags, GitHub Releases, and publication records were unchanged.
```

## Public-safe execution result

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
fitbit_origin_provenance=not-separately-confirmed
release_records_changed=False
```

## Provenance note

The configured provider and UI source are confirmed as `google_health` / Google
Health. The current normalized response and UI do not expose a separate device
provenance field, so this record does not infer or publish a Fitbit-device origin.
If the operator can independently confirm that the displayed sleep was measured
by the Fitbit device, that confirmation may be recorded later as a boolean marker
without publishing device identifiers or private sleep values.

## Evidence handling

The reviewed PC and smartphone images contain personal health details. They must
not be added to Git, a release ZIP, issue, pull request, or public documentation.
Only the marker names and boolean/classification results above are Public-safe.

## Acceptance boundary

This execution record does not by itself accept W-5b2 or complete parent W-5.
Acceptance still requires:

```text
- source-tree checks and the full credential-free backend/Flutter suites;
- diff review and operator approval;
- a separate acceptance synchronization commit;
- continued W-5 parent CURRENT / NOT_COMPLETED status until that sync passes.
```

C-1 through R-1 remain planned. No release-readiness or release completion state
is advanced by this record.
