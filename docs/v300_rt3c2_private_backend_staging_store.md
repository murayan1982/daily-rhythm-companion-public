# DRC v3.0.0 RT-3c2 private Backend voice-input staging store

Updated: 2026-07-27

```text
RT-3: CURRENT / BLOCKED_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
RT-3c: CURRENT / NOT_COMPLETED
RT-3c1: COMPLETED / ACCEPTED
RT-3c2: COMPLETED / ACCEPTED
RT-3c2 implementation: COMPLETED / ACCEPTED
RT-3c3: CURRENT / NOT_COMPLETED
RT-3c3 implementation: NOT_STARTED
RT-3c3 authorization: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
RT-3c4: BLOCKED_PENDING_RT3C3_ACCEPTANCE
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

Source anchors:

```text
DRC source commit: c61eeb2616a3ed5b3c411a3a6b55750ed9d786d2
DRC tracked-tree archive SHA-256: BFBA6724FAA02E5D060F90F49DEAE80C45156DBA83F7372FB9CC791E99D17191
```

## Purpose

RT-3c2 adds only the bounded DRC Backend store and configuration needed to own
future voice-input upload artifacts privately.

It does not add a FastAPI upload route, Flutter transfer code, Framework import,
VoiceInputSession creation, provider execution, transcription, or STT evidence.

## Added configuration

Safe defaults:

```text
VOICE_INPUT_STAGING_TTL_SECONDS=300
VOICE_INPUT_STAGING_MAX_COUNT=8
VOICE_INPUT_STAGING_MAX_BYTES=1048576
```

All three values use the existing positive-integer configuration loader. Empty,
zero, negative, or invalid values fall back to the safe defaults.

The default managed location is:

```text
backend/local_data/voice_input/staging
```

`backend/local_data/` is already excluded from Git. No private server path is
placed in a response model, public metadata object, documentation example, log,
or committed evidence.

## Added private store

`VoiceInputStagingStore` provides:

```text
stage_chunks(...)
consume(staging_id, scoped_consumer)
discard(staging_id)
has_artifact(staging_id)
artifact_count()
cleanup()
```

The store accepts a chunk iterable so RT-3c3 can later connect a bounded streamed
request body without multipart. RT-3c2 tests use generated silent WAV bytes only;
no microphone artifact or provider payload is used.

### Staging boundary

```text
accepted format: WAV
accepted media types: audio/wav, application/octet-stream
maximum artifact size: configured, default 1048576 bytes
minimum structural check: RIFF/WAVE signature
staging ID: server-generated 32-character lowercase hexadecimal value
public metadata: staging ID, format, media type, byte count
private path: never returned
```

Partial files are removed after an empty body, invalid chunk, unsupported media,
oversize rejection, malformed WAV header, filesystem exception, or failed final
promotion.

### Bounded lifecycle

```text
expiry: lazy TTL cleanup
capacity: oldest managed artifact removed while the new artifact is protected
consume: single-use scoped private-path callback, then deletion
consumer exception: deletion still attempted
explicit discard: supported by opaque ID
malformed/traversal ID: rejected before path resolution
symlink: never consumed or deleted
unmanaged file: ignored
```

The store holds the process-local staging lock while the scoped consumer runs.
This prevents another local cleanup/consume call from claiming the same artifact.
The later RT-3c4 adapter remains responsible for ensuring that its return value is
path-free.

## Added tests

Focused Backend coverage verifies:

- safe configuration defaults, overrides, and invalid-value fallback;
- opaque/path-free staging metadata;
- chunked WAV staging;
- byte-limit and partial-file cleanup;
- supported media normalization;
- invalid format, media, chunk, and WAV-header rejection;
- TTL cleanup;
- capacity cleanup;
- single-use consume;
- cleanup after consumer exception;
- explicit discard;
- traversal/malformed-ID rejection;
- symlink and unmanaged-file preservation.

Expected focused count:

```text
14 passed
```

Expected full Backend count after RT-3c2:

```text
127 passed
```

The existing Flutter tree is unchanged, so the expected full Flutter regression
count remains 192.

## Explicit non-actions

RT-3c2 does not:

No FastAPI upload route is added in RT-3c2.

- modify `backend/app/main.py`;
- modify the metadata-only `backend/app/api/voice_input_demo.py` route;
- add any new FastAPI route;
- add `python-multipart` or another dependency;
- modify Flutter source, tests, dependencies, or platform files;
- import AI Character Framework;
- create `VoiceInputAudioSource` or `VoiceInputSession`;
- read a real microphone artifact;
- upload audio;
- execute a fake or real Framework adapter;
- execute a provider or STT;
- change version, release, vendor, or operator-evidence files.

## Acceptance

RT-3c2 is COMPLETED / ACCEPTED after compileall, all four RT-3 gates, focused
Backend 14, full Backend 127 with one existing warning, clean Flutter analysis,
full Flutter 192, exact 18-file surface review, and `git diff --check` passed.
No real microphone artifact was read, no audio was uploaded, Framework was not
imported, and no provider or STT was executed.

## Next authorization

```text
authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
```

RT-3c3 is CURRENT / NOT_COMPLETED and NOT_STARTED. It may add only the guarded
bounded binary WAV upload route and Flutter scoped staging consumer. Framework
import, VoiceInputSession handoff, provider execution, and STT remain forbidden.

## Local validation

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts

.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c2_private_backend_staging_store.py

.\.venv\Scripts\python.exe -m pytest -q `
  backend\tests\test_temporary_lifecycle_config.py `
  backend\tests\test_voice_input_staging_store.py

.\.venv\Scripts\python.exe -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```
