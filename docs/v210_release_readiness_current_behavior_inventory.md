# Daily Rhythm Companion v2.1.0 R-1a release/readiness current behavior inventory

Updated: 2026-07-25
Status: COMPLETED / ACCEPTED
Completed small commit: R-1a
Current small commit: R-1d
Parent phase: R-1 CURRENT / NOT_COMPLETED

## Purpose

R-1a freezes the current release/readiness surface before v2.1.0 release implementation. It is source-tree-only and does not read credentials, execute providers, create evidence, build a ZIP, inspect or create Git tags, or access GitHub Releases.

## Current released baseline

```text
current released version: v2.0.1
immutable capability baseline: v2.0.0
backend APP_VERSION: 2.0.1
Flutter package version: 2.0.1+2
v2.0.0 annotated tag / release / fixed ZIP: historical and immutable
v2.0.1 annotated tag / release / fixed ZIP: historical and immutable
```

The v2.1.0 source contains accepted W-1 through W-5, C-1, T-1, and V-1 work, but its application version metadata still correctly identifies the current released version until a separately accepted release-candidate commit updates it.

## Existing reusable packaging boundary

`build_release.bat` is the generic package producer. Its current denylist excludes Git data, release output, local env variants, credentials, token stores, provider/operator evidence, caches, build outputs, private paths, patch/diff bundles, internal development docs, and nested ZIP files. It creates a timestamped `DailyRhythmCompanion_*.zip` under the ignored `release/` directory.

`scripts/check_release_package.py` is the generic ZIP hygiene checker. It rejects blocked paths/suffixes, private Windows paths, LAN IP literals, control characters, and non-placeholder sensitive env assignments. This checker is reusable by a future v2.1.0 same-artifact verifier.

`.gitignore` excludes `release/`, operator evidence, local data, token stores, local env profiles, and generated build output from source commits.

## Historical v2.0.1 release implementation

The following files are completed historical v2.0.1 records and are not active v2.1.0 release implementations:

```text
build_v201_fixed_release_zip_from_head.ps1
scripts/check_v20x_maintenance_readiness.py
scripts/check_v20x_patch_release.py
docs/v20x_maintenance_readiness.md
docs/v20x_patch_release.md
docs/v201_patch_release_record.md
release_notes/v2.0.1.md
```

The v2.0.1 builder already demonstrates the required safety pattern:

```text
clean official Public main
HEAD == origin/main
one Public root commit
immutable DRC_v2.0.0 baseline tag
one detached committed-HEAD worktree
one build_release.bat release invocation
one fixed ZIP
SHA-256 recorded outside the ZIP
same ZIP verified without rebuilding
explicit approval before annotated tag / GitHub Release publication
post-publication asset re-download and SHA-256 verification
```

It cannot be reused directly for v2.1.0 because it is intentionally hard-coded to v2.0.1 metadata, tag absence/presence rules, historical source HEAD, fixed ZIP tuple, and M-9 records.

## Current accepted verification baseline

```text
Backend pytest: 110 passed
Flutter test: 103 passed
V-1c focused presentation tests: 9 passed
V-1c focused card tests: 5 passed
V-1c focused HomeScreen integration tests: 5 passed
Web build: passed at V-1c implementation verification
Windows build: passed at V-1c implementation verification
```

R-1 must run its own aggregate gate from the intended final committed source. Prior phase counts and builds are inventory inputs, not R-1 completion evidence.

## Existing smartphone Web evidence

Separately accepted prior-phase evidence exists:

```text
W-5b2: configured Google Health request returned HTTP 200, normalized sleep summary confirmed, and PC plus smartphone Web showed Google Health / real data / acquired state.
T-1c: real in-app TTS generation and audible play/stop/replay/completion/expiry/regenerate behavior were accepted on PC and smartphone Web.
```

Raw screenshots, exact sleep values, raw audio, tokens, provider payloads, private paths, and LAN IPs remain outside Git. R-1 currently has no final integrated smartphone Web evidence aggregate covering the frozen v2.1.0 candidate source.

## Missing v2.1.0 release/readiness files

R-1a confirms that the following v2.1.0-specific files do not yet exist:

```text
build_v210_fixed_release_zip_from_head.ps1
scripts/check_v210_release_readiness.py
scripts/check_v210_fixed_release_zip.py
docs/v210_release_readiness.md
docs/v210_release_record.md
release_notes/v2.1.0.md
```

No v2.1.0 fixed ZIP, `DRC_v2.1.0` annotated tag, or v2.1.0 GitHub Release is created or accepted by source presence.

## R-1 small-commit split

```text
R-1a  COMPLETED / ACCEPTED   Release/readiness current behavior inventory
R-1b  COMPLETED / ACCEPTED   Aggregate source-tree/test gate and v2.1.0 candidate metadata
R-1c  COMPLETED / ACCEPTED     Final smartphone Web evidence aggregate
R-1d  CURRENT / NOT_COMPLETED  One-time fixed ZIP build and same-artifact verification
      NOT_STARTED
R-1e  PLANNED                  Explicit approval, publication, and post-publication verification
```

### R-1b boundary

Create the credential-free aggregate source-tree/test gate, update backend/Flutter metadata to the accepted v2.1.0 candidate values, and prepare release policy/record/notes without building a ZIP or creating a tag/Release.

### R-1c boundary

Run and record the final integrated smartphone Web checkpoint against the frozen candidate source. Commit only public-safe marker evidence; keep raw screenshots, sleep values, audio, tokens, payloads, paths, and LAN IPs local.

### R-1d boundary

Require clean official Public `main` with `HEAD == origin/main`, build exactly one fixed ZIP from a detached committed-HEAD worktree, and verify that same artifact without rebuilding. Stop before tag or GitHub Release publication.

### R-1e boundary

Present the exact source HEAD / ZIP basename / size / SHA-256 tuple, receive explicit final operator approval, create the annotated `DRC_v2.1.0` tag and GitHub Release, upload the same fixed ZIP, re-download it, and verify the published SHA-256 before completion sync.

## R-1a non-goals

```text
no Backend or Flutter runtime change
no dependency or asset change
no application version update
no aggregate release gate implementation
no provider or health-data execution
no smartphone Web execution
no fixed ZIP build or verification
no tag creation
no GitHub Release publication
no modification of v2.0.0/v2.0.1 historical records
```

## R-1a acceptance record

```text
accepted on: 2026-07-25
implementation commit: dbc84db
compileall: passed
all check_v210_*.py: 18 / 18 passed
v2.0.x compatibility / maintenance guards: passed
Backend pytest: 110 passed
Flutter test: 103 passed
git diff --check: passed
diff review: docs/test-only scope confirmed
explicit operator approval: received
version metadata changed: false
fixed ZIP built: false
tag created: false
GitHub Release created: false
historical release records changed: false
```

R-1a and R-1b are `COMPLETED / ACCEPTED`. R-1c is `CURRENT / NOT_COMPLETED` and `IMPLEMENTED / NOT_ACCEPTED`.


## Accepted R-1b candidate transition

R-1a's accepted inventory snapshot remains Backend `2.0.1` / Flutter `2.0.1+2`. The separately checked R-1b implementation now advances the active source candidate to Backend `2.1.0` / Flutter `2.1.0+3`, adds `scripts/check_v210_release_readiness.py`, `docs/v210_release_readiness.md`, `docs/v210_release_record.md`, and `release_notes/v2.1.0.md`, and keeps the following later implementation absent:

```text
build_v210_fixed_release_zip_from_head.ps1
scripts/check_v210_fixed_release_zip.py
```

This later transition does not retroactively alter the R-1a acceptance record or claim a fixed ZIP, tag, GitHub Release, provider execution, or final smartphone Web aggregate.

## Accepted R-1c evidence transition

The separately checked R-1c implementation added the final PC/smartphone Web evidence contract, a deliberately rejected public example manifest, and a validator for one ignored private manifest. The private manifest validated against exact clean synchronized candidate source `1e922e68685dadfc1008f1119d0ce492584e8f19` after all six required evidence items were reviewed with the actual DRC Backend on PC and smartphone Web. The accepted R-1a snapshot and R-1b candidate gate remain intact, and the current source-tree aggregate retains 19 checks including the accepted R-1c validator.

```text
accepted candidate source HEAD: 1e922e68685dadfc1008f1119d0ce492584e8f19
final private manifest validated: true
required evidence items accepted: 6 / 6
final PC Web aggregate accepted: true
final smartphone Web aggregate accepted: true
public-safe opaque screenshot references recorded: true
raw/private evidence committed: false
fixed ZIP built: false
tag created: false
GitHub Release created: false
R-1d current/not completed: true
```
