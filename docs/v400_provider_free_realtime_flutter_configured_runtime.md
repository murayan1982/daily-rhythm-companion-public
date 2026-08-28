# DRC-V4-6 Control A Configured Provider-free FW v6 Flutter Runtime

Status: DRC-V4-6 Control A COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED

```text
baseline:
26a4222eec724a7517f2e812dfe4bd039c5b511d

implementation commit:
246260fa9c92abc1df02a378b0ab1d84040cc208

commit:
COMPLETED

push:
COMPLETED
```

## Scope

DRC-V4-6 Control A adds a configured provider-free FW v6 Flutter
session runtime/factory. It creates no HomeScreen UI wiring, no main.dart
composition, no automatic session open, and no startup Backend request.

Implementation files:

```text
app/lib/services/configured_framework_v600_realtime_session_runtime.dart
app/test/configured_framework_v600_realtime_session_runtime_test.dart
```

The runtime returns an optional
`FrameworkV600RealtimeSessionController Function()?` from
`buildControllerFactory()`. When enabled and configured with a valid Backend
base URL, each invocation of that returned factory creates a fresh
`http.Client`, a fresh `FrameworkV600RealtimeSessionClient`, and a fresh
`FrameworkV600RealtimeSessionController`.

## Configuration

```text
compile-time flag:
DRC_V4_ENABLE_FRAMEWORK_V6_PROVIDER_FREE_SESSION

defaultValue:
false
```

`ConfiguredFrameworkV600RealtimeSessionRuntime.fromEnvironment()` uses
`BackendApiClient.baseUrl` as the configured base URL. The default HTTP client
factory is `http.Client.new`.

## Base URL Validation

The runtime validates `baseUrl.trim()`.

Accepted:

```text
absolute http://
absolute https://
non-empty host
optional port
optional path prefix
```

Rejected:

```text
empty
relative URL
non-http/https scheme
missing host
userInfo
fragment
```

Path prefixes are preserved. For example:

```text
baseUrl:
https://example.invalid:8443/api/

explicit controller.open() request:
https://example.invalid:8443/api/realtime/framework-v6/provider-free/sessions
```

## Required Semantics

Disabled runtime:

```text
buildControllerFactory(): null
HTTP client factory call: 0
HTTP request: 0
session open: 0
```

Invalid base URL:

```text
buildControllerFactory(): null
HTTP client factory call: 0
HTTP request: 0
exception exposed: no
```

Enabled valid base URL:

```text
runtime constructor HTTP client factory call: 0
runtime constructor HTTP request: 0
buildControllerFactory HTTP client factory call: 0
buildControllerFactory HTTP request: 0
returned factory invocation: creates fresh owned client/session client/controller
returned factory invocation HTTP request: 0
new controller state: idle
automatic open: 0
```

Only an explicit later `controller.open()` call may invoke the accepted V4-4
client `createSession()` path.

## Ownership

The factory product is owned by the future widget or binding that receives it.
The existing V4-4 lifecycle is unchanged.

```text
controller.dispose() closes owned HTTP client: YES
controller.dispose() silently performs Backend DELETE: NO
Backend session DELETE is limited to controller.close(): YES
```

## Capability Truth

```text
configured FW-v6 runtime/factory:
IMPLEMENTED / ACCEPTED

HomeScreen FW-v6 UI:
NOT_IMPLEMENTED

main.dart FW-v6 composition:
NOT_IMPLEMENTED

automatic startup network:
NO

automatic startup session open:
NO

provider execution:
NO

existing v3 runtime replacement:
NO

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED

DRC-V4 aggregate:
PARTIAL_READY
```

Network truth:

```text
Backend HTTP capability: YES
Control A automatic startup network: NO
verification network: NO / fake transport only
provider network: NO
external provider execution: NO
```

Accepted implementation evidence:

```text
DRC-V4-6 Control A:
COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED

implementation baseline:
26a4222eec724a7517f2e812dfe4bd039c5b511d

implementation commit:
246260fa9c92abc1df02a378b0ab1d84040cc208

Corrective R1:
PASS

exact implementation surface:
9 files

implementation surface:
MODIFY 5 / ADD 4 / DELETE 0

dedicated candidate checker:
PASS / HISTORICAL

post-commit/final-sync checker rerun:
NOT_RUN / BY_DESIGN

focused Backend:
62 PASS

Flutter analyze:
PASS

focused Flutter:
51 PASS

full Flutter:
551 PASS

protected Backend:
PASS

protected main.dart:
PASS

protected HomeScreen:
PASS

protected V4-4 boundary:
PASS

protected V4-5 readiness doc:
PASS

git diff --check:
PASS

post-push working tree:
clean

GitHub main after implementation push:
246260fa9c92abc1df02a378b0ab1d84040cc208

final acceptance-sync baseline:
246260fa9c92abc1df02a378b0ab1d84040cc208

final acceptance-sync commit:
none

acceptance-sync commit / push:
NOT_AUTHORIZED
```

Historical checker handling:

```text
dedicated candidate checker:
PASS / HISTORICAL

post-commit/final-sync checker rerun:
NOT_RUN / BY_DESIGN
```

Corrective R1 history:

```text
Corrective R1:
PASS

corrective repo surface:
README.md only

other 8 implementation candidate files changed by corrective:
0
```

## Forbidden Behavior

Control A does not implement:

```text
app/lib/main.dart wiring
HomeScreen wiring
automatic session open
app startup FW-v6 request
HomeScreen startup FW-v6 request
constructor HTTP request
automatic refresh
provider SDK execution
microphone
voice capture
STT
LLM provider
TTS
audio playback
VTube Studio
motion runtime
existing integrated voice-turn connection
existing realtime text stream connection
/realtime/text replacement
v3 runtime replacement
unified realtime pipeline claim
```

## Control B/C Boundary

```text
DRC-V4-6 Control B:
PROPOSED / NOT_AUTHORIZED

DRC-V4-6 Control C:
PROPOSED / NOT_AUTHORIZED

DRC-V4-6 aggregate:
PARTIAL_READY / NOT_COMPLETED
```

## Historical V4-5 State

```text
DRC-V4-5:
COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED

implementation commit:
838ab047bb7a7e96f26f3c6ab436a1b9241c2c0e

final acceptance-sync commit:
26a4222eec724a7517f2e812dfe4bd039c5b511d
```
