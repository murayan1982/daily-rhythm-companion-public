# Post-advice chat smartphone Web manual evidence

This document defines the safe evidence record for the real smartphone Web post-advice chat manual run.

## Purpose

Day11 defined the required smartphone Web verification flow.

Day12 defines how to record the result safely.

This is a manual evidence template. It does not add runtime behavior.

## Recommended runtime path

### Backend

```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend URL shape:

```text
http://<PC_LAN_IP>:8000
```

### Flutter Web release build

```powershell
cd app
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

### Static hosting

```powershell
python -m http.server 18080 --bind 0.0.0.0 --directory build\web
```

Smartphone URL shape:

```text
http://<PC_LAN_IP>:18080
```

## Manual evidence checklist

Record the following as safe yes/no or short text values.

```text
Device/browser:
- smartphone browser used:
- PC localhost URL shape checked: http://localhost:18080
- PC LAN URL shape checked: http://<PC_LAN_IP>:18080
- smartphone URL shape checked: http://<PC_LAN_IP>:18080

Runtime:
- backend running on 0.0.0.0:8000:
- static web server running on 0.0.0.0:18080:
- release build used:
- DRC Home visible on smartphone:

Backend/UI:
- Backend status: ok visible:
- API base URL visible:
- API base URL shape: http://<PC_LAN_IP>:8000

Advice:
- character selection visible:
- mood selection visible:
- advice action used:
- advice result visible:
- source/fallback explanation visible:

Post-advice chat:
- Post-advice Chat visible:
- 少し話す visible:
- 今日はここまで visible:
- 少し話す selected:
- Chat session visible:
- message input visible:
- 送信 button visible:
- test user message sent:
- user message visible:
- character response visible:
- Chat source visible:
```

## Public-safe summary template

Use this summary format in public notes.

```text
Manual smartphone Web post-advice chat evidence:
- Runtime: release build static hosting
- Backend URL shape: http://<PC_LAN_IP>:8000
- Web URL shape: http://<PC_LAN_IP>:18080
- Smartphone browser opened DRC Home: yes
- Backend status shown in UI: ok
- API base URL shown in UI: http://<PC_LAN_IP>:8000
- Advice result visible: yes
- Post-advice Chat visible: yes
- 少し話す flow started: yes
- User message visible: yes
- Character response visible: yes
- Chat source visible: yes
- Result: mock-safe smartphone Web post-advice chat UI verified
```

## Success definition

Day12 success means:

```text
- smartphone Web UI can load the release-built DRC app
- smartphone Web UI can reach the actual backend API
- smartphone Web UI can show Backend status: ok
- smartphone Web UI can show the configured API base URL
- smartphone Web UI can create advice
- smartphone Web UI can start the post-advice chat flow
- smartphone Web UI can send a message
- smartphone Web UI can show user and character messages
- smartphone Web UI can show Chat source
```

Day12 success does not mean:

```text
- configured real LLM chat succeeded
- AI Character Framework text chat succeeded
- STT voice chat succeeded
- TTS playback succeeded
- Live2D/VTS motion succeeded
- Google Health real API access succeeded
```

## Non-exposure rules

Do not record in public docs, release notes, shared logs, screenshots, or issue comments:

```text
- real API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- private credential paths
- raw provider payloads
- full provider debug traces
- private absolute paths
- private LAN IP values
```

Screenshots are useful, but before sharing publicly, verify that they do not expose private LAN IP values, tokens, file paths, or provider data.

## Day12 conclusion

Day12 records the actual smartphone Web post-advice chat UI path as mock-safe evidence.

Configured AI Character Framework text chat verification remains a later explicit opt-in step.
