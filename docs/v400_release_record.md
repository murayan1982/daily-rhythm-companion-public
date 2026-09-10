# Daily Rhythm Companion v4.0.0 release record

## Header State

```text
Status:
PREPARED / NOT_RELEASED

Current phase:
Control D Stage 4 Authorization Sync STAGE4_AUTHORIZATION_SYNC / IMPLEMENTED / AWAITING_REVIEW

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

Control B implementation commit:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Control C verification baseline:
5908cb5b0d88c2e8aa6370105c3d618064cb4665

Control C implementation commit:
4cae15573f3332cbc476557461babdfe2eb3c0bf

Control C:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

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
```

## Release Tuple

```text
release source HEAD:
46f5af49106c6ecc0d478a425cf709cf511da1be

verification HEAD:
NOT_RECORDED

fixed ZIP basename:
DailyRhythmCompanion_v4.0.0_20260908_173440.zip

fixed ZIP size:
3018230 bytes

fixed ZIP SHA-256:
F02B43A219D7E89FD9E40DD6C1F7CD588076DE7B260D6085FFA99966B3C49142

fixed ZIP builder invocation count:
1

same-artifact verification:
AUTHORIZED / NOT_RUN

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

Control C verification:
COMPLETED / VERIFIED / REVIEWED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Backend FW-v6 focused:
62 PASS

Backend v3 realtime preservation:
29 PASS

Backend full:
479 PASS

Flutter analyze:
PASS / No issues found

Flutter FW-v6 focused:
70 PASS

Flutter v3 realtime preservation:
328 PASS

Flutter full:
570 PASS

Flutter SDK startup issue:
NON_PRODUCT_ENVIRONMENT_FAILURE / RESOLVED

initial Flutter FW-v6 focused timeout:
NON_PRODUCT_COMPLETION_TIMEOUT / RESOLVED_BY_CORRECTIVE_RERUN

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


Control D Stage 4 authorization-sync status: IMPLEMENTED / AWAITING_REVIEW. Stage 3 fixed ZIP build is COMPLETED / PASS / ACCEPTED, the artifact tuple is RECORDED, Stage 4 same-artifact verification is AUTHORIZED / NOT_RUN, Control E is NOT_AUTHORIZED, tag/publication are NOT_RUN, and DRC v4.0.0 is NOT_RELEASED. Stage 3 builder rerun is forbidden; the fixed ZIP must not be deleted, renamed, overwritten, or regenerated. Stage 4 authorization-sync candidate cannot run release-zip verifier until reviewed, accepted, committed, and pushed. After commit/push, Stage 4 verifier still needs separate explicit approval. Verification HEAD remains NOT_RECORDED until Stage 4 execution acceptance-sync.
