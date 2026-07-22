# v2.0.0 Day65: Real TTS Web audio output execution evidence

Day65 starts the real execution evidence phase for the second v2.0.0 completion requirement:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

Day53 prepared the provider gate and Day54 prepared the public-safe evidence gate. Day65 does **not** replace those gates. It adds a marker-only acceptance layer for a configured operator run that has already confirmed real provider synthesis and audible smartphone Web playback.

## Completion boundary

The Day65 real TTS Web audio requirement can be accepted only when all of the following are true:

```text
v200_real_tts_web_audio_execution_evidence_status: operator-execution-evidence-contract-ready
v200_real_tts_web_audio_execution_requirement_key: real_tts_web_audio_output
v200_real_tts_web_audio_execution_operator_run_required: True
v200_real_tts_web_audio_execution_mock_safe_default: True
```

The actual accepted operator evidence must confirm:

```text
explicit_operator_opt_in_enabled
framework_voice_output_boundary_used
neutral_voice_contract_used
real_provider_synthesis_confirmed
safe_backend_audio_contract_confirmed
smartphone_web_audio_audibly_confirmed
fallback_or_skip_not_counted
public_safe_evidence_recorded
```

The configured run must use the AI Character Framework voice output boundary. DRC should pass a neutral request contract, not provider-specific values. The public evidence may confirm that provider synthesis and Web audio playback happened, but it must not include the synthesized text body, provider payloads, generated audio artifacts, private audio URLs, provider voice IDs, or screenshots.

`mock`, `framework_fallback`, `provider_unavailable`, `synthesis_failed`, `playback_failed`, `skipped`, `unavailable`, and `error` are useful states to display, but they must not be counted as real execution success.

## Mock-safe source-tree check

Use this check during normal local development and CI-like verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py

cd app
flutter test
cd ..
```

Expected marker:

```text
[v200-real-tts-web-audio-execution-day65-check] OK
```

The default check does not call providers, call AI Character Framework voice output, start a backend, open a browser, synthesize audio, play audio, inspect audio artifacts, read audio URLs, or validate screenshots. It verifies the Day65 evidence contract and validates the public-safe example marker file only.

## Configured operator run outline

Run this only in a private local/demo environment with real TTS credentials configured through private environment variables and the AI Character Framework voice output boundary configured.

1. Start the backend with the configured framework voice output route.
2. Confirm the real TTS provider path is explicitly enabled by the operator.
3. Confirm DRC uses the neutral FW voice output boundary instead of provider-specific DRC code.
4. Trigger the Web voice output path from the DRC UI or the documented demo boundary.
5. Confirm real provider synthesis completed.
6. Confirm generated audio is exposed to Web through a safe backend audio contract.
7. Open the Web UI from the smartphone browser.
8. Trigger or play the generated voice from the smartphone Web UI.
9. Confirm the audio is audibly heard.
10. Record only marker-only public-safe evidence.

Optional Day54 evidence validation can still be used as a pre-check:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py --operator-evidence-json .\operator_evidence\200_real_tts_web_audio_day54.json
```

Day65 evidence must additionally prove the execution-success boundary: real provider synthesis, safe backend audio exposure, and audible smartphone Web playback cannot be fallback, skipped, unavailable, or failed states.

## Marker-only evidence JSON

After the configured operator run, create a small redacted JSON file outside normal source control, or copy the template under `docs/operator_evidence_templates/` and keep only boolean markers.

Validate it with:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py --operator-evidence-json .\operator_evidence\200_real_tts_web_audio_day65.json
```

The accepted marker-only shape is:

```json
{
  "explicit_operator_opt_in_enabled": true,
  "framework_voice_output_boundary_used": true,
  "neutral_voice_contract_used": true,
  "real_provider_synthesis_confirmed": true,
  "safe_backend_audio_contract_confirmed": true,
  "smartphone_web_audio_audibly_confirmed": true,
  "fallback_or_skip_not_counted": true,
  "public_safe_evidence_recorded": true
}
```

Do not add raw values to this JSON. It should contain booleans only.

## Public-safe evidence policy

Public evidence may include:

```text
- check names and OK/SKIP/ERROR statuses
- configured FW voice output boundary confirmation
- neutral contract confirmation
- provider synthesis success marker
- safe backend audio contract marker
- audible smartphone Web playback confirmation
- requested audio format label, if public-safe
- redacted backend URL shape such as http://<PC_LAN_IP>:8000
- redacted execution date
```

Public evidence must not include:

```text
- API keys
- provider voice IDs when they are private configuration values
- private text bodies used for synthesis
- raw provider payloads
- raw provider errors that include private payloads
- generated audio artifacts
- raw audio URLs
- raw LAN IPs
- private absolute paths
- raw screenshots
- browser storage dumps
```

## What Day65 does not complete

Day65 accepts only the second v2.0.0 real execution requirement when a configured operator evidence JSON validates successfully.

Day65 does not complete:

```text
- real Google Health sleep data evidence
- Web image display execution evidence
- public repo readiness final sweep
- v2.0.0 final aggregate gate
- fixed v2.0.0 release zip verification
```

Until the remaining requirements are accepted, v2.0.0 release readiness remains incomplete.
