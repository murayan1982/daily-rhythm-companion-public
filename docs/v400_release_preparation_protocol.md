# DRC v4.0.0 Release Preparation Protocol

## Status

```text
Current checkpoint:
DRC v4.0.0 Control E Release Authorization Sync Corrective R6

Current small commit:
DRC v4.0.0 Control E Release Authorization Sync Corrective R6

Current implementation:
DRC v4.0.0 Control E Release Authorization Sync Corrective R6

Current implementation state:
CONTROL_E_RELEASE_AUTHORIZATION_SYNC_CORRECTIVE_R6 / IMPLEMENTED / STATIC_VERIFIED / SCHEMA_SELFCHECK_FILESYSTEM_INDEPENDENT / RAW_TOKEN_EXACT_MATCH_PRESERVED / ACTUAL_CONTRACT_PRECHECK_BEFORE_SCHEMA_VERIFIED / INVALID_CONTRACT_DOWNSTREAM_BLOCK_VERIFIED / MIDDLE_VERSION_SHADOW_HEADING_GUARD_PRESERVED / DEFAULT_RUNTIME_GUARD_CONNECTED / PUBLICATION_REACHABILITY_RUNTIME_VERIFIED / POST_SOURCE_MATRIX_0_TO_7_VERIFIED / HANDOFF_SELF_HASH_VERIFIED / CONTROL_E_NOT_RUN / NEW_THREAD_HANDOFF_CREATED / READY_FOR_RE_REVIEW

Control C baseline:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Control C implementation commit:
4cae15573f3332cbc476557461babdfe2eb3c0bf

Control D Stage 1:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 1 implementation commit:
a204f6b11d25baeea67b7b7be8860c9a4f9ea945

Control D Stage 1 surface:
13 files / M10 A3 D0

current implementation commit:
none

current implementation commit / push:
NOT_AUTHORIZED

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
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control B implementation baseline:
b752491632c58c557c02b06587cab28edcb901ca

Control B implementation commit:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Candidate Backend:
4.0.0

Candidate Flutter:
4.0.0+5

release notes:
RELEASE CANDIDATE / NOT_RELEASED

release record:
PREPARED / NOT_RELEASED

Control C:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control C baseline:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Control D:
CURRENT / NOT_COMPLETED

Control D Stage 1:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2: CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2 acceptance-sync commit:
697d0918cb8a6de5c0459324464b7d7e376b3a5a

Control D Stage 3: BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED

Control D Stage 4 authorization-sync:
COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED

Control D Stage 4 authorization-sync commit:
0a6e6e65f8c775022471018bc3ca6c03b2ed588b

Stage 4 invocation 1:
EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED

verification verdict:
PASS

failure class:
NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE

release-package scanner known fixtures:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

ZIP structural/version checks reached before failure:
PASS

extracted compileall:
PASS

extracted Backend pytest:
PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED

fixed ZIP preservation:
PRESERVED / BYTE_IDENTICAL

Historical Stage 4 retry:
CONSUMED / FAILED

Stage 4 invocation 3:
EXACTLY_ONCE_EXECUTED / PASS / REVIEWED / ACCEPTED

Stage 4 invocation 3 process exit code:
0

Stage 4 invocation 3 Backend result:
479 passed / 1 warning

Stage 4 invocation 3 scanner result:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

Stage 4 invocation 3 same artifact verified:
TRUE

Stage 4 invocation 3 builder invoked by verifier:
FALSE

Invocation 3 completed invocation count:
1

Invocation 3 explicit authorization budget:
1

Invocation 3 explicit authorization budget remaining:
0

Invocation 3 authorization state:
CONSUMED

Additional Stage 4 invocation authorized:
FALSE

Stage 4 release-ZIP reachability:
FALSE

Control D Stage 4:
COMPLETED / PASS / ACCEPTED

Cumulative completed Stage 4 verifier invocations:
3

Next authorized invocation number:
NOT_AUTHORIZED

Historical retry invocation count:
1

Historical retry budget remaining:
0

Control E:
AUTHORIZED / NOT_RUN

fixed ZIP builder invocation count:
1

fixed ZIP:
release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip

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
documentation/static-gate milestone. Control B prepared candidate metadata,
release notes, and the pre-release record while keeping DRC v4.0.0
`NOT_RELEASED`. Control C completed release-candidate verification and a
source-only no-build preflight while preserving package, tag, and publication
boundaries. Control D Stage 1 added fixed ZIP tooling and is closed. Control D
Stage 2 clean committed source preflight completed, passed, and is accepted.

Control D Stage 3 fixed ZIP build completed, passed, and is accepted. Control D
Stage 4 authorization-sync completed and was committed, pushed, reviewed, and
accepted at `0a6e6e65f8c775022471018bc3ca6c03b2ed588b`. Stage 4 invocation 1
was executed exactly once and failed before a conclusive verdict; the failure
class is `NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE`.

The release-package scanner findings were the exact accepted source-matched
fixtures. ZIP structure/version checks passed, and extracted compileall passed.
The extracted Backend pytest process completed, but its result/count was not
evaluated because output emission raised `UnicodeEncodeError`. The Stage 4
conclusive verdict was not reached. The fixed ZIP remains preserved. Stage 4 retry is CONSUMED / FAILED, Control E is authorized for exactly one not-run publication, and DRC
v4.0.0 remains `NOT_RELEASED`.

The accepted Stage 2 source preflight preserved the bounded release scope:
bounded coexistence adoption. It does not claim that Framework v6.0.0 provides a
production unified real STT -> streaming LLM -> TTS -> motion runtime.
Current guard statements: Control D Stage 4 authorization-sync completed and was committed, pushed, reviewed, and accepted. Stage 4 invocation 1 was executed exactly once and failed. failure class is NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE. scanner findings were the exact accepted source-matched fixtures. extracted Backend pytest process completed, but its result/count was not evaluated. Stage 4 invocation 2 was executed exactly once and failed. pytest default shared user TEMP root. 272 passed / 207 setup errors. Stage 4 conclusive verdict was not reached. fixed ZIP remains preserved. Stage 4 retry is CONSUMED / FAILED. Invocation 3 authorization is consumed. Control E is authorized for exactly one not-run publication. DRC v4.0.0 remains NOT_RELEASED. bounded release scope: bounded coexistence adoption. does not claim that Framework v6.0.0 provides a production unified real STT -> streaming LLM -> TTS -> motion runtime.

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
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control B implementation commit:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Control C:
Release Candidate verification / no-build preflight
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D:
Fixed source ZIP / same-artifact acceptance
CURRENT / NOT_COMPLETED

Control D Stage 1:
Fixed ZIP tooling implementation
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2:
Clean committed source preflight
COMPLETED / PASS / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 3:
Build exactly once
COMPLETED / PASS / ACCEPTED

Control D Stage 4 authorization-sync:
COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED

Stage 4 invocation 1:
EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED

verification verdict:
PASS

failure class:
NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE

Historical Stage 4 retry:
CONSUMED / FAILED

Stage 4 invocation 3:
EXACTLY_ONCE_EXECUTED / PASS / REVIEWED / ACCEPTED

Stage 4 invocation 3 process exit code:
0

Stage 4 invocation 3 Backend result:
479 passed / 1 warning

Stage 4 invocation 3 scanner result:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

Stage 4 invocation 3 same artifact verified:
TRUE

Stage 4 invocation 3 builder invoked by verifier:
FALSE

Invocation 3 completed invocation count:
1

Invocation 3 explicit authorization budget:
1

Invocation 3 explicit authorization budget remaining:
0

Invocation 3 authorization state:
CONSUMED

Additional Stage 4 invocation authorized:
FALSE

Stage 4 release-ZIP reachability:
FALSE

Control D Stage 4:
COMPLETED / PASS / ACCEPTED

Cumulative completed Stage 4 verifier invocations:
3

Next authorized invocation number:
NOT_AUTHORIZED

Historical retry invocation count:
1

Historical retry budget remaining:
0

Control E:
Publication
NOT_AUTHORIZED / NOT_RUN

DRC v4.0.0:
NOT_RELEASED
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

Control B selected the v4.0.0 / 4.0.0+5 candidate metadata and prepared the
release notes and release record while still keeping DRC v4.0.0 `NOT_RELEASED`.

```text
Control B:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control B implementation baseline:
b752491632c58c557c02b06587cab28edcb901ca

Control B implementation commit:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

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

Control B did not run release-candidate full regression, configured operator
acceptance, packaging, fixed-ZIP building, tag creation, GitHub Release
creation, or publication.

## Control C Boundary

Control C is the accepted release-candidate verification and no-build preflight.
It ran full source/runtime regressions, configured coexistence verification,
and source-only release-package hygiene preflight. The current checkpoint is
Control D Stage 4 Verifier Output Encoding Corrective R1.

```text
Control C:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control C baseline:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

full source/runtime regression:
AUTHORIZED_FOR_VERIFICATION

v3/FW-v6 provider-free coexistence focused verification:
AUTHORIZED_FOR_SOURCE_AND_IN_PROCESS_TESTS

source-only release-package hygiene preflight:
AUTHORIZED

fixed ZIP builder invocation count:
0

fixed ZIP:
NOT_BUILT
```

Control C was a historical no-build preflight. Its fixed ZIP builder invocation
count was `0`, and its fixed ZIP state was `NOT_BUILT`. Control C does not
execute a real provider, read credentials or `.env`
contents, use microphone/STT/LLM/TTS/audio playback/VTube Studio/motion, run
private operators, start the Backend server, perform loopback HTTP operator
execution, access external networks, build Flutter release artifacts, invoke a
release builder, create release artifacts, stage, commit, push, tag, or publish.

## Control D Boundary

Control D is split into four separately accepted stages. Stage 1 implemented
credential-free, provider-free, private-evidence-free fixed ZIP tooling and is
closed at commit `a204f6b11d25baeea67b7b7be8860c9a4f9ea945`. Stage 2 clean
committed source preflight completed, passed, and is accepted. This does not authorize
Stage 3, Stage 4, Control E, package creation, tag creation, GitHub Release
creation, or publication.

Control D owns the release source HEAD, verification HEAD, and fixed ZIP.

```text
Control D:
CURRENT / NOT_COMPLETED

Control D Stage 1:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2: CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2 acceptance-sync commit: 697d0918cb8a6de5c0459324464b7d7e376b3a5a

Control D Stage 3: BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED

Control D Stage 4 authorization-sync:
COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED

Control D Stage 4 authorization-sync commit:
0a6e6e65f8c775022471018bc3ca6c03b2ed588b

Stage 4 invocation 1:
EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED

verification verdict:
PASS

failure class:
NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE

release-package scanner known fixtures:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

ZIP structural/version checks reached before failure:
PASS

extracted compileall:
PASS

extracted Backend pytest:
PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED

fixed ZIP preservation:
PRESERVED / BYTE_IDENTICAL

Historical Stage 4 retry:
CONSUMED / FAILED

Stage 4 invocation 3:
EXACTLY_ONCE_EXECUTED / PASS / REVIEWED / ACCEPTED

Stage 4 invocation 3 process exit code:
0

Stage 4 invocation 3 Backend result:
479 passed / 1 warning

Stage 4 invocation 3 scanner result:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

Stage 4 invocation 3 same artifact verified:
TRUE

Stage 4 invocation 3 builder invoked by verifier:
FALSE

Invocation 3 completed invocation count:
1

Invocation 3 explicit authorization budget:
1

Invocation 3 explicit authorization budget remaining:
0

Invocation 3 authorization state:
CONSUMED

Additional Stage 4 invocation authorized:
FALSE

Stage 4 release-ZIP reachability:
FALSE

Control D Stage 4:
COMPLETED / PASS / ACCEPTED

Cumulative completed Stage 4 verifier invocations:
3

Next authorized invocation number:
NOT_AUTHORIZED

Historical retry invocation count:
1

Historical retry budget remaining:
0

silent rebuild:
NO

fixed ZIP builder invocation count:
1

fixed ZIP:
release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip

publication:
NO
```

Stage 2 accepted evidence:

```text
Stage 2 source preflight HEAD:
eb68cf9334f46a30c0c06d3921d59f56abb540bb

source-tree verifier:
COMPLETED / PASS / exit 0

accepted corrective source-tree verifier invocation count:
1

elapsed:
00:05:08.0615422

Python:
3.12.0 / dependency-complete repository runtime

Backend full:
479 PASS

Flutter SDK:
3.41.7 stable

Flutter framework revision:
cc0734ac716fbb8b90f3f9db8020958b1553afa7

Flutter analyze:
PASS / No issues found

Flutter full:
570 PASS

Flutter web build:
PASS

Flutter Windows build:
PASS

Flutter APK debug build:
PASS

repository preservation:
working tree clean / Git index empty

package_config:
PRESERVED / SHA-256 AND TIMESTAMP UNCHANGED

release builder invocation:
0

fixed ZIP:
NOT_BUILT

DRC_v4.0.0 tag:
NOT_CREATED
```

Stage 1 added `docs/v400_fixed_release_zip.md`,
`build_v400_fixed_release_zip_from_head.ps1`, and
`scripts/check_v400_fixed_release_zip.py`.

`-PreflightOnly` must not create a worktree, run `build_release.bat`, create a
generic ZIP, create a fixed ZIP, create a tag, or publish. The current Stage 4
authorization marker count is exact 2 across the current v4 documents. Dirty
default mode validates the exact M12 authorization-sync candidate surface, the
fixed ZIP exact-one artifact, and the recorded tuple for
`DailyRhythmCompanion_v4.0.0_20260908_173440.zip` with size `3018230`,
SHA-256 `F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142`,
and source HEAD `46f5af49106c6ecc0d478a425cf709cf511da1be`. The Stage 3
one-time build authorization token is consumed; current documentation count is
0 and builder rerun is forbidden. The release ZIP verifier remains unreachable
until Stage 4 authorization-sync is clean, committed, and pushed. Stage 4
same-artifact verification has completed and passed. Control E is authorized for exactly one not-run publication.

Mode-specific ordering is part of the fixed ZIP tooling contract. Default mode
is limited to Stage 2 accepted static/current-state checks, consumed Stage 2
authorization-token absence, Stage 2 accepted marker exactness, consumed Stage 3
authorization-token absence, Stage 4 authorization-marker exactness, fixed ZIP
tuple preservation, and exact dirty/clean Stage 4 authorization-sync surface
checks.
Source-tree mode requires Stage 2 accepted state and uses the
fixed-ZIP absent policy. Release-ZIP mode requires Stage 4 authorization plus a
Stage 3 artifact-ready accepted state and verifies exactly one supplied fixed
ZIP with the supplied expected source HEAD and SHA-256; it does not use the
absent-artifact gate.

Known privacy-scanner fixture exceptions must exactly match the expected source
HEAD Git blobs and required marker bytes. Extracted Flutter dependency
preparation may run only offline `pub get` inside the temporary extracted tree
when package config is missing; repository source-tree verification must not run
`pub get`. Repository source-tree and temporary extracted ZIP Flutter tests use
the shared `<ABSOLUTE_FLUTTER_COMMAND> test --no-pub --reporter expanded`
command helper. If verification HEAD contains source-affecting changes after
the expected source HEAD, the artifact is invalidated.

For current v4 sources, known fixtures are always verified regardless of the
generic scanner result. The expected scanner result is exactly two findings for
the known fixture files, and scanner pass, missing fixtures, sanitized or
modified fixtures, duplicate findings, missing findings, unexpected findings,
source mismatch, and marker absence are rejected.

ZIP Backend and Flutter metadata must be read from the ZIP and matched to the
expected source HEAD blobs. Backend must declare exactly `4.0.0`, Flutter must
declare exactly `4.0.0+5`, duplicate active version declarations are rejected,
and ZIP/source mismatch is rejected. The checker's mode dispatcher and
deterministic self-checks use the same mode-policy contract.


Control D Stage 4 authorization-sync is COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED at `0a6e6e65f8c775022471018bc3ca6c03b2ed588b`. Stage 4 invocation 1 was EXACTLY_ONCE_EXECUTED and ended EXECUTION_FAILED before a verification verdict; verdict is NOT_REACHED and failure class is NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE. Stage 4 invocation 2 was EXACTLY_ONCE_EXECUTED and ended EXECUTION_FAILED with NON_PRODUCT_VERIFIER_PYTEST_BASETEMP_PERMISSION_FAILURE after Backend pytest reported 272 passed / 207 setup errors from PermissionError / WinError 5 on pytest default shared user TEMP root. Release-package scanner known fixtures were EXACT_EXPECTED_FINDINGS / ACCEPTED, ZIP structural/version checks reached before failure were PASS, extracted compileall was PASS, and extracted Backend pytest was PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED. Stage 4 authorization marker was consumed. The fixed ZIP is PRESERVED and must not be deleted, renamed, overwritten, regenerated, or retried. Stage 4 retry is CONSUMED / FAILED, Control E is authorized for exactly one not-run publication, tag/publication are NOT_RUN, and DRC v4.0.0 is NOT_RELEASED. The exact artifact was created and its tuple is recorded; fixed ZIP exact-one artifact remains preserved. Stage 3 one-time build authorization token is consumed; current documentation count is 0. The release-ZIP verifier remains unreachable from the current corrective modes; Stage 4 invocation 1 executed and failed before verdict, and historical retry budget is consumed and Invocation 3 authorization is consumed. Control E is authorized for exactly one not-run publication, tag/publication are not run, and DRC v4.0.0 is not released.

## Future Control E

Control E is future work under separate exact review. It may perform publication
preflight, require explicit final operator approval, create the annotated tag,
create the GitHub Release, upload the unchanged accepted fixed ZIP, run
post-publication artifact/SHA/tag verification, and perform final documentation
sync. Control E owns tag, GitHub Release, and publication.

```text
Control E:
AUTHORIZED / NOT_RUN

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
12 files / M12 A0 D0

MODIFY:
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
docs/v400_release_preparation_protocol.md
docs/v400_release_candidate_metadata.md
docs/v400_release_candidate_no_build_preflight.md
docs/v400_fixed_release_zip.md
docs/v400_release_record.md
scripts/check_v400_fixed_release_zip.py
scripts/check_v400_release_candidate_no_build_preflight.py

ADD:
0

DELETE:
0
```

Protected surfaces include app, Backend, tests, release notes, version metadata,
dependency files, lockfiles, existing V4 detailed docs and checker scripts other
than the new Control C preflight gate, v3 release records, packaging/build
scripts, release artifacts, tags, and GitHub Releases.

## Stop State

```text
DRC v4.0.0 Release Preparation Protocol:
CONTROL_E_RELEASE_AUTHORIZATION_SYNC_CORRECTIVE_R6 / IMPLEMENTED / STATIC_VERIFIED / SCHEMA_SELFCHECK_FILESYSTEM_INDEPENDENT / RAW_TOKEN_EXACT_MATCH_PRESERVED / ACTUAL_CONTRACT_PRECHECK_BEFORE_SCHEMA_VERIFIED / INVALID_CONTRACT_DOWNSTREAM_BLOCK_VERIFIED / MIDDLE_VERSION_SHADOW_HEADING_GUARD_PRESERVED / DEFAULT_RUNTIME_GUARD_CONNECTED / PUBLICATION_REACHABILITY_RUNTIME_VERIFIED / POST_SOURCE_MATRIX_0_TO_7_VERIFIED / HANDOFF_SELF_HASH_VERIFIED / CONTROL_E_NOT_RUN / NEW_THREAD_HANDOFF_CREATED / READY_FOR_RE_REVIEW

Control B:
CLOSED

Control C:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

exact surface:
12 files / M12 A0 D0

Control D:
CURRENT / NOT_COMPLETED

Control D Stage 1:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2:
CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 3:
BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED

Control D Stage 4 authorization-sync:
COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED

Control D Stage 4 authorization-sync commit:
0a6e6e65f8c775022471018bc3ca6c03b2ed588b

Stage 4 invocation 1:
EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED

verification verdict:
PASS

failure class:
NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE

release-package scanner known fixtures:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

ZIP structural/version checks reached before failure:
PASS

extracted compileall:
PASS

extracted Backend pytest:
PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED

fixed ZIP preservation:
PRESERVED / BYTE_IDENTICAL

Historical Stage 4 retry:
CONSUMED / FAILED

Stage 4 invocation 3:
EXACTLY_ONCE_EXECUTED / PASS / REVIEWED / ACCEPTED

Stage 4 invocation 3 process exit code:
0

Stage 4 invocation 3 Backend result:
479 passed / 1 warning

Stage 4 invocation 3 scanner result:
EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED

Stage 4 invocation 3 same artifact verified:
TRUE

Stage 4 invocation 3 builder invoked by verifier:
FALSE

Invocation 3 completed invocation count:
1

Invocation 3 explicit authorization budget:
1

Invocation 3 explicit authorization budget remaining:
0

Invocation 3 authorization state:
CONSUMED

Additional Stage 4 invocation authorized:
FALSE

Stage 4 release-ZIP reachability:
FALSE

Control D Stage 4:
COMPLETED / PASS / ACCEPTED

Cumulative completed Stage 4 verifier invocations:
3

Next authorized invocation number:
NOT_AUTHORIZED

Historical retry invocation count:
1

Historical retry budget remaining:
0

DRC v4.0.0:
NOT_RELEASED

fixed ZIP builder invocation count:
1

fixed ZIP:
release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip

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
## Control E Release Authorization Sync Corrective R6 Current Section

Current checkpoint: DRC v4.0.0 Control E Release Authorization Sync Corrective R6
Current implementation state: CONTROL_E_RELEASE_AUTHORIZATION_SYNC_CORRECTIVE_R6 / IMPLEMENTED / STATIC_VERIFIED / SCHEMA_SELFCHECK_FILESYSTEM_INDEPENDENT / RAW_TOKEN_EXACT_MATCH_PRESERVED / ACTUAL_CONTRACT_PRECHECK_BEFORE_SCHEMA_VERIFIED / INVALID_CONTRACT_DOWNSTREAM_BLOCK_VERIFIED / MIDDLE_VERSION_SHADOW_HEADING_GUARD_PRESERVED / DEFAULT_RUNTIME_GUARD_CONNECTED / PUBLICATION_REACHABILITY_RUNTIME_VERIFIED / POST_SOURCE_MATRIX_0_TO_7_VERIFIED / HANDOFF_SELF_HASH_VERIFIED / CONTROL_E_NOT_RUN / NEW_THREAD_HANDOFF_CREATED / READY_FOR_RE_REVIEW
Control D Stage 4: COMPLETED / PASS / ACCEPTED / COMMITTED / PUSHED / CLOSED
Control D Stage 4 result-sync commit: 6aaf35e73df50cf5f570373a0b97da4290cc4e4e
Stage 4 invocation 1 result: EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED
Stage 4 invocation 1 failure class: NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE
Stage 4 invocation 2 result: EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED
Stage 4 invocation 2 failure class: NON_PRODUCT_VERIFIER_PYTEST_BASETEMP_PERMISSION_FAILURE
Stage 4 invocation 2 Backend result: 272 passed / 207 setup errors
Stage 4 invocation 2 first conclusive failure: PermissionError / WinError 5 on pytest default shared user TEMP root
Stage 4 invocation 3 result: EXACTLY_ONCE_EXECUTED / PASS / REVIEWED / ACCEPTED
Stage 4 invocation 3 start: 2026-09-16T12:55:17.0067656+09:00
Stage 4 invocation 3 end: 2026-09-16T12:55:56.9863189+09:00
Stage 4 invocation 3 process exit code: 0
Stage 4 invocation 3 verification HEAD: f1de9f527c8a01d7c75f7a8cfef274cf32ac74ef
Stage 4 invocation 3 Backend result: 479 passed / 1 warning
Stage 4 invocation 3 scanner result: EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED
Stage 4 invocation 3 tooling state: RELEASE_ZIP_VERIFICATION
Stage 4 invocation 3 same artifact verified: TRUE
Stage 4 invocation 3 builder invoked by verifier: FALSE
Stage 4 invocation 3 final marker: [v400-fixed-release-zip-check] OK
Stage 4 verification verdict: PASS
release-package scanner known fixtures: EXACT_SOURCE_MATCHED_SYNTHETIC_FIXTURES / ACCEPTED
Historical Stage 4 retry: CONSUMED / FAILED
Cumulative completed Stage 4 verifier invocations: 3
Historical retry invocation count: 1
Historical retry budget remaining: 0
Next authorized invocation number: NOT_AUTHORIZED
Invocation 3 completed invocation count: 1
Invocation 3 explicit authorization budget: 1
Invocation 3 explicit authorization budget remaining: 0
Invocation 3 authorization state: CONSUMED
Additional Stage 4 invocation authorized: FALSE
Stage 4 release-ZIP reachability: FALSE
Control E: AUTHORIZED / NOT_RUN
Control E authorized: TRUE
Control E execution count: 0
Control E explicit authorization budget: 1
Control E explicit authorization budget remaining: 1
Next authorized action: CREATE_DRC_V4_0_0_ANNOTATED_TAG_AND_GITHUB_RELEASE_FOR_FIXED_ZIP
Control E execution eligibility: REQUIRES_CLEAN_COMMITTED_PUSHED_CONTROL_E_RELEASE_AUTHORIZATION_SYNC
Fixed ZIP authorized publication artifact: release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip
Builder invoked by verifier: FALSE
fixed ZIP basename: DailyRhythmCompanion_v4.0.0_20260908_173440.zip
fixed ZIP size: 3018230
fixed ZIP SHA-256: F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142
fixed ZIP source HEAD: 46f5af49106c6ecc0d478a425cf709cf511da1be
fixed ZIP UTC timestamp: 2026-09-08 08:35:05
fixed ZIP: PRESERVED / BYTE_IDENTICAL
annotated tag: NOT_CREATED
GitHub Release: NOT_CREATED
DRC v4.0.0: NOT_RELEASED
## Stage 4 Retry Authorization Notes

Invocation 1 remains historical failure evidence and must not be rewritten as PASS or completed; its verdict remains NOT_REACHED. The corrective fixed verifier output handling and retry authorization guarding only. Product/source ZIP contents were not repaired or regenerated. Authorization applies only to the preserved fixed ZIP tuple: release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip / 3018230 bytes / F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142 / source HEAD 46f5af49106c6ecc0d478a425cf709cf511da1be / UTC 2026-09-08 08:35:05.

The retry authorization is consumed and inert. The release-ZIP verifier remains unreachable in every mode. Invocation 3 completed with PASS and consumed its authorization budget. Automatic retry is forbidden. No additional Stage 4 invocation is authorized. The builder remains forbidden. Control E is authorized for exactly one not-run publication only after this authorization-sync is clean, committed, and pushed. Tag, publication, and GitHub Release remain not created. Bounded historical Control B, Control C, and Stage 3 evidence remains preserved.
## R1 Review Handoff

Implementation handoff: exact M12 authorization-sync candidate updates current docs/checker diagnostics only; product source, builder, fixed ZIP, tag, publication, and Control E remain unchanged and not authorized.

Static verification handoff: Python syntax compile, fixed-ZIP default static checker, and no-build preflight static checker are the review inputs; Invocation 3, `--release-zip`, fixed-ZIP Backend pytest, builder, stage, commit, push, amend, tag, GitHub Release, and publication are not run.

Dispatch handoff: dirty and clean-not-pushed Invocation 3 authorization-sync states keep release_zip_reachability FALSE; clean+pushed Invocation 3 authorization-sync makes release_zip_reachability TRUE for later separately reviewed execution eligibility only.

## Control E Release Authorization Token
Control E release publication authorization: AUTHORIZED_FOR_EXACTLY_ONE_CONTROL_E_RELEASE_PUBLICATION
