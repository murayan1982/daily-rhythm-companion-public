# Daily Rhythm Companion v3.0.0 RT-9b release readiness

Updated: 2026-08-04
Status: COMPLETED / ACCEPTED / PUSHED

## Candidate identity

```text
Public repository: murayan1982/daily-rhythm-companion-public
RT-9a accepted commit: 0e4af7603f60c56f0240271fbb2590d72a189a65
RT-9b implementation baseline: 0e4af7603f60c56f0240271fbb2590d72a189a65
RT-9b implementation commit: 15908a548c229726287867ad89c7ce8b4b916298
current released version: v2.1.0 RELEASED / ACCEPTED
Backend candidate version: 3.0.0
Flutter candidate version: 3.0.0+4
release tag: DRC_v3.0.0 — NOT_CREATED
fixed ZIP: NOT_BUILT
GitHub Release: NOT_CREATED
v3.0.0: NOT_RELEASED
```

RT-9b synchronized candidate metadata and added the active v3 aggregate
source/test/build gate. It is accepted and pushed; it remains a candidate
readiness step rather than a release publication step.

## Gate modes

### Portable candidate gate

```powershell
python scripts\check_v300_rt9_release_readiness.py
```

The portable mode is credential-free, provider-free, network-free,
private-manifest-free, browser-free, release-artifact-free, tag-free, and
publication-free. It runs:

```text
source/exact-surface/security contract
python compileall for backend and scripts
accepted v2.0.x maintenance compatibility aggregate
active application version alignment
Backend full regression (accepted baseline: 417 passed)
historical release hash protection
package denylist source inspection
private/generated-directory no-change snapshots
```

The accepted v2.0.x compatibility aggregate is reused because it is current-main
compatible and credential-free. Historical v2 release-specific fixed-ZIP and
publication gates are not invoked.

### Full Windows acceptance gate

```powershell
python scripts\check_v300_rt9_release_readiness.py `
    --with-flutter `
    --with-builds `
    --rt8-manifest-json `
    operator_evidence\v300_rt8_pc_android_realtime_acceptance.json
```

The full mode additionally requires:

```text
Flutter analyze
Flutter full regression (accepted baseline: 500 passed)
Flutter Web build
Flutter Windows build
Flutter Android debug APK build
strict accepted RT-8 aggregate-manifest validation
```

The Android debug build is compile verification only. RT-9b does not sign or
publish APK, AAB, MSIX, App Store, or Google Play artifacts.

## RT-8 private aggregate validation

The portable mode does not read the ignored manifest. The explicit full mode
requires one supplied file below `operator_evidence/`. It:

```text
requires an ignored, untracked, regular, non-symlink file
uses the accepted strict validator schema and exact aggregate-stage contract
requires both accepted candidate commits to exist and be ancestors
requires aggregate status accepted
computes before/after bytes only to prove no modification
prints no manifest content or private values
never stages, commits, or pushes the manifest
```

In pre-commit candidate mode, the gate performs the equivalent strict schema,
path, ignore, and ancestry checks while allowing the exact thirteen-file dirty
surface. In clean committed-source mode it additionally uses the validator's
official synchronized-Git-state check.

## Active gate classification

The aggregate does not run every `check_v300_*.py` script. There are 63
historical/current v300 checks before the new RT-9b gate and 64 including it.
Many earlier checks are intentionally bound to old baselines, exact candidate
diffs, private operator stages, or configured execution.

Active for RT-9b:

```text
scripts/check_v300_rt9_release_readiness.py
scripts/check_v20x_maintenance_readiness.py
scripts/check_v20x_application_version_metadata.py
python -m pytest -q backend/tests (through maintenance aggregate)
Flutter analyze/test/build commands in explicit full mode
scripts/validate_v300_rt8_private_operator_manifest.py contract in explicit full mode
```

Retained but not blindly rerun:

```text
historical v300 pre-commit exact-diff gates
configured PC/Android/VTS/operator execution runners and gates
v2.0.0, v2.0.1, and v2.1.0 fixed-ZIP/release gates
private local provider, microphone, audio, VTS, or browser checks
```

## Candidate release document state

`release_notes/v3.0.0.md` remains `RELEASE CANDIDATE / NOT_RELEASED`.
`docs/v300_release_record.md` remains `PREPARED / NOT_RELEASED` with no source
HEAD or artifact tuple recorded.

## Release claims

Candidate notes may conservatively describe:

```text
guarded bounded microphone capture
configured real STT path
bounded SSE text streaming and cooperative cancellation
DRC-local voice queue/flush and soft barge-in
realtime character presentation
configured manual VTS motion through separately supplied fixed released FW v5.5.0
accepted PC Windows and Android operator paths
safe default, explicit opt-in, and visible execution state
```

Required non-claims:

```text
provider-level hard cancel
Backend HTTP hard cancel
Framework unified realtime runtime or real TTS queue flush
always-on/background microphone or automatic next-turn capture
automatic voice-to-motion synchronization or emotion inference
all Android devices or iOS realtime acceptance
production multi-user hosting or production security readiness
App Store / Google Play readiness
signed APK, AAB, or MSIX distribution
bundled AI Character Framework
release-ZIP-only immediate configured VTS execution
```

## Exact RT-9b surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt9_release_readiness_current_behavior_inventory.md
docs/v300_rt9_release_readiness.md
docs/v300_release_record.md
release_notes/v3.0.0.md
scripts/check_v300_rt9_release_readiness.py
scripts/check_v20x_application_version_metadata.py
backend/app/version.py
app/pubspec.yaml
```

## Protected and unchanged

```text
backend/app/** except backend/app/version.py
backend/tests/**
app/** except app/pubspec.yaml
vendor/**
operator_evidence/** except explicit read-only full-gate input
backend/local_data/**
release/**
.gitignore
build_release.bat
scripts/check_release_package.py
all v2 fixed-ZIP builders/verifiers and release records
RT-8 validator, runners, and focused tests
dependencies, lock files, assets, and platform declarations
tags and GitHub Releases
```

## Stop rule

After exact verification, stop for diff, surface, privacy, test, and build review.
Do not add RT-9c tooling, invoke a fixed-ZIP builder, create `DRC_v3.0.0`,
publish a GitHub Release, or claim v3.0.0 released without separate approval.

## RT-9c accepted tooling/preflight handoff

RT-9c Stage 1 was accepted and pushed at `7110035eff205d77157b8058b274b4c281a51f7e`. Stage 2 then passed the
clean committed-source no-build preflight from that exact HEAD with Backend 417,
Flutter analyze, Flutter 500, Web/Windows/Android debug builds, and strict
read-only RT-8 aggregate validation. Builder invocation remained zero. Stage 3
now synchronizes only public-safe status. Fixed ZIP build, tuple recording, tag,
and GitHub Release remain unauthorized.

<!-- RT-9D-ENTRY-SYNC:BEGIN -->
## RT-9d fixed-ZIP entry-state sync candidate

```text
RT-9: CURRENT / NOT_COMPLETED
RT-9a: COMPLETED / ACCEPTED / PUSHED
RT-9b: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 1 implementation commit: 7110035eff205d77157b8058b274b4c281a51f7e
RT-9c Stage 2: COMPLETED / PASS / ACCEPTED
RT-9c Stage 3: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 3 acceptance-sync commit: 859eeae53b7b84d2c90fb301eb9e2b981cc731c0
RT-9c: COMPLETED / ACCEPTED / PUSHED
RT-9d entry sync: IMPLEMENTED / AWAITING_REVIEW
RT-9d entry-sync baseline: 859eeae53b7b84d2c90fb301eb9e2b981cc731c0
RT-9d entry-sync surface: exact 9 public documentation files
RT-9d: READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-9e: BLOCKED_PENDING_RT9D_ACCEPTANCE / NOT_AUTHORIZED
fixed ZIP builder invocation count: 0
release source HEAD: NOT_RECORDED
fixed ZIP basename: NOT_BUILT
fixed ZIP size: NOT_RECORDED
fixed ZIP SHA-256: NOT_RECORDED
same-artifact verification: NOT_COMPLETED
DRC_v3.0.0 annotated tag: NOT_CREATED
GitHub Release: NOT_CREATED
v3.0.0: NOT_RELEASED
entry-sync commit / push: NOT_AUTHORIZED
```

This entry sync closes the self-referential RT-9c Stage 3 state and establishes
the exact committed precondition required by the one-time v3 builder. It changes
only the nine public documentation files. It does not read private evidence,
execute provider/network/microphone/STT/TTS/VTS paths, invoke the builder or
artifact verifier, create a fixed ZIP, record an artifact tuple, create a tag,
or publish a GitHub Release.

After this candidate is separately reviewed, committed, and pushed, that new
clean synchronized Public `main` commit becomes the prospective RT-9d release
source HEAD. Actual fixed-ZIP build-once remains separately unauthorized.
<!-- RT-9D-ENTRY-SYNC:END -->
