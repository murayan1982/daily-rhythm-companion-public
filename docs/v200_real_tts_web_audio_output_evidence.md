# v2.0.0 Day54 real TTS Web audio output evidence

Day54 prepares the public-safe evidence contract for the v2.0.0 pre-release requirement:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

Day53 defined the provider gate: DRC should not own a provider-specific TTS implementation, and provider-specific configuration stays behind the AI Character Framework voice output boundary. Day54 builds on that and defines the evidence shape for a configured run that proves real provider synthesis and audible Web output.

Default checks are still mock-safe. They do not call ElevenLabs, OpenAI TTS, AI Character Framework voice output, the backend, a browser, Flutter, audio generation, audio playback, or audio artifact creation.

## Status marker

```text
v200_real_tts_web_audio_evidence_status: operator-evidence-contract-ready
```

This means the evidence contract is ready. It does **not** mean the real TTS Web voice output requirement is satisfied yet.

## Required configured-run evidence

A configured operator run can satisfy this gate only after all of the following are confirmed:

```text
- explicit_operator_opt_in_enabled
- framework_voice_output_boundary_used
- provider_synthesis_confirmed
- safe_backend_audio_contract_confirmed
- web_audio_output_audibly_confirmed
- public_safe_evidence_recorded
```

The configured run should prove:

```text
- the real TTS provider call was explicitly enabled by the operator
- DRC used the neutral AI Character Framework voice output boundary
- provider synthesis completed successfully
- generated audio was exposed to the Web UI through a safe backend audio contract
- the Web UI audibly output the generated voice
- shared evidence is marker-based and public-safe
```

## Public safety policy

Do not record or commit:

```text
- API keys
- provider voice IDs that are private to an account
- private text bodies used for synthesis
- raw provider payloads
- generated audio artifacts
- raw audio URLs
- raw LAN IPs
- private absolute paths
- raw screenshots
- browser storage dumps
```

Public evidence should use only coarse markers, redacted labels, and safe booleans.

## Mock-safe source-tree check

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py

cd app
flutter test
cd ..
```

Expected output includes:

```text
[v200-prerelease-requirements-check] OK
[v200-real-llm-web-answer-day52-check] OK
[v200-real-tts-provider-gate-day53-check] OK
[v200-real-tts-web-audio-output-day54-check] OK
```

## Default smoke renderer

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py
```

Expected marker:

```text
v200_real_tts_web_audio_evidence_status: operator-evidence-contract-ready
```

## Optional redacted operator evidence validation

After a configured manual run, an operator may create a small **local-only** redacted JSON summary. Do not commit the file unless it has been reviewed for public safety.

Example shape:

```json
{
  "explicit_operator_opt_in_enabled": true,
  "framework_voice_output_boundary_used": true,
  "provider_synthesis_confirmed": true,
  "safe_backend_audio_contract_confirmed": true,
  "web_audio_output_audibly_confirmed": true,
  "public_safe_evidence_recorded": true,
  "api_keys_included": false,
  "private_text_bodies_included": false,
  "raw_provider_payloads_included": false,
  "audio_artifacts_committed": false,
  "raw_lan_ips_included": false,
  "private_paths_included": false,
  "raw_screenshots_included": false
}
```

Validation command:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py --operator-evidence-json .\operator_evidence.json
```

This validation does not call providers or play audio. It only checks that a marker-only summary has all required booleans and does not claim unsafe publication.

## Requirement status

Day54 keeps the v2.0.0 real TTS Web voice output requirement pending until a configured operator run confirms real provider synthesis and audible Web output. The source-tree check only confirms that the evidence contract, safety policy, and previous Day52/Day53 gates remain intact.
