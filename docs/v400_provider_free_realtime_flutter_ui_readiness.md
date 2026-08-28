# DRC-V4-5 Provider-free FW v6 Flutter UI / Configured Runtime Readiness

Status: DRC-V4-5 IMPLEMENTED / AWAITING_REVIEW

Baseline: `cf82518cd0b96a752ad92151bb3d706a88b9147c`

This document is an inventory/readiness contract only. It records future
adoption seams and constraints without implementing UI wiring, configured
runtime wiring, app startup behavior, Backend behavior, provider execution, or
replacement of existing accepted v3 runtime paths.

## Historical V4-4 State

```text
DRC-V4-4: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED
DRC-V4-4 implementation commit: a05d62447e85be28d674201853d0667aef11e2ae
DRC-V4-4 final acceptance-sync commit: cf82518cd0b96a752ad92151bb3d706a88b9147c
```

## A. Accepted V4-4 Flutter Boundary

```text
FrameworkV600Realtime model projections: READY / ACCEPTED
FrameworkV600RealtimeSessionClient: READY / ACCEPTED
FrameworkV600RealtimeSessionController: READY / ACCEPTED
```

This boundary already provides:

```text
provider-free Backend HTTP session create
text turn
interrupt
diagnostics
close
bounded response parsing
safe problem projection
session/turn/generation identity validation
close lifecycle protection
late result rejection
```

DRC-V4-5 does not redefine or modify this accepted behavior.

## B. Existing Application Composition Boundary

Current source inventory:

```text
app/lib/main.dart
app/lib/screens/home_screen.dart
```

Current `main.dart` already composes existing configured v3-era runtimes and
injects factories/bindings into `DailyRhythmCompanionApp` / `HomeScreen`.
Current `HomeScreen` already exposes dependency-injection seams for existing
controller/binding factories.

```text
HomeScreen dependency-injection seam:
READY_FOR_EXACT_IMPLEMENTATION_REVIEW

main.dart configured-runtime composition seam:
READY_FOR_EXACT_IMPLEMENTATION_REVIEW
```

DRC-V4-5 does not modify `app/lib/main.dart` or
`app/lib/screens/home_screen.dart`.

## C. Future V4 Adoption Boundary

Future work only:

```text
configured provider-free FW v6 Flutter runtime/factory
HomeScreen explicit manual FW-v6 session controls/presentation
main.dart default-off configured composition
```

State:

```text
NOT_IMPLEMENTED
NOT_AUTHORIZED in DRC-V4-5
```

## Current Nonclaims

```text
HomeScreen wiring:
NOT_IMPLEMENTED

main.dart wiring:
NOT_IMPLEMENTED

configured runtime wiring:
NOT_IMPLEMENTED

automatic startup session open:
NOT_IMPLEMENTED / NOT_AUTHORIZED

automatic startup Backend request:
NOT_IMPLEMENTED / NOT_AUTHORIZED

existing v3 realtime replacement:
NOT_AUTHORIZED

provider execution:
OUT_OF_SCOPE

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED
```

## Readiness Classification

```text
V4-4 Flutter model/client/controller:
READY / ACCEPTED

V4-3 Backend provider-free HTTP API:
READY / ACCEPTED

HomeScreen dependency-injection seam:
READY_FOR_EXACT_IMPLEMENTATION_REVIEW

main.dart configured-runtime composition seam:
READY_FOR_EXACT_IMPLEMENTATION_REVIEW

configured provider-free FW-v6 runtime:
NOT_IMPLEMENTED

HomeScreen provider-free FW-v6 session UI:
NOT_IMPLEMENTED

main.dart provider-free FW-v6 composition:
NOT_IMPLEMENTED

automatic startup network:
NOT_AUTHORIZED

automatic startup session open:
NOT_AUTHORIZED

replacement of existing v3 realtime flow:
NOT_AUTHORIZED

provider execution:
OUT_OF_SCOPE

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED

DRC-V4 aggregate:
PARTIAL_READY
```

## Future UI Behavior Constraints

Future provider-free V4 UI must be:

```text
default-off
explicit user action only
no HTTP request from:
constructor
initState
app startup
HomeScreen startup
automatic refresh
```

Future manually exposed lifecycle may include:

```text
idle
opening
ready
turnRunning
closing
closed
failed
```

Explicit controls may eventually include:

```text
open session
send text turn
interrupt
request diagnostics
close session
```

No other automatic behavior is authorized.

## Future Scope Exclusions

The first V4 UI adoption must not automatically connect:

```text
microphone
voice capture
STT
LLM provider
TTS
audio playback
VTube Studio
motion runtime
existing integrated voice-turn flow
existing realtime text stream flow
/realtime/text replacement
```

DRC-V4-5 itself implements none of these.

## Network Truth

```text
Backend HTTP capability:
YES

current V4-4 HTTP usage:
explicit client method invocation only

automatic startup network:
NO

verification network:
NO / fake transport only

provider network:
NO

external provider execution:
NO
```

## Ownership Inventory

```text
Who owns HTTP client?
future configured runtime / binding layer

Who creates FrameworkV600RealtimeSessionController?
future injected controller factory

Who owns the controller lifecycle?
the widget/binding receiving the factory product

Who calls close()?
explicit user action or separately reviewed bounded owner cleanup

Does controller construction make HTTP?
NO

Does client construction make HTTP?
NO

Does HomeScreen construction make FW-v6 HTTP?
NO

Does app startup open a FW-v6 session?
NO

Does dispose() imply a hidden Backend DELETE?
NO
```

DRC-V4-5 does not change V4-4 implementation to achieve these statements.

## Proposed Next Split

### DRC-V4-6 Control A

```text
Configured provider-free FW v6 Flutter runtime/factory
default-off
no HomeScreen modification
no main.dart modification
injected HTTP client
no automatic session open
no provider execution
```

### DRC-V4-6 Control B

```text
HomeScreen explicit manual FW-v6 session controls
fake/widget acceptance first
no main.dart configured production wiring
no automatic open
no existing v3 realtime replacement
```

### DRC-V4-6 Control C

```text
main.dart default-off configured composition
explicit compile-time/environment opt-in
no automatic session open
no provider execution
no v3 runtime replacement
```

### DRC-V4-6 aggregate

```text
provider-free configured local Backend session acceptance
```

DRC-V4-6 numbering/split is established by DRC-V4-5 inventory. It was not a
pre-existing canonical checkpoint before DRC-V4-5.

## V4-5 Boundary

```text
runtime behavior changes:
0

app changes:
0

Backend changes:
0

existing checkers changed:
0

commit:
NOT_AUTHORIZED

push:
NOT_AUTHORIZED
```
