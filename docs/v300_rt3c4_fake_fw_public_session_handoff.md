# DRC v3.0.0 RT-3c4 fake FW public-session handoff

```text
Source commit: 87ebbf1ad0722b4689311c4d7a2b8e982110efdc
Source archive SHA-256: B3A44AE494F7CE0F19E4530CF615035DB3A6E049F96377EDD5000AA4B76FC75E
Framework release: v5.3.0
RT-3c4: COMPLETED / ACCEPTED
RT-3c4 implementation: COMPLETED / ACCEPTED
Authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

## Purpose

RT-3c4 crosses the DRC Backend-to-Framework public voice-input boundary for the
first time. It consumes one accepted DRC-owned staged WAV artifact, constructs
only FW v5.3.0 public host-audio/request/session objects, explicitly injects
`FakeVoiceInputProviderAdapter`, normalizes the result into a path-free DRC type,
closes the public session, and lets the staging store remove the artifact once.

This is a fake contract handoff. It is not real transcription and does not
unblock RT-3 real STT acceptance.

## Backend boundary

The guarded endpoint is:

```text
POST /demo/voice-input/staging/{staging_id}/fake-handoff
```

The existing three gates still apply:

```text
VOICE_INPUT_DEMO_ENABLED=true
CONVERSATION_ENGINE=framework
VOICE_INPUT_ADAPTER_MODE=framework
```

The request contains safe metadata only:

```text
language
optional duration_ms in 1..15000
```

The response intentionally omits the staging ID, private path, FW audio ID, raw
audio, provider payload, credentials, and Framework root. It reports only the
fake outcome and explicit safety/lifecycle booleans.

## Public FW objects used

```text
VoiceInputAudioFormat.wav(...)
VoiceInputAudioSource.from_file_path(...)
VoiceInputRequest(...)
FakeVoiceInputProviderAdapter(...)
create_voice_input_session(...)
VoiceInputSession.transcribe_audio_result(...)
VoiceInputSession.close()
```

The Backend private path exists only inside
`VoiceInputStagingStore.consume(...)`. It is passed to FW's data-only
`VoiceInputAudioSource` reference and is never returned by the DRC adapter or
API. FW's fake adapter is required to report:

```text
adapter: fake
source_kind: file_path
audio_read: false
microphone_accessed: false
provider_execution_executed: false
```

Any unexpected runtime-side-effect flag is rejected as a safe contract failure.

## Single-use cleanup

Framework root/import/public-contract preflight occurs before staging consume. A
preflight failure preserves the staged artifact so configuration can be fixed
and retried.

Once the scoped consume callback begins:

- successful fake handoff removes the staged artifact;
- fake session failure removes the staged artifact;
- unexpected fake result removes the staged artifact;
- `VoiceInputSession.close()` is attempted in `finally`;
- a second consume returns `artifact_not_found`;
- public success and error payloads remain path-free.

## Honest execution status

```text
synthetic staged WAV used by tests/gate: yes
private Backend path passed to FW data contract: yes, scoped only
FW public package imported: yes
FW public VoiceInputSession created: yes
FakeVoiceInputProviderAdapter used: yes
FW session closed: yes
staged artifact single-use cleanup: yes
audio file read by FW fake adapter: no
microphone accessed: no
provider client created: no
provider execution: no
real transcription: no
real STT execution: no
real operator microphone artifact used: no
```

## Changed runtime surface

```text
backend/app/api/voice_input_demo.py
backend/app/models/voice_input_demo.py
backend/app/services/framework_voice_input_fake_handoff.py
backend/tests/test_framework_voice_input_fake_handoff.py
backend/tests/test_voice_input_fake_handoff_api.py
```

No Flutter, dependency, configuration, platform, version, release, or vendor FW
file changes are part of RT-3c4.

## Implementation validation target

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts

.\.venv\Scripts\python.exe `
  scripts\check_v300_framework_v530_stt_integration_inventory.py

.\.venv\Scripts\python.exe `
  scripts\check_v300_host_audio_handoff_lifecycle.py

.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c_private_staging_fw_handoff_readiness.py

.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c2_private_backend_staging_store.py

.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c3_guarded_upload_flutter_staging_consumer.py

.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c4_fake_fw_public_session_handoff.py

.\.venv\Scripts\python.exe -m pytest -q `
  backend\tests\test_framework_voice_input_fake_handoff.py `
  backend\tests\test_voice_input_fake_handoff_api.py

.\.venv\Scripts\python.exe -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

Expected implementation checkpoint counts:

```text
Focused Backend: 8 passed
Full Backend: 145 passed with the existing Starlette warning in the local environment
Flutter: 200 passed
```

RT-3c4 and parent RT-3c are `COMPLETED / ACCEPTED`. Acceptance passed with compileall, six RT-3 gates, focused Backend 8, full Backend 145 with the existing Starlette warning, clean Flutter analysis, full Flutter 200, exact 22-file surface review, `git diff --check`, and explicit operator approval. RT-3d remains blocked because FW v5.3.0 still has no concrete real STT provider execution.
