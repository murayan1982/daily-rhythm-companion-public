# Daily Rhythm Companion v3.0.0 RT-6c Framework mock motion-session adapter

Updated: 2026-08-01

## Status

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6b implementation: 17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594
RT-6b acceptance sync: 9442f511f9e41d18f64a65cf7fa44a375e7a67ce
RT-6c: IMPLEMENTED / AWAITING_REVIEW
RT-6c baseline: 9442f511f9e41d18f64a65cf7fa44a375e7a67ce
RT-6c implementation commit/push: NOT_AUTHORIZED
RT-6d through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
FW baseline version: 5.4.0
FW canonical reference commit: d313eb6acb643103fe25988720ebee5976a04f78
FW local source mode: external-vendored-snapshot
```

## Purpose

RT-6c adds a guarded Backend adapter from the accepted RT-6b
`CharacterMotionPlan` contract to the FW v5.4.0 root-public motion-session
boundary defined by canonical reference commit
`d313eb6acb643103fe25988720ebee5976a04f78`. The local FW source is an external
vendored snapshot outside DRC Git history, so the reference commit records the
small-commit compatibility baseline rather than asserting vendor Git identity.
The adapter is default-off, synchronous, bounded to three commands, and
mock-only. It creates a new local session for each execution and normalizes FW
results into DRC-owned bounded models.

RT-6c does not add a route, configuration flag, environment profile, runtime
caller, Flutter client, controller, or HomeScreen wiring. No normal DRC runtime
path enables this adapter. RT-6d through RT-6f remain separately reviewed work.
Real Live2D/VTS execution remains blocked in RT-7.

## Exact change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6c_framework_mock_motion_session_adapter.md
scripts/check_v300_rt6c_framework_mock_motion_session_adapter.py
backend/app/models/character_motion_adapter.py
backend/app/services/framework_mock_motion_session_adapter.py
backend/tests/test_framework_mock_motion_session_adapter.py
```

```text
documentation/static gate: 7 files
Backend runtime: 2 new files
Backend focused test: 1 new file
total: exact ten files
```

The accepted RT-6b models, mapper, and tests are not changed. Existing
motion-demo, realtime, API, config, Flutter, dependency, asset, version, and
release files are not changed.

## DRC-owned execution result

`FrameworkMockMotionExecutionResult` retains only bounded application data:

```text
status
source fact and cue
bounded source event/session/turn/character IDs
commands requested/completed
maximum three normalized command results
maximum twelve event type strings
Framework import/session lifecycle booleans
fixed mock/real/provider/network safety booleans
bounded reason code and safe message
```

It does not retain:

```text
FW session ID
FW request ID
raw FW request/result/session/capability/event objects
arbitrary metadata mappings
exception text
filesystem paths
provider payloads
tokens or credentials
```

Aggregate statuses are:

```text
completed
ignored
disabled
unavailable
failed
```

The model rejects real-adapter, provider-execution, or network-execution claims.
A completed result requires every requested command to complete and the owned
session to close successfully.

## Default-off and stop rules

The adapter constructor is:

```python
FrameworkMockMotionSessionAdapter(
    framework_root=<optional path>,
    enabled=False,
)
```

When disabled, it returns a typed `disabled` result before Framework import,
session creation, command conversion, or execution.

When enabled, an RT-6b ignored plan returns `ignored` before Framework import.
This preserves the accepted recursion and fail-closed rules:

```text
motion_active -> ignored
unknown -> ignored
```

A missing, blank, nonexistent, or non-directory Framework root returns a typed
`unavailable` result with fixed public-safe wording. The configured path is not
included in the result.

## Root-public-only Framework boundary

The only dynamic Framework import is:

```python
importlib.import_module("framework")
```

The adapter obtains these symbols from that root module:

```text
create_motion_session
MotionRequest
MotionIntent
```

It contains no direct or static import of:

```text
framework.motion
framework.motion_session
provider-specific Framework modules
VTube Studio or websocket modules
Live2D runtime modules
```

During the bounded call, the configured checkout is temporarily added to
`sys.path` and used as the current directory. Both are restored in `finally`.
No path value is returned through the DRC result.

## Forced mock session creation

Session creation uses fixed safe arguments:

```python
create_motion_session(
    project_root=str(framework_root),
    adapter="mock",
    real_adapter_enabled=False,
    allow_provider_execution=False,
    public_metadata={
        "boundary": "drc_rt6c",
        "mode": "mock",
    },
)
```

Adapter selection, real-adapter enablement, provider execution, model ID, VTS
URL/token, private model path, and provider configuration are not caller inputs.
A new session is created for every call; the adapter does not retain mutable FW
session state between executions.

## Preflight requirement

Before applying a command, the adapter calls `session.preflight()` exactly once.
It accepts only a capability with:

```text
adapter_status: mock_available
supports_motion_session: true
supports_mock_motion: true
supports_real_adapter: false
```

Any mismatch returns `unavailable`, applies zero commands, and closes the
session. Missing root-public symbols or missing required session methods fail
closed with fixed wording.

## Exact command conversion

| DRC intent | FW root-public request |
|---|---|
| `expression` | `MotionRequest.expression_change(...)` |
| `speaking_state` | `MotionRequest.speaking_state(...)` |
| `stop_motion` | `MotionRequest.stop_motion(...)` |
| `idle_motion` | `MotionRequest(intent=MotionIntent.IDLE_MOTION, ...)` |
| `reset_expression` | `MotionRequest(intent=MotionIntent.RESET_EXPRESSION, ...)` |

Each FW request receives only:

```text
character_id
boundary=drc_rt6c
command_order=1..3
drc_intent=<bounded enum>
drc_cue=<bounded enum or none>
```

The DRC source event type, session ID, and turn ID are deliberately not copied
to FW metadata.

## Execution semantics

Commands run synchronously in contiguous order. The adapter creates no worker
thread, queue, timer, retry loop, or background task. At most three
`apply_motion()` calls occur.

If every normalized FW result has `outcome=completed`, the aggregate result is
`completed`. The result records the bounded command outcomes and confirms that
the session was created and closed. Provider and network execution remain false.

The first non-completed result stops later commands. Outcomes such as
`unsupported`, `unavailable`, `not_configured`, `not_implemented`, and `closed`
normalize to aggregate `unavailable`; other non-completed outcomes normalize to
`failed`. No retry occurs.

Exceptions are converted to fixed values:

```text
reason_code: framework_mock_motion_failed
safe_message: Framework mock motion execution failed.
```

Raw exception text is not returned. A close failure becomes:

```text
reason_code: framework_mock_motion_close_failed
safe_message: Framework mock motion session cleanup failed.
```

The adapter calls `close()` once from its own `finally` block after successful
session creation.

## Event observation

The adapter registers one root-public `on_event()` callback. It retains only the
bounded `type` string from each public mapping and stops retaining after twelve
entries. Session/request IDs, metadata, messages, adapter details, and raw event
objects are discarded.

Events are observation-only. RT-6c does not update DRC realtime state, publish a
route event, or drive Flutter presentation.

## Focused test contract

Focused tests cover:

```text
- default disabled behavior and zero Framework import
- disabled precedence and enabled ignored-plan stop
- missing/invalid root handling without path disclosure
- root-public module name and missing-symbol fail-closed behavior
- forced mock/real-disabled/provider-disallowed session arguments
- one preflight before application
- capability mismatch rejection and cleanup
- conversion of all five DRC command intents
- command order and maximum three apply calls
- bounded request metadata and no source-ID forwarding
- all-completed aggregate result
- first non-completed fail-fast behavior
- exception and close-error fixed safe wording
- event-type-only retention capped at twelve
- raw FW identifiers/objects/metadata not exposed
- new session per call
- cwd/sys.path restoration
- result-model safety validation
- AST absence of Framework internal imports and runtime dependencies
```

Generation-side focused result:

```text
38 passed
```

## Dedicated gate contract

The dedicated gate verifies the exact ten-file surface and prints:

```text
v300_rt6c_status: implemented-awaiting-review
v300_rt6c_exact_change_surface: True
v300_rt6c_change_file_count: 10
v300_rt6c_backend_runtime_file_count: 2
v300_rt6c_backend_test_file_count: 1
v300_rt6c_rt6b_model_changed: False
v300_rt6c_rt6b_mapper_changed: False
v300_rt6c_api_routes_changed: False
v300_rt6c_config_changed: False
v300_rt6c_flutter_changed: False
v300_rt6c_framework_changed: False
v300_rt6c_dependencies_changed: False
v300_rt6c_root_public_only: True
v300_rt6c_default_enabled: False
v300_rt6c_mock_adapter_forced: True
v300_rt6c_real_adapter_enabled: False
v300_rt6c_provider_execution_allowed: False
v300_rt6c_disabled_import_attempted: False
v300_rt6c_ignored_import_attempted: False
v300_rt6c_max_apply_calls: 3
v300_rt6c_fail_fast: True
v300_rt6c_session_close_guaranteed: True
v300_rt6c_raw_framework_objects_exposed: False
v300_rt6c_max_retained_event_types: 12
v300_rt6c_framework_version: 5.4.0
v300_rt6c_framework_reference_commit: d313eb6acb643103fe25988720ebee5976a04f78
v300_rt6c_framework_source_mode: external-vendored-snapshot
v300_rt6c_framework_git_identity_required: False
v300_rt6c_framework_root_public_contract_passed: True
v300_rt6c_framework_mock_smoke_passed: True
v300_rt6c_real_fw_mock_smoke_passed: True
v300_rt6c_network_execution: False
v300_rt6c_provider_execution: False
v300_rt6c_vts_connection_used: False
v300_rt6c_live2d_runtime_loaded: False
v300_rt6d_authorized: False
v300_rt6c_commit_push_authorized: False
```

Normal mode requires DRC HEAD/origin main at
`9442f511f9e41d18f64a65cf7fa44a375e7a67ce`. The small-commit contract records
FW baseline version `5.4.0`, canonical reference commit
`d313eb6acb643103fe25988720ebee5976a04f78`, and source mode
`external-vendored-snapshot`. Because vendor is intentionally outside DRC Git
history, the gate does not require vendor Git HEAD, clean status, or full-source
identity. It verifies the required root-public motion symbols and executes a
representative three-command plan through the supplied local mock session.

Snapshot mode runs an isolated synthetic root-public mock smoke for candidate
reconstruction. Snapshot success does not replace normal vendored-source
contract verification.

## Verification commands

Run from the DRC repository root while the candidate remains uncommitted:

```powershell
$env:FRAMEWORK_ROOT = "<DRC-root>\vendor\ai-character-framework-5.4.0"
python -m compileall -q backend scripts
python scripts\check_v300_rt6c_framework_mock_motion_session_adapter.py `
    --framework-root $env:FRAMEWORK_ROOT
python -m pytest -q backend\tests\test_framework_mock_motion_session_adapter.py
python -m pytest -q

cd app
flutter analyze
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --stat
git diff --name-only
git ls-files --others --exclude-standard
```

Expected candidate results:

```text
focused RT-6c Backend: 38 passed
Backend full: 279 passed
Flutter analyze: No issues found
Flutter full: 411 passed
exact surface: 10 files
external vendor FW root-public contract/mock smoke: PASS
provider/network/VTS/Live2D execution: none
```

## Non-actions and non-claims

RT-6c does not:

```text
- change RT-6b mapping models, mapper, or tests
- change existing motion-demo/realtime behavior or routes
- add config/env enablement or a runtime caller
- expose the adapter through HTTP
- add Flutter models, client, controller, or HomeScreen wiring
- import FW internal modules or provider-specific modules
- enable a real adapter or provider execution
- open a network or VTS WebSocket connection
- load Live2D or private model runtime
- read tokens, credentials, private paths, payloads, or evidence
- change microphone, audio, STT, LLM, or TTS behavior
- authorize RT-6d through RT-6f
- claim real motion acceptance or v3.0.0 release readiness
```

## Next action

```text
Review the exact ten-file RT-6c candidate.
RT-6c commit/push remains NOT_AUTHORIZED.
RT-6d implementation remains NOT_AUTHORIZED.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
