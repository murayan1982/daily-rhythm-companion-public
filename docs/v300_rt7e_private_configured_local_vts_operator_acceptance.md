# Daily Rhythm Companion v3.0.0 RT-7e private configured local VTS operator acceptance

Updated: 2026-08-03

## Current state

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7d: COMPLETED / ACCEPTED / PUSHED
RT-7e operator tooling: IMPLEMENTED / AWAITING_REVIEW
RT-7e baseline: 715b28a97f46260efc0bd76e59828d46c8749dbd
RT-7e Stage 1 surface: exact 9 files
real VTube Studio operator execution: NOT_AUTHORIZED
private token / hotkey read: NOT_AUTHORIZED
RT-7e acceptance sync: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-7e is split into two separately authorized stages.

```text
Stage 1: credential-free operator tooling implementation and tests
Stage 2: private configured local VTube Studio execution and acceptance
```

Stage 1 adds only documentation, an inert-by-default local operator runner, a
credential-free test module, and a static exact-surface gate. It changes no
Backend runtime, Flutter runtime, accepted RT-7d route, fixed vendor Framework,
dependency, version, release artifact, tag, or GitHub Release.

Stage 1 does not read `backend/.env`, import the Framework, call the Backend,
open a WebSocket, execute a provider request, access VTube Studio, or perform
real motion. Stage 2 remains separately unauthorized until Stage 1 has passed
review, commit, push, and clean-tree verification.

## Accepted runtime reused without modification

RT-7e reuses the accepted RT-7d path unchanged:

```text
explicit HomeScreen Apply
→ POST /demo/character-motion/vts/presentation
→ one bounded command
→ private Backend configuration loader
→ accepted FrameworkVtsMotionSessionAdapter
→ fixed vendor/ai-character-framework-5.5.0 root-public facade
→ local VTube Studio
```

The accepted route remains default off at Flutter compile time, HomeScreen
session opt-in, Backend adapter enablement, and Backend provider execution.

## Exact Stage 1 surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
scripts/run_v300_rt7e_private_configured_local_vts_operator.py
backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py
```

Protected and unchanged:

```text
backend/app/**
backend/.env.example
backend/requirements*.txt
app/lib/**
app/test/**
vendor/**
release/**
version metadata
fixed ZIPs
tags
GitHub Releases
Framework development checkout
```

## Inert-by-default operator runner

The runner is:

```text
scripts/run_v300_rt7e_private_configured_local_vts_operator.py
```

Without `--execute-real-vts`, it exits without any HTTP, Framework, provider,
network, or motion operation and prints only public-safe false markers.

The only accepted Backend base URL is exactly:

```text
http://127.0.0.1:8000
```

A changed port, hostname, localhost alias, LAN address, remote address, user
information, query, or fragment is rejected before transport.

When separately authorized in Stage 2, the runner sends exactly one POST to:

```text
http://127.0.0.1:8000/demo/character-motion/vts/presentation
```

The fixed request is:

```json
{
  "schema_version": "drc.v3.framework-vts-motion-presentation-request.1",
  "command": {
    "order": 1,
    "intent": "gesture",
    "expression": null,
    "emotion": null,
    "gesture": "rt7e_acceptance_gesture",
    "character_id": null
  }
}
```

The public alias `gesture:rt7e_acceptance_gesture` is mapped only inside the
ignored private Backend configuration to an actual private VTube Studio hotkey
identifier. The runner never receives or displays that identifier.

Transport is bounded to one POST, no redirect, no retry, no loop, a 10-second
request timeout, `application/json`, and at most 65536 response bytes.

## Result acceptance markers

The runner does not print raw response JSON. It accepts only a bounded result
with all of the following markers:

```text
schema_version: drc.v3.framework-vts-motion-execution.1
status: completed
commands_requested: 1
commands_applied: 1
commands_completed: 1
optional_commands_skipped: 0
framework_import_attempted: true
session_created: true
session_closed: true
real_adapter_enabled: true
provider_execution_allowed: true
provider_execution_attempted: true
network_execution_attempted: true
real_motion_executed: true
command_results: exactly one
command intent: gesture
command outcome: completed
command skipped: false
```

After those markers pass, the runner asks once whether the configured gesture
was visibly observed in VTube Studio. The operator must type exactly `ACCEPT`.
A missing marker, non-literal boolean, malformed result, transport failure,
negative visual confirmation, or EOF fails closed.

## Private Stage 2 configuration

Only after separate authorization, the ignored local `backend/.env` may contain:

```text
DRC_RT7_ENABLE_FRAMEWORK_VTS_MOTION=1
DRC_RT7_ALLOW_VTS_PROVIDER_EXECUTION=1
DRC_RT7_VTS_RUNTIME_AVAILABLE=1
DRC_RT7_VTS_MODEL_SELECTED=1
DRC_RT7_VTS_ENDPOINT_HOST=127.0.0.1
DRC_RT7_VTS_ENDPOINT_PORT=<private-local-port>
DRC_RT7_VTS_AUTHENTICATION_TOKEN=<private-token>
DRC_RT7_VTS_HOTKEY_BINDINGS_JSON=<private-json>
```

Conceptual binding only:

```json
{
  "gesture:rt7e_acceptance_gesture": "<private-hotkey-id>"
}
```

Actual token, port, hotkey ID, private model identifier, provider payload,
WebSocket payload, raw response, raw exception, private path, LAN IP,
screenshot, VTS log, and operator evidence file must not be displayed, pasted,
or committed.

## Stage 1 focused tests

The exact eight credential-free tests verify:

```text
1. no explicit flag performs zero requests
2. non-fixed or non-loopback Backend URL is rejected
3. fixed gesture request performs exactly one POST
4. redirects are never followed
5. response size is bounded to 65536 bytes
6. a missing completion marker fails closed
7. negative visual confirmation fails
8. output never echoes private or raw response fields
```

## Stage 1 verification

Run from the DRC repository root:

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

Expected Stage 1 state:

```text
operator tooling: implemented-awaiting-review
exact change surface: 9 files
private configuration read: false
provider execution attempted: false
network execution attempted: false
real motion executed: false
real operator execution authorized: false
commit / push authorized: false
```

## Separately authorized Stage 2 controls

Stage 2 is not authorized by this implementation.

```text
Control A: private local VTube Studio readiness
Control B: direct Backend operator runner, exactly one gesture
Control C: Flutter explicit Apply, exactly one gesture
Control D: Reset / opt-out / dispose produce no extra motion
Control E: restore all real flags to zero and verify clean tree
```

RT-7e can be accepted only after both direct Backend and Flutter explicit Apply
show completed 1/1/1 markers, closed session, provider/network/real-motion true,
visible motion confirmed, no extra execution, private-value review, and clean
working tree.
