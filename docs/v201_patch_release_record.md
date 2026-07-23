# Daily Rhythm Companion v2.0.1 patch release record

Updated: 2026-07-23
Status: PREPARED / NOT_RELEASED
Release tag: NOT_CREATED
GitHub Release: NOT_CREATED
Fixed release ZIP: NOT_BUILT
Fixed release ZIP SHA-256: NOT_RECORDED
Post-publication SHA-256 re-verification: NOT_RUN

## Record contract

M-9 prepares the v2.0.1 patch release but does not complete or publish it. The exact release tuple must be captured after the fixed ZIP is built once and the same file passes verification.

```text
Public repository: murayan1982/daily-rhythm-companion-public
source branch: main
source HEAD: <record after final committed-source gate>
annotated tag: DRC_v2.0.1
fixed ZIP basename: <record after one-time build>
fixed ZIP size bytes: <record after one-time build>
fixed ZIP SHA-256: <record after one-time build>
same-ZIP verification: <record after verification>
GitHub Release: <record only after final approval>
post-publication SHA-256 re-verification: <record after publication>
```

## Non-circular SHA rule

The final ZIP SHA-256 is not embedded into the ZIP that it hashes. The exact source HEAD, ZIP basename, size, and SHA-256 belong in the annotated tag message and GitHub Release body. A later post-publication documentation commit may synchronize those already-published values without rewriting the release tag or artifact.

## Current stop condition

```text
- M-1 through M-8 are completed and accepted.
- M-9 is CURRENT / NOT_COMPLETED.
- v2.0.1 release notes are prepared.
- No fixed v2.0.1 ZIP has been built by this preparation commit.
- DRC_v2.0.1 has not been created.
- No v2.0.1 GitHub Release has been published.
- Final publication requires explicit operator approval after same-ZIP verification.
```

The v2.0.0 historical checklist, release notes, tag, release asset, and recorded SHA-256 remain unchanged.
