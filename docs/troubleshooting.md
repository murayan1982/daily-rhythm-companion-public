# Troubleshooting

## Backend does not start

Check that the backend virtual environment is active and dependencies are installed:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```txt
http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

## Flutter app cannot reach backend on the development PC

Confirm the backend is running at the URL the app uses.

Development default:

```txt
http://127.0.0.1:8000
```

Also check:

- backend process is still running
- port 8000 is not blocked or occupied
- CORS middleware is enabled by backend
- the app is using the expected backend base URL

## Smartphone Web UI opens but backend calls fail

Most likely cause: the app is calling `127.0.0.1` from the phone.

On a smartphone, `127.0.0.1` is the phone itself. Use the development PC's LAN IP or a tunnel URL.

Backend should be started for LAN access:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Flutter Web can be started for LAN access:

```powershell
cd app
flutter run -d web-server --web-hostname 0.0.0.0 --web-port 8080
```

Then open from the phone:

```txt
http://<PC_LAN_IP>:8080
```

Confirm the app's effective backend API base URL points to:

```txt
http://<PC_LAN_IP>:8000
```

## Phone cannot open backend health URL

Check:

- phone and PC are on the same network
- Wi-Fi isolation is disabled
- VPN is not separating the devices
- firewall allows inbound traffic to port 8000
- backend is bound to `0.0.0.0`, not only `127.0.0.1`
- the LAN IP address is correct

## Framework mode does not work

Return to mock-safe mode first:

```env
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=mock
```

Then verify the app works without framework mode.

For framework mode, check:

```env
CONVERSATION_ENGINE=framework
FRAMEWORK_ROOT=<path-to-ai-character-framework>
FRAMEWORK_PRESET=text_chat
FRAMEWORK_CHARACTER=default
FRAMEWORK_ADAPTER_MODE=local_import
```

Provider API keys are optional unless intentionally validating real FW/LLM generation.

Framework unavailable states should not break the normal text advice flow.

## Voice input / TTS / motion are unavailable

This is acceptable in mock-safe mode.

Expected behavior:

```txt
status explains unavailable/skipped/fallback
text advice remains usable
save/history remains usable
app does not crash
```

## Google Health says disabled, blocked, or unavailable

This is expected in mock-safe mode.

Real Google Health requests require explicit opt-in and configured local/demo credentials. Do not enable real API flags casually.

Safe default:

```env
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

## History or trend wording looks too strong

History, recent sleep trend, and weekly summary should be conservative.

Avoid wording that sounds like:

```txt
diagnosis
medical advice
guaranteed improvement
alarmist warning
today's confirmed sleep when based on history
```

Prefer wording that frames trends as lightweight historical reflection.

## Public repository hygiene issue

Before publishing, check that the repo does not contain:

```txt
.env
tokens
client secrets
Authorization headers
raw provider payloads
local_data/
cache directories
build outputs
machine-specific absolute paths
```

If a file is useful only as old development history, classify it through the Day2 inventory policy before deleting or archiving it.
