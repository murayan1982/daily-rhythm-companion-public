# Daily Rhythm Companion v3.0.0 RT-8c configured PC Windows realtime acceptance

Updated: 2026-08-03

## Stage 1 candidate state

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8b: COMPLETED / ACCEPTED / PUSHED
RT-8b1: COMPLETED / ACCEPTED / PUSHED
RT-8b1 commit: 4815403d4c94b05551df03678e9c2c4e1dfe754e
RT-8c Stage 1: IMPLEMENTED / AWAITING_REVIEW
RT-8c Stage 1 surface: exact 9 files
RT-8c Stage 2: NOT_AUTHORIZED
RT-8c Stage 3: NOT_AUTHORIZED
RT-8d: BLOCKED_PENDING_RT8C_ACCEPTANCE / NOT_AUTHORIZED
schema: drc.v3.rt8-platform-acceptance.2
private manifest created: false
private manifest read: false
private configuration read: false
Backend / Flutter started: false
provider / network execution attempted: false
real TTS / playback / VTS executed: false
commit / push: NOT_AUTHORIZED
```

## Purpose

Stage 1 adds only credential-free operator tooling, focused synthetic tests,
this runbook, and a static gate. It changes no Backend runtime, Flutter runtime,
Framework source, fixed vendor, dependency, platform declaration, version, or
release artifact.

The operator runner does not execute Controls A-H. It cannot start Backend,
Flutter, a provider, audio playback, or VTube Studio and contains no HTTP,
socket, provider SDK, microphone, audio, `pyvts`, or `websockets` client. Its
only later authorized write is one ignored strict manifest after fixed operator
confirmations.

## Three-stage split

```text
Stage 1: tracked credential-free tooling -> review -> commit/push
Stage 2: private PC Controls A-H -> ignored manifest -> strict validation
Stage 3: exact seven-file public-safe acceptance synchronization
```

Stage 2 must use the accepted Stage 1 commit as the clean synchronized PC
candidate source HEAD. Stage 1 creates and reads no private manifest.

## Exact Stage 1 surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md
scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py
scripts/run_v300_rt8c_private_pc_windows_operator.py
backend/tests/test_v300_rt8c_private_pc_windows_operator.py
```

## Fixed PC execution chronology

The later separately authorized operator sequence is exactly:

```text
A -> B -> D -> C -> E -> F -> G -> H
```

B must finish before D uses its completed terminal. D must finish before C
replaces the visible stream terminal with a cancelled result. E then creates the
second completed terminal and second TTS playback used for flush.

## Controls and exact counts

### A — inert/default-off

Normal Windows startup without RT-8c defines performs no configured execution.
Configured startup also begins with every session-local opt-in off and performs
no stream, TTS, mock-motion, or VTS action before explicit operator input.

### B — stream 1 completed

One bounded manual stream produces incremental output before one completed
terminal. It starts no automatic TTS.

### D — TTS 1 natural completion

The B terminal is explicitly enqueued and explicitly processed once. Real
root-public synthesis succeeds and audible local playback completes naturally.

### C — stream 2 cooperative cancellation

A second bounded manual stream receives exactly one cooperative cancel request,
reaches one cancelled terminal, retains partial output, and makes no provider or
Backend hard-cancel claim. A cancelled terminal is not enqueued for TTS.

### E — stream 3, TTS 2, active-playback flush

A third manual stream creates the second completed terminal. It is explicitly
enqueued and processed. During active playback, one explicit app-owned flush
requests and succeeds in stopping the local player and leaves pending zero and
active false. No Framework queue flush or provider hard cancel is claimed.

### F — app-owned mock motion

Exactly one explicit RT-6f speaking Apply completes through the mock adapter.
Provider execution, external Framework network execution, and real provider
motion remain false.

### G — manual real VTS

Exactly one RT-7d Flutter Apply uses the public gesture alias and reports one
requested/applied/completed command, Framework session created/closed,
provider/network attempted true, Backend/Flutter `real_motion_executed=false`,
and separate operator-visible physical motion true.

The historical RT-7e runner must not be executed in real mode during RT-8c.

```text
total real VTS executions: exactly 1
```

### H — lifecycle and cleanup

RT-6 and RT-7 local reset, opt-out, and Flutter disposal cause no additional
Backend request, provider execution, network execution, or visible motion.
Recognized processes are stopped, flags closed, private process values removed,
local generated artifacts/logs/backups removed, and DRC/FW trees left clean.

Exact accepted counts:

```text
manual_stream_start_count: 3
completed_stream_terminal_count: 2
cancelled_stream_terminal_count: 1
cooperative_cancel_request_count: 1
explicit_tts_enqueue_count: 2
explicit_tts_process_count: 2
explicit_flush_count: 1
pending_after_flush: 0
app_owned_motion_presentation_count: 1
manual_vts_apply_count: 1
vts_commands_requested: 1
vts_commands_applied: 1
vts_commands_completed: 1
```

PC Windows acceptance does not use or claim real microphone, STT, soft
barge-in, always-on capture, automatic next-turn capture, provider hard cancel,
Framework unified realtime, automatic voice-motion synchronization, or physical
motion proof from runtime state.

## Runner modes

Credential-free inert check:

```powershell
python scripts\run_v300_rt8c_private_pc_windows_operator.py --check-inert
```

Later Stage 2 preflight:

```powershell
python scripts\run_v300_rt8c_private_pc_windows_operator.py `
  --preflight `
  --expected-source-head <RT8C_STAGE1_ACCEPTED_COMMIT>
```

Later Stage 2 manifest recording:

```powershell
python scripts\run_v300_rt8c_private_pc_windows_operator.py `
  --record-pc-windows `
  --expected-source-head <RT8C_STAGE1_ACCEPTED_COMMIT>
```

The recorder accepts only:

```text
PASS-PC-A
PASS-PC-B
PASS-PC-C
PASS-PC-D
PASS-PC-E
PASS-PC-F
PASS-PC-G
PASS-PC-H
ACCEPT-PC-WINDOWS
```

It accepts no free-form evidence and writes only the fixed ignored target. An
existing target or symlink is rejected without reading or overwriting it.

## Stage 2 validation command

Not authorized by Stage 1:

```powershell
python scripts\validate_v300_rt8_private_operator_manifest.py `
  --manifest-json operator_evidence\v300_rt8_pc_android_realtime_acceptance.json `
  --stage pc-windows `
  --minimum-source-head 4815403d4c94b05551df03678e9c2c4e1dfe754e
```

After Stage 1 acceptance, the PC candidate source field must be the Stage 1
commit, while this minimum source remains the accepted RT-8b1 commit.

## Focused tests

The exact twelve credential-free tests cover inert mode, synthetic clean
preflight, wrong HEAD, dirty tree, fixed target boundary, nonignored target,
existing target without read, symlink target, rejected confirmation, exact
manifest creation, strict schema-v2 validation, and output redaction.

## Stage 3 surface

Only after PC Controls A-H and strict validation pass:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md
scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py
```

## Protected and unchanged

```text
backend/app/**
app/**
vendor/**
.gitignore
backend/.env.example
backend/env_profiles/**
backend/requirements*.txt
app/pubspec.yaml
app/pubspec.lock
platform declarations
assets
versions
release/**
release_notes/**
tags and GitHub Releases
Framework development checkout
private environment files
operator_evidence/**
historical RT-4 through RT-8b1 contracts and gates
```

## Stage 1 stop rule

After automated verification, stop for exact diff and privacy review. Do not
create/read a private manifest, read private configuration, start Backend or
Flutter, use a microphone, call a provider, synthesize/play audio, connect to
VTube Studio, execute physical motion, start Stage 2/3, or commit/push without
separate approval.
