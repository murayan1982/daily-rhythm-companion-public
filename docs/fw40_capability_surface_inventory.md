# FW4.0.0 capability surface inventory

This document maps FW4.0.0-era capability targets to the current DRC backend, Web UI, and configuration surfaces.

## Purpose

DRC is a public demo app for AI Character Framework.

v1.9.0 must move toward this required demo path:

```text
smartphone browser
→ Flutter Web UI
→ actual Daily Rhythm Companion backend API
→ configured AI Character Framework / provider runtime
→ visible UI result
```

Day3 records the current capability surface inventory before implementing additional runtime behavior.

## Capability target summary

```text
LLM
STT / voice input
TTS / voice output
Live2D / VTS motion
```

For each capability, DRC must distinguish:

```text
- backend endpoint exists
- Web UI can trigger or display status
- configured real execution actually succeeded
```

The first two are necessary but not sufficient for the third.

## LLM

### Current backend surface

Primary endpoint:

```text
POST /advice
```

Primary files:

```text
backend/app/api/advice.py
backend/app/models/advice.py
backend/app/services/advice_prompt_builder.py
```

Related source/fallback contract:

```text
AdviceSource
mock
framework
framework_fallback
```

Configured real API placeholders:

```text
OPENAI_API_KEY
GEMINI_API_KEY
GOOGLE_API_KEY
XAI_API_KEY
DRC_FW40_ENABLE_LLM_REAL_API_SMOKE
```

### Current Web UI surface

Primary file:

```text
app/lib/screens/home_screen.dart
```

Current visible areas:

```text
- character choice
- mood choice
- advice action
- advice result
- source/fallback explanation
- DailyRecord save result
- report-informed advice context when present
```

### Current evidence status

LLM has the strongest current DRC path because `/advice` already drives the daily advice loop and earlier v1.3.0 work established framework/fallback source-label behavior.

Current gap:

```text
Smartphone Web verification still needs configured provider-backed evidence from the UI.
API-only output is not enough.
framework_fallback is not configured real LLM success.
```

### Configured success evidence later required

A later v1.9.0 check should verify:

```text
- configured provider/FW mode is explicitly enabled
- /advice returns a framework-backed or configured provider-backed result
- Home advice result shows the generated message
- UI shows source/fallback state clearly
- no secret, raw provider payload, authorization header, or private path appears in shared logs
```

## STT / voice input

### Current backend surface

Primary endpoint group:

```text
GET  /demo/voice-input/status
POST /demo/voice-input
```

Primary files:

```text
backend/app/api/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
backend/app/models/voice_input_demo.py
```

Configuration gate:

```text
VOICE_INPUT_DEMO_ENABLED
```

Configured real API placeholders:

```text
DRC_FW40_ENABLE_STT_REAL_API_SMOKE
```

### Current Web UI surface

Primary file:

```text
app/lib/screens/home_screen.dart
```

Current visible area:

```text
voice input demo
```

Current client call surface:

```text
app/lib/services/backend_api_client.dart
POST /demo/voice-input
```

### Current evidence status

Current STT demo surface is a safe request/status boundary.

It can prove:

```text
- Web UI can call the voice input demo endpoint
- backend can return a guarded status/result
- unavailable/skipped behavior can be surfaced safely
```

It does not yet prove:

```text
real STT execution
audio capture
audio upload
speech recognition result from a configured provider
```

### Configured success evidence later required

A later v1.9.0 check should verify:

```text
- configured STT path is explicitly enabled
- smartphone Web UI can initiate the voice input demo path
- recognized text or configured STT result is visible in the UI
- skipped / unavailable / fallback is not counted as configured success
```

## TTS / voice output

### Current backend surface

Primary endpoint group:

```text
GET  /demo/voice-output/status
POST /demo/voice-output
```

Primary files:

```text
backend/app/api/voice_output_demo.py
backend/app/services/voice_output_demo_service.py
backend/app/models/voice_output_demo.py
```

Configuration gate:

```text
VOICE_OUTPUT_DEMO_ENABLED
```

Configured real API placeholders:

```text
ELEVENLABS_API_KEY
DRC_FW40_ENABLE_TTS_REAL_API_SMOKE
```

### Current Web UI surface

Primary file:

```text
app/lib/screens/home_screen.dart
```

Current visible area:

```text
voice output demo
```

Current client call surface:

```text
app/lib/services/backend_api_client.dart
POST /demo/voice-output
```

### Current evidence status

Current TTS demo surface is a safe request/status boundary.

It can prove:

```text
- Web UI can call the voice output demo endpoint
- backend can return a guarded status/result
- unavailable/skipped behavior can be surfaced safely
```

It does not yet prove:

```text
real ElevenLabs execution
FW voice output boundary execution
audio generation
audio playback from the smartphone Web UI
```

### Configured success evidence later required

A later v1.9.0 check should verify:

```text
- configured TTS path is explicitly enabled
- ElevenLabs or FW voice output provider is selected safely
- UI shows TTS request/result status
- if audio playback is added, the UI shows playback state
- skipped / unavailable / fallback is not counted as configured success
```

## Live2D / VTS motion

### Current backend surface

Primary endpoint group:

```text
GET  /demo/motion/status
POST /demo/motion
```

Primary files:

```text
backend/app/api/motion_demo.py
backend/app/services/motion_demo_service.py
backend/app/models/motion_demo.py
```

Configuration gate:

```text
MOTION_DEMO_ENABLED
```

Configured runtime placeholder:

```text
DRC_FW40_ENABLE_LIVE2D_VTS_RUNTIME_SMOKE
```

### Current Web UI surface

Primary file:

```text
app/lib/screens/home_screen.dart
```

Current visible area:

```text
motion demo
```

Current client call surface:

```text
app/lib/services/backend_api_client.dart
POST /demo/motion
```

### Current evidence status

Current Live2D/VTS motion demo surface is a safe request/status boundary.

It can prove:

```text
- Web UI can call the motion demo endpoint
- backend can return a guarded status/result
- unavailable/skipped behavior can be surfaced safely
```

It does not yet prove:

```text
real VTube Studio connection
real Live2D model loading
real VTS motion command dispatch
visible model motion
```

### Configured success evidence later required

A later v1.9.0 check should verify:

```text
- configured Live2D/VTS path is explicitly enabled
- VTS connection or equivalent FW runtime bridge is available
- UI shows motion trigger/result status
- visible motion evidence is captured manually or through a safe status indicator
- skipped / unavailable / fallback is not counted as configured success
```

## Cross-capability verification rule

For every capability:

```text
API route exists != configured real execution succeeded
Web UI button exists != configured real execution succeeded
status endpoint exists != configured real execution succeeded
```

Configured success requires:

```text
- explicit opt-in
- configured runtime/provider available
- actual backend API call
- Web UI visible result
- safe logs with no secrets or raw provider payloads
```

## Day3 gap list

```text
- LLM needs smartphone Web configured-provider evidence.
- STT needs real speech recognition evidence, not only metadata-only request/status wiring.
- TTS needs real voice output / audio generation evidence, not only metadata-only request/status wiring.
- Live2D/VTS needs real VTS connection or motion evidence, not only metadata-only request/status wiring.
- Each capability needs a later executable or manual Web UI evidence checklist.
```

## Day3 conclusion

DRC already has useful backend and Web UI surfaces for all FW4.0.0-era capability categories.

The next work should convert this inventory into:

```text
- per-capability configured success criteria
- smartphone Web UI evidence steps
- explicit runtime configuration gates
- safe provider execution checks where available
```
