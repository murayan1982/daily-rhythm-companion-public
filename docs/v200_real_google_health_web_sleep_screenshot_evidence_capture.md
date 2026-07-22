# v2.0.0 Day78 real Google Health Web sleep screenshot evidence capture

Day78 defines the private evidence item validator for the **real Google Health sleep data** Web execution requirement.

This document is public-safe. It does not contain OAuth tokens, refresh tokens, authorization headers, raw Google Health payloads, raw sleep data exports, raw screenshots, local paths, LAN IPs, or private operator files.

## Status marker

```text
v200_real_google_health_web_sleep_screenshot_evidence_status: real-google-health-web-sleep-screenshot-evidence-validator-ready
```

## Accepted private evidence requirements

Only private operator evidence with all of these markers may feed the Day80 accepted Web evidence manifest:

```text
status=accepted
capability=real_google_health_sleep_data
actual_drc_backend_api_used=true
web_ui_execution_confirmed=true
web_execution_result_visible=true
google_health_sleep_data_visible=true
real_google_health_api_confirmed=true
google_health_oauth_or_valid_token_confirmed=true
normalized_sleep_summary_confirmed=true
data_source_label_visible=true
screenshot_captured=true
screenshot_reference_recorded=true
screenshot_reference=private-operator-evidence://v200/day78/real-google-health-web-sleep-screenshot-redacted
screenshot_private_storage_confirmed=true
screenshot_public_safe_redaction_confirmed=true
operator_review_accepted=true
not_api_only=true
not_source_tree_only=true
not_command_output_only=true
not_mock_only=true
not_fallback=true
not_skipped=true
not_unavailable=true
not_placeholder=true
```

The evidence must come from the Daily Rhythm Companion Web UI using the actual DRC backend API. API-only smoke output, source-tree checks, command output, mock data, fallback data, skipped runs, unavailable states, placeholders, or missing screenshots do not count as v2.0.0 completion.

## Rejected success states

The Day78 validator rejects private evidence that indicates any of the following:

```text
api_only_success
source_tree_only_success
command_output_only_success
web_ui_not_confirmed
google_health_api_not_confirmed
google_health_sleep_data_not_visible
normalized_sleep_summary_not_confirmed
screenshot_missing
screenshot_reference_missing
screenshot_not_reviewed
raw_screenshot_committed
raw_health_data_committed
oauth_token_exposed
authorization_header_exposed
actual_drc_backend_api_not_used
mock_only
fallback_only
skipped
unavailable
placeholder
error
```

## Public-safe omissions

Public docs, release notes, release zips, and shared logs must omit:

```text
api_keys
oauth_tokens
refresh_tokens
authorization_headers
raw_google_health_payloads
raw_sleep_data_exports
raw_screenshot_files
raw_lan_ips
private_paths
production_claims
app_store_claims
medical_claims
```

## Manifest slot

Only `accepted` validation can feed the Day80 accepted Web evidence manifest.

```text
web_evidence.real_google_health_sleep_data
```

Day78 does not itself call Google Health, OAuth endpoints, backend APIs, Flutter Web, browsers, screenshot tools, release builders, fixed-zip checks, GitHub, or external network services in default mode.
