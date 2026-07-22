# v2.0.0 Day83 final release readiness fixed-zip gate with accepted Web evidence

```text
v200_final_release_readiness_fixed_zip_with_web_evidence_status: final-release-ready-fixed-zip-with-accepted-web-evidence
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day80_accepted_manifest: true
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day81_final_readiness: true
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day82_fixed_zip_verification: true
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_evidence_with_release_zip_for_acceptance: true
v200_final_release_readiness_fixed_zip_with_web_evidence_allows_inspection_only_mode: true
v200_final_release_readiness_fixed_zip_with_web_evidence_inspects_zip_as_is: true
v200_final_release_readiness_fixed_zip_with_web_evidence_creates_or_rebuilds_zip: false
v200_final_release_readiness_fixed_zip_with_web_evidence_marker_only_acceptance_allowed: false
v200_final_release_readiness_fixed_zip_with_web_evidence_zip_only_acceptance_allowed: false
```

Day83 is the final release readiness check for the exact fixed v2.0.0 zip that passed Day81 and Day82. It keeps the accepted private Web evidence rule active and independently reopens the same artifact rather than trusting Day82 marker JSON alone.

## Same-artifact rule

Day83 requires the same `$zip` path and SHA-256 recorded for Day82. It does not rebuild, modify, timestamp-refresh, rename, tag, or publish the artifact.

The Day83 smoke has three distinct modes:

```text
source-tree contract mode:
  no zip and no private evidence; validates only the implementation contract

inspection-only mode:
  --release-zip plus --inspect-zip-only; inspects the package but does not accept Day83

acceptance mode:
  --release-zip plus --evidence-json; both are required and must describe the same zip
```

A bare `--release-zip` invocation is rejected so package inspection cannot be mistaken for final readiness.

Artifact inspection:

```text
- runs scripts/check_release_package.py against the supplied file;
- opens the same zip directly and runs the CRC test;
- requires exactly one DailyRhythmCompanion package root;
- preserves every Day82 required-entry and forbidden-entry rule;
- additionally requires the Day83 final readiness doc, service, smoke script, and public example template;
- rejects operator evidence, worktree .git metadata, raw screenshots/audio/health data, secrets, tokens, private paths, LAN IPs, replacement bundles, caches, nested release outputs, and source-tree-only day scripts;
- hashes before and after inspection and rejects an artifact that changed.
```

## Required private evidence

The private Day83 marker evidence must confirm accepted Day80, Day81, and Day82 results, the recorded fixed zip path, same-zip inspection, no rebuild, accepted Web screenshot evidence, a public-safe release surface, and operator review. It must bind the current inspection values and the Day82-verified hash:

```text
fixed_release_zip_path
fixed_release_zip_name
fixed_release_zip_size_bytes
fixed_release_zip_sha256
day82_verified_release_zip_sha256
same_fixed_zip_used_for_day81_day82_day83
```

Raw private evidence remains outside the repository and release zip.

## Commands

Source-tree contract check before the artifact exists:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py
```

Optional package inspection after Day82, without final-readiness acceptance:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"

python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py `
  --release-zip $zip `
  --inspect-zip-only
```

Day83 readiness requires the same zip and the private marker JSON:

```powershell
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py `
  --release-zip $zip `
  --evidence-json "<private-Day83-marker-json>"
```

Day83 default source-tree checks do not call providers, Google Health, OAuth endpoints, backend APIs, Flutter Web, browsers, screenshot tools, GitHub, or external networks. Passing the source-tree check alone does not build the zip, accept Day83, create a tag, or release v2.0.0.

## G-7 immutable final artifact record handoff

Day83 requires the G-7 record doc, service, and smoke script in the same fixed zip. After Day83 passes, validate a public-safe final artifact record against that exact zip with `scripts/smoke_framework_v200_final_release_artifact_record.py`. Under the Public-P4 topology, the record must bind the full Public source HEAD, matching Public `main` and `origin/main`, the annotated tag target, exactly one Public root commit, the zip basename, size, and SHA-256; legacy `develop_head` fields are rejected.

No source or documentation commit may be created after the final fixed zip build. The validated record is copied unchanged into the annotated `DRC_v2.0.0` tag message and GitHub Release body. Private evidence, raw media/health data, secrets, LAN IPs, and private paths remain outside both the repository and release metadata.
