# DRC v3.0.0 RT-2d microphone capture lifecycle and fake engine

Updated: 2026-07-27

Parent phase: RT-2 CURRENT / NOT_COMPLETED
Completed small commit: RT-2d COMPLETED / ACCEPTED
Current small commit: RT-2e CURRENT / NOT_COMPLETED; NOT_STARTED

## Purpose

RT-2d fixes the DRC-owned capture lifecycle before any real microphone adapter
is introduced. It adds request, state, result, controller, deadline, engine, and
deterministic fake-engine contracts. The controller checks the existing
permission gateway, enforces one active capture and a hard duration bound, and
normalizes stop, cancel, timeout, permission, busy, and cleanup failures.

This checkpoint does not request an operating-system permission, open a
microphone, capture or persist audio, expose bytes or local paths, upload data,
change the UI, call Backend/Framework/provider runtime, or execute STT.

## Changed runtime and test files

```text
app/lib/services/microphone_capture.dart
app/test/microphone_capture_test.dart
```

Planning and gate files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_microphone_capture_lifecycle.md
scripts/check_v300_microphone_capture_lifecycle.py
```

Declared changed-file surface: 9 files.

## App-owned lifecycle contract

`MicrophoneCapturePhase` keeps these lifecycle states distinct:

```text
idle
checkingPermission
starting
capturing
stopping
completed
cancelled
denied
permanentlyDenied
restricted
unsupported
timedOut
failed
```

`MicrophoneCaptureOutcome` additionally exposes command outcomes that should not
replace the currently active lifecycle state:

```text
started
completed
cancelled
denied
permanentlyDenied
restricted
unsupported
busy
timedOut
failed
noActiveCapture
```

A second start while checking, starting, capturing, or stopping returns typed
`busy` and does not replace or restart the active session.

## Bounded duration

Every `MicrophoneCaptureRequest` carries `maxDuration`. The controller rejects
zero/negative durations and requests above its hard maximum before checking
permission or starting an engine. The default hard maximum is 60 seconds.

A deadline is scheduled only after the engine reaches `capturing`. Deadline
expiry cancels the engine and publishes typed `timedOut`, including whether
cleanup succeeded. Tests inject a deterministic scheduler instead of sleeping.

## Permission boundary

RT-2d calls only:

```text
MicrophonePermissionGateway.checkPermission()
```

It does not call `requestPermission()` or `openAppSettings()`. Explicit platform
permission requests remain a later UI action. The controller maps granted,
denied, permanently denied, restricted, unsupported, unknown, failed, and thrown
permission checks into safe DRC-owned outcomes without exposing raw errors.

## Fake engine boundary

`FakeMicrophoneCaptureEngine` records start, stop, cancel, and dispose calls and
returns an opaque fake identifier on stop. It never opens a platform microphone
or produces audio. Its metadata always records:

```text
microphone_accessed: false
audio_captured: false
raw_audio_exposed: false
```

`MicrophoneCaptureEngineResult` intentionally has no byte buffer, filesystem
path, platform handle, or raw-audio field. The fake result is state-machine
evidence only and must not be treated as a real audio artifact.

## Cleanup rules

```text
normal stop: cancel deadline, stop engine, publish completed
explicit cancel: cancel deadline, cancel engine, publish cancelled
start failure after partial activation: attempt engine cancel
stop failure: attempt engine cancel before publishing failed
timeout: cancel engine and publish timedOut even if cleanup also fails
close/dispose: cancel deadline, cancel active fake engine, dispose engine
```

Raw exception messages are not copied into public metadata or user messages.

## Protected boundaries

```text
permission_handler adapter changed: false
permission request executed: false
new capture dependency: false
Android/iOS declarations changed: false
startup/HomeScreen/voice-input UI changed: false
real microphone opened/accessed: false
real audio captured/persisted/uploaded: false
raw audio bytes/path/handle exposed: false
Backend changed: false
Framework/provider/STT execution: false
RT-2e authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only
```

## Focused tests

The focused test suite covers:

```text
idle state
granted permission and fake-only start
denied/permanently-denied/restricted/unsupported mapping
single-active busy result
positive and hard-maximum duration validation
opaque fake stop result
explicit cancel cleanup
deterministic timeout cleanup
partial-start cleanup
stop-error cleanup
cancel-cleanup failure typing
permission-check exception redaction
close/dispose cleanup
immutable public metadata
```

## Operator acceptance

RT-2d is `COMPLETED / ACCEPTED`. The following evidence passed on 2026-07-27:

```text
compileall
RT-2d source/surface gate
flutter analyze: No issues found
focused Flutter: 17 passed
full Flutter: 142 passed
full Backend regression: 116 passed with one existing warning
git diff --check
9-file declared changed-surface review
explicit operator approval
```

No permission request, real microphone access, audio capture, raw-audio
exposure, Backend upload, Framework/provider call, or STT execution occurred.

Android/iOS build execution is not required for RT-2d because it changes no
plugin dependency, generated plugin registration, native manifest, or platform
implementation. Tests must use only fake permission and capture components.

Expected accepted gate output:

```text
v300_microphone_capture_lifecycle_status: completed-accepted
v300_rt2d_capture_contract_added: True
v300_rt2d_controller_added: True
v300_rt2d_fake_engine_added: True
v300_rt2d_single_active_capture_enforced: True
v300_rt2d_bounded_duration_enforced: True
v300_rt2d_permission_request_executed: False
v300_rt2d_real_capture_dependency_added: False
v300_rt2d_ui_changed: False
v300_rt2d_backend_changed: False
v300_rt2d_microphone_accessed: False
v300_rt2d_audio_captured: False
v300_rt2d_raw_audio_exposed: False
v300_rt2_parent_status: current-pending-rt2e-implementation
v300_rt2e_authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only
```
