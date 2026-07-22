# Smartphone Web runtime inventory

This document records the current runtime path for the v1.9.0 smartphone Web FW4.0.0 demo hardening milestone.

## Purpose

DRC must be demonstrable from the developer's own smartphone through Web access.

The required path is:

```text
smartphone browser
→ Flutter Web UI
→ actual Daily Rhythm Companion backend API
→ configured AI Character Framework integration where configured
→ visible result in the Web UI
```

Day2 is an inventory step. It documents the current implementation state and identifies the gaps that later v1.9.0 days should close.

## Current Flutter Web API client

Current file:

```text
app/lib/services/backend_api_client.dart
```

Current default after the Day6 update:

```text
BackendApiClient.defaultBaseUrl
String.fromEnvironment('DRC_BACKEND_API_BASE_URL', defaultValue: 'http://127.0.0.1:8000')
```

This default remains useful for local desktop Chrome smoke tests.

For smartphone Web demonstration, Flutter Web can use a LAN-accessible backend URL such as:

```text
--dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

Day6 update: the Home screen also displays the active API base URL so the operator can verify which backend the browser UI is using without exposing secrets.

## Current API calls used by the Web UI

`BackendApiClient` currently covers the main runtime surfaces:

```text
GET  /health
GET  /demo/status
GET  /characters
GET  /sleep/summary
GET  /daily-records
GET  /daily-records/recent-sleep-trend
GET  /daily-records/weekly-summary
GET  /daily-records/rhythm-report
GET  /fitbit/status
GET  /fitbit/connect
GET  /google-health/connection-ux
GET  /google-health/diagnostics
GET  /google-health/self-check
GET  /google-health/preflight
POST /demo/voice-input
POST /demo/voice-output
POST /demo/motion
POST /advice
```

These calls show that the app already has a broad backend API surface for daily loop, reports, health data status, and configured demo tools.

## Current Web UI surfaces

Current file:

```text
app/lib/screens/home_screen.dart
```

The Home screen currently includes visible sections for:

```text
- backend connection / reload
- daily loop status
- daily loop demo context
- character choice
- mood choice
- advice action
- advice result
- DailyRecord save result
- report-informed advice context when present
- advanced demo tools
- demo status
- voice input demo
- voice output demo
- motion demo
- health data status
- Google Health connection UX
- Google Health developer checks
```

Current file:

```text
app/lib/screens/history_screen.dart
```

The History screen currently includes visible record/review surfaces such as:

```text
- saved DailyRecord list
- advice message summary
- advice basis
- source display
- report-informed reflection copy when present
```

## Current FW4.0.0-era capability status

### LLM

The app has an advice flow through `/advice`.

Current status:

```text
- mock-safe advice path exists.
- framework / framework_fallback source labels exist from earlier v1.3.0 work.
- configured provider-backed LLM remains optional and explicitly gated.
```

Day2 gap:

```text
Smartphone Web verification still needs a clear configured LLM demo evidence path showing the UI-visible result, not only API output.
```

### STT / voice input

Current backend files:

```text
backend/app/api/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
```

Current behavior:

```text
- GET /demo/voice-input/status returns guarded status.
- POST /demo/voice-input accepts a metadata-only voice input demo request.
- It does not process audio yet.
```

Day2 gap:

```text
Current voice input demo can prove request/status UI wiring, but not real STT execution.
Later v1.9.0 work must distinguish UI-visible placeholder/status from configured real STT success.
```

### TTS / voice output

Current backend files:

```text
backend/app/api/voice_output_demo.py
backend/app/services/voice_output_demo_service.py
```

Current behavior:

```text
- GET /demo/voice-output/status returns guarded status.
- POST /demo/voice-output accepts a metadata-only voice output demo request.
- It does not perform TTS yet.
```

Day2 gap:

```text
Current voice output demo can prove request/status UI wiring, but not real ElevenLabs or FW TTS execution.
Later v1.9.0 work must define configured TTS evidence separately.
```

### Live2D / VTS motion

Current backend files:

```text
backend/app/api/motion_demo.py
backend/app/services/motion_demo_service.py
```

Current behavior:

```text
- GET /demo/motion/status returns guarded status.
- POST /demo/motion accepts a metadata-only Live2D/VTS motion request.
- It does not connect to VTube Studio, load Live2D runtime dependencies, or send motion commands yet.
```

Day2 gap:

```text
Current motion demo can prove motion request/status UI wiring, but not real VTS execution.
Later v1.9.0 work must define configured VTS evidence separately.
```

## Current smartphone Web gap list

```text
- BackendApiClient default is desktop-local 127.0.0.1.
- A documented smartphone-accessible backend base URL path is needed.
- Web UI result evidence rules exist as requirements, but not yet as an executable/manual checklist for each capability.
- STT / TTS / Live2D-VTS endpoints are still safe contract placeholders, not real execution proof.
- Configured real API environment variables exist as placeholders, but the runtime checks still need explicit follow-up implementation.
- Web UI capability evidence must separate configured success from skipped / unavailable / fallback.
```

## Day2 conclusion

The app already has useful Web UI and backend API surfaces for the required public demo direction.

The next v1.9.0 work should focus on:

```text
- making smartphone-accessible backend API configuration explicit
- mapping each FW4.0.0-era capability to a Web UI surface
- defining exact UI-visible evidence for configured success
- preserving mock-safe and safe fallback behavior
```
