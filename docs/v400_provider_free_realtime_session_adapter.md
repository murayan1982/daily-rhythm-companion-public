# DRC-V4-2 Provider-Free FW v6 RealtimeSession Adapter

Status: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED

## Baseline

```text
baseline HEAD: e6ec8fcfbb819a35f5f74be9386ff2c63a5c64f3
branch: main
DRC-V4-1: CLOSED / ACCEPTED
DRC-V4-2: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED
current released version: v3.0.0 RELEASED / ACCEPTED
DRC v4 release status: development work / not released
implementation commit: 5eed0fe5e1b7ad0c7a9bd89afde50629b16d664b
current acceptance-sync baseline: 5eed0fe5e1b7ad0c7a9bd89afde50629b16d664b
acceptance-sync commit: none
acceptance-sync commit / push: NOT_AUTHORIZED
```

## Acceptance Record

```text
implementation baseline: e6ec8fcfbb819a35f5f74be9386ff2c63a5c64f3
implementation commit: 5eed0fe5e1b7ad0c7a9bd89afde50629b16d664b
implementation exact surface: 10 files
compileall: PASS
dedicated gate: PASS
focused Backend: 23 PASS
full Backend: 440 PASS
Flutter analyze: PASS
Flutter full: 500 PASS
final dedicated gate: PASS
git diff --check: PASS
exact surface: PASS
protected review: PASS
privacy/security: PASS
fixed official FW v6 SDK smoke: NOT_RUN / OFFICIAL_ZIP_NOT_SUPPLIED / NON_BLOCKING
corrective history before implementation commit: R1 / R2 / R3 / R4
push verification: HEAD == origin/main == GitHub main == 5eed0fe5e1b7ad0c7a9bd89afde50629b16d664b
working tree after push: clean
```

## Exact Surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
docs/v400_provider_free_realtime_session_adapter.md
scripts/check_v400_provider_free_realtime_session_adapter.py
backend/app/models/framework_v600_realtime.py
backend/app/services/framework_v600_realtime_session_adapter.py
backend/tests/test_framework_v600_realtime_session_adapter.py
```

## Framework v6.0.0 Provenance

```text
Framework release: v6.0.0
Framework annotated tag target: 61e15f62d1ecc5faee016abae82200f8de56c5dd
Framework official ZIP: ai-character-framework_v6.0.0.zip
Framework official ZIP SHA-256: 6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2
Framework distribution name: ai-character-framework
Framework required distribution version: 6.0.0
Framework root-public inventory: 127 names / frozen
```

## Provider-Free Design

DRC-V4-2 adopts the canonical provider-neutral FW v6 RealtimeSession lifecycle
through a provider-free adapter first. The adapter creates only the default
provider-free session:

```text
framework.create_realtime_session()
```

Required runtime boundary:

```text
real_runtime_enabled = False
provider execution = False
network = False
microphone = False
real STT = False
real LLM = False
real TTS = False
playback = False
VTube Studio / real motion = False
Flutter wiring = False
FastAPI route wiring = False
existing v3 runtime replacement = False
```

DRC-V4-2 does not pass `real_runtime_enabled=True`, `voice_input_stage`,
`text_generation_stage`, `voice_output_stage`, `motion_stage`, provider config,
credentials, endpoints, or private paths.

## Installed SDK Root-Import Boundary

The production adapter treats FW v6.0.0 as an installed SDK. It verifies
distribution `ai-character-framework` version `6.0.0` through standard-library
distribution metadata before creating any Framework session.

The only allowed Framework import in production adapter code is:

```text
importlib.import_module("framework")
```

The production adapter does not import `framework.realtime`,
`framework.realtime_session`, `framework.identity`,
`framework.session_diagnostics`, or any other `framework.*` submodule. It does
not mutate `sys.path`, mutate `sys.modules`, invalidate import caches, change
CWD, discover `FRAMEWORK_ROOT`, use a development-checkout fallback, use a
vendor fallback, or probe factory signatures.

## Identity Ownership

Framework owns canonical identity generation. DRC preserves canonical serialized
identity strings exactly and only validates their public forms:

```text
SessionId: fw_session_<32 lowercase hexadecimal characters>
TurnId: fw_turn_<32 lowercase hexadecimal characters>
GenerationId: fw_generation_<32 lowercase hexadecimal characters>
EventSequence: integer >= 1
```

DRC does not replace Framework IDs, reinterpret provider request IDs as
Framework IDs, invent generation IDs, or re-number event sequences.

## Canonical Event Ordering

For the deterministic provider-free completed turn, DRC-V4-2 requires this
exact canonical event order:

```text
1. realtime.turn.started
2. realtime.listening.started
3. realtime.listening.completed
4. realtime.transcript.final
5. realtime.response.started
6. realtime.response.completed
7. realtime.synthesis.started
8. realtime.synthesis.completed
9. realtime.turn.completed
```

EventSequence must be strictly increasing. The admitted turn's GenerationId
must remain stable across all events carrying a generation ID. DRC must not
re-sequence events.

## Exactly-Once Terminal

Framework owns terminal semantics. DRC does not create a second terminal
registry or synthesize duplicate terminal events.

For a normal provider-free completed turn:

```text
exactly one canonical terminal event
terminal event == realtime.turn.completed
terminal == True
returned turn result is terminal
result outcome == completed
result session_id matches session
result turn_id matches terminal event
result generation_id matches terminal generation
```

Inconsistent correlation fails closed with a safe adapter contract failure.

## Stale-Result Ownership

Framework remains authoritative for stale-result rejection. DRC does not create
a generation gate and does not manufacture internal Framework stale completions
from production adapter code.

Ordinary provider-free acceptance requires:

```text
stale_completion_count == 0
duplicate_terminal_count == 0
overflow_count == 0
```

Unit tests may use fake root-public objects to verify safe projection of
non-zero counters.

## Capability Truthfulness

The adapter uses `session.capabilities` as the authoritative source and
preserves bounded public facts:

```text
schema_version
snapshot_scope
snapshot_generation
session_id
supports_text_chat
supports_voice_input
supports_voice_output
supports_motion
real_runtime_enabled
hard_cancel_supported
tts_queue_flush_supported
text generation
voice input
voice output
motion
fake runtime
real runtime
guarded
runtime availability
unavailable reason
cooperative cancel support
provider hard-cancel support
pending flush support
host playback ownership facts
```

The R2 corrected projection models the actual FW v6 nested capability hierarchy
instead of stringifying nested runtime values:

```text
text_generation.runtime.configured
text_generation.runtime.runtime_available
text_generation.runtime.guarded
text_generation.runtime.fake_runtime
text_generation.runtime.real_runtime
text_generation.runtime.unavailable_reason
text_generation.cooperative_cancel_supported
text_generation.provider_hard_cancel_supported

voice_output.runtime.configured
voice_output.runtime.runtime_available
voice_output.runtime.guarded
voice_output.runtime.fake_runtime
voice_output.runtime.real_runtime
voice_output.runtime.unavailable_reason
voice_output.pending_flush_supported
voice_output.provider_hard_cancel_supported
voice_output.playback_ownership
voice_output.host_playback_stop_request_supported
voice_output.host_playback_stop_ack_supported

motion.runtime.configured
motion.runtime.runtime_available
motion.runtime.guarded
motion.runtime.fake_runtime
motion.runtime.real_runtime
motion.runtime.unavailable_reason
motion.provider_neutral_intent_supported
motion.stop_motion_supported
```

The DRC-side non-claim fields are contract invariants, not Framework
`RealtimeCapabilitySnapshot` fields:

```text
real_unified_runtime_available == False
unified_real_pipeline_claimed == False
```

V4-2 required public truth:

```text
supports_text_chat == True
supports_voice_input == True
supports_voice_output == True
supports_motion == False
real_runtime_enabled == False
hard_cancel_supported == False
tts_queue_flush_supported == False
text_generation.runtime.configured == True
text_generation.runtime.runtime_available == True
text_generation.runtime.guarded == False
text_generation.runtime.fake_runtime == True
text_generation.runtime.real_runtime == False
text_generation.streaming_supported == False
text_generation.cooperative_cancel_supported == False
text_generation.provider_hard_cancel_supported == False
voice_input.runtime.fake_runtime == True
voice_input.final_transcript_supported == True
voice_input.audio_chunk_input_supported == False
voice_input.partial_transcript_supported == False
voice_input.input_abort_supported == False
voice_input.backpressure_supported == False
voice_output.runtime.fake_runtime == True
voice_output.pending_flush_supported == False
voice_output.playback_ownership == host
voice_output.host_playback_stop_request_supported == True
voice_output.host_playback_stop_ack_supported == True
motion.runtime.configured == False
motion.runtime.runtime_available == False
motion.runtime.fake_runtime == False
motion.runtime.unavailable_reason == not_wired_to_realtime_session
real unified runtime available: False
unified real STT -> streaming LLM -> TTS -> motion: NOT_CLAIMED
motion in the default unified provider-free turn: not a real motion claim
```

## Typed Interrupt Boundary

The adapter uses root-public Framework interrupt types only: root
`InterruptRequest` and `session.interrupt(...)`. It normalizes public-safe
result facts:

```text
outcome
scope
reason
provider_cancel_supported
provider_cancel_applied
queue_flush_supported
queue_flush_applied
host playback stop facts
safe_message
retryable
```

Required V4-2 claim:

```text
typed cooperative interrupt observation: supported
provider hard cancel: NOT_CLAIMED
real TTS cancellation: NOT_CLAIMED
real playback stop: NOT_EXECUTED
real barge-in acceptance: NOT_CLAIMED
```

The adapter does not parse exception strings to determine capability.

## Safe Diagnostics

The adapter reads diagnostics only through `session.diagnostics_snapshot` and
projects:

```text
session_id
state
phase
is_closed
active_turn_id
active_generation_id
queue_depth
active_generation_count
last terminal safe summary
last_safe_error_code
stale_completion_count
duplicate_terminal_count
overflow_count
```

It does not expose transcript, response text, audio, provider payload, metadata,
raw exception, credential, callback, thread, client, or filesystem value.

Changed-content privacy review covers credentials, API keys/tokens, private or
local paths, raw audio, transcripts, provider payloads, operator evidence, LAN
IPs, screenshots, and private configuration.

## Existing v3 Runtime Preservation

DRC-V4-2 does not alter accepted v3 realtime, voice input, voice output, motion,
Framework v5.5.0 VTS, or configured real-runtime paths. Existing accepted v3
real adapters remain retained. Removal of v3 real adapters is NOT_AUTHORIZED.

## Real Unified Runtime Non-Claim

FW v6.0.0 does NOT provide a production real unified
RealtimeSession.run_turn() pipeline coordinating
real STT -> streaming LLM -> TTS -> motion.

DRC-V4-2 therefore does not claim real unified runtime support and does not
migrate the real STT/LLM/TTS/VTS runtime to RealtimeSession.

## Next-Step Authorization

DRC-V4-2 implementation is **COMPLETED / VERIFIED / ACCEPTED / COMMITTED /
PUSHED / CLOSED**.

Future follow-up work remains separately unauthorized unless explicitly
reviewed: FW submodule adoption, real-runtime stage injection, FastAPI route
wiring, Flutter wiring, provider execution, v3 adapter removal, and production
real unified runtime claims.
