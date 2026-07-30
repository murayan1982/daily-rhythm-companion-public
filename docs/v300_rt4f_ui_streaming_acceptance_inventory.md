# DRC v3.0.0 RT-4f1 UI streaming acceptance inventory

Updated: 2026-07-30

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4e: COMPLETED / ACCEPTED / PUSHED
RT-4f: CURRENT / NOT_COMPLETED
RT-4f1: COMPLETED / ACCEPTED / PUSHED
RT-4f2: AUTHORIZED / NOT_STARTED
RT-4f3: NOT_STARTED
RT-4f4: NOT_STARTED
Current small commit: RT-4f2 AUTHORIZED / NOT_STARTED
Current implementation step: HomeScreen stream presentation and controller lifecycle wiring with injected fake stream client/controller and bounded manual input
Current implementation state: AUTHORIZED / NOT_STARTED
Current implementation commit: none
Last accepted small commit: RT-4f1 COMPLETED / ACCEPTED / PUSHED at f54e8638f0255b28e015702bc64b624a6d4a36af
Next action: inspect and begin RT-4f2 only; do not begin RT-4f3 transcript handoff
RT-4e implementation commit: 1cfe6134b0d19a4d14ebcf3ec76812ce07dac261
RT-4e acceptance docs commit: 964cbae19728618e85cef0917f747f21ae5c5e4e
RT-4f1 implementation commit: f54e8638f0255b28e015702bc64b624a6d4a36af
```

## Purpose

RT-4f1 records the current HomeScreen, metadata-only voice-input demo path,
absent app-visible real-STT transcript handoff, accepted RT-4e Flutter stream
client/controller boundary, Backend realtime routes, configured local streaming
boundary, minimum UI acceptance requirements, and protected boundaries before
RT-4f runtime wiring starts.

This commit is docs/test-only. Runtime behavior does not change.

## HomeScreen Ownership

Inspected paths:

```text
app/lib/screens/home_screen.dart
app/lib/main.dart
app/lib/services/backend_api_client.dart
app/lib/services/backend_voice_input_staging_consumer.dart
app/lib/services/microphone_capture.dart
app/lib/services/microphone_capture_host_audio_handoff.dart
app/lib/services/record_microphone_capture_engine.dart
app/test/backend_voice_input_staging_consumer_test.dart
app/test/microphone_capture_host_audio_handoff_test.dart
app/test/widget_test.dart
app/test/post_advice_chat_lifecycle_widget_test.dart
```

Current facts:

- `HomeScreen` constructor injects `BackendApiClient apiClient` and optional `VoiceOutputAudioEngine voiceOutputAudioEngine`.
- `main.dart` constructs `const HomeScreen()` and does not provide realtime stream client/controller injection or configuration.
- `_HomeScreenState` owns loading/error booleans, voice-input demo response/error state, post-advice chat session/problem/error state, selected character/mood state, Google Health diagnostics state, and a voice-output player controller.
- `_HomeScreenState` owns `_postAdviceChatMessageController` and `_voiceOutputAudioPlayerController`.
- `initState()` creates the voice-output player controller, attaches one listener, loads initial data, refreshes demo status, and refreshes Google Health UX/checks.
- `dispose()` removes the voice-output listener, disposes the voice-output player controller, and disposes the post-advice chat text controller.
- Existing presentation uses booleans for progress indicators, bounded public error strings, problem cards, status chips, diagnostic rows, and terminal/lifecycle display in the post-advice chat section.
- The current voice-input demo section sends a metadata-only request and displays request state, capability, input mode, transcript display text, safe message, checks, and candidate names.
- The current post-advice chat section starts a normal chat session after advice creation, sends full user messages, updates the session with full responses, and supports skip/restart lifecycle.
- HomeScreen currently has no import of `realtime_text_stream.dart`, `realtime_text_stream_client.dart`, or `realtime_text_stream_controller.dart`.
- HomeScreen currently has no realtime stream controller field, listener, start/cancel action, incremental output display, or stream terminal UI.

## RT-3 Transcript Availability

Inspected paths:

```text
app/lib/models/voice_input_demo.dart
app/lib/services/backend_api_client.dart
app/lib/services/backend_voice_input_staging_consumer.dart
app/lib/screens/home_screen.dart
backend/app/models/voice_input_demo.py
backend/app/api/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
backend/app/services/framework_voice_input_fake_handoff.py
backend/app/services/framework_voice_input_openai_fake_executor.py
backend/app/services/framework_voice_input_openai_real_operator.py
backend/tests/test_voice_input_fake_handoff_api.py
backend/tests/test_voice_input_openai_fake_executor_api.py
backend/tests/test_framework_voice_input_openai_real_operator.py
```

Current facts:

- `VoiceInputDemoRequestResponse` has a nullable `transcript` field and `displayTranscript` can render it when present.
- HomeScreen calls `BackendApiClient.submitVoiceInputDemoRequest()`, which posts to the metadata-only `/demo/voice-input` placeholder.
- `VoiceInputDemoService.submit_request()` always returns `accepted=False`, `request_state="not_started"`, and `transcript=None`.
- Metadata-only voice-input demo transcript: always null in production.
- Accepted real RT-3 transcript reaches Flutter/HomeScreen: false.
- Fake Backend transcript routes exist for staged fake handoff and OpenAI fake executor responses, but they are not wired to any Flutter/HomeScreen consumer.
- Fake Backend transcript routes wired to Flutter: false.
- The accepted real STT transcript is stored as the private `_transcript` field of `FrameworkVoiceInputOpenAIRealOperatorResult` and is exposed only through `private_transcript` to the private operator caller.
- Real-STT transcript public API route: absent.
- Real-STT transcript Flutter handoff: absent.
- App-owned transcript-to-stream handoff: absent.
- Transcript is not forwarded to post-advice chat, LLM, or realtime stream endpoints.
- The current source has no app-visible accepted real-STT transcript to connect.
- RT-4f3 must first add the missing app-owned provider-neutral handoff boundary.
- The current HomeScreen voice-input demo request sends metadata and a safe text hint; it does not send captured audio from HomeScreen.
- `BackendVoiceInputStagingConsumer` creates a path-free staging handle through `takeStagedArtifact()` only; it does not execute STT or retrieve a transcript.
- Existing fake/widget injection points include `HomeScreen(apiClient: fakeClient)` and fake voice-input Backend clients in widget tests.
- RT-3 staging and fake/real operator paths are Backend/operator boundaries. RT-4f1 does not read raw audio, transcripts, provider payloads, private paths, screenshots, credentials, or operator evidence.
- Lifecycle after success/cancel/failure remains owned by existing response/error state. There is no app-owned transcript-to-stream handoff lifecycle yet.

## RT-4e Integration Boundary

Inspected paths:

```text
app/lib/models/realtime_text_stream.dart
app/lib/services/realtime_text_stream_client.dart
app/lib/services/realtime_text_stream_controller.dart
app/test/realtime_text_stream_client_test.dart
app/test/realtime_text_stream_controller_test.dart
```

Current facts:

- `RealtimeTextStreamClient` is constructed with a required `baseUrl`, a required injected `http.Client`, and an optional `maximumSseEventBytes`.
- `createSession(inputText:)` posts to `/realtime/text/sessions` and returns a normalized create response.
- `streamEvents(createResponse)` opens the accepted same-origin `eventsPath`, parses SSE incrementally, validates event order/session/turn/payload, and yields normalized events until terminal.
- `cancel(createResponse)` posts to the accepted same-origin `cancelPath`.
- `events_path` and `cancel_path` (`eventsPath` and `cancelPath` in Flutter) must be absolute same-origin paths with no scheme, authority, host, network-path reference, relative path, or fragment.
- Flutter enforces same-origin `eventsPath` and `cancelPath` resolution before opening events or cancel requests.
- `RealtimeTextStreamController` is constructed with a `RealtimeTextStreamClient`.
- Controller public interface is `state`, `start(inputText:)`, `cancel()`, and `dispose()`.
- Public state fields appropriate for UI include `phase`, `outputText`, `lastSequence`, `cancelMode`, `hardCancelSupported`, `createResponse`, `terminal`, `problem`, `isActive`, and `isTerminal`.
- The controller rejects simultaneous or active replacement starts with `active_stream_replacement_rejected`.
- Cancellation is cooperative. `hardCancelSupported` is always false.
- Local cancel moves phase to `cancelRequested`; a delayed `streamStarted` does not move it back to streaming.
- Failed, terminal, and dispose paths release the SSE subscription.
- Normal tests use fake or in-memory transports and fake HTTP clients only.

## Backend Configured Path

Inspected paths:

```text
backend/app/api/realtime_text.py
backend/app/services/realtime_text_stream_transport.py
backend/app/services/framework_realtime_text_stream_adapter.py
backend/app/config.py
backend/app/main.py
backend/tests/test_realtime_text_stream_transport.py
backend/tests/test_framework_realtime_text_stream_adapter.py
```

Current facts:

- `POST /realtime/text/sessions` creates one bounded stream session and returns `events_path` and `cancel_path`.
- `GET /realtime/text/sessions/{session_id}/events` attaches the single SSE consumer and streams normalized RT-4 events.
- `POST /realtime/text/sessions/{session_id}/cancel` requests cooperative cancellation and returns a public-safe cancel response.
- Backend CORS is configured from `WEB_CORS_ORIGINS`; the default value allows local Flutter use.
- Framework text streaming is default-off through `DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM`.
- Default-safe behavior uses the provider-free transport registry when Framework streaming is not enabled.
- The FW v5.4.0 adapter boundary uses root-public `create_text_chat_session()`, `ask_stream()`, `interrupt()`, and close/dispose behavior only.
- Configured real acceptance in RT-4f4 would prove local Backend/FW streaming reaches visible UI state and that cooperative cancel is requested.
- Configured real acceptance would not prove provider-level immediate hard cancellation, TTS queue control, transcript persistence, or production hosting readiness.
- RT-4f makes no provider-level immediate hard cancellation claim.

## UI Acceptance Requirements

RT-4f must visibly satisfy these minimum behaviors before parent RT-4 acceptance:

- an explicit user action starts exactly one stream;
- provider-neutral transcript input or bounded manual test input is visibly identifiable without persisting private text by default;
- connecting, streaming, cancelRequested, completed, cancelled, failed, and closed state are visible;
- incremental generated text visibly updates;
- cancel affordance is enabled only while valid;
- duplicate starts are blocked;
- errors are bounded and public-safe;
- transcript text, provider payloads, private paths, credentials, screenshots, and raw operator evidence are not committed or persisted by default;
- no automatic TTS starts;
- no provider-level hard-cancel claim is made.

## Protected Boundaries

RT-4f must not:

- add a DRC provider client;
- import Framework internal modules;
- weaken same-origin checks;
- add reconnect/resume or WebSocket;
- add always-on or background microphone behavior;
- persist raw audio or transcripts by default;
- do not add TTS queue/flush/barge-in;
- claim provider-level immediate cancellation;
- modify the FW repository;
- change dependencies, versions, or platform permissions unless a later reviewed split proves it necessary.

## Resolved RT-4f Split

```text
RT-4f1
COMPLETED / ACCEPTED / PUSHED
Current behavior inventory and exact small-commit split.
Docs/test-only. No runtime change.

RT-4f2
AUTHORIZED / NOT_STARTED
Flutter HomeScreen stream presentation and controller lifecycle wiring with
injected fake stream client/controller and bounded manual test input. No real
Backend, Framework, provider, or STT handoff. Widget/fake tests only.

RT-4f3
NOT_STARTED
Define and implement the missing app-owned transcript-to-stream handoff
boundary. Connect an injected/fake provider-neutral transcript result to
exactly one stream start. The current source has no app-visible accepted
real-STT transcript to connect. RT-4f3 must first add the missing app-owned
provider-neutral handoff boundary. Fake transcript and fake stream tests only.
No real provider/operator execution.

RT-4f4
NOT_STARTED
Configured local Backend/FW streaming and cooperative cancel operator execution
and visible UI acceptance. Real-STT-to-stream acceptance can be performed only
if a safe transcript transport/exposure boundary is separately reviewed and
exists; without that boundary, RT-4f4 does not complete or claim real STT
transcript handoff. Private local environment only. No committed transcripts,
provider payloads, screenshots, private paths, LAN IPs, credentials, or
operator evidence.
```

## Non-Actions

```text
Runtime behavior changed: false
HomeScreen changed: false
main.dart changed: false
backend_api_client.dart changed: false
Dart runtime/tests changed: false
Backend runtime/tests changed: false
pubspec changed: false
version changed: false
platform permissions changed: false
release notes changed: false
Framework repository changed: false
real network execution: false
provider-level hard cancel claimed: false
TTS queue/flush/barge-in added: false
RT-4f2 started: false
RT-4f3 started: false
RT-4f4 started: false
```

## Acceptance Record

```text
implementation commit: f54e8638f0255b28e015702bc64b624a6d4a36af
implementation pushed: true
compileall: passed
dedicated RT-4f1 gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 233 passed
exact seven-file review: passed
git diff --check: passed
factual transcript inventory correction: accepted
explicit operator approval: accepted
RT-4f1 status: COMPLETED / ACCEPTED / PUSHED
RT-4f2 authorization: AUTHORIZED / NOT_STARTED
```

## Exact Change Surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt4f_ui_streaming_acceptance_inventory.md
scripts/check_v300_rt4f_ui_streaming_acceptance_inventory.py
```

This is the historical seven-file RT-4f1 implementation surface. The later
acceptance documentation sync changes six documentation files only and does not
modify the dedicated gate script.
