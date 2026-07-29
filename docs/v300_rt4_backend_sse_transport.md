# DRC v3.0.0 RT-4c bounded Backend SSE transport and cancel boundary

Updated: 2026-07-29

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4a: COMPLETED / ACCEPTED / PUSHED
RT-4b: COMPLETED / ACCEPTED / PUSHED
RT-4c: COMPLETED / ACCEPTED / PUSHED
RT-4c implementation commit: 72622cab2e73699adaff4b628cfbc4b14323a23a
RT-4d: COMPLETED / ACCEPTED / PUSHED
RT-4d implementation commit: f713f515eef723a1d51cfbe35c1dfe16e3547420
RT-4e: AUTHORIZED / NOT_STARTED
DRC RT-4b baseline HEAD: 7e1e10e2ca33dd76ee963fcda31c2c5f800b4901
FW v5.4.0 HEAD/tag: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-4c exposes the accepted RT-4b provider-neutral stream events through a
bounded Backend Server-Sent Events transport. It adds session creation, one
SSE consumer, a separate cooperative cancel request, timeout/capacity limits,
and disconnect cleanup. It does not execute Framework or a provider.

## Public routes

```text
POST /realtime/text/sessions
GET  /realtime/text/sessions/{session_id}/events
POST /realtime/text/sessions/{session_id}/cancel
```

The create request accepts one bounded `input_text` value. The Backend keeps it
only in the bounded in-memory entry for the future RT-4d adapter. It is not
echoed by the create response, SSE events, cancel response, logs, or errors.

The create response returns opaque session/turn identifiers, relative event and
cancel paths, configured limits, `cancel_mode=cooperative`, and
`hard_cancel_supported=false`.

## SSE contract

The event route returns `text/event-stream` with no-cache/no-store,
`X-Accel-Buffering: no`, and `nosniff`. Every frame is UTF-8 and uses:

```text
id: <monotonic sequence>
event: <normalized RT-4b event type>
data: <compact JSON RealtimeTextStreamEvent>
```

Only normalized DRC models are serialized. Raw provider events, exceptions,
payloads, credentials, paths, transcripts, or Framework objects are forbidden.

## Bounds

Defaults:

```text
idle TTL: 120 seconds
maximum stream duration: 60 seconds
active session capacity: 8
maximum pending events per session: 32
maximum serialized SSE event: 32768 bytes
RT-4b maximum chunk: 512 characters
RT-4b maximum aggregate output: 4096 characters
single consumer per session: required
```

All settings are positive environment-backed values. Event-byte settings are
clamped to at least 1024 bytes so a public-safe terminal remains deliverable.
The transport does not weaken the RT-4b character limits.

When capacity is full, creation returns HTTP 429. A second consumer returns
HTTP 409. Missing sessions return HTTP 404. Expired, disconnected, or already
consumed sessions return HTTP 410 with bounded public-safe problem details.

If the pending buffer fills, queued data is discarded and replaced by one
retryable `stream_event_buffer_exceeded` failed terminal. If a serialized event
would exceed the byte limit, it is replaced by a deliverable failed terminal
without repeating the partial generated text.

## Cooperative cancellation

The cancel route emits `cancel_requested` and then a `stream_cancelled`
terminal at the DRC transport boundary. RT-4c has no Framework/provider worker
to interrupt. RT-4d will connect the same request to root-public
`TextChatSession.interrupt()` while preserving:

```text
cancel_mode: cooperative
hard_cancel_supported: false
provider-level immediate cancellation: not claimed
```

## Timeout and disconnect cleanup

An attached stream is failed with a retryable public terminal when idle TTL or
maximum duration wins. An unattached expired session is removed before new
creation/lookups. When an SSE consumer disconnects before seeing a terminal,
the Backend closes and removes the session and clears the private in-memory
input. A terminal consumed by the one allowed consumer is also removed.

There is no worker, background producer, reconnect/resume buffer, WebSocket,
or multi-consumer fan-out in RT-4c.

## Exact RT-4c change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
backend/.env.example
backend/app/config.py
backend/app/main.py
backend/app/api/realtime_text.py
backend/app/models/realtime_text_stream_transport.py
backend/app/services/realtime_text_stream_transport.py
backend/tests/test_realtime_text_stream_transport.py
backend/tests/test_temporary_lifecycle_config.py
docs/v300_rt4_backend_sse_transport.md
scripts/check_v300_rt4_backend_sse_transport.py
```

## Protected non-change surface

```text
backend/app/services/realtime_text_stream_service.py
backend/app/models/realtime_text_stream.py
backend/app/services/framework_text_chat_*.py
backend/app/services/framework_realtime_normalizer.py
app/lib/**
app/test/**
app/pubspec.yaml
release_notes/**
AI Character Framework repository
```

No dependency, version, platform permission, audio, transcript, credential,
provider payload, private path, LAN address, screenshot, operator evidence,
release artifact, tag, or release record is part of RT-4c.

## Tests

Focused tests cover route creation without input echo, monotonic SSE frames,
headers, cooperative cancellation, public-safe 404/410 problems, active
capacity, one-consumer ownership, idle/max-duration terminals, bounded pending
events, event-byte overflow replacement, disconnect cleanup, compact UTF-8
serialization, whitespace-only input rejection, and configuration defaults,
overrides, and invalid-value fallback.

## Acceptance result

```text
implementation commit: 72622cab2e73699adaff4b628cfbc4b14323a23a
implementation pushed: true
compileall: passed
dedicated RT-4c gate: passed in commit-scoped reconstructed candidate
focused Backend tests: 16 passed
full Backend tests: 192 passed
Flutter analyze: passed
Flutter tests: 200 passed
exact fifteen-file review: passed
changed-content private scan: passed
git diff --check: passed
explicit operator approval: accepted
RT-4c status: COMPLETED / ACCEPTED / PUSHED
RT-4d status: COMPLETED / ACCEPTED / PUSHED
RT-4e authorization: AUTHORIZED / NOT_STARTED
```
