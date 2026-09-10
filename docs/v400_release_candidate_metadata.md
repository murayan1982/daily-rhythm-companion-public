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

Control D Stage 4:
SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED / NOT_RUN

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
`46f5af49106c6ecc0d478a425cf709cf511da1be`. Control D Stage 4 same-artifact
verification is authorized but not run. Control E is not authorized,
tag/publication are not run, and DRC v4.0.0 is not released. Stage 3 builder
rerun is forbidden; the fixed ZIP must not be deleted, renamed, overwritten, or
regenerated. Stage 4 authorization-sync candidate cannot run release-zip
verifier until reviewed, accepted, committed, and pushed. After commit/push,
Stage 4 verifier still needs separate explicit approval. Verification HEAD
remains NOT_RECORDED until Stage 4 execution acceptance-sync.
