# v2.0.x application version metadata

Updated: 2026-07-22
Current patch source version: v2.0.1
Current small commit: M-2
Status: CURRENT / NOT_COMPLETED

## Purpose

M-2 aligns the active post-v2.0.0 source metadata without changing or replacing the published `DRC_v2.0.0` tag, ZIP, release notes, or source snapshot.

## Source owners

```text
Backend/API semantic version: backend/app/version.py -> APP_VERSION
Flutter package version/build: app/pubspec.yaml -> version
```

The two source owners have different build-system responsibilities but must share the same semantic version. M-2 sets them to:

```text
Backend/API: 2.0.1
Flutter package: 2.0.1+2
```

No additional production constant is introduced in Dart, HTML, Web manifest, Android, iOS, macOS, Windows, or Linux source.

## Runtime and platform surfaces

### Backend

```text
backend/app/version.py
  -> authoritative backend APP_VERSION
backend/app/main.py
  -> FastAPI/OpenAPI version
backend/app/api/health.py
  -> /health version field
```

The `/health` response is additive and remains compatible with clients that only read `status`:

```json
{"status":"ok","version":"2.0.1"}
```

### Flutter and Web

```text
app/pubspec.yaml
  -> Flutter build name 2.0.1
  -> Flutter build number 2
```

Android, iOS, macOS, Windows, and Linux use Flutter-generated build metadata derived from `pubspec.yaml`. The Web source files keep product identity only; M-2 intentionally does not hard-code a second version into `app/web/index.html` or `app/web/manifest.json`. Generated Flutter Web build metadata remains derived from the Flutter package version.

### User-visible status

`BackendApiClient` formats the version returned by `/health` as:

```text
ok / API v2.0.1
```

The existing Backend status area displays that value. If an older backend returns no `version`, the Flutter client continues to display the legacy status string, such as `ok`.

## Version boundary

```text
- v2.0.1 identifies the current maintenance source; it is not released during M-2.
- M-2 does not create a tag, fixed ZIP, or GitHub Release.
- Patch release handling remains M-9 work after the maintenance scope is accepted.
- Historical v2.0.0 validators may intentionally pin 2.0.0 metadata and are not the active current-main version check.
```

## Verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py

cd app
flutter test
cd ..
```

The source-tree checks are credential-free. They do not call providers, OAuth endpoints, Google Health, Fitbit, AI Character Framework, TTS, STT, or motion runtimes.
