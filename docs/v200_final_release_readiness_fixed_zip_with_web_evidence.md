# v2.0.0 Day83 final release readiness fixed-zip gate with accepted Web evidence

```text
v200_final_release_readiness_fixed_zip_with_web_evidence_status: final-release-ready-fixed-zip-with-accepted-web-evidence
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day80_accepted_manifest: true
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day81_final_readiness: true
v200_final_release_readiness_fixed_zip_with_web_evidence_requires_day82_fixed_zip_verification: true
v200_final_release_readiness_fixed_zip_with_web_evidence_inspects_zip_as_is: true
v200_final_release_readiness_fixed_zip_with_web_evidence_creates_or_rebuilds_zip: false
v200_final_release_readiness_fixed_zip_with_web_evidence_marker_only_acceptance_allowed: false
```

Day83 is the final release readiness check for the exact fixed v2.0.0 zip that passed Day82. It keeps the accepted private Web evidence rule active and independently reopens the same artifact rather than trusting Day82 marker JSON alone.

## Same-artifact rule

Day83 requires the same `$zip` path recorded by the one-time committed-HEAD builder and passed to Day82. It does not rebuild, modify, timestamp-refresh, rename, tag, or publish the artifact.

With `--release-zip`, Day83:

```text
- runs scripts/check_release_package.py against the supplied file;
- opens the same zip directly and runs the CRC test;
- requires exactly one DailyRhythmCompanion package root;
- preserves every Day82 required-entry and forbidden-entry rule;
- additionally requires the Day83 final readiness doc, service, smoke script, and public example template;
- rejects operator evidence, worktree .git metadata, raw screenshots/audio/health data, secrets, tokens, private paths, LAN IPs, replacement bundles, caches, nested release outputs, and source-tree-only day scripts;
- hashes before and after inspection and rejects an artifact that changed;
- rejects `--evidence-json` when no `--release-zip` is supplied.
```

## Required private evidence

The private Day83 marker evidence must confirm accepted Day80, Day81, and Day82 results, the recorded fixed zip path, same-zip inspection, no rebuild, accepted Web screenshot evidence, a public-safe release surface, and operator review. Raw private evidence remains outside the repository and release zip.

## Commands

Source-tree contract check before the artifact exists:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py
```

After Day82 passes, reuse the same path:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"

python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py --release-zip $zip
```

Private marker validation, when authored, must accompany the same zip:

```powershell
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py `
  --release-zip $zip `
  --evidence-json "<private-Day83-marker-json>"
```

Day83 default source-tree checks do not call providers, Google Health, OAuth endpoints, backend APIs, Flutter Web, browsers, screenshot tools, GitHub, or external networks. Passing the source-tree check alone does not build the zip, create a tag, or release v2.0.0.

## G-7 immutable final artifact record handoff

Day83 now requires the G-7 record doc, service, and smoke script in the same fixed zip. After Day83 passes, validate a public-safe final artifact record against that exact zip with `scripts/smoke_framework_v200_final_release_artifact_record.py`. The record must bind the full source HEAD, matching `main` and `develop` refs, annotated tag target, zip basename, size, and SHA-256.

No source or documentation commit may be created after the final fixed zip build. The validated record is copied unchanged into the annotated `DRC_v2.0.0` tag message and GitHub Release body. Private evidence, raw media/health data, secrets, LAN IPs, and private paths remain outside both the repository and release metadata.
