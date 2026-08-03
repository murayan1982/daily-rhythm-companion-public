# Daily Rhythm Companion v3.0.0 RT-8c configured PC Windows realtime acceptance

Updated: 2026-08-03

## Accepted state

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8b: COMPLETED / ACCEPTED / PUSHED
RT-8b1: COMPLETED / ACCEPTED / PUSHED
RT-8c: COMPLETED / ACCEPTED / PUSHED
RT-8c Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-8c Stage 1 commit: fa39065130a4a4689c2e54195f231a5e79c62a35
RT-8c Stage 2 credential-free preflight: COMPLETED / PASS
RT-8c Stage 2 Controls A-H: COMPLETED / ACCEPTED
RT-8c Stage 2 manifest recording: COMPLETED / ACCEPTED
RT-8c Stage 2 strict validation: COMPLETED / ACCEPTED
RT-8c Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW
RT-8c Stage 3 surface: exact 7 documentation/static-gate files
RT-8d exact contract review: READY
RT-8d implementation: NOT_AUTHORIZED
RT-8e: BLOCKED_PENDING_RT8D / NOT_AUTHORIZED
RT-9: BLOCKED_PENDING_RT8 / NOT_AUTHORIZED
schema: drc.v3.rt8-platform-acceptance.2
acceptance-sync commit / push: NOT_AUTHORIZED
```

RT-8c accepts the configured Windows PC realtime path at the clean synchronized
source commit `fa39065130a4a4689c2e54195f231a5e79c62a35`. The private configured
Controls A-H were executed separately from the tracked tooling, followed by one
ignored PC-stage manifest recording and strict validation. This Stage 3 change
only synchronizes public-safe acceptance facts.

## Stage 1 accepted tooling

```text
implementation baseline: 4815403d4c94b05551df03678e9c2c4e1dfe754e
implementation commit: fa39065130a4a4689c2e54195f231a5e79c62a35
implementation commit message: test/docs: add RT-8c PC Windows operator tooling
implementation surface: exact 9 files
dedicated gate: PASS
inert runner: PASS
focused Backend tests: 12 passed
Backend full regression: 381 passed, 1 existing warning
Flutter analyze: PASS
Flutter full regression: 500 passed
working tree after push: clean
```

Stage 1 added the inert-by-default runner, twelve credential-free focused tests,
this runbook, and the static gate. The runner did not execute Controls A-H. It
performed no Backend/Flutter startup, HTTP request, provider/network operation,
TTS/playback action, VTS action, microphone access, STT, or physical motion.

## Stage 2 preflight

The credential-free preflight passed against the accepted Stage 1 source:

```text
source HEAD verified: true
origin/main synchronized: true
working tree clean: true
fixed target Git ignored: true
private manifest created: false
private manifest read: false
configured execution attempted: false
```

## Fixed operator chronology

The accepted PC sequence was exactly:

```text
A -> B -> D -> C -> E -> F -> G -> H
```

B completed the first stream terminal before D used it for natural TTS
completion. C then replaced the visible stream result with the cancelled
terminal. E created the second completed terminal and used its second playback
for the active-playback flush. F and G were separate explicit motion controls.

## Control A — default-off and configured-idle startup

Normal Windows startup was confirmed unconfigured/default-off. Configured
startup was then confirmed idle with all session-local opt-ins off and no
execution before explicit operator action.

```text
default_off_startup_confirmed: true
execution_before_explicit_action: false
stream state: configured / idle
TTS state: configured / opt-in off / pending 0 / active no
mock motion state: configured / opt-in off / idle
VTS state: configured / opt-in off / idle
integrated voice turn: disabled / unconfigured
```

## Controls B and C — completed stream and cooperative cancellation

Control B performed the first manual stream. Incremental output was visible
before one completed terminal, and no automatic TTS or playback started.

Control C performed the second manual stream. Exactly one cooperative cancel
request reached one cancelled terminal while retaining partial output. No
provider hard cancel or Backend HTTP hard cancel was claimed, and the cancelled
terminal was not enqueued for TTS.

```text
manual stream starts covered by B/C: 2
completed terminals covered by B/C: 1
cancelled terminals covered by B/C: 1
cooperative cancel requests: 1
incremental output before terminal: true
partial output retained: true
provider hard cancel claimed: false
automatic TTS started: false
```

## Controls D and E — real TTS, natural completion, and local flush

Control D explicitly enqueued and processed the first completed terminal once.
Real root-public synthesis succeeded, audible local playback started, and that
playback completed naturally without a flush.

Control E completed the third stream, explicitly enqueued and processed the
second completed terminal once, and pressed the app-owned flush exactly once
while local playback was active. The flush requested and successfully stopped
the local player and left pending zero and active false.

```text
real TTS generated: true
audible playback started: true
first playback completed naturally: true
active playback before flush: true
local playback stop requested: true
local playback stop succeeded: true
pending after flush: 0
active after flush: false
Framework real TTS queue flush claimed: false
provider TTS hard cancel claimed: false
```

## Control F — app-owned mock motion presentation

Exactly one explicit `speaking` lifecycle Apply completed through the RT-6 mock
adapter.

```text
app_owned_motion_presentation_count: 1
presentation phase: completed
execution status: completed
cue: speaking
commands requested: 2
commands completed: 2
adapter: mock
real adapter enabled: false
provider execution attempted: false
network execution: false
```

The repository character image remained static. Control F did not execute
Live2D, VTube Studio, provider motion, or external motion networking.

## Control G — manual configured VTS execution

Exactly one explicit configured VTS Apply used the public gesture alias and
completed one command. The accepted public result separated runtime state from
operator-visible physical motion.

```text
manual_vts_apply_count: 1
vts_commands_requested: 1
vts_commands_applied: 1
vts_commands_completed: 1
optional skips: 0
Framework import attempted: true
Framework session created: true
Framework session closed: true
provider execution attempted: true
network execution attempted: true
Backend / Flutter real_motion_executed: false
operator-visible physical motion confirmed: true
operator-visible physical motion count: 1
historical RT-7e real runner executed: false
```

`Backend / Flutter real_motion_executed: false` is the accepted conservative
runtime value. It is not used as proof of physical motion. The separate operator
observation records that the configured VTube Studio model visibly moved once.

## Control H — reset, opt-out, disposal, and cleanup

The mock-motion and VTS local states were reset, all opt-ins were turned off,
Flutter was disposed, Backend was stopped, and the configured process-local
private values were removed.

```text
reset additional Backend request: false
opt-out additional Backend request: false
disposal additional Backend request: false
additional provider execution: false
additional network execution: false
additional visible motion: false
recognized processes stopped: true
real execution flags closed: true
private process values removed: true
Backend port closed: true
DRC working tree clean: true
DRC HEAD / origin/main synchronized: true
FW working tree clean: true
```

## Exact accepted PC counts

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

## Manifest recording and strict validation

After Controls A-H passed, the operator runner accepted only the nine fixed
confirmation tokens and created one new ignored PC-stage manifest. It did not
execute the controls itself and did not overwrite an existing target.

```text
manifest schema: drc.v3.rt8-platform-acceptance.2
manifest stage: pc-windows
manifest status: accepted
confirmation count: 9
private manifest created: true
private manifest overwritten: false
private manifest content printed: false
private configuration read by runner: false
execution performed by runner: false
strict schema validation: PASS
candidate Git-state validation: PASS
private values printed by validator: false
private manifest remains Git ignored: true
private manifest tracked: false
private manifest committed: false
private manifest pushed: false
working tree after validation: clean
```

The private manifest content is not reproduced in tracked documentation and is
not read by the Stage 3 acceptance-sync gate.

## PC non-claims

RT-8c does not use or claim any of the following:

```text
PC real microphone acceptance
PC real STT acceptance
PC soft barge-in acceptance
always-on microphone
automatic next-turn capture
provider LLM hard cancel
provider STT hard cancel
provider TTS hard cancel
Backend HTTP hard cancel
Framework real TTS queue flush
Framework unified realtime runtime
automatic voice-motion synchronization
automatic emotion inference
physical motion proven by runtime state
Web or iOS acceptance
all Android devices accepted
production security readiness
v3.0.0 release readiness
```

Android microphone/STT/voice-turn/soft-barge-in acceptance remains owned by
RT-8d and has not been accepted by RT-8c.

## Public privacy boundary

The Stage 3 tracked synchronization includes no private evidence or free-form
operator material. It contains none of the following:

```text
private environment values
credentials, tokens, or authorization headers
private endpoint or private filesystem path
LAN address or device identifier
VTS model identity or private hotkey identity
provider identity, model, payload, or response JSON
spoken input, transcript, or generated response
raw audio, PCM, audio URL, or artifact identifier
stream session or turn identifier
screenshot, recording, or raw log
raw exception or private backup
private manifest JSON content
```

## Exact Stage 3 surface

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
backend/tests/**
app/**
vendor/**
scripts/run_v300_rt8c_private_pc_windows_operator.py
scripts/validate_v300_rt8_private_operator_manifest.py
docs/operator_evidence_templates/**
.gitignore
backend/.env.example
backend/env_profiles/**
dependencies and lock files
platform declarations
assets and version metadata
release/**
release_notes/**
tags and GitHub Releases
Framework repository
private environment files
operator_evidence/**
```

## Stage 3 verification

Run from the DRC repository root while the exact seven acceptance-sync files are
modified against implementation commit
`fa39065130a4a4689c2e54195f231a5e79c62a35`:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt8c_configured_pc_windows_realtime_acceptance.py
python -m pytest -q backend/tests/test_v300_rt8c_private_pc_windows_operator.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

The acceptance-sync gate verifies the accepted exact nine-file implementation
history, the current exact seven-file change surface, public acceptance markers,
unchanged runner/focused tests, inert runner behavior, and the ignored/untracked
manifest state without reading its content. It starts no runtime and performs no
configured execution.

## Stage 3 stop rule

After automated verification, stop for exact diff and privacy review. Do not
edit, read, delete, track, commit, or push the ignored private manifest. Do not
restart Backend, Flutter, providers, TTS/playback, VTube Studio, microphone, STT,
or motion execution. Do not authorize RT-8d implementation or commit/push the
Stage 3 synchronization without separate approval.
