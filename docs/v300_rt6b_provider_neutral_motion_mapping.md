# Daily Rhythm Companion v3.0.0 RT-6b provider-neutral motion mapping

Updated: 2026-08-01

## Status

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6a implementation: cbcb218aa54d286da7515a01e899121b22d8f3fc
RT-6a acceptance sync: 6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68
RT-6b: IMPLEMENTED / AWAITING_REVIEW
RT-6b baseline: 6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68
RT-6b implementation commit/push: NOT_AUTHORIZED
RT-6c through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-6b adds a pure DRC-owned mapping boundary between accepted realtime
lifecycle facts and bounded provider-neutral character-motion plans. The mapper
is deterministic and stateless. It does not own a Framework session, motion
runtime, route, network client, queue, timer, UUID source, clock, random source,
or mutable global state.

RT-6b is fake-only planning work. It does not send motion. FW root-public mock
session integration remains RT-6c. Flutter presentation remains RT-6d.
HomeScreen wiring remains RT-6e. Configured local mock-motion acceptance
remains RT-6f. Real Live2D/VTS execution remains blocked in RT-7.

## Exact change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6b_provider_neutral_motion_mapping.md
scripts/check_v300_rt6b_provider_neutral_motion_mapping.py
backend/app/models/character_motion.py
backend/app/services/character_motion_mapper.py
backend/tests/test_character_motion_mapper.py
```

```text
documentation/static gate: 7 files
Backend runtime: 2 new files
Backend focused test: 1 new file
total: exact ten files
```

No existing Backend runtime file, existing test, API route, Flutter file,
Framework file, dependency, lockfile, platform manifest, environment profile,
asset, version, or release record changes in RT-6b.

## App-owned lifecycle facts

```text
idle
listening
transcribing
thinking
responding
tts_preparing
speaking
motion_active
interrupted
completed
failed
closed
unavailable
unknown
```

`tts_preparing` is app-owned and reserved for later voice-output orchestration.
It is not added to the existing `RealtimeState` enum by RT-6b.

`motion_active` is a recursion stop fact. It must never generate another motion
plan. `unknown` fails closed and is ignored.

## App-owned cue vocabulary

```text
greeting
thinking
happy
tired_supportive
speaking
idle
```

The vocabulary remains compatible with the existing metadata-only DRC motion
demo. Automatic lifecycle mapping in RT-6b emits only:

```text
idle
thinking
speaking
tired_supportive
```

`greeting` and `happy` are reserved for later explicit/manual or advice-driven
mapping and are not generated automatically by RT-6b.

## App-owned command intent vocabulary

```text
expression
speaking_state
idle_motion
stop_motion
reset_expression
```

These are DRC-owned strings. RT-6b imports no FW module or FW type. A later
RT-6c adapter may convert this bounded plan to released FW root-public motion
requests under its own exact contract.

## Model contract

`CharacterMotionMappingInput` accepts only:

```text
schema_version
fact
source_event_type
session_id
turn_id
character_id
```

Arbitrary metadata dictionaries are prohibited. IDs and source event type are
bounded to 128 characters. This prevents an unbounded or secret-bearing
metadata channel from being introduced by the mapper.

`CharacterMotionCommand` contains:

```text
order: 1 through 3
intent
expression_id: optional, max 64 characters
motion_event: optional bounded enum
speaking: optional bool
```

Command payload validation is intent-specific:

```text
expression       requires only expression_id
speaking_state   requires only speaking
idle_motion      requires only motion_event=idle
stop_motion      accepts no payload
reset_expression accepts no payload
```

`CharacterMotionPlan` contains a mapped/ignored outcome, source fact, optional
cue, bounded reason code, maximum three commands, and the same bounded safe
IDs. Commands must use contiguous one-based order. Ignored plans contain no cue
and no commands. Mapped plans contain a cue and at least one command.

## Exact mapping table

| Lifecycle fact | Cue | Ordered commands |
|---|---|---|
| `idle` | `idle` | `speaking_state(false)` -> `reset_expression` -> `idle_motion(idle)` |
| `listening` | `idle` | `speaking_state(false)` -> `expression(supportive)` |
| `transcribing` | `thinking` | `speaking_state(false)` -> `expression(thinking)` |
| `thinking` | `thinking` | `speaking_state(false)` -> `expression(thinking)` |
| `responding` | `thinking` | `speaking_state(false)` -> `expression(thinking)` |
| `tts_preparing` | `thinking` | `speaking_state(false)` -> `expression(thinking)` |
| `speaking` | `speaking` | `expression(speaking)` -> `speaking_state(true)` |
| `motion_active` | none | ignored, no commands |
| `interrupted` | `idle` | `stop_motion` -> `speaking_state(false)` -> `reset_expression` |
| `completed` | `idle` | `speaking_state(false)` -> `reset_expression` -> `idle_motion(idle)` |
| `failed` | `tired_supportive` | `stop_motion` -> `speaking_state(false)` -> `expression(supportive)` |
| `closed` | `idle` | `stop_motion` -> `speaking_state(false)` -> `reset_expression` |
| `unavailable` | `idle` | `stop_motion` -> `speaking_state(false)` -> `reset_expression` |
| `unknown` | none | ignored, no commands |

Stop rules:

```text
- No plan contains more than three commands.
- motion_active never produces recursive commands.
- unknown is ignored rather than guessed.
- interrupted, failed, closed, and unavailable begin with stop_motion.
- speaking is the only fact that sets speaking=true.
- idle and completed restore speaking=false, reset expression, and idle motion.
```

## Existing RealtimeState mapping

```text
RealtimeState.IDLE          -> idle
RealtimeState.LISTENING     -> listening
RealtimeState.TRANSCRIBING  -> transcribing
RealtimeState.THINKING      -> thinking
RealtimeState.RESPONDING    -> responding
RealtimeState.SPEAKING      -> speaking
RealtimeState.MOTION        -> motion_active / ignored
RealtimeState.INTERRUPTED   -> interrupted
RealtimeState.FAILED        -> failed
RealtimeState.COMPLETED     -> completed
RealtimeState.CLOSED        -> closed
RealtimeState.UNAVAILABLE   -> unavailable
RealtimeState.UNKNOWN       -> unknown / ignored
```

The existing `backend/app/models/realtime.py` is not modified. There is no
existing `RealtimeState` equivalent for `tts_preparing`; later orchestration
must create that app-owned fact explicitly.

## Determinism and bounded behavior

For the same validated input, `CharacterMotionMapper.map()` returns the same
value-equivalent plan. It uses no current time, random value, generated ID,
external configuration, environment variable, file, database, network call,
provider callback, or mutable state.

The mapper preserves only the bounded source event type, session ID, turn ID,
and character ID. It does not copy arbitrary source payloads or metadata.

## Focused test contract

The RT-6b focused tests cover:

```text
- exact mapping for every mapped lifecycle fact
- exact command order and payload
- maximum three commands
- recursion stop for motion_active
- fail-closed unknown handling
- complete existing RealtimeState mapping
- deterministic value equality
- safe ID preservation
- only speaking sets speaking=true
- stop-first terminal/failure behavior
- extra/private metadata rejection
- overlong ID rejection
- ambiguous command rejection
- non-contiguous and unbounded plan rejection
- wrong input type rejection
- source AST contains no FW import
```

Generation-side verification for this candidate:

```text
focused RT-6b Backend tests: 37 passed
Backend full tests: 241 passed
Flutter runtime changed: false
Flutter tests changed: false
```

These generation-side results do not replace real-checkout review, full
Windows-host verification, explicit approval, commit, push, or clean-tree
verification.

## Dedicated gate contract

The dedicated gate verifies:

```text
v300_rt6b_status: implemented-awaiting-review
v300_rt6b_exact_change_surface: True
v300_rt6b_change_file_count: 10
v300_rt6b_backend_runtime_file_count: 2
v300_rt6b_backend_test_file_count: 1
v300_rt6b_existing_motion_demo_changed: False
v300_rt6b_existing_realtime_models_changed: False
v300_rt6b_api_routes_changed: False
v300_rt6b_flutter_changed: False
v300_rt6b_framework_changed: False
v300_rt6b_dependencies_changed: False
v300_rt6b_fw_imported: False
v300_rt6b_mapping_deterministic: True
v300_rt6b_max_commands_per_plan: 3
v300_rt6b_recursive_motion_fact_ignored: True
v300_rt6b_unknown_fact_ignored: True
v300_rt6b_network_execution: False
v300_rt6b_provider_execution: False
v300_rt6b_vts_connection_used: False
v300_rt6b_live2d_runtime_loaded: False
v300_rt6c_authorized: False
```

Normal mode requires DRC HEAD/origin main at baseline
`6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68` and a clean FW v5.4.0 checkout at
`d313eb6acb643103fe25988720ebee5976a04f78`. Snapshot mode skips Git history
and FW checkout checks for extracted candidate reconstruction.

## Verification commands

Run from the DRC repository root while RT-6b remains uncommitted:

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
git ls-files --others --exclude-standard
```

Expected baseline and candidate results:

```text
focused RT-6b Backend: 37 passed
Backend full: 241 passed
Flutter analyze: No issues found
Flutter full: 411 passed
exact surface: 10 files
FW execution: none
```

## Non-actions and non-claims

RT-6b changes no existing motion-demo behavior or route. The existing demo
continues returning metadata-only `not_started`, `motion_sent=false`, and
`vts_connection_used=false` responses.

RT-6b does not:

```text
- import or call AI Character Framework
- create or own MotionSession
- open a network or VTS WebSocket connection
- read VTS tokens, credentials, private paths, or model files
- load Live2D runtime or provider SDKs
- send motion, expression, speaking, or stop commands
- add an API route or Flutter client/controller
- wire HomeScreen
- change microphone, audio, STT, LLM, or TTS runtime
- claim real adapter support or acceptance
- authorize RT-6c through RT-6f
- claim v3.0.0 release readiness
```

## Next action

```text
Review the exact ten-file RT-6b candidate.
RT-6b commit/push remains NOT_AUTHORIZED.
RT-6c implementation remains NOT_AUTHORIZED.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
