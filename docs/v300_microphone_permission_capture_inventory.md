# DRC v3.0.0 RT-2a microphone permission and capture inventory

Updated: 2026-07-26

## Status

```text
Parent phase: RT-2 CURRENT / NOT_COMPLETED
Current small commit: RT-2b CURRENT / NOT_COMPLETED
Implementation state: RT-2a COMPLETED / ACCEPTED; RT-2b NOT_STARTED
Completed small commit: RT-2a COMPLETED / ACCEPTED
Microphone access: NOT_STARTED
Audio capture: NOT_STARTED
Real STT: BLOCKED_REAL_STT_NOT_IMPLEMENTED
```

## Purpose

RT-2a reads the actual Flutter, platform, and existing voice-input demo source and
freezes the smallest safe implementation sequence before DRC adds any microphone
dependency, permission declaration, or capture runtime. It prevents a package,
manifest edit, permission prompt, recording engine, and STT upload from being
introduced in one unreviewable change.

This checkpoint is docs/test-only.

## Inspected source

```text
app/pubspec.yaml
app/android/app/src/main/AndroidManifest.xml
app/ios/Runner/Info.plist
app/lib/screens/home_screen.dart
app/lib/models/voice_input_demo.dart
app/lib/services/backend_api_client.dart
backend/app/api/voice_input_demo.py
backend/app/models/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
```

## Current behavior inventory

### Flutter dependencies and app abstraction

`app/pubspec.yaml` contains HTTP, URL launch, and voice-output playback support,
but no microphone permission, recording, speech-to-text, media recorder, or audio
capture dependency. There is no DRC-owned microphone permission gateway, capture
engine, capture controller, or capture session model.

### Android

The main Android manifest does not declare `android.permission.RECORD_AUDIO`.
Debug/profile manifests contain development `INTERNET` permission only. DRC does
not currently request or access Android microphone permission.

### iOS

`app/ios/Runner/Info.plist` does not contain `NSMicrophoneUsageDescription`. DRC
does not currently request or access the iOS microphone.

### Web and desktop

There is no browser `getUserMedia`/`MediaRecorder` adapter and no Windows capture
adapter. Unsupported platforms currently have no typed DRC permission/capture
result because the app-owned abstraction has not been added yet.

### Existing Flutter voice-input demo

The Home screen button submits metadata such as a client event ID and text hint
to the existing Backend demo route. The UI explicitly explains that recording
and microphone permission are not used. It does not attach audio bytes, a file,
a stream, or a device identifier.

### Existing Backend voice-input demo

`POST /demo/voice-input` accepts a JSON metadata request. The route and service do
not accept audio, open a microphone, import an STT runtime, or execute a provider.
The response remains not-started/unavailable with `transcript=null`.

## RT-2 small-commit split

```text
RT-2a  Inventory and split
       Docs/test-only. Freeze current absence and safety requirements.

RT-2b  Permission contract and fake gateway
       Add DRC-owned permission states/results and a gateway interface.
       Add deterministic fake/unsupported gateways and Flutter unit tests.
       Do not add a permission plugin or platform declarations.

RT-2c  Platform permission wiring
       Add the selected permission dependency and Android/iOS declarations.
       Request permission only after an explicit user action.
       Do not start capture or send audio.

RT-2d  Capture lifecycle and fake engine
       Add DRC-owned capture state/result/session models, controller, fake engine,
       bounded state transitions, cancellation, and cleanup tests.
       Do not access a real microphone.

RT-2e  Guarded real capture adapter
       Add explicitly enabled bounded microphone capture with one active session,
       hard duration, explicit stop/cancel, temporary artifact cleanup, and clear
       unsupported/denied/error results. Do not call STT or upload audio.
```

Each child requires separate implementation, local verification, explicit
operator approval, acceptance sync, and commit before the next child begins.

## Safety contract

Later RT-2 implementation must preserve all of the following:

```text
- Safe default: microphone permission/capture disabled or unavailable.
- Explicit user gesture before a permission prompt or capture start.
- Permission states remain distinct: unknown, not_requested, granted, denied,
  permanently_denied, restricted, unsupported, and error.
- Capture states remain distinct: idle, preparing, ready, capturing, stopping,
  completed, cancelled, denied, unavailable, and error.
- Only one active capture session.
- Hard maximum duration and deterministic timeout result.
- Stop and cancel are idempotent.
- Raw audio is not persisted by default.
- Temporary artifacts are cleaned after completion, cancellation, or error.
- No background recording, always-on microphone, or wake-word listener.
- No transcript claim without RT-3 Framework STT execution.
- No audio upload/provider call before RT-3 authorization.
- No private device identifiers, audio paths, or captured payloads in public logs.
```

## RT-2a changed files

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_microphone_permission_capture_inventory.md
scripts/check_v300_microphone_permission_capture_inventory.py
```

## Protected surfaces

RT-2a must not change:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/app/src/main/AndroidManifest.xml
app/ios/Runner/Info.plist
backend/app/version.py
release_notes/**
```

## Verification boundary

The gate is credential-free, network-free, Framework-import-free, provider-free,
permission-free, microphone-free, capture-free, playback-free, and STT-free. It
reads source files and runs local structural assertions only.

Accepted output:

```text
v300_microphone_permission_capture_inventory_status: completed-accepted
v300_rt2a_backend_runtime_changed: False
v300_rt2a_flutter_runtime_changed: False
v300_rt2a_existing_tests_changed: False
v300_rt2a_microphone_dependency_added: False
v300_rt2a_android_record_audio_added: False
v300_rt2a_ios_microphone_usage_added: False
v300_rt2a_microphone_accessed: False
v300_rt2a_audio_captured: False
v300_rt2_parent_status: current-pending-rt2b-implementation
v300_rt2b_authorization: authorized-permission-contract-and-fake-gateway-only
```

## Acceptance evidence

RT-2a was accepted on 2026-07-26 after compileall, the RT-1b and RT-2a gates, Backend 116 with one existing Starlette deprecation warning, Flutter 103, `git diff --check`, seven-file diff review, and explicit operator approval passed.

## Stop rule

Do not add a microphone or permission dependency, Android/iOS permission, browser
media adapter, capture runtime, raw-audio artifact, upload, STT call, or realtime
session in RT-2a. RT-2b may now begin only as a separate app-owned permission
contract and fake/unsupported gateway change, without a platform plugin, manifest
permission, microphone access, capture, upload, STT, or realtime execution.
