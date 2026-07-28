# DRC v3.0.0 RT-3b app-owned host-audio handoff lifecycle

Updated: 2026-07-27

```text
RT-3: CURRENT / BLOCKED_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
RT-3a: COMPLETED / ACCEPTED
RT-3b: COMPLETED / ACCEPTED
RT-3b implementation: COMPLETED / ACCEPTED
RT-3c: COMPLETED / ACCEPTED
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

Accepted authorization:

```text
completed-accepted-app-owned-host-audio-lifecycle-contract-fake-only
```

## Purpose

RT-3b adds the DRC-owned lifecycle between a completed mobile microphone capture
and a future private Backend staging consumer. It does not add that staging
consumer yet.

```text
completed MicrophoneCaptureResult
-> validate opaque artifact and public audio format
-> retain one app-owned private-artifact lease
-> invoke an injected consumer
-> discard on completion, failure, cancel, or close
-> return a path-free provider-neutral public result
```

## Added Flutter contract

```text
HostAudioHandoffDescriptor
HostAudioHandoffConsumerResult
HostAudioHandoffResult
HostAudioHandoffState
HostAudioHandoffException
HostAudioPrivateArtifactLease
HostAudioHandoffConsumer
FakeHostAudioHandoffConsumer
HostAudioHandoffController
```

The controller accepts only a completed capture with:

```text
non-empty opaque capture id
positive duration
maximum duration at or below 15 seconds
encoding
sample rate
channel count
registered private artifact resolvable by the app-owned access boundary
```

## Private artifact boundary

The controller stores the opaque capture identity only inside the lease. The
private path has no getter and is never copied into a public result, public
metadata, UI state, log, or API payload.

A future app-owned staging consumer may use the scoped callback:

```text
HostAudioPrivateArtifactLease.withPrivateArtifactPath(...)
```

The callback is available only while `HostAudioHandoffConsumer.consume()` is
active. RT-3b production and focused fake tests do not read audio, create a
network request, import Framework code, execute a provider, or perform STT.

## Cleanup contract

```text
consume success  -> discard private artifact
consume failure  -> discard private artifact
consumer throw   -> normalize error, discard private artifact
cancel           -> cancel fake consumer, discard private artifact
explicit discard -> discard private artifact
close            -> cancel, discard, dispose consumer
cleanup failure  -> retain lease for explicit discard retry
```

Only one retained artifact is allowed at a time.

## Public-safe output

Public results include typed phase/outcome, a safe technical code, audio-format
metadata, duration, and cleanup booleans. They do not include:

```text
private path
opaque capture id
raw audio
byte buffer
platform handle
provider payload
transcript
credential
```

Public metadata uses an allowlist. Unknown keys such as `private_path`,
`opaque_capture_id`, and credential-like values are dropped.

## Non-actions

RT-3b does not:

- change the existing RT-2 operator capture/discard path;
- change Backend runtime, FastAPI routes, or Backend tests;
- upload or stage audio;
- import the vendored Framework;
- construct `VoiceInputAudioSource` or `VoiceInputSession`;
- execute a provider or STT;
- access a real microphone;
- read the private audio file;
- change dependencies or platform files;
- change release/version metadata.

## Local validation target

```text
python -m compileall -q backend scripts
python scripts/check_v300_host_audio_handoff_lifecycle.py
python -m pytest -q backend/tests
cd app
flutter analyze
flutter test test/microphone_capture_host_audio_handoff_test.dart
flutter test
cd ..
git diff --check
```

Expected focused Flutter count: 21.
Expected full Flutter count after RT-3b: 192.

## Acceptance evidence

```text
source gate: passed
Backend: 116 passed with one existing warning
flutter analyze: No issues found
focused Flutter: 21 passed
full Flutter: 192 passed
exact changed surface: ten files
git diff --check: passed
cleanup-retry test order: corrected and revalidated
```

No Backend route, network upload, audio read, FW import, provider execution, STT,
dependency, platform, vendor, private environment, version, or release surface
changed.

RT-3c is COMPLETED / ACCEPTED. Its implementation authorization was
`authorized-private-backend-staging-and-fake-fw-public-session-handoff-only`.
Real RT-3 acceptance remains blocked because FW v5.3.0 has no concrete real STT
provider execution.


## RT-3c1 consumer boundary decision

The accepted `HostAudioPrivateArtifactLease.withPrivateArtifactPath(...)`
callback is the only Flutter-side place where RT-3c3 may read and stream the
private WAV file. The lease must stay active until the Backend response is
received. The existing controller then discards the original mobile artifact
after consumer completion or failure.

RT-3c1 and RT-3c2 are COMPLETED / ACCEPTED. RT-3c3 is COMPLETED / ACCEPTED; it adds only the guarded binary upload route and Flutter scoped staging consumer authorized by RT-3c2.

RT-3c1 does not add that consumer. It only fixes these future rules:

- the consumer streams once to the configured Backend;
- it never places the path in a URL, JSON body, result, log, or evidence;
- it sends only safe audio metadata and bounded bytes;
- it treats a Backend staging ID as opaque;
- RT-3c3 does not import FW or execute STT;
- cleanup failure remains explicit and retryable through the accepted RT-3b
  controller.


## RT-3c2 downstream staging update

The consumer boundary prepared by RT-3b now connects the Flutter lease to the accepted Backend-owned private staging store through a guarded bounded request. `BackendVoiceInputStagingConsumer` opens the file only inside `withPrivateArtifactPath(...)`; after success or failure, `HostAudioHandoffController` still performs the local discard. The consumer exposes only safe booleans in the public handoff result and retains the opaque, path-free Backend staging handle separately for RT-3c4. RT-3c3 did not import Framework, create a VoiceInputSession, execute a provider, or execute STT, and is COMPLETED / ACCEPTED after the full local validation set. RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED after compileall, six RT-3 gates, focused Backend 8, full Backend 145 with one existing warning, clean Flutter analysis, full Flutter 200, exact 22-file surface review, `git diff --check`, and explicit operator approval.

## RT-3c4 downstream fake-session update

The accepted Flutter lifecycle remains unchanged. RT-3c4 operates only after the mobile artifact has been uploaded and represented by a path-free Backend staging handle. The Backend resolves the private server path solely inside `VoiceInputStagingStore.consume(...)`, passes it into FW's data-only public file-source contract, closes the fake session, and removes the staged artifact. No private path returns to Flutter or enters the public handoff result. RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED; real STT remains blocked.
