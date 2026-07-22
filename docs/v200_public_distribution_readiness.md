# Daily Rhythm Companion v2.0.0 Public distribution readiness

Status: **VALIDATOR READY — PUBLIC REPOSITORY NOT CREATED**
Release status: **NOT RELEASED**
Source of truth: `docs/DRC_v200_goal_checklist_small_commit.md`

## Purpose

Public-P2 adds one direct validator for the source surface that will be exported to the clean-history Public repository and for the final fixed zip built from that Public repository commit.

The validator does not publish a repository, create or move tags, build a zip, call providers, read ignored operator evidence, or use the network.

## Command

Private-repository Public-export view:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py
```

This mode enumerates tracked and non-ignored files, then applies the committed Public export policy before inspection. The following remain available in the Private repository but are omitted from the clean Public snapshot:

```text
docs/internal/**
historical patch/diff/temp/package artifacts
source-only day check scripts and day handoff notes
ignored/local operator evidence and build/cache output
```

The exported Public repository and every fixed ZIP are validated without this Private-only allowance.

Fixed-zip mode:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py `
  --release-zip release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip
```

Source-tree mode uses `git ls-files --cached --others --exclude-standard`. This means it inspects tracked files and non-ignored untracked files while leaving ignored local `.env`, operator evidence, release output, caches, and other local-only files unread.

Fixed-zip mode opens the supplied artifact as-is, runs the existing release-package hygiene check, verifies ZIP CRC and a single package root, then applies the same Public metadata and forbidden-surface checks. It never rebuilds the artifact.

## Required Public metadata

The validator requires:

```text
Flutter package version: 2.0.0+1
Web application name: Daily Rhythm Companion
Web short name: DRC
Web description: public AI Character Framework demo wording
release_notes/v2.0.0.md
MIT LICENSE
README Public migration boundary
single docs/ checklist source of truth
Public migration and retention policy documents
```

## Forbidden surface

The validator rejects:

```text
Private Git metadata/history
actual operator evidence
raw screenshots, audio, health data, or provider payloads
API keys, OAuth tokens, Authorization headers, or private keys
private Windows user paths or raw private LAN IPs
local .env variants
release output, Python `__pycache__` / `.pyc` / `.pyo`, Flutter `.dart_tool`, build output, patch/diff/temp/backup files
untracked Flutter generated plugin registrants for Android, iOS, Linux, and Windows
superseded Private candidate zips
obsolete duplicate/archive/check/release-chain files removed by Cleanup-1 through Cleanup-8
```

The validator intentionally does not read ignored local evidence or credential files.

## Final fixed-ZIP generated-file boundary

The final fixed ZIP must come from the committed-HEAD detached-worktree builder. A manual archive of an operator working directory is not an acceptable substitute, even when its package root and required files look correct.

The validator and `scripts/check_release_package.py` reject the following Flutter-generated plugin registration outputs when they appear in a source surface or fixed ZIP:

```text
app/android/app/src/main/java/io/flutter/plugins/GeneratedPluginRegistrant.java
app/ios/Runner/GeneratedPluginRegistrant.h
app/ios/Runner/GeneratedPluginRegistrant.m
app/linux/flutter/generated_plugin_registrant.cc
app/linux/flutter/generated_plugin_registrant.h
app/linux/flutter/generated_plugins.cmake
app/windows/flutter/generated_plugin_registrant.cc
app/windows/flutter/generated_plugin_registrant.h
app/windows/flutter/generated_plugins.cmake
```

These files were observed in a manually archived working directory but are absent from the authoritative Public `main` source surface. Required Flutter project source and platform build configuration remain allowed.

## Canonical snapshot immutability

Strict `--source-directory` validation must be run on the canonical exported directory before any command that can write generated files. Do not run `compileall`, dependency resolution, or Flutter tests directly in the canonical snapshot that will become the Public repository.

Python imports and `compileall` can create `__pycache__` and `.pyc` files. Flutter commands can create `app/.dart_tool` and other generated output. Public-P3.1 rejects those files explicitly. Runtime verification must use a disposable verification copy, while the canonical export remains byte-for-byte unchanged.

## Final retention classification

Cleanup-9 leaves no deferred tracked cleanup group. The remaining Day64-Day73 and Day76-Day80 capability evidence contracts, Day82/Day83 fixed-ZIP gates, public-safe example markers, acceptance synchronization, and final artifact record are explicitly retained as the reproducible v2.0.0 audit chain.

The v1.9 release-readiness chain, superseded pre-Web v2.0 readiness paths, completed TTS preparation chain, and Day74-Day75 intermediate evidence layer are no longer part of the tracked Public source surface. Canonical release history remains under `release_notes/`.

## Completion boundary

Public-P2 proves that the clean Public export view derived from the current Private preparation source passes the direct Public-distribution checks. It does not claim that the full Private repository, including retained `docs/internal/**`, historical patch/diff files, or source-only day checks, is itself a Public repository. It also does not prove that:

```text
the clean Public snapshot has been exported
the Public repository exists
the Public source commit exists
the final fixed zip has been built
the final fixed zip has passed Day82/Day83
the Public annotated tag exists
the GitHub Release exists
```

## Public-P3 export boundary

Public-P3 adds the committed-HEAD exporter documented in `docs/v200_public_snapshot_export.md`. The exporter validates the selected committed files before writing, writes only to a new directory outside the Private repository, byte-compares the written result with the validated selection, and then applies strict exported-directory inspection.

Public-P3 tooling readiness does not mean the snapshot has been written or the Public repository exists.

## Cleanup-8 and Cleanup-9 boundary

The validator rejects restoration of the superseded Day74 screenshot-collection checklist and Day75 intermediate private-manifest validator. Day80 is the authoritative accepted private evidence manifest contract. Cleanup-9 explicitly retains the remaining capability evidence and final audit chain and advances the next focus to clean snapshot export and strict validation in the new Public repository.

## Current next focus

Resolve the remaining final Public pre-build gate issues, commit and push the final Public source, verify a clean Public `main`, freeze source, build one fixed ZIP, and run Day81, Day82, and Day83 against that same artifact. This validator update does not build or accept the final ZIP, create a tag, or publish a GitHub Release.
