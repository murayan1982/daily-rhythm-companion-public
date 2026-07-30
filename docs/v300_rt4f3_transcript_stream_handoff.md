# DRC v3.0.0 RT-4f3 transcript-to-stream handoff

Updated: 2026-07-30

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4e: COMPLETED / ACCEPTED / PUSHED
RT-4f: CURRENT / NOT_COMPLETED
RT-4f1: COMPLETED / ACCEPTED / PUSHED
RT-4f2: COMPLETED / ACCEPTED / PUSHED
RT-4f3: IMPLEMENTED / AWAITING_ACCEPTANCE
RT-4f4: NOT_STARTED
Current small commit: RT-4f3 IMPLEMENTED / AWAITING_ACCEPTANCE
Current implementation: App-owned provider-neutral transcript-to-stream handoff using injected/fake transcript and fake/in-memory stream dependencies
Current implementation commit: none
Last accepted small commit: RT-4f2 COMPLETED / ACCEPTED / PUSHED at 1e1a4b27a0fe7c105eec344bfde39afe6a077f8a
Next action: verify and accept RT-4f3 only; do not begin configured RT-4f4 execution
```

## Scope

RT-4f3 adds an app-owned provider-neutral handoff boundary between an injected
final transcript result and the accepted RT-4e realtime text stream controller.
It does not add a real transcript source. The accepted real-STT transcript
still does not reach Flutter.

The provider-neutral model is:

```dart
ProviderNeutralTranscriptResult({
  required String resultId,
  required String text,
  required bool isFinal,
})
```

The model intentionally carries no provider name, model name, confidence,
audio path, provider payload, raw response, or credential. `resultId` is opaque.

## Handoff Contract

`RealtimeTextStreamTranscriptHandoff` is a ChangeNotifier owned by HomeScreen.
It depends on an accepted `RealtimeTextStreamController` and an injected
`ProviderNeutralTranscriptProvider`.

The service:

- does not own or dispose the realtime controller;
- owns no HTTP client, BackendApiClient, microphone/STT object, or provider client;
- stores no transcript text in fields or public state;
- stores no result ID in public state;
- may retain only a bounded in-memory queue of opaque consumed result IDs;
- clears consumed result IDs on dispose;
- never notifies listeners after dispose.

Before it calls `controller.start(inputText:)`, the service rejects disposed,
simultaneous, active-stream, null, non-final, empty, overlong, invalid-ID, and
duplicate-result cases safely. A valid result ID is marked consumed before
exactly one stream start call. No automatic retry occurs, including when stream
start fails.

Boundaries:

```text
maximum transcript text: 4096 Unicode code points
maximum result ID: 128 Unicode code points
maximum remembered result IDs: 32
maximum public-safe problem message: 240 Unicode code points
```

Safe messages are whitespace-compacted and bounded. They never concatenate
exception text, problem code, result ID, transcript text, HTTP body, path, or
stack trace.

## HomeScreen Contract

HomeScreen accepts an optional `RealtimeTextStreamTranscriptHandoffFactory`.
The factory is called once in `initState()` only when the RT-4f2 realtime
controller exists. The exact HomeScreen-owned realtime controller is passed to
the factory. HomeScreen registers a handoff listener, removes it in `dispose()`,
disposes the handoff, then disposes the realtime controller under the existing
RT-4f2 ownership rule.

Normal `const HomeScreen()` remains valid and handoff-unconfigured because
`main.dart` remains unchanged and no real transcript provider is constructed.

Stable widget keys:

```text
realtime-text-stream-transcript-handoff
realtime-text-stream-transcript-start-button
realtime-text-stream-transcript-status
realtime-text-stream-transcript-error
realtime-text-stream-transcript-unconfigured
realtime-text-stream-transcript-privacy-note
```

Visible handoff phases:

```text
unconfigured
ready
acquiring
accepted
rejected
failed
```

The UI does not display transcript text or result IDs, does not copy transcript
text into the manual input controller, does not use
`VoiceInputDemoRequestResponse.transcript` for handoff, and does not start TTS.

## Test Boundary

Focused unit and widget tests use the accepted RT-4e model/client/controller and
fake/in-memory HTTP only. They use no socket, localhost, real Backend,
Framework, provider, microphone, STT, transcript persistence, or TTS execution.

Coverage includes valid final transcript, active stream rejection, simultaneous
duplicate invocation, invalid transcript/result ID, duplicate consumed ID,
provider null/throw, controller failure, long safe message bounding, disposal
during a pending provider, bounded consumed-ID memory, HomeScreen lifecycle,
no VoiceInputDemo coupling, and no TTS coupling.

## Non-Actions

```text
real microphone capture: false
real STT execution: false
private operator transcript read: false
VoiceInputDemo transcript wired: false
Backend transcript route added: false
Backend/FW/provider execution: false
configured runtime wiring: false
main.dart changed: false
provider client added: false
Framework internal import: false
transcript persistence: false
transcript text displayed: false
result ID displayed: false
raw exception displayed: false
automatic TTS start: false
TTS queue/flush/barge-in added: false
hard cancel added: false
reconnect/resume added: false
WebSocket added: false
RT-4f4 started: false
```

## Exact Change Surface

```text
app/lib/models/provider_neutral_transcript.dart
app/lib/services/realtime_text_stream_transcript_handoff.dart
app/lib/screens/home_screen.dart
app/test/realtime_text_stream_transcript_handoff_test.dart
app/test/realtime_text_stream_transcript_handoff_home_screen_widget_test.dart
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt4f_ui_streaming_acceptance_inventory.md
docs/v300_rt4f3_transcript_stream_handoff.md
scripts/check_v300_rt4f3_transcript_stream_handoff.py
```
