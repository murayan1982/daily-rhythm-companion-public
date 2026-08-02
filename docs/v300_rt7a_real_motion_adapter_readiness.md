# Daily Rhythm Companion v3.0.0 RT-7a real-motion adapter readiness

Updated: 2026-08-02

## Accepted state

```text
RT-6: COMPLETED / ACCEPTED / PUSHED
RT-7: CURRENT / NOT_COMPLETED
RT-7a: COMPLETED / ACCEPTED / PUSHED
DRC baseline: c3c78316fd2bcd4f9939dcaadc32134a704374cf
implementation commit: efb139b2c0b6c7cc66912a229bd674b36df82dd7
implementation surface: exact 7 documentation/static-gate files
acceptance-sync surface: exact 7 documentation/static-gate files
Framework version: 5.4.0
Framework reference commit: d313eb6acb643103fe25988720ebee5976a04f78
readiness: BLOCKED_FRAMEWORK_REAL_MOTION_ADAPTER_RELEASE_REQUIRED
acceptance-sync commit/push: NOT_AUTHORIZED
```

## Accepted result

RT-7a freezes the accepted RT-6 mock-motion path and records the exact
prerequisite for real Live2D / VTube Studio execution. It is an inventory and
requirement checkpoint only. It does not implement or execute a real adapter.

Accepted verification:

```text
compileall: PASS
dedicated RT-7a gate: PASS
Backend full: 289 passed
Backend dependency warnings: 1
Flutter analyze: No issues found
Flutter full: 483 passed
exact seven-file implementation review: PASS
changed-content privacy scan: PASS
CRLF-aware git diff --check: PASS
explicit implementation commit approval: ACCEPTED
implementation commit/push: COMPLETED
post-push DRC clean: true
post-push Framework clean: true
```

The warning came from the installed Starlette/httpx test dependency boundary
and did not fail the Backend regression suite.

## Frozen accepted DRC path

```text
explicit HomeScreen Apply
→ bounded local Backend presentation route
→ accepted app-owned motion mapper
→ accepted FW root-public mock MotionSession adapter
→ normalized mock-only result
→ bounded Flutter presentation
```

No accepted RT-6 runtime or test is changed by RT-7a or this acceptance sync.

## Released Framework v5.4.0 inventory

The released root-public package exports:

```text
MotionAdapterStatus
MotionCapability
MotionErrorCode
MotionEventType
MotionIntent
MotionOutcome
MotionRequest
MotionResult
MotionState
MotionSession
MotionSessionInfo
create_motion_session
```

The public contract provides typed states including `disabled`,
`mock_available`, `not_configured`, `token_missing`,
`provider_execution_not_allowed`, `runtime_not_installed`,
`model_not_selected`, `not_implemented`, `unsupported_adapter`, and `closed`.

Released v5.4.0 is intentionally mock-safe. For `live2d`, `vts`, or
`vtube_studio`, real adapter support remains false and an explicitly enabled
provider path resolves to a typed not-implemented capability/result. The
session does not connect to VTube Studio, open a VTS WebSocket, read a token,
load a private model or Live2D runtime, or import provider SDK modules.

## Accepted readiness decision

```text
READY_AND_FROZEN:
- accepted RT-6 app-owned mapping
- accepted FW root-public mock adapter
- accepted Backend/Flutter configured local mock presentation

BLOCKED:
- real Live2D runtime execution
- VTube Studio WebSocket connection
- VTS authentication/token lifecycle
- configured model selection and real command dispatch
- real adapter reconnect/resource lifecycle

DECISION:
BLOCKED_FRAMEWORK_REAL_MOTION_ADAPTER_RELEASE_REQUIRED
```

DRC cannot make the missing capability real through a Framework
internal/provider import or a DRC-owned VTS/provider bypass.

## Minimum released Framework real-adapter contract required by DRC

A future Framework release must provide all of the following through stable
root-public APIs:

```text
- create_motion_session() selects a documented real adapter.
- real_adapter_supported=true only when the released adapter is implemented.
- provider execution remains explicit and default-off.
- preflight distinguishes not configured, token missing, runtime unavailable,
  model not selected, authentication rejected, connection unavailable, and
  unsupported capability with typed public-safe status/error values.
- Framework owns VTS WebSocket connection, authentication, reconnect policy,
  request correlation, and close/dispose cleanup.
- capability reports supported expression, emotion, speaking-state, gesture,
  look-at, stop-motion, and reset behavior accurately.
- apply_motion() returns bounded typed completed, unavailable, interrupted, or
  failed results without raw VTS payloads or private values.
- token values, authorization data, private model paths, host details, and raw
  provider exceptions never enter public results, events, logs, or DRC UI.
- mock and real adapters remain usable through the same root-public session and
  request/result contracts.
- DRC needs no Framework internal/provider import.
```

## DRC stop rule

Until a released Framework version satisfies the real-adapter contract:

```text
- do not add a DRC real-adapter runtime or provider client;
- do not add VTS/WebSocket dependencies to DRC;
- do not read token or private model configuration in DRC;
- do not change the accepted RT-6 mock route into a real route;
- do not claim Live2D/VTS execution, animation, PC acceptance, smartphone
  acceptance, or release readiness;
- keep RT-7 runtime implementation blocked.
```

After a released Framework update, DRC requires a separate exact-contract
reassessment before any runtime change. Smartphone end-to-end evidence remains
RT-8 work.

## Exact implementation and acceptance-sync surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7a_real_motion_adapter_readiness.md
scripts/check_v300_rt7a_real_motion_adapter_readiness.py
```

Both the implementation and acceptance-state synchronization use the same
seven documentation/static-gate files. The acceptance sync changes no Backend
runtime, Flutter runtime, existing test, dependency, lockfile, platform
manifest, environment profile, asset, version, release record, or Framework
source file.

## Non-actions and non-claims

RT-7a performs no HTTP, provider, network, WebSocket, VTS, Live2D, token,
credential, private model, microphone, audio, STT, LLM, TTS, screenshot, or
operator execution. It does not indicate that a real adapter is available.

## Next action

```text
Commit/push the exact seven-file acceptance sync only after separate approval.
RT-7 real runtime remains blocked pending a released Framework adapter.
```
