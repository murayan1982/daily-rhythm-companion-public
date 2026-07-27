# DRC v3.0.0 RT-2b microphone permission contract

Date: 2026-07-26

Parent phase: RT-2 CURRENT / NOT_COMPLETED
Current small commit: RT-2c IMPLEMENTED / NOT_ACCEPTED
Implementation state: COMPLETED / ACCEPTED
RT-2c authorization: AUTHORIZED for platform permission wiring without capture only
RT-2c implementation: mobile gateway and Android/iOS declarations added; acceptance pending

## Purpose

RT-2b introduces the app-owned permission contract that later platform wiring
must implement. It deliberately stops before any operating-system permission
plugin, platform declaration, microphone access, or capture lifecycle.

## Changed runtime and test files

```text
app/lib/services/microphone_permission.dart
app/test/microphone_permission_test.dart
```

## Public app-owned model

The Flutter layer now owns these provider-neutral types:

```text
MicrophonePermissionStatus
  unknown
  granted
  denied
  permanentlyDenied
  restricted
  unsupported
  failed

MicrophonePermissionOperation
  check
  request
  openSettings

MicrophonePermissionResult
  status
  operation
  safeMessage
  canRequest
  canOpenSettings
  requestAttempted
  technicalCode
  immutable publicMetadata
```

The model remains conservative:

```text
unknown / denied       -> permission may be requested later
granted                -> permission state is usable, but capture is still absent
permanently denied     -> no repeated request; settings path may be offered
restricted             -> no repeated request
unsupported / failed   -> typed safe terminal result
```

A granted permission result does not imply that a microphone was opened or that
audio capture exists.

## Gateway contract

```text
MicrophonePermissionGateway.checkPermission()
MicrophonePermissionGateway.requestPermission()
MicrophonePermissionGateway.openAppSettings()
```

The interface contains no plugin type, platform type, audio type, raw bytes, file
path, provider payload, or Framework object.

## Fake gateway

`FakeMicrophonePermissionGateway` is a deterministic in-memory implementation for
unit tests and later UI state wiring. It provides:

```text
initial status
scripted request-status sequence
check/request/open-settings call counters
manual fake status update
settings-supported switch
```

The fake gateway explicitly reports:

```text
platform_permission_requested: false
settings_opened: false
```

It never calls an operating-system permission API and never opens settings.

## Focused tests

The focused test file verifies:

```text
unknown is conservative and requestable
granted remains distinct from capture availability
permanent denial offers settings rather than repeated request
public metadata is immutable
check does not request a platform permission
scripted request results are deterministic
open-settings is recorded but not executed
unsupported settings path stays typed
manual fake state changes do not touch a microphone
```

## Explicit non-goals

RT-2b does not add or change:

```text
permission_handler or another permission dependency
record / flutter_sound / microphone capture dependency
Android RECORD_AUDIO
Android runtime permission request
Apple NSMicrophoneUsageDescription
MethodChannel or platform implementation
browser getUserMedia / mediaDevices
HomeScreen or voice-input UI
capture state/controller/engine
audio bytes, files, persistence, or upload
Backend runtime or routes
AI Character Framework imports or calls
provider execution
STT execution
always-on or background recording
```

## Protected behavior

The current voice-input demo remains metadata-only. The Backend still accepts no
audio body and starts no STT session. Existing voice-output playback and all v2.x
release records remain unchanged.

## Acceptance requirements

RT-2b acceptance evidence confirmed on 2026-07-26:

```text
compileall passes
RT-2b source/runtime gate passes
focused Flutter permission tests pass
full Flutter tests pass
full Backend regression tests pass
git diff --check passes
changed files are limited to the declared surface
explicit approval is given
```

Accepted gate state:

```text
v300_microphone_permission_contract_status: completed-accepted
v300_rt2b_flutter_contract_added: True
v300_rt2b_focused_tests_added: True
v300_rt2b_dependency_added: False
v300_rt2b_platform_permission_added: False
v300_rt2b_method_channel_added: False
v300_rt2b_ui_changed: False
v300_rt2b_backend_changed: False
v300_rt2b_microphone_accessed: False
v300_rt2b_audio_captured: False
v300_rt2_parent_status: current-pending-rt2c-implementation
v300_rt2c_authorization: authorized-platform-permission-wiring-without-capture-only
```

Operator evidence: compileall passed; RT-2b gate passed after portable protected-surface fixes; focused Flutter 9 passed; full Flutter 112 passed; Backend 116 passed with one existing Starlette deprecation warning; `git diff --check` passed; changed files matched the declared nine-file surface; explicit approval was given.


RT-2c follow-up state: IMPLEMENTED / NOT_ACCEPTED. The RT-2b app-owned contract remains unchanged; the new plugin adapter and the generated Windows plugin-registration review are documented separately in `docs/v300_microphone_platform_permission_wiring.md`.
