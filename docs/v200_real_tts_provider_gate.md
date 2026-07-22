# v2.0.0 Day53 real TTS provider gate design

Day53 prepares the safe provider gate for the second v2.0.0 pre-release requirement:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

This document does **not** claim that real Web voice output is already satisfied. It defines the boundary that must be in place before a configured real TTS operator run is accepted as evidence.

## Current status

```text
v200_real_tts_provider_gate_status: provider-gate-contract-ready
v200_real_tts_provider_requirement_key: real_tts_web_audio_output
v200_real_tts_provider_operator_run_required: True
v200_real_tts_provider_mock_safe_default: True
```

## Design rule

DRC should not own a provider-specific TTS implementation.

DRC should call a neutral AI Character Framework voice output boundary. The framework side owns provider-specific behavior such as ElevenLabs, future OpenAI TTS, provider voice IDs, provider API keys, endpoint parameters, retries, provider payload parsing, and provider-specific error handling.

## Neutral DRC request contract

The app/backend side may pass neutral fields such as:

```text
voice_profile_id
text
requested_audio_format
character_id
utterance_purpose
```

These fields describe what the app wants. They must not expose provider-specific details such as ElevenLabs voice IDs, provider model IDs, provider API keys, raw request payloads, raw response payloads, or audio storage internals.

Expected marker:

```text
v200_real_tts_provider_neutral_contract_fields: voice_profile_id,text,requested_audio_format,character_id,utterance_purpose
v200_real_tts_provider_drc_provider_specific_implementation: forbidden
v200_real_tts_provider_provider_specific_config_owner: ai-character-framework
```

## Mock-safe default behavior

The default Day53 source-tree check is credential-free. It must not call providers, the backend, the browser, Flutter, Web UI, audio generation, audio playback, AI Character Framework sessions, or framework voice output.

Expected default markers:

```text
v200_real_tts_provider_default_provider_call_status: not-called
v200_real_tts_provider_default_framework_call_status: not-called
v200_real_tts_provider_default_backend_call_status: not-called
v200_real_tts_provider_default_audio_generation_status: not-called
v200_real_tts_provider_default_audio_playback_status: not-started
v200_real_tts_provider_default_audio_artifact_status: not-created
```

## Public-safe evidence policy

Do not record or commit:

```text
- API keys or OAuth secrets
- provider voice IDs when they are private configuration values
- raw provider request payloads
- raw provider response payloads
- private text bodies used for synthesis evidence
- generated audio artifacts
- audio URLs with private/local/LAN details
- raw LAN IPs
- private local paths
- raw screenshots that expose local details
```

Acceptable public evidence should use metadata and redacted markers, for example:

```text
- explicit opt-in was enabled
- configured FW voice output boundary was selected
- provider label was redacted or generic
- requested audio format was public-safe
- audio was generated during the operator run
- Web output was audibly confirmed by the operator
- private text, raw provider payloads, and audio artifacts were not committed
```

## Default check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_provider_gate.py

cd app
flutter test
cd ..
```

## Default smoke renderer

```powershell
python scripts\smoke_framework_v200_real_tts_provider_gate.py
```

## Optional backend status probe

The optional Day53 probe is not a real synthesis check. It may be used by a prepared operator to inspect the backend voice-output status endpoint without logging text bodies, provider payloads, audio URLs, or generated audio.

```powershell
$env:DRC_V200_ENABLE_REAL_TTS_PROVIDER_GATE_SMOKE="1"
$env:DRC_BACKEND_API_BASE_URL="http://127.0.0.1:8000"
python scripts\smoke_framework_v200_real_tts_provider_gate.py --require-running-backend
```

Do not paste raw LAN IPs or private backend URLs into committed evidence.

## Requirement satisfaction boundary

Day53 means the provider gate contract is ready. The v2.0.0 real TTS Web voice output requirement can be marked satisfied only after a later configured operator run confirms:

```text
- explicit opt-in was enabled
- DRC used a neutral FW voice output boundary
- the configured real TTS provider generated audio
- generated audio was exposed through a safe backend contract
- Web output was audibly confirmed
- public evidence omitted private text, API keys, provider payloads, audio artifacts, raw LAN IPs, private paths, and raw screenshots
```
