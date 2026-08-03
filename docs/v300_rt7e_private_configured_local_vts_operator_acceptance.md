# Daily Rhythm Companion v3.0.0 RT-7e private configured local VTS operator acceptance

Updated: 2026-08-03

## Current state

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7d: COMPLETED / ACCEPTED / PUSHED
RT-7e Stage 1: COMPLETED / VERIFIED / PUSHED
RT-7e operator corrective: IMPLEMENTED / AWAITING_REVIEW
RT-7e corrective baseline: c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f
RT-7e corrective surface: exact 4 files
Control A: PASS
Control B first attempt: NOT_ACCEPTED
Control B corrective attempt: NOT_ACCEPTED
manual VTube Studio hotkey verification: PASS
private binding rewritten: PASS / execution flags closed
additional real VTube Studio execution: NOT_AUTHORIZED
RT-7e acceptance sync: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```

## Corrective purpose

The Stage 1 runner required the Backend response to claim
`real_motion_executed: true` before asking the operator whether physical motion
was visible. That contract does not match the fixed Framework v5.5.0 transport.

The fixed transport can verify that the provider hotkey request completed and
that the configured hotkey name resolved, but it intentionally keeps physical
motion claims false. Physical motion is accepted only when the operator watches
the VTube Studio model and types exactly `ACCEPT` after observing the configured
gesture.

This corrective therefore requires Backend `real_motion_executed: false` before
the prompt. Successful operator confirmation promotes the final real-motion
acceptance in the runner only; it does not rewrite the Backend response.

## Exact corrective surface

```text
scripts/run_v300_rt7e_private_configured_local_vts_operator.py
backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
```

Protected and unchanged:

```text
backend/app/**
app/**
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

The corrective changes no Backend runtime, Flutter runtime, fixed vendored
Framework, dependency, private configuration, release artifact, tag, or GitHub
Release.

## Accepted runtime reused without modification

RT-7e continues to reuse the accepted RT-7d path:

```text
explicit HomeScreen Apply
→ POST /demo/character-motion/vts/presentation
→ one bounded gesture command
→ private Backend configuration loader
→ accepted FrameworkVtsMotionSessionAdapter
→ fixed vendor/ai-character-framework-5.5.0 root-public facade
→ local VTube Studio
```

The fixed request remains:

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

Transport remains one POST, no redirect, no retry, no loop, a 10-second timeout,
JSON only, and at most 65536 response bytes.

## Corrected Backend response contract

Before any visual confirmation, the runner requires all of the following:

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
Backend real_motion_executed: false
command_results: exactly one
command intent: gesture
command outcome: completed
command skipped: false
```

`Backend real_motion_executed: false` is mandatory. A Backend value of `true`
before visual confirmation fails closed because it would claim physical motion
without operator evidence.

After the Backend contract passes, the runner prints:

```text
v300_rt7e_operator_backend_contract_valid: True
v300_rt7e_operator_backend_real_motion_executed: False
```

It then asks exactly once whether the configured gesture was visibly observed.
Only an exact `ACCEPT` succeeds. The operator confirmation promotes the final
real-motion acceptance and produces:

```text
v300_rt7e_operator_visible_motion_confirmed: True
v300_rt7e_operator_real_motion_executed: True
```

`ACCEPT` must be entered only while watching the VTube Studio model and only
when the configured gesture is visibly performed by that request.

## Allowlisted safe diagnostics

A non-completed or malformed semantic result fails closed. The runner never
prints raw response JSON. For a structured failed Backend result, it may print
only these allowlisted safe diagnostics:

```text
status
reason_code
commands_requested
commands_applied
commands_completed
session_created
session_closed
provider_execution_attempted
network_execution_attempted
Backend real_motion_executed
command intent
command outcome
command public_error_code
command retryable
```

String values are checked against fixed public allowlists. Counts must be
bounded integers and booleans must be literal booleans; otherwise the diagnostic
value becomes `unrecognized`.

The runner must not display or derive the private token, endpoint, hotkey name,
hotkey identifier, model identity, provider payload, WebSocket payload, raw
response, raw exception, private path, LAN IP, screenshot, VTS log, or operator
evidence file.

## Corrective focused tests

The exact nine credential-free tests verify:

```text
1. no explicit flag performs zero requests
2. non-fixed or non-loopback Backend URL is rejected
3. the fixed gesture performs exactly one POST and requires operator acceptance
4. redirects are never followed
5. the response is bounded to 65536 bytes
6. Backend real-motion must remain false before operator confirmation
7. negative visual confirmation never promotes real motion
8. failed results print only allowlisted safe diagnostics
9. successful output never echoes private or raw response fields
```

## Corrective verification

Run from the DRC repository root while all private execution flags remain
closed and no Backend or VTube Studio provider operation is started:

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

Expected corrective gate state:

```text
corrective status: implemented-awaiting-review
exact change surface: true
change file count: 4
Backend runtime changed: false
Flutter runtime changed: false
vendor Framework changed: false
private configuration read: false
provider execution attempted: false
network execution attempted: false
real motion executed: false
Backend real-motion marker required false: true
operator confirmation promotes real motion: true
allowlisted safe diagnostics: true
additional real execution authorized: false
acceptance sync authorized: false
commit / push authorized: false
```

## Stage 2 state after corrective review

The corrective implementation does not authorize another provider request.
After the exact four-file candidate passes review, tests, commit, push, and
clean-tree verification, Control B may be separately authorized for one new
attempt using the rewritten private binding.

```text
Control A: PASS
Control B: BLOCKED_PENDING_CORRECTIVE_ACCEPTANCE
Control C: BLOCKED_PENDING_CONTROL_B_PASS
Control D: BLOCKED_PENDING_CONTROL_C_PASS
Control E: BLOCKED_PENDING_CONTROLS_B_TO_D
```

RT-7e acceptance sync remains a separate later authorization and is not part of
this corrective commit.
