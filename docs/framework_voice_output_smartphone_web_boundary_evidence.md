# FW4.0.0 TTS / voice output smartphone Web boundary evidence

Day40 records the guarded TTS / voice output smartphone Web boundary evidence for v1.9.0.

The goal is to verify that DRC exposes the voice output demo boundary through the backend API and Flutter Web UI without performing configured TTS runtime execution.

Expected source-tree evidence:

```text
voice_output_smartphone_web_boundary_evidence_status: verified
voice_output_smartphone_web_boundary_evidence_mode: source-tree-boundary
voice_output_smartphone_web_boundary_source_mode: voice_output_demo_boundary
voice_output_smartphone_web_boundary_status_route_present: True
voice_output_smartphone_web_boundary_request_route_present: True
voice_output_smartphone_web_boundary_api_client_route_present: True
voice_output_smartphone_web_boundary_flutter_section_visible: True
voice_output_smartphone_web_boundary_flutter_button_visible: True
voice_output_smartphone_web_boundary_request_contract_metadata_only: True
voice_output_smartphone_web_boundary_synthesis_blocked: True
voice_output_smartphone_web_boundary_audio_generation_blocked: True
voice_output_smartphone_web_boundary_audio_playback_not_used: True
voice_output_smartphone_web_boundary_generated_audio_absent: True
voice_output_smartphone_web_boundary_audio_url_hidden_or_absent: True
voice_output_smartphone_web_boundary_text_body_hidden_or_placeholder: True
voice_output_smartphone_web_boundary_provider_call_not_made: True
voice_output_smartphone_web_boundary_public_safe_evidence_only: True
voice_output_smartphone_web_boundary_next_step: record-manual-smartphone-web-voice-output-boundary-evidence
```

Source-tree checks cover:

```text
GET /demo/voice-output/status
POST /demo/voice-output
BackendApiClient.submitVoiceOutputDemoRequest
Voice Output / TTS Demo section
Voice output demo button
metadata-only request fields such as text_content, voice_profile_id, and audio_format
safe response fields where audio_url and audio_format remain absent
```

Configured TTS runtime execution remains a separate explicit opt-in decision. Day40 does not synthesize speech, generate audio files, play sound, call ElevenLabs/OpenAI/Gemini/Grok/TTS providers, import AI Character Framework audio runtime modules, create sessions, connect to Live2D/VTS, or dispatch motion.

Public-safe evidence must not contain synthesized audio, generated audio files, audio URLs, provider payloads, API key values, authorization headers, private paths, raw LAN IPs, raw screenshots, raw provider error payloads, prompt bodies, response bodies, or text bodies beyond placeholder/metadata labels.

Manual smartphone Web evidence can be recorded later with:

```powershell
python scripts\smoke_framework_voice_output_smartphone_web_boundary_evidence.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --voice-output-section-visible `
  --voice-output-button-visible `
  --voice-output-request-sent `
  --voice-output-response-visible `
  --capability-status-visible `
  --checks-visible `
  --synthesis-blocked `
  --audio-generation-blocked `
  --audio-playback-not-used `
  --generated-audio-absent `
  --audio-url-hidden-or-absent `
  --text-body-hidden-or-placeholder `
  --provider-call-not-made
```
