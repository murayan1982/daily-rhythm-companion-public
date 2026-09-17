# DRC v4.0.0 fixed release ZIP tooling

## Status

```text
Status:
CONTROL_E_RELEASE_AUTHORIZATION_SYNC_CORRECTIVE_R6 / IMPLEMENTED / STATIC_VERIFIED / SCHEMA_SELFCHECK_FILESYSTEM_INDEPENDENT / RAW_TOKEN_EXACT_MATCH_PRESERVED / ACTUAL_CONTRACT_PRECHECK_BEFORE_SCHEMA_VERIFIED / INVALID_CONTRACT_DOWNSTREAM_BLOCK_VERIFIED / MIDDLE_VERSION_SHADOW_HEADING_GUARD_PRESERVED / DEFAULT_RUNTIME_GUARD_CONNECTED / PUBLICATION_REACHABILITY_RUNTIME_VERIFIED / POST_SOURCE_MATRIX_0_TO_7_VERIFIED / HANDOFF_SELF_HASH_VERIFIED / CONTROL_E_NOT_RUN / NEW_THREAD_HANDOFF_CREATED / READY_FOR_RE_REVIEW

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
CONSUMED / FAILED

Control E:
NOT_AUTHORIZED

builder invocation count:
1

fixed ZIP:
release/DailyRhythmCompanion_v4.0.0_20260908_173440.zip

release source HEAD:
46f5af49106c6ecc0d478a425cf709cf511da1be

verification HEAD:
f1de9f527c8a01d7c75f7a8cfef274cf32ac74ef

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


Control D Stage 4 authorization-sync is COMMITTED / PUSHED / REVIEWED / ACCEPTED / CLOSED at `0a6e6e65f8c775022471018bc3ca6c03b2ed588b`. Stage 4 invocation 1 was EXACTLY_ONCE_EXECUTED and ended EXECUTION_FAILED before a verification verdict; verdict is NOT_REACHED and failure class is NON_PRODUCT_VERIFIER_OUTPUT_ENCODING_FAILURE. Stage 4 invocation 2 was EXACTLY_ONCE_EXECUTED and ended EXECUTION_FAILED with NON_PRODUCT_VERIFIER_PYTEST_BASETEMP_PERMISSION_FAILURE after Backend pytest reported 272 passed / 207 setup errors from PermissionError / WinError 5 on pytest default shared user TEMP root. Release-package scanner known fixtures were EXACT_EXPECTED_FINDINGS / ACCEPTED, ZIP structural/version checks reached before failure were PASS, extracted compileall was PASS, and extracted Backend pytest was PROCESS_COMPLETED / EXIT_CODE_NOT_RECORDED / PASS_COUNT_NOT_RECORDED. Stage 4 authorization marker was consumed. The fixed ZIP is PRESERVED and must not be deleted, renamed, overwritten, regenerated, or retried. Stage 4 retry is CONSUMED / FAILED, Control E is authorized for exactly one not-run publication, tag/publication are NOT_RUN, and DRC v4.0.0 is NOT_RELEASED.

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
`release`, output basename, size, SHA-256, and source HEAD, leave verification status `not-run`, and clean temporary state even on failure. It must refuse
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

Mode dispatch is strict. Default dirty mode validates the exact Control D Stage 4 verifier output-encoding corrective M12 candidate surface, requires exactly one fixed ZIP artifact, and matches its basename, size, SHA-256, and source HEAD against the recorded tuple. Current docs must contain zero Stage 4 same-artifact authorization markers and zero Stage 3 one-time build authorization tokens. Stage 4 invocation 1 executed and failed before verdict; retry budget is consumed and Invocation 3 authorization is consumed and the release-ZIP verifier remains unreachable in default corrective mode. Control E is authorized for exactly one not-run publication. DRC v4.0.0 remains not released. Source-tree mode is mutually exclusive with release-ZIP mode and requires Control D Stage 2 accepted state before clean committed source/runtime preflight. Release-ZIP mode is mutually exclusive with source-tree mode and verifies the exact supplied artifact instead of applying the source-tree artifact gate.

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

## Stage 4 Verifier Output-Encoding Corrective R1 Stop Rule

Stage 4 authorization-sync stops as a dirty exact candidate for external diff
review. The current dirty R5 candidate does not stage, commit, push, invoke
`--release-zip`, rerun the builder, run another Control D Stage 2 source-tree
preflight, build or replace a fixed ZIP, package, tag, create a GitHub Release,
publish, authorize Control E, or clean release artifacts.
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