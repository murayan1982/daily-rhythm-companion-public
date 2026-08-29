# DRC-V4-6 Aggregate Acceptance Protocol - provider-free configured local Backend session acceptance

Status:
DRC-V4-6 Aggregate Final Acceptance Sync IMPLEMENTED / AWAITING_REVIEW

```text
Current small commit:
DRC-V4-6 Aggregate Final Acceptance Sync

Current implementation:
DRC-V4-6 Aggregate Final Acceptance Sync

Current implementation state:
IMPLEMENTED / AWAITING_REVIEW

final acceptance-sync baseline:
9f382cd787e132b98061b4cc6cf3b8dfbb50bde5

final acceptance-sync commit:
none

DRC-V4-6 Aggregate Acceptance Protocol:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

protocol baseline:
13127ac93054840caeff5ec12698ae82f36bb514

protocol implementation commit:
9f382cd787e132b98061b4cc6cf3b8dfbb50bde5

Corrective R1:
PASS / ACCEPTED

operator acceptance:
COMPLETED / VERIFIED / ACCEPTED / PASS

operator configured presentation:
PASS

operator pre-Open phase:
idle / PASS

operator pre-Open session:
not opened / PASS

operator Open Session:
PASS

operator Send:
PASS

operator turn outcome:
completed

operator turn safe projection:
PASS

operator Interrupt:
PASS

operator interrupt outcome:
no_active_turn

operator Diagnostics:
PASS

operator Close:
PASS

operator final phase:
closed

operator Framework distribution:
ai-character-framework 6.0.0 / PASS

operator provider execution:
NO / PASS

operator repository modified:
NO / PASS

operator post-run repository:
clean / PASS

stage:
NOT_AUTHORIZED / NOT_RUN

commit:
NOT_AUTHORIZED / NOT_RUN

push:
NOT_AUTHORIZED / NOT_RUN

DRC-V4-6 aggregate:
COMPLETED / VERIFIED / ACCEPTED / CLOSED

DRC-V4 aggregate:
PARTIAL_READY / NOT_COMPLETED
```

## Purpose

```text
DRC-V4-6 Aggregate Acceptance Protocol
provider-free configured local Backend session acceptance
```

This milestone defines acceptance criteria, operator preflight, operator action
sequence, safe evidence schema, automated-vs-operator evidence boundary, and a
static candidate checker. It does not execute operator acceptance and does not
introduce a new runtime, UI, or Backend capability.

This is not real provider acceptance.

## Existing Accepted Composition

```text
Backend provider-free FW-v6 API:
IMPLEMENTED / ACCEPTED

configured FW-v6 runtime/factory:
IMPLEMENTED / ACCEPTED

HomeScreen manual FW-v6 controls:
IMPLEMENTED / ACCEPTED

main.dart FW-v6 composition:
IMPLEMENTED / ACCEPTED
```

## Operator Acceptance Sequence

Fixed sequence:

```text
1. repository preflight
2. Backend environment preflight
3. local Backend start
4. Flutter app start with FW-v6 provider-free flag enabled
5. configured presentation confirmation
6. pre-Open state confirmation
7. explicit Open Session
8. explicit Send
9. explicit Interrupt
10. explicit Diagnostics
11. explicit Close
12. post-run repository/security confirmation
```

This sequence is not authorized for this implementation milestone.

## Backend Configuration

Accepted local Backend endpoint:

```text
http://127.0.0.1:8000
```

Existing Backend entrypoint:

```text
backend\run_dev.bat
```

Important: `run_dev.bat --framework` can install optional Framework/provider
SDK dependencies. That is separate from confirming that the
`ai-character-framework` distribution itself is already installed.

Operator preflight checks:

```text
distribution:
ai-character-framework

required version:
6.0.0
```

This protocol does not define a new Framework install procedure. Missing
installation or version mismatch is an operator-run STOP.

## Flutter Configuration

Operator run compile-time configuration:

```text
DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION=true

DRC_BACKEND_API_BASE_URL=http://127.0.0.1:8000
```

The concrete device and `flutter run` command are not fixed in this milestone.
They are selected after operator execution authorization by confirming the local
environment.

## Accepted API Paths

Exact paths:

```text
POST
/realtime/framework-v6/provider-free/sessions

POST
/realtime/framework-v6/provider-free/sessions/{sessionId}/turns

POST
/realtime/framework-v6/provider-free/sessions/{sessionId}/interrupt

GET
/realtime/framework-v6/provider-free/sessions/{sessionId}/diagnostics

DELETE
/realtime/framework-v6/provider-free/sessions/{sessionId}
```

The turn path must be plural `/turns`.

Turn request:

```json
{"input_text":"<exact operator input>"}
```

Interrupt accepted defaults:

```text
scope:
current_turn

reason:
host_app_request
```

## Operator PASS Criteria

Startup / pre-Open:

```text
FW-v6 configured presentation:
PASS

automatic FW-v6 Backend request:
0

automatic FW-v6 session open:
0
```

This does not claim zero network for the existing HomeScreen general Backend
initial load.

Open, from explicit `Open Session` only:

```text
configured local Backend:
reachable

FW-v6 provider-free session:
opened / usable

safe session projection:
presented
```

The raw session ID must not be stored in public operator evidence.

Send criteria:

```text
fixed non-sensitive input submitted exactly

accepted local Backend API path exercised

typed FrameworkV600RealtimeTurnResult received

safe UI projection presented

no raw JSON
no raw exception
no provider payload
no private information
```

A real LLM response is not required. The protocol validates the FW-v6
provider-free/mock-safe capability rather than a specific turn outcome value.

Interrupt criteria:

```text
explicit action only
accepted default scope/reason
typed safe interrupt result presented
```

Diagnostics criteria:

```text
explicit action only
typed safe diagnostics projection presented
```

Close criteria:

```text
explicit action only
accepted closed lifecycle reached
```

## Automated Historical Evidence Vs Operator Evidence

Already accepted as AUTOMATED / HISTORICAL:

```text
exact endpoint paths
HTTP methods
lazy controller/client factory creation
pre-Open request count = 0
explicit Open create request
exact Send input
Interrupt request boundary
Diagnostics request boundary
explicit Close
hidden DELETE = 0
safe typed UI projection
no automatic retry/timer/polling
```

The operator run must not add packet capture or raw HTTP logging to re-prove
these historical facts.

New OPERATOR / REAL LOCAL COMPOSITION confirmations:

```text
actual Flutter composition starts configured
actual local Backend is reachable
actual installed FW v6.0.0 provider-free session opens
Open -> Send -> Interrupt -> Diagnostics -> Close is operable
safe UI projection remains intact
provider execution is not introduced
existing v3 path is not replaced
repository remains clean
```

## Evidence Security

Operator evidence stays outside the repo.

Forbidden evidence:

```text
.env contents
API keys
credentials
raw HTTP request/response bodies
raw Backend logs
raw FW event payloads
transcripts
audio
screenshots
private filesystem paths
LAN/private IP addresses
provider SDK output
stack traces
raw session IDs
```

Sanitized results are allowed, for example:

```text
panel configured: PASS
pre-Open FW-v6 request: 0 / PASS
Open Session: PASS
session safe projection: PASS
Send: PASS
turn safe projection: PASS
Interrupt: PASS
Diagnostics: PASS
Close: PASS
provider execution: NO / PASS
repository modified: NO / PASS
```

`127.0.0.1` is allowed as the fixed loopback endpoint.

## Network Truth

```text
Backend HTTP capability:
YES

FW-v6 automatic startup request:
NO

FW-v6 automatic session open:
NO

explicit operator action local Backend HTTP:
YES

operator application traffic:
local loopback Backend

provider network:
NO

provider execution:
NO
```

Environment preparation/package installation traffic must not be mixed with
operator application traffic.

## Capability Truth

```text
microphone:
NO

STT:
NO

real LLM provider:
NO

TTS:
NO

audio playback:
NO

VTube Studio:
NO

motion:
NO

existing v3 replacement:
NO

/realtime/text replacement:
NO

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED
```

## Aggregate State

```text
DRC-V4-6 Control A: CLOSED
DRC-V4-6 Control B: CLOSED
DRC-V4-6 Control C: CLOSED

DRC-V4-6 Control A:
CLOSED

DRC-V4-6 Control B:
CLOSED

DRC-V4-6 Control C:
CLOSED

DRC-V4-6 Control C implementation commit:
8c807507e930b546f562acad97f52a6ba652b35f

DRC-V4-6 Control C final acceptance-sync commit:
13127ac93054840caeff5ec12698ae82f36bb514

Control C implementation commit:
8c807507e930b546f562acad97f52a6ba652b35f

Control C final acceptance-sync commit:
13127ac93054840caeff5ec12698ae82f36bb514

Current small commit:
DRC-V4-6 Aggregate Final Acceptance Sync

Current implementation:
DRC-V4-6 Aggregate Final Acceptance Sync

Current implementation state:
IMPLEMENTED / AWAITING_REVIEW

final acceptance-sync baseline:
9f382cd787e132b98061b4cc6cf3b8dfbb50bde5

final acceptance-sync commit:
none

DRC-V4-6 Aggregate Acceptance Protocol:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

protocol baseline:
13127ac93054840caeff5ec12698ae82f36bb514

protocol implementation commit:
9f382cd787e132b98061b4cc6cf3b8dfbb50bde5

Corrective R1:
PASS / ACCEPTED

operator acceptance:
COMPLETED / VERIFIED / ACCEPTED / PASS

operator configured presentation:
PASS

operator pre-Open phase:
idle / PASS

operator pre-Open session:
not opened / PASS

operator Open Session:
PASS

operator Send:
PASS

operator turn outcome:
completed

operator turn safe projection:
PASS

operator Interrupt:
PASS

operator interrupt outcome:
no_active_turn

operator Diagnostics:
PASS

operator Close:
PASS

operator final phase:
closed

operator Framework distribution:
ai-character-framework 6.0.0 / PASS

operator provider execution:
NO / PASS

operator repository modified:
NO / PASS

operator post-run repository:
clean / PASS

stage:
NOT_AUTHORIZED / NOT_RUN

commit:
NOT_AUTHORIZED / NOT_RUN

push:
NOT_AUTHORIZED / NOT_RUN

DRC-V4-6 aggregate:
COMPLETED / VERIFIED / ACCEPTED / CLOSED

DRC-V4 aggregate:
PARTIAL_READY / NOT_COMPLETED
```
