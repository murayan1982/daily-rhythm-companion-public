# Daily Rhythm Companion v2.0.1 patch release gate

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED
Active small commit: none
Source of truth: `docs/DRC_v20x_maintenance_checklist.md`

## Release result

```text
release version: v2.0.1
annotated tag: DRC_v2.0.1
GitHub Release: published
source HEAD: 3e4c9f6186ef7195045a445307e14f412924bc26
fixed ZIP: DailyRhythmCompanion_20260723_143447.zip
fixed ZIP size bytes: 1493130
fixed ZIP SHA-256: ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1
builder invocation count: 1
same-ZIP verification without rebuilding: passed
post-publication downloaded-asset SHA-256 re-verification: passed
v2.0.0 historical records: unchanged
```

## Purpose

M-9 closed the accepted v2.0.x maintenance scope without changing the published v2.0.0 release record. It used a final committed-source gate, a one-time fixed-ZIP builder, same-artifact verification, an explicit approval boundary, and a post-publication SHA-256 check for v2.0.1.

## Accepted patch scope

The v2.0.1 release contains only the accepted M-1 through M-8 maintenance work:

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

The pre-publication source gate was:

```powershell
python scripts\check_v20x_patch_release.py --source-tree --with-flutter
```

At execution time it required clean official Public `main`, `HEAD == origin/main`, one Public root commit, the immutable annotated `DRC_v2.0.0` tag, absence of `DRC_v2.0.1`, accepted M-1 through M-8 state, M-9 preparation state, compileall, backend pytest, Flutter test, historical-record hashes, and unchanged `backend/local_data`.

The gate passed for source HEAD `3e4c9f6186ef7195045a445307e14f412924bc26`.

## One-time fixed ZIP build

The fixed artifact was built with:

```powershell
.\build_v201_fixed_release_zip_from_head.ps1
```

The builder invoked `build_release.bat release` exactly once from a detached worktree at the recorded committed HEAD. It produced exactly one ZIP and did not verify, rebuild, tag, or publish the artifact.

```text
fixed ZIP: DailyRhythmCompanion_20260723_143447.zip
size: 1493130 bytes
SHA-256: ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1
```

The builder must not be rerun for this release.

## Same-ZIP verification

The exact fixed ZIP was verified without rebuilding:

```powershell
python scripts\check_v20x_patch_release.py `
  --release-zip "release\DailyRhythmCompanion_20260723_143447.zip" `
  --expected-sha256 "ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1" `
  --expected-source-head "3e4c9f6186ef7195045a445307e14f412924bc26" `
  --with-flutter
```

The verifier checked the hash before and after inspection, file size and modification timestamp stability, release-package hygiene, ZIP CRC, one package root, v2.0.1 metadata, M-9 files, v2.0.0 historical hashes, extracted backend tests, extracted Flutter tests, and absence of builder invocation.

## Approval and publication

After the same-ZIP verification passed, the exact artifact tuple and gate results were presented to the operator. Explicit final approval was received before publication.

The release then created and published:

```text
annotated tag: DRC_v2.0.1
annotated tag target: 3e4c9f6186ef7195045a445307e14f412924bc26
GitHub Release title: Daily Rhythm Companion v2.0.1
GitHub Release asset: DailyRhythmCompanion_20260723_143447.zip
```

The uploaded asset reported the same size and SHA-256. The published asset was downloaded and independently rehashed; its SHA-256 matched `ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1`.

## Non-circular SHA rule

The final ZIP does not contain its own final SHA-256. The exact source HEAD, ZIP basename, size, and SHA-256 are recorded outside the ZIP in the annotated tag message, GitHub Release body, and this post-publication source record.

## Current verification commands

Portable post-release record gate:

```powershell
python scripts\check_v20x_patch_release.py
```

Strict current-main and annotated-tag gate after the post-release record commit is pushed:

```powershell
python scripts\check_v20x_patch_release.py --source-tree --with-flutter
```

Published fixed-ZIP re-verification remains available using the exact path, SHA-256, and release source HEAD shown above. It inspects the released ZIP as-is and never rebuilds it.

## Historical immutability

The following remain unchanged and must not be rewritten:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
annotated tag DRC_v2.0.0
published v2.0.0 GitHub Release
published v2.0.0 fixed ZIP
```
