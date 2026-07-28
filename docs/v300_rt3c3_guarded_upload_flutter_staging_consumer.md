# DRC v3.0.0 RT-3c3 guarded upload and Flutter scoped staging consumer

```text
Source commit: 6f97014715c8e198ae639420f7cf9334d9a61029
Source archive SHA-256: 93DC227CEACF640709695F758A0E73DEBDF63749FE4418F071CDBEC69E07AD42
RT-3c3: COMPLETED / ACCEPTED
RT-3c3 implementation: COMPLETED / ACCEPTED
Authorization at implementation: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
RT-3c4: COMPLETED / ACCEPTED
RT-3c4 implementation: COMPLETED / ACCEPTED
RT-3c4 authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

## Purpose

RT-3c3 connects the accepted app-owned mobile artifact lease to the accepted DRC Backend private staging store. The connection is intentionally limited to DRC-owned transport and staging. It does not cross the Framework public-session boundary yet.

## Backend upload boundary

`POST /demo/voice-input/staging` accepts a direct streamed request body. Multipart is not used and `python-multipart` is not added. The route is available only when all of these explicit guards pass:

```text
VOICE_INPUT_DEMO_ENABLED=true
CONVERSATION_ENGINE=framework
VOICE_INPUT_ADAPTER_MODE=framework
```

Required request contract:

```text
Content-Type: audio/wav
X-DRC-Audio-Format: wav
X-DRC-Sample-Rate-Hz: 16000
X-DRC-Channel-Count: 1
X-DRC-Duration-Ms: 1..15000
maximum body: 1048576 bytes
```

`Request.stream()` is passed to `VoiceInputStagingStore.stage_async_chunks(...)`. The store writes incrementally to a private unique `.part` file, validates the size and RIFF/WAVE header, atomically finalizes the artifact, and removes partial/final files after rejection or exception. The public response contains only safe metadata and a server-generated 32-character opaque staging ID. It contains no filesystem path or raw bytes.

## Flutter scoped staging consumer

`BackendVoiceInputStagingConsumer` implements `HostAudioHandoffConsumer`. It receives no path getter. It can access the file only through:

```text
HostAudioPrivateArtifactLease.withPrivateArtifactPath(...)
```

Inside that callback it rejects non-files, symlinks, empty files, and files over the client-side byte bound. It sends the file through `http.StreamedRequest` and `File.openRead()`; it does not call `readAsBytes()`, put the path or capture ID in the URL/headers/body, or expose the path in a public result/error.

After a successful 201 response, the consumer retains one `BackendVoiceInputStagedArtifact`. This handle contains only the opaque Backend staging ID and safe audio metadata. `takeStagedArtifact()` transfers that handle once to the future RT-3c4 layer. A second upload is rejected while a handle remains pending.

Local mobile cleanup remains controlled by `HostAudioHandoffController`: after consumer success or failure it discards the original mobile artifact using the accepted RT-3b lifecycle. The public handoff result contains safe booleans only; it does not contain the staging ID, capture ID, path, or raw bytes.

## Error and cancellation boundary

Backend validation/store failures are converted to path-free problem codes. Flutter normalizes Backend problem codes without exposing Backend detail messages. Network and malformed-response failures use safe technical codes and retryability flags. `cancel()` closes an active transport, and `dispose()` is idempotent.

RT-3c3 does not delete or consume the Backend staged artifact because the next fake Framework handoff has not occurred. That single-use server-side consume/discard lifecycle is reserved for RT-3c4.

## Verification surface

Backend synthetic tests cover:

- successful generated-WAV staging and path-free response metadata;
- feature, engine, and adapter guards;
- media type and required metadata;
- sample rate, channel count, and duration limits;
- declared/streamed body limit;
- invalid WAV rejection and partial cleanup.

Flutter synthetic tests cover:

- scoped WAV streaming and safe headers;
- local artifact cleanup after success/failure;
- local size rejection before sending;
- safe Backend problem normalization;
- malformed response rejection;
- single pending staging handle;
- idempotent disposal.

Expected local validation after patch application:

```text
compileall: pass
RT-3 gates: pass
focused Backend: 21 passed
full Backend: 137 passed
flutter analyze: no issues
focused Flutter handoff + staging consumer: 29 passed
full Flutter: 200 passed
git diff --check: pass
exact changed surface: 22 files
```

The Backend counts were verified against the exact source archive with generated WAV bytes. Flutter execution remains a local operator validation requirement.

## Explicit non-evidence

```text
real microphone artifact read by this verification: no
real operator audio uploaded: no
running Backend contacted by Flutter verification: no
Framework imported: no
VoiceInputSession created: no
provider client created: no
provider execution: no
transcription/STT execution: no
private path committed or exposed: no
raw audio committed: no
```

## Acceptance boundary

RT-3c3 is `COMPLETED / ACCEPTED`. Acceptance passed with compileall, five RT-3 gates, focused Backend 21, full Backend 137 with one existing warning, clean Flutter analysis, focused Flutter 29, full Flutter 200, exact 22-file surface review, `git diff --check`, and explicit operator approval. No real microphone artifact was read or uploaded; Framework was not imported, no `VoiceInputSession` was created, and no provider or STT execution occurred. RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED under authorization `authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only`. Real RT-3 acceptance remains blocked because FW v5.3.0 has no concrete real STT provider execution.

## RT-3c4 implementation update

RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED after compileall, six RT-3 gates, focused Backend 8, full Backend 145 with one existing warning, clean Flutter analysis, full Flutter 200, exact 22-file surface review, `git diff --check`, and explicit operator approval. The path-free handle produced by RT-3c3 can now be submitted to the guarded Backend fake-handoff endpoint. The Backend consumes the private staged artifact once, constructs FW v5.3.0 public file-source/request/session objects, injects `FakeVoiceInputProviderAdapter`, closes the session, and returns a path-free fake transcript result. The Flutter RT-3c3 implementation is unchanged. Real microphone operator upload, provider execution, and real STT remain absent.
