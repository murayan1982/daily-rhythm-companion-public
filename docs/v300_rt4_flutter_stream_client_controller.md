# DRC v3.0.0 RT-4e Flutter stream client/controller

Updated: 2026-07-30

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4c: COMPLETED / ACCEPTED / PUSHED
RT-4d: COMPLETED / ACCEPTED / PUSHED
RT-4e: COMPLETED / ACCEPTED / PUSHED
RT-4f: AUTHORIZED / NOT_STARTED
```

## Purpose

RT-4e adds Flutter-side stream consumption primitives for the accepted Backend
RT-4c/RT-4d text stream boundary. It does not integrate HomeScreen, connect STT
transcripts, run a real Backend, import Framework, or call any provider.

## Flutter Boundary

Added:

```text
app/lib/models/realtime_text_stream.dart
app/lib/services/realtime_text_stream_client.dart
app/lib/services/realtime_text_stream_controller.dart
```

The model layer mirrors the Backend public contract:

```text
maximum chunk: 512 characters
maximum accumulated output: 4096 characters
monotonic positive sequence
cancel_mode=cooperative
hard_cancel_supported=false
```

The client accepts an injected `http.Client`, creates stream sessions, consumes
SSE by incremental UTF-8 blank-line frame boundaries, safely handles CRLF/LF
HTTP chunk boundaries, parses `id`, `event`, and `data` fields, deserializes
only normalized DRC JSON event payloads, and enforces same-origin
`events_path` and `cancel_path` values.

The controller is a `ChangeNotifier` with immutable state. It exposes idle,
connecting, streaming, cancelRequested, completed, cancelled, failed, and closed
phases, rejects active-stream replacement, appends chunks incrementally, handles
cooperative cancel, validates monotonic sequence/session/turn values, validates
event type/state/payload/terminal consistency, enforces Unicode code-point
chunk/output/safe-message bounds, closes local subscriptions after failed,
terminal, and dispose paths, rejects simultaneous `start()` calls, preserves
local `cancelRequested` when a delayed `streamStarted` event arrives, and
ignores obsolete callbacks.

## Non-Actions

```text
HomeScreen integration: false
STT transcript connection: false
real Backend execution in tests: false
Framework import: false
DRC provider client: false
provider-level hard cancel claim: false
reconnect/resume: false
WebSocket: false
dependency change: false
version change: false
TTS queue/flush/barge-in: false
```

## Exact Change Surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
app/lib/models/realtime_text_stream.dart
app/lib/services/realtime_text_stream_client.dart
app/lib/services/realtime_text_stream_controller.dart
app/test/realtime_text_stream_client_test.dart
app/test/realtime_text_stream_controller_test.dart
docs/v300_rt4_flutter_stream_client_controller.md
scripts/check_v300_rt4_flutter_stream_client_controller.py
```

## Tests

Normal tests use fake/in-memory streams and fake `http.BaseClient` only:

```text
successful create and incremental SSE parsing
UTF-8 split across response chunks
multiple SSE frames in one response chunk
SSE field split across response chunks
completed, cancelled, and failed terminals
cooperative cancel request
malformed JSON and missing sequence
duplicate/out-of-order sequence
oversized chunk/output rejection
active-stream replacement rejection
late event ignored after terminal/dispose
no input echo in public state/errors
```

## Acceptance

RT-4e is accepted and pushed at
`1cfe6134b0d19a4d14ebcf3ec76812ce07dac261`.

Accepted RT-4e behavior:

```text
Flutter normalized realtime stream models added
injectable HTTP/SSE client added
ChangeNotifier stream controller added
incremental UTF-8 SSE parsing accepted
CRLF/LF HTTP chunk-boundary handling accepted
same-origin events_path and cancel_path enforcement accepted
monotonic sequence/session/turn validation accepted
event type/state/payload/terminal validation accepted
Unicode code-point chunk/output/safe-message bounds accepted
cooperative cancel only
hard_cancel_supported=false
failed/terminal/dispose subscription cleanup accepted
active-stream replacement and simultaneous start rejection accepted
local cancel remains cancelRequested when a delayed streamStarted event arrives
fake/in-memory transport only in normal tests
HomeScreen integration remains absent
STT transcript handoff remains absent
real Backend/Framework/provider execution was not performed by RT-4e
TTS queue/flush/barge-in remains RT-5 work
```

Verification record:

```text
implementation commit: 1cfe6134b0d19a4d14ebcf3ec76812ce07dac261
implementation pushed: true
compileall: passed
dedicated RT-4e gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter RT-4e tests: 33 passed
Flutter full tests: 233 passed
exact twelve-file review: passed
changed-content private scan: passed
git diff --check: passed
explicit operator approval: accepted
RT-4e status: COMPLETED / ACCEPTED / PUSHED
RT-4f authorization: AUTHORIZED / NOT_STARTED
```
