# DRC v3.0.0 RT-2e-c2 operator capture harness

Status: COMPLETED / ACCEPTED
Parent small commit: RT-2e-c CURRENT / NOT_COMPLETED
Previous small commit: RT-2e-c1 COMPLETED / ACCEPTED
Completed small commit: RT-2e-c2 COMPLETED / ACCEPTED
Current evidence small commit: RT-2e-c3a COMPLETED / ACCEPTED
Authorization: separate-operator-harness-and-fake-widget-tests-only

## Purpose

RT-2e-c2 adds the separately launched operator harness fixed by RT-2e-c1. It
compiles the real-capable permission and record adapters behind two explicit
opt-ins, while all verification in this checkpoint uses fake permission,
capture, and private-artifact implementations.

No real permission request, microphone access, audio capture, upload, provider
call, or STT execution is part of RT-2e-c2.

## Double opt-in boundary

The harness is available only through:

```text
entrypoint: app/lib/main_rt2ec_operator.dart
compile-time flag: --dart-define=DRC_RT2EC_OPERATOR=true
in-app acknowledgement: required before dependency factory invocation
```

Without the compile-time flag, the target renders a blocked screen and does not
invoke the production dependency factory. With the flag but before the in-app
acknowledgement and activation action, the production-capable permission
gateway, record engine, and capture controller are still not constructed.

The normal `app/lib/main.dart` and `HomeScreen` remain unchanged.

## Explicit operator actions

The harness exposes each action separately:

```text
permission check
permission request
capture start
capture stop
capture cancel
```

There is no startup permission request or startup microphone open. Capture
start is enabled only after a granted permission result. The production
controller and every fake test controller use a hard maximum of 15 seconds.
The accepted record adapter remains WAV, 16 kHz, mono file mode and does not use
`startStream`.

## Private artifact cleanup

A completed stop result is handled as follows:

1. Read the opaque capture id only inside the operator harness action.
2. Call `discardPrivateArtifact` immediately.
3. Retain only the boolean registered/discarded/cleanup outcome in safe
   evidence.
4. Never render or copy the opaque id, private path, bytes, or audio content.

Cancel, timeout, close, and errors retain the accepted controller/engine cleanup
paths. Dependency disposal is owned by the bootstrap and is executed when the
separate operator app is removed.

## Safe evidence allowlist

The UI evidence model contains exactly:

```text
operator target enabled: boolean
acknowledgement completed: boolean
permission status: enum name
permission request attempted: boolean
capture phase: enum name
capture outcome: enum name
technical code: safe typed code
requested maximum duration: milliseconds
captured duration: milliseconds
microphone accessed: boolean
audio captured: boolean
raw audio exposed: false
private artifact registered: boolean
private artifact discarded: boolean
cleanup succeeded: boolean
```

It contains no opaque capture id, private path, raw bytes, audio content,
transcript, provider payload, or raw platform error.

## Fake/widget verification

`app/test/rt2ec_microphone_capture_operator_test.dart` verifies:

```text
disabled target does not invoke dependency factory
compile-time opt-in still requires acknowledgement
acknowledgement constructs only injected fake dependencies in tests
no permission or capture action runs at startup
permission check and request are separate
start remains disabled until permission is granted
start request is exactly 15 seconds
completed stop immediately discards by opaque id
cancel produces no completed artifact
safe evidence is an exact allowlist with no id/path/bytes
```

The test source does not instantiate
`PermissionHandlerMicrophonePermissionGateway` or
`RecordMicrophoneCaptureEngine.mobile()`.

## Explicit non-goals

RT-2e-c2 does not change or execute:

```text
default main.dart / HomeScreen
pubspec dependencies or lockfile
Android/iOS declarations
generated plugin registration
Backend routes or uploads
application settings opening
real permission request
real microphone access
real audio capture or playback
raw-byte streaming
Framework/provider calls
STT or transcript persistence
release/version metadata
```

## Expected verification

```text
compileall: pass
RT-2e-c2 gate: completed-accepted
Backend regression: 116 passed, existing warning allowed
flutter analyze: no issues
focused operator Flutter tests: 10 passed
full Flutter tests: 171 passed
git diff --check: pass
changed surface: exact twelve files
```

No Android app launch is part of this checkpoint. APK compilation is optional
because dependencies and platform registration are unchanged from accepted
RT-2e-b.

## Acceptance state

RT-2e-c2 is COMPLETED / ACCEPTED after compileall, the RT-2e-c2 gate,
Backend 116 with one existing warning, `flutter analyze`, focused Flutter 10,
full Flutter 171, `git diff --check`, exact twelve-file review, and explicit
operator approval passed. No real permission request, microphone access, audio
capture, upload, or STT execution occurred. RT-2e-c3a is COMPLETED / ACCEPTED
as docs/test-only preflight. RT-2e-c3b is CURRENT / NOT_COMPLETED and NOT_STARTED
under `authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only`;
no upload or STT is authorized.

## RT-2e-c3a preflight follow-up

RT-2e-c3a is COMPLETED / ACCEPTED as a docs/test-only physical-Android
operator preflight. It fixes the exact separate-target command, manual permission
reset and explicit request, one non-sensitive capture stopped before 15 seconds,
immediate opaque-id private-artifact discard, and marker-only safe evidence.
No Flutter/runtime/dependency/platform/Backend source changed and no permission
request, microphone access, audio capture, evidence collection, upload, or STT
execution occurred. Acceptance passed with compileall, the RT-2e-c3a gate,
Backend 116 with the existing warning, `flutter analyze`, full Flutter 171,
`git diff --check`, exact ten-file review, and explicit operator approval.
RT-2e-c3b is CURRENT / NOT_COMPLETED and NOT_STARTED under
`authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only`.
