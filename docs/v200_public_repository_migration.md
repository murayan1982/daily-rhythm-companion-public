# Daily Rhythm Companion v2.0.0 Public repository migration

Status: **IN PROGRESS**
Release status: **NOT RELEASED**
Source of truth: `docs/DRC_v200_goal_checklist_small_commit.md`

## Purpose

Prepare Daily Rhythm Companion v2.0.0 in the existing Private development repository, then publish a clean-history source snapshot in a separate Public repository without exposing the Private repository's Git history or local/operator evidence.

## Superseded Private candidate

The previously built artifact remains a valid record of its own inspection, but it is not the final Public release asset.

```text
release_zip_name: DailyRhythmCompanion_20260721_190129.zip
release_zip_size_bytes: 1518863
release_zip_sha256: 8d8e654f13b8bbe4db4240b060e835ed68e0a6661c88a8d7be98941a1eae8d4f
zip_entries: 641
private_tag_name: DRC_v2.0.0
private_tag_type: annotated
day82_fixed_zip_verification: passed
day83_final_release_readiness: passed
zip_crc: passed
public_release_use: superseded-do-not-publish
```

Do not edit, rebuild, or upload this candidate as the new Public release asset.

## Repository topology

```text
Existing Private repository
  - keeps full development history
  - keeps private/local evidence outside tracked Public material
  - receives Public preparation commits
  - remains Private

New Public repository
  - is initialized from one reviewed clean source snapshot
  - does not receive the Private .git directory, refs, tags, branches, or commit history
  - creates a new authoritative Public source commit
  - builds and verifies the final Public fixed zip from that Public commit
  - creates a new annotated DRC_v2.0.0 tag
  - publishes the GitHub Release with the same verified zip
```

The new Public repository must use a distinct GitHub owner/name from the existing Private repository, unless the existing Private repository is renamed first. Two repositories under the same owner cannot have the same repository name.

## Why the old final artifact record cannot be reused

Git commit IDs include parent history. A clean-history Public repository therefore receives a different commit SHA even when its file tree matches the Private preparation tree.

The earlier G-7 contract requires:

```text
source_head == main_head == develop_head == annotated tag target
```

That equality can only authorize the repository where the recorded commit exists. For the clean-history Public release, the artifact record must instead bind the new Public repository commit, Public tag target, and fixed zip built from that Public commit.

## Public preparation gates in the Private repository

- Public-facing Flutter version is `2.0.0+1`.
- Web manifest, title, and description use `Daily Rhythm Companion`.
- `release_notes/v2.0.0.md` exists.
- README and roadmap describe the migration and current release state accurately.
- Obsolete files are removed in small, independently verified commits.
- Public-retained development/evidence documents are intentionally classified.
- A Public-distribution validator checks required metadata and forbidden content in Private-repository Public-export-view mode and strict fixed-ZIP mode.
- The final builder runs the Public-export-view validator before creating the fixed ZIP.
- Day82 and Day83 run the validator against the supplied unchanged fixed ZIP.
- Mock-safe checks remain credential-free.
- Existing real-execution acceptance markers remain public-safe and do not expose raw evidence.

## Public-P1 metadata alignment

Public-P1 completes the user-facing metadata portion of the migration without claiming release completion:

```text
flutter_package_version: 2.0.0+1
web_application_name: Daily Rhythm Companion
web_short_name: DRC
web_title: Daily Rhythm Companion
web_description: aligned-public-demo-description
v200_release_notes: release_notes/v2.0.0.md
release_status: NOT_RELEASED
```

The remaining gates are retention cleanup, Public-distribution validation, clean snapshot creation, the new Public source commit, Public artifact-record binding, the one-time fixed zip, the Public annotated tag, and the GitHub Release.

## Cleanup-2 checklist source consolidation

Cleanup-2 removes the duplicate root-level `DRC_v200_goal_checklist_small_commit.md`. The only tracked source of truth is now:

```text
docs/DRC_v200_goal_checklist_small_commit.md
```

Source-tree and fixed-zip validators are updated to require the docs path and to reject restoration of the legacy root copy. This removes one large duplicated file without changing any accepted evidence result or release status.

The broader retention review remains open; Cleanup-2 does not yet remove historical evidence documents, operator runbooks, or versioned release validators.

## Cleanup-3 first-pass file retention

Cleanup-3 removes a small isolated set that has no active references and is already superseded by canonical documentation or current checks:

```text
docs/v0.30.0_release_notes.md
docs/v1100_release_foundation.md
scripts/check_v025_release_readiness.py
scripts/check_v030_framework_integration_foundation.py
```

The removal is intentionally narrow. Current v2.0.0 evidence/readiness validators, public-safe operator runbooks and example templates, runtime/user setup documentation, backend/app tests, and canonical release history under `release_notes/` remain retained. The old v1.9 release-finalization chain is deferred because current v2.0.0 prerequisite and package checks still reference parts of it.

The detailed classification is recorded in `docs/v200_public_snapshot_file_retention.md`. The overall cleanup gate remains open until the Public-distribution validator owns the final required/forbidden file policy.

## Cleanup-4 canonical v1.9.0 release note

Cleanup-4 moves the retained v1.9.0 release note from `docs/release_notes_v1.9.0.md` to the canonical release-history path `release_notes/v1.9.0.md` and updates every active reference. This removes the last versioned release-note record outside `release_notes/` without deleting the historical release content.

Public-P2 replaces the current package-surface ownership that previously kept the v1.9 implementation chain dependency-bound. Cleanup-5 removes that obsolete chain while retaining `release_notes/v1.9.0.md` as the historical release record.

## Cleanup-5 v1.9 release-chain retirement

Cleanup-5 removes the obsolete v1.9.0 Day46-Day49 release-readiness/package/finalization implementation files and v1.9-specific cleanup helpers. The active v2.0 prerequisite check now relies on the canonical v1.9.0 release note rather than removed implementation documents.

Current ownership is:

```text
historical v1.9.0 release record: release_notes/v1.9.0.md
current Public metadata/package validation: Public-P2
final fixed-ZIP validation: Day82 and Day83
remaining deferred cleanup: historical v2.0 evidence/readiness chain
```

## Cleanup-6 pre-Web v2.0 readiness-chain retirement

Cleanup-6 removes the superseded Day57/Day58 Public-readiness aggregate chain and Day71/Day72 pre-Web fixed-ZIP chain. These files are no longer authoritative after Public-P2 and the accepted-Web-evidence Day80-Day83 path assumed current ownership.

Removed categories:

```text
Day57/Day58 docs, services, and smoke scripts
Day71/Day72 docs, services, smoke scripts, and example operator templates
```

No actual operator evidence, accepted marker state, runtime source, release ZIP, Git ref, or GitHub Release is changed by this cleanup.

## Clean snapshot exclusions

The Public snapshot must not include:

```text
.git/
Private repository refs or tags
operator_evidence/
raw screenshots
raw audio
raw health data
raw provider payloads
API keys or OAuth tokens
Authorization headers
private absolute paths
raw LAN IPs
local .env files
virtual environments
build/cache output
patch/diff/temp/backup files
superseded Private candidate zip
```

## Public repository release sequence

1. Finish and verify all Public preparation commits in the Private repository.
2. Confirm the tracked working tree is clean.
3. Export one reviewed clean source snapshot without Private Git metadata or ignored/local files.
4. Initialize the new Public repository and create its authoritative source commit.
5. Run source-tree, mock-safe, Flutter, and Public-distribution checks in the Public checkout.
6. Build one fixed zip from the committed Public source.
7. Run Day82 and Day83 against that exact zip without rebuilding.
8. Validate the Public artifact record against the Public source commit and zip.
9. Create a new annotated `DRC_v2.0.0` tag targeting the same Public source commit.
10. Create the GitHub Release and attach the exact same fixed zip.
11. Confirm the existing Private repository remains Private.

## Public-P2 direct distribution validator

Public-P2 adds `scripts/smoke_framework_v200_public_distribution_readiness.py`. Source-tree mode inspects tracked and non-ignored files without reading ignored local evidence or credentials. Fixed-ZIP mode opens one supplied artifact as-is, runs package hygiene and CRC/root checks, then applies the same metadata and forbidden-surface contract.

The final committed-head builder, Day82, and Day83 are wired to this validator. Cleanup-5 removes the former historical version-specific package chain after Public-P2 assumes current Public metadata/package validation ownership.

## Cleanup-7 completed TTS private-run preparation-chain retirement

Cleanup-7 removes the source-tree-only TTS operator runbook, preflight, handoff, checkpoint, and authoring helpers that existed to prepare the already completed private configured run. They are not runtime dependencies and are not required to reproduce the public acceptance decision.

The Public snapshot retains:

```text
backend/env_profiles/framework_real_tts_operator.env.example
backend/app/services/framework_v200_real_tts_provider_gate.py
backend/app/services/framework_v200_real_tts_web_audio_output_evidence.py
backend/app/services/framework_v200_real_tts_web_audio_execution_evidence.py
backend/app/services/framework_v200_real_tts_web_audio_screenshot_evidence.py
backend/app/services/framework_v200_real_tts_web_audio_acceptance.py
scripts/smoke_framework_v200_real_tts_web_audio_*evidence.py
scripts/smoke_framework_v200_real_tts_web_audio_acceptance.py
scripts/smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
docs/v200_real_tts_provider_gate.md
docs/v200_real_tts_web_audio_*evidence*.md
docs/operator_evidence_templates/v200_real_tts_web_audio_*.example.json
```

These retained files document and validate the public-safe acceptance surface without exposing raw audio, provider payloads, secrets, private paths, LAN IPs, screenshots, or operator evidence.

## Cleanup-8 completed Day74-Day75 intermediate evidence-chain retirement

Cleanup-8 removes the obsolete screenshot collection checklist and intermediate private-manifest validator. These files prepared evidence before the accepted Day80 manifest aggregate existed. Day80 now provides the authoritative accepted manifest contract, while Day73 enforcement, Day76-Day79 capability evidence, and Day82-Day83 final fixed-ZIP gates remain retained.

## Cleanup-9 completed final retention classification

Cleanup-9 closes the tracked-file cleanup phase. The remaining Day64-Day73 and Day76-Day80 capability evidence contracts, public-safe example markers, acceptance synchronization, Day82/Day83 fixed-ZIP gates, and final artifact-record contract are explicitly retained. They are not private raw evidence; together they provide the reproducible audit path required to verify that skipped, mock-only, unavailable, placeholder, or screenshot-missing states cannot authorize the release.

Private-only history, source-only day checks, patch/diff artifacts, ignored operator evidence, and local build/configuration material remain excluded by the Public export view. No further tracked-file cleanup group remains deferred before export.

## Public-P3 committed snapshot export tooling

Public-P3 adds `scripts/export_v200_public_snapshot_from_head.py` and `docs/v200_public_snapshot_export.md`. The exporter requires a clean working tree, reads the exact committed HEAD through `git archive`, applies the committed Public export policy, validates the selected files strictly, and can write one new directory outside the Private repository. It does not copy `.git`, read ignored files, initialize Git, build a ZIP, create tags, publish GitHub content, or access the network.

Public-P2 also accepts `--source-directory` for strict validation of the exported tree without Private-source exclusions. This makes the export boundary independently verifiable before and after the new Public repository is initialized.

## Current status

```text
cleanup_1: completed-f05744d
public_p0_migration_gate: documented
public_metadata_alignment: completed-public-p1
flutter_package_version: 2.0.0+1
web_public_metadata: aligned
v200_release_notes: present
cleanup_2_checklist_consolidation: completed
cleanup_3_first_pass_retention: completed
cleanup_4_canonical_release_note: completed
cleanup_5_v190_release_chain: completed
cleanup_6_pre_web_v200_readiness_chain: completed
cleanup_7_tts_private_run_preparation_chain: completed
cleanup_8_day74_day75_intermediate_chain: completed
cleanup_9_final_retention_classification: completed
public_distribution_validator: source-tree-passed-public-p2-cleanup-complete
public_snapshot_export_tooling: ready-public-p3
initial_public_snapshot: invalidated-after-in-place-generated-cache-write
public_snapshot_validator: public-p3.1-cache-hardening-pending
public_repository: not-created
public_source_commit: not-created
public_fixed_release_zip: not-built
public_tag: not-created
public_github_release: not-created
release_status: NOT_RELEASED
```
