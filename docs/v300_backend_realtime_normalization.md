# DRC v3.0.0 RT-1b Backend Realtime Model and Normalization Boundary

Updated: 2026-07-26

Implementation state: IMPLEMENTED / NOT_ACCEPTED

## Purpose

RT-1b adds the first DRC-owned Backend realtime data boundary after the released
AI Character Framework v5.2.0 public-contract adoption gate.

This checkpoint does not start a realtime runtime. It gives later DRC services a
stable internal model that does not expose Framework enums, dataclasses,
provider objects, private paths, raw payloads, or version-specific object shapes.

## Added Backend boundary

```text
backend/app/models/realtime.py
backend/app/services/framework_realtime_normalizer.py
backend/tests/test_framework_realtime_normalizer.py
```

The model layer owns:

```text
RealtimeState
RealtimeEventType
RealtimeCapabilityStatus
RealtimeCapabilities
RealtimeEvent
RealtimeSessionSnapshot
```

The normalizer owns:

```text
Framework object / mapping read compatibility
Framework Enum value normalization
Framework event type to DRC event type mapping
Framework state to DRC state mapping
unknown future event preservation
public metadata sanitization
session-specific capability precedence
global capability snapshot fallback
DRC realtime session snapshot construction
```

## Capability precedence

FW v5.2.0 exports Voice Input, Realtime, interrupt/output-control, and Motion
public session contracts. Its inherited global `get_capabilities()` snapshot can
still report those boundaries as missing through the older v5.1 schema.

RT-1b therefore uses this order:

```text
1. v5.2.0 session-specific info / capability fields
2. global capability snapshot only as fallback
3. conservative unavailable defaults when no public metadata exists
```

This prevents DRC from treating a stale global snapshot as evidence that the
released v5.2.0 public session factories do not exist.

The normalized capability model separately records:

```text
public_contract_released
mock_contract_available
real_runtime_supported
real_runtime_configured
real_runtime_available
```

A released mock-safe contract is not treated as real provider/runtime success.

## Event normalization

The normalizer accepts either attribute objects or mappings. Known Framework
v5.2.0 events are converted to DRC-owned event names while the original event
string remains in `source_event_type`.

Unknown future events do not fail validation. They become:

```text
event_type: unknown
source_event_type: <original public event string>
state: unknown unless a safe state is supplied
```

The normalized event keeps only provider-neutral fields:

```text
session_id
turn_id
state
previous_state
boundary
public_error_code
safe_message
retryable
public_metadata
```

## Metadata safety

Metadata keys that look like credentials, tokens, authorization values, private
paths, local paths, raw provider payloads, or raw audio are replaced with
`<redacted>`.

Unsupported opaque objects are represented by their public type marker rather
than `repr(...)`, so object representations cannot accidentally expose private
paths or provider internals.

## Explicit non-goals

RT-1b does not add or change:

```text
FastAPI routes
WebSocket or SSE transport
microphone permission or capture
raw audio upload
Framework import at DRC module import time
real STT
real realtime orchestration
LLM streaming
provider-level hard cancellation
real TTS queue flush or playback stop
barge-in audio detection
Flutter models or UI
real Live2D / VTube Studio execution
Backend or Flutter version metadata
v2.x release records
```

## Historical gate policy

RT-0a through RT-1a were docs/test-only checkpoints whose source-tree gates
intentionally froze the pre-runtime Backend tree. RT-1b is the first accepted
v3 Backend code checkpoint, so those whole-tree immutability gates are
historical evidence and are not rerun as RT-1b child gates.

RT-1b uses its own source-tree gate plus the complete Backend and Flutter test
suites. The historical documents and accepted state markers remain unchanged.

## Verification

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_backend_realtime_normalization.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests/test_framework_realtime_normalizer.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

Expected implementation checkpoint:

```text
focused Backend tests: 6 passed
full Backend tests: 116 passed
Flutter regression baseline: 103 passed
real provider execution: false
Framework import: false
API route added: false
microphone used: false
realtime runtime started: false
```

## Phase state

```text
RT-1a  COMPLETED / ACCEPTED
RT-1b  COMPLETED / ACCEPTED
RT-1   COMPLETED / ACCEPTED
RT-2   CURRENT / NOT_COMPLETED
       guarded microphone permission/capture planning only; NOT_STARTED
```

## Acceptance record

Accepted on 2026-07-26 after all of the following passed:

```text
compileall: passed
RT-1b source/runtime gate: passed
focused Backend: 6 passed
full Backend: 116 passed, 1 existing warning
Flutter: 103 passed
git diff --check: passed
10-file diff review: passed
explicit operator approval: passed
Framework import: false
API route added: false
microphone used: false
provider execution: false
realtime runtime started: false
```

RT-1b acceptance completes parent RT-1. RT-2 guarded microphone permission and
capture planning is authorized, but no microphone access, capture runtime, or
real STT execution is authorized by this checkpoint.
