# v2.0.0 Day81 final release readiness with accepted Web evidence

```text
v200_final_release_readiness_with_web_evidence_status: final-release-readiness-with-accepted-web-evidence-validator-ready
v200_final_release_readiness_requires_day80_accepted_manifest: true
v200_final_release_readiness_requires_fixed_release_zip: true
v200_final_release_readiness_tag_allowed_without_accepted_manifest: false
v200_final_release_readiness_api_only_counts_as_success: false
v200_final_release_readiness_source_tree_only_counts_as_success: false
v200_final_release_readiness_command_output_only_counts_as_success: false
```

Day81 is the final release readiness correction for v2.0.0. It prevents the project from treating mock-safe gates, source-tree checks, API-only smoke results, placeholder evidence, or fixed-zip checks alone as v2.0.0 completion.

## Required accepted evidence

A v2.0.0 final release may proceed only when final evidence has `status=accepted` and a private Day80 Web execution evidence manifest validates as `accepted`. The accepted manifest must include:

```text
web_evidence.real_llm_web_answer
web_evidence.real_tts_web_audio_output
web_evidence.real_google_health_sleep_data
web_evidence.web_image_display
web_evidence.image_asset_intake_review
web_evidence.public_repo_final_sweep_review
web_evidence.final_aggregate_review
```

For Web-executed real capabilities, the accepted evidence must confirm:

```text
- actual Daily Rhythm Companion backend API was used.
- Web UI execution was confirmed.
- the result was visible in the Web UI.
- a screenshot was captured.
- a public-safe private screenshot reference was recorded.
- operator review accepted the evidence.
```

## Explicit rejection states

The following must not count as v2.0.0 release success:

```text
API-only success
source-tree-only success
command-output-only success
mock-only success
fallback success
skipped success
unavailable success
placeholder success
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

## Public-safe evidence rule

The public repository and release zip may contain only public-safe summaries and private evidence references, for example:

```text
private-operator-evidence://v200/final/web-evidence-manifest-redacted
```

They must not contain raw screenshots, raw prompts, raw provider payloads, raw audio, raw Google Health payloads, API keys, OAuth tokens, authorization headers, private absolute paths, or raw LAN IPs.

## Default check behavior

The default Day81 source-tree check is credential-free. It does not call external providers, Google Health, the Daily Rhythm Companion backend API, Flutter Web, browser automation, screenshot tools, release builders, fixed-zip checks, GitHub, or external network services.

The private operator path may validate a fixed release zip and a private accepted Day80 manifest kept outside the public repository.
