# v2.0.0 immutable final release artifact record

```text
v200_final_release_artifact_record_status: immutable-final-release-artifact-record-ready
v200_final_release_artifact_record_requirement_key: v200_final_release_artifact_record
v200_final_release_artifact_record_release_target: v2.0.0
v200_final_release_artifact_record_tag_name: DRC_v2.0.0
v200_final_release_artifact_record_locations: annotated-git-tag-message,github-release-body
```

Commit G-7 closes the process gap between the last committed source state and the artifact that can only exist after that commit. It does not treat a post-build documentation commit as part of the release. Instead, the final committed source remains immutable after the one-time build, and the public-safe artifact outcome is recorded in both the annotated `DRC_v2.0.0` tag message and the GitHub Release body.


## Public repository migration override

The G-7 contract above was designed for a release completed inside the same repository whose `main`, `develop`, tag target, and fixed-zip source all share one commit SHA. Public-P0 introduces a different topology: the existing development repository remains Private and a new Public repository is initialized from a clean snapshot without Private Git history.

A clean snapshot receives a new commit SHA. Consequently:

```text
- The previously verified Private-repository candidate artifact record is historical only.
- The Private candidate zip and annotated tag must not be reused for the Public release.
- The new Public repository commit becomes the authoritative release source_head.
- The final Public fixed zip must be built from that committed Public source.
- The Public annotated DRC_v2.0.0 tag must target that same Public source_head.
- Day82, Day83, the artifact-record validator, and GitHub Release must all bind the same new Public zip.
- Raw or ignored Private evidence must not be copied into the Public repository merely to satisfy a builder preflight.
```

Until the code-level artifact-record and builder contracts are updated for this clean-history topology, the current G-7 validator remains useful as historical same-repository coverage but does not authorize the new Public release.

## Why the record is outside a post-build source commit

The fixed-zip rule requires a new artifact whenever committed source, documentation, evidence rules, or release surface changes. Updating the checklist after a successful build would therefore invalidate the artifact it described. G-7 resolves that cycle before the final build:

```text
- Commit G-7 first.
- Align main and develop to the same committed G-7 HEAD.
- Build one new fixed zip from that exact committed HEAD.
- Verify Day82 and Day83 against that same zip without rebuilding.
- Do not make a post-build source or documentation commit.
- Put the validated public-safe artifact record in the annotated tag message.
- Copy the same record into the GitHub Release body and attach the same zip.
```

The committed checklist remains the source of truth for requirements and release procedure. The annotated tag and GitHub Release metadata are the immutable public record of the final post-build outcome.

## Required public-safe fields

```text
status: accepted
release_target: v2.0.0
record_kind: final_release_artifact_record
source_head: full 40-character lowercase commit SHA
develop_head: same source_head
main_head: same source_head
tag_name: DRC_v2.0.0
tag_target_head: same source_head
tag_object_type: annotated
release_zip_name: basename only
release_zip_size_bytes: positive integer
release_zip_sha256: full lowercase SHA-256
```

Required accepted markers:

```text
day80_accepted_manifest_passed: true
day82_fixed_zip_verification_passed: true
day83_final_release_readiness_passed: true
fixed_zip_inspected_as_is: true
main_and_develop_match_source_head: true
annotated_tag_targets_source_head: true
github_release_same_fixed_zip_required: true
operator_review_accepted: true
```

Required false markers:

```text
fixed_zip_rebuilt_after_verification: false
source_changed_after_fixed_zip_build: false
private_evidence_included: false
raw_screenshots_included: false
raw_audio_included: false
raw_health_data_included: false
raw_provider_payloads_included: false
api_keys_included: false
oauth_tokens_included: false
authorization_headers_included: false
private_paths_included: false
raw_lan_ips_included: false
```

The record must contain the zip basename only. Do not put absolute paths, LAN IPs, private screenshot references, operator-evidence paths, provider payloads, tokens, or credentials in tag or release metadata.

## Source-tree verification

Before committing G-7:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_release_artifact_record.py

cd app
flutter test
cd ..
```

The source-tree smoke checks an accepted synthetic record, rejects representative hash, branch, tag, private-path, and post-build-source-change cases, and verifies that Day82 and Day83 require the G-7 release-surface files.

## Final same-artifact validation

After the new committed G-7 HEAD produces one fixed zip and the same zip passes Day82 and Day83, prepare a public-safe record object and validate it against that artifact. The actual final command must use the real full commit SHA, zip basename, byte size, SHA-256, and branch/tag values.

```powershell
$record = @{
    status = "accepted"
    release_target = "v2.0.0"
    record_kind = "final_release_artifact_record"
    source_head = $head
    develop_head = $developHead
    main_head = $mainHead
    tag_name = "DRC_v2.0.0"
    tag_target_head = $tagTargetHead
    tag_object_type = "annotated"
    release_zip_name = (Split-Path $zip -Leaf)
    release_zip_size_bytes = $zipSize
    release_zip_sha256 = $zipHash
    day80_accepted_manifest_passed = $true
    day82_fixed_zip_verification_passed = $true
    day83_final_release_readiness_passed = $true
    fixed_zip_inspected_as_is = $true
    main_and_develop_match_source_head = $true
    annotated_tag_targets_source_head = $true
    github_release_same_fixed_zip_required = $true
    operator_review_accepted = $true
    fixed_zip_rebuilt_after_verification = $false
    source_changed_after_fixed_zip_build = $false
    private_evidence_included = $false
    raw_screenshots_included = $false
    raw_audio_included = $false
    raw_health_data_included = $false
    raw_provider_payloads_included = $false
    api_keys_included = $false
    oauth_tokens_included = $false
    authorization_headers_included = $false
    private_paths_included = $false
    raw_lan_ips_included = $false
} | ConvertTo-Json -Compress

python scripts\smoke_framework_v200_final_release_artifact_record.py `
  --release-zip $zip `
  --record-json $record
```

The validator directly reopens the supplied Day83 release surface, checks package hygiene, CRC, required and forbidden entries, and binds the record's zip name, size, and SHA-256 to the inspected artifact. It does not create the tag, move branches, publish GitHub Release, rebuild the zip, or use the network.
