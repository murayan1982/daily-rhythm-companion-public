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
release source HEAD: f5fb54dc4beecdd1fdec957e92bf0b8cfc76513a
verification HEAD: 4b08d20425c469e41277cfb7a013ed2a266c3489
fixed ZIP: DailyRhythmCompanion_v3.0.0_20260804_183416.zip — BUILT / VERIFIED / NOT_PUBLISHED
fixed ZIP size: 2774558
fixed ZIP SHA-256: 9a4f28d337ace03bb1a1371165a2299f90c2c4d2ecbfefa95130b2fabedb3cd6
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

<!-- RT-9D-ACCEPTANCE-SYNC:BEGIN -->
## RT-9d acceptance-sync candidate

```text
RT-9: CURRENT / NOT_COMPLETED
RT-9a: COMPLETED / ACCEPTED / PUSHED
RT-9b: COMPLETED / ACCEPTED / PUSHED
RT-9c: COMPLETED / ACCEPTED / PUSHED
RT-9d Control A: COMPLETED / PASS / ACCEPTED
RT-9d Control B: COMPLETED / PASS / ACCEPTED
RT-9d Control C: COMPLETED / PASS / ACCEPTED / PUSHED
RT-9d Control C commit: b5a41e8568a73e0efecc57f4273f7b254e13353a
RT-9d acceptance sync: IMPLEMENTED / AWAITING_REVIEW
RT-9d acceptance-sync baseline: b5a41e8568a73e0efecc57f4273f7b254e13353a
RT-9d acceptance-sync exact surface: exact 9 public documentation files
RT-9d: COMPLETED / ACCEPTED
release source HEAD: f5fb54dc4beecdd1fdec957e92bf0b8cfc76513a
verification HEAD: 4b08d20425c469e41277cfb7a013ed2a266c3489
post-build verifier-only corrective commits: 2
fixed ZIP basename: DailyRhythmCompanion_v3.0.0_20260804_183416.zip
fixed ZIP size: 2774558
fixed ZIP SHA-256: 9a4f28d337ace03bb1a1371165a2299f90c2c4d2ecbfefa95130b2fabedb3cd6
fixed ZIP builder invocation count: 1
artifact count: 1
artifact size / mtime / SHA-256 unchanged: PASS
same-artifact verification: COMPLETED / PASS / ACCEPTED
release-package hygiene: PASS / exact-source-matched-synthetic-fixtures
ZIP CRC and single-package-root verification: PASS
unsafe paths / symlinks / duplicate-case collisions: ABSENT
required Public files and historical protected hashes: PASS
Backend pytest from extracted ZIP: 417 passed
Flutter analyze from extracted ZIP: PASS
Flutter test from extracted ZIP: 500 passed
Flutter Web build from extracted ZIP: PASS
Flutter Windows build from extracted ZIP: PASS
Flutter Android debug build from extracted ZIP: PASS
builder invoked by verifier: false
artifact rebuilt by verifier: false
private RT-8 manifest read by verifier: false
private RT-8 manifest: ignored / untracked / unpushed
explicit final operator release approval: NOT_RECEIVED
DRC_v3.0.0 annotated tag: NOT_CREATED
GitHub Release: NOT_CREATED
post-publication verification: NOT_STARTED
RT-9e: READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
v3.0.0: NOT_RELEASED
acceptance-sync commit / push: NOT_AUTHORIZED
```

Controls A and B established and verified one immutable fixed ZIP. Control C
recorded that exact tuple in public documentation and was accepted, committed,
and pushed at `b5a41e8568a73e0efecc57f4273f7b254e13353a`.

This acceptance-sync candidate closes parent RT-9d and opens RT-9e for a
separate exact publication-contract review. It changes public documentation
only. It does not invoke a builder or artifact verifier, read private evidence,
alter the fixed ZIP, execute provider/network/microphone/STT/TTS/VTS paths,
create a tag, publish a GitHub Release, grant final release approval, perform
post-publication verification, or mark v3.0.0 released.
<!-- RT-9D-ACCEPTANCE-SYNC:END -->
