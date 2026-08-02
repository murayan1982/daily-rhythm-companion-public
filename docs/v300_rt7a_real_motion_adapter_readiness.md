# Daily Rhythm Companion v3.0.0 RT-7a real-motion adapter readiness

Updated: 2026-08-02

## Candidate state

```text
RT-6: COMPLETED / ACCEPTED / PUSHED
RT-7: CURRENT / NOT_COMPLETED
RT-7a: IMPLEMENTED / AWAITING_REVIEW
DRC baseline: c3c78316fd2bcd4f9939dcaadc32134a704374cf
Framework version: 5.4.0
Framework reference commit: d313eb6acb643103fe25988720ebee5976a04f78
change surface: exact 7 documentation/static-gate files
readiness: BLOCKED_FRAMEWORK_REAL_MOTION_ADAPTER_RELEASE_REQUIRED
commit/push: NOT_AUTHORIZED
```

## Purpose

RT-7a freezes the accepted RT-6 mock-motion path and records the exact
prerequisite for real Live2D / VTube Studio execution. It is an inventory and
requirement checkpoint only. It does not implement or execute a real adapter.

The accepted DRC path remains:

```text
explicit HomeScreen Apply
→ bounded local Backend presentation route
→ accepted app-owned motion mapper
→ accepted FW root-public mock MotionSession adapter
→ normalized mock-only result
→ bounded Flutter presentation
```

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

The public contract already provides typed states including:

```text
disabled
mock_available
not_configured
token_missing
provider_execution_not_allowed
runtime_not_installed
model_not_selected
not_implemented
unsupported_adapter
closed
```

The released implementation is intentionally mock-safe. The mock adapter is
local and credential-free. For `live2d`, `vts`, or `vtube_studio`, real adapter
support remains false and an explicitly enabled provider path resolves to a
typed not-implemented capability/result. The session does not connect to VTube
Studio, open a WebSocket, read a token, load a private model or Live2D runtime,
or import provider SDK modules.

## Readiness decision

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

DRC cannot make the missing capability real by importing
`framework.motion`, `framework.motion_session`, internal/provider modules, or a
VTS library directly. DRC also cannot add a provider-specific VTS client that
bypasses the Framework root-public boundary.

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

After a released Framework update, DRC must perform a separate exact-contract
reassessment before any runtime change. That future review may consider a
default-off Backend root-public real-adapter assembly, bounded typed API
responses, reuse of the accepted Flutter presentation path, and configured PC
operator acceptance. Smartphone end-to-end evidence remains RT-8 work.

## Exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7a_real_motion_adapter_readiness.md
scripts/check_v300_rt7a_real_motion_adapter_readiness.py
```

No Backend runtime, Flutter runtime, existing test, dependency, lockfile,
platform manifest, environment profile, asset, version, release record, or
Framework source file is changed.

## Verification contract

```text
python -m compileall -q backend scripts
python scripts/check_v300_rt7a_real_motion_adapter_readiness.py
python -m pytest -q backend/tests
cd app
flutter analyze
flutter test
cd ..
git -c core.whitespace=cr-at-eol diff --check
git status --short
```

Normal mode requires DRC `HEAD` and `origin/main` at `c3c78316fd2bcd4f9939dcaadc32134a704374cf`, a clean FW v5.4.0
checkout at `d313eb6acb643103fe25988720ebee5976a04f78`, and an exact seven-file DRC candidate surface. Snapshot mode
skips Git identity checks but preserves documentation and DRC source checks.

## Non-actions and non-claims

RT-7a performs no HTTP, provider, network, WebSocket, VTS, Live2D, token,
credential, private model, microphone, audio, STT, LLM, TTS, screenshot, or
operator execution. It changes no runtime or existing test and does not
indicate that a real adapter is available.

## Next action

```text
Review and verify the exact seven-file RT-7a candidate.
Commit/push remains NOT_AUTHORIZED.
RT-7 real runtime remains blocked pending a released Framework adapter.
```
