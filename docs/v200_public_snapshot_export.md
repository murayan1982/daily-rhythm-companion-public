# Daily Rhythm Companion v2.0.0 Public snapshot export

Status: **EXPORT TOOLING READY — CLEAN SNAPSHOT RE-EXPORT REQUIRED**
Release status: **NOT RELEASED**
Source of truth: `docs/DRC_v200_goal_checklist_small_commit.md`

## Purpose

Public-P3 adds one committed-HEAD exporter for the clean-history Public repository migration. The exporter reads only the committed Private repository tree, applies the same Public export policy used by Public-P2, validates the selected files strictly, and optionally writes one new snapshot outside the Private repository.

It does not copy `.git`, initialize a repository, build a release ZIP, create or move tags, publish GitHub content, read ignored operator evidence, or access the network.

## Files

```text
backend/app/services/framework_v200_public_snapshot_export.py
scripts/export_v200_public_snapshot_from_head.py
scripts/smoke_framework_v200_public_snapshot_export.py
```

## Pre-commit verification

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_public_distribution_readiness.py
python scripts\smoke_framework_v200_public_snapshot_export.py
```

The smoke test validates the current working Public export view without writing files. It also proves that an unfiltered `docs/internal/**` file or patch would be rejected by strict Public validation.

## Post-commit committed-HEAD validation

After Public-P3 is committed and pushed, validate the exact committed HEAD without writing a snapshot:

```powershell
$head = (git rev-parse HEAD).Trim()
python scripts\export_v200_public_snapshot_from_head.py `
  --validate-only `
  --expected-head $head
```

Required success markers include:

```text
v200_public_snapshot_selection_status: accepted
v200_public_snapshot_selection_required_files_present: True
v200_public_snapshot_selection_metadata_aligned: True
v200_public_snapshot_selection_public_safe: True
v200_public_snapshot_export_private_git_history_copied: False
v200_public_snapshot_export_ignored_files_read: False
v200_public_snapshot_export_write_status: not-written-validate-only
[export-v200-public-snapshot-from-head] OK
```

## One-time snapshot write

Choose a new directory outside the Private repository. The destination must not already exist.

```powershell
$head = (git rev-parse HEAD).Trim()
$publicDir = "E:\work\deverop\public_release\daily-rhythm-companion-public"

python scripts\export_v200_public_snapshot_from_head.py `
  --output-directory $publicDir `
  --expected-head $head
```

The exporter removes a partially written destination if validation or writing fails. A successful write is byte-compared with the validated committed selection and then inspected again in strict exported-directory mode.


## Public-P3.1 immutable verification correction

The first real export passed strict validation at 576 files, but later in-place verification changed that directory: Python bytecode generation increased it to 834 files, and Flutter dependency preparation increased it again to 838 files before the Flutter test stopped on the Windows Developer Mode requirement. That directory is therefore not the canonical Public source snapshot and must be discarded.

The corrected rule is:

```text
canonical export: never run write-producing verification commands inside it
disposable verification copy: compileall, Python smoke checks, and Flutter tests run here
post-verification: delete the disposable copy and strictly revalidate the untouched canonical export
```

Public-P3.1 adds explicit rejection for `__pycache__`, `.pyc`, `.pyo`, and existing Flutter generated directories.

## Independent strict directory check

Before initializing Git in the exported directory, run:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py `
  --source-directory $publicDir
```

This mode applies no Private-repository source exclusions. It ignores only `.git/**` repository metadata if the operator runs it again after initializing the new Public repository.


## Disposable runtime verification copy

Create a second export directory only for runtime verification. Keep Python bytecode outside that directory as an additional guard.

```powershell
$verifyDir = Join-Path $env:TEMP ("DRC_v200_public_verify_" + (Get-Date -Format "yyyyMMdd_HHmmss"))

python scripts\export_v200_public_snapshot_from_head.py `
  --output-directory $verifyDir `
  --expected-head $head

$env:PYTHONPYCACHEPREFIX = Join-Path $env:TEMP "drc_v200_public_pycache"

cd $verifyDir
python -m compileall -q backend scripts
python scripts\check_env_profile.py --profile mock-safe --env-path .\backend\env_profiles\mock_safe.env
python scripts\smoke_framework_v200_public_distribution_readiness.py --source-directory $verifyDir

cd app
flutter test
cd ..

Remove-Item Env:PYTHONPYCACHEPREFIX
```

Flutter plugin tests on Windows require Developer Mode or equivalent symlink permission. Enable it before rerunning the disposable-copy test. Generated files in the verification copy are expected and do not authorize copying that directory into the Public repository.

## Completion boundary

Public-P3 tooling readiness does not mean the snapshot has been exported or the Public repository exists. Completion still requires:

```text
committed Public-P3 HEAD validation
one clean snapshot write outside the Private repository
strict directory validation
new Public Git repository initialization
new authoritative Public source commit
one fixed ZIP built from that Public commit
Day82 and Day83 against the same ZIP
matching annotated DRC_v2.0.0 tag
GitHub Release using the same ZIP
```
