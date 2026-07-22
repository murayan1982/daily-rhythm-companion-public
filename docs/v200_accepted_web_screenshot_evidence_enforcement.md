# v2.0.0 accepted Web screenshot evidence enforcement

Status marker:

```text
v200_accepted_web_screenshot_evidence_status: accepted-web-screenshot-evidence-enforcement-ready
```

## Purpose

Day73 prevents v2.0.0 from being treated as complete merely because source-tree checks, API-only checks, or marker-only readiness gates pass.

v2.0.0 release completion requires accepted evidence that the real capabilities were executed through the Web UI using the actual Daily Rhythm Companion backend API, and that each Web execution result was confirmed by a screenshot.

## Required rule

```text
Web execution is required for v2.0.0 completion.
A screenshot is required for every Web-executed result.
API-only smoke does not count.
Source-tree-only checks do not count.
Mock, fallback, skipped, unavailable, placeholder, and error states do not count.
```

## Capabilities requiring Web screenshot evidence

Each capability below must have accepted operator evidence:

```text
real_llm_web_answer
real_tts_web_audio_output
real_google_health_sleep_data
web_image_display
```

For each of those capabilities, the operator evidence must confirm:

```text
status=accepted
actual_drc_backend_api_used
web_ui_execution_confirmed
web_execution_result_visible
web_execution_result_screenshot_captured
screenshot_reference_recorded
screenshot_public_safe_redaction_confirmed
operator_review_accepted
not_api_only
not_source_tree_only
not_mock_only
not_fallback
not_skipped
not_unavailable
not_placeholder
```

Additional capability-specific markers are required:

```text
real_llm_web_answer:
- real_provider_response_confirmed

real_tts_web_audio_output:
- real_provider_audio_synthesis_confirmed
- audible_playback_confirmed

real_google_health_sleep_data:
- real_sleep_data_source_confirmed
- sleep_summary_normalized_confirmed

web_image_display:
- repository_safe_asset_displayed
- displayed_asset_identity_confirmed
```

## Non-Web review items

The final evidence record must also confirm:

```text
image_asset_intake_accepted
public_repo_final_sweep_accepted
final_aggregate_review_accepted
all_web_screenshot_evidence_reviewed
```

## Screenshot evidence policy

Screenshots are required as test confirmation evidence, but raw screenshots must not be committed to the public repository or included in the release zip.

Public-safe evidence should store only redacted references such as:

```text
private-operator-evidence://v200/day73/real_llm_web_answer_redacted.png
```

Do not store:

```text
- raw screenshot files in the repo
- local absolute screenshot paths
- private LAN IPs
- screenshots containing secrets, tokens, raw prompts, raw provider payloads, raw health payloads, raw sleep events, or private user data
```

## Operator evidence template

Use this template as a public-safe shape reference:

```text
docs/operator_evidence_templates/v200_accepted_web_screenshot_evidence_day73.example.json
```

A real operator evidence file should be stored outside the public repository, or converted into a redacted public-safe marker summary before being referenced in release handling.

## Verification command

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py

cd app
flutter test
cd ..
```

Optional configured operator evidence validation:

```powershell
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py --operator-evidence-json .\operator_evidence\v200_accepted_web_screenshot_evidence_day73.json
```

## What Day73 does not do

Day73 default checks do not call OpenAI, Gemini, Grok, ElevenLabs, OpenAI TTS, Google Health, Fitbit, AI Character Framework, STT, TTS, Live2D/VTS, VTube Studio, microphones, audio generation, audio playback, image-generation services, backend APIs, Flutter Web, browsers, screenshot tools, release builds, release zip verification, GitHub publication, or external network services.

Day73 records and verifies the enforcement contract only. Configured Web execution and screenshot collection remain explicit operator work.

## Release impact

If Day73 is added after a fixed v2.0.0 release candidate zip was already built, that old zip must not be used for the final v2.0.0 release. After Day73 source changes pass, build one new fixed release candidate zip and restart the fixed-zip verification path.
