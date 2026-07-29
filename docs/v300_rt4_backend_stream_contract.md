# DRC v3.0.0 RT-4b Backend provider-neutral text stream contract

Updated: 2026-07-29

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4a: COMPLETED / ACCEPTED / PUSHED
RT-4a implementation commit: 235654e470f8c0cac17644ddf216ac7e6e223514
RT-4b: IMPLEMENTED / AWAITING_ACCEPTANCE
RT-4c: NOT_STARTED
FW baseline: clean v5.4.0 at d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-4b adds the DRC-owned Backend state machine needed to represent one
incremental LLM text response without adding transport or provider execution.
The checkpoint is deterministic, credential-free, network-free, Framework-free,
and fake-callback-only.

RT-4b deliberately separates these responsibilities:

```text
RT-4b owns:
- provider-neutral session and turn snapshots
- stream lifecycle and event vocabulary
- bounded text chunks
- monotonic per-session event sequence
- completed, cancelled, failed, and closed terminal payloads
- cooperative cancel-request state
- rejection of late or stale callbacks
- fake-only Backend regression tests

RT-4b does not own:
- FastAPI routes
- SSE or WebSocket transport
- active-session capacity, TTL, or disconnect cleanup
- Framework imports or session creation
- provider clients or external requests
- Flutter stream consumption or UI
- provider-level hard cancellation
- TTS queue control, output flush, or barge-in
```

## Added Backend models

File: `backend/app/models/realtime_text_stream.py`

Public DRC-owned models:

```text
RealtimeTextStreamState
RealtimeTextStreamEventType
RealtimeTextStreamTerminalOutcome
RealtimeTextStreamCallbackReason
RealtimeTextStreamSession
RealtimeTextStreamTurn
RealtimeTextStreamChunk
RealtimeTextStreamTerminal
RealtimeTextStreamEvent
RealtimeTextStreamCallbackResult
```

The session snapshot always reports:

```text
cancel_mode: cooperative
hard_cancel_supported: false
```

Those fields prevent a future UI or transport from mistaking an accepted
`TextChatSession.interrupt()` request for provider-level hard cancellation.

## Lifecycle contract

The fake-only state machine begins in `idle` and emits sequence numbers starting
at one. Every accepted lifecycle, chunk, or terminal event increments the same
session sequence exactly once. Rejected callbacks do not advance the sequence.

```text
idle
→ streaming
→ completed

idle
→ streaming
→ cancel_requested
→ cancelled

idle
→ streaming
→ failed

idle / streaming / cancel_requested / terminal
→ closed
```

A completed, cancelled, or failed session may start a later turn. The new turn
receives a different turn ID. A callback carrying an older turn ID is rejected
as `stale_turn` without mutating current state or text.

A second turn cannot replace an active turn. It is rejected as `active_turn`.

## Chunk and aggregate limits

Defaults owned by the Backend service:

```text
maximum characters per chunk: 512
maximum aggregate output characters: 4096
```

The service measures Python text characters and stores only accepted bounded
chunks. An oversized chunk terminalizes the turn as failed with
`chunk_limit_exceeded`. A chunk that would exceed the aggregate limit is not
stored; the existing bounded partial text is returned in a failed terminal with
`output_limit_exceeded`.

An empty chunk is ignored through an explicit rejected callback result and does
not advance the event sequence.

RT-4c may add transport byte limits and session/time limits. It must not weaken
these RT-4b character limits.

## Cooperative cancellation semantics

`request_cancel()` records a cooperative cancel request and emits one
`cancel_requested` event. It does not call Framework or a provider.

After cancellation is requested:

```text
- later text chunks are rejected;
- sequence does not advance for rejected chunks;
- cancel() emits a cancelled terminal; and
- complete() also resolves to cancelled so a completion/cancel race cannot be
  reported as successful completion after cancellation already won.
```

RT-4d will connect this state to FW v5.4.0 root-public `interrupt()`. It must
continue to report `hard_cancel_supported=false` unless a later released public
Framework contract proves otherwise.

## Failure and close behavior

`fail()` accepts only a public error code, public-safe message, and retryable
flag. It accepts no raw provider exception or payload. Codes are normalized to
a bounded lowercase identifier and messages are whitespace-normalized and
bounded.

`close()` emits a `closed` terminal containing only already accepted bounded
partial text. After close, every callback is rejected as `session_closed`.

## Exact RT-4b change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
backend/app/models/realtime_text_stream.py
backend/app/services/realtime_text_stream_service.py
backend/tests/test_realtime_text_stream_service.py
docs/v300_rt4_backend_stream_contract.md
scripts/check_v300_rt4_backend_stream_contract.py
```

## Protected non-change surface

```text
backend/app/main.py
backend/app/api/**
backend/app/models/realtime.py
backend/app/services/framework_realtime_normalizer.py
app/lib/**
app/test/**
app/pubspec.yaml
release_notes/**
```

No dependency, version metadata, platform permission, v2.x release artifact,
FW repository file, private audio, transcript, credential, provider payload,
private path, screenshot, LAN address, or operator evidence is part of RT-4b.

## Tests

Focused fake-only regressions verify:

```text
- deterministic start event and capability snapshot
- active-turn replacement rejection
- monotonic sequence across start, chunks, and terminal
- bounded chunk and aggregate output behavior
- cooperative cancel-request state
- late chunk rejection after cancel request
- cancel/completion race resolving to cancelled
- stale callback rejection after a later turn starts
- public failure normalization
- active-turn close and post-close callback rejection
- empty-chunk rejection without sequence advance
```

## Candidate acceptance

```text
compileall: pending operator execution
dedicated RT-4b gate: pending operator execution
focused Backend tests: pending operator execution
full Backend tests: pending operator execution
Flutter analyze/full tests: pending operator execution
exact ten-file diff review: pending
changed-content private scan: pending
git diff --check: pending
explicit operator approval: pending
RT-4c authorization: blocked pending RT-4b acceptance
```
