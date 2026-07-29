# DRC v3.0.0 RT-4e Flutter stream client/controller

Updated: 2026-07-29

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4c: COMPLETED / ACCEPTED / PUSHED
RT-4d: COMPLETED / ACCEPTED / PUSHED
RT-4e: IMPLEMENTED / AWAITING_ACCEPTANCE
RT-4f: NOT_STARTED
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
SSE by UTF-8 blank-line frame boundaries, parses `id`, `event`, and `data`
fields, and deserializes only normalized DRC JSON event payloads.

The controller is a `ChangeNotifier` with immutable state. It exposes idle,
connecting, streaming, cancelRequested, completed, cancelled, failed, and closed
phases, rejects active-stream replacement, appends chunks incrementally, handles
cooperative cancel, closes local subscriptions after terminal events, and ignores
obsolete callbacks.

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

Candidate acceptance is pending local verification and explicit operator review.
