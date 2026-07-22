# v2.0.0 immutable final release artifact record

```text
v200_final_release_artifact_record_status: immutable-final-release-artifact-record-ready
v200_final_release_artifact_record_requirement_key: v200_final_release_artifact_record
v200_final_release_artifact_record_release_target: v2.0.0
v200_final_release_artifact_record_tag_name: DRC_v2.0.0
v200_final_release_artifact_record_repository_topology: clean_history_public_snapshot
v200_final_release_artifact_record_public_repository: murayan1982/daily-rhythm-companion-public
v200_final_release_artifact_record_locations: annotated-git-tag-message,github-release-body
```

## Public-P4 clean-history topology

The final Public release is produced from the clean-history repository:

```text
murayan1982/daily-rhythm-companion-public
```

The existing Private development repository remains Private and is not the
release source. Its commit IDs, refs, tags, history, ignored evidence, raw
screenshots, raw audio, health payloads, provider payloads, credentials,
private paths, and LAN IPs are not copied into the Public artifact record.

The authoritative release relationship is:

```text
Public main HEAD
  == fixed ZIP source_head
  == annotated DRC_v2.0.0 tag target
```

The Public repository must have exactly one root commit. It may contain more
than one normal Public preparation commit before the release tag, but it must
not contain the Private repository history.

The obsolete same-repository relationship is not accepted:

```text
source_head == main_head == develop_head
```

`develop_head` and `main_and_develop_match_source_head` must not appear in the
clean-history Public artifact record.

## Why the record is outside a post-build source commit

The fixed-ZIP rule requires a new artifact whenever committed source,
documentation, evidence rules, or the release surface changes. Updating a
tracked document after a successful build would invalidate the artifact it
described.

The final sequence is therefore:

```text
1. Commit and push the last Public source change.
2. Confirm Public main, origin/main, and source_head are identical.
3. Confirm the Public repository has exactly one root commit.
4. Build one fixed ZIP from that committed Public source.
5. Run Day82 and Day83 against the same ZIP without rebuilding.
6. Validate the public-safe artifact record against that exact ZIP.
7. Create the annotated DRC_v2.0.0 tag at source_head.
8. Verify the annotated tag target.
9. Copy the same record into the GitHub Release body.
10. Attach the exact same ZIP.
```

No tracked source or documentation commit is permitted after step 4.

## Builder boundary

`build_v200_final_fixed_release_zip_from_head.ps1` rejects:

```text
non-main branch
missing or mismatched origin/main
non-official Public origin
multiple root commits
an existing local DRC_v2.0.0 tag
dirty source
generated caches in the strict Public source surface
a Day80 manifest stored inside the Public repository
an existing destination ZIP
```

The accepted Day80 manifest must be supplied by absolute path from outside the
Public repository. The builder validates it but never copies it into the ZIP
or prints the private path.

## Required public-safe fields

```text
status: accepted
release_target: v2.0.0
record_kind: final_release_artifact_record
repository_topology: clean_history_public_snapshot
public_repository: murayan1982/daily-rhythm-companion-public
source_head: full 40-character lowercase Public commit SHA
main_head: same source_head
public_root_commit_count: 1
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
public_main_matches_source_head: true
clean_history_public_root_verified: true
annotated_tag_targets_source_head: true
github_release_same_fixed_zip_required: true
operator_review_accepted: true
```

Required false markers:

```text
fixed_zip_rebuilt_after_verification: false
source_changed_after_fixed_zip_build: false
private_git_history_included: false
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

The record contains the ZIP basename only. Do not put absolute paths, Private
repository commit IDs, screenshot references, operator-evidence paths,
provider payloads, tokens, credentials, or LAN IPs in the tag or GitHub
Release metadata.

## Source-tree verification

Before the final Public-P4 commit:

```powershell
$previousDontWriteBytecode = $env:PYTHONDONTWRITEBYTECODE

try {
    $env:PYTHONDONTWRITEBYTECODE = "1"

    python scripts\smoke_framework_v200_public_distribution_readiness.py `
      --source-directory (Get-Location).Path

    python scripts\smoke_framework_v200_final_release_artifact_record.py

    cd app
    flutter test
    cd ..
}
finally {
    if ([string]::IsNullOrEmpty($previousDontWriteBytecode)) {
        Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
    }
    else {
        $env:PYTHONDONTWRITEBYTECODE = $previousDontWriteBytecode
    }
}
```

The smoke accepts a clean-history Public synthetic record and rejects
representative ZIP hash, Public main, topology, Private history, multiple-root,
legacy develop field, lightweight-tag, private-path, and post-build source
change cases.

## Final same-artifact validation

After the same fixed ZIP passes Day82 and Day83:

```powershell
$head = (git rev-parse HEAD).Trim()
$mainHead = (git rev-parse main).Trim()
$publicRootCommitCount = @(git rev-list --max-parents=0 HEAD).Count

$recordObject = [ordered]@{
    status = "accepted"
    release_target = "v2.0.0"
    record_kind = "final_release_artifact_record"
    repository_topology = "clean_history_public_snapshot"
    public_repository = "murayan1982/daily-rhythm-companion-public"
    source_head = $head
    main_head = $mainHead
    public_root_commit_count = $publicRootCommitCount
    tag_name = "DRC_v2.0.0"
    tag_target_head = $head
    tag_object_type = "annotated"
    release_zip_name = (Split-Path $zip -Leaf)
    release_zip_size_bytes = $zipSize
    release_zip_sha256 = $zipHash
    day80_accepted_manifest_passed = $true
    day82_fixed_zip_verification_passed = $true
    day83_final_release_readiness_passed = $true
    fixed_zip_inspected_as_is = $true
    public_main_matches_source_head = $true
    clean_history_public_root_verified = $true
    annotated_tag_targets_source_head = $true
    github_release_same_fixed_zip_required = $true
    operator_review_accepted = $true
    fixed_zip_rebuilt_after_verification = $false
    source_changed_after_fixed_zip_build = $false
    private_git_history_included = $false
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
}

$record = $recordObject | ConvertTo-Json -Compress

python scripts\smoke_framework_v200_final_release_artifact_record.py `
  --release-zip $zip `
  --record-json $record
```

The validator directly reopens the supplied Day83 release surface, checks
package hygiene, CRC, required and forbidden entries, and binds the record's
ZIP name, size, and SHA-256 to the inspected artifact. It does not create the
tag, move branches, publish GitHub Release, rebuild the ZIP, or use the network.
