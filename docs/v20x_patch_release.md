# Daily Rhythm Companion v2.0.1 patch release gate

Updated: 2026-07-23
Status: CURRENT / NOT_COMPLETED
Active small commit: M-9 patch release preparation
Source of truth: `docs/DRC_v20x_maintenance_checklist.md`

## Purpose

M-9 closes the accepted v2.0.x maintenance scope without changing the published v2.0.0 release record. It adds a final committed-source gate, a one-time fixed-ZIP builder, same-artifact verification, and the patch-release record contract for v2.0.1.

## Accepted patch scope

The v2.0.1 patch candidate contains only the accepted M-1 through M-8 maintenance work:

```text
- post-v2.0.0 maintenance source of truth
- backend and Flutter version metadata alignment to v2.0.1 / 2.0.1+2
- normal credential-free backend pytest foundation
- Framework fallback and DRC-owned voice artifact safety regression coverage
- bounded temporary chat sessions and TTS artifacts
- configurable Web CORS origins with the released wildcard local-demo default
- clarified Fitbit current-state and migration wording
- one aggregate current-main maintenance readiness command
```

No new user-facing subsystem, real provider acceptance, production hosting work, account system, realtime voice work, or Live2D/VTS execution is part of this patch.

## Final committed-source gate

The final source gate is:

```powershell
python scripts\check_v20x_patch_release.py --source-tree --with-flutter
```

It requires:

```text
- the official Public repository root
- branch main
- a clean tracked and untracked working tree
- HEAD == main == origin/main
- exactly one Public root commit
- the annotated DRC_v2.0.0 baseline tag remains present
- DRC_v2.0.1 does not exist yet
- M-1 through M-8 remain COMPLETED / ACCEPTED
- M-9 remains CURRENT / NOT_COMPLETED
- compileall, backend pytest, and Flutter test pass
- v2.0.0 historical normalized-content hashes remain unchanged
- backend/local_data is not created or modified
```

Run `git fetch origin main --tags` before this gate so `origin/main` and local tags are current. The gate does not create a ZIP, tag, or GitHub Release.

## One-time fixed ZIP build

After the committed-source gate passes and the preparation commit is pushed:

```powershell
.\build_v201_fixed_release_zip_from_head.ps1
```

The builder:

```text
- repeats the strict committed-source gate
- creates a detached temporary worktree from the recorded Public HEAD
- invokes build_release.bat release exactly once
- expects exactly one ZIP from that invocation
- refuses to overwrite an existing destination
- moves that ZIP to release/
- prints the source HEAD, file size, and SHA-256
- does not verify, rebuild, tag, or publish the artifact
```

The output is the fixed artifact. Do not rerun the builder merely to change its timestamp or filename.

## Same-ZIP verification

Bind the emitted path and SHA-256, then verify the same file:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
$sha = "<builder-emitted-sha256>"
$head = (git rev-parse HEAD).Trim()

python scripts\check_v20x_patch_release.py `
  --release-zip $zip `
  --expected-sha256 $sha `
  --expected-source-head $head `
  --with-flutter
```

The verifier:

```text
- hashes the supplied ZIP before and after verification
- records its size and modification timestamp before and after verification
- runs the release-package hygiene validator
- runs ZIP CRC validation
- requires one DailyRhythmCompanion package root
- verifies v2.0.1 metadata, M-9 files, and v2.0.0 historical hashes inside the ZIP
- extracts the supplied ZIP to a temporary directory
- runs the aggregate maintenance gate from the extracted ZIP
- runs Flutter test from the extracted ZIP when --with-flutter is present
- confirms the supplied ZIP did not change
- never invokes a release builder
```

## SHA-256 and release record

A ZIP cannot safely contain its own final SHA-256 without changing that SHA. Therefore the exact final artifact tuple is recorded outside the ZIP in:

```text
- the annotated DRC_v2.0.1 tag message
- the GitHub Release body
- an optional post-publication source record after release acceptance
```

Required tuple:

```text
source HEAD
fixed ZIP basename
fixed ZIP size in bytes
fixed ZIP SHA-256
same-ZIP verification result
post-publication SHA-256 re-verification result
```

`docs/v201_patch_release_record.md` defines the tracked record fields and current not-yet-released state.

## Approval boundary

After same-ZIP verification, stop and present the artifact tuple and gate outputs. Do not create `DRC_v2.0.1`, publish a GitHub Release, mark M-9 completed, or mark v2.0.1 released until the operator gives explicit final approval.

## Historical immutability

The following are not edit targets:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
annotated tag DRC_v2.0.0
published v2.0.0 GitHub Release
published v2.0.0 fixed ZIP
```
