# Daily Rhythm Companion v3.0.0 RT-6d Flutter motion presentation

Updated: 2026-08-01

## Accepted state

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6c: COMPLETED / ACCEPTED / PUSHED
RT-6d: COMPLETED / ACCEPTED / PUSHED
implementation baseline: cd423fa2236ce16a7635f0c67460f2fa2fd210e9
implementation commit: 0f220b792feb7ebb82c5871a794731aa1327439a
implementation surface: exact 12 files
acceptance-sync surface: exact 7 documentation/static-gate files
RT-6e: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
acceptance-sync commit/push: NOT_AUTHORIZED
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
are recorded because the Flutter model mirrors the DRC-owned normalized result
boundary established around the FW v5.4.0 mock session. The ignored vendor copy
is not required to expose a Git HEAD or clean status for this Flutter-only step.

## Accepted exact implementation surface

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

The acceptance-state sync changes only the seven documentation/static-gate
files. The accepted three Flutter runtime files and two focused test files
remain unchanged.

## Accepted Flutter model boundary

`app/lib/models/character_motion_presentation.dart` defines immutable,
provider-neutral DRC-owned contracts for:

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

The Flutter vocabulary mirrors the accepted RT-6b lifecycle facts, cues, and
command intents. It strictly accepts the RT-6c normalized result schema
`drc.v3.framework-mock-motion-execution.1` and enforces:

```text
maximum commands: 3
maximum event types: 12
maximum identifier length: 128 Unicode code points
maximum expression length: 64 Unicode code points
maximum safe message length: 256 Unicode code points
contiguous one-based command order
commands_completed <= commands_requested
aggregate/result-count consistency
completed execution requires all commands and a closed session
ignored/disabled execution cannot claim Framework session activity
adapter == mock
real_adapter_enabled == false
provider_execution_allowed == false
provider_execution_attempted == false
network_execution == false
```

Unknown schemas, enums, fields, unsafe flags, inconsistent counts, and
oversized values are rejected as typed public-safe problems.

## Accepted injected client boundary

`app/lib/services/character_motion_presentation_client.dart` accepts only an
injected `CharacterMotionPresentationTransport`:

```dart
typedef CharacterMotionPresentationTransport =
    Future<Map<String, Object?>> Function(
      CharacterMotionPresentationRequest request,
    );
```

The client serializes the bounded request, invokes the injected transport,
strictly decodes the normalized result, and converts arbitrary transport
failures into a fixed `motion_transport_failed` problem with a safe message.
It exposes no HTTP, SSE, WebSocket, Backend path, Framework import, provider
client, token, VTS connection, or Live2D runtime.

Normal focused tests use fake/in-memory transports only.

## Accepted ChangeNotifier controller boundary

`app/lib/services/character_motion_presentation_controller.dart` exposes one
immutable `CharacterMotionPresentationState`.

```text
idle -> applying -> completed | ignored | disabled | unavailable | failed
any non-closed state -> idle through reset()
any state -> closed through close()/dispose()
```

Only one active request is allowed. Simultaneous apply and active replacement
are rejected with a typed safe problem. There is no queueing, coalescing,
automatic retry, automatic lifecycle subscription, or visible UI ownership.

Each operation has a local generation. `reset()`, `close()`, and `dispose()`
invalidate that generation, so a delayed fake/in-memory transport completion
cannot overwrite the current state. No notification occurs after disposal.

The controller retains only the bounded request, normalized result, or safe
problem. It retains no raw response map, arbitrary metadata, transport object,
HTTP body/header, raw exception, path, credential, provider payload, or private
log.

## Accepted focused tests

Client tests cover completed, ignored, disabled, unavailable, and failed
results; maximum command/event limits; request bounds; schema/enum/field
rejection; command count/order consistency; aggregate lifecycle consistency;
mock-only safety flags; bounded identifiers/messages; and raw transport
exception normalization.

Controller tests cover each terminal phase, one-active-request enforcement,
reset/close/dispose stale-completion rejection, reset after terminal, closed
apply rejection, safe failure state, listener ordering, idempotent close, and
absence of raw/private error retention.

```text
focused Flutter tests: 41 passed
Flutter full tests: 452 passed
```

## Exact non-actions and non-claims

RT-6d changed none of the following:

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

The existing static character activity states remain idle/loading/speaking.
RT-6d does not claim those states are Framework motion events. HomeScreen
ownership, default-off runtime wiring, and visible character-motion
presentation remain RT-6e work. Configured local mock-motion presentation
acceptance remains RT-6f work. Real Live2D/VTS execution remains blocked in
RT-7.

RT-6d does not claim configured HTTP execution, Backend-to-Flutter motion
transport, Framework execution, provider motion execution, VTS/Live2D
connection, smartphone/PC visible animation acceptance, or v3.0.0 release
readiness.

## Accepted verification

```text
implementation commit: 0f220b792feb7ebb82c5871a794731aa1327439a
implementation pushed: true
compileall: PASS
dedicated RT-6d gate: PASS
Backend full: 279 passed
Backend dependency warnings: 3
Dart format: PASS
Flutter analyze: No issues found
focused Flutter: 41 passed
Flutter full: 452 passed
exact twelve-file review: PASS
changed-content privacy review: PASS
CRLF-aware git diff --check: PASS
explicit operator approval: ACCEPTED
post-push DRC working tree: clean
```

The three Backend warnings came from installed dependency deprecations and did
not fail the suite. The initial artifact contained three unformatted Dart test/
model files; the real-checkout `dart format` correction remained inside the
accepted exact twelve-file surface, and a second format check reported zero
changes before analysis, tests, commit, and push.

## Historical acceptance-sync gate markers

```text
v300_rt6d_status: completed-accepted-pushed
v300_rt6d_exact_acceptance_sync_surface: True
v300_rt6d_acceptance_sync_file_count: 7
v300_rt6d_implementation_commit: 0f220b792feb7ebb82c5871a794731aa1327439a
v300_rt6d_implementation_surface: 12
v300_rt6d_flutter_runtime_file_count: 3
v300_rt6d_flutter_test_file_count: 2
v300_rt6d_focused_flutter_passed: 41
v300_rt6d_flutter_full_passed: 452
v300_rt6d_backend_full_passed: 279
v300_rt6d_backend_warning_count: 3
v300_rt6d_dart_format_passed: True
v300_rt6d_flutter_analyze_passed: True
v300_rt6d_injected_transport_only: True
v300_rt6d_real_http_execution: False
v300_rt6d_max_commands: 3
v300_rt6d_max_event_types: 12
v300_rt6d_active_request_limit: 1
v300_rt6d_stale_result_ignored: True
v300_rt6d_raw_transport_exception_exposed: False
v300_rt6d_raw_response_exposed: False
v300_rt6d_runtime_changed_by_acceptance_sync: False
v300_rt6d_flutter_runtime_changed_by_acceptance_sync: False
v300_rt6d_flutter_tests_changed_by_acceptance_sync: False
v300_rt6d_backend_changed: False
v300_rt6d_home_screen_changed: False
v300_rt6d_main_changed: False
v300_rt6d_character_display_changed: False
v300_rt6d_dependencies_changed: False
v300_rt6d_framework_changed: False
v300_rt6d_vendor_changed: False
v300_rt6d_framework_version: 5.4.0
v300_rt6d_framework_reference_commit: d313eb6acb643103fe25988720ebee5976a04f78
v300_rt6d_framework_source_mode: external-vendored-snapshot
v300_rt6d_framework_execution: False
v300_rt6e_status: ready-for-exact-contract-review-not-authorized
v300_rt6e_implementation_authorized: False
v300_rt6f_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6d_acceptance_sync_commit_push_authorized: False
```

## Next action

```text
Review the exact RT-6e contract separately.
RT-6e implementation remains NOT_AUTHORIZED.
RT-6f remains NOT_STARTED / NOT_AUTHORIZED.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
