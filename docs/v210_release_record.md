# Daily Rhythm Companion v2.1.0 release record

Updated: 2026-07-25
Status: PREPARED / NOT_RELEASED
Current phase: R-1e CURRENT / NOT_COMPLETED (NOT_STARTED)

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
source branch: main
source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
fixed ZIP basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
fixed ZIP size: 1747337 bytes
fixed ZIP SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
fixed ZIP builder invocation count for the accepted candidate: 1
same-artifact verification: COMPLETED / PASSED
release-package hygiene: PASSED
ZIP CRC and single-package-root verification: PASSED
Backend pytest from extracted ZIP: 110 passed
Flutter test from extracted ZIP: 103 passed
Flutter Web build from extracted ZIP: passed
Flutter Windows build from extracted ZIP: passed
verifier rebuilt artifact: false
explicit final operator approval: NOT_RECEIVED
annotated tag publication: NOT_CREATED
GitHub Release publication: NOT_CREATED
post-publication SHA-256 verification: NOT_COMPLETED
```

The fixed ZIP SHA-256 is intentionally recorded outside the ZIP. The candidate ZIP contains the pre-artifact source record from the exact source HEAD that produced it; this later acceptance record does not modify or rebuild the accepted artifact.

## Gate state

```text
R-1a release/readiness inventory: COMPLETED / ACCEPTED
R-1b aggregate gate and candidate metadata: COMPLETED / ACCEPTED (implementation commit 72dd42c)
R-1c final smartphone Web aggregate: COMPLETED / ACCEPTED
R-1d fixed ZIP build and same-artifact verification: COMPLETED / ACCEPTED
R-1e publication and post-publication verification: CURRENT / NOT_COMPLETED (NOT_STARTED)
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

## R-1d accepted artifact record

```text
implementation commits: 42e93f1, 377d98d, 6e7af31
accepted release source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
fixed ZIP basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
fixed ZIP size bytes: 1747337
fixed ZIP SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
preflight-only source/test/build gate: passed
accepted-candidate builder invocation count: 1
same-artifact verification without rebuilding: passed
verifier builder invocation: false
tag created: false
GitHub Release created: false
```

A superseded pre-fix candidate was rejected before publication after the generic package checker exposed a tracked Flutter registrant policy mismatch. It is not part of the accepted tuple and was never tagged or published.

## Immutable historical releases

```text
DRC_v2.0.0 tag, GitHub Release, fixed ZIP, and records: unchanged
DRC_v2.0.1 tag, GitHub Release, fixed ZIP, and records: unchanged
```

## Publication boundary

R-1e must receive explicit operator approval for the exact source HEAD / ZIP basename / size / SHA-256 tuple above before creating `DRC_v2.1.0` or publishing a GitHub Release. The annotated tag must target the recorded release source HEAD, and the published asset must be the unchanged fixed ZIP. The asset must then be re-downloaded and its size and SHA-256 must match this record before R-1 can complete.
