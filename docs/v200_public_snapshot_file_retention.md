# Daily Rhythm Companion v2.0.0 Public snapshot file retention

Status: **IN PROGRESS**
Release status: **NOT RELEASED**
Source of truth: `docs/DRC_v200_goal_checklist_small_commit.md`

## Purpose

Define which tracked file classes belong in the clean-history Public source snapshot and remove obsolete material in small, independently verified commits.

This document does not authorize a release zip, tag, repository publication, or GitHub Release.

## Retention classes

### RETAIN — runtime and user-facing source

Retain the application/backend source, assets, dependency manifests, configuration examples, quick starts, troubleshooting, framework setup, and tests needed to understand, run, and verify Daily Rhythm Companion.

### RETAIN — current v2.0.0 release safety surface

Retain the active v2.0.0 checklist, release migration procedure, fixed-zip/readiness validators, artifact-record contract, public-safe evidence marker validators, and the example evidence templates required by those validators.

These files expose process structure, but not raw evidence or secrets. They remain useful for reproducibility and auditability until a later Public-distribution validator defines a smaller complete allowlist.

### RETAIN — public-safe configured-operation guidance

Retain public-safe operator runbooks and helper scripts for optional framework, TTS, voice, motion, and Google Health paths when they:

```text
use placeholders instead of secrets
require explicit opt-in
do not print credential values
do not include raw evidence
do not include private absolute paths or LAN IPs
```

### RETAIN — canonical release history

Canonical release notes live under:

```text
release_notes/
```

The Public snapshot keeps that directory as the supported release-history surface.

### PRIVATE-ONLY / FORBIDDEN

The Public snapshot and release package must not contain:

```text
.git/ or Private repository refs/history
operator_evidence/ actual files
raw screenshots, audio, health data, prompts, answers, or provider payloads
API keys, OAuth tokens, Authorization headers, or credential files
private absolute paths or raw LAN IPs
local .env files
virtual environments, caches, build output, temp/backup/patch/diff files
superseded Private candidate zip
```

### RETAIN — final capability evidence and release audit chain

Cleanup-9 explicitly retains the remaining Day64-Day73 and Day76-Day80 capability evidence contracts, public-safe example markers, acceptance synchronization, Day82/Day83 fixed-ZIP checks, and final artifact-record contract. These files are not raw operator evidence. They form the reproducible public-safe verification chain that proves each accepted capability and prevents mock-only, skipped, unavailable, placeholder, API-only, or screenshot-missing states from authorizing the release.

The retained audit chain is intentionally separate from `operator_evidence/`, raw screenshots, raw audio, raw health payloads, prompts, answers, tokens, private paths, and LAN addresses, all of which remain excluded.

## Cleanup-3 first-pass removals

The following files are removed because they have no active references and are superseded by current checks or canonical release documentation:

```text
docs/v0.30.0_release_notes.md
- historical pre-v1 release notes outside the canonical release_notes/ directory

docs/v1100_release_foundation.md
- superseded by release_notes/v1.10.0.md and current v2.0.0 checklist/migration docs

scripts/check_v025_release_readiness.py
- obsolete v0.25 package check requiring paths that no longer exist in the current source tree

scripts/check_v030_framework_integration_foundation.py
- obsolete v0.30 aggregate wrapper; its underlying current checks remain independently available
```

## Cleanup-4 canonical release-note migration

The retained v1.9.0 release note is moved to:

```text
release_notes/v1.9.0.md
```

All active references and validators use the canonical path. The old `docs/release_notes_v1.9.0.md` path is removed. This is a path consolidation, not a deletion of the v1.9.0 release record.

## Cleanup-5 v1.9 release-chain retirement

Cleanup-5 removes the completed historical v1.9.0 Day46-Day49 implementation chain and its version-specific cleanup helpers:

```text
backend/app/services/framework_v190_release_readiness.py
backend/app/services/framework_v190_release_package_candidate.py
backend/app/services/framework_v190_fixed_release_zip_evidence.py
backend/app/services/framework_v190_release_finalization.py
docs/framework_v190_release_readiness.md
docs/framework_v190_release_package_candidate.md
docs/framework_v190_fixed_release_zip_evidence.md
docs/framework_v190_release_finalization.md
docs/release_cleanup_policy.md
scripts/smoke_framework_v190_release_readiness.py
scripts/smoke_framework_v190_release_package_candidate.py
scripts/smoke_framework_v190_fixed_release_zip_evidence.py
scripts/smoke_framework_v190_release_finalization.py
scripts/check_v190_release_package_candidate.py
scripts/check_v190_release_surface_cleanup.py
scripts/cleanup_v190_release_dev_artifacts.py
```

The canonical historical release record `release_notes/v1.9.0.md` remains retained. Current source/package validation is owned by Public-P2, and final fixed-ZIP verification remains owned by Day82 and Day83.

## Cleanup-6 pre-Web v2.0 readiness-chain retirement

Cleanup-6 removes the following superseded preparation contracts:

```text
backend/app/services/public_repo_v200_readiness.py
backend/app/services/v200_release_requirements_final_gate.py
backend/app/services/framework_v200_fixed_release_candidate_zip_verification.py
backend/app/services/framework_v200_final_release_readiness.py
docs/v200_public_repo_readiness.md
docs/v200_release_requirements_final_gate.md
docs/v200_fixed_release_candidate_zip_verification.md
docs/v200_final_release_readiness.md
scripts/smoke_v200_public_repo_readiness.py
scripts/smoke_v200_release_requirements_final_gate.py
scripts/smoke_framework_v200_fixed_release_candidate_zip_verification.py
scripts/smoke_framework_v200_final_release_readiness.py
docs/operator_evidence_templates/v200_fixed_release_candidate_zip_day71.example.json
docs/operator_evidence_templates/v200_final_release_readiness_day72.example.json
```

Public-P2 replaces the former Public metadata/package gate. Day80, Day82, and Day83 replace the former pre-Web fixed-candidate/final-readiness authorization path.

## Cleanup-7 TTS private-run preparation-chain retirement

Cleanup-7 removes the following completed source-tree-only preparation helpers:

```text
backend/app/services/framework_v200_real_tts_web_audio_actual_run_checkpoint.py
backend/app/services/framework_v200_real_tts_web_audio_evidence_authoring_handoff.py
backend/app/services/framework_v200_real_tts_web_audio_local_preflight_checkpoint.py
backend/app/services/framework_v200_real_tts_web_audio_operator_runbook.py
backend/app/services/framework_v200_real_tts_web_audio_preflight.py
backend/app/services/framework_v200_real_tts_web_audio_preflight_execution_handoff.py
backend/app/services/framework_v200_real_tts_web_audio_run_validation_flow.py
docs/v200_real_tts_web_audio_operator_runbook.md
scripts/smoke_framework_v200_real_tts_web_audio_actual_run_checkpoint.py
scripts/smoke_framework_v200_real_tts_web_audio_evidence_authoring_handoff.py
scripts/smoke_framework_v200_real_tts_web_audio_local_preflight_checkpoint.py
scripts/smoke_framework_v200_real_tts_web_audio_operator_runbook.py
scripts/smoke_framework_v200_real_tts_web_audio_preflight.py
scripts/smoke_framework_v200_real_tts_web_audio_preflight_execution_handoff.py
scripts/smoke_framework_v200_real_tts_web_audio_run_validation_flow.py
```

The configured TTS runtime boundary, provider-neutral env example, Day54/Day65/Day77 evidence contracts and templates, combined acceptance gate, public acceptance synchronization, and final Day80-Day83 audit chain remain retained.

The Google Health preflight and operator launcher remain retained because `backend/scripts/run_google_health_real_api_operator.ps1` actively invokes the preflight as part of optional configured operation.

## Cleanup-8 Day74-Day75 intermediate-chain retirement

Cleanup-8 removes the following superseded preparation layer:

```text
backend/app/services/framework_v200_web_execution_screenshot_collection.py
backend/app/services/framework_v200_private_web_evidence_manifest_validation.py
docs/v200_web_execution_screenshot_evidence_collection.md
docs/v200_private_web_evidence_manifest_validation.md
scripts/smoke_framework_v200_web_execution_screenshot_collection.py
scripts/smoke_framework_v200_private_web_evidence_manifest_validation.py
scripts/check_v200_web_execution_screenshot_collection_day74.py
scripts/check_v200_private_web_evidence_manifest_day75.py
docs/operator_evidence_templates/v200_web_execution_screenshot_collection_day74.example.json
docs/operator_evidence_templates/v200_private_web_evidence_manifest_day75.example.json
```

Day74 was a pre-execution collection plan and Day75 was an intermediate manifest format. The accepted Day80 manifest aggregate now owns the authoritative release evidence contract. Day73 enforcement and Day76-Day79 capability evidence remain retained for the next classification step.

## Cleanup-9 final audit-chain retention

Cleanup-9 closes the remaining tracked-file classification by retaining these dependency-bound groups:

```text
Day64-Day68 capability execution evidence contracts
Day69 public repository final sweep
Day70 final prerelease aggregate review
Day73 accepted Web screenshot enforcement
Day76-Day79 capability screenshot evidence contracts
Day80 authoritative accepted private evidence manifest aggregate
Day81 accepted-Web-evidence readiness contract
Day82 same-ZIP fixed artifact verification
Day83 same-ZIP final release readiness
final immutable artifact-record contract
public-safe acceptance synchronization checks
required public-safe example evidence templates
```

Retention is required because Day80 consumes the capability and aggregate contracts, Day82/Day83 consume Day80 and Public-P2, and the final artifact record binds the resulting Public source commit, annotated tag, and fixed ZIP. Removing individual links would either make the release claim unverifiable or duplicate the same rules in a new validator.

No remaining historical/release-process group is deferred after Cleanup-9. Future removal is a post-v2.0.0 maintenance decision and must preserve equivalent verification coverage.

## Public-P2 validator ownership

Current Public metadata and package-surface validation is owned by:

```text
docs/v200_public_distribution_readiness.md
backend/app/services/framework_v200_public_distribution_readiness.py
scripts/smoke_framework_v200_public_distribution_readiness.py
```

The final builder runs Private-repository Public-export-view mode, and Day82/Day83 run strict fixed-ZIP mode. The export view intentionally omits retained `docs/internal/**`, historical patch/diff files, and day-by-day source checks while the final ZIP remains subject to the full forbidden-file and sensitive-content policy. After Cleanup-8, the contract also forbids restoration of the retired TTS preparation chain and Day74-Day75 intermediate evidence layer. Cleanup-9 explicitly retains the remaining capability evidence and final Day80-Day83 audit chain, so no tracked cleanup group remains deferred before Public export.

## Remaining gate

Tracked-file cleanup and retention classification are complete. Public-P3 now provides the committed-HEAD exporter and strict exported-directory validator. The remaining publication gates are:

- commit Public-P3 and validate the exact committed HEAD;
- write one clean Public snapshot outside the Private repository;
- run the Public-distribution validator in strict `--source-directory` mode;
- create the new Public repository source commit without Private Git history;
- build and verify one fixed ZIP from that committed Public source; and
- create the matching annotated tag and GitHub Release.
