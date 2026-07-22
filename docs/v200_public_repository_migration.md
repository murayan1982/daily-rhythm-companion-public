# Daily Rhythm Companion v2.0.0 Public repository migration

Status: **IN PROGRESS**
Release status: **NOT RELEASED**
Source of truth: `docs/DRC_v200_goal_checklist_small_commit.md`

## Purpose

Prepare Daily Rhythm Companion v2.0.0 in the existing Private development repository, maintain the reviewed clean-history source in `murayan1982/daily-rhythm-companion-public`, and complete the final Public artifact/tag/Release sequence without exposing Private Git history or local/operator evidence.

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

Clean-history Public repository
  - was initialized from one reviewed clean source snapshot
  - does not receive the Private .git directory, refs, tags, branches, or commit history
  - has an authoritative Public root commit and subsequent Public preparation commits
  - will build and verify the final Public fixed ZIP from the frozen Public `main` commit
  - will create a new annotated DRC_v2.0.0 tag
  - will publish the GitHub Release with the same verified ZIP
```

The Public repository uses the distinct owner/name `murayan1982/daily-rhythm-companion-public`; the existing Private repository remains separate and Private.

## Why the old final artifact record cannot be reused

Git commit IDs include parent history. A clean-history Public repository therefore receives a different commit SHA even when its file tree matches the Private preparation tree.

The earlier G-7 contract used the original same-repository topology:

```text
source_head == main_head == develop_head == annotated tag target
```

Public-P4 replaces that historical requirement with the clean-history Public topology:

```text
repository_topology == clean_history_public_snapshot
public_repository == murayan1982/daily-rhythm-companion-public
source_head == public_main_head == annotated_public_tag_target
public_root_commit_count == 1
private_git_history_included == false
```

The Public fixed-ZIP builder now requires the official Public origin and committed Public `main`. It removes the repository-local ignored-manifest dependency from the Public checkout, but still requires an explicit `ManifestPath` to the accepted Day80 manifest outside the Public repository. The builder validates that external manifest without copying it into the worktree or ZIP and without printing its private path. The Private candidate artifact record remains historical only.

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

Retention cleanup, Public-distribution validation, clean snapshot creation, Public repository initialization, and Public artifact-record/builder binding are complete. The remaining gates are the final committed Public source freeze, one-time fixed ZIP, Day82/Day83 same-artifact verification, final artifact record, Public annotated tag, and GitHub Release.

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

- [x] Finish and verify Public preparation through Public-P4 in the Private repository.
- [x] Export one reviewed clean source snapshot without Private Git metadata or ignored/local files.
- [x] Initialize `murayan1982/daily-rhythm-companion-public` and create its authoritative root commit.
- [x] Run strict Public-distribution checks and Flutter tests in the Public checkout using disposable runtime copies.
- [x] Align the final artifact record and builder with clean-history Public `main` in Public-P4.
- [x] Synchronize README/checklist/roadmap/migration status in Public-P5.
- [x] Require evidence-backed Day82/Day83 acceptance in Public-P6 follow-up 1.
- [x] Reject untracked Flutter generated registrants in Public-P6 follow-up 2.
- [x] Synchronize the active Public main-only release sequence in Public-P6 follow-up 3.
- [ ] Confirm the final Public pre-build synchronization commit is pushed and the Public working tree is clean.
- [ ] Run final source-tree, acceptance-contract, and Flutter checks from the committed Public source.
- [ ] Build one fixed ZIP exactly once from the committed Public source using the external accepted Day80 manifest.
- [ ] Run Day81, Day82, and Day83 against that exact ZIP without rebuilding.
- [ ] Validate the Public artifact record against the same Public source commit and ZIP.
- [ ] Create a new annotated `DRC_v2.0.0` tag targeting that Public source commit.
- [ ] Create the GitHub Release and attach the exact same fixed ZIP and artifact record.
- [x] Confirm the existing Private repository remains Private.

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

Public-P2 also accepts `--source-directory` for strict validation of the exported tree without Private-source exclusions. This makes the export boundary independently verifiable before and after the clean-history Public repository is initialized.

## Public-P3.1 generated-cache hardening and canonical export

Public-P3.1 rejects Python bytecode/cache directories and Flutter-generated cache/build output from strict Public source validation. Runtime checks are run only in disposable verification copies so the canonical export remains untouched.

A fresh canonical snapshot passed strict validation at 576 files and was used to initialize the clean-history Public repository. The earlier mutated export remains invalidated and was not used.

## Public repository initialization

```text
public_repository: murayan1982/daily-rhythm-companion-public
initial_commit: c02fef89362fa6660ccdc2559cfb1a9da506f81a
initial_commit_message: Initial public source snapshot for v2.0.0
root_commit_count: 1
tracked_file_count: 576
private_git_history_transferred: false
superseded_private_candidate_transferred: false
```

The initial Public snapshot passed strict Public-distribution validation. Python and Flutter runtime checks were performed in disposable copies rather than in the canonical checkout.

## Public-P4 clean-history artifact contract and builder

Public-P4 updates these four release-contract files in both repositories:

```text
backend/app/services/framework_v200_final_release_artifact_record.py
scripts/smoke_framework_v200_final_release_artifact_record.py
build_v200_final_fixed_release_zip_from_head.ps1
docs/v200_final_release_artifact_record.md
```

The final artifact record now requires the clean-history Public repository, Public `main`, exactly one root commit, the official Public origin, no Private Git history, and no legacy `develop_head` field. The fixed-ZIP builder uses committed public-safe acceptance markers, rejects repository-local private-manifest storage, and requires the accepted Day80 manifest through an explicit path outside the Public repository.

Public-P4 validation passed in both preparation and Public checkouts, including strict Public-distribution validation, artifact-record smoke checks, and Flutter tests. It did not build a ZIP, create a tag, or publish a Release.

## Public-P5 and Public-P6 pre-build synchronization

Public-P5 synchronized `README.md`, `roadmap.md`, the goal checklist, and this migration procedure with the completed Public-P3.1/Public initialization/Public-P4 state. Public-P6 fixed the empty-tag preflight and accepted-manifest gate. Public-P6 follow-up 1 separates inspection-only ZIP checks from evidence-backed Day82/Day83 acceptance, follow-up 2 rejects untracked Flutter generated registrants, and follow-up 3 aligns all active instructions with the Public main-only topology and external Day80 manifest boundary. These steps preserve `NOT_RELEASED` and leave the fixed ZIP, actual Day81/Day82/Day83 artifact verification, final artifact record, annotated tag, and GitHub Release pending.

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
public_distribution_validator: private-export-view-and-public-strict-passed
public_snapshot_export_tooling: completed-public-p3
public_snapshot_validator: completed-public-p3.1
canonical_public_snapshot: exported-untouched-strictly-validated
public_repository: murayan1982/daily-rhythm-companion-public
public_repository_initial_commit: c02fef89362fa6660ccdc2559cfb1a9da506f81a
public_repository_root_commit_count: 1
public_repository_tracked_files: 576
public_artifact_record_contract: completed-public-p4
public_fixed_zip_builder: completed-public-p4
public_status_document_sync: completed-public-p5
public_prebuild_acceptance_contract: completed-public-p6-follow-up-1
public_generated_release_guard: completed-public-p6-follow-up-2
public_final_sequence_sync: completed-public-p6-follow-up-3
public_fixed_release_zip: not-built
public_tag: not-created
public_github_release: not-created
release_status: NOT_RELEASED
```
