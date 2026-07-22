# Post-advice chat smartphone Web verification

This document defines the manual smartphone Web verification path for the mock-safe post-advice chat UI.

## Purpose

Day10 added the Flutter post-advice chat UI.

Day11 defines how to verify that flow from smartphone Web:

```text
smartphone browser
→ Flutter Web UI
→ actual DRC backend API
→ advice result
→ Post-advice Chat
→ mock-safe chat session
→ visible character response
```

## Recommended runtime path

Use the release build static hosting path for smartphone verification.

### Backend

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend URL shape:

```text
http://<PC_LAN_IP>:8000
```

### Flutter Web build

```powershell
cd app
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

### Static server

```powershell
python -m http.server 18080 --bind 0.0.0.0 --directory build\web
```

Smartphone URL shape:

```text
http://<PC_LAN_IP>:18080
```

Do not use private LAN IP values in public release notes.

## Required preflight UI evidence

Confirm on smartphone Web:

```text
- DRC Home screen is visible
- API base URL is visible
- API base URL points to http://<PC_LAN_IP>:8000
- Backend status: ok is visible
```

## Required advice UI evidence

Confirm:

```text
- character selection is visible
- mood selection is visible
- advice action is visible
- advice result is visible
- source/fallback explanation is visible
```

## Required post-advice chat UI evidence

After advice result is visible, confirm:

```text
- Post-advice Chat section is visible
- "少し話す" option is visible
- "今日はここまで" option is visible
```

Choose:

```text
少し話す
```

Then confirm:

```text
- Chat session is visible
- Chat source is visible
- message input is visible
- 送信 button is visible
```

Send a short safe message, such as:

```text
ありがとう、もう少しだけ話したい
```

Then confirm:

```text
- user message is visible
- character response is visible
- Chat source remains visible
- UI does not expose raw provider payloads or secrets
```

## Mock-safe success definition

Day11 verifies mock-safe smartphone Web chat UI behavior.

Day11 success means:

```text
- smartphone Web UI can create advice
- smartphone Web UI can start post-advice chat
- smartphone Web UI can send one message
- smartphone Web UI can show the mock-safe character response
```

Day11 does not mean:

```text
- configured real LLM chat succeeded
- AI Character Framework text chat succeeded
- STT voice chat succeeded
- TTS playback succeeded
- Live2D/VTS motion succeeded
```

## Manual evidence record

Safe evidence to record:

```text
- device/browser
- Web UI URL shape
- backend API base URL shape
- visible Backend status: ok
- selected character
- selected mood
- advice result visible
- Post-advice Chat visible
- Chat session visible
- Chat source visible
- user message visible
- character response visible
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

## Day11 conclusion

The post-advice chat flow should be verified as a smartphone Web UI flow before adding configured AI Character Framework text chat verification.

This keeps mock-safe UI behavior, backend route wiring, and configured real LLM/FW success clearly separated.
