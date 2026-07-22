# v2.0.0 D-3: real TTS Web audio acceptance gate

Status: acceptance gate ready; real TTS evidence not accepted by source-tree checks alone.

```text
v200_real_tts_web_audio_acceptance_status: real-tts-web-audio-acceptance-gate-ready
```

## Purpose

D-3 is the final marker-only acceptance gate for the v2.0.0 real TTS Web audio output requirement.

This gate combines three already-defined private operator evidence layers:

```text
- Day54 real TTS Web audio output evidence
- Day65 real TTS Web audio execution evidence
- Day77 real TTS Web audio screenshot evidence
```

The gate does not call a TTS provider, call AI Character Framework, start the DRC backend, open Flutter Web, play audio, inspect screenshots, or create release artifacts. It only validates public-safe marker JSON produced after a separate private configured operator run.

## Completion boundary

`real_tts_web_audio_output` may be accepted in the v2.0.0 checklist only when this combined validation returns:

```text
v200_real_tts_web_audio_acceptance_validation_status: accepted
v200_real_tts_web_audio_acceptance_requirement_satisfied: True
```

The validation requires all of the following sources to be accepted together:

```text
day54_output_evidence
day65_execution_evidence
day77_screenshot_evidence
```

A source-tree-only check, command-output-only check, API-only check, mock result, fallback, skipped run, unavailable provider, silent output, or placeholder evidence must not be counted as success.

## Default source-tree check

Use this during normal development:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance.py

cd app
flutter test
cd ..
```

Expected marker:

```text
[smoke-framework-v200-real-tts-web-audio-acceptance] OK
```

This default mode only renders the acceptance contract. It does not satisfy the requirement.

## Private operator validation

After the operator has completed the configured real TTS Web run, audible Web playback confirmation, and private screenshot capture, validate the redacted marker-only JSON files with:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py --operator-evidence-json .\operator_evidence\200_real_tts_web_audio_day54.json
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py --operator-evidence-json .\operator_evidence\200_real_tts_web_audio_day65.json
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py --evidence-json .\operator_evidence\200_real_tts_web_audio_day77.json
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance.py --day54-json .\operator_evidence\200_real_tts_web_audio_day54.json --day65-json .\operator_evidence\200_real_tts_web_audio_day65.json --day77-json .\operator_evidence\200_real_tts_web_audio_day77.json
```

The `operator_evidence\*.json` files are local/private operator records and must not be committed.

## Marker templates

Public-safe examples live under:

```text
docs/operator_evidence_templates/v200_real_tts_web_audio_day54.example.json
docs/operator_evidence_templates/v200_real_tts_web_audio_day65.example.json
docs/operator_evidence_templates/v200_real_tts_web_audio_screenshot_day77.example.json
```

Copy them into a local ignored operator evidence folder only after the real private run. Do not replace `false` or placeholder fields with `true` unless that specific condition was actually observed by the operator.

## Public safety policy

Do not commit or paste:

```text
- API keys
- OAuth tokens
- authorization headers
- provider voice IDs when private
- private synthesis text bodies
- raw provider payloads
- raw provider errors with private payloads
- generated audio files
- raw audio URLs
- raw LAN IPs
- private absolute paths
- raw screenshots
- browser storage dumps
```

Allowed public evidence is limited to marker names, accepted/incomplete status, safe booleans, redacted labels, and opaque screenshot references such as:

```text
private-operator-evidence://v200/day77/real-tts-web-audio-output-screenshot-redacted
```

## Checklist update rule

After the combined D-3 acceptance script returns accepted, update only the real TTS section of `docs/DRC_v200_goal_checklist_small_commit.md`.

Do not mark the following complete from this gate:

```text
real_google_health_sleep_data
web_image_display
public_repo_final_sweep_review
accepted_private_evidence_manifest
final_fixed_release_zip
DRC_v2.0.0 release/tag
```

## Accepted public-safe result

The configured private Web run was later completed and synchronized publicly by D-next-18. The following block is the retained public acceptance record after Cleanup-7 removes the private-run preparation helpers:

```text
commit_scope: Commit D-next-18 only
implementation_status: real-tts-web-audio-acceptance-public-safe-synchronized
accepted_requirement_key: real_tts_web_audio_output
actual_drc_backend_api_status: confirmed
pc_web_audible_playback_status: confirmed
smartphone_web_audible_playback_status: confirmed
day54_output_evidence_status: accepted
day65_execution_evidence_status: accepted
day65_requirement_satisfied: True
day77_screenshot_evidence_status: accepted
day77_public_safe: True
combined_acceptance_status: accepted
combined_requirement_satisfied: True
real_tts_web_audio_output: ACCEPTED
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
private_evidence_policy: raw audio, screenshots, provider payloads, secrets, URLs, LAN IPs, private paths, and operator evidence files remain uncommitted
release_completion_status: NOT_RELEASED
```

The historical later-gate values in this block reflect the D-next-18 commit boundary. Current overall release state remains governed by `docs/DRC_v200_goal_checklist_small_commit.md`.
