# Daily Rhythm Companion v4.0.0 release record

## Header State

```text
Status:
PREPARED / NOT_RELEASED

Current phase:
Control B IMPLEMENTED / AWAITING_REVIEW

release version:
v4.0.0

Backend APP_VERSION:
4.0.0

Flutter package version:
4.0.0+5

planned annotated tag:
DRC_v4.0.0

planned GitHub Release title:
Daily Rhythm Companion v4.0.0

current published release:
v3.0.0 RELEASED / ACCEPTED

Control A accepted commit:
b752491632c58c557c02b06587cab28edcb901ca

Control B implementation baseline:
b752491632c58c557c02b06587cab28edcb901ca
```

## Release Tuple

```text
release source HEAD:
NOT_RECORDED

verification HEAD:
NOT_RECORDED

fixed ZIP basename:
NOT_BUILT

fixed ZIP size:
NOT_RECORDED

fixed ZIP SHA-256:
NOT_RECORDED

fixed ZIP builder invocation count:
0

same-artifact verification:
NOT_COMPLETED

release-package hygiene:
NOT_COMPLETED

ZIP CRC/single-package-root verification:
NOT_COMPLETED

extracted ZIP Backend verification:
NOT_RUN

extracted ZIP Flutter verification/builds:
NOT_RUN

verifier rebuilt artifact:
false

explicit final operator approval:
NOT_RECEIVED

annotated tag publication:
NOT_CREATED

GitHub Release publication:
NOT_CREATED

post-publication downloaded asset:
NOT_DOWNLOADED

post-publication SHA-256 verification:
NOT_COMPLETED
```

Do not invent artifact names, source HEADs, verification HEADs, sizes, hashes,
tag objects, URLs, final approval dates, or publication results.

## Artifact Invalidation Rule

If a source-affecting correction is required after a future fixed ZIP is built,
that accepted artifact is invalidated and cannot silently remain the release
artifact.

If a future correction is verifier-only and does not change frozen release
source, the record must keep these separately:

```text
release source HEAD
verification HEAD
artifact SHA-256
```

Do not blur them into one generic HEAD.
