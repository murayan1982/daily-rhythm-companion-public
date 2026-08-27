# Daily Rhythm Companion Scripts

This directory contains development, verification, release, compatibility, and configured-demo helper scripts for Daily Rhythm Companion.

## v2.1.0 W-1 accepted source-tree boundary

The authoritative v2.1.0 source of truth is `docs/DRC_v210_goal_checklist_small_commit.md`. W-1 established it after source-tree verification, diff review, and operator approval passed.

Current state:

```text
current released version: v3.0.0 RELEASED / ACCEPTED
current released metadata: Backend 3.0.0 / Flutter 3.0.0+4 RELEASED
previous released version: v2.1.0 RELEASED / ACCEPTED
completed maintenance line: v2.0.x COMPLETED / ACCEPTED
completed development line: v2.1.0 COMPLETED / ACCEPTED
W-1: COMPLETED / ACCEPTED
W-2: COMPLETED / ACCEPTED
W-3: COMPLETED / ACCEPTED
current small commit: DRC-V4-1 FW v6.0.0 readiness acceptance sync
current implementation state: IMPLEMENTED / AWAITING_REVIEW
current implementation baseline: 6311864237d8f5d86db49c14d17ca083e1af5c03
last accepted release control: RT-9e Control D POST_PUBLICATION_VERIFICATION / PASS / ACCEPTED
completed small commit: R-1e COMPLETED / ACCEPTED
completed phase: V-1 COMPLETED / ACCEPTED
completed phase: T-1 COMPLETED / ACCEPTED
DRC-V4-1 aggregate decision: PARTIAL_READY
DRC-V4-2: NOT_STARTED / NOT_AUTHORIZED
Framework release: v6.0.0
Framework annotated tag target: 61e15f62d1ecc5faee016abae82200f8de56c5dd
Framework official ZIP: ai-character-framework_v6.0.0.zip
Framework official ZIP SHA-256: 6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2
Framework root-public inventory: 127 names / frozen
```

## v4.0.0 DRC-V4-1 FW v6.0.0 readiness acceptance check

Detailed readiness:
`docs/v400_framework_v600_readiness_acceptance.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v400_framework_v600_readiness_acceptance.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v400_framework_v600_readiness_acceptance.py
git diff --check
git status --short
git diff --stat
```

The DRC-V4-1 gate is local, credential-free, provider-free, network-free,
microphone-free, real STT/LLM/TTS-free, playback-free, VTube Studio-free, and
real-motion-free. It verifies the exact seven-file docs/static-gate surface,
the required FW v6.0.0 readiness matrix, the `PARTIAL_READY` aggregate decision,
the critical unified `RealtimeSession.run_turn()` non-claim, and that DRC-V4-2
remains `NOT_STARTED / NOT_AUTHORIZED`.

The gate also freezes FW v6.0.0 provenance, root-public inventory count, the
provider-free DRC-V4-2 future exact-review scope, root `framework` imports only
for initial adoption, retained v3 real adapters, and the non-authorization of
FW submodule adoption, v3 adapter removal, and real unified RealtimeSession
claims.

W-1 inventoried the existing Fitbit implementation and established the v2.1.0 checklist. It changed no backend runtime, Flutter runtime, existing tests, version metadata, released fixed ZIP, tags, GitHub Releases, or publication records.

W-2 is completed and accepted. It adds conservative token/status/reconnect states, one-time OAuth state consumption, injected fake-HTTP refresh tests, and old/new Flutter response parsing without performing configured real Fitbit execution. W-3 is also completed and accepted after the full mock-safe gate, 84 backend tests, 50 Flutter tests, diff review, and operator approval passed. W-4 is completed and accepted. W-4a passed 8 focused backend tests, 92 full backend tests, and 50 Flutter tests. W-4b implementation commit `1fbea58` passed 4 focused model tests, 35 widget tests, 92 backend tests, 57 Flutter tests, diff review, and operator approval. W-5a implementation commit `7f84980` is completed and accepted after the public-safe preflights, source-tree guards, 92 backend tests, 57 Flutter tests, diff review, and operator approval passed. W-5b1, W-5b2, and parent W-5 are completed and accepted. C-1a is completed and accepted at implementation commit `a4263ca`; C-1b is completed and accepted at implementation commit `3055995`; C-1c and parent C-1 are completed and accepted at implementation commit `c856374`. T-1 and V-1 are completed and accepted. R-1a is completed and accepted at implementation commit `dbc84db`; R-1b is completed/accepted at implementation commit `72dd42c`; R-1c and R-1d are completed/accepted; R-1e and parent R-1 are completed/accepted; v2.1.0 is released. V-1a is completed and accepted at implementation commit `1602b2f`; V-1b at `e1f8d6f`; V-1c at `995145d`.


## v2.1.0 R-1a release/readiness current behavior inventory check

Detailed inventory: `docs/v210_release_readiness_current_behavior_inventory.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_release_readiness_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

The accepted R-1a check is credential-free, provider-free, network-free, and artifact-free. It freezes the accepted release surface before v2.1.0 release implementation: backend `2.0.1`, Flutter `2.0.1+2`, generic denylist packaging, generic ZIP hygiene validation, historical v2.0.1 one-time builder/verifier, `release/` Git exclusion, 110 Backend tests, 103 Flutter tests, and immutable v2.0.0/v2.0.1 records. Acceptance passed on 2026-07-25 at implementation commit `dbc84db` after compileall, all 18 v2.1.0 checks, v2.0.x guards, 110 Backend tests, 103 Flutter tests, diff review, and operator approval. No v2.1.0 release builder, aggregate gate, release record, release notes, fixed ZIP, tag, or GitHub Release was created by R-1a. R-1b is completed/accepted at implementation commit `72dd42c`; R-1c and R-1d are completed/accepted; R-1e and parent R-1 are completed/accepted; v2.1.0 is released.


## v2.1.0 R-1b release-candidate aggregate readiness gate

Detailed contract: `docs/v210_release_readiness.md`.

Portable credential-free gate:

```powershell
python scripts\check_v210_release_readiness.py
```

Full Windows-host implementation/acceptance gate:

```powershell
python scripts\check_v210_release_readiness.py --with-flutter --with-builds
```

The gate runs compileall, all 18 previously accepted `check_v210_*.py` child checks, the accepted v2.0.x maintenance/compatibility aggregate, and 110 Backend tests. The full mode additionally requires 103 Flutter tests, a Web build, and a Windows build. It snapshots `backend/local_data` and `release` and fails if either changes. It does not run providers, start a browser, invoke `build_release.bat`, build a fixed ZIP, create `DRC_v2.1.0`, or publish a GitHub Release.

R-1b set candidate metadata to Backend `2.1.0` and Flutter `2.1.0+3`. `scripts/check_v20x_application_version_metadata.py` continues to protect the accepted M-2 `2.0.1` record while allowing the later aligned v2.1.0 source. The historical R-1b candidate notes and prepared release record were explicitly `NOT_RELEASED`; R-1e later finalized and published them.

R-1b was accepted on 2026-07-25 at implementation commit `72dd42c`. The full Windows-host gate passed all 18 child checks, the v2.0.x compatibility aggregate, 110 Backend tests, 103 Flutter tests, Web build, and Windows build. `backend/local_data` and `release` remained unchanged; no fixed ZIP, tag, or GitHub Release was created. R-1c and R-1d are now completed/accepted; R-1e and parent R-1 are completed/accepted; v2.1.0 is released.

## v2.1.0 V-1a character display current behavior inventory check

Detailed inventory: `docs/v210_character_display_current_behavior_inventory.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_character_display_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

The V-1a check is credential-free, provider-free, network-free, decoder-free, and motion-adapter-free. It verifies the 4,195-line HomeScreen inventory, stable CharacterPreset fields, advice-source fallback boundary, accepted TTS playback phases, separate Motion Demo state, 2,669-line existing widget-test baseline, pubspec asset registration, three character images, two backgrounds, one repository fallback image, unchanged Flutter runtime/tests/assets, and immutable v2.0.0/v2.0.1 release records.

V-1a, V-1b, V-1c, and parent V-1 are `COMPLETED / ACCEPTED`. V-1c was accepted at implementation commit `995145d`; R-1a is `COMPLETED / ACCEPTED`; R-1b is `COMPLETED / ACCEPTED` at implementation commit `72dd42c`; R-1c and R-1d are `COMPLETED / ACCEPTED`; R-1e and parent R-1 are `COMPLETED / ACCEPTED`; v2.1.0 is released.

## v2.1.0 V-1b deterministic character display state check

Detailed contract: `docs/v210_character_display_state_contract.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_character_display_current_behavior_inventory.py
python scripts\check_v210_character_display_state.py

cd app
flutter test test/character_display_presentation_test.dart
flutter test test/character_display_card_test.dart
flutter test
cd ..

python -m pytest -q backend/tests
git diff --check
```

The accepted V-1b check is credential-free, provider-free, network-free, decoder-free, and motion-adapter-free. It verifies mood/advice/fallback content states, idle/loading/speaking activity states, deterministic precedence, safe fallback copy, the standalone static character card, nine model tests, four widget tests, unchanged HomeScreen/Motion Demo/assets/dependencies, and immutable release records. Acceptance passed with implementation commit `e1f8d6f`, 110 Backend tests, 9 focused model tests, 4 focused widget tests, and 97 full Flutter tests. V-1b does not connect HomeScreen or claim Live2D/VTube Studio execution; V-1c and parent V-1 are completed/accepted; R-1a is completed/accepted; R-1b is completed/accepted at implementation commit `72dd42c`; R-1c and R-1d are completed/accepted; R-1e and parent R-1 are completed/accepted; v2.1.0 is released.


## v2.1.0 V-1c HomeScreen character display integration check

Detailed contract: `docs/v210_character_display_home_integration.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_character_display_current_behavior_inventory.py
python scripts\check_v210_character_display_state.py
python scripts\check_v210_character_display_home_integration.py
python -m pytest -q backend/tests

cd app
flutter test test/character_display_presentation_test.dart
flutter test test/character_display_card_test.dart
flutter test test/character_display_home_integration_test.dart
flutter test
flutter build web
flutter build windows
cd ..

git diff --check
```

The V-1c check is credential-free, provider-free, network-free, and motion-adapter-free. It verifies HomeScreen wiring for mood/advice/loading/speaking/fallback, repository fallback-image retry, five focused HomeScreen tests, five focused card tests, unchanged V-1b presentation model, unchanged Backend/Motion Demo/dependencies/static assets, and immutable release records. V-1c and parent V-1 are `COMPLETED / ACCEPTED` at implementation commit `995145d`; R-1a is `COMPLETED / ACCEPTED`; R-1b is `COMPLETED / ACCEPTED` at implementation commit `72dd42c`; R-1c and R-1d are `COMPLETED / ACCEPTED`; R-1e and parent R-1 are `COMPLETED / ACCEPTED`; v2.1.0 is released.

Run the W-1 checks from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The W-1 source-tree check verifies:

```text
- README, roadmap, tasklist, checklist, and inventory describe W-1 as COMPLETED / ACCEPTED
- W-2 is COMPLETED / ACCEPTED
- W-3 is COMPLETED / ACCEPTED
- W-4 is COMPLETED / ACCEPTED
- W-5 is COMPLETED / ACCEPTED
- C-1 is COMPLETED / ACCEPTED
- T-1 is COMPLETED / ACCEPTED
- V-1 is COMPLETED / ACCEPTED
- V-1a is COMPLETED / ACCEPTED
- V-1b is COMPLETED / ACCEPTED
- V-1c is COMPLETED / ACCEPTED
- R-1a is COMPLETED / ACCEPTED
- R-1b is COMPLETED / ACCEPTED at implementation commit 72dd42c
- R-1c and R-1d are COMPLETED / ACCEPTED
- R-1e and parent R-1 are COMPLETED / ACCEPTED; v2.1.0 is RELEASED
- the accepted W-1 inventory and W-1 acceptance state remain recorded
- files outside the accepted W-2 change surface still match the inspected W-1 baseline
- approved W-2 runtime and Flutter files carry the separately checked W-2 contract
- v2.0.0 and v2.0.1 release records, builders, and patch-release validator are unchanged
- no credential, token, raw Fitbit payload, private path, or LAN value is added to W-1 docs
```

It does not read `backend/local_data`, make network calls, open an OAuth browser, exchange or refresh a real token, retrieve real Fitbit sleep data, build a release ZIP, or modify the repository.

Accepted W-1 verification recorded compileall success, the W-1 source-tree check, 38 backend pytest tests, and 43 Flutter tests. Configured real Fitbit verification remains explicit opt-in W-5 work. W-1 success must not be reported as live token validation, permission acceptance, real sleep retrieval, smartphone Web acceptance, or v2.1.0 completion.


## v2.1.0 W-2 accepted token/status/reconnect check

Detailed contract: `docs/v210_fitbit_token_status_reconnect.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests/test_fitbit_current_state_contract.py
python -m pytest -q backend/tests/test_fitbit_token_status_reconnect.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The accepted W-2 check verifies the new response states, backward-compatible fields, no-network status boundary, one-time OAuth state marker, fake-HTTP injection, conservative Flutter wording, W-3 accepted status, W-4 current status, and unchanged v2.0.0/v2.0.1 release records. Accepted W-2 verification recorded 57 backend tests and 50 Flutter tests. It does not load local credentials, call Fitbit, open OAuth, retrieve sleep data, or build a release artifact.

## v2.1.0 W-3 Fitbit sleep normalization check

Detailed contract: `docs/v210_fitbit_real_sleep_normalization.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v210_fitbit_real_sleep_normalization.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests/test_fitbit_real_sleep_normalization.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The W-3 check verifies allow-listed API error classification, safe exception
text, positive-duration normalization, main-sleep and summary fallback behavior,
`SleepSummary` real-data fields, unavailable reasons, synthetic fixture policy,
unchanged Flutter/runtime boundaries outside W-3, and immutable v2.0.0/v2.0.1
release records. It does not load local operator tokens, call Fitbit, open OAuth,
collect smartphone Web evidence, or build a release artifact.

W-3 is `COMPLETED / ACCEPTED`. Acceptance recorded 84 backend tests and 50
Flutter tests, with real Fitbit execution remaining false. W-4 is also
`COMPLETED / ACCEPTED`; W-5a, W-5b1, W-5b2, and parent W-5 are completed and accepted. C-1, T-1, and V-1 are completed and accepted; R-1a is completed/accepted; R-1b is completed/accepted at implementation commit `72dd42c`; R-1c and R-1d are completed/accepted; R-1e and parent R-1 are completed/accepted; v2.1.0 is released.


## v2.1.0 W-4a sleep-provider selection status check

Detailed contract: `docs/v210_sleep_provider_selection_source_labels.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v210_fitbit_real_sleep_normalization.py
python scripts\check_v210_sleep_provider_selection_source_labels.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests/test_sleep_provider_selection_contract.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The W-4a check verifies the read-only `GET /sleep/providers` route, backend-config
selection mode, stable provider roles, deprecated `fitbit_stub` alias, conservative
unknown-provider behavior, unchanged W-3 runtime files, immutable v2.0.0/v2.0.1
release records, and public-safe source text. It does not instantiate a provider,
read local token stores, refresh credentials, open OAuth, call Fitbit or Google
Health, collect smartphone Web evidence, or build a release artifact.

W-4a is `COMPLETED / ACCEPTED`. Acceptance recorded implementation commit
`1619b0b`, 8 focused backend tests, 92 full backend tests, 50 Flutter tests, diff
review, and operator approval. Real operator execution remained false and release
records remained unchanged. W-4b and W-4 are `COMPLETED / ACCEPTED`; W-5 is
`COMPLETED / ACCEPTED` and C-1 is `CURRENT / NOT_COMPLETED`.

## v2.1.0 W-4b Flutter provider/source-label UI check

Detailed contract: `docs/v210_flutter_sleep_provider_source_ui.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v210_fitbit_real_sleep_normalization.py
python scripts\check_v210_sleep_provider_selection_source_labels.py
python scripts\check_v210_flutter_sleep_provider_source_ui.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests

cd app
flutter test test/sleep_provider_selection_test.dart test/widget_test.dart
flutter test
cd ..
```

The W-4b check verifies the Flutter provider metadata model/client, separate
configured-provider and actual-source labels, conditional Fitbit status loading,
concise Google Health normal-user copy, retained Advanced operator details,
mock/Fitbit/Google Health fake-client regressions, unchanged accepted backend
boundaries, immutable release records, and public-safe source text.

It does not open OAuth, read real tokens, call external providers, validate live
Fitbit scopes or permissions, collect smartphone Web evidence, or build release
artifacts. W-4b and W-4 are `COMPLETED / ACCEPTED` after implementation commit
`1fbea58`, 4 focused model tests, 35 widget tests, 92 backend tests, 57 Flutter
tests, diff review, and operator approval. W-5 is `COMPLETED / ACCEPTED`; C-1 is `CURRENT / NOT_COMPLETED`.

## v2.0.x completed maintenance baseline

v2.0.0 is **RELEASED** as the immutable Public baseline. The completed v2.0.x maintenance source of truth is `docs/DRC_v20x_maintenance_checklist.md`.

Current released patch and maintenance status:

```text
v2.0.1 RELEASED
M-1 through M-9 COMPLETED / ACCEPTED
current small commit: none
```

M-1 through M-9 are completed and accepted. v2.0.1 is released with one fixed ZIP built from committed Public main, verified without rebuilding, published through annotated tag `DRC_v2.0.1` and GitHub Release, and re-verified after publication.

Install the development test dependencies and run the current checks from the repository root:

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py
python scripts\check_v20x_backend_mock_safe_regression.py
python scripts\check_v20x_framework_fallback_voice_artifact_regression.py
python scripts\check_v20x_temporary_lifecycle_limits.py
python scripts\check_v20x_web_cors_origins.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_readiness.py
python -m pytest -q backend/tests

# Full M-8 operator gate
python scripts\check_v20x_maintenance_readiness.py --with-flutter

# M-9 post-release record gate
python scripts\check_v20x_patch_release.py

# Strict current-main / annotated-tag gate after record commit + push
python scripts\check_v20x_patch_release.py --source-tree --with-flutter

# Re-verify the published fixed ZIP as-is; never rerun the builder
python scripts\check_v20x_patch_release.py `
  --release-zip "release\DailyRhythmCompanion_20260723_143447.zip" `
  --expected-sha256 "ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1" `
  --expected-source-head "3e4c9f6186ef7195045a445307e14f412924bc26" `
  --with-flutter
```

The accepted M-6 regression boundary verifies:

```text
- `WEB_CORS_ORIGINS=*` preserves the existing local-demo default
- explicit comma- or space-separated origins load into AppConfig
- separator-only values fall back to the local-demo default
- configured origins are passed to FastAPI CORSMiddleware
- allowed preflight origins succeed and unlisted origins are rejected
- credentials remain disabled and existing methods/headers remain wildcarded
- tests remain credential-free and do not import the full production app
- At M-6 acceptance, M-7 through M-9 remained PLANNED
```

The accepted M-7 regression boundary verifies:

```text
- provider roles remain explicit: mock, wearable_stub, fitbit_stub, and legacy fitbit
- local token-like data does not become verified real-use wording
- authorization URL readiness does not become connection-success wording
- existing Fitbit routes and response fields remain compatible
- backend tests use fakes and never access backend/local_data or the network
- Flutter presentation tests remain deterministic
- At M-7 acceptance, M-8 and M-9 remained PLANNED
```

M-7 was accepted on 2026-07-23 after compileall, M-1 through M-7 checks, 38 backend pytest tests, 43 Flutter tests, diff review, and operator approval passed. M-7 did not release v2.0.1.

The M-8 aggregate maintenance boundary verifies:

```text
- the accepted M-7 terminal chain still reaches M-1 through M-6
- compileall and full backend pytest pass in the portable default path
- --with-flutter adds Flutter test for the operator acceptance gate
- backend/local_data is not created or modified
- historical v2.0.0 release-evidence validators are not invoked
- M-9 entry conditions are documented without creating a release artifact
- M-9 remains PLANNED after M-8 acceptance
```

M-8 was accepted on 2026-07-23 after compileall, the aggregate gate with Flutter, 38 backend pytest tests, 43 Flutter tests, diff review, and operator approval passed. M-8 does not build or inspect a ZIP, create a tag or GitHub Release, call real providers, or change runtime/API/Flutter behavior.

The completed M-9 patch release boundary verifies:

```text
- current source records v2.0.1 as RELEASED and M-9 as COMPLETED / ACCEPTED
- DRC_v2.0.0 remains an immutable annotated baseline tag
- DRC_v2.0.1 points to release source HEAD 3e4c9f6186ef7195045a445307e14f412924bc26
- fixed ZIP DailyRhythmCompanion_20260723_143447.zip was built once from detached committed HEAD
- size 1493130 bytes and SHA-256 ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1 are recorded
- the supplied fixed ZIP is tested and hashed without rebuilding
- v2.0.0 historical normalized hashes remain unchanged
- post-publication downloaded-asset SHA-256 matches the recorded value
```

See `docs/v20x_patch_release.md`, `docs/v201_patch_release_record.md`, and `release_notes/v2.0.1.md`.

M-6 does not add authentication, production hosting policy, reverse-proxy configuration, TLS handling, provider calls, Flutter changes, release ZIP work, a tag, or a v2.0.1 release. M-6 was accepted on 2026-07-23 after compileall, M-1 through M-6 checks, 31 backend pytest tests, 39 Flutter tests, diff review, and operator approval passed.

Historical v2.0.0 release-evidence validators remain available for the released/tagged surface. They may intentionally pin v2.0.0 metadata and are not the active current-main regression suite.

## Historical v2.0.0 Public repository migration verification status

The existing Private-repository fixed zip and annotated tag are superseded for Public release use. Public-P0 defines a clean-history repository migration, so the final Public commit SHA will differ from the Private preparation HEAD.

Public-P1 aligns Flutter version `2.0.0+1`, the Web application metadata, and `release_notes/v2.0.0.md` without claiming release completion.

Cleanup-2 removes the duplicate root checklist. All active v2.0.0 checks use `docs/DRC_v200_goal_checklist_small_commit.md` as the only tracked source of truth, and fixed-zip validation no longer requires the former root copy.

Cleanup-3 first pass removes the isolated obsolete v0.25/v0.30 aggregate checks and their superseded release-foundation documents. Current v2.0.0 validators and public-safe configured-operation helpers remain retained. See `docs/v200_public_snapshot_file_retention.md`.

Cleanup-4 moves the retained v1.9.0 release note to `release_notes/v1.9.0.md` and updates all active check/document references.

Public-P2 adds `scripts/smoke_framework_v200_public_distribution_readiness.py`. In the Private repository it validates the clean Public export view, excluding retained Private-only history such as `docs/internal/**`, old patch/diff files, and source-only day checks. With `--release-zip` it validates the supplied fixed ZIP strictly as-is. It checks required Public files, v2.0.0 version/Web metadata, canonical release notes, forbidden local/private artifacts, and obvious sensitive content.

Cleanup-5 removes the obsolete v1.9.0 Day46-Day49 release-chain helpers and v1.9-specific cleanup scripts. Cleanup-6 retires the superseded pre-Web v2.0 readiness paths. Cleanup-7 removes the completed TTS private-run preparation chain while retaining the runtime, public acceptance, marker-template, and final audit surfaces. Cleanup-8 removes the obsolete Day74 collection plan and Day75 intermediate manifest validator; Day80 owns accepted-manifest validation. Cleanup-9 explicitly retains the remaining capability evidence and Day80-Day83/final-artifact audit chain, closing tracked cleanup before export. Public-P3 adds committed-HEAD clean snapshot export and strict exported-directory validation. Current Public source/package checks use Public-P2, while Day82 and Day83 retain final fixed-ZIP ownership.

The current G-7 artifact-record smoke still covers the historical same-repository contract. A later Public migration commit must add or update validators so they require:

```text
- final Public source commit exists before the fixed zip build
- Flutter/package and Web metadata identify v2.0.0 and Daily Rhythm Companion
- release_notes/v2.0.0.md exists
- clean snapshot contains no Private Git history, ignored evidence, local env, or superseded candidate artifact
- final zip is built from the committed Public source
- Day82/Day83 and the Public annotated tag bind that same Public source and zip
```

Public migration procedure: `docs/v200_public_repository_migration.md`

### Cleanup-7 TTS private-run preparation-chain retirement

The D-next-4 through D-next-13 operator runbook, preflight, handoff, checkpoint, and marker-authoring helpers were source-tree preparation tools for a private configured run that is already complete. Cleanup-7 removes those helpers from the Public snapshot.

The retained TTS verification surface begins with the FW v5 runtime/handoff contracts and continues through Day54, Day65, Day77, combined acceptance, acceptance synchronization, and the final Day80-Day83 audit chain.

### Cleanup-8 Day74-Day75 intermediate evidence-chain retirement

Day74 documented a screenshot collection plan and Day75 validated an intermediate private manifest before the final accepted manifest design existed. Day80 now owns the authoritative accepted private evidence manifest contract, so the Day74/Day75 service, smoke, source-only check, docs, and example-template files are retired. Day73 enforcement, Day76-Day79 capability evidence, and Day80-Day83 final audit gates remain retained.

### Cleanup-9 final retention classification

The remaining Day64-Day73 and Day76-Day80 capability evidence, Day82/Day83 fixed-ZIP checks, public-safe templates, acceptance synchronization, and final artifact record are retained as one dependency-bound audit chain. No additional historical/release-process group remains deferred before clean Public snapshot export.

### Public-P3 committed clean snapshot export

```powershell
python scripts\smoke_framework_v200_public_snapshot_export.py

$head = (git rev-parse HEAD).Trim()
python scripts\export_v200_public_snapshot_from_head.py --validate-only --expected-head $head
```

The exporter reads only committed HEAD, requires a clean working tree, applies the Public export policy, and never copies `.git` or ignored evidence. Use `--output-directory` only after Public-P3 is committed. Validate the written directory strictly with:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py --source-directory <PUBLIC_DIR>
```

Public-P3 does not initialize Git, build a release ZIP, create tags, publish GitHub content, or access the network.

### D-next-14 FW v5 public voice output contract alignment

D-next-14 aligns DRC's guarded runtime with the released FW v5 public API shape.

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_real_tts_web_runtime_contract.py
python scripts\smoke_v200_fw_voice_output_boundary_for_drc.py
```

The fake FW fixture now requires `create_voice_output_session(project_root=..., default_voice_profile_id=..., real_tts_enabled=...)`, `VoiceOutputRequest`, `session.create_output(...)`, mp3, and the FW v5 artifact-reference result shape. These checks remain provider-free and audio-free. They do not add the browser audio resolver and do not accept `real_tts_web_audio_output`.

### D-next-15 safe Web audio artifact handoff

D-next-15 places FW-generated mp3 artifacts behind a DRC-owned opaque relative URL and blocks local path exposure.

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_real_tts_web_audio_handoff.py
python scripts\smoke_v200_real_tts_web_runtime_contract.py
python scripts\smoke_v200_fw_voice_output_boundary_for_drc.py
```

The handoff smoke uses a temporary dummy mp3 and checks the opaque URL, actual backend file route, `audio/mpeg`, `no-store`, `nosniff`, managed-directory boundary, unsupported-format rejection, and traversal rejection. It does not call a provider, validate real audio content, start backend/Web, play audio, inspect screenshots, or accept `real_tts_web_audio_output`.

The public repository cleanup rule is:

```text
Keep active checks easy to find.
Keep compatibility coverage documented.
Move historical helpers only after classification.
Do not delete old scripts blindly.
```

---

## C-1a post-advice chat current behavior inventory

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_post_advice_chat_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The accepted C-1a check is credential-free and provider-free. It preserves the historical pre-change inventory and unchanged Framework boundary while allowing the separately checked C-1b Backend files and C-1c Flutter lifecycle/recovery surface.

## C-1b Backend lifecycle and outcome contract

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_post_advice_chat_current_behavior_inventory.py
python scripts\check_v210_post_advice_chat_backend_lifecycle.py
python -m pytest -q backend/tests/test_post_advice_chat_lifecycle.py backend/tests/test_post_advice_chat_outcomes.py backend/tests/test_temporary_lifecycle_config.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The C-1b check is credential-free and provider-free. It verifies the preserved 1800-second TTL, 100-session capacity, LRU behavior, new 8-turn default, structured lifecycle/outcome models, expired/evicted/unknown classification, restartable HTTP 409 turn-limit handling, bounded terminal-reason metadata, deterministic fake-adapter tests, unchanged Flutter runtime, and unchanged release records. C-1b is COMPLETED / ACCEPTED at implementation commit `3055995`; C-1c and parent C-1 are COMPLETED / ACCEPTED at implementation commit `c856374`; T-1 is COMPLETED / ACCEPTED and V-1 is CURRENT / NOT_COMPLETED.

## T-1a TTS player current behavior inventory

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_tts_player_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The T-1a check is source-tree only and provider-free. It pins the accepted Backend artifact-store/audio-route and Flutter voice-output baseline, including opaque MP3 URLs, 86400-second TTL, 100-artifact cap, no-store/nosniff headers, the external URL launch baseline, generic 404 handling, and the pre-T-1 in-app player gap. T-1a is COMPLETED / ACCEPTED at implementation commit `0b06378`. T-1b is COMPLETED / ACCEPTED at implementation commit `161e624` after ten focused Flutter tests, 110 Backend tests, 74 Flutter tests, diff review, operator approval, and push passed. T-1c and parent T-1 are COMPLETED / ACCEPTED; V-1 is CURRENT / NOT_COMPLETED.

## T-1b Flutter audio-player controller contract

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_tts_player_current_behavior_inventory.py
python scripts\check_v210_tts_player_controller.py
python -m pytest -q backend/tests

cd app
flutter test test/voice_output_audio_player_test.dart
flutter test
cd ..
```

The T-1b check is credential-free, provider-free, network-free, and decoder-free. It verifies the adapter-neutral engine interface, explicit playback state model, play/stop/replay/reset/expiry/disposal behavior, stale-operation guard, safe user-facing errors, fake-engine tests, unchanged HomeScreen/Backend/pubspec boundaries, and unchanged release records. T-1b is COMPLETED / ACCEPTED at implementation commit `161e624`; T-1c and parent T-1 are also COMPLETED / ACCEPTED, and V-1 is CURRENT / NOT_COMPLETED.

## T-1c Flutter in-app player integration

```powershell
flutter pub get
python -m compileall -q backend scripts
python scripts\check_v210_tts_player_current_behavior_inventory.py
python scripts\check_v210_tts_player_controller.py
python scripts\check_v210_tts_player_home_integration.py
python -m pytest -q backend/tests

cd app
flutter test test/voice_output_audio_player_test.dart
flutter test test/audioplayers_voice_output_audio_engine_test.dart
flutter test test/voice_output_audio_player_widget_test.dart
flutter test
flutter build web
flutter build windows
cd ..
```

The T-1c source-tree check validates the concrete audioplayers engine boundary, HTTP 404/410 expiry mapping, HomeScreen play/stop/replay/regenerate controls, CMake 3.15 Windows policy, mock-safe engine/widget tests, unchanged Backend runtime, and unchanged release records. Normal automated checks remain provider-free; the separate operator run confirmed real Framework/TTS generation, PC and smartphone audible playback, stop/replay/completion, expiry mapping, regenerate recovery, and raw URL/private-path hiding. T-1c and parent T-1 are COMPLETED / ACCEPTED; V-1 is CURRENT / NOT_COMPLETED.

## C-1c Flutter lifecycle and recovery UI

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_post_advice_chat_current_behavior_inventory.py
python scripts\check_v210_post_advice_chat_backend_lifecycle.py
python scripts\check_v210_post_advice_chat_flutter_lifecycle.py
python -m pytest -q backend/tests

cd app
flutter test test/post_advice_chat_lifecycle_test.dart test/post_advice_chat_lifecycle_widget_test.dart
flutter test
cd ..
```

The C-1c check is credential-free and provider-free. It verifies structured Flutter lifecycle/outcome/problem parsing, legacy payload compatibility, typed HTTP problem handling, turn-progress presentation, terminal send disabling, direct restart after expired/evicted/not-found/turn-limit outcomes, user-facing unavailable/blocked/skipped/fallback distinctions, developer-detail separation, unchanged Backend runtime, and unchanged release records. C-1c and parent C-1 are COMPLETED / ACCEPTED at implementation commit `c856374`; T-1 is COMPLETED / ACCEPTED and V-1 is CURRENT / NOT_COMPLETED.


## Script categories

### Default / mock-safe checks

Default checks should run without external credentials, real Google Health requests, microphone access, TTS providers, Live2D/VTS runtime, or AI Character Framework configuration.

Examples:

```text
scripts/check_release_package.py
```

### Release checks

Release checks protect a fixed release package or release execution flow.

Current protected v1.0.0 release checks:

```text
scripts/check_v100_release_package_day10.py
scripts/check_v100_final_release_day11.py
scripts/check_v100_compatibility_final_sweep_day12.py
```

The fixed v1.0.0 release zip remains:

```text
release\DailyRhythmCompanion_20260520_214945.zip
```

Do not rebuild a fixed release zip while verifying it.

### v1.0.0 scripts cleanup compatibility markers

These markers are intentionally kept because older v1.0.0 readiness checks still validate the scripts cleanup policy text.

```text
Daily Rhythm Companion scripts
configured-only
MERGE
fixed zip path
repository root
secrets
tokens
raw payloads
local_data
docs/quickstart_smartphone_web.md
docs/google_health_real_api_opt_in.md
```


### v1.0.0 public repository hygiene compatibility markers

These markers are intentionally kept because older v1.0.0 public repository hygiene checks still validate the scripts README index.

```text
Public repository hygiene
backend/env_profiles/mock_safe.env
GOOGLE_HEALTH_CREDENTIALS_FILE
credentials.json
```


### v1.0.0 release package compatibility markers

These markers are intentionally kept because older v1.0.0 release package checks still validate the scripts README index.

```text
scripts/check_v100_release_package_day10.py
docs/internal/v100_release_package_day10.md
Current v1.0 release package check
build_release.bat
release mode
handoff mode
source-tree mode
fixed release zip mode
root scripts/
excluded from release zip
Day1-Day10 readiness docs
v1.0 public docs
Do not rebuild during final verification
```

This section preserves compatibility with `scripts/check_v100_release_package_day10.py` while v1.1.0 keeps the updated public repository readiness policy.

### v1.0.0 fixed release zip compatibility markers

These markers are intentionally kept because the v1.0.0 Day10 release package check validates the fixed-zip verification wording exactly.

```text
Build the release zip once
fixed zip path
build_release.bat
record release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip
run release package checks against that exact zip
run final release checks against that exact zip
Do not rebuild during final verification
Release package mode
Source-tree mode
Release-zip mode
root scripts remain excluded from release mode packages
scripts/README.md lists the Day10 check
```

The current v1.1.0 cleanup workflow should keep this wording so v1.0.0 final and compatibility gates remain reproducible.

### v1.0.0 final and compatibility gates

These markers are intentionally kept for v1.0.0 compatibility checks.

```text
docs/internal/v100_final_release_day11.md
Current v1.0 final release check
Do not rebuild during final verification
docs/internal/v100_compatibility_final_sweep_day12.md
Current v1.0 compatibility/final sweep
legacy compatibility skips
Current v1.0 release notes check
release_notes/v1.0.0.md
Current v1.0 release execution check
release\DailyRhythmCompanion_20260520_214945.zip
```

The v1.0.0 final and compatibility scripts are kept as protected release gates while v1.1.0 cleanup proceeds.

### Compatibility checks

Compatibility checks protect old milestone contracts that are still intentionally supported.

They may not be part of the newest default flow, but they should not look like random clutter. Keep the reason documented in roadmap or internal policy docs.

Known policy:

```text
Old v0xx checks should be classified before moving or deleting.
```

### Configured-only checks

Configured-only checks may require optional setup such as:

```text
- AI Character Framework local path
- external LLM provider credentials
- Google Health explicit opt-in configuration
- microphone or voice input setup
- TTS provider setup
- Live2D/VTS runtime setup
```

Configured-only checks must not become mandatory for mock-safe local development.

### v1.3.0 Framework / LLM configured demo checks

v1.3.0 starts from the existing text advice boundary and makes the configured AI Character Framework / LLM path easier to explain and verify.

Current v1.3.0 checks:

```powershell
python scripts\check_v130_framework_llm_configured_demo_day1.py
python scripts\check_v130_framework_llm_configured_demo_day2.py
python scripts\check_v130_framework_llm_configured_demo_day3.py
python scripts\check_v130_framework_llm_configured_demo_day4.py
python scripts\check_v130_framework_llm_configured_demo_day5.py
python scripts\check_v130_framework_llm_configured_demo_day6.py
python scripts\check_v130_framework_llm_configured_demo_day7.py
```

Fixed release zip verification after creating one zip:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v130_framework_llm_configured_demo_day8.py $zip
```

Day3 also adds an optional configured-only smoke:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py
python scripts\smoke_v130_framework_llm_configured_demo.py --create-session
```

Provider-backed ask smoke remains explicit opt-in:

```powershell
$env:DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE = "1"
# Equivalent gate marker: DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE=1
python scripts\smoke_v130_framework_llm_configured_demo.py --ask
```

The Day1-Day4 checks are intentionally mock-safe:

Day5 extends the same mock-safe policy.

The Day1-Day5 checks are intentionally mock-safe:

```text
- does not import AI Character Framework in Day1/Day2 source-tree checks
- does not require a real AI Character Framework checkout
- does not call session.ask() in Day1/Day2 source-tree checks
- does not call external LLM providers
- does not require provider API keys
- verifies configured-only smoke with clear SKIP behavior
- does not call `session.ask()` unless `--ask` is passed
- verifies mock/framework/framework_fallback source-label boundaries from source files and local fake-runtime checks
- verifies configured LLM skip is an operator smoke state, not an AdviceSource.engine value
- verifies fallback wording does not claim configured LLM/provider success
- verifies the FW-backed advice operator checklist for backend status, /advice source labels, DailyRecord save, History review, and optional provider-backed ask smoke
- verifies framework-mode setup docs and framework_local.env.example hygiene
- verifies FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT / FRAMEWORK_PRESET / FRAMEWORK_CHARACTER / FRAMEWORK_ADAPTER_MODE documentation
- verifies the temporary current working directory workaround and FW-side project-root fix direction are documented
```

Configured-only checks must print a clear SKIP when `FRAMEWORK_ROOT`, provider credentials, or explicit configured-demo gates are missing.

The Day6 aggregate check runs Day1-Day5 and clears FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT and provider-key variables for the SKIP fixture before verifying the configured smoke skip path.

The Day7 final source-tree check runs Day6 aggregate readiness and verifies the v1.3.0 docs/check/smoke inventory before release packaging.

The Day8 fixed release zip check requires a zip path argument and inspects the provided zip as-is. It must not create, rebuild, modify, or timestamp-refresh release artifacts.

Final v1.3.0 release readiness and release notes checks reuse the same fixed zip:

```powershell
$zip = "release\DailyRhythmCompanion_20260521_155200.zip"
python scripts\check_v130_framework_llm_configured_demo_day9.py $zip
python scripts\check_v130_framework_llm_configured_demo_day10.py $zip
```


### v1.4.0 Character experience checks

v1.4.0 starts from the existing DRC character contract and makes the demo characters easier to distinguish without turning DRC into a large character platform.

Current v1.4.0 checks:

```powershell
python scripts\check_v140_character_experience_day1.py
python scripts\check_v140_character_experience_day2.py
python scripts\check_v140_character_experience_day3.py
python scripts\check_v140_character_experience_day4.py
python scripts\check_v140_character_experience_day5.py
python scripts\check_v140_character_experience_day6.py
python scripts\check_v140_character_experience_day7.py
python scripts\check_v140_character_experience_day8.py
```

After Day8 passes and the release zip has been built once, verify the fixed zip as-is and then run final release readiness against that same zip:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v140_character_experience_day9.py $zip
python scripts\check_v140_character_experience_day10.py $zip
python scripts\check_v140_character_experience_day11.py $zip
python scripts\check_v140_character_experience_day12.py $zip
```

The v1.4.0 Day1 check is mock-safe. It verifies v1.3.0 released / v1.4.0 in-progress consistency, the Day1 character experience plan, canonical release notes under `release_notes/`, existing character contract fields, mock-safe boundaries, FW mapping constraints, and conservative non-medical wording.

The v1.4.0 Day2 check is mock-safe. It verifies the character profile inventory, stable app-facing fields, tone-hint fields, backend/Flutter character surfaces, and explicit DRC-to-FW mapping without requiring a real FW checkout or provider credentials.

The v1.4.0 Day3 check is mock-safe. It verifies the character advice tone matrix, situation-specific tone differences, deterministic mock-advice direction, and conservative non-medical wording boundaries without requiring a real FW checkout or provider credentials.

The v1.4.0 Day4 check is mock-safe. It verifies the release cleanup checkpoint policy, including generated helper bundles, temporary root notes, stale root release notes, extraction folders, generated cache/build outputs, release zip rebuild drift, and fixed-zip verification hygiene.

The v1.4.0 Day5 check is mock-safe. It verifies character selection UX copy, selection-facing metadata boundaries, alignment with the character inventory and tone matrix, and the requirement that v1.4.0 release packaging reruns the cleanup checkpoint before creating a fixed release zip.

The v1.4.0 Day6 check is mock-safe. It verifies the DRC character_id to AI Character Framework character mapping contract, including default mapping, configured override metadata, fallback behavior, and source-file alignment, without requiring a real FW checkout or provider credentials.

The v1.4.0 Day7 check is mock-safe. It aggregates Day1-Day6 checks, including the Day4 release cleanup checkpoint, and verifies the v1.4.0 source-tree docs/check inventory without creating or rebuilding release artifacts.

The v1.4.0 Day8 check is mock-safe. It is the final pre-release source-tree cleanup verification before fixed release zip packaging, reruns the Day7 aggregate path and cleanup surface checks, and does not create or rebuild release artifacts.

The v1.4.0 Day9 fixed release zip check requires a zip path argument and inspects the provided zip as-is. It verifies v1.4.0 docs/check inventory, canonical release notes, env profile examples, and package hygiene without rebuilding.

The v1.4.0 Day10 final release readiness check requires the same fixed zip path that passed Day9. It reruns Day9 and then runs the protected v1.0.0 release package, final release, default compatibility, and `--compat` compatibility sweeps without rebuilding.

The v1.4.0 Day11 app runtime verification check requires the same fixed zip path that passed Day9 and Day10. It reruns Day10, runs `flutter test` from `app/`, and verifies that `flutter devices` reports a Chrome web device. It does not rebuild the fixed release zip. If Flutter or Chrome verification requires app code changes, rebuild one new fixed zip after rerunning the cleanup gate, then restart Day9 through Day11 with that new zip.

The v1.4.0 Day12 release notes check requires the same fixed zip path that passed Day9 through Day11. It reruns Day11, verifies `release_notes/v1.4.0.md`, records the final verification outputs, and does not rebuild the fixed release zip.


### v1.5.0 Mood and personalization checks

v1.5.0 completed the mood and personalization foundation while preserving mock-safe defaults, stable canonical mood IDs, and conservative health wording.

v1.5.0 checks:

```powershell
python scripts\check_v150_mood_personalization_day1.py
python scripts\check_v150_mood_personalization_day2.py
python scripts\check_v150_mood_personalization_day3.py
python scripts\check_v150_mood_personalization_day4.py
python scripts\check_v150_mood_personalization_day5.py
python scripts\check_v150_mood_personalization_day6.py
python scripts\check_v150_mood_personalization_day7.py
python scripts\check_v150_mood_personalization_day8.py
python scripts\check_v150_mood_personalization_day9.py $zip
python scripts\check_v150_mood_personalization_day10.py $zip
python scripts\check_v150_mood_personalization_day11.py $zip
python scripts\check_v150_mood_personalization_day12.py $zip
```

The v1.5.0 fixed release zip is:

```text
release\DailyRhythmCompanion_20260521_221101.zip
```

Day9 through Day12 verify the same fixed zip as-is and do not rebuild it.

### v1.6.0 Weekly/monthly rhythm reports checks

v1.6.0 starts the weekly/monthly rhythm reports loop. The goal is to expand DailyRecord history from simple review into lightweight reflection while preserving mock-safe defaults and conservative non-medical wording.

Current v1.6.0 checks:

```powershell
python scripts\check_v160_rhythm_reports_day1.py
python scripts\check_v160_rhythm_reports_day2.py
python scripts\check_v160_rhythm_reports_day3.py
python scripts\check_v160_rhythm_reports_day4.py
python scripts\check_v160_rhythm_reports_day5.py
python scripts\check_v160_rhythm_reports_day6.py
python scripts\check_v160_rhythm_reports_day7.py
- `check_v160_rhythm_reports_day8.py` - v1.6.0 final pre-release source-tree cleanup verification.
- `check_v160_rhythm_reports_day9.py` - v1.6.0 fixed release zip verification.
```

The v1.6.0 Day1 check is mock-safe and source-tree only. It verifies v1.5.0 released / v1.6.0 in-progress consistency, the Day1 rhythm reports plan, DailyRecord history boundaries, weekly/monthly summary direction, trend/history wording constraints, source-label direction, and the policy that Day1 does not create or rebuild release artifacts.

Day7 aggregate readiness:

```powershell
python scripts\check_v160_rhythm_reports_day7.py
```

The Day7 aggregate readiness check runs the Day6 check, so the backend/API/Flutter path and Flutter test coverage remain reachable from one command.


### v1.7.0 Rhythm report polish checks

v1.7.0 starts the Rhythm report polish and app-side explanation hardening loop after the completed v1.6.0 weekly/monthly rhythm reports release.

Day1 planning/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day1.py
```

Day2 inventory/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day2.py
```

Day3 copy-contract/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day3.py
```

Day4 Flutter polish/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day4.py
```

Day5 Flutter regression/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day5.py
```

Day6 manual Chrome smoke/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day6.py
```

Day7 aggregate readiness/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day7.py
```

Day8 final pre-release cleanup/check command:

```powershell
python scripts\check_v170_rhythm_report_polish_day8.py
```

Day9 fixed release zip/check command:

```powershell
.\build_release.bat
$zip = Get-ChildItem .\release\DailyRhythmCompanion_*.zip |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

python scripts\check_v170_rhythm_report_polish_day9.py $zip.FullName
```


The v1.7.0 Day1 check is mock-safe and source-tree only. It verifies the post-release consistency update, v1.6.0 fixed release record, v1.7.0 in-progress roadmap, app-side report explanation goals, empty/fallback wording direction, source labels, report range and record count visibility, manual Chrome smoke hardening, conservative non-medical wording, and the rule that Day1 does not create or rebuild release artifacts.

The v1.7.0 Day2 check is mock-safe and source-tree only. It verifies the rhythm report explanation inventory across backend model/service, API payload, Flutter model, History screen card, widget-test coverage, current explanation gaps, and the rule that Day2 does not create or rebuild release artifacts.

The v1.7.0 Day3 check is mock-safe and source-tree only. It reruns the Day2 inventory gate, verifies the rhythm report user-facing copy contract, confirms Day2 remains rerunnable after roadmap progress, and keeps Flutter UI implementation changes deferred to Day4.

The v1.7.0 Day4 check is mock-safe and source-tree only. It reruns the Day3 copy-contract gate, verifies Flutter display helpers, verifies polished weekly/monthly report card copy, verifies widget-test expectations for range/source/coverage/quality labels, and confirms raw report source/scope/quality payload labels are no longer the default card copy.

The v1.7.0 Day5 check is source-tree only except for an optional `flutter test` execution when Flutter is available. It reruns the Day4 gate, verifies focused RhythmReport helper tests, verifies History screen fallback-state widget coverage, and confirms polished report explanation copy stays protected without rebuilding release artifacts.

The v1.7.0 Day6 check is mock-safe and source-tree only except for the optional Day5 `flutter test` path. It reruns the Day5 gate, verifies `docs/app_runtime_verification.md` contains the History screen rhythm report manual Chrome smoke checklist, and confirms the manual smoke guidance covers Weekly/Monthly report cards, range, record coverage, source/scope/quality labels, fallback wording, and raw debug-label avoidance without rebuilding release artifacts.

The v1.7.0 Day7 check is the aggregate v1.7.0 readiness gate for the polish loop. It reruns the Day6 gate, verifies the Day1-Day6 documentation/check inventory, confirms the Flutter model/helper, History screen, widget-test, copy-contract, and manual Chrome smoke guardrails are still present, and keeps the milestone source-tree only before final cleanup and release packaging.

The v1.7.0 Day8 check is the final pre-release source-tree cleanup gate before fixed release zip packaging. It reruns the Day7 aggregate readiness gate, verifies the Day1-Day8 documentation/check inventory, confirms v1.7.0 public docs and Flutter polish files remain present, and fails if temporary v1.7.0 helper bundles, replacement folders, extraction folders, or local release work folders remain in the repository root. Day8 is source-tree only and does not create or rebuild release artifacts.

The v1.7.0 Day9 check is the fixed release zip verification gate. Build the v1.7.0 release zip once after Day8 passes, record the generated path, and pass that exact zip to `scripts/check_v170_rhythm_report_polish_day9.py`. The check reruns Day8, inspects the provided zip as-is, verifies the v1.7.0 docs/checks/Flutter polish inventory, confirms the previous v1.6.0 release record remains included, and fails if temporary helper, cache, build, or generated artifacts are packaged. It does not call `build_release.bat` or rebuild the provided zip.


### v1.8.0 Report-to-advice handoff checks

v1.8.0 starts the Report-to-advice handoff and DailyRecord reflection polish loop after the completed v1.7.0 rhythm report polish release.

Day1 planning/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day1.py
```

Day2 inventory/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day2.py
```

Day3 copy-rule/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day3.py
```

Day4 backend boundary/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day4.py
```

Day5 advice metadata/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day5.py
```

Day6 Flutter display/reflection check command:

```powershell
python scripts\check_v180_report_advice_handoff_day6.py
```

Day7 aggregate readiness/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day7.py
```

Day8 final pre-release cleanup/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day8.py
```

Day9 fixed release zip/check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v180_report_advice_handoff_day8.py

.\build_release.bat

$zip = Get-ChildItem .\release\DailyRhythmCompanion_*.zip |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

python scripts\check_v180_report_advice_handoff_day9.py $zip.FullName
```

The v1.8.0 Day1 check is mock-safe and source-tree only. It verifies the post-release consistency update, v1.7.0 fixed release record, v1.8.0 in-progress roadmap, report-to-advice handoff direction, DailyRecord reflection polish scope, source/data-quality preservation, conservative non-medical wording, mock-safe defaults, and the rule that Day1 does not create or rebuild release artifacts.

The v1.8.0 Day2 check is mock-safe and source-tree only. It reruns Day1, validates `docs/report_advice_handoff_inventory.md`, inventories the current RhythmReport / AdviceRequest / DailyRecord surfaces, records that RhythmReport is not yet passed into advice generation, and checks the smallest safe ReportHandoffContext direction before implementation.

The v1.8.0 Day3 check is mock-safe and source-tree only. It reruns Day2, validates `docs/report_advice_handoff_copy_rules.md`, and verifies user-facing copy rules for report-informed advice, DailyRecord reflection, usable/partial/insufficient report states, source/data-quality explanation, advice_basis display copy, and conservative non-medical wording before implementation.

The v1.8.0 Day4 check is mock-safe and source-tree/runtime only. It reruns Day3, validates `docs/report_handoff_context_backend.md`, imports the new `ReportHandoffContext` boundary, verifies usable/partial/insufficient advice_basis prefix behavior, checks conservative prompt guidance, and confirms `/advice`, `AdviceRequest`, DailyRecord persistence, Flutter runtime behavior, and the fixed v1.7.0 zip remain unchanged.

The v1.8.0 Day5 check is mock-safe and source-tree/runtime only. It reruns Day4, validates `docs/report_advice_handoff_metadata.md`, verifies the optional `AdviceRequest.report_handoff` and `AdviceSource.report_handoff` fields, checks that the prompt builder uses `build_report_handoff_prompt_section`, verifies report-informed `advice_basis` precedence for usable/partial contexts, and confirms insufficient or unsafe report contexts are dropped before prompt generation, response metadata, or DailyRecord persistence. Flutter runtime behavior and the fixed v1.7.0 zip remain unchanged.

The v1.8.0 Day6 check reruns Day5, validates `docs/report_advice_handoff_flutter.md`, verifies `app/lib/models/report_handoff_context.dart`, checks Flutter-side `AdviceSource` and `DailyRecord` display helpers, confirms Home advice result and History DailyRecord reflection use user-facing report context copy, and runs `flutter test` when Flutter is available. If Flutter is unavailable in a minimal source-tree environment, it reports a skip after source-tree checks pass. Day6 does not automatically fetch RhythmReport from Home or rebuild the fixed v1.7.0 zip.

The v1.8.0 Day7 check is the aggregate v1.8.0 readiness gate for the report-to-advice handoff loop. It reruns Day6, validates the Day1-Day6 documentation/check inventory, confirms backend `ReportHandoffContext`, advice metadata, Flutter `ReportHandoffContext`, Home advice context display, History DailyRecord reflection, and widget/model-test guardrails remain present, and stays source-tree only before final cleanup and release packaging.

The v1.8.0 Day8 check is the final pre-release source-tree cleanup gate before fixed release zip packaging. It reruns Day7, validates the Day1-Day8 documentation/check inventory, confirms the v1.8.0 public handoff docs, backend handoff boundary, advice metadata, Flutter display/reflection files, and report handoff tests remain present, and fails if temporary v1.8.0 helper bundles, replacement folders, extraction folders, or local release work folders remain in the repository root. Day8 is source-tree only and does not create or rebuild release artifacts.

The v1.8.0 Day9 check is the fixed release zip verification gate. Build the release zip once after Day8 passes, record the printed path, and pass that exact artifact to the check. It reruns the Day8 cleanup gate, inspects the provided zip as-is, verifies Day1-Day9 v1.8.0 docs/check files plus the backend and Flutter report handoff surfaces are included, and confirms obvious temporary/helper/generated artifacts are absent. Day9 does not call `build_release.bat` or rebuild the provided zip.

### v1.9.0 Day6 smartphone Web API base URL configuration check

Day6 adds a runtime-facing Flutter Web configuration path for smartphone Web demonstration.

Primary Day6 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day6.py
```

Day6 verifies:

```text
- BackendApiClient can read DRC_BACKEND_API_BASE_URL through String.fromEnvironment.
- BackendApiClient keeps http://127.0.0.1:8000 as the default desktop-local base URL.
- HomeScreen displays the active API base URL.
- Widget tests cover default and configured API base URL display.
- docs include a smartphone-Web-oriented flutter run command with --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000.
```

The Day6 check also reruns the Day5 check, which reruns Day4, Day3, Day2, and Day1.


### v1.9.0 Day10 Flutter post-advice chat UI check

Day10 wires the mock-safe post-advice chat API into the Flutter Web UI.

Primary Day10 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day10.py
```

Day10 verifies:

```text
- app/lib/models/chat.dart parses ChatSession, ChatMessage, ChatSource, and ChatMessageResponse.
- BackendApiClient can create a post-advice chat session and send a chat message.
- HomeScreen shows the Post-advice Chat section after advice.
- HomeScreen exposes 少し話す / 今日はここまで.
- HomeScreen shows Chat session, Chat source, messages, message input, and send button.
- widget tests cover starting mock-safe chat, sending a message, and skipping chat.
- The flow remains mock-safe and provider-free.
```

The Day10 check also reruns the Day9 check, which reruns Day8 through Day1.


### v1.9.0 Day9 mock-safe post-advice chat API check

Day9 implements the first mock-safe backend boundary for the post-advice chat continuation flow.

Primary Day9 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day9.py
```

Day9 verifies that the backend defines:

```text
- PostAdviceChatContext
- ChatSession / ChatMessage / ChatSource
- POST /chat/sessions
- GET /chat/sessions/{session_id}
- POST /chat/sessions/{session_id}/messages
- app.include_router(chat.router)
- mock-safe provider-free PostAdviceChatService
```

The Day9 check also reruns the Day8 check, which reruns Day7 through Day1.


### v1.9.0 Day41 TTS / voice output smartphone Web boundary evidence record check

Primary Day41 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day41.py
```

Day41 adds:

```text
backend/app/services/framework_voice_output_smartphone_web_boundary_evidence_record.py
scripts/smoke_framework_voice_output_smartphone_web_boundary_evidence_record.py
docs/framework_voice_output_smartphone_web_boundary_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day41.md
scripts/check_v190_smartphone_web_fw_demo_day41.py
```

Expected marker:

```text
v190_voice_output_smartphone_web_boundary_record_status: recorded
v190_voice_output_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-voice-output-boundary-evidence
```

Configured TTS runtime execution remains separate. Day41 checks do not synthesize speech, generate audio files, play audio, call providers, connect to Live2D/VTS, or dispatch motion.

### v1.9.0 Day40 TTS / voice output smartphone Web boundary evidence check

Primary Day40 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day40.py
```

Day40 adds:

```text
backend/app/services/framework_voice_output_smartphone_web_boundary_evidence.py
scripts/smoke_framework_voice_output_smartphone_web_boundary_evidence.py
docs/framework_voice_output_smartphone_web_boundary_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day40.md
scripts/check_v190_smartphone_web_fw_demo_day40.py
```

Expected marker:

```text
voice_output_smartphone_web_boundary_evidence_status: verified
voice_output_smartphone_web_boundary_next_step: record-manual-smartphone-web-voice-output-boundary-evidence
```

Day40 checks do not call configured TTS runtime execution, start Flutter, open a browser, call providers, synthesize speech, generate audio files, play audio, connect to Live2D/VTS, or dispatch motion.

### v1.9.0 Day39 FW4.0.0 capability coverage after voice input evidence check

Primary Day39 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day39.py
```

Day39 adds:

```text
backend/app/services/framework_fw40_capability_coverage_after_voice_input.py
scripts/smoke_framework_fw40_capability_coverage_after_voice_input.py
docs/framework_fw40_capability_coverage_after_voice_input.md
docs/internal/v190_smartphone_web_fw_demo_day39.md
scripts/check_v190_smartphone_web_fw_demo_day39.py
```

Expected marker:

```text
v190_fw40_capability_coverage_after_voice_input_status: text-chat-and-voice-input-boundary-evidence-complete-remaining-boundaries-pending
v190_fw40_capability_coverage_after_voice_input_next_focus: tts_voice_output
```

Day39 checks do not call configured STT runtime execution, start Flutter, open a browser, call providers, touch microphones, upload audio, generate audio, connect to Live2D/VTS, or dispatch motion.

### v1.9.0 Day38 STT / voice input smartphone Web boundary evidence record check

Primary Day38 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day38.py
```

Day38 adds:

```text
backend/app/services/framework_voice_input_smartphone_web_boundary_evidence_record.py
scripts/smoke_framework_voice_input_smartphone_web_boundary_evidence_record.py
docs/framework_voice_input_smartphone_web_boundary_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day38.md
scripts/check_v190_smartphone_web_fw_demo_day38.py
```

Expected marker:

```text
v190_voice_input_smartphone_web_boundary_record_status: recorded
```

Manual evidence command after a smartphone Web UI check:

```powershell
python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence_record.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --voice-input-section-visible `
  --voice-input-button-visible `
  --voice-input-request-sent `
  --voice-input-response-visible `
  --capability-status-visible `
  --checks-visible `
  --audio-processing-blocked `
  --microphone-not-used `
  --raw-audio-not-uploaded `
  --transcript-body-hidden-or-absent
```

Configured STT runtime execution remains separate. Day38 checks do not open microphones, upload audio, call STT providers, or store transcript bodies.

### v1.9.0 Day37 STT / voice input smartphone Web boundary evidence check

Primary Day37 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day37.py
```

Day37 adds:

```text
backend/app/services/framework_voice_input_smartphone_web_boundary_evidence.py
scripts/smoke_framework_voice_input_smartphone_web_boundary_evidence.py
docs/framework_voice_input_smartphone_web_boundary_evidence.md
```

Source-tree boundary smoke:

```powershell
python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence.py
```

Manual smartphone Web boundary evidence can be recorded with boolean flags only:

```powershell
python scripts\smoke_framework_voice_input_smartphone_web_boundary_evidence.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --voice-input-section-visible `
  --voice-input-button-visible `
  --voice-input-request-sent `
  --voice-input-response-visible `
  --capability-status-visible `
  --checks-visible `
  --audio-processing-blocked `
  --microphone-not-used `
  --raw-audio-not-uploaded `
  --transcript-body-hidden-or-absent
```

The renderer reports `voice_input_smartphone_web_boundary_evidence_status: verified`. Configured STT runtime execution remains separate and requires a future explicit opt-in decision.

### v1.9.0 Day36 FW4.0.0 capability coverage checkpoint check

Primary Day36 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day36.py
```

Day36 adds:

```text
backend/app/services/framework_fw40_capability_coverage_checkpoint.py
scripts/smoke_framework_fw40_capability_coverage_checkpoint.py
docs/framework_fw40_capability_coverage_checkpoint.md
```

Source-tree capability coverage smoke:

```powershell
python scripts\smoke_framework_fw40_capability_coverage_checkpoint.py
```

The renderer reports `v190_fw40_capability_coverage_status: text-chat-complete-boundary-capabilities-pending` and records that the next focus is STT / voice input. No provider, microphone, audio, VTube Studio, or motion runtime is called.

### v1.9.0 Day35 FW text-chat smartphone Web completion evidence check

Primary Day35 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day35.py
```

Day35 adds:

```text
backend/app/services/framework_text_chat_v190_completion_evidence.py
scripts/smoke_framework_text_chat_v190_completion_evidence.py
docs/framework_text_chat_v190_completion_evidence.md
```

Source-tree completion evidence smoke:

```powershell
python scripts\smoke_framework_text_chat_v190_completion_evidence.py
```

The renderer reports `v190_fw40_text_chat_smartphone_web_completion_status: completed` for the public-safe FW4.0.0 LLM/text-chat smartphone Web proof chain. Prompt and response bodies remain hidden from evidence output.

### v1.9.0 Day34 smartphone Web UI live FW reply evidence record check

Primary Day34 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day34.py
```

Day34 adds:

```text
backend/app/services/framework_text_chat_smartphone_web_ui_evidence_record.py
scripts/smoke_framework_text_chat_smartphone_web_ui_evidence_record.py
docs/framework_text_chat_smartphone_web_ui_evidence_record.md
```

Source-tree evidence record smoke:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence_record.py
```

Optional manual smartphone Web UI record rendering after local strict UI verification:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence_record.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --advice-result-visible `
  --post-advice-chat-visible `
  --chat-source-visible `
  --live-reply-visible `
  --response-non-empty `
  --body-hidden
```

The renderer may report `v190_smartphone_web_ui_live_reply_record_status: recorded` and `v190_smartphone_web_ui_live_reply_record_source_mode: framework_text_chat_live_message`. Prompt and response bodies are hidden from evidence output.

### v1.9.0 Day33 smartphone Web UI live FW reply evidence check

Primary Day33 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day33.py
```

Day33 adds:

```text
backend/app/services/framework_text_chat_smartphone_web_ui_evidence.py
scripts/smoke_framework_text_chat_smartphone_web_ui_evidence.py
docs/framework_text_chat_smartphone_web_ui_evidence.md
```

Source-tree evidence smoke:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence.py
```

Manual smartphone Web UI evidence rendering after local strict UI verification:

```powershell
python scripts\smoke_framework_text_chat_smartphone_web_ui_evidence.py `
  --record-manual-ui-evidence `
  --backend-status-ok `
  --api-base-url-visible `
  --advice-result-visible `
  --post-advice-chat-visible `
  --chat-source-visible `
  --live-reply-visible `
  --response-non-empty `
  --body-hidden
```

The renderer may report `smartphone_web_ui_live_reply_evidence_status: verified` and `smartphone_web_ui_live_reply_source_mode: framework_text_chat_live_message`. Prompt and response bodies are hidden from evidence output.


### v1.9.0 Day32 DRC adapter live FW text-chat reply wiring check

Primary Day32 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day32.py
```

Day32 adds:

```text
backend/app/services/framework_text_chat_drc_live_reply.py
scripts/smoke_framework_text_chat_drc_adapter_live_reply.py
docs/framework_text_chat_drc_adapter_live_reply.md
```

Source-tree adapter/API smoke:

```powershell
python scripts\smoke_framework_text_chat_drc_adapter_live_reply.py
```

Optional strict local adapter/API smoke:

```powershell
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE="1"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"
python scripts\smoke_framework_text_chat_drc_adapter_live_reply.py --require-real-framework
```

The smoke may report `drc_adapter_live_reply_source_mode: framework_text_chat_live_message`. Prompt and response bodies are hidden from smoke output.


### v1.9.0 Day31 framework live text-chat message evidence check

Primary Day31 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day31.py
```

Day31 adds:

```text
backend/app/services/framework_text_chat_live_message_evidence.py
scripts/smoke_framework_text_chat_live_message_evidence.py
docs/framework_text_chat_live_message_evidence.md
```

Source-tree evidence smoke:

```powershell
python scripts\smoke_framework_text_chat_live_message_evidence.py
```

Optional strict local evidence smoke after Day30 gates are enabled:

```powershell
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"
python scripts\smoke_framework_text_chat_live_message_evidence.py --require-real-framework
```

The evidence may report `live_text_chat_message_evidence_status: verified` after one bounded Day30 live-message smoke reports `live_text_chat_message_smoke_status: responded`. Prompt and response bodies are hidden.


### v1.9.0 Day30 framework live text-chat message smoke check

Primary Day30 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day30.py
```

Day30 adds:

```text
backend/app/services/framework_text_chat_live_message_smoke.py
scripts/smoke_framework_text_chat_live_message.py
docs/framework_text_chat_live_message_smoke.md
```

Source-tree smoke:

```powershell
python scripts\smoke_framework_text_chat_live_message.py
```

Optional strict local smoke after Day29 gate is enabled:

```powershell
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
$env:DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE="1"
python scripts\smoke_framework_text_chat_live_message.py --require-real-framework
```

The strict smoke may report `live_text_chat_message_smoke_status: responded` after one bounded message. It can also report `live_text_chat_message_smoke_status: blocked` or `blocked-provider-env-placeholder` before a provider call. Prompt and response bodies are hidden.


### v1.9.0 Day29 framework live text-chat message gate check

Primary Day29 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day29.py
```

Day29 adds:

```text
backend/app/services/framework_text_chat_live_message_gate.py
scripts/smoke_framework_text_chat_live_message_gate.py
docs/framework_text_chat_live_message_gate.md
```

Source-tree smoke:

```powershell
python scripts\smoke_framework_text_chat_live_message_gate.py
```

Optional strict gate command after Day28 session-created evidence is ready:

```powershell
python scripts\smoke_framework_text_chat_live_message_gate.py --require-real-framework
```

The gate output includes `live_text_chat_message_gate_status: blocked` by default and can report `live_text_chat_message_gate_status: ready` only when `DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1` is explicitly set locally. Day29 does not call ask, ask_stream, or provider APIs.


### v1.9.0 Day28 framework text chat session created evidence check

Primary Day28 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day28.py
```

Day28 adds:

```text
backend/app/services/framework_text_chat_session_created_evidence.py
scripts/smoke_framework_text_chat_session_created_evidence.py
docs/framework_text_chat_session_created_evidence.md
```

Source-tree smoke:

```powershell
python scripts\smoke_framework_text_chat_session_created_evidence.py
```

Optional strict evidence command after local provider env readiness is ready:

```powershell
python scripts\smoke_framework_text_chat_session_created_evidence.py --require-real-framework
```

The evidence shape includes `session_created_evidence_status: created` and `session_created_evidence_next_step: design-explicit-live-text-chat-message-gate`. It does not call ask, ask_stream, or provider APIs, and it must not print API key values.

### v1.9.0 Day27 framework text chat provider env local opt-in check

Primary Day27 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day27.py
```

Day27 adds:

```text
scripts/smoke_framework_text_chat_provider_env_operator_opt_in.py
docs/framework_text_chat_provider_env_local_opt_in.md
```

Local operator readiness command:

```powershell
python scripts\smoke_framework_text_chat_provider_env_operator_opt_in.py --check-local --required-env GOOGLE_API_KEY
```

The script prints provider env names and `set=True|False` only. It does not call ask, ask_stream, or provider APIs, and it must not print API key values.

### v1.9.0 Day26 framework text chat provider env readiness check

Day26 adds a public-safe readiness gate for the Day25 provider-env-missing blocker.

Primary Day26 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day26.py
```

Provider env readiness smoke:

```text
scripts/smoke_framework_text_chat_provider_env_readiness.py
```

Day26 verifies:

```text
- GOOGLE_API_KEY readiness is represented by env var names and boolean set/unset status only.
- API key values are not printed, persisted, or returned.
- Strict session diagnosis output can include provider_env_readiness_status for provider-env-missing.
- Day26 remains preflight/readiness only and does not call ask, ask_stream, or provider APIs.
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day26.py

cd app
flutter test
cd ..
```

Optional local readiness check after setting provider env values locally only:

```powershell
python scripts\smoke_framework_text_chat_provider_env_readiness.py --required-env GOOGLE_API_KEY
```

The Day26 check also reruns the Day25 check, which reruns Day24 through Day1.

### v1.9.0 Day25 framework text chat provider env diagnosis check

Day25 records the next strict configured session-creation blocker after the Day24 import setup fix.

Primary Day25 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day25.py
```

Provider env diagnosis smoke:

```text
scripts/smoke_framework_text_chat_provider_env_diagnosis.py
```

Day25 verifies:

```text
- The strict configured session failure `GOOGLE_API_KEY is not defined.` is classified as provider-env-missing.
- Provider env readiness is represented by env var names and boolean set/unset status only.
- API key values are not printed, persisted, or returned.
- Session diagnosis output includes failure_kind.
- Day25 remains preflight/diagnosis only and does not call ask, ask_stream, or provider APIs.
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day25.py

cd app
flutter test
cd ..
```

The Day25 check also reruns the Day24 check, which reruns Day23 through Day1.

### v1.9.0 Day24 framework text chat session import setup check

Day24 applies the Day23 import layout evidence to the session-creation diagnosis path.

Primary Day24 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day24.py
```

Updated session diagnosis smoke:

```text
scripts/smoke_framework_text_chat_session_creation_diagnosis.py
```

Day24 verifies:

```text
- Framework text chat import setup is centralized in framework_text_chat_import_setup.py.
- The setup keeps configured sys.path roots active through create_text_chat_session.
- The fake framework smoke performs a lazy top-level import registry during session creation.
- The smoke no longer treats registry ModuleNotFoundError as the expected next blocker.
- Day24 remains preflight/diagnosis only and does not call ask, ask_stream, or provider APIs.
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day24.py

cd app
flutter test
cd ..
```

The Day24 check also reruns the Day23 check, which reruns Day22 through Day1.

### v1.9.0 Day23 vendor framework import layout diagnosis check

Day23 adds a source-tree-safe diagnosis for the vendored FW4.0.0 package/import layout behind the `registry` blocker.

Primary Day23 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day23.py
```

Source-tree diagnosis smoke:

```text
scripts/smoke_framework_text_chat_import_layout_diagnosis.py
```

Day23 verifies:

```text
- FrameworkTextChatImportLayoutDiagnosisService exists.
- The smoke uses a temporary fake framework checkout.
- Candidate layouts include configured-root-only, framework-package-dir-only, and a combined layout.
- Public-safe fields include framework_spec_status and registry_spec_status.
- The diagnosis records whether DRC adapter sys.path handling can absorb the issue or whether FW packaging/import-layout feedback is needed.
- The diagnosis does not create framework sessions or call ask, ask_stream, or provider APIs.
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day23.py

cd app
flutter test
cd ..
```

The Day23 check also reruns the Day22 check, which reruns Day21 through Day1.

### v1.9.0 Day22 goal alignment checkpoint check

Day22 verifies that v1.9.0 remains aligned with the DRC smartphone Web FW4.0.0 demo goal.

Primary Day22 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day22.py
```

Day22 verifies:

```text
- DRC is documented as a public demo app for AI Character Framework v4.0.0
- smartphone Web verification through actual DRC backend APIs remains the goal
- LLM/text chat, STT, TTS, and Live2D/VTS remain the FW4.0.0 capability targets
- general app-store consumer release remains v2.0.0+
- registry import diagnosis is scoped only to the LLM/text chat demo blocker
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day22.py

cd app
flutter test
cd ..
```

The Day22 check also reruns the Day21 check, which reruns Day20 through Day1.


### v1.9.0 Day21 vendor framework session creation FacadeConfigError diagnosis check

Strict configured evidence recorded:

```text
docs/framework_text_chat_session_creation_diagnosis_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day21_evidence.md
```

Recorded result:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
likely_cwd_dependency -> False
```


Day21 adds a safe diagnosis script for the `FacadeConfigError` observed when attempting strict vendor framework session creation.

Primary Day21 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day21.py
```

Source-tree diagnosis smoke:

```text
scripts/smoke_framework_text_chat_session_creation_diagnosis.py
```

Strict configured operator run:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

Day21 verifies:

```text
- current-cwd and framework-root-cwd attempts are compared
- FacadeConfigError can be captured safely
- safe_message redacts private paths and secrets
- likely_cwd_dependency can be detected
- ask and ask_stream are not called
- provider APIs are not called
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day21.py

cd app
flutter test
cd ..
```

The Day21 check also reruns the Day20 check, which reruns Day19 through Day1.


### v1.9.0 Day20 framework text chat session creation preflight check

Day20 adds a safe session creation preflight for framework text chat.

Primary Day20 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day20.py
```

Source-tree smoke:

```text
scripts/smoke_framework_text_chat_session_creation_preflight.py
```

Strict configured operator run:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_preflight.py --require-real-framework
```

Day20 verifies:

```text
- create_text_chat_session can be called in a fake-framework smoke
- a session object is created
- session info is visible
- ask and ask_stream are not called
- provider APIs are not called
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day20.py

cd app
flutter test
cd ..
```

The Day20 check also reruns the Day19 check, which reruns Day18 through Day1.


### v1.9.0 Day19 vendor framework checkout preflight evidence check

Day19 records the strict configured preflight evidence for the vendored AI Character Framework v4.0.0 checkout.

Primary Day19 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day19.py
```

Recorded strict preflight result:

```text
[smoke-framework-text-chat-configured-preflight] OK
module: framework
project_root_shape: <configured-framework-root>
has_create_text_chat_session: True
has_text_chat_session_class: True
No session was created and no provider call was made.
```

Public-safe checkout shape:

```text
vendor/AI-Character-Framework_v4.0.0
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day19.py

cd app
flutter test
cd ..
```

The Day19 check also reruns the Day18 check, which reruns Day17 through Day1.


### v1.9.0 Day18 configured framework text chat local import preflight smoke check

Day18 adds an operator-facing smoke script for the real framework checkout local import preflight.

Primary Day18 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day18.py
```

Configured smoke:

```text
scripts/smoke_framework_text_chat_configured_preflight.py
```

Default skip-safe run:

```powershell
python scripts\smoke_framework_text_chat_configured_preflight.py
```

Strict operator run:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_configured_preflight.py --require-real-framework
```

Day18 verifies:

```text
- real framework checkout import preflight is available as an explicit operator smoke
- default behavior is skipped unless the preflight gate is enabled
- --require-real-framework fails if the framework checkout is missing or unavailable
- create_text_chat_session visibility can be checked without calling it
- no text chat session is created
- no provider APIs are called
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day18.py

cd app
flutter test
cd ..
```

The Day18 check also reruns the Day17 check, which reruns Day16 through Day1.


### v1.9.0 Day17 framework text chat local import preflight check

Day17 verifies a safe local import preflight boundary for future configured framework text chat.

Primary Day17 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day17.py
```

Additional smoke:

```text
scripts/smoke_framework_text_chat_local_import_preflight.py
```

Day17 verifies:

```text
- DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=0 exists in the configured env example
- framework_text_chat_preflight_enabled is loaded in backend config
- FrameworkTextChatPreflightService can return skipped/unavailable/available preflight states
- available state is tested with a temporary fake framework module
- create_text_chat_session visibility can be checked without calling it
- no real AI Character Framework session is created
- no provider APIs are called
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day17.py

cd app
flutter test
cd ..
```

The Day17 check also reruns the Day16 check, which reruns Day15 through Day1.


### v1.9.0 Day16 framework text chat unavailable UI verification check

Day16 verifies the safe unavailable state for the configured framework text chat boundary.

Primary Day16 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day16.py
```

Additional backend smoke:

```text
scripts/smoke_post_advice_framework_text_chat_unavailable.py
```

Day16 verifies:

```text
- framework text chat gate enabled does not claim configured success
- backend service can return framework_text_chat_unavailable safely
- Flutter widget test can show framework / framework_text_chat_unavailable in Chat source
- unavailable guidance is visible
- no AI Character Framework import or execution happens on Day16
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day16.py

cd app
flutter test
cd ..
```

The Day16 check also reruns the Day15 check, which reruns Day14 through Day1.


### v1.9.0 Day15 framework text chat adapter skeleton check

Day15 verifies the backend skeleton for configured AI Character Framework text chat.

Primary Day15 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day15.py
```

Day15 verifies:

```text
- DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE remains the explicit opt-in gate
- framework_text_chat_smoke_enabled is loaded in backend config
- FrameworkPostAdviceChatAdapter and FrameworkTextChatResult exist
- post-advice chat remains mock-safe by default
- configured gate routes through the framework adapter boundary
- enabled-but-not-configured framework text chat returns safe unavailable/skipped states
- no AI Character Framework import or execution happens on Day15
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day15.py
cd app
flutter test
cd ..
```

The Day15 check also reruns the Day14 check, which reruns Day13 through Day1.


### v1.9.0 Day14 configured AI Character Framework text chat boundary check

Day14 defines the safe boundary for moving post-advice chat from mock-safe behavior toward configured AI Character Framework text chat.

Primary Day14 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day14.py
```

Day14 verifies that docs and env examples define:

```text
- explicit opt-in gate: DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=0
- post-advice chat UI remains mock-safe by default
- configured framework text chat requires explicit opt-in
- request context can include character, mood, advice message, advice basis, AdviceSource, report_handoff, and chat history
- configured success requires backend API call, framework text chat path, Web UI visible response, and safe evidence
- mock chat is not configured framework text chat success
- framework fallback is not configured framework text chat success
- unavailable / skipped / fallback / error are visible states but not configured success
- public evidence must not include secrets, tokens, raw provider payloads, private paths, or private LAN IP values
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day14.py
cd app
flutter test
```

The Day14 check also reruns the Day13 check, which reruns Day12 through Day1.


### v1.9.0 Day13 smartphone Web post-advice chat evidence record check

Day13 records the confirmed smartphone Web post-advice chat manual result in a public-safe form.

Primary Day13 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day13.py
```

Day13 verifies that docs define:

```text
- release build static hosting was used as the runtime shape
- smartphone Web DRC Home was visible
- Backend status: ok was visible
- API base URL was visible with placeholder URL shape http://<PC_LAN_IP>:8000
- advice result was visible
- Post-advice Chat was visible
- 少し話す flow was started
- Chat session was visible
- user message was visible
- character response was visible
- Chat source was visible
- result is mock-safe smartphone Web post-advice chat UI verified
- result does not claim configured real LLM/FW chat success
- public evidence does not contain private LAN IP values, secrets, tokens, private paths, or raw provider payloads
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day13.py
cd app
flutter test
```

The Day13 check also reruns the Day12 check, which reruns Day11 through Day1.


### v1.9.0 Day12 smartphone Web post-advice chat manual evidence check

Day12 defines how to safely record manual smartphone Web evidence for the post-advice chat flow.

Primary Day12 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day12.py
```

Day12 verifies that docs define:

```text
- release build static hosting as the recommended smartphone Web runtime path
- smartphone browser URL shape http://<PC_LAN_IP>:18080
- safe evidence fields for Backend status: ok, API base URL, advice result, Post-advice Chat, 少し話す, message send, user message, character response, and Chat source
- a public-safe evidence summary that uses placeholder URL shapes, not private LAN IP values
- a clear distinction that mock-safe smartphone Web chat UI evidence is not configured real LLM/FW chat success
- non-exposure rules for secrets, tokens, authorization headers, raw provider payloads, private credential paths, private absolute paths, and private LAN IP values
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day12.py
cd app
flutter test
```

The Day12 check also reruns the Day11 check, which reruns Day10 through Day1.


### v1.9.0 Day11 smartphone Web post-advice chat verification check

Day11 defines the smartphone Web manual verification requirements for the post-advice chat UI path.

Primary Day11 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day11.py
```

Day11 verifies that docs and code define:

```text
- release build static hosting for smartphone Web verification
- smartphone URL shape http://<PC_LAN_IP>:18080
- UI evidence for backend status ok and API base URL
- UI evidence for advice result
- UI evidence for Post-advice Chat
- UI evidence for "少し話す" and "今日はここまで"
- UI evidence for Chat session, message input, user message, character response, and Chat source
- distinction that mock-safe chat UI verification is not configured real LLM/FW chat success
- Flutter widget test coverage for post-advice chat starts after advice and shows mock response
```

Suggested verification:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day11.py
cd app
flutter test
```

The Day11 check also reruns the Day10 check, which reruns Day9 through Day1.


### v1.9.0 Day8 post-advice chat continuation flow inventory check

Day8 restores the intended post-advice chat continuation flow to the roadmap.

Primary Day8 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day8.py
```

Day8 verifies that docs define:

```text
- current implemented flow: sleep / mood / character -> advice -> DailyRecord save -> History review
- missing intended flow: advice result -> "少し話す？" / "今日はここまで" -> optional character chat continuation
- future backend boundaries: ChatSession, ChatMessage, post-advice context, mock-safe chat response, configured AI Character Framework text chat
- future Web UI surfaces: post-advice prompt, chat panel/screen, message input, character response, end/save relation
- future DailyRecord / History relation policy for chat context
- smartphone Web UI evidence rules for post-advice chat
- Day7 release build static hosting recommendation for smartphone Web evidence
```

The Day8 check also reruns the Day7 check, which reruns Day6 through Day1.


### v1.9.0 Day7 smartphone Web manual runtime checklist check

Day7 defines the manual smartphone Web runtime checklist for the FW4.0.0 demo path.

Primary Day7 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day7.py
```

Day7 verifies that docs define:

```text
- backend LAN startup with python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
- Flutter Web LAN startup with flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080
- smartphone Web API base URL injection with --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
- smartphone browser access through http://<PC_LAN_IP>:8080
- UI evidence for API base URL, backend connection, characters, sleep summary, advice, DailyRecord save, History review, demo status, voice input, voice output, motion, and health data
- safe manual evidence rules with no secrets, tokens, authorization headers, private credential paths, raw provider payloads, or private absolute paths
```

The Day7 check also reruns the Day6 check, which reruns Day5 through Day1.


### v1.9.0 Day5 Web UI verification evidence rules check

Day5 defines the evidence rules for smartphone Web / browser UI verification.

Primary Day5 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day5.py
```

Day5 verifies that docs define:

```text
- API success alone is not enough.
- Web UI visible result is required for demo completion.
- LLM evidence appears in advice result/source/fallback UI.
- STT evidence appears in recognized text or unavailable/skipped UI.
- TTS evidence appears in voice output status, result, or playback state UI.
- Live2D/VTS evidence appears in motion trigger/status or visible motion evidence.
- Google Health evidence appears in health data or safe unavailable/error UI.
- DailyRecord and History evidence appear after save/review.
- report-informed advice/reflection evidence appears when report handoff is used.
- configured success must be separated from fallback, unavailable, skipped, and error.
- shared manual evidence must not include secrets, tokens, authorization headers, private credential paths, raw provider payloads, or full provider debug traces.
```

The Day5 check also reruns the Day4 check, which reruns Day3, Day2, and Day1.


### v1.9.0 Day4 configured real API environment profile check

Day4 documents the configured real API environment profile for later FW4.0.0 smartphone Web demo verification.

Primary Day4 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day4.py
```

Day4 verifies placeholder-only env examples and non-exposure guardrails:

```text
- backend/env_profiles/fw40_configured_real_api.env.example exists.
- docs/fw40_configured_real_api_profile.md exists.
- configured real API placeholders cover OpenAI, Gemini, Grok, ElevenLabs, and Google Health API.
- explicit opt-in gates exist for configured real API checks.
- mock-safe default checks remain separate from configured real API checks.
- public docs and placeholder-only env examples do not contain obvious real secrets, tokens, authorization headers, raw provider payloads, or private absolute paths.
```

The Day4 check also reruns the Day3 check, which reruns Day2 and Day1.


### v1.9.0 Day3 FW4.0.0 capability surface inventory check

Day3 maps each required FW4.0.0-era capability to the current DRC backend, Web UI, and configuration surfaces.

Primary Day3 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day3.py
```

Capability targets:

```text
- LLM
- STT / voice input
- TTS / voice output
- Live2D / VTS motion
```

Day3 verifies that the inventory documents:

```text
- LLM uses /advice, AdviceSource, framework/fallback labels, and the Home advice result UI.
- STT / voice input uses /demo/voice-input, VOICE_INPUT_DEMO_ENABLED, and the Home voice input demo UI.
- TTS / voice output uses /demo/voice-output, VOICE_OUTPUT_DEMO_ENABLED, and the Home voice output demo UI.
- Live2D / VTS motion uses /demo/motion, MOTION_DEMO_ENABLED, and the Home motion demo UI.
- Request/status wiring is not the same thing as configured real execution proof.
- skipped / unavailable / fallback must not be counted as configured real execution success.
```

The Day3 check also reruns the Day2 check, which reruns the Day1 check.


### v1.9.0 Day2 smartphone Web runtime inventory check

Day2 records the current implementation state for smartphone Web runtime verification.

Primary Day2 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day2.py
```

Day2 verifies that the repository documents and exposes the current runtime inventory:

```text
- Flutter Web uses BackendApiClient for backend API calls.
- BackendApiClient currently defaults to http://127.0.0.1:8000.
- This local default is not enough by itself for smartphone Web demonstration.
- The Web UI already has visible surfaces for backend connection, characters, advice, DailyRecord save, demo status, voice input demo, voice output demo, motion demo, health data, and Google Health checks.
- Current voice input / voice output / motion endpoints are safe demo request boundaries, not real STT / TTS / VTS execution proof.
- Later v1.9.0 days should turn this inventory into concrete smartphone Web configuration and UI-visible verification evidence.
```

The Day2 check also reruns the Day1 documentation consistency check.


### v1.9.0 Smartphone Web FW4.0.0 demo hardening checks

v1.9.0 starts from documentation and requirement alignment after the completed v1.8.0 release.

Primary Day1 check:

```text
scripts/check_v190_smartphone_web_fw_demo_day1.py
```

Day1 verifies that the repository documents:

```text
- v1.8.0 released / v1.9.0 next target consistency
- public AI Character Framework demo app positioning
- target FW repository: https://github.com/murayan1982/ai-character-framework.git
- public repository requirement
- smartphone Web demonstration requirement
- actual backend API calls from Web UI
- FW4.0.0-era capability targets: LLM, STT, TTS, Live2D/VTS
- Web UI visible result verification, not API-only completion
- configured real API environment placeholders for OpenAI / Gemini / Grok / ElevenLabs / Google Health
- AI-generated app visual asset planning
- App Store / Google Play consumer release work deferred to v2.0.0 or later
```

Configured real API checks must remain explicit opt-in and must never require secrets for mock-safe/default checks.


### Release cleanup checkpoint

Before creating a release zip, run the current milestone cleanup checkpoint.

For v1.4.0 this is:

```powershell
python scripts\check_v140_character_experience_day4.py
```

Run it once during the Day4 cleanup checkpoint and again during the Day8 final pre-release source-tree cleanup verification immediately before creating the fixed v1.4.0 release zip. Later v1.4.0 fixed-zip/final checks should rely on this cleanup checkpoint having passed before packaging.

The checkpoint should catch or document cleanup for generated helper bundles such as `README_v140_day*_bundle.md`, root-level temporary migration notes, stale root `release_notes_v*.md` files, local extraction/work folders, generated caches, build outputs, and release zip rebuild drift.

The release workflow remains:

```text
Build the release zip once, record its path, then run final checks against that fixed zip without rebuilding.
```

### Release notes records

Release notes should live under `release_notes/` instead of accumulating at the repository root.

Current canonical release-note records:

```text
release_notes/v1.2.0.md
release_notes/v1.3.0.md
release_notes/v1.4.0.md
release_notes/v1.5.0.md
release_notes/v1.6.0.md
```

Keep historical release notes stable once a tag is cut. Future release notes should use the same folder.

### Archive policy

Historical or one-off scripts can move to:

```text
scripts/archive/
```

Archive only after classifying the script with the v1.1.0 Day3 policy:

```text
KEEP / COMPATIBILITY / ARCHIVE / DELETE
```

Do not use `scripts/archive/` as a trash can.

---

## v1.1.0 cleanup policy

The v1.1.0 cleanup sequence is:

```text
Day1: public repository publication plan
Day2: docs inventory policy
Day3: scripts inventory policy
Day4: first safe cleanup structure and scripts README policy
Day5: public repo hygiene and release readiness aggregation
```

Current v1.1.0 aggregate check:

```powershell
```

Historical v1.1.0 milestone checks:

```powershell
```

The historical Day1-Day4 checks may include milestone-specific roadmap markers. After roadmap.md advances to Day5, use the Day5 aggregate check as the current source-tree gate.

---

## Protected scripts during early v1.1.0 cleanup

Do not move, delete, or rename these without a specific replacement plan:

```text
scripts/check_release_package.py
scripts/check_v100_release_package_day10.py
scripts/check_v100_final_release_day11.py
scripts/check_v100_compatibility_final_sweep_day12.py
```

---

## Recommended local verification

For the current v1.4.0 character experience source-tree checks:

```powershell
python -m compileall -q backend scripts
python scripts\check_v140_character_experience_day1.py
python scripts\check_v140_character_experience_day2.py
python scripts\check_v140_character_experience_day3.py
python scripts\check_v140_character_experience_day4.py
python scripts\check_v140_character_experience_day5.py
python scripts\check_v140_character_experience_day6.py
python scripts\check_v140_character_experience_day7.py
python scripts\check_v140_character_experience_day8.py
```

After Day8 passes and the release zip has been built once, verify the fixed zip as-is and then run final release readiness against that same zip:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v140_character_experience_day9.py $zip
python scripts\check_v140_character_experience_day10.py $zip
python scripts\check_v140_character_experience_day11.py $zip
python scripts\check_v140_character_experience_day12.py $zip
```

For historical v1.1.0 public repo readiness aggregation:

```powershell
```

Optional fixed zip verification after creating a v1.1.0 release package:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
```

The Day5 aggregate check must not rebuild release artifacts. Pass an existing fixed zip when verifying package contents.

For v1.0.0 fixed release verification:

```powershell
$zip = "release\DailyRhythmCompanion_20260520_214945.zip"

python scripts\check_v100_release_package_day10.py $zip
python scripts\check_v100_final_release_day11.py $zip
python scripts\check_v100_compatibility_final_sweep_day12.py $zip
python scripts\check_v100_compatibility_final_sweep_day12.py $zip --compat
```

Do not rebuild a fixed release zip while verifying it.

### v1.5.0 Day8 final pre-release source-tree cleanup verification

```powershell
python scripts\check_v150_mood_personalization_day8.py
```

Runs the Day7 aggregate readiness gate and checks that obvious temporary/generated development artifacts are absent before release packaging.

## v1.5.0 Day9 fixed release zip verification

```powershell
python scripts\check_v150_mood_personalization_day9.py <fixed-release-zip>
```

This check reruns the Day8 final pre-release source-tree cleanup verification and then inspects the provided release zip as-is. It must not call `build_release.bat` or create a new release artifact.


### v1.5.0 Day10 final release readiness

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python scripts\check_v150_mood_personalization_day10.py $zip
```

Runs the Day9 fixed release zip verification and protected v1.0.0 release/final/compatibility checks against the provided fixed zip. It does not create or rebuild release artifacts.


### v1.5.0 Day11 Flutter / Chrome app-side verification

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python scripts\check_v150_mood_personalization_day11.py $zip
```

Runs Day10 final release readiness, Flutter widget tests, Flutter devices, and Chrome web-device detection. It does not create or rebuild release artifacts.


### v1.5.0 Day12 release notes

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python scripts\check_v150_mood_personalization_day12.py $zip
```

Runs Day11 Flutter / Chrome app-side verification and verifies `release_notes/v1.5.0.md`. It does not create or rebuild release artifacts.

Day2 adds the rhythm report inventory check:

```powershell
python scripts\check_v160_rhythm_reports_day2.py
```

The Day2 check is mock-safe and source-tree only. It verifies the DailyRecord, SleepSummary, DailyRecordStore, RecentSleepTrend, WeeklySleepSummary, API client, and HistoryScreen surfaces that can support weekly/monthly rhythm reports. It also verifies the monthly-report gap, source/data label direction, and conservative non-medical wording boundaries.

Day3 adds the rhythm report contract check:

```powershell
python scripts\check_v160_rhythm_reports_day3.py
```

The Day3 check is mock-safe and source-tree only. It verifies the generic RhythmReport contract, period=weekly/monthly decision, source-label policy, sparse-history and unavailable-history wording, data-quality labels, and compatibility with the existing WeeklySleepSummary foundation.

Day4 and Day5 add backend/API rhythm report checks:

```powershell
python scripts\check_v160_rhythm_reports_day4.py
python scripts\check_v160_rhythm_reports_day5.py
```

The Day4 check verifies the mock-safe RhythmReport model/service foundation. The Day5 check verifies the `/daily-records/rhythm-report` API for weekly/monthly reports and confirms the existing weekly summary and DailyRecord date routes remain available.

Day6 adds the Flutter rhythm report presentation check:

```powershell
python scripts\check_v160_rhythm_reports_day6.py
```

The Day6 check runs the Day5 backend/API gate, verifies Flutter source markers for RhythmReport, and runs `flutter test` when Flutter is available.


### v1.9.0 Day43 Live2D / VTS motion smartphone Web boundary evidence check

Primary Day43 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day43.py
```

Day43 adds:

```text
backend/app/services/framework_motion_smartphone_web_boundary_evidence.py
scripts/smoke_framework_motion_smartphone_web_boundary_evidence.py
docs/framework_motion_smartphone_web_boundary_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day43.md
scripts/check_v190_smartphone_web_fw_demo_day43.py
```

Expected marker:

```text
motion_smartphone_web_boundary_evidence_status: verified
motion_smartphone_web_boundary_next_step: record-manual-smartphone-web-motion-boundary-evidence
```

Day43 checks do not connect to VTube Studio, load Live2D runtime code, dispatch motion, start Flutter, open a browser, call providers, touch microphones, synthesize speech, generate audio, play audio, or store motion payload bodies.

### v1.9.0 Day42 FW4.0.0 capability coverage after voice output evidence check

Primary Day42 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day42.py
```

Day42 adds:

```text
backend/app/services/framework_fw40_capability_coverage_after_voice_output.py
scripts/smoke_framework_fw40_capability_coverage_after_voice_output.py
docs/framework_fw40_capability_coverage_after_voice_output.md
docs/internal/v190_smartphone_web_fw_demo_day42.md
scripts/check_v190_smartphone_web_fw_demo_day42.py
```

Expected status:

```text
v190_fw40_capability_coverage_after_voice_output_status: text-chat-voice-input-and-voice-output-boundary-evidence-complete-motion-boundary-pending
v190_fw40_capability_coverage_after_voice_output_next_focus: live2d_vts_motion
```

Live2D/VTS motion becomes the next focus. Day42 checks do not start Flutter, open a browser, call providers, touch microphones, synthesize speech, generate audio, play audio, connect to Live2D/VTS, or dispatch motion.

### v1.9.0 Day44 Live2D / VTS motion smartphone Web boundary evidence record check

Primary Day44 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day44.py
```

Day44 adds:

```text
backend/app/services/framework_motion_smartphone_web_boundary_evidence_record.py
scripts/smoke_framework_motion_smartphone_web_boundary_evidence_record.py
docs/framework_motion_smartphone_web_boundary_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day44.md
scripts/check_v190_smartphone_web_fw_demo_day44.py
```

Expected marker:

```text
v190_motion_smartphone_web_boundary_record_status: recorded
v190_motion_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-motion-boundary-evidence
```

Configured Live2D/VTS runtime execution remains separate. Day44 checks do not connect to VTube Studio, load Live2D runtime code, dispatch motion, start Flutter, open a browser, call providers, touch microphones, synthesize speech, generate audio, play audio, or store motion payload bodies.

### v1.9.0 Day45 FW4.0.0 capability coverage after motion evidence check

Primary Day45 check:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day45.py
```

Day45 adds:

```text
backend/app/services/framework_fw40_capability_coverage_after_motion.py
scripts/smoke_framework_fw40_capability_coverage_after_motion.py
docs/framework_fw40_capability_coverage_after_motion.md
docs/internal/v190_smartphone_web_fw_demo_day45.md
scripts/check_v190_smartphone_web_fw_demo_day45.py
```

Expected marker:

```text
v190_fw40_capability_coverage_after_motion_status: fw40-smartphone-web-capability-evidence-complete
v190_fw40_capability_coverage_after_motion_next_focus: v190-release-readiness
```

v1.9.0 release readiness becomes the next focus after Day45. Day45 checks do not connect to VTube Studio, load Live2D runtime code, dispatch motion, start Flutter, open a browser, call providers, touch microphones, synthesize speech, generate audio, play audio, or store motion payload bodies.

## v1.9.0 release-chain retirement

Cleanup-5 removes the obsolete v1.9.0 Day46-Day49 release-readiness/package/finalization helpers and the v1.9-specific cleanup scripts. The completed release record remains at `release_notes/v1.9.0.md`.

Current Public source and package-surface validation uses:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py
```

Final fixed-ZIP validation remains owned by the v2.0.0 Day82 and Day83 checks.

### v2.0.0 pre-release requirements checks

These checks document the release requirements that must be satisfied before v2.0.0:

```powershell
python scripts\smoke_framework_v200_prerelease_requirements.py
python scripts\check_v200_prerelease_requirements.py
python scripts\check_v190_smartphone_web_fw_demo_day51.py
```

Expected public-safe marker:

```text
v200_prerelease_requirements_status: documented-pending-before-v2.0.0
```

The checks require docs to mention real LLM API Web answers, real TTS API Web voice output, real Google Health API sleep data retrieval, Web image display, public-repo-ready as an AI Character Framework demo app including LICENSE if needed, and explicit release requirements.

Canonical script paths:

```text
scripts/check_v200_prerelease_requirements.py
scripts/smoke_framework_v200_prerelease_requirements.py
scripts/check_v190_smartphone_web_fw_demo_day51.py
```


### v2.0.0 Day52 real LLM Web answer evidence checks

Day52 prepares the public-safe evidence contract for the first v2.0.0 pre-release requirement:

```text
real LLM API: Web上で回答が生成できること / real LLM API Web answer generation
```

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_llm_web_answer_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_real_llm_web_answer_evidence.py
```

Expected marker:

```text
v200_real_llm_web_answer_evidence_status: operator-evidence-contract-ready
```

Optional configured backend API probe, for prepared local operators only:

```powershell
$env:DRC_V200_ENABLE_REAL_LLM_WEB_ANSWER_SMOKE="1"
$env:DRC_BACKEND_API_BASE_URL="http://127.0.0.1:8000"
python scripts\smoke_framework_v200_real_llm_web_answer_evidence.py --require-running-backend
```

Canonical paths:

```text
docs/v200_real_llm_web_answer_evidence.md
backend/app/services/framework_v200_real_llm_web_answer_evidence.py
scripts/smoke_framework_v200_real_llm_web_answer_evidence.py
scripts/smoke_framework_v200_real_llm_web_answer_evidence.py
```

The default Day52 check does not call OpenAI, Gemini, Grok, ElevenLabs, Google Health, the backend, a browser, Web UI, AI Character Framework sessions, ask, or ask_stream. It records the evidence contract only; configured real LLM Web answer evidence remains explicit operator opt-in.


### v2.0.0 Day53 real TTS provider gate checks

Day53 prepares the public-safe provider gate contract for the second v2.0.0 pre-release requirement:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_provider_gate.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_real_tts_provider_gate.py
```

Expected marker:

```text
v200_real_tts_provider_gate_status: provider-gate-contract-ready
```

Optional backend status probe, for prepared local operators only:

```powershell
$env:DRC_V200_ENABLE_REAL_TTS_PROVIDER_GATE_SMOKE="1"
$env:DRC_BACKEND_API_BASE_URL="http://127.0.0.1:8000"
python scripts\smoke_framework_v200_real_tts_provider_gate.py --require-running-backend
```

Canonical paths:

```text
docs/v200_real_tts_provider_gate.md
backend/app/services/framework_v200_real_tts_provider_gate.py
scripts/smoke_framework_v200_real_tts_provider_gate.py
scripts/smoke_framework_v200_real_tts_provider_gate.py
```

The default Day53 check does not call ElevenLabs, OpenAI TTS, AI Character Framework voice output, the backend, a browser, Web UI, audio generation, audio playback, or audio artifact creation. It records the provider gate contract only; configured real TTS Web voice output evidence remains explicit operator opt-in.


### v2.0.0 Day54 real TTS Web audio output evidence checks

Day54 prepares the public-safe evidence contract for the configured real TTS Web audio output requirement:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py
```

Expected marker:

```text
v200_real_tts_web_audio_evidence_status: operator-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py --operator-evidence-json .\operator_evidence.json
```

The marker-only `operator_evidence.json` shape should include:

```text
explicit_operator_opt_in_enabled
framework_voice_output_boundary_used
provider_synthesis_confirmed
safe_backend_audio_contract_confirmed
web_audio_output_audibly_confirmed
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_real_tts_web_audio_output_evidence.md
backend/app/services/framework_v200_real_tts_web_audio_output_evidence.py
scripts/smoke_framework_v200_real_tts_web_audio_output_evidence.py
scripts/smoke_framework_v200_real_tts_web_audio_output_evidence.py
```

The default Day54 check does not call ElevenLabs, OpenAI TTS, AI Character Framework voice output, the backend, a browser, Web UI, audio generation, audio playback, or audio artifact creation. It records the evidence contract only; configured real TTS Web voice output evidence remains explicit operator opt-in.


### v2.0.0 Day55 real Google Health sleep data evidence checks

Day55 prepares the public-safe evidence contract for the configured real Google Health sleep-data requirement:

```text
Google Health実APIを使用して、実睡眠データが取得できること / real Google Health API sleep-data retrieval
```

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_google_health_sleep_data_day55.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_v200_real_google_health_sleep_data_evidence.py
```

Expected marker:

```text
v200_real_google_health_sleep_evidence_status: operator-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_v200_real_google_health_sleep_data_evidence.py --operator-evidence-json .\operator_evidence.json
```

The marker-only `operator_evidence.json` shape should include:

```text
explicit_operator_opt_in_enabled
google_health_real_api_gate_enabled
oauth_connection_available
real_sleep_data_fetch_succeeded
sleep_summary_normalized_to_public_contract
backend_sleep_summary_real_data_confirmed
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_real_google_health_sleep_data_evidence.md
backend/app/services/google_health_v200_real_sleep_data_evidence.py
scripts/smoke_v200_real_google_health_sleep_data_evidence.py
scripts/check_v200_real_google_health_sleep_data_day55.py
```

The default Day55 check does not call Google Health APIs, read OAuth tokens, call the backend, open a browser, start Flutter, normalize real health payloads, or create health-data artifacts. It records the evidence contract only; configured real Google Health sleep-data evidence remains explicit operator opt-in.


### v2.0.0 Day56 Web image display evidence checks

Day56 prepares the public-safe evidence contract for the configured Web image display requirement:

```text
画像を用いて、Web上で表示確認できること / Web image display evidence
```

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_web_image_display_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_v200_web_image_display_evidence.py
```

Expected marker:

```text
v200_web_image_display_evidence_status: operator-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_v200_web_image_display_evidence.py --operator-evidence-json .\operator_evidence.json
```

The marker-only `operator_evidence.json` shape should include:

```text
public_safe_image_assets_selected
flutter_asset_manifest_registration_confirmed
flutter_web_release_build_display_confirmed
smartphone_web_display_confirmed
missing_image_fallback_confirmed
release_package_asset_inclusion_confirmed
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_web_image_display_evidence.md
backend/app/services/web_image_v200_display_evidence.py
scripts/smoke_v200_web_image_display_evidence.py
scripts/smoke_v200_web_image_display_evidence.py
```

The default Day56 check does not generate images, call image-generation services, start Flutter, open a browser, build Web release artifacts, call the backend, create image artifacts, or validate screenshots. It records the evidence contract only; configured Web image display evidence remains explicit operator confirmation.

### Retired pre-Web Public readiness checks

Cleanup-6 removes the former Day57 and Day58 smoke paths. Use the current direct Public-distribution validator instead:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py
```

The retired checks were preparation-stage marker contracts and are not required by the final Public snapshot.

### v2.0.0 Day64 real LLM Web answer execution evidence checks

Day64 starts the real execution evidence phase for the first v2.0.0 completion requirement. It validates marker-only evidence after a configured operator has confirmed both the DRC `/advice` backend API response and the smartphone Web UI visible answer.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_llm_web_answer_execution_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_real_llm_web_answer_execution_evidence.py
```

Expected marker:

```text
v200_real_llm_web_answer_execution_evidence_status: operator-execution-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_real_llm_web_answer_execution_evidence.py --operator-evidence-json .\operator_evidence\v200_real_llm_web_answer_day64.json
```

The marker-only evidence JSON shape should include:

```text
explicit_operator_opt_in_enabled
backend_advice_api_called
configured_framework_route_used
source_engine_framework_confirmed
message_non_empty_confirmed
smartphone_web_ui_visible_answer_confirmed
fallback_or_skip_not_counted
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_real_llm_web_answer_execution_evidence.md
docs/operator_evidence_templates/v200_real_llm_web_answer_day64.example.json
backend/app/services/framework_v200_real_llm_web_answer_execution_evidence.py
scripts/smoke_framework_v200_real_llm_web_answer_execution_evidence.py
scripts/smoke_framework_v200_real_llm_web_answer_execution_evidence.py
```

The default Day64 check does not call providers, start backend services, open browsers, create framework sessions, call `ask`, call `/advice`, inspect answer bodies, validate screenshots, or create release artifacts. It records the evidence contract only; configured real LLM Web answer execution evidence remains explicit operator opt-in.
### v2.0.0 Day65 real TTS Web audio output execution evidence checks

Day65 starts the real execution evidence phase for the second v2.0.0 completion requirement. It validates marker-only evidence after a configured operator has confirmed real provider synthesis, safe backend audio exposure, and audible smartphone Web UI playback.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py
```

Expected marker:

```text
v200_real_tts_web_audio_execution_evidence_status: operator-execution-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py --operator-evidence-json .\operator_evidence\v200_real_tts_web_audio_day65.json
```

The marker-only evidence JSON shape should include:

```text
explicit_operator_opt_in_enabled
framework_voice_output_boundary_used
neutral_voice_contract_used
real_provider_synthesis_confirmed
safe_backend_audio_contract_confirmed
smartphone_web_audio_audibly_confirmed
fallback_or_skip_not_counted
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_real_tts_web_audio_execution_evidence.md
docs/operator_evidence_templates/v200_real_tts_web_audio_day65.example.json
backend/app/services/framework_v200_real_tts_web_audio_execution_evidence.py
scripts/smoke_framework_v200_real_tts_web_audio_execution_evidence.py
scripts/smoke_framework_v200_real_tts_web_audio_execution_evidence.py
```

The default Day65 check does not call providers, call AI Character Framework voice output, start backend services, open browsers, synthesize audio, play audio, inspect audio files, record audio URLs, validate screenshots, or create release artifacts. It records the execution evidence contract only; configured real TTS Web audio execution evidence remains explicit operator opt-in.

### v2.0.0 Day66 real Google Health sleep data execution evidence checks

Day66 starts the real execution evidence phase for the third v2.0.0 completion requirement. It validates marker-only evidence after a configured operator has confirmed real Google Health API use, real sleep-data fetch success, SleepSummary normalization, backend real-data source confirmation, and smartphone Web UI real-source confirmation.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_google_health_sleep_data_execution_day66.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py
```

Expected marker:

```text
v200_real_google_health_sleep_data_execution_evidence_status: operator-execution-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py --operator-evidence-json .\operator_evidence\v200_real_google_health_sleep_data_day66.json
```

The marker-only evidence JSON shape should include:

```text
explicit_operator_opt_in_enabled
google_health_real_api_gate_enabled
oauth_connection_available
real_google_health_api_request_confirmed
real_sleep_data_fetch_succeeded
sleep_summary_normalized_to_public_contract
backend_sleep_summary_real_data_confirmed
smartphone_web_sleep_summary_real_source_confirmed
fallback_or_skip_not_counted
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_real_google_health_sleep_data_execution_evidence.md
docs/operator_evidence_templates/v200_real_google_health_sleep_data_day66.example.json
backend/app/services/framework_v200_real_google_health_sleep_data_execution_evidence.py
scripts/smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py
scripts/check_v200_real_google_health_sleep_data_execution_day66.py
```

The default Day66 check does not call Google Health APIs, read OAuth tokens, read local token files, call backend services, open browsers, parse raw health payloads, inspect raw sleep events, inspect precise personal sleep timestamps, validate screenshots, or create release artifacts. It records the execution evidence contract only; configured real Google Health sleep-data execution evidence remains explicit operator opt-in.


### v2.0.0 Day67 image asset generation and repository-safe intake checks

Day67 starts the repository-safe asset-intake phase for the fourth v2.0.0 completion requirement. It validates marker-only evidence after a configured operator has confirmed generated or sourced image assets are safe for public repository use before Flutter asset registration and Web display verification.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py
```

Expected marker:

```text
v200_image_asset_generation_intake_evidence_status: operator-execution-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_image_asset_generation_intake_evidence.py --operator-evidence-json .\operator_evidence\200_image_asset_generation_intake_day67.json
```

The marker-only evidence JSON shape should include:

```text
explicit_operator_opt_in_enabled
image_asset_generation_review_completed
public_safe_asset_sources_confirmed
required_asset_inventory_selected
repository_safe_asset_paths_reserved
generated_asset_metadata_sanitized
third_party_or_copyrighted_sources_absent
private_or_living_person_references_absent
raw_generation_workspace_excluded
fallback_placeholder_strategy_confirmed
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_image_asset_generation_intake_evidence.md
docs/operator_evidence_templates/v200_image_asset_generation_intake_day67.example.json
backend/app/services/framework_v200_image_asset_generation_intake_evidence.py
scripts/smoke_framework_v200_image_asset_generation_intake_evidence.py
scripts/smoke_framework_v200_image_asset_generation_intake_evidence.py
```

The default Day67 check does not call image-generation services, create image files, register Flutter assets, start backend services, open browsers, inspect screenshots, read local generation work folders, or create release artifacts. It records the image asset generation/intake evidence contract only; configured asset generation and repository-safe asset intake evidence remain explicit operator opt-in.

### v2.0.0 Day68 Web image display execution evidence checks

Day68 starts the Web image display execution evidence phase for the fourth v2.0.0 completion requirement. It validates marker-only evidence after a configured operator has confirmed reviewed image assets or placeholders are registered and visible in the actual Flutter Web UI, including smartphone Web confirmation.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_web_image_display_execution_evidence.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_web_image_display_execution_evidence.py
```

Expected marker:

```text
v200_web_image_display_execution_evidence_status: operator-execution-evidence-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_web_image_display_execution_evidence.py --operator-evidence-json .\operator_evidence\v200_web_image_display_execution_day68.json
```

The marker-only evidence JSON shape should include:

```text
explicit_operator_opt_in_enabled
day67_asset_intake_evidence_accepted
public_safe_assets_available_in_app_tree
flutter_asset_manifest_registration_confirmed
flutter_web_runtime_display_confirmed
smartphone_web_display_confirmed
actual_app_route_used
missing_image_fallback_confirmed
release_package_asset_inclusion_ready
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_web_image_display_execution_evidence.md
docs/operator_evidence_templates/v200_web_image_display_execution_day68.example.json
backend/app/services/framework_v200_web_image_display_execution_evidence.py
scripts/smoke_framework_v200_web_image_display_execution_evidence.py
scripts/smoke_framework_v200_web_image_display_execution_evidence.py
```

The default Day68 check does not generate images, inspect image files, run Flutter Web builds, start backend services, open browsers, inspect screenshots, record LAN URLs, or create release artifacts. It records the Web image display execution evidence contract only; configured Web image display execution evidence remains explicit operator opt-in.

### v2.0.0 Day69 public repo readiness final sweep checks

Day69 starts the public repository final sweep phase for the fifth v2.0.0 completion requirement. It validates marker-only evidence after a configured operator has reviewed Day57 public repository readiness plus Day64 through Day68 execution evidence and confirmed that the repository remains public-safe as an AI Character Framework demo app.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_public_repo_final_sweep.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_public_repo_final_sweep.py
```

Expected marker:

```text
v200_public_repo_final_sweep_status: public-repo-final-sweep-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_public_repo_final_sweep.py --operator-evidence-json .\operator_evidence\v200_public_repo_final_sweep_day69.json
```

The marker-only evidence JSON shape should include:

```text
day57_public_repo_readiness_review_accepted
day64_real_llm_execution_evidence_reviewed
day65_real_tts_execution_evidence_reviewed
day66_real_google_health_execution_evidence_reviewed
day67_image_asset_intake_evidence_reviewed
day68_web_image_display_evidence_reviewed
license_scope_confirmed
public_positioning_claims_reviewed
public_docs_secret_hygiene_final_scan_completed
release_surface_local_artifacts_absent
raw_evidence_material_excluded
mock_safe_default_preserved
public_safe_evidence_recorded
```

Canonical paths:

```text
docs/v200_public_repo_final_sweep.md
docs/operator_evidence_templates/v200_public_repo_final_sweep_day69.example.json
backend/app/services/framework_v200_public_repo_final_sweep.py
scripts/smoke_framework_v200_public_repo_final_sweep.py
scripts/smoke_framework_v200_public_repo_final_sweep.py
```

The default Day69 check does not publish to GitHub, build release artifacts, create release zips, call providers, call Google Health, start backend services, run Flutter, open browsers, inspect screenshots, inspect audio/image binaries, or access external network services. It records the public repository final sweep evidence contract only; configured public repo final sweep evidence remains explicit operator opt-in.


### v2.0.0 Day70 final prerelease aggregate gate checks

Day70 starts the final prerelease aggregate phase before building one fixed v2.0.0 release candidate zip. It validates marker-only evidence that Day52-Day58 foundation gates, Day64-Day68 real execution evidence, Day69 public repo final sweep, API-level review, smartphone Web review, public-safe evidence handling, and mock-safe defaults are ready.

Mock-safe source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_prerelease_aggregate_gate.py

cd app
flutter test
cd ..
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_final_prerelease_aggregate_gate.py
```

Expected marker:

```text
v200_final_prerelease_aggregate_gate_status: final-prerelease-aggregate-contract-ready
```

Optional redacted operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_final_prerelease_aggregate_gate.py --operator-evidence-json .\operator_evidence\v200_final_prerelease_aggregate_gate_day70.json
```

The marker-only evidence JSON shape should include:

```text
day52_to_day58_foundation_gates_passed
day64_real_llm_web_answer_execution_accepted
day65_real_tts_web_audio_execution_accepted
day66_real_google_health_sleep_data_execution_accepted
day67_image_asset_intake_accepted
day68_web_image_display_execution_accepted
day69_public_repo_final_sweep_accepted
smartphone_web_evidence_reviewed
api_level_evidence_reviewed
fallback_skipped_unavailable_not_counted
mock_safe_default_preserved
credential_free_default_checks_preserved
public_safe_marker_only_evidence_preserved
release_zip_not_created_by_aggregate_check
ready_to_build_one_fixed_v200_release_candidate
```

Canonical paths:

```text
docs/v200_final_prerelease_aggregate_gate.md
docs/operator_evidence_templates/v200_final_prerelease_aggregate_gate_day70.example.json
backend/app/services/framework_v200_final_prerelease_aggregate_gate.py
scripts/smoke_framework_v200_final_prerelease_aggregate_gate.py
scripts/smoke_framework_v200_final_prerelease_aggregate_gate.py
```

The default Day70 check does not build release artifacts, create release zips, inspect release zips, call providers, call Google Health, start backend services, run Flutter, open browsers, inspect screenshots, inspect audio/image binaries, publish to GitHub, or access external network services. It records the final prerelease aggregate evidence contract only; configured final aggregate evidence remains explicit operator opt-in.


### Retired pre-Web fixed-ZIP checks

Cleanup-6 removes the former Day71 and Day72 smoke paths. They predated the accepted Web screenshot requirement.

Use the current final chain:

```powershell
python scripts\smoke_framework_v200_public_distribution_readiness.py
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py <fixed-zip>
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py <fixed-zip>
```

The final two commands inspect the same supplied fixed ZIP and must not rebuild it.

### v2.0.0 Day73 accepted Web screenshot evidence enforcement checks

Day73 prevents v2.0.0 from being considered complete from API-only, source-tree-only, mock-safe, fallback, skipped, unavailable, placeholder, or fixed-zip-only results.

Run the accepted Web screenshot evidence enforcement contract:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py

cd app
flutter test
cd ..
```

The Day73 check validates:

```text
- docs/v200_accepted_web_screenshot_evidence_enforcement.md
- docs/operator_evidence_templates/v200_accepted_web_screenshot_evidence_day73.example.json
- backend/app/services/framework_v200_accepted_web_screenshot_evidence_enforcement.py
- scripts/smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
- scripts/smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
- scripts/smoke_framework_v200_final_prerelease_aggregate_gate.py
- scripts/smoke_framework_v200_public_repo_final_sweep.py
- scripts/smoke_framework_v200_web_image_display_execution_evidence.py
- scripts/smoke_framework_v200_image_asset_generation_intake_evidence.py
- scripts/smoke_framework_v200_real_google_health_sleep_data_execution_evidence.py
- scripts/smoke_framework_v200_real_tts_web_audio_execution_evidence.py
- scripts/smoke_framework_v200_real_llm_web_answer_execution_evidence.py
- scripts/check_v200_prerelease_requirements.py
```

Default smoke renderer:

```powershell
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
```

Optional configured operator evidence validation, for prepared local operators only:

```powershell
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py --operator-evidence-json .\operator_evidence\200_accepted_web_screenshot_evidence_day73.json
```

The accepted evidence JSON must include Web execution screenshot confirmation for real LLM, real TTS audio, real Google Health sleep data, and Web image display. It must also confirm image asset intake, public repo final sweep, final aggregate review, and all Web screenshot evidence review.

API-only smoke does not count as v2.0.0 completion. Source-tree-only checks do not count. The default Day73 check does not call providers, Google Health, backend APIs, Flutter Web, browsers, screenshot tools, release builders, fixed-zip checks, GitHub, or external network services.

If Day73 changes are applied after a fixed release candidate zip was already built, do not use that old zip for v2.0.0 final release handling. Build one new fixed zip after Day73 passes and restart fixed-zip verification.


### v2.0.0 Day76 real LLM Web screenshot evidence capture checks

Day76 validates the public-safe contract for the private real LLM Web screenshot evidence item. See docs/v200_real_llm_web_screenshot_evidence_capture.md.
Default checks do not call providers, backend APIs, Flutter Web, browser automation, screenshot tools, or external network services.

Public-safe evidence validation:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
```

The optional private operator path validates a real LLM Web evidence item kept outside the public repository:

```powershell
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py --evidence-json "<private-real-llm-web-evidence-json>"
```

Accepted evidence must include actual DRC backend API use, Web UI execution, visible real provider-backed answer, screenshot capture, public-safe private screenshot reference, and explicit rejection of API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, and screenshot-missing states.


### v2.0.0 Day77 real TTS Web audio screenshot evidence capture checks

Day77 validates the public-safe contract for the private real TTS Web audio screenshot evidence item. See docs/v200_real_tts_web_audio_screenshot_evidence_capture.md. Default checks do not call TTS providers, FW voice output, backend APIs, Flutter Web, browser automation, screenshot tools, audio devices, or external network services.

Run after Day76 passes:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
```

The optional private operator path validates a real TTS Web audio evidence item kept outside the public repository:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py --evidence-json "<private-real-tts-web-audio-evidence-json>"
```

Accepted evidence must include actual DRC backend API use, Web UI execution, visible TTS audio output result, real TTS provider audio confirmation, Web audio playback confirmation, screenshot capture, public-safe private screenshot reference, and explicit rejection of API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, and screenshot-missing states.


### v2.0.0 Day78 real Google Health Web sleep screenshot evidence capture checks

Day78 validates the public-safe contract for the private real Google Health Web sleep data screenshot evidence item. See docs/v200_real_google_health_web_sleep_screenshot_evidence_capture.md. Default checks do not call Google Health, OAuth endpoints, backend APIs, Flutter Web, browser automation, screenshot tools, release builders, fixed-zip checks, GitHub, or external network services.

Run after Day77 passes:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_google_health_web_sleep_screenshot_day78.py
python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
```

The optional private operator path validates a real Google Health Web sleep evidence item kept outside the public repository:

```powershell
python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py --evidence-json "<private-real-google-health-web-sleep-evidence-json>"
```

Accepted evidence must include actual DRC backend API use, Web UI execution, visible Google Health-backed sleep result, normalized SleepSummary confirmation, real Google Health API/OAuth confirmation, screenshot capture, public-safe private screenshot reference, and explicit rejection of API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, screenshot-missing, token-exposed, raw-health-data-exposed, and medical-claim states.


### v2.0.0 Day79 Web image display screenshot evidence capture checks

Day79 validates the public-safe contract for the private Web image display screenshot evidence item. See docs/v200_web_image_display_screenshot_evidence_capture.md. Default checks do not generate images, copy assets, start backend APIs, run Flutter Web, open browsers, inspect screenshots, run release builders, check fixed zips, call GitHub, or use external network services.

Run after Day78 passes:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_web_image_display_screenshot_evidence.py
python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
```

The optional private operator path validates a Web image display evidence item kept outside the public repository:

```powershell
python scripts\smoke_framework_v200_web_image_display_screenshot_evidence.py --evidence-json "<private-web-image-display-screenshot-evidence-json>"
```

Accepted evidence must include actual DRC backend API use, Web UI execution, visible accepted image asset, repository-safe image asset confirmation, Day67 image asset intake review acceptance, screenshot capture, public-safe private screenshot reference, and explicit rejection of API-only, source-tree-only, command-output-only, generated-but-not-displayed, mock, fallback, skipped, unavailable, placeholder, screenshot-missing, raw-image-exposed, raw-screenshot-committed, local-path, and copyright-risk states.


### v2.0.0 Day80 accepted Web evidence manifest aggregate checks

Day80 validates the public-safe contract for the private accepted Web evidence manifest aggregate. See docs/v200_accepted_web_evidence_manifest_aggregate.md. Default checks do not call providers, Google Health, backend APIs, Flutter Web, browser automation, screenshot tools, release builders, fixed-zip checks, GitHub, or external network services.

Run after Day79 passes:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py
python scripts\smoke_framework_v200_web_image_display_screenshot_evidence.py
python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py

cd app
flutter test
cd ..
```

The Day80 check validates:

```text
- docs/v200_accepted_web_evidence_manifest_aggregate.md exists.
- the public example manifest is not accepted evidence.
- synthetic accepted manifest evidence validates only when every required private evidence item is accepted.
- real LLM, real TTS, real Google Health, and Web image display entries each require Web UI execution and screenshot references.
- image asset intake, public repo final sweep, and final aggregate entries are required.
- API-only, source-tree-only, command-output-only, mock-only, fallback, skipped, unavailable, placeholder, screenshot-missing, raw-screenshot-committed, raw-provider-payload, raw-audio, raw-health-data, private path, LAN IP, API key, and OAuth token states are rejected.
```


The private operator candidate must use the ignored path below; the committed example remains intentionally non-accepted:

```powershell
Copy-Item `
  .\docs\operator_evidence_templates\v200_accepted_web_evidence_manifest_day80.example.json `
  .\operator_evidence\v200_accepted_web_evidence_manifest_day80.json

# Edit only the ignored copy after reviewing the actual accepted private evidence set.
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py `
  --manifest-json .\operator_evidence\v200_accepted_web_evidence_manifest_day80.json
```

Do not commit the Day80 manifest or any raw/private evidence. The source-tree smoke now verifies that the public example is rejected, a complete synthetic marker-only manifest is accepted, and representative missing-item, screenshot-missing, unsafe-reference, placeholder, and private-path cases are rejected. These synthetic checks do not accept the real private manifest.

### v2.0.0 Day81 final release readiness with accepted Web evidence checks

Day81 validates the public-safe contract for the final v2.0.0 release readiness gate that requires an accepted Day80 private Web execution evidence manifest. See docs/v200_final_release_readiness_with_web_evidence.md. Default checks do not call providers, Google Health, backend APIs, Flutter Web, browser automation, screenshot tools, release builders, fixed-zip checks, GitHub, or external network services.

Run after Day80 passes:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py
python scripts\smoke_framework_v200_web_image_display_screenshot_evidence.py
python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py
python scripts\smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py

cd app
flutter test
cd ..
```

Private final release readiness validation uses the fixed zip and private manifest without committing raw evidence:

```powershell
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py --release-zip "<fixed-v200-release-zip>" --manifest-json "<private-accepted-day80-manifest-json>"
```

Day81 requires actual Daily Rhythm Companion backend API use, Web UI execution, screenshot references for Web results, and accepted Day80 manifest status before v2.0.0 tag/release handling. API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, and screenshot-missing evidence must not count as v2.0.0 completion.

## v2.0.0 Day82 fixed release zip verification with accepted Web evidence

Day82 doc: `docs/v200_fixed_release_zip_with_web_evidence_verification.md`

Commit G-6 makes Day82 an actual fixed-artifact inspection. The source-tree smoke creates synthetic accepted/rejected zips to exercise required-entry, private-evidence, worktree `.git` metadata-file, and package-root behavior. Package-only inspection requires `--release-zip` together with `--inspect-zip-only`; Day82 acceptance requires `--release-zip` together with `--evidence-json`, and the evidence must bind the inspected basename, byte size, and SHA-256. A bare `--release-zip` and marker-only `--evidence-json` are both rejected. Inspection first runs `check_release_package.py`, then opens the supplied zip directly, tests CRC, verifies one `DailyRhythmCompanion` root, checks required and forbidden entries, calculates SHA-256, and confirms the zip did not change while inspected. It never creates, modifies, timestamp-refreshes, or rebuilds the artifact.

Source-tree check before artifact creation:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py
```

After the committed-HEAD builder has run exactly once:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"

python scripts\check_release_package.py $zip

# Optional package-only inspection; not Day82 acceptance.
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py `
  --release-zip $zip `
  --inspect-zip-only

# Day82 acceptance.
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py `
  --release-zip $zip `
  --evidence-json "<private-Day82-marker-json>"
```

Do not rebuild the zip after this check passes. Reuse the same fixed zip for the next final readiness step.


## v2.0.0 Day83 final release readiness fixed-zip gate with accepted Web evidence

Day83 doc: `docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md`

Day83 requires the same fixed artifact and private Day83 evidence through `--release-zip` plus `--evidence-json`. It reruns package hygiene, directly reopens the zip, preserves every Day82 required/forbidden rule, requires the Day83 final readiness files, verifies CRC/root/SHA-256/unchanged-artifact state, and binds the Day82-verified SHA-256 to the Day83 inspection. A bare `--release-zip` and marker-only final readiness are rejected.

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py `
  --release-zip $zip `
  --evidence-json "<private-Day83-marker-json>"
```

Do not run `build_v200_final_fixed_release_zip_from_head.ps1` again between Day82 and Day83.

## v2.0.0 D-next-16 / D-next-17 retained outcome

D-next-16 established provider-secret separation and release-package hygiene. D-next-17 aligned smartphone Web execution with the Flutter compile-time key `DRC_BACKEND_API_BASE_URL`. Cleanup-7 removes the completed private-run preparation checks, but retains the runtime contract, FW boundary guard, opaque Web audio handoff, release-package hygiene, public acceptance record, and marker validators.

Current credential-free checks for the retained runtime surface are:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_real_tts_web_runtime_contract.py
python scripts\smoke_v200_fw_voice_output_boundary_for_drc.py
python scripts\smoke_v200_real_tts_web_audio_handoff.py
```

Provider keys and provider-specific configuration remain outside the DRC repository. Raw audio, provider payloads, screenshots, private paths, LAN IPs, and operator evidence remain forbidden from the Public source and release package.

## v2.0.0 D-next-18 public-safe real TTS Web audio acceptance synchronization

D-next-18 synchronizes `real_tts_web_audio_output: ACCEPTED` from the completed private configured Web run using public-safe markers only. It records that the actual DRC backend path was used, audible playback was confirmed in PC and smartphone Web UI, and Day54, Day65, Day77, and combined acceptance validation succeeded.

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v200_real_tts_web_runtime_contract.py
python scripts\smoke_v200_fw_voice_output_boundary_for_drc.py
python scripts\smoke_v200_real_tts_web_audio_handoff.py
python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py
```

The acceptance-sync smoke reads committed source-tree markers only. It does not call a provider, start backend/Web processes, play audio, inspect screenshots, or read `operator_evidence/`. Raw audio, screenshots, provider payloads, secrets, URLs, LAN IPs, private paths, and private evidence files remain uncommitted.

D-next-18 does not advance `real_google_health_sleep_data`, `accepted_private_evidence_manifest`, the final fixed release zip, `DRC_v2.0.0` tag creation, or `release_status: NOT_RELEASED`.

### v2.0.0 Commit E-3 real Google Health local env preflight

E-3 adds the source-tree safe private-env handoff before a configured real Google
Health sleep-data Web run. Default mode does not call Google Health, read OAuth
credentials/tokens, start the backend/Web UI, inspect screenshots, or accept
evidence.

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py
```

Create a dedicated ignored operator copy:

```powershell
Copy-Item .\backend\env_profiles\google_health_real_api_guarded.env.example .\backend\env_profiles\google_health_real_api_operator.local.env
```

Validate only key/value markers without printing private values:

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py --env-file .\backend\env_profiles\google_health_real_api_operator.local.env
```

Expected private-local preflight marker:

```text
v200_real_google_health_sleep_data_preflight_env_file_validation_status: accepted
```

See `docs/v200_real_google_health_sleep_data_operator_runbook.md`.

E-3 preserves:

```text
real_google_health_sleep_data: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

### v2.0.0 Commit E-4 actual Google Health local env preflight checkpoint

E-4 records the public-safe accepted marker observed from the actual ignored local
Google Health operator env preflight. It does not commit or print private env
values, credential contents, OAuth token values, client IDs, private paths, raw
health payloads, or raw sleep data.

Recorded public-safe checkpoint:

```text
v200_real_google_health_sleep_data_preflight_env_file_validation_status: accepted
v200_real_google_health_sleep_data_preflight_env_file_missing_or_invalid_keys:
v200_real_google_health_sleep_data_preflight_env_file_forbidden_keys_present:
v200_real_google_health_sleep_data_preflight_env_file_public_safe: True
credentials_file_exists=True
token_file_exists=True
operator_env_git_status=ignored
```

E-4 does not call Google Health, start the DRC backend or Flutter Web UI, inspect a
screenshot, create Day55/Day66/Day78 operator evidence, or accept the requirement.
It preserves:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

The next small commit must prepare the source-tree safe actual configured Google
Health backend/Web run checkpoint before any private execution evidence is
accepted.

### v2.0.0 Commit E-5 actual Google Health backend/Web run checkpoint

E-5 adds the source-tree safe checkpoint and guarded backend env-loading handoff
for the later private configured Google Health run. It does not read the private
env or OAuth token values, call Google Health, start backend/Web processes, inspect
screenshots, or accept evidence.

```powershell
python scripts\smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py
```

The dedicated launcher validates and loads the ignored operator env, forces
`DRC_SKIP_BACKEND_DOTENV=1`, prints key names and boolean presence markers only,
and supports a no-start validation mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\backend\scripts\run_google_health_real_api_operator.ps1 -EnvFile .\backend\env_profiles\google_health_real_api_operator.local.env -ValidateOnly
```

Actual private backend start:

```powershell
powershell -ExecutionPolicy Bypass -File .\backend\scripts\run_google_health_real_api_operator.ps1 -EnvFile .\backend\env_profiles\google_health_real_api_operator.local.env
```

After startup, the guarded operator-only request confirms both the real HTTP
boundary and the normalized backend `/sleep/summary` handoff:

```powershell
python scripts\smoke_google_health_real_sleep_request.py --base-url http://127.0.0.1:8000 --allow-real-request
```

Required backend markers include:

```text
backend_sleep_summary_source=google_health
backend_sleep_summary_available=True
backend_sleep_summary_is_real_data=True
backend_sleep_summary_positive_duration=True
```

Flutter Web must use the implemented compile-time key:

```powershell
cd app
flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
cd ..
```

The Web result must visibly show `data_kind_label=実データ`, source `Google Health`,
and availability `取得済み`. Raw LAN IPs, private paths, OAuth values, raw health
payloads, precise personal sleep timestamps, and screenshots remain local-only.

E-5 preserves:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

### v2.0.0 Commit E-6 actual Google Health launcher validation checkpoint

E-6 records the public-safe success markers from the actual ignored operator env
passed to the E-5 backend launcher in `-ValidateOnly` mode.

Observed public-safe checkpoint:

```text
operator_env_validation=accepted
backend_dotenv_override=disabled
credentials_file_exists=True
token_file_exists=True
loaded_key_names=key-names-only-no-values
validate_only=True
backend_start=not-started
validate_exit_code=0
operator_env_git_status=ignored
```

E-6 does not commit raw launcher logs, env values, credential contents, OAuth token
values, client IDs, private paths, or LAN IPs. It also does not start the backend,
call Google Health, request `/sleep/summary`, start Flutter Web, inspect a
screenshot, or validate private Day55/Day66/Day78 evidence.

The next private execution command starts the actual backend using the same
validated ignored profile:

```powershell
powershell -ExecutionPolicy Bypass -File .\backend\scripts\run_google_health_real_api_operator.ps1 -EnvFile .\backend\env_profiles\google_health_real_api_operator.local.env
```

After startup, run the guarded real request smoke from another terminal:

```powershell
python scripts\smoke_google_health_real_sleep_request.py --base-url http://127.0.0.1:8000 --allow-real-request
```

E-6 preserves:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

### v2.0.0 Commit E-7 actual Google Health backend/API checkpoint

E-7 records the public-safe success markers from the actual configured Google
Health backend/API run. The existing authorization had returned `invalid_grant`,
so the operator completed a fresh authorization with the current OAuth client.
No OAuth values or raw health data are committed.

Recorded public-safe markers:

```text
oauth_state_valid=True
oauth_token_exchange_attempted=True
oauth_token_saved=True
token_stored=True
required_sleep_scope_in_token=True
reconnect_recommended=False
google_health_http_status=200
google_health_source_status=ok
real_http_attempted=True
safe_to_use_sleep_summary=True
backend_sleep_summary_source=google_health
backend_sleep_summary_available=True
backend_sleep_summary_is_real_data=True
backend_sleep_summary_positive_duration=True
provider_error_summary=None
real_request_smoke_status=OK
real_request_exit_code=0
```

This confirms the real Google Health HTTP boundary and normalized DRC
`/sleep/summary` backend handoff. It does not confirm Flutter Web display,
smartphone Web execution, screenshot review, or private Day55/Day66/Day78 marker
evidence.

The next private command starts Flutter Web against the already-running actual
backend:

```powershell
cd app
flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
cd ..
```

Keep the actual LAN IP, screenshot, target date, exact sleep values, raw Google
Health payloads, OAuth values, credentials, private paths, and backend logs
local-only.

E-7 preserves:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

### v2.0.0 Commit E-8 actual Google Health PC/smartphone Web and private screenshot checkpoint

E-8 records public-safe markers from the completed PC and smartphone Web check
against the actual configured DRC backend. The visible UI confirmed `Google Health`,
`実データ`, `取得済み`, and a normalized sleep summary without mock, fallback, or
error status. A smartphone screenshot was captured and stored under an ignored
local path; the image and private path are not committed.

Recorded public-safe markers:

```text
actual_drc_backend_api_status=confirmed
pc_web_ui_confirmed=True
smartphone_web_ui_confirmed=True
data_source_google_health_visible=True
real_data_label_visible=True
availability_acquired_visible=True
normalized_sleep_summary_visible=True
error_or_fallback_visible=False
private_screenshot_captured=True
private_screenshot_stored_under_ignored_path=True
private_screenshot_git_ignore_confirmed=True
```

The successful smartphone delivery used a release Web build served over the
private LAN. LAN IPs, screenshot bytes, exact personal sleep values, dates,
timestamps, raw Google Health payloads, OAuth values, credentials, private paths,
and raw logs remain local-only.

E-8 does not author or validate the private Day55, Day66, and Day78 marker-only
evidence files and therefore preserves:

```text
real_google_health_sleep_data: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
release_completion_status: NOT_RELEASED
```

## v2.0.0 Commit E-9 public-safe real Google Health sleep-data acceptance synchronization

E-9 synchronizes `real_google_health_sleep_data: ACCEPTED` from the completed
private configured Google Health run using public-safe markers only. Day55, Day66,
and Day78 marker-only evidence all validated as accepted; the Day78 screenshot
reference was public-safe; and the forbidden success-state checks remained clear.

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_actual_run_checkpoint.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_acceptance_sync.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py

cd app
flutter test
cd ..
```

The acceptance-sync smoke reads committed source-tree markers only. It does not
call Google Health, read credentials or OAuth tokens, start backend/Web processes,
inspect screenshot bytes, read `operator_evidence/`, or build release artifacts.
Raw screenshots, raw Google Health payloads, exact sleep values, precise timestamps,
OAuth values, credentials, authorization headers, LAN IPs, private paths, and
private evidence files remain uncommitted.

```text
real_google_health_sleep_data: ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```

E-9 closes only the real Google Health sleep-data requirement. The next step is
the Day69 public repository final sweep, followed by accepted private manifest
validation and final fixed-zip release handling.

## v2.0.0 Commit G-2 public-safe public repository final sweep acceptance synchronization

G-2 synchronizes `public_repo_final_sweep_review: ACCEPTED` from the completed Day69 marker-only operator review. The evidence validator accepted all required review markers, reported public-safe handling, and found no forbidden success states. G-1 had already removed tracked private evidence from the public repository surface and normalized secret-shaped/private-path fixtures before the final sweep.

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_public_repo_final_sweep.py
python scripts\smoke_framework_v200_public_repo_final_sweep_acceptance_sync.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_acceptance_sync.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
python scripts\smoke_framework_v200_final_prerelease_aggregate_gate.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py

cd app
flutter test
cd ..
```

The acceptance-sync smoke reads committed source-tree markers only. It does not read private operator evidence, publish to GitHub, build release artifacts, create release zips, call providers, call Google Health, start backend/Web services, open browsers, inspect screenshots, or access external networks. Raw evidence, operator evidence files, screenshots, audio, provider payloads, health data, secrets, tokens, LAN IPs, private paths, and local artifacts remain ignored and uncommitted.

```text
public_repo_final_sweep_review: ACCEPTED
final_aggregate_review: NOT_ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```

G-2 closes only the public repository final sweep requirement. The next step is the Day70 final prerelease aggregate review, followed by accepted private manifest validation and final fixed-zip release handling.

## v2.0.0 Commit G-3 public-safe final prerelease aggregate acceptance synchronization

G-3 synchronizes `final_aggregate_review: ACCEPTED` from the completed Day70 marker-only operator review. The validator accepted the foundation, real Web capability, image, Day69 public repository, smartphone Web, API-level, mock-safe, and credential-free review markers; reported public-safe handling; found no forbidden success states; and confirmed that the aggregate check did not create a release zip.

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_prerelease_aggregate_gate.py
python scripts\smoke_framework_v200_final_prerelease_aggregate_acceptance_sync.py
python scripts\smoke_framework_v200_public_repo_final_sweep_acceptance_sync.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_acceptance_sync.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py

cd app
flutter test
cd ..
```

The acceptance-sync smoke reads committed source-tree markers only. It does not read private operator evidence, build or inspect release zips, call providers or Google Health, start backend/Web services, open browsers, inspect screenshots/audio/images, publish to GitHub, create tags, or access external networks. Raw evidence, operator evidence files, screenshots, audio, provider payloads, health data, secrets, tokens, LAN IPs, private paths, release zips, and local artifacts remain ignored and uncommitted.

```text
public_repo_final_sweep_review: ACCEPTED
final_aggregate_review: ACCEPTED
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```

G-3 closes only the final aggregate review requirement. The next step is the accepted private evidence manifest. The final fixed release zip must still be built once only after that manifest is accepted, then verified as the same fixed artifact before tagging or releasing v2.0.0.
## v2.0.0 Commit G-4 Day80 private manifest validation handoff hardening

G-4 hardens the existing Day80 accepted private evidence manifest validator before the real ignored manifest is populated. It adds source-tree positive and negative contract checks and documents the exact local manifest path and validation command.

Changed behavior:

```text
public Day80 example manifest: rejected-as-template
complete synthetic marker-only manifest: accepted
missing required evidence item: rejected
screenshot_missing=true: rejected
unsafe screenshot reference: rejected
placeholder_success=true: rejected
private_paths_included=true: rejected
```

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py
python scripts\smoke_framework_v200_final_prerelease_aggregate_acceptance_sync.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py

cd app
flutter test
cd ..
```

The next private operator step is to copy the public example to `operator_evidence/v200_accepted_web_evidence_manifest_day80.json`, populate only the ignored copy from the actual accepted private evidence set, and run the Day80 smoke with `--manifest-json`. G-4 itself does not read `operator_evidence/`, accept the private manifest, build a release zip, create a tag, or release v2.0.0.

```text
accepted_private_evidence_manifest: NOT_ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```

## v2.0.0 Commit G-5 public-safe accepted private evidence manifest synchronization

G-5 synchronizes `accepted_private_evidence_manifest: ACCEPTED` after the ignored Day80 manifest validated successfully against the actual accepted private evidence set. Only public-safe marker results are committed; the private manifest, screenshot files, raw audio, raw health data, prompts, provider payloads, secrets, tokens, LAN IPs, and private paths remain ignored and uncommitted.

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py
python scripts\smoke_framework_v200_final_prerelease_aggregate_acceptance_sync.py
python scripts\smoke_framework_v200_public_repo_final_sweep_acceptance_sync.py
python scripts\smoke_framework_v200_real_google_health_sleep_data_acceptance_sync.py
python scripts\smoke_framework_v200_real_tts_web_audio_acceptance_sync.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py

cd app
flutter test
cd ..
```

The acceptance-sync smoke reads committed source-tree markers only. It does not read the ignored Day80 manifest, inspect private screenshots or audio, call providers or Google Health, start backend/Web services, build a release zip, publish to GitHub, create a tag, or access external networks.

```text
public_repo_final_sweep_review: ACCEPTED
final_aggregate_review: ACCEPTED
accepted_private_evidence_manifest: ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```

G-5 closes only the accepted private evidence manifest requirement. The next step is to build one final fixed v2.0.0 release zip after this acceptance and verify that exact artifact without rebuilding.

## v2.0.0 Commit G-6 committed-HEAD final zip and direct Day82/Day83 verification hardening

G-6 adds `build_v200_final_fixed_release_zip_from_head.ps1`. The script requires a clean tracked/non-ignored working tree, validates the committed G-5 public-safe state, requires an explicit path to the accepted Day80 manifest outside the Public repository, records the current branch and committed `HEAD`, creates a detached temporary worktree at that exact commit, invokes `build_release.bat release` exactly once, refuses to overwrite an existing release artifact, and prints the repository-relative zip path, size, and SHA-256. The external private manifest is validated without being copied into the detached worktree or release zip and without printing its path. The existing package builder and package checker are also hardened to exclude and reject the worktree `.git` metadata file.

G-6 also upgrades the Day82 and Day83 smoke paths from marker-only validation to direct same-zip inspection through `--release-zip`.

Source-tree verification:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py
python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py
python scripts\smoke_framework_v200_final_release_readiness_with_web_evidence.py

cd app
flutter test
cd ..
```

G-6 does not build or accept the final fixed release zip. Run the new builder only after this commit is committed and pushed and the source-tree/Flutter checks pass.

```text
accepted_private_evidence_manifest: ACCEPTED
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```

## v2.0.0 Commit G-7 immutable final release artifact record

G-7 adds `backend/app/services/framework_v200_final_release_artifact_record.py`, `scripts/smoke_framework_v200_final_release_artifact_record.py`, and `docs/v200_final_release_artifact_record.md`. Its original same-repository contract bound matching `main`/`develop` refs. Public-P4 supersedes that historical topology: the active Public record binds Public `main`, `origin/main`, the annotated `DRC_v2.0.0` tag target, exactly one Public root commit, fixed zip basename, byte size, SHA-256, Day82/Day83 acceptance, same-artifact use, and public-safe omission markers; legacy `develop_head` fields are rejected.

The source-tree smoke validates a synthetic accepted record, rejects hash mismatch, branch mismatch, lightweight tag, private-path inclusion, and post-build source-change cases, and verifies that the G-7 files are required by both Day82 and Day83 release surfaces.

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_release_artifact_record.py
```

The historical G-7 sequence aligned `main`/`develop`; do not use that instruction for the clean-history Public release. After the final Public pre-build synchronization commit is pushed, confirm `Public main HEAD == origin/main`, one Public root commit, a clean working tree, and no existing `DRC_v2.0.0` tag, then build one new fixed zip from that committed Public HEAD. Do not create a source or documentation commit after the build. The accepted public-safe record is placed in the annotated tag message and copied into the GitHub Release body; raw evidence and private paths remain excluded.

```text
final_release_artifact_record: contract-ready-artifact-not-recorded
final_fixed_release_zip: not-built
DRC_v2.0.0_tag: not-created
release_status: NOT_RELEASED
```


## Public-P3.1 generated-cache hardening

The canonical Public export must remain untouched. Run Python and Flutter verification in a disposable export copy. Public-P2 strict inspection rejects `__pycache__`, `.pyc`, `.pyo`, and Flutter generated directories before Public Git initialization.

## v2.1.0 W-5a accepted Fitbit real operator contract and preflight

Detailed runbook: `docs/v210_fitbit_real_operator_runbook.md`.

Run the public-safe source-tree gate from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_v210_fitbit_real_operator_preflight.py
python scripts\smoke_v210_fitbit_real_operator_preflight.py --check-example
python scripts\check_v210_fitbit_real_operator_contract.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The default/example preflight is credential-free and network-free. A private
operator profile is validated with key names and safe markers only:

```powershell
python scripts\smoke_v210_fitbit_real_operator_preflight.py `
  --env-file .\backend\env_profiles\fitbit_real_operator.local.env

powershell -ExecutionPolicy Bypass -File `
  .\backend\scripts\run_fitbit_real_operator.ps1 `
  -EnvFile .\backend\env_profiles\fitbit_real_operator.local.env `
  -ValidateOnly
```

Legacy Fitbit backend execution is retired in W-5b1 and refuses to
run without consent:

```powershell
python scripts\smoke_v210_fitbit_real_operator_execution.py `
  --base-url http://127.0.0.1:8000 `
  --allow-real-request
```

W-5a acceptance did not perform OAuth, print token/env values, call Fitbit, or verify
smartphone Web, accept W-5, build a release ZIP, or change release records.


## v2.1.0 W-5b1 Google Health migration audit

```powershell
python scripts\check_v210_google_health_migration_audit.py
python -m pytest -q backend/tests/test_google_health_v4_migration_contract.py
```

This gate is mock-safe, makes no OAuth or provider request, and confirms that legacy Fitbit execution is blocked.

## v2.1.0 W-5b2 configured Google Health operator verification record

Detailed record: `docs/v210_google_health_real_operator_verification.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_google_health_migration_audit.py
python scripts\check_v210_google_health_real_operator_verification.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The W-5b2 source-tree check reads Public documentation only. It records that the
ignored operator profile and ValidateOnly launcher passed, the guarded stored-token
refresh succeeded, the explicit real Google Health request returned HTTP 200, the
backend normalized available real Google Health sleep data, and PC/smartphone Web
showed Google Health / 実データ / 取得済み. It does not read local env, credentials,
tokens, raw provider data, or screenshots and does not make a network request.

W-5b2 is `COMPLETED / ACCEPTED`. Acceptance records execution commit `ed50d9e`,
HTTP 200, normalized real Google Health sleep, PC/smartphone Web display, 100
backend tests, 57 Flutter tests, and operator-confirmed Fitbit Versa 2 origin.
Screenshots and private sleep values remain outside Git. Parent W-5 is completed;
C-1, T-1, and V-1 are completed and accepted; R-1a is completed/accepted; R-1b is completed/accepted at implementation commit `72dd42c`; R-1c and R-1d are completed/accepted; R-1e and parent R-1 are completed/accepted; v2.1.0 is released.

## v2.1.0 R-1c accepted final PC/smartphone Web evidence validator

```powershell
python scripts\check_v210_final_smartphone_web_evidence.py
```

The default check is credential-free, provider-free, browser-free, screenshot-free, and artifact-free. It validates the committed accepted R-1c record, confirms that the public example manifest remains deliberately rejected, and records accepted candidate source `1e922e68685dadfc1008f1119d0ce492584e8f19` without reading ignored evidence.

The ignored private manifest may be revalidated locally with:

```powershell
python scripts\check_v210_final_smartphone_web_evidence.py `
  --manifest-json .\operator_evidence\v210_final_smartphone_web_evidence_r1c.json
```

The accepted record covers six evidence items on PC and smartphone Web, public-safe opaque screenshot references, actual DRC Backend use, real Google Health and Framework/TTS execution, and no committed raw/private evidence. R-1c and R-1d are `COMPLETED / ACCEPTED`; R-1e is `COMPLETED / ACCEPTED`; explicit approval, publication, and post-publication verification passed.


## Historical v2.1.0 R-1d implementation and verifier

Source-only implementation check:

```powershell
python scripts\check_v210_fixed_release_zip.py
```

After the implementation commit is accepted and pushed, the one-time builder is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_v210_fixed_release_zip_from_head.ps1
```

The builder requires clean synchronized official Public `main`, preserves the annotated v2.0.0/v2.0.1 tags, requires `DRC_v2.1.0` to be absent, rejects an existing `DailyRhythmCompanion_v2.1.0_*.zip`, creates a detached committed-HEAD worktree, and invokes `build_release.bat release` exactly once. It prints the exact source HEAD, basename, size, and SHA-256 and stops before verification or publication.

The generated ZIP must then be passed explicitly to `check_v210_fixed_release_zip.py` with the builder-recorded source HEAD and SHA-256. The verifier never invokes a builder and confirms that the same file remains unchanged before and after package inspection, safe extraction, tests, and requested builds.

### Windows PowerShell 5.1 preflight

The Windows release host may use Windows PowerShell 5.1 without `pwsh`. Before the one-time build, run:

```powershell
powershell.exe `
  -NoProfile `
  -ExecutionPolicy Bypass `
  -File .\build_v210_fixed_release_zip_from_head.ps1 `
  -PreflightOnly
```

This runs the strict source/test/build gate but stops with build invocation count `0` and creates no ZIP. The builder uses a URI-based relative-path helper instead of the PowerShell 7-only `[IO.Path]::GetRelativePath()` API.

## v2.1.0 R-1d accepted fixed ZIP record

```powershell
python scripts\check_v210_fixed_release_zip.py
```

```text
source HEAD: 6e7af31f85eb6ee7887df3e184ac6a58142d6fec
fixed ZIP basename: DailyRhythmCompanion_v2.1.0_20260725_160036.zip
fixed ZIP size bytes: 1747337
fixed ZIP SHA-256: 55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5
accepted-candidate builder invocation count: 1
same-artifact verification: passed
verifier rebuilt artifact: false
tag / GitHub Release at R-1d acceptance: not created
```

R-1d is `COMPLETED / ACCEPTED`. R-1e is completed/accepted after explicit tuple approval, publication, and downloaded-asset verification.


## v2.1.0 R-1e publication completion

R-1e and parent R-1 are `COMPLETED / ACCEPTED`. Explicit approval was received for the exact tuple, annotated tag `DRC_v2.1.0` was published at `6e7af31f85eb6ee7887df3e184ac6a58142d6fec`, the GitHub Release was published with the unchanged fixed ZIP, and the downloaded asset was independently verified at `1747337` bytes / SHA-256 `55bf584592b1824948ec847205132582a436f2c521feb593bac914a4904074e5`. No provider, runtime, dependency, asset, historical release record, or fixed ZIP content changed in the post-publication source sync.


## v3.0.0 RT-0a realtime current behavior inventory

Detailed inventory: `docs/v300_realtime_current_behavior_inventory.md`.

Run the credential-free source-tree gate from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

RT-0a is `COMPLETED / ACCEPTED`. Acceptance passed after compileall, the
credential-free source-tree gate, 110 Backend tests, 103 Flutter tests, diff
review, and explicit operator approval. The check validates the actual v2.1.0 voice-input, chat, TTS, character, motion, transport,
permission, and integration-cost boundaries while protecting Backend/Flutter
runtime, existing tests, platform metadata, version metadata, and immutable v2.x
release records with normalized hashes.

The gate does not import AI Character Framework, call providers or network, read
private env files, open a microphone, start Flutter/browser execution, or start a
realtime session. RT-0b is `CURRENT / NOT_COMPLETED` and `NOT_STARTED`; RT-0c
remains planned, and RT-1 through RT-9 remain blocked.


## v3.0.0 RT-0b released Framework public realtime readiness

Detailed readiness matrix: `docs/v300_framework_realtime_contract_readiness.md`.

At RT-0a acceptance, RT-0b was `NOT_STARTED`. RT-0b later became
`COMPLETED / ACCEPTED`; at that checkpoint RT-0c became current and not started. RT-0c is now `COMPLETED / ACCEPTED`.

Run the credential-free source-tree review from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

The RT-0b gate checks the recorded released Framework snapshot:

```text
release: v5.0.0
commit: 6494da306015c4f714f869b43e773ba51a2478a2
public readiness: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
```

Expected accepted output:

```text
v300_framework_realtime_contract_readiness_status: completed-accepted
v300_framework_release_snapshot: v5.0.0@6494da306015c4f714f869b43e773ba51a2478a2
v300_framework_public_readiness: blocked-framework-update-required
v300_framework_required_contracts_ready: False
v300_rt0b_drc_runtime_changed: False
v300_rt0b_existing_tests_changed: False
v300_rt0b_framework_runtime_changed: False
v300_rt0b_real_provider_execution: False
v300_rt1_authorization: blocked-pending-rt0c-and-released-fw-update
```

The gate protects Backend/Flutter runtime, existing tests, platform/version
metadata, accepted RT-0a evidence, and immutable v2.x release records with
normalized hashes. It verifies that the review records:

```text
- public text-chat and one-shot voice-output current-use boundaries;
- missing public voice-input/STT, realtime, cancellation, queue, and motion contracts;
- partial streaming/events, capabilities, errors, factories, and close lifecycle;
- absent standard installable package metadata in the inspected release;
- README session.speak(...) versus implementation create_output(...) mismatch;
- Framework feedback FW-F1 through FW-F12;
- BLOCKED_FRAMEWORK_UPDATE_REQUIRED and blocked RT-1 authorization.
```

This check does not import or clone AI Character Framework, call GitHub or a
provider, read private env files, open a microphone, start Flutter/browser
execution, or start a realtime session. RT-0b changed no DRC or Framework
runtime. RT-0c is current and RT-1 through RT-9 remain blocked.

## v3.0.0 RT-0c Framework v5.1.0 reassessment

Detailed reassessment: `docs/v300_framework_v510_reassessment.md`.

RT-0a, RT-0b, and RT-0c are `COMPLETED / ACCEPTED`. No v3.0.0 small commit
is current while the required Framework realtime public contracts remain unreleased.

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python scripts\check_v300_framework_v510_reassessment.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

The RT-0c gate records:

```text
Framework release: v5.1.0
Tag commit: b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
Host-app foundation: SUBSTANTIALLY_READY_WITH_TRANSITION_GAPS
Realtime decision: BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING
RESOLVED_V510: FW-F4, FW-F5, FW-F7, FW-F8
PARTIAL_V510: FW-F1, FW-F2, FW-F3, FW-F6
MISSING_REALTIME_BLOCKER: FW-F9, FW-F10, FW-F11, FW-F12
```

Accepted output:

```text
v300_framework_v510_reassessment_status: completed-accepted
v300_framework_release_snapshot: v5.1.0@b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
v300_framework_host_app_foundation: substantially-ready-with-transition-gaps
v300_framework_realtime_prerequisites_ready: False
v300_framework_feedback_resolved: FW-F4,FW-F5,FW-F7,FW-F8
v300_framework_feedback_partial: FW-F1,FW-F2,FW-F3,FW-F6
v300_framework_feedback_missing: FW-F9,FW-F10,FW-F11,FW-F12
v300_rt0c_drc_runtime_changed: False
v300_rt0c_existing_tests_changed: False
v300_rt0c_framework_runtime_changed: False
v300_rt0c_real_provider_execution: False
v300_rt1_authorization: blocked-pending-released-voice-input-realtime-cancel-contracts
v300_rt6_authorization: blocked-pending-released-motion-contract
```

The gate is source-tree-only and credential-free. It protects DRC runtime,
existing tests, platform/version metadata, accepted RT-0a/RT-0b evidence, and
immutable v2.x release records. It does not import Framework, call GitHub or a
provider, open a microphone, or start a realtime session.

## v3.0.0 RT-1a Framework v5.2.0 public-contract adoption check

Detailed contract: `docs/v300_framework_v520_contract_adoption.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python scripts\check_v300_framework_realtime_contract_readiness.py
python scripts\check_v300_framework_v510_reassessment.py
python scripts\check_v300_framework_v520_contract_adoption.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

The RT-1a check is credential-free, provider-free, microphone-free,
network-free, playback-free, and motion-runtime-free. RT-1a is COMPLETED / ACCEPTED
after compileall, the RT-0/RT-1a gates, Backend 110 tests through the DRC `.venv`,
Flutter 103 tests, diff review, and explicit operator approval passed. It preserves
the accepted RT-0 records and all Backend/Flutter runtime and existing tests while recording:

```text
RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED
real Framework realtime execution: not ready
next implementation: RT-1b CURRENT / NOT_COMPLETED; NOT_STARTED; Backend model/normalizer only
```


## v3.0.0 RT-1b Backend realtime normalization check

Detailed contract: `docs/v300_backend_realtime_normalization.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_backend_realtime_normalization.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests/test_framework_realtime_normalizer.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

Current acceptance state: `COMPLETED / ACCEPTED`.

RT-1b adds DRC-owned Backend realtime models and a Framework v5.2.0 contract
normalizer only. It does not import Framework, add a route or transport, use a
microphone, call providers, change Flutter runtime, or start realtime execution.
The docs-only RT-0a through RT-1a whole-tree hash gates are historical and are
not rerun after this first v3 Backend code checkpoint.

RT-1b was accepted on 2026-07-26 after compileall, the RT-1b gate, focused
Backend 6, full Backend 116 with one existing warning, Flutter 103,
`git diff --check`, 10-file diff review, and explicit operator approval passed.
The accepted check reports parent RT-1 completed and RT-2 guarded-capture
planning authorized.


## v3.0.0 RT-2a microphone permission/capture inventory check

Detailed contract: `docs/v300_microphone_permission_capture_inventory.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_microphone_permission_capture_inventory.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
git status --short
```

Current implementation state: `COMPLETED / ACCEPTED`. RT-2b is `CURRENT / NOT_COMPLETED; NOT_STARTED`.

RT-2a is docs/test-only. The gate freezes Backend and Flutter runtime/test trees,
`pubspec.yaml`, Android/iOS permission metadata, versions, and release notes while
recording the RT-2b through RT-2e split. It does not request permission, access a
microphone, capture audio, import Framework, call a provider, upload audio, or
start STT/realtime execution.

Expected accepted output:

```text
v300_microphone_permission_capture_inventory_status: completed-accepted
v300_rt2a_backend_runtime_changed: False
v300_rt2a_flutter_runtime_changed: False
v300_rt2a_existing_tests_changed: False
v300_rt2a_microphone_dependency_added: False
v300_rt2a_android_record_audio_added: False
v300_rt2a_ios_microphone_usage_added: False
v300_rt2a_microphone_accessed: False
v300_rt2a_audio_captured: False
v300_rt2_parent_status: current-pending-rt2b-implementation
v300_rt2b_authorization: authorized-permission-contract-and-fake-gateway-only
```

RT-2a was accepted on 2026-07-26 after compileall, the RT-1b and RT-2a gates, Backend 116 with one existing warning, Flutter 103, `git diff --check`, seven-file diff review, and explicit operator approval passed.


## v3.0.0 RT-2b microphone permission contract check

Detailed contract: `docs/v300_microphone_permission_contract.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_microphone_permission_contract.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter test test/microphone_permission_test.dart
flutter test
cd ..

git diff --check
git status --short
```

Current implementation state: `COMPLETED / ACCEPTED`.

RT-2b adds the app-owned Flutter permission model/interface and deterministic
fake gateway only. It does not add a permission plugin, capture package, platform
declaration, MethodChannel, UI integration, microphone access, audio capture,
Backend change, Framework import, provider execution, or STT execution. The
accepted docs-only RT-2a whole-tree hash gate is historical and is not rerun after
this first RT-2 Flutter code checkpoint.

Expected accepted output:

```text
v300_microphone_permission_contract_status: completed-accepted
v300_rt2b_flutter_contract_added: True
v300_rt2b_focused_tests_added: True
v300_rt2b_dependency_added: False
v300_rt2b_platform_permission_added: False
v300_rt2b_method_channel_added: False
v300_rt2b_ui_changed: False
v300_rt2b_backend_changed: False
v300_rt2b_microphone_accessed: False
v300_rt2b_audio_captured: False
v300_rt2_parent_status: current-pending-rt2c-implementation
v300_rt2c_authorization: authorized-platform-permission-wiring-without-capture-only
```

RT-2b was accepted on 2026-07-26 after compileall, the RT-2b gate, focused Flutter 9, full Flutter 112, Backend 116 with one existing warning, `git diff --check`, nine-file review, the portable protected-surface gate fixes, and explicit operator approval passed. RT-2c is COMPLETED / ACCEPTED on 2026-07-27; RT-2d is CURRENT / NOT_COMPLETED and NOT_STARTED.


## v3.0.0 RT-2c microphone platform permission wiring check

Detailed contract: `docs/v300_microphone_platform_permission_wiring.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter pub get
flutter analyze
flutter test test/permission_handler_microphone_permission_gateway_test.dart
flutter test
flutter build apk --debug
cd ..

.\.venv\Scripts\python.exe scripts\check_v300_microphone_platform_permission_wiring.py

git diff --check
git status --short
```

Current implementation state: `COMPLETED / ACCEPTED`.

RT-2c pins `permission_handler` 12.0.3, adds an Android/iOS-only adapter for the
existing app-owned permission gateway, declares Android `RECORD_AUDIO`, and adds
the iOS microphone usage description. The gateway is not referenced by startup
or `HomeScreen`, and focused tests inject a fake driver. No permission dialog,
microphone access, capture, raw audio, upload, Framework/provider call, or STT is
executed by these tests.

Expected accepted output:

```text
v300_microphone_platform_permission_wiring_status: completed-accepted
v300_rt2c_permission_dependency_added: True
v300_rt2c_lock_resolved: True
v300_rt2c_gateway_added: True
v300_rt2c_android_record_audio_added: True
v300_rt2c_ios_microphone_usage_added: True
v300_rt2c_windows_generated_registration_added: True
v300_rt2c_ui_changed: False
v300_rt2c_backend_changed: False
v300_rt2c_permission_request_executed: False
v300_rt2c_microphone_accessed: False
v300_rt2c_audio_captured: False
v300_rt2_parent_status: current-pending-rt2d-implementation
v300_rt2d_authorization: authorized-capture-lifecycle-and-fake-engine-only
```

`flutter pub get` modifies `app/pubspec.lock` and, because the resolved package
includes `permission_handler_windows`, also regenerates
`app/windows/flutter/generated_plugin_registrant.cc` and
`app/windows/flutter/generated_plugins.cmake`. The gate allows those two generated
files only when each contains exactly one expected permission-handler registration
marker. Include all three generated/resolved files in the 16-file RT-2c review and
the eventual acceptance commit. The Android APK build verifies native plugin
compilation without requesting the permission. iOS build execution remains
unavailable on Windows and is not claimed. Acceptance evidence recorded on
2026-07-27 at implementation commit `fe26c3c`: `flutter analyze` reported no issues; focused Flutter 13, full
Flutter 125, and Backend 116 passed; the RT-2c gate and `git diff --check`
passed; the Android debug APK was produced. The build emitted a Kotlin daemon
incremental-cache warning in `audioplayers_android`, then completed through
Gradle fallback.


## v3.0.0 RT-2d microphone capture lifecycle check

Detailed contract: `docs/v300_microphone_capture_lifecycle.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_microphone_capture_lifecycle.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/microphone_capture_test.dart
flutter test
flutter build apk --debug
cd ..

git diff --check
git status --short
```

Current implementation state: `COMPLETED / ACCEPTED`. RT-2e is `CURRENT / NOT_COMPLETED; NOT_STARTED`.

RT-2d adds the DRC-owned lifecycle/request/result/controller contracts, a hard
duration deadline boundary, and a deterministic fake capture engine. It calls
only the permission gateway check operation. It adds no real capture dependency,
UI wiring, platform change, microphone access, audio persistence/upload, raw
bytes/path/handle, Backend change, Framework/provider call, or STT execution.

Expected accepted output:

```text
v300_microphone_capture_lifecycle_status: completed-accepted
v300_rt2d_capture_contract_added: True
v300_rt2d_controller_added: True
v300_rt2d_fake_engine_added: True
v300_rt2d_single_active_capture_enforced: True
v300_rt2d_bounded_duration_enforced: True
v300_rt2d_permission_request_executed: False
v300_rt2d_real_capture_dependency_added: False
v300_rt2d_ui_changed: False
v300_rt2d_backend_changed: False
v300_rt2d_microphone_accessed: False
v300_rt2d_audio_captured: False
v300_rt2d_raw_audio_exposed: False
v300_rt2_parent_status: current-pending-rt2e-implementation
v300_rt2e_authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only
```

RT-2d acceptance completed on 2026-07-27 after compileall, the RT-2d gate,
`flutter analyze` with no issues, focused Flutter 17, full Flutter 142, Backend
116 with one existing warning, `git diff --check`, nine-file review, and explicit
operator approval passed. No permission request, real microphone access, audio
capture, raw-audio exposure, Backend upload, Framework/provider call, or STT
execution occurred. RT-2e is current but not started.


## v3.0.0 RT-2e-a real capture adapter readiness check

Detailed contract: `docs/v300_microphone_real_capture_adapter_readiness.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_microphone_real_capture_adapter_readiness.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

RT-2e-a is `COMPLETED / ACCEPTED` and docs/test-only. It records the
exact accepted SDK/dependency/capture surface and selects `record` 6.2.1 for the
later RT-2e-b adapter. Acceptance passed after compileall, the RT-2e-a gate,
`flutter analyze` clean, full Flutter 142, Backend 116 with one existing warning,
`git diff --check`, seven-file review, and explicit operator approval. It does
not add the package, alter a lockfile or generated plugin registration, change
Flutter runtime/platform/UI code, request permission, open a microphone,
capture/create/upload audio, expose raw bytes/path/handles, or execute STT.
RT-2e-b is CURRENT / NOT_COMPLETED and NOT_STARTED.

Expected output:

```text
v300_microphone_real_capture_adapter_readiness_status: completed-accepted
v300_rt2ea_exact_current_surface_inspected: True
v300_rt2ea_record_candidate_selected: record-6.2.1
v300_rt2ea_record_7x_compatible_with_current_sdk: False
v300_rt2ea_dependency_added: False
v300_rt2ea_flutter_runtime_changed: False
v300_rt2ea_platform_files_changed: False
v300_rt2ea_permission_request_executed: False
v300_rt2ea_microphone_accessed: False
v300_rt2ea_audio_captured: False
v300_rt2e_parent_status: current-pending-rt2eb-implementation
v300_rt2eb_authorization: authorized-injectable-record-adapter-and-private-temporary-artifact-fake-tests-only
```


## v3.0.0 RT-2e-b record microphone capture adapter check

Detailed contract: `docs/v300_record_microphone_capture_adapter.md`.

After applying the implementation patch, resolve the exact dependencies before
running the gate:

```powershell
cd app
flutter pub get
cd ..

.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_record_microphone_capture_adapter.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/record_microphone_capture_engine_test.dart
flutter test test/microphone_capture_test.dart
flutter test
cd ..

git diff --check
git status --short
```

RT-2e-b pins `record` 6.2.1 and direct `path_provider` 2.1.6. It adds
an injectable package driver, a private temporary path/artifact boundary, an
opaque capture id, cleanup on start/cancel/error/dispose, safe controller
metadata propagation, and fake-driver tests. File mode uses WAV, 16 kHz, mono.
The Android debug APK build verifies native dependency/registration compilation
without launching the app or accessing a microphone. `startStream` is forbidden. The production driver is compiled but not wired to
startup/UI and is not used by tests. No real microphone access, real audio
capture, permission request, upload, Framework/provider call, or STT execution
is performed in this checkpoint. RT-2e-b is COMPLETED / ACCEPTED after
operator dependency resolution, generated plugin review, analyzer cleanup,
focused Flutter 18/18, full Flutter 161, Backend 116 with one existing warning,
the RT-2e-b gate, Android debug APK compilation, `git diff --check`, 19-file
review, and explicit operator approval. The Kotlin incremental-cache daemon
reported a cross-drive cache error before Gradle fallback produced the APK.
RT-2e-c is CURRENT / NOT_COMPLETED and NOT_STARTED.

Expected accepted output:

```text
v300_record_microphone_capture_adapter_status: completed-accepted
v300_rt2eb_record_dependency_resolved: True
v300_rt2eb_path_provider_direct_dependency: True
v300_rt2eb_injectable_driver_added: True
v300_rt2eb_private_artifact_boundary_added: True
v300_rt2eb_controller_safe_metadata_propagation_added: True
v300_rt2eb_fake_driver_tests_added: True
v300_rt2eb_generated_plugin_registration_review_ready: True
v300_rt2eb_real_permission_request_executed: False
v300_rt2eb_real_microphone_accessed: False
v300_rt2eb_real_audio_captured: False
v300_rt2eb_raw_audio_exposed: False
v300_rt2e_parent_status: current-pending-rt2ec-implementation
v300_rt2ec_authorization: authorized-explicit-opt-in-real-device-bounded-capture-evidence-only
```

## v3.0.0 RT-2e-c1 operator capture harness readiness check

Detailed contract: `docs/v300_rt2ec_operator_capture_harness_readiness.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt2ec_operator_capture_harness_readiness.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

RT-2e-c1 is `COMPLETED / ACCEPTED` and was docs/test-only. It rereads the
accepted RT-2e-b source and fixes a later operator harness contract: separate
entrypoint, compile-time and in-app double opt-in, explicit permission and
capture actions, 15-second bound, automatic opaque-id cleanup, safe evidence
allowlist, unchanged default app, and no upload/STT. This checkpoint does not
add or run the harness and does not request permission, access a microphone, or
capture audio. RT-2e-c2 is CURRENT / NOT_COMPLETED and NOT_STARTED with
`authorized-separate-operator-harness-and-fake-widget-tests-only`; RT-2e-c3
remains blocked pending RT-2e-c2 acceptance.

Expected output:

```text
v300_rt2ec_operator_capture_harness_readiness_status: completed-accepted
v300_rt2ec1_exact_current_surface_inspected: True
v300_rt2ec1_separate_operator_entrypoint_planned: True
v300_rt2ec1_compile_time_opt_in_required: True
v300_rt2ec1_in_app_acknowledgement_required: True
v300_rt2ec1_permission_actions_explicit_only: True
v300_rt2ec1_maximum_capture_seconds: 15
v300_rt2ec1_private_artifact_auto_discard_required: True
v300_rt2ec1_safe_evidence_allowlist_required: True
v300_rt2ec1_default_app_wiring_changed: False
v300_rt2ec1_flutter_runtime_changed: False
v300_rt2ec1_permission_request_executed: False
v300_rt2ec1_microphone_accessed: False
v300_rt2ec1_audio_captured: False
v300_rt2ec_parent_status: current-pending-rt2ec2-implementation
v300_rt2ec2_authorization: authorized-separate-operator-harness-and-fake-widget-tests-only
v300_rt2ec3_authorization: authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only
```

## v3.0.0 RT-2e-c2 operator capture harness check

Detailed contract: `docs/v300_rt2ec_operator_capture_harness.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt2ec_operator_capture_harness.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/rt2ec_microphone_capture_operator_test.dart
flutter test
cd ..

git diff --check
git status --short
```

RT-2e-c2 is COMPLETED / ACCEPTED. It adds the separate
`main_rt2ec_operator.dart` target, fail-closed `DRC_RT2EC_OPERATOR=true` flag,
in-app acknowledgement before production dependency construction, explicit
permission/capture actions, exact 15-second bound, immediate
`discardPrivateArtifact`, safe evidence allowlist, and fake/widget tests. The
default app, dependencies, platform declarations, generated registration, and
Backend remain unchanged. Acceptance passed after compileall, the RT-2e-c2 gate,
Backend 116 with one existing warning, `flutter analyze`, focused Flutter 10,
full Flutter 171, `git diff --check`, exact twelve-file review, and explicit
operator approval. No real permission request, microphone access, audio capture,
upload, or STT execution occurred at the RT-2e-c2 checkpoint. RT-2e-c3 is now COMPLETED / ACCEPTED from the accepted physical-Android evidence. No upload or STT is authorized, and RT-3 remains BLOCKED_REAL_STT_NOT_IMPLEMENTED.

Expected output:

```text
v300_rt2ec_operator_capture_harness_status: completed-accepted
v300_rt2ec2_separate_entrypoint_added: True
v300_rt2ec2_compile_time_opt_in_added: True
v300_rt2ec2_acknowledgement_before_dependencies: True
v300_rt2ec2_explicit_permission_actions_added: True
v300_rt2ec2_bounded_capture_seconds: 15
v300_rt2ec2_private_artifact_auto_discard_added: True
v300_rt2ec2_safe_evidence_allowlist_added: True
v300_rt2ec2_fake_widget_tests_added: True
v300_rt2ec2_default_app_wiring_changed: False
v300_rt2ec2_dependency_changed: False
v300_rt2ec2_platform_files_changed: False
v300_rt2ec2_real_permission_request_executed: False
v300_rt2ec2_real_microphone_accessed: False
v300_rt2ec2_real_audio_captured: False
v300_rt2ec_parent_status: completed-accepted
v300_rt2ec3_authorization: authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only
v300_rt2ec3_status: completed-accepted
v300_rt2_status: completed-accepted
v300_next_phase: blocked-real-stt-not-implemented
```

## v3.0.0 RT-2e-c3a real Android capture preflight check

Detailed contract: `docs/v300_rt2ec_real_android_capture_preflight.md`.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt2ec_real_android_capture_preflight.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

RT-2e-c3a is COMPLETED / ACCEPTED and docs/test-only. It reread the accepted
operator target, permission gateway, record adapter, Android declaration, and
safe-evidence panel before any real-device execution. The gate fixes one
physical-Android target, exact separate-target launch, manual permission reset,
explicit check/request/start/stop actions, one non-sensitive capture stopped
before 15 seconds, immediate private-artifact discard, and marker-only evidence.
Acceptance passed with compileall, the RT-2e-c3a gate, Backend 116 with the
existing warning, `flutter analyze`, full Flutter 171, `git diff --check`, exact
ten-file review, and explicit operator approval. It did not launch Flutter,
connect a device, request permission, access a microphone, capture audio, create
operator evidence, upload audio, or execute STT at the RT-2e-c3a checkpoint. RT-2e-c3b is now COMPLETED / ACCEPTED from the accepted marker-only physical-Android run.

Expected output:

```text
v300_rt2ec_real_android_capture_preflight_status: completed-accepted
v300_rt2ec3a_exact_current_surface_inspected: True
v300_rt2ec3a_physical_android_required: True
v300_rt2ec3a_separate_operator_target_required: True
v300_rt2ec3a_compile_time_opt_in_required: True
v300_rt2ec3a_in_app_acknowledgement_required: True
v300_rt2ec3a_explicit_permission_request_required: True
v300_rt2ec3a_single_bounded_capture_required: True
v300_rt2ec3a_maximum_capture_seconds: 15
v300_rt2ec3a_private_artifact_cleanup_required: True
v300_rt2ec3a_safe_evidence_contract_added: True
v300_rt2ec3a_default_app_wiring_changed: False
v300_rt2ec3a_flutter_runtime_changed: False
v300_rt2ec3a_permission_request_executed: False
v300_rt2ec3a_microphone_accessed: False
v300_rt2ec3a_audio_captured: False
v300_rt2ec_parent_status: completed-accepted
v300_rt2ec3b_authorization: authorized-explicit-opt-in-real-android-bounded-capture-and-cleanup-evidence-only
v300_rt2ec3b_status: completed-accepted
v300_rt2_status: completed-accepted
v300_next_phase: blocked-real-stt-not-implemented
```


Checkpoint note: the c2 and c3a gates continue to report their own historical
non-execution facts (`real_permission_request_executed: False`, microphone/audio
false) because those facts describe those individual checkpoints. Their parent
and next-phase lines now reflect the accepted current state: RT-2 completed and
RT-3 blocked.

## v3.0.0 RT-2e-c3b real Android capture evidence check

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt2ec_real_android_capture_evidence.py
.\.venv\Scripts\python.exe -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

The gate validates the exact eleven-file acceptance surface or a clean tree, the
accepted source commit ancestry, the unchanged double-opt-in operator runtime
contract, and the marker-only evidence recorded in
`docs/v300_rt2ec_real_android_capture_evidence.md`. It does not connect a device,
request permission, access a microphone, replay audio, resolve private paths,
upload audio, or execute STT.

Expected output:

```text
v300_rt2ec_real_android_capture_evidence_status: completed-accepted
v300_rt2ec3b_source_commit: ddae21944ac0e251cd8194bf93982bd5dc7a4ae8
v300_rt2ec3b_target_class: physical-android
v300_rt2ec3b_operator_target_enabled: True
v300_rt2ec3b_acknowledgement_completed: True
v300_rt2ec3b_permission_status: granted
v300_rt2ec3b_permission_request_attempted: True
v300_rt2ec3b_capture_outcome: completed
v300_rt2ec3b_technical_code: capture_completed
v300_rt2ec3b_requested_maximum_duration_milliseconds: 15000
v300_rt2ec3b_captured_duration_milliseconds: 4820
v300_rt2ec3b_microphone_accessed: True
v300_rt2ec3b_audio_captured: True
v300_rt2ec3b_raw_audio_exposed: False
v300_rt2ec3b_private_artifact_registered: True
v300_rt2ec3b_private_artifact_discarded: True
v300_rt2ec3b_cleanup_succeeded: True
v300_rt2ec3b_backend_started: False
v300_rt2ec3b_audio_uploaded: False
v300_rt2ec3b_stt_executed: False
v300_rt2ec3b_post_run_working_tree_clean: True
v300_rt2_status: completed-accepted
v300_next_phase: blocked-real-stt-not-implemented
```

RT-2e-c3b is COMPLETED / ACCEPTED. RT-2 is closed as COMPLETED / ACCEPTED.
No upload or STT is authorized; RT-3 remains BLOCKED_REAL_STT_NOT_IMPLEMENTED.

## v3.0.0 RT-3a Framework v5.3.0 STT integration inventory

Detailed inventory:

```text
docs/v300_framework_v530_stt_integration_inventory.md
```

Set the already-vendored FW root in the current private operator shell, then run:

```powershell
$env:FRAMEWORK_ROOT = (Resolve-Path `
  ".\vendor\ai-character-framework-5.3.0").Path

python -m compileall -q backend scripts
python scripts\check_v300_framework_v530_stt_integration_inventory.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

The gate inspects source only. It does not import FW, load backend `.env`, read
credential values, read/upload audio, open a microphone, create a provider
client, execute STT, or change vendor files. It prints no private FW path.

Expected accepted-state markers include:

```text
v300_framework_v530_stt_integration_inventory_status: completed-accepted
v300_framework_public_host_audio_contract_present: True
v300_framework_public_voice_input_session_wiring_present: True
v300_framework_fake_adapter_present: True
v300_framework_guarded_real_adapter_present: True
v300_framework_real_provider_execution_present: False
v300_drc_capture_private_artifact_boundary_present: True
v300_drc_operator_auto_discard_present: True
v300_drc_backend_audio_upload_boundary_present: False
v300_drc_voice_input_endpoint_metadata_only: True
v300_rt3_parent_status: current-blocked-real-provider-execution-not-implemented
v300_rt3b_authorization: authorized-app-owned-host-audio-lifecycle-contract-fake-only
```


RT-3a acceptance evidence:

```text
source-only inventory gate: passed
Backend: 116 passed, one existing warning
flutter analyze: No issues found
Flutter: 171 passed
git diff --check: passed
exact changed surface: seven files
```

RT-3a is COMPLETED / ACCEPTED. RT-3b is CURRENT / NOT_COMPLETED and is authorized only for the app-owned fake-only host-audio lifecycle contract. Real STT acceptance remains blocked because FW v5.3.0 has no concrete provider execution.


## v3.0.0 RT-3b host-audio handoff lifecycle gate

```powershell
.\.venv\Scripts\python.exe scripts\check_v300_host_audio_handoff_lifecycle.py
```

Expected accepted-state markers:

```text
v300_host_audio_handoff_lifecycle_status: completed-accepted
v300_rt3b_app_owned_contract_added: True
v300_rt3b_opaque_artifact_retention_added: True
v300_rt3b_scoped_private_path_access_added: True
v300_rt3b_consume_cleanup_added: True
v300_rt3b_cancel_cleanup_added: True
v300_rt3b_close_cleanup_added: True
v300_rt3b_public_result_path_free: True
v300_rt3b_fake_consumer_tests_added: True
v300_rt3b_backend_changed: False
v300_rt3b_network_upload_added: False
v300_rt3b_framework_imported: False
v300_rt3b_provider_execution_executed: False
v300_rt3b_stt_executed: False
v300_rt3_parent_status: current-blocked-real-provider-execution-not-implemented
v300_rt3b_status: completed-accepted
v300_rt3c_status: current-not-completed
v300_rt3c_authorization: authorized-private-backend-staging-and-fake-fw-public-session-handoff-only
v300_rt3_real_acceptance: blocked-framework-real-provider-execution-not-implemented
```

The gate permits the exact RT-3b ten-file acceptance surface or a clean tree after commit. It does not execute Flutter, read audio, upload data, import the vendored Framework, call a provider, or perform STT.

RT-3b acceptance evidence: source gate, Backend 116 with one existing warning, clean Flutter analysis, focused Flutter 21, full Flutter 192, exact ten-file review, cleanup-retry test correction, and `git diff --check` passed.


## v3.0.0 RT-3c1 private staging and fake FW handoff readiness gate

```powershell
$env:FRAMEWORK_ROOT = (Resolve-Path `
  ".\vendor\ai-character-framework-5.3.0").Path

.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c_private_staging_fw_handoff_readiness.py
```

Expected accepted-state markers:

```text
v300_rt3c_private_staging_fw_handoff_readiness_status: completed-accepted
v300_rt3c1_exact_current_surface_inspected: True
v300_rt3c1_flutter_scoped_private_path_lease_present: True
v300_rt3c1_flutter_http_dependency_present: True
v300_rt3c1_backend_voice_input_metadata_only: True
v300_rt3c1_backend_private_staging_store_present_at_inventory: False
v300_rt3c1_backend_audio_upload_route_present: False
v300_rt3c1_backend_staging_lifecycle_config_present_at_inventory: False
v300_rt3c2_backend_private_staging_store_present: True
v300_rt3c2_backend_staging_lifecycle_config_present: True
v300_rt3c1_python_multipart_dependency_present: False
v300_rt3c1_bounded_streamed_wav_transport_selected: True
v300_rt3c1_framework_public_fake_file_handoff_present: True
v300_rt3c1_framework_real_provider_execution_present: False
v300_rt3c1_runtime_changed: False
v300_rt3c1_audio_read: False
v300_rt3c1_audio_uploaded: False
v300_rt3c1_framework_imported: False
v300_rt3c1_stt_executed: False
v300_rt3_parent_status: current-blocked-real-provider-execution-not-implemented
v300_rt3c_parent_status: current-pending-rt3c3-implementation
v300_rt3c1_status: completed-accepted
v300_rt3c2_status: completed-accepted
v300_rt3c2_implementation: completed-accepted
v300_rt3c3_status: current-not-completed
v300_rt3c3_implementation: not-started
v300_rt3c3_authorization: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
v300_rt3_real_acceptance: blocked-framework-real-provider-execution-not-implemented
```

RT-3c1 acceptance evidence: compileall, the source-only gate, Backend 116 with one existing warning, clean Flutter analysis, full Flutter 192, exact nine-file review, and `git diff --check` passed.

The gate validates source only. It does not import the vendored FW, read audio,
open a microphone, upload data, create staging files, start Backend/Flutter,
create provider clients, or execute STT.


## v3.0.0 RT-3c2 private Backend staging store gate

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt3c2_private_backend_staging_store.py
.\.venv\Scripts\python.exe -m pytest -q backend\tests\test_temporary_lifecycle_config.py backend\tests\test_voice_input_staging_store.py
.\.venv\Scripts\python.exe -m pytest -q backend\tests
```

Expected accepted-state markers:

```text
v300_rt3c2_private_backend_staging_store_status: completed-accepted
v300_rt3c2_config_defaults_added: True
v300_rt3c2_private_store_added: True
v300_rt3c2_opaque_id_added: True
v300_rt3c2_path_free_metadata: True
v300_rt3c2_bounded_chunk_staging_added: True
v300_rt3c2_single_use_consume_added: True
v300_rt3c2_explicit_discard_added: True
v300_rt3c2_cleanup_lifecycle_added: True
v300_rt3c2_upload_route_added: False
v300_rt3c2_flutter_changed: False
v300_rt3c2_framework_imported: False
v300_rt3c2_provider_execution_executed: False
v300_rt3c2_stt_executed: False
v300_rt3c_parent_status: completed-accepted
v300_rt3c2_status: completed-accepted
v300_rt3c3_status: completed-accepted
v300_rt3c3_implementation: completed-accepted
v300_rt3c4_status: completed-accepted
v300_rt3c4_implementation: completed-accepted
v300_rt3c4_authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
```

RT-3c2 acceptance evidence: compileall, four RT-3 gates, focused Backend 14, full Backend 127 with one existing warning, clean Flutter analysis, full Flutter 192, exact 18-file surface review, and `git diff --check` passed. RT-3c3 is also COMPLETED / ACCEPTED after compileall, five RT-3 gates, focused Backend 21, full Backend 137 with one existing warning, clean Flutter analysis, focused Flutter 29, full Flutter 200, exact 22-file surface review, and `git diff --check`. RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED; real provider execution and real STT remain forbidden.

## v3.0.0 RT-3c3 guarded upload and Flutter scoped staging consumer gate

```powershell
.\.venv\Scripts\python.exe scripts\check_v300_rt3c3_guarded_upload_flutter_staging_consumer.py
```

This source-and-synthetic gate validates the exact accepted RT-3c3 surface: the guarded streamed `audio/wav` route, async bounded store input, path-free response models, Flutter scoped staging consumer, and tests. It creates only generated WAV bytes in a temporary directory. It does not read a real microphone artifact, contact a running Backend over the network, import Framework, create a `VoiceInputSession`, call a provider, or execute STT. Current state: `COMPLETED / ACCEPTED`; RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED under authorization `authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only`.

Expected accepted-state markers:

```text
v300_rt3c3_guarded_upload_flutter_staging_consumer_status: completed-accepted
v300_rt3c3_status: completed-accepted
v300_rt3c3_implementation: completed-accepted
v300_rt3c4_status: completed-accepted
v300_rt3c4_implementation: completed-accepted
v300_rt3c4_authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
```

RT-3c3 acceptance evidence: compileall, five RT-3 gates, focused Backend 21, full Backend 137 with one existing warning, clean Flutter analysis, focused Flutter 29, full Flutter 200, exact 22-file surface review, and `git diff --check` passed.

## RT-3c4 fake FW public-session handoff gate

```powershell
.\.venv\Scripts\python.exe `
  scripts\check_v300_rt3c4_fake_fw_public_session_handoff.py
```

The gate uses generated WAV bytes in a temporary DRC staging root and the configured FW v5.3.0 public package. It verifies explicit fake-adapter selection, public file-source/session wiring, path-free normalization, session close, single-use cleanup, and zero audio read/provider/STT execution. It does not print `FRAMEWORK_ROOT`, use a real microphone artifact, or call a provider. Status: `COMPLETED / ACCEPTED`. Acceptance passed with compileall, six RT-3 gates, focused Backend 8, full Backend 145 with one existing warning, clean Flutter analysis, full Flutter 200, exact 22-file surface review, `git diff --check`, and explicit operator approval. Parent RT-3c is COMPLETED / ACCEPTED; RT-3d remains blocked pending real provider execution.


## v3.0.0 RT-3d0 Framework real STT requirement feedback check

Detailed feedback:
`docs/v300_framework_real_stt_requirement_feedback.md`.

Status: **COMPLETED / ACCEPTED**.

FW v5.3.0 remains the released baseline. RT-3d remains
`BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED`.

Run after the six historical RT-3 gates pass on a clean baseline:

```powershell
python -m compileall -q backend scripts
python scripts/check_v300_framework_real_stt_requirement_feedback.py
git diff --check
```

This is source-only and does not select the next FW version or provider, import
Framework, read audio, open a microphone, create a provider client, or execute
STT.


## v3.0.0 RT-3d1 Framework v5.4.0 adoption inventory check

Status: **COMPLETED / ACCEPTED**.

```powershell
$env:FRAMEWORK_ROOT = "<clean FW v5.4.0 checkout>"
python -m compileall -q backend scripts
python scripts/check_v300_framework_v540_real_stt_adoption_inventory.py
git diff --check
```

The source-only gate checks the exact v5.4.0 tag/HEAD, ZIP SHA-256, public
exports, accepted safe FW gates, and seven-file DRC surface. RT-3d remains
`BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.


## v3.0.0 RT-3d2a Framework v5.4.0 executor-path correction

```powershell
$env:FRAMEWORK_ROOT = "E:\\work\\deverop\\AI-Character-Framework\\Development"
python -m compileall -q backend scripts
python scripts/check_v300_rt3d2a_framework_v540_executor_path_correction.py
git diff --check
```

The gate verifies that the Voice Input session is data-only, the OpenAI adapter's session-facing `transcribe()` is execution-free, and the public fake and real executor classes are the correct RT-3d2/RT-3d3 boundaries. It performs no DRC runtime or real-provider execution.

RT-3d2a acceptance reports
`v300_rt3d2a_executor_path_correction_status: completed-accepted` and
`v300_rt3d2b_authorization: authorized-not-started`.

## v3.0.0 RT-3d2b bounded marked-fake executor wiring

```powershell
$env:FRAMEWORK_ROOT = "<clean FW v5.4.0 checkout>"
python -m compileall -q backend scripts
python scripts/check_v300_rt3d2b_bounded_marked_fake_executor_wiring.py
python -m pytest -q backend/tests/test_framework_voice_input_openai_fake_executor.py backend/tests/test_voice_input_openai_fake_executor_api.py
python -m pytest -q backend/tests
cd app
flutter analyze
flutter test
cd ..
git diff --check
```

The dedicated gate verifies the separate bounded marked-fake runtime path,
path-free normalization, single-use cleanup, and absence of credentials, OpenAI
SDK/client creation, network execution, microphone access, and real STT.

RT-3d2b acceptance is recorded in a follow-up acceptance-only commit because
the thirteen-file implementation was already committed and pushed as
`044f978240b1abda3d28206093e25c4ce285906d`.

The accepted gate reports
`v300_rt3d2b_bounded_marked_fake_executor_status: completed-accepted`,
`v300_rt3d2b_operator_approval: accepted`, and
`v300_rt3d2c_authorization: authorized-not-started`.

## v3.0.0 RT-3d2c guarded real-executor assembly contract

```powershell
$env:FRAMEWORK_ROOT = "<clean FW v5.4.0 checkout>"
.\.venv\Scripts\python.exe -m compileall -q backend scripts
.\.venv\Scripts\python.exe scripts\check_v300_rt3d2c_guarded_real_executor_assembly_contract.py
.\.venv\Scripts\python.exe -m pytest -q backend\tests\test_framework_voice_input_openai_real_executor_assembly.py
.\.venv\Scripts\python.exe -m pytest -q backend\tests
cd app
flutter analyze
flutter test
cd ..
git diff --check
```

The dedicated gate verifies the exact nine-file RT-3d2c surface, exact FW
v5.4.0 HEAD/tag, root-public real-executor exports, pre-import opt-in ordering,
opaque private credential-object injection, and assembly-only behavior.

It rejects OpenAI SDK imports, environment credential reads, direct provider
clients, client-factory invocation, executor execution, staging/audio access,
microphone access, private paths, raw audio, provider payloads, transcripts, and
real STT claims.

The accepted gate reports
`v300_rt3d2c_guarded_real_executor_assembly_status: completed-accepted`,
`v300_rt3d2c_operator_approval: accepted`, and
`v300_rt3d3_authorization: authorized-not-started`.

RT-3d2c acceptance is recorded in a separate acceptance-only seven-file change
after implementation commit `12a9d35b161da303325097a58f3913fe0c3b5708`.

### `check_v300_rt3d3_private_real_stt_operator_boundary.py`

Validates the RT-3d3 nine-file implementation candidate against the accepted
DRC baseline and exact FW v5.4.0 tag. It checks the explicit-gate ordering,
single-use staging consume, FW root-public execution call, private transcript
repr boundary, synthetic focused tests, and documentation state.

Set `FRAMEWORK_ROOT` to the local FW v5.4.0 checkout before running. The gate
does not read credentials, import the OpenAI SDK, create a real provider client,
use the network, read operator audio, or perform real STT. RT-3d remains
`BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.

## RT-3d3 real operator execution checkpoint

```text
RT-3d3: COMPLETED / ACCEPTED
RT-3d2: COMPLETED / ACCEPTED
RT-3d: COMPLETED / ACCEPTED
FW baseline: clean v5.4.0
Transport response status: 200
Transcript nonempty: True
Expected phrase match: True
Staged artifact cleanup complete: True
Provider payload exposed: False
Private path exposed: False
Raw audio exposed: False
Transcript exposed: False
Private operator evidence committed: False
Explicit operator approval: ACCEPTED
Implementation commit: 5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c
```

The deterministic private operator run used the released FW v5.4.0 public
real-STT boundary and completed without changing the repository during
execution. Only fixed public-safe markers are synchronized here.

## v3.0.0 RT-4a streaming/cancel current behavior inventory gate

Detailed inventory:
`docs/v300_rt4_streaming_cancel_current_behavior_inventory.md`.

Run from the DRC repository root with `FRAMEWORK_ROOT` pointing to the clean
FW v5.4.0 checkout:

```powershell
$env:FRAMEWORK_ROOT = "<FW_V540_ROOT>"
python -m compileall -q backend scripts
python scripts\check_v300_rt4_streaming_cancel_current_behavior_inventory.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

The gate requires DRC HEAD and `origin/main` at the accepted RT-3 acceptance
commit, exact seven-file working-tree changes, and a clean FW v5.4.0 HEAD/tag.
It inspects only public FW exports/source and current DRC source. It does not
create a Framework session, call a provider, read credentials, open audio,
use a transcript, start a streaming transport, or request cancellation.

Expected candidate markers:

```text
v300_rt4_streaming_cancel_inventory_status: implemented-awaiting-acceptance
v300_rt4a_backend_runtime_changed: False
v300_rt4a_flutter_runtime_changed: False
v300_rt4a_streaming_transport_added: False
v300_rt4a_provider_execution: False
v300_rt4a_hard_cancel_claimed: False
v300_rt4b_authorization: blocked-pending-rt4a-acceptance
```

## v3.0.0 RT-4b Backend provider-neutral text stream gate

Detailed contract: `docs/v300_rt4_backend_stream_contract.md`.

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt4_backend_stream_contract.py
python -m pytest -q backend\tests\test_realtime_text_stream_service.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

The gate imports only DRC-owned Backend models/service and uses deterministic
fake callbacks. It verifies monotonic sequence, bounded text, cooperative cancel
state, cancel/completion race handling, stale callback rejection, and protected
non-change hashes. It does not import Framework, create a provider session, add
a route, open SSE/WebSocket transport, use credentials, process audio or a
transcript, or change Flutter.

Expected candidate markers:

```text
v300_rt4_backend_stream_status: implemented-awaiting-acceptance
v300_rt4b_backend_models_added: True
v300_rt4b_fake_only_service_added: True
v300_rt4b_monotonic_sequence_enforced: True
v300_rt4b_bounded_text_enforced: True
v300_rt4b_stale_callback_rejected: True
v300_rt4b_backend_route_added: False
v300_rt4b_framework_imported: False
v300_rt4b_provider_execution: False
v300_rt4b_hard_cancel_claimed: False
v300_rt4b_flutter_changed: False
v300_rt4c_authorization: blocked-pending-rt4b-acceptance
```


## v3.0.0 RT-4c bounded Backend SSE transport gate

Detailed contract: `docs/v300_rt4_backend_sse_transport.md`.

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt4_backend_sse_transport.py
python -m pytest -q backend\tests\test_realtime_text_stream_transport.py backend\tests\test_temporary_lifecycle_config.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

The gate verifies the exact fifteen-file surface, bounded SSE frames, separate
cooperative cancel endpoint, one-consumer ownership, active capacity, idle and
maximum-duration terminals, pending-event and event-byte limits, disconnect
cleanup, no public input echo, protected Flutter/RT-4b hashes, and public-safe
errors. Framework import and provider execution remain false.

Expected candidate markers:

```text
v300_rt4_backend_sse_status: implemented-awaiting-acceptance
v300_rt4c_sse_transport_added: True
v300_rt4c_cancel_endpoint_added: True
v300_rt4c_single_consumer_enforced: True
v300_rt4c_capacity_and_time_limits_enforced: True
v300_rt4c_disconnect_cleanup_enforced: True
v300_rt4c_event_buffer_and_byte_limits_enforced: True
v300_rt4c_input_echoed_publicly: False
v300_rt4c_framework_imported: False
v300_rt4c_provider_execution: False
v300_rt4c_hard_cancel_claimed: False
v300_rt4c_flutter_changed: False
v300_rt4d_authorization: blocked-pending-rt4c-acceptance
```

RT-4c is now COMPLETED / ACCEPTED / PUSHED at `72622cab2e73699adaff4b628cfbc4b14323a23a`. The marker above is retained as the historical output of the RT-4c candidate gate.

## v3.0.0 RT-4d FW root-public streaming adapter gate

Detailed contract:
`docs/v300_rt4_framework_public_streaming_adapter.md`.

Implementation commit: `f713f515eef723a1d51cfbe35c1dfe16e3547420`. RT-4d is COMPLETED / ACCEPTED / PUSHED after commit-scoped reconstruction, the dedicated gate, 32 focused Backend tests, full Backend/Flutter regression, exact diff review, changed-content private scan, `git diff --check`, and explicit operator approval. The script continues to print its historical candidate marker.

Run from the repository root:

```powershell
python scripts\check_v300_rt4_framework_public_streaming_adapter.py
```

This gate builds a fake root `framework` package and verifies the DRC adapter
uses only root-public text-chat APIs: `create_text_chat_session()`,
`ask_stream()`, `interrupt()`, and close/dispose. It checks fake stream chunks,
cooperative interrupt request handling, no public input echo, no Framework
internal import, no DRC provider client, no provider-level hard-cancel claim,
and no Flutter change.

Expected candidate markers:

```text
v300_rt4_framework_public_streaming_adapter_status: implemented-awaiting-acceptance
v300_rt4d_framework_root_public_api_only: True
v300_rt4d_fake_public_ask_stream_chunks: True
v300_rt4d_cooperative_interrupt_requested: True
v300_rt4d_framework_internal_import: False
v300_rt4d_drc_provider_client: False
v300_rt4d_provider_level_hard_cancel_claimed: False
v300_rt4d_flutter_changed: False
```

## v3.0.0 RT-4e Flutter stream client/controller gate

Detailed contract:
`docs/v300_rt4_flutter_stream_client_controller.md`.

Run from the repository root:

```powershell
python scripts\check_v300_rt4_flutter_stream_client_controller.py
```

This source-tree gate enforces the exact twelve-file RT-4e change surface,
checks the Flutter stream model/client/controller/test markers, verifies
HomeScreen, main.dart, backend_api_client.dart, pubspec.yaml, Backend files,
release notes, and Framework files remain unchanged, scans added content for
private or unsafe evidence, and prints fixed public-safe candidate markers.

RT-4e is now COMPLETED / ACCEPTED / PUSHED at
`1cfe6134b0d19a4d14ebcf3ec76812ce07dac261`. Acceptance covered Flutter
normalized realtime stream models, an injectable HTTP/SSE client, a
ChangeNotifier stream controller, incremental UTF-8 SSE parsing, CRLF/LF HTTP
chunk-boundary handling, same-origin events_path and cancel_path enforcement,
monotonic sequence/session/turn validation, event type/state/payload/terminal
validation, Unicode code-point chunk/output/safe-message bounds, cooperative
cancel only, hard_cancel_supported=false, failed/terminal/dispose subscription
cleanup, active-stream replacement and simultaneous start rejection, delayed
streamStarted preserving local cancelRequested, fake/in-memory normal tests, no
HomeScreen integration, no STT transcript handoff, no real
Backend/Framework/provider execution, and no TTS queue/flush/barge-in work.

Historical RT-4e implementation-candidate gate markers:

```text
v300_rt4_flutter_stream_client_controller_status: implemented-awaiting-acceptance
v300_rt4e_exact_change_surface: True
v300_rt4e_flutter_models_added: True
v300_rt4e_sse_client_added: True
v300_rt4e_controller_added: True
v300_rt4e_fake_transport_tests_added: True
v300_rt4e_home_screen_changed: False
v300_rt4e_backend_changed: False
v300_rt4e_real_network_execution: False
v300_rt4e_framework_imported: False
v300_rt4e_provider_level_hard_cancel_claimed: False
v300_rt4f_authorization: blocked-pending-rt4e-acceptance
```

These markers describe the uncommitted twelve-file RT-4e implementation
candidate that the source-tree gate validates. The gate is not expected to pass
against the later six-file acceptance documentation sync. The active accepted
state is RT-4e COMPLETED / ACCEPTED / PUSHED, and RT-4f is AUTHORIZED /
NOT_STARTED.

## v3.0.0 RT-4f1 UI streaming acceptance inventory gate

Detailed contract:
`docs/v300_rt4f_ui_streaming_acceptance_inventory.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt4f_ui_streaming_acceptance_inventory.py
python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
flutter analyze
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --stat
git diff --name-only
```

The RT-4f1 gate is source-tree-only. It verifies the exact seven-file
docs/test-only surface, preserves the RT-4e accepted commit markers, checks the
RT-4f1/RT-4f2/RT-4f3/RT-4f4 split statuses, confirms inspected Flutter and
Backend paths exist, confirms HomeScreen, RT-3 handoff, RT-4e controller,
configured Backend, UI acceptance, and protected-boundary inventory sections,
checks protected runtime/test/dependency/release surfaces are unchanged, scans
added content only for private material, and does not import Backend/FW runtime
or execute network requests.

Historical RT-4f1 implementation-candidate gate markers:

```text
v300_rt4f_ui_streaming_acceptance_inventory_status: implemented-awaiting-acceptance
v300_rt4f1_exact_change_surface: True
v300_rt4f1_docs_test_only: True
v300_rt4f1_home_screen_realtime_import: False
v300_rt4f1_transcript_forwarded_to_stream: False
v300_rt4f1_real_stt_transcript_reaches_flutter: False
v300_rt4f1_metadata_demo_transcript_nonnull: False
v300_rt4f1_real_stt_public_api_route: False
v300_rt4f1_app_transcript_stream_handoff: False
v300_rt4f1_backend_framework_streaming_default_on: False
v300_rt4f1_provider_level_hard_cancel_claimed: False
v300_rt4f2_status: not-started
v300_rt4f3_status: not-started
v300_rt4f4_status: not-started
```

The gate validates the historical uncommitted seven-file RT-4f1 candidate.
It is not expected to pass against the later six-file acceptance documentation
sync. The active accepted state is RT-4f1 COMPLETED / ACCEPTED / PUSHED, and
RT-4f2 is AUTHORIZED / NOT_STARTED.

## v3.0.0 RT-4f2 HomeScreen stream UI gate

Detailed contract:
`docs/v300_rt4f2_home_screen_stream_ui.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt4f2_home_screen_stream_ui.py
python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
flutter analyze
flutter test test\realtime_text_stream_home_screen_widget_test.dart
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

The RT-4f2 gate is source-tree-only. It verifies the exact ten-file candidate
surface, HomeScreen optional factory ownership, controller listener/dispose
lifecycle, bounded manual input, visible stream state keys, fake/in-memory
widget coverage, protected unchanged files, and added-content private scan. It
does not import Backend/FW runtime, run Flutter, execute network requests,
claim provider-level hard cancel, or start RT-4f3 transcript handoff.

Historical RT-4f2 implementation-candidate gate markers:

```text
v300_rt4f2_home_screen_stream_ui_status: implemented-awaiting-acceptance
v300_rt4f2_exact_change_surface: True
v300_rt4f2_home_screen_factory_owned_controller: True
v300_rt4f2_real_network_execution: False
v300_rt4f2_stt_handoff_added: False
v300_rt4f2_incremental_output_ui: True
v300_rt4f2_cooperative_cancel_ui: True
v300_rt4f2_hard_cancel_supported: False
v300_rt4f2_tts_auto_start: False
v300_rt4f3_status: not-started
v300_rt4f4_status: not-started
```

The dedicated gate validates the historical uncommitted ten-file RT-4f2
implementation candidate.

It is not expected to pass against the later seven-file acceptance
documentation sync.

These markers describe the historical uncommitted ten-file RT-4f2
implementation candidate and its later acceptance sync, not the active RT-4f3
or RT-4f4 state.

## v3.0.0 RT-4f3 transcript-to-stream handoff gate

Detailed contract:
`docs/v300_rt4f3_transcript_stream_handoff.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt4f3_transcript_stream_handoff.py
python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
flutter analyze
flutter test test\realtime_text_stream_transcript_handoff_test.dart
flutter test test\realtime_text_stream_transcript_handoff_home_screen_widget_test.dart
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git diff --numstat -- app/lib/screens/home_screen.dart
git status --short
```

The RT-4f3 gate is source-tree-only. It verifies the exact thirteen-file
candidate surface, provider-neutral transcript model, handoff service
ownership and exactly-one-start contract, HomeScreen optional handoff factory
and UI keys, fake/in-memory unit and widget coverage, protected unchanged
files, and added-content private scan. It does not import Backend/FW runtime,
run Flutter, execute network requests, claim provider-level hard cancel, or
start RT-4f4 configured execution.

Historical RT-4f3 implementation-candidate gate markers:

```text
v300_rt4f3_transcript_stream_handoff_status: implemented-awaiting-acceptance
v300_rt4f3_exact_change_surface: True
v300_rt4f3_provider_neutral_transcript_model: True
v300_rt4f3_exactly_one_stream_start: True
v300_rt4f3_consumed_result_ids_bounded: True
v300_rt4f3_transcript_text_retained_in_state: False
v300_rt4f3_voice_input_demo_transcript_wired: False
v300_rt4f3_real_stt_execution: False
v300_rt4f3_real_network_execution: False
v300_rt4f3_main_runtime_wiring: False
v300_rt4f3_tts_auto_start: False
v300_rt4f4_status: not-started
```

The dedicated gate validates the historical uncommitted thirteen-file RT-4f3
implementation candidate.

It is not expected to pass against the later seven-file acceptance
documentation sync.

The historical RT-4f3 milestone is COMPLETED / ACCEPTED / PUSHED. The later
RT-4f4 implementation is committed and pushed at
`9b19e379634a718df2ab3ed5eb49bb20bfe7e240`; the configured operator
acceptance is completed and accepted. Operator evidence is not committed or
pushed. The RT-4f4 milestone is COMPLETED / ACCEPTED / PUSHED, RT-4f and RT-4
are COMPLETED / ACCEPTED, and RT-5 is NOT_STARTED / NOT_AUTHORIZED.

## v3.0.0 RT-4f4 configured local stream acceptance gate

Detailed contract:
`docs/v300_rt4f4_configured_local_stream_acceptance.md`.

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt4f4_configured_local_stream_acceptance.py
python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
flutter analyze
flutter test test\configured_realtime_text_stream_runtime_test.dart
flutter test test\main_realtime_text_stream_wiring_widget_test.dart
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

The RT-4f4 gate is source-tree-only, credential-free, provider-free, and
network-free. It verifies the exact thirteen-file candidate surface,
default-off configured Flutter runtime wiring, reuse of the existing Backend
base URL define, lazy HTTP client construction, main.dart injection,
mock-safe tests, protected unchanged runtime surfaces, historical RT-4f3
markers, and added-content private scan. It does not run Flutter, import
Backend/FW runtime, execute network requests, claim provider-level hard cancel,
claim real-STT-to-stream acceptance, or start RT-5 TTS queue/flush/barge-in.

Expected historical candidate markers:

```text
v300_rt4f4_configured_local_stream_acceptance_status: implemented-awaiting-acceptance
v300_rt4f4_exact_change_surface: True
v300_rt4f4_default_enabled: False
v300_rt4f4_main_runtime_wiring: True
v300_rt4f4_reuses_backend_base_url: True
v300_rt4f4_controller_factory_lazy: True
v300_rt4f4_mock_tests_real_network_execution: False
v300_rt4f4_real_stt_source_configured: False
v300_rt4f4_real_stt_to_stream_accepted: False
v300_rt4f4_cooperative_cancel_only: True
v300_rt4f4_hard_cancel_supported: False
v300_rt4f4_tts_auto_start: False
v300_rt4f4_private_lan_scanner_self_check: True
v300_rt4f4_windows_absolute_path_scanner_self_check: True
v300_rt4f4_per_document_status_checks: True
v300_rt4f4_normalized_base_url_reused: True
v300_rt5_status: not-started
```

These markers describe the historical uncommitted thirteen-file RT-4f4
implementation candidate. They intentionally remain
`implemented-awaiting-acceptance`; the gate itself was not changed for the
later acceptance documentation sync and is not expected to pass against the
docs-only eight-file surface.

The RT-4f4 implementation gate passed before implementation commit
`9b19e379634a718df2ab3ed5eb49bb20bfe7e240`, and the implementation was pushed.
The later configured local operator acceptance also passed with public-safe
markers only: configured
local Backend/FW execution passed, manual bounded input only, real incremental
streaming accepted, one `stream_started`, 23 `stream_chunk`, one
`stream_completed`, cooperative cancel POST HTTP 200, `cancel_requested` UI
phase confirmed, cancelled terminal confirmed, `hard_cancel_supported=false`,
real-STT-to-stream not executed or accepted, provider-level hard cancel not
claimed, automatic TTS not started, and RT-5 TTS queue/flush/barge-in not
started. Operator evidence is not committed or pushed.

## v3.0.0 RT-5a TTS output-control current behavior inventory

This credential-free docs/test-only gate validates the accepted DRC baseline,
the clean released FW v5.4.0 public output-control surface, the current
one-shot voice-output and single-source local playback behavior, the absence
of DRC queue/flush/automatic-TTS runtime, and the exact seven-file RT-5a
candidate.

Run from the DRC repository root:

```powershell
$env:FRAMEWORK_ROOT = "LOCAL_CLEAN_FW_V540_CHECKOUT"
python scripts\check_v300_rt5_tts_output_control_current_behavior_inventory.py
```

The placeholder must be replaced only in the private local shell. Do not write
a private absolute Framework path into repository files.

The gate performs no network request, credential read, provider execution,
voice-output session creation, synthesis call, audio generation/playback,
microphone access, or real barge-in execution.

Historical RT-0 through RT-4 implementation, authorization, and acceptance
markers remain historical. The dedicated RT-5a gate is also a historical
implementation-candidate gate bound to the pre-implementation baseline and
exact seven-file working-tree surface.

Historical candidate output:

```text
v300_rt5_tts_output_control_inventory_status: implemented-awaiting-acceptance
v300_rt5b_authorization: blocked-pending-rt5a-acceptance
```

Do not rerun that candidate gate after implementation commit `1cf77774dca75b9875099c2b6c6c03992456d80f`.

## v3.0.0 RT-5a acceptance record

RT-5a is `COMPLETED / ACCEPTED / PUSHED` at implementation commit
`1cf77774dca75b9875099c2b6c6c03992456d80f`.

Accepted verification:

```text
compileall: passed
dedicated RT-5a candidate gate: passed before commit
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 278 passed
exact implementation surface: 7 files
git diff --check: passed
changed-content privacy scan: passed
explicit operator approval: accepted
implementation push: completed
```

RT-5 remains `CURRENT / NOT_COMPLETED`. RT-5b is
`COMPLETED / ACCEPTED / PUSHED` at implementation commit
`c48238256cb0b17c925f8063c3b636d3b4ccf533` under the separately authorized exact Flutter-only
fake/in-memory contract. At that RT-5b acceptance checkpoint, RT-5c was still
`NOT_STARTED / NOT_AUTHORIZED`; it was authorized later under a separate exact
contract and is now `COMPLETED / ACCEPTED / PUSHED` at implementation commit
`f00214cd7e75b28c041728bca6ffc3b180face80`. RT-5d remains `NOT_STARTED / NOT_AUTHORIZED`.

## v3.0.0 RT-5b app-owned voice-output queue gate

Detailed contract:
`docs/v300_rt5b_voice_output_queue_contract.md`.

Run from the repository root after applying the exact candidate:

```powershell
python -m compileall -q backend scripts
python scripts/check_v300_rt5b_voice_output_queue_contract.py
python -m pytest -q backend/tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
dart format lib/services/voice_output_queue.dart test/voice_output_queue_test.dart
flutter analyze
flutter test test/voice_output_queue_test.dart
flutter test
cd ..

Remove-Item -Recurse -Force .pytest-tmp
git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

The gate is source-tree-only, credential-free, network-free, Backend-runtime-free,
Framework-free, provider-free, and audio-free. It validates the exact nine-file
candidate, bounds, FIFO/single-active lifecycle, generation invalidation,
concurrent flush deduplication, injected local stop callback, public-state text
privacy, protected non-change paths, and added-content privacy.

Expected candidate markers:

```text
v300_rt5b_voice_output_queue_status: implemented-awaiting-acceptance
v300_rt5b_exact_change_surface: True
v300_rt5b_pending_item_limit: 8
v300_rt5b_utterance_code_point_limit: 4096
v300_rt5b_retained_code_point_limit: 16384
v300_rt5b_generation_late_result_rejection: True
v300_rt5b_concurrent_flush_stop_deduplicated: True
v300_rt5b_home_screen_changed: False
v300_rt5b_backend_changed: False
v300_rt5b_framework_imported: False
v300_rt5b_real_audio_playback: False
v300_rt5b_automatic_tts: False
v300_rt5b_provider_hard_cancel_claimed: False
v300_rt5c_authorization: blocked-pending-rt5b-acceptance
```

Do not connect the queue to HomeScreen, Backend voice output, the existing real
player, Framework, or a provider in RT-5b.

## v3.0.0 RT-5b acceptance record

RT-5b is `COMPLETED / ACCEPTED / PUSHED` at implementation commit
`c48238256cb0b17c925f8063c3b636d3b4ccf533`.

Accepted verification:

```text
dart format: passed
compileall: passed
dedicated RT-5b candidate gate: passed before commit
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter RT-5b tests: 15 passed
Flutter full tests: 293 passed
exact implementation surface: 9 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
```

The dedicated RT-5b gate remains a historical implementation-candidate gate
bound to the pre-commit baseline and exact nine-file working-tree surface. It
is not rerun for the later six-document acceptance sync.

RT-5 remains `CURRENT / NOT_COMPLETED`. RT-5c was separately reviewed,
explicitly authorized, and is now `COMPLETED / ACCEPTED / PUSHED` at
implementation commit `f00214cd7e75b28c041728bca6ffc3b180face80`. RT-5d remains
`NOT_STARTED / NOT_AUTHORIZED`. RT-5b acceptance alone did not
connect HomeScreen, Backend voice output, the existing real player, Framework,
or a provider, and does not claim real audio playback, automatic TTS,
Framework real output flush, provider hard cancel, or real barge-in.

## v3.0.0 RT-5c realtime-terminal voice-output orchestration gate

Detailed contract:
`docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md`.

Run from the repository root after applying the exact candidate:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5c_realtime_terminal_voice_output_orchestration_contract.py
python -m pytest -q backend/tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
dart format lib/services/realtime_terminal_voice_output_orchestrator.dart test/realtime_terminal_voice_output_orchestrator_test.dart
flutter analyze
flutter test test/realtime_terminal_voice_output_orchestrator_test.dart
flutter test
cd ..

Remove-Item -Recurse -Force .pytest-tmp
git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

The default gate is commit-scoped to baseline
`5fcac869f81e1070e854550f4376353e109905e5` and the exact nine-file surface.
It verifies explicit enqueue/process separation, one-item processing, bounded
completed-terminal deduplication, fake synthesis/playback delegates, bounded
opaque URI validation, operation-epoch plus queue-generation invalidation,
concurrent flush deduplication, public-state privacy, protected non-change paths,
and added-content privacy.

Expected candidate markers:

```text
v300_rt5c_realtime_terminal_voice_output_status: implemented-awaiting-review
v300_rt5c_exact_change_surface: True
v300_rt5c_explicit_enqueue_only: True
v300_rt5c_one_item_per_process_call: True
v300_rt5c_completed_terminal_dedup_limit: 32
v300_rt5c_audio_uri_code_point_limit: 2048
v300_rt5c_generation_and_epoch_late_result_rejection: True
v300_rt5c_concurrent_flush_stop_deduplicated: True
v300_rt5c_home_screen_changed: False
v300_rt5c_backend_changed: False
v300_rt5c_framework_imported: False
v300_rt5c_real_synthesis: False
v300_rt5c_real_audio_playback: False
v300_rt5c_automatic_tts: False
v300_rt5c_provider_hard_cancel_claimed: False
v300_rt5d_authorization: blocked-pending-rt5c-acceptance
```

No HomeScreen integration, Backend HTTP, existing real-player wiring, Framework
or provider execution, real synthesis, real audio playback, automatic TTS,
Framework real output flush, provider hard cancel, or speech-triggered barge-in
was added.

## v3.0.0 RT-5c acceptance record

RT-5c is `COMPLETED / ACCEPTED / PUSHED` at implementation commit
`f00214cd7e75b28c041728bca6ffc3b180face80`.

Accepted verification:

```text
dart format: passed
compileall: passed
dedicated RT-5c candidate gate: passed before commit
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter RT-5c tests: 22 passed
Flutter full tests: 315 passed
exact implementation surface: 9 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
```

The dedicated RT-5c gate remains a historical implementation-candidate gate
bound to baseline `5fcac869f81e1070e854550f4376353e109905e5` and the exact nine-file
working-tree surface. It is not rerun for the later six-document acceptance
sync.

RT-5 remains `CURRENT / NOT_COMPLETED`. RT-5d was separately reviewed,
accepted, and pushed at `eff46a3b4de771aa37a48ea9ef5959918e407200`.
RT-5e was separately reviewed and authorized and is now
`IMPLEMENTED / AWAITING_REVIEW`.

## v3.0.0 RT-5d HomeScreen manual voice-output controls gate

Detailed contract:
`docs/v300_rt5d_home_screen_voice_output_controls.md`.

Historical pre-commit candidate command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5d_home_screen_voice_output_controls.py

python -m pytest -q backend\tests `
  --basetemp .pytest-tmp `
  -p no:cacheprovider

Push-Location app
flutter analyze
flutter test test\realtime_terminal_voice_output_home_screen_widget_test.dart
flutter test
Pop-Location

git -c core.whitespace=cr-at-eol diff --check
git status --short
```

RT-5d is `COMPLETED / ACCEPTED / PUSHED` at implementation commit
`eff46a3b4de771aa37a48ea9ef5959918e407200`. Acceptance recorded compileall, the dedicated
candidate gate, Backend 192 passed with one existing warning, Flutter analyze,
16 focused Flutter tests, 331 full Flutter tests, exact ten-file review,
changed-content privacy review, `git diff --check`, explicit operator approval,
implementation commit, post-commit verification, and push. The final
HomeScreen diff was insertion-only `+396/-0`.

The dedicated gate is source-tree-only, credential-free, network-free,
Backend-runtime-free, Framework-free, provider-free, and platform-audio-free.
It is bound to the pre-commit baseline and exact ten-file candidate, so it
remains historical and is not rerun for this six-document acceptance sync.

No `main.dart`, Backend, existing RT-5c orchestrator, queue, existing real
player, dependency, permission, version, release record, or Framework file was
changed. No Backend HTTP, Framework/provider execution, real synthesis, real
audio playback, automatic TTS, Framework real output flush, provider hard
cancel, or speech-triggered barge-in was added.

RT-5e was separately reviewed, implemented, committed, pushed, and operator-accepted at `ef5f96337b5f601277a9bcc38b9e6fedc520b0a6`. Private operator artifacts and logs were cleaned and are not committed.

## v3.0.0 RT-5e configured local voice-output candidate gate

Detailed contract and public-safe acceptance record:
`docs/v300_rt5e_configured_local_voice_output_acceptance.md`.

Historical implementation command from the accepted RT-5d baseline:

```powershell
python -m compileall -q backend scripts
if ($LASTEXITCODE -ne 0) { throw "compileall failed: $LASTEXITCODE" }

python scripts\check_v300_rt5e_configured_local_voice_output_acceptance.py
if ($LASTEXITCODE -ne 0) { throw "RT-5e gate failed: $LASTEXITCODE" }

python scripts\smoke_v200_fw_voice_output_boundary_for_drc.py
if ($LASTEXITCODE -ne 0) { throw "FW voice-output smoke failed: $LASTEXITCODE" }

python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed: $LASTEXITCODE" }

Push-Location app
try {
    flutter analyze
    if ($LASTEXITCODE -ne 0) { throw "Flutter analyze failed: $LASTEXITCODE" }

    flutter test `
        test\configured_realtime_terminal_voice_output_runtime_test.dart `
        test\main_realtime_terminal_voice_output_wiring_widget_test.dart `
        test\realtime_terminal_voice_output_home_screen_widget_test.dart `
        test\realtime_terminal_voice_output_orchestrator_test.dart `
        test\voice_output_queue_test.dart `
        test\voice_output_audio_player_test.dart `
        test\audioplayers_voice_output_audio_engine_test.dart
    if ($LASTEXITCODE -ne 0) { throw "Focused Flutter tests failed: $LASTEXITCODE" }

    flutter test
    if ($LASTEXITCODE -ne 0) { throw "Flutter tests failed: $LASTEXITCODE" }
}
finally {
    Pop-Location
}

git -c core.whitespace=cr-at-eol diff --check
if ($LASTEXITCODE -ne 0) { throw "git diff --check failed: $LASTEXITCODE" }

git status --short
if ($LASTEXITCODE -ne 0) { throw "git status failed: $LASTEXITCODE" }
```

The gate is bound to baseline `ead613d27cd32c625b1b0a07eef96387027d70d5`
and the exact thirteen-file implementation candidate. It is credential-free,
network-free, provider-free, and platform-audio-free and remains a historical
pre-commit gate. It is not rerun for the later six-document acceptance sync.

RT-5e implementation commit `ef5f96337b5f601277a9bcc38b9e6fedc520b0a6` passed the dedicated gate, FW
root-public boundary smoke, Backend 192 tests with one existing warning,
Flutter analyze, 82 focused Flutter tests, 343 full Flutter tests, exact
thirteen-file review, HomeScreen semantic-only `+6/-6`, privacy review, and
`git diff --check`, then was explicitly approved and pushed.

Configured local operator acceptance later passed with explicit opt-in,
explicit enqueue, real FW root-public synthesis, natural audible playback, and
an explicit flush during active playback. Flush ended with `completed`,
cleared pending `0`, local stop requested/succeeded `true`, phase `idle`,
pending `0`, and active `no`. Cleanup stopped both runtimes, restored FW real
provider gates to disabled, removed three operator artifact files and private
logs/backups, and left both working trees clean.

RT-5e is `COMPLETED / ACCEPTED / PUSHED`. Automatic TTS, automatic queue
drain, Backend HTTP cancel, provider hard cancel, FW real flush,
speech-triggered barge-in, and real-STT-to-TTS remain unclaimed. RT-5f0 is
`COMPLETED / ACCEPTED / PUSHED` at
`348669884e872475aaa4242a5960a6de6fb7e10b`; RT-5f1 remains
`NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED`.


## RT-5f1 app-visible provider-neutral real-STT source check

RT-5f1 is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`daca3a68672eb3106e861278ebb65612380140ed`.

Historical pre-commit verification commands:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f1_app_visible_real_stt_contract.py
python -m pytest -q backend/tests/test_framework_voice_input_app_transcript.py
python -m pytest -q backend/tests/test_voice_input_real_transcript_api.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/backend_provider_neutral_transcript_provider_test.dart
flutter test
cd ..

git diff --check
```

Acceptance recorded 12 focused Backend tests, 204 full Backend tests, Flutter
analyze, 12 focused Flutter tests, 355 full Flutter tests, exact seventeen-file
review, privacy review, explicit approval, push, and clean DRC/FW working
trees. Checks remained credential-free, provider-free, network-free,
microphone-free, playback-free, and real-transcript-free.

The dedicated gate remains a historical pre-commit gate bound to the
`e4ecd46487b43e20b359ce350fc90b5e0ac36d95` baseline and exact seventeen-file
candidate. It is not rerun by the docs-only acceptance sync.

```text
RT-5f2: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

## v3.0.0 RT-5f0 real-input and soft-barge-in readiness gate

Detailed accepted contract:
`docs/v300_rt5f_readiness_and_exact_split.md`.

The dedicated gate is retained as the historical pre-commit verifier for the
exact seven-file RT-5f0 implementation candidate. It is bound to DRC baseline
`6272f613906317de3fecd899d4389ce0f13155e8`, clean FW v5.4.0
`d313eb6acb643103fe25988720ebee5976a04f78`, and the pre-commit candidate
state. Do not rerun it against the accepted docs-only state sync.

Historical command sequence:

```powershell
$env:FRAMEWORK_ROOT = "<clean FW v5.4.0 checkout>"
python -m compileall -q backend scripts
python scripts\check_v300_rt5f_readiness_and_exact_split.py
python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider

Push-Location app
try {
    flutter analyze
    flutter test
}
finally {
    Pop-Location
}

Remove-Item -Recurse -Force .pytest-tmp -ErrorAction SilentlyContinue
git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

Historical expected markers:

```text
v300_rt5f0_readiness_status: implemented-awaiting-review
v300_rt5f0_exact_change_surface: True
v300_rt5f0_backend_runtime_changed: False
v300_rt5f0_flutter_runtime_changed: False
v300_rt5f0_existing_tests_changed: False
v300_rt5f0_app_visible_real_stt_source_exists: False
v300_rt5f0_transcript_handoff_boundary_exists: True
v300_rt5f0_normal_main_microphone_or_stt_wiring_exists: False
v300_rt5f0_speech_activity_source_exists: False
v300_rt5f0_local_soft_barge_in_primitives_exist: True
v300_rt5f0_fw_real_runtime_enabled: False
v300_rt5f0_fw_tts_queue_flush_supported: False
v300_rt5f0_fw_hard_cancel_supported: False
v300_rt5f0_final_claim: drc-local-soft-barge-in-only
v300_rt5f1_authorization: blocked-pending-rt5f0-acceptance
```

Acceptance result:

```text
implementation commit: 348669884e872475aaa4242a5960a6de6fb7e10b
compileall: passed
dedicated pre-commit gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 343 passed
exact implementation surface: 7 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
post-push working tree: clean
RT-5f1: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

RT-5f0 does not authorize RT-5f1 implementation, commit, or push. A separate
exact contract review and explicit authorization remain required.

## RT-5f2 accepted fake-only integrated voice-turn gate

```text
implementation commit: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6
corrective commit: b7bd436196210f27782b64c1a094aa65d6893915
acceptance-sync baseline: b7bd436196210f27782b64c1a094aa65d6893915
acceptance-sync surface: exact seven files
```

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test test/integrated_voice_turn_coordinator_test.dart
flutter test
cd ..

git diff --check
```

The gate verifies both committed implementation surfaces, queue exclusivity,
processed-item identity, operation-epoch invalidation, fake-only/privacy
boundaries, and the accepted progress markers.

```text
expected Backend full: 204 passed, 1 existing warning
expected focused Flutter: 26 passed
expected Flutter full: 381 passed
RT-5f2 COMPLETED / ACCEPTED / PUSHED
RT-5f3 COMPLETED / ACCEPTED / PUSHED
```

This acceptance sync changes documentation and this gate only. After the sync
commit, the gate is historical and is not rerun against the new HEAD.


## RT-5f3 default-off HomeScreen and production speech-activity gate

Accepted implementation:

```text
RT-5f3: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 888814d09fad75039733a4a94719454e0a69db63
implementation commit: 75504424c37222234ea8a4314d01ce386ff92d23
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact implementation surface: 20 files
exact acceptance-sync surface: 7 files
focused Flutter: 53 passed
Flutter full: 408 passed
real operator acceptance: NOT_EXECUTED / NOT_CLAIMED
RT-5f4: COMPLETED / ACCEPTED / PUSHED
```

Run from the DRC repository root while HEAD remains the pushed implementation
commit and the exact seven-file acceptance sync is uncommitted:

```powershell
python scripts\check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py
```

The acceptance-sync gate verifies the implementation parent and exact
commit-scoped twenty-file surface, the exact seven-file docs/test-only worktree
surface, default-off runtime gates, dedicated stream/TTS ownership,
capture-phase disarm, bounded production detector defaults, one event per
arming generation, metadata-only HomeScreen markers, neutral coordinator
messages, focused test coverage, unchanged dependency files, accepted
verification records, and the RT-5f4 non-authorization boundary.

It accesses no credential, microphone/audio, network, provider, Framework
runtime, synthesis, playback, or operator evidence. This acceptance sync
changes documentation and this gate only. After the acceptance-sync commit,
the gate is historical and is not rerun against the new HEAD.

Detailed accepted contract:
`docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md`.


## RT-5f4 configured local end-to-end acceptance-sync gate

Accepted implementation and operator checkpoint:

```text
RT-5f4: COMPLETED / ACCEPTED / PUSHED
checkpoint baseline: ec6844c63b89803041e0b4e064d45c924e2d0438
checkpoint commit: c84617e7ce07ecb1ca1605956eda7435b797c2fe
corrective commit / expected HEAD: bf17538f8b33aa504671289edda8f55c511fe77d
RT-5f3 implementation: 75504424c37222234ea8a4314d01ce386ff92d23
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact checkpoint surface: 7 files
exact corrective surface: 5 files
exact acceptance-sync surface: 7 files
private operator execution: COMPLETED / ACCEPTED
operator acceptance: ACCEPTED
Control A: PASS / ACCEPTED
Control B: PASS / ACCEPTED
Control C: PASS / ACCEPTED
Control D: PASS / ACCEPTED
repeated Stop Capture corrective: REAL-DEVICE PASS
playback-time speech detection corrective: REAL-DEVICE PASS
Backend full: 204 passed, 1 existing warning
Flutter analyze: No issues found
Flutter full: 411 passed
RT-5f: COMPLETED / ACCEPTED
RT-5: COMPLETED / ACCEPTED
RT-6: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
acceptance-sync commit/push: NOT_AUTHORIZED
```

Run from the DRC repository root while HEAD remains the pushed corrective
commit and the exact seven-file acceptance sync is uncommitted:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt5f4_configured_local_end_to_end_acceptance.py
python -m pytest -q backend/tests --basetemp .pytest-tmp -p no:cacheprovider

cd app
flutter analyze
flutter test
cd ..

Remove-Item -Recurse -Force .pytest-tmp
git -c core.whitespace=cr-at-eol diff --check
git diff --name-only
git diff --stat
git status --short
```

The acceptance-sync gate verifies the checkpoint/corrective ancestry and exact
seven-file/five-file committed surfaces, the exact seven-file docs/static-gate
worktree surface, the two corrective runtime contracts and focused regression
markers, default-off prerequisites, accepted public-safe operator results,
parent completion, RT-6 non-authorization, explicit non-claims, and privacy
boundaries.

It reads no private env, credential, microphone/audio, network, provider,
synthesis, playback, private path, LAN address, screenshot, raw log, or
operator evidence. This acceptance sync changes documentation and this gate
only. After the acceptance-sync commit, the gate is historical and is not
rerun against the new HEAD.

Detailed accepted contract:
`docs/v300_rt5f4_configured_local_end_to_end_acceptance.md`.


## v3.0.0 RT-6a character-motion mapping acceptance-sync gate

RT-6a is **COMPLETED / ACCEPTED / PUSHED** at `cbcb218aa54d286da7515a01e899121b22d8f3fc`. This historical
acceptance-sync gate verifies the exact seven-file implementation commit and
the current seven-file documentation/static-gate synchronization candidate
against clean DRC and FW checkouts.

Set `FRAMEWORK_ROOT` when the FW checkout cannot be discovered from the normal
workspace layout, then run from the DRC repository root before the acceptance
sync is committed:

```powershell
$env:FRAMEWORK_ROOT = "<clean AI Character Framework v5.4.0 checkout>"
python -m compileall -q backend scripts
python scripts\check_v300_rt6a_character_motion_mapping_readiness.py
python -m pytest -q

cd app
flutter analyze
flutter test
cd ..

git diff --check
git status --short
```

Expected markers include:

```text
v300_rt6a_status: completed-accepted-pushed
v300_rt6a_exact_acceptance_sync_surface: True
v300_rt6a_acceptance_sync_file_count: 7
v300_rt6a_implementation_commit: cbcb218aa54d286da7515a01e899121b22d8f3fc
v300_rt6a_implementation_surface: 7
v300_rt6a_backend_full_passed: 204
v300_rt6a_backend_warning_count: 3
v300_rt6a_flutter_analyze_passed: True
v300_rt6a_flutter_full_passed: 411
v300_rt6_status: current-not-completed
v300_rt6b_status: ready-for-exact-contract-review-not-authorized
v300_rt6b_implementation_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6a_acceptance_sync_commit_push_authorized: False
```

The gate also rechecks the metadata-only DRC motion-demo boundary, static
Flutter character presentation, FW root-public mock-safe motion contract,
absence of real Live2D/VTS implementation, exact implementation history,
changed-content privacy, and no runtime/dependency/FW change in the acceptance
sync.

The `--snapshot` option skips DRC/FW commit/tag/worktree checks for extracted
snapshot reconstruction. After the acceptance-sync commit is created, this
gate is historical and is not rerun against the new HEAD.

Detailed accepted contract:
`docs/v300_rt6a_character_motion_mapping_readiness.md`.


## v3.0.0 RT-6b provider-neutral motion mapping acceptance gate

RT-6b is **COMPLETED / ACCEPTED / PUSHED** at `17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594`. The historical gate now
validates the exact seven-file acceptance-state synchronization against that
implementation commit while rechecking the accepted pure mapping behavior.

Run before the acceptance-sync commit from the DRC root:

```powershell
$env:FRAMEWORK_ROOT = "<clean AI Character Framework v5.4.0 checkout>"
python -m compileall -q backend scripts
python scripts\check_v300_rt6b_provider_neutral_motion_mapping.py
python -m pytest -q backend\tests\test_character_motion_mapper.py
python -m pytest -q

cd app
flutter analyze
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --stat
git diff --name-only
```

Expected markers:

```text
v300_rt6b_status: completed-accepted-pushed
v300_rt6b_exact_acceptance_sync_surface: True
v300_rt6b_acceptance_sync_file_count: 7
v300_rt6b_implementation_commit: 17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594
v300_rt6b_implementation_surface: 10
v300_rt6b_focused_backend_passed: 37
v300_rt6b_backend_full_passed: 241
v300_rt6b_flutter_analyze_passed: True
v300_rt6b_flutter_full_passed: 411
v300_rt6b_mapping_deterministic: True
v300_rt6b_max_commands_per_plan: 3
v300_rt6b_runtime_changed_by_acceptance_sync: False
v300_rt6_status: current-not-completed
v300_rt6c_status: ready-for-exact-contract-review-not-authorized
v300_rt6c_implementation_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6b_acceptance_sync_commit_push_authorized: False
```

Normal mode requires DRC HEAD/origin main `17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594` and clean FW v5.4.0
`d313eb6acb643103fe25988720ebee5976a04f78`. `--snapshot` skips commit/tag/FW-clean checks for extracted candidate
reconstruction. After the acceptance-sync commit is created, this gate is
historical and is not rerun against the new HEAD.

Detailed accepted contract: `docs/v300_rt6b_provider_neutral_motion_mapping.md`.

## v3.0.0 RT-6c Framework mock motion-session adapter acceptance gate

RT-6c is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`f929e8faa65a817f1ba4fed82b729438b73dbfab`. The historical gate now validates the exact seven-file
acceptance-state synchronization while rechecking the accepted root-public
mock adapter contract.

Framework record:

```text
FW baseline version: 5.4.0
FW canonical reference commit: d313eb6acb643103fe25988720ebee5976a04f78
FW local source mode: external-vendored-snapshot
FW vendor Git identity required: false
```

Run before the acceptance-sync commit from the DRC root:

```powershell
$env:FRAMEWORK_ROOT = "<DRC-root>\vendor\ai-character-framework-5.4.0"
python -m compileall -q backend scripts
python scripts\check_v300_rt6c_framework_mock_motion_session_adapter.py `
    --framework-root $env:FRAMEWORK_ROOT
python -m pytest -q backend\tests\test_framework_mock_motion_session_adapter.py
python -m pytest -q

cd app
flutter analyze
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --stat
git diff --name-only
```

Expected markers:

```text
v300_rt6c_status: completed-accepted-pushed
v300_rt6c_exact_acceptance_sync_surface: True
v300_rt6c_acceptance_sync_file_count: 7
v300_rt6c_implementation_commit: f929e8faa65a817f1ba4fed82b729438b73dbfab
v300_rt6c_implementation_surface: 10
v300_rt6c_backend_runtime_file_count: 2
v300_rt6c_backend_test_file_count: 1
v300_rt6c_focused_backend_passed: 38
v300_rt6c_backend_full_passed: 279
v300_rt6c_backend_warning_count: 3
v300_rt6c_flutter_analyze_passed: True
v300_rt6c_flutter_full_passed: 411
v300_rt6c_framework_version: 5.4.0
v300_rt6c_framework_reference_commit: d313eb6acb643103fe25988720ebee5976a04f78
v300_rt6c_framework_source_mode: external-vendored-snapshot
v300_rt6c_framework_git_identity_required: False
v300_rt6c_framework_root_public_contract_passed: True
v300_rt6c_framework_mock_smoke_passed: True
v300_rt6c_real_fw_mock_smoke_passed: True
v300_rt6c_runtime_changed_by_acceptance_sync: False
v300_rt6c_backend_runtime_changed_by_acceptance_sync: False
v300_rt6c_backend_tests_changed_by_acceptance_sync: False
v300_rt6c_api_routes_changed: False
v300_rt6c_config_changed: False
v300_rt6c_flutter_changed: False
v300_rt6c_framework_changed: False
v300_rt6c_dependencies_changed: False
v300_rt6c_network_execution: False
v300_rt6c_provider_execution: False
v300_rt6c_vts_connection_used: False
v300_rt6c_live2d_runtime_loaded: False
v300_rt6_status: current-not-completed
v300_rt6d_status: ready-for-exact-contract-review-not-authorized
v300_rt6d_implementation_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6c_acceptance_sync_commit_push_authorized: False
```

Normal mode requires DRC HEAD/origin main `f929e8faa65a817f1ba4fed82b729438b73dbfab`. The configured vendor copy
remains outside DRC Git history, so the gate does not require vendor Git HEAD
or clean status. It verifies the declared FW v5.4.0 root-public motion symbols
and executes the representative local mock plan. `--snapshot` uses an isolated
synthetic root-public mock for artifact reconstruction. After the acceptance
sync is committed, this gate becomes historical and is not rerun against the
new HEAD.

Detailed accepted contract:
`docs/v300_rt6c_framework_mock_motion_session_adapter.md`.


## v3.0.0 RT-6d Flutter motion presentation acceptance gate

RT-6d is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`0f220b792feb7ebb82c5871a794731aa1327439a`. This historical gate validates the exact seven-file
acceptance-state synchronization against that implementation while preserving
the accepted Flutter runtime and focused tests unchanged.

Run before the acceptance-sync commit from repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt6d_flutter_motion_presentation.py
python -m pytest -q

cd app
dart format --output=none --set-exit-if-changed `
    lib\models\character_motion_presentation.dart `
    lib\services\character_motion_presentation_client.dart `
    lib\services\character_motion_presentation_controller.dart `
    test\character_motion_presentation_client_test.dart `
    test\character_motion_presentation_controller_test.dart
flutter analyze
flutter test `
    test\character_motion_presentation_client_test.dart `
    test\character_motion_presentation_controller_test.dart
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
```

Artifact-generation snapshot mode:

```powershell
python scripts\check_v300_rt6d_flutter_motion_presentation.py --snapshot
```

Expected historical markers include:

```text
v300_rt6d_status: completed-accepted-pushed
v300_rt6d_exact_acceptance_sync_surface: True
v300_rt6d_acceptance_sync_file_count: 7
v300_rt6d_implementation_commit: 0f220b792feb7ebb82c5871a794731aa1327439a
v300_rt6d_implementation_surface: 12
v300_rt6d_flutter_runtime_file_count: 3
v300_rt6d_flutter_test_file_count: 2
v300_rt6d_focused_flutter_passed: 41
v300_rt6d_flutter_full_passed: 452
v300_rt6d_backend_full_passed: 279
v300_rt6d_backend_warning_count: 3
v300_rt6d_dart_format_passed: True
v300_rt6d_flutter_analyze_passed: True
v300_rt6d_runtime_changed_by_acceptance_sync: False
v300_rt6d_home_screen_changed: False
v300_rt6d_main_changed: False
v300_rt6d_backend_changed: False
v300_rt6d_dependencies_changed: False
v300_rt6d_framework_execution: False
v300_rt6e_status: ready-for-exact-contract-review-not-authorized
v300_rt6e_implementation_authorized: False
v300_rt6f_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6d_acceptance_sync_commit_push_authorized: False
```

The gate performs no HTTP, Framework, provider, network, VTS, Live2D, audio,
STT, LLM, TTS, or credential execution. It checks the accepted Dart source and
tests statically; the recorded Flutter/Backend counts are separately rerun by
the validation commands above. After the acceptance-sync commit is created,
this gate becomes historical and is not rerun against the new HEAD.

Detailed accepted contract:
`docs/v300_rt6d_flutter_motion_presentation.md`.

## v3.0.0 RT-6e HomeScreen character-motion acceptance gate

RT-6e is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`13343017738d0bb5fe23583467856233d62196fb`. This historical gate validates the exact seven-file
acceptance-state synchronization while preserving the accepted HomeScreen,
panel, and focused test unchanged.

Run before the acceptance-sync commit from repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt6e_home_screen_character_motion_wiring.py
python -m pytest -q

cd app
dart format --output=none --set-exit-if-changed `
    lib\screens\home_screen.dart `
    lib\widgets\character_motion_presentation_panel.dart `
    test\character_motion_home_screen_test.dart
flutter analyze
flutter test test\character_motion_home_screen_test.dart
flutter test
cd ..

git -c core.whitespace=cr-at-eol diff --check
```

Artifact-generation snapshot mode:

```powershell
python scripts\check_v300_rt6e_home_screen_character_motion_wiring.py --snapshot
```

Expected historical markers include:

```text
v300_rt6e_status: completed-accepted-pushed
v300_rt6e_exact_acceptance_sync_surface: True
v300_rt6e_acceptance_sync_file_count: 7
v300_rt6e_implementation_commit: 13343017738d0bb5fe23583467856233d62196fb
v300_rt6e_implementation_surface: 10
v300_rt6e_focused_flutter_passed: 16
v300_rt6e_flutter_full_passed: 468
v300_rt6e_backend_full_passed: 279
v300_rt6e_runtime_changed_by_acceptance_sync: False
v300_rt6e_flutter_runtime_changed_by_acceptance_sync: False
v300_rt6e_flutter_tests_changed_by_acceptance_sync: False
v300_rt6e_framework_execution: False
v300_rt6f_status: ready-for-exact-contract-review-not-authorized
v300_rt6f_implementation_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6e_acceptance_sync_commit_push_authorized: False
```

The gate performs no HTTP, Framework, provider, network, VTS, Live2D, audio,
STT, LLM, TTS, or credential execution. It checks the accepted Flutter source
and test statically; recorded Flutter/Backend counts are rerun separately by
the validation commands. After the acceptance-sync commit, this gate becomes
historical and is not rerun against the new HEAD.

Detailed accepted contract:
`docs/v300_rt6e_home_screen_character_motion_wiring.md`.

## v3.0.0 RT-6f configured local mock-motion acceptance-sync gate

RT-6f is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`fcdce38b9260604ea7c435c6de44fc129dc613f6` against baseline `e1d4f63d71c2de485b05fbfc5dad6811b81b31fc`. The implementation surface is exact
nineteen files. This acceptance synchronization changes only seven
documentation/static-gate files and does not change runtime or tests.

Run from the clean implementation commit before committing the acceptance sync:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt6f_configured_local_mock_motion_presentation_acceptance.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
```

Handoff snapshot mode, used only when the implementation Git object is absent:

```powershell
python scripts\check_v300_rt6f_configured_local_mock_motion_presentation_acceptance.py --snapshot
```

The acceptance-sync gate requires `HEAD` and `origin/main` to equal
`fcdce38b9260604ea7c435c6de44fc129dc613f6` in normal mode and requires the working tree change surface to be the
exact seven documentation/static-gate files. It rechecks the accepted
Backend/Flutter implementation markers without executing HTTP, Framework,
provider, VTS, Live2D, audio, STT, LLM, TTS, credential, or token work.

Recorded accepted results:

```text
focused Backend: 10 passed
Backend full: 289 passed, 1 dependency deprecation warning
Flutter analyze: passed
focused Flutter: 15 passed
Flutter full: 483 passed
configured local Controls A-E: passed
implementation push: completed
post-push DRC/FW working trees: clean
RT-6: COMPLETED / ACCEPTED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
acceptance-sync commit/push: NOT_AUTHORIZED
```

Detailed accepted contract:
`docs/v300_rt6f_configured_local_mock_motion_presentation_acceptance.md`.

## v3.0.0 RT-7a real-motion adapter readiness acceptance-sync gate

RT-7a is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`efb139b2c0b6c7cc66912a229bd674b36df82dd7` against DRC baseline `c3c78316fd2bcd4f9939dcaadc32134a704374cf`. The implementation and this
acceptance-state synchronization each use the exact same seven
documentation/static-gate files.

Run from the clean implementation commit before committing the acceptance sync:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7a_real_motion_adapter_readiness.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
```

Artifact-generation snapshot mode:

```powershell
python scripts\check_v300_rt7a_real_motion_adapter_readiness.py --snapshot
```

Normal mode requires `HEAD` and `origin/main` to equal
`efb139b2c0b6c7cc66912a229bd674b36df82dd7`, requires a clean Framework v5.4.0 checkout at `d313eb6acb643103fe25988720ebee5976a04f78`, and requires
an exact seven-file DRC acceptance-sync surface.

Expected acceptance-state markers:

```text
v300_rt7a_status: completed-accepted-pushed
v300_rt7_status: current-not-completed-blocked-framework-real-motion-adapter-release-required
v300_rt7a_exact_acceptance_sync_surface: True
v300_rt7a_acceptance_sync_file_count: 7
v300_rt7a_implementation_baseline: c3c78316fd2bcd4f9939dcaadc32134a704374cf
v300_rt7a_implementation_commit: efb139b2c0b6c7cc66912a229bd674b36df82dd7
v300_rt7a_backend_full_passed: 289
v300_rt7a_backend_warning_count: 1
v300_rt7a_flutter_analyze_passed: True
v300_rt7a_flutter_full_passed: 483
v300_rt7a_rt6_runtime_changed_by_acceptance_sync: False
v300_rt7a_existing_tests_changed_by_acceptance_sync: False
v300_rt7a_framework_source_changed: False
v300_rt7a_vts_connection_opened: False
v300_rt7a_token_read: False
v300_rt7a_private_model_loaded: False
v300_rt7a_real_motion_executed: False
v300_rt7a_drc_provider_bypass_allowed: False
v300_rt7a_framework_update_required: True
v300_rt7a_implementation_push_completed: True
v300_rt7a_acceptance_sync_commit_push_authorized: False
```

The gate is static and credential-free. It verifies the frozen accepted RT-6
mock path and the released Framework root-public mock-safe boundary without
opening a VTS WebSocket, reading a token, loading a private model, executing
Live2D, performing motion dispatch, or changing DRC/FW runtime.

Detailed accepted contract:
`docs/v300_rt7a_real_motion_adapter_readiness.md`.

## v3.0.0 RT-7b vendored Framework v5.5.0 readiness gate

Detailed contract:
`docs/v300_rt7b_vendored_fw_v550_readiness.md`.

The gate imports Framework only from:

```text
vendor/ai-character-framework-5.5.0
```

It does not discover or import a Framework development checkout. Candidate mode
checks the exact eight-file change surface, vendor privacy and keyset, required
release files, root-public origin/API/exports, mock compatibility, and the
closed provider guard without `pyvts`, network, or real motion.

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py
python -m pytest -q backend/tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py
git diff --check
```

Strict release-artifact provenance requires explicit operator-local paths:

```powershell
python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py `
  --require-release-artifact `
  --release-zip <local-fixed-v5.5.0-zip> `
  --release-sidecar <local-fixed-v5.5.0-sha256-sidecar>
```

Strict mode compares the sidecar digest, ZIP integrity and duplicate state,
exact release-eligible member set, and every ZIP member byte with the vendor
copy. The ZIP, sidecar, private configuration, and output evidence remain
outside Git.

RT-7c runtime composition, private VTube Studio configuration, provider
execution, commit, and push remain separately unauthorized.

<!-- RT-7b-VENDORED-FW-v5.5.0:BEGIN -->
## v3.0.0 RT-7b accepted vendored Framework v5.5.0 readiness gate

Detailed accepted contract:
`docs/v300_rt7b_vendored_fw_v550_readiness.md`.

Run from the DRC repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py
git -c core.whitespace=cr-at-eol diff --check
```

Accepted implementation:

```text
RT-7b: COMPLETED / ACCEPTED / PUSHED
implementation commit: c766610ce66a539efaabf4e4026a7c12ad2887c9
Framework release: v5.5.0
Framework local source: vendor/ai-character-framework-5.5.0
official ZIP SHA-256: d6603003ea33abd5d543d85d4437f71e00571a86a9ed06a902506e6be3a9b5fe
official ZIP files: 328
Backend full: 289 passed
Flutter analyze: PASS
Flutter full: 483 passed
```

The normal acceptance-sync gate does not download or rebuild a release
artifact. It verifies the accepted fixed-vendor/root-public boundary and records
the completed strict provenance evidence. Optional local strict re-verification
remains available:

```powershell
python scripts\check_v300_rt7b_vendored_fw_v550_readiness.py `
  --require-release-artifact `
  --release-zip "<official ZIP path>" `
  --release-sidecar "<official sidecar path>"
```

The gate imports Framework only from
`vendor/ai-character-framework-5.5.0`. It does not read private configuration,
import `pyvts`, connect to VTube Studio, or execute real motion. RT-7c remains
not authorized.
<!-- RT-7b-VENDORED-FW-v5.5.0:END -->

<!-- RT-7c-GUARDED-VENDORED-FW-v5.5.0-VTS:BEGIN -->
## v3.0.0 RT-7c guarded vendored FW v5.5.0 VTS adapter acceptance-sync gate

RT-7c is **COMPLETED / ACCEPTED / PUSHED** through implementation commit
`4a2374854801791caefdf0be8cd246e5a2e9278e` and strict-boolean corrective commit
`484ba17245d24a98407907984b28995b247581fa` against baseline
`35582f06ca037401b2cef8d97cfc5fc26cd40654`.

```text
implementation surface: exact 11 files
corrective surface: exact 4 files
acceptance-sync surface: exact 7 documentation/static-gate files
focused Backend accepted: 31 passed
Backend full accepted: 320 passed, 1 existing warning
Flutter analyze accepted: PASS
Flutter full accepted: 483 passed
RT-7d exact contract review: READY
RT-7d implementation: NOT_AUTHORIZED
RT-7e: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
acceptance-sync commit / push: NOT_AUTHORIZED
```

Run the acceptance-sync gate from the DRC repository root while the exact seven
files are modified against corrective commit `484ba17245d24a98407907984b28995b247581fa`:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

The gate verifies the historical exact 11-file implementation and exact 4-file
corrective surfaces, the current exact 7-file acceptance-sync surface, fixed
vendor provenance, root-public-only loading, API version 5.5.0, exact dependency
pins, intent vocabulary, strict literal-boolean safety, closed guards, and an
incomplete-config preflight.

The gate is credential-free and network-free. It reads no private VTS
configuration, imports no `pyvts`, opens no WebSocket, attempts no provider or
network execution, and executes no real motion. The full Backend and Flutter
regression results above are accepted historical evidence and are not launched
automatically by this docs/static-gate sync.

Detailed accepted contract:
`docs/v300_rt7c_guarded_vendored_fw_v550_vts_session_adapter.md`.
<!-- RT-7c-GUARDED-VENDORED-FW-v5.5.0-VTS:END -->


<!-- RT-7d-DEFAULT-OFF-CONFIGURED-VTS:BEGIN -->
## RT-7d default-off configured VTS manual wiring acceptance

RT-7d is **COMPLETED / ACCEPTED / PUSHED** at implementation commit
`37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2` against baseline
`2a5e3b035bcfdd273a7d056d59af01235e2459f5` under the exact 28-file contract.

Accepted verification:

```text
compileall: PASS
dedicated RT-7d gate: PASS before and after regressions
focused Backend: 16 passed, 1 existing dependency warning
Backend full: 336 passed, 1 existing dependency warning
Dart focused format: PASS
Flutter analyze: No issues found
focused Flutter: 16 passed
Flutter full: 499 passed
exact implementation surface: 28 files
CRLF-aware git diff --check: PASS
provider execution attempted: false
network execution attempted: false
real motion executed: false
implementation commit / push: COMPLETED
post-push HEAD / origin/main: 37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2
post-push working tree: clean
```

The accepted wiring keeps the RT-6 mock route unchanged and adds a separate
one-command manual VTS route. Flutter compile-time enablement, HomeScreen
session-local opt-in, Backend adapter enablement, and Backend provider opt-in
remain independently default off. Startup, construction, opt-in, opt-out,
reset, and disposal perform no transport or motion execution.

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7c: COMPLETED / ACCEPTED / PUSHED
RT-7d: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 2a5e3b035bcfdd273a7d056d59af01235e2459f5
implementation commit: 37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2
implementation surface: exact 28 files
acceptance-sync surface: exact 7 documentation/static-gate files
existing RT-6 route preserved: true
one-command manual boundary: true
Flutter default off: true
Backend default off: true
session opt-in default off: true
Framework development checkout referenced: false
Framework internal import: false
pyvts direct import: false
websockets direct import: false
provider/network/real motion execution: false
RT-7e exact contract review: READY
RT-7e implementation: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
acceptance-sync commit / push: NOT_AUTHORIZED
```

Run the historical acceptance-sync gate from the DRC repository root while the
exact seven files are modified against implementation commit `37f7ac8bedc5303f3ddf53e4e543b71f35ce2ed2`:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7d_default_off_configured_vts_manual_wiring.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

The gate rechecks the exact 28-file implementation history, the current exact
7-file acceptance-sync surface, default-off Backend and Flutter boundaries,
one-command manual request contract, preserved RT-6 route, fixed-vendor
root-public adapter path, and closed provider/network/real-motion markers. It
reads no private VTS configuration, imports no `pyvts`, opens no WebSocket, and
executes no real motion.

Detailed accepted contract:
`docs/v300_rt7d_default_off_configured_vts_manual_wiring.md`.
Historical acceptance-sync gate:
`scripts/check_v300_rt7d_default_off_configured_vts_manual_wiring.py`.
<!-- RT-7d-DEFAULT-OFF-CONFIGURED-VTS:END -->

## v3.0.0 RT-7e Control E acceptance-sync gate

The historical gate validates the final exact seven-file documentation/static-
gate synchronization against accepted Control D commit `ddd392c24907eae4d8c91850d84b31a7b84e760f`.

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
python -m pytest -q backend\tests\test_v300_rt7e_private_configured_local_vts_operator.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test test\framework_vts_motion_home_screen_test.dart
flutter test
cd ..

python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

For an extracted tracked-source snapshot without Git history:

```powershell
python scripts\check_v300_rt7e_private_configured_local_vts_operator_acceptance.py --snapshot
```

Normal mode verifies:

```text
HEAD and origin/main: ddd392c24907eae4d8c91850d84b31a7b84e760f
Stage 1 exact 9 files: 715b28a97f46260efc0bd76e59828d46c8749dbd..c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f
operator corrective exact 4 files: c4455fb6d14d5a6e31f2ff782e364c0eb92d2f4f..84429683d5ea26e5480bff17f5e29ad201b6ee71
Control C corrective exact 2 files: 84429683d5ea26e5480bff17f5e29ad201b6ee71..a26d027fcd40d6734cb8919059a4683c322f55da
Control D corrective exact 3 files: a26d027fcd40d6734cb8919059a4683c322f55da..ddd392c24907eae4d8c91850d84b31a7b84e760f
Control E worktree exact 7 files
Controls A-E accepted markers
RT-7 completed and RT-8 review-ready markers
protected runtime/test/vendor/dependency/release boundaries
```

Snapshot mode validates source content and protected boundaries only. It does
not claim that Git history, origin/main synchronization, or the current exact
worktree surface were independently verified.

The gate invokes the operator runner only in inert default mode. It reads no
private configuration, sends no HTTP request, imports no provider, opens no
WebSocket, starts no VTube Studio operation, and executes no real motion. The
gate never authorizes commit/push by itself.

<!-- RT-8a-PC-ANDROID-READINESS:BEGIN -->
## v3.0.0 RT-8a PC/Android realtime acceptance readiness gate

RT-8a is an exact seven-file docs/static-gate checkpoint against accepted
Control E commit `0440aa28fa7d1f49a8e15fd056de8735c83ce2ae`. It verifies the current source-level platform
matrix and freezes RT-8b through RT-8e without starting any real execution.

Run from the repository root before the RT-8a commit:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_rt8_pc_android_realtime_acceptance_readiness.py
python -m pytest -q backend\tests

cd app
flutter analyze
flutter test
cd ..

python scripts\check_v300_rt8_pc_android_realtime_acceptance_readiness.py
git -c core.whitespace=cr-at-eol diff --check
git status --short
git diff --name-only
```

For an extracted tracked-source snapshot without authoritative Git history:

```powershell
python scripts\check_v300_rt8_pc_android_realtime_acceptance_readiness.py --snapshot
```

Normal mode verifies:

```text
HEAD and origin/main: 0440aa28fa7d1f49a8e15fd056de8735c83ce2ae
Control E parent: ddd392c24907eae4d8c91850d84b31a7b84e760f
Control E committed surface: exact 7 files
RT-8a worktree surface: exact 7 files
mobile integrated voice support: native Android/iOS only
PC Windows integrated real voice support: false
PC manual stream/TTS/VTS evidence path: ready for later bounded execution
Android integrated voice plus manual VTS evidence path: ready for later bounded execution
identical cross-platform voice claim: false
automatic voice-motion synchronization claim: false
runtime/test/vendor/dependency/release changes: false
private/provider/network/microphone/VTS execution: false
```

Snapshot mode validates tracked source content, documentation markers, source
platform boundaries, protected files, and changed-content safety. It does not
claim authoritative Git-history or origin/main verification when those are not
available.

The gate never starts Backend or Flutter, reads private configuration, opens a
microphone, sends HTTP/provider/network traffic, imports a provider, opens a
VTS WebSocket, performs TTS/playback, or executes real motion. It does not
authorize commit/push or RT-8b implementation.

Detailed candidate contract:
`docs/v300_rt8_pc_android_realtime_acceptance_readiness.md`.
<!-- RT-8a-PC-ANDROID-READINESS:END -->

<!-- RT-8b-PRIVATE-OPERATOR-MANIFEST:BEGIN -->
## RT-8b private operator manifest, validator, and runbook

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8a commit: a3af4fae002c1425fdfb61b46f66e35e2443ad17
RT-8b: IMPLEMENTED / AWAITING_REVIEW
RT-8b baseline: a3af4fae002c1425fdfb61b46f66e35e2443ad17
RT-8b surface: exact 10 files
readiness: READY_FOR_BOUNDED_PRIVATE_RT8_OPERATOR_MANIFEST_AND_NETWORK_FREE_VALIDATION
RT-8c exact contract review: READY_AFTER_RT8B_ACCEPTANCE
RT-8c implementation: NOT_AUTHORIZED
RT-8d implementation: NOT_AUTHORIZED
RT-8e implementation: NOT_AUTHORIZED
private manifest created: false
private manifest read: false
private configuration read: false
provider/network/microphone/TTS/VTS execution: false
commit / push: NOT_AUTHORIZED
```

RT-8b adds a strict JSON validator, an intentionally rejected public example,
focused credential-free tests, a source preflight gate, and a fixed operator
runbook. A real manifest must remain under ignored `operator_evidence/`; RT-8b
does not create or read one.

```text
schema: drc.v3.rt8-platform-acceptance.1
stages: example / pc_windows / android / aggregate
maximum private manifest size: 65536 bytes
unknown, missing, and duplicate JSON keys: rejected
free-form text and private-looking values: rejected
public example status: example_not_accepted
```

Exact RT-8b surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt8b_private_operator_manifest_and_runbook.md
docs/operator_evidence_templates/v300_rt8_pc_android_realtime_acceptance.example.json
scripts/validate_v300_rt8_private_operator_manifest.py
scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py
backend/tests/test_v300_rt8_private_operator_manifest.py
```

Protected and unchanged are `.gitignore`, Backend/Flutter runtime, all existing
tests, dependencies, platform declarations, fixed vendor Framework, versions,
release records, historical RT-8a files, and all private configuration or
evidence. RT-8c, RT-8d, RT-8e, RT-9, and every configured real execution remain
separately unauthorized.

Detailed candidate contract:
`docs/v300_rt8b_private_operator_manifest_and_runbook.md`.
Validator:
`scripts/validate_v300_rt8_private_operator_manifest.py`.
Dedicated candidate gate:
`scripts/check_v300_rt8b_private_operator_manifest_and_runbook.py`.
<!-- RT-8b-PRIVATE-OPERATOR-MANIFEST:END -->

<!-- RT-8b1-STRICT-PC-COUNT-CORRECTIVE:BEGIN -->
## RT-8b1 strict PC execution-count contract corrective

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8a: COMPLETED / ACCEPTED / PUSHED
RT-8b: COMPLETED / ACCEPTED / PUSHED
RT-8b commit: eedc32a6293b99435d1d2e60b4a4a6e7c519c8d5
RT-8b1: IMPLEMENTED / AWAITING_REVIEW
RT-8b1 baseline: eedc32a6293b99435d1d2e60b4a4a6e7c519c8d5
RT-8b1 surface: exact 10 files
schema: drc.v3.rt8-platform-acceptance.2
RT-8c: BLOCKED_PENDING_RT8B1_ACCEPTANCE / NOT_AUTHORIZED
private manifest created: false
private manifest read: false
private configuration read: false
provider execution attempted: false
network execution attempted: false
microphone used: false
real TTS executed: false
real motion executed: false
commit / push: NOT_AUTHORIZED
```

RT-8b1 corrects only the strict PC execution-count schema before any configured
PC run. The bounded PC sequence requires three manual stream starts: two
completed terminals and one cancelled terminal. The two completed terminals
feed two explicit TTS enqueue/process actions; the second playback is stopped by
one explicit local flush.

```text
manual_stream_start_count: 3
completed_stream_terminal_count: 2
cancelled_stream_terminal_count: 1
cooperative_cancel_request_count: 1
explicit_tts_enqueue_count: 2
explicit_tts_process_count: 2
explicit_flush_count: 1
app_owned_motion_presentation_count: 1
manual_vts_apply_count: 1
```

The public example remains `example_not_accepted`. RT-8b1 creates and reads no
private manifest and performs no Backend, Flutter, provider, network,
microphone, STT, TTS, playback, VTS, or physical-motion operation.
<!-- RT-8b1-STRICT-PC-COUNT-CORRECTIVE:END -->

<!-- RT-8c-PC-WINDOWS-ACCEPTANCE:BEGIN -->
## RT-8c configured PC Windows realtime acceptance

RT-8c is **COMPLETED / ACCEPTED / PUSHED** at source commit
`fa39065130a4a4689c2e54195f231a5e79c62a35` against accepted baseline
`4815403d4c94b05551df03678e9c2c4e1dfe754e`.

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8c: COMPLETED / ACCEPTED / PUSHED
RT-8c Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-8c Stage 1 commit: fa39065130a4a4689c2e54195f231a5e79c62a35
RT-8c Stage 1 surface: exact 9 files
RT-8c Stage 2 credential-free preflight: COMPLETED / PASS
RT-8c Stage 2 Controls A-H: COMPLETED / ACCEPTED
RT-8c Stage 2 manifest recording: COMPLETED / ACCEPTED
RT-8c Stage 2 strict validation: COMPLETED / ACCEPTED
RT-8c Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW
RT-8c Stage 3 surface: exact 7 documentation/static-gate files
RT-8d exact contract review: READY
RT-8d implementation: NOT_AUTHORIZED
RT-8e: BLOCKED_PENDING_RT8D / NOT_AUTHORIZED
schema: drc.v3.rt8-platform-acceptance.2
acceptance-sync commit / push: NOT_AUTHORIZED
```

Accepted PC chronology and exact counts:

```text
chronology: A -> B -> D -> C -> E -> F -> G -> H
manual_stream_start_count: 3
completed_stream_terminal_count: 2
cancelled_stream_terminal_count: 1
cooperative_cancel_request_count: 1
explicit_tts_enqueue_count: 2
explicit_tts_process_count: 2
explicit_flush_count: 1
pending_after_flush: 0
app_owned_motion_presentation_count: 1
manual_vts_apply_count: 1
vts_commands_requested: 1
vts_commands_applied: 1
vts_commands_completed: 1
```

The accepted PC path includes incremental streaming, one cooperative cancelled
terminal with retained partial output, two explicit real-TTS enqueue/process
operations, one natural audible completion, one active-playback app-owned local
flush, one mock-motion presentation, and one manual configured VTS Apply.
Backend/Flutter `real_motion_executed` remains false; separate operator-visible
physical motion was confirmed once.

The ignored strict PC-stage manifest was created without overwrite after nine
fixed confirmations and passed schema-v2 and candidate Git-state validation. It
remains ignored, untracked, uncommitted, and unpushed. Its content and private
values are not included in tracked files and are not read by the Stage 3 gate.

RT-8c does not claim PC microphone, PC STT, PC soft barge-in, provider or Backend
hard cancel, Framework real TTS queue flush, unified realtime, automatic
voice-motion synchronization, or runtime proof of physical motion. Android
voice acceptance remains owned by RT-8d.

Detailed accepted contract:
`docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md`.
Historical implementation and Stage 3 acceptance-sync gate:
`scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py`.
Operator recorder retained unchanged:
`scripts/run_v300_rt8c_private_pc_windows_operator.py`.
<!-- RT-8c-PC-WINDOWS-ACCEPTANCE:END -->

<!-- RT-8d-STAGE1-ANDROID-TOOLING:BEGIN -->
## RT-8d configured Android smartphone realtime acceptance

```text
RT-8: CURRENT / NOT_COMPLETED
RT-8c: COMPLETED / ACCEPTED / PUSHED
RT-8d: COMPLETED / ACCEPTED / PUSHED
RT-8d Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-8d Stage 1 commit: 0e7fc6fc5922c293b8460fc816610d41c2a79e9a
RT-8d Stage 2a: COMPLETED / PASS
RT-8d Stage 2b: COMPLETED / PASS
RT-8d Stage 2c: COMPLETED / PASS / ACCEPTED
RT-8d Stage 2d: COMPLETED / PASS / ACCEPTED
RT-8d Stage 2e: COMPLETED / PASS / ACCEPTED
RT-8d Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW
RT-8d Stage 3 surface: exact 7 documentation/static-gate files
RT-8e exact contract review: READY
RT-8e implementation: NOT_AUTHORIZED
RT-9: BLOCKED_PENDING_RT8 / NOT_AUTHORIZED
schema: drc.v3.rt8-platform-acceptance.2
accepted PC source: fa39065130a4a4689c2e54195f231a5e79c62a35
accepted Android source: 0e7fc6fc5922c293b8460fc816610d41c2a79e9a
acceptance-sync commit / push: NOT_AUTHORIZED
```

Accepted chronology and counts:

```text
A -> B -> C -> D -> E -> F -> G -> H
natural_voice_turn_count: 1
silent_control_interruption_count: 0
confirmed_user_speech_event_count: 1
drc_local_interruption_count: 1
pending_voice_output_after_interruption: 0
recovery_voice_turn_count: 1
manual_vts_apply_count: 1
vts_commands_requested: 1
vts_commands_applied: 1
vts_commands_completed: 1
```

The configured VTS boundary completed one explicit Apply. Framework session
creation/closure and provider/network attempts were true. The conservative
Backend/Flutter `real_motion_executed` value remained false, while the operator
separately confirmed exactly one visible physical model motion.

The original Stage 2c attempt remains FAILED / NOT_ACCEPTED. Its Controls A-F
observations were not reused; all accepted facts come only from the separately
authorized fresh A-H rerun.

The ignored manifest transitioned from accepted PC stage to accepted Android
stage using nine fixed confirmations. The previous PC section was preserved.
Strict schema, candidate Git-state, and PC-to-Android ancestry validation passed.
The private manifest remains ignored, untracked, uncommitted, and unpushed.

Stage 3 changes only the exact seven public documentation/static-gate files. It
does not read private manifest content or perform aggregate transition,
Backend/Flutter/device startup, microphone/STT, provider/network, TTS/playback,
or VTS execution. Aggregate cleanup and RT-8 acceptance synchronization remain
owned by RT-8e.

Detailed accepted contract:
`docs/v300_rt8d_configured_android_realtime_acceptance.md`.

Dedicated Stage 3 gate:
`scripts/check_v300_rt8d_configured_android_realtime_acceptance.py`.

Operator runner retained unchanged:
`scripts/run_v300_rt8d_private_android_operator.py`.
<!-- RT-8d-STAGE1-ANDROID-TOOLING:END -->

<!-- RT-8E-STAGE1-AGGREGATE-TOOLING:BEGIN -->
## RT-8e aggregate cleanup and RT-8 acceptance

```text
RT-8: COMPLETED / ACCEPTED
RT-8d: COMPLETED / ACCEPTED / PUSHED
RT-8d Stage 3 acceptance-sync commit: 84839efd6e381cb5a2c45022a7e8f7d9eafcb5df
RT-8e: COMPLETED / ACCEPTED / PUSHED
RT-8e Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-8e Stage 1 commit: 25c003405fe1a59f3ca7e8a8a6788698ad30bf6d
RT-8e Stage 1 surface: exact 9 files
RT-8e Stage 2: COMPLETED / PASS / ACCEPTED
RT-8e Stage 2 aggregate transition: COMPLETED / PASS / ACCEPTED
RT-8e Stage 2 strict validation: COMPLETED / PASS / ACCEPTED
RT-8e Stage 3 acceptance sync: IMPLEMENTED / AWAITING_REVIEW
RT-8e Stage 3 surface: exact 7 documentation/static-gate files
RT-9: READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
v3.0.0: RELEASED / ACCEPTED
schema: drc.v3.rt8-platform-acceptance.2
accepted PC candidate source: fa39065130a4a4689c2e54195f231a5e79c62a35
accepted Android candidate source: 0e7fc6fc5922c293b8460fc816610d41c2a79e9a
private manifest stage: aggregate
private manifest status: accepted
private manifest read by Stage 3 gate: false
private manifest modified by Stage 3: false
configured execution performed by Stage 3: false
acceptance-sync commit / push: NOT_AUTHORIZED
```

Stage 1 added the inert aggregate-transition runner, exact eighteen focused
Backend tests, the fixed three-stage contract, and the dedicated gate. Its
implementation commit is `25c003405fe1a59f3ca7e8a8a6788698ad30bf6d`. Verification passed with the dedicated
gate, 18 focused Backend tests, 417 full Backend tests with one existing warning,
Flutter analyze, 500 full Flutter tests, exact-surface review, privacy review,
push, and clean-tree verification.

Stage 2 then passed inert/preflight/Android-transition checks, the fixed nine
aggregate confirmations, atomic Android-to-aggregate manifest transition,
strict aggregate-stage schema/Git validation, and final DRC/FW clean-state
verification. The private manifest remains ignored, untracked, uncommitted, and
unpushed. No Backend, Flutter, ADB, microphone/STT, provider/network, TTS/playback,
VTS/WebSocket, motion, or additional PC/Android control execution occurred.

Stage 3 changes only the exact seven public documentation/static-gate files. It
does not read private manifest content, repeat cleanup, or perform configured
execution. It synchronizes parent RT-8 completion and leaves RT-9 only ready for
an exact contract review; RT-9 implementation remains unauthorized and v3.0.0
remains unreleased.

Detailed accepted contract:
`docs/v300_rt8e_aggregate_cleanup_and_rt8_acceptance.md`.

Dedicated Stage 3 gate:
`scripts/check_v300_rt8e_aggregate_cleanup_and_acceptance.py`.

Aggregate runner retained unchanged:
`scripts/run_v300_rt8e_private_aggregate_cleanup.py`.
<!-- RT-8E-STAGE1-AGGREGATE-TOOLING:END -->


<!-- RT-9A-RELEASE-INVENTORY:BEGIN -->
## RT-9a accepted release/security inventory

```text
RT-8: COMPLETED / ACCEPTED
RT-8e: COMPLETED / ACCEPTED / PUSHED
RT-8e Stage 3 acceptance-sync commit: 4c3b724a0c42e0d078c876c02b07a04d4c71e24d
RT-9: COMPLETED / ACCEPTED
RT-9a: COMPLETED / ACCEPTED / PUSHED
RT-9a implementation commit: 0e4af7603f60c56f0240271fbb2590d72a189a65
RT-9a surface: exact 7 documentation/static-gate files
RT-9b: COMPLETED / ACCEPTED / PUSHED
RT-9b implementation commit: 15908a548c229726287867ad89c7ce8b4b916298
RT-9c Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 1 implementation commit: 7110035eff205d77157b8058b274b4c281a51f7e
RT-9c Stage 2: COMPLETED / PASS / ACCEPTED
RT-9c Stage 3: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 3 acceptance-sync commit: 859eeae53b7b84d2c90fb301eb9e2b981cc731c0
RT-9d: COMPLETED / ACCEPTED
RT-9e: COMPLETED / ACCEPTED
v3.0.0: RELEASED / ACCEPTED
```

RT-9a froze the release/security current behavior, the RT-9a through RT-9e
split, current test/version/tooling baselines, package privacy boundary, allowed
release claims, required non-claims, and the stop rule. Its dedicated gate,
Backend 417-test regression, Flutter analyze, Flutter 500-test regression,
exact-surface/privacy review, explicit approval, push, and clean-tree
verification passed. It created no release ZIP, tag, or GitHub Release.

Detailed accepted inventory:
`docs/v300_rt9_release_readiness_current_behavior_inventory.md`.

Historical RT-9a gate:
`scripts/check_v300_rt9_release_readiness_current_behavior_inventory.py`.
<!-- RT-9A-RELEASE-INVENTORY:END -->

<!-- RT-9B-RELEASE-READINESS:BEGIN -->
## RT-9b accepted v3.0.0 candidate metadata and aggregate readiness

```text
RT-9: COMPLETED / ACCEPTED
RT-9a: COMPLETED / ACCEPTED / PUSHED
RT-9a commit: 0e4af7603f60c56f0240271fbb2590d72a189a65
RT-9b: COMPLETED / ACCEPTED / PUSHED
RT-9b implementation commit: 15908a548c229726287867ad89c7ce8b4b916298
RT-9b surface: exact 13 files
Backend candidate metadata: 3.0.0
Flutter candidate metadata: 3.0.0+4
current released version: v2.1.0 RELEASED / ACCEPTED
v3.0.0 release notes: RELEASE CANDIDATE / NOT_RELEASED
v3.0.0 release record: PREPARED / NOT_RELEASED
RT-9c Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 1 implementation commit: 7110035eff205d77157b8058b274b4c281a51f7e
RT-9c Stage 2: COMPLETED / PASS / ACCEPTED
RT-9c Stage 3: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 3 acceptance-sync commit: 859eeae53b7b84d2c90fb301eb9e2b981cc731c0
RT-9d: COMPLETED / ACCEPTED
RT-9e: COMPLETED / ACCEPTED
v3.0.0 fixed ZIP: NOT_BUILT
DRC_v3.0.0 annotated tag: NOT_CREATED
GitHub Release: NOT_CREATED
```

RT-9b synchronized Backend `3.0.0` and Flutter `3.0.0+4` candidate metadata,
added the active v3 source/test/build readiness gate, preserved historical
release records, and kept publication state unfilled. Portable and full Windows
verification passed with Backend 417 tests, Flutter analyze, Flutter 500 tests,
Web/Windows/Android debug builds, strict read-only RT-8 aggregate validation,
exact-surface/privacy review, explicit approval, push, and clean-tree checks.
No fixed ZIP, tag, or GitHub Release was created.

Detailed accepted contract:
`docs/v300_rt9_release_readiness.md`.

Active aggregate gate:
`scripts/check_v300_rt9_release_readiness.py`.
<!-- RT-9B-RELEASE-READINESS:END -->

<!-- RT-9C-STAGE1-FIXED-ZIP-TOOLING:BEGIN -->
## RT-9c accepted fixed-ZIP tooling and no-build preflight

```text
RT-9: COMPLETED / ACCEPTED
RT-9b: COMPLETED / ACCEPTED / PUSHED
RT-9b implementation commit: 15908a548c229726287867ad89c7ce8b4b916298
RT-9c: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 1: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 1 implementation commit: 7110035eff205d77157b8058b274b4c281a51f7e
RT-9c Stage 1 surface: exact 13 files
RT-9c Stage 2: COMPLETED / PASS / ACCEPTED
RT-9c Stage 2 source HEAD: 7110035eff205d77157b8058b274b4c281a51f7e
RT-9c Stage 2 source branch: main
RT-9c Stage 2 builder invocation count: 0
RT-9c Stage 2 fixed ZIP built: false
RT-9c Stage 2 private manifest: read-only / unchanged / ignored / untracked / unpushed
RT-9c Stage 3: COMPLETED / ACCEPTED / PUSHED
RT-9c Stage 3 acceptance-sync commit: 859eeae53b7b84d2c90fb301eb9e2b981cc731c0
RT-9c Stage 3 baseline: 7110035eff205d77157b8058b274b4c281a51f7e
RT-9c Stage 3 surface: exact 9 public documentation files
RT-9d: COMPLETED / ACCEPTED
RT-9e: COMPLETED / ACCEPTED
fixed ZIP builder invocation count: 0
v3.0.0 fixed ZIP: NOT_BUILT
same-artifact verification: NOT_COMPLETED
DRC_v3.0.0 annotated tag: NOT_CREATED
GitHub Release: NOT_CREATED
v3.0.0: RELEASED / ACCEPTED
implementation commit / push: NOT_AUTHORIZED
```

Stage 1 added credential-free one-time fixed-ZIP builder/verifier tooling and
was accepted, committed, and pushed at `7110035eff205d77157b8058b274b4c281a51f7e`. Stage 2 then ran the
committed-source `-PreflightOnly` path from clean synchronized official Public
`main`. Backend 417 tests, Flutter analyze, Flutter 500 tests, Web/Windows/Android
debug builds, and strict read-only RT-8 aggregate validation passed. The private
manifest remained ignored, untracked, unchanged, and unpushed. The generic
builder was invoked zero times, and no fixed ZIP, tag, or GitHub Release was
created.

Stage 3 changed only the exact nine public documentation files and was accepted, committed, and pushed. It does not read
private evidence, execute provider/network/microphone/STT/TTS/VTS paths, invoke
any builder or verifier artifact mode, record a release tuple, create a tag, or
publish a release. The detailed Stage 1 tooling file remains the immutable
implementation-time contract; these current public state files are the active
acceptance source of truth.

Detailed tooling contract:
`docs/v300_rt9_fixed_release_zip.md`.

One-time builder:
`build_v300_fixed_release_zip_from_head.ps1`.

Source/same-artifact verifier:
`scripts/check_v300_fixed_release_zip.py`.
<!-- RT-9C-STAGE1-FIXED-ZIP-TOOLING:END -->

<!-- RT-9E-FINAL-DOCS-SYNC:BEGIN -->
## RT-9e publication completion and final documentation-sync candidate

```text
RT-9: COMPLETED / ACCEPTED
RT-9a: COMPLETED / ACCEPTED / PUSHED
RT-9b: COMPLETED / ACCEPTED / PUSHED
RT-9c: COMPLETED / ACCEPTED / PUSHED
RT-9d: COMPLETED / ACCEPTED
RT-9d Control A: COMPLETED / PASS / ACCEPTED
RT-9d Control B: COMPLETED / PASS / ACCEPTED
RT-9d Control C: COMPLETED / PASS / ACCEPTED / PUSHED
RT-9d Control C commit: b5a41e8568a73e0efecc57f4273f7b254e13353a
RT-9d acceptance sync: COMPLETED / PASS / ACCEPTED / PUSHED
RT-9d acceptance-sync commit: 513046be6016fae787dc77b2dda44681c697ed9c
RT-9e Control A: PREFLIGHT / PASS / ACCEPTED
RT-9e Control B: FINAL OPERATOR APPROVAL / RECEIVED / ACCEPTED
RT-9e Control C: PUBLICATION / PASS / ACCEPTED
RT-9e Control D: POST_PUBLICATION_VERIFICATION / PASS / ACCEPTED
RT-9e: COMPLETED / ACCEPTED
RT-9e final docs sync: IMPLEMENTED / AWAITING_REVIEW
RT-9e final docs-sync baseline: 513046be6016fae787dc77b2dda44681c697ed9c
RT-9e final docs-sync exact surface: exact 9 public documentation files
publication-preparation HEAD: 513046be6016fae787dc77b2dda44681c697ed9c
release source HEAD: f5fb54dc4beecdd1fdec957e92bf0b8cfc76513a
verification HEAD: 4b08d20425c469e41277cfb7a013ed2a266c3489
post-build verifier-only corrective commits: 2
tuple-record commit: b5a41e8568a73e0efecc57f4273f7b254e13353a
explicit final operator release approval: RECEIVED / ACCEPTED / 2026-08-04
annotated tag: DRC_v3.0.0
annotated tag type: tag
annotated tag object: ab61a1583370ccd2a61789e67ee837c09dc7c663
annotated tag target: f5fb54dc4beecdd1fdec957e92bf0b8cfc76513a
annotated tag message: Daily Rhythm Companion v3.0.0
annotated tag publication: PUBLISHED
GitHub Release title: Daily Rhythm Companion v3.0.0
GitHub Release URL: https://github.com/murayan1982/daily-rhythm-companion-public/releases/tag/DRC_v3.0.0
GitHub Release publication: PUBLISHED
GitHub Release draft: false
GitHub Release prerelease: false
frozen release body size: 2862
frozen release body SHA-256: 9c3f51fd25de28af9f1ae5e69efe1f8f458dd8885228067fc2d57fab9c5fd82f
fixed ZIP basename: DailyRhythmCompanion_v3.0.0_20260804_183416.zip
fixed ZIP size: 2774558
fixed ZIP SHA-256: 9a4f28d337ace03bb1a1371165a2299f90c2c4d2ecbfefa95130b2fabedb3cd6
fixed ZIP builder invocation count: 1
artifact count: 1
same-artifact verification: COMPLETED / PASS / ACCEPTED
release-package hygiene: PASS / exact-source-matched-synthetic-fixtures
ZIP CRC and single-package-root verification: PASS
Backend pytest from extracted ZIP: 417 passed
Flutter analyze from extracted ZIP: PASS
Flutter test from extracted ZIP: 500 passed
Flutter Web build from extracted ZIP: PASS
Flutter Windows build from extracted ZIP: PASS
Flutter Android debug build from extracted ZIP: PASS
published asset basename: DailyRhythmCompanion_v3.0.0_20260804_183416.zip
published asset size: 2774558
published asset SHA-256: 9a4f28d337ace03bb1a1371165a2299f90c2c4d2ecbfefa95130b2fabedb3cd6
post-publication asset re-downloaded: true
downloaded asset matches fixed ZIP: PASS
post-publication SHA-256 verification: COMPLETED / PASS
fixed ZIP rebuilt / replaced by publication: false
local fixed ZIP unchanged after publication: PASS
private RT-8 manifest read by final docs sync: false
private RT-8 manifest: ignored / untracked / unpushed
historical DRC_v2.0.0 / DRC_v2.0.1 / DRC_v2.1.0 releases changed: false
v3.0.0: RELEASED / ACCEPTED
final docs-sync commit / push: NOT_AUTHORIZED
```

The immutable fixed ZIP was built once from the recorded release source HEAD,
verified without rebuilding, published as the only GitHub Release asset, and
re-downloaded into a temporary directory. The downloaded basename, size, and
SHA-256 matched the accepted fixed tuple exactly.

This final docs-sync candidate records only public release facts. It does not
read private evidence, alter runtime or tests, invoke a builder or artifact
verifier, rebuild or replace the fixed ZIP, modify the annotated tag or GitHub
Release, upload another asset, repeat provider/network/microphone/STT/TTS/VTS
execution, commit, or push.
<!-- RT-9E-FINAL-DOCS-SYNC:END -->
