# DRC v3.0.0 RT-4f2 HomeScreen stream UI

Updated: 2026-07-30

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4e: COMPLETED / ACCEPTED / PUSHED
RT-4f: CURRENT / NOT_COMPLETED
RT-4f1: COMPLETED / ACCEPTED / PUSHED
RT-4f2: IMPLEMENTED / AWAITING_ACCEPTANCE
RT-4f3: NOT_STARTED
RT-4f4: NOT_STARTED
Current small commit: RT-4f2 IMPLEMENTED / AWAITING_ACCEPTANCE
Current implementation: HomeScreen fake streaming presentation and controller lifecycle wiring with bounded manual input
Current implementation commit: none
Last accepted small commit: RT-4f1 COMPLETED / ACCEPTED / PUSHED at f54e8638f0255b28e015702bc64b624a6d4a36af
Next action: verify and accept RT-4f2 only; do not begin RT-4f3 transcript handoff
```

## Scope

RT-4f2 wires the accepted RT-4e `RealtimeTextStreamController` into HomeScreen
through an optional factory:

```dart
RealtimeTextStreamController Function()? realtimeTextStreamControllerFactory
```

HomeScreen invokes the factory once in `initState()`, owns the created
controller, registers one listener, removes the listener in `dispose()`,
disposes the controller, and disposes the manual input controller. A null
factory leaves the stream section visible but unconfigured. `main.dart` remains
unchanged, so normal `const HomeScreen()` does not construct a real client or
perform stream network requests.

## Visible UI Contract

The HomeScreen realtime text stream section exposes stable widget keys:

```text
realtime-text-stream-section
realtime-text-stream-input
realtime-text-stream-start-button
realtime-text-stream-cancel-button
realtime-text-stream-phase
realtime-text-stream-output
realtime-text-stream-error
realtime-text-stream-cancel-mode
realtime-text-stream-hard-cancel-supported
realtime-text-stream-unconfigured
```

Visible phases are:

```text
idle
connecting
streaming
cancel_requested
completed
cancelled
failed
closed
unconfigured
```

The section displays bounded manual input, start, current phase, incremental
output, cooperative cancel, cancel mode, `hardCancelSupported=false`, bounded
safe error text, and unconfigured state. It does not display session IDs, turn
IDs, event paths, cancel paths, transcript text, provider/model payloads,
private paths, credentials, raw exceptions, stack traces, or input echo outside
the input field.

## Manual Input Boundary

Manual input is trimmed before start. Empty input is rejected before calling the
controller. Input above 4096 Unicode code points is rejected before calling the
controller. Validation errors use fixed public-safe messages only. The input may
remain in the input field after start, but it is not copied to output, errors,
advice, post-advice chat, voice output, transcript, or any persistence path.

## Start And Cancel

Start is disabled when no controller factory is configured or when the
controller state is active. Active phases are connecting, streaming, and
cancelRequested. Each valid start action calls `controller.start(inputText:)`
once and preserves the accepted RT-4e active replacement guard.

Cancel is enabled only after a create response exists, the phase is streaming,
and the state is non-terminal. It calls `controller.cancel()` as a cooperative
request. Duplicate cancel while cancel is pending or cancelRequested is blocked
by the accepted controller contract. UI always shows
`hardCancelSupported=false` and makes no provider-level immediate termination
claim.

## Test Boundary

Focused widget tests use:

```text
fake BackendApiClient
real accepted RealtimeTextStreamClient
real accepted RealtimeTextStreamController
fake/in-memory http.BaseClient transport
controlled POST create, GET SSE events, and POST cooperative cancel
```

They use no socket, localhost, real Backend, Framework, provider, transcript,
or TTS execution. The fake transport covers unconfigured state, factory
lifecycle/disposal, bounded input, incremental completion, duplicate start
prevention, cooperative cancel, safe failure, closed terminal, and no automatic
voice-output playback.

## Non-Actions

```text
main.dart changed: false
real client auto construction: false
real Backend execution: false
real Framework execution: false
provider execution: false
STT transcript handoff added: false
accepted real-STT transcript reaches Flutter: false
RT-4f3 transcript handoff started: false
automatic TTS start: false
TTS queue/flush/barge-in added: false
provider-level hard cancel claimed: false
reconnect/resume added: false
WebSocket added: false
```

## Exact Change Surface

```text
app/lib/screens/home_screen.dart
app/test/realtime_text_stream_home_screen_widget_test.dart
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt4f_ui_streaming_acceptance_inventory.md
docs/v300_rt4f2_home_screen_stream_ui.md
scripts/check_v300_rt4f2_home_screen_stream_ui.py
```
