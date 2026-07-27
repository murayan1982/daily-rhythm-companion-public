# DRC v3.0.0 RT-2e-a real capture adapter readiness

Date: 2026-07-27
Parent phase: RT-2 CURRENT / NOT_COMPLETED
Parent small commit: RT-2e CURRENT / NOT_COMPLETED
Current small commit: RT-2e-a COMPLETED / ACCEPTED
Next small commit: RT-2e-b CURRENT / NOT_COMPLETED; NOT_STARTED

## Purpose

Freeze the exact dependency and adapter decision before adding any real recorder
plugin or runtime path. This checkpoint is docs/test-only.

## Exact accepted surface

```text
Flutter/Dart project SDK constraint: ^3.11.5
permission_handler direct dependency: 12.0.3
record direct dependency: absent
path_provider direct dependency: absent
path_provider transitive dependency: present
Android RECORD_AUDIO: already declared
iOS NSMicrophoneUsageDescription: already declared
RT-2d capture controller/fake engine: accepted
UI/startup real capture wiring: absent
Backend audio route/upload: absent
```

## Package decision

The current Dart baseline is 3.11.5. The `record` 7.x line requires Dart 3.12
or newer and is therefore not selected. `record` 6.2.1 is selected for RT-2e-b
as the compatible final pre-7 stable line.

The relevant package API provides:

```text
AudioRecorder.start(config, path: requiredPath)
AudioRecorder.startStream(config)
AudioRecorder.stop() -> private path or null
AudioRecorder.cancel() -> stop and discard/delete
AudioRecorder.dispose()
```

## DRC adapter decision

```text
permission check/request owner: existing MicrophonePermissionGateway
record package permission helper: not used by DRC adapter
output mode: file mode only
stream mode: forbidden for RT-2e because it exposes raw bytes
file location: private temporary directory allocated inside adapter boundary
returned public value: opaque capture id only
private path: never placed in public result/metadata/log/test output
stop: registers private artifact and returns opaque result
cancel/error/timeout/close: deletes partial/private artifact
upload/STT: forbidden until separately authorized
```

RT-2e-b must add direct dependencies only when implementation starts.
`path_provider` is already transitive but must become a direct dependency if the
DRC adapter imports it. RT-2e-b is authorized only for pinned dependencies, an
injectable adapter, private temporary artifact cleanup, and fake-driver tests;
real capture execution remains blocked for RT-2e-c.

## Small-commit split

```text
RT-2e-a  readiness/package decision; docs/test-only
RT-2e-b  pinned dependency + injectable adapter/private temporary artifact; fake tests only
RT-2e-c  explicit operator real-device bounded capture evidence
```

## Protected boundaries

RT-2e-a performs none of the following:

```text
flutter pub get
dependency or lockfile change
generated plugin registration change
Android/iOS/native file change
Flutter runtime or UI change
permission request
microphone open/access
audio capture or file creation
raw bytes/path/platform handle exposure
Backend upload
Framework/provider/STT execution
```

## Acceptance evidence

RT-2e-a was accepted on 2026-07-27 after compileall, the RT-2e-a
gate, Backend 116 tests with one existing warning, `flutter analyze`
with no issues, full Flutter 142 tests, `git diff --check`, seven-file
review, and explicit operator approval passed. No dependency, runtime,
platform, permission request, microphone access, audio capture, file
creation, upload, Framework/provider call, or STT execution occurred.

## Expected gate

```text
v300_microphone_real_capture_adapter_readiness_status: completed-accepted
v300_rt2ea_exact_current_surface_inspected: True
v300_rt2ea_record_candidate_selected: record-6.2.1
v300_rt2ea_record_7x_compatible_with_current_sdk: False
v300_rt2ea_dependency_added: False
v300_rt2ea_flutter_runtime_changed: False
v300_rt2ea_platform_files_changed: False
v300_rt2ea_permission_request_executed: False
v300_rt2ea_microphone_accessed: False
v300_rt2ea_audio_captured: False
v300_rt2e_parent_status: current-pending-rt2eb-implementation
v300_rt2eb_authorization: authorized-injectable-record-adapter-and-private-temporary-artifact-fake-tests-only
```
