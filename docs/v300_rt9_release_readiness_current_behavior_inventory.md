# Daily Rhythm Companion v3.0.0 RT-9 release-readiness current behavior inventory

Updated: 2026-08-04

## Current RT-9a candidate state

```text
RT-8: COMPLETED / ACCEPTED
RT-8e: COMPLETED / ACCEPTED / PUSHED
RT-8e Stage 3 acceptance-sync commit: 4c3b724a0c42e0d078c876c02b07a04d4c71e24d
RT-9: CURRENT / NOT_COMPLETED
RT-9a: IMPLEMENTED / AWAITING_REVIEW
RT-9a baseline: 4c3b724a0c42e0d078c876c02b07a04d4c71e24d
RT-9a exact surface: 7 documentation/static-gate files
RT-9b through RT-9e: NOT_AUTHORIZED
v3.0.0: NOT_RELEASED
```

RT-9a is credential-free, provider-free, network-free, private-manifest-free,
artifact-free, tag-free, and publication-free. It inventories the accepted RT-8
source and freezes a bounded release sequence before any version or release
implementation is allowed.

## Current source and test baseline

```text
Public repository: murayan1982/daily-rhythm-companion-public
baseline branch: main
baseline HEAD / origin-main: 4c3b724a0c42e0d078c876c02b07a04d4c71e24d
current released version: v2.1.0 RELEASED / ACCEPTED
Backend APP_VERSION: 2.1.0
Flutter package version: 2.1.0+3
Backend full regression baseline: 417 passed, 1 existing warning
Flutter full regression baseline: 500 passed
v300 check scripts before RT-9a: 62
v300 check scripts including RT-9a gate: 63
```

RT-9a does not change either version. Candidate metadata `3.0.0` and `3.0.0+4`
belongs only to separately reviewed RT-9b.

## Current release tooling inventory

Present and retained:

```text
build_release.bat
scripts/check_release_package.py
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
build_v210_fixed_release_zip_from_head.ps1
scripts/check_v20x_patch_release.py
scripts/check_v210_release_readiness.py
scripts/check_v210_fixed_release_zip.py
docs/v210_release_record.md
release_notes/v2.0.0.md
release_notes/v2.0.1.md
release_notes/v2.1.0.md
```

Not present before RT-9 implementation:

```text
docs/v300_rt9_release_readiness.md
docs/v300_release_record.md
release_notes/v3.0.0.md
scripts/check_v300_rt9_release_readiness.py
build_v300_fixed_release_zip_from_head.ps1
scripts/check_v300_fixed_release_zip.py
DailyRhythmCompanion_v3.0.0_*.zip
DRC_v3.0.0 annotated tag
v3.0.0 GitHub Release
```

The v2 release gates and builders are historical version-specific contracts and
must not be edited into v3 tools. RT-9b and RT-9c add new v300-owned files while
preserving all prior release records and fixed artifacts.

## v300 gate classification boundary

There are 62 existing `scripts/check_v300_*.py` files at the accepted RT-8
baseline. Many are historical candidate gates bound to an earlier exact diff,
baseline commit, configured operator stage, or private local prerequisite.
Running every historical gate blindly from a release aggregate would be
incorrect.

RT-9b must explicitly classify the release aggregate into:

```text
1. active current-source structural/security gates
2. active current runtime regression tests
3. separately supplied strict accepted RT-8 aggregate-manifest validation
4. historical pre-commit/exact-diff gates retained but not rerun
5. configured/private/operator gates retained but not rerun
```

RT-9a does not choose or run the final RT-9b child list. That list requires its
own exact review after this inventory is accepted.

## Package and private-data boundary

The current generic package builder and repository policy exclude at least:

```text
.git/
release/
vendor/
operator_evidence/
backend/local_data/
.env and local environment files
credential, token, key, and OAuth-state files
raw logs, temporary files, backups, databases, caches, and build outputs
existing ZIP files
```

The accepted fixed Framework v5.5.0 vendor remains local and Git-ignored. The
v3.0.0 DRC source ZIP must not bundle that vendor. Release documentation may
state that configured manual VTS motion requires a separately obtained and
placed fixed released Framework v5.5.0; it must not claim bundled Framework or
out-of-box configured VTS execution.

RT-9a does not read, enumerate, copy, hash, print, modify, commit, or push the
ignored RT-8 aggregate manifest or any private configuration/evidence.

## Accepted exact RT-9 split

```text
RT-9a  release/security current-behavior inventory and exact split
RT-9b  v3.0.0 candidate metadata and aggregate source/test/build readiness
RT-9c  one-time fixed-ZIP builder/verifier implementation and no-build preflight
RT-9d  fixed ZIP build-once, same-artifact verification, and tuple record
RT-9e  explicit approval, annotated tag/GitHub Release, and post-publication verification
```

### RT-9a

Docs/static-gate only. Freeze current metadata, tests, tooling, privacy/package
boundary, release split, protected surface, and stop rule.

### RT-9b

Separately review candidate versions, v3 release notes/record placeholders,
active aggregate child classification, full source/test/build gate, strict RT-8
aggregate validation input, and unchanged private/generated directories. No
fixed ZIP, tag, or publication.

### RT-9c

Separately add the one-time v3 builder and same-artifact verifier. Require a
clean synchronized official Public main, preserved annotated historical tags,
absent `DRC_v3.0.0`, absent prior v3 fixed ZIP, detached committed-HEAD worktree,
exactly one generic builder invocation, and initial `-PreflightOnly` execution
with zero artifact builds.

### RT-9d

After separate approval, invoke the accepted builder exactly once, record the
source HEAD/basename/size/SHA-256, and validate that exact same ZIP without
rebuilding. Remain `NOT_RELEASED`; do not create a tag or GitHub Release.

### RT-9e

After explicit approval of the exact RT-9d tuple, create an annotated
`DRC_v3.0.0` tag, publish one non-draft/non-prerelease GitHub Release with the
unchanged accepted ZIP, download the published asset, and reverify basename,
size, and SHA-256 before synchronizing the final public release record.

## Expected later version boundary

Not authorized by RT-9a:

```text
Backend APP_VERSION: 3.0.0
Flutter package version: 3.0.0+4
release tag: DRC_v3.0.0
fixed ZIP pattern: DailyRhythmCompanion_v3.0.0_<YYYYMMDD_HHMMSS>.zip
```

## Allowed release claims

The future release notes may conservatively describe accepted guarded/default-
off capabilities, bounded realtime paths, configured manual VTS motion through
the separately supplied fixed released Framework v5.5.0, and accepted PC Windows
and Android operator paths.

## Required non-claims

```text
provider-level hard cancel
Backend HTTP hard cancel
Framework unified realtime runtime
Framework real TTS queue flush
always-on or background microphone
automatic next-turn capture
automatic voice-to-motion synchronization
automatic emotion inference
all Android devices
iOS realtime acceptance
production multi-user hosting or production security readiness
App Store / Google Play readiness
signed APK, AAB, MSIX, or store publication
bundled AI Character Framework
release-ZIP-only immediate configured VTS execution
```

## RT-9a exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt9_release_readiness_current_behavior_inventory.md
scripts/check_v300_rt9_release_readiness_current_behavior_inventory.py
```

## Protected and unchanged

```text
backend/app/**
backend/tests/**
app/**
vendor/**
.gitignore
build_release.bat
scripts/check_release_package.py
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
build_v210_fixed_release_zip_from_head.ps1
scripts/check_v20x_patch_release.py
scripts/check_v210_release_readiness.py
scripts/check_v210_fixed_release_zip.py
docs/v210_release_record.md
release_notes/v2.0.0.md
release_notes/v2.0.1.md
release_notes/v2.1.0.md
release/**
operator_evidence/**
backend/local_data/**
private configuration, credentials, tokens, endpoints, model/hotkey values
annotated tags and GitHub Releases
```

## RT-9a verification

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt9_release_readiness_current_behavior_inventory.py
python -m pytest -q backend\tests

Set-Location app
flutter analyze
flutter test
Set-Location ..

git -c core.whitespace=cr-at-eol diff --check
git status --short
```

Expected:

```text
dedicated RT-9a gate: PASS
Backend full: 417 passed, 1 existing warning
Flutter analyze: PASS
Flutter full: 500 passed
exact implementation surface: 7 files
Backend runtime changed: false
Flutter runtime changed: false
existing tests changed: false
version metadata changed: false
historical release tooling/records changed: false
private manifest read/modified: false
release ZIP built: false
tag/GitHub Release created: false
```

## RT-9a stop rule

Stop after exact diff, dedicated gate, full Backend/Flutter regression, privacy
review, and explicit operator approval. Do not change version metadata, create
v3 release notes/record, implement RT-9b through RT-9e, run configured/private
execution, build a fixed ZIP, create a tag, publish a GitHub Release, or claim
v3.0.0 release readiness.
