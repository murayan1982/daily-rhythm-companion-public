# v2.0.0 real TTS Web audio screenshot evidence capture

Status: Day77 real TTS Web audio screenshot evidence validator ready

```text
v200_real_tts_web_audio_screenshot_evidence_status: real-tts-web-audio-screenshot-evidence-validator-ready
```

## Purpose

Day77 starts the capability-by-capability real Web execution evidence capture phase.
This Day77 capability is real TTS Web audio output.

Day77 does not complete v2.0.0 by itself. It defines the private evidence item that must be produced after the operator runs the Web UI against the actual Daily Rhythm Companion backend API with a real configured TTS provider and confirms the Web audio output result in the UI.

## Required private evidence item

The private evidence JSON must include:

```text
status=accepted
capability=real_tts_web_audio_output
actual_drc_backend_api_used=true
web_ui_execution_confirmed=true
web_execution_result_visible=true
web_audio_playback_confirmed=true
audio_output_result_visible=true
real_tts_provider_audio_confirmed=true
framework_voice_output_boundary_confirmed=true
screenshot_captured=true
screenshot_reference_recorded=true
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

The evidence feeds the Day80 accepted Web evidence manifest as:

```text
web_evidence.real_tts_web_audio_output
```

## Screenshot requirement

The screenshot must show the Web UI result, not only a terminal or API response.
The screenshot reference in public-safe docs must be an opaque private evidence reference, for example:

```text
private-operator-evidence://v200/day77/real-tts-web-audio-output-screenshot-redacted
```

Raw screenshot files must stay outside the public repository and release zip.

## Rejected states

The evidence is rejected if it is any of the following:

```text
api_only_success
source_tree_only_success
command_output_only_success
web_ui_not_confirmed
web_audio_playback_not_confirmed
audio_output_result_not_visible
screenshot_missing
screenshot_reference_missing
screenshot_not_reviewed
raw_screenshot_committed
actual_drc_backend_api_not_used
mock_only
fallback_only
skipped
unavailable
placeholder
error
```

The evidence is also rejected if it exposes API keys, OAuth tokens, authorization headers, raw prompts, raw audios, raw provider payloads, raw screenshot files, raw LAN IPs, private paths, production claims, app store claims, or medical claims.

## Default source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
```

## Optional private operator validation

After the operator runs the real Web TTS audio flow and captures private screenshots:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py --evidence-json "<private-real-tts-web-evidence-json>"
```

Only `accepted` validation can feed the Day80 accepted Web evidence manifest.

## Non-goals

Default Day77 checks do not call ElevenLabs, OpenAI TTS, configured FW TTS providers, AI Character Framework, backend APIs, Flutter Web, browser automation, screenshot tools, release builds, release zips, GitHub, or external network services.
