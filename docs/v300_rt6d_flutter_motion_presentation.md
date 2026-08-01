# Daily Rhythm Companion v3.0.0 RT-6d Flutter motion presentation

Updated: 2026-08-01

## Status

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6c: COMPLETED / ACCEPTED / PUSHED
RT-6d: IMPLEMENTED / AWAITING_REVIEW
implementation baseline: cd423fa2236ce16a7635f0c67460f2fa2fd210e9
implementation commit: none
RT-6e through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
commit/push authorization: false
```

## Framework baseline record

```text
Framework baseline version: 5.4.0
Framework canonical reference commit: d313eb6acb643103fe25988720ebee5976a04f78
Framework local source mode: external-vendored-snapshot
Framework execution in RT-6d: false
Framework vendor Git identity required: false
```

RT-6d imports or executes no Framework code. The version and canonical commit
are recorded because RT-6d mirrors the DRC-owned normalized result boundary
accepted in RT-6c. The local vendor copy remains outside DRC Git history.

## Purpose

RT-6d adds Flutter-only, provider-neutral presentation primitives for bounded
character-motion results. It follows the accepted RT-4e separation of immutable
models, an injectable client, a ChangeNotifier controller, and fake/in-memory
focused tests without HomeScreen integration.

The new Flutter layer accepts only DRC-owned normalized data. It does not accept
raw Framework objects, internal identifiers, arbitrary metadata, filesystem
paths, raw exception text, provider payloads, credentials, or operator evidence.

## Exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6d_flutter_motion_presentation.md
scripts/check_v300_rt6d_flutter_motion_presentation.py
app/lib/models/character_motion_presentation.dart
app/lib/services/character_motion_presentation_client.dart
app/lib/services/character_motion_presentation_controller.dart
app/test/character_motion_presentation_client_test.dart
app/test/character_motion_presentation_controller_test.dart
```

```text
documentation/static gate: 7 files
Flutter runtime: 3 files
Flutter focused tests: 2 files
total: exact 12 files
```

## Flutter model boundary

`app/lib/models/character_motion_presentation.dart` defines:

```text
CharacterMotionPresentationPhase
CharacterMotionLifecycleFact
CharacterMotionCue
CharacterMotionCommandIntent
CharacterMotionExecutionStatus
CharacterMotionPresentationRequest
CharacterMotionPresentationCommandResult
CharacterMotionPresentationResult
CharacterMotionPresentationProblem
CharacterMotionPresentationProblemException
CharacterMotionPresentationState
```

Presentation phases are bounded to:

```text
idle
applying
completed
ignored
disabled
unavailable
failed
closed
```

The source-fact, cue, and command-intent vocabularies mirror the accepted RT-6b
DRC-owned contract. The normalized execution status and result shape mirror the
accepted RT-6c application boundary.

Bounds:

```text
maximum commands: 3
maximum event types: 12
maximum source/character identifiers: 128 Unicode code points
maximum enum values: 64 Unicode code points
maximum reason code: 64 Unicode code points
maximum safe message: 256 Unicode code points
```

The result parser rejects unknown schemas/enums, unexpected fields,
inconsistent aggregate counts, non-contiguous command order, oversized event types, oversized public-safe strings, and inconsistent
completed/ignored/disabled lifecycle claims.

Every accepted result must preserve:

```text
adapter == mock
real_adapter_enabled == false
provider_execution_allowed == false
provider_execution_attempted == false
network_execution == false
```

## Injectable client boundary

`app/lib/services/character_motion_presentation_client.dart` defines an injected
transport function:

```dart
typedef CharacterMotionPresentationTransport =
    Future<Map<String, Object?>> Function(
      CharacterMotionPresentationRequest request,
    );
```

The client calls only that injected function and strictly parses the returned
DRC-owned map. It contains no HTTP, SSE, WebSocket, Backend path, Framework
import, provider client, VTS connection, Live2D runtime, token, or credential
logic. Raw transport exceptions become a fixed typed public-safe problem.

## ChangeNotifier controller boundary

`app/lib/services/character_motion_presentation_controller.dart` exposes one
immutable `CharacterMotionPresentationState`.

State transitions:

```text
idle -> applying -> completed | ignored | disabled | unavailable | failed
any non-closed state -> idle through reset()
any state -> closed through close()/dispose()
```

Only one active request is allowed. Simultaneous apply and active replacement
are rejected with a typed safe problem. There is no queueing, coalescing,
automatic retry, or automatic lifecycle subscription.

Each operation has a local generation. `reset()`, `close()`, and `dispose()`
invalidate the generation, so delayed fake/in-memory transport completion cannot
overwrite current state. No notification occurs after disposal.

The controller retains only the bounded request, normalized result, or safe
problem. It never retains raw maps, arbitrary metadata, transport objects,
HTTP bodies/headers, raw exceptions, paths, credentials, provider payloads, or
private logs.

## Focused tests

Client tests cover:

```text
completed/ignored/disabled/unavailable/failed parsing
maximum three ordered commands
maximum twelve event types
request bounds and public-safe serialization
unknown schema and enum rejection
unexpected field rejection
command count/order consistency
completed and inactive lifecycle consistency
mock-only safety flag enforcement
bounded identifier/reason/message enforcement
raw transport exception normalization
```

Controller tests cover:

```text
idle -> applying -> each terminal phase
single active request enforcement
reset/close/dispose stale completion rejection
terminal reset
closed apply rejection
safe typed failure state
listener order and idempotent close
no private/raw error retention
```

Normal focused tests use fake/in-memory transport only.

## Exact non-actions

RT-6d changes none of the following:

```text
app/lib/main.dart
app/lib/screens/home_screen.dart
app/lib/models/character_display_presentation.dart
app/lib/models/motion_demo.dart
app/lib/services/backend_api_client.dart
app/lib/widgets/character_display_card.dart
backend/**
vendor/**
Framework source
pubspec.yaml or lockfiles
platform manifests
assets
environment/configuration
API routes
versions/releases
existing tests
```

The current static character activity states remain idle/loading/speaking.
RT-6d does not claim those states are FW motion events. HomeScreen ownership,
configured runtime wiring, and visible character-motion presentation remain
RT-6e work. Configured local mock-motion acceptance remains RT-6f work. Real
Live2D/VTS execution remains blocked in RT-7.

## Verification contract

```text
python -m compileall -q backend scripts
python scripts/check_v300_rt6d_flutter_motion_presentation.py
python -m pytest -q

cd app
flutter analyze
flutter test test/character_motion_presentation_client_test.dart
flutter test test/character_motion_presentation_controller_test.dart
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
```

## Current claims

```text
Flutter provider-neutral motion presentation models: implemented
injected fake/in-memory presentation client: implemented
ChangeNotifier presentation controller: implemented
HomeScreen integration: false
configured real HTTP execution: false
Framework execution: false
provider/network/VTS/Live2D execution: false
RT-6e authorization: false
RT-6f authorization: false
RT-7 real adapter status: blocked
commit/push authorization: false
```
