# Daily Rhythm Companion v4.0.0 release candidate metadata

## Status

```text
Status:
IMPLEMENTED / AWAITING_REVIEW

Control B baseline:
b752491632c58c557c02b06587cab28edcb901ca

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
FUTURE / NOT_AUTHORIZED

Control D:
FUTURE / NOT_AUTHORIZED

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

Control C owns release-candidate verification and no-build preflight. Control D owns fixed ZIP and same-artifact acceptance. Control E owns publication.
