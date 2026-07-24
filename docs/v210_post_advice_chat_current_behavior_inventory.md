# v2.1.0 post-advice chat current behavior inventory

Updated: 2026-07-24
Status: C-1a IMPLEMENTED / NOT_ACCEPTED
Purpose: record the accepted chat/session and Flutter UI behavior before C-1 runtime changes

## Interpretation rule

```text
Existing source boundary != clear user-facing lifecycle state
HTTP 404 != proof that a session specifically expired
Framework source metadata != normal-user unavailable/fallback copy
TTL/capacity bounds != bounded conversation turns
Mock-safe regression != configured Framework operator acceptance
```

This inventory is source-tree only. It does not read private Framework configuration, call an LLM provider, start a browser, expose prompts or replies, or modify released v2.0.0/v2.0.1 records.

## Accepted lifecycle baseline

The v2.0.x M-5 contract remains authoritative for temporary chat storage:

```text
POST_ADVICE_CHAT_TTL_SECONDS=1800
POST_ADVICE_CHAT_MAX_SESSIONS=100
successful get/message refreshes recency
capacity eviction is least-recently-used
storage is process-local and in-memory
```

C-1 must preserve the 30-minute idle TTL, 100-session default capacity, and LRU behavior unless a later separately reviewed contract intentionally changes them.

## Backend API and model boundary

The current routes are:

```text
POST /chat/sessions
GET  /chat/sessions/{session_id}
POST /chat/sessions/{session_id}/messages
```

`ChatSessionResponse` contains:

```text
session_id
status
source
context
messages
```

`ChatMessageResponse` contains:

```text
session_id
reply
source
messages
```

Current limitations:

```text
- created sessions always use status=active;
- there is no explicit turn count or turn-limit field;
- there is no lifecycle reason such as expired, evicted, unknown, or closed;
- expired, capacity-evicted, and unknown IDs all become the same HTTP 404 detail;
- the service returns None for every missing-session case, so the API cannot classify them;
- there is no app-facing retry/restart recommendation in the response contract.
```

## Session service behavior

`PostAdviceChatService` currently:

```text
- cleans expired sessions before create/get/message operations;
- refreshes last-used time after successful get or message;
- evicts the least-recently-used session before creating beyond capacity;
- stores the opening assistant message and then user/assistant message pairs;
- has no maximum-turn or maximum-message limit;
- has no explicit close operation;
- loses all sessions when the backend process restarts.
```

The existing `RLock` permits the optional initial user message to call the message path while session creation is holding the lock.

## Framework adapter outcome boundary

`FrameworkPostAdviceChatAdapter` already distinguishes internal outcomes:

```text
skipped
unavailable
blocked-live-message-gate
responded
provider/fallback statuses returned by the live-reply service
```

The current chat API does not expose that result status as a dedicated field. The Flutter UI can infer only from `source.engine`, `source.mode`, and assistant reply text.

Source modes already include:

```text
framework_text_chat_boundary
framework_text_chat_skipped
framework_text_chat_unavailable
framework_text_chat_live_message_blocked
framework_text_chat_live_message
provider-safe fallback modes
```

C-1 must continue to use released AI Character Framework public session boundaries only. It must not import Framework internals or move provider-specific logic into DRC.

## Flutter client boundary

`BackendApiClient` currently:

```text
- creates a post-advice session;
- sends messages to an existing session;
- does not fetch/resume a session through the GET route;
- converts every non-200 chat response into a generic Exception containing only the HTTP status;
- does not decode a structured lifecycle/error reason.
```

Therefore Flutter cannot distinguish expired, evicted, unknown, blocked, unavailable, or provider fallback solely from the client error type.

## Flutter HomeScreen state boundary

The HomeScreen currently owns chat state through independent values:

```text
_isStartingPostAdviceChat
_isSendingPostAdviceChatMessage
_postAdviceChatSkipped
_postAdviceChatError
_postAdviceChatSession
```

Current behavior:

```text
- advice creation clears prior chat state;
- 少し話す creates a session;
- 今日はここまで clears the local session and keeps DailyRecord/History visible;
- send displays generic errors through _formatUserFacingError;
- a message HTTP 404 leaves the stale session object in memory;
- while a stale session remains, 少し話す stays disabled;
- the user can recover indirectly by choosing 今日はここまで and starting again;
- framework unavailable/fallback states are shown mainly through technical source labels and assistant copy;
- session ID, source mode, and status are displayed in the normal chat card as diagnostics.
```

C-1 should separate normal-user lifecycle copy from optional operator diagnostics.

## Existing mock-safe regression boundary

Backend normal tests currently cover:

```text
- idle expiry;
- successful get refreshing TTL;
- successful message refreshing TTL;
- LRU capacity eviction;
- explicit cleanup;
- preserved HTTP 404 response shape;
- default and overridden TTL/capacity configuration.
```

Flutter widget tests currently cover:

```text
- mock chat session start and message send;
- visible Framework unavailable response/source mode;
- skip flow preserving DailyRecord/History.
```

Missing focused regression areas include:

```text
- bounded turn enforcement;
- explicit expired versus unknown/evicted classification;
- stale-session recovery without first pressing skip;
- structured unavailable/fallback/blocked display states;
- normal-user copy separated from operator diagnostics;
- deterministic restart/new-session behavior after lifecycle failure.
```

## C-1 small-commit split

```text
C-1a  CURRENT / NOT_COMPLETED  Current behavior inventory and implementation contract
C-1b  PLANNED                  Backend lifecycle outcomes, bounded turns, and mock-safe tests
C-1c  PLANNED                  Flutter lifecycle state, recovery UI, and aggregate C-1 acceptance
```

### C-1a boundary

```text
- docs/check only;
- no backend or Flutter runtime change;
- no existing backend or Flutter test change;
- pin the inspected source using normalized hashes;
- keep 1800-second TTL and 100-session capacity accepted and unchanged;
- keep C-1 parent NOT_COMPLETED;
- keep T-1, V-1, and R-1 PLANNED.
```

### C-1b planned responsibility

```text
- define provider-neutral app-facing lifecycle/outcome semantics;
- add a conservative configurable bounded-turn default;
- preserve existing routes and accepted TTL/capacity/LRU behavior;
- use deterministic clocks/fakes and no provider calls;
- keep compatibility behavior explicit where HTTP status or fields change.
```

### C-1c planned responsibility

```text
- introduce an explicit Flutter chat UI state rather than relying only on booleans;
- provide clear expired/restart, unavailable, blocked, fallback, active, sending, and skipped copy;
- clear stale sessions after terminal lifecycle failures and allow direct restart;
- keep operator source/session details outside the primary normal-user message;
- add focused model/widget tests and complete parent C-1 only after full review.
```

C-1a does not satisfy C-1b, C-1c, T-1, V-1, R-1, or release readiness.
