# DRC v3.0.0 RT-2e-b record microphone capture adapter

Date: 2026-07-27

Parent small commit: RT-2e CURRENT / NOT_COMPLETED
Current small commit: RT-2e-b COMPLETED / ACCEPTED
Previous small commit: RT-2e-a COMPLETED / ACCEPTED
Next small commit: RT-2e-c CURRENT / NOT_COMPLETED; NOT_STARTED

## Purpose

RT-2e-b adds the real-capable package adapter required by the accepted RT-2d
capture lifecycle while keeping all execution credential-free and fake-only.
The adapter compiles against pinned `record` 6.2.1 and `path_provider` 2.1.6,
but it is not connected to startup, HomeScreen, widgets, routes, Backend,
Framework, provider, or STT code.

Official `record` 6.2.1 contract used by this adapter:

```text
AudioRecorder.start(RecordConfig, path: privatePath)
AudioRecorder.stop() -> private path or null
AudioRecorder.cancel() -> stop and discard/delete
AudioRecorder.dispose()
```

The package permission helper and byte-stream API are intentionally unused:

```text
AudioRecorder.hasPermission(): forbidden in DRC adapter
AudioRecorder.startStream(): forbidden in RT-2e
```

Permission ownership remains in `MicrophonePermissionGateway`, and raw byte
streaming remains blocked because it would cross the existing opaque-artifact
boundary.

## Added runtime boundary

```text
RecordMicrophoneCaptureDriverRequest
RecordMicrophoneCaptureDriver
RecordPackageMicrophoneCaptureDriver
RecordMicrophoneCapturePrivateFileSystem
PathProviderRecordMicrophoneCapturePrivateFileSystem
RecordMicrophoneCapturePrivateArtifactAccess
RecordMicrophoneCaptureEngine
```

`RecordMicrophoneCaptureEngine.mobile()` is a construction boundary only. No
current app code invokes it.

## Recording format

```text
container/encoding: WAV
sample rate: 16,000 Hz
channels: mono
maximum duration: existing controller hard limit, 60 seconds
output location: app-private temporary directory
public completion value: opaque capture id
```

The private path is held only inside the adapter and can be resolved through an
app-internal private-artifact interface for a future upload/STT consumer. It is
never copied into `MicrophoneCaptureEngineResult`, controller public metadata,
UI state, logs, or HTTP payloads.

## Cleanup contract

```text
start failure: best-effort driver cancel + private path deletion
cancel: driver cancel + private path deletion
stop null path: private path deletion + typed failure
stop unexpected path: reject + delete only the owned expected path
opaque id failure: private path deletion + typed failure
discard: delete registered private artifact exactly once
dispose: cancel active capture, delete unconsumed artifacts, dispose driver
```

Raw package/native errors are converted to typed
`MicrophoneCaptureEngineException` codes and are not exposed to public results.

## Controller metadata correction

RT-2d defaulted all top-level capture metadata to `false`. RT-2e-b keeps those
safe defaults for all non-completion paths, but on successful stop it copies
only these allowlisted booleans from the engine result:

```text
microphone_accessed
audio_captured
raw_audio_exposed
private_artifact_registered
```

Unknown engine metadata and private paths are not propagated.

## Test boundary

The focused tests instantiate only:

```text
_FakeRecordDriver
_FakePrivateFileSystem
injected clock
injected opaque-id generator
```

They do not instantiate `RecordPackageMicrophoneCaptureDriver`, call
`RecordMicrophoneCaptureEngine.mobile()`, request permission, open a microphone,
create audio, invoke platform channels, upload a file, or execute STT.

## Explicit non-goals

RT-2e-b does not add:

```text
UI/startup capture wiring
permission request execution
real-device microphone access
real audio capture evidence
raw audio byte streaming
public/private path logging
Backend upload endpoint
Framework voice-input execution
provider/STT execution
release acceptance
```

## Acceptance boundary

RT-2e-b acceptance verified:

```text
flutter pub get
resolved pinned lockfile
generated plugin diff review
compileall
RT-2e-b gate
Backend tests
flutter analyze
focused adapter tests
focused lifecycle tests
full Flutter tests
Android debug APK build (compile only; no app launch or capture)
git diff --check
changed-file review
explicit approval
```

All listed checks passed on 2026-07-27. The final focused adapter count is 18,
the focused lifecycle count is 18, and the full Flutter count is 161 after
three analyzer warnings were converted into explicit failure-path tests. Backend
116 passed with one existing warning. Android debug APK compilation succeeded;
the Kotlin incremental-cache daemon reported a cross-drive cache error before
Gradle fallback produced the APK. No app launch, permission request, microphone
access, or audio capture occurred. RT-2e-c is CURRENT / NOT_COMPLETED and
NOT_STARTED and requires separate explicit operator action.

## Expected gate

```text
v300_record_microphone_capture_adapter_status: completed-accepted
v300_rt2eb_record_dependency_resolved: True
v300_rt2eb_path_provider_direct_dependency: True
v300_rt2eb_injectable_driver_added: True
v300_rt2eb_private_artifact_boundary_added: True
v300_rt2eb_controller_safe_metadata_propagation_added: True
v300_rt2eb_fake_driver_tests_added: True
v300_rt2eb_generated_plugin_registration_review_ready: True
v300_rt2eb_real_permission_request_executed: False
v300_rt2eb_real_microphone_accessed: False
v300_rt2eb_real_audio_captured: False
v300_rt2eb_raw_audio_exposed: False
v300_rt2e_parent_status: current-pending-rt2ec-implementation
v300_rt2ec_authorization: authorized-explicit-opt-in-real-device-bounded-capture-evidence-only
```
