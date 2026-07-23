# Daily Rhythm Companion

Daily Rhythm Companion is a lightweight daily rhythm companion and a public demo application for **AI Character Framework**.

AI Character Framework repository: [https://github.com/murayan1982/ai-character-framework.git](https://github.com/murayan1982/ai-character-framework.git)

Current released version: v2.0.1 (**RELEASED**)
Immutable capability baseline: v2.0.0
Completed maintenance line: v2.0.x (**COMPLETED / ACCEPTED**)
Current development line: v2.1.0 (**W-1/W-2 COMPLETED / ACCEPTED; W-3 CURRENT / NOT_COMPLETED**)
Current small commit: W-3 — Fitbit real sleep normalization and API regression tests
Strategic target: v3.0.0

## Current release and development status

Daily Rhythm Companion v2.0.1 is the current Public patch release. Daily Rhythm Companion v2.0.0 remains the immutable capability and historical release baseline.

Current v2.0.1 patch release:

```text
Public repository: murayan1982/daily-rhythm-companion-public
Release / annotated tag: DRC_v2.0.1
Release status: RELEASED
Source HEAD: 3e4c9f6186ef7195045a445307e14f412924bc26
Fixed release ZIP: DailyRhythmCompanion_20260723_143447.zip
Fixed release ZIP size: 1493130 bytes
Fixed release ZIP SHA-256: ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1
Same-ZIP verification without rebuilding: completed
Post-publication SHA-256 re-verification: completed
```

Immutable v2.0.0 baseline record:

```text
Public repository: murayan1982/daily-rhythm-companion-public
Release / annotated tag: DRC_v2.0.0
Release status: RELEASED
Fixed release ZIP: DailyRhythmCompanion_20260722_180426.zip
Fixed release ZIP SHA-256: b32c7b8a64842480898fcc86ca7838625efb712f1429ab9fe7b33a4001ddc0c1
Post-publication SHA-256 re-verification: completed
```

Post-release rules:

```text
- Do not rewrite the DRC_v2.0.0 tag.
- Do not replace the published v2.0.0 release asset.
- Do not modify the released v2.0.0 source snapshot.
- Apply post-release changes through a new commit and a new version.
- Keep the v2.0.0 checklist and release notes as historical evidence.
```

The completed v2.0.0 records remain:

- [`docs/DRC_v200_goal_checklist_small_commit.md`](docs/DRC_v200_goal_checklist_small_commit.md)
- [`release_notes/v2.0.0.md`](release_notes/v2.0.0.md)
- GitHub Release and annotated tag `DRC_v2.0.0`

They are historical release records and are not the active task list for post-release work.

The authoritative v2.1.0 source of truth is:

- [`docs/DRC_v210_goal_checklist_small_commit.md`](docs/DRC_v210_goal_checklist_small_commit.md)
- [`roadmap.md`](roadmap.md)
- [`tasklist.md`](tasklist.md)

W-1 established and accepted this source of truth after source-tree verification, diff review, and operator approval passed.

The completed v2.0.x maintenance source of truth remains available as historical accepted work:

- [`docs/DRC_v20x_maintenance_checklist.md`](docs/DRC_v20x_maintenance_checklist.md)

M-1 through M-9 are complete and accepted. v2.0.1 was released from the accepted M-1 through M-8 scope after the final committed-source gate, one-time fixed-ZIP build, same-artifact verification, explicit final approval, annotated tag publication, GitHub Release publication, and post-publication SHA-256 re-verification all passed.

W-1 is completed and accepted. It inventoried the existing Fitbit OAuth, token, refresh, sleep API, normalization, provider, and Flutter presentation boundaries without changing runtime behavior or claiming configured real Fitbit success.

Accepted W-1 verification on 2026-07-23:

```text
compileall: passed
W-1 source-tree check: passed
backend pytest: 38 passed
Flutter test: 43 passed
runtime / Flutter / existing tests / release records changed: false
real operator execution: false
```

Run the accepted W-1 source-tree check with:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

W-2 is completed and accepted. It added conservative `connection_state` / `verified` response fields, deterministic local token-expiry classification, one-time OAuth state consumption, fake-HTTP refresh tests, and old/new Flutter response parsing. The existing `connected/provider/message` fields remain backward compatible. Normal status inspection performs no external HTTP and does not refresh a token.

The detailed W-2 contract is [`docs/v210_fitbit_token_status_reconnect.md`](docs/v210_fitbit_token_status_reconnect.md).

Run the accepted W-2 checks with:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

Accepted W-2 verification on 2026-07-23:

```text
compileall: passed
W-1/W-2 source-tree checks: passed
v2.0.x compatibility and historical guards: passed
backend pytest: 57 passed
Flutter test: 50 passed
real operator execution: false
release records changed: false
```

W-3 is CURRENT / NOT_COMPLETED with implementation ready for verification. The backend now classifies allow-listed Fitbit sleep API failures, requires usable normalized sleep duration, maps real-provider fields into `SleepSummary`, and includes deterministic fake-HTTP/API regression tests. The detailed contract is [`docs/v210_fitbit_real_sleep_normalization.md`](docs/v210_fitbit_real_sleep_normalization.md). Real OAuth, live token exchange/refresh, configured permission/scope evidence, real Fitbit sleep retrieval, provider-selection UI, and smartphone Web acceptance remain W-4/W-5 work and are not completed by W-3 source presence or mock-safe success.

Run the current W-3 verification with:

```powershell
python -m compileall -q backend scripts
python scripts\check_v210_fitbit_current_behavior_inventory.py
python scripts\check_v210_fitbit_token_status_reconnect.py
python scripts\check_v210_fitbit_real_sleep_normalization.py
python scripts\check_v20x_fitbit_current_state_contract.py
python scripts\check_v20x_maintenance_baseline.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

M-7 accepted contract:

```text
mock: credential-free default
wearable_stub: recommended deterministic wearable-shaped sample
fitbit_stub: deprecated compatibility alias
fitbit: retained legacy migration/reference provider
/fitbit/status connected=true: local credentials and token-like fields detected, not live validation
/fitbit/connect ready=true: authorization URL prepared, not connection success
real Fitbit operator acceptance: deferred to v2.1.0
M-7 acceptance: compileall, M-1 through M-7 checks, 38 backend pytest tests, 43 Flutter tests, diff review, and operator approval passed
```

See [`docs/v20x_fitbit_current_state_contract.md`](docs/v20x_fitbit_current_state_contract.md).

M-8 accepted contract:

```text
Default aggregate: compileall + accepted M-7 terminal chain + full backend pytest
Full local gate: add --with-flutter to run Flutter test from app/
Historical release validators: retained but not invoked by the current-main aggregate
Patch release: M-9 remains PLANNED after M-8 acceptance
Release artifacts: not created by M-8
```

See [`docs/v20x_maintenance_readiness.md`](docs/v20x_maintenance_readiness.md).

M-9 accepted release record:

```text
Accepted scope: M-1 through M-8 only
Final source gate: passed on source HEAD 3e4c9f6186ef7195045a445307e14f412924bc26
Fixed artifact: DailyRhythmCompanion_20260723_143447.zip, built once from detached committed HEAD
Fixed artifact size: 1493130 bytes
Fixed artifact SHA-256: ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1
Verification: same ZIP inspected and tested without rebuilding
Release: annotated tag DRC_v2.0.1 and GitHub Release published after explicit final approval
Post-publication SHA-256 re-verification: completed
Current state: COMPLETED / ACCEPTED / RELEASED
```

See [`docs/v20x_patch_release.md`](docs/v20x_patch_release.md), [`docs/v201_patch_release_record.md`](docs/v201_patch_release_record.md), and [`release_notes/v2.0.1.md`](release_notes/v2.0.1.md).

M-6 accepted contract:

```text
Local-demo default: WEB_CORS_ORIGINS=* preserves the existing all-origin behavior
Explicit restriction: comma- or space-separated origins are passed to FastAPI CORSMiddleware
Credentials: remain disabled
Compatibility: existing routes, response models, Flutter behavior, and v2.0.0 history remain unchanged
Excluded from M-6: production hosting claims, authentication, proxy policy, TLS, provider execution, and release work
```

Install and run the accepted v2.0.x maintenance checks with:

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

# Full local M-8 gate, including Flutter
python scripts\check_v20x_maintenance_readiness.py --with-flutter

# M-9 post-release record gate
python scripts\check_v20x_patch_release.py

# Strict current-main / annotated-tag gate after the record commit is pushed
python scripts\check_v20x_patch_release.py --source-tree --with-flutter

# Re-verify the published fixed ZIP as-is; never rebuild it
python scripts\check_v20x_patch_release.py `
  --release-zip "release\DailyRhythmCompanion_20260723_143447.zip" `
  --expected-sha256 "ac24378da3a0dcd7227591f8cbaa8bca010dda219a404c3723ae2f7d2716c1d1" `
  --expected-source-head "3e4c9f6186ef7195045a445307e14f412924bc26" `
  --with-flutter
```

The historical v2.0.0 release validators remain available for the tagged release surface, but they are not the primary current-main maintenance suite.

The v1.0 direction is:

```txt
A user can try the app from their own smartphone browser
+
The repository can be published as an understandable AI Character Framework demo app
```

Daily Rhythm Companion is not meant to be a production health app at v1.0. It is a realistic demo app that shows how a Flutter UI and FastAPI backend can pass app context into AI Character Framework and present the result through text, optional voice, optional motion, and saved daily records.

## Required demo-app requirements

Daily Rhythm Companion is a **public demo application for AI Character Framework**, not just a standalone daily rhythm app.

Target framework repository:

```text
https://github.com/murayan1982/ai-character-framework.git
```

The project requirements are:

```text
- This repository is developed as a public repository because it is a demo app for AI Character Framework.
- The app must be demonstrable from the developer's own smartphone through Web access.
- The smartphone Web UI must call the actual Daily Rhythm Companion backend API.
- The backend must call the configured AI Character Framework integration path when configured.
- FW4.0.0-era capabilities must be verifiable through this app:
  - LLM
  - STT / voice input
  - TTS / voice output
  - Live2D / VTS motion
- These capabilities must be included in verification requirements.
- API-only checks are not enough for the final demo requirement; Web UI operation and visible UI results must also be checked.
- mock-safe mode remains available for public/default local development.
- skipped / unavailable / fallback states must be visible and must not be counted as configured real execution success.
- General consumer App Store / Google Play release work is deferred to v2.0.0 or later.
```

Configured real API verification may use already-obtained credentials for:

```text
- LLM: OpenAI, Gemini, Grok
- TTS: ElevenLabs
- Health data: Google Health API
```

Do not commit actual API keys, OAuth secrets, refresh tokens, access tokens, raw provider payloads, or local credential files.

## What the app demonstrates

```txt
Sleep / mood / daily context
→ Daily Rhythm Companion backend
→ AI Character Framework or mock engine
→ character response / optional voice / optional motion
→ Flutter app UI
→ DailyRecord history
```

The v1.0 demo should show that:

- The backend can run safely in mock-safe mode without external credentials.
- The app can display sleep/context, mood, character selection, advice, save actions, and History.
- Framework mode can route advice generation through AI Character Framework when configured.
- Voice input, voice output / TTS, and Live2D / VTS motion are visible as optional demo capabilities.
- Optional capabilities have clear fallback states when unavailable.
- Google Health real API access remains disabled by default but has a documented explicit opt-in verification path.
- The repository avoids committing secrets, tokens, raw provider payloads, local data, caches, and build artifacts.

## v1.0 user-facing demo goal

The v1.0 user-facing goal is to run a smartphone Web demo:

```txt
Open the Web UI from a smartphone browser
→ confirm backend connectivity
→ see sleep/context
→ select mood
→ select character
→ generate advice
→ save a DailyRecord
→ review History
→ inspect capability status
```

The smartphone Web demo is primarily for local/demo use. It is not the same as an App Store / Google Play release or a production hosted service.

See:

- [Post-v2.0.0 release baseline](docs/post_v200_release_baseline.md)
- [v2.0.x application version metadata](docs/v20x_application_version_metadata.md)
- [v2.0.x Web CORS origin configuration](docs/v20x_web_cors_origins.md)
- [v2.0.x maintenance checklist](docs/DRC_v20x_maintenance_checklist.md)
- [Public / Private development policy](docs/public_private_development_policy.md)
- [Local quickstart](docs/quickstart_local.md)
- [Smartphone Web quickstart](docs/quickstart_smartphone_web.md)
- [Framework demo setup](docs/framework_demo_setup.md)
- [Framework source labels](docs/framework_source_labels.md)
- [Character experience inventory](docs/character_experience_inventory.md)
- [Character advice tone matrix](docs/character_advice_tone_matrix.md)
- [Character selection UX copy](docs/character_selection_ux_copy.md)
- [Character framework mapping](docs/character_framework_mapping.md)
- [Personalization profile boundary](docs/personalization_profile_boundary.md)
- [App runtime verification](docs/app_runtime_verification.md)
- [Report-to-advice handoff inventory](docs/report_advice_handoff_inventory.md)
- [Report handoff copy rules](docs/report_advice_handoff_copy_rules.md)
- [ReportHandoffContext backend boundary](docs/report_handoff_context_backend.md)
- [Rhythm report contract](docs/rhythm_report_contract.md)
- [Rhythm report Flutter UI contract](docs/rhythm_report_flutter_ui_contract.md)
- [Rhythm report explanation inventory](docs/rhythm_report_explanation_inventory.md)
- [Rhythm report user-facing copy contract](docs/rhythm_report_user_facing_copy.md)
- [Framework-backed advice operator checklist](docs/framework_advice_operator_checklist.md)
- [v2.0.0 pre-release requirements](docs/v2_prerelease_requirements.md)
- [v2.0.0 goal checklist source of truth](docs/DRC_v200_goal_checklist_small_commit.md)
- [v2.0.0 Public distribution readiness](docs/v200_public_distribution_readiness.md)
- [v2.0.0 Day52 real LLM Web answer evidence](docs/v200_real_llm_web_answer_evidence.md)
- [v2.0.0 Day64 real LLM Web answer execution evidence](docs/v200_real_llm_web_answer_execution_evidence.md)
- [v2.0.0 Day53 real TTS provider gate](docs/v200_real_tts_provider_gate.md)
- [v2.0.0 Day54 real TTS Web audio output evidence](docs/v200_real_tts_web_audio_output_evidence.md)
- [v2.0.0 Day65 real TTS Web audio output execution evidence](docs/v200_real_tts_web_audio_execution_evidence.md)
- [v2.0.0 Day55 real Google Health sleep data evidence](docs/v200_real_google_health_sleep_data_evidence.md)
- [v2.0.0 Day66 real Google Health sleep data execution evidence](docs/v200_real_google_health_sleep_data_execution_evidence.md)
- [v2.0.0 Day56 Web image display evidence](docs/v200_web_image_display_evidence.md)
- [v2.0.0 Day67 image asset generation and repository-safe intake](docs/v200_image_asset_generation_intake_evidence.md)
- [v2.0.0 Day68 Web image display execution evidence](docs/v200_web_image_display_execution_evidence.md)
- [v2.0.0 Day69 public repo readiness final sweep](docs/v200_public_repo_final_sweep.md)
- [v2.0.0 Day70 final prerelease aggregate gate](docs/v200_final_prerelease_aggregate_gate.md)
- [v2.0.0 Day73 accepted Web screenshot evidence enforcement](docs/v200_accepted_web_screenshot_evidence_enforcement.md)
- [v2.0.0 Day76 real LLM Web screenshot evidence capture](docs/v200_real_llm_web_screenshot_evidence_capture.md)
- [v2.0.0 Day77 real TTS Web audio screenshot evidence capture](docs/v200_real_tts_web_audio_screenshot_evidence_capture.md)
- [v2.0.0 Day78 real Google Health Web sleep screenshot evidence capture](docs/v200_real_google_health_web_sleep_screenshot_evidence_capture.md)
- [v2.0.0 Day79 Web image display screenshot evidence capture](docs/v200_web_image_display_screenshot_evidence_capture.md)
- [v2.0.0 Day80 accepted Web evidence manifest aggregate](docs/v200_accepted_web_evidence_manifest_aggregate.md)
- [v2.0.0 Day81 final release readiness with accepted Web evidence](docs/v200_final_release_readiness_with_web_evidence.md)

- [v2.0.0 Day82 fixed release zip verification with accepted Web evidence](docs/v200_fixed_release_zip_with_web_evidence_verification.md)
- [v2.0.0 Day83 final release readiness fixed-zip gate with accepted Web evidence](docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md)
- [v2.0.0 immutable final release artifact record](docs/v200_final_release_artifact_record.md)
- [Release notes](release_notes/)
- [Google Health real API opt-in](docs/google_health_real_api_opt_in.md)
- [Troubleshooting](docs/troubleshooting.md)

## v1.0 public repository goal

The v1.0 public repository readiness goal is that the repository should be understandable to someone seeing it as an AI Character Framework demo app.

Public repository readiness means:

- README and public docs explain what the app is and what it is not.
- A new developer can run mock-safe local mode from documented steps.
- A demo operator can understand how to try the smartphone Web demo.
- Framework mode, optional voice/TTS/motion, and Google Health real API opt-in are documented.
- Scripts and checks are grouped by purpose.
- Obsolete one-off docs/scripts are removed, merged, or archived only after inventory.
- Sensitive files and local artifacts are excluded from the repository and release package.

See the v1.0 planning docs under `docs/internal/` for the Day-by-Day cleanup direction.

## Quickstart: mock-safe local mode

Normal development starts in mock-safe mode.

```env
CONVERSATION_ENGINE=mock
SLEEP_PROVIDER=mock
```

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env -Force
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd app
flutter pub get
flutter test
flutter run
```

For more detail, use [docs/quickstart_local.md](docs/quickstart_local.md).

## Smartphone Web demo

A smartphone cannot reach the backend through `127.0.0.1` on the development PC. For a smartphone Web demo, the backend and Flutter Web UI must be reachable through a phone-accessible host such as a LAN IP address or a tunnel URL.

Typical local demo shape:

```txt
PC backend:     http://<PC_LAN_IP>:8000
Flutter Web UI: http://<PC_LAN_IP>:8080
Smartphone:    same Wi-Fi network, opens the Flutter Web UI URL
```

Before calling the smartphone Web demo complete, confirm the effective Flutter backend API base URL points to the phone-accessible backend URL. If the app still uses the development default `http://127.0.0.1:8000`, Day5 should add or verify the required configuration path before final v1.0 release readiness.

See [docs/quickstart_smartphone_web.md](docs/quickstart_smartphone_web.md).

## Framework mode

Framework mode is optional and intended for configured local/demo environments.

Use the AI Character Framework repository above as the framework checkout source. In other words, this app is a demo app for `https://github.com/murayan1982/ai-character-framework.git`.

```env
CONVERSATION_ENGINE=framework
SLEEP_PROVIDER=mock
FRAMEWORK_ROOT=<path-to-ai-character-framework>
FRAMEWORK_PRESET=text_chat
FRAMEWORK_CHARACTER=default
FRAMEWORK_ADAPTER_MODE=local_import
```

Provider API keys are not required for mock-safe checks. Only enable real provider-backed FW/LLM validation intentionally in a configured environment.

For the full local checklist, see [docs/framework_local_setup.md](docs/framework_local_setup.md).

For the current DRC character_id to framework character mapping policy, see [docs/character_framework_mapping.md](docs/character_framework_mapping.md).

See [docs/framework_demo_setup.md](docs/framework_demo_setup.md).

## Google Health real API policy

Google Health real API access is guarded by default.

Keep these disabled unless intentionally verifying the real API path:

```env
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE=0
GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH=0
GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS=0
GOOGLE_HEALTH_REAL_API_OPT_IN=0
GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED=0
```

v1.0 requires a documented explicit opt-in path for configured local/demo verification. It does not require polished real-user onboarding or store-release-grade OAuth UX.

See [docs/google_health_real_api_opt_in.md](docs/google_health_real_api_opt_in.md).

## Public safety rules

Do not commit or publish:

```txt
.env
access tokens
refresh tokens
client secrets
Authorization headers
raw provider payloads
local token files
local_data/
cache directories
build outputs
machine-specific absolute paths
```

The app should expose capability state and safe user guidance, not secret values or raw provider data.

## Release notes

Release notes are kept under `release_notes/` so version records do not accumulate at the repository root.

Current release-note records:

- [v2.0.0](release_notes/v2.0.0.md) — Public release content; publication remains gated
- [v1.10.0](release_notes/v1.10.0.md)
- [v1.9.0](release_notes/v1.9.0.md)
- [v1.8.0](release_notes/v1.8.0.md)
- [v1.7.0](release_notes/v1.7.0.md)
- [v1.6.0](release_notes/v1.6.0.md)
- [v1.5.0](release_notes/v1.5.0.md)
- [v1.4.0](release_notes/v1.4.0.md)
- [v1.3.0](release_notes/v1.3.0.md)
- [v1.2.0](release_notes/v1.2.0.md)
- [v1.1.0](release_notes/v1.1.0.md)
- [v1.0.0](release_notes/v1.0.0.md)


## v1.9.0 Day10 Flutter post-advice chat UI

Day10 adds the Flutter Web UI path for the mock-safe post-advice chat API.

Implemented app flow:

```text
advice result
→ Post-advice Chat
→ 少し話す / 今日はここまで
→ mock-safe character chat session
→ one or more chat messages
```

Day10 keeps the chat path provider-free:

```text
- no OpenAI/Gemini/Grok call
- no AI Character Framework call
- no STT/TTS/Live2D execution
- backend source remains engine: mock / mode: post_advice_chat
```

The UI now shows:

```text
- Post-advice Chat section after advice
- 少し話す button
- 今日はここまで button
- Chat session ID
- Chat source
- user and character messages
- message input and send button
```

Day10 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day10.py
cd app
flutter test
```


## v1.9.0 Day9 mock-safe post-advice chat API

Day9 implements the first mock-safe backend boundary for the restored post-advice chat continuation flow.

Implemented backend flow:

```text
advice result context
→ POST /chat/sessions
→ mock-safe ChatSession
→ POST /chat/sessions/{session_id}/messages
→ mock-safe character reply
→ GET /chat/sessions/{session_id}
```

New backend boundaries:

```text
PostAdviceChatContext
ChatSession
ChatMessage
ChatSource

POST /chat/sessions
GET  /chat/sessions/{session_id}
POST /chat/sessions/{session_id}/messages
```

Day9 remains provider-free. It does not call OpenAI, Gemini, Grok, AI Character Framework, ElevenLabs, Google Health, STT, TTS, or Live2D/VTS.

Day9 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day9.py
```


## v1.9.0 Day41 TTS / voice output smartphone Web boundary evidence record

Day41 records the guarded TTS / voice output smartphone Web boundary evidence as a v1.9.0 public-safe record.

Day41 adds:

```text
backend/app/services/framework_voice_output_smartphone_web_boundary_evidence_record.py
scripts/smoke_framework_voice_output_smartphone_web_boundary_evidence_record.py
docs/framework_voice_output_smartphone_web_boundary_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day41.md
scripts/check_v190_smartphone_web_fw_demo_day41.py
```

The record shape is:

```text
v190_voice_output_smartphone_web_boundary_record_status: recorded
v190_voice_output_smartphone_web_boundary_record_from_evidence_status: verified
v190_voice_output_smartphone_web_boundary_record_source_mode: voice_output_demo_boundary
v190_voice_output_smartphone_web_boundary_record_backend_status_ok: True
v190_voice_output_smartphone_web_boundary_record_api_base_url_visible: True
v190_voice_output_smartphone_web_boundary_record_request_sent: True
v190_voice_output_smartphone_web_boundary_record_response_visible: True
v190_voice_output_smartphone_web_boundary_record_synthesis_blocked: True
v190_voice_output_smartphone_web_boundary_record_audio_generation_blocked: True
v190_voice_output_smartphone_web_boundary_record_audio_playback_not_used: True
v190_voice_output_smartphone_web_boundary_record_generated_audio_absent: True
v190_voice_output_smartphone_web_boundary_record_audio_url_hidden_or_absent: True
v190_voice_output_smartphone_web_boundary_record_provider_call_not_made: True
v190_voice_output_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-voice-output-boundary-evidence
```

Day41 does not call configured TTS runtime execution. It does not start Flutter, open a browser, call the backend, import AI Character Framework audio modules, create sessions, call `ask`, call `ask_stream`, synthesize audio, generate audio files, play audio, call TTS providers, connect to Live2D/VTS, call VTube Studio, or dispatch motion.

Day41 check command:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day41.py
```

## v1.9.0 Day40 TTS / voice output smartphone Web boundary evidence

Day40 records the guarded TTS / voice output smartphone Web boundary evidence after the FW4.0.0 coverage checkpoint moved the next focus to TTS / voice output.

Day40 adds:

```text
backend/app/services/framework_voice_output_smartphone_web_boundary_evidence.py
scripts/smoke_framework_voice_output_smartphone_web_boundary_evidence.py
docs/framework_voice_output_smartphone_web_boundary_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day40.md
scripts/check_v190_smartphone_web_fw_demo_day40.py
```

The source-tree evidence shape is:

```text
voice_output_smartphone_web_boundary_evidence_status: verified
voice_output_smartphone_web_boundary_evidence_mode: source-tree-boundary
voice_output_smartphone_web_boundary_source_mode: voice_output_demo_boundary
voice_output_smartphone_web_boundary_status_route_present: True
voice_output_smartphone_web_boundary_request_route_present: True
voice_output_smartphone_web_boundary_api_client_route_present: True
voice_output_smartphone_web_boundary_flutter_section_visible: True
voice_output_smartphone_web_boundary_flutter_button_visible: True
voice_output_smartphone_web_boundary_synthesis_blocked: True
voice_output_smartphone_web_boundary_audio_generation_blocked: True
voice_output_smartphone_web_boundary_audio_playback_not_used: True
voice_output_smartphone_web_boundary_generated_audio_absent: True
voice_output_smartphone_web_boundary_audio_url_hidden_or_absent: True
voice_output_smartphone_web_boundary_provider_call_not_made: True
voice_output_smartphone_web_boundary_next_step: record-manual-smartphone-web-voice-output-boundary-evidence
```

Day40 source-tree mode does not call configured TTS runtime execution. It does not start Flutter, open a browser, call the backend, import AI Character Framework audio modules, create sessions, call `ask`, call `ask_stream`, synthesize audio, generate audio files, play audio, call TTS providers, connect to Live2D/VTS, call VTube Studio, or dispatch motion.

Day40 check command:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day40.py
```

## v1.9.0 Day39 FW4.0.0 capability coverage after voice input evidence

Day39 updates the FW4.0.0 coverage checkpoint after the voice input smartphone Web boundary record.

Day39 adds:

```text
backend/app/services/framework_fw40_capability_coverage_after_voice_input.py
scripts/smoke_framework_fw40_capability_coverage_after_voice_input.py
docs/framework_fw40_capability_coverage_after_voice_input.md
docs/internal/v190_smartphone_web_fw_demo_day39.md
scripts/check_v190_smartphone_web_fw_demo_day39.py
```

Expected public-safe coverage markers:

```text
v190_fw40_capability_coverage_after_voice_input_status: text-chat-and-voice-input-boundary-evidence-complete-remaining-boundaries-pending
v190_fw40_capability_coverage_after_voice_input_llm_text_chat_status: completed
v190_fw40_capability_coverage_after_voice_input_stt_voice_input_status: boundary-evidence-recorded
v190_fw40_capability_coverage_after_voice_input_tts_voice_output_status: boundary-ready
v190_fw40_capability_coverage_after_voice_input_live2d_vts_motion_status: boundary-ready
v190_fw40_capability_coverage_after_voice_input_next_focus: tts_voice_output
```

Day39 source-tree mode does not call configured STT runtime execution. It does not start Flutter, open a browser, call the backend, import AI Character Framework runtime modules, create sessions, call `ask`, call `ask_stream`, touch microphones, read or upload audio, call STT providers, generate audio, call TTS providers, connect to Live2D/VTS, call VTube Studio, or dispatch motion.

Day39 check command:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day39.py
```

## v1.9.0 Day38 STT / voice input smartphone Web boundary evidence record

Day38 records the guarded STT / voice input smartphone Web boundary evidence as a v1.9.0 public-safe checkpoint.

Day38 adds:

```text
backend/app/services/framework_voice_input_smartphone_web_boundary_evidence_record.py
scripts/smoke_framework_voice_input_smartphone_web_boundary_evidence_record.py
docs/framework_voice_input_smartphone_web_boundary_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day38.md
scripts/check_v190_smartphone_web_fw_demo_day38.py
```

Expected public-safe record markers:

```text
v190_voice_input_smartphone_web_boundary_record_status: recorded
v190_voice_input_smartphone_web_boundary_record_from_evidence_status: verified
v190_voice_input_smartphone_web_boundary_record_source_mode: voice_input_demo_boundary
v190_voice_input_smartphone_web_boundary_record_request_sent: True
v190_voice_input_smartphone_web_boundary_record_response_visible: True
v190_voice_input_smartphone_web_boundary_record_audio_processing_blocked: True
v190_voice_input_smartphone_web_boundary_record_raw_audio_not_uploaded: True
v190_voice_input_smartphone_web_boundary_record_transcript_body_hidden_or_absent: True
```

Day38 source-tree mode does not start Flutter, open a browser, call the backend, import AI Character Framework voice modules, create realtime voice sessions, touch microphones, read local audio files, upload audio, call STT providers, or persist transcript bodies.

Manual evidence can be recorded after an operator checks the smartphone Web UI:

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

Day38 check command:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day38.py
```

## v1.9.0 Day37 STT / voice input smartphone Web boundary evidence

Day37 records the guarded STT / voice input smartphone Web boundary evidence after the FW4.0.0 LLM/text-chat smartphone Web proof was completed.

Day37 adds:

```text
backend/app/services/framework_voice_input_smartphone_web_boundary_evidence.py
scripts/smoke_framework_voice_input_smartphone_web_boundary_evidence.py
docs/framework_voice_input_smartphone_web_boundary_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day37.md
scripts/check_v190_smartphone_web_fw_demo_day37.py
```

The source-tree evidence shape is:

```text
voice_input_smartphone_web_boundary_evidence_status: verified
voice_input_smartphone_web_boundary_evidence_mode: source-tree-boundary
voice_input_smartphone_web_boundary_source_mode: voice_input_demo_boundary
voice_input_smartphone_web_boundary_status_route_present: True
voice_input_smartphone_web_boundary_request_route_present: True
voice_input_smartphone_web_boundary_api_client_route_present: True
voice_input_smartphone_web_boundary_flutter_section_visible: True
voice_input_smartphone_web_boundary_flutter_button_visible: True
voice_input_smartphone_web_boundary_request_contract_metadata_only: True
voice_input_smartphone_web_boundary_audio_processing_blocked: True
voice_input_smartphone_web_boundary_microphone_not_used: True
voice_input_smartphone_web_boundary_raw_audio_not_uploaded: True
voice_input_smartphone_web_boundary_transcript_body_hidden_or_absent: True
voice_input_smartphone_web_boundary_public_safe_evidence_only: True
```

Day37 source-tree mode does not start Flutter, open a browser, import AI Character Framework voice modules, create realtime voice sessions, touch microphones, read local audio files, upload audio, call STT providers, or persist transcript bodies.

Manual smartphone Web boundary evidence can be recorded with boolean flags only using `scripts/smoke_framework_voice_input_smartphone_web_boundary_evidence.py --record-manual-ui-evidence`.

Day37 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day37.py
```


## v1.9.0 Day36 FW4.0.0 capability coverage checkpoint

Day36 records the FW4.0.0 capability coverage checkpoint after the LLM/text-chat smartphone Web proof chain was completed.

Day36 adds:

```text
backend/app/services/framework_fw40_capability_coverage_checkpoint.py
scripts/smoke_framework_fw40_capability_coverage_checkpoint.py
docs/framework_fw40_capability_coverage_checkpoint.md
docs/internal/v190_smartphone_web_fw_demo_day36.md
scripts/check_v190_smartphone_web_fw_demo_day36.py
```

The checkpoint shape is:

```text
v190_fw40_capability_coverage_status: text-chat-complete-boundary-capabilities-pending
v190_fw40_capability_llm_text_chat_status: completed
v190_fw40_capability_stt_voice_input_status: boundary-ready
v190_fw40_capability_tts_voice_output_status: boundary-ready
v190_fw40_capability_live2d_vts_motion_status: boundary-ready
v190_fw40_capability_completed_count: 1
v190_fw40_capability_boundary_ready_count: 3
v190_fw40_capability_pending_configured_evidence_count: 3
v190_fw40_capability_public_safe_evidence_only: True
v190_fw40_capability_next_focus: stt_voice_input
```

Meaning: LLM/text-chat is complete for the v1.9.0 smartphone Web public demo proof point. STT / voice input, TTS / voice output, and Live2D / VTS motion remain guarded boundary capabilities with configured smartphone Web evidence still pending.

Day36 source-tree mode does not start Flutter, open a browser, import AI Character Framework, create sessions, call `ask`, call `ask_stream`, call provider APIs, touch microphones, upload audio, generate audio, connect to VTube Studio, or dispatch Live2D/VTS motion.

Day36 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day36.py
```


## v1.9.0 Day35 FW text-chat smartphone Web completion evidence

Day35 records the FW4.0.0 LLM/text-chat smartphone Web proof chain as complete for v1.9.0.

The completed chain is:

```text
Day28: session creation evidence verified
Day31: one bounded live text-chat message evidence verified
Day32: DRC post-advice chat adapter/API routed the live FW reply
Day33: smartphone Web UI displayed the live FW reply through the actual backend API
Day34: smartphone Web UI evidence record created
```

Day35 adds:

```text
backend/app/services/framework_text_chat_v190_completion_evidence.py
scripts/smoke_framework_text_chat_v190_completion_evidence.py
docs/framework_text_chat_v190_completion_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day35.md
scripts/check_v190_smartphone_web_fw_demo_day35.py
```

The v1.9.0 completion evidence shape is:

```text
v190_fw40_text_chat_smartphone_web_completion_status: completed
v190_fw40_text_chat_smartphone_web_source_mode: framework_text_chat_live_message
v190_fw40_text_chat_session_creation_verified: True
v190_fw40_text_chat_live_message_verified: True
v190_fw40_text_chat_drc_adapter_live_reply_verified: True
v190_fw40_text_chat_smartphone_web_ui_live_reply_recorded: True
v190_fw40_text_chat_actual_backend_api_used: True
v190_fw40_text_chat_response_non_empty: True
v190_fw40_text_chat_prompt_body_hidden_in_evidence: True
v190_fw40_text_chat_response_body_hidden_in_evidence: True
v190_fw40_text_chat_smartphone_web_next_step: prepare-v190-release-readiness-checkpoint
```

Day35 source-tree mode does not start Flutter, open a browser, import AI Character Framework, create sessions, call `ask`, call `ask_stream`, or call provider APIs. Prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, raw LAN IPs, and raw provider error payloads remain excluded.

Day35 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day35.py
```


## v1.9.0 Day34 smartphone Web UI live FW reply evidence record

Day34 records the verified smartphone Web UI live FW4.0.0 text-chat reply as a v1.9.0 public-safe proof point.

Day33 manual smartphone Web UI evidence confirmed:

```text
smartphone_web_ui_live_reply_evidence_status: verified
smartphone_web_ui_live_reply_source_mode: framework_text_chat_live_message
smartphone_web_ui_response_non_empty: True
smartphone_web_ui_body_hidden_in_evidence: True
smartphone_web_ui_next_step: record-v190-live-text-chat-smartphone-web-ui-evidence
```

Day34 adds:

```text
backend/app/services/framework_text_chat_smartphone_web_ui_evidence_record.py
scripts/smoke_framework_text_chat_smartphone_web_ui_evidence_record.py
docs/framework_text_chat_smartphone_web_ui_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day34.md
scripts/check_v190_smartphone_web_fw_demo_day34.py
```

The v1.9.0 record shape is:

```text
v190_smartphone_web_ui_live_reply_record_status: recorded
v190_smartphone_web_ui_live_reply_record_from_evidence_status: verified
v190_smartphone_web_ui_live_reply_record_source_mode: framework_text_chat_live_message
v190_smartphone_web_ui_backend_status_ok: True
v190_smartphone_web_ui_response_non_empty: True
v190_smartphone_web_ui_body_hidden_in_evidence: True
v190_smartphone_web_ui_live_reply_record_next_step: prepare-v190-fw40-demo-evidence-summary
```

Day34 source-tree mode does not start Flutter, open a browser, import AI Character Framework, create sessions, call `ask`, call `ask_stream`, or call provider APIs. It records only public-safe booleans and labels; prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, and raw LAN IPs remain excluded.

Day34 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day34.py
```


## v1.9.0 Day33 smartphone Web UI live FW reply evidence

Day33 prepares the public-safe evidence path for verifying the Day32 live FW4.0.0 text-chat reply from the smartphone Web UI through the actual DRC backend API.

Day32 confirmed:

```text
drc_adapter_live_reply_status: responded
drc_adapter_live_reply_source_mode: framework_text_chat_live_message
drc_chat_api_live_reply_body_hidden: True
drc_adapter_live_reply_next_step: verify-live-fw-response-through-smartphone-web-ui
```

Day33 adds:

```text
backend/app/services/framework_text_chat_smartphone_web_ui_evidence.py
scripts/smoke_framework_text_chat_smartphone_web_ui_evidence.py
docs/framework_text_chat_smartphone_web_ui_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day33.md
scripts/check_v190_smartphone_web_fw_demo_day33.py
```

The source-tree smoke renders a synthetic public-safe evidence shape. Manual smartphone Web evidence should record booleans and labels only:

```text
smartphone_web_ui_live_reply_evidence_status: verified
smartphone_web_ui_live_reply_source_mode: framework_text_chat_live_message
smartphone_web_ui_backend_status_ok: True
smartphone_web_ui_api_base_url_visible: True
smartphone_web_ui_chat_source_visible: True
smartphone_web_ui_response_non_empty: True
smartphone_web_ui_body_hidden_in_evidence: True
smartphone_web_ui_next_step: record-v190-live-text-chat-smartphone-web-ui-evidence
```

Smartphone Web local URL shapes must stay placeholder-based in public docs:

```text
http://<PC_LAN_IP>:8000
http://<PC_LAN_IP>:18080
```

Day33 source-tree mode does not start Flutter, open a browser, call `ask`, call `ask_stream`, or call provider APIs. Strict local UI verification remains an operator action using the Day32 gates, and public evidence must not include prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, or raw LAN IPs.

Day33 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day33.py
```


## v1.9.0 Day32 DRC adapter live FW text-chat reply wiring

Day32 wires the Day31 verified live FW4.0.0 text-chat response path into the DRC post-advice chat adapter/API boundary.

Day31 confirmed:

```text
live_text_chat_message_evidence_status: verified
live_text_chat_message_evidence_smoke_status: responded
live_text_chat_message_evidence_next_step: wire-live-text-chat-response-through-drc-adapter
```

Day32 adds:

```text
backend/app/services/framework_text_chat_drc_live_reply.py
backend/app/services/framework_text_chat_adapter.py
backend/app/services/post_advice_chat_service.py
scripts/smoke_framework_text_chat_drc_adapter_live_reply.py
docs/framework_text_chat_drc_adapter_live_reply.md
docs/internal/v190_smartphone_web_fw_demo_day32.md
scripts/check_v190_smartphone_web_fw_demo_day32.py
```

The source-tree smoke uses a fake live reply service and verifies the DRC adapter/API wiring without provider calls:

```text
drc_adapter_live_reply_status: responded
drc_adapter_live_reply_source_mode: framework_text_chat_live_message
drc_adapter_live_reply_configured_success: True
drc_chat_api_live_reply_source_mode: framework_text_chat_live_message
drc_chat_api_live_reply_body_hidden: True
```

Strict local adapter/API smoke requires all explicit gates:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<configured-framework-root>
```

Day32 source-tree mode does not call `ask`, `ask_stream`, OpenAI, Gemini, Grok, ElevenLabs, Google Health, Fitbit, STT, TTS, Live2D/VTS, or provider APIs. Strict local mode may make one bounded `session.ask` call through the DRC adapter, but smoke output hides prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, and raw LAN IPs. The next step is `verify-live-fw-response-through-smartphone-web-ui`.

Day32 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day32.py
```


## v1.9.0 Day31 framework live text-chat message evidence

Day31 records the public-safe evidence shape after Day30 strict local live-message smoke reached a real FW4.0.0 text chat response.

Day30 confirmed:

```text
live_text_chat_message_smoke_status: responded
live_text_chat_message_smoke_gate_status: ready
live_text_chat_message_smoke_provider_call_attempted: True
live_text_chat_message_smoke_response_received: True
live_text_chat_message_smoke_response_type: str
live_text_chat_message_smoke_response_non_empty: True
live_text_chat_message_smoke_failure_kind: none
```

Day31 adds:

```text
backend/app/services/framework_text_chat_live_message_evidence.py
scripts/smoke_framework_text_chat_live_message_evidence.py
docs/framework_text_chat_live_message_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day31.md
scripts/check_v190_smartphone_web_fw_demo_day31.py
```

The evidence renderer keeps only public-safe metadata:

```text
live_text_chat_message_evidence_status: verified
live_text_chat_message_evidence_smoke_status: responded
live_text_chat_message_evidence_provider_call_attempted: True
live_text_chat_message_evidence_response_received: True
live_text_chat_message_evidence_response_type: str
live_text_chat_message_evidence_response_text_length_present: True
live_text_chat_message_evidence_response_non_empty: True
live_text_chat_message_evidence_next_step: wire-live-text-chat-response-through-drc-adapter
```

Source-tree smoke remains provider-free:

```powershell
python scripts\smoke_framework_text_chat_live_message_evidence.py
```

Strict local evidence smoke uses the same explicit gates as Day30:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<configured-framework-root>
```

Day31 does not print prompt bodies, response bodies, provider payloads, API key values, authorization headers, private paths, or raw LAN IPs. The next step is to wire the verified live response through the DRC post-advice chat adapter/API boundary.


## v1.9.0 Day30 framework live text-chat message smoke

Day30 adds the first explicitly gated local smoke that may send one bounded message through FW4.0.0 text chat. It is separate from Day29's gate evaluator so source-tree checks remain provider-free by default.

Day30 adds:

```text
backend/app/services/framework_text_chat_live_message_smoke.py
scripts/smoke_framework_text_chat_live_message.py
docs/framework_text_chat_live_message_smoke.md
docs/internal/v190_smartphone_web_fw_demo_day30.md
```

The strict local gates are:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1
FRAMEWORK_PROJECT_ROOT=<configured-framework-root>
```

Default source-tree smoke remains safe:

```powershell
python scripts\smoke_framework_text_chat_live_message.py
```

Strict local live-message smoke:

```powershell
python scripts\smoke_framework_text_chat_live_message.py --require-real-framework
```

The rendered result is public-safe:

```text
live_text_chat_message_smoke_status: blocked
live_text_chat_message_smoke_status: responded
live_text_chat_message_smoke_provider_call_attempted: True
live_text_chat_message_smoke_response_received: True
live_text_chat_message_smoke_response_non_empty: True
```

If a local provider env value looks like a placeholder, the smoke blocks before the provider call:

```text
live_text_chat_message_smoke_status: blocked-provider-env-placeholder
```

Prompt and response bodies are hidden. Day30 does not print provider payloads, API key values, authorization headers, raw private paths, or raw LAN IPs.

Day30 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day30.py

cd app
flutter test
cd ..
```


## v1.9.0 Day29 framework live text-chat message gate

Day29 defines the explicit local operator gate for the next step after Day28 session-created evidence. The gate is intentionally separate from session creation so the first real message send cannot happen accidentally.

Day28 verified:

```text
session_created_evidence_status: created
session_created_evidence_session_created: True
session_created_evidence_has_session_info: True
session_created_evidence_next_step: design-explicit-live-text-chat-message-gate
```

Day29 adds:

```text
backend/app/services/framework_text_chat_live_message_gate.py
scripts/smoke_framework_text_chat_live_message_gate.py
docs/framework_text_chat_live_message_gate.md
docs/internal/v190_smartphone_web_fw_demo_day29.md
```

The new env gate is off by default:

```text
DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=0
```

Default gate output remains blocked:

```text
live_text_chat_message_gate_status: blocked
live_text_chat_message_gate_env_name: DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE
live_text_chat_message_gate_enabled: False
live_text_chat_message_gate_session_created_evidence_status: created
live_text_chat_message_gate_next_step: enable-explicit-live-text-chat-message-gate-locally
```

If an operator explicitly sets `DRC_FW40_ENABLE_LIVE_TEXT_CHAT_MESSAGE=1`, Day29 can report `live_text_chat_message_gate_status: ready`, but it still does not call `ask`, `ask_stream`, or provider APIs. The first actual message send belongs to a separate future live-message smoke, whose next-step label is `run-explicit-live-text-chat-message-smoke`.

Day29 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day29.py

cd app
flutter test
cd ..
```


## v1.9.0 Day28 framework text chat session created evidence

Day28 records the public-safe success evidence after Day27 local opt-in allowed strict FW session diagnosis to reach:

```text
status: created
likely_cwd_dependency: True
attempt: framework-root-cwd
  status: created
  session_created: True
  has_session_info: True
No ask, ask_stream, or provider call was made.
```

Day28 adds a compact evidence renderer:

```text
backend/app/services/framework_text_chat_session_created_evidence.py
scripts/smoke_framework_text_chat_session_created_evidence.py
docs/framework_text_chat_session_created_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day28.md
```

The rendered evidence shape is intentionally public-safe:

```text
session_created_evidence_status: created
session_created_evidence_likely_cwd_dependency: True
session_created_evidence_created_attempt: framework-root-cwd
session_created_evidence_session_created: True
session_created_evidence_has_session_info: True
session_created_evidence_next_step: design-explicit-live-text-chat-message-gate
```

This confirms that the configured FW4.0.0 text chat path is verified through session creation. The next step is to design an explicit live text-chat message gate before any `ask` / `ask_stream` call is introduced.

Day28 remains session-created evidence only and does not call `ask`, `ask_stream`, or provider APIs.

Day28 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day28.py

cd app
flutter test
cd ..
```

## v1.9.0 Day27 framework text chat provider env local opt-in

Day27 records the local-only operator step after Day26 reported provider env readiness as blocked:

```text
provider_env_readiness_status: blocked
provider_env_required_names: GOOGLE_API_KEY
provider_env: GOOGLE_API_KEY set= False
```

Day27 adds a public-safe local opt-in smoke:

```text
scripts/smoke_framework_text_chat_provider_env_operator_opt_in.py
docs/framework_text_chat_provider_env_local_opt_in.md
docs/internal/v190_smartphone_web_fw_demo_day27.md
```

The smoke can verify either a fake in-memory source-tree setup or the local operator environment. It prints only env names and set/unset booleans. It never prints, persists, or returns API key values.

Local readiness check command:

```powershell
python scripts\smoke_framework_text_chat_provider_env_operator_opt_in.py --check-local --required-env GOOGLE_API_KEY
```

If it reports `status: ready`, re-run strict session diagnosis:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<repo-root>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"

python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

Day27 also documents blank provider key placeholders in `backend/.env.example`:

```text
GOOGLE_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
XAI_API_KEY=
```

Day27 remains preflight/readiness only and does not call `ask`, `ask_stream`, or provider APIs.

Day27 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day27.py

cd app
flutter test
cd ..
```

## v1.9.0 Day26 framework text chat provider env readiness

Day26 adds a public-safe provider env readiness gate for the Day25 blocker:

```text
framework-root-cwd -> OSError
safe_message: GOOGLE_API_KEY is not defined.
failure_kind: provider-env-missing
```

The readiness gate reports provider env names and boolean set/unset status only. It never prints, persists, or returns API key values.

Day26 adds:

```text
backend/app/services/framework_text_chat_provider_env_readiness.py
scripts/smoke_framework_text_chat_provider_env_readiness.py
docs/framework_text_chat_provider_env_readiness.md
docs/internal/v190_smartphone_web_fw_demo_day26.md
```

The strict session diagnosis now also prints public-safe readiness details when it sees `provider-env-missing`:

```text
provider_env_readiness_status: blocked|ready
provider_env_required_names: GOOGLE_API_KEY
provider_env: GOOGLE_API_KEY set= False|True
```

Day26 remains preflight/readiness only and does not call `ask`, `ask_stream`, or provider APIs.

Day26 check command:

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


## v1.9.0 Day25 framework text chat provider env diagnosis

Day25 records the next strict configured session-creation blocker after the Day24 import setup fix.

Day24 strict configured result now reaches provider environment initialization:

```text
framework-root-cwd -> OSError
safe_message: GOOGLE_API_KEY is not defined.
failure_kind: provider-env-missing
```

This means the `registry` import-layout blocker is no longer the active blocker. The configured FW session path now needs provider environment readiness before session creation can complete.

Day25 adds the public-safe provider env diagnosis helper:

```text
backend/app/services/framework_text_chat_provider_env_diagnosis.py
scripts/smoke_framework_text_chat_provider_env_diagnosis.py
docs/framework_text_chat_provider_env_diagnosis.md
docs/internal/v190_smartphone_web_fw_demo_day25.md
```

The helper records env var names and boolean set/unset status only. It does not print, persist, or return API key values.

Known provider env names are tracked by name only:

```text
GOOGLE_API_KEY
GEMINI_API_KEY
OPENAI_API_KEY
XAI_API_KEY
```

Day25 remains preflight/diagnosis only and does not call `ask`, `ask_stream`, or provider APIs.

Day25 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day25.py

cd app
flutter test
cd ..
```

## v1.9.0 Day24 framework text chat session import setup

Day24 applies the Day23 import layout evidence to the session-creation diagnosis path.

Day23 strict configured result:

```text
configured-root-only
  framework_spec_status: found
  registry_spec_status: found
```

Day24 adds a shared import setup helper:

```text
backend/app/services/framework_text_chat_import_setup.py
```

The helper keeps the configured FW import layout active during both:

```text
import framework
create_text_chat_session
```

This prevents a false `ModuleNotFoundError` from lazy top-level imports, such as `registry`, that may happen after the public package import.

Day24 updates the session creation diagnosis smoke so the fake framework performs a lazy `import registry` inside `create_text_chat_session`. The expected source-tree result is:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> created
no ModuleNotFoundError for registry
```

Day24 may create a framework text chat session only for preflight/diagnosis. It still does not call `ask`, `ask_stream`, or provider APIs.

Day24 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day24.py

cd app
flutter test
cd ..
```

## v1.9.0 Day23 vendor framework package import layout diagnosis

Day23 investigates the vendored FW4.0.0 package/import layout for the current LLM/text chat blocker.

Previous strict configured diagnosis:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
likely_cwd_dependency -> False
```

Day23 compares candidate import layouts:

```text
configured-root-only
configured-src-only
framework-package-dir-only
configured-root-plus-framework-package-dir
configured-src-plus-framework-package-dir
```

The diagnosis records whether `framework` and the top-level `registry` module specs are discoverable from each layout. If the combined configured-root plus framework-package-dir layout resolves both names, DRC may be able to absorb the issue with a narrow adapter `sys.path` layout; otherwise the result should become FW packaging/import-layout feedback.

Day23 does not create framework sessions and does not call `ask`, `ask_stream`, or provider APIs.

Day23 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day23.py

cd app
flutter test
cd ..
```

## v1.9.0 Day22 goal alignment checkpoint

Day22 keeps the work aligned with the v1.9.0 goal before continuing deeper framework diagnosis.

v1.9.0 goal:

```text
DRC is a public demo app for AI Character Framework v4.0.0.
The operator can verify FW4.0.0 capability surfaces from their own smartphone Web browser through actual DRC backend APIs.
```

In-scope FW4.0.0 capability targets:

```text
LLM / text chat
STT / voice input boundary
TTS / voice output boundary
Live2D / VTS motion boundary
```

Current LLM/text chat blocker:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
likely_cwd_dependency -> False
```

The `registry` import diagnosis remains in scope only as a blocker investigation for the v1.9.0 FW4.0.0 demo path.

Day22 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day22.py

cd app
flutter test
cd ..
```


## v1.9.0 Day21 vendor framework session creation FacadeConfigError diagnosis

### Day21 strict configured diagnosis evidence

The strict configured diagnosis against the vendored framework checkout was recorded in public-safe form.

```text
status: error
module: framework
project_root_shape: <configured-framework-root>
likely_cwd_dependency: False
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
No ask, ask_stream, or provider call was made.
```

This means the next issue is not a simple CWD switch. The next target is the vendored framework import/package layout, especially top-level `registry` import resolution.


Day21 adds a safe diagnosis boundary for the `FacadeConfigError` found during the strict vendor framework session creation preflight.

Observed Day20 strict result:

```text
Configured framework session creation preflight did not create a session:
error: create_text_chat_session failed safely: FacadeConfigError
```

Day21 diagnosis compares two controlled attempts:

```text
current-cwd
framework-root-cwd
```

This helps identify CWD-dependent preset/character resolution without sending chat messages.

Day21 still does not call `ask`, `ask_stream`, or provider APIs.

Day21 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day21.py

cd app
flutter test
cd ..
```

Strict configured diagnosis shape:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```


## v1.9.0 Day20 framework text chat session creation preflight

Day20 adds a safe preflight for creating a framework text chat session without sending messages.

Default source-tree smoke uses a fake framework module:

```text
create_text_chat_session()
→ session created
→ session info visible
→ no ask / ask_stream
→ no provider call
```

Strict configured operator run shape:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_preflight.py --require-real-framework
```

Day20 does not execute framework text chat responses.

Day20 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day20.py

cd app
flutter test
cd ..
```


## v1.9.0 Day19 vendor framework checkout preflight evidence

Day19 records the strict configured preflight result using the app vendor framework checkout.

Public-safe verified result:

```text
[smoke-framework-text-chat-configured-preflight] OK
module: framework
project_root_shape: <configured-framework-root>
has_create_text_chat_session: True
has_text_chat_session_class: True
No session was created and no provider call was made.
```

Verified framework checkout shape:

```text
vendor/AI-Character-Framework_v4.0.0
```

This confirms that the DRC backend can local-import the vendored AI Character Framework v4.0.0 checkout and see the public text chat session API surface.

Day19 still does not create a framework text chat session, send a chat message, or call provider APIs.

Day19 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day19.py

cd app
flutter test
cd ..
```


## v1.9.0 Day18 configured framework text chat local import preflight smoke

Day18 adds an operator-facing smoke script for the real AI Character Framework checkout local import preflight.

Default behavior is safe:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=0
→ configured preflight smoke reports SKIPPED
```

Strict configured check:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_configured_preflight.py --require-real-framework
```

The smoke verifies:

```text
- configured framework root can be used for local import
- framework module imports
- create_text_chat_session is visible
- no text chat session is created
- no provider API is called
```

Day18 still does not execute real framework text chat responses.

Day18 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day18.py

cd app
flutter test
cd ..
```


## v1.9.0 Day17 framework text chat local import preflight

Day17 adds a safe local import preflight for future configured AI Character Framework text chat.

The preflight checks only import/API visibility:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=1
→ resolve FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT
→ import framework module
→ confirm create_text_chat_session is visible
→ do not create a session
→ do not send chat messages
→ do not call provider APIs
```

New backend boundary names:

```text
FrameworkTextChatPreflightService
FrameworkTextChatPreflightResult
```

Day17 still does not execute real framework text chat.

Day17 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day17.py

cd app
flutter test
cd ..
```


## v1.9.0 Day16 framework text chat unavailable UI verification

Day16 verifies the visible unavailable state for the configured framework text chat boundary.

Day15 added the adapter skeleton. Day16 confirms that when the configured framework gate is enabled but the real framework path is not configured or not implemented yet, the app exposes a safe non-success state instead of pretending that framework text chat succeeded.

Verified state target:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
→ Chat source: framework / framework_text_chat_boundary
→ message send
→ Chat source: framework / framework_text_chat_unavailable
→ safe unavailable guidance visible
```

Day16 still does not call AI Character Framework.

Day16 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day16.py

cd app
flutter test
cd ..
```


## v1.9.0 Day15 framework text chat adapter skeleton

Day15 adds the backend skeleton for the configured AI Character Framework text chat boundary.

The mock-safe post-advice chat path remains the default.

Default behavior:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=0
→ post-advice chat uses mock-safe replies
```

Configured boundary behavior:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
→ post-advice chat routes through FrameworkPostAdviceChatAdapter
→ Day15 returns safe skipped/unavailable states
→ Day15 does not call AI Character Framework yet
```

New backend boundary names:

```text
FrameworkPostAdviceChatAdapter
FrameworkTextChatResult
framework_text_chat_boundary
framework_text_chat_skipped
framework_text_chat_unavailable
```

Day15 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day15.py
cd app
flutter test
cd ..
```


## v1.9.0 Day14 configured AI Character Framework text chat boundary

Day14 defines the safe boundary for moving from the mock-safe post-advice chat flow to configured AI Character Framework text chat.

Current verified state:

```text
mock-safe smartphone Web post-advice chat UI verified
```

Day14 planned boundary:

```text
post-advice chat UI
→ DRC backend /chat boundary
→ configured AI Character Framework text chat adapter
→ visible Web UI chat response
```

Configured framework text chat must remain explicit opt-in:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=0
```

Day14 does not call AI Character Framework yet. It defines:

```text
- opt-in gate
- framework available / unavailable / fallback / success states
- request context that may be passed to FW text chat
- public-safe evidence requirements
- rule that mock chat and framework fallback are not configured framework text chat success
```

Day14 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day14.py
cd app
flutter test
```


## v1.9.0 Day13 smartphone Web post-advice chat evidence record

Day13 records the actual smartphone Web post-advice chat manual verification result in a public-safe form.

Verified manual flow:

```text
release build static hosting
→ smartphone browser
→ DRC Home visible
→ Backend status: ok visible
→ API base URL visible
→ advice result visible
→ Post-advice Chat visible
→ 少し話す selected
→ Chat session visible
→ message sent
→ user message visible
→ character response visible
→ Chat source visible
```

Public-safe result:

```text
Result: mock-safe smartphone Web post-advice chat UI verified
```

This verifies the mock-safe smartphone Web UI path. It does not claim configured real LLM chat, AI Character Framework text chat, STT, TTS, Live2D/VTS, or Google Health real API success.

Day13 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day13.py
cd app
flutter test
```


## v1.9.0 Day12 smartphone Web post-advice chat manual evidence

Day12 adds a safe manual evidence template for the smartphone Web post-advice chat flow.

Manual target flow:

```text
release build static hosting
→ smartphone browser
→ DRC Home
→ Backend status: ok
→ API base URL visible
→ advice result
→ Post-advice Chat
→ 少し話す
→ message send
→ user message visible
→ character response visible
→ Chat source visible
```

Day12 does not add new runtime behavior. It records how to safely document the result of the real smartphone Web check without leaking private LAN IP values, API keys, tokens, raw provider payloads, private paths, or screenshots that expose secrets.

Day12 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day12.py
cd app
flutter test
```

Manual run reminder:

```powershell
cd app
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
python -m http.server 18080 --bind 0.0.0.0 --directory build\web
```

Then open this from the smartphone browser:

```text
http://<PC_LAN_IP>:18080
```


## v1.9.0 Day11 smartphone Web post-advice chat verification

Day11 defines the manual smartphone Web verification path for the post-advice chat flow added in Day10.

Required manual UI flow:

```text
smartphone browser
→ Flutter Web UI
→ backend API base URL visible
→ backend status ok
→ create advice
→ Post-advice Chat section visible
→ choose "少し話す"
→ Chat session visible
→ send a message
→ user message visible
→ character response visible
→ Chat source visible
```

Recommended runtime path remains the Day7 release build static hosting path:

```powershell
cd app
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
python -m http.server 18080 --bind 0.0.0.0 --directory build\web
```

Smartphone URL shape:

```text
http://<PC_LAN_IP>:18080
```

Day11 does not require configured real LLM/FW chat execution. It verifies the mock-safe post-advice chat UI path from smartphone Web.

Day11 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day11.py
cd app
flutter test
```


## v1.9.0 Day8 post-advice chat continuation flow inventory

Day8 restores the originally intended post-advice chat continuation flow to the roadmap.

Current DRC flow:

```text
sleep / mood / character
→ advice
→ optional DailyRecord save
→ History review
```

Missing intended flow:

```text
advice result
→ "少し話す？" / "今日はここまで"
→ optional character chat continuation
→ optional DailyRecord / History relation
```

Day8 is an inventory step. It does not implement chat yet.

Future backend boundary names include `ChatSession`, `ChatMessage`, and `PostAdviceChatContext`.

It records the required future boundaries:

```text
- post-advice chat prompt in the Web UI
- chat session model
- chat message model
- mock-safe chat response path
- configured AI Character Framework text-chat path
- advice context handoff into chat
- DailyRecord / History relation policy
- smartphone Web UI evidence rules for the chat continuation flow
```

Day8 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day8.py
```


## v1.9.0 Day7 smartphone Web manual runtime checklist

Day7 defines the manual runtime checklist for demonstrating DRC from a smartphone browser through Flutter Web and the actual backend API.

Manual runtime shape:

```text
PC backend:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

Recommended Flutter Web smartphone path:
flutter build web --release --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
python -m http.server 18080 --bind 0.0.0.0 --directory build\web

Smartphone:
http://<PC_LAN_IP>:18080
```

Required UI checks:

```text
- the Web UI opens from the smartphone browser
- API base URL is visible and points to http://<PC_LAN_IP>:8000
- backend connection / health is visible
- character list and selected character are visible
- sleep summary or safe unavailable state is visible
- advice can be requested and result state is visible
- DailyRecord save result is visible
- History review can show the saved result
- demo status / voice input / voice output / motion / health data surfaces are visible
```

Day7 still does not require real provider execution. It defines the manual smartphone Web path and safe evidence rules.

Day7 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day7.py
```


## v1.9.0 Day6 smartphone Web API base URL configuration

Day6 adds the first runtime-facing change for smartphone Web demonstration.

Flutter Web backend API URL configuration now supports:

```text
--dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

Default behavior remains mock-safe and desktop-local:

```text
http://127.0.0.1:8000
```

The Home screen now shows:

```text
API base URL: <configured backend API URL>
```

This makes the smartphone Web evidence path clearer because the operator can confirm from the UI which backend API URL the browser is using.

Example desktop-local run:

```powershell
cd app
flutter run -d chrome
```

Example smartphone-Web-oriented run:

```powershell
cd app
flutter run -d chrome --web-hostname 0.0.0.0 --web-port 8080 --dart-define=DRC_BACKEND_API_BASE_URL=http://<PC_LAN_IP>:8000
```

Day6 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day6.py
```


## v1.9.0 Day5 Web UI verification evidence rules

Day5 defines the evidence rules for smartphone Web / browser UI verification.

Core rule:

```text
API success alone is not enough.
The relevant result, status, fallback, unavailable state, skipped state, or save result must be visible in the Web UI.
```

Day5 defines UI evidence requirements for:

```text
- LLM / advice
- STT / voice input
- TTS / voice output
- Live2D / VTS motion
- Google Health / health data status
- DailyRecord save and History review
- report-informed advice and reflection
```

Day5 also defines safe manual evidence rules:

```text
- record device/browser and URL shape
- record selected character/mood/capability mode
- record visible UI result or state
- do not record secrets, tokens, authorization headers, private credential paths, raw provider payloads, or full provider debug traces
```

Day5 does not execute real providers. It defines what later Web UI/manual checks must prove.

Day5 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day5.py
```


## v1.9.0 Day4 configured real API environment profile

Day4 documents the configured real API environment profile for FW4.0.0 smartphone Web demo verification.

The profile is intentionally separate from the mock-safe default.

Configured real API inputs may use already-obtained credentials for:

```text
- LLM: OpenAI, Gemini, Grok
- TTS: ElevenLabs
- Health data: Google Health API
```

Public repository rule:

```text
Commit environment variable names and empty placeholders only.
Do not commit real keys, OAuth secrets, refresh tokens, access tokens, local credential files, authorization headers, raw provider payloads, or private absolute paths.
```

Configured real execution remains explicit opt-in:

```text
DRC_FW40_ENABLE_CONFIGURED_REAL_API_SMOKE=1
DRC_FW40_ENABLE_LLM_REAL_API_SMOKE=1
DRC_FW40_ENABLE_STT_REAL_API_SMOKE=1
DRC_FW40_ENABLE_TTS_REAL_API_SMOKE=1
DRC_FW40_ENABLE_LIVE2D_VTS_RUNTIME_SMOKE=1
DRC_FW40_ENABLE_GOOGLE_HEALTH_REAL_API_SMOKE=1
```

Day4 does not call providers. It prepares the safe profile and non-exposure guardrails for later configured checks.

Day4 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day4.py
```


## v1.9.0 Day3 FW4.0.0 capability surface inventory

Day3 inventories the current surfaces for FW4.0.0-era demo capabilities.

Capability targets:

```text
- LLM
- STT / voice input
- TTS / voice output
- Live2D / VTS motion
```

Day3 records, for each capability:

```text
- current backend endpoint surface
- current Web UI surface
- current configuration / opt-in gate
- mock-safe or placeholder behavior
- configured-success evidence that will be required later
- current gap between request/status wiring and real execution proof
```

Important Day3 conclusion:

```text
LLM has the strongest existing DRC path through /advice and framework/fallback source labels.
STT / TTS / Live2D-VTS currently have useful Web UI and backend request/status surfaces, but they remain safe demo/contract boundaries until real configured execution evidence is added.
```

Day3 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day3.py
```


## v1.9.0 Day2 smartphone Web runtime inventory

Day2 inventories the current runtime path for the required smartphone Web demo.

Current implementation notes:

```text
- Flutter Web calls the backend through BackendApiClient.
- BackendApiClient currently defaults to http://127.0.0.1:8000.
- That default is enough for local desktop browser smoke, but not enough by itself for smartphone Web demonstration.
- Smartphone Web demonstration needs a documented LAN-accessible backend API base URL path.
- Existing Home UI surfaces already include backend connection, character choice, advice, DailyRecord save, demo status, voice input demo, voice output demo, motion demo, health data status, and Google Health developer checks.
- Current voice input, voice output, and motion endpoints are safe demo/contract boundaries; they expose status and request results but do not yet prove real STT, real TTS, or real VTS execution.
```

Day2 does not change runtime code. It records the current state so later v1.9.0 days can close the gaps deliberately.

Day2 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day2.py
```


## v1.9.0 development start

v1.9.0 starts the Smartphone Web FW4.0.0 demo hardening milestone after the completed v1.8.0 Report-to-advice handoff and DailyRecord reflection polish release.

v1.8.0 remains a completed fixed release record:

```text
release\DailyRhythmCompanion_20260522_234744.zip
release_notes/v1.8.0.md
```

Do not rebuild the v1.8.0 fixed zip. Use it only as the completed release artifact.

v1.9.0 is centered on the original DRC requirement:

```text
The developer can demonstrate the public AI Character Framework demo app from their own smartphone through Web access, using the actual DRC backend API and configured FW4.0.0-era capabilities.
```

v1.9.0 documentation and checks should cover:

```text
- public AI Character Framework demo app positioning
- smartphone Web access as a required demo path
- real backend API calls from Web UI
- configured FW4.0.0 capability verification for LLM / STT / TTS / Live2D-VTS
- configured real API environment variables for OpenAI / Gemini / Grok / ElevenLabs / Google Health
- Web UI result verification, not API-only completion
- AI-generated app visual asset planning for backgrounds and character images
- v2.0.0-or-later boundary for general consumer app-store release work
```

Day1 planning/check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day1.py
```


## v1.8.0 development start

v1.8.0 starts the Report-to-advice handoff and DailyRecord reflection polish milestone after the completed v1.7.0 rhythm report polish release.

The goal is to connect the polished weekly/monthly rhythm report surface to the character advice and saved DailyRecord reflection loop without making provider-backed LLM execution, real health APIs, or production health claims mandatory. The first loop focuses on handoff boundaries, explanation wording, saved-record reflection copy, source/data-quality preservation, and mock-safe verification.

v1.7.0 remains a completed fixed release record:

```text
release\DailyRhythmCompanion_20260522_214532.zip
release_notes/v1.7.0.md
```

Do not rebuild the v1.7.0 fixed zip. Use it only as the completed release artifact.

Day1 planning/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day1.py
```

Day2 inventory/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day2.py
```

Day2 is source-tree only. It inventories the current rhythm report, advice, and DailyRecord reflection surfaces, records that RhythmReport is not yet passed into AdviceRequest, and defines the smallest safe ReportHandoffContext direction before implementation.

Day3 copy-rule/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day3.py
```

Day3 is source-tree only. It defines `docs/report_advice_handoff_copy_rules.md` so report-informed advice and DailyRecord reflection can explain usable, partial, insufficient, fallback, source/data-quality, and non-medical states before runtime implementation.

Day4 backend boundary/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day4.py
```

Day4 adds `backend/app/models/report_handoff.py`, `backend/app/services/report_handoff_service.py`, and `docs/report_handoff_context_backend.md`. It creates a mock-safe `ReportHandoffContext` boundary with `should_inform_advice`, `advice_basis_prefix`, user-facing source/scope/quality labels, and conservative prompt guidance while keeping `/advice`, `AdviceRequest`, DailyRecord persistence, and Flutter runtime behavior unchanged.

Day5 advice metadata/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day5.py
```

Day5 wires the existing `ReportHandoffContext` boundary into the backend advice contract with an optional `AdviceRequest.report_handoff` field and `AdviceSource.report_handoff` metadata. Usable reports produce `rhythm_report+mood+character+<engine>` advice_basis values, partial reports produce `rhythm_report_partial+mood+character+<engine>`, and insufficient/unsafe reports are dropped before prompt generation or DailyRecord persistence. Flutter runtime behavior remains unchanged on Day5; the app can continue to ignore the new optional response metadata until the next UI pass.


Day6 Flutter display/reflection check command:

```powershell
python scripts\check_v180_report_advice_handoff_day6.py
```

Day6 adds `app/lib/models/report_handoff_context.dart`, extends `AdviceSource` and `DailyRecord` display helpers, and shows safe report-informed context in the Home advice result and History DailyRecord reflection when optional `AdviceSource.report_handoff` metadata is present. The app uses user-facing report labels and avoids exposing raw `source_label`, `data_scope`, `data_quality`, or full `rhythm_report+...` basis strings as the main copy. Day6 does not automatically fetch RhythmReport from the Home advice flow or rebuild the fixed v1.7.0 zip.

Day7 aggregate readiness/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day7.py
```

Day7 adds the aggregate v1.8.0 readiness gate for the report-to-advice handoff loop. It reruns the Day6 check, verifies the Day1 through Day6 docs/check inventory, confirms backend `ReportHandoffContext`, advice metadata, Flutter display helpers, Home/History UI, and widget/model-test guardrails are still present, and remains source-tree only before final cleanup and release packaging.

Day8 final pre-release source-tree cleanup/check command:

```powershell
python scripts\check_v180_report_advice_handoff_day8.py
```

Day8 adds the final pre-release source-tree cleanup gate before creating a v1.8.0 fixed release zip. It reruns the Day7 aggregate readiness check, verifies Day1 through Day8 docs/check inventory, confirms the v1.8.0 public handoff docs and backend/Flutter handoff files remain present, and fails if temporary v1.8.0 helper bundles, replacement folders, extraction folders, or local release work folders remain in the repository root. Day8 does not build or rebuild a release zip.

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

Day9 introduces the v1.8.0 fixed release zip verification gate. Build the release zip once after Day8 passes, record the printed path, and verify that fixed zip without rebuilding. The Day9 check reruns the Day8 source-tree cleanup gate, inspects the provided zip as-is, verifies the v1.8.0 docs/check/backend/Flutter handoff inventory is included, and confirms temporary helper/generated artifacts are absent from the package. The check does not call `build_release.bat` or rebuild the provided zip.

## Common checks

From the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v180_report_advice_handoff_day1.py
python scripts\check_v180_report_advice_handoff_day2.py
python scripts\check_v180_report_advice_handoff_day3.py
python scripts\check_v180_report_advice_handoff_day4.py
python scripts\check_v180_report_advice_handoff_day5.py
python scripts\check_v180_report_advice_handoff_day6.py
python scripts\check_v180_report_advice_handoff_day7.py
python scripts\check_v180_report_advice_handoff_day8.py
python scripts\check_v180_report_advice_handoff_day9.py release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip
python scripts\check_v170_rhythm_report_polish_day12.py release\DailyRhythmCompanion_20260522_214532.zip
python scripts\check_v100_release_package_day10.py release\DailyRhythmCompanion_20260522_214532.zip
python scripts\check_v100_final_release_day11.py release\DailyRhythmCompanion_20260522_214532.zip
python scripts\check_v100_compatibility_final_sweep_day12.py release\DailyRhythmCompanion_20260522_214532.zip
python scripts\check_v100_compatibility_final_sweep_day12.py release\DailyRhythmCompanion_20260522_214532.zip --compat
```

After Day8 passes, build the release zip once and verify that fixed zip as-is:
- Day9 fixed release zip verification: current

```powershell
.\build_release.bat
$zip = Get-ChildItem .\release\DailyRhythmCompanion_*.zip |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

python scripts\check_v170_rhythm_report_polish_day9.py $zip.FullName
```

Day10 final release readiness must use the same fixed zip that passed Day9. Do not run `build_release.bat` again between Day9 and Day10. Day11 app-side verification must also use that same fixed zip and must not run `build_release.bat` again. Day12 release notes must reference that same fixed zip and must not rebuild it.

Day11 runs the final release readiness check, `flutter test`, and a Chrome device availability check. It also documents a manual Chrome smoke path for a backend-connected browser session. If Day11 finds an app-side issue that requires code changes, rerun the cleanup gate, build a new fixed zip once, and restart Day9 through Day11 with the new zip before writing release notes.

Day12 adds the v1.4.0 release notes under `release_notes/v1.4.0.md`, reruns the Day11 app-side verification against the same fixed zip, and records the final release checks without rebuilding the package. In other words, Day12 does not rebuild the package.

The v1.4.0 Day4 check is mock-safe. It establishes the release cleanup checkpoint for generated helper files, root-level temporary notes, stale release-note locations, local extraction folders, and fixed-zip verification hygiene.

The v1.4.0 Day6 check is mock-safe. It verifies the DRC character_id to AI Character Framework character mapping contract without requiring a real FW checkout, provider credentials, external LLM calls, or release artifact creation.

The v1.4.0 Day7 check is mock-safe. It aggregates the Day1-Day6 character experience checks, including the Day4 release cleanup checkpoint, without creating or rebuilding release artifacts.
- Day8 final pre-release source-tree cleanup verification: completed

The v1.4.0 Day8 check is mock-safe. It is the final pre-release source-tree cleanup verification before fixed release zip packaging, reruns the Day7 aggregate path, verifies the cleanup surface again, and still does not create or rebuild release artifacts.

The v1.4.0 Day9 fixed release zip check inspects the provided zip as-is. Build the release zip once after Day8 passes, record the path, and reuse that same zip for later final release checks without rebuilding.

The v1.4.0 Day10 final release readiness check reuses the same fixed zip that passed Day9, reruns the fixed-zip verification, and runs the protected v1.0.0 release/final/compatibility checks without rebuilding.

The v1.4.0 Day11 app runtime verification check reuses the same fixed zip, reruns Day10, runs `flutter test`, and verifies Chrome appears as a Flutter web device.

The v1.4.0 Day12 release notes check reuses the same fixed zip, reruns Day11, and verifies `release_notes/v1.4.0.md` as the source-tree release record. The fixed zip is not rebuilt to add release notes.

The v1.4.0 Day5 check is mock-safe. It verifies character selection UX copy, selection-facing metadata boundaries, alignment with the character inventory and tone matrix, and confirms that the v1.4.0 release path must run the cleanup checkpoint before creating the fixed release zip.


For the completed v1.3.0 release record, keep the canonical release notes under `release_notes/v1.3.0.md` and keep using the same fixed zip without rebuilding:

```powershell
$zip = "release\DailyRhythmCompanion_20260521_155200.zip"
python scripts\check_v130_framework_llm_configured_demo_day9.py $zip
python scripts\check_v130_framework_llm_configured_demo_day10.py $zip
```

The v1.3.0 Day1-Day5 checks are mock-safe. They validate the Framework / LLM configured demo hardening plan, framework-mode setup docs, profile hygiene, configured-only smoke behavior, the app-facing source-label contract, and the FW-backed advice operator checklist without requiring a real AI Character Framework checkout or provider credentials.

The Day1 and Day2 source-tree checks still verify framework-mode setup docs without importing AI Character Framework or calling external LLM providers. Day4 also checks that `AdviceSource.engine` and saved `DailyRecord.advice_basis` distinguish `mock`, `framework`, and `framework_fallback` responses, and documents configured LLM skip states as operator-check output rather than generated advice. Day5 adds the operator checklist for FW-backed advice, DailyRecord save, History review, and optional provider-backed ask verification.

The v1.3.0 Day6 aggregate check is mock-safe. Day6 aggregate runs the Day1-Day5 checks and an isolated configured smoke SKIP path, and it does not create or rebuild release artifacts.

The v1.3.0 Day7 final source-tree check is mock-safe. It runs the Day6 aggregate check, verifies the v1.3.0 docs/check/smoke inventory, and does not create or rebuild release artifacts.

The v1.3.0 Day8 fixed release zip check inspects the provided zip as-is. Create the release zip once, record the printed path, and verify that fixed zip without rebuilding:

```powershell
.\build_release.bat
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"
python scripts\check_v130_framework_llm_configured_demo_day8.py $zip
```

Day8 checks that v1.3.0 docs/check/smoke files are present in the zip and that obvious private/dev/generated artifacts are absent. It does not create or rebuild release artifacts.

The v1.4.0 Day1 check is mock-safe. It verifies the post-release consistency update, records v1.3.0 as the released baseline, starts the Character experience expansion plan, and checks that the current character contract remains simple, explicit, and non-medical.

The v1.4.0 Day2 check is mock-safe. It verifies the character profile inventory, stable app-facing fields, tone-hint fields, Flutter/backend character surfaces, and explicit DRC-to-FW mapping without requiring a real Framework checkout or provider credentials.

The v1.4.0 Day3 check is mock-safe. It verifies the character advice tone matrix, character-specific advice posture, situation-specific tone differences, deterministic mock-advice direction, and conservative non-medical wording boundaries.


Day3 also adds an optional configured-only smoke command:

```powershell
python scripts\smoke_v130_framework_llm_configured_demo.py
```

The configured-only smoke prints SKIP when framework/LLM setup is absent. It does not call external LLM providers unless explicitly gated with `DRC_V130_ENABLE_CONFIGURED_LLM_SMOKE=1` and `--ask`.

Existing release checks from previous versions should continue to pass until they are intentionally merged, archived, or replaced by newer aggregate checks.


## v1.5.0 development start

v1.5.0 begins the Mood and personalization foundation work. The first check is mock-safe and source-tree only:

```powershell
python scripts\check_v150_mood_personalization_day1.py
```

Unnecessary helper files should still be removed before v1.5.0 release packaging, not broadly deleted at the Day1 start.


## v1.5.0 Day2 mood inventory

Day2 adds the Mood input and advice-context inventory:

```powershell
python scripts\check_v150_mood_personalization_day2.py
```

It documents the current stable mood IDs, Flutter mood UI surface, backend AdviceRequest.mood contract, prompt builder behavior, mock advice behavior, and DailyRecord mood persistence before character-aware mood labels or user-adjusted labels are added.


## v1.5.0 Day3 character-aware mood choice copy

Day3 adds the Character-aware mood choice copy matrix:

```powershell
python scripts\check_v150_mood_personalization_day3.py
```

It defines character-specific presentation copy for `energetic`, `normal`, and `tired` across ミナ, ソラ, and レイ while preserving the stable mood ID contract. Day3 does not change `AdviceRequest.mood`, `DailyRecord.mood`, advice basis labels, mock behavior, or release artifacts.


## v1.5.0 Day4 Flutter mood choice display copy

Day4 implements the Day3 mood choice copy matrix in the Flutter home screen:

```powershell
python scripts\check_v150_mood_personalization_day4.py
```

The UI now resolves character-aware labels, support messages, and advice focus text for the bundled DRC characters while preserving stable mood IDs and `mood: _selectedMood` for advice creation. Unknown/default characters continue to use the generic labels `元気`, `ふつう`, and `だるい`.


## v1.5.0 Day5 Flutter mood choice widget-test coverage

Day5 adds Flutter test coverage for the Day4 character-aware mood choice display copy:

```powershell
python scripts\check_v150_mood_personalization_day5.py
```

The check runs the Day4 source-tree guard and `flutter test`. It verifies that ミナ / ソラ / レイ display their character-aware mood labels while advice creation still receives stable mood IDs such as `tired`, not the display label `低め`.


## v1.5.0 Day6 Lightweight profile boundary

Day6 defines the lightweight profile/preference boundary before implementing user-adjusted mood labels or profile fields:

```powershell
python scripts\check_v150_mood_personalization_day6.py
```

The boundary allows future app-level hints such as `nickname`, `preferred_mood_labels`, `advice_focus_preference`, and `tone_preference`, but Day6 does not add profile persistence, backend user-profile endpoints, AdviceRequest schema changes, DailyRecord schema changes, provider memory, or medical profiling.


## v1.5.0 Day7 aggregate readiness

Day7 adds the aggregate readiness gate for the first v1.5.0 mood/personalization loop:

```powershell
python scripts\check_v150_mood_personalization_day7.py
```

The aggregate reuses the Day6 check as the primary child gate, which keeps Day1-Day6 coverage reachable while also running the Day5 Flutter mood-choice widget tests. Day7 does not create or rebuild release artifacts, and unnecessary helper files remain scheduled for cleanup before v1.5.0 release packaging.

## v1.6.0 development start

v1.6.0 starts the Weekly/monthly rhythm reports milestone.

The goal is to expand saved DailyRecord history from simple review into lightweight reflection while preserving mock-safe defaults, clear source labels, and conservative non-medical wording.

Day1 planning/check command:

```powershell
python scripts\check_v160_rhythm_reports_day1.py
```

Day1 is source-tree only. It does not create a release zip, rebuild the v1.5.0 fixed release zip, call external LLM providers, call real Google Health APIs, or require AI Character Framework checkout.

## Not included in v1.0

v1.0 does not need to include:

- Store release
- Production-grade Google Health onboarding
- Always-on realtime assistant behavior
- Perfect mobile UX polish
- Advanced analytics
- Full personalization system
- Full production character animation experience

## v1.5.0 Day8 final pre-release source-tree cleanup verification

Day8 adds the source-tree cleanup gate before v1.5.0 release packaging.

It verifies the Day7 aggregate readiness path and checks for obvious temporary or generated development artifacts before a fixed release zip is built.

Run:

```powershell
python scripts\check_v150_mood_personalization_day8.py
```

Day8 does not create, rebuild, modify, or timestamp-refresh release artifacts.

## v1.5.0 Day9 fixed release zip verification

v1.5.0 Day9 verifies the fixed release zip for the Mood and personalization foundation work.

Recommended command sequence:

```powershell
python -m compileall -q backend scripts
python scripts\check_v150_mood_personalization_day8.py

.\build_release.bat

$zip = Get-ChildItem .\release\DailyRhythmCompanion_*.zip |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

python scripts\check_v150_mood_personalization_day9.py $zip.FullName
```

Day9 inspects the provided zip as-is and does not create, rebuild, modify, or timestamp-refresh release artifacts.


### v1.5.0 Day10 final release readiness

v1.5.0 Day10 reuses the same fixed release zip that passed Day9 and runs final release readiness checks without rebuilding it.

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python -m compileall -q backend scripts
python scripts\check_v150_mood_personalization_day10.py $zip
```

Day10 runs Day9 fixed release zip verification plus the protected v1.0.0 release package, final release, default compatibility, and `--compat` compatibility checks.


### v1.5.0 Day11 Flutter / Chrome app-side verification

v1.5.0 Day11 reuses the same fixed release zip that passed Day9 and Day10, then verifies Flutter / Chrome app-side readiness without rebuilding it.

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python -m compileall -q backend scripts
python scripts\check_v150_mood_personalization_day11.py $zip
```

Day11 runs Day10 final release readiness, `flutter test`, `flutter devices`, and Chrome web-device detection.


### v1.5.0 Day12 release notes

v1.5.0 Day12 adds `release_notes/v1.5.0.md` as the source-tree release record for the fixed zip.

```powershell
$zip = "release\DailyRhythmCompanion_20260521_221101.zip"

python -m compileall -q backend scripts
python scripts\check_v150_mood_personalization_day12.py $zip
```

Day12 runs Day11 Flutter / Chrome app-side verification and verifies the v1.5.0 release notes.

## v1.6.0 Day2 rhythm report inventory

Day2 inventories the current DailyRecord, recent trend, weekly summary, backend API, and Flutter History surfaces before adding monthly report implementation.

Day2 check command:

```powershell
python scripts\check_v160_rhythm_reports_day2.py
```

Day2 is source-tree only. It does not change the DailyRecord schema, create monthly report runtime code, create a release zip, rebuild the v1.5.0 fixed release zip, call external LLM providers, call real Google Health APIs, or require AI Character Framework checkout.

## v1.6.0 Day3 rhythm report contract

Day3 defines the weekly/monthly rhythm report contract before backend or Flutter implementation.

Decision:

```text
Use a generic RhythmReport contract with period=weekly/monthly.
```

The contract keeps source-label policy, sparse-history wording, unavailable-history wording, data quality labels, and non-medical report boundaries explicit.

Day3 check command:

```powershell
python scripts\check_v160_rhythm_reports_day3.py
```

Day3 is source-tree only. It does not create backend runtime report code, change the DailyRecord schema, create a release zip, rebuild the v1.5.0 fixed release zip, call external LLM providers, call real Google Health APIs, or require AI Character Framework checkout.

## v1.6.0 Day4 rhythm report backend foundation

Day4 adds the mock-safe backend model/service foundation for weekly/monthly rhythm reports.

Added runtime foundation:

```text
backend/app/models/rhythm_report.py
backend/app/services/rhythm_report_service.py
```

Day4 check command:

```powershell
python scripts\check_v160_rhythm_reports_day4.py
```

Day4 is source-tree only. It reads saved DailyRecord history, keeps conservative non-medical wording, preserves WeeklySleepSummary compatibility, and does not create or rebuild release artifacts.

## v1.6.0 Day5 rhythm report API foundation

Day5 exposes the backend rhythm report foundation through the DailyRecord API.

Added API surface:

```http
GET /daily-records/rhythm-report?period=weekly
GET /daily-records/rhythm-report?period=monthly
```

Day5 check command:

```powershell
python scripts\check_v160_rhythm_reports_day5.py
```

The endpoint returns `RhythmReport` from saved DailyRecord history only. It preserves source labels, data quality labels, non-medical wording, the existing `/daily-records/weekly-summary` endpoint, and the stable DailyRecord schema.


## v1.6.0 Day6 Flutter rhythm report presentation

Day6 adds the Flutter-side presentation path for weekly/monthly rhythm reports on the existing History screen.

Added Flutter surface:

```text
app/lib/models/rhythm_report.dart
BackendApiClient.fetchRhythmReport(period: weekly|monthly)
HistoryScreen rhythm report cards
```

Day6 check command:

```powershell
python scripts\check_v160_rhythm_reports_day6.py
```

The History screen shows Weekly Rhythm Report and Monthly Rhythm Report after the existing Simple Weekly Summary card. The cards are history-derived, keep source/data labels visible, preserve non-medical wording, and do not change the DailyRecord schema.


## v1.6.0 Day7 aggregate rhythm report readiness

Day7 adds the aggregate readiness gate for the first v1.6.0 rhythm report implementation loop.

Day7 check command:

```powershell
python scripts\check_v160_rhythm_reports_day7.py
- `python scripts\check_v160_rhythm_reports_day8.py` - v1.6.0 final pre-release source-tree cleanup verification
- `python scripts\check_v160_rhythm_reports_day9.py <fixed-release-zip>` - v1.6.0 fixed release zip verification
```

The aggregate runs the Day6 check, which keeps Day1 through Day6, backend rhythm report API coverage, and Flutter rhythm report widget-test coverage reachable from one command.

Day7 is still source-tree/runtime only. It does not create or rebuild release artifacts, change the stable DailyRecord schema, call external providers, require AI Character Framework checkout, or call real health APIs.


## v1.9.0 Day43 Live2D / VTS motion smartphone Web boundary evidence

Day43 records the guarded Live2D / VTS motion smartphone Web boundary evidence after the FW4.0.0 coverage checkpoint moved the next focus to Live2D / VTS motion.

Day43 adds:

```text
backend/app/services/framework_motion_smartphone_web_boundary_evidence.py
scripts/smoke_framework_motion_smartphone_web_boundary_evidence.py
docs/framework_motion_smartphone_web_boundary_evidence.md
docs/internal/v190_smartphone_web_fw_demo_day43.md
scripts/check_v190_smartphone_web_fw_demo_day43.py
```

The source-tree evidence shape is:

```text
motion_smartphone_web_boundary_evidence_status: verified
motion_smartphone_web_boundary_evidence_mode: source-tree-boundary
motion_smartphone_web_boundary_source_mode: motion_demo_boundary
motion_smartphone_web_boundary_status_route_present: True
motion_smartphone_web_boundary_request_route_present: True
motion_smartphone_web_boundary_api_client_route_present: True
motion_smartphone_web_boundary_flutter_section_visible: True
motion_smartphone_web_boundary_flutter_button_visible: True
motion_smartphone_web_boundary_motion_send_blocked: True
motion_smartphone_web_boundary_vts_connection_not_used: True
motion_smartphone_web_boundary_live2d_runtime_not_loaded: True
motion_smartphone_web_boundary_motion_payload_hidden_or_absent: True
motion_smartphone_web_boundary_next_step: record-manual-smartphone-web-motion-boundary-evidence
```

Day43 source-tree mode does not call configured Live2D/VTS runtime execution. It does not start Flutter, open a browser, call the backend, connect to VTube Studio, load Live2D runtime code, dispatch motion, call providers, create framework sessions, call `ask`, call `ask_stream`, process audio, generate audio, or play audio.

Day43 check command:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day43.py
```

## v1.9.0 Day42 FW4.0.0 capability coverage after voice output evidence

Day42 updates the FW4.0.0 coverage checkpoint after the voice output smartphone Web boundary record.

Added files:

```text
backend/app/services/framework_fw40_capability_coverage_after_voice_output.py
scripts/smoke_framework_fw40_capability_coverage_after_voice_output.py
docs/framework_fw40_capability_coverage_after_voice_output.md
docs/internal/v190_smartphone_web_fw_demo_day42.md
scripts/check_v190_smartphone_web_fw_demo_day42.py
```

Expected public-safe output:

```text
v190_fw40_capability_coverage_after_voice_output_status: text-chat-voice-input-and-voice-output-boundary-evidence-complete-motion-boundary-pending
v190_fw40_capability_coverage_after_voice_output_llm_text_chat_status: completed
v190_fw40_capability_coverage_after_voice_output_stt_voice_input_status: boundary-evidence-recorded
v190_fw40_capability_coverage_after_voice_output_tts_voice_output_status: boundary-evidence-recorded
v190_fw40_capability_coverage_after_voice_output_live2d_vts_motion_status: boundary-ready
v190_fw40_capability_coverage_after_voice_output_next_focus: live2d_vts_motion
```

Day42 does not run STT, TTS, Live2D/VTS, audio playback, motion dispatch, framework sessions, ask, ask_stream, provider calls, Flutter, browsers, or backend API calls. It records labels and booleans only.

## v1.9.0 Day44 Live2D / VTS motion smartphone Web boundary evidence record

Day44 records the guarded Live2D / VTS motion smartphone Web boundary evidence after the Day43 source-tree boundary evidence and the manual smartphone Web UI check.

Day44 adds:

```text
backend/app/services/framework_motion_smartphone_web_boundary_evidence_record.py
scripts/smoke_framework_motion_smartphone_web_boundary_evidence_record.py
docs/framework_motion_smartphone_web_boundary_evidence_record.md
docs/internal/v190_smartphone_web_fw_demo_day44.md
scripts/check_v190_smartphone_web_fw_demo_day44.py
```

The public-safe record shape is:

```text
v190_motion_smartphone_web_boundary_record_status: recorded
v190_motion_smartphone_web_boundary_record_from_evidence_status: verified
v190_motion_smartphone_web_boundary_record_source_mode: motion_demo_boundary
v190_motion_smartphone_web_boundary_record_motion_send_blocked: True
v190_motion_smartphone_web_boundary_record_vts_connection_not_used: True
v190_motion_smartphone_web_boundary_record_live2d_runtime_not_loaded: True
v190_motion_smartphone_web_boundary_record_motion_payload_hidden_or_absent: True
v190_motion_smartphone_web_boundary_record_next_step: update-fw40-capability-coverage-after-motion-boundary-evidence
```

Day44 check command:

```powershell
python scripts\check_v190_smartphone_web_fw_demo_day44.py
```

Day44 records only booleans and source labels. It does not store raw screenshots, raw LAN IPs, motion payload bodies, VTS WebSocket payloads, Live2D runtime state, provider payloads, API key values, private paths, audio, transcripts, prompt bodies, or response bodies. It does not connect to VTube Studio or dispatch motion.

## v1.9.0 Day45 FW4.0.0 capability coverage after motion evidence

Day45 updates the FW4.0.0 coverage checkpoint after the Live2D / VTS motion smartphone Web boundary record.

Day45 adds:

```text
backend/app/services/framework_fw40_capability_coverage_after_motion.py
scripts/smoke_framework_fw40_capability_coverage_after_motion.py
docs/framework_fw40_capability_coverage_after_motion.md
docs/internal/v190_smartphone_web_fw_demo_day45.md
scripts/check_v190_smartphone_web_fw_demo_day45.py
```

Expected source-tree evidence:

```text
v190_fw40_capability_coverage_after_motion_status: fw40-smartphone-web-capability-evidence-complete
v190_fw40_capability_coverage_after_motion_llm_text_chat_status: completed
v190_fw40_capability_coverage_after_motion_stt_voice_input_status: boundary-evidence-recorded
v190_fw40_capability_coverage_after_motion_tts_voice_output_status: boundary-evidence-recorded
v190_fw40_capability_coverage_after_motion_live2d_vts_motion_status: boundary-evidence-recorded
v190_fw40_capability_coverage_after_motion_evidence_recorded_count: 4
v190_fw40_capability_coverage_after_motion_remaining_boundary_evidence_count: 0
v190_fw40_capability_coverage_after_motion_configured_runtime_verified_count: 1
v190_fw40_capability_coverage_after_motion_next_focus: v190-release-readiness
```

Day45 check command:

```powershell
python -m compileall -q backend scripts
python scripts\check_v190_smartphone_web_fw_demo_day45.py

cd app
flutter test
cd ..
```

Day45 is source-tree evidence aggregation only. It does not call configured STT/TTS/Live2D/VTS runtime execution and does not perform provider, browser, backend, microphone, audio, VTS, Live2D, or motion calls.

## v1.9.0 release completion record

v1.9.0 remains a completed historical FW4.0.0 smartphone Web demo release. Its canonical release record is retained at [`release_notes/v1.9.0.md`](release_notes/v1.9.0.md).

Cleanup-5 removes the obsolete Day46-Day49 release-readiness, package-candidate, fixed-zip-evidence, finalization, and v1.9-specific cleanup implementation files. Those files described a completed historical release workflow and are no longer part of the current v2.0.0 Public release path. Current Public metadata/package validation is owned by `scripts/smoke_framework_v200_public_distribution_readiness.py`, with final fixed-artifact verification owned by Day82 and Day83.

The historical v1.9.0 release note is retained; Private evidence and old implementation-only release helpers are not.

## v2.0.0 pre-release requirements

The following items are **required before v2.0.0** and are tracked in [docs/v2_prerelease_requirements.md](docs/v2_prerelease_requirements.md). The active source of truth for release completion is [docs/DRC_v200_goal_checklist_small_commit.md](docs/DRC_v200_goal_checklist_small_commit.md).

Current status: **v2.0.0 is NOT RELEASED**. Validator gates, mock-safe checks, API-only smoke checks, example evidence files, fixed zip checks, and tags do not count as completion without accepted real Web UI execution evidence and screenshot references.

```text
- real LLM API: Web上で回答が生成できること / real LLM API Web answer generation
- real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
- real Google Health API: 実睡眠データが取得できること / real Google Health API sleep data retrieval
- Web image display: 画像を用いてWeb上で表示確認できること / Web image display
- public-repo-ready as an AI Character Framework demo app: LICENSEを必要に応じて作成
- explicit release requirements: 上記をリリース要件として明示的に含むこと
```

v1.9.0 is the FW4.0.0 smartphone Web public demo evidence release. v1.9.0 is not a general consumer/app-store release and does not close the v2.0.0 pre-release requirements above.

v1.10.0 is the v2.0.0 prerelease evidence gate foundation. v1.10.0 does not complete real LLM Web execution, real TTS Web audio output, real Google Health sleep retrieval, image asset generation/intake, Web image display, accepted private evidence manifest review, final fixed zip verification, or final v2.0.0 release handling.


## v2.0.0 Day52 real LLM Web answer evidence

Day52 starts the first v2.0.0 pre-release requirement after the v1.9.0 release:

```text
real LLM API: Web上で回答が生成できること / real LLM API Web answer generation
```

Day52 adds the public-safe evidence contract in [docs/v200_real_llm_web_answer_evidence.md](docs/v200_real_llm_web_answer_evidence.md). The default check is still credential-free and does not call providers, the backend, the browser, or AI Character Framework sessions.

Expected marker:

```text
v200_real_llm_web_answer_evidence_status: operator-evidence-contract-ready
```

Day52 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_llm_web_answer_day52.py
# canonical path: scripts/check_v200_real_llm_web_answer_day52.py

cd app
flutter test
cd ..
```

Configured real LLM evidence remains operator-only. It requires explicit opt-in and a running backend configured for the framework / real LLM path. Public evidence must not include API keys, prompt bodies, answer bodies, raw provider payloads, raw LAN IPs, private paths, or raw screenshots.


## v2.0.0 Day53 real TTS provider gate design

Day53 starts the second v2.0.0 pre-release requirement path:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

Day53 adds the public-safe provider gate contract in [docs/v200_real_tts_provider_gate.md](docs/v200_real_tts_provider_gate.md). DRC should call a neutral AI Character Framework voice output boundary instead of embedding a provider-specific TTS implementation.

Expected marker:

```text
v200_real_tts_provider_gate_status: provider-gate-contract-ready
```

Day53 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_tts_provider_gate_day53.py
# canonical path: scripts/check_v200_real_tts_provider_gate_day53.py

cd app
flutter test
cd ..
```

Configured real TTS Web voice output evidence remains operator-only. It requires explicit opt-in, a configured FW voice output boundary, generated audio through a real provider, and audible Web confirmation. Public evidence must not include API keys, private text bodies, raw provider payloads, generated audio artifacts, raw LAN IPs, private paths, or raw screenshots.


## v2.0.0 Day54 real TTS Web audio output evidence

Day54 continues the second v2.0.0 pre-release requirement path:

```text
real TTS API: Web上で音声出力が行えること / real TTS API Web voice output
```

Day54 adds the public-safe evidence contract in [docs/v200_real_tts_web_audio_output_evidence.md](docs/v200_real_tts_web_audio_output_evidence.md). It builds on the Day53 provider gate and defines how a configured operator run should prove provider synthesis, safe backend audio exposure, and audible Web output.

Expected marker:

```text
v200_real_tts_web_audio_evidence_status: operator-evidence-contract-ready
```

Day54 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_tts_web_audio_output_day54.py
# canonical path: scripts/check_v200_real_tts_web_audio_output_day54.py

cd app
flutter test
cd ..
```

Configured real TTS Web audio evidence remains operator-only. It requires explicit opt-in and must omit API keys, private text bodies, raw provider payloads, audio artifacts, raw LAN IPs, private paths, raw screenshots, and raw audio URLs from public evidence.


## v2.0.0 Day55 real Google Health sleep data evidence

Day55 starts the third v2.0.0 pre-release requirement path:

```text
Google Health実APIを使用して、実睡眠データが取得できること / real Google Health API sleep-data retrieval
```

Day55 adds the public-safe evidence contract in [docs/v200_real_google_health_sleep_data_evidence.md](docs/v200_real_google_health_sleep_data_evidence.md). It defines how a configured operator run should prove real Google Health retrieval, safe SleepSummary normalization, and backend real-data confirmation.

Expected marker:

```text
v200_real_google_health_sleep_evidence_status: operator-evidence-contract-ready
```

Day55 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_google_health_sleep_data_day55.py
# canonical path: scripts/check_v200_real_google_health_sleep_data_day55.py

cd app
flutter test
cd ..
```

Configured real Google Health evidence remains operator-only. It requires explicit opt-in and must omit client secrets, access tokens, refresh tokens, authorization headers, raw Google Health payloads, raw sleep events, precise personal sleep timestamps, raw LAN IPs, private paths, raw screenshots, browser storage, and local token files from public evidence.


## v2.0.0 Day56 Web image display evidence

Day56 starts the fourth v2.0.0 pre-release requirement path:

```text
画像を用いて、Web上で表示確認できること / Web image display evidence
```

Day56 adds the public-safe evidence contract in [docs/v200_web_image_display_evidence.md](docs/v200_web_image_display_evidence.md). It defines how a configured operator run should prove Flutter asset registration, Flutter Web display, smartphone Web display, missing-image fallback behavior, and release-package inclusion for public-safe image assets or placeholders.

Expected marker:

```text
v200_web_image_display_evidence_status: operator-evidence-contract-ready
```

Day56 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_web_image_display_day56.py
# canonical path: scripts/check_v200_web_image_display_day56.py

cd app
flutter test
cd ..
```

Configured Web image evidence remains operator-only. It requires explicit Web display confirmation and must omit private generated prompts when they contain private context, copyrighted source-image references, raw screenshots, raw LAN IPs, private paths, and unreviewed image artifacts from public evidence.

Day56 also records the intended future demo asset plan without generating images yet: lightweight public-safe character images and backgrounds should be placed under `app/assets/images/` only after generation/licensing review, then registered in `app/pubspec.yaml` and verified on Flutter Web.

## v2.0.0 historical pre-Web readiness gates

The former Day57 public-repository readiness contract and Day58 aggregate gate were preparation-stage marker contracts. Cleanup-6 removes their dedicated documents, services, and smoke scripts after Public-P2 assumes current Public metadata/package validation ownership.

The former Day71 fixed-candidate and Day72 final-readiness contracts are also retired. They predated accepted Web screenshot enforcement and were superseded by the Day80 accepted manifest plus the Day82/Day83 fixed-ZIP gates.

Current release-safety ownership is:

```text
Public metadata and forbidden-surface inspection: Public-P2
Accepted real Web evidence aggregate: Day80
Final unchanged fixed-ZIP verification: Day82
Final fixed-ZIP readiness: Day83
Immutable Public artifact binding: final artifact record
```

Cleanup-6 does not alter accepted real-execution evidence, build a release ZIP, move tags, publish a repository, or claim release completion.

## v2.0.0 Day64 real LLM Web answer execution evidence

Day64 starts the real execution evidence phase for the first v2.0.0 completion requirement. It builds on the Day52 evidence gate and adds marker-only acceptance for a configured operator run that proves both the DRC backend API response and the smartphone Web UI visible answer.

Expected marker:

```text
v200_real_llm_web_answer_execution_evidence_status: operator-execution-evidence-contract-ready
```

Day64 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_llm_web_answer_execution_day64.py
# canonical path: scripts/check_v200_real_llm_web_answer_execution_day64.py

cd app
flutter test
cd ..
```

See [docs/v200_real_llm_web_answer_execution_evidence.md](docs/v200_real_llm_web_answer_execution_evidence.md).

Configured real LLM execution evidence remains operator-only. Accepted evidence requires `source.engine=framework`, a non-empty backend `/advice` message, and a non-empty smartphone Web UI visible answer. `mock`, `framework_fallback`, `skipped`, `unavailable`, and `error` states must not be counted as real execution success. Public evidence must remain marker-only and must not include API keys, prompt bodies, answer bodies, raw provider payloads, raw LAN IPs, private paths, or raw screenshots.

Day64 does not complete v2.0.0 by itself. Real TTS Web audio output, real Google Health sleep data, Web image display, public repo final sweep, final aggregate verification, and fixed v2.0.0 release zip verification remain required.
## v2.0.0 Day65 real TTS Web audio output execution evidence

Day65 continues the real execution evidence phase for the second v2.0.0 completion requirement. It builds on the Day53 provider gate and Day54 evidence gate, then adds marker-only acceptance for a configured operator run that proves real provider synthesis, safe backend audio exposure, and audible smartphone Web playback.

Expected marker:

```text
v200_real_tts_web_audio_execution_evidence_status: operator-execution-evidence-contract-ready
```

Day65 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_tts_web_audio_execution_day65.py
# canonical path: scripts/check_v200_real_tts_web_audio_execution_day65.py

cd app
flutter test
cd ..
```

See [docs/v200_real_tts_web_audio_execution_evidence.md](docs/v200_real_tts_web_audio_execution_evidence.md).

Configured real TTS Web audio execution evidence remains operator-only. Accepted evidence requires the AI Character Framework voice output boundary, the neutral DRC voice contract, real provider synthesis, safe backend audio exposure, and audible smartphone Web playback. `mock`, `framework_fallback`, `provider_unavailable`, `synthesis_failed`, `playback_failed`, `skipped`, `unavailable`, and `error` states must not be counted as real TTS success. Public evidence must remain marker-only and must not include API keys, private text bodies, provider voice IDs, raw provider payloads, generated audio artifacts, raw audio URLs, raw LAN IPs, private paths, or raw screenshots.

Day65 does not complete v2.0.0 by itself. Real Google Health sleep data, Web image display, public repo final sweep, final aggregate verification, and fixed v2.0.0 release zip verification remain required.
## v2.0.0 Day66 real Google Health sleep data execution evidence

Day66 continues the real execution evidence phase for the third v2.0.0 completion requirement. It builds on the Day55 evidence gate and adds marker-only acceptance for a configured operator run that proves real Google Health API use, real sleep-data fetch success, SleepSummary normalization, backend real-data source confirmation, and smartphone Web UI real-source confirmation.

Expected marker:

```text
v200_real_google_health_sleep_data_execution_evidence_status: operator-execution-evidence-contract-ready
```

Day66 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_google_health_sleep_data_execution_day66.py
# canonical path: scripts/check_v200_real_google_health_sleep_data_execution_day66.py

cd app
flutter test
cd ..
```

See [docs/v200_real_google_health_sleep_data_execution_evidence.md](docs/v200_real_google_health_sleep_data_execution_evidence.md).

Configured real Google Health sleep-data execution evidence remains operator-only. Accepted evidence requires explicit opt-in, the real Google Health API gate, OAuth availability, real API request confirmation, real sleep-data fetch success, SleepSummary normalization, backend real-data source confirmation, and smartphone Web UI real-source confirmation. `mock_data`, `fixture_data`, `fallback_data`, `simulated_data`, `skipped`, `unavailable`, `oauth_missing`, `token_invalid`, `api_failed`, `normalization_failed`, `backend_not_called`, `web_ui_not_confirmed`, and `error` states must not be counted as real Google Health success. Public evidence must remain marker-only and must not include client secrets, tokens, authorization headers, raw health payloads, raw sleep events, precise personal sleep timestamps, raw LAN IPs, private paths, raw screenshots, browser storage dumps, or local token files.

Day66 does not complete v2.0.0 by itself. Web image display, public repo final sweep, final aggregate verification, and fixed v2.0.0 release zip verification remain required.


## v2.0.0 Day67 image asset generation and repository-safe intake

Day67 continues the real execution evidence phase for the fourth v2.0.0 completion requirement. It builds on the Day56 Web image display evidence gate and adds marker-only acceptance for a configured operator review that confirms generated or sourced app image assets are public-safe before they are committed, registered, displayed, or packaged.

Day67 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_image_asset_generation_intake_day67.py

cd app
flutter test
cd ..
```

Day67 canonical paths:

```text
docs/v200_image_asset_generation_intake_evidence.md
docs/operator_evidence_templates/v200_image_asset_generation_intake_day67.example.json
backend/app/services/framework_v200_image_asset_generation_intake_evidence.py
scripts/smoke_framework_v200_image_asset_generation_intake_evidence.py
scripts/check_v200_image_asset_generation_intake_day67.py
```

Day67 does not generate images in the default source-tree check, does not call image-generation services, does not commit unreviewed artifacts, does not register Flutter assets, does not open a browser, does not validate screenshots, and does not create release artifacts. It records the asset-generation/intake evidence contract only; configured image generation and repository-safe asset intake remain explicit operator opt-in.

Day67 does not complete v2.0.0 by itself. Web image display execution evidence, public repo final sweep, final aggregate verification, and fixed v2.0.0 release zip verification remain required.

## v2.0.0 Day68 Web image display execution evidence

Day68 continues the real execution evidence phase for the fourth v2.0.0 completion requirement. It builds on the Day56 Web image display evidence gate and Day67 repository-safe image asset intake, then adds marker-only acceptance for a configured operator run that proves reviewed image assets or placeholders are registered and visible in the actual Flutter Web UI, including smartphone Web confirmation.

Expected marker:

```text
v200_web_image_display_execution_evidence_status: operator-execution-evidence-contract-ready
```

Day68 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_web_image_display_execution_day68.py
# canonical path: scripts/check_v200_web_image_display_execution_day68.py

cd app
flutter test
cd ..
```

See [docs/v200_web_image_display_execution_evidence.md](docs/v200_web_image_display_execution_evidence.md).

Configured Web image display execution evidence remains operator-only. Accepted evidence requires accepted Day67 asset-intake evidence, public-safe assets in the app tree, Flutter asset manifest registration, Flutter Web runtime display, smartphone Web display, real app route confirmation, missing-image fallback confirmation, and public-safe marker-only evidence. `day67_not_accepted`, `unreviewed_asset`, `missing_asset_manifest_registration`, `flutter_web_not_confirmed`, `smartphone_web_not_confirmed`, `static_file_preview_only`, `skipped`, `unavailable`, `fallback_only`, and `error` states must not be counted as Web image display success. Public evidence must not include raw screenshots, raw LAN IPs, private paths, browser storage dumps, raw prompts, raw generation metadata, or unreviewed image work folders.

Day68 does not complete v2.0.0 by itself. Public repo final sweep, final aggregate verification, and fixed v2.0.0 release zip verification remain required.

## v2.0.0 Day69 public repo readiness final sweep

Day69 continues the real execution evidence phase for the fifth v2.0.0 completion requirement. It builds on the Day57 public repo readiness / LICENSE / secret hygiene gate and reviews the Day64 through Day68 marker-only execution evidence layers before the v2.0.0 final aggregate gate.

Expected marker:

```text
v200_public_repo_final_sweep_status: public-repo-final-sweep-contract-ready
```

Day69 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_public_repo_final_sweep_day69.py
# canonical path: scripts/check_v200_public_repo_final_sweep_day69.py

cd app
flutter test
cd ..
```

See [docs/v200_public_repo_final_sweep.md](docs/v200_public_repo_final_sweep.md).

Configured public repo final sweep evidence remains operator-only. Accepted evidence requires Day57 public readiness review plus Day64, Day65, Day66, Day67, and Day68 evidence review, LICENSE scope confirmation, public positioning review, secret-hygiene final scan, release-surface local artifact absence, raw evidence material exclusion, and mock-safe default preservation. `skipped`, `unavailable`, `fallback_only`, raw evidence, private path, replacement bundle, extracted workdir, production/store claim, and medical claim states must not be counted as success.

Day69 does not complete v2.0.0 by itself. Final aggregate verification and fixed v2.0.0 release zip verification remain required.


## v2.0.0 Day70 final prerelease aggregate gate

Day70 continues the v2.0.0 real execution evidence phase as the final prerelease aggregate gate before building one fixed v2.0.0 release candidate zip.

Expected marker:

```text
v200_final_prerelease_aggregate_gate_status: final-prerelease-aggregate-contract-ready
```

Day70 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_final_prerelease_aggregate_gate_day70.py
# canonical path: scripts/check_v200_final_prerelease_aggregate_gate_day70.py

cd app
flutter test
cd ..
```

See [docs/v200_final_prerelease_aggregate_gate.md](docs/v200_final_prerelease_aggregate_gate.md).

Configured final prerelease aggregate evidence remains operator-only. Accepted evidence requires Day52-Day58 foundation gates, Day64 real LLM Web answer evidence, Day65 real TTS Web audio evidence, Day66 real Google Health evidence, Day67 image intake evidence, Day68 Web image display evidence, Day69 public repo final sweep, API-level evidence review, smartphone Web evidence review, no fallback/skipped/unavailable success counting, and mock-safe credential-free defaults. Day70 does not build, create, inspect, or verify a release zip.

Day70 does not complete fixed release package verification by itself. After Day70 passes, build one fixed v2.0.0 release candidate zip, record its exact path, and run fixed-zip verification against that same artifact without rebuilding.

## v2.0.0 retired Day71/Day72 fixed-candidate path

Cleanup-6 removes the former Day71/Day72 implementation and command path. The authoritative fixed-artifact sequence is Public-P2 plus Day82 and Day83 against the same unchanged ZIP.

## v2.0.0 Day73 accepted Web screenshot evidence enforcement

Day73 established the accepted-Web-evidence correction to the earlier pre-Web readiness interpretation: passing source-tree gates, API-only smokes, or fixed-zip checks is not enough to complete v2.0.0.

v2.0.0 completion requires accepted Web execution screenshot evidence for each Web-executed real capability. The Web UI must use the actual Daily Rhythm Companion backend API, and the operator evidence must include screenshot confirmation of the visible Web result.

Day73 source-tree check:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_accepted_web_screenshot_evidence_day73.py

cd app
flutter test
cd ..
```

Day73 validates:

```text
- docs/v200_accepted_web_screenshot_evidence_enforcement.md
- docs/operator_evidence_templates/v200_accepted_web_screenshot_evidence_day73.example.json
- backend/app/services/framework_v200_accepted_web_screenshot_evidence_enforcement.py
- scripts/smoke_framework_v200_accepted_web_screenshot_evidence_enforcement.py
- scripts/check_v200_accepted_web_screenshot_evidence_day73.py
```

Accepted evidence must cover:

```text
- real LLM Web answer generation screenshot evidence
- real TTS Web audio output screenshot evidence and audible playback confirmation
- real Google Health sleep data Web result screenshot evidence
- Web image display screenshot evidence
- image asset intake acceptance
- public repo final sweep acceptance
- final aggregate review acceptance
```

API-only smoke does not count as v2.0.0 completion. Source-tree-only checks do not count. Mock, fallback, skipped, unavailable, placeholder, and error states do not count. Web execution screenshot evidence must be reviewed before any v2.0.0 tag/release decision.

Raw screenshots must not be committed to the public repository or included in the release zip. Public records should use redacted screenshot references only.

If Day73 is added after a fixed v2.0.0 release candidate zip was already built, that previous zip is invalidated for final v2.0.0 release handling. After Day73 passes, build one new fixed release candidate zip and restart fixed-zip verification.


## v2.0.0 Day76 real LLM Web screenshot evidence capture

Day76 starts the real Web execution evidence capture phase with the real LLM Web answer requirement.
It does not call external providers or the browser in default checks. Instead, it defines and validates the private operator evidence item that must be produced after the operator runs the Daily Rhythm Companion Web UI against the actual DRC backend API with a real configured LLM provider.

The Day76 private evidence item must prove that the LLM result was executed through Web, the Web UI displayed a real provider-backed answer, the actual DRC backend API was used, and a screenshot confirmation exists in private operator evidence storage. API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, or screenshot-missing evidence is rejected.

Run:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_llm_web_screenshot_day76.py
```

After this check passes, the operator can run the private real Web LLM flow and validate the private evidence item with:

```powershell
python scripts\smoke_framework_v200_real_llm_web_screenshot_evidence.py --evidence-json "<private-real-llm-web-evidence-json>"
```

The accepted Day76 item is summarized by the Day80 accepted Web evidence manifest under `real_llm_web_answer`.


## v2.0.0 Day77 real TTS Web audio screenshot evidence capture

Day77 continues the real Web execution evidence capture phase with the real TTS Web audio output requirement. It does not synthesize audio, start the backend, open Flutter Web, or inspect screenshots in default checks. Instead, it defines and validates the private operator evidence item that must be produced after the operator runs the Daily Rhythm Companion Web UI against the actual DRC backend API with a real configured TTS provider and confirms Web audio output.

The Day77 private evidence item must prove that the TTS result was executed through Web, the Web UI displayed the audio output result, the actual DRC backend API was used, real TTS provider audio was confirmed, Web audio playback was confirmed, and a screenshot confirmation exists in private operator evidence storage. API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, or screenshot-missing evidence is rejected.

Run:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_tts_web_audio_screenshot_day77.py
python scripts\check_v200_real_llm_web_screenshot_day76.py
```

After this check passes, the operator can run the private real Web TTS audio flow and validate the private evidence item with:

```powershell
python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py --evidence-json "<private-real-tts-web-audio-evidence-json>"
```

The accepted Day77 item is summarized by the Day80 accepted Web evidence manifest under `real_tts_web_audio_output`.


## v2.0.0 Day78 real Google Health Web sleep screenshot evidence capture

Day78 continues the real Web execution evidence capture phase with the real Google Health sleep data requirement. It does not call Google Health, start the backend, open Flutter Web, or inspect screenshots in default checks. Instead, it defines and validates the private operator evidence item that must be produced after the operator runs the Daily Rhythm Companion Web UI against the actual DRC backend API with real Google Health access and confirms a visible sleep summary result.

The Day78 private evidence item must prove that the sleep result was executed through Web, the Web UI displayed Google Health-backed sleep data, the actual DRC backend API was used, real Google Health API access was confirmed, the result was normalized into SleepSummary, and a screenshot confirmation exists in private operator evidence storage. API-only, source-tree-only, command-output-only, mock, fallback, skipped, unavailable, placeholder, or screenshot-missing evidence is rejected.

Run:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_real_google_health_web_sleep_screenshot_day78.py
python scripts\check_v200_real_tts_web_audio_screenshot_day77.py
```

After this check passes, the operator can run the private real Web Google Health sleep flow and validate the private evidence item with:

```powershell
python scripts\smoke_framework_v200_real_google_health_web_sleep_screenshot_evidence.py --evidence-json "<private-real-google-health-web-sleep-evidence-json>"
```

The accepted Day78 item is summarized by the Day80 accepted Web evidence manifest under `real_google_health_sleep_data`.


## v2.0.0 Day79 Web image display screenshot evidence capture

Day79 continues the real Web execution evidence capture phase with the Web image display requirement. It does not generate images, copy image assets, start the backend, open Flutter Web, or inspect screenshots in default checks. Instead, it defines and validates the private operator evidence item that must be produced after the operator runs the Daily Rhythm Companion Web UI against the actual DRC backend API and confirms that the repository-safe image asset is visibly rendered in Web.

The Day79 private evidence item must prove that the image display result was executed through Web, the Web UI displayed the accepted repository-safe image asset, the actual DRC backend API was used, the Day67 image asset intake review was accepted, and a screenshot confirmation exists in private operator evidence storage. API-only, source-tree-only, command-output-only, generated-but-not-displayed, mock, fallback, skipped, unavailable, placeholder, or screenshot-missing evidence is rejected.

Run:

```powershell
python -m compileall -q backend scripts
python scripts\check_v200_web_image_display_screenshot_day79.py
python scripts\check_v200_real_google_health_web_sleep_screenshot_day78.py
```

After this check passes, the operator can run the private Web image display flow and validate the private evidence item with:

```powershell
python scripts\smoke_framework_v200_web_image_display_screenshot_evidence.py --evidence-json "<private-web-image-display-screenshot-evidence-json>"
```

The accepted Day79 item is summarized by the Day80 accepted Web evidence manifest under `web_image_display`.

## v2.0.0 Day82 fixed release zip verification with accepted Web evidence

Doc: `docs/v200_fixed_release_zip_with_web_evidence_verification.md`

Day82 returns the v2.0.0 flow to fixed release zip verification after Day80 private evidence acceptance. Commit G-6 removes the remaining marker-only gap before the final artifact is created. The final builder uses a detached temporary Git worktree at the recorded committed `HEAD`, requires an explicit `ManifestPath` to the accepted Day80 manifest outside the Public repository, validates that manifest without copying or printing its path, invokes `build_release.bat release` exactly once, and moves that one artifact into `release/` without rebuilding or overwriting it. The package builder explicitly excludes the worktree `.git` metadata file so its private administrative path cannot enter the zip.

Day82 does not create or rebuild the release zip. It runs `check_release_package.py`, opens the supplied zip directly, verifies CRC integrity, requires exactly one `DailyRhythmCompanion` package root, checks required release entries, rejects forbidden/private entries, records the zip basename, size, and SHA-256, and confirms the artifact did not change during inspection. Marker-only Day82 evidence is rejected unless the same fixed zip is also supplied with `--release-zip`.

After G-6 is committed and pushed, and after the source tree and Flutter tests pass, build the final zip once:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py

cd app
flutter test
cd ..

$manifest = "<absolute path to accepted Day80 manifest outside Public repository>"
.\build_v200_final_fixed_release_zip_from_head.ps1 -ManifestPath $manifest
```

Copy the exact `v200_final_fixed_release_zip_path` printed by the builder and verify that same artifact without running the builder again:

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"

python scripts\check_release_package.py $zip

# Optional package-only inspection; this does not accept Day82.
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py `
  --release-zip $zip `
  --inspect-zip-only

# Day82 acceptance requires evidence bound to this exact ZIP.
python scripts\smoke_framework_v200_fixed_release_zip_with_web_evidence_verification.py `
  --release-zip $zip `
  --evidence-json "<private-Day82-marker-json>"
```

The same `$zip` must then be reused for Day83, tag, and GitHub Release handling. Any committed source, documentation, release rule, or release-surface change invalidates that artifact and requires a new one-time build from the new committed `HEAD`.


## v2.0.0 Day83 final release readiness fixed-zip gate with accepted Web evidence

Day83 reuses and directly reopens the exact fixed zip that passed Day82. It runs the release-package hygiene check again, preserves the Day82 CRC/package-root/required/forbidden/unchanged-artifact rules, additionally requires the Day83 final readiness release surface, and rejects marker-only Day83 acceptance when `--release-zip` is absent. It does not rebuild, modify, tag, publish, call providers, call Google Health, start Flutter Web, or inspect raw screenshots.

Doc: `docs/v200_final_release_readiness_fixed_zip_with_web_evidence.md`
Check: `scripts/smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py`

```powershell
$zip = "release\DailyRhythmCompanion_YYYYMMDD_HHMMSS.zip"

python scripts\smoke_framework_v200_final_release_readiness_fixed_zip_with_web_evidence.py `
  --release-zip $zip `
  --evidence-json "<private-Day83-marker-json>"
```

The `$zip` value must be identical to the artifact path used for Day82. Source-tree-only Day83 output does not authorize tagging or release.

## v2.0.0 G-7 / Public-P4 immutable final release artifact record

Doc: `docs/v200_final_release_artifact_record.md`
Check: `scripts/smoke_framework_v200_final_release_artifact_record.py`

G-7 resolved the final-build bookkeeping cycle for the original same-repository topology. Public-P4 updates that contract for `murayan1982/daily-rhythm-companion-public`: the committed Public `main` HEAD, official Public origin, exactly one root commit, no Private Git history, and no legacy `develop_head` field. No post-build source or documentation commit is allowed.

The public-safe final outcome is recorded in both the annotated `DRC_v2.0.0` tag message and GitHub Release body. The record binds the full Public source HEAD, matching Public `main` and annotated tag target, ZIP basename, byte size, SHA-256, Day82/Day83 acceptance, one-root/no-Private-history verification, and same-artifact/public-safety markers. It must not contain Private repository commit IDs, private evidence, raw screenshots/audio/health data, private paths, LAN IPs, provider payloads, tokens, or credentials.

Source-tree check before the final one-time build:

```powershell
python -m compileall -q backend scripts
python scripts\smoke_framework_v200_final_release_artifact_record.py
```

Any fixed ZIP built from an earlier source state is not the final artifact after the Public-P6 pre-build follow-ups change the release surface. Build only after the final Public pre-build synchronization commit is committed and pushed, `HEAD == origin/main`, the working tree is clean, and all source-tree and Flutter checks pass.
