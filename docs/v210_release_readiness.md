# Daily Rhythm Companion v2.1.0 R-1b release-candidate readiness gate

Updated: 2026-07-25
Status: COMPLETED / ACCEPTED
Completed small commit: R-1b
Current small commit: R-1d
Parent phase: R-1 CURRENT / NOT_COMPLETED
Release state: CANDIDATE / NOT_RELEASED

```text
R-1a: COMPLETED / ACCEPTED
R-1b: COMPLETED / ACCEPTED
R-1c: COMPLETED / ACCEPTED
R-1d: CURRENT / NOT_COMPLETED (NOT_STARTED)
R-1e: PLANNED
```

## Purpose

R-1b creates the credential-free aggregate source-tree/test gate and advances the active application metadata to the v2.1.0 release-candidate values. It prepares public-safe release policy, candidate notes, and an unfilled release record without building a ZIP, creating a tag, or publishing a GitHub Release.

## Candidate metadata

```text
Backend APP_VERSION: 2.1.0
Flutter package version: 2.1.0+3
Release tag name reserved for later approval: DRC_v2.1.0
Current released version: v2.0.1
v2.1.0 publication state: NOT_RELEASED
```

The Flutter build number advances from `+2` to `+3`. Runtime health and FastAPI/OpenAPI version surfaces continue to use the single Backend `APP_VERSION` constant. Existing Flutter tests that feed a fake `API v2.0.1` response remain compatibility fixtures rather than active package metadata.

## Aggregate child checks

The accepted R-1b gate ran 18 source-tree checks. The current portable gate runs those same 18 checks plus the R-1c validator as a nineteenth child check, in sorted order:

```text
check_v210_character_display_current_behavior_inventory.py
check_v210_character_display_home_integration.py
check_v210_character_display_state.py
check_v210_final_smartphone_web_evidence.py
check_v210_fitbit_current_behavior_inventory.py
check_v210_fitbit_real_operator_contract.py
check_v210_fitbit_real_sleep_normalization.py
check_v210_fitbit_token_status_reconnect.py
check_v210_flutter_sleep_provider_source_ui.py
check_v210_google_health_migration_audit.py
check_v210_google_health_real_operator_verification.py
check_v210_post_advice_chat_backend_lifecycle.py
check_v210_post_advice_chat_current_behavior_inventory.py
check_v210_post_advice_chat_flutter_lifecycle.py
check_v210_release_readiness_current_behavior_inventory.py
check_v210_sleep_provider_selection_source_labels.py
check_v210_tts_player_controller.py
check_v210_tts_player_current_behavior_inventory.py
check_v210_tts_player_home_integration.py
```

It also runs the accepted v2.0.x maintenance/compatibility aggregate `check_v20x_maintenance_readiness.py`.

It also requires:

```text
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_readiness.py
python -m pytest -q backend/tests          expected accepted baseline: 110 passed
flutter test                              expected accepted baseline: 103 passed
flutter build web                         required for R-1b acceptance
flutter build windows                     required for R-1b acceptance on the Windows release host
```

## Commands

Portable credential-free gate:

```powershell
python scripts\check_v210_release_readiness.py
```

Full local R-1b acceptance gate:

```powershell
python scripts\check_v210_release_readiness.py --with-flutter --with-builds
```

`--with-builds` requires Windows because the accepted candidate must include a successful Windows desktop build as well as the Web build.

## Safety guarantees

The gate:

```text
- does not read local operator env files or credentials;
- does not call Google Health, Fitbit, AI Character Framework, LLM, TTS, or STT providers;
- does not start the Backend, browser, or smartphone Web checkpoint;
- snapshots backend/local_data and release before/after execution;
- does not invoke build_release.bat or any fixed-ZIP builder;
- does not create or inspect DRC_v2.1.0 tags or GitHub Releases;
- preserves immutable v2.0.0/v2.0.1 release records and builders.
```

The accepted W-5b2 and T-1c operator records are checked only as public-safe source records. They are not re-executed by R-1b.

## Prepared candidate files

```text
docs/v210_release_readiness.md
release_notes/v2.1.0.md
docs/v210_release_record.md
scripts/check_v210_release_readiness.py
```

The release record intentionally contains `NOT_RECORDED`, `NOT_BUILT`, `NOT_RECEIVED`, and `NOT_CREATED` placeholders. R-1d/R-1e must replace them only after the one-time artifact workflow and explicit approval.

## Deferred boundaries

```text
R-1c: final integrated smartphone Web evidence aggregate
R-1d: clean official main, one-time fixed ZIP build, same-artifact verification
R-1e: explicit approval, annotated tag, GitHub Release, post-publication SHA-256 verification
```

## R-1b non-goals

```text
no functional Backend or Flutter behavior change
no dependency or asset change
no provider execution
no final smartphone Web evidence
no fixed ZIP build or verification
no DRC_v2.1.0 tag
no GitHub Release
no modification of v2.0.0/v2.0.1 historical release records
```

## R-1b acceptance record

```text
accepted on: 2026-07-25
implementation commit: 72dd42c
accepted R-1b child checks: 18 / 18 passed
v2.0.x maintenance/compatibility aggregate: passed
Backend pytest: 110 passed
Flutter test: 103 passed
Flutter Web build: passed
Flutter Windows build: passed
backend/local_data unchanged: true
release unchanged: true
fixed ZIP built: false
tag created: false
GitHub Release created: false
git diff --check and diff review: passed
explicit operator approval: received
```

R-1b is `COMPLETED / ACCEPTED`. R-1c is `CURRENT / NOT_COMPLETED` and `IMPLEMENTED / NOT_ACCEPTED`.

## Accepted R-1c evidence transition

R-1c adds `scripts/check_v210_final_smartphone_web_evidence.py`, the public-safe contract `docs/v210_final_smartphone_web_evidence.md`, and a deliberately rejected operator-manifest example. The aggregate source-tree gate includes the R-1c validator as its nineteenth child check while preserving the accepted R-1b record of 18 / 18 checks.

The ignored private manifest validated against exact clean synchronized candidate source `1e922e68685dadfc1008f1119d0ce492584e8f19`. The actual DRC Backend, PC Web, and smartphone Web completed all six required evidence items; screenshot references remained opaque and raw screenshots/audio/health values/private paths remained outside Git.

R-1c is `COMPLETED / ACCEPTED`; R-1d is `CURRENT / NOT_COMPLETED` and `NOT_STARTED`; R-1e remains `PLANNED`.
