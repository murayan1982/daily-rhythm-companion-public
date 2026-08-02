# Daily Rhythm Companion v3.0.0 RT-6f configured local mock-motion presentation

Updated: 2026-08-02

## Accepted state

```text
Source HEAD / implementation baseline: e1d4f63d71c2de485b05fbfc5dad6811b81b31fc
RT-6: COMPLETED / ACCEPTED
RT-6e: COMPLETED / ACCEPTED / PUSHED
RT-6f: COMPLETED / ACCEPTED / PUSHED
implementation commit: fcdce38b9260604ea7c435c6de44fc129dc613f6
implementation surface: exact 19 files
acceptance-sync surface: exact 7 documentation/static-gate files
Framework version: 5.4.0
Framework reference commit: d313eb6acb643103fe25988720ebee5976a04f78
acceptance-sync commit/push: NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
```

## Accepted purpose

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
field `network_execution=false` means that the Framework mock adapter did not
use a provider, VTS, Live2D, or external network runtime.

## Accepted exact implementation surface

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

The acceptance synchronization changes only the seven documentation/static-gate
files listed at the top of the implementation surface.

## Accepted double default-off contract

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
The accepted RT-6e session-local opt-in additionally defaults off and is not
persisted.

## Accepted Backend and Flutter contract

The strict route remains:

```text
POST /demo/character-motion/presentation
```

The body accepts only schema
`drc.v3.character-motion-presentation-request.1`, accepted lifecycle facts,
fixed `home_screen_manual_motion`, null source session/turn IDs, and an optional
bounded character ID. Extra keys are rejected.

The service performs only:

```text
strict request validation
-> CharacterMotionMappingInput
-> CharacterMotionMapper.map()
-> FrameworkMockMotionSessionAdapter.execute()
-> FrameworkMockMotionExecutionResult response
```

Backend default-off returns typed HTTP 200 `disabled` without Framework import.
Enabled requests with no usable Framework root return typed `unavailable`.
`motion_active` and `unknown` remain mapper-owned `ignored` results and stop
before Framework import. Mapped requests use only a new root-public mock
session with `adapter=mock`, `real_adapter_enabled=false`, and
`allow_provider_execution=false`.

Only session-local opt-in plus one explicit Apply can send one POST. Runtime
construction, factory lookup, controller construction, HomeScreen load,
character selection, opt-in, reset, opt-out, and disposal perform zero HTTP
requests. There is no automatic lifecycle subscription, retry, queue,
coalescing, background execution, or active-request replacement.

The accepted HTTP boundary is:

```text
method: POST
request content type: application/json; charset=utf-8
accepted response status: 200 only
redirect following: false
accepted response content type: exact application/json media type
accepted response shape: JSON object only
maximum response body: 65536 bytes
whole-response timeout: 10 seconds
```

Failures become the existing generic `motion_transport_failed` problem. Raw
URL, response body, exception text, private IDs, command payloads, and provider
data are not retained in public state.

## Accepted automated verification

```text
Dart format: PASS
python compileall: PASS
dedicated RT-6f gate: PASS
focused Backend: 10 passed
Backend full: 289 passed
Backend warning: 1 existing Starlette/httpx deprecation warning
Flutter analyze: No issues found
focused Flutter: 15 passed
Flutter full: 483 passed
exact implementation surface: 19 files
changed-content privacy review: PASS
CRLF-aware git diff --check: PASS
implementation commit: fcdce38b9260604ea7c435c6de44fc129dc613f6
implementation push: PASS
post-push DRC working tree: clean
post-push Framework working tree: clean
```

The corrective review fixed the whole-response timeout boundary, exact JSON
media-type validation, the focused tests for those cases, and the executable
Backend test path in `scripts/README.md` without expanding the exact nineteen-file
surface.

## Accepted configured local controls

### Control A — default-off

The operator accepted normal startup with both RT-6f flags omitted:

```text
configuration: unconfigured
session opt-in: off
automatic RT-6f request: none
```

### Control B — configured idle

The operator accepted configured startup before session opt-in:

```text
configuration: configured
session opt-in: off
presentation phase: idle
Apply unavailable while opted out
```

### Control C — speaking mock completion

The accepted screen showed:

```text
selected fact: speaking
presentation phase: completed
execution status: completed
cue: speaking
commands requested: 2
commands completed: 2
adapter: mock
real adapter enabled: false
provider attempted: false
network execution: false
reason code: framework_mock_motion_completed
```

### Control D — unknown pre-import ignore

The accepted screen showed:

```text
selected fact: unknown
presentation phase: ignored
execution status: ignored
commands requested: 0
commands completed: 0
event type count: 0
adapter: mock
real adapter enabled: false
provider attempted: false
network execution: false
reason code: unknown_fact_ignored
```

The UI also reported that the request was ignored before Framework import or
session creation.

### Control E — reset, opt-out, and cleanup

The accepted screen after reset and opt-out showed:

```text
configuration: configured
session opt-in: off
presentation phase: idle
execution status: none
commands requested/completed: 0 / 0
real adapter enabled: false
provider attempted: false
network execution: false
```

Per-Apply maximum-one-request and local-only reset/opt-out behavior are also
covered by the focused Flutter tests. After operator execution and the
implementation push, DRC and Framework working trees were clean. Private
screenshots, local paths, LAN data, raw results, and operator evidence were not
committed.

## Protected non-change and non-claims

RT-6f did not change the accepted RT-6b mapper, RT-6c adapter, RT-6d
model/client/controller, or RT-6e HomeScreen/panel runtime. It did not change
Framework source, provider code, platform files, assets, dependencies, version
metadata, or release records.

RT-6f does not implement or accept real Live2D animation, VTube Studio
WebSocket, a real motion adapter, provider execution, credential/token reads,
private model loading, automatic realtime lifecycle-to-motion wiring,
automatic voice/stream/TTS-to-motion wiring, persistent opt-in, retry,
background motion queues, smartphone/iOS/all-device real-motion acceptance,
v3.0.0 release readiness, or RT-7 authorization.

## Completion and stop rule

```text
RT-6f implementation: COMPLETED / ACCEPTED / PUSHED
parent RT-6: COMPLETED / ACCEPTED
acceptance-sync surface: exact 7 documentation/static-gate files
acceptance-sync commit/push: NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
```

Do not start RT-7 by substituting mock motion for a missing real Live2D/VTS
adapter. Do not commit or push this acceptance synchronization without separate
explicit approval.
