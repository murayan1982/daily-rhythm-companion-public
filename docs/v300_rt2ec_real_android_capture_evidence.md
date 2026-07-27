# DRC v3.0.0 RT-2e-c3b real Android capture evidence

Date: 2026-07-27
Status: COMPLETED / ACCEPTED
Parent small commit: RT-2e-c3 COMPLETED / ACCEPTED
Source commit: ddae21944ac0e251cd8194bf93982bd5dc7a4ae8
Evidence mode: marker-only public-safe record
Next phase: RT-3 BLOCKED_REAL_STT_NOT_IMPLEMENTED

## Acceptance execution note

A first operator session confirmed explicit stop and private-artifact discard,
but the captured-duration marker was not retained before the session ended. That
session is not used as acceptance evidence. The marker below represents the
later acceptance session, which performed exactly one completed capture.

A private operator screenshot was reviewed to transcribe the allowlisted values.
The screenshot itself, its path, device details, and all non-allowlisted content
are intentionally absent from the repository.

## Accepted marker

```json
{
  "schema": "drc-v300-rt2ec3b-real-android-capture-v1",
  "source_commit": "ddae21944ac0e251cd8194bf93982bd5dc7a4ae8",
  "target_class": "physical-android",
  "operator_target_enabled": true,
  "acknowledgement_completed": true,
  "permission_status": "granted",
  "permission_request_attempted": true,
  "capture_phase": "completed",
  "capture_outcome": "completed",
  "technical_code": "capture_completed",
  "requested_maximum_duration_milliseconds": 15000,
  "captured_duration_milliseconds": 4820,
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
  "raw_screenshot_committed": false,
  "post_run_working_tree_clean": true
}
```

## Acceptance interpretation

```text
source commit matched the accepted RT-2e-c3a clean HEAD: true
physical Android target: true
separate operator target and compile-time opt-in: true
in-app acknowledgement: true
explicit permission request and granted result: true
completed capture within 1..15000 ms: true
microphone accessed and audio captured: true
raw audio exposed: false
private artifact registered and discarded: true
cleanup succeeded: true
Backend started: false
audio uploaded: false
STT executed: false
private identifiers/content committed: false
post-run working tree clean: true
```

The accepted duration is 4820 ms, below the exact 15000 ms maximum. The public
result contains no raw audio, path, opaque id, device identifier, transcript, or
provider payload.

## Scope closure

RT-2e-c3b, RT-2e-c3, RT-2e-c, RT-2e, and RT-2 are COMPLETED / ACCEPTED. The
normal app remains unchanged and the operator harness remains opt-in only. This
evidence does not authorize audio upload or STT. RT-3 remains blocked until an
accepted real STT public boundary exists.

## Verification

Run from the repository root before committing the acceptance sync:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt2ec_real_android_capture_evidence.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

No second real-device execution is required for this docs/test acceptance sync.
