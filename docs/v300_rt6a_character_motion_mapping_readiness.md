# Daily Rhythm Companion v3.0.0 RT-6a character-motion mapping readiness

Updated: 2026-08-01

## Status

```text
RT-5: COMPLETED / ACCEPTED
RT-5f: COMPLETED / ACCEPTED
RT-5f4 acceptance sync: COMPLETED / ACCEPTED / PUSHED
RT-5f4 acceptance-sync commit: ca1bd17ed32aba1e6b7d4dfd4f8eea3f10652ef7
RT-6: CURRENT / NOT_COMPLETED
RT-6a: IMPLEMENTED / AWAITING_REVIEW
RT-6b through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
DRC baseline HEAD/origin: ca1bd17ed32aba1e6b7d4dfd4f8eea3f10652ef7
FW v5.4.0 HEAD/tag: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-6a freezes the actual accepted DRC and released FW v5.4.0 behavior before
adding realtime character presentation or motion-event mapping. The checkpoint
is documentation/static-gate only. It separates existing static presentation,
existing metadata-only motion-demo endpoints, available FW mock-safe public
contracts, missing DRC mapping/controller work, and unavailable real
Live2D/VTube Studio execution.

## Inspected DRC source

```text
backend/app/api/motion_demo.py
backend/app/models/motion_demo.py
backend/app/services/motion_demo_service.py
backend/app/services/motion_boundary_probe.py
backend/app/models/realtime.py
backend/app/services/framework_realtime_normalizer.py
app/lib/models/character_display_presentation.dart
app/lib/widgets/character_display_card.dart
app/lib/services/voice_output_audio_player.dart
app/lib/models/realtime_text_stream.dart
app/lib/services/realtime_text_stream_controller.dart
app/lib/services/integrated_voice_turn_home_screen_binding.dart
```

## Existing Backend motion-demo boundary

The Backend exposes `GET /demo/motion/status` and `POST /demo/motion`. The
service has an application-owned vocabulary:

```text
greeting
thinking
happy
tired_supportive
speaking
idle
```

It normalizes request metadata and reports capability status, but does not send
a motion command. Current request responses remain conservative:

```text
accepted: false
request_state: not_started
motion_sent: false
vts_connection_used: false
```

The service intentionally does not import FW motion modules, connect to VTube
Studio, load Live2D runtime dependencies, read tokens, or send expressions.
No current DRC route constitutes a realtime lifecycle-to-motion transport.

## Existing Flutter character presentation

Flutter already resolves static mood/advice/fallback content and local display
activity. The current activity states are:

```text
idle
loading
speaking
```

`VoiceOutputPlaybackPhase.playing` resolves to `speaking`. This is a UI/local
playback presentation rule. It is not an FW motion event, an animation command,
or a realtime lifecycle mapping. There is no current motion request/result
model, motion client, ChangeNotifier motion controller, stale motion-request
handling, or HomeScreen motion-session ownership.

## Released FW v5.4.0 public motion boundary

The root package exports the provider-neutral motion types and factory:

```text
MotionAdapterStatus
MotionCapability
MotionErrorCode
MotionEventType
MotionIntent
MotionOutcome
MotionRequest
MotionResult
MotionState
MotionSession
MotionSessionInfo
create_motion_session
```

The public intent vocabulary is:

```text
expression
emotion
speaking_state
idle_motion
gesture
look_at
stop_motion
reset_expression
```

The mock adapter is local and credential-free. It supports expression,
emotion, speaking-state, gesture, look-at, and stop-motion capability markers.
Public event callbacks emit public-safe metadata and redact secret-like keys.

The released real adapter boundary remains unavailable:

```text
real_adapter_supported: false
real Live2D / VTS connection: not implemented
VTS WebSocket: not opened
VTS token: not read
Live2D model/runtime: not loaded
provider SDK: not imported by the public mock session
```

## Vocabulary mapping gap

DRC event labels such as `thinking` and `tired_supportive` are not FW
`MotionIntent` values. They must never be forwarded as accidental provider or
adapter identifiers. RT-6b must own a pure provider-neutral mapping contract
from accepted DRC realtime/voice-output lifecycle facts to bounded app motion
requests.

Candidate input facts for RT-6b planning:

```text
listening
transcribing
thinking
responding
TTS preparing
TTS speaking
soft-barge-in / interrupted
completed
failed
idle
```

Candidate normalized outputs for separate exact review:

```text
expression
emotion
speaking_state
idle_motion
stop_motion
reset_expression
```

RT-6a does not approve a concrete mapping table or add runtime code.

## Readiness decision

```text
READY_FOR_RT6_APP_OWNED_MOCK_SAFE_MAPPING_WORK
BLOCKED_FOR_REAL_LIVE2D_VTS_EXECUTION
```

DRC may proceed in small commits using app-owned pure mapping and the FW
root-public mock session only. No Framework internal import, DRC custom VTS
client, direct provider execution, token handling, or real adapter claim is
authorized.

## Exact RT-6 split

### RT-6a — current behavior inventory, readiness, and exact split

Docs/static-gate only. Freeze current source facts, root-public semantics,
exact surface, child ownership, privacy boundary, and stop rules.

### RT-6b — app-owned provider-neutral motion mapping contract

Add a pure, deterministic mapping layer with bounded app-owned request models
and fake-only tests. It calls no FW session, route, network, VTS, Live2D, audio,
or provider. Unknown/stale/terminal input must fall back safely.

### RT-6c — guarded FW root-public mock motion-session adapter

Use only root-public symbols. Default to `adapter=mock`,
`real_adapter_enabled=false`, and `allow_provider_execution=false`. Use an
injectable factory, bounded ownership, typed result normalization, and
idempotent close. Real adapters remain rejected/not implemented.

### RT-6d — Flutter motion presentation model/client/controller

Add Flutter app-owned presentation/request/result state with fake transport,
sequence/stale-result protection, terminal restoration, and deterministic
close/dispose behavior. Do not wire HomeScreen yet.

### RT-6e — default-off HomeScreen character-motion wiring

Connect existing stream, integrated voice-turn, and local playback state only
through the accepted app-owned boundaries. No direct widget-to-FW call,
background provider connection, always-on animation, or unbounded event queue.

### RT-6f — configured local mock-motion presentation acceptance

Accept thinking, speaking, interruption, idle restoration, repeated turn,
failure fallback, and cleanup using mock motion. This is not real Live2D/VTS
operator acceptance.

## Root-public import boundary

Future DRC FW integration may import only reviewed symbols from `framework`.
Direct imports from `framework.motion`, `framework.motion_session`, provider
modules, VTS libraries, or internal adapters are not authorized.

## Exact RT-6a change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6a_character_motion_mapping_readiness.md
scripts/check_v300_rt6a_character_motion_mapping_readiness.py
```

## Non-actions

RT-6a changes no Backend/Flutter runtime, existing test, dependency, lockfile,
platform manifest, environment profile, API route, asset, version, release
metadata, Framework source, provider client, network execution, VTS WebSocket,
Live2D runtime, token/credential access, private model path, microphone/audio,
STT, LLM, TTS, screenshot, raw log, private transcript, or operator evidence.

## Stop rules

Stop and return to exact contract review if any candidate requires:

```text
- a Backend or Flutter runtime file in RT-6a
- an existing test change in RT-6a
- a Framework internal-module import
- a real VTS/Live2D adapter or token
- a direct widget-to-Framework call
- provider/network execution in normal tests
- private path, model, screenshot, audio, transcript, or raw payload evidence
- a claim that mock motion proves real adapter behavior
```

## Candidate acceptance

```text
compileall: pending operator execution
dedicated RT-6a gate: pending operator execution
Backend full tests: pending operator execution
Flutter analyze/full tests: pending operator execution
exact seven-file review: pending
changed-content privacy scan: pending
git diff --check: pending
explicit operator approval: pending
RT-6b authorization: blocked pending RT-6a acceptance
```
