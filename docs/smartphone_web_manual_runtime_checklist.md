# Smartphone Web manual runtime checklist

This checklist defines the manual smartphone Web runtime path for the v1.9.0 FW4.0.0 demo hardening milestone.

## Purpose

DRC must be demonstrable from the developer's own smartphone through Web access.

The required runtime path is:

```text
smartphone browser
→ Flutter Web UI
→ actual Daily Rhythm Companion backend API
→ visible UI result
```

Configured FW/provider execution is a later opt-in layer on top of this manual runtime path. Day7 confirms the smartphone Web path itself.

## Network assumptions

```text
- PC and smartphone are on the same local network.
- The PC firewall allows inbound access to the selected backend and Flutter Web ports.
- The operator knows the PC LAN IP address.
```

Placeholder:

```text
<PC_LAN_IP>
```

Do not commit private LAN IP values into public docs.


## Recommended smartphone runtime path

Release build static hosting is the recommended smartphone path.

`flutter run -d chrome` or `flutter run -d web-server` may open or depend on debug-service URLs that are local to the PC. In that case, `localhost` may work while `http://<PC_LAN_IP>:<WEB_PORT>` or smartphone browser access can show a blank page.

Use this stable path for smartphone Web evidence.

### Build Flutter Web

```powershell
cd app
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

### Serve the built Web app

```powershell
python -m http.server 18080 --bind 0.0.0.0 --directory build\web
```

Recommended Web URL shapes:

```text
http://localhost:18080
http://<PC_LAN_IP>:18080
```

Smartphone URL shape:

```text
http://<PC_LAN_IP>:18080
```

The operator verified this path with:

```text
PC localhost URL shape: http://localhost:18080
PC LAN URL shape: http://<PC_LAN_IP>:18080
smartphone browser URL shape: http://<PC_LAN_IP>:18080
visible UI result: DRC Home screen loaded
Backend status: ok
API base URL: http://<PC_LAN_IP>:8000
```

Do not paste the private LAN IP value into public release notes.

## Backend LAN startup

From the repository root:

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected backend API base URL shape:

```text
http://<PC_LAN_IP>:8000
```

Optional desktop preflight from the PC:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://<PC_LAN_IP>:8000/health
```

Do not paste private LAN IP values into public release notes.

## Flutter Web debug startup

This is useful for local development, but the release build static hosting path above is recommended for smartphone browser evidence.

## Flutter Web LAN startup

From another terminal:

```powershell
cd app
flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

Expected Flutter Web URL shape:

```text
http://<PC_LAN_IP>:8080
```

## Smartphone browser access

On the smartphone browser, open:

```text
http://<PC_LAN_IP>:8080
```

The UI should load the Flutter Web app and use:

```text
API base URL: http://<PC_LAN_IP>:8000
```

## Required UI evidence checklist

### Web UI startup

Confirm:

```text
- smartphone browser opens the Flutter Web UI
- API base URL is visible
- API base URL points to http://<PC_LAN_IP>:8000
- backend connection / health status is visible
```

### Character and mood

Confirm:

```text
- character list is visible
- selected character is visible
- mood choice is visible
- selected mood is visible
```

### Sleep summary

Confirm one of:

```text
- sleep summary is visible
- safe unavailable/fallback state is visible
```

### Advice

Confirm:

```text
- advice action can be triggered
- advice result or safe fallback/error state is visible
- source/fallback explanation is visible
```

### DailyRecord save

Confirm:

```text
- DailyRecord save action is visible when advice exists
- save result is visible
```

### History review

Confirm:

```text
- History screen opens
- saved DailyRecord appears when a record was saved
- advice basis/source copy is visible
- report-informed reflection copy is visible when report_handoff was used
```

### Demo status and FW capability surfaces

Confirm visible surfaces for:

```text
- demo status
- voice input demo
- voice output demo
- motion demo
- health data status
- Google Health connection UX or safe unavailable state
```

These surfaces prove UI visibility and backend route wiring only. They do not prove configured real STT, TTS, Live2D/VTS, or Google Health execution unless the later configured checks explicitly run and show configured success.

## Manual evidence record

Safe evidence to record:

```text
- device/browser
- Web UI URL shape
- backend API base URL shape
- selected character
- selected mood
- visible UI result
- visible state: configured success / fallback / unavailable / skipped / error
- whether the run was mock-safe or configured real API
```

Do not record:

```text
- API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- private credential paths
- raw provider payloads
- full provider debug traces
- private absolute paths
- private LAN IP values in public release notes
```

## Day7 completion rule

Day7 completion means the repository documents the manual smartphone Web runtime path.

It does not mean configured real LLM/STT/TTS/Live2D/VTS/Google Health execution has succeeded.
