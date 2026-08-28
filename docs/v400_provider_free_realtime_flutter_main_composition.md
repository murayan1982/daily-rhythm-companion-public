# DRC-V4-6 Control C - main.dart default-off FW-v6 provider-free session composition

Status:
DRC-V4-6 Control C IMPLEMENTED / AWAITING_REVIEW

```text
baseline:
3ef11c87d8e12393ab6dbe8f3308ffe9a1ca6f43

implementation commit:
none

commit:
NOT_AUTHORIZED

push:
NOT_AUTHORIZED
```

## Exact Surface

```text
exact surface:
9 files / M6 A3 D0

MODIFY:
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
app/lib/main.dart

ADD:
docs/v400_provider_free_realtime_flutter_main_composition.md
scripts/check_v400_provider_free_realtime_flutter_main_composition.py
app/test/framework_v600_realtime_session_main_composition_test.dart

DELETE:
0
```

## Responsibility Split

```text
Control A:
configured runtime/factory

Control B:
HomeScreen explicit manual UI

Control C:
main.dart default-off composition
```

Control C composes the accepted Control A
`ConfiguredFrameworkV600RealtimeSessionRuntime` with the accepted Control B
`HomeScreen.frameworkV600RealtimeSessionControllerFactory` injection point.
It adds no new runtime, controller, client, model, or HomeScreen state machine.

## Lazy Semantics

```text
ConfiguredFrameworkV600RealtimeSessionRuntime creation:
YES

buildControllerFactory():
YES

FW-v6 controller factory invocation:
0

http.Client creation for FW-v6 session:
0

FW-v6 Backend request:
0

session open:
0

turn:
0

interrupt:
0

diagnostics:
0

close:
0
```

With the default flag-disabled runtime, `buildControllerFactory()` returns
null and HomeScreen remains unconfigured. With a valid enabled runtime,
HomeScreen reports configured, but no controller factory invocation, HTTP
client creation, Backend request, or session open occurs until the explicit
`Open Session` button is used.

## Capability Truth

```text
configured FW-v6 runtime/factory:
IMPLEMENTED / ACCEPTED

HomeScreen FW-v6 provider-free manual UI:
IMPLEMENTED / ACCEPTED

main.dart FW-v6 composition:
IMPLEMENTED / AWAITING_REVIEW

FW-v6 automatic startup network:
NO

FW-v6 automatic session open:
NO

explicit Open Session Backend HTTP:
YES

verification network:
NO / fake only

provider network:
NO

provider execution:
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

existing v3 replacement:
NO

/realtime/text replacement:
NO

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED
```

## Control State

```text
DRC-V4-6 Control A:
CLOSED

DRC-V4-6 Control B:
COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control B implementation commit:
3f9d38107f0306e023c127e68ce657cc4bd90b18

Control B final acceptance-sync commit:
3ef11c87d8e12393ab6dbe8f3308ffe9a1ca6f43

DRC-V4-6 Control C:
IMPLEMENTED / AWAITING_REVIEW

implementation baseline:
3ef11c87d8e12393ab6dbe8f3308ffe9a1ca6f43

implementation commit:
none

commit / push:
NOT_AUTHORIZED

DRC-V4-6 aggregate:
PARTIAL_READY / NOT_COMPLETED
```
