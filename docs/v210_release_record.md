# Daily Rhythm Companion v2.1.0 release record

Updated: 2026-07-25
Status: PREPARED / NOT_RELEASED
Current phase: R-1d CURRENT / NOT_COMPLETED (NOT_STARTED)

## Candidate identity

```text
release version: v2.1.0
Backend APP_VERSION: 2.1.0
Flutter package version: 2.1.0+3
annotated tag: DRC_v2.1.0 (NOT_CREATED)
current released version: v2.0.1
```

## Release tuple

```text
source HEAD: NOT_RECORDED
fixed ZIP basename: NOT_BUILT
fixed ZIP size: NOT_RECORDED
fixed ZIP SHA-256: NOT_RECORDED
same-artifact verification: NOT_COMPLETED
explicit final operator approval: NOT_RECEIVED
annotated tag publication: NOT_CREATED
GitHub Release publication: NOT_CREATED
post-publication SHA-256 verification: NOT_COMPLETED
```

No value in this prepared record claims that a v2.1.0 artifact or publication exists.

## Gate state

```text
R-1a release/readiness inventory: COMPLETED / ACCEPTED
R-1b aggregate gate and candidate metadata: COMPLETED / ACCEPTED (implementation commit 72dd42c)
R-1c final smartphone Web aggregate: COMPLETED / ACCEPTED
R-1d fixed ZIP build and same-artifact verification: CURRENT / NOT_COMPLETED (NOT_STARTED)
R-1e publication and post-publication verification: PLANNED
parent R-1: CURRENT / NOT_COMPLETED
```

## R-1c accepted evidence record

```text
R-1c implementation commit: 1e922e6
accepted candidate source HEAD: 1e922e68685dadfc1008f1119d0ce492584e8f19
private manifest validation: COMPLETED / ACCEPTED
required evidence items: 6 / 6 accepted
PC Web final aggregate: COMPLETED / ACCEPTED
smartphone Web final aggregate: COMPLETED / ACCEPTED
actual DRC Backend API used: true
public-safe screenshot references: RECORDED_AS_OPAQUE_PRIVATE_URIS
raw/private evidence committed: false
fixed ZIP built by R-1c: false
tag or GitHub Release created by R-1c: false
```

The ignored manifest and raw evidence remain outside Git. R-1d must use a later clean committed source HEAD for the one-time fixed ZIP and same-artifact verification.

## Immutable historical releases

```text
DRC_v2.0.0 tag, GitHub Release, fixed ZIP, and records: unchanged
DRC_v2.0.1 tag, GitHub Release, fixed ZIP, and records: unchanged
```

## Publication boundary

R-1d must record the exact committed source HEAD and the one fixed ZIP basename/size/SHA-256 tuple. R-1e must receive explicit operator approval for that exact tuple before creating `DRC_v2.1.0` or publishing a GitHub Release. The published asset must be re-downloaded and its SHA-256 must match this record before R-1 can complete.
