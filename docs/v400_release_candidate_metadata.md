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
NOT_BUILT

builder invocation count:
0

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

Control D Stage 2: CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED

Control D Stage 3: BUILD_EXACTLY_ONCE / READY_FOR_SEPARATE_AUTHORIZATION / NOT_AUTHORIZED

Control D Stage 4:
SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / BLOCKED_PENDING_STAGE3_ARTIFACT / NOT_AUTHORIZED

Control E:
FUTURE / NOT_AUTHORIZED
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
2 clean committed source preflight completed, passed, and is accepted. Stage 3
is ready for separate authorization but remains not authorized. Stage 4 remains
blocked pending the Stage 3 artifact. Control E owns publication and remains
future/not authorized.
