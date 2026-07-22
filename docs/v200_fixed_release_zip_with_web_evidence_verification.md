# v2.0.0 Day82 fixed release zip verification with accepted Web evidence

```text
v200_fixed_release_zip_with_web_evidence_status: fixed-release-zip-with-accepted-web-evidence-verification-ready
v200_fixed_release_zip_with_web_evidence_requires_day81_final_readiness: true
v200_fixed_release_zip_with_web_evidence_requires_evidence_with_release_zip_for_acceptance: true
v200_fixed_release_zip_with_web_evidence_allows_inspection_only_mode: true
v200_fixed_release_zip_with_web_evidence_inspects_zip_as_is: true
v200_fixed_release_zip_with_web_evidence_creates_or_rebuilds_zip: false
v200_fixed_release_zip_with_web_evidence_marker_only_acceptance_allowed: false
v200_fixed_release_zip_with_web_evidence_zip_only_acceptance_allowed: false
```

Day82 verifies one fixed release zip after all capability evidence, the ignored Day80 private evidence manifest, and Day81 readiness are accepted. Commit G-6 hardens both sides of this handoff before the final artifact is built. The Public pre-build follow-up separates package inspection from Day82 acceptance and removes the circular `release_zip_built_once_after_day81` marker.

## Build and verification sequence

The active order is:

```text
1. Confirm the accepted Day80 manifest outside the Public repository.
2. Commit and push the final Public source.
3. Verify clean Public main and freeze the source.
4. Build one fixed zip exactly once from that committed Public source.
5. Run Day81 against that fixed zip.
6. Run Day82 against the same zip with private Day82 evidence.
7. Run Day83 against the same zip with private Day83 evidence.
```

Day82 evidence must assert that the zip was built once from the final committed Public source and before Day82. It must not assert that the zip was built after Day81.

## Build-once source rule

Use `build_v200_final_fixed_release_zip_from_head.ps1` only after the final Public source is committed and pushed and the source-tree and Flutter checks pass. The builder:

```text
- requires a clean tracked/non-ignored working tree;
- validates committed public-safe acceptance markers;
- validates the accepted Day80 manifest without copying it;
- records the current branch and committed HEAD;
- creates a detached temporary Git worktree at that exact HEAD;
- invokes build_release.bat release exactly once inside that worktree;
- explicitly excludes the worktree `.git` metadata file from package copying and sanitization;
- refuses to overwrite an existing release artifact;
- moves the single created zip to release/;
- prints the repository-relative path, source HEAD, byte size, and SHA-256;
- removes the temporary worktree after the build.
```

The builder does not verify or accept Day81, Day82, or Day83. Its output explicitly leaves verification as `not-run`.

## Direct same-zip verification

The Day82 smoke has three distinct modes:

```text
source-tree contract mode:
  no zip and no private evidence; validates only the implementation contract

inspection-only mode:
  --release-zip plus --inspect-zip-only; inspects the package but does not accept Day82

acceptance mode:
  --release-zip plus --evidence-json; both are required and must describe the same zip
```

A bare `--release-zip` invocation is rejected so package inspection cannot be mistaken for Day82 acceptance.

Artifact inspection performs these checks:

```text
- runs scripts/check_release_package.py against the supplied file;
- opens the zip directly without rebuilding;
- runs the zip CRC test;
- requires exactly one DailyRhythmCompanion package root;
- rejects unsafe, duplicate, outside-root, or malformed entries;
- rejects a packaged worktree `.git` metadata file;
- verifies every required public release entry;
- rejects operator_evidence, private evidence, raw screenshot/audio/health paths, local/release/cache paths, replacement bundles, and source-tree-only day check scripts;
- records the zip basename, entry count, byte size, and SHA-256;
- hashes the artifact before and after inspection and rejects changes during verification.
```

Evidence-backed acceptance additionally requires the private Day82 markers to bind these exact inspected values:

```text
fixed_release_zip_path
fixed_release_zip_name
fixed_release_zip_size_bytes
fixed_release_zip_sha256
```

Public files may describe private evidence through redacted references such as `private-operator-evidence://...`, but raw private artifacts must never be included.

## Commands

Before building:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py

cd app
flutter test
cd ..
```

Build once from committed HEAD, record the exact printed path, and run Day81 against that path before Day82.

Optional package inspection without acceptance:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"

python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py `
  --release-zip $zip `
  --inspect-zip-only
```

Day82 acceptance requires both the same zip and the private marker JSON:

```powershell
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py `
  --release-zip $zip `
  --evidence-json "<private-Day82-marker-json>"
```

Do not run the builder again during Day81, Day82, or Day83. If committed source, documentation, evidence rules, or release surface changes after artifact creation, discard the old artifact and perform one new build from the new committed HEAD, then restart fixed-zip verification.

Day82 default source-tree checks do not call LLM providers, TTS providers, Google Health, OAuth endpoints, backend APIs, Flutter Web, browser automation, screenshot tools, GitHub, or external network services. They do not build, modify, or timestamp-refresh a release zip.

## G-7 immutable artifact-record release surface

Commit G-7 adds the public-safe final artifact record contract to the required Day82 release surface:

```text
docs/v200_final_release_artifact_record.md
backend/app/services/framework_v200_final_release_artifact_record.py
scripts/smoke_framework_v200_final_release_artifact_record.py
```

Any zip built before G-7 is committed is not the final v2.0.0 artifact because the required release surface changed. After G-7 is committed and `main` and `develop` point to the same HEAD, build one new fixed zip and restart Day82/Day83 verification. Do not update source files after that build; record the accepted artifact outcome in the annotated tag and GitHub Release metadata instead.
