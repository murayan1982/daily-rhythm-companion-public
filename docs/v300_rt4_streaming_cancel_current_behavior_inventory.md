# DRC v3.0.0 RT-4a streaming/cancel current behavior inventory

Updated: 2026-07-29

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4a: IMPLEMENTED / AWAITING_ACCEPTANCE
DRC accepted baseline HEAD/origin: eecf13d7dce653f341721ad007ca39aca91f497e
DRC RT-3 implementation commit: 5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c
FW release: v5.4.0
FW HEAD/tag: d313eb6acb643103fe25988720ebee5976a04f78
RT-4b: NOT_STARTED
```

## Purpose

RT-4a freezes the actual accepted DRC and released FW v5.4.0 behavior before
adding LLM streaming or cancellation runtime. It separates current full-response
chat, public soft-cancel support, missing DRC transport/client work, and
unsupported provider-level hard cancellation. This checkpoint is docs/test-only.

## Inspected DRC source

```text
backend/app/services/framework_text_chat_drc_live_reply.py
backend/app/services/framework_text_chat_adapter.py
backend/app/services/post_advice_chat_service.py
backend/app/api/chat.py
backend/app/main.py
backend/app/models/realtime.py
backend/app/services/framework_realtime_normalizer.py
backend/app/api/voice_input_demo.py
app/lib/services/backend_api_client.dart
app/lib/services/backend_voice_input_staging_consumer.dart
app/lib/screens/home_screen.dart
backend/tests/**
app/test/**
```

## Current DRC text-chat execution

The configured post-advice Framework path creates a public text-chat session
and calls `session.ask(prompt)`. The returned response is normalized into one
complete reply string. The `POST /chat/sessions/{session_id}/messages` route
returns one `ChatMessageResponse`; it does not stream chunks.

Current properties:

```text
full-response session.ask(): implemented and previously accepted
DRC ask_stream() use: absent
DRC text chunk model: absent
monotonic chunk sequence: absent
stream terminal outcome model: absent
active stream/session cancellation registry: absent
disconnect-driven stream cleanup: absent
provider-level hard cancel: absent
```

The existing `PostAdviceChatService` owns bounded synchronous chat sessions
with TTL, capacity, turn limits, and lifecycle outcomes. Those accepted limits
do not constitute a streaming lifecycle or cancellation boundary.

## Current DRC transport and Flutter client

Backend routes are normal request/response FastAPI handlers. The current source
contains no `StreamingResponse`, `text/event-stream` response, or WebSocket
route for LLM output. `backend/app/main.py` includes no RT-4 router.

Flutter uses `Future`-based API methods for session creation and message send,
then replaces the complete chat session after one response. It has no EventSource
or WebSocket stream client, stream event parser, sequence validation, cancel
controller, or incremental assistant-message UI.

## Existing DRC realtime normalization

`backend/app/models/realtime.py` already defines provider-neutral lifecycle and
event names such as thinking/responding, text-chat started/completed, interrupt
requested/accepted/completed/unsupported, and terminal states. It does not
define an LLM text chunk payload, chunk sequence, final text aggregate, or
stream-specific terminal outcome. RT-4b may extend this DRC-owned boundary
without replacing the accepted RT-1 normalization models.

## RT-3 transcript handoff state

RT-3 accepts one bounded microphone artifact, stages it privately, executes the
released FW v5.4.0 public STT boundary under explicit operator gates, and returns
one completed transcript result. The transcript is not connected to a streaming
LLM turn, and incremental STT transcript delivery is not claimed by RT-4.

## Released FW v5.4.0 public boundary

Required root-public exports for RT-4 planning:

```text
TextChatSession
TextChatSessionInfo
TextChatSessionEvent
TextChatStateChange
create_text_chat_session
RealtimeSession
RealtimeSessionInfo
InterruptRequest
InterruptResult
```

`TextChatSessionInfo` reports streaming, events, and interrupt support. Public
`ask()` joins `ask_stream()` chunks. Public `ask_stream()` emits response-started,
response-chunk, response-completed/error events and checks an interrupt flag
between yielded provider chunks.

Public `interrupt()` sets the session interrupt flag and reports acceptance.
This is cooperative soft cancellation. It does not prove that an in-flight
provider request was cancelled immediately, that provider billing stopped, or
that no later provider-side work occurred.

The public `RealtimeSession` remains a mock-safe orchestration skeleton. Its
public info reports `real_runtime_enabled=false`, `hard_cancel_supported=false`,
and `tts_queue_flush_supported=false`. RT-4 must not claim unified real
RealtimeSession execution, hard cancellation, output flush, or barge-in.

## RT-4 implementation decision

DRC may proceed against FW v5.4.0 for incremental LLM text delivery and
cooperative cancellation using only root-public text-session APIs. No DRC
provider client or Framework internal-module import is authorized.

```text
AUTHORIZED FOR RT-4:
- public create_text_chat_session()
- public TextChatSession.ask_stream()
- public text-session events/state callbacks
- public TextChatSession.interrupt() as cooperative cancel
- public TextChatSession.close()/dispose()
- DRC-owned stream event normalization, transport, limits, and UI state

NOT AUTHORIZED / NOT CLAIMED:
- Framework internal imports
- DRC custom provider client or direct provider API
- provider-level hard cancel
- real unified Framework RealtimeSession orchestration
- TTS queue cancel/flush or barge-in
- raw provider event/payload forwarding
```

## Accepted RT-4 small-commit split

### RT-4a — current behavior inventory and split

Docs/test-only. Freeze source facts, FW semantics, exact change surface, stop
rules, and RT-4b through RT-4f ownership.

### RT-4b — Backend provider-neutral stream lifecycle

Add DRC-owned stream session/turn/chunk/terminal models and a deterministic
fake-only service. Include monotonic sequence, bounded text, completed/cancelled/
failed/closed terminal outcomes, and stale-callback rejection. Add no route,
Framework import, provider call, or Flutter change.

### RT-4c — bounded Backend SSE transport and cancel request

Add a bounded SSE `text/event-stream` transport and cancel request boundary with active-session
capacity, idle/max-duration limits, one-consumer ownership, chunk/output limits,
disconnect cleanup, and public-safe errors. Provider execution remains fake-only.

Provisional route contract:

```text
POST /realtime/text/sessions
GET  /realtime/text/sessions/{session_id}/events
POST /realtime/text/sessions/{session_id}/cancel
```

### RT-4d — FW v5.4.0 public streaming adapter

Connect the RT-4b/c service only to FW root-public text-session creation,
`ask_stream()`, callbacks, `interrupt()`, and close/dispose. Normal tests inject
a fake public session. Report `cancel_mode=cooperative` and
`hard_cancel_supported=false`.

### RT-4e — Flutter stream client/controller

Add app-owned stream events, sequence validation, lifecycle/controller states,
cancel request handling, disconnect/error mapping, and fake transport tests.
Do not integrate HomeScreen yet.

### RT-4f — UI and configured acceptance

Integrate incremental assistant text, connect the accepted RT-3 transcript to
one LLM streaming turn, verify PC and smartphone Web incremental display and
cooperative cancel, and accept parent RT-4. Keep transcript text, private paths,
provider payloads, screenshots, and operator evidence outside Git.

## Parent RT-4 acceptance floor

```text
real incremental LLM text streaming: required
DRC normalized start/chunk/terminal event consumption: required
bounded session/turn/chunk/output lifecycle: required
transport disconnect cleanup: required
cooperative cancel request and terminal state: required
provider-level hard cancel: false / unsupported unless FW later proves it
real unified FW RealtimeSession: not claimed
TTS queue/flush/barge-in: deferred to RT-5
incremental STT transcript: not claimed
```

## Exact RT-4a change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt4_streaming_cancel_current_behavior_inventory.md
scripts/check_v300_rt4_streaming_cancel_current_behavior_inventory.py
```

## Non-actions

RT-4a changes no Backend/Flutter runtime, existing tests, dependency, API route,
configuration, version, Framework source, provider client, network execution,
audio, transcript, private path, release record, tag, or fixed ZIP. It does not
start a session, stream a response, request cancellation, or execute STT/LLM/TTS.

## Candidate acceptance

```text
compileall: pending operator execution
dedicated RT-4a gate: pending operator execution
Backend full tests: pending operator execution
Flutter analyze/full tests: pending operator execution
exact seven-file review: pending
changed-content private scan: pending
git diff --check: pending
explicit operator approval: pending
RT-4b authorization: blocked pending RT-4a acceptance
```
