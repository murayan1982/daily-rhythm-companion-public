# Daily Rhythm Companion v2.1.0 release record

Updated: 2026-07-25
Status: RELEASED / ACCEPTED
Current phase: none (R-1e and parent R-1 COMPLETED / ACCEPTED)

## Release identity

```text
release version: v2.1.0
Backend APP_VERSION: 2.1.0
Flutter package version: 2.1.0+3
annotated tag: DRC_v2.1.0
annotated tag type: tag
annotated tag target: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
current released version: v2.1.0
GitHub Release URL: https://github.com/murayan1982/daily-rhythm-companion-public/releases/tag/DRC_v2.1.0
```

## Final release tuple

```text
source branch: main
release source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
publication-preparation commit: c6263feb2f2550293635c2535d5f19a4eb6a4c3d
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
explicit final operator approval: RECEIVED
annotated tag publication: PUBLISHED
GitHub Release publication: PUBLISHED
GitHub Release draft: false
GitHub Release prerelease: false
post-publication downloaded asset basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
post-publication downloaded asset size: 1747337 bytes
post-publication downloaded asset SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
post-publication SHA-256 verification: COMPLETED / PASSED
```

The fixed ZIP SHA-256 is intentionally recorded outside the ZIP. The published asset is the unchanged fixed artifact accepted in R-1d; this post-publication source record does not alter or rebuild the tag target or release asset.

## Gate state

```text
R-1a release/readiness inventory: COMPLETED / ACCEPTED
R-1b aggregate gate and candidate metadata: COMPLETED / ACCEPTED (implementation commit 72dd42c)
R-1c final smartphone Web aggregate: COMPLETED / ACCEPTED
R-1d fixed ZIP build and same-artifact verification: COMPLETED / ACCEPTED
R-1e publication and post-publication verification: COMPLETED / ACCEPTED
parent R-1: COMPLETED / ACCEPTED
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
```

A superseded pre-fix candidate was rejected before publication and is not part of the accepted tuple.

## R-1e publication record

```text
explicit final operator approval: received on 2026-07-25
annotated tag: DRC_v2.1.0
annotated tag type: tag
annotated tag target: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
GitHub Release: published
GitHub Release draft: false
GitHub Release prerelease: false
published asset basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
published asset size bytes: 1747337
published asset SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
post-publication asset re-downloaded: true
post-publication downloaded asset size bytes: 1747337
post-publication downloaded asset SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
post-publication SHA-256 re-verification: passed
fixed ZIP rebuilt or replaced: false
```

## Immutable historical releases

```text
DRC_v2.0.0 tag, GitHub Release, fixed ZIP, and records: unchanged
DRC_v2.0.1 tag, GitHub Release, fixed ZIP, and records: unchanged
```

## Completion state

R-1e and parent R-1 are completed and accepted. Daily Rhythm Companion v2.1.0 is released. Future development must use a new commit and version boundary; the planned strategic target is v3.0.0.
