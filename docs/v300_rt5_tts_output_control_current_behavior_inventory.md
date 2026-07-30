# DRC v3.0.0 RT-5 TTS output-control current behavior inventory

Updated: 2026-07-30

## 1. Purpose

RT-5a freezes the current DRC and released AI Character Framework v5.4.0
TTS/output-control boundary before any RT-5 runtime implementation begins.

RT-5a is docs/test-only. It defines terminology, readiness, the exact RT-5
small-commit split, and the stop rule. It does not implement a queue, flush,
automatic TTS, provider cancellation, or speech-triggered barge-in.

## 2. Frozen DRC baseline

```text
DRC baseline HEAD / origin/main:
2b4364f8777cd95a686104dd1868ebcfe72064c9

RT-4f4 implementation:
9b19e379634a718df2ab3ed5eb49bb20bfe7e240

RT-4f4 acceptance docs:
2b4364f8777cd95a686104dd1868ebcfe72064c9

RT-4:
COMPLETED / ACCEPTED
```

RT-5a is evaluated only from the clean accepted DRC baseline plus the exact
seven-file docs/gate candidate.

## 3. Frozen Framework baseline

```text
Framework release:
v5.4.0

Framework HEAD / v5.4.0 tag:
d313eb6acb643103fe25988720ebee5976a04f78

Framework working tree required:
clean
```

DRC must use released public Framework boundaries. RT-5 must not import
Framework internal modules or add a provider-specific TTS client.

## 4. Inspected DRC Backend surface

The inventory inspects at least:

```text
backend/app/api/voice_output_demo.py
backend/app/models/voice_output_demo.py
backend/app/services/voice_output_demo_service.py
backend/app/services/framework_voice_output_adapter.py
backend/app/services/voice_output_artifact_store.py
backend/app/config.py
backend/app/main.py
backend/app/api/realtime_text.py
backend/app/services/realtime_text_stream_service.py
backend/app/services/framework_realtime_text_stream_adapter.py
```

Current Backend facts:

- `POST /demo/voice-output` is one guarded request/response operation.
- The real-TTS path is default-off and requires explicit private operator opt-in.
- One accepted request can expose at most one playable DRC-owned audio URL.
- A Framework-local artifact reference is never returned to Flutter.
- A safe artifact is copied/published through the existing opaque DRC URL.
- Existing artifact retention and cleanup remain unchanged.
- There is no DRC TTS utterance queue.
- There is no queued-item registry or turn-linked generated-audio queue.
- There is no Backend synthesis-cancel endpoint.
- There is no Backend output-flush endpoint.
- There is no provider-synthesis hard-cancel implementation.
- Realtime text terminal events do not automatically submit voice output.

## 5. Inspected Flutter surface

The inventory inspects at least:

```text
app/lib/screens/home_screen.dart
app/lib/models/voice_output_demo.dart
app/lib/models/realtime_text_stream.dart
app/lib/services/backend_api_client.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/audioplayers_voice_output_audio_engine.dart
app/lib/services/realtime_text_stream_controller.dart
app/lib/services/realtime_text_stream_transcript_handoff.dart
app/lib/widgets/character_display_card.dart
```

Current Flutter facts:

- `VoiceOutputAudioPlayerController` owns one current source.
- Local load, play, stop, replay, reset, completion, failure, and expiry exist.
- `stop()` stops Flutter local playback only.
- Local stop does not cancel a Backend synthesis request.
- Local stop does not flush a Framework TTS queue.
- Local stop does not hard-cancel a provider request.
- HomeScreen starts voice generation from an explicit button.
- HomeScreen starts playback from an explicit play button.
- There is no pending utterance queue or generated-audio queue.
- There is no app queue length, current queue item ID, turn-linked item, or
  queue-flush result model.
- Realtime text completion/cancellation does not start voice generation.
- Realtime text cooperative cancel and voice playback stop use separate
  controllers.
- The app-visible real transcript source remains unconfigured.
- There is no speech-triggered real barge-in.

## 6. Inspected Framework public surface

The credential-free probe imports only root `framework` and verifies the
released public names:

```text
VoiceOutputSession
VoiceOutputRequest
VoiceOutputResult
RealtimeSession
RealtimeSessionInfo
InterruptRequest
InterruptResult
OutputFlushRequest
OutputFlushResult
TTSQueueState
BargeInPolicy
BargeInDecision
create_realtime_session
```

Released v5.4.0 facts:

- Public provider-neutral output-control data contracts exist.
- `RealtimeSession` is a mock-safe skeleton, not real orchestration.
- `RealtimeSessionInfo.real_runtime_enabled` defaults to false.
- `RealtimeSessionInfo.hard_cancel_supported` defaults to false.
- `RealtimeSessionInfo.tts_queue_flush_supported` defaults to false.
- `get_tts_queue_state()` reports an empty mock queue.
- The mock queue reports `supports_flush=false`.
- The mock queue reports `supports_provider_cancel=false`.
- Empty mock output flush can return a typed nothing-to-flush result.
- Active real queue flush and playback stop are not implemented by the skeleton.
- `interrupt()` does not perform provider hard cancellation.
- Barge-in policy and decision types describe host-app intent and decisions;
  they do not detect speech or execute provider cancellation.
- The public one-shot voice-output session does not provide a real shared
  realtime TTS queue.

## 7. Current one-shot synthesis lifecycle

```text
explicit HomeScreen action
-> BackendApiClient POST /demo/voice-output
-> guarded VoiceOutputDemoService
-> public/provider-neutral Framework voice-output adapter
-> zero or one accepted audio handoff
-> DRC opaque Web audio URL
-> explicit Flutter playback action
```

This is a one-shot lifecycle. It is not a realtime output queue.

## 8. Current local playback lifecycle

```text
idle
-> loading
-> playing
-> stopped | completed | failed | expired
```

The player keeps one source and uses an operation sequence to ignore stale
local async results. This protects local playback state only.

## 9. Missing queue, flush, cancel, and barge-in behavior

```text
DRC app-owned TTS queue: absent
DRC pending queue clear: absent
DRC Backend synthesis cancel: absent
DRC output flush endpoint: absent
FW real active TTS queue runtime: absent
FW real queue flush: unsupported / not implemented
provider synthesis hard cancel: unsupported / not claimed
automatic stream-to-TTS: absent
real speech-triggered barge-in: absent
real-STT-to-TTS: not executed / not accepted
```

## 10. Terminology separation matrix

| Term | Current meaning | Current support |
| --- | --- | --- |
| local playback stop | Stop the current Flutter audio driver | Exists |
| app-owned pending queue clear | Remove not-yet-synthesized app utterances | Absent |
| Backend synthesis cancellation | Cancel an active `/demo/voice-output` operation | Absent |
| FW TTS queue flush | Clear/stop a Framework-owned active queue | Public type only; real runtime unsupported |
| provider synthesis hard cancellation | Abort provider work immediately | Unsupported / not claimed |
| LLM stream cooperative cancel | RT-4 text-stream interrupt request | Accepted, separate from TTS |
| speech-triggered barge-in | Real voice activity causes interruption | Absent |
| barge-in policy decision | Provider-neutral decision contract | Public mock-safe contract only |

Required summary:

```text
local playback stop exists: true
DRC app-owned TTS queue exists: false
DRC Backend synthesis cancel exists: false
DRC output flush endpoint exists: false
FW public output-control data contract exists: true
FW real TTS queue runtime exists: false
FW real queue flush supported: false
provider hard cancel supported: false
automatic stream-to-TTS exists: false
real speech-triggered barge-in exists: false
```

## 11. Readiness classification

```text
RT-5 readiness:
PARTIAL_READY_FOR_DRC_APP_OWNED_QUEUE_AND_LOCAL_PLAYBACK_FLUSH
```

Ready without Framework modification:

- app-owned bounded utterance queue;
- serial one-shot synthesis requests through the existing public DRC/FW boundary;
- late-result rejection using app-owned operation/generation IDs;
- pending app-queue clear;
- Flutter local playback stop;
- explicit manual flush UI;
- deterministic fake-only lifecycle tests.

Not ready or not claimable:

- provider synthesis hard cancel;
- Framework-backed active TTS queue cancellation;
- Framework real output flush;
- full unified realtime session orchestration;
- speech-triggered real barge-in;
- real-STT-to-TTS handoff.

## 12. Exact RT-5 split

```text
RT-5a  COMPLETED / ACCEPTED / PUSHED
        Current DRC/FW TTS output-control inventory, readiness classification,
        terminology separation, and exact small-commit split.
        Docs/test-only. No runtime, provider, network, audio, or existing-test change.

RT-5b  NOT_STARTED / NOT_AUTHORIZED
        App-owned bounded TTS utterance queue and local playback-flush lifecycle
        contract with fake-only tests.
        No HomeScreen integration, real HTTP, FW/provider execution, or audio playback.

RT-5c  NOT_STARTED
        Injectable orchestration boundary between accepted realtime text terminal,
        existing Backend voice-output request, and local audio player.
        Fake Backend client and fake audio engine only. No HomeScreen integration.

RT-5d  NOT_STARTED
        HomeScreen presentation and explicit opt-in enqueue/play/flush controls.
        Automatic TTS remains default-off. Fake/in-memory dependencies only.

RT-5e  NOT_STARTED
        Configured local Backend/FW one-shot synthesis, sequential playback,
        pending app-queue clear, and local playback-stop operator acceptance.
        Provider hard cancel and FW real queue flush are not claimed.

RT-5f  NOT_STARTED / BLOCKED_READINESS
        Speech-triggered real barge-in and real-STT-to-TTS acceptance only after
        a separately reviewed app-visible real input source and sufficient public
        FW execution capability exist.
```

Parent state:

```text
RT-5 CURRENT / NOT_COMPLETED
```

RT-5a acceptance does not automatically authorize RT-5b. RT-5b remains NOT_STARTED / NOT_AUTHORIZED until a separate exact fake-only contract review authorizes it.

## 13. Exact seven-file change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5_tts_output_control_current_behavior_inventory.md
scripts/check_v300_rt5_tts_output_control_current_behavior_inventory.py
```

## 14. Explicit non-change surface

RT-5a changes none of:

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
backend/.env.example
dependencies
platform permissions
version metadata
release records
release builders
existing check scripts
AI Character Framework repository
```

## 15. Credential-free verification

The dedicated gate:

- reads source and public type metadata only;
- performs no network request;
- creates no voice-output session;
- calls no synthesis method;
- creates no provider client;
- reads no credential value;
- generates and plays no audio;
- uses no microphone;
- modifies no runtime or existing test.

The mock-safe Framework realtime session probe may inspect empty queue,
typed flush, typed interrupt, and barge-in decision behavior because those
operations execute no provider, network, audio, or microphone path.

## 16. Privacy boundary

Never add or record:

```text
credential values
private env values
provider payloads
provider/model acceptance evidence
actual synthesis text
generated audio or bytes
artifact private paths
private repository paths
LAN IPs
private session/turn IDs
screenshots
operator evidence
raw logs
raw HTTP bodies
```

## 17. Stop rule

Stop after the exact seven-file candidate and verification.

Do not start RT-5b. Do not add a queue, automatic TTS, runtime orchestration,
HomeScreen behavior, real TTS, network execution, provider execution, audio
playback, microphone use, or barge-in execution.

## 18. Acceptance checklist

```text
[x] exact seven-file candidate
[x] compileall passed
[x] dedicated RT-5a candidate gate passed
[x] Backend full tests passed: 192 passed, 1 existing warning
[x] Flutter analyze passed
[x] Flutter full tests passed: 278 passed
[x] git diff --check passed
[x] changed-content private scan passed
[x] diff review passed
[x] explicit operator approval received
[x] commit approved
[x] push approved
```

Acceptance result:

```text
RT-5a: COMPLETED / ACCEPTED / PUSHED
RT-5a implementation commit: 1cf77774dca75b9875099c2b6c6c03992456d80f
RT-5: CURRENT / NOT_COMPLETED
RT-5b: NOT_STARTED / NOT_AUTHORIZED
Backend runtime changed: false
Flutter runtime changed: false
existing tests changed: false
real TTS executed: false
audio playback executed: false
automatic stream-to-TTS added: false
provider-level hard cancel claimed: false
```

RT-5b requires a separate exact fake-only contract review and authorization.

## 19. Historical/current marker policy

Historical RT-0 through RT-4 records retain the status true at their own
checkpoint. Current top-level status may advance to RT-5a without rewriting
historical authorization, not-started, implementation-candidate, or acceptance
markers.

The RT-4f4 implementation commit and later RT-4f4 acceptance-docs commit remain
distinct. Private operator evidence remains uncommitted and unpushed.
