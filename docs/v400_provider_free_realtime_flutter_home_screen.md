# DRC-V4-6 Control B - HomeScreen manual FW-v6 provider-free session UI

Status:
DRC-V4-6 Control B IMPLEMENTED / AWAITING_REVIEW

```text
baseline:
9bba7db5ed20abf6a0ffa1444fa37b340f3189cd

implementation commit:
none

commit:
NOT_AUTHORIZED

push:
NOT_AUTHORIZED
```

## Exact Surface

```text
exact surface 9 files
M6 / A3 / D0

MODIFY:
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
app/lib/screens/home_screen.dart

ADD:
docs/v400_provider_free_realtime_flutter_home_screen.md
scripts/check_v400_provider_free_realtime_flutter_home_screen.py
app/test/framework_v600_realtime_session_home_screen_widget_test.dart

DELETE:
0
```

## Control State

```text
Control A:
CLOSED

Control B:
IMPLEMENTED / AWAITING_REVIEW

Control C:
PROPOSED / NOT_AUTHORIZED

main.dart changes:
0

Backend changes:
0
```

## Capability Truth

```text
configured FW-v6 runtime/factory:
IMPLEMENTED / ACCEPTED

HomeScreen FW-v6 provider-free manual UI:
IMPLEMENTED / AWAITING_REVIEW

main.dart FW-v6 composition:
NOT_IMPLEMENTED

automatic startup network:
NO

automatic session open:
NO

explicit user action Backend HTTP:
YES

provider network:
NO

external provider execution:
NO

existing v3 replacement:
NO

/realtime/text replacement:
NO

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED
```

## Manual Lifecycle

The HomeScreen adds an optional
`frameworkV600RealtimeSessionControllerFactory` dependency. The factory is
not called by the constructor, State constructor, initState, build,
automatic refresh, existing initial loading, or app startup. The first
controller is created only by the explicit `Open Session` button.

Open creates a fresh controller from the injected factory, registers the
HomeScreen listener, and then calls `controller.open()`. A closed controller
is not reused: the next explicit Open removes the old listener, disposes the
old controller, creates a fresh controller, registers the listener, and opens
again.

Send uses the dedicated HomeScreen text field and calls
`controller.runTurn(inputText: inputText)` only when the controller is ready
and the trimmed input is non-empty. The UI does not truncate or rewrite the
input. The input is cleared after a successful ready-state turn.

Interrupt calls `controller.interrupt()` with the accepted default
`current_turn` / `host_app_request` contract. Diagnostics calls
`controller.diagnostics()`. Close calls `controller.close()` only from the
explicit Close lifecycle.

HomeScreen disposal removes the listener, disposes the controller, and
disposes the FW-v6 text controller. It does not call `controller.close()`;
therefore widget disposal performs no hidden Backend DELETE.

## Safe Presentation

The UI presents only the typed/safe controller projection:

```text
phase
sessionId
latestTurnResult.outcome
latestTurnResult.safeMessage
latestInterruptResult.outcome
latestDiagnostics.state
latestDiagnostics.phase
problem.code
problem.message
```

It does not display raw exception details, stack traces, raw JSON, HTTP
bodies, provider payloads, credentials, private paths, audio, transcript logs,
LAN/private IPs, provider SDK output, or private provider state.

## Acceptance Boundary

```text
automatic startup network:
NO

automatic session open:
NO

explicit user action Backend HTTP:
YES

verification network:
NO / fake only

provider network:
NO

external provider execution:
NO

microphone:
NO

STT:
NO

LLM provider:
NO

TTS:
NO

audio playback:
NO

VTube Studio:
NO

motion:
NO
```

The widget test uses fake HTTP/client/controller wiring only and validates
the explicit request boundaries for:

```text
POST /realtime/framework-v6/provider-free/sessions
POST /realtime/framework-v6/provider-free/sessions/{sessionId}/turns
POST /realtime/framework-v6/provider-free/sessions/{sessionId}/interrupt
GET /realtime/framework-v6/provider-free/sessions/{sessionId}/diagnostics
DELETE /realtime/framework-v6/provider-free/sessions/{sessionId}
```
