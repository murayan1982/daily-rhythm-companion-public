# Daily Rhythm Companion Scripts

This directory contains development, verification, release, compatibility, and configured-demo helper scripts for Daily Rhythm Companion.

## v2.0.x current maintenance baseline

v2.0.0 is **RELEASED** as the immutable Public baseline. The active detailed source of truth is `docs/DRC_v20x_maintenance_checklist.md`.

Current patch source and small commit:

```text
v2.0.1
M-8  COMPLETED / ACCEPTED
test/docs: add v2.0.x aggregate maintenance readiness
```

M-1 through M-8 are completed and accepted. No small commit is currently active, and M-9 remains PLANNED. M-8 adds the normal aggregate maintenance gate while keeping historical release evidence separate.

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
