# Daily Rhythm Companion v3.0.0 RT-8e aggregate cleanup and RT-8 acceptance

Updated: 2026-08-04

## Current Stage 1 candidate state

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8d: COMPLETED / ACCEPTED / PUSHED
RT-8d Stage 3 acceptance-sync commit: 84839efd6e381cb5a2c45022a7e8f7d9eafcb5df
RT-8e: CURRENT / NOT_COMPLETED
RT-8e Stage 1: IMPLEMENTED / AWAITING_REVIEW
RT-8e Stage 1 baseline: 84839efd6e381cb5a2c45022a7e8f7d9eafcb5df
RT-8e Stage 1 surface: exact 9 files
RT-8e Stage 2: BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED
RT-8e Stage 3: BLOCKED_PENDING_AGGREGATE_ACCEPTANCE / NOT_AUTHORIZED
RT-9: BLOCKED_PENDING_RT8 / NOT_AUTHORIZED
v3.0.0: NOT_RELEASED
schema: drc.v3.rt8-platform-acceptance.2
accepted PC candidate source: fa39065130a4a4689c2e54195f231a5e79c62a35
accepted Android candidate source: 0e7fc6fc5922c293b8460fc816610d41c2a79e9a
implementation commit / push: NOT_AUTHORIZED
```

RT-8e closes the accepted RT-8 PC Windows and Android evidence line without
performing another configured realtime run. Stage 1 adds credential-free,
inert-by-default aggregate-transition tooling. Stage 2 later owns the private
cleanup confirmation and ignored-manifest transition. Stage 3 later owns only
the public-safe parent RT-8 acceptance synchronization.

## Accepted exact split

```text
RT-8e Stage 1  credential-free aggregate-transition tooling
RT-8e Stage 2  private aggregate cleanup and manifest transition
RT-8e Stage 3  public-safe RT-8 acceptance synchronization
```

Stage 1 does not read the private manifest in inert or preflight mode. It does
not perform cleanup, process shutdown, provider/network work, microphone/STT,
TTS/playback, VTS/WebSocket work, or any configured execution.

## Stage 1 exact surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8e_aggregate_cleanup_and_rt8_acceptance.md
scripts/check_v300_rt8e_aggregate_cleanup_and_acceptance.py
scripts/run_v300_rt8e_private_aggregate_cleanup.py
backend/tests/test_v300_rt8e_private_aggregate_cleanup.py
```

The first five files synchronize the active small-commit state. The contract,
dedicated gate, runner, and exact eighteen focused tests are new. Backend and
Flutter runtime, existing tests, the strict validator, earlier operator runners,
private configuration, operator evidence, dependencies, version metadata, and
release records remain unchanged.

## Stage 1 runner modes

```text
--check-inert
--preflight
--check-android-transition
--record-aggregate
--expected-source-head <RT8E_STAGE1_COMMIT>
```

### Inert mode

`--check-inert` performs no Git inspection, private-manifest read or write,
private-configuration read, Backend/Flutter process access, cleanup, microphone,
STT, provider/network, TTS/playback, VTS/WebSocket, or motion action. It emits
only fixed public-safe false-state markers.

### Preflight mode

`--preflight` requires all of the following before any private manifest read:

```text
branch: main
HEAD == origin/main
HEAD == --expected-source-head
working tree: clean
RT-8d acceptance-sync baseline is an ancestor
accepted PC candidate is an ancestor
accepted Android candidate is an ancestor
fixed private-manifest target exists
fixed target is ignored and untracked
fixed target is a regular non-symlink file
RT-8e temporary transition target is absent
```

The committed RT-8d acceptance-sync baseline itself is rejected as the expected
source so Stage 2 cannot run before the Stage 1 implementation is committed,
pushed, and synchronized.

### Android transition check

`--check-android-transition` is the first mode allowed to read the ignored
private manifest. It requires the exact accepted Android-stage manifest:

```text
schema_version: drc.v3.rt8-platform-acceptance.2
stage: android
status: accepted
PC candidate: fa39065130a4a4689c2e54195f231a5e79c62a35
Android candidate: 0e7fc6fc5922c293b8460fc816610d41c2a79e9a
PC section: accepted exact schema
Android section: accepted exact schema
aggregate_cleanup.status: not_run
```

It prints no manifest content, path, provider value, endpoint, credential,
private process value, audio value, or operator evidence.

### Aggregate recording

`--record-aggregate` accepts only these nine fixed confirmations:

```text
PASS-AGGREGATE-A
PASS-AGGREGATE-B
PASS-AGGREGATE-C
PASS-AGGREGATE-D
PASS-AGGREGATE-E
PASS-AGGREGATE-F
PASS-AGGREGATE-G
PASS-AGGREGATE-H
ACCEPT-RT8-AGGREGATE
```

They confirm, outside the runner:

```text
A  accepted PC evidence remains valid
B  accepted Android evidence remains valid
C  both candidate commits are verified
D  both platform cleanups and recognized process shutdown passed
E  private environment/process values, staged audio, logs, and backups are removed
F  all real-execution flags are closed
G  operator evidence is neither committed nor pushed
H  DRC is clean/synchronized, FW is clean, and RT-9 remains unauthorized
```

The runner does not perform those cleanup actions. After all confirmations, it
atomically replaces only the fixed ignored target with the existing validator's
exact aggregate-stage schema. The accepted PC and Android sections remain
structurally unchanged.

## Aggregate manifest result

The generated aggregate result is exactly:

```text
stage: aggregate
status: accepted
aggregate_cleanup.status: accepted
pc_accepted: true
android_accepted: true
both_candidate_commits_verified: true
both_platform_cleanups_passed: true
backend_processes_stopped: true
flutter_processes_stopped: true
private_environment_values_removed: true
private_process_values_removed: true
all_real_execution_flags_closed: true
private_staged_audio_remaining: false
private_logs_remaining: false
private_backups_remaining: false
operator_evidence_committed: false
operator_evidence_pushed: false
drc_working_tree_clean: true
drc_head_origin_main_synchronized: true
fw_working_tree_clean: true
rt9_implementation_authorized: false
```

All privacy and non-claim fields remain false. The validator schema and expected
manifest builder are reused unchanged.

## Atomicity and output boundary

```text
fixed ignored target only
exclusive temporary-file creation
flush and fsync before replacement
reread-before-replace concurrency check
os.replace atomic replacement
no backup creation
failure preserves the original manifest
failure removes the temporary target
manifest content is never printed
raw exceptions and private values are never printed
```

## Exact focused-test contract

```text
1. inert mode performs no access, write, cleanup, or execution
2. clean committed source preflight passes
3. wrong expected HEAD is rejected
4. dirty tree is rejected
5. RT-8d acceptance-sync ancestry is required
6. PC and Android candidate ancestry is required
7. missing manifest is rejected
8. nonignored manifest is rejected
9. symlink, tracked, nonregular, or temporary target is rejected
10. valid Android transition check passes
11. wrong previous stage is rejected
12. wrong PC candidate source is rejected
13. wrong Android candidate source is rejected
14. already-aggregate manifest is rejected
15. wrong confirmation creates no update
16. successful transition creates the exact aggregate manifest
17. accepted PC and Android sections remain structurally equal
18. atomic failure preserves the original and leaks no private data
```

## Stage 1 verification contract

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt8e_aggregate_cleanup_and_acceptance.py
python -m pytest -q backend\tests\test_v300_rt8e_private_aggregate_cleanup.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
```

Expected counts from the accepted RT-8d baseline are:

```text
focused Backend: 18 passed
Backend full: 417 passed, 1 existing warning
Flutter full: 500 passed
```

## Stage 2 bounded sequence

Stage 2 remains blocked until Stage 1 review, verification, explicit approval,
commit, push, and clean-tree verification pass. Its later sequence is:

```text
1. --check-inert
2. --preflight
3. --check-android-transition
4. confirm accepted PC/Android facts and both candidate commits
5. confirm recognized Backend/Flutter processes are stopped
6. close all real-execution flags
7. remove private environment/process values
8. remove private staged audio, logs, and temporary backups
9. confirm DRC clean/synchronized and FW clean
10. --record-aggregate with the exact nine confirmations
11. strict aggregate-stage validation
12. confirm ignored/untracked/uncommitted/unpushed state
13. stop before public Stage 3 synchronization
```

The strict validator command is:

```powershell
python scripts\validate_v300_rt8_private_operator_manifest.py `
  --manifest-json operator_evidence\v300_rt8_pc_android_realtime_acceptance.json `
  --stage aggregate `
  --minimum-source-head <RT8E_STAGE1_COMMIT>
```

## Stage 2 prohibited execution

```text
Backend startup
Flutter startup
ADB or device startup
microphone permission or capture
STT execution
LLM/provider execution
TTS synthesis
audio playback
VTS/WebSocket execution
physical motion
additional PC or Android controls
screenshot or recording
raw private evidence output
private manifest commit or push
RT-9 implementation
```

## Stage 3 future public-safe surface

After separately accepted Stage 2, Stage 3 will change exactly:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8e_aggregate_cleanup_and_rt8_acceptance.md
scripts/check_v300_rt8e_aggregate_cleanup_and_acceptance.py
```

It will synchronize RT-8e and parent RT-8 acceptance without reading private
manifest content or repeating configured execution. Only after its accepted
commit and push may RT-9 become `READY_FOR_EXACT_CONTRACT_REVIEW /
NOT_AUTHORIZED`; v3.0.0 remains `NOT_RELEASED`.

## Protected and unchanged

```text
backend/app/**
existing backend/tests/**
app/**
vendor/**
scripts/validate_v300_rt8_private_operator_manifest.py
scripts/run_v300_rt8c_private_pc_windows_operator.py
scripts/run_v300_rt8d_private_android_operator.py
existing RT-8 focused tests
.gitignore
dependencies and lock files
platform declarations
assets
version metadata
release/**
release_notes/**
fixed ZIPs
tags and GitHub Releases
Framework repository
operator_evidence/**
private env, endpoint, token, model, and hotkey files
```

## Stage 1 stop rule

Stage 1 stops after local verification, exact-diff review, and explicit operator
approval. It does not commit, push, read or transition the private manifest,
perform cleanup, start Stage 2, synchronize parent RT-8 acceptance, authorize
RT-9, build a release artifact, tag, publish, or claim v3.0.0 release readiness.
