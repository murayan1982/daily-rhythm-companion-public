# Daily Rhythm Companion v3.0.0 goal checklist and small-commit plan

Updated: 2026-07-26

```text
Current released version: v2.1.0 RELEASED / ACCEPTED
Current released metadata: Backend 2.1.0 / Flutter 2.1.0+3
Strategic target: v3.0.0
Current parent phase: RT-0 CURRENT / NOT_COMPLETED
Current small commit: RT-0b CURRENT / NOT_COMPLETED
Current implementation step: released Framework public realtime readiness review
Current implementation state: NOT_STARTED
Completed small commit: RT-0a COMPLETED / ACCEPTED
Next acceptance action: inspect released Framework public APIs and record the RT-0b readiness matrix without changing DRC or Framework runtime
```

## Source of truth

This file is the active v3.0.0 small-commit checklist.

Supporting RT-0a inventory:

```text
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
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
RT-0b  CURRENT / NOT_COMPLETED   Verify released Framework public realtime prerequisites and classify every gap
        NOT_STARTED
RT-0c  PLANNED                   Accept the blocked/unblocked decision and freeze the DRC-to-FW handoff boundary
```

RT-1 through RT-9 remain blocked until RT-0c accepts that the required Framework
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
```

## Current RT-0b output

RT-0b is CURRENT / NOT_COMPLETED and NOT_STARTED. It will inspect the released AI Character Framework public surface and classify:

```text
voice-input/STT session
realtime lifecycle/event model
streaming result model
hard cancellation and interruption
TTS queue/output control
motion-event/VTS adapter
provider-neutral capability report
typed results and public errors
installable/project-root-independent import
session close/dispose
```

The review will use released/verifiable public APIs only. Framework internals or
unreleased source candidates cannot unblock DRC.
