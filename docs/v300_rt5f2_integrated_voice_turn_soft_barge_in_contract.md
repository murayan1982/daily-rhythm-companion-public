# Daily Rhythm Companion v3.0.0 RT-5f2 integrated voice-turn contract

Updated: 2026-08-01

## Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5f0: COMPLETED / ACCEPTED / PUSHED
RT-5f1: COMPLETED / ACCEPTED / PUSHED
RT-5f2: IMPLEMENTED / CORRECTIVE_PATCH_AWAITING_REVIEW
RT-5f2 implementation commit: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6
RT-5f2 corrective patch baseline: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6
DRC original implementation baseline: 1cba847b7c443c4d41a2ff6bd2c18d20689e5029
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
corrective patch commit/push: not authorized
RT-5f3: BLOCKED_PENDING_RT5F2_ACCEPTANCE / NOT_AUTHORIZED
```

## Claim boundary

RT-5f2 may claim only:

```text
fake-only integrated voice-turn coordinator
fake-only DRC-local soft-barge-in behavior
```

It does not claim a real microphone, production speech detection, Backend or
provider execution, real STT, real streaming, real synthesis, real playback,
provider hard cancel, Backend HTTP hard cancel, FW real queue flush, or a
unified Framework realtime runtime.

## Reused accepted boundaries

The coordinator composes, without modifying:

```text
MicrophoneCaptureResult
HostAudioHandoffResult
RealtimeTextStreamTranscriptHandoff
RealtimeTextStreamController
RealtimeTerminalVoiceOutputOrchestrator
VoiceOutputQueueController generation/flush behavior
```

Capture completion and staging are injected callbacks. The transcript handoff,
stream controller, and RT-5c voice-output orchestrator retain their existing
validation and ownership rules.

## Normal fake turn

```text
completed fake capture
→ completed fake staging
→ final provider-neutral transcript
→ existing transcript-to-stream handoff
→ fake/in-memory text stream
→ completed terminal only
→ existing RT-5c enqueue
→ exactly one processNext()
→ injected fake synthesis
→ bounded opaque HTTP(S) URI
→ injected fake terminal playback
```

Cancelled, failed, closed, or inconsistent stream terminals never reach TTS.

## Exclusive voice-output ownership

A new turn may start only while the injected RT-5c voice-output state is
exclusive and empty:

```text
pendingCount == 0
activeItem == null
isProcessing == false
phase != flushing
phase != disposed
```

The same condition is checked before the voice-output phase transition and
rechecked after synchronous coordinator phase listeners return, immediately
before the completed terminal is enqueued. If another owner adds or activates
voice-output work while capture, staging, transcript acquisition, streaming, or
the phase notification is in progress, the current turn fails safely before its
own enqueue and does not consume that other work.

The coordinator retains the queue item returned by
`enqueueCompletedTerminal()`. A successful `processNext()` result is accepted
only when its item has the same `itemId` and `generation`. Completing a different
pre-existing or externally claimed item cannot complete the current voice turn.

## Operation epoch

Every started turn owns one private operation token and epoch. Public state
contains only counters and enums.

After every await, the coordinator verifies that the operation is still current.
A stale completion returns `invalidated` and cannot start a stream, enqueue a
terminal, synthesize, play, complete/fail a queue item, or update public state.

## Speech activity input

RT-5f2 defines only an injected event contract:

```text
event_id: ASCII [A-Za-z0-9._-], 1..128 Unicode code points
confirmed: true
foreground: true
remembered event IDs: maximum 32
```

The event ID is used only for private in-memory duplicate suppression and is
never copied into public state.

Invalid/background/unconfirmed events do nothing. Duplicate events are rejected.
Concurrent distinct confirmed events coalesce onto one interruption.

Production amplitude/VAD thresholds, consecutive-sample logic, cooldown,
single-fire latch, and source lifetime remain RT-5f3 work.

## Soft interruption ordering

Before the first interruption await:

```text
increment coordinator epoch
clear active-turn ownership
detach the stream terminal listener
dispose the transcript handoff
complete the old terminal wait as stale
request cooperative stream cancel once when active
request RT-5c flush once
```

RT-5c flush invalidates the queue generation and active operation, clears
pending work, and requests only the injected local playback stop boundary.

The next turn may begin after local playback stop succeeds, even when an old
capture, staging, transcript, stream cancel, synthesis, or playback Future has
not completed. Every late old completion remains inert.

## Local playback stop failure

A failed local playback stop preserves old-work invalidation but sets:

```text
phase: interruptionFailed
localStopRetryRequired: true
```

No new turn may start until another distinct confirmed foreground speech event
retries the flush successfully. Stop failure is never reported as accepted
barge-in.

## Dispose

Dispose increments the epoch, detaches the current turn, requests cooperative
cancel where applicable, requests RT-5c flush, clears remembered speech-event
IDs, and makes all later completions inert. The coordinator does not own or
dispose the injected RT-5c orchestrator.

## Public state

Allowed:

```text
phase enum
operation epoch
turn generation
interruption count
pending voice-output count
local-stop retry flag
last outcome enums
bounded safe message
bounded safe technical code
```

Forbidden:

```text
transcript or generated response text
capture/staging/result/session/turn/event IDs
audio URI
private path or raw audio
provider/model/payload/credential
raw exception
```

## Race coverage

Focused tests cover:

```text
happy-path full fake voice turn
speech during capture
speech during staging
speech during transcript acquisition
speech during stream
speech during synthesis
speech during playback
duplicate speech events
concurrent distinct speech events
concurrent flush coalescing
late STT/stream/synthesis/playback completion
new turn before old Future completion
local playback stop failure and retry
stream cancel request failure
cancelled terminal exclusion from TTS
dispose during capture
dispose during staging
dispose during transcript acquisition
dispose during stream
dispose during synthesis
dispose during playback
dispose during interruption
bounded remembered speech-event IDs
public-state privacy
pre-existing pending voice output blocks capture
pre-existing active synthesis blocks capture
voice-output exclusivity is rechecked before terminal enqueue
synchronous voice-output phase listener cannot steal queue ownership
processed queue item matches the current terminal item ID and generation
```

## Exact nine-file implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md
scripts/check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py
app/lib/services/integrated_voice_turn_coordinator.dart
app/test/integrated_voice_turn_coordinator_test.dart
```

The original implementation was committed and pushed at
`c538dc89c2aa9780cd3014aa4ba11c17a9e378e6` before exact acceptance review.
The acceptance review identified one queue-ownership blocker. The corrective
candidate is restricted to this exact four-file surface:

```text
app/lib/services/integrated_voice_turn_coordinator.dart
app/test/integrated_voice_turn_coordinator_test.dart
docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md
scripts/check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py
```

## Explicit non-change surface

```text
FW repository
backend/**
private env files
app/lib/main.dart
app/lib/screens/home_screen.dart
existing microphone capture and host-audio files
existing Backend staging/transcript provider
existing transcript model/handoff
existing stream controller/client
existing voice-output queue
existing RT-5c orchestrator
existing RT-5e configured runtime
dependencies and platform wrappers
version/release metadata
```

## Verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/integrated_voice_turn_coordinator_test.dart
flutter test
cd ..

git diff --check
```

The verification is credential-free, provider-free, network-free,
microphone-free, platform-audio-free, and real-transcript-free. Corrective
validation must report an exact four-file change surface against
`c538dc89c2aa9780cd3014aa4ba11c17a9e378e6`.

## Stop rule

Stop before commit/push if implementation requires any real runtime, existing
runtime-file modification, HomeScreen/main wiring, provider-specific client,
Framework internal import, private data exposure, unbounded ID/text/history, or
a claim broader than DRC-local soft interruption.
