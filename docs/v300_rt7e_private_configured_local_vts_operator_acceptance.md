# Daily Rhythm Companion v3.0.0 RT-7e private configured local VTS operator acceptance

Updated: 2026-08-03

## Current state

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7d: COMPLETED / ACCEPTED / PUSHED
RT-7e Stage 1: COMPLETED / VERIFIED / PUSHED
RT-7e operator corrective: COMPLETED / VERIFIED / COMMITTED / PUSHED
RT-7e operator corrective commit: 84429683d5ea26e5480bff17f5e29ad201b6ee71
Control A: PASS
Control B: PASS / ACCEPTED
Control B exactly-one POST: PASS
Control B process cleanup: PASS
Control C contract corrective: IMPLEMENTED / AWAITING_REVIEW
Control C execution: NOT_AUTHORIZED
Control D: BLOCKED_PENDING_CONTROL_C_PASS
Control E: BLOCKED_PENDING_CONTROLS_C_AND_D
RT-7e acceptance sync: NOT_AUTHORIZED
Control C corrective commit / push: NOT_AUTHORIZED
```

## Control B accepted result

Control B used the corrected operator contract and completed exactly one Backend
POST. The Backend returned a completed one-command result, closed the Framework
session, and reported provider and network execution. The fixed Framework
transport and Backend correctly kept `real_motion_executed: false`.

The operator watched the VTube Studio model, visibly observed the configured
acceptance gesture caused by that request, and typed exactly `ACCEPT`. Only that
operator observation promoted the final Control B real-motion acceptance.

Afterward, the Backend was stopped, process-local real-execution flags were
restored to zero, private process values were removed, and no additional
provider or motion execution occurred.

## Why Control C needs a separate contract corrective

The earlier Stage 2 wording expected Flutter to display
`real_motion_executed: true` after explicit Apply. That expectation is
incompatible with the accepted fixed Framework v5.5.0 contract.

The fixed Framework can verify that the provider hotkey request completed, but
it does not claim that a physical Live2D change was visible. The Backend
therefore returns `real_motion_executed: false` even on a completed provider
request. Flutter parses that Backend boolean and displays it without promoting
or rewriting it.

Control C must consequently separate these two facts:

```text
Backend / Flutter transport fact:
real_motion_executed: false

Operator-observed physical fact:
configured gesture visibly occurred after the one explicit Flutter Apply
```

The operator observation promotes final Control C acceptance outside the
Backend response and outside the Flutter result model. No Backend or Flutter
runtime field is rewritten.

## Exact Control C contract-corrective surface

```text
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
```

Protected and unchanged:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
vendor/**
backend/.env.example
backend/requirements*.txt
release/**
version metadata
fixed ZIPs
tags
GitHub Releases
Framework development checkout
private environment files
private token files
VTube Studio model and hotkey configuration
```

This corrective changes no Backend runtime, Flutter runtime, fixed vendored
Framework, dependency, private configuration, release artifact, tag, or GitHub
Release. It performs no HTTP request, provider import, WebSocket connection,
VTube Studio operation, or real motion.

## Accepted runtime reused without modification

Control C reuses the accepted RT-7d Flutter path:

```text
explicit Flutter compile-time enablement
→ HomeScreen session-local opt-in
→ intent gesture
→ public selector alias rt7e_acceptance_gesture
→ Apply one VTS command exactly once
→ POST /demo/character-motion/vts/presentation
→ one bounded gesture command
→ private Backend configuration loader
→ accepted FrameworkVtsMotionSessionAdapter
→ fixed vendor/ai-character-framework-5.5.0 root-public facade
→ local VTube Studio
```

Flutter configuration remains default off through:

```text
DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION=false
```

Control C requires explicit compile-time enablement:

```text
--dart-define=DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION=true
```

The Flutter runtime uses one POST, disables redirects, applies a 10-second
timeout, accepts JSON only, and limits the response to 65536 bytes.

## Correct Control C execution contract

Control C is separately authorized only after this exact two-file corrective
passes review, verification, commit, push, and clean-tree checks.

The operator must:

```text
1. Start the Backend with private values loaded process-locally.
2. Set DRC_SKIP_BACKEND_DOTENV=1 so backend/.env cannot override them.
3. Open Backend real-adapter and provider-execution flags only in that process.
4. Start Flutter with DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION=true.
5. Confirm the Configured VTS Motion panel reports Configuration: configured.
6. Turn the session-local VTS motion opt-in on.
7. Select intent gesture.
8. Enter the public alias rt7e_acceptance_gesture.
9. Return the VTube Studio model to its normal pre-gesture state.
10. Press Apply one VTS command exactly once.
11. Do not press Apply again.
```

The Flutter UI must show the completed Backend result:

```text
Configuration: configured
Opt-in: on
Intent: gesture
Phase: completed
Status: completed
Reason: framework_vts_motion_completed
Commands requested: 1
Commands applied: 1
Commands completed: 1
Optional skips: 0
Command outcome: completed
Framework import attempted: true
Session created: true
Session closed: true
Provider attempted: true
Network attempted: true
Real motion executed: false
```

`Real motion executed: false` is mandatory and correct at the Backend/Flutter
boundary. A value of `true` would claim a physical observation that neither the
fixed Framework nor Flutter can establish.

While the Apply request is executing, the operator must watch the VTube Studio
model. Control C final real motion is accepted only when the configured gesture
is visibly observed as a result of that single Apply.

The Control C record may therefore state:

```text
Flutter Backend contract: completed / 1-1-1 / session closed
Flutter Backend real_motion_executed: false
operator visible motion confirmed: true
Control C final real motion accepted: true
Flutter Apply count: exactly 1
```

No raw Backend JSON, provider payload, WebSocket payload, token, endpoint,
hotkey name, hotkey identifier, model identity, private path, LAN IP,
screenshot, VTS log, or operator evidence file may be displayed, pasted, or
committed.

## Control D and Control E after Control C

Control D remains blocked until Control C passes. It must verify that Reset local state, turning opt-in off, and Flutter disposal produce no additional
Backend request, provider execution, network execution, or visible motion.

Control E remains blocked until Controls C and D pass. It must restore every
process-local real-execution flag to zero, remove private process values, stop
Backend and Flutter processes, and verify the DRC working tree is clean.

## Corrective verification

Run from the DRC repository root while all private execution flags remain
closed and no Backend, Flutter runtime, or VTube Studio provider operation is
started:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
python -m pytest -q backend\tests\test_v300_rt7e_private_configured_local_vts_operator.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

Expected Control C contract-corrective gate state:

```text
Control C contract corrective status: implemented-awaiting-review
baseline: 84429683d5ea26e5480bff17f5e29ad201b6ee71
exact change surface: true
change file count: 2
Control B accepted: true
Backend runtime changed: false
Flutter runtime changed: false
vendor Framework changed: false
Flutter compile flag explicit: true
Flutter session opt-in required: true
Flutter explicit Apply exactly one: true
Flutter Backend real-motion marker required false: true
operator visual confirmation promotes Control C real motion: true
private configuration read: false
provider execution attempted: false
network execution attempted: false
real motion executed: false
Control C execution authorized: false
acceptance sync authorized: false
commit / push authorized: false
```

RT-7e acceptance sync remains a separate later authorization and is not part of
this corrective.
