# DRC v3.0.0 RT-4f3 transcript-to-stream handoff

Updated: 2026-07-30

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4e: COMPLETED / ACCEPTED / PUSHED
RT-4f: CURRENT / NOT_COMPLETED
RT-4f1: COMPLETED / ACCEPTED / PUSHED
RT-4f2: COMPLETED / ACCEPTED / PUSHED
RT-4f3: COMPLETED / ACCEPTED / PUSHED
RT-4f4: IMPLEMENTED / AWAITING_REVIEW
Current small commit: RT-4f4 IMPLEMENTED / AWAITING_REVIEW
Current implementation: Default-off configured Flutter realtime text stream runtime wiring for configured local Backend/FW streaming and cooperative cancel visible UI acceptance. Real-STT-to-stream execution may be included only if a separately reviewed safe real transcript source is configured.
Current implementation state: IMPLEMENTED / AWAITING_REVIEW
Current implementation commit: none
Last accepted small commit: RT-4f3 COMPLETED / ACCEPTED / PUSHED at d651a00be8713a70be3a46524f33c787299bbe9c
Next action: review RT-4f4 implementation candidate only; do not claim configured real Backend/FW execution, real-STT-to-stream acceptance, or RT-5 TTS queue/flush/barge-in
```

## Scope

RT-4f3 adds an app-owned provider-neutral handoff boundary between an injected
final transcript result and the accepted RT-4e realtime text stream controller.
It does not add a real transcript source. The accepted real-STT transcript
still does not reach Flutter.

RT-4f3 is COMPLETED / ACCEPTED / PUSHED at implementation commit
`d651a00be8713a70be3a46524f33c787299bbe9c`.

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
active-stream, null, non-final, empty, overlong, invalid-ID, and
duplicate-result cases safely. Simultaneous invocation is protected by an
independent private in-flight guard; duplicate calls do not invoke the provider
again and do not change the active `acquiring` phase to `rejected`. A valid
result ID is marked consumed before exactly one stream start call. No automatic
retry occurs, including when stream start fails.

Boundaries:

```text
maximum transcript text: 4096 Unicode code points
maximum result ID: 128 Unicode code points
maximum remembered result IDs: 32
maximum public-safe problem message: 240 Unicode code points
```

Safe messages are whitespace-compacted and bounded. They never concatenate
exception text, problem code, result ID, transcript text, HTTP body, path,
session ID, turn ID, or stack trace.

Transcript text is used only as the local argument to one `controller.start()`
invocation. Transcript text is not copied into handoff public state, retained
in a handoff field, copied into HomeScreen manual input, rendered by the UI,
logged, or persisted. Opaque result IDs are not rendered in the UI. Only a
bounded in-memory consumed-ID collection may retain opaque result IDs.

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

## Acceptance Record

```text
implementation commit:
d651a00be8713a70be3a46524f33c787299bbe9c

implementation pushed:
true

compileall:
passed

dedicated RT-4f3 gate:
passed

focused RT-4f3 unit tests:
15 passed

focused RT-4f3 widget tests:
9 passed

Backend full tests:
192 passed, 1 existing warning

Flutter analyze:
passed

Flutter full tests:
266 passed

exact thirteen-file implementation review:
passed

git diff --check:
passed

HomeScreen implementation numstat:
115 additions / 0 deletions

independent in-flight guard:
accepted

three-or-more concurrent invocation coverage:
accepted

concurrent create-failure exactly-once coverage:
accepted

provider calls during concurrent invocation:
1

create calls during concurrent invocation:
1

transcript retained in public state:
false

VoiceInputDemo transcript wired:
false

real STT execution:
false

real network execution:
false

main runtime wiring:
false

automatic TTS start:
false

hard cancel supported:
false

explicit operator approval:
accepted

RT-4f3 status:
COMPLETED / ACCEPTED / PUSHED

RT-4f4 authorization:
AUTHORIZED / NOT_STARTED
```

## Test Boundary

Focused unit and widget tests use the accepted RT-4e model/client/controller and
fake/in-memory HTTP only. They use no socket, localhost, real Backend,
Framework, provider, microphone, STT, transcript persistence, or TTS execution.

Coverage includes valid final transcript, active stream rejection,
three-or-more simultaneous duplicate invocation with provider/create counts at
1, concurrent create failure with provider/create counts at 1, invalid
transcript/result ID, duplicate consumed ID, provider null/throw, controller
failure, long safe message bounding, disposal during a pending provider,
bounded consumed-ID memory, HomeScreen lifecycle, no VoiceInputDemo coupling,
and no TTS coupling.

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

RT-4f3 adds a provider-neutral interface and handoff boundary only.
RT-4f3 does not add a configured real transcript source. The private real-STT
operator result still does not automatically reach Flutter. RT-4f4 is
implemented and awaiting review for default-off configured Flutter runtime
wiring toward configured local Backend/FW text streaming and cooperative
cancel visible UI acceptance. RT-4f4 may claim real-STT-to-stream execution
only if a separately reviewed, safe, app-visible real transcript source is
configured. Without that separately reviewed source, RT-4f4 must not claim
real-STT transcript handoff acceptance. RT-5 TTS queue/flush/barge-in remains
excluded.

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

This is the historical thirteen-file RT-4f3 implementation surface. The later
acceptance documentation sync changes seven documentation files only and does
not modify the transcript model, handoff service, HomeScreen, tests, or the
dedicated gate script.
