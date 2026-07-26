# v3.0.0 realtime current behavior inventory

Updated: 2026-07-26

```text
Small commit: RT-0a
Status: COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED
Runtime changed: false
Existing tests changed: false
Version metadata changed: false
Release records changed: false
Real provider execution: false
Microphone used: false
Realtime session started: false
```

## Purpose

This document records the current DRC implementation before any v3.0.0 runtime
change. It was produced by reading the actual Backend, Flutter, tests, platform
metadata, roadmap, and tasklist. It separates accepted v2.1.0 behavior from
metadata-only boundaries, source discovery, and future realtime work.

This inventory does not claim that a capability is connected merely because a
route, model, probe, file, or UI section exists.

## Released baseline

```text
Current release: v2.1.0 RELEASED / ACCEPTED
Backend metadata: 2.1.0
Flutter metadata: 2.1.0+3
Accepted Backend test baseline: 110 passed
Accepted Flutter test baseline: 103 passed
Fixed ZIP: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
Fixed ZIP SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
```

RT-0a does not modify or rebuild this release.

## Files inspected

### Backend application and adapters

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

### Flutter application and platform metadata

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

### Regression and planning surfaces

```text
backend/tests/**
app/test/**
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_record.md
scripts/check_v210_*.py
scripts/check_v20x_*.py
```

## 1. Current Backend transport

`backend/app/main.py` registers ordinary FastAPI routers for health, advice,
chat, voice-input demo, voice-output demo, motion demo, Fitbit, and Google
Health.

The inspected application has no DRC-owned:

```text
WebSocket route
Server-Sent Events route
StreamingResponse route
multipart audio-upload route
realtime session route
client event cursor or sequence contract
heartbeat or reconnect endpoint
cancel/interrupt endpoint
```

The current Flutter `BackendApiClient` uses request/response HTTP calls for the
voice-input, voice-output, motion, and chat APIs. No WebSocket, EventSource, or
streaming transport is wired.

Conclusion:

```text
realtime transport state: NOT_IMPLEMENTED
```

## 2. Voice input / STT boundary

Current files:

```text
backend/app/api/voice_input_demo.py
backend/app/models/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
app/lib/models/voice_input_demo.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
```

The Backend intentionally performs a no-import source-tree probe for likely
Framework voice/realtime/audio files and public symbol candidates. The POST
request is metadata-only.

The response contract remains:

```text
accepted: false
request_state: not_started
transcript: null
```

The service explicitly does not:

```text
import Framework audio runtime
open a microphone
read audio_reference
read an audio file
process audio bytes
execute speech recognition
start a realtime session
```

Flutter exposes the guarded request/status UI, but it does not capture audio.

`app/pubspec.yaml` contains no microphone recording or permission dependency.
The Android main manifest contains no `android.permission.RECORD_AUDIO`, and the
iOS Info.plist contains no `NSMicrophoneUsageDescription`.

Conclusion:

```text
voice-input discovery/probe: IMPLEMENTED
voice-input request contract: IMPLEMENTED, METADATA_ONLY
microphone permission: NOT_IMPLEMENTED
microphone capture: NOT_IMPLEMENTED
real STT execution: NOT_IMPLEMENTED
incremental transcript: NOT_IMPLEMENTED
```

## 3. LLM/chat boundary

The accepted post-advice chat lifecycle provides bounded process-local sessions,
TTL/capacity/LRU, turn limits, structured terminal outcomes, and Flutter
recovery UI.

Configured Framework execution uses the public `create_text_chat_session`
boundary, then obtains a full reply through `ask(prompt)`. DRC does not currently
consume Framework response chunks or Framework session events as a realtime
orchestration stream.

The current adapter path also includes external-checkout integration workarounds:

```text
FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT
signature inspection
sys.path manipulation through the import setup boundary
defensive sys.modules/cache handling
temporary CWD change around session creation/use
```

These were sufficient for the accepted v2.x configured demo but are not the
basis for a new v3 realtime adapter.

Conclusion:

```text
bounded post-advice chat: IMPLEMENTED / ACCEPTED
configured full-response Framework chat: IMPLEMENTED / ACCEPTED
DRC incremental LLM streaming: NOT_IMPLEMENTED
provider-level hard cancellation: NOT_IMPLEMENTED
unified realtime event consumption: NOT_IMPLEMENTED
project-root-independent Framework SDK use: NOT_IMPLEMENTED
```

## 4. Voice output and playback boundary

The accepted v2.1.0 path provides:

```text
explicit guarded Framework voice-output request
one provider-neutral output result
DRC-owned opaque MP3 artifact URL
24-hour / 100-artifact retention defaults
Flutter in-app load, play, stop, replay, completion, failure, expiry, regenerate
```

`VoiceOutputAudioPlayerController.stop()` stops the local Flutter audio engine.
It does not cancel a Framework synthesis call, LLM response generation, a queued
utterance, or any Backend realtime session.

The current Backend adapter creates one output request at a time. No DRC-owned
TTS queue, utterance sequence, synthesis cancellation token, or barge-in
coordination exists.

The voice-output adapter still imports an external Framework checkout through a
temporary import context with `sys.path`, `sys.modules`, and import-cache
handling.

Conclusion:

```text
single voice artifact generation: IMPLEMENTED / ACCEPTED
in-app artifact playback: IMPLEMENTED / ACCEPTED
local playback stop: IMPLEMENTED / ACCEPTED
TTS request queue: NOT_IMPLEMENTED
Framework synthesis cancel/interrupt: NOT_IMPLEMENTED
barge-in coordination: NOT_IMPLEMENTED
```

## 5. Character presentation state

`CharacterDisplayPresentation` currently resolves content and fallback state and
uses only three activity states:

```text
idle
loading
speaking
```

It does not yet model:

```text
requesting_permission
capturing
listening
transcribing
thinking
streaming_response
queueing_speech
interrupt_requested
interrupted
reconnecting
realtime_error
```

The extracted `CharacterDisplayCard` is a useful v2.1.0 foundation, but realtime
state ownership and UI integration do not yet exist.

Conclusion:

```text
static deterministic character presentation: IMPLEMENTED / ACCEPTED
realtime character state model: NOT_IMPLEMENTED
```

## 6. Motion / Live2D / VTube Studio boundary

Current files:

```text
backend/app/api/motion_demo.py
backend/app/models/motion_demo.py
backend/app/services/motion_demo_service.py
backend/app/services/motion_boundary_probe.py
app/lib/models/motion_demo.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
```

The Backend safely probes configured Framework checkout shape and returns a
simulator/request-contract result. The request does not import Framework motion
runtime, load a Live2D model, open a VTube Studio WebSocket, or send a motion.

The response remains conservative:

```text
accepted: false
request_state: not_started
motion_sent: false
vts_connection_used: false
```

Flutter displays a lightweight static expression simulator and the request
boundary. It does not own or connect a Live2D/VTS runtime.

Conclusion:

```text
motion discovery/probe: IMPLEMENTED
motion request contract and static simulator: IMPLEMENTED
public Framework motion adapter: NOT_IMPLEMENTED
real VTS WebSocket execution: NOT_IMPLEMENTED
real Live2D runtime execution: NOT_IMPLEMENTED
```

## 7. Capability and execution-state boundary

The existing demo-status surfaces distinguish several safe states such as
configured, unavailable, skipped, blocked, fallback, and successful execution.
They are useful input for v3.

However, there is no single realtime capability object that negotiates the
combined availability of:

```text
microphone capture
STT
incremental LLM
hard cancellation
TTS queue/interruption
motion adapter
reconnect
session close/dispose
```

Conclusion:

```text
component demo capability status: IMPLEMENTED
provider-neutral realtime capability negotiation: NOT_IMPLEMENTED
```

## 8. Lifecycle, cleanup, and concurrency

Accepted v2.x lifecycle limits include:

```text
post-advice chat: 30-minute idle TTL / 100 sessions / 8-turn default
voice artifacts: 24-hour publish TTL / 100 artifact default
```

There is no realtime session store, event buffer, audio-frame buffer, disconnect
cleanup, heartbeat timeout, cancellation ownership, or stale-event rejection
contract.

Conclusion:

```text
chat/artifact bounded lifecycle: IMPLEMENTED / ACCEPTED
realtime lifecycle and cleanup: NOT_IMPLEMENTED
```

## 9. Flutter size and extraction debt

At the inspected baseline:

```text
app/lib/screens/home_screen.dart: 4161 lines
app/test/widget_test.dart: 2753 lines
app/lib/services/backend_api_client.dart: 549 lines
```

V-1 successfully extracted the static character card and deterministic
presentation model, and T-1 isolated the audio engine/controller. HomeScreen
still owns voice-input demo, voice-output demo, motion demo, advice/chat, and
large portions of the daily loop.

Realtime work must introduce app-owned controllers/models/widgets rather than
adding microphone, transport, cancellation, and motion lifecycle directly to
HomeScreen.

## 10. Planning conclusion

The current DRC source provides valuable accepted building blocks:

```text
mock-safe defaults
explicit real-execution gates
structured chat lifecycle outcomes
opaque TTS artifact handoff
in-app playback controller
static character presentation extraction
voice-input and motion discovery/request boundaries
PC/smartphone Web acceptance discipline
```

It does not yet provide a realtime runtime. The v3.0.0 implementation must not
reinterpret existing discovery-only boundaries as connected execution.

RT-0a conclusion:

```text
DRC current behavior inventory: COMPLETED / ACCEPTED
Framework realtime readiness: NOT_EVALUATED_BY_RT-0a
Current next small commit: RT-0b CURRENT / NOT_COMPLETED; NOT_STARTED
RT-1 implementation authorization: BLOCKED_PENDING_RT-0b_AND_RT-0c
```

## v3.0.0 purpose fixed by RT-0a

```text
Preserve the accepted daily companion flow and add a provider-neutral,
observable, bounded realtime character session that coordinates microphone/STT,
LLM response, voice output, interruption, and public motion events through
stable released AI Character Framework contracts.
```

## Scope fixed by RT-0a

```text
- Realtime session/state/event/capability/error models.
- Microphone permission and guarded capture abstraction.
- Bounded Flutter-to-Backend realtime transport.
- Framework public voice-input/realtime integration.
- Incremental transcript/response where supported.
- Cancellation, TTS queue, interruption, and barge-in.
- Character and motion synchronization.
- Degraded capability handling.
- Cleanup, test, operator evidence, and release readiness.
```

## Exclusions fixed by RT-0a

```text
- Always-on listening, wake word, and background continuous recording.
- Raw audio persistence by default.
- Provider clients or Framework internals inside DRC.
- New import/CWD/cache workarounds.
- Live2D asset production.
- Accounts, cloud sync, production hosting, or store distribution.
- Unrelated health-provider feature expansion.
- Any rewrite of released v2.x artifacts.
```

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

## Explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
version metadata
release_notes/**
historical v2.x checklists and release records
release builders, fixed ZIPs, tags, and GitHub Releases
```

## Acceptance record

```text
Acceptance date: 2026-07-26
compileall: passed
RT-0a source-tree gate: passed
Backend pytest: 110 passed
Flutter test: 103 passed
git diff --check: passed
runtime changed: false
existing tests changed: false
real provider execution: false
microphone used: false
realtime session started: false
diff review / explicit operator approval: passed
```

RT-0a is completed and accepted. RT-0b is the next current small commit but is
not started by this inventory acceptance record. RT-1 remains blocked pending
RT-0b and RT-0c.

## Verification boundary

The RT-0a check is credential-free and source-tree-only. It validates the
inventory markers, the corrected active task state, representative code
contracts, absence of microphone permissions/dependencies, and normalized tree
hashes for runtime/test/release surfaces.

It does not:

```text
import AI Character Framework
read private env files
call providers or network
open a microphone
start Flutter or a browser
start a realtime session
modify runtime or release records
```
