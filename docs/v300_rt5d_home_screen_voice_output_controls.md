# DRC v3.0.0 RT-5d HomeScreen manual voice-output controls contract

Updated: 2026-07-31

## 1. Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5a: COMPLETED / ACCEPTED / PUSHED
RT-5b: COMPLETED / ACCEPTED / PUSHED
RT-5c: COMPLETED / ACCEPTED / PUSHED
RT-5d: IMPLEMENTED / AWAITING_REVIEW
RT-5e: NOT_STARTED / BLOCKED_PENDING_RT5D_ACCEPTANCE
```

RT-5d adds HomeScreen presentation and ownership for the accepted RT-5c
fake/in-memory orchestration boundary. It provides session-local explicit
opt-in plus three independent manual actions:

```text
enqueue one completed realtime terminal
process at most one queued item
flush the app-owned queue and injected local fake stop
```

It does not configure a runtime in `main.dart`, call Backend voice output,
connect the existing real audio player, synthesize real audio, or add automatic
TTS.

## 2. Accepted baseline

```text
DRC HEAD / origin/main before RT-5d:
04b52a2e12d5f4dafd4e9a1172d628c6c58f9a70

RT-5c implementation:
f00214cd7e75b28c041728bca6ffc3b180face80

RT-5c acceptance sync:
04b52a2e12d5f4dafd4e9a1172d628c6c58f9a70

Framework release:
v5.4.0

Framework HEAD / tag:
d313eb6acb643103fe25988720ebee5976a04f78
```

RT-5d does not modify or import the Framework repository.

## 3. Default-off composition

`HomeScreen` receives an optional
`RealtimeTerminalVoiceOutputHomeScreenBindingFactory`.

The factory is called exactly once only when both of the following are present:

```text
a realtime text-stream controller
an RT-5d binding factory
```

Normal application composition remains unchanged because `main.dart` does not
provide the binding factory. Therefore the public/default application remains
unconfigured for RT-5d.

A factory exception fails closed to the fixed visible code
`configuration_failed`. Raw exception text is not displayed.

## 4. Binding ownership

RT-5c intentionally does not own final disposal of its injected queue or other
composition resources. RT-5d adds the app-owned binding boundary:

```text
RealtimeTerminalVoiceOutputHomeScreenBinding
OwnedRealtimeTerminalVoiceOutputHomeScreenBinding
```

The binding exposes only the orchestrator and an idempotent synchronous
`dispose()` method.

Binding disposal:

```text
invalidates the orchestrator
starts its best-effort queue flush / injected local fake stop
runs binding-owned final cleanup once
swallows raw teardown errors
does not double-dispose on repeated calls
```

HomeScreen owns the binding. It removes the orchestrator listener before
disposing the binding. HomeScreen does not separately dispose the orchestrator
or queue.

## 5. Session-local explicit opt-in

The RT-5d switch is:

```text
off by default
not persisted
not restored
not enabled when the binding is unconfigured
```

Turning the switch on performs no enqueue, synthesis, playback, or flush.

Turning the switch off is allowed only when:

```text
pending count == 0
active item absent
not synthesizing
not playing
not flushing
not disposed
```

RT-5d does not silently flush merely because the user attempts to turn opt-in
off. The user must press the explicit flush action first.

## 6. Explicit enqueue action

The enqueue button is enabled only when:

```text
binding configured
session opt-in on
realtime controller configured
controller phase == completed
orchestrator not flushing
orchestrator not disposed
```

A button press calls exactly:

```text
orchestrator.enqueueCompletedTerminal(controller.state)
```

There is no realtime-controller listener that enqueues a terminal. Stream
completion alone does nothing. Enqueue success does not call `processNext()`.

Duplicate and malformed terminal rejection remain owned by RT-5c. The UI
displays only a fixed typed outcome name and does not display terminal content
or identifiers.

## 7. Explicit one-item process action

The process button is enabled only when:

```text
session opt-in on
pending count > 0
no active item
not synthesizing
not playing
phase == ready
```

Each press calls `processNext()` once. RT-5d never drains the remaining queue
automatically.

HomeScreen uses a UI process sequence. A flush increments that sequence before
awaiting the flush result. Therefore an old invalidated synthesis/playback
future cannot later overwrite the visible result of a newer generation.

After RT-5c releases its process slot during flush, the HomeScreen process
button may handle a new generation without waiting for the old delegate future
to settle.

## 8. Explicit flush action

The flush button requires opt-in and visible work:

```text
pending item
or active item
or synthesizing / playing operation
```

It is disabled while already flushing or disposed.

A press calls RT-5c `flush()` once. RT-5c and RT-5b remain authoritative for
generation invalidation, pending clear, active invalidation, concurrent flush
deduplication, and one injected local fake stop.

Visible flush result is bounded to:

```text
typed flush outcome
cleared pending count
local fake stop requested
local fake stop succeeded
fixed technical code
```

RT-5d flush does not claim or perform:

```text
existing Voice Output Demo player stop
Backend synthesis cancellation
Framework real output flush
provider hard cancellation
LLM stream cancellation
speech-triggered barge-in
```

## 9. Existing real-player separation

HomeScreen already owns `VoiceOutputAudioPlayerController` for the existing
guarded Voice Output Demo.

RT-5d does not pass that controller or its engine into RT-5c. Focused tests
verify that RT-5d enqueue, process, and flush do not call the existing engine's
load, play, or stop methods.

The UI explicitly states:

```text
This fake RT-5 lifecycle does not control the existing Voice Output Demo player.
```

## 10. Visible state and privacy

The RT-5d section displays only:

```text
configured / unconfigured / configuration_failed
session opt-in on / off
orchestrator phase
pending count
active yes / no
last typed enqueue outcome
last typed process outcome
last typed flush outcome
cleared pending count
local fake stop requested / succeeded
fixed bounded technical code
```

It does not display or duplicate:

```text
utterance
realtime terminal final text
session ID
turn ID
queue item ID
audio URI
Backend response
provider payload
raw exception
private path
```

The existing Realtime Text Stream section may continue to display its accepted
stream output. RT-5d does not copy that output into its own section.

No logging, persistence, screenshot, operator evidence, or analytics event is
added.

## 11. HomeScreen lifecycle

Initialization order:

```text
construct existing Voice Output Demo player
construct existing optional realtime controller
construct existing optional transcript handoff
construct RT-5d binding only when controller + factory exist
register one orchestrator listener
```

Disposal order for RT-5d:

```text
mark HomeScreen as disposing
invalidate pending RT-5d UI result sequences
remove orchestrator listener
dispose binding once
continue existing transcript/controller/player cleanup
```

Every awaited RT-5d action checks both `mounted` and the disposing flag before
calling `setState`.

## 12. Focused fake-only widget verification

The focused widget tests cover:

```text
unconfigured controls
factory exactly once
default opt-out
stream completion alone starts nothing
opt-in alone starts nothing
explicit enqueue without automatic processing
duplicate terminal rejection
one process click for one queue item
duplicate process tap guard
multiple queued items remain manual one by one
manual pending flush
duplicate flush tap shares one local fake stop
flush during synthesis
flush during playback
new-generation processing while old future waits
binding disposal exactly once
late work after screen disposal is inert
bounded configuration failure
RT-5d section privacy
existing real-player non-use
```

All synthesis, playback, and local-stop dependencies are deterministic fakes.
No Backend HTTP, Framework, provider, platform audio, or real synthesis is
executed.

## 13. Exact ten-file implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
app/lib/screens/home_screen.dart
app/lib/services/realtime_terminal_voice_output_home_screen_binding.dart
app/test/realtime_terminal_voice_output_home_screen_widget_test.dart
docs/v300_rt5d_home_screen_voice_output_controls.md
scripts/check_v300_rt5d_home_screen_voice_output_controls.py
```

## 14. Explicit non-change surface

```text
backend/**
app/lib/main.dart
app/lib/services/configured_realtime_text_stream_runtime.dart
app/lib/services/backend_api_client.dart
app/lib/services/realtime_text_stream_controller.dart
app/lib/services/realtime_terminal_voice_output_orchestrator.dart
app/lib/services/voice_output_queue.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/audioplayers_voice_output_audio_engine.dart
existing tests
app/pubspec.yaml
app/pubspec.lock
dependencies
platform permissions
versions
release records
AI Character Framework repository
```

## 15. Candidate verification

```powershell
dart format `
  app\lib\screens\home_screen.dart `
  app\lib\services\realtime_terminal_voice_output_home_screen_binding.dart `
  app\test\realtime_terminal_voice_output_home_screen_widget_test.dart

python -m compileall -q backend scripts
python scripts\check_v300_rt5d_home_screen_voice_output_controls.py

python -m pytest -q backend\tests `
  --basetemp .pytest-tmp `
  -p no:cacheprovider

Push-Location app
flutter analyze
flutter test test\realtime_terminal_voice_output_home_screen_widget_test.dart
flutter test
Pop-Location

Remove-Item -Recurse -Force .pytest-tmp
python scripts\check_v300_rt5d_home_screen_voice_output_controls.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --stat
```

## 16. Review and stop rule

RT-5d remains `IMPLEMENTED / AWAITING_REVIEW` until the actual ten-file patch,
focused widget tests, full regressions, privacy scan, and exact surface are
reviewed and explicit commit approval is received.

Do not commit or push without explicit approval.

Do not modify `main.dart` or connect Backend/FW/provider execution, the existing
real player, real synthesis, real audio playback, automatic TTS, Framework real
output flush, provider hard cancel, or speech-triggered barge-in. RT-5e remains
blocked pending RT-5d acceptance.

## Dedicated gate contract vocabulary

The following phrases are explicit RT-5d contract terms used by the
credential-free dedicated source-tree gate. They restate the accepted
manual, fake-only HomeScreen lifecycle without expanding runtime scope.

```text
one explicit process action per queued item
```
