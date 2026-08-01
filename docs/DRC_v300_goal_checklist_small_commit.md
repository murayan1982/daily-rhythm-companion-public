# Daily Rhythm Companion v3.0.0 goal checklist and small-commit plan

Updated: 2026-08-01
```text
Current released version: v2.1.0 RELEASED / ACCEPTED
Current released metadata: Backend 2.1.0 / Flutter 2.1.0+3
Strategic target: v3.0.0
Current parent phase: RT-5 CURRENT / NOT_COMPLETED
Current small commit: none
Current implementation step: RT-5f3 default-off configured integrated voice-turn wiring accepted
Current implementation state: COMPLETED / ACCEPTED
Current implementation baseline: 888814d09fad75039733a4a94719454e0a69db63
Current implementation commit: 75504424c37222234ea8a4314d01ce386ff92d23
Last accepted small commit: RT-5f3 default-off HomeScreen and production speech-activity wiring COMPLETED / ACCEPTED / PUSHED at 75504424c37222234ea8a4314d01ce386ff92d23
Accepted RT-4c implementation: 72622cab2e73699adaff4b628cfbc4b14323a23a
Next implementation action: prepare a separate exact RT-5f4 contract review; RT-5f4 remains NOT_AUTHORIZED
```

## Source of truth

This file is the active v3.0.0 small-commit checklist.

Supporting RT-0 inventories and checks:

```text
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
docs/v300_framework_v520_contract_adoption.md
scripts/check_v300_framework_v520_contract_adoption.py
docs/v300_backend_realtime_normalization.md
scripts/check_v300_backend_realtime_normalization.py
docs/v300_microphone_permission_capture_inventory.md
scripts/check_v300_microphone_permission_capture_inventory.py
docs/v300_microphone_permission_contract.md
scripts/check_v300_microphone_permission_contract.py
docs/v300_microphone_platform_permission_wiring.md
scripts/check_v300_microphone_platform_permission_wiring.py
docs/v300_framework_v530_stt_integration_inventory.md
scripts/check_v300_framework_v530_stt_integration_inventory.py
docs/v300_framework_real_stt_requirement_feedback.md
scripts/check_v300_framework_real_stt_requirement_feedback.py
docs/v300_framework_v540_real_stt_adoption_inventory.md
scripts/check_v300_framework_v540_real_stt_adoption_inventory.py
docs/v300_rt3d2a_framework_v540_executor_path_correction.md
scripts/check_v300_rt3d2a_framework_v540_executor_path_correction.py
docs/v300_rt3d2b_bounded_marked_fake_executor_wiring.md
scripts/check_v300_rt3d2b_bounded_marked_fake_executor_wiring.py
docs/v300_rt4_streaming_cancel_current_behavior_inventory.md
scripts/check_v300_rt4_streaming_cancel_current_behavior_inventory.py
docs/v300_rt4_backend_stream_contract.md
scripts/check_v300_rt4_backend_stream_contract.py
docs/v300_rt5_tts_output_control_current_behavior_inventory.md
scripts/check_v300_rt5_tts_output_control_current_behavior_inventory.py
docs/v300_rt5b_voice_output_queue_contract.md
scripts/check_v300_rt5b_voice_output_queue_contract.py
docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md
scripts/check_v300_rt5c_realtime_terminal_voice_output_orchestration_contract.py
docs/v300_rt5d_home_screen_voice_output_controls.md
scripts/check_v300_rt5d_home_screen_voice_output_controls.py
```

Historical release sources remain immutable:

```text
docs/DRC_v200_goal_checklist_small_commit.md
docs/DRC_v20x_maintenance_checklist.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_record.md
release_notes/v2.0.0.md
release_notes/v2.0.1.md
release_notes/v2.1.0.md
DRC_v2.0.0 / DRC_v2.0.1 / DRC_v2.1.0 tags and GitHub Releases
```

## Accepted RT-5a through RT-5e checkpoints

```text
RT-5 CURRENT / NOT_COMPLETED
RT-5a COMPLETED / ACCEPTED / PUSHED
RT-5b COMPLETED / ACCEPTED / PUSHED
RT-5c COMPLETED / ACCEPTED / PUSHED
RT-5d COMPLETED / ACCEPTED / PUSHED
RT-5e COMPLETED / ACCEPTED / PUSHED
RT-5f CURRENT / NOT_COMPLETED
RT-5f0 COMPLETED / ACCEPTED / PUSHED
RT-5f1 COMPLETED / ACCEPTED / PUSHED
RT-5f2 COMPLETED / ACCEPTED / PUSHED
RT-5f3 COMPLETED / ACCEPTED / PUSHED
RT-5f4 NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

RT-5a is docs/test-only. It inventories current DRC Backend voice-output
request behavior, current Flutter local playback behavior, the current absence
of app-owned queue/flush/cancel/barge-in runtime, released FW v5.4.0
root-public output-control data contracts, readiness classification, exact
seven-file change surface, explicit non-change surface, credential-free
verification, and the stop rule.

RT-5 readiness classification:

```text
PARTIAL_READY_FOR_DRC_APP_OWNED_QUEUE_AND_LOCAL_PLAYBACK_FLUSH
```

RT-5a acceptance passed on 2026-07-30 at implementation commit `1cf77774dca75b9875099c2b6c6c03992456d80f` with compileall, the dedicated candidate gate, Backend 192 passed with one existing warning, Flutter analyze, Flutter 278 passed, exact seven-file review, privacy scan, `git diff --check`, explicit operator approval, commit, and push.

RT-5b is COMPLETED / ACCEPTED / PUSHED at implementation commit
`c48238256cb0b17c925f8063c3b636d3b4ccf533` under the exact Flutter-only fake/in-memory contract
below. This does not authorize HomeScreen, Backend/FW/provider execution, real
audio playback, automatic TTS, hard cancel, barge-in, or RT-5c.
RT-5c was later separately reviewed and authorized and is now
COMPLETED / ACCEPTED / PUSHED at implementation commit `f00214cd7e75b28c041728bca6ffc3b180face80`.
RT-5d was later separately reviewed and authorized for the exact ten-file
fake-only HomeScreen implementation and is now COMPLETED / ACCEPTED /
PUSHED at implementation commit `eff46a3b4de771aa37a48ea9ef5959918e407200`.
RT-5e is COMPLETED / ACCEPTED / PUSHED at implementation commit
`ef5f96337b5f601277a9bcc38b9e6fedc520b0a6` under the separately authorized exact thirteen-file contract after
configured real synthesis, natural audible playback, explicit binding-owned
playback-stop, cleanup, and clean-tree verification passed. RT-5f0 is
COMPLETED / ACCEPTED / PUSHED at `348669884e872475aaa4242a5960a6de6fb7e10b` as the exact seven-file
docs/test-only readiness checkpoint. RT-5f1 is COMPLETED / ACCEPTED / PUSHED at `daca3a68672eb3106e861278ebb65612380140ed` after the exact seventeen-file implementation, full synthetic verification, explicit approval, push, and clean-tree verification passed. RT-5f2 is COMPLETED / ACCEPTED / PUSHED through `c538dc89c2aa9780cd3014aa4ba11c17a9e378e6` and `b7bd436196210f27782b64c1a094aa65d6893915`. RT-5f3 is COMPLETED / ACCEPTED / PUSHED at `75504424c37222234ea8a4314d01ce386ff92d23` after the dedicated gate, Backend 204, Flutter analyze, focused Flutter 53, Flutter full 408, exact surface/privacy review, explicit commit approval, push, and clean DRC working tree passed. Real operator acceptance remains outside RT-5f3. RT-5f4 is ready only for a separate exact contract review and remains NOT_AUTHORIZED.


## RT-5f1 accepted implementation checkpoint

```text
RT-5f1 COMPLETED / ACCEPTED / PUSHED
implementation commit: daca3a68672eb3106e861278ebb65612380140ed
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
change surface: exact seventeen files
RT-5f2: COMPLETED / ACCEPTED / PUSHED
```

- [x] Add default-off `VOICE_INPUT_REAL_STT_ENABLED`.
- [x] Add body-only `POST /demo/voice-input/transcript`.
- [x] Check credential and FW root before consuming staged audio.
- [x] Enforce process-wide single-flight without consuming on busy.
- [x] Reuse FW root-public real-executor assembly only.
- [x] Return exact provider-neutral final transcript response with no-store.
- [x] Bound transcript to 4096 Unicode code points.
- [x] Add Flutter Backend transcript provider with one-shot artifact ownership.
- [x] Reject redirects, oversized responses, missing no-store, and extra keys.
- [x] Verify compatibility with existing transcript-to-stream handoff.
- [x] Add synthetic Backend and Flutter tests.
- [x] Keep main.dart, HomeScreen, private env, FW, TTS, speech activity, and barge-in unchanged.
- [x] Review exact seventeen-file diff and Windows Flutter results.
- [x] Explicit RT-5f1 commit and push approval.
- [x] Push implementation and verify clean DRC/FW working trees.

Acceptance verification:

```text
compileall: passed
dedicated RT-5f1 pre-commit gate: passed
focused Backend tests: 12 passed
Backend full tests: 204 passed, 1 existing warning
Flutter analyze: passed
focused Flutter tests: 12 passed
Flutter full tests: 355 passed
exact implementation surface: 17 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
post-push DRC/FW working trees: clean
```

Detailed accepted contract:
`docs/v300_rt5f1_app_visible_real_stt_contract.md`.
Historical pre-commit gate:
`scripts/check_v300_rt5f1_app_visible_real_stt_contract.py`.

## RT-5f0 accepted readiness checkpoint

```text
RT-5f0 COMPLETED / ACCEPTED / PUSHED
implementation commit: 348669884e872475aaa4242a5960a6de6fb7e10b
FW v5.4.0 HEAD: d313eb6acb643103fe25988720ebee5976a04f78
RT-5f1 COMPLETED / ACCEPTED / PUSHED
RT-5f2 COMPLETED / ACCEPTED / PUSHED
```

- [x] Accepted RT-3d3 real STT remains private operator-only.
- [x] App-visible real-STT route/provider is absent.
- [x] Provider-neutral transcript handoff exists and remains unconfigured in normal startup.
- [x] Normal `main.dart` contains no microphone or real-STT assembly.
- [x] Production recorder boundary contains no speech-onset/amplitude event.
- [x] RT-5e queue generation/operation epoch reject stale output.
- [x] RT-5e explicit flush requests binding-owned local playback stop.
- [x] Backend HTTP and provider synthesis cancellation remain absent.
- [x] FW root-public capability probe reports real runtime false.
- [x] FW root-public capability probe reports TTS queue flush false.
- [x] FW root-public capability probe reports hard cancel false.
- [x] Final RT-5f claim is limited to DRC-local soft barge-in.
- [x] Exact RT-5f1 through RT-5f4 split is frozen.
- [x] Exact seven-file docs/test-only implementation surface is frozen.
- [x] Runtime, existing tests, dependency, private env, provider execution, audio, transcript, version, and release records remain unchanged.
- [x] RT-5f0 explicit review and acceptance.
- [x] RT-5f0 implementation commit and push.
- [x] Separate RT-5f1 exact contract review and explicit implementation authorization.

Readiness classification:

```text
PARTIAL_READY_FOR_APP_VISIBLE_REAL_STT_AND_DRC_LOCAL_SOFT_BARGE_IN
```

Acceptance verification:

```text
compileall: passed
dedicated RT-5f0 pre-commit gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 343 passed
exact implementation surface: 7 files
changed-content privacy review: passed
git diff --check: passed
explicit operator approval: accepted
implementation push: completed
post-push working tree: clean
```

Accepted contract and stop rule:
`docs/v300_rt5f_readiness_and_exact_split.md`.
Historical pre-commit gate:
`scripts/check_v300_rt5f_readiness_and_exact_split.py`.

The gate remains bound to the pre-commit baseline and exact seven-file
candidate. It is retained as historical evidence and is not rerun for the
six-file docs-only acceptance sync.

## Accepted RT-5b checkpoint

```text
RT-5b COMPLETED / ACCEPTED / PUSHED
RT-5c at this checkpoint: NOT_STARTED / NOT_AUTHORIZED
```

Contract:

```text
pending FIFO maximum: 8
utterance maximum: 4096 Unicode code points
retained active + pending maximum: 16384 Unicode code points
active claim maximum: 1
flush generation invalidates late results: true
concurrent flush local stop calls: 1
public state contains utterance text: false
HomeScreen / Backend / Framework / provider / real audio: unchanged
```

Exact implementation surface: nine files listed in
`docs/v300_rt5b_voice_output_queue_contract.md`. Focused tests use only an
in-memory queue and fake local playback-stop callback. RT-5b acceptance
passed on 2026-07-30 at implementation commit `c48238256cb0b17c925f8063c3b636d3b4ccf533`
with Dart formatting, compileall, the dedicated candidate gate, Backend 192
passed with one existing warning, Flutter analyze, 15 focused Flutter tests,
293 full Flutter tests, exact nine-file review, changed-content privacy review,
`git diff --check`, explicit operator approval, commit, and push.

The dedicated gate remains a historical pre-commit candidate gate and is not
rerun for this docs-only acceptance sync. RT-5b acceptance did not itself start
or authorize RT-5c; RT-5c was later separately reviewed and authorized.

## Accepted RT-5c checkpoint

```text
RT-5c COMPLETED / ACCEPTED / PUSHED
RT-5d NOT_STARTED / NOT_AUTHORIZED
baseline HEAD / origin/main: 5fcac869f81e1070e854550f4376353e109905e5
implementation commit: f00214cd7e75b28c041728bca6ffc3b180face80
```

Accepted contract:

```text
explicit completed-terminal enqueue: true
automatic realtime listener: false
automatic queue drain: false
one item per explicit processNext: true
private completed-terminal dedup window: 32
opaque audio URI maximum: 2048 Unicode code points
accepted URI: absolute HTTP(S), host, no user-info/fragment/controls/backslash
fake synthesis outcomes: audioReady / rejected / failed
fake terminal playback outcomes: completed / failed / expired / stopped
queue complete only after playback completed: true
operation epoch plus queue generation/item revalidation: true
flush releases new-generation process slot: true
public state contains terminal text / IDs / URI / raw error: false
```

Exact nine-file surface is recorded in
`docs/v300_rt5c_realtime_terminal_voice_output_orchestration_contract.md`.
Focused tests are fake/in-memory only. No HomeScreen, Backend HTTP, existing real
player, Framework/provider, real synthesis, real audio playback, automatic TTS,
Framework real output flush, provider hard cancel, or speech-triggered barge-in
is added.

RT-5c acceptance passed on 2026-07-31 at implementation commit
`f00214cd7e75b28c041728bca6ffc3b180face80` with Dart formatting, compileall, the dedicated
candidate gate, Backend 192 passed with one existing warning, Flutter analyze,
22 focused Flutter tests, 315 full Flutter tests, exact nine-file review,
changed-content privacy review, `git diff --check`, explicit operator approval,
commit, and push.

The dedicated gate remains a historical pre-commit candidate gate bound to
baseline `5fcac869f81e1070e854550f4376353e109905e5` and the exact nine-file
surface. It is not rerun for the later six-document acceptance sync. RT-5c
acceptance did not itself start or authorize RT-5d; RT-5d was later separately
reviewed and authorized under the candidate contract below.

## Accepted RT-5e checkpoint

```text
RT-5e COMPLETED / ACCEPTED / PUSHED
implementation commit: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
private operator acceptance: passed
DRC HEAD / origin/main: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
FW HEAD: d313eb6acb643103fe25988720ebee5976a04f78
RT-5f NOT_STARTED / BLOCKED_READINESS / NOT_AUTHORIZED
```

Accepted configured runtime contract:

```text
default-off Flutter runtime: true
existing Backend /demo/voice-output only: true
FW root-public create_voice_output_session().create_output only: true
one queued item per explicit process action: true
exact generated URL/MP3 contract required: true
binding-owned dedicated player: true
existing Voice Output Demo player shared: false
automatic enqueue/drain: false
explicit queue/local-player flush: true
Backend HTTP/provider hard cancel: false
FW real flush: false
speech-triggered barge-in: false
real-STT-to-stream-to-TTS: false
```

Implementation verification passed with compileall, the dedicated RT-5e gate,
FW root-public voice-output smoke, Backend 192 passed with one existing warning,
Flutter analyze, 82 focused Flutter tests, 343 full Flutter tests, exact
thirteen-file review, HomeScreen semantic-only `+6/-6`, changed-content privacy
review, `git diff --check`, explicit approval, commit, and push.

Private configured operator acceptance passed on 2026-07-31:

```text
configured runtime visible with opt-in default off: true
completed realtime terminal: confirmed
explicit enqueue: accepted
real FW root-public synthesis: accepted
natural audible playback completion: accepted
second active playback before flush: confirmed
explicit flush: completed
cleared pending: 0
local playback stop requested: true
local playback stop succeeded: true
audible playback interruption: confirmed
final phase / pending / active: idle / 0 / no
operator artifact files removed: 3
operator artifacts remaining: false
private logs/backups removed or restored: true
FW real provider gates restored disabled: true
DRC/FW working trees after cleanup: clean
private evidence committed or pushed: false
```

The exact implementation and public-safe acceptance record is
`docs/v300_rt5e_configured_local_voice_output_acceptance.md`. The dedicated
source gate remains historical and is not rerun for this six-document
acceptance sync.

No Backend/FW source change, DRC provider client, FW internal import, automatic
TTS, automatic queue drain, Backend HTTP cancellation, provider hard cancel,
FW real flush, speech-triggered barge-in, or real-STT-to-TTS is claimed.

RT-5 remains CURRENT / NOT_COMPLETED. RT-5e acceptance does not start or
authorize RT-5f.

## Accepted RT-5d checkpoint

```text
RT-5d COMPLETED / ACCEPTED / PUSHED
RT-5e state at RT-5d acceptance: NOT_STARTED / NOT_AUTHORIZED
baseline HEAD / origin/main: 04b52a2e12d5f4dafd4e9a1172d628c6c58f9a70
implementation commit: eff46a3b4de771aa37a48ea9ef5959918e407200
```

Accepted contract:

```text
optional HomeScreen binding factory: true
normal main.dart configures binding: false
session opt-in default: off
opt-in persistence: false
stream completion automatically enqueues: false
opt-in automatically enqueues/processes: false
explicit enqueue button: true
enqueue automatically processes: false
one processNext per process button press: true
automatic queue drain: false
explicit flush button: true
flush existing Voice Output Demo player: false
binding dispose idempotent: true
old process UI result invalidated by flush: true
visible terminal text / IDs / item ID / URI / raw error: false
```

Exact ten-file implementation surface is recorded in
`docs/v300_rt5d_home_screen_voice_output_controls.md`. Focused widget tests use
only fake controller state, fake synthesis, fake terminal playback, fake local
stop, and a fake existing audio engine.

Acceptance passed on 2026-07-31 after compileall, the dedicated candidate gate,
Backend 192 passed with one existing warning, Flutter analyze, 16 focused
Flutter tests, 331 full Flutter tests, exact ten-file review, changed-content
privacy review, `git diff --check`, explicit operator approval, implementation
commit, post-commit verification, and push. The final HomeScreen candidate was
reviewed as an insertion-only `+396/-0` diff.

No `main.dart`, Backend, configured runtime, existing RT-5c orchestrator,
queue, existing real player, dependency, permission, version, release record,
or Framework file was changed.

No Backend HTTP, Framework/provider execution, real synthesis, real audio
playback, automatic TTS, Framework real output flush, provider hard cancel, or
speech-triggered barge-in was added.

The dedicated RT-5d gate remains a historical pre-commit candidate gate bound
to baseline `04b52a2e12d5f4dafd4e9a1172d628c6c58f9a70` and the exact ten-file
surface. It is not rerun for this six-document acceptance sync. RT-5d
acceptance does not authorize or start RT-5e.

## v3.0.0 goal

```text
Preserve the accepted daily sleep, mood, advice, chat, TTS, character, and
history loop while evolving DRC into a provider-neutral realtime character
runtime demonstration with observable voice-input, streaming response,
voice-output, interruption, capability, and motion lifecycle states.
```

v3.0.0 is not complete merely because individual STT, LLM, TTS, or motion code
exists. The accepted result must coordinate those capabilities through stable
public AI Character Framework boundaries and must remain mock-safe by default.

## Guarding policy

```text
Safe default + documented explicit opt-in + visible execution state.
```

RT-0 must distinguish all of the following:

```text
source exists
discovery probe detected a candidate
public Framework contract is released
DRC adapter is wired
configured execution succeeded
PC/smartphone UI evidence was accepted
```

None of those states may be substituted for another.

## v3.0.0 scope fixed for planning

```text
- App-owned realtime session ID, lifecycle, events, capability, and safe error models.
- Flutter microphone permission and capture through an app-owned abstraction.
- A bounded realtime transport between Flutter and the DRC Backend.
- Stable AI Character Framework public voice-input/realtime session integration.
- Incremental transcript and LLM response handling where the public contract supports it.
- Cancellation, TTS queue control, interruption, and barge-in coordination.
- Listening, transcribing, thinking, responding, speaking, interrupted,
  reconnecting, unavailable, and error presentation states.
- Public motion-event integration and configured Live2D/VTube Studio execution.
- Capability negotiation and degraded operation when one optional component is unavailable.
- Session, event, audio, and artifact limits and cleanup.
- Credential-free fake-session tests and explicit opt-in operator acceptance.
```

## Explicit exclusions

```text
- Always-on microphone or wake-word detection.
- Background continuous recording.
- Persisting raw conversation audio by default.
- Provider-specific STT, LLM, TTS, Live2D, or VTS clients inside DRC.
- Importing AI Character Framework internal modules.
- Adding new sys.path, sys.modules, import-cache, or temporary-CWD workarounds.
- Live2D model creation, rigging, or commercial asset production.
- Multiple simultaneous character conversations.
- Accounts, cloud synchronization, production multi-user hosting, or store publication.
- New Fitbit/Google Health capability work unrelated to realtime orchestration.
- Rewriting any v2.0.0, v2.0.1, or v2.1.0 release artifact or record.
```

## RT-0 split

```text
RT-0a  COMPLETED / ACCEPTED      Inventory current DRC realtime-related code and freeze the v3 planning boundary
RT-0b  COMPLETED / ACCEPTED     Verify released Framework public realtime prerequisites and classify every gap
RT-0c  COMPLETED / ACCEPTED     Reassess released Framework v5.1.0 and accept the remaining realtime block
```

RT-1 through RT-9 remain blocked after RT-0c acceptance until the required Framework
contracts are released and verifiable.

## RT-0a purpose

```text
- Read the actual Backend, Flutter, tests, platform manifests, roadmap, and tasklist.
- Record what is real runtime, what is a guarded request boundary, and what is discovery only.
- Correct the stale tasklist R-1 CURRENT marker without changing its historical accepted record.
- Freeze the RT-0a change and non-change surfaces.
- Add one credential-free source-tree check for the inventory.
- Do not change runtime behavior or claim Framework readiness.
```

## RT-0a inspected implementation surface

Backend:

```text
backend/app/main.py
backend/app/config.py
backend/app/api/voice_input_demo.py
backend/app/models/voice_input_demo.py
backend/app/services/voice_input_demo_service.py
backend/app/api/voice_output_demo.py
backend/app/models/voice_output_demo.py
backend/app/services/voice_output_demo_service.py
backend/app/services/framework_voice_output_adapter.py
backend/app/api/motion_demo.py
backend/app/models/motion_demo.py
backend/app/services/motion_demo_service.py
backend/app/services/motion_boundary_probe.py
backend/app/api/chat.py
backend/app/models/chat.py
backend/app/services/post_advice_chat_service.py
backend/app/services/framework_text_chat_adapter.py
backend/app/services/framework_text_chat_drc_live_reply.py
```

Flutter and platform metadata:

```text
app/pubspec.yaml
app/lib/screens/home_screen.dart
app/lib/services/backend_api_client.dart
app/lib/models/voice_input_demo.dart
app/lib/models/voice_output_demo.dart
app/lib/models/motion_demo.dart
app/lib/models/character_display_presentation.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/audioplayers_voice_output_audio_engine.dart
app/lib/widgets/character_display_card.dart
app/android/app/src/main/AndroidManifest.xml
app/ios/Runner/Info.plist
```

Regression surface:

```text
backend/tests/**
app/test/**
scripts/check_v210_*.py
scripts/check_v20x_*.py
```

## RT-0a current behavior summary

```text
- Backend routing is ordinary FastAPI HTTP request/response; no realtime transport is wired.
- Voice input is a metadata-only guarded boundary and always returns not_started with no transcript.
- Motion is a guarded simulator/probe boundary and never sends motion or opens VTS WebSocket.
- Configured FW text chat uses a full-response ask() path, not DRC streaming orchestration.
- Existing FW adapters still carry project-root/import-context integration workarounds.
- Voice output produces one opaque artifact and Flutter controls local playback only.
- Flutter stop does not cancel Framework synthesis, LLM generation, or a TTS queue.
- Character activity presentation is limited to idle, loading, and speaking.
- No microphone plugin, Android RECORD_AUDIO permission, or iOS microphone usage description exists.
- HomeScreen and the main widget-test file remain large and require extraction before realtime UI growth.
```

Detailed evidence is frozen in `docs/v300_realtime_current_behavior_inventory.md`.

## RT-0a change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
```

## RT-0a explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
release_notes/**
docs/DRC_v200_goal_checklist_small_commit.md
docs/DRC_v20x_maintenance_checklist.md
docs/DRC_v210_goal_checklist_small_commit.md
docs/v210_release_record.md
build_v200_final_fixed_release_zip_from_head.ps1
build_v201_fixed_release_zip_from_head.ps1
build_v210_fixed_release_zip_from_head.ps1
release ZIPs, tags, GitHub Releases, and private operator evidence
```

## RT-0a verification

Run from the repository root:

```powershell
python -m compileall -q backend scripts
python scripts\check_v300_realtime_current_behavior_inventory.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..

git diff --check
```

RT-0a acceptance result:

```text
- The inventory agrees with the inspected implementation: passed.
- Credential-free RT-0a source-tree gate: passed.
- Backend pytest: 110 passed.
- Flutter tests: 103 passed.
- git diff --check: passed.
- Backend/Flutter runtime and existing tests changed: false.
- Version and immutable release records changed: false.
- Real provider execution, microphone use, and realtime session start: false.
- Diff review and explicit operator approval: passed.
```

## RT-0a stop rule

```text
Do not add microphone dependencies or permissions.
Do not add WebSocket/SSE/audio-upload endpoints.
Do not wire STT, streaming LLM, cancellation, TTS queues, barge-in, or motion execution.
Do not modify AI Character Framework.
RT-0a was marked accepted only after local verification and operator approval.
RT-0a implementation did not start RT-0b; RT-0b becomes current only after RT-0a acceptance.
Historical RT-0a acceptance marker: `RT-0c  PLANNED`.
```

## RT-0b purpose

```text
- Inspect the released AI Character Framework v5.0.0 public host-app surface.
- Freeze the exact released commit and public export inventory used for the review.
- Classify every v3 prerequisite as READY_CURRENT_USE, PARTIAL_BLOCKING,
  MISSING_BLOCKING, or DEFECT_BLOCKING.
- Preserve the accepted v4 text-chat and v5 one-shot voice-output behavior while
  distinguishing it from full realtime readiness.
- Record the accumulated DRC real-app integration feedback and new realtime gaps.
- Make no DRC or Framework runtime change and perform no real provider execution.
```

At RT-0a acceptance, RT-0b was `NOT_STARTED`. RT-0b is now COMPLETED / ACCEPTED after the RT-0a/RT-0b gates, 110 Backend tests, 103 Flutter tests, diff review, and explicit operator approval passed.

## RT-0b released Framework snapshot

```text
Repository: murayan1982/ai-character-framework
Released line: v5.0.0
Inspected public-source commit: 6494da306015c4f714f869b43e773ba51a2478a2
Release implementation commit: a2df57e2e8ed226b7c9e9c72ed68a79c8a48b6db
RT-0b readiness: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
```

Detailed matrix:

```text
docs/v300_framework_realtime_contract_readiness.md
```

Credential-free source-tree gate:

```text
scripts/check_v300_framework_realtime_contract_readiness.py
```

## RT-0b readiness summary

```text
READY_CURRENT_USE:
- full-response public text chat for existing v2.1.0 use;
- one-shot provider-neutral voice-output request/result and opaque handoff.

PARTIAL_BLOCKING:
- text streaming and state/events;
- typed results/public errors across all session types;
- consolidated capability reporting;
- project-root-independent stable factories;
- provider config responsibility;
- session close/dispose.

MISSING_BLOCKING:
- public voice-input/STT session;
- unified realtime session/lifecycle;
- provider-level hard cancellation;
- TTS queue/cancel/flush and barge-in acknowledgement;
- public motion-event/Live2D/VTS adapter;
- installable SDK packaging boundary.

DEFECT_BLOCKING:
- released README uses session.speak(...), while the released implementation
  exposes VoiceOutputSession.create_output(...) and no speak() method.
```

RT-0b records Framework feedback `FW-F1` through `FW-F12`. RT-0c owns their
handoff ordering and the explicit blocked/unblocked acceptance decision.

## RT-0b change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
```

## RT-0b explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
release_notes/**
historical v2.x checklists and release records
AI Character Framework repository/runtime
release ZIPs, tags, GitHub Releases, and private operator evidence
```

## RT-0b verification

Run from the repository root:

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

Accepted RT-0b status:

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

## RT-0b stop rule

```text
Do not modify AI Character Framework in RT-0b.
Do not import Framework internals to replace missing public contracts.
Do not add another DRC method/factory probing layer for realtime features.
Do not add microphone, transport, STT, cancellation, queue, barge-in, or motion runtime.
RT-1 through RT-9 remain blocked after RT-0b implementation and acceptance.
RT-0c must accept the handoff boundary, and a released Framework update must
provide the required public contracts before RT-1 can be authorized.
```

## RT-0c Framework v5.1.0 reassessment

Historical RT-0b decision: BLOCKED_FRAMEWORK_UPDATE_REQUIRED
Historical RT-0b authorization marker: RT-1 authorization: BLOCKED pending RT-0c and a released Framework update
Historical RT-0c pre-implementation marker: RT-0c  CURRENT / NOT_COMPLETED; NOT_STARTED

Current RT-0c state:

```text
RT-0c implementation: COMPLETED / ACCEPTED
Framework release: v5.1.0
Framework tag commit: b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
Host-app foundation: SUBSTANTIALLY_READY_WITH_TRANSITION_GAPS
Realtime decision: BLOCKED_REALTIME_PUBLIC_CONTRACTS_MISSING
```

Accepted v5.1.0 host-app foundations recorded by RT-0c:

```text
FW-F4 capability snapshot: RESOLVED_V510
FW-F5 provider config ownership: RESOLVED_V510
FW-F7 opaque voice artifact: RESOLVED_V510
FW-F8 public conformance gate: RESOLVED_V510
```

Transition gaps recorded by RT-0c:

```text
FW-F1 package-like import without a published wheel: PARTIAL_V510
FW-F2 factory/method transition surfaces: PARTIAL_V510
FW-F3 typed Text Chat result without universal cross-session result: PARTIAL_V510
FW-F6 lifecycle methods without real provider cleanup proof: PARTIAL_V510
```

Remaining blockers:

```text
FW-F9 public voice-input/STT: MISSING_REALTIME_BLOCKER
FW-F10 unified realtime lifecycle/events: MISSING_REALTIME_BLOCKER
FW-F11 hard cancel/TTS queue/flush/barge-in: MISSING_REALTIME_BLOCKER
FW-F12 public motion/VTS adapter: MISSING_REALTIME_BLOCKER
```

RT-1 through RT-5 remain blocked until released public voice-input, realtime,
and cancellation/queue contracts are verifiable. RT-6 through RT-7 remain
blocked until a released public motion contract is verifiable. RT-8 through
RT-9 remain blocked by their prerequisite runtime phases.

Detailed contract:

```text
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
```

RT-0c change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_v510_reassessment.md
scripts/check_v300_framework_v510_reassessment.py
```

RT-0c explicit non-change surface:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
app/android/**
app/ios/**
backend/.env.example
backend/app/version.py
docs/v300_realtime_current_behavior_inventory.md
scripts/check_v300_realtime_current_behavior_inventory.py
docs/v300_framework_realtime_contract_readiness.md
scripts/check_v300_framework_realtime_contract_readiness.py
release_notes/**
historical v2.x checklists and release records
AI Character Framework repository/runtime
```

RT-0c verification:

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

Expected accepted marker:

```text
v300_framework_v510_reassessment_status: completed-accepted
v300_framework_release_snapshot: v5.1.0@b68c62b5e80328b8c50f9eeef98164f6ae2a3b0f
v300_framework_realtime_prerequisites_ready: False
v300_rt1_authorization: blocked-pending-released-voice-input-realtime-cancel-contracts
v300_rt6_authorization: blocked-pending-released-motion-contract
```

RT-0c stop rule:

```text
Do not start RT-1 after RT-0c acceptance until a later Framework release
provides the missing public contracts. Do not migrate the existing DRC runtime
adapter in this docs/test-only commit. Do not add another import or method probe.
```

## RT-1 split after Framework v5.2.0 release

```text
RT-1a  COMPLETED / ACCEPTED
       Verified the released v5.2.0 mock-safe public contracts and authorized the
       bounded DRC integration surface.

RT-1b  COMPLETED / ACCEPTED
       Adds Backend-only DRC realtime state/event/capability/session models and a
       Framework-contract normalizer. No API route or provider execution.
```

RT-1a decision:

```text
RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED
```

The released v5.2.0 root exports public Voice Input, Realtime, interrupt/output
control, and Motion contracts. Their real provider/runtime implementations are
not complete. RT-1 may begin with model and mock-contract integration only.

Historical phase boundaries immediately after RT-1a acceptance:

```text
RT-1: COMPLETED / ACCEPTED
RT-2: CURRENT / NOT_COMPLETED; RT-2a COMPLETED / ACCEPTED; RT-2b NOT_STARTED; microphone access NOT_STARTED
RT-3: BLOCKED_REAL_STT_NOT_IMPLEMENTED
RT-4: BLOCKED_REAL_STREAMING_CANCEL_NOT_IMPLEMENTED
RT-5: BLOCKED_REAL_OUTPUT_CONTROL_NOT_IMPLEMENTED
RT-6: PLANNED_AFTER_RT1; mock motion contract available
RT-7: BLOCKED_REAL_MOTION_ADAPTER_NOT_IMPLEMENTED
RT-8 through RT-9: BLOCKED by prerequisites
```

Detailed contract:

```text
docs/v300_framework_v520_contract_adoption.md
scripts/check_v300_framework_v520_contract_adoption.py
docs/v300_backend_realtime_normalization.md
scripts/check_v300_backend_realtime_normalization.py
```



## RT-1b implementation checkpoint

```text
Implementation state: COMPLETED / ACCEPTED
Backend models added: true
Framework-contract normalizer added: true
Focused Backend tests: 6 passed in local implementation verification
Full Backend tests: 116 passed in local implementation verification
Framework import: false
API route added: false
microphone used: false
realtime runtime started: false
Provider execution: false
Flutter runtime changed: false
```

RT-1b was accepted on 2026-07-26 after compileall, the RT-1b source/runtime
gate, focused Backend 6, full Backend 116 with one existing warning, Flutter 103,
`git diff --check`, 10-file diff review, and explicit operator approval passed.
Parent RT-1 is COMPLETED / ACCEPTED. At this historical RT-1b checkpoint, RT-2 was CURRENT / NOT_COMPLETED and remained NOT_STARTED until its guarded permission/capture split was accepted. RT-2 is now COMPLETED / ACCEPTED.

## RT-2 small-commit split

Current parent status: COMPLETED / ACCEPTED

Historical split state at the early RT-2 checkpoints:

```text
RT-2a  COMPLETED / ACCEPTED
       Current Flutter/platform permission and capture inventory; docs/test-only.
RT-2b  COMPLETED / ACCEPTED
       DRC-owned permission state/result and gateway interface with fake gateway.
RT-2c  COMPLETED / ACCEPTED
       Android/iOS permission adapter and declarations; no UI invocation or capture.
RT-2d  COMPLETED / ACCEPTED
       Capture lifecycle/controller and deterministic fake engine; no microphone access.
RT-2e  CURRENT / NOT_COMPLETED
  RT-2e-a  COMPLETED / ACCEPTED
             Exact-surface and record 6.2.1 readiness; docs/test-only.
  RT-2e-b  COMPLETED / ACCEPTED
             Pinned record adapter/private temporary artifact boundary; fake tests only.
  RT-2e-c  CURRENT / NOT_COMPLETED
             NOT_STARTED; explicit operator real-device bounded capture evidence.
```

RT-2a inspected the actual source and confirmed:

```text
Flutter microphone/permission/capture dependency: absent
Android RECORD_AUDIO: absent
iOS NSMicrophoneUsageDescription: absent
Web/desktop microphone adapter: absent
App-owned microphone permission gateway: absent
App-owned capture engine/controller: absent
Current voice-input UI: metadata-only backend request
Current Backend voice-input route: no audio body and no STT execution
```

Safety contract for later RT-2 children:

```text
explicit user action only
safe default disabled/unavailable
typed denied/permanently-denied/restricted/unsupported/error states
single active capture
hard bounded duration and explicit stop/cancel
no always-on or background recording
no raw audio persistence by default
cleanup after completion/cancel/error
no STT/provider upload before RT-3 authorization
```

RT-2a was accepted on 2026-07-26 after compileall, the RT-1b and RT-2a gates, Backend 116 with one existing warning, Flutter 103, `git diff --check`, seven-file diff review, and explicit operator approval passed.

RT-2a protected results:

```text
Backend runtime changed: false
Flutter runtime changed: false
Existing tests changed: false
Microphone dependency added: false
Android RECORD_AUDIO added: false
iOS microphone usage added: false
Microphone accessed: false
Audio captured: false
```

## Historical accepted marker compatibility

The following strings are retained only so the accepted RT-0b/RT-0c source-tree
checks continue to validate their historical checkpoints. They do not describe
the active RT-1a state.

```text
Historical RT-0c parent marker: Current parent phase: RT-0 COMPLETED / ACCEPTED
Historical RT-0c terminal marker: Current small commit: none
Historical RT-0c completion marker: Completed small commit: RT-0c COMPLETED / ACCEPTED
Historical RT-0b planning marker: RT-1   BLOCKED
```

## RT-2b app-owned permission contract and fake gateway

Implementation state: COMPLETED / ACCEPTED

Changed runtime/test files:

```text
app/lib/services/microphone_permission.dart
app/test/microphone_permission_test.dart
```

Contract additions:

```text
status: unknown, granted, denied, permanentlyDenied, restricted, unsupported, failed
operation: check, request, openSettings
result: safe message, technical code, request/settings affordances, immutable public metadata
gateway: checkPermission, requestPermission, openAppSettings
fake: deterministic request sequence and call counters; no OS side effect
```

Protected boundaries:

```text
permission/capture dependency added: false
Android RECORD_AUDIO added: false
iOS NSMicrophoneUsageDescription added: false
MethodChannel or browser media API added: false
HomeScreen/voice-input UI changed: false
Backend changed: false
Framework imported: false
platform permission requested: false
microphone accessed: false
audio captured or persisted: false
provider/STT called: false
```

Acceptance completed on 2026-07-26 after compileall, the RT-2b source gate,
focused Flutter 9, full Flutter 112, Backend 116 with one existing warning,
`git diff --check`, nine-file review, gate portability fixes, and explicit operator approval passed.
RT-2c is COMPLETED / ACCEPTED on 2026-07-27 at implementation commit `fe26c3c`. The mobile gateway, platform declarations, resolved lockfile, generated Windows registration, analyzer cleanup, tests, gate, Android debug APK build, and 16-file review were accepted. RT-2d is COMPLETED / ACCEPTED after fake-only lifecycle verification; RT-2e is CURRENT / NOT_COMPLETED and NOT_STARTED.


## RT-2c mobile platform permission wiring without capture

Implementation state: COMPLETED / ACCEPTED

Changed runtime/test files:

```text
app/pubspec.yaml
app/pubspec.lock (generated by operator flutter pub get)
app/android/app/src/main/AndroidManifest.xml
app/ios/Runner/Info.plist
app/windows/flutter/generated_plugin_registrant.cc (generated by operator flutter pub get)
app/windows/flutter/generated_plugins.cmake (generated by operator flutter pub get)
app/lib/services/permission_handler_microphone_permission_gateway.dart
app/test/permission_handler_microphone_permission_gateway_test.dart
```

Implemented boundary:

```text
permission_handler 12.0.3 pinned
Android RECORD_AUDIO declared once
iOS NSMicrophoneUsageDescription declared
Android/iOS-only real permission gateway
web/desktop unsupported short-circuit
DRC-owned typed status/error normalization
injected fake driver focused tests
```

Protected boundaries:

```text
startup/HomeScreen invocation: false
platform permission request executed during tests: false
microphone opened/accessed: false
audio captured/persisted/uploaded: false
capture package added: false
Backend changed: false
Framework/provider/STT execution: false
RT-2d authorization: authorized-capture-lifecycle-and-fake-engine-only
```

Acceptance completed on 2026-07-27 after `flutter pub get`, exact generated
Windows plugin-registration review, `flutter analyze` with no issues, focused
Flutter 13, full Flutter 125, Backend 116 with one existing warning, the RT-2c
source/platform gate, Android debug APK build, `git diff --check`, 16-file review,
and operator acceptance evidence passed. The Android build emitted a Kotlin
daemon incremental-cache warning in `audioplayers_android`, then completed via
Gradle fallback and produced `app-debug.apk`. iOS build execution was not
available on the Windows operator environment and is not claimed.

## RT-2d capture lifecycle contract and fake engine

Implementation state: COMPLETED / ACCEPTED

Implemented scope: DRC-owned lifecycle/request/result/controller contracts, a
deadline scheduler boundary, and a deterministic fake capture engine. Single
active capture, hard bounded duration, stop/cancel/timeout/error/close cleanup,
and typed denied/permanently-denied/restricted/unsupported/busy/timeout states
are fixed before any real adapter. UI wiring, platform capture packages,
microphone access, raw audio, upload, Framework/provider calls, and STT remain
forbidden.

Changed runtime/test files:

```text
app/lib/services/microphone_capture.dart
app/test/microphone_capture_test.dart
```

Protected evidence:

```text
permission request executed: false
real capture dependency added: false
UI/platform/Backend changed: false
microphone accessed: false
audio captured/persisted/uploaded: false
raw audio bytes/path/handle exposed: false
RT-2e authorization: authorized-explicit-opt-in-bounded-real-capture-adapter-only
```

Acceptance completed on 2026-07-27 after compileall, the RT-2d source/surface
gate, `flutter analyze` with no issues, focused Flutter 17, full Flutter 142,
Backend 116 with one existing warning, `git diff --check`, nine-file review, and
explicit operator approval passed. No permission request, microphone access,
audio capture, raw-audio exposure, upload, provider call, or STT execution occurred.

## RT-2e explicitly guarded bounded real capture adapter

Parent state: COMPLETED / ACCEPTED
Authorization outcome: completed-accepted-explicitly-guarded-bounded-real-capture

### RT-2e-a exact-surface and recorder-package readiness

Implementation state: COMPLETED / ACCEPTED

Exact accepted code review confirms Dart `^3.11.5`, no direct recorder or path
provider dependency, accepted RT-2d controller/fake engine, and existing mobile
permission declarations. `record` 7.x is not compatible with the current Dart
baseline. RT-2e-b selects `record` 6.2.1, the compatible final pre-7 line.

`startStream` is forbidden because it exposes raw bytes. A later concrete
adapter may use file mode only with a private temporary path/artifact registry;
public DRC results remain opaque. Permission ownership stays in the existing
DRC permission gateway.

RT-2e-a is docs/test-only and does not add dependencies, change generated plugin
registrations or platform files, request permission, access a microphone,
capture/create/upload audio, expose bytes/path/handles, or execute STT.
Acceptance completed on 2026-07-27 after compileall, the RT-2e-a gate,
`flutter analyze` clean, full Flutter 142, Backend 116 with one existing
warning, `git diff --check`, seven-file review, and explicit operator
approval passed.

### RT-2e-b record adapter and private temporary artifact boundary

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; fake-only verification boundary added

Pinned direct dependencies are `record` 6.2.1 and `path_provider` 2.1.6.
The adapter uses injectable recorder/private-filesystem boundaries, WAV file
mode at 16 kHz mono, an opaque capture id, and private temporary artifact
cleanup. `startStream` and public raw bytes/path/handles are forbidden.

The production package driver is compiled but not connected to startup/UI and
is not instantiated by tests. Real permission request, no real microphone
access, real audio capture, upload, provider execution, and STT remain absent.
Acceptance completed on 2026-07-27 after operator dependency resolution, generated
plugin review, analyzer cleanup, focused Flutter 18/18, full Flutter 161, Backend
116 with one existing warning, the RT-2e-b gate, Android debug APK compilation,
`git diff --check`, 19-file review, and explicit operator approval. The Kotlin
incremental-cache daemon reported a cross-drive cache error before Gradle
fallback produced the APK. No app launch, permission request, microphone access,
or audio capture occurred.

### RT-2e-c explicit operator real-device capture evidence

State: COMPLETED / ACCEPTED
Authorization outcome: completed-accepted-explicit-real-device-bounded-capture-evidence

#### RT-2e-c1 operator-only harness/readiness contract

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; docs/test-only

The accepted `5a7f814` source surface was reread before implementation. The
later operator harness must use a separate `lib/main_rt2ec_operator.dart`
entrypoint, require `--dart-define=DRC_RT2EC_OPERATOR=true`, and require an
in-app acknowledgement. The normal `lib/main.dart` and `HomeScreen` remain
unchanged.

Permission check, permission request, start, stop, and cancel are separate
explicit user actions. Start requires granted permission. Capture remains
single-active and is capped at 15 seconds using WAV 16 kHz mono file mode. Stop
must immediately discard the private artifact through its opaque id. Safe
evidence is allowlisted to status/code/booleans/duration/cleanup and must not
contain private paths, raw bytes, audio content, transcript content, Backend
payloads, Framework/provider payloads, or STT results.

This checkpoint changed docs and a source/surface gate only. It added no Flutter
runtime, dependency, generated plugin, platform, UI, or Backend change and did
not execute permission request, microphone access, audio capture, upload, or
STT. Acceptance followed compileall, the RT-2e-c1 gate, Backend 116 with one
existing warning, `flutter analyze`, full Flutter 161, `git diff --check`, exact
eight-file review, and explicit operator approval.

#### RT-2e-c2 operator-only harness and fake/widget tests

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED
Authorization: completed-accepted-fake-widget-only

The separate `main_rt2ec_operator.dart` target now fails closed without
`DRC_RT2EC_OPERATOR=true`, requires an in-app acknowledgement before invoking
the production dependency factory, and exposes permission check/request plus
capture start/stop/cancel as separate actions. Start is granted-only and bounded
to 15 seconds. Completed artifacts are immediately discarded by opaque id and
only safe evidence fields are rendered. Fake/widget tests cover the double
opt-in, no-startup-action boundary, bounded request, discard, cancel, and exact
allowlist. This stage performed no real permission request, microphone access, or audio
capture. Acceptance followed compileall, the RT-2e-c2 gate, Backend 116 with one
existing warning, `flutter analyze`, focused Flutter 10, full Flutter 171,
`git diff --check`, exact twelve-file review, and explicit operator approval.

#### RT-2e-c3 real Android bounded capture and cleanup evidence

State: COMPLETED / ACCEPTED

##### RT-2e-c3a real Android operator preflight and safe evidence contract

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; docs/test-only
Authorization: completed-docs-test-only-preflight

The accepted `b2e2adb` source archive with SHA-256
`18d39ea0676bcd3213c104a71fd5ce2c096c6b96002eb7aaef7ceccd06a2fd86`
was reread before real-device execution. The contract requires one physical
Android device, the separate `main_rt2ec_operator.dart` target,
`DRC_RT2EC_OPERATOR=true`, in-app acknowledgement, explicit permission
check/request, and one non-sensitive capture stopped before the 15-second hard
limit.

Completed evidence is marker-only. It may contain the accepted safe panel
status/code/boolean/duration fields and the clean source commit. It must not
contain device serial/model, private path, opaque capture id, raw audio, audio
content, transcript, provider payload, raw platform error, or raw screenshot.
The completed artifact must be registered and immediately discarded, with
cleanup succeeded. Backend upload, Framework/provider execution, and STT are
forbidden.

This checkpoint changed documentation and one source/surface gate only. It did
not run Flutter, connect a device, request permission, access a microphone,
capture audio, create private evidence, upload audio, or execute STT. Acceptance
passed with compileall, the RT-2e-c3a gate, Backend 116 with the existing warning,
`flutter analyze`, full Flutter 171, `git diff --check`, exact ten-file review,
and explicit operator approval.

##### RT-2e-c3b explicit real Android bounded capture and cleanup evidence

State: COMPLETED / ACCEPTED
Implementation: COMPLETED / ACCEPTED; marker-only real Android evidence
Authorization: completed-accepted-explicit-real-android-bounded-capture-evidence

Run the explicit operator target from the clean accepted RT-2e-c3a commit on
one physical Android device. Accept only granted permission,
request attempted, completed capture, duration 1..15000 ms, microphone/audio
true, raw audio exposed false, private artifact registered/discarded true, and
cleanup succeeded true. Keep all private evidence and audio outside commits. No
Backend upload or STT execution.


RT-2e-c3b accepted marker summary:

```text
source commit: ddae21944ac0e251cd8194bf93982bd5dc7a4ae8
physical Android: true
operator target enabled: true
acknowledgement completed: true
permission granted/request attempted: true/true
capture completed: true
requested/captured duration ms: 15000/4820
microphone/audio: true/true
raw audio exposed: false
private artifact registered/discarded: true/true
cleanup succeeded: true
Backend/upload/STT: false/false/false
private path/opaque id/device identifier/raw audio/raw screenshot committed: false
post-run working tree clean: true
```

An earlier non-acceptance dry run confirmed cleanup but did not retain the
duration marker. The accepted marker is from the later single-capture acceptance
session. RT-2 is now COMPLETED / ACCEPTED. RT-3 remains
`BLOCKED_REAL_STT_NOT_IMPLEMENTED`.

## RT-3a Framework v5.3.0 STT integration inventory

```text
RT-3: CURRENT / BLOCKED_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
RT-3a: COMPLETED / ACCEPTED
RT-3a implementation: COMPLETED / ACCEPTED
RT-3b: COMPLETED / ACCEPTED
RT-3c: COMPLETED / ACCEPTED
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

RT-3a fixes the exact DRC/FW boundary before runtime work:

```text
DRC private mobile capture
-> app-owned opaque/private artifact lifecycle
-> future private backend staging
-> FW public VoiceInputAudioSource
-> FW public VoiceInputSession
-> provider adapter
-> typed VoiceInputResult
```

Verified current facts:

```text
FW v5.3.0 public host-audio contract: present
FW v5.3.0 fake adapter: present
FW v5.3.0 VoiceInputSession adapter wiring: present
FW v5.3.0 guarded real adapter: present
FW v5.3.0 actual provider execution: absent
DRC private capture artifact boundary: present
DRC operator immediate discard: present
DRC voice-input audio upload/staging: absent
DRC current voice-input endpoint: metadata-only
```

RT-3b authorization:

```text
authorized-app-owned-host-audio-lifecycle-contract-fake-only
```

RT-3a acceptance evidence: source-only gate, Backend 116, clean Flutter analysis,
Flutter 171, exact seven-file review, and `git diff --check` passed.

RT-3b must not upload audio or call FW/provider code. RT-3c may later add
private backend staging and a fake FW public-session handoff. RT-3d real STT
evidence remains blocked until FW implements and accepts concrete provider
execution.


## RT-3b app-owned host-audio handoff lifecycle acceptance

```text
RT-3b: COMPLETED / ACCEPTED
RT-3b implementation: COMPLETED / ACCEPTED
RT-3c: COMPLETED / ACCEPTED
RT-3 real acceptance: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

Added boundary:

```text
completed MicrophoneCaptureResult
-> HostAudioHandoffController.retain
-> HostAudioPrivateArtifactLease
-> injected HostAudioHandoffConsumer
-> cleanup on completion/failure/cancel/discard/close
-> public path-free HostAudioHandoffResult
```

RT-3b is accepted as fake-only. No Backend route, upload, audio read, FW import, provider execution, STT, dependency, platform, vendor, or RT-2 operator-path change was added.

Acceptance evidence: source gate, Backend 116 with one existing warning, clean Flutter analysis, focused Flutter 21, full Flutter 192, exact ten-file review, cleanup-retry test correction, and `git diff --check` passed.

RT-3c authorization:

```text
authorized-private-backend-staging-and-fake-fw-public-session-handoff-only
```


## RT-3c1 private staging and fake FW handoff readiness

```text
RT-3: CURRENT / BLOCKED_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
RT-3a: COMPLETED / ACCEPTED
RT-3b: COMPLETED / ACCEPTED
RT-3c: COMPLETED / ACCEPTED
RT-3c1: COMPLETED / ACCEPTED
RT-3c1 implementation: COMPLETED / ACCEPTED
RT-3c2: COMPLETED / ACCEPTED
RT-3c2 implementation: COMPLETED / ACCEPTED
RT-3c3: COMPLETED / ACCEPTED
RT-3c3 implementation: COMPLETED / ACCEPTED
RT-3c4: COMPLETED / ACCEPTED
RT-3c4 implementation: COMPLETED / ACCEPTED
RT-3c4 authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
RT-3d: BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

RT-3c1 exact findings:

```text
Flutter scoped private path lease: present
Flutter http dependency: present
Backend voice-input endpoint: metadata-only
Backend voice-input staging store: absent
Backend voice-input upload route: absent
Backend staging TTL/count/body limits: absent
Backend FW voice-input adapter: absent
python-multipart dependency: absent
FW public file-path audio source: present
FW public fake adapter/session path: present
FW real provider execution: absent
```

Selected future transport/lifecycle:

```text
streamed audio/wav body; no multipart
1048576-byte maximum
300-second TTL
maximum 8 staged artifacts
WAV / 16000 Hz / mono / <=15000 ms
server-generated opaque staging ID
backend/local_data ignored private root
single-use consume and cleanup
no private path in public result/log/evidence
```

RT-3c1 changes no Backend/Flutter runtime or tests, dependencies, routes, configuration, vendor, platform, version, or release surface and performs no audio read/upload/staging, FW import, provider execution, or STT. Acceptance passed with compileall, the source-only gate, Backend 116 with one existing warning, clean Flutter analysis, full Flutter 192, exact nine-file review, and `git diff --check`. RT-3c2 is COMPLETED / ACCEPTED after compileall, four RT-3 gates, focused Backend 14, full Backend 127 with one existing warning, clean Flutter analysis, full Flutter 192, exact 18-file surface review, and `git diff --check`. RT-3c3 is COMPLETED / ACCEPTED after compileall, five RT-3 gates, focused Backend 21, full Backend 137 with one existing warning, clean Flutter analysis, focused Flutter 29, full Flutter 200, exact 22-file surface review, and `git diff --check`. RT-3c4 and parent RT-3c are COMPLETED / ACCEPTED after compileall, six RT-3 gates, focused Backend 8, full Backend 145 with one existing warning, clean Flutter analysis, full Flutter 200, exact 22-file surface review, `git diff --check`, and explicit operator approval. Authorization at implementation: `authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only`.


## RT-3c2 private Backend staging store and lifecycle

```text
RT-3c2: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
RT-3c3: COMPLETED / ACCEPTED
RT-3c3 implementation: COMPLETED / ACCEPTED
RT-3c4: COMPLETED / ACCEPTED
RT-3c4 implementation: COMPLETED / ACCEPTED
RT-3c4 authorization: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
```

Implemented and awaiting local acceptance:

- [x] `VOICE_INPUT_STAGING_TTL_SECONDS=300` safe default.
- [x] `VOICE_INPUT_STAGING_MAX_COUNT=8` safe default.
- [x] `VOICE_INPUT_STAGING_MAX_BYTES=1048576` safe default.
- [x] Private ignored root `backend/local_data/voice_input/staging`.
- [x] Chunked WAV staging with RIFF/WAVE structural guard.
- [x] Server-generated opaque 32-hex staging ID.
- [x] Path-free safe metadata.
- [x] TTL/capacity/partial/rejection cleanup.
- [x] Scoped single-use consume and explicit discard.
- [x] Traversal and symlink safety regression tests.
- [x] Local compileall, four RT-3 gates, focused Backend 14, full Backend 127.
- [x] Unchanged Flutter analyze/full 192 confirmation.
- [x] Explicit acceptance sync after approval.

Forbidden in RT-3c2: FastAPI upload route, Flutter audio transfer, Framework import,
VoiceInputSession creation, provider execution, transcription, STT evidence, dependency
change, platform change, version change, or release change.


## RT-3c3 guarded upload and Flutter scoped staging consumer

```text
RT-3c3: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
authorization at implementation: authorized-guarded-binary-upload-route-and-flutter-scoped-staging-consumer-only
RT-3c4: COMPLETED / ACCEPTED
RT-3c4 implementation: COMPLETED / ACCEPTED
```

Implemented:

- guarded `POST /demo/voice-input/staging`;
- direct streamed `audio/wav` body into the bounded private Backend store;
- safe metadata validation for WAV/16000 Hz/mono/maximum 15000 ms;
- public-safe error codes and path-free opaque staging metadata;
- Flutter `BackendVoiceInputStagingConsumer` using only the scoped private-path lease;
- `http.StreamedRequest` transfer without `readAsBytes` or multipart;
- local mobile artifact cleanup through the accepted RT-3b controller;
- one path-free staged-artifact handle reserved for RT-3c4;
- synthetic route and consumer tests.

Not performed: real microphone artifact upload, Framework import, `VoiceInputSession` creation, provider execution, transcription, or STT. RT-3c3 acceptance passed with compileall, five RT-3 gates, focused Backend 21, full Backend 137 with one existing warning, clean Flutter analysis, focused Flutter 29, full Flutter 200, exact 22-file surface review, and `git diff --check`.


## RT-3c4 fake FW public-session handoff and single-use staged cleanup

```text
RT-3c4: COMPLETED / ACCEPTED
implementation: COMPLETED / ACCEPTED
authorization at implementation: authorized-fake-fw-public-session-handoff-and-single-use-staged-artifact-cleanup-only
```

RT-3c4 may add only a Backend adapter that consumes one accepted private staged artifact, constructs FW v5.3.0 public host-audio/session objects with `FakeVoiceInputProviderAdapter`, returns a typed path-free result, and guarantees single-use consume/discard cleanup. Real provider execution, real transcription, and real STT remain forbidden.


## RT-3d0 - Framework real STT requirement feedback handoff

Status:

```text
RT-3d0  COMPLETED / ACCEPTED
RT-3d   BLOCKED_FRAMEWORK_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
```

Changed files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_real_stt_requirement_feedback.md
scripts/check_v300_framework_real_stt_requirement_feedback.py
```

Acceptance requirements:

- [x] six accepted RT-3 gates passed on clean `7cf980e` before RT-3d0
- [x] `python -m compileall -q backend scripts`
- [x] `python scripts/check_v300_framework_real_stt_requirement_feedback.py`
- [x] `python -m pytest -q backend/tests`
- [x] `cd app && flutter analyze && flutter test && cd ..`
- [x] exact seven-file surface review
- [x] `git diff --check`
- [x] no Backend/Flutter/FW runtime change
- [x] no dependency/platform/version change
- [x] no private environment, audio, microphone, or provider execution
- [x] no next FW version/provider selection
- [x] no release artifact, tag, or publication
- [x] explicit operator approval


## RT-3d1 - Framework v5.4.0 real STT adoption inventory

```text
RT-3d1  COMPLETED / ACCEPTED
RT-3d   BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
```

Exact change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_v540_real_stt_adoption_inventory.md
scripts/check_v300_framework_v540_real_stt_adoption_inventory.py
```

Acceptance requirements:

- [x] RT-3d0 is pushed to `origin/main`
- [x] FW v5.4.0 clean HEAD/tag and ZIP SHA-256 are verified
- [x] required public exports/signatures pass
- [x] accepted safe FW v5.4.0 gates pass
- [x] compileall and dedicated gate pass
- [x] Backend full pytest passes
- [x] Flutter analyze and full tests pass
- [x] exact seven-file review and `git diff --check` pass
- [x] no runtime/dependency/version/platform/FW change
- [x] no audio/microphone/credential/provider/network execution
- [x] explicit operator approval


Acceptance record:

```text
FW v5.4.0 identity/public surface/safe gates: PASS
RT-3d1 dedicated source-only gate: PASS
Backend tests: 145 passed, one existing warning
Flutter analyze: No issues found
Flutter tests: 200 passed
exact seven-file surface: PASS
git diff --check: PASS
explicit operator approval: RECEIVED
```

RT-3d2 is authorized but not started. RT-3d remains
`BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.


## RT-3d2a - FW v5.4.0 executor-path correction

```text
RT-3d2a  COMPLETED / ACCEPTED
RT-3d2   CURRENT / NOT_COMPLETED
RT-3d    BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
```

Acceptance requirements:

- [x] exact FW v5.4.0 HEAD/tag is verified
- [x] Voice Input session data-only delegation is verified
- [x] OpenAI adapter `transcribe()` execution-free behavior is verified
- [x] public fake and real executor exports are verified
- [x] FW fake-execution and real-runtime safe smokes pass
- [x] compileall and dedicated RT-3d2a gate pass
- [x] Backend full pytest passes
- [x] Flutter analyze and full tests pass
- [x] exact eight-file review and `git diff --check` pass
- [x] no Backend/Flutter runtime or dependency change
- [x] no private audio, credential, SDK/client, or real provider execution
- [x] explicit operator approval

Acceptance result:

```text
RT-3d2a operator approval: ACCEPTED
RT-3d2b authorization: AUTHORIZED / NOT_STARTED
Additional Framework development requirement: False
```

## RT-3d2b - bounded marked-fake executor wiring

```text
RT-3d2b  COMPLETED / ACCEPTED
RT-3d2   CURRENT / NOT_COMPLETED
RT-3d    BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
```

Acceptance requirements:

- [x] accepted RT-3d2a baseline is pushed and clean
- [x] exact FW v5.4.0 HEAD/tag is verified
- [x] existing RT-3c4 fake-session route remains unchanged
- [x] separate guarded OpenAI marked-fake executor route exists
- [x] private staged WAV is read only inside single-use consume scope
- [x] marked fake client and bounded fake policy are explicit
- [x] provider-neutral path-free response is verified
- [x] success, guard, preflight, failure, unsafe-result, and reuse cleanup tests pass
- [x] FW accepted fake-execution smoke passes
- [x] compileall and dedicated RT-3d2b gate pass
- [x] focused Backend tests pass
- [x] Backend full pytest passes
- [x] Flutter analyze and full tests pass unchanged
- [x] exact thirteen-file review and `git diff --check` pass
- [x] no credential value, OpenAI SDK/client, network, microphone, or real STT
- [x] no new Framework development requirement
- [x] explicit operator approval

Acceptance result:

```text
RT-3d2b implementation commit: 044f978240b1abda3d28206093e25c4ce285906d
RT-3d2b operator approval: ACCEPTED
RT-3d2c authorization: AUTHORIZED / NOT_STARTED
Additional Framework development requirement: False
```

## RT-3d2c - guarded real-executor assembly contract

```text
RT-3d2c  COMPLETED / ACCEPTED
RT-3d2   CURRENT / NOT_COMPLETED
RT-3d    BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
```

Acceptance requirements:

- [x] accepted RT-3d2b baseline is pushed and clean
- [x] exact FW v5.4.0 HEAD/tag is verified
- [x] assembly service uses only released FW root public exports
- [x] complete explicit operator/provider opt-in is required before Framework import
- [x] credential-object builder runs only after public-contract validation
- [x] DRC never reads the credential value
- [x] real client factory is constructed but never invoked
- [x] real provider executor is constructed but never executed
- [x] no staging consume, audio read, microphone, path, payload, transcript, or real STT
- [x] focused Backend assembly tests pass
- [x] dedicated RT-3d2c gate passes
- [x] Backend full pytest passes
- [x] Flutter analyze and full tests pass unchanged
- [x] exact nine-file review and `git diff --check` pass
- [x] explicit operator approval

Current implementation result:

```text
compileall: PASS
dedicated RT-3d2c gate: PASS
focused Backend tests: 5 passed
Backend full tests: 158 passed, one existing warning
Flutter analyze: No issues found
Flutter full tests: 200 passed
exact nine-file surface: PASS
git diff --check: PASS
Credential value read by DRC: False
OpenAI SDK imported: False
Provider client created: False
Network request executed: False
Audio read: False
Microphone accessed: False
Real provider execution: False
Additional Framework development requirement: False
RT-3d2c implementation commit: 12a9d35b161da303325097a58f3913fe0c3b5708
RT-3d2c operator approval: ACCEPTED
RT-3d3 authorization: AUTHORIZED / NOT_STARTED
```

## RT-3d3 - private real-STT operator boundary

```text
RT-3d3  COMPLETED / ACCEPTED
RT-3d2  COMPLETED / ACCEPTED
RT-3d   COMPLETED / ACCEPTED
```

Implementation requirements:

- [x] accepted RT-3d2c baseline is pushed and clean
- [x] exact FW v5.4.0 HEAD/tag is verified
- [x] all six explicit operator/provider gates are required before Framework resolution or staging consume
- [x] accepted RT-3d2c assembler is reused
- [x] only released FW root public exports are used
- [x] one staged private WAV is consumed through `VoiceInputStagingStore.consume()`
- [x] private path exists only inside the scoped consumer
- [x] success and failure both perform single-use artifact cleanup
- [x] transcript is excluded from public `repr` and committed evidence
- [x] unsafe public path/audio/payload/transcript metadata is rejected
- [x] no API route, AppConfig credential field, provider dependency, or DRC custom provider client
- [x] focused synthetic Backend tests pass
- [x] non-provider static audit, Backend full tests, and Flutter full tests pass
- [x] dedicated RT-3d3 implementation gate passes after docs/gate application
- [x] exact nine-file review and `git diff --check` pass
- [ ] explicit private real-provider execution opt-in
- [ ] actual real-STT operator execution
- [ ] private operator acceptance
- [ ] explicit commit approval
- [ ] explicit push approval

Current implementation result:

```text
RT-3d3 core synthetic tests: 5 passed
Backend full tests before docs/gate: 163 passed, one existing warning
Flutter full tests before docs/gate: 200 passed
Credential value read by current verification: False
OpenAI SDK imported by current verification: False
Provider client created by current verification: False
Network request executed by current verification: False
Real provider execution performed: False
Private operator evidence committed: False
Implementation commit: 5f7c7a682b5d52de2ba3ff9592d253f9bbb3341c
Real provider execution: COMPLETED
Transport response status: 200
Transcript nonempty: True
Expected phrase match: True
Staged artifact cleanup complete: True
Provider payload exposed: False
Private path exposed: False
Raw audio exposed: False
Transcript exposed: False
Private operator evidence committed: False
RT-3d3 accepted: True
Explicit operator approval: ACCEPTED
```

Actual provider execution is intentionally outside this implementation
checkpoint until the operator explicitly opts in. Any private credential
handoff, private audio location, provider payload, transcript, screenshot,
LAN address, and operator evidence must stay outside the repository.

## RT-4 — Streaming LLM, DRC event consumption, and cooperative cancellation

```text
RT-4   COMPLETED / ACCEPTED
RT-4a  COMPLETED / ACCEPTED
RT-4b  COMPLETED / ACCEPTED
RT-4c  COMPLETED / ACCEPTED / PUSHED
RT-4d  COMPLETED / ACCEPTED / PUSHED
RT-4e  COMPLETED / ACCEPTED / PUSHED
RT-4f  COMPLETED / ACCEPTED
  RT-4f1  COMPLETED / ACCEPTED / PUSHED
  RT-4f2  COMPLETED / ACCEPTED / PUSHED
  RT-4f3  COMPLETED / ACCEPTED / PUSHED
  RT-4f4  COMPLETED / ACCEPTED / PUSHED
```

### RT-4a — Current behavior inventory and small-commit split

RT-4a is docs/test-only. It freezes the exact accepted RT-3 DRC source and FW
v5.4.0 public streaming/cancel boundary before any runtime implementation.

Verified current boundary:

- [x] DRC configured Framework chat uses `session.ask()` and full-response HTTP.
- [x] DRC has no text stream chunk/terminal model or active stream registry.
- [x] Backend has no SSE/WebSocket streaming route or cancel endpoint.
- [x] Flutter has no streaming client/controller or incremental response UI.
- [x] RT-3 real STT output is not connected to an LLM streaming path.
- [x] FW v5.4.0 root exports `TextChatSession`, `create_text_chat_session`, and streaming/events/interrupt methods.
- [x] FW `interrupt()` is cooperative and does not prove provider-level hard cancel.
- [x] FW public `RealtimeSession` still does not provide real unified orchestration or TTS queue flush.

Accepted small-commit responsibility split:

```text
RT-4a  Inventory/split only; no runtime, tests, dependency, transport, or provider execution.
RT-4b  Backend stream state/event/chunk/terminal contract and fake-only service tests.
RT-4c  Bounded SSE transport, cancel request boundary, disconnect cleanup, and limits.
RT-4d  FW root-public ask_stream/event/interrupt adapter; cooperative cancel semantics.
RT-4e  Flutter streaming client/controller and fake transport tests; no HomeScreen integration.
RT-4f  UI integration, transcript-to-stream handoff, configured streaming, and cancel acceptance.
```

RT-4 parent acceptance result:

```text
real incremental LLM streaming: accepted
DRC normalized event consumption: accepted
configured local Backend/FW stream completion: accepted
cooperative cancel: accepted
bounded Backend transport lifecycle: accepted from RT-4c
disconnect cleanup: accepted from RT-4c
Flutter incremental response consumption: accepted
provider-level hard cancel: not claimed
hard_cancel_supported: false
real-STT-to-stream: not executed / not accepted
automatic TTS: not started
TTS queue/flush/barge-in: RT-5 only
```

RT-4a acceptance result:

- [x] exact seven-file implementation prepared
- [x] compileall passed
- [x] dedicated RT-4a gate passed
- [x] Backend 163 passed
- [x] Flutter analyze and Flutter 200 passed
- [x] exact seven-file review passed
- [x] changed-content private scan passed
- [x] `git diff --check` passed
- [x] explicit operator approval, commit, and push completed

Implementation commit: `235654e470f8c0cac17644ddf216ac7e6e223514`.

### RT-4b — Backend provider-neutral stream lifecycle and fake-only tests

RT-4b adds an independent Backend text-stream contract without transport or
Framework/provider execution.

Implementation contract:

- [x] add session and turn snapshots;
- [x] add lifecycle, bounded chunk, and terminal event models;
- [x] use one monotonic per-session sequence;
- [x] default to 512 characters per chunk and 4096 aggregate characters;
- [x] expose completed, cancelled, failed, and closed outcomes;
- [x] expose `cancel_mode=cooperative` and `hard_cancel_supported=false`;
- [x] reject active-turn replacement, late chunks, stale turns, and post-close callbacks;
- [x] add deterministic fake-only focused Backend tests;
- [x] keep FastAPI routes, Framework imports, provider calls, dependencies, and Flutter unchanged.

Exact change surface:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
backend/app/models/realtime_text_stream.py
backend/app/services/realtime_text_stream_service.py
backend/tests/test_realtime_text_stream_service.py
docs/v300_rt4_backend_stream_contract.md
scripts/check_v300_rt4_backend_stream_contract.py
```

RT-4b acceptance result:

- [x] implementation and 13 focused test cases prepared
- [x] compileall passed
- [x] dedicated RT-4b gate passed
- [x] focused Backend 13 passed
- [x] Backend full 176 passed
- [x] Flutter analyze and Flutter 200 passed
- [x] exact ten-file review passed
- [x] changed-content private scan passed
- [x] `git diff --check` passed
- [x] explicit operator approval, commit, and push completed

Implementation commit: `7e1e10e2ca33dd76ee963fcda31c2c5f800b4901`.

Stop rule satisfied: RT-4b added no routes, SSE/WebSocket, Framework imports, provider calls, Flutter code, hard-cancel claims, or TTS queue control.

### RT-4c — Bounded Backend SSE transport and cancel request

RT-4c adds a provider-free transport over the accepted RT-4b state machine.

Implementation contract:

- [x] add `POST /realtime/text/sessions`;
- [x] add one-consumer `GET .../events` using `text/event-stream`;
- [x] add separate cooperative `POST .../cancel`;
- [x] add active capacity, idle TTL, maximum duration, pending-event, and event-byte bounds;
- [x] preserve RT-4b 512-character chunk and 4096-character aggregate bounds;
- [x] remove consumed/disconnected sessions and clear retained input;
- [x] return bounded public-safe 404/409/410/429 problems;
- [x] do not echo input text in responses or SSE;
- [x] keep `hard_cancel_supported=false`;
- [x] keep Framework import, provider execution, Flutter, dependencies, and versions unchanged.

Exact change surface: fifteen files listed in `docs/v300_rt4_backend_sse_transport.md`.

RT-4c acceptance result:

- [x] implementation and 16 focused/config test cases prepared
- [x] implementation committed and pushed at `72622cab2e73699adaff4b628cfbc4b14323a23a`
- [x] compileall passed
- [x] dedicated RT-4c gate passed in a commit-scoped reconstructed candidate
- [x] focused Backend 16 passed
- [x] Backend full 192 passed
- [x] Flutter analyze and Flutter 200 passed
- [x] exact fifteen-file review passed
- [x] changed-content private scan passed
- [x] `git diff --check` passed
- [x] explicit operator approval and acceptance completed

Stop rule: do not import Framework, call `ask_stream()`, execute a provider, change Flutter, claim provider-level hard cancel, add TTS queue control, or start RT-4d in RT-4c. Provider execution remains false.

### RT-4d — FW root-public streaming adapter and cooperative cancel

RT-4d connects RT-4c transport sessions to FW v5.4.0 root-public text streaming
behind an explicit default-off gate.

Implementation contract:

- [x] use only `framework.create_text_chat_session()`;
- [x] consume public `TextChatSession.ask_stream()` chunks;
- [x] request public `TextChatSession.interrupt()` on Backend cancel;
- [x] close/dispose the public text session when the stream ends;
- [x] keep `cancel_mode=cooperative` and `hard_cancel_supported=false`;
- [x] avoid Framework internal imports and DRC provider clients;
- [x] keep normal tests fake-public-session-only;
- [x] keep Flutter unchanged.

RT-4d acceptance result:

- [x] implementation and focused fake public-session tests prepared
- [x] implementation committed and pushed at `f713f515eef723a1d51cfbe35c1dfe16e3547420`
- [x] compileall passed
- [x] dedicated RT-4d gate passed in a commit-scoped reconstructed candidate
- [x] focused Backend 32 passed
- [x] Backend full 192 passed
- [x] Flutter analyze and Flutter 200 passed
- [x] exact fourteen-file review passed
- [x] changed-content private scan passed
- [x] `git diff --check` passed
- [x] explicit operator approval and acceptance completed

Detailed contract:
`docs/v300_rt4_framework_public_streaming_adapter.md`.

Stop rule: do not import Framework internals, add a DRC provider client, claim
provider-level hard cancel, read/display transcript text, change Flutter UI, or
add TTS queue control. RT-4c and RT-4d are accepted.

### RT-4e — Flutter stream client/controller without HomeScreen integration

RT-4e adds Flutter-only primitives for consuming the accepted Backend text
stream contract.

Implementation contract:

- [x] add immutable Flutter stream models;
- [x] preserve 512-character chunk and 4096-character accumulated output bounds;
- [x] preserve `cancel_mode=cooperative` and `hard_cancel_supported=false`;
- [x] add injectable HTTP/SSE client with fake `http.BaseClient` tests;
- [x] parse UTF-8 SSE incrementally by blank-line frame boundaries;
- [x] validate `id`, `event`, and normalized DRC JSON `data`;
- [x] reject malformed, mismatched, stale, duplicate, out-of-order, and oversized events;
- [x] add ChangeNotifier controller with immutable exposed state;
- [x] reject active-stream replacement and ignore obsolete callbacks;
- [x] support safe idempotent cooperative cancel;
- [x] close local event subscription after terminal events;
- [x] avoid HomeScreen integration, real network execution, Framework imports, provider clients, reconnect/resume, WebSocket, dependencies, versions, and TTS queue control.

RT-4e acceptance result:

- [x] implementation and fake transport tests prepared
- [x] Flutter normalized realtime stream models added
- [x] injectable HTTP/SSE client added
- [x] ChangeNotifier stream controller added
- [x] incremental UTF-8 SSE parsing accepted
- [x] CRLF/LF HTTP chunk-boundary handling accepted
- [x] same-origin `events_path` and `cancel_path` enforcement accepted
- [x] monotonic sequence/session/turn validation accepted
- [x] event type/state/payload/terminal validation accepted
- [x] Unicode code-point chunk/output/safe-message bounds accepted
- [x] cooperative cancel only with `hard_cancel_supported=false`
- [x] failed/terminal/dispose subscription cleanup accepted
- [x] active-stream replacement and simultaneous start rejection accepted
- [x] local cancel remains `cancelRequested` when a delayed `streamStarted` event arrives
- [x] fake/in-memory transport only in normal tests
- [x] HomeScreen integration remains absent
- [x] STT transcript handoff remains absent
- [x] real Backend/Framework/provider execution was not performed by RT-4e
- [x] TTS queue/flush/barge-in remains RT-5 work
- [x] compileall passed
- [x] dedicated RT-4e gate passed
- [x] Backend full tests passed: 192 passed, 1 existing warning
- [x] Flutter analyze passed
- [x] focused Flutter RT-4e tests passed: 33 passed
- [x] Flutter full tests passed: 233 passed
- [x] exact twelve-file review passed
- [x] changed-content private scan passed
- [x] `git diff --check` passed
- [x] explicit operator approval received
- [x] implementation committed and pushed

Detailed contract:
`docs/v300_rt4_flutter_stream_client_controller.md`.

Stop rule: do not edit HomeScreen, integrate the controller into UI, connect STT
transcripts, execute a real Backend/Framework/provider, import Framework, add a
DRC provider client, claim provider-level hard cancel, add reconnect/resume,
add WebSocket, add dependencies, change versions, or implement TTS
queue/flush/barge-in. Historical next marker after RT-4e: RT-4f was not yet
complete. RT-4f is now COMPLETED / ACCEPTED after RT-4f4 operator acceptance.

RT-4e verification record:

```text
implementation commit: 1cfe6134b0d19a4d14ebcf3ec76812ce07dac261
implementation pushed: true
compileall: passed
dedicated RT-4e gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused Flutter RT-4e tests: 33 passed
Flutter full tests: 233 passed
exact twelve-file review: passed
changed-content private scan: passed
git diff --check: passed
explicit operator approval: accepted
RT-4e status: COMPLETED / ACCEPTED / PUSHED
RT-4f authorization: AUTHORIZED / NOT_STARTED
```

### RT-4f1 — Current behavior inventory and exact small-commit split

RT-4f1 is docs/test-only and changes no runtime behavior.

Current factual inventory:

- [x] HomeScreen injects `BackendApiClient` and optional `VoiceOutputAudioEngine`.
- [x] HomeScreen owns existing loading/error, voice-input demo, post-advice chat, and voice-output player state.
- [x] HomeScreen starts initial backend/demo/health checks in `initState()` and disposes its text/audio controllers.
- [x] HomeScreen has no realtime stream import, client, controller, listener, or stream UI.
- [x] `main.dart` constructs `const HomeScreen()` and provides no realtime stream injection.
- [x] `VoiceInputDemoRequestResponse` has a nullable `transcript` field.
- [x] HomeScreen calls the metadata-only `/demo/voice-input` placeholder.
- [x] `VoiceInputDemoService.submit_request()` always returns `accepted=False`, `request_state="not_started"`, and `transcript=None`.
- [x] Accepted real RT-3 transcript reaches Flutter/HomeScreen: false.
- [x] Metadata-only voice-input demo transcript: always null in production.
- [x] Fake Backend transcript routes wired to Flutter: false.
- [x] Real-STT transcript public API route: absent.
- [x] Real-STT transcript Flutter handoff: absent.
- [x] App-owned transcript-to-stream handoff: absent.
- [x] The private real-STT transcript is held only by the private operator result handoff field.
- [x] RT-4e provides `RealtimeTextStreamClient` with injected `http.Client` and base URL.
- [x] RT-4e provides `RealtimeTextStreamController` with start/cancel/dispose and immutable public state.
- [x] Backend create/events/cancel routes exist under `/realtime/text`.
- [x] CORS uses configured origins and Framework text streaming is default-off.
- [x] Configured real acceptance would prove local Backend/FW streaming and cooperative cancel only.
- [x] RT-5 TTS queue/flush/barge-in remains excluded.

Resolved RT-4f split:

```text
RT-4f1  COMPLETED / ACCEPTED / PUSHED
        Current behavior inventory and exact small-commit split.
        Docs/test-only. No runtime change.
RT-4f2  COMPLETED / ACCEPTED / PUSHED
        Flutter HomeScreen stream presentation and controller lifecycle wiring
        with injected fake stream client/controller and bounded manual test
        input. No real Backend, Framework, provider, or STT handoff.
RT-4f3  COMPLETED / ACCEPTED / PUSHED
        App-owned provider-neutral transcript-to-stream handoff boundary.
        Connects an injected/fake provider-neutral final transcript result to
        exactly one stream start with an independent in-flight guard. No real
        provider/operator execution and no configured real transcript source.
RT-4f4  COMPLETED / ACCEPTED / PUSHED
        Default-off configured Flutter runtime wiring for configured local
        Backend/FW streaming and cooperative cancel operator
        execution and visible UI acceptance. Real-STT-to-stream acceptance can
        be performed only if a safe transcript transport/exposure boundary is
        separately reviewed and exists; without that boundary, RT-4f4 does not
        complete or claim real STT transcript handoff. Private local
        environment only.
```

RT-4f protected boundaries:

- [x] do not add a DRC provider client;
- [x] do not import Framework internal modules;
- [x] do not weaken same-origin checks;
- [x] do not add reconnect/resume or WebSocket;
- [x] do not add always-on/background microphone;
- [x] do not persist raw audio or transcripts by default;
- [x] do not add TTS queue/flush/barge-in;
- [x] do not claim provider-level immediate cancellation;
- [x] do not modify FW repository;
- [x] do not change dependencies, versions, or platform permissions unless a later reviewed split proves it necessary.

Detailed inventory:
`docs/v300_rt4f_ui_streaming_acceptance_inventory.md`.

Dedicated gate:
`scripts/check_v300_rt4f_ui_streaming_acceptance_inventory.py`.

RT-4f1 acceptance record:

```text
implementation commit: f54e8638f0255b28e015702bc64b624a6d4a36af
implementation pushed: true
compileall: passed
dedicated RT-4f1 gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
Flutter full tests: 233 passed
exact seven-file review: passed
git diff --check: passed
factual transcript inventory correction: accepted
explicit operator approval: accepted
RT-4f1 status: COMPLETED / ACCEPTED / PUSHED
RT-4f2 authorization: AUTHORIZED / NOT_STARTED
```

### RT-4f2 — HomeScreen fake streaming presentation and lifecycle wiring

RT-4f2 is completed, accepted, and pushed at implementation commit
`1e1a4b27a0fe7c105eec344bfde39afe6a077f8a`. It adds HomeScreen ownership of
an optional `RealtimeTextStreamController` factory, controller listener
registration/removal, owned controller and manual input controller disposal,
bounded manual input validation, visible `idle`, `connecting`, `streaming`,
`cancel_requested`, `completed`, `cancelled`, `failed`, `closed`, and
`unconfigured` presentation, incremental output display, cooperative cancel UI,
and bounded public-safe error display.

Normal `const HomeScreen()` remains unconfigured because `main.dart` is
unchanged. Focused tests use fake BackendApiClient and fake/in-memory HTTP with
the accepted RT-4e client/controller. RT-4f2 adds no STT transcript handoff, no
real Backend/FW/provider execution, no automatic TTS start, no
TTS queue/flush/barge-in, no provider-level hard cancel, no reconnect/resume,
and no WebSocket.

Detailed contract:
`docs/v300_rt4f2_home_screen_stream_ui.md`.

Dedicated gate:
`scripts/check_v300_rt4f2_home_screen_stream_ui.py`.

RT-4f2 acceptance record:

```text
implementation commit: 1e1a4b27a0fe7c105eec344bfde39afe6a077f8a
implementation pushed: true
compileall: passed
dedicated RT-4f2 gate: passed
Backend full tests: 192 passed, 1 existing warning
Flutter analyze: passed
focused RT-4f2 widget tests: 9 passed
Flutter full tests: 242 passed
exact ten-file implementation review: passed
git diff --check: passed
HomeScreen unrelated formatting removal: accepted
HomeScreen implementation numstat: 239 additions / 0 deletions
bounded safe problem display: 240 Unicode code points
input echo assertion correction: accepted
fake/in-memory HTTP only: true
real network execution: false
STT transcript handoff added: false
automatic TTS start: false
hard cancel supported: false
explicit operator approval: accepted
RT-4f2 status: COMPLETED / ACCEPTED / PUSHED
RT-4f3 authorization: AUTHORIZED / NOT_STARTED
```

RT-4f2 did not connect a transcript to streaming. The current source still has
no app-visible accepted real-STT transcript. RT-4f3 is responsible for defining
and implementing the missing app-owned, provider-neutral transcript-to-stream
handoff boundary using injected/fake transcript and fake stream dependencies.
RT-4f3 must not claim that the private real-STT operator transcript already
reaches Flutter.

### RT-4f3 — App-owned provider-neutral transcript-to-stream handoff

RT-4f3 is completed, accepted, and pushed at implementation commit
`d651a00be8713a70be3a46524f33c787299bbe9c`. It adds
`ProviderNeutralTranscriptResult` and `RealtimeTextStreamTranscriptHandoff` as
an app-owned boundary between an injected provider-neutral final transcript
result and the accepted RT-4e realtime controller.

Implementation contract:

- [x] provider-neutral transcript model has opaque `resultId`, `text`, and `isFinal` only;
- [x] model carries no provider name, model name, confidence, audio path, provider payload, raw response, or credential;
- [x] handoff service does not own or dispose `RealtimeTextStreamController`;
- [x] handoff owns no HTTP client, BackendApiClient, microphone/STT object, or provider client;
- [x] active controller state is rejected before invoking the transcript provider;
- [x] simultaneous invocation is protected by an independent private in-flight guard;
- [x] duplicate calls do not invoke the provider again or change the active acquiring phase to rejected;
- [x] final, nonempty transcript text is bounded to 4096 Unicode code points;
- [x] opaque result ID is trimmed, nonempty, and bounded to 128 Unicode code points;
- [x] consumed result IDs are remembered in-memory only and bounded to 32 entries;
- [x] consumed result ID is marked before exactly one `controller.start(inputText:)`;
- [x] no automatic retry occurs, including after controller start failure;
- [x] transcript text and result ID are not exposed in handoff public state;
- [x] safe messages are whitespace-compacted and bounded to 240 Unicode code points;
- [x] disposed/late provider completion does not notify or start a stream.

HomeScreen contract:

- [x] optional `RealtimeTextStreamTranscriptHandoffFactory` is accepted;
- [x] normal `const HomeScreen()` remains valid and handoff-unconfigured;
- [x] `main.dart` remains unchanged;
- [x] handoff factory is called once in `initState()` only when the RT-4f2 realtime controller exists;
- [x] the exact HomeScreen-owned realtime controller is passed to the handoff factory;
- [x] HomeScreen owns/listens to/disposes the handoff before disposing the realtime controller;
- [x] UI exposes transcript handoff keys, phase, safe error, privacy note, and explicit injected/provider-neutral start button;
- [x] transcript text and result ID are not displayed;
- [x] transcript text is not copied into the manual stream input;
- [x] `_voiceInputDemoResponse.transcript` is not wired to handoff;
- [x] no automatic TTS starts.

Acceptance verification:

- [x] compileall passed with only the existing backend `.pytest_cache` list warning;
- [x] dedicated RT-4f3 source-tree gate passed;
- [x] Backend full tests passed: 192 passed, 1 existing warning;
- [x] Flutter analyze passed;
- [x] focused RT-4f3 unit tests passed: 15;
- [x] focused RT-4f3 HomeScreen widget tests passed: 9;
- [x] Flutter full tests passed: 266;
- [x] exact thirteen-file implementation surface and `git diff --check` passed;
- [x] HomeScreen implementation numstat was 115 additions / 0 deletions;
- [x] three-or-more simultaneous invocation coverage kept provider/create counts at 1;
- [x] concurrent create-failure coverage kept provider/create counts at 1;
- [x] explicit operator approval, commit, and push completed.

RT-4f3 adds an interface/boundary, not a real transcript source. The current
accepted real-STT transcript still does not reach Flutter. All transcript
acceptance tests use injected fake results. RT-4f3 performs no real
Backend/FW/provider/STT execution, adds no Backend transcript route, and does
not configure runtime wiring. RT-4f4 later accepted configured local Backend/FW
text streaming and cooperative cancel visible UI behavior with manual bounded
input. Real transcript source remains unconfigured, real-STT-to-stream
acceptance remains false, and RT-5 TTS queue/flush/barge-in remains excluded.

Detailed contract:
`docs/v300_rt4f3_transcript_stream_handoff.md`.

Dedicated gate:
`scripts/check_v300_rt4f3_transcript_stream_handoff.py`.

### RT-4f4 - Configured local stream acceptance wiring

RT-4f4 implementation is committed and pushed at
`9b19e379634a718df2ab3ed5eb49bb20bfe7e240`; the later configured operator
acceptance is completed and accepted. Operator evidence is not committed or
pushed. The RT-4f4 milestone is COMPLETED / ACCEPTED / PUSHED. It adds
`ConfiguredRealtimeTextStreamRuntime` and default-off `main.dart` wiring so the
normal Flutter startup path can construct the accepted RT-4e
`RealtimeTextStreamController` from the existing `BackendApiClient.baseUrl`
when `DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM=true`.

Implementation contract:

- [x] Flutter configured realtime text stream runtime is default-off;
- [x] disabled runtime returns no controller factory and does not construct an HTTP client;
- [x] existing `DRC_BACKEND_API_BASE_URL` / `BackendApiClient.baseUrl` is reused;
- [x] no separate Backend URL configuration surface is added;
- [x] only absolute `http` and `https` URLs with nonempty host, no user info, and no fragment are accepted;
- [x] invalid URLs safely return unconfigured without throwing or exposing raw URL text;
- [x] HTTP client construction is lazy and happens only when the controller factory is invoked;
- [x] each factory invocation creates an independent `http.Client`, `RealtimeTextStreamClient`, and `RealtimeTextStreamController`;
- [x] controller dispose closes the HTTP client through accepted RT-4e ownership;
- [x] runtime construction, factory lookup, and widget pump start no stream HTTP request;
- [x] `DailyRhythmCompanionApp` injects `BackendApiClient` and optional realtime controller factory into HomeScreen;
- [x] HomeScreen itself remains unchanged and keeps existing RT-4f2 lifecycle ownership;
- [x] RT-4f3 transcript handoff remains unconfigured unless separately injected.

Operator acceptance record:

- [x] configured Flutter stream runtime enabled for operator execution;
- [x] configured local Backend/FW execution passed;
- [x] input source was bounded manual input only;
- [x] real transcript source configured: false;
- [x] real-STT-to-stream executed: false;
- [x] SSE events request observed;
- [x] stream event counts: `stream_started=1`, `stream_chunk=23`, `stream_completed=1`;
- [x] chunks arrived at multiple distinct times;
- [x] real incremental streaming accepted;
- [x] incremental UI output before terminal confirmed;
- [x] completed terminal confirmed;
- [x] duplicate start blocked while active;
- [x] cancel button enabled only while active;
- [x] cooperative cancel POST returned HTTP 200;
- [x] `cancel_requested` UI phase confirmed;
- [x] cancelled terminal confirmed;
- [x] partial output retained at cancellation;
- [x] output stopped after cancelled;
- [x] start button re-enabled after cancelled;
- [x] cancel button disabled after cancelled;
- [x] cancel mode: cooperative;
- [x] `hard_cancel_supported=false`;
- [x] automatic TTS start: false;
- [x] provider-neutral transcript handoff: unconfigured;
- [x] private evidence committed: false;
- [x] Backend Framework-stream flag restored off;
- [x] DRC and FW working trees clean after execution.

RT-4f and RT-4 are COMPLETED / ACCEPTED. Real transcript source remains
unconfigured, private real-STT operator output does not reach Flutter,
real-STT-to-stream was not executed or accepted, cooperative cancel only
remains the boundary, provider-level hard cancel is not claimed, automatic TTS
is not started, RT-5 is NOT_STARTED / NOT_AUTHORIZED, and RT-5 TTS
queue/flush/barge-in remains excluded.

Detailed contract:
`docs/v300_rt4f4_configured_local_stream_acceptance.md`.

Dedicated gate:
`scripts/check_v300_rt4f4_configured_local_stream_acceptance.py`.

## RT-5f2 accepted implementation checkpoint

```text
RT-5f2 COMPLETED / ACCEPTED / PUSHED
implementation commit: c538dc89c2aa9780cd3014aa4ba11c17a9e378e6
corrective commit: b7bd436196210f27782b64c1a094aa65d6893915
original surface: exact nine files
corrective surface: exact four files
RT-5f3: COMPLETED / ACCEPTED / PUSHED
```

- [x] Compose fake capture, staging, transcript, stream, and RT-5c output.
- [x] Invalidate old work with a private operation epoch.
- [x] Bound confirmed foreground speech events and duplicate memory.
- [x] Reuse cooperative stream cancel and local queue/player flush only.
- [x] Block turns after local stop failure until a later speech retry succeeds.
- [x] Require exclusive voice output before capture and terminal enqueue.
- [x] Recheck exclusivity after synchronous phase listeners return.
- [x] Require processed `itemId`/`generation` to match the enqueue item.
- [x] Preserve public-state privacy and inert late completions.
- [x] Keep Backend, main.dart, HomeScreen, FW, dependencies, and versions unchanged.
- [x] Review exact nine-file implementation and four-file correction.
- [x] Pass Backend 204, Flutter analyze, focused 26, and full 381.
- [x] Pass privacy/fake-only review and `git diff --check`.
- [x] Push implementation and corrective commits.
- [x] Verify clean DRC/FW working trees.

Detailed accepted contract:
`docs/v300_rt5f2_integrated_voice_turn_soft_barge_in_contract.md`.


## RT-5f3 accepted implementation checkpoint

```text
RT-5f3: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 888814d09fad75039733a4a94719454e0a69db63
implementation commit: 75504424c37222234ea8a4314d01ce386ff92d23
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
exact implementation surface: 20 files
acceptance sync surface: exact seven files
real operator acceptance: NOT_EXECUTED / NOT_CLAIMED
RT-5f4: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
```

- [x] Keep the configured integrated runtime default-off.
- [x] Require both accepted configured text-stream and voice-output gates.
- [x] Require session-local opt-in and explicit Start/Stop capture actions.
- [x] Keep speech activity disarmed during initial capture.
- [x] Arm only during staging, transcript acquisition, streaming, or voice output.
- [x] Use a dedicated stream/TTS ownership graph separate from manual UI resources.
- [x] Drain/drop PCM16 and keep amplitude/audio data out of public state and UI.
- [x] Require three consecutive samples and one event per arming generation.
- [x] Disarm on opt-out, background, event, terminal phase, and dispose.
- [x] Preserve RT-5f2 queue exclusivity and processed-item identity checks.
- [x] Add metadata-only HomeScreen presentation and synthetic focused tests.
- [x] Add exact twenty-file contract and dedicated gate.
- [x] Pass the dedicated gate in the real Git checkout.
- [x] Pass Backend full: 204 passed, 1 existing warning.
- [x] Pass Flutter analyze: no issues.
- [x] Pass focused Flutter: 53 passed.
- [x] Pass full Flutter: 408 passed.
- [x] Pass exact surface, privacy, and `git diff --check` review.
- [x] Receive explicit commit approval.
- [x] Commit and push exact twenty-file implementation at `75504424c37222234ea8a4314d01ce386ff92d23`.
- [x] Verify post-push DRC working tree clean.
- [x] Preserve real operator acceptance, audible barge-in quality, provider hard cancel, FW real queue flush, and release readiness as non-claims.

Detailed accepted contract:
`docs/v300_rt5f3_default_off_home_screen_speech_activity_contract.md`.
Historical acceptance-sync gate:
`scripts/check_v300_rt5f3_default_off_home_screen_speech_activity_contract.py`.
