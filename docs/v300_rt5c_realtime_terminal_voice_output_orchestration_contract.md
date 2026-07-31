# DRC v3.0.0 RT-5c realtime-terminal voice-output orchestration contract

Updated: 2026-07-31

## 1. Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5a: COMPLETED / ACCEPTED / PUSHED
RT-5b: COMPLETED / ACCEPTED / PUSHED
RT-5c: COMPLETED / ACCEPTED / PUSHED
RT-5d: NOT_STARTED / NOT_AUTHORIZED
```

RT-5c adds a Flutter-only, app-owned, injectable orchestration boundary from a
validated completed realtime text terminal through the accepted RT-5b FIFO to
fake synthesis and fake terminal playback lifecycle delegates.

It does not connect HomeScreen, perform Backend HTTP, call AI Character
Framework, execute a provider, synthesize real audio, or use the existing real
local audio player.

## 2. Accepted baseline

```text
DRC HEAD / origin/main before RT-5c:
5fcac869f81e1070e854550f4376353e109905e5

RT-5b implementation:
c48238256cb0b17c925f8063c3b636d3b4ccf533

RT-5b acceptance sync:
5fcac869f81e1070e854550f4376353e109905e5

RT-5c implementation:
f00214cd7e75b28c041728bca6ffc3b180face80

Framework release:
v5.4.0

Framework HEAD / tag:
d313eb6acb643103fe25988720ebee5976a04f78
```

RT-5c does not modify or import the Framework repository.

## 3. Explicit invocation only

RT-5c exposes separate explicit operations:

```text
enqueueCompletedTerminal(...)
processNext()
flush()
dispose()
```

The orchestrator does not register a realtime-controller listener and does not
observe terminal state automatically. Enqueue does not start synthesis.
`processNext()` claims and processes at most one queue item. It does not drain
remaining pending items automatically.

Therefore RT-5c does not add automatic TTS. A later separately reviewed UI
commit must provide any explicit enqueue, play, or flush control.

## 4. Completed-terminal validation

Only a consistent completed snapshot may be enqueued:

```text
controller phase: completed
terminal present: true
terminal outcome: completed
problem present: false
create response present and accepted: true
session ID and turn ID: non-empty, unpadded, and mutually consistent
terminal sequence == controller last sequence
terminal final text == controller output text
terminal output count == output Unicode code-point count
trimmed output text: non-empty
```

Cancelled, failed, closed, connecting, streaming, malformed, inconsistent, and
empty terminal snapshots are rejected before queue mutation.

## 5. Bounded duplicate suppression

A completed terminal is identified privately in memory by:

```text
session ID + turn ID + terminal sequence
```

The key is remembered only after RT-5b queue enqueue succeeds. Queue rejection
therefore does not consume the terminal. Remembered keys are insertion ordered
and bounded to 32 entries by default. Oldest-key eviction permits a later
explicit replay only after it leaves that bounded window.

Flush does not clear remembered keys. This prevents the same still-present
terminal snapshot from being immediately re-enqueued after invalidation.
Dispose clears the private key set.

Terminal IDs are not copied into public orchestrator state, technical codes, or
logs.

## 6. Injected fake synthesis boundary

The injected synthesis delegate receives only:

```text
RT-5b queue item metadata
claimed utterance
```

Typed fake outcomes are:

```text
audioReady with one opaque URI string
rejected
failed
```

Delegate exceptions and typed failures are converted to fixed public-safe
technical codes. Raw exception text and provider payloads are not retained.

RT-5c does not use `BackendApiClient`, perform HTTP, resolve a Backend-relative
artifact path, import Framework, or call a provider. A later configured adapter
must return an already-resolved absolute HTTP(S) URI.

## 7. Bounded opaque audio URI validation

An `audioReady` result is accepted only when the opaque URI:

```text
is at most 2048 Unicode code points
has no leading or trailing whitespace
contains no ASCII whitespace/control character
contains no backslash
parses as an absolute URI
uses http or https
has a non-empty host
has no user-info component
has no fragment
may contain a query
```

Relative URLs, file URLs, unsupported schemes, credentials in the authority,
fragments, controls, whitespace, backslashes, and over-limit values fail the
claimed queue item with `invalid_audio_uri`.

After it arrives in the injected synthesis result, the URI is held only in a
local operation variable and passed to the injected playback delegate. It is
not copied into orchestrator public state, enqueue/process results, technical
codes, or logs.

## 8. Injected fake terminal playback lifecycle

The playback delegate future represents terminal playback lifecycle, not merely
load/start completion. Typed outcomes are:

```text
completed
failed
expired
stopped
```

Only `completed` calls RT-5b queue `complete()`. All other terminal outcomes and
delegate exceptions call queue `fail()` with fixed bounded technical codes.

RT-5c does not instantiate or import `VoiceOutputAudioPlayerController` and does
not perform real audio playback.

## 9. FIFO and concurrency

The accepted RT-5b queue remains authoritative for FIFO, bounds, one active
claim, completion, failure, and generation invalidation.

```text
one processNext call -> zero or one claim -> zero or one terminal result
```

A second `processNext()` while one non-invalidated operation is active returns a
typed `processInProgress` result. It does not share, replace, or duplicate the
active operation.

Completed terminals may still be explicitly enqueued while another item is
processing. They remain pending until a later explicit `processNext()` call.

## 10. Flush and late-result invalidation

The orchestrator synchronously:

```text
publishes the shared in-flight flush future
increments its operation epoch
releases its active-process slot
starts RT-5b queue flush
publishes the already-invalidated queue as flushing
```

Publishing the shared future first makes a flush triggered reentrantly by a
state listener join the same operation instead of starting a second stop.
Starting RT-5b flush before the orchestrator notification also prevents a
listener from enqueueing or claiming an item in a pre-flush window.

RT-5b queue flush synchronously begins by:

```text
increments queue generation
clears pending items
invalidates the active claim
clears retained text
requests the injected local playback stop once
```

The orchestrator revalidates both its operation token/epoch and the RT-5b
active item/generation:

```text
before synthesis starts
after synthesis returns
after URI validation immediately before playback starts
after the playback delegate returns its future
after playback terminal returns
immediately before queue complete or fail
```

Consequences:

```text
flush during synthesis cannot start late playback
flush during playback makes a late terminal result inert
an old result cannot complete or fail a new-generation item
new-generation work may start after flush without waiting for an invalidated
old delegate future to settle
```

Concurrent orchestrator flush callers share one in-flight queue flush and one
local playback-stop request. A local stop failure does not restore pending or
active items.

RT-5c flush means app queue invalidation plus injected local playback stop only.
It does not claim Backend synthesis cancellation, Framework real output flush,
provider hard cancellation, or speech-triggered barge-in.

## 11. Public state privacy

Public orchestrator state contains only:

```text
orchestration phase
pending count
RT-5b active item metadata
last typed process outcome
last typed enqueue rejection
last RT-5b queue rejection
fixed bounded technical code
```

It does not contain:

```text
utterance text
terminal final text
session ID
turn ID
audio URI
Backend response
provider payload
raw exception text
```

No logging, persistence, screenshot, operator evidence, or private path handling
is added.

## 12. Dispose ownership

Dispose invalidates late operation callbacks, releases the process slot, clears
remembered terminal keys, and starts a best-effort RT-5b queue flush so the
injected local stop boundary is requested.

The orchestrator does not dispose the injected queue or delegates. Their final
ownership remains with a future composition/wiring layer.

## 13. Exact nine-file implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
app/lib/services/realtime_terminal_voice_output_orchestrator.dart
app/test/realtime_terminal_voice_output_orchestrator_test.dart
docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md
scripts/check_v300_rt5c_realtime_terminal_voice_output_orchestration_contract.py
```

## 14. Explicit non-change surface

```text
backend/**
app/lib/screens/home_screen.dart
app/lib/main.dart
app/lib/services/backend_api_client.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/realtime_text_stream_controller.dart
app/lib/services/voice_output_queue.dart
existing tests
app/pubspec.yaml
dependencies
platform permissions
versions
release records
AI Character Framework repository
```

## 15. Focused fake-only verification

The focused Flutter tests cover:

```text
public-state privacy and idle state
explicit enqueue without automatic synthesis
completed-terminal consistency validation
successful-enqueue-only duplicate consumption
bounded duplicate retention across flush
FIFO and one-item-per-process behavior
concurrent process rejection
synthesis rejected / failed / exception mapping
absolute bounded opaque URI validation
playback completed / failed / expired / stopped / exception mapping
reentrant flush before synthesis starts
flushing notification has no pre-flush enqueue/claim window
flush during synthesis
flush during playback
reentrant and concurrent flush deduplication
new-generation processing while an old future remains pending
local playback-stop failure without queue restoration
dispose late-result invalidation
empty queue typed result
```

All synthesis, playback, and stop dependencies are deterministic in-memory
fakes. No platform audio, HTTP, Backend, Framework, provider, or HomeScreen
execution occurs.

## 16. Accepted verification

```text
implementation commit: f00214cd7e75b28c041728bca6ffc3b180face80
dart format: passed
compileall: passed
dedicated RT-5c candidate gate: passed before commit
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter RT-5c tests: 22 passed
Flutter full tests: 315 passed
exact implementation surface: 9 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
```

The dedicated gate remains a historical pre-commit implementation-candidate
gate bound to baseline `5fcac869f81e1070e854550f4376353e109905e5` and the
exact nine-file working-tree surface. It is not rerun for the later
six-document acceptance sync.

## 17. Acceptance and stop rule

RT-5c is `COMPLETED / ACCEPTED / PUSHED` at implementation commit
`f00214cd7e75b28c041728bca6ffc3b180face80`.

Acceptance does not connect HomeScreen, Backend HTTP, Framework, provider
execution, real synthesis, or real playback, and does not claim automatic TTS,
Framework real output flush, provider hard cancel, or speech-triggered
barge-in. RT-5d remains `NOT_STARTED / NOT_AUTHORIZED` until a separate exact
HomeScreen explicit opt-in contract is reviewed and explicitly authorized.
