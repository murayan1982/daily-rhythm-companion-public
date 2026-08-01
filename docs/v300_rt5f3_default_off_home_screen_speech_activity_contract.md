# Daily Rhythm Companion v3.0.0 RT-5f3 default-off HomeScreen and production speech-activity contract

Status: **IMPLEMENTED / AWAITING_REVIEW**

```text
baseline DRC HEAD: 888814d09fad75039733a4a94719454e0a69db63
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
implementation commit: none
exact implementation surface: 20 files
commit/push: NOT_AUTHORIZED
real operator acceptance: NOT_EXECUTED
RT-5: CURRENT / NOT_COMPLETED
```

## Purpose

RT-5f3 connects the accepted RT-5f1 real-input boundary and RT-5f2
integrated voice-turn coordinator to one default-off HomeScreen binding. It also
adds a DRC-owned bounded production speech-activity source that can forward one
confirmed foreground event to the existing DRC-local soft-interruption
boundary.

The candidate does not claim real audible barge-in acceptance, production
speech-detection quality, echo-cancellation effectiveness, provider hard
cancel, Framework queue flush, or release readiness. Those claims remain
outside RT-5f3 and require separate operator acceptance.

## Exact 20-file implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md
scripts/check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py
app/lib/main.dart
app/lib/screens/home_screen.dart
app/lib/services/integrated_voice_turn_coordinator.dart
app/lib/services/speech_activity_source.dart
app/lib/services/record_speech_activity_source.dart
app/lib/services/integrated_voice_turn_home_screen_binding.dart
app/lib/services/configured_integrated_voice_turn_runtime.dart
app/test/integrated_voice_turn_coordinator_test.dart
app/test/speech_activity_source_test.dart
app/test/record_speech_activity_source_test.dart
app/test/integrated_voice_turn_home_screen_binding_test.dart
app/test/integrated_voice_turn_home_screen_widget_test.dart
app/test/main_integrated_voice_turn_wiring_widget_test.dart
```

Any changed or untracked path outside this set is a stop condition.

## Default-off gates

The configured assembly requires all of the following:

```text
DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN=true
DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM=true
DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT=true
valid configured Backend base URL
supported Android or iOS target
session-local HomeScreen opt-in
explicit Start voice turn action
```

`DRC_RT5F3_ENABLE_CONFIGURED_VOICE_TURN` has `defaultValue: false`. Building the
runtime, obtaining its factory, constructing the HomeScreen, and toggling the
session opt-in do not request microphone permission, open package:record,
execute HTTP/provider work, synthesize speech, or start playback.

The opt-in is memory-only and starts false on every binding construction. An
explicit Stop capture action completes the bounded first capture. Turning the
opt-in off disarms speech activity and cancels an active capture.

## Dedicated ownership boundary

The integrated binding creates and owns a separate dependency graph:

```text
microphone capture controller/session
host-audio staging controller
provider-neutral transcript provider
per-turn realtime text-stream controller
realtime transcript handoff
dedicated terminal voice-output binding
dedicated TTS queue/orchestrator/local player
production speech-activity source
integrated coordinator
```

It does not share the HomeScreen manual RT-4f4 stream controller or the manual
RT-5e queue, orchestrator, or player. The accepted RT-5f2 queue exclusivity and
processed-item identity checks remain unchanged.

## Production speech-activity boundary

The production driver uses the already pinned `record: 6.2.1` dependency.
`AudioRecorder.startStream()` is configured for mono 16 kHz PCM16 with the
package auto-gain, echo-cancel, and noise-suppress options enabled. PCM chunks
are drained and dropped immediately. They are never retained, persisted,
logged, placed in public state, or rendered by HomeScreen.

Only package-provided dBFS amplitude samples enter the detector. Defaults are:

```text
sample interval: 100 ms
threshold: -24.0 dBFS
required consecutive samples: 3
cooldown/latch period: 1500 ms
maximum armed lifetime: 90 seconds
one confirmed event per arming generation: true
```

A below-threshold sample resets an incomplete consecutive run. After one
confirmed event, the current arming generation remains latched and cannot emit
again. A later turn must disarm and arm a new generation. The source fails
closed with fixed technical codes and never exposes package/platform
exceptions.

The public event contains only:

```text
eventId: bounded ASCII-safe private in-memory identifier
confirmed: boolean
foreground: boolean
```

It contains no amplitude, PCM bytes, timestamp, device name, path, transcript,
provider metadata, credential, payload, session ID, turn ID, or raw exception.
The coordinator retains at most 32 event identifiers and preserves the accepted
128-code-point event-ID bound.

## Arming lifecycle

Speech activity is disarmed while the coordinator is:

```text
idle
capturing
interrupting
ready
completed
failed
interruptionFailed
disposed
```

It may be armed only for the exact turn generation authorized by an explicit
Start voice turn action, while session opt-in and foreground are both true and
the coordinator is in one of:

```text
staging
acquiringTranscript
streaming
voiceOutput
```

The binding disarms on opt-out, background transition, terminal/failure phase,
confirmed event forwarding, and disposal. A background transition clears the
authorized generation, so foreground return or a later opt-in toggle cannot
restart speech monitoring for an already active turn. It never automatically
starts a new capture after interruption.

## HomeScreen metadata-only UI

The HomeScreen section displays only fixed configuration and lifecycle
metadata:

```text
configured/unconfigured
session opt-in
foreground/background
coordinator phase
speech-source phase
operation epoch
turn generation
interruption count
pending voice-output count
local-stop retry required
last turn/speech/action outcome enums
```

It does not render transcript text, generated response text, stream chunks,
capture/staging/result/event/session/turn identifiers, amplitude values, audio
URLs, provider/model/payload data, credentials, private paths, or raw
exceptions. The existing manual RT-4f4 and RT-5e labels remain unique and their
bindings remain unchanged.

## Coordinator modification boundary

The RT-5f2 coordinator logic is not widened. RT-5f3 only neutralizes fake-only
documentation and safe-message wording so the injected coordinator can describe
a production adapter graph without making provider-specific claims.

The following accepted behavior remains mandatory:

```text
three voice-output exclusivity checks
processed itemId and generation identity check
private operation epoch invalidation before await
cooperative text-stream cancellation request
one app-owned queue flush/local-player stop request
bounded duplicate speech-event memory
late capture/staging/STT/stream/synthesis/playback completions inert
```

## Synthetic tests

The candidate adds focused coverage for:

```text
bounded detector defaults and invalid configuration
three-consecutive-sample confirmation
below-threshold reset
single event per arming generation
new event after a new generation
background disarm
maximum lifetime
late amplitude after disarm
in-flight driver start settled before disposal
serialized capture-to-staging source operations
foreground return does not rearm an active turn
fixed start/stream failure codes
idempotent close
default session opt-in off
toggle-only non-execution
capture-phase source disarmed
post-capture staging-phase source armed
opt-out capture cancellation
background lifecycle disarm
confirmed event forwarding and turn invalidation
dedicated resource disposal
metadata-only HomeScreen presentation
unique manual/integrated labels
compile-time prerequisite gating
main wiring default-off behavior
provider-neutral coordinator messages
```

All focused tests use fake/in-memory dependencies. They must not execute a real
microphone, network, provider, Framework synthesis, or local playback.

## Verification commands

Run from the real DRC repository root while HEAD remains the approved baseline:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/integrated_voice_turn_coordinator_test.dart
flutter test test/speech_activity_source_test.dart
flutter test test/record_speech_activity_source_test.dart
flutter test test/integrated_voice_turn_home_screen_binding_test.dart
flutter test test/integrated_voice_turn_home_screen_widget_test.dart
flutter test test/main_integrated_voice_turn_wiring_widget_test.dart
flutter test
cd ..

git diff --check
```

## Explicit non-change surface

```text
FW repository
backend/**
app/pubspec.yaml
app/pubspec.lock
Android/iOS permission manifests
existing RT-4f4 runtime semantics
existing manual RT-4f4 HomeScreen controls
existing RT-5e runtime semantics
existing manual RT-5e HomeScreen controls
existing microphone capture semantics
existing host-audio handoff semantics
existing transcript provider/model
existing text-stream transport/controller
existing voice-output queue/orchestrator semantics
version metadata
release metadata
```

## Non-claims and stop conditions

RT-5f3 does not establish any of the following:

```text
real microphone-to-STT-to-stream-to-TTS acceptance
real audible soft-barge-in acceptance
speech threshold quality acceptance
acoustic echo cancellation acceptance
provider-level LLM hard cancel
provider-level synthesis hard cancel
FW real TTS queue flush
automatic post-interruption capture restart
unified Framework realtime runtime
v3.0.0 release readiness
```

Stop review if the exact 20-file surface differs; any Backend, Framework,
dependency, lockfile, platform manifest, version, or release file changes; the
integrated graph shares manual stream/TTS ownership; a default switch becomes
true; toggle-only execution appears; speech activity arms during capture;
private text/IDs/amplitude/audio/provider/path/error data reaches UI; accepted
RT-5f2 ownership checks are relaxed; real execution occurs in synthetic tests;
or focused/full regression verification fails.

## Candidate state

```text
RT-5f3: IMPLEMENTED / AWAITING_REVIEW
implementation commit: none
commit/push: NOT_AUTHORIZED
operator acceptance: NOT_EXECUTED
RT-5: CURRENT / NOT_COMPLETED
```
