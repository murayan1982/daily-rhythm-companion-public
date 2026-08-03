# Daily Rhythm Companion v3.0.0 RT-7e configured local VTS operator acceptance

Updated: 2026-08-03

## Accepted state

```text
RT-7: COMPLETED / ACCEPTED
RT-7e: COMPLETED / ACCEPTED / PUSHED
Stage 1: COMPLETED / VERIFIED / COMMITTED / PUSHED
Stage 1 commit: c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f
operator corrective: COMPLETED / VERIFIED / COMMITTED / PUSHED
operator corrective commit: 84429683d5ea26e5480bff17f5e29ad201b6ee71
Control C contract corrective: COMPLETED / VERIFIED / COMMITTED / PUSHED
Control C contract corrective commit: a26d027fcd40d6734cb8919059a4683c322f55da
Control D docs/test-only corrective: COMPLETED / VERIFIED / COMMITTED / PUSHED
Control D docs/test-only corrective commit: ddd392c24907eae4d8c91850d84b31a7b84e760f
Control A: PASS / ACCEPTED
Control B: PASS / ACCEPTED
Control C: PASS / ACCEPTED
Control D: PASS / ACCEPTED
Control E: PASS / ACCEPTED
RT-8 exact contract review: READY
RT-8 implementation: NOT_AUTHORIZED
v3.0.0 release: NOT_RELEASED
```

RT-7e accepts a private configured local VTube Studio gesture only through the
already accepted RT-7d Backend/API/Flutter boundary and the fixed vendored AI
Character Framework v5.5.0 root-public VTS session facade. DRC does not add a
provider client, import Framework internals, or directly import `pyvts` or
`websockets`.

## Evidence classification

The Backend and Flutter contract correctly remains:

```text
status: completed
commands requested / applied / completed: 1 / 1 / 1
Framework session created: true
Framework session closed: true
provider execution attempted: true
network execution attempted: true
Backend / Flutter real_motion_executed: false
```

`real_motion_executed: false` is mandatory. Neither the fixed Framework nor DRC
can prove a physical display observation. The accepted physical result is
therefore recorded separately:

```text
operator-visible physical motion confirmed: true
final configured local VTS motion accepted: true
```

The operator observation is not promoted into an API response, Flutter model,
persistent record, log, release artifact, or committed evidence file.

## Accepted commit chain and exact surfaces

### Stage 1 operator tooling

```text
baseline: 715b28a97f46260efc0bd76e59828d46c8749dbd
commit: c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f
exact files: 9
```

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

Stage 1 added an inert-by-default operator runner, focused credential-free
tests, documentation, and a static gate. Without `--execute-real-vts`, it makes
zero HTTP requests and performs no Framework/provider/network/motion operation.

### Operator contract corrective

```text
baseline: c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f
commit: 84429683d5ea26e5480bff17f5e29ad201b6ee71
exact files: 4
```

```text
backend/tests/test_v300_rt7e_private_configured_local_vts_operator.py
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
scripts/run_v300_rt7e_private_configured_local_vts_operator.py
```

The corrective retained one local fixed gesture, one POST, no redirect, no
retry, a 10-second timeout, a 65536-byte response bound, allowlisted output,
and explicit operator-visible confirmation.

### Control C contract corrective

```text
baseline: 84429683d5ea26e5480bff17f5e29ad201b6ee71
commit: a26d027fcd40d6734cb8919059a4683c322f55da
exact files: 2
```

```text
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
```

The public Flutter selector remains `rt7e_acceptance_gesture`. The private
Backend selector was corrected process-locally to
`gesture:rt7e_acceptance_gesture`; no private hotkey value was recorded.

### Control D local-lifecycle corrective

```text
baseline: a26d027fcd40d6734cb8919059a4683c322f55da
commit: ddd392c24907eae4d8c91850d84b31a7b84e760f
exact files: 3
```

```text
app/test/framework_vts_motion_home_screen_test.dart
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
```

The deterministic widget test proves that, after one completed Apply, Reset
local state, opt-in OFF, and HomeScreen disposal leave the fake transport call
count exactly one.

### Control E acceptance synchronization

```text
baseline: ddd392c24907eae4d8c91850d84b31a7b84e760f
exact files: 7
```

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7e_private_configured_local_vts_operator_acceptance.md
scripts/check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
```

Control E changes documentation and the historical static gate only. It changes
no Backend runtime, Flutter runtime, existing test, fixed vendor Framework,
dependency, private configuration, version, release artifact, tag, or GitHub
Release.

## Control chronology

### Control A — inert default

```text
runner execution flag absent: true
HTTP request attempted: false
provider execution attempted: false
network execution attempted: false
real motion executed: false
result: PASS / ACCEPTED
```

### Control B — operator runner exactly-one POST

```text
explicit execution: separately authorized
local request count: exactly 1
Backend status: completed
commands requested / applied / completed: 1 / 1 / 1
Backend real_motion_executed: false
operator-visible gesture confirmed: true
result: PASS / ACCEPTED
```

The recognized local Backend process was stopped after the control and private
process-local values were removed.

### Control C — Flutter Apply

Control C used two bounded attempts.

```text
first attempt:
Flutter Apply count: exactly 1
failed before Framework session creation
provider execution attempted: false
network execution attempted: false
visible motion accepted: false
result: FAILED / NOT_ACCEPTED

private selector corrective:
bare private selector rejected by fixed FW v5.5.0
correct private selector: gesture:rt7e_acceptance_gesture
public Flutter selector remains: rt7e_acceptance_gesture
private hotkey value preserved outside Git
execution flags remained closed during correction

retry:
separately authorized
Flutter Apply count: exactly 1
Backend status: completed
commands requested / applied / completed: 1 / 1 / 1
Framework session created and closed: true
provider execution attempted: true
network execution attempted: true
Backend / Flutter real_motion_executed: false
operator-visible motion confirmed: true
result: PASS / ACCEPTED
```

Cleanup after the accepted retry:

```text
recognized RT-7e Backend listener stopped
local Backend port closed
private execution flags closed
private process values removed
additional Apply count: 0
additional provider/network/real-motion execution: false
operator evidence files retained: false
DRC working tree clean
```

### Control D — local reset, opt-out, and disposal

The accepted Flutter instance had already been disposed during Control C
cleanup, so the lifecycle claims were not made retroactively. A deterministic
fake-transport widget test executes:

```text
1. Build configured HomeScreen with fake transport.
2. Turn session-local opt-in ON.
3. Press Apply exactly once and display completed / 1-1-1.
4. Press Reset local state; transport count remains exactly one.
5. Turn opt-in OFF; transport count remains exactly one.
6. Dispose HomeScreen; transport count remains exactly one.
```

This proves:

```text
Reset local state additional Backend request: false
opt-in OFF additional Backend request: false
Flutter disposal additional Backend request: false
additional provider execution: false
additional network execution: false
additional visible motion: false
result: PASS / ACCEPTED
```

Control D does not authorize or require a second real VTube Studio execution.

### Control E — aggregate cleanup and acceptance synchronization

Control E reuses the accepted Control C cleanup evidence and Control D
local-only proof. It does not start or call Backend, Flutter, Framework, a
provider, a network, a WebSocket, VTube Studio, or motion execution.

```text
additional Flutter Apply: false
additional Backend request: false
additional provider execution: false
additional network execution: false
additional visible motion: false
private configuration read: false
private process values present: false
real-execution flags open: false
recognized local Backend/Flutter processes left running: false
operator evidence file committed: false
DRC HEAD / origin/main before Control E candidate: ddd392c24907eae4d8c91850d84b31a7b84e760f
DRC working tree before Control E candidate: clean
result: PASS / ACCEPTED
```

## Protected and unchanged

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
scripts/run_v300_rt7e_private_configured_local_vts_operator.py
vendor/**
backend/.env.example
backend/requirements*.txt
app/pubspec.yaml
platform declarations and generated registration
assets
version metadata
release/**
release_notes/**
fixed ZIPs
tags
GitHub Releases
Framework development checkout
private environment files
private token files
private endpoint values
VTube Studio model/hotkey configuration
screenshots, logs, payloads, responses, and operator evidence files
```

Historical RT-7b, RT-7c, and RT-7d documents and gates remain unchanged. Their
older `NOT_AUTHORIZED` markers describe their own historical checkpoints and
must not be mass-rewritten.

## Privacy contract

No private endpoint, token, hotkey value, hotkey identifier, model identity,
provider payload, WebSocket payload, raw Backend response, raw exception,
private path, LAN IP, screenshot, VTube Studio log, or operator evidence file
may be displayed, pasted, committed, packaged, or published.

The public aliases `rt7e_acceptance_gesture` and
`gesture:rt7e_acceptance_gesture` are contract markers, not private hotkey
values.

## Historical Control E verification

Run from the DRC repository root with all private execution flags closed and no
Backend, Flutter runtime, or VTube Studio provider operation running:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
python -m pytest -q backend\tests\test_v300_rt7e_private_configured_local_vts_operator.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test test\framework_vts_motion_home_screen_test.dart
flutter test
cd ..

python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

Expected pre-commit gate markers:

```text
Control E acceptance-sync status: implemented-awaiting-review
HEAD / origin/main baseline: ddd392c24907eae4d8c91850d84b31a7b84e760f
Stage 1 exact surface: true / 9 files
operator corrective exact surface: true / 4 files
Control C corrective exact surface: true / 2 files
Control D corrective exact surface: true / 3 files
Control E exact surface: true / 7 files
Controls A-E accepted markers: true
Backend runtime changed by Control E: false
Flutter runtime changed by Control E: false
existing tests changed by Control E: false
vendor Framework changed by Control E: false
private configuration read: false
provider execution attempted: false
network execution attempted: false
real motion executed: false
RT-8 exact contract review ready: true
RT-8 implementation authorized: false
Control E gate authorizes commit / push: false
```

The gate is credential-free and network-free. `--snapshot` validates source
content and protected boundaries in an extracted tracked-source snapshot, but
it does not claim independent verification of Git history, origin/main, or the
current exact worktree surface.
