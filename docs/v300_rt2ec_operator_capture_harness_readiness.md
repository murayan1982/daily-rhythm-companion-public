# DRC v3.0.0 RT-2e-c1 operator capture harness readiness

Status: COMPLETED / ACCEPTED
Parent small commit: RT-2e-c CURRENT / NOT_COMPLETED
Completed small commit: RT-2e-c1 COMPLETED / ACCEPTED
Current small commit: RT-2e-c2 CURRENT / NOT_COMPLETED; NOT_STARTED
Evidence small commit: RT-2e-c3 BLOCKED / NOT_STARTED
Authorization: docs-test-only-readiness-before-real-device-execution

## Purpose

RT-2e-c1 rereads the exact accepted `5a7f814` source surface and fixes the
operator-only real-device harness contract before any executable harness or
real microphone action is added. It is a docs/test-only checkpoint.

## Exact current surface confirmed

```text
Dart SDK: ^3.11.5
record: 6.2.1 direct and locked
path_provider: 2.1.6 direct and locked
permission_handler: 12.0.3
capture controller: accepted, single-active, bounded, check-only
record adapter: accepted, WAV 16 kHz mono file mode
private artifact access: opaque id resolver/discard boundary
normal startup: lib/main.dart -> HomeScreen
voice-input demo: Backend metadata-only request; no microphone wiring
Android RECORD_AUDIO: declared
iOS NSMicrophoneUsageDescription: declared
```

The accepted production-capable record driver is compiled but no default app
path instantiates or executes it.

## RT-2e-c split

```text
RT-2e-c1  operator-only harness/readiness contract; docs/test-only
RT-2e-c2  operator harness implementation and fake/widget tests; no real execution
RT-2e-c3  explicit real Android bounded capture and cleanup evidence
```

RT-2e-c1 is accepted. RT-2e-c2 is authorized for the separate operator
harness and fake/widget tests only. RT-2e-c3 remains blocked until RT-2e-c2 is
accepted.

## Required operator boundary

The later harness must satisfy all of the following:

1. Use a separate `app/lib/main_rt2ec_operator.dart` target.
2. Require `--dart-define=DRC_RT2EC_OPERATOR=true`.
3. Render a blocked screen and construct no real-capable dependencies without
   that compile-time flag.
4. Require an in-app acknowledgement that the operator will speak only
   non-sensitive test audio and that no upload/STT occurs.
5. Keep `app/lib/main.dart` and `HomeScreen` unchanged.
6. Expose permission check, permission request, start, stop, and cancel as
   separate explicit user actions. No startup action may request permission or
   open the microphone.
7. Allow start only after a granted permission result.
8. Use exactly one active capture with a maximum duration of 15 seconds.
9. Reuse WAV, 16 kHz, mono file mode. `startStream` remains forbidden.
10. On completed stop, immediately discard the private artifact through
    `RecordMicrophoneCapturePrivateArtifactAccess.discardPrivateArtifact` using
    only the opaque capture id.
11. On cancel, timeout, close, and error, preserve the accepted cleanup paths.
12. Never display, log, copy, persist, upload, or commit a private path, raw
    audio bytes, audio content, transcript, provider payload, or raw platform
    error payload.

## Safe operator evidence allowlist

Only these values may be shown or copied as evidence:

```text
operator target enabled: boolean
acknowledgement completed: boolean
permission status: enum name
permission request attempted: boolean
capture phase/outcome: enum name
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

Opaque capture ids are app-internal and should not be included in pasted or
committed evidence. Private paths are forbidden.

## Explicit non-goals

RT-2e-c1 does not add or execute:

```text
operator Flutter entrypoint or UI
runtime microphone wiring
permission request
application settings open
microphone access
real audio capture or playback
raw-byte stream
Backend route or upload
Framework/provider call
STT execution
transcript persistence
release/version change
```

## Expected verification

```text
compileall: pass
RT-2e-c1 source/surface gate: completed-accepted
Backend regression: 116 passed, existing warning allowed
flutter analyze: no issues
full Flutter tests: 161 passed
git diff --check: pass
changed surface: exact eight files
```

No real Android run is part of RT-2e-c1.

## Acceptance record

RT-2e-c1 is COMPLETED / ACCEPTED after compileall, the source/surface gate,
Backend 116 tests with one existing warning, `flutter analyze`, full Flutter 161
tests, `git diff --check`, exact eight-file review, and explicit operator
approval passed. No permission request, microphone access, audio capture,
upload, or STT execution occurred. RT-2e-c2 is CURRENT / NOT_COMPLETED and
NOT_STARTED with authorization
`authorized-separate-operator-harness-and-fake-widget-tests-only`.
