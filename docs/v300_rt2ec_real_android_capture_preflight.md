# DRC v3.0.0 RT-2e-c3a real Android capture preflight

Status: COMPLETED / ACCEPTED
Parent small commit: RT-2e-c3 CURRENT / NOT_COMPLETED
Previous small commit: RT-2e-c2 COMPLETED / ACCEPTED
Completed small commit: RT-2e-c3a COMPLETED / ACCEPTED
Current evidence small commit: RT-2e-c3b CURRENT / NOT_COMPLETED; NOT_STARTED
Authorization: authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only

## Inspected accepted source

```text
Accepted operator implementation commit: b2e2adb
Exact archive SHA-256: 18d39ea0676bcd3213c104a71fd5ce2c096c6b96002eb7aaef7ceccd06a2fd86
Operator entrypoint: app/lib/main_rt2ec_operator.dart
Operator harness: app/lib/operators/rt2ec_microphone_capture_operator.dart
Android permission: android.permission.RECORD_AUDIO
Permission adapter: permission_handler 12.0.3
Capture adapter: record 6.2.1
Private directory adapter: path_provider 2.1.6
Encoding: WAV / 16000 Hz / mono
Maximum duration: 15 seconds
Raw stream mode: forbidden
```

No Flutter/runtime/dependency/platform/Backend source changed.
RT-2e-c3a changes documentation and one source/surface gate only. It does not
launch Flutter, connect a device, request permission, access a microphone,
capture audio, generate operator evidence, upload audio, or run STT.

## RT-2e-c3 split

```text
RT-2e-c3a  real Android operator preflight/runbook and safe evidence contract
            docs/test-only; completed and accepted
RT-2e-c3b  explicit physical-Android permission/capture/cleanup evidence
            current, not completed, not started
            completed stop must call discardPrivateArtifact by opaque id
```

## Required execution environment for RT-2e-c3b

RT-2e-c3b accepts only:

```text
one physical Android handset connected by USB or approved wireless debugging
clean accepted repository HEAD
Android Flutter target selected explicitly by device id
separate operator entrypoint
compile-time operator flag enabled
in-app acknowledgement completed
non-sensitive spoken test phrase
Backend not started
no STT/provider runtime configured or invoked
private evidence kept outside Git
```

The following are not accepted as the real-device target:

```text
Android emulator
Chrome/Web
Windows desktop
Linux/macOS desktop
iOS
normal app/lib/main.dart startup
```

Do not record a device serial, model name, account name, local private path, or
raw screenshot in a commit, public issue, release asset, or marker-only evidence.

## Pre-run safety checks

Before the later real run:

1. Confirm the repository is clean and record the accepted source commit using
   only the commit SHA.
2. Confirm exactly one intended physical Android target with `flutter devices`.
   Do not paste or commit its serial/model output.
3. Stop Backend and any STT/provider process. The operator harness does not need
   Backend.
4. In Android settings, revoke/deny microphone permission for the debug app, or
   uninstall the prior debug app, so the explicit permission request can be
   observed.
5. Use only a short non-sensitive phrase such as a neutral test count. Do not
   speak names, health information, addresses, credentials, or private content.
6. Choose a private evidence location outside the repository. Raw screenshots
   remain private and uncommitted.
7. Confirm `git status --short` is empty immediately before the run.

## Only accepted operator launch command

Run from `app` at the clean accepted RT-2e-c3a HEAD:

```powershell
flutter run `
  -d <ANDROID_DEVICE_ID> `
  --target lib/main_rt2ec_operator.dart `
  --dart-define=DRC_RT2EC_OPERATOR=true
```

`<ANDROID_DEVICE_ID>` is local/private and must not be committed or copied into
marker-only evidence. Do not launch `lib/main.dart`. Do not add Backend URL or
provider defines.

## Exact in-app sequence

Perform one completed capture only:

1. Confirm the operator opt-in screen appears.
2. Read and select the in-app acknowledgement.
3. Select `オペレーターハーネスを有効化`.
4. Select `権限を確認`.
5. Select `権限を要求` and grant Android microphone permission.
6. Confirm capture start becomes enabled only after granted permission.
7. Select `録音を開始`.
8. Speak one non-sensitive phrase for approximately 2 to 5 seconds.
9. Select `録音を停止` before 15 seconds.
10. Confirm the UI reports that the private artifact was deleted.
11. Record only the safe evidence fields below.
12. Terminate `flutter run` and confirm `git status --short` remains empty.

Do not play the recording, resolve its private path, inspect its bytes, upload
it, send it to Backend/Framework/provider code, or execute STT.

## Accepted safe evidence

Marker-only evidence may contain exactly these public-safe fields:

```json
{
  "schema": "drc-v300-rt2ec3b-real-android-capture-v1",
  "source_commit": "<accepted-clean-head-sha>",
  "target_class": "physical-android",
  "operator_target_enabled": true,
  "acknowledgement_completed": true,
  "permission_status": "granted",
  "permission_request_attempted": true,
  "capture_phase": "completed",
  "capture_outcome": "completed",
  "technical_code": "capture_completed",
  "requested_maximum_duration_milliseconds": 15000,
  "captured_duration_milliseconds": 1,
  "microphone_accessed": true,
  "audio_captured": true,
  "raw_audio_exposed": false,
  "private_artifact_registered": true,
  "private_artifact_discarded": true,
  "cleanup_succeeded": true,
  "backend_started": false,
  "audio_uploaded": false,
  "stt_executed": false,
  "private_path_recorded": false,
  "opaque_capture_id_recorded": false,
  "device_identifier_recorded": false,
  "raw_audio_recorded": false,
  "raw_screenshot_committed": false
}
```

`captured_duration_milliseconds` must be an observed integer from 1 through
15000. The sample value `1` above is schema documentation, not execution
evidence.

## Forbidden evidence

Never include:

```text
device id / serial / model
Android account or notification content
private filesystem path
opaque capture id
raw audio bytes or encoded audio
audio file or audio content
transcript or spoken phrase
provider payload or raw platform exception
API keys, tokens, authorization headers
raw screenshot in Git or release artifacts
private evidence directory path
```

Raw screenshots may be reviewed privately, but only the marker-only allowlist is
eligible for acceptance records.

## RT-2e-c3b acceptance conditions

Every item is required:

```text
source commit is the clean accepted RT-2e-c3a commit
physical Android target used
compile-time flag and in-app acknowledgement both true
permission request attempted true
permission status granted
capture phase/outcome completed
technical code capture_completed
requested maximum exactly 15000 ms
captured duration in 1..15000 ms
microphone accessed true
audio captured true
raw audio exposed false
private artifact registered true
private artifact discarded true
cleanup succeeded true
Backend started false
audio uploaded false
STT executed false
no private path, opaque id, device identifier, raw audio, or raw screenshot committed
post-run working tree clean
```

Failure, denial, cleanup failure, timeout, duration above 15 seconds, raw-audio
exposure, upload, STT, or a dirty working tree blocks acceptance. Do not retry by
loosening the contract.

## RT-2e-c3a non-change and non-execution record

```text
Flutter runtime changed: false
Backend runtime changed: false
pubspec/lock changed: false
Android/iOS declaration changed: false
generated plugin registration changed: false
operator harness changed: false
permission request executed: false
microphone accessed: false
audio captured: false
operator evidence created: false
Backend upload executed: false
STT executed: false
```

## RT-2e-c3a verification

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt2ec_real_android_capture_preflight.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

Expected regression baseline:

```text
Backend: 116 passed, existing warning allowed
flutter analyze: no issues
Flutter: 171 passed
changed surface: exact ten files
git diff --check: pass
```

RT-2e-c3a is COMPLETED / ACCEPTED after compileall, the RT-2e-c3a gate,
Backend 116 with the existing warning, `flutter analyze`, full Flutter 171,
`git diff --check`, exact ten-file review, and explicit operator approval passed.
No real permission request, microphone access, or audio capture occurred during
this docs/test-only checkpoint. RT-2e-c3b is CURRENT / NOT_COMPLETED and
NOT_STARTED under
`authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only`.
