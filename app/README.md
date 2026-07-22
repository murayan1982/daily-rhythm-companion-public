# Daily Rhythm Companion Flutter App

Flutter frontend for Daily Rhythm Companion.

The app is the user-facing surface for the v1.0 AI Character Framework demo:

```txt
Sleep / context → Mood → Character → Advice → Save → History
```

It connects to the FastAPI backend and displays:

- backend connection status
- sleep summary / unavailable sleep fallback
- mood selection
- character selection
- advice generation results
- DailyRecord save and History flow
- recent sleep trend and weekly summary as conservative historical context
- capability status for LLM, voice input, voice output / TTS, Live2D / VTS motion, and Google Health real API readiness

The Flutter app does not call wearable, Google Health, LLM provider, TTS provider, microphone, or VTube Studio APIs directly. Those capabilities are exposed through backend APIs and should remain optional/config-gated.

## Default backend

Development default:

```txt
http://127.0.0.1:8000
```

This default works when the app and backend are both accessed from the same development machine.

For smartphone Web demo use, `127.0.0.1 points to the phone itself`, not the development PC. The effective backend base URL must point to a phone-accessible backend URL such as:

```txt
http://<PC_LAN_IP>:8000
```

If the app still uses the development default internally, treat smartphone Web access as a v1.0 verification item and update the API base URL configuration before final release readiness.

## Run locally

From this `app/` directory:

```powershell
flutter pub get
flutter test
flutter run
```

## Run as Web server for smartphone demo

From this `app/` directory:

```powershell
flutter run -d web-server --web-hostname 0.0.0.0 --web-port 8080
```

Then open the Web server URL from the smartphone browser, using the development PC's LAN IP address.

See the repository-level docs:

- `docs/quickstart_local.md`
- `docs/quickstart_smartphone_web.md`
- `docs/framework_demo_setup.md`
- `docs/troubleshooting.md`

## Backend APIs used by the app

```txt
GET  /health
GET  /demo/status
GET  /characters
GET  /sleep/summary
POST /advice
GET  /daily-records
POST /daily-records
GET  /daily-records/recent-sleep-trend
GET  /daily-records/weekly-summary
```

Optional demo capability APIs:

```txt
GET  /demo/voice-input/status
POST /demo/voice-input
GET  /demo/voice-output/status
POST /demo/voice-output
GET  /demo/motion/status
POST /demo/motion
```

Google Health state and safe guidance are backend-provided through Google Health API routes. The Flutter app should display safe state and guidance only; it should not expose secrets, raw payloads, local token paths, or Authorization headers.

## UI expectations for v1.0

The UI should make these states understandable:

```txt
available
unavailable
skipped
fallback
guarded
mock-safe
framework mode
```

When optional FW / voice / TTS / Live2D capability is unavailable, the normal text advice and History flow should remain usable.

History, recent sleep trend, and weekly summary should remain conservative. They should not be presented as diagnosis, medical advice, or today's confirmed sleep state.
