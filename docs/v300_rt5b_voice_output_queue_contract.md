# DRC v3.0.0 RT-5b app-owned voice-output queue contract

Updated: 2026-07-30

## 1. Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5a: COMPLETED / ACCEPTED / PUSHED
RT-5b: IMPLEMENTED / AWAITING_REVIEW
RT-5c: NOT_STARTED / BLOCKED_PENDING_RT5B_ACCEPTANCE
```

RT-5b adds a Flutter-only, app-owned, in-memory voice-output utterance queue and
local playback-flush lifecycle. No HomeScreen integration, real HTTP,
AI Character Framework/provider execution, or real audio playback is added.

## 2. Accepted baseline

```text
DRC HEAD / origin/main before RT-5b:
ba51fa8ef3e1d2dbc528ddd9506241b544c1b3d6

RT-5a implementation:
1cf77774dca75b9875099c2b6c6c03992456d80f

RT-5a acceptance sync:
ba51fa8ef3e1d2dbc528ddd9506241b544c1b3d6

Framework release:
v5.4.0

Framework HEAD / tag:
d313eb6acb643103fe25988720ebee5976a04f78
```

RT-5b does not modify or import the Framework repository.

## 3. Queue ownership

The queue is owned entirely by the Flutter app layer:

```text
bounded utterance input
-> app-owned pending FIFO
-> one active claim
-> future injected orchestration boundary
-> complete | fail | flush invalidation
```

RT-5b does not synthesize audio. A claimed utterance is returned only to the
direct caller for a later separately reviewed RT-5c orchestration boundary.
Utterance text is not copied into public queue state, logs, storage, or UI.

## 4. Fixed bounds

```text
maximum pending items: 8
maximum utterance length: 4096 Unicode code points
maximum retained text: 16384 Unicode code points
maximum active items: 1
maximum concurrent local playback stop requests per flush: 1
```

The retained-text bound includes the active claim and all pending utterances.
Whitespace-only utterances are rejected. Length checks use Unicode code points,
not UTF-16 code units.

## 5. Typed lifecycle

Public queue phases:

```text
idle
ready
active
flushing
disposed
```

Supported operations:

```text
enqueue
claimNext
complete
fail
flush
dispose
```

Typed rejection reasons keep invalid input, queue limits, retained-text limits,
active replacement, empty queue, flush-in-progress, stale generation, stale
item, missing active item, and disposed state separate.

Only one claimed item may be active. Completion and failure release the active
item and retained text. Pending FIFO order is preserved.

## 6. Flush contract

One flush request:

```text
1. increments the app-owned generation;
2. clears all pending utterances;
3. invalidates the active claim;
4. clears retained utterance text;
5. requests the injected local playback-stop callback exactly once;
6. returns a typed result.
```

Concurrent flush callers share one in-flight flush and one stop callback.

A callback from an older generation is rejected and cannot complete or fail a
new active item. Queue clear happens before the injected stop completes.
Therefore a local playback-stop failure does not restore pending or active
utterances.

Typed flush outcomes:

```text
completed
completedWithLocalPlaybackStopFailure
disposed
```

A partial result uses only the public-safe technical code
`local_playback_stop_failed`; the underlying exception is not exposed.

## 7. Meaning of local playback flush

RT-5b flush means:

```text
app pending queue clear
+ app active-claim invalidation
+ injected Flutter local playback stop request
```

It does not mean:

```text
Backend synthesis cancellation
Framework active TTS queue flush
provider synthesis hard cancellation
LLM stream cancellation
speech-triggered barge-in
real-STT-to-TTS orchestration
```

## 8. Exact nine-file implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
app/lib/services/voice_output_queue.dart
app/test/voice_output_queue_test.dart
docs/v300_rt5b_voice_output_queue_contract.md
scripts/check_v300_rt5b_voice_output_queue_contract.py
```

## 9. Explicit non-change surface

```text
backend/**
app/lib/screens/home_screen.dart
app/lib/main.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/backend_api_client.dart
app/pubspec.yaml
existing tests
dependencies
platform permissions
versions
release records
AI Character Framework repository
```

No HTTP request, provider execution, Framework import, synthesis, real audio
playback, microphone access, automatic TTS, or barge-in execution is performed.

## 10. Focused fake-only verification

The focused Flutter tests cover:

```text
initial state and public-state text privacy
FIFO enqueue and claim
empty input rejection
Unicode code-point utterance bound
pending item bound
retained active-plus-pending text bound
single active claim
completion and failure lifecycle
flush pending/active clear
generation-based late-result rejection
local playback-stop failure partial result
concurrent flush deduplication
enqueue/claim rejection during flush
stale item rejection
dispose cleanup
```

The stop dependency is a deterministic fake callback. Tests perform no
platform audio operation.

## 11. Acceptance checklist

```text
[ ] exact nine-file candidate
[ ] dart format applied to the two new Dart files
[ ] compileall passed
[ ] dedicated RT-5b gate passed
[ ] focused Flutter RT-5b tests passed
[ ] Backend full tests passed
[ ] Flutter analyze passed
[ ] Flutter full tests passed
[ ] git diff --check passed
[ ] changed-content private scan passed
[ ] exact diff review passed
[ ] explicit operator approval received
[ ] commit approved
[ ] push approved
```

Until every acceptance item passes:

```text
RT-5b: IMPLEMENTED / AWAITING_REVIEW
RT-5c: NOT_STARTED / BLOCKED_PENDING_RT5B_ACCEPTANCE
```

## 12. Stop rule

Stop after the exact nine-file candidate and verification.

Do not connect the queue to HomeScreen, the realtime text controller, Backend
voice-output requests, the existing real player, Framework, or a provider.
Do not start RT-5c. Do not claim Backend cancellation, Framework real output
flush, provider hard cancel, automatic TTS, or real barge-in.
