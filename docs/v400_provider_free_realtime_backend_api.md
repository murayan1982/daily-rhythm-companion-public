# DRC-V4-3 Provider-Free FW v6 Realtime Backend API

Status: IMPLEMENTED / AWAITING_REVIEW

```text
baseline HEAD: 384006073aa9e8757c904cb89d9bcd62a2b9fb35
DRC-V4-1: CLOSED / ACCEPTED
DRC-V4-2: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED
DRC-V4-3: IMPLEMENTED / AWAITING_REVIEW
DRC-V4-3 exact surface: exact 12 files
Commit: NOT_AUTHORIZED
Push: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
current released version: v3.0.0 RELEASED / ACCEPTED
DRC v4 release status: development work / not released
Framework release: v6.0.0
Framework annotated tag target: 61e15f62d1ecc5faee016abae82200f8de56c5dd
Framework official ZIP: ai-character-framework_v6.0.0.zip
Framework official ZIP SHA-256: 6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2
Framework root-public inventory: 127 names / frozen
```

## Purpose

DRC-V4-3 exposes the accepted DRC-V4-2 provider-free installed-SDK root-public
FW v6 RealtimeSession adapter through a bounded DRC-owned FastAPI Backend API.
It does not replace or modify the existing accepted v3 realtime implementation.

```text
FastAPI API
-> DRC-V4-3 process-local registry
-> existing DRC-V4-2 provider-free adapter
-> lazy root framework import only inside the existing adapter
```

The new V4-3 API files do not directly import Framework, do not mutate
`sys.path`, `sys.modules`, import caches, or CWD, do not discover Framework
checkout/vendor paths, and do not probe Framework signatures.

## Endpoint Contract

Exact prefix:

```text
/realtime/framework-v6/provider-free
```

Endpoints:

```text
POST   /realtime/framework-v6/provider-free/sessions
POST   /realtime/framework-v6/provider-free/sessions/{session_id}/turns
POST   /realtime/framework-v6/provider-free/sessions/{session_id}/interrupt
GET    /realtime/framework-v6/provider-free/sessions/{session_id}/diagnostics
DELETE /realtime/framework-v6/provider-free/sessions/{session_id}
```

`POST /sessions` constructs `FrameworkV600RealtimeSessionAdapter()`, calls
`open()`, and registers successful sessions by the canonical FW `session_id`.
It does not generate a separate DRC session id. Unavailable adapter results are
returned as HTTP 503 with a bounded `FrameworkV600RealtimeApiProblem`.

`POST /sessions/{session_id}/turns` accepts only `input_text`, which must be
non-empty and no longer than 4096 characters. It calls only
`await adapter.run_turn(input_text=request.input_text)`. Typed failed turn
results remain normal HTTP 200 responses.

`POST /sessions/{session_id}/interrupt` accepts only the DRC-V4-2 FW v6
provider-free interrupt vocabulary.

Allowed scopes:

```text
current_turn
llm_stream
tts_queue
voice_output
motion
all
```

Allowed reasons:

```text
user_barge_in
user_cancel
new_turn_started
session_closed
timeout
host_app_request
provider_failure
```

Defaults:

```text
scope: current_turn
reason: host_app_request
```

Invalid scope or reason is rejected by request validation with HTTP 422.

`GET /sessions/{session_id}/diagnostics` returns only the accepted
`FrameworkV600DiagnosticsSnapshot` shape. It contains no transcript, input text,
response text, raw event payloads, provider payloads, credentials, private
paths, or network details.

`DELETE /sessions/{session_id}` is idempotent. Present sessions are closed and
removed from the registry with HTTP 204. Missing sessions also return HTTP 204.
No tombstone is retained, and the old id is no longer usable.

Unknown turn, interrupt, and diagnostics session ids return HTTP 404 with code
`session_not_found`; the supplied id is not echoed in the message.

## Registry Boundary

```text
registry storage: process-local / in-memory / non-persistent
MAX_SESSIONS: 8
identity: canonical FW session_id only
capacity: 8 accepted; 9th create rejected with HTTP 429
capacity error code: session_capacity_reached
auto reopen: false
single-active-turn reimplementation: false
adapter factory: injectable for provider-free tests
```

The registry protects dictionary access and does not hold its global registry
lock across a complete async turn.

## Non-Execution Boundary

```text
provider-free only: true
real_runtime_enabled: False
provider execution: False
network: False
microphone: False
real STT: False
real LLM: False
real TTS: False
playback: False
VTube Studio / real motion: False
Flutter wiring: False
existing v3 runtime replacement: False
```

Critical non-claim: FW v6.0.0 does NOT provide a production real unified
`RealtimeSession.run_turn()` pipeline coordinating real STT -> streaming LLM ->
TTS -> motion. DRC-V4-3 does not claim or enable that real unified pipeline.

The existing `/realtime/text` v3 path remains retained and untouched. Existing
accepted v3 real adapters remain retained; removal of v3 real adapters is
NOT_AUTHORIZED. The fixed FW v5.5.0 integration remains preserved.

DRC-owned responsibilities outside FW ownership remain outside this checkpoint:

```text
Flutter microphone permission / foreground lifecycle
product UX and explicit opt-in policy
DailyRecord / sleep / mood / character context
host-local playback final control
presentation state
persistence
```

## Verification

Required verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v400_provider_free_realtime_backend_api.py
python -m pytest -q backend/tests/test_framework_v600_realtime_api.py backend/tests/test_framework_v600_realtime_session_adapter.py
python -m pytest -q backend/tests --basetemp <fresh-outside-repo-path>

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v400_provider_free_realtime_backend_api.py
git diff --check
git status --short
git diff --stat
git diff --name-only
```

The fixed FW v6.0.0 SDK smoke remains NOT_RUN /
OFFICIAL_ZIP_NOT_SUPPLIED / NON_BLOCKING unless an official ZIP is separately
supplied. DRC-V4-3 does not download Framework.
