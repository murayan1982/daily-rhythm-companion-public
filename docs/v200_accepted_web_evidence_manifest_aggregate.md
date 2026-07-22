# v2.0.0 Day80 accepted Web evidence manifest aggregate

Day80 defines the private manifest aggregate validator for **accepted Web execution screenshot evidence**.

This document is public-safe. It does not contain raw screenshots, raw prompts, raw provider payloads, raw audio, raw Google Health data, OAuth tokens, API keys, local paths, LAN IPs, private operator files, or release-only screenshots.

## Status marker

```text
v200_accepted_web_evidence_manifest_aggregate_status: accepted-web-evidence-manifest-aggregate-validator-ready
```

## Accepted private manifest requirements

Only a private operator evidence manifest with all of these aggregate markers may be treated as v2.0.0 completion evidence:

```text
status=accepted
release_target=v2.0.0
manifest_kind=private_web_execution_evidence
all_required_evidence_items_accepted=true
actual_drc_backend_api_used_for_web_capabilities=true
web_ui_execution_confirmed_for_web_capabilities=true
web_execution_results_visible=true
all_required_screenshots_captured=true
all_screenshot_references_recorded=true
screenshot_references_public_safe=true
screenshots_private_storage_confirmed=true
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

The manifest must include accepted evidence for each item:

```text
web_evidence.real_llm_web_answer
web_evidence.real_tts_web_audio_output
web_evidence.real_google_health_sleep_data
web_evidence.web_image_display
web_evidence.image_asset_intake_review
web_evidence.public_repo_final_sweep_review
web_evidence.final_aggregate_review
```

The four Web capability items must also include:

```text
actual_drc_backend_api_used=true
web_ui_execution_confirmed=true
web_execution_result_visible=true
screenshot_captured=true
screenshot_reference_recorded=true
screenshot_reference=private-operator-evidence://...
screenshot_private_storage_confirmed=true
operator_review_accepted=true
```

The aggregate requires that the actual DRC backend API was used. It also requires that each Web result was visible in the Web UI and that a screenshot was captured.

## Rejected states

The aggregate validator rejects these states as v2.0.0 completion evidence:

```text
api_only_success
source_tree_only_success
command_output_only_success
mock_only_success
fallback_success
skipped_success
unavailable_success
placeholder_success
web_ui_not_confirmed
actual_drc_backend_api_not_used
screenshot_missing
screenshot_reference_missing
screenshot_not_reviewed
raw_screenshot_committed
raw_provider_payload_committed
raw_audio_committed
raw_health_data_committed
private_path_exposed
raw_lan_ip_exposed
api_key_exposed
oauth_token_exposed
authorization_header_exposed
medical_claim
production_claim
app_store_claim
```

## Public-safe omissions

Public docs, release notes, release zips, and repository files must omit:

```text
raw_screenshot_files
raw_prompts
raw_provider_payloads
raw_audio_files
raw_google_health_payloads
api_keys
oauth_tokens
authorization_headers
local_paths
raw_lan_ips
private_operator_files
production_claims
app_store_claims
medical_claims
```

## Default check behavior

Default checks are marker-only and credential-free. They do not:

```text
- call LLM providers
- call TTS providers
- call Google Health
- start the DRC backend
- run Flutter Web
- open browser automation
- inspect screenshot files
- inspect audio files
- inspect raw generated images
- create or inspect release zips
- call GitHub
- use external network services
```

## Private operator manifest authoring handoff

Use this exact ignored local destination:

```text
operator_evidence/v200_accepted_web_evidence_manifest_day80.json
```

Create the local candidate from the public non-accepted example, then edit only the ignored copy after reviewing the already accepted private evidence records:

```powershell
Copy-Item `
  .\docs\operator_evidence_templates\v200_accepted_web_evidence_manifest_day80.example.json `
  .\operator_evidence\v200_accepted_web_evidence_manifest_day80.json
```

The copied example is intentionally rejected until every required marker is grounded in the actual private evidence set. Do not set `status=accepted`, aggregate markers, item statuses, screenshot markers, or operator-review markers merely to satisfy the validator.

Validate the ignored private manifest with:

```powershell
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py `
  --manifest-json .\operator_evidence\v200_accepted_web_evidence_manifest_day80.json
```

Expected accepted result after the operator has reviewed and populated the real private evidence manifest:

```text
v200_accepted_web_evidence_manifest_aggregate_validation_status: accepted
v200_accepted_web_evidence_manifest_aggregate_public_safe: True
v200_accepted_web_evidence_manifest_aggregate_screenshot_references_public_safe: True
v200_accepted_web_evidence_manifest_aggregate_required_items_accepted: True
v200_accepted_web_evidence_manifest_aggregate_forbidden_success_states_absent: True
[smoke-framework-v200-accepted-web-evidence-manifest-aggregate] OK
```

Keep the manifest, raw screenshots, raw audio, raw health data, provider payloads, exact endpoints, LAN IPs, and private paths under ignored/private storage. Only a later public-safe acceptance synchronization may update the committed checklist status.

## G-5 public-safe acceptance synchronization

The ignored private Day80 manifest has been populated from the accepted private evidence set and validated successfully. The public repository records only the following public-safe acceptance markers:

```text
commit_scope: Commit G-5 only
implementation_status: accepted-private-evidence-manifest-public-safe-synchronized
accepted_requirement_key: accepted_private_evidence_manifest
day80_private_manifest_validation_status: accepted
day80_private_manifest_public_safe: True
day80_screenshot_references_public_safe: True
day80_required_items_accepted: True
day80_forbidden_success_states_absent: True
required_evidence_items: real_llm_web_answer,real_tts_web_audio_output,real_google_health_sleep_data,web_image_display,image_asset_intake_review,public_repo_final_sweep_review,final_aggregate_review
actual_drc_backend_api_used_for_web_capabilities: True
web_ui_execution_confirmed_for_web_capabilities: True
web_execution_results_visible: True
all_required_screenshots_captured: True
all_screenshot_references_recorded: True
screenshots_private_storage_confirmed: True
operator_review_accepted: True
api_only_source_tree_command_output_rejected: True
mock_fallback_skipped_unavailable_placeholder_rejected: True
private_manifest_committed: False
raw_evidence_committed: False
private_evidence_policy: raw screenshots, audio, health data, prompts, provider payloads, secrets, tokens, LAN IPs, private paths, and operator evidence files remain ignored and uncommitted
accepted_private_evidence_manifest: ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_completion_status: NOT_RELEASED
```

The source-tree acceptance synchronization does not read the ignored manifest or inspect raw screenshots, audio, health data, prompts, provider payloads, LAN IPs, or private paths. It verifies only committed public-safe status markers. The next unresolved gate is to build one final fixed release zip after this acceptance and verify that same artifact without rebuilding.

## Release rule

Day80 does not complete v2.0.0 by itself. It only defines the aggregate validator for private evidence. The release may proceed only after the private manifest validates as accepted and later fixed-zip checks are rerun against a new fixed release candidate.

API-only, source-tree-only, command-output-only, mock-only, fallback, skipped, unavailable, placeholder, and screenshot-missing evidence must not count as v2.0.0 completion.
