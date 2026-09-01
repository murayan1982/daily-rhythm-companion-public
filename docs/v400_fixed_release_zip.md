# DRC v4.0.0 fixed release ZIP tooling

## Status

```text
Status:
FIXED_ZIP_TOOLING / IMPLEMENTED / AWAITING_REVIEW

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

builder invocation count:
0

fixed ZIP:
NOT_BUILT

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

annotated tag:
NOT_CREATED

GitHub Release:
NOT_CREATED
```

## Stage 1 Boundary

Stage 1 implements credential-free, provider-free, private-evidence-free fixed
ZIP tooling only. It does not read credentials, tokens, private paths, LAN
values, audio, transcripts, provider payloads, operator evidence, local
databases, or generated build outputs.

Stage 1 completion does not approve Stage 2, Stage 3, Stage 4, Control E,
package creation, tag creation, GitHub Release creation, or publication.

`-PreflightOnly` must not create a worktree, run `build_release.bat`, create a
generic ZIP, create a fixed ZIP, create a tag, or publish. It must report
builder invocation count `0`.

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

The actual build path is permitted only when a future committed document adds
the tooling-defined Stage 3 one-time-build authorization marker. This Stage 1
document intentionally does not spell that marker token.

When authorized in the future, actual build must create a detached temporary
worktree from exact committed HEAD, verify that worktree HEAD, run
`build_release.bat release` exactly once, carry forward only the generic
timestamp, move the final ZIP to `release`, output basename, size, SHA-256, and
source HEAD, leave verification status `not-run`, and clean temporary state
even on failure. It must refuse silent rebuild, overwrite, or replacement.

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
default: Stage 1 dirty candidate or clean committed tooling static gate
--source-tree: future clean committed main no-artifact preflight
--release-zip: future same fixed ZIP verification
```

The verifier must not invoke the builder. The release ZIP verifier must verify
only the supplied fixed ZIP and must remain inert unless a future committed
document adds the tooling-defined Stage 4 same-artifact authorization marker.
This Stage 1 document intentionally does not spell that marker token.

Release ZIP verification must not mutate the ZIP and must keep release source
HEAD, verification HEAD, and artifact SHA-256 separate.

Mode dispatch is strict. Default mode validates only Stage 1 current-state
documentation, authorization-marker absence, fixed ZIP absence, blocked future
authorization, and exact dirty/clean Stage 1 static checks. Source-tree mode is
mutually exclusive with release-ZIP mode and requires Control D Stage 2
authorization or accepted state before clean committed source/runtime preflight.
Release-ZIP mode is mutually exclusive with source-tree mode and verifies the
exact supplied artifact instead of applying the absent-artifact gate.

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

Flutter checks from an extracted ZIP use the explicit absolute Flutter command.
If `app/.dart_tool/package_config.json` is absent in the temporary extraction,
the verifier may run `flutter pub get --offline` only inside that temporary
extracted tree, then requires the package config to exist before
`flutter analyze --no-pub`, `flutter test --no-pub`, and optional build checks.
Repository source-tree mode does not run `flutter pub get`.

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

## Stage 1 Stop Rule

Stage 1 stops as a dirty exact candidate for external diff review. It does not
stage, commit, push, run Control D Stage 2, run Control D Stage 3, run Control D
Stage 4, build a fixed ZIP, package, tag, create a GitHub Release, publish, or
clean release artifacts.
