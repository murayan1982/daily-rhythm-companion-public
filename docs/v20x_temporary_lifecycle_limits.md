# v2.0.x temporary chat and TTS artifact lifecycle limits

Updated: 2026-07-22  
Small commit: M-5  
Status: COMPLETED / ACCEPTED

## Purpose

M-5 bounds two process-local resources that were intentionally left unbounded in the v2.0.0 release baseline:

```text
- optional post-advice chat sessions
- DRC-owned voice-output staging/public artifacts
```

The cleanup path is lazy and request-driven. M-5 does not add a scheduler, background worker, public cleanup endpoint, persistent chat database, or cloud artifact store.

## Configuration

```text
POST_ADVICE_CHAT_TTL_SECONDS=1800
POST_ADVICE_CHAT_MAX_SESSIONS=100
VOICE_OUTPUT_ARTIFACT_TTL_SECONDS=86400
VOICE_OUTPUT_ARTIFACT_MAX_COUNT=100
```

All values are positive integers. Missing, empty, zero, negative, or malformed values use the bounded defaults.

## Post-advice chat lifecycle

```text
- Sessions remain process-local.
- Idle TTL is measured from the last successful create, get, or message operation.
- create/get/message operations remove expired sessions before lookup or insertion.
- cleanup() provides an explicit in-process cleanup pass for tests and future callers.
- Capacity eviction uses least-recently-used order.
- A successful GET refreshes recency; it is an active session read.
- Expired and evicted sessions preserve the existing 404 Chat session not found API response.
- Existing ChatSessionResponse and ChatMessageResponse models are unchanged.
```

The service accepts an injected clock in tests, so expiry and eviction do not depend on `sleep()` or wall-clock timing.

## Voice artifact lifecycle

```text
- Framework output is still accepted only from the managed staging directory.
- Public MP3 TTL starts when DRC moves the file into the public directory.
- Publication time is recorded in filesystem mtime so separate store instances share the same retention state.
- Resolving or downloading an artifact does not refresh its TTL.
- Lazy cleanup runs when the staging directory is requested, an artifact is published, an artifact is resolved, or cleanup() is called.
- Both staging leftovers and public files are count-bounded.
- A publish cleanup protects the newly published file and removes older files first.
- Cleanup scans direct regular files only; it does not recurse or follow/delete symlinks.
- Expired and evicted public artifacts preserve the existing 404 audio-artifact response.
- The opaque `/demo/voice-output/audio/<artifact-id>` URL remains unchanged.
```

`VoiceOutputDemoService` passes the active `AppConfig`. The audio resolver keeps the historical no-argument `VoiceOutputArtifactStore()` construction for fake-store compatibility; the store loads the same active configuration internally.

## Mock-safe regression boundary

The normal backend tests use temporary directories, fake bytes, and injected clocks. They do not:

```text
- call a real Framework checkout
- call an LLM or TTS provider
- generate real audio
- access OAuth or health-provider credentials
- use backend/local_data
- start a browser
- create a release ZIP, tag, GitHub Release, or v2.0.1 release
```

Focused coverage includes:

```text
- safe configuration defaults, overrides, and invalid-value fallback
- chat idle-TTL refresh and expiry
- chat LRU capacity eviction
- explicit chat cleanup and unchanged API 404 behavior
- public artifact publish-time expiry
- public artifact oldest-first capacity eviction
- staging leftover TTL/count cleanup
- retained outside-path, format, traversal, malformed-ID, and opaque-URL safety tests
```

## Verification

From the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py
python scripts\check_v20x_backend_mock_safe_regression.py
python scripts\check_v20x_framework_fallback_voice_artifact_regression.py
python scripts\check_v20x_temporary_lifecycle_limits.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

M-5 was accepted on 2026-07-22 after the complete check set, 26 backend pytest tests, 39 Flutter tests, diff review, and operator approval passed. The published `DRC_v2.0.0` records remain immutable.
