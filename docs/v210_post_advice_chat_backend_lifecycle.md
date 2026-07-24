# v2.1.0 post-advice chat Backend lifecycle and outcome contract

Updated: 2026-07-24
Status: C-1b COMPLETED / ACCEPTED
Parent phase: C-1 CURRENT / NOT_COMPLETED

## Purpose

C-1b adds a provider-neutral Backend contract for post-advice chat lifecycle and
latest-operation outcomes while preserving the accepted temporary-resource bounds.
It is mock-safe and does not call AI Character Framework, an LLM provider, or any
other external service during normal checks.

## Preserved accepted bounds

```text
POST_ADVICE_CHAT_TTL_SECONDS=1800
POST_ADVICE_CHAT_MAX_SESSIONS=100
successful get/message refreshes idle recency
capacity eviction remains least-recently-used
storage remains process-local and in-memory
```

C-1b adds one new conservative bound:

```text
POST_ADVICE_CHAT_MAX_TURNS=8
```

A turn is one accepted user message and its assistant reply. The optional
`initial_user_message` counts as the first turn. The final allowed response is
returned normally and marks the session `turn_limit_reached`. A later send returns
HTTP 409 with a restartable structured problem.

## Structured lifecycle model

`ChatLifecycle` is added to session and message responses:

```text
state
turn_count
turn_limit
can_send_message
can_restart
```

Supported C-1b lifecycle states are:

```text
active
turn_limit_reached
```

Existing `ChatSessionResponse.status` remains present and mirrors the lifecycle
state so older clients keep receiving the field they already parse.

## Structured outcome model

`ChatOutcome` is added to session and message responses:

```text
kind
can_continue
can_restart
user_message
technical_code
```

Provider-neutral kinds are:

```text
mock
pending
configured
fallback
unavailable
blocked
skipped
```

`user_message` is normal-user copy and does not contain environment-variable or
operator-gate instructions. `technical_code` preserves a safe status marker for
optional diagnostics. Raw prompts, replies in logs, provider payloads, credentials,
and exceptions are not added to Public records.

## Missing-session classification

The Backend keeps a bounded terminal-reason cache containing only session ID,
reason, and ordering metadata. It does not retain removed message bodies.
The cache is limited to `POST_ADVICE_CHAT_MAX_SESSIONS` entries.

HTTP 404 now distinguishes:

```text
session_expired
session_evicted
session_not_found
```

The body uses FastAPI's existing `detail` wrapper and a structured problem:

```json
{
  "detail": {
    "code": "session_expired",
    "message": "Chat session not found",
    "user_message": "...",
    "can_restart": true
  }
}
```

The English compatibility message remains `Chat session not found`; the exact
response shape intentionally changes from a string detail to a structured object
so C-1c can recover deterministically.

Turn-limit rejection uses:

```text
HTTP 409
code=turn_limit_reached
can_restart=true
```

The limited session remains readable through GET so the UI can show its final
messages and offer a new-session action.

## Compatibility and non-change boundary

C-1b preserves:

```text
POST /chat/sessions
GET  /chat/sessions/{session_id}
POST /chat/sessions/{session_id}/messages
30-minute default idle TTL
100-session default capacity
LRU eviction
mock-safe default conversation path
released Framework public adapter boundary
existing source metadata fields
```

C-1b intentionally changes:

```text
- Backend chat responses gain lifecycle/outcome fields;
- missing-session detail becomes structured;
- post-limit sends return HTTP 409;
- Backend config gains POST_ADVICE_CHAT_MAX_TURNS;
- Backend tests cover outcomes and restartable lifecycle failures.
```

C-1b does not change:

```text
app/lib/**
app/test/**
Flutter parsing or UI recovery behavior
Framework adapter implementation
real Framework/LLM execution
TTS, character display, release metadata, tags, or release assets
```

Flutter ignores the added response fields until C-1c. The existing Flutter generic
HTTP exception behavior therefore remains unchanged in this commit.

## Mock-safe regression coverage

Focused Backend tests cover:

```text
- accepted TTL refresh and expiry;
- LRU capacity eviction;
- expired versus evicted versus unknown HTTP 404 codes;
- turn counting including initial_user_message;
- final allowed response and HTTP 409 after the limit;
- bounded terminal-reason cache;
- configured, fallback, unavailable, blocked, skipped, and mock outcome mapping;
- default, override, and invalid max-turn configuration.
```

Tests use deterministic clocks and fake adapters. They do not read credentials,
private env files, `backend/local_data`, or network resources.

## C-1b accepted completion record

```text
implementation commit: 3055995
compileall: passed
C-1a / C-1b source-tree checks: passed
W-1 through W-5 checks: passed
v2.0.x guards: passed
focused Backend tests: 17 passed
backend pytest: 110 passed
Flutter test: 57 passed
diff review / operator approval: passed
Backend runtime changed: true
Backend tests changed: true
Flutter runtime changed: false
Flutter tests changed: false
real Framework/LLM execution: false
release records changed: false
parent C-1 completed: false
```

C-1b was completed and accepted on 2026-07-24. C-1c and parent C-1 were subsequently completed and accepted; T-1 is CURRENT / NOT_COMPLETED
and will consume the structured Backend fields in Flutter. Parent C-1 remains
CURRENT / NOT_COMPLETED.
