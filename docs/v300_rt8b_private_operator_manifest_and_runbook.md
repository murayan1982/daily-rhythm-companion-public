# Daily Rhythm Companion v3.0.0 RT-8b private operator manifest, validator, and runbook

Updated: 2026-08-03

## Candidate state

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8a commit: a3af4fae002c1425fdfb61b46f66e35e2443ad17
RT-8b: IMPLEMENTED / AWAITING_REVIEW
RT-8b baseline: a3af4fae002c1425fdfb61b46f66e35e2443ad17
RT-8b surface: exact 10 files
readiness: READY_FOR_BOUNDED_PRIVATE_RT8_OPERATOR_MANIFEST_AND_NETWORK_FREE_VALIDATION
RT-8c exact contract review: READY_AFTER_RT8B_ACCEPTANCE
RT-8c implementation: NOT_AUTHORIZED
RT-8d implementation: NOT_AUTHORIZED
RT-8e implementation: NOT_AUTHORIZED
RT-9: BLOCKED_PENDING_RT8
private manifest created: false
private manifest read: false
private configuration read: false
provider execution attempted: false
network execution attempted: false
microphone used: false
real TTS executed: false
real motion executed: false
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-8b prepares public-safe, credential-free tooling for the later bounded PC Windows and Android smartphone operator controls. It does not execute those
controls. The implementation freezes:

```text
- one strict private manifest schema;
- one deliberately rejected public example;
- one network-free validator;
- one source/static preflight gate;
- focused synthetic tests;
- one fixed preflight, execution, cleanup, and validation runbook.
```

A real private manifest may be created only after a later separately authorized
operator stage. It must live under ignored `operator_evidence/` and must never
be committed, pushed, packaged, or pasted into public review output.

## Readiness classification

```text
READY_FOR_BOUNDED_PRIVATE_RT8_OPERATOR_MANIFEST_AND_NETWORK_FREE_VALIDATION
```

This does not mean:

```text
READY_FOR_PC_WINDOWS_REAL_EXECUTION
READY_FOR_ANDROID_REAL_EXECUTION
READY_FOR_PRIVATE_CONFIGURATION_READ
READY_FOR_PROVIDER_OR_NETWORK_EXECUTION
READY_FOR_RELEASE
```

## Exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8b_private_operator_manifest_and_runbook.md
docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json
scripts/validate_v300_rt8_private_operator_manifest.py
scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py
backend/tests/test_v300_rt8_private_operator_manifest.py
```

New files:

```text
docs/v300_rt8b_private_operator_manifest_and_runbook.md
docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json
scripts/validate_v300_rt8_private_operator_manifest.py
scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py
backend/tests/test_v300_rt8_private_operator_manifest.py
```

The remaining five files synchronize current-state and exact-contract markers.

## Existing ignore boundary

The repository already ignores:

```text
operator_evidence/
```

RT-8b does not change `.gitignore`. Public-safe templates stay under
`docs/operator_evidence_templates/`; actual private manifests and any raw local
operator evidence stay under `operator_evidence/` only.

## Manifest envelope

Every manifest uses the exact envelope below. Unknown, missing, and duplicate
JSON keys are rejected.

```text
schema_version: drc.v3.rt8-platform-acceptance.1
manifest_kind: private_rt8_pc_android_realtime_acceptance
stage: example | pc_windows | android | aggregate
status: example_not_accepted | accepted
candidate_branch: main
pc_windows_candidate_source_head: fixed placeholder or 40 lowercase hex
android_candidate_source_head: fixed placeholder or 40 lowercase hex
sections:
  pc_windows
  android
  aggregate_cleanup
  privacy
  non_claims
```

Allowed placeholder:

```text
REPLACE_WITH_40_LOWERCASE_HEX
```

No other free-form string is permitted. The maximum private manifest size is
65536 bytes. UTF-8 is strict. The JSON root must be one object.

## Stage progression

### Public `example`

```text
stage: example
status: example_not_accepted
candidate heads: fixed placeholders
PC status: not_run
Android status: not_run
aggregate status: not_run
all booleans: false
all counts: 0
```

The committed example is intentionally unusable as accepted evidence. Running
`--check-example` confirms `rejected-as-template` and reads no private file.

### Private `pc_windows`

```text
stage: pc_windows
status: accepted
PC candidate head: current 40-lowercase-hex source commit
Android candidate head: fixed placeholder
PC status: accepted
Android status: not_run
aggregate status: not_run
```

The PC section requires the fixed Controls PC-A through PC-H:

```text
PC-A inert/default-off startup:
  default_off_startup_confirmed: true
  execution_before_explicit_action: false

PC-B manual incremental stream:
  manual_stream_start_count: 1
  incremental_output_before_terminal: true
  completed_terminal: true

PC-C cooperative cancel:
  cooperative_cancel_request_count: 1
  cancelled_terminal: true
  partial_output_retained: true
  provider_hard_cancel_claimed: false

PC-D explicit TTS natural completion:
  explicit_tts_process_count: 1
  real_tts_generated: true
  audible_playback_started: true
  audible_playback_completed_naturally: true

PC-E explicit local flush:
  active_playback_before_flush: true
  explicit_flush_count: 1
  local_playback_stop_requested: true
  local_playback_stop_succeeded: true
  pending_after_flush: 0
  active_after_flush: false

PC-F app-owned motion presentation:
  app_owned_motion_presentation_count: 1
  app_owned_motion_presentation_completed: true
  real_provider_motion_execution_claimed: false

PC-G manual VTS Apply:
  manual_vts_apply_count: 1
  vts_commands_requested/applied/completed: 1/1/1
  framework_session_created/closed: true/true
  provider_execution_attempted: true
  network_execution_attempted: true
  backend_flutter_real_motion_executed: false
  operator_visible_physical_motion_confirmed: true

PC-H local lifecycle and cleanup:
  reset/opt_out/disposal additional Backend requests: false
  additional provider/network/visible-motion execution: false
  recognized_processes_stopped: true
  real_execution_flags_closed: true
  private_process_values_removed: true
```

PC acceptance does not include real microphone, STT, or soft barge-in.

### Private `android`

```text
stage: android
status: accepted
PC status: accepted
Android status: accepted
aggregate status: not_run
PC candidate head: accepted ancestor
Android candidate head: current source commit
```

The Android section requires the fixed Controls Android-A through Android-H:

```text
Android-A inert/default-off startup:
  default_off_startup_confirmed: true
  execution_before_explicit_action: false

Android-B natural full voice turn:
  natural_voice_turn_count: 1
  bounded microphone capture: completed
  private staging: consumed and cleaned
  real STT: completed
  provider-neutral transcript handoff: completed
  incremental stream: completed
  completed terminal-to-TTS handoff: true
  real TTS generated: true
  audible playback completed naturally: true

Android-C silent negative control:
  silent_negative_control_observed: true
  playback_remained_active_during_silence: true
  silent_control_interruption_count: 0

Android-D real speech interruption:
  confirmed_user_speech_event_count: 1
  drc_local_interruption_count: 1
  local playback stop requested/succeeded: true/true

Android-E old-work invalidation:
  old_work_remained_inert: true
  old_audio_resumed: false
  late_old_completion_affected_current_state: false
  pending_voice_output_after_interruption: 0

Android-F recovery turn:
  recovery_voice_turn_count: 1
  recovery STT/stream/TTS/playback completed: true

Android-G manual VTS Apply:
  manual_vts_apply_count: 1
  vts_commands_requested/applied/completed: 1/1/1
  framework_session_created/closed: true/true
  provider_execution_attempted: true
  network_execution_attempted: true
  backend_flutter_real_motion_executed: false
  operator_visible_physical_motion_confirmed: true

Android-H local lifecycle and cleanup:
  reset/opt_out/disposal additional Backend requests: false
  additional provider/network/visible-motion execution: false
  recognized_processes_stopped: true
  real_execution_flags_closed: true
  private_process_values_removed: true
  private capture/audio artifacts remaining: false
```

### Private `aggregate`

```text
stage: aggregate
status: accepted
PC status: accepted
Android status: accepted
aggregate status: accepted
```

Aggregate cleanup requires:

```text
PC accepted: true
Android accepted: true
both candidate commits verified: true
both platform cleanups passed: true
Backend processes stopped: true
Flutter processes stopped: true
private environment values removed: true
private process values removed: true
all real-execution flags closed: true
private staged audio remaining: false
private logs remaining: false
private backups remaining: false
operator evidence committed: false
operator evidence pushed: false
DRC working tree clean: true
DRC HEAD/origin-main synchronized: true
FW working tree clean: true
RT-9 implementation authorized: false
```

## Privacy section

Every marker below must remain `false`:

```text
spoken_text_included
transcript_included
generated_response_included
raw_audio_or_pcm_included
audio_url_or_artifact_id_included
stream_session_or_turn_id_included
provider_identity_included
provider_model_included
provider_payload_included
credential_included
token_included
authorization_header_included
private_endpoint_included
private_path_included
lan_ip_included
device_identifier_included
vts_model_or_hotkey_identity_included
screenshot_or_recording_included
raw_log_included
raw_exception_included
operator_evidence_file_committed
operator_evidence_file_pushed
```

The validator also rejects sensitive-looking token strings, authorization
headers, user-private Windows or Unix paths, and local/private address values.
It reports only a fixed reason code and, where safe, a schema key name. It never
echoes a rejected value or manifest path.

## Explicit non-claims section

Every marker below must remain `false`:

```text
pc_real_microphone_claimed
pc_real_stt_claimed
pc_soft_barge_in_claimed
web_microphone_acceptance_claimed
ios_acceptance_claimed
all_android_devices_claimed
always_on_microphone_claimed
automatic_next_turn_capture_claimed
provider_llm_hard_cancel_claimed
provider_stt_hard_cancel_claimed
provider_tts_hard_cancel_claimed
backend_http_hard_cancel_claimed
fw_real_tts_queue_flush_claimed
fw_unified_realtime_runtime_claimed
automatic_voice_motion_sync_claimed
automatic_emotion_inference_claimed
physical_motion_proven_by_runtime_claimed
production_security_ready_claimed
v300_release_ready_claimed
```

## Validator safety contract

`scripts/validate_v300_rt8_private_operator_manifest.py` is the sole RT-8
private manifest validator.

```text
default mode: none; one explicit mode is required
public mode: --check-example
private mode: --manifest-json plus --stage and --minimum-source-head
private directory: operator_evidence/ only
ignored-by-Git check: required
regular non-symlink file: required
maximum size: 65536 bytes
encoding: strict UTF-8
JSON root: object only
duplicate JSON keys: rejected
unknown or missing keys: rejected
free-form strings: rejected
branch: main
HEAD/origin-main sync: required for accepted private stages
clean working tree: required for accepted private stages
candidate commit existence/ancestry: required
```

The validator may invoke local Git only. It contains no HTTP client, socket,
provider SDK, microphone, recorder, audio player, WebSocket, `pyvts`, or
`websockets` dependency. It never starts Backend or Flutter.

## Focused synthetic tests

`backend/tests/test_v300_rt8_private_operator_manifest.py` verifies:

```text
- public example rejected as a template;
- synthetic PC, Android, and aggregate manifests accepted;
- missing and unknown keys rejected;
- duplicate keys rejected;
- oversized and malformed UTF-8 input rejected;
- outside-directory and non-ignored private files rejected;
- malformed commit hash and stage mismatch rejected;
- free-form text rejected;
- token, Windows path, Unix path, and local/private address shapes rejected;
- public errors do not echo private values or paths.
```

All tests use synthetic fixed values and temporary directories only. They read
no private configuration and perform no network or device operation.

## Source preflight

Run before any later private manifest exists:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt8b_private_operator_manifest_and_runbook.py
python scripts\validate_v300_rt8_private_operator_manifest.py --check-example
python -m pytest -q backend\tests\test_v300_rt8_private_operator_manifest.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt8b_private_operator_manifest_and_runbook.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

This preflight reads no private manifest.

## Later private validation commands

These command shapes are frozen but are not authorized by RT-8b.

PC stage:

```powershell
python scripts\validate_v300_rt8_private_operator_manifest.py `
  --manifest-json operator_evidence\v300_rt8_pc_android_realtime_acceptance.json `
  --stage pc-windows `
  --minimum-source-head <RT8B_ACCEPTED_COMMIT>
```

Android stage:

```powershell
python scripts\validate_v300_rt8_private_operator_manifest.py `
  --manifest-json operator_evidence\v300_rt8_pc_android_realtime_acceptance.json `
  --stage android `
  --minimum-source-head <RT8B_ACCEPTED_COMMIT>
```

Aggregate stage:

```powershell
python scripts\validate_v300_rt8_private_operator_manifest.py `
  --manifest-json operator_evidence\v300_rt8_pc_android_realtime_acceptance.json `
  --stage aggregate `
  --minimum-source-head <RT8B_ACCEPTED_COMMIT>
```

## Fixed later operator sequence

Every future platform stage must be separately authorized and bounded:

```text
1. Verify exact accepted source commit, main/origin-main sync, and clean trees.
2. Verify all relevant execution switches are closed.
3. Prepare process-local private values without printing them.
4. Start only the recognized local Backend and one target Flutter runtime.
5. Execute only the separately authorized fixed platform controls.
6. Record only strict booleans, counts, fixed enums, and candidate commits.
7. Stop recognized Flutter and Backend processes.
8. Close every real-execution switch.
9. Remove private process values, staged audio, logs, and temporary backups.
10. Validate the ignored private manifest with the fixed validator.
11. Verify no operator evidence is staged, committed, or pushed.
12. Stop for explicit review before any acceptance sync or commit.
```

PC and Android runs remain separate. A pass on one platform does not imply a
pass on the other.

## Protected and unchanged

```text
.gitignore
backend/app/**
all existing backend/tests/**
app/**
vendor/**
backend/.env.example
backend/env_profiles/**
backend/requirements*.txt
dependencies and lockfiles
platform declarations and generated registration
assets
version metadata
release/**
release_notes/**
fixed ZIPs
tags and GitHub Releases
Framework development checkout
historical RT-8a document and gate
historical RT-4 through RT-7 contracts and gates
private environment/token/endpoint/hotkey/model files
operator_evidence/**
```

The only test addition is the new focused RT-8 validator test file. Existing
tests are unchanged.

## RT-8b non-actions

```text
private manifest created: false
private manifest read: false
private configuration read: false
Backend startup: false
Flutter startup: false
microphone permission requested: false
microphone capture: false
audio staging: false
real STT: false
LLM/provider execution: false
real TTS: false
local playback: false
HTTP/network request: false
VTS WebSocket opened: false
physical motion executed: false
screenshot or recording captured: false
RT-8c PC execution: false
RT-8d Android execution: false
RT-8e aggregate acceptance: false
```

## Expected gate state

```text
v300_rt8b_status: implemented-awaiting-review
v300_rt8b_baseline: a3af4fae002c1425fdfb61b46f66e35e2443ad17
v300_rt8b_exact_change_surface: True
v300_rt8b_change_file_count: 10
v300_rt8b_operator_evidence_ignore_rule_exists: True
v300_rt8b_public_example_rejected: True
v300_rt8b_strict_manifest_schema_frozen: True
v300_rt8b_validator_network_free: True
v300_rt8b_validator_provider_free: True
v300_rt8b_validator_microphone_free: True
v300_rt8b_validator_vts_free: True
v300_rt8b_private_manifest_created: False
v300_rt8b_private_manifest_read: False
v300_rt8c_exact_contract_review_ready: True
v300_rt8c_implementation_authorized: False
v300_rt8b_commit_push_authorized: False
```

## Stop rule

After automated verification:

```text
- stop for exact diff and privacy review;
- do not create or read a private manifest;
- do not read private configuration;
- do not start Backend, Flutter, provider, microphone, TTS, playback, or VTS;
- do not start RT-8c, RT-8d, RT-8e, or RT-9;
- do not commit or push without separate explicit approval.
```
