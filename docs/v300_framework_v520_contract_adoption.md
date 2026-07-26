# v3.0.0 RT-1a AI Character Framework v5.2.0 public-contract adoption gate

Updated: 2026-07-26

```text
Parent phase: RT-1 CURRENT / NOT_COMPLETED
Small commit: RT-1a COMPLETED / ACCEPTED
Implementation state: COMPLETED / ACCEPTED
Released Framework snapshot: v5.2.0@c2e247064987c94bf735a359700f0462439b8286
Decision: RT1_MOCK_CONTRACT_INTEGRATION_AUTHORIZED
```

## Purpose

RT-0a through RT-0c remain accepted historical checkpoints. RT-1a does not
rewrite their v5.0.0 or v5.1.0 findings. It verifies the later released
AI Character Framework v5.2.0 public package and decides which DRC v3 phases may
start without claiming real provider/runtime implementation.

RT-1a is docs/test-only. It does not import Framework at DRC runtime, call a
provider, access a microphone, start audio playback, connect to Live2D/VTube
Studio, or modify Backend/Flutter runtime.

## Released Framework snapshot inspected

```text
Repository: murayan1982/ai-character-framework
Released tag: v5.2.0
Tag commit: c2e247064987c94bf735a359700f0462439b8286
Tag comparison: v5.2.0 is identical to c2e247064987c94bf735a359700f0462439b8286
Release scope: mock-safe DRC-driven public realtime contracts
```

Public files inspected:

```text
framework/__init__.py
framework/voice_input.py
framework/voice_input_session.py
framework/voice_input_capability.py
framework/realtime.py
framework/realtime_session.py
framework/output_control.py
framework/motion.py
framework/motion_session.py
framework/capabilities.py
docs/v520_release_readiness_gate.md
docs/v520_final_release_tag_readiness.md
```

## Public contract inventory added by v5.2.0

The released root package exports provider-neutral public boundaries for:

```text
Voice Input / STT contract:
- VoiceInputRequest
- VoiceInputResult
- VoiceInputSession
- VoiceInputSessionInfo
- VoiceInputCapabilities
- create_voice_input_session()

Realtime contract:
- RealtimeState
- RealtimeEventType
- RealtimeEvent
- RealtimeTurn
- RealtimeTurnResult
- RealtimeSession
- RealtimeSessionInfo
- create_realtime_session()

Interrupt and output control contract:
- InterruptRequest
- InterruptResult
- InterruptScope
- InterruptReason
- TTSQueueState
- OutputFlushRequest
- OutputFlushResult
- BargeInPolicy
- BargeInDecision

Motion contract:
- MotionRequest
- MotionResult
- MotionCapability
- MotionSession
- MotionSessionInfo
- create_motion_session()
```

These exports satisfy the release condition needed to begin DRC RT-1's
app-owned state/event/capability/session model against a stable mock-safe public
surface.

## Honest runtime status

v5.2.0 intentionally releases contract skeletons rather than real provider
orchestration.

```text
real STT execution: NOT_IMPLEMENTED
real realtime STT -> LLM -> TTS orchestration: NOT_IMPLEMENTED
incremental transcript events: NOT_IMPLEMENTED
incremental LLM response chunk events: NOT_IMPLEMENTED
provider-level hard cancellation: NOT_IMPLEMENTED
real TTS queue flush/playback stop: NOT_IMPLEMENTED
real barge-in audio detection: NOT_IMPLEMENTED
real Live2D/VTS adapter execution: NOT_IMPLEMENTED
```

The public sessions return typed unavailable/not-implemented/closed results and
mock lifecycle events. DRC must not count mock completion, text fallback, empty
queue flush, or mock motion as configured real execution evidence.

## Important transition findings

### Global capability snapshot is stale for v5.2.0 additions

The released `framework.get_capabilities()` implementation still uses the
`v5.1.capabilities` schema and reports voice input, realtime, and motion as
`public_boundary_missing`, even though v5.2.0 exports those public sessions.

DRC RT-1 must therefore not use the global snapshot as the sole source of truth
for the new v5.2.0 boundaries. The first integration should normalize:

```text
- released public export availability;
- VoiceInputSession.info / capabilities;
- RealtimeSession.info;
- MotionSession.info / capability;
- explicit real-runtime support flags.
```

A later Framework release should align the global capability snapshot with the
v5.2.0 exports.

### Realtime event correlation is only partial

`RealtimeEvent` includes `session_id` and `turn_id`, but does not expose an
app-facing event ID, sequence number, or timestamp. It also lacks partial
transcript and response-chunk event types.

RT-1b should introduce a DRC-owned normalized event envelope with bounded
monotonic sequence and timestamp fields while preserving the Framework event
name, session ID, turn ID, safe message, and public metadata.

### Realtime run_turn is mock-only

`RealtimeSession.run_turn()` emits a deterministic mock lifecycle and returns a
completed result with no real stage execution. DRC may use it for contract and
state-machine tests only.

### Output-control methods are typed but not operational

Interrupt, cancel-current-turn, output-flush, TTS queue state, and barge-in
policy APIs exist. Hard cancellation and real queue/playback control remain
unsupported/not implemented.

### Motion is ready for mock mapping only

The public motion session can complete mock expression/emotion/speaking/gesture
requests. Real Live2D/VTS adapters return typed not-implemented or unavailable
results.

## DRC phase authorization

```text
RT-1: AUTHORIZED / CURRENT
  Scope: DRC-owned realtime state, event, capability, and session models.
  Allowed Framework use: mock-safe v5.2.0 public contracts only.

RT-2: BLOCKED pending RT-1 acceptance
  App microphone permission/capture scope remains a separate commit.

RT-3: BLOCKED_REAL_STT_NOT_IMPLEMENTED
  Public contract exists; real Framework STT execution does not.

RT-4: BLOCKED_REAL_STREAMING_CANCEL_NOT_IMPLEMENTED
  Lifecycle contract exists; incremental transcript/response streaming and
  provider cancel execution do not.

RT-5: BLOCKED_REAL_OUTPUT_CONTROL_NOT_IMPLEMENTED
  Typed interrupt/queue/flush/barge-in contracts exist; real execution does not.

RT-6: PLANNED_AFTER_RT1
  Public mock motion mapping contract exists and may be integrated after the
  core DRC realtime model is accepted.

RT-7: BLOCKED_REAL_MOTION_ADAPTER_NOT_IMPLEMENTED
  Real Live2D/VTS adapter execution is absent.

RT-8 through RT-9: BLOCKED by prerequisite runtime phases.
```

## Next RT-1 implementation split

After RT-1a acceptance, start RT-1b with a Backend-only, provider-free model and
normalization boundary.

Proposed RT-1b change surface:

```text
backend/app/models/realtime_session.py                 new
backend/app/services/realtime_contract_normalizer.py  new
backend/tests/test_realtime_session_contract.py       new
docs/DRC_v300_goal_checklist_small_commit.md
README.md
roadmap.md
tasklist.md
scripts/README.md
```

RT-1b must not add a public API route, microphone dependency, WebSocket/SSE
transport, real provider execution, Flutter UI, or Framework internal import.
Those remain separate small commits after the model contract is accepted.

## RT-1a change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_framework_v520_contract_adoption.md
scripts/check_v300_framework_v520_contract_adoption.py
```

## Explicit non-change surface

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
existing RT-0 inventory/reassessment docs and checks
historical v2.x checklists and release records
AI Character Framework repository/runtime
release ZIPs, tags, GitHub Releases, and private operator evidence
```

```text
DRC runtime changed: false
Existing tests changed: false
Framework runtime changed: false
Real provider execution: false
Microphone access: false
Realtime runtime started: false
```

## Verification

Run from the DRC repository root:

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
git status --short
```

Expected accepted RT-1a marker:

```text
v300_framework_v520_contract_adoption_status: completed-accepted
v300_framework_release_snapshot: v5.2.0@c2e247064987c94bf735a359700f0462439b8286
v300_framework_public_contracts_released: True
v300_framework_real_runtime_ready: False
v300_rt1_authorization: authorized-mock-contract-only
v300_rt3_authorization: blocked-real-stt-not-implemented
v300_rt4_authorization: blocked-real-streaming-cancel-not-implemented
v300_rt5_authorization: blocked-real-output-control-not-implemented
v300_rt6_authorization: planned-after-rt1-mock-motion-contract-available
v300_rt7_authorization: blocked-real-motion-adapter-not-implemented
```

## Acceptance record

Accepted on 2026-07-26 after all of the following passed:

```text
compileall: passed
RT-0a / RT-0b / RT-0c / RT-1a source-tree gates: passed
Backend pytest through .venv: 110 passed, 1 existing warning
Flutter tests: 103 passed
git diff --check: passed
DRC runtime changed: false
Existing tests changed: false
Framework runtime changed: false
Real provider execution: false
Microphone access: false
Realtime runtime started: false
diff review / explicit operator approval: passed
```

## Stop rule

RT-1b may now begin, but only within the accepted Backend-only model and
normalization boundary. Do not add an API route, WebSocket/SSE transport,
microphone access, Flutter UI, provider execution, or Framework internal import.
Do not use v5.2.0 mock completion as real STT, realtime, cancellation, TTS queue,
barge-in, or motion evidence.
