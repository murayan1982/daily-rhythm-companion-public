# Daily Rhythm Companion v3.0.0 RT-6b provider-neutral motion mapping

Updated: 2026-08-01

## Status

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6a implementation: cbcb218aa54d286da7515a01e899121b22d8f3fc
RT-6a acceptance sync: 6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6b implementation baseline: 6ed5f2252c6c6f47fc8c50f577c4f20b7fa0cb68
RT-6b implementation commit: 17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594
RT-6b acceptance-sync commit/push: NOT_AUTHORIZED
RT-6c: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-6d through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
FW v5.4.0: d313eb6acb643103fe25988720ebee5976a04f78
```

## Accepted result

RT-6b accepted the exact ten-file pure DRC-owned mapping implementation at
`17f0c46eb0b4e26e2fdf5ffd4090c15c69f4e594`. The implementation is deterministic, stateless, bounded to three
commands, provider-neutral, and independent of Framework runtime ownership.

```text
compileall: PASS
dedicated RT-6b gate: PASS
focused Backend tests: 37 passed
Backend full tests: 241 passed
Backend dependency warnings: 3
Flutter analyze: No issues found
Flutter full tests: 411 passed
exact ten-file review: PASS
changed-content privacy review: PASS
CRLF-aware git diff --check: PASS
explicit operator approval: ACCEPTED
implementation commit/push: COMPLETED
DRC post-push clean: true
FW clean: true
```

The three Backend warnings came from installed dependency deprecations and did
not fail the suite.

## Accepted exact implementation surface

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
Backend pure-mapping runtime: 2 new files
Backend focused test: 1 new file
total: exact ten files
```

## Accepted model and mapper boundary

The app-owned lifecycle facts are:

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

The bounded cue vocabulary remains compatible with the metadata-only DRC
motion demo:

```text
greeting
thinking
happy
tired_supportive
speaking
idle
```

Automatic lifecycle mapping emits only `idle`, `thinking`, `speaking`, and
`tired_supportive`. `greeting` and `happy` remain reserved.

The app-owned command intents are:

```text
expression
speaking_state
idle_motion
stop_motion
reset_expression
```

RT-6b imports no Framework module or type. Arbitrary metadata dictionaries are
rejected. Source event type, session ID, turn ID, and character ID are bounded
to 128 characters. Expression IDs are bounded to 64 characters. Plans contain
at most three contiguous one-based commands.

## Accepted exact mapping

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

Accepted stop rules:

```text
- No plan contains more than three commands.
- motion_active never produces recursive commands.
- unknown is ignored rather than guessed.
- interrupted, failed, closed, and unavailable begin with stop_motion.
- speaking is the only fact that sets speaking=true.
- idle and completed restore speaking=false, reset expression, and idle motion.
```

## Accepted RealtimeState mapping

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

The existing `RealtimeState` model is unchanged. `tts_preparing` remains an
app-owned fact for later orchestration.

## Exact acceptance-sync surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6b_provider_neutral_motion_mapping.md
scripts/check_v300_rt6b_provider_neutral_motion_mapping.py
```

The acceptance sync changes no Backend runtime or test file. It records the
accepted implementation and moves RT-6c only to exact-contract-review
readiness.

## Non-actions and non-claims

RT-6b and its acceptance sync do not import or execute AI Character Framework,
create a MotionSession, add or change an API route, change Flutter, wire
HomeScreen, open network or VTS WebSocket connections, load a Live2D runtime,
read tokens, credentials, private paths, or model files, or change microphone,
audio, STT, LLM, or TTS runtime.

The existing motion demo remains metadata-only with `not_started`,
`motion_sent=false`, and `vts_connection_used=false`. RT-6b does not claim real
motion execution, real Live2D/VTS support, configured mock-session acceptance,
or v3.0.0 release readiness.

## Next action

```text
Review the exact RT-6c contract separately.
RT-6c implementation remains NOT_AUTHORIZED.
RT-6d through RT-6f remain NOT_AUTHORIZED.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
