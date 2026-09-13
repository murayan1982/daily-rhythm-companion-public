# Daily Rhythm Companion v4.0.0 release candidate metadata

## Status

```text
Status:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control B baseline:
b752491632c58c557c02b06587cab28edcb901ca

Control B implementation commit:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Control A:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control A commit:
b752491632c58c557c02b06587cab28edcb901ca

current released version:
v3.0.0 RELEASED / ACCEPTED

Backend candidate version:
4.0.0

Flutter candidate version:
4.0.0+5

candidate release:
v4.0.0 RELEASE CANDIDATE / NOT_RELEASED

planned tag:
DRC_v4.0.0

fixed ZIP:
release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip

builder invocation count:
1

GitHub Release:
NOT_CREATED

DRC v4.0.0:
NOT_RELEASED

Control C:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control C implementation commit:
4cae15573f3332cbc476557461babdfe2eb3c0bf

Control D:
CURRENT / NOT_COMPLETED

Control D Stage 1:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 1 implementation commit:
a204f6b11d25baeea67b7b7be8860c9a4f9ea945

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
NOT_REACHED

failure class:
NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE

release-package scanner known fixtures:
EXACT_EXPECTED_FINDINGS / ACCEPTED

ZIP structural/version checks reached before failure:
PASS

extracted compileall:
PASS

extracted Backend pytest:
PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED

fixed ZIP preservation:
PRESERVED

Stage 4 retry:
AUTHORIZED / NOT_RUN

Control E:
NOT_AUTHORIZED
```

## Version Ownership

`backend/app/version.py` is the Backend/API semantic version owner.
`app/pubspec.yaml` is the Flutter semantic version/build owner. The candidate
semantic version is `4.0.0`, and the Flutter build number for this candidate is
`5`. Do not add duplicate version constants to Web or platform sources.

## Control B Boundary

Control B performs candidate metadata and release-document preparation only.

Control B does not run release candidate full regression, run configured
operator acceptance, build the fixed ZIP, invoke the release builder, record the
release source HEAD, create a tag, create a GitHub Release, or publish.

Control C owns the accepted release-candidate verification and no-build
preflight. Control D Stage 1 added credential-free fixed ZIP tooling and is
closed at commit `a204f6b11d25baeea67b7b7be8860c9a4f9ea945`. Control D Stage
2 clean committed source preflight completed, passed, and is accepted, committed,
and pushed. Control D Stage 3 fixed ZIP build is completed and passed; the exact
artifact was created and its tuple is recorded as
`DailyRhythmCompanion_v4.0.0_20260908_173440.zip`, size `3018230`, SHA-256
`F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142`, source HEAD
`46f5af49106c6ecc0d478a425cf709cf511da1be`. Control D Stage 4 authorization-sync is committed, pushed, reviewed, accepted, and closed at `0a6e6e65f8c775022471018bc3ca6c03b2ed588b`. Stage 4 invocation 1 was executed exactly once and failed before verdict with failure class `NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE`. Retry is not authorized or run. Control E is not authorized, tag/publication are not run, and DRC v4.0.0 is not released.
## Stage 4 Retry Authorization Sync Corrective R5 Current Section
Current checkpoint: DRC v4.0.0 Control D Stage 4 Retry Authorization Sync Corrective R5
Current implementation state: CONTROL_D_STAGE4_RETRY_AUTHORIZATION_SYNC_CORRECTIVE_R5 / IMPLEMENTED / STATIC_VERIFIED / AWAITING_RE_REVIEW
Output-encoding corrective commit: 4a5e848458445f170da53d4b60781154e65117ec
Stage 4 invocation 1 result: EXACTLY_ONCE_EXECUTED / EXECUTION_FAILED
Stage 4 invocation 1 verification verdict: NOT_REACHED
Stage 4 retry: AUTHORIZED / NOT_RUN
Cumulative completed Stage 4 verifier invocations: 1
Next authorized invocation number: 2
Retry invocation budget: EXACTLY_ONE
No third invocation authorized: TRUE
fixed ZIP basename: DailyRhythmCompanion_v4.0.0_20260908_173440.zip
fixed ZIP size: 3018230
fixed ZIP SHA-256: F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142
fixed ZIP source HEAD: 46f5af49106c6ecc0d478a425cf709cf511da1be
fixed ZIP UTC timestamp: 2026-09-08 08:35:05
Control E: NOT_AUTHORIZED
DRC v4.0.0: NOT_RELEASED

## Stage 4 Retry Authorization Notes

Invocation 1 remains historical failure evidence and must not be rewritten as PASS or completed; its verdict remains NOT_REACHED. The corrective fixed verifier output handling and retry authorization guarding only. Product/source ZIP contents were not repaired or regenerated. Authorization applies only to the preserved fixed ZIP tuple: release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip / 3018230 bytes / F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142 / source HEAD 46f5af49106c6ecc0d478a425cf709cf511da1be / UTC 2026-09-08 08:35:05.

The retry authorization is inert while dirty, uncommitted, or not pushed. The release-ZIP verifier remains unreachable while dirty or not pushed. Only invocation number 2 is authorized. Automatic retry is forbidden. Any result from invocation 2 must stop further execution. No third invocation is authorized. The builder remains forbidden. Tag, publication, GitHub Release, and Control E remain blocked. Bounded historical Control B, Control C, and Stage 3 evidence remains preserved.
