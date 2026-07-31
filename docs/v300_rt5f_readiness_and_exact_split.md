# Daily Rhythm Companion v3.0.0 RT-5f0 readiness and exact split

Updated: 2026-07-31

## Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5e: COMPLETED / ACCEPTED / PUSHED
RT-5f: CURRENT / NOT_COMPLETED
RT-5f0: COMPLETED / ACCEPTED / PUSHED
RT-5f0 implementation commit: 348669884e872475aaa4242a5960a6de6fb7e10b
RT-5f1: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
DRC implementation baseline: 6272f613906317de3fecd899d4389ce0f13155e8
FW v5.4.0 HEAD: d313eb6acb643103fe25988720ebee5976a04f78
```

RT-5f0 is an accepted docs/test-only checkpoint. It freezes the current
executable boundaries and the small-commit split before any app-visible real
transcript source, integrated voice-turn coordinator, speech-activity adapter,
automatic TTS, or real barge-in runtime is added.

## Functional baseline already accepted

```text
real bounded Android microphone capture: accepted through operator path
real FW root-public STT: accepted through private operator path
provider-neutral transcript-to-stream handoff: implemented with fake provider
configured FW root-public text streaming: accepted
cooperative text-stream cancel: accepted
app-owned bounded TTS queue: accepted
completed-terminal to one-item synthesis/playback orchestration: accepted
configured FW root-public TTS synthesis: accepted
natural local playback: accepted
explicit binding-owned local playback stop: accepted
```

These are separate boundaries. They do not yet form one normal-app voice
conversation loop.

## Current gap 1: real STT is private operator-only

`FrameworkVoiceInputOpenAIRealOperatorResult` stores the completed transcript
only in a private in-memory field and exposes it only through
`private_transcript`. The public-safe fields continue to report
`transcript_exposed=false`. The accepted RT-3d3 contract explicitly adds no
FastAPI route and no Flutter change.

The existing `/demo/voice-input/staging` route can stage bounded WAV data, and
existing fake handoff/executor routes can return fake transcripts. There is no
normal app-visible route that consumes a staging ID through the accepted real
FW executor assembly and returns a bounded provider-neutral final transcript.

```text
app-visible real-STT source exists: false
DRC provider-specific STT client exists: false
FW internal import required by current accepted real executor: false
```

## Current gap 2: normal Flutter startup has no microphone/STT assembly

Normal `app/lib/main.dart` configures only:

```text
ConfiguredRealtimeTextStreamRuntime
ConfiguredRealtimeTerminalVoiceOutputRuntime
```

It does not instantiate `RecordMicrophoneCaptureEngine.mobile()`, a microphone
capture controller, a staging uploader, a real transcript provider, or a
`RealtimeTextStreamTranscriptHandoffFactory`. HomeScreen has an optional
provider-neutral transcript handoff boundary, but normal startup leaves it
unconfigured.

The transcript boundary already enforces:

```text
final transcript only
text maximum: 4096 Unicode code points
result ID maximum: 128 Unicode code points
remembered duplicate-result window: 32
no provider-specific model or payload in the Flutter result
```

## Current gap 3: speech activity is not observable

The production `RecordMicrophoneCaptureDriver` exposes only:

```text
start
stop
cancel
dispose
```

No amplitude stream, speech-onset event, VAD decision, consecutive-sample
threshold, cooldown, or single-fire latch exists. The existing explicit flush
button therefore proves local interruption, not speech-triggered barge-in.

## Existing local soft-interruption primitives

RT-5b through RT-5e already provide the local primitives needed by a future
DRC-owned soft barge-in coordinator:

```text
queue generation invalidation
operation epoch invalidation
late synthesis-result rejection
late playback-result rejection
pending queue clear
active queue item invalidation
binding-owned local player stop
cooperative text-stream cancel request
```

An RT-5e flush does not cancel an in-flight Backend HTTP request, cancel
provider synthesis, delete a generated artifact, invoke FW real output flush,
or prove provider hard cancellation.

## FW v5.4.0 public capability result

The gate uses only the FW root public package and verifies:

```text
RealtimeSessionInfo.real_runtime_enabled: false
RealtimeSessionInfo.tts_queue_flush_supported: false
RealtimeSessionInfo.hard_cancel_supported: false
TTSQueueState.supports_flush: false
TTSQueueState.supports_provider_cancel: false
empty mock flush outcome: nothing_to_flush
interrupt without active turn: no_active_turn
```

`BargeInPolicy` and `BargeInDecision` are public decision contracts. They do
not provide speech detection, real output queue ownership, provider synthesis
cancellation, or a unified real realtime runtime.

## Readiness classification

```text
PARTIAL_READY_FOR_APP_VISIBLE_REAL_STT_AND_DRC_LOCAL_SOFT_BARGE_IN
```

Ready without FW source modification:

```text
- app-visible provider-neutral real-STT response using existing private staging
  and accepted FW root-public real executor assembly;
- default-off Flutter transcript provider and existing handoff boundary;
- app-owned integrated voice-turn coordinator;
- queue/operation invalidation and local player stop;
- cooperative text-stream cancel request;
- bounded speech-activity source owned by DRC;
- private configured local operator acceptance.
```

Not supported or not claimable with FW v5.4.0:

```text
- unified FW real realtime orchestration;
- FW real output queue flush;
- provider synthesis hard cancel;
- Backend HTTP hard cancel;
- provider-level LLM hard cancel.
```

## Final RT-5f product claim

RT-5f must use this exact claim:

```text
speech-triggered DRC-local soft barge-in
```

Accepted behavior may be:

```text
confirmed foreground speech activity
→ increment app-owned operation epoch
→ invalidate active and pending app-owned TTS work
→ request stop on the RT-5e-owned local player
→ request cooperative cancellation of an active text stream when applicable
→ reject all late old-turn completions
→ permit the next bounded voice turn
```

Explicit non-claims:

```text
Backend HTTP hard cancellation: false
provider synthesis hard cancellation: false
FW real TTS queue flush: false
provider-level LLM hard cancellation: false
unified FW realtime runtime: false
```

## Exact follow-up split

### RT-5f1 — App-visible provider-neutral real-STT source

Goal:

```text
private staged WAV
→ single-use consume
→ accepted FW v5.4.0 root-public real-STT executor assembly
→ bounded provider-neutral final transcript response
→ Flutter transcript provider
→ existing RealtimeTextStreamTranscriptHandoff
```

Required constraints:

```text
default off and explicit foreground opt-in
one staged artifact consumed once
final transcript only
maximum transcript: 4096 Unicode code points
no credential in Flutter/request/response
no provider name/model/payload in Flutter contract
no private path, raw audio, staging ID, transcript, or raw error in logs
no transcript persistence or UI echo
no DRC provider-client bypass
FW root public API only
```

RT-5f1 must not add TTS automation, speech detection, barge-in, or HomeScreen
integration beyond an injectable transcript provider boundary.

### RT-5f2 — Fake-only integrated voice-turn and soft-barge-in coordinator

Use fake/in-memory dependencies only to coordinate capture completion, staging,
transcript, text stream, completed terminal, queue, synthesis, terminal
playback, and interruption.

Required race coverage includes speech during stream/synthesis/playback,
duplicate speech events, concurrent flush, late STT/stream/TTS/playback results,
new turn before old Future completion, and dispose during interruption.

No real microphone, network, provider, Backend runtime, or platform audio.

### RT-5f3 — Default-off HomeScreen and production speech-activity wiring

Add a DRC-owned bounded `SpeechActivitySource` abstraction and a production
adapter only after an exact package boundary review. Required controls include
foreground-only operation, maximum lifetime, threshold, consecutive samples,
single-fire latch, cooldown, duplicate suppression, and dispose cleanup.

Wire the integrated coordinator to normal startup behind a new compile-time
default-off switch and a session-local opt-in that defaults off. UI state must
remain metadata-only and must not display transcript, generated text copies,
staging/session/turn IDs, audio URLs, provider payloads, private paths, or raw
exceptions.

### RT-5f4 — Configured local end-to-end and audible soft-barge-in acceptance

Required configured flow:

```text
real bounded microphone capture
→ private staging
→ real FW root-public STT
→ app-visible in-memory final transcript
→ FW root-public text streaming
→ completed terminal
→ app-owned TTS queue
→ FW root-public TTS
→ RT-5e-owned local playback
```

Required interruption evidence:

```text
active audible playback
→ real user speech activity confirmed
→ DRC-local soft barge-in accepted
→ audible local playback stops
→ app-owned old-turn work becomes inert
→ next real voice turn can proceed
```

Playback echo alone must not satisfy speech-triggered acceptance. Private
operator evidence, logs, transcripts, audio, screenshots, paths, LAN addresses,
provider payloads, and credentials remain uncommitted.

## Exact RT-5f0 implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f_readiness_and_exact_split.md
scripts/check_v300_rt5f_readiness_and_exact_split.py
```

Exact seven-file docs/test-only implementation surface.

## Acceptance record

```text
implementation commit: 348669884e872475aaa4242a5960a6de6fb7e10b
compileall: passed
dedicated pre-commit gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 343 passed
exact implementation surface: 7 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
post-push local HEAD / origin/main: 348669884e872475aaa4242a5960a6de6fb7e10b
post-push working tree: clean
```

No private credential values, private paths, raw audio, provider payloads,
transcripts, screenshots, LAN addresses, logs, or operator evidence were added
to the repository.

The follow-up state is:

```text
RT-5f1: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

A separate exact RT-5f1 contract review and explicit authorization are required
before any runtime implementation, commit, or push.

## Acceptance-sync surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5f_readiness_and_exact_split.md
```

Exact six-file docs-only state sync. It changes no runtime, existing test,
dependency, private env, provider execution, microphone, audio, transcript,
version, or release record.

## Explicit non-change surface

```text
backend/**
app/lib/**
app/test/**
app/pubspec.yaml
app/pubspec.lock
platform wrappers
Framework repository
private env files
dependency versions
application/release versions
release notes and release assets
```

## Stop rule

Stop the next implementation review if any proposed path requires:

```text
- FW internal-module import;
- a DRC provider-specific client bypass;
- credentials in Flutter or ordinary API payloads;
- private paths, raw audio, transcript, provider payload, or raw error logging;
- transcript persistence or unbounded transcript exposure;
- unbounded microphone/audio/text/queue/session lifetime;
- provider hard cancel or FW real flush as an acceptance requirement;
- playback echo accepted as proof of user speech;
- runtime changes outside a separately reviewed exact surface.
```

## RT-5f0 execution boundary

RT-5f0 performed source-tree inspection and a root-public FW capability probe
only. It performed no Backend/Flutter runtime, network request, provider
execution, microphone access, audio playback, transcript creation, or private
env read. The implementation was explicitly accepted, committed, pushed, and
verified clean. RT-5f1 remains unauthorized until a separate exact contract
review and explicit authorization are completed.
