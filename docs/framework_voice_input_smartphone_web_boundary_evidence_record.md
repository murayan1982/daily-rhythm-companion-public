# STT / voice input smartphone Web boundary evidence record

Day38 records the Day37 STT / voice input smartphone Web boundary evidence as a v1.9.0 public-safe checkpoint.

The record verifies only the guarded DRC voice input demo boundary:

```text
v190_voice_input_smartphone_web_boundary_record_status: recorded
v190_voice_input_smartphone_web_boundary_record_from_evidence_status: verified
v190_voice_input_smartphone_web_boundary_record_source_mode: voice_input_demo_boundary
v190_voice_input_smartphone_web_boundary_record_request_sent: True
v190_voice_input_smartphone_web_boundary_record_response_visible: True
v190_voice_input_smartphone_web_boundary_record_audio_processing_blocked: True
v190_voice_input_smartphone_web_boundary_record_raw_audio_not_uploaded: True
v190_voice_input_smartphone_web_boundary_record_transcript_body_hidden_or_absent: True
```

Manual evidence command:

```powershell
python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence_record.py `
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

The record must not include raw audio, transcript bodies, prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, raw LAN IPs, raw screenshots, microphone access, or raw provider error payloads.

Configured STT runtime execution remains a separate explicit opt-in decision. Day38 does not call STT providers, create AI Character Framework realtime voice sessions, upload audio, or dispatch voice runtime events.
