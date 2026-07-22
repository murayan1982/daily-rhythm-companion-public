# Smartphone Web quickstart

This guide describes the v1.0 smartphone Web demo target.

Goal:

```txt
Open Daily Rhythm Companion from a smartphone browser
→ connect to the backend
→ complete the daily loop
→ save and review a DailyRecord
```

This is a local/demo workflow. It is not a production hosted service or store release.

## Important networking rule

`127.0.0.1 and localhost mean` "this device".

On a smartphone, `http://127.0.0.1:8000` points to the smartphone, not the development PC. For the phone to reach the backend, use one of these:

```txt
- the development PC's LAN IP address
- a trusted tunnel URL
- a deployed demo backend URL
```

For local testing on the same Wi-Fi network, the shape is usually:

```txt
Backend:     http://<PC_LAN_IP>:8000
Flutter Web: http://<PC_LAN_IP>:8080
Phone:       opens http://<PC_LAN_IP>:8080
```

## 1. Start the backend for LAN access

From `backend/` with the virtual environment active:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then test from the development PC:

```txt
http://127.0.0.1:8000/health
http://<PC_LAN_IP>:8000/health
```

Then test from the smartphone browser:

```txt
http://<PC_LAN_IP>:8000/health
```

Expected response:

```json
{"status":"ok"}
```

If the phone cannot open this URL, check firewall, Wi-Fi isolation, VPN, and whether the backend is bound to `0.0.0.0`.

## 2. Start Flutter Web for LAN access

From `app/`:

```powershell
flutter pub get
flutter run -d web-server --web-hostname 0.0.0.0 --web-port 8080
```

Open from the smartphone browser:

```txt
http://<PC_LAN_IP>:8080
```

## 3. Confirm the Flutter backend API base URL

The Flutter app must call a backend URL the phone can reach.

For smartphone Web demo, the effective backend base URL should be similar to:

```txt
http://<PC_LAN_IP>:8000
```

If the current app build still uses the development default:

```txt
http://127.0.0.1:8000
```

then the UI may load on the phone but backend calls will fail. Before marking the v1.0 smartphone Web demo complete, Day5 should add or verify a configuration path for the phone-accessible backend URL.

## 4. Complete the daily loop from the phone

Use the phone browser to verify:

```txt
1. Web UI opens.
2. Backend connection status is ok.
3. Sleep/context is visible.
4. Mood can be selected.
5. Character can be selected.
6. Advice can be generated.
7. Advice can be saved as a DailyRecord.
8. History can be opened.
9. Recent sleep trend / weekly summary are framed as historical context.
10. Capability status is visible.
11. Optional voice/TTS/motion unavailable states do not break the flow.
12. Google Health real API does not run without explicit opt-in.
```

## 5. Keep the demo safe

For v1.0, the smartphone Web demo should still default to:

```env
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=mock
```

Do not expose development credentials or token files through a tunnel or public URL.

If using a tunnel, treat it as temporary and private. Stop it after the demo.
