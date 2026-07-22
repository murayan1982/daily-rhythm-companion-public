# Local quickstart

This guide starts Daily Rhythm Companion in mock-safe local mode.

Mock-safe mode is the default development mode. It does not require Google Health credentials, provider API keys, microphone access, TTS provider credentials, VTube Studio, or Live2D runtime dependencies.

## Prerequisites

- Python 3.11 or later recommended
- Flutter stable SDK
- PowerShell on Windows, or equivalent shell commands on another OS

## 1. Create the backend environment

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Configure mock-safe mode

Use `.env.example` as the starting point.

```powershell
Copy-Item .env.example .env -Force
```

Confirm the important defaults:

```env
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=mock
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

Do not commit `.env`.

## 3. Start the backend

From `backend/` with the virtual environment active:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```txt
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

Expected health response:

```json
{"status":"ok"}
```

## 4. Run backend smoke checks

From the repository root with the backend virtual environment active:

```powershell
python -m compileall -q backend\app
```

Older release checks may also be run as long as they remain part of the active release workflow.

## 5. Run the Flutter app

In another terminal:

```powershell
cd app
flutter pub get
flutter test
flutter run
```

## 6. Try the local daily loop

In the app:

```txt
confirm backend connection
→ review sleep/context
→ select mood
→ select character
→ generate advice
→ save DailyRecord
→ open History
→ check recent trend / weekly summary wording
→ inspect capability status
```

## Mock-safe expectations

In mock-safe mode:

- `/health` returns ok.
- `/sleep/summary` returns mock or safe fallback sleep data.
- `/advice` works without external LLM providers.
- `/demo/status` reports capability state without making real provider requests.
- Google Health real API requests do not run.
- Optional voice/TTS/motion absence does not break the text flow.

## Next steps

- Use `quickstart_smartphone_web.md` to try the app from a smartphone browser.
- Use `framework_demo_setup.md` to intentionally enable AI Character Framework mode.
- Use `google_health_real_api_opt_in.md` only for guarded local/demo real API verification.
