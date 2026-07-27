# Daily Rhythm Companion v3.0.0 goal checklist and small-commit plan

Updated: 2026-07-27

```text
Current released version: v2.1.0 RELEASED / ACCEPTED
Current released metadata: Backend 2.1.0 / Flutter 2.1.0+3
Strategic target: v3.0.0
Current parent phase: RT-2 COMPLETED / ACCEPTED
Current small commit: none
Current implementation step: RT-3 blocked; real STT public runtime is not implemented
Current implementation state: BLOCKED_REAL_STT_NOT_IMPLEMENTED
Completed small commit: RT-2e-c3b COMPLETED / ACCEPTED
Next implementation action: no RT-3 implementation until an accepted real STT public boundary exists
```

## Source of truth

This file is the active v3.0.0 small-commit checklist.

Supporting RT-0 inventories and checks:

```text
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
docs/v300_framework_v520_contract_adoption.md
scripts/check_v300_framework_v520_contract_adoption.py
docs/v300_backend_realtime_normalization.md
scripts/check_v300_backend_realtime_normalization.py
docs/v300_microphone_permission_capture_inventory.md
scripts/check_v300_microphone_permission_capture_inventory.py
docs/v300_microphone_permission_contract.md
scripts/check_v300_microphone_permission_contract.py
docs/v300_microphone_platform_permission_wiring.md
scripts/check_v300_microphone_platform_permission_wiring.py
```

Historical release sources remain immutable:

```text
docs/DRC_v200_goal_checklist_small_commit.md
docs/DRC_v20x_maintenance_checklist.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_record.md
release_notes/v2.0.0.md
release_notes/v2.0.1.md
release_notes/v2.1.0.md
DRC_v2.0.0 / DRC_v2.0.1 / DRC_v2.1.0 tags and GitHub Releases
```

## v3.0.0 goal

```text
Preserve the accepted daily sleep, mood, advice, chat, TTS, character, and
history loop while evolving DRC into a provider-neutral realtime character
runtime demonstration with observable voice-input, streaming response,
voice-output, interruption, capability, and motion lifecycle states.
```

v3.0.0 is not complete merely because individual STT, LLM, TTS, or motion code
exists. The accepted result must coordinate those capabilities through stable
public AI Character Framework boundaries and must remain mock-safe by default.

## Guarding policy

```text
Safe default + documented explicit opt-in + visible execution state.
```

RT-0 must distinguish all of the following:

```text
source exists
discovery probe detected a candidate
public Framework contract is released
DRC adapter is wired
configured execution succeeded
PC/smartphone UI evidence was accepted
```

None of those states may be substituted for another.

## v3.0.0 scope fixed for planning

```text
- App-owned realtime session ID, lifecycle, events, capability, and safe error models.
- Flutter microphone permission and capture through an app-owned abstraction.
- A bounded realtime transport between Flutter and the DRC Backend.
- Stable AI Character Framework public voice-input/realtime session integration.
- Incremental transcript and LLM response handling where the public contract supports it.
- Cancellation, TTS queue control, interruption, and barge-in coordination.
- Listening, transcribing, thinking, responding, speaking, interrupted,
  reconnecting, unavailable, and error presentation states.
- Public motion-event integration and configured Live2D/VTube Studio execution.
- Capability negotiation and degraded operation when one optional component is unavailable.
- Session, event, audio, and artifact limits and cleanup.
- Credential-free fake-session tests and explicit opt-in operator acceptance.
```

## Explicit exclusions

```text
- Always-on microphone or wake-word detection.
- Background continuous recording.
- Persisting raw conversation audio by default.
- Provider-specific STT, LLM, TTS, Live2D, or VTS clients inside DRC.
- Importing AI Character Framework internal modules.
- Adding new sys.path, sys.modules, import-cache, or temporary-CWD workarounds.
- Live2D model creation, rigging, or commercial asset production.
- Multiple simultaneous character conversations.
- Accounts, cloud synchronization, production multi-user hosting, or store publication.
- New Fitbit/Google Health capability work unrelated to realtime orchestration.
- Rewriting any v2.0.0, v2.0.1, or v2.1.0 release artifact or record.
```

## RT-0 split

```text
RT-0a  COMPLETED / ACCEPTED      Inventory current DRC realtime-related code and freeze the v3 planning boundary
RT-0b  COMPLETED / ACCEPTED     Verify released Framework public realtime prerequisites and classify every gap
RT-0c  COMPLETED / ACCEPTED     Reassess released Framework v5.1.0 and accept the remaining realtime block
```

RT-1 through RT-9 remain blocked after RT-0c acceptance until the required Framework
contracts are released and verifiable.

## RT-0a purpose

```text
- Read the actual Backend, Flutter, tests, platform manifests, roadmap, and tasklist.
- Record what is real runtime, what is a guarded request boundary, and what is discovery only.
- Correct the stale tasklist R-1 CURRENT marker without changing its historical accepted record.
- Freeze the RT-0a change and non-change surfaces.
- Add one credential-free source-tree check for the inventory.
- Do not change runtime behavior or claim Framework readiness.
```

## RT-0a inspected implementation surface

Backend:

```text
backend/app/main.py
backend/app/config.py
backend/app/api/voice_input_demo.py
backend/app/models/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
backend/app/api/voice_output_demo.py
backend/app/models/voice_output_demo.py
backend/app/services/voice_output_demo_service.py
backend/app/services/framework_voice_output_adapter.py
backend/app/api/motion_demo.py
backend/app/models/motion_demo.py
backend/app/services/motion_demo_service.py
backend/app/services/motion_boundary_probe.py
backend/app/api/chat.py
backend/app/models/chat.py
backend/app/services/post_advice_chat_service.py
backend/app/services/framework_text_chat_adapter.py
backend/app/services/framework_text_chat_drc_live_reply.py
```

Flutter and platform metadata:

```text
app/pubspec.yaml
app/lib/screens/home_screen.dart
app/lib/services/backend_api_client.dart
app/lib/models/voice_input_demo.dart
app/lib/models/voice_output_demo.dart
app/lib/models/motion_demo.dart
app/lib/models/character_display_presentation.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/audioplayers_voice_output_audio_engine.dart
app/lib/widgets/character_display_card.dart
app/android/app/src/main/AndroidManifest.xml
app/ios/Runner/Info.plist
```

Regression surface:

```text
backend/tests/**
app/test/**
scripts/check_v210_*.py
scripts/check_v20x_*.py
```

## RT-0a current behavior summary

```text
- Backend routing is ordinary FastAPI HTTP request/response; no realtime transport is wired.
- Voice input is a metadata-only guarded boundary and always returns not_started with no transcript.
- Motion is a guarded simulator/probe boundary and never sends motion or opens VTS WebSocket.
- Configured FW text chat uses a full-response ask() path, not DRC streaming orchestration.
- Existing FW adapters still carry project-root/import-context integration workarounds.
- Voice output produces one opaque artifact and Flutter controls local playback only.
- Flutter stop does not cancel Framework synthesis, LLM generation, or a TTS queue.
- Character activity presentation is limited to idle, loading, and speaking.
- No microphone plugin, Android RECORD_AUDIO permission, or iOS microphone usage description exists.
- HomeScreen and the main widget-test file remain large and require extraction before realtime UI growth.
```

Detailed evidence is frozen in `docs/v300_realtime_current_behavior_inventory.md`.

## RT-0a change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
```

## RT-0a explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
release_notes/**
docs/DRC_v200_goal_checklist_small_commit.md
docs/DRC_v20x_maintenance_checklist.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_record.md
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
build_v210_fixed_release_zip_from_head.ps1
release ZIPs, tags, GitHub Releases, and private operator evidence
```

## RT-0a verification

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

RT-0a acceptance result:

```text
- The inventory agrees with the inspected implementation: passed.
- Credential-free RT-0a source-tree gate: passed.
- Backend pytest: 110 passed.
- Flutter tests: 103 passed.
- git diff --check: passed.
- Backend/Flutter runtime and existing tests changed: false.
- Version and immutable release records changed: false.
- Real provider execution, microphone use, and realtime session start: false.
- Diff review and explicit operator approval: passed.
```

## RT-0a stop rule

```text
Do not add microphone dependencies or permissions.
Do not add WebSocket/SSE/audio-upload endpoints.
Do not wire STT, streaming LLM, cancellation, TTS queues, barge-in, or motion execution.
Do not modify AI Character Framework.
RT-0a was marked accepted only after local verification and operator approval.
RT-0a implementation did not start RT-0b; RT-0b becomes current only after RT-0a acceptance.
Historical RT-0a acceptance marker: `RT-0c  PLANNED`.
```

## RT-0b purpose

```text
- Inspect the released AI Character Framework v5.0.0 public host-app surface.
- Freeze the exact released commit and public export inventory used for the review.
- Classify every v3 prerequisite as READY_CURRENT_USE, PARTIAL_BLOCKING,
  MISSING_BLOCKING, or DEFECT_BLOCKING.
- Preserve the accepted v4 text-chat and v5 one-shot voice-output behavior while
  distinguishing it from full realtime readiness.
- Record the accumulated DRC real-app integration feedback and new realtime gaps.
- Make no DRC or Framework runtime change and perform no real provider execution.
```

At RT-0a acceptance, RT-0b was `NOT_STARTED`. RT-0b is now COMPLETED / ACCEPTED after the RT-0a/RT-0b gates, 110 Backend tests, 103 Flutter tests, diff review, and explicit operator approval passed.

## RT-0b released Framework snapshot

```text
Repository: murayan1982/ai-character-framework
Released line: v5.0.0
Inspected public-source commit: 6494da306015c4f714f869b43e773ba51a2478a2
Release implementation commit: a2df57e2e8ed226b7c9e9c72ed68a79c8a48b6db
RT-0b readiness: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
```

Detailed matrix:

```text
docs/v300_framework_realtime_contract_readiness.md
```

Credential-free source-tree gate:

```text
scripts/check_v300_framework_realtime_contract_readiness.py
```

## RT-0b readiness summary

```text
READY_CURRENT_USE:
- full-response public text chat for existing v2.1.0 use;
- one-shot provider-neutral voice-output request/result and opaque handoff.

PARTIAL_BLOCKING:
- text streaming and state/events;
- typed results/public errors across all session types;
- consolidated capability reporting;
- project-root-independent stable factories;
- provider config responsibility;
- session close/dispose.

MISSING_BLOCKING:
- public voice-input/STT session;
- unified realtime session/lifecycle;
- provider-level hard cancellation;
- TTS queue/cancel/flush and barge-in acknowledgement;
- public motion-event/Live2D/VTS adapter;
- installable SDK packaging boundary.

DEFECT_BLOCKING:
- released README uses session.speak(...), while the released implementation
  exposes VoiceOutputSession.create_output(...) and no speak() method.
```

RT-0b records Framework feedback `FW-F1` through `FW-F12`. RT-0c owns their
handoff ordering and the explicit blocked/unblocked acceptance decision.

## RT-0b change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
```

## RT-0b explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
release_notes/**
historical v2.x checklists and release records
AI Character Framework repository/runtime
release ZIPs, tags, GitHub Releases, and private operator evidence
```

## RT-0b verification

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

Accepted RT-0b status:

```text
v300_framework_realtime_contract_readiness_status: completed-accepted
v300_framework_release_snapshot: v5.0.0@6494da306015c4f714f869b43e773ba51a2478a2
v300_framework_public_readiness: blocked-framework-update-required
v300_framework_required_contracts_ready: False
v300_rt0b_drc_runtime_changed: False
v300_rt0b_existing_tests_changed: False
v300_rt0b_framework_runtime_changed: False
v300_rt0b_real_provider_execution: False
v300_rt1_authorization: blocked-pending-rt0c-and-released-fw-update
```

## RT-0b stop rule

```text
Do not modify AI Character Framework in RT-0b.
Do not import Framework internals to replace missing public contracts.
Do not add another DRC method/factory probing layer for realtime features.
Do not add microphone, transport, STT, cancellation, queue, barge-in, or motion runtime.
RT-1 through RT-9 remain blocked after RT-0b implementation and acceptance.
RT-0c must accept the handoff boundary, and a released Framework update must
provide the required public contracts before RT-1 can be authorized.
```

## RT-0c Framework v5.1.0 reassessment

Historical RT-0b decision: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
Historical RT-0b authorization marker: RT-1 authorization: BLOCKED pending RT-0c and a released Framework update
Historical RT-0c pre-implementation marker: RT-0c  CURRENT / NOT_COMPLETED; NOT_STARTED

Current RT-0c state:

```text
RT-0c implementation: COMPLETED / ACCEPTED
Framework release: v5.1.0
Framework tag commit: b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
Host-app foundation: SUBSTANTIALLY_READY_WITH_TRANSITION_GAPS
Realtime decision: BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING
```

Accepted v5.1.0 host-app foundations recorded by RT-0c:

```text
FW-F4 capability snapshot: RESOLVED_V510
FW-F5 provider config ownership: RESOLVED_V510
FW-F7 opaque voice artifact: RESOLVED_V510
FW-F8 public conformance gate: RESOLVED_V510
```

Transition gaps recorded by RT-0c:

```text
FW-F1 package-like import without a published wheel: PARTIAL_V510
FW-F2 factory/method transition surfaces: PARTIAL_V510
FW-F3 typed Text Chat result without universal cross-session result: PARTIAL_V510
FW-F6 lifecycle methods without real provider cleanup proof: PARTIAL_V510
```

Remaining blockers:

```text
FW-F9 public voice-input/STT: MISSING_REALTIME_BLOCKER
FW-F10 unified realtime lifecycle/events: MISSING_REALTIME_BLOCKER
FW-F11 hard cancel/TTS queue/flush/barge-in: MISSING_REALTIME_BLOCKER
FW-F12 public motion/VTS adapter: MISSING_REALTIME_BLOCKER
```

RT-1 through RT-5 remain blocked until released public voice-input, realtime,
and cancellation/queue contracts are verifiable. RT-6 through RT-7 remain
blocked until a released public motion contract is verifiable. RT-8 through
RT-9 remain blocked by their prerequisite runtime phases.

Detailed contract:

```text
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
```

RT-0c change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
```

RT-0c explicit non-change surface:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
release_notes/**
historical v2.x checklists and release records
AI Character Framework repository/runtime
```

RT-0c verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python scripts\check_v300_framework_v510_reassessment.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

Expected accepted marker:

```text
v300_framework_v510_reassessment_status: completed-accepted
v300_framework_release_snapshot: v5.1.0@b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
v300_framework_realtime_prerequisites_ready: False
v300_rt1_authorization: blocked-pending-released-voice-input-realtime-cancel-contracts
v300_rt6_authorization: blocked-pending-released-motion-contract
```

RT-0c stop rule:

```text
Do not start RT-1 after RT-0c acceptance until a later Framework release
provides the missing public contracts. Do not migrate the existing DRC runtime
adapter in this docs/test-only commit. Do not add another import or method probe.
```

## RT-1 split after Framework v5.2.0 release

```text
RT-1a  COMPLETED / ACCEPTED
       Verified the released v5.2.0 mock-safe public contracts and authorized the
       bounded DRC integration surface.

RT-1b  COMPLETED / ACCEPTED
       Adds Backend-only DRC realtime state/event/capability/session models and a
       Framework-contract normalizer. No API route or provider execution.
```

RT-1a decision:

```text
RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED
```

The released v5.2.0 root exports public Voice Input, Realtime, interrupt/output
control, and Motion contracts. Their real provider/runtime implementations are
not complete. RT-1 may begin with model and mock-contract integration only.

Phase boundaries after RT-1a acceptance:

```text
RT-1: COMPLETED / ACCEPTED
RT-2: CURRENT / NOT_COMPLETED; RT-2a COMPLETED / ACCEPTED; RT-2b NOT_STARTED; microphone access NOT_STARTED
RT-3: BLOCKED_REAL_STT_NOT_IMPLEMENTED
RT-4: BLOCKED_REAL_STREAMING_CANCEL_NOT_IMPLEMENTED
RT-5: BLOCKED_REAL_OUTPUT_CONTROL_NOT_IMPLEMENTED
RT-6: PLANNED_AFTER_RT1; mock motion contract available
RT-7: BLOCKED_REAL_MOTION_ADAPTER_NOT_IMPLEMENTED
RT-8 through RT-9: BLOCKED by prerequisites
```

Detailed contract:

```text
docs/v300_framework_v520_contract_adoption.md
scripts/check_v300_framework_v520_contract_adoption.py
docs/v300_backend_realtime_normalization.md
scripts/check_v300_backend_realtime_normalization.py
```



## RT-1b implementation checkpoint

```text
Implementation state: COMPLETED / ACCEPTED
Backend models added: true
Framework-contract normalizer added: true
Focused Backend tests: 6 passed in local implementation verification
Full Backend tests: 116 passed in local implementation verification
Framework import: false
API route added: false
microphone used: false
realtime runtime started: false
Provider execution: false
Flutter runtime changed: false
```

RT-1b was accepted on 2026-07-26 after compileall, the RT-1b source/runtime
gate, focused Backend 6, full Backend 116 with one existing warning, Flutter 103,
`git diff --check`, 10-file diff review, and explicit operator approval passed.
Parent RT-1 is COMPLETED / ACCEPTED. RT-2 is CURRENT / NOT_COMPLETED but remains
NOT_STARTED until its guarded permission/capture small-commit split is accepted.

## RT-2 small-commit split

```text
RT-2a  COMPLETED / ACCEPTED
       Current Flutter/platform permission and capture inventory; docs/test-only.
RT-2b  COMPLETED / ACCEPTED
       DRC-owned permission state/result and gateway interface with fake gateway.
RT-2c  COMPLETED / ACCEPTED
       Android/iOS permission adapter and declarations; no UI invocation or capture.
RT-2d  COMPLETED / ACCEPTED
       Capture lifecycle/controller and deterministic fake engine; no microphone access.
RT-2e  CURRENT / NOT_COMPLETED
  RT-2e-a  COMPLETED / ACCEPTED
             Exact-surface and record 6.2.1 readiness; docs/test-only.
  RT-2e-b  COMPLETED / ACCEPTED
             Pinned record adapter/private temporary artifact boundary; fake tests only.
  RT-2e-c  CURRENT / NOT_COMPLETED
             NOT_STARTED; explicit operator real-device bounded capture evidence.
```

RT-2a inspected the actual source and confirmed:

```text
Flutter microphone/permission/capture dependency: absent
Android RECORD_AUDIO: absent
iOS NSMicrophoneUsageDescription: absent
Web/desktop microphone adapter: absent
App-owned microphone permission gateway: absent
App-owned capture engine/controller: absent
Current voice-input UI: metadata-only backend request
Current Backend voice-input route: no audio body and no STT execution
```

Safety contract for later RT-2 children:

```text
explicit user action only
safe default disabled/unavailable
typed denied/permanently-denied/restricted/unsupported/error states
single active capture
hard bounded duration and explicit stop/cancel
no always-on or background recording
no raw audio persistence by default
cleanup after completion/cancel/error
no STT/provider upload before RT-3 authorization
```

RT-2a was accepted on 2026-07-26 after compileall, the RT-1b and RT-2a gates, Backend 116 with one existing warning, Flutter 103, `git diff --check`, seven-file diff review, and explicit operator approval passed.

RT-2a protected results:

```text
Backend runtime changed: false
Flutter runtime changed: false
Existing tests changed: false
Microphone dependency added: false
Android RECORD_AUDIO added: false
iOS microphone usage added: false
Microphone accessed: false
Audio captured: false
```

## Historical accepted marker compatibility

The following strings are retained only so the accepted RT-0b/RT-0c source-tree
checks continue to validate their historical checkpoints. They do not describe
the active RT-1a state.

```text
Historical RT-0c parent marker: Current parent phase: RT-0 COMPLETED / ACCEPTED
Historical RT-0c terminal marker: Current small commit: none
Historical RT-0c completion marker: Completed small commit: RT-0c COMPLETED / ACCEPTED
Historical RT-0b planning marker: RT-1   BLOCKED
```

## RT-2b app-owned permission contract and fake gateway

Implementation state: COMPLETED / ACCEPTED

Changed runtime/test files:

```text
app/lib/services/microphone_permission.dart
app/test/microphone_permission_test.dart
```

Contract additions:

```text
status: unknown, granted, denied, permanentlyDenied, restricted, unsupported, failed
operation: check, request, openSettings
result: safe message, technical code, request/settings affordances, immutable public metadata
gateway: checkPermission, requestPermission, openAppSettings
fake: deterministic request sequence and call counters; no OS side effect
```

Protected boundaries:

```text
permission/capture dependency added: false
Android RECORD_AUDIO added: false
iOS NSMicrophoneUsageDescription added: false
MethodChannel or browser media API added: false
HomeScreen/voice-input UI changed: false
Backend changed: false
Framework imported: false
platform permission requested: false
microphone accessed: false
audio captured or persisted: false
provider/STT called: false
```

Acceptance completed on 2026-07-26 after compileall, the RT-2b source gate,
focused Flutter 9, full Flutter 112, Backend 116 with one existing warning,
`git diff --check`, nine-file review, gate portability fixes, and explicit operator approval passed.
RT-2c is COMPLETED / ACCEPTED on 2026-07-27 at implementation commit `fe26c3c`. The mobile gateway, platform declarations, resolved lockfile, generated Windows registration, analyzer cleanup, tests, gate, Android debug APK build, and 16-file review were accepted. RT-2d is COMPLETED / ACCEPTED after fake-only lifecycle verification; RT-2e is CURRENT / NOT_COMPLETED and NOT_STARTED.


## RT-2c mobile platform permission wiring without capture

Implementation state: COMPLETED / ACCEPTED

Changed runtime/test files:

```text
app/pubspec.yaml
app/pubspec.lock (generated by operator flutter pub get)
app/android/app/src/main/AndroidManifest.xml
app/ios/Runner/Info.plist
app/windows/flutter/generated_plugin_registrant.cc (generated by operator flutter pub get)
app/windows/flutter/generated_plugins.cmake (generated by operator flutter pub get)
app/lib/services/permission_handler_microphone_permission_gateway.dart
app/test/permission_handler_microphone_permission_gateway_test.dart
```

Implemented boundary:

```text
permission_handler 12.0.3 pinned
Android RECORD_AUDIO declared once
iOS NSMicrophoneUsageDescription declared
Android/iOS-only real permission gateway
web/desktop unsupported short-circuit
DRC-owned typed status/error normalization
injected fake driver focused tests
```

Protected boundaries:

```text
startup/HomeScreen invocation: false
platform permission request executed during tests: false
microphone opened/accessed: false
audio captured/persisted/uploaded: false
capture package added: false
Backend changed: false
Framework/provider/STT execution: false
RT-2d authorization: authorized-capture-lifecycle-and-fake-engine-only
```

Acceptance completed on 2026-07-27 after `flutter pub get`, exact generated
Windows plugin-registration review, `flutter analyze` with no issues, focused
Flutter 13, full Flutter 125, Backend 116 with one existing warning, the RT-2c
source/platform gate, Android debug APK build, `git diff --check`, 16-file review,
and operator acceptance evidence passed. The Android build emitted a Kotlin
daemon incremental-cache warning in `audioplayers_android`, then completed via
Gradle fallback and produced `app-debug.apk`. iOS build execution was not
available on the Windows operator environment and is not claimed.

## RT-2d capture lifecycle contract and fake engine

Implementation state: COMPLETED / ACCEPTED

Implemented scope: DRC-owned lifecycle/request/result/controller contracts, a
deadline scheduler boundary, and a deterministic fake capture engine. Single
active capture, hard bounded duration, stop/cancel/timeout/error/close cleanup,
and typed denied/permanently-denied/restricted/unsupported/busy/timeout states
are fixed before any real adapter. UI wiring, platform capture packages,
microphone access, raw audio, upload, Framework/provider calls, and STT remain
forbidden.

Changed runtime/test files:

```text
app/lib/services/microphone_capture.dart
app/test/microphone_capture_test.dart
```

Protected evidence:

```text
permission request executed: false
real capture dependency added: false
UI/platform/Backend changed: false
microphone accessed: false
audio captured/persisted/uploaded: false
raw audio bytes/path/handle exposed: false
RT-2e authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only
```

Acceptance completed on 2026-07-27 after compileall, the RT-2d source/surface
gate, `flutter analyze` with no issues, focused Flutter 17, full Flutter 142,
Backend 116 with one existing warning, `git diff --check`, nine-file review, and
explicit operator approval passed. No permission request, microphone access,
audio capture, raw-audio exposure, upload, provider call, or STT execution occurred.

## RT-2e explicitly guarded bounded real capture adapter

Parent state: CURRENT / NOT_COMPLETED
Authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only

### RT-2e-a exact-surface and recorder-package readiness

Implementation state: COMPLETED / ACCEPTED

Exact accepted code review confirms Dart `^3.11.5`, no direct recorder or path
provider dependency, accepted RT-2d controller/fake engine, and existing mobile
permission declarations. `record` 7.x is not compatible with the current Dart
baseline. RT-2e-b selects `record` 6.2.1, the compatible final pre-7 line.

`startStream` is forbidden because it exposes raw bytes. A later concrete
adapter may use file mode only with a private temporary path/artifact registry;
public DRC results remain opaque. Permission ownership stays in the existing
DRC permission gateway.

RT-2e-a is docs/test-only and does not add dependencies, change generated plugin
registrations or platform files, request permission, access a microphone,
capture/create/upload audio, expose bytes/path/handles, or execute STT.
Acceptance completed on 2026-07-27 after compileall, the RT-2e-a gate,
`flutter analyze` clean, full Flutter 142, Backend 116 with one existing
warning, `git diff --check`, seven-file review, and explicit operator
approval passed.

### RT-2e-b record adapter and private temporary artifact boundary

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; fake-only verification boundary added

Pinned direct dependencies are `record` 6.2.1 and `path_provider` 2.1.6.
The adapter uses injectable recorder/private-filesystem boundaries, WAV file
mode at 16 kHz mono, an opaque capture id, and private temporary artifact
cleanup. `startStream` and public raw bytes/path/handles are forbidden.

The production package driver is compiled but not connected to startup/UI and
is not instantiated by tests. Real permission request, no real microphone
access, real audio capture, upload, provider execution, and STT remain absent.
Acceptance completed on 2026-07-27 after operator dependency resolution, generated
plugin review, analyzer cleanup, focused Flutter 18/18, full Flutter 161, Backend
116 with one existing warning, the RT-2e-b gate, Android debug APK compilation,
`git diff --check`, 19-file review, and explicit operator approval. The Kotlin
incremental-cache daemon reported a cross-drive cache error before Gradle
fallback produced the APK. No app launch, permission request, microphone access,
or audio capture occurred.

### RT-2e-c explicit operator real-device capture evidence

State: CURRENT / NOT_COMPLETED
Authorization: authorized-explicit-opt-in-real-device-bounded-capture-evidence-only

#### RT-2e-c1 operator-only harness/readiness contract

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; docs/test-only

The accepted `5a7f814` source surface was reread before implementation. The
later operator harness must use a separate `lib/main_rt2ec_operator.dart`
entrypoint, require `--dart-define=DRC_RT2EC_OPERATOR=true`, and require an
in-app acknowledgement. The normal `lib/main.dart` and `HomeScreen` remain
unchanged.

Permission check, permission request, start, stop, and cancel are separate
explicit user actions. Start requires granted permission. Capture remains
single-active and is capped at 15 seconds using WAV 16 kHz mono file mode. Stop
must immediately discard the private artifact through its opaque id. Safe
evidence is allowlisted to status/code/booleans/duration/cleanup and must not
contain private paths, raw bytes, audio content, transcript content, Backend
payloads, Framework/provider payloads, or STT results.

This checkpoint changed docs and a source/surface gate only. It added no Flutter
runtime, dependency, generated plugin, platform, UI, or Backend change and did
not execute permission request, microphone access, audio capture, upload, or
STT. Acceptance followed compileall, the RT-2e-c1 gate, Backend 116 with one
existing warning, `flutter analyze`, full Flutter 161, `git diff --check`, exact
eight-file review, and explicit operator approval.

#### RT-2e-c2 operator-only harness and fake/widget tests

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED
Authorization: completed-accepted-fake-widget-only

The separate `main_rt2ec_operator.dart` target now fails closed without
`DRC_RT2EC_OPERATOR=true`, requires an in-app acknowledgement before invoking
the production dependency factory, and exposes permission check/request plus
capture start/stop/cancel as separate actions. Start is granted-only and bounded
to 15 seconds. Completed artifacts are immediately discarded by opaque id and
only safe evidence fields are rendered. Fake/widget tests cover the double
opt-in, no-startup-action boundary, bounded request, discard, cancel, and exact
allowlist. This stage performed no real permission request, microphone access, or audio
capture. Acceptance followed compileall, the RT-2e-c2 gate, Backend 116 with one
existing warning, `flutter analyze`, focused Flutter 10, full Flutter 171,
`git diff --check`, exact twelve-file review, and explicit operator approval.

#### RT-2e-c3 real Android bounded capture and cleanup evidence

State: CURRENT / NOT_COMPLETED

##### RT-2e-c3a real Android operator preflight and safe evidence contract

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; docs/test-only
Authorization: completed-docs-test-only-preflight

The accepted `b2e2adb` source archive with SHA-256
`18d39ea0676bcd3213c104a71fd5ce2c096c6b96002eb7aaef7ceccd06a2fd86`
was reread before real-device execution. The contract requires one physical
Android device, the separate `main_rt2ec_operator.dart` target,
`DRC_RT2EC_OPERATOR=true`, in-app acknowledgement, explicit permission
check/request, and one non-sensitive capture stopped before the 15-second hard
limit.

Completed evidence is marker-only. It may contain the accepted safe panel
status/code/boolean/duration fields and the clean source commit. It must not
contain device serial/model, private path, opaque capture id, raw audio, audio
content, transcript, provider payload, raw platform error, or raw screenshot.
The completed artifact must be registered and immediately discarded, with
cleanup succeeded. Backend upload, Framework/provider execution, and STT are
forbidden.

This checkpoint changed documentation and one source/surface gate only. It did
not run Flutter, connect a device, request permission, access a microphone,
capture audio, create private evidence, upload audio, or execute STT. Acceptance
passed with compileall, the RT-2e-c3a gate, Backend 116 with the existing warning,
`flutter analyze`, full Flutter 171, `git diff --check`, exact ten-file review,
and explicit operator approval.

##### RT-2e-c3b explicit real Android bounded capture and cleanup evidence

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; marker-only real Android evidence
Authorization: completed-accepted-explicit-real-android-bounded-capture-evidence

Run the explicit operator target from the clean accepted RT-2e-c3a commit on
one physical Android device. Accept only granted permission,
request attempted, completed capture, duration 1..15000 ms, microphone/audio
true, raw audio exposed false, private artifact registered/discarded true, and
cleanup succeeded true. Keep all private evidence and audio outside commits. No
Backend upload or STT execution.


RT-2e-c3b accepted marker summary:

```text
source commit: ddae21944ac0e251cd8194bf93982bd5dc7a4ae8
physical Android: true
operator target enabled: true
acknowledgement completed: true
permission granted/request attempted: true/true
capture completed: true
requested/captured duration ms: 15000/4820
microphone/audio: true/true
raw audio exposed: false
private artifact registered/discarded: true/true
cleanup succeeded: true
Backend/upload/STT: false/false/false
private path/opaque id/device identifier/raw audio/raw screenshot committed: false
post-run working tree clean: true
```

An earlier non-acceptance dry run confirmed cleanup but did not retain the
duration marker. The accepted marker is from the later single-capture acceptance
session. RT-2 is now COMPLETED / ACCEPTED. RT-3 remains
`BLOCKED_REAL_STT_NOT_IMPLEMENTED`.
