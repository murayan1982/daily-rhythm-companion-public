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
FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW

Control D Stage 2:
CLEAN_COMMITTED_SOURCE_PREFLIGHT / BLOCKED_PENDING_STAGE1_ACCEPTANCE / NOT_AUTHORIZED

Control D Stage 3:
BUILD_EXACTLY_ONCE / BLOCKED_PENDING_STAGE2_ACCEPTANCE / NOT_AUTHORIZED

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
preflight. Control D Stage 1 adds credential-free fixed ZIP tooling only;
Stage 2 through Stage 4 remain blocked pending separate acceptance and
authorization. Control E owns publication and remains future/not authorized.
