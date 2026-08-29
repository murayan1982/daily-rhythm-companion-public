# DRC v4.0.0 Release Preparation Protocol

## Status

```text
Current checkpoint:
DRC v4.0.0 Release Preparation Protocol Control B

Current small commit:
DRC v4.0.0 Release Preparation Protocol Control B

Current implementation:
DRC v4.0.0 Release Preparation Protocol Control B

Current implementation state:
IMPLEMENTED / AWAITING_REVIEW

Control B baseline:
b752491632c58c557c02b06587cab28edcb901ca

implementation commit:
none

current released version:
v3.0.0 RELEASED / ACCEPTED

current v4 candidate metadata:
Backend 4.0.0 / Flutter 4.0.0+5 NOT_RELEASED

DRC-V4 Aggregate Readiness Reassessment:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

reassessment commit:
7ff8e34037808f6c002b1644201e856c1e0187f2

DRC-V4 bounded coexistence readiness:
READY_FOR_RELEASE_PREPARATION

DRC-V4 aggregate:
READY_FOR_RELEASE_PREPARATION

DRC v4.0.0:
NOT_RELEASED

Framework v6.0.0 framework-level readiness:
PARTIAL_READY / HISTORICAL_AND_STILL_TRUE

existing v3 real runtime:
PRESERVED / RELEASED / ACCEPTED

existing v3 replacement:
NO

/realtime/text replacement:
NO

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED

real unified FW runtime release blocker:
NO

Control A:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control A commit:
b752491632c58c557c02b06587cab28edcb901ca

Control B:
IMPLEMENTED / AWAITING_REVIEW

Candidate Backend:
4.0.0

Candidate Flutter:
4.0.0+5

release notes:
RELEASE CANDIDATE / NOT_RELEASED

release record:
PREPARED / NOT_RELEASED

Control C:
FUTURE / NOT_AUTHORIZED

Control D:
FUTURE / NOT_AUTHORIZED

Control E:
FUTURE / NOT_AUTHORIZED

fixed ZIP builder invocation count:
0

fixed ZIP:
NOT_BUILT

annotated tag:
NOT_CREATED

GitHub Release:
NOT_CREATED

stage:
NOT_AUTHORIZED / NOT_RUN

commit:
NOT_AUTHORIZED / NOT_RUN

push:
NOT_AUTHORIZED / NOT_RUN

package:
NOT_AUTHORIZED / NOT_RUN

tag:
NOT_AUTHORIZED / NOT_RUN

publication:
NOT_AUTHORIZED / NOT_RUN
```

## Purpose

Control A froze the DRC v4.0.0 release-preparation protocol as a
documentation/static-gate milestone. Control B prepares candidate metadata,
release notes, and the pre-release record while keeping DRC v4.0.0
`NOT_RELEASED`. It does not build a package, create a tag, or publish a release.

DRC v4.0.0 can proceed to release preparation because its accepted scope is
bounded coexistence adoption. It does not claim that Framework v6.0.0 provides a
production unified real STT -> streaming LLM -> TTS -> motion runtime.

## Accepted Starting State

```text
Current released version:
v3.0.0 RELEASED / ACCEPTED

DRC-V4 Aggregate Readiness Reassessment:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

reassessment commit:
7ff8e34037808f6c002b1644201e856c1e0187f2

Framework v6.0.0:
PARTIAL_READY / HISTORICAL_AND_STILL_TRUE

real unified FW runtime:
NOT_AVAILABLE / NOT_CLAIMED

real unified FW runtime release blocker:
NO

existing v3 replacement:
NO

/realtime/text replacement:
NO
```

The existing DRC v3 real runtime path remains preserved while DRC v4 adopts the
Framework v6 provider-free path alongside it.

## Five Release Controls

```text
Control A:
Release inventory / preparation protocol
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control A commit:
b752491632c58c557c02b06587cab28edcb901ca

Control B:
Candidate metadata / release-record preparation
IMPLEMENTED / AWAITING_REVIEW

Control C:
Release Candidate verification / no-build preflight
FUTURE / NOT_AUTHORIZED

Control D:
Fixed source ZIP / same-artifact acceptance
FUTURE / NOT_AUTHORIZED

Control E:
Publication
FUTURE / NOT_AUTHORIZED
```

Completion or acceptance of one control does not authorize the next control.

## Control A Boundary

```text
current milestone:
Control A - Release inventory / preparation protocol

docs/static gate only:
YES

version change:
NO

release-notes candidate mutation:
NO

package:
NOT_AUTHORIZED / NOT_RUN

tag:
NOT_AUTHORIZED / NOT_RUN

publication:
NOT_AUTHORIZED / NOT_RUN
```

No future version or build number was selected in Control A.

## Control B Boundary

Control B selects the v4.0.0 / 4.0.0+5 candidate metadata and prepares the
release notes and release record while still keeping DRC v4.0.0 `NOT_RELEASED`.

```text
Control B:
IMPLEMENTED / AWAITING_REVIEW

Control B baseline:
b752491632c58c557c02b06587cab28edcb901ca

Candidate Backend:
4.0.0

Candidate Flutter:
4.0.0+5

release notes:
RELEASE CANDIDATE / NOT_RELEASED

release record:
PREPARED / NOT_RELEASED

fixed ZIP builder invocation count:
0

fixed ZIP:
NOT_BUILT

annotated tag:
NOT_CREATED

GitHub Release:
NOT_CREATED
```

Control B does not run release-candidate full regression, configured operator
acceptance, packaging, fixed-ZIP building, tag creation, GitHub Release
creation, or publication.

## Future Control C

Control C is future work under separate exact review. It may run full
source/runtime regressions, configured coexistence verification, and
release-package hygiene preflight.

```text
Control C:
FUTURE / NOT_AUTHORIZED

fixed ZIP builder invocation count:
0

fixed ZIP:
NOT_BUILT
```

Control C is a no-build preflight. The fixed ZIP builder invocation count remains
`0`.

## Future Control D

Control D is future work under separate exact review. It may freeze the exact
release source HEAD, build the fixed ZIP exactly once, record artifact basename,
size, and SHA-256 outside the artifact, perform same-artifact verification,
extract the exact same ZIP, and execute the accepted verification matrix.

```text
Control D:
FUTURE / NOT_AUTHORIZED

silent rebuild:
NO

publication:
NO
```

## Future Control E

Control E is future work under separate exact review. It may perform publication
preflight, require explicit final operator approval, create the annotated tag,
create the GitHub Release, upload the unchanged accepted fixed ZIP, run
post-publication artifact/SHA/tag verification, and perform final documentation
sync.

```text
Control E:
FUTURE / NOT_AUTHORIZED

annotated tag:
NOT_CREATED

GitHub Release:
NOT_CREATED
```

## Authorization Boundaries

```text
implementation approval != stage approval
stage/commit approval != push approval
commit/push approval != package approval
package approval != tag approval
tag approval != publication approval
```

Package, tag, and publication remain separately gated.

## Artifact Invalidation Rule

If a source-affecting correction is required after the fixed ZIP has been built,
the accepted ZIP must not silently continue to be used. The artifact is treated
as invalidated, and any rebuild must be handled under a separately reviewed and
approved release contract.

artifact is treated as invalidated.

If a verifier-only correction does not change the frozen release source tuple,
record these independently:

```text
release source HEAD
verification HEAD
artifact SHA-256
```

Do not blur these values into one generic HEAD.

## Release Privacy Boundary

Release preparation and public artifacts must not contain:

```text
.env
API keys
credentials
tokens
raw audio
transcripts
provider payloads
screenshots
private filesystem paths
LAN/private IP addresses
operator evidence
local databases/data
generated build outputs
nested release artifacts
```

No credential inspection is required for this task.

## Static Verification Boundary

```text
static checker:
scripts/check_v400_release_preparation_protocol.py

provider API access:
NO

credentials:
NO

network requests:
NO

repository modification:
NO

release artifact creation:
NO

release builder invocation:
NO

tag creation:
NO

publication:
NO
```

## Exact Surface

```text
exact surface:
13 files / M9 A4 D0

MODIFY:
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
docs/v400_release_preparation_protocol.md
backend/app/version.py
app/pubspec.yaml
scripts/check_v20x_application_version_metadata.py

ADD:
docs/v400_release_candidate_metadata.md
docs/v400_release_record.md
release_notes/v4.0.0.md
scripts/check_v400_release_candidate_metadata.py

DELETE:
0
```

Protected surfaces include app, Backend, tests, release notes, version metadata,
dependency files, lockfiles, existing V4 detailed docs, existing V4 checker
scripts, v3 release records, packaging/build scripts, release artifacts, tags,
and GitHub Releases.

## Stop State

```text
DRC v4.0.0 Release Preparation Protocol:
IMPLEMENTED / AWAITING_REVIEW

DRC v4.0.0:
NOT_RELEASED

fixed ZIP builder invocation count:
0

fixed ZIP:
NOT_BUILT

annotated tag:
NOT_CREATED

GitHub Release:
NOT_CREATED

stage:
NOT_AUTHORIZED / NOT_RUN

commit:
NOT_AUTHORIZED / NOT_RUN

push:
NOT_AUTHORIZED / NOT_RUN

package:
NOT_AUTHORIZED / NOT_RUN

tag:
NOT_AUTHORIZED / NOT_RUN

publication:
NOT_AUTHORIZED / NOT_RUN
```
