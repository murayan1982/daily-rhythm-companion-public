# Smartphone Web API base URL configuration

Day6 adds the first runtime-facing implementation step for v1.9.0 smartphone Web demonstration.

## Problem

`BackendApiClient` previously defaulted directly to:

```text
http://127.0.0.1:8000
```

That works for desktop-local Chrome smoke tests.

It does not work by itself for smartphone Web demonstration because a phone's `127.0.0.1` points to the phone, not the developer PC.

## Configuration

Flutter Web can now receive the backend API base URL through a compile-time dart define:

```text
DRC_BACKEND_API_BASE_URL
```

Default:

```text
http://127.0.0.1:8000
```

Smartphone-Web-oriented value:

```text
http://<PC_LAN_IP>:8000
```

## Example commands

Desktop-local Chrome smoke:

```powershell
cd app
flutter run -d chrome
```

Smartphone-Web-oriented run:

```powershell
cd app
flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

The phone should access the Flutter Web URL exposed by the development machine, while the Flutter app calls:

```text
http://<PC_LAN_IP>:8000
```

for backend API requests.

## UI evidence

The Home screen displays:

```text
API base URL: <configured backend API URL>
```

This is part of the Day5 evidence rule: API-only success is not enough, and the Web UI must show relevant runtime state.

## Safe default

The default remains:

```text
http://127.0.0.1:8000
```

This preserves existing desktop-local and mock-safe development behavior.

## Non-secret rule

The API base URL may include a LAN host/IP and port, but it must not include:

```text
- API keys
- OAuth secrets
- tokens
- authorization headers
- private credential file paths
- raw provider payloads
```

## Day6 conclusion

Day6 does not prove real provider execution.

It removes a key blocker for smartphone Web demonstration by making the backend API base URL configurable and visible in the UI.
