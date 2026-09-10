# DRC v4.0.0 fixed release ZIP tooling

## Status

```text
Status:
STAGE4_AUTHORIZATION_SYNC / IMPLEMENTED / AWAITING_REVIEW

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

Control D Stage 2:
CLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED / COMMITTED / PUSHED / CLOSED

Control D Stage 2 acceptance-sync commit:
697d0918cb8a6de5c0459324464b7d7e376b3a5a

Control D Stage 3:
BUILD_EXACTLY_ONCE / COMPLETED / PASS / ACCEPTED

Control D Stage 4 authorization:
AUTHORIZED_FOR_SAME_ARTIFACT_VERIFICATION

Control D Stage 4:
SAME_ARTIFACT_VERIFICATION_AND_TUPLE_RECORD / AUTHORIZED / NOT_RUN

Control E:
NOT_AUTHORIZED

builder invocation count:
1

fixed ZIP:
release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip

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

annotated tag:
NOT_CREATED

GitHub Release:
NOT_CREATED
```

## Stage 2 Accepted Source Preflight

Stage 1 implemented credential-free, provider-free, private-evidence-free fixed
ZIP tooling and was accepted, committed, pushed, and closed at
`a204f6b11d25baeea67b7b7be8860c9a4f9ea945`.

Stage 2 clean committed source preflight completed, passed, and is accepted at
source HEAD `eb68cf9334f46a30c0c06d3921d59f56abb540bb`. The accepted preflight
used exactly one source-tree verifier invocation, exited `0`, and elapsed
`00:05:08.0615422`.

```text
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

At the Stage 2 checkpoint, Stage 2 acceptance was committed, pushed, and
closed, and Stage 3 was authorized for exactly one fixed ZIP build. That
historical Stage 3 authorization has now been consumed by the accepted Stage 3
build. It does not approve another Stage 3 build, Stage 4 execution, Control E,
package creation, tag creation, GitHub Release creation, or publication.

`-PreflightOnly` must not create a worktree, run `build_release.bat`, create a
generic ZIP, create a fixed ZIP, create a tag, or publish. It must report
builder invocation count `0`.


Stage 3 fixed ZIP build completed, passed, and is accepted. The Stage 3 one-time build authorization is consumed; Stage 3 builder rerun is forbidden. The fixed ZIP must not be deleted, renamed, overwritten, or regenerated. Stage 4 verifies only the same basename, size, SHA-256, and release source HEAD recorded here. Stage 4 authorization-sync candidate cannot run release-zip verifier until reviewed, accepted, committed, and pushed. After commit/push, Stage 4 verifier still needs separate explicit approval. Stage 4 verifier does not call the builder; failure does not rebuild. Verification HEAD remains NOT_RECORDED until Stage 4 execution acceptance-sync. DRC v4.0.0 remains NOT_RELEASED, the DRC_v4.0.0 tag is NOT_CREATED, GitHub Release is NOT_CREATED, and Control E is NOT_AUTHORIZED.

## Builder Contract

The v4 one-time builder is:

```text
build_v400_fixed_release_zip_from_head.ps1
```

Parameters:

```text
OutputDirectory: default release
PythonCommand: default python
FlutterCommand: mandatory absolute command path
PreflightOnly: switch
```

The builder must reject bare `flutter` and must not fall back to PATH lookup.
Repository documentation must not record machine-specific absolute paths; use a
placeholder such as `<ABSOLUTE_FLUTTER_COMMAND>`.

Common preconditions:

```text
repository root: official repository root
origin: murayan1982/daily-rhythm-companion-public
branch: main
working tree: clean
HEAD == origin/main
root commit count: 1
DRC_v2.0.0 annotated tag: present
DRC_v2.0.1 annotated tag: present
DRC_v2.1.0 annotated tag: present
DRC_v3.0.0 annotated tag: present
DRC_v4.0.0 tag: absent
release/DailyRhythmCompanion_v4.0.0_*.zip: absent
output directory: release
overwrite: forbidden
```

`-PreflightOnly` invokes only:

```text
python scripts\check_v400_fixed_release_zip.py --source-tree --with-flutter --with-builds --flutter-command <ABSOLUTE_FLUTTER_COMMAND>
```

The actual build path was authorized by the then-current accepted Stage 3
document marker, and only for one fixed ZIP build. That build completed, passed,
and is accepted; the builder must not be rerun.



The authorized one-time build must create a detached temporary worktree from
exact committed HEAD, verify that worktree HEAD, run `build_release.bat release`
exactly once, carry forward only the generic timestamp, move the final ZIP to
`release`, output basename, size, SHA-256, and source HEAD, leave verification
status `not-run`, and clean temporary state even on failure. It must refuse
silent rebuild, overwrite, or replacement.

The fixed basename must be:

```text
DailyRhythmCompanion_v4.0.0_<YYYYMMDD_HHMMSS>.zip
```

## Verifier Contract

The v4 verifier is:

```text
scripts/check_v400_fixed_release_zip.py
```

Modes:

```text
default: Stage 4 authorization-sync dirty candidate or exact clean committed authorization static gate
--source-tree: authorized clean committed main no-artifact preflight
--release-zip: committed/pushed Stage 4 same-artifact verification path, still requiring separate explicit execution approval
```

The verifier must not invoke the builder.

Release ZIP verification must not mutate the ZIP and must keep release source
HEAD, verification HEAD, and artifact SHA-256 separate.

Mode dispatch is strict. Default dirty mode validates the exact Control D Stage 4
authorization-sync M12 candidate surface, requires exactly one fixed ZIP
artifact, and matches its basename, size, SHA-256, and source HEAD against the
recorded tuple. Current docs must contain exactly two Stage 4 authorization
markers and zero Stage 3 one-time build authorization tokens. Stage 4
same-artifact verification is authorized but not run; the release-ZIP verifier
remains unreachable until the Stage 4 authorization-sync is clean, committed,
and pushed. Control E remains not authorized. Source-tree mode is mutually
exclusive with release-ZIP mode and requires Control D Stage 2 accepted state
before clean committed source/runtime preflight. Release-ZIP mode is mutually
exclusive with source-tree mode and verifies the exact supplied artifact instead
of applying the source-tree artifact gate.

The release-ZIP verifier applies `scripts/check_release_package.py` without
weakening the generic scanner. The only tolerated scanner findings are known
fixtures whose ZIP members exactly match the expected source HEAD Git blobs and
contain their required marker bytes; unexpected findings, missing fixtures,
duplicate findings, fixture content mismatch, and fixture marker absence are
rejected.

For the current v4 source, the generic scanner result is intentionally fixed to
exit code `1`, first non-empty line `[release-package-check] NG`, and exactly
two findings for:

```text
backend/tests/test_v300_rt8_private_operator_manifest.py
scripts/check_v300_rt4f4_configured_local_stream_acceptance.py
```

Scanner exit `0`, sanitized or missing fixtures, modified fixtures, source
mismatch, duplicate findings, unexpected findings, and missing findings are all
rejected. The fixture files are required package files so fixture verification
cannot be skipped by omission.

The ZIP metadata identity check validates
`DailyRhythmCompanion/backend/app/version.py` and
`DailyRhythmCompanion/app/pubspec.yaml` from the ZIP itself. Both members must
match the expected source HEAD Git blobs after CRLF and standalone CR
normalization. Backend active version must be exactly `4.0.0`, Flutter active
version must be exactly `4.0.0+5`, duplicate active version declarations are
rejected, and ZIP/source mismatch is rejected.

Flutter checks from a repository source tree or extracted ZIP use the explicit
absolute Flutter command with the shared expanded reporter helper:

```text
<ABSOLUTE_FLUTTER_COMMAND>
test
--no-pub
--reporter
expanded
```

Flutter checks from an extracted ZIP use the explicit absolute Flutter command.
If `app/.dart_tool/package_config.json` is absent in the temporary extraction,
the verifier may run `flutter pub get --offline` only inside that temporary
extracted tree, then requires the package config to exist before
`flutter analyze --no-pub`, `flutter test --no-pub --reporter expanded`, and
optional build checks. Repository source-tree mode does not run
`flutter pub get`.

The same dependency-plan helper is used by source-tree and extracted-tree
verification. Repository source tree with package config uses the existing
config; repository source tree without package config rejects without pub get.
Temporary extraction with package config uses the existing config; temporary
extraction without package config runs only offline pub get.

Artifact invalidation is enforced when verification HEAD differs from expected
source HEAD. Only zero commits or a bounded verifier-only corrective sequence is
allowed after expected source HEAD. Product/runtime/test/dependency/build
source, release notes, version metadata, builder changes, delete/rename/copy
changes, and broad unreviewed surfaces invalidate the artifact.

## Package Exclusions

The public package must exclude credentials, tokens, private paths, LAN values,
audio, transcripts, provider payloads, operator evidence, local databases/data,
generated build outputs, vendor directories, nested ZIP files, `.git`, and
`release`.

AI Character Framework is not bundled.

## Artifact Invalidation

After a source-affecting corrective, any existing artifact is invalidated. A
verifier-only corrective may be recorded only by keeping release source HEAD,
verification HEAD, and artifact SHA-256 distinct.

## Stage 4 Authorization-Sync Stop Rule

Stage 4 authorization-sync stops as a dirty exact candidate for external diff
review. The current dirty R5 candidate does not stage, commit, push, invoke
`--release-zip`, rerun the builder, run another Control D Stage 2 source-tree
preflight, build or replace a fixed ZIP, package, tag, create a GitHub Release,
publish, authorize Control E, or clean release artifacts.
