# Daily Rhythm Companion v2.0.x maintenance checklist

Updated: 2026-07-23
Status: IN_PROGRESS
Current small commit: none (M-8 accepted; M-9 planned)
Expected first patch release: v2.0.1

## Source-of-truth rule

This file is the detailed source of truth for v2.0.x maintenance. `tasklist.md` is the concise operator index and `roadmap.md` defines version direction.

The completed v2.0.0 checklist remains historical and must not be edited into a post-release checklist:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
GitHub Release / annotated tag: DRC_v2.0.0
```

## Progress rule

```text
- At most one small commit is CURRENT at a time.
- A task remains NOT_COMPLETED until its files, checks, and operator review pass.
- Later tasks remain PLANNED and must not be marked complete early.
- A guarded boundary is not counted as real runtime implementation.
- A source-tree check is not counted as configured real execution evidence.
```

## Immutable baseline

```text
v2.0.0 status: RELEASED
fixed ZIP: DailyRhythmCompanion_20260722_180426.zip
SHA-256: b32c7b8a64842480898fcc86ca7838625efb712f1429ab9fe7b33a4001ddc0c1
post-publication SHA-256 re-verification: completed
```

The published v2.0.0 tag and release asset are not edit targets.

---

# M-1 — Establish post-v2.0.0 maintenance baseline

Status: COMPLETED
Commit title:

```text
docs: establish post-v2.0.0 maintenance baseline
```

Accepted outcomes:

```text
- v2.0.0 RELEASED is the immutable baseline.
- This v2.0.x checklist is the active detailed source of truth.
- Public source and Private operator-environment boundaries are documented.
- Historical v2.0.0 checklist and release-note content remain unchanged.
- Runtime behavior was not changed by M-1.
```

---

# M-2 — Align application version metadata

Status: COMPLETED
Commit title:

```text
fix/test: align application version metadata
```

## Purpose

```text
- Inventory backend, Flutter, Web, platform, and user-visible version surfaces.
- Advance the current maintenance source to semantic version 2.0.1.
- Keep backend and Flutter version ownership explicit without adding conflicting production constants.
- Expose the backend version through FastAPI/OpenAPI and the additive /health runtime field.
- Keep Flutter/Web display backward compatible when an older backend omits the version.
- Add focused credential-free regression checks.
```

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/app/version.py
backend/app/main.py
backend/app/api/health.py
app/pubspec.yaml
app/lib/services/backend_api_client.dart
app/test/widget_test.dart
docs/v20x_application_version_metadata.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
```

## Inspected but intentionally unchanged

```text
app/web/index.html
app/web/manifest.json
app/android/app/build.gradle.kts
app/ios/Runner/Info.plist
app/macos/Runner/Configs/AppInfo.xcconfig
app/windows/runner/Runner.rc
app/linux/CMakeLists.txt
```

These surfaces either contain product identity only or inherit Flutter-generated version/build values from `app/pubspec.yaml`. M-2 does not add a second hard-coded application version to them.

## Explicit non-change surface

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
provider and OAuth implementation
health-data provider selection or normalization
LLM, TTS, STT, chat, and motion behavior
persistence schema
release ZIP, tag, and GitHub Release handling
```

## Completion requirements

```text
- backend/app/version.py is the only backend runtime version constant and contains APP_VERSION=2.0.1.
- FastAPI/OpenAPI uses APP_VERSION instead of the former 0.15.0 literal.
- /health returns status=ok and version=2.0.1.
- app/pubspec.yaml uses version 2.0.1+2.
- Flutter semantic version 2.0.1 matches backend APP_VERSION.
- BackendApiClient displays the optional /health version and preserves legacy no-version behavior.
- Web source metadata does not introduce a duplicate hard-coded version.
- docs/v20x_application_version_metadata.md records the source-owner and inheritance rules.
- M-3 through M-9 remain PLANNED.
- Historical v2.0.0 checklist and release-note normalized content hashes remain unchanged.
- python -m compileall -q backend scripts passes.
- python scripts\check_v20x_maintenance_baseline.py passes.
- python scripts\check_v20x_application_version_metadata.py passes.
- flutter test passes from app/.
- The operator reviews the diff and approves the small commit.
```

M-2 was accepted and committed before M-3 began. M-2 did not release v2.0.1.

---

# M-3 — Add backend mock-safe regression foundation

Status: COMPLETED
Commit title:

```text
test: add backend mock-safe regression foundation
```

## Purpose

```text
- Introduce a normal backend pytest layout separate from historical release-evidence smoke checks.
- Cover core credential-free health, character, sleep, advice, and DailyRecord behavior.
- Make normal regression execution deterministic and independent from backend/.env.
- Keep real providers, OAuth, Framework execution, and real TTS outside the default suite.
```

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/requirements-dev.txt
backend/tests/conftest.py
backend/tests/test_core_api.py
backend/tests/test_mock_advice.py
backend/tests/test_daily_record_store.py
docs/v20x_backend_mock_safe_regression.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
```

## Explicit non-change surface

```text
backend application/runtime implementation
backend/requirements.txt production dependency set
Framework success/fallback behavior
voice output artifact behavior
real LLM, TTS, STT, health API, OAuth, or motion execution
persistence schema
release ZIP, tag, and GitHub Release handling
```

## Test boundary

```text
- conftest disables backend/.env loading and clears real-execution environment variables.
- API tests create a small local FastAPI instance with only health, characters, and sleep routers.
- Advice tests call MockConversationEngine directly.
- DailyRecord tests use pytest tmp_path and never use backend/local_data.
- Full app Framework fallback and voice artifact tests remain M-4 work.
```

## Completion requirements

```text
- backend/requirements-dev.txt includes backend/requirements.txt and a bounded pytest dependency.
- backend/tests contains the shared mock-safe fixture and focused core regression modules.
- health returns the active APP_VERSION.
- characters returns the stable three bundled character IDs and display names.
- sleep summary uses the deterministic mock provider.
- mock advice preserves stable mock source metadata and does not invent unavailable sleep values.
- DailyRecord upsert/read/update behavior is verified in a temporary SQLite database.
- No normal M-3 test imports app.main or accesses backend/local_data.
- docs/v20x_backend_mock_safe_regression.md records setup, scope, exclusions, and commands.
- M-4 through M-9 remain PLANNED.
- Historical v2.0.0 checklist and release-note normalized content hashes remain unchanged.
- python -m compileall -q backend scripts passes.
- python scripts\check_v20x_maintenance_baseline.py passes.
- python scripts\check_v20x_application_version_metadata.py passes.
- python scripts\check_v20x_backend_mock_safe_regression.py passes.
- python -m pytest -q backend/tests passes.
- flutter test passes from app/.
- The operator reviews the diff and approves the small commit.
```

M-3 was accepted and committed before M-4 began. M-3 did not release v2.0.1.

---

# M-4 — Cover Framework fallback and voice artifact safety

Status: COMPLETED
Commit title:

```text
test: cover Framework fallback and voice artifact safety
```

## Accepted outcomes

```text
- FrameworkConversationEngine calls the public create_text_chat_session facade in a temporary fake package.
- Framework success preserves framework source and character-mapping metadata.
- Empty Framework responses raise FrameworkEngineError.
- Framework failure remains visible as framework_fallback without claiming provider success.
- Managed staging MP3 publication returns an opaque DRC URL.
- Outside paths, unsupported formats, traversal strings, and malformed IDs are rejected.
- The normal tests remain credential-free and do not modify backend/local_data.
- M-4 changed tests and documentation only; backend runtime behavior was unchanged.
```

M-4 was accepted before M-5 began. M-4 did not release v2.0.1.

---

# M-5 — Bound temporary chat sessions and TTS artifacts

Status: COMPLETED
Commit title:

```text
fix/test: bound temporary chat sessions and TTS artifacts
```

## Purpose

```text
- Bound process-local post-advice chat sessions by idle TTL and count capacity.
- Bound DRC-managed TTS staging/public artifacts by TTL and count capacity.
- Add lazy cleanup without background workers or new public cleanup endpoints.
- Preserve existing chat and voice-output API response models and not-found behavior.
- Keep the implementation mock-safe and covered by deterministic clock-driven tests.
```

## Accepted default configuration

```text
POST_ADVICE_CHAT_TTL_SECONDS=1800
POST_ADVICE_CHAT_MAX_SESSIONS=100
VOICE_OUTPUT_ARTIFACT_TTL_SECONDS=86400
VOICE_OUTPUT_ARTIFACT_MAX_COUNT=100
```

All four settings require positive integers. Missing, zero, negative, or malformed values fall back to the bounded defaults rather than disabling cleanup.

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/.env.example
backend/env_profiles/mock_safe.env
backend/app/config.py
backend/app/services/post_advice_chat_service.py
backend/app/services/voice_output_artifact_store.py
backend/app/services/voice_output_demo_service.py
backend/tests/test_post_advice_chat_lifecycle.py
backend/tests/test_temporary_lifecycle_config.py
backend/tests/test_voice_output_artifact_store.py
docs/v20x_framework_fallback_voice_artifact_regression.md
docs/v20x_temporary_lifecycle_limits.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
scripts/check_v20x_temporary_lifecycle_limits.py
```

## Inspected but intentionally unchanged

```text
backend/app/api/voice_output_demo.py
backend/app/api/chat.py
backend/app/models/chat.py
backend/app/models/voice_output_demo.py
```

The audio resolver retains its historical no-argument `VoiceOutputArtifactStore()` construction so existing fake-store smoke replacement remains compatible. The store loads active lifecycle configuration internally.

## Explicit non-change surface

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
chat API models and route paths
voice-output response models and opaque URL shape
Framework provider implementation
real LLM, TTS, STT, health API, OAuth, or motion execution
Flutter application behavior
persistence schema
release ZIP, tag, and GitHub Release handling
```

## Chat-session lifecycle contract

```text
- TTL is measured from the last successful create, get, or message operation.
- Expired sessions are removed lazily before create/get/message operations and by cleanup().
- Capacity eviction removes the least-recently-used session before a new session is stored.
- Successful get and message operations refresh recency.
- Expired or evicted sessions preserve the existing 404 Chat session not found API behavior.
- ChatSessionResponse and ChatMessageResponse remain unchanged.
```

## TTS-artifact lifecycle contract

```text
- Public artifact TTL is measured from DRC publication time, stored in file mtime.
- Resolving an artifact does not extend its lifetime.
- Staging leftovers and public artifacts receive lazy TTL/count cleanup.
- framework_artifact_dir reserves capacity for the next generated staging file.
- Public capacity cleanup retains the newly published artifact and removes older files first.
- Cleanup operates only on direct regular files under managed staging/public directories.
- Symlinks are not followed or deleted by cleanup and are never served as artifacts.
- Expired or evicted artifacts preserve the existing 404 voice artifact behavior.
- The opaque /demo/voice-output/audio/<artifact-id> URL contract remains unchanged.
```

## Completion requirements

```text
- AppConfig exposes all four bounded lifecycle settings and load_config parses them safely.
- backend/.env.example and mock_safe.env document the same bounded defaults.
- PostAdviceChatService implements idle expiry, LRU capacity, explicit cleanup, and deterministic clock injection.
- VoiceOutputArtifactStore implements publish-time TTL, staging/public cleanup, capacity limits, and deterministic clock injection.
- VoiceOutputDemoService passes active AppConfig and the audio resolver preserves its no-argument store construction; both resolve lifecycle settings through VoiceOutputArtifactStore.
- Tests verify chat TTL refresh, expiry, LRU eviction, cleanup, and unchanged 404 behavior.
- Tests verify TTS expiry, count eviction, staging cleanup, and existing unsafe-path rejection.
- M-6 through M-9 remain PLANNED.
- Historical v2.0.0 checklist and release-note normalized content hashes remain unchanged.
- python -m compileall -q backend scripts passes.
- M-1 through M-5 checks pass.
- python -m pytest -q backend/tests passes.
- flutter test passes from app/.
- The operator reviews the diff and approves the small commit.
```

M-5 was accepted on 2026-07-22 after compileall, M-1 through M-5 checks, 26 backend pytest tests, 39 Flutter tests, diff review, and operator approval passed. M-5 did not release v2.0.1.

---

# M-6 — Make Web CORS origins configurable

Status: COMPLETED / ACCEPTED
Commit title:

```text
fix/test: make Web CORS origins configurable
```

## Purpose

```text
- Replace the hard-coded Web CORS origin list with AppConfig ownership.
- Preserve the released local-demo wildcard default.
- Allow explicit comma- or space-separated origin restrictions.
- Add mock-safe configuration and preflight boundary regression tests.
```

## Current configuration contract

```text
WEB_CORS_ORIGINS=*
```

`*` preserves the current local-demo behavior. Explicit origins are supplied as a comma- or space-separated list. Missing, blank, or separator-only values fall back to `*`.

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/.env.example
backend/env_profiles/mock_safe.env
backend/app/config.py
backend/app/main.py
backend/tests/test_web_cors_config.py
docs/v20x_web_cors_origins.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
scripts/check_v20x_temporary_lifecycle_limits.py
scripts/check_v20x_web_cors_origins.py
```

## Explicit non-change surface

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
existing API routes and response models
Flutter application behavior
authentication, reverse-proxy, trusted-host, and TLS policy
real LLM, TTS, STT, health API, OAuth, or motion execution
release ZIP, tag, GitHub Release, or v2.0.1 publication
```

## Current implementation contract

```text
- AppConfig owns web_cors_origins with the default tuple ("*",).
- load_config reads WEB_CORS_ORIGINS using the existing comma/space tuple parser.
- backend/app/main.py passes list(config.web_cors_origins) to CORSMiddleware.
- allow_credentials remains False.
- allow_methods and allow_headers remain ["*"].
- Focused tests use a temporary FastAPI app and do not import the full production app.
```

## Completion requirements

```text
- Default configuration preserves wildcard preflight behavior.
- Explicit configured origins are accepted at the CORS boundary.
- Unlisted origins are rejected at the preflight boundary.
- backend/.env.example and mock_safe.env document the local-demo default.
- At M-6 acceptance, M-7 through M-9 remained PLANNED.
- Historical v2.0.0 checklist and release-note normalized content hashes remain unchanged.
- python -m compileall -q backend scripts passes.
- M-1 through M-6 checks pass.
- python -m pytest -q backend/tests passes.
- flutter test passes from app/.
- The operator reviews the diff and approves the small commit.
```

M-6 was accepted on 2026-07-23 after compileall, M-1 through M-6 checks, 31 backend pytest tests, 39 Flutter tests, diff review, and operator approval passed. M-6 did not release v2.0.1.

---

# Planned queue

## M-7 — Clarify Fitbit current-state contract

Status: COMPLETED / ACCEPTED

Commit title:

```text
docs/test: clarify Fitbit current-state contract
```

### Purpose

```text
- Inventory recommended, stub, deprecated alias, legacy, unavailable, and migration roles from the actual implementation.
- Keep retained Fitbit source boundaries distinct from configured real-use acceptance.
- Prevent local token-like data or OAuth URL preparation from appearing as verified connection success in Flutter presentation.
- Add mock-safe backend and Flutter regression coverage.
- Define the handoff into the v2.1.0 Fitbit completion scope.
```

### Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
backend/tests/test_fitbit_current_state_contract.py
app/lib/models/fitbit_status.dart
app/lib/models/fitbit_connect_response.dart
app/test/fitbit_current_state_contract_test.dart
docs/fitbit_integration_plan.md
docs/legacy_fitbit_cleanup_plan.md
docs/v20x_fitbit_current_state_contract.md
docs/DRC_v20x_maintenance_checklist.md
scripts/check_legacy_fitbit_boundary.py
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
scripts/check_v20x_temporary_lifecycle_limits.py
scripts/check_v20x_web_cors_origins.py
scripts/check_v20x_fitbit_current_state_contract.py
```

### Explicit non-change surface

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
/fitbit/status, /fitbit/connect, and /fitbit/callback route shapes
Fitbit response-model fields
OAuth state, token exchange, refresh, token storage, sleep API, and normalization logic
Google Health behavior accepted in v2.0.0
real Fitbit/provider execution or private operator evidence
release ZIP, tag, GitHub Release, or v2.0.1 publication
```

### Current implementation contract

```text
- mock is the credential-free default.
- wearable_stub is the recommended deterministic wearable-shaped sample.
- fitbit_stub is a deprecated compatibility alias for wearable_stub behavior.
- fitbit is a retained legacy migration/reference provider.
- /fitbit/status connected=true means local credentials and token-like fields were detected; it does not prove live token validity or real sleep retrieval.
- /fitbit/connect ready=true means an authorization URL was prepared; it does not prove authorization, token exchange, connection, or sleep retrieval.
- Flutter presents the legacy connected state as local-token detection / unverified, not an unqualified connected or available state.
- Real Fitbit completion and configured operator acceptance remain v2.1.0 work.
```

### Completion requirements

```text
- The real / legacy / stub / unavailable / migration distinctions are documented from inspected source.
- Existing route and response-model compatibility is preserved.
- Backend tests remain credential-free, network-free, and independent from backend/local_data.
- Flutter tests verify conservative legacy status and authorization-URL wording.
- At M-7 acceptance, M-8 and M-9 remained PLANNED.
- Historical v2.0.0 checklist and release-note normalized content hashes remain unchanged.
- python -m compileall -q backend scripts passes.
- M-1 through M-7 checks pass.
- python -m pytest -q backend/tests passes.
- flutter test passes from app/.
- The operator reviews the diff and approves the small commit.
```

M-7 was accepted on 2026-07-23 after compileall, M-1 through M-7 checks, 38 backend pytest tests, 43 Flutter tests, diff review, and operator approval passed. Source-tree checks and mock-safe tests still do not count as configured real Fitbit execution evidence, and M-7 did not release v2.0.1.

## M-8 — Add aggregate maintenance readiness

Status: COMPLETED / ACCEPTED
Commit title:

```text
test/docs: add v2.0.x aggregate maintenance readiness
```

### Purpose

```text
- Provide one credential-free current-main maintenance command.
- Aggregate the accepted M-1 through M-7 regression chain.
- Keep historical v2.0.0 release-evidence validators outside the normal maintenance aggregate.
- Define the conditions required before M-9 patch-release work may become CURRENT.
```

### Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v20x_maintenance_checklist.md
docs/v20x_maintenance_readiness.md
scripts/check_v20x_maintenance_readiness.py
scripts/check_v20x_maintenance_baseline.py
scripts/check_v20x_application_version_metadata.py
scripts/check_v20x_backend_mock_safe_regression.py
scripts/check_v20x_framework_fallback_voice_artifact_regression.py
scripts/check_v20x_temporary_lifecycle_limits.py
scripts/check_v20x_web_cors_origins.py
scripts/check_v20x_fitbit_current_state_contract.py
```

### Aggregate contract

```text
- The default aggregate runs compileall, the accepted M-7 terminal maintenance chain, and full backend pytest.
- The M-7 terminal chain reaches the accepted M-1 through M-6 checks.
- --with-flutter additionally runs flutter test from app/.
- The portable default does not require Flutter, but Flutter remains required for operator acceptance.
- Historical normalized-content hashes remain protected.
- backend/local_data must not be created or modified.
- No real provider, network, credential, private evidence, release ZIP, tag, or GitHub Release is required.
```

### Historical release separation

```text
- v2.0.0 Web evidence, screenshot, fixed-ZIP, final-release, and publication validators remain historical.
- The M-8 aggregate does not invoke those validators.
- M-8 does not reinterpret historical evidence as current-main runtime regression coverage.
- docs/DRC_v200_goal_checklist_small_commit.md and release_notes/v2.0.0.md remain unchanged.
```

### M-9 entry conditions

```text
- M-1 through M-8 must be COMPLETED / ACCEPTED.
- The final M-8 aggregate must pass from the intended committed Public source state.
- backend pytest and Flutter test must pass without real-provider execution.
- The accepted patch scope must be frozen and unrelated changes excluded.
- One fixed ZIP must be built from the final committed Public source and that same ZIP must be verified without rebuilding.
- The DRC_v2.0.0 tag and release asset must remain untouched.
- At M-8 acceptance, M-9 remained PLANNED.
```

### Completion requirements

```text
- docs/v20x_maintenance_readiness.md documents the aggregate and M-9 entry contract.
- scripts/check_v20x_maintenance_readiness.py is credential-free and mock-safe.
- python -m compileall -q backend scripts passes.
- python scripts/check_v20x_maintenance_readiness.py passes.
- python scripts/check_v20x_maintenance_readiness.py --with-flutter passes in the operator environment.
- backend pytest and Flutter test pass.
- Historical v2.0.0 normalized-content hashes remain unchanged.
- M-9 remains PLANNED.
- The operator reviews the diff and approves the small commit.
```

M-8 was accepted on 2026-07-23 after compileall, the aggregate gate with Flutter, 38 backend pytest tests, 43 Flutter tests, historical-record and backend/local_data protection checks, diff review, and operator approval passed. M-8 did not build a release ZIP, create a tag or GitHub Release, or release v2.0.1. M-9 remains PLANNED.

## M-9 — Patch release

Status: PLANNED

```text
- Freeze accepted patch scope.
- Build one fixed ZIP from final committed Public source.
- Verify the same ZIP and publish a new patch tag and GitHub Release.
- Do not replace DRC_v2.0.0 assets.
```

---

# Future-version boundary

v2.1.0 is planned for the real wearable daily loop led by Fitbit completion. v3.0.0 is reserved for realtime multimodal work such as real STT, microphone capture, interruption/cancel, and Live2D/VTS execution. These are not v2.0.x completion requirements.
