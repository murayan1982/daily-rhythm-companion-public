# Daily Rhythm Companion v3.0.0 RT-7c guarded vendored FW v5.5.0 VTS session adapter

Updated: 2026-08-03

## Candidate state

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7a: COMPLETED / ACCEPTED / PUSHED
RT-7b: COMPLETED / ACCEPTED / PUSHED
RT-7c: IMPLEMENTED / AWAITING_REVIEW
RT-7d: NOT_AUTHORIZED
RT-7e: NOT_AUTHORIZED
implementation baseline: 35582f06ca037401b2cef8d97cfc5fc26cd40654
implementation commit: none
Framework release: v5.5.0
Framework release commit: f56697b6de066b062794ac7bb01330d2d9e91759
Framework local source: vendor/ai-character-framework-5.5.0
Framework development checkout: PROHIBITED
Framework internal import: PROHIBITED
pyvts direct import: PROHIBITED
real VTube Studio execution: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-7c adds only the guarded Backend adapter core required to consume the
released Framework v5.5.0 root-public VTube Studio motion-session boundary.

It does not connect the adapter to Backend configuration, a FastAPI route,
Flutter, HomeScreen, automatic realtime lifecycle events, or private operator
configuration. Those concerns remain separate RT-7d and RT-7e work.

## Exact eleven-file surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md
scripts/check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py
backend/requirements.txt
backend/app/models/framework_vts_motion.py
backend/app/services/framework_vts_motion_session_adapter.py
backend/tests/test_framework_vts_motion_session_adapter.py
```

```text
documentation/static gate: 7 files
dependency manifest: 1 file
Backend runtime core: 2 files
focused Backend test: 1 file
total: exact 11 files
```

## Fixed Framework source

The only production Framework source is:

```text
vendor/ai-character-framework-5.5.0
```

The adapter computes this path from the DRC repository and validates the loaded
root package origin against:

```text
vendor/ai-character-framework-5.5.0/framework/__init__.py
```

The adapter does not read `FRAMEWORK_ROOT`, `FRAMEWORK_PROJECT_ROOT`, another
checkout, a moving branch, current working directory, or a caller-supplied
production Framework path.

The root package is loaded with `importlib.util.spec_from_file_location`.
Framework package modules are temporarily isolated for the complete public
session lifetime. The adapter does not change cwd or mutate `sys.path`.

## Root-public-only boundary

The adapter consumes only attributes exported by `framework`:

```text
MotionRequest
MotionIntent
MotionSessionInfo
create_motion_session
```

It does not import:

```text
framework.motion
framework.motion_session
framework.vtube_studio_*
framework internal plugins
live2d
pyvts
websockets
```

Framework retains ownership of provider dependency loading, VTube Studio
client/WebSocket construction, authentication, model/hotkey inventory,
timeouts, provider exception normalization, and transport cleanup.

## Explicit private configuration

`FrameworkVtsMotionPrivateConfig` accepts explicit values only:

```text
enabled
allow_provider_execution
runtime_available
model_selected
endpoint_host
endpoint_port
authentication_token
hotkey_bindings
connect_timeout_seconds
authenticate_timeout_seconds
request_timeout_seconds
close_timeout_seconds
```

It performs no environment or filesystem read. Endpoint, port, token, and
hotkey values are excluded from dataclass `repr`. The adapter does not place
them in DRC results, events, logs, exceptions, metadata, or test output.

A separately reviewed RT-7d configuration loader may construct this object
later. RT-7c does not modify `backend/.env.example` or `backend/app/config.py`.

## Double opt-in and closed guards

Normal construction is disabled. Execution requires both:

```text
enabled=True
allow_provider_execution=True
```

Disabled and provider-disallowed results return before vendor resolution,
Framework import, session creation, pyvts import, provider execution, network,
or real motion.

When execution is enabled but configuration is incomplete, the adapter may
create a root-public VTS session and call `preflight()`. Framework v5.5.0 must
return a typed unavailable capability before importing pyvts or opening a
network connection. `apply_motion()` is never called unless preflight reports a
ready real adapter.

## Request vocabulary

`FrameworkVtsMotionCommand` accepts exactly:

```text
expression
emotion
gesture
reset_expression
stop_motion
```

Payload rules:

```text
expression: exactly one expression field
emotion: exactly one emotion field
gesture: exactly one gesture field
reset_expression: no expression/emotion/gesture payload
stop_motion: no expression/emotion/gesture payload
```

The following are rejected at model validation and must not be inferred from
the mock adapter:

```text
speaking_state
idle_motion
look_at
```

Generic `value` is not used.

## Required and optional capability behavior

Required released intents:

```text
expression
emotion
gesture
reset_expression
```

Every command is checked with the public capability before
`apply_motion()`.

An unsupported required intent returns a typed `unsupported` aggregate and is
not applied. Unsupported `stop_motion` is an optional safe skip and does not
convert otherwise completed required commands into provider failure.

## Session flow

```text
validate one-to-five contiguous commands
→ evaluate DRC closed guards
→ resolve fixed vendor
→ load root-public package and verify API version 5.5.0
→ create one adapter="vts" session with explicit double opt-in
→ register a bounded event-type observer
→ preflight once
→ branch on typed capability
→ check capability per command
→ construct intent-specific MotionRequest
→ apply supported commands in order
→ normalize allowlisted public fields and booleans
→ close the session in every created-session path
→ restore prior Python module state
```

Session close failure is normalized to a fixed cleanup result. Raw exception
text is discarded.

## Public result boundary

The DRC result may retain only:

```text
aggregate status
command count
command order and intent
allowlisted outcome/state/adapter status/public error code
retryable and optional-skip booleans
bounded fixed safe message
allowlisted bounded event type strings
Framework import/session-created/session-closed booleans
provider/network/real-motion execution booleans
```

The result must not retain:

```text
endpoint host or port
authentication token or token path
hotkey selector/name/identifier
private model identity or path
Framework session ID or request ID
source session/turn IDs
raw Framework public_metadata
raw event payload
raw provider payload
raw exception
private operator evidence
screenshots
local drive paths
```

## Dependencies

RT-7c adds the exact Framework v5.5.0 VTS runtime pins to Backend requirements:

```text
pyvts==0.3.3
websockets==16.0
```

Application code imports neither package directly. The fixed Framework performs
lazy provider loading only after its complete explicit guard passes.

## Focused tests

The fake/injected tests cover:

```text
disabled guard without Framework import
provider-execution guard without Framework import
missing fixed vendor
unexpected Framework origin
missing root-public symbol
exact VTS double opt-in session arguments
required expression/emotion/gesture/reset completion
unsupported required intent
optional unsupported stop_motion
speaking_state/idle_motion/look_at rejection
ambiguous or missing payload rejection
preflight unavailable and preflight exception
apply exception normalization
close exception normalization
bounded allowlisted event types
allowlisted execution booleans only
private config/result non-exposure
contiguous command ordering
no cwd or Framework sys.path workaround
```

All focused tests use injected root-public fake sessions. They import no pyvts,
open no network connection, and execute no real motion.

## Candidate verification

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py
python -m pytest -q backend\tests\test_framework_vts_motion_session_adapter.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
```

Expected candidate boundary:

```text
exact change surface: 11
focused RT-7c tests: all passed
Backend full baseline: 289 plus RT-7c tests
Flutter analyze: no issues
Flutter full baseline: 483
pyvts imported by gate: false
provider execution attempted by gate: false
network execution attempted by gate: false
real motion executed by gate: false
```

Actual checkout results remain pending until the generated candidate is applied
and verified.

## Protected non-change surface

```text
backend/.env.example
backend/app/config.py
backend/app/main.py
backend/app/api/**
backend/app/models/character_motion.py
backend/app/models/character_motion_adapter.py
backend/app/models/character_motion_presentation.py
backend/app/services/character_motion_mapper.py
backend/app/services/framework_mock_motion_session_adapter.py
backend/app/services/character_motion_presentation_service.py
backend/tests/test_character_motion_mapper.py
backend/tests/test_framework_mock_motion_session_adapter.py
backend/tests/test_character_motion_presentation_api.py
app/**
vendor/**
```

RT-6 mock routes and Flutter presentation remain unchanged and continue to use
their existing mock-only result contract.

## Explicit non-actions

RT-7c does not:

- read process environment or a private `.env`;
- add an API route or modify existing API response types;
- wire Flutter, HomeScreen, or automatic lifecycle events;
- access a Framework development checkout;
- import Framework internals, pyvts, or websockets directly;
- own a VTube Studio WebSocket or token file;
- execute a provider, network operation, or real motion during verification;
- collect private operator evidence;
- authorize RT-7d or RT-7e;
- commit or push itself.

## Next boundary

```text
RT-7c acceptance: pending review
RT-7d default-off configured Backend/API/Flutter manual VTS wiring:
NOT_AUTHORIZED
RT-7e private configured local VTS execution and acceptance:
NOT_AUTHORIZED
real VTube Studio execution:
NOT_AUTHORIZED
```
