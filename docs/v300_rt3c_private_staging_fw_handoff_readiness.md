# DRC v3.0.0 RT-3c1 private Backend staging and fake FW handoff readiness

Status:

```text
RT-3c1: COMPLETED / ACCEPTED
RT-3c1 implementation: COMPLETED / ACCEPTED
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
DRC source commit: cf734aa04990aa55ccfcd56b65052fbe206f74fb
DRC source archive SHA-256: AE42AE996DA0A2E42F132C1AD3A0EF69329E00A709BB10891F6306D459ABFE35
Framework release: v5.3.0
Framework surface archive SHA-256: 60AF94A8C3623C0F8D5421B5CA2A6E798E04CD39A1EEA3E9B3A8A29E54BD0096
```

## Purpose

RT-3c1 fixes the exact staging, transport, ownership, and fake Framework
handoff design before any audio is read or transferred.

This checkpoint is docs/test-only.

## Exact current DRC findings

### Flutter

The accepted RT-3b contract provides:

- one retained opaque capture artifact;
- WAV / 16 kHz / mono / maximum 15-second validation;
- scoped private-path access only during consumer execution;
- cleanup after consume, failure, cancel, discard, or close;
- path-free and opaque-ID-free public results.

The Flutter app already depends on `http`, but it has no host-audio upload
consumer and no voice-input staging model/API method.

### Backend

The existing `/demo/voice-input` endpoint is metadata-only. It intentionally
does not process audio.

The current Backend has no:

- voice-input staging store;
- audio upload route;
- body-size limit for voice-input audio;
- staging TTL or capacity configuration;
- staging ID model;
- FW public voice-input session adapter;
- single-use staged artifact consume operation.

`VoiceOutputArtifactStore` demonstrates bounded TTL/capacity and safe path
validation, but its public-serving/move-to-public behavior must not be reused
for private voice-input staging.

The current requirements do not include `python-multipart`.

### Framework v5.3.0

The public facade exports:

```text
VoiceInputAudioFormat
VoiceInputAudioSource
VoiceInputRequest
VoiceInputResult
VoiceInputSession
create_voice_input_session
FakeVoiceInputProviderAdapter
```

The public session can run a fake adapter with a file-path source and return a
typed result. The fake adapter does not read audio.

The guarded real adapter remains unavailable with
`real_stt_not_implemented`. Real provider execution is absent.

## Selected later transport

RT-3c uses a bounded streamed request body rather than multipart.

```text
content type: audio/wav (application/octet-stream may be accepted by tests)
maximum request body: 1048576 bytes
audio encoding: WAV
sample rate: 16000 Hz
channels: 1
maximum duration: 15000 ms
```

Safe metadata may be provided in validated headers or query fields. A phone
private path must never be sent as metadata.

`python-multipart` is not required by this design.

## Selected Backend staging lifecycle

```text
private root: backend/local_data/voice_input/staging
server ID: generated opaque hexadecimal ID
TTL: 300 seconds
maximum count: 8
ownership: DRC Backend
visibility: no public file-serving route
consume: single-use
cleanup: success, rejection, exception, expiry, capacity, explicit discard
```

Public responses may contain the generated staging ID and safe status/format
metadata. They must never contain the private server path, phone path, raw
bytes, provider payload, credential, or vendor root.

## RT-3c small-commit split

### RT-3c1

Exact readiness inventory only.

No runtime change.

### RT-3c2

Add the bounded private Backend staging store and configuration only.

RT-3c2 must not add:

- a FastAPI upload route;
- Flutter network code;
- Framework imports;
- audio transcription;
- provider execution.

### RT-3c3

Add a guarded streamed upload route and a Flutter
`HostAudioHandoffConsumer` that streams the scoped private WAV file.

RT-3c3 may transfer audio only to the configured DRC Backend. It must not import
FW or execute STT.

### RT-3c4

Add the Backend adapter that creates FW public host-audio/session objects and
uses `FakeVoiceInputProviderAdapter`.

The staged artifact is single-use and cleaned after the fake typed result. The
fake adapter must remain provider-free and audio-read-free.

### RT-3d

Real provider execution and physical-device transcript evidence.

Blocked until FW ships accepted real provider execution.

## Non-actions

RT-3c1 does not:

- modify Backend or Flutter runtime;
- modify existing tests;
- add a route or dependency;
- read or upload audio;
- create staging files;
- import FW;
- create a FW session;
- execute a fake or real adapter;
- execute provider code or STT;
- open a microphone;
- load private env values;
- print the vendor root;
- change platform, version, release, or vendor files.

## Acceptance

RT-3c1 is COMPLETED / ACCEPTED after compileall, the source-only gate, Backend
116 with one existing warning, clean Flutter analysis, full Flutter 192, exact
nine-file review, and `git diff --check` passed.

RT-3c2 is COMPLETED / ACCEPTED after compileall, four RT-3 gates, focused
Backend 14, full Backend 127 with one existing warning, clean Flutter analysis,
full Flutter 192, exact 18-file surface review, and `git diff --check` passed.
RT-3c3 is CURRENT / NOT_COMPLETED and NOT_STARTED. Its authorization is limited
to the guarded bounded binary upload route and Flutter scoped staging consumer.
It must not import Framework, create a VoiceInputSession, execute a provider, or
execute STT.

## Local validation

```powershell
$env:FRAMEWORK_ROOT = (Resolve-Path `
  ".\vendor\ai-character-framework-5.3.0").Path

.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt3c_private_staging_fw_handoff_readiness.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

Expected existing regression counts:

```text
Backend: 127 passed with one existing warning
Flutter: 192 passed
```


## RT-3c2 implementation update

The selected private staging design is implemented and accepted. The Backend adds
only configuration, the bounded private store, and mock-safe tests. The existing
metadata-only route and all Flutter/FW/provider/STT surfaces remain unchanged.

```text
RT-3c2 implementation: COMPLETED / ACCEPTED
RT-3c3: CURRENT / NOT_COMPLETED
RT-3c3 implementation: NOT_STARTED
RT-3c3 authorization: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
```
