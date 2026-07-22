# STT / voice input smartphone Web boundary evidence

Day37 records the v1.9.0 STT / voice input smartphone Web boundary evidence.

This is a guarded boundary proof, not configured STT runtime success. The goal is to verify that the smartphone Web UI can reach the DRC backend voice-input request contract while the app still avoids microphone access, raw audio upload, transcript persistence, FW realtime voice runtime, and STT provider calls.

## Source-tree evidence

```text
voice_input_smartphone_web_boundary_evidence_status: verified
voice_input_smartphone_web_boundary_evidence_mode: source-tree-boundary
voice_input_smartphone_web_boundary_source_mode: voice_input_demo_boundary
voice_input_smartphone_web_boundary_status_route_present: True
voice_input_smartphone_web_boundary_request_route_present: True
voice_input_smartphone_web_boundary_api_client_route_present: True
voice_input_smartphone_web_boundary_flutter_section_visible: True
voice_input_smartphone_web_boundary_flutter_button_visible: True
voice_input_smartphone_web_boundary_request_contract_metadata_only: True
voice_input_smartphone_web_boundary_audio_processing_blocked: True
voice_input_smartphone_web_boundary_microphone_not_used: True
voice_input_smartphone_web_boundary_raw_audio_not_uploaded: True
voice_input_smartphone_web_boundary_transcript_body_hidden_or_absent: True
voice_input_smartphone_web_boundary_public_safe_evidence_only: True
```

Source-tree smoke:

```powershell
python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence.py
```

## Manual smartphone Web evidence

After launching the backend and Flutter Web app on the LAN, confirm the Advanced Demo Tools voice input area on a smartphone browser, press the voice input demo button, and record only booleans:

```powershell
python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --voice-input-section-visible `
  --voice-input-button-visible `
  --voice-input-request-sent `
  --voice-input-response-visible `
  --capability-status-visible `
  --checks-visible `
  --audio-processing-blocked `
  --microphone-not-used `
  --raw-audio-not-uploaded `
  --transcript-body-hidden-or-absent
```

Expected manual result:

```text
voice_input_smartphone_web_boundary_evidence_status: verified
voice_input_smartphone_web_boundary_evidence_mode: manual-smartphone-web-ui-boundary
voice_input_smartphone_web_boundary_source_mode: voice_input_demo_boundary
voice_input_smartphone_web_boundary_request_sent: True
voice_input_smartphone_web_boundary_response_visible: True
voice_input_smartphone_web_boundary_audio_processing_blocked: True
voice_input_smartphone_web_boundary_microphone_not_used: True
voice_input_smartphone_web_boundary_raw_audio_not_uploaded: True
```

## Public-safe policy

Do not record:

```text
- raw audio
- transcript bodies
- prompt bodies
- response bodies
- provider payloads
- API key values
- authorization headers
- private absolute paths
- raw LAN IPs
- raw screenshots
- raw provider error payloads
```

Day37 does not count STT / voice input as configured STT runtime success. It only records the guarded smartphone Web boundary as verified. Configured STT runtime execution remains a separate explicit opt-in decision.
