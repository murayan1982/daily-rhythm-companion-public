# Daily Rhythm Companion v3.0.0 RT-6f configured local mock-motion presentation

Updated: 2026-08-01

## Candidate state

```text
Source HEAD / implementation baseline: e1d4f63d71c2de485b05fbfc5dad6811b81b31fc
RT-6: CURRENT / NOT_COMPLETED
RT-6e: COMPLETED / ACCEPTED / PUSHED
RT-6f: IMPLEMENTED / AWAITING_REVIEW
implementation commit: none
implementation surface: exact 19 files
commit/push: NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
```

## Purpose

RT-6f connects only the two accepted unconfigured boundaries left by RT-6c
and RT-6e:

```text
explicit HomeScreen Apply
-> local Flutter HTTP transport
-> DRC Backend presentation endpoint
-> accepted RT-6b CharacterMotionMapper
-> accepted RT-6c FrameworkMockMotionSessionAdapter
-> FW v5.4.0 root-public mock MotionSession
-> normalized mock-only result
-> accepted RT-6d controller
-> accepted RT-6e public-safe panel
```

The local Flutter-to-Backend HTTP request is real local transport. The result
field `network_execution=false` continues to mean that the Framework mock
adapter did not use a provider, VTS, Live2D, or external network runtime.

## Exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6f_configured_local_mock_motion_presentation_acceptance.md
scripts/check_v300_rt6f_configured_local_mock_motion_presentation_acceptance.py

backend/.env.example
backend/app/config.py
backend/app/main.py
backend/app/api/character_motion_presentation.py
backend/app/models/character_motion_presentation.py
backend/app/services/character_motion_presentation_service.py
backend/tests/conftest.py
backend/tests/test_character_motion_presentation_api.py

app/lib/main.dart
app/lib/services/configured_character_motion_presentation_runtime.dart
app/test/configured_character_motion_presentation_runtime_test.dart
app/test/main_character_motion_presentation_wiring_widget_test.dart
```

```text
documentation/static gate: 7
Backend config/runtime: 6
Backend tests/safety: 2
Flutter runtime: 2
Flutter tests: 2
total: exact 19
```

## Double default-off contract

Backend execution is enabled only by:

```text
DRC_RT6_ENABLE_FRAMEWORK_MOCK_MOTION=1
```

Flutter normal-startup assembly is enabled only by:

```text
--dart-define=DRC_RT6_ENABLE_CONFIGURED_MOCK_MOTION=true
```

The Backend reuses only `FRAMEWORK_PROJECT_ROOT` / `FRAMEWORK_ROOT`. The
Flutter runtime reuses only `DRC_BACKEND_API_BASE_URL` through
`BackendApiClient.baseUrl`. Existing Motion Demo settings are not reused.

With either RT-6f flag disabled, normal startup performs no Framework import,
session creation, provider execution, motion command, or RT-6f HTTP request.

## Backend request and execution contract

The new route is:

```text
POST /demo/character-motion/presentation
```

The body is strict and extra keys are rejected:

```text
schema_version: drc.v3.character-motion-presentation-request.1
source_fact: accepted CharacterMotionLifecycleFact
source_event_type: home_screen_manual_motion only
source_session_id: null only
source_turn_id: null only
character_id: optional, maximum 128 characters
```

The service performs only:

```text
strict request validation
-> CharacterMotionMappingInput
-> CharacterMotionMapper.map()
-> FrameworkMockMotionSessionAdapter.execute()
-> FrameworkMockMotionExecutionResult response
```

Backend default-off returns typed HTTP 200 `disabled` without Framework
import. Enabled requests with no usable Framework root return typed
`unavailable`. `motion_active` and `unknown` remain mapper-owned `ignored`
results and stop before Framework import.

A mapped request can create only a new root-public FW mock session with:

```text
adapter=mock
real_adapter_enabled=false
allow_provider_execution=false
```

The accepted RT-6c maximum of three synchronous commands, bounded normalized
events/results, and mandatory close behavior remain unchanged.

## Flutter configured runtime contract

The runtime returns a controller factory only when the Flutter flag is true
and the Backend base URL is an absolute HTTP(S) URL with a host, no userinfo,
and no fragment.

Runtime construction, factory lookup, controller construction, HomeScreen
load, character selection, opt-in, reset, opt-out, and disposal perform zero
HTTP requests. Only session-local opt-in plus one explicit Apply can send one
POST. There is no automatic lifecycle subscription, retry, queue,
coalescing, background execution, or active-request replacement.

The HTTP boundary:

```text
method: POST
request content type: application/json; charset=utf-8
accepted response status: 200 only
redirect following: false
accepted response content type: application/json
accepted response shape: JSON object only
maximum response body: 65536 bytes
timeout: 10 seconds
```

Non-200, redirect, timeout, oversized, wrong-content-type, malformed JSON, and
non-object responses become the existing generic
`motion_transport_failed` problem. Raw URL, response body, exception text,
private IDs, command payloads, and provider data are not retained in public
state.

Each configured controller owns one HTTP client and closes it on controller
disposal. `main.dart` injects only the optional factory; the accepted RT-6e
HomeScreen remains unchanged and retains default-off opt-in and local-only
reset/opt-out invalidation.

## Protected non-change surface

```text
backend/app/api/motion_demo.py
backend/app/models/motion_demo.py
backend/app/services/motion_demo_service.py
backend/app/models/character_motion.py
backend/app/models/character_motion_adapter.py
backend/app/services/character_motion_mapper.py
backend/app/services/framework_mock_motion_session_adapter.py
backend/tests/test_character_motion_mapper.py
backend/tests/test_framework_mock_motion_session_adapter.py

app/lib/models/character_motion_presentation.dart
app/lib/services/character_motion_presentation_client.dart
app/lib/services/character_motion_presentation_controller.dart
app/lib/screens/home_screen.dart
app/lib/widgets/character_motion_presentation_panel.dart
app/test/character_motion_home_screen_test.dart
app/test/character_motion_presentation_client_test.dart
app/test/character_motion_presentation_controller_test.dart

app/lib/services/backend_api_client.dart
app/pubspec.yaml
app/pubspec.lock
platform files
assets
versions
release records
Framework repository/vendor source
```

## Candidate verification

Automated Backend verification in the handoff workspace:

```text
python -m compileall -q backend/app: PASS
focused Backend RT-6f tests: 10 passed
```

The focused Backend tests cover default-off, missing root, ignored facts,
root-public mock completion, no provider/network/real-adapter flags, strict
manual source, null session/turn IDs, schema rejection, and extra-key
rejection.

Flutter formatting, analysis, focused tests, full Flutter regression, and the
configured local operator controls must be run in the real Windows checkout
where Flutter is installed. They are not claimed by this source-snapshot
workspace.

## Configured local acceptance controls

```text
Control A: both flags omitted -> unconfigured, HTTP 0, FW import/session 0
Control B: both flags enabled, opt-in off -> configured idle, HTTP/FW 0
Control C: speaking Apply -> one POST, completed, speaking cue, all mock commands completed
Control D: unknown Apply -> one POST, ignored, command count 0, FW import/session false
Control E: reset and opt-out -> no additional POST, delayed result invalidated
Cleanup: both normal defaults restored, operator artifacts removed, DRC/FW trees clean
```

## Explicit non-claims

RT-6f does not implement or accept real Live2D animation, VTube Studio
WebSocket, a real motion adapter, provider execution, credential/token reads,
private model loading, automatic realtime lifecycle-to-motion wiring,
automatic voice/stream/TTS-to-motion wiring, persistent opt-in, retry,
background motion queues, smartphone/iOS/all-device motion acceptance,
v3.0.0 release readiness, or RT-7 authorization.

## Stop rule

```text
Review the exact nineteen-file candidate and run the real-checkout validation.
Do not commit or push without separate explicit operator approval.
Do not mark RT-6f accepted before configured local Controls A-E and cleanup pass.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
