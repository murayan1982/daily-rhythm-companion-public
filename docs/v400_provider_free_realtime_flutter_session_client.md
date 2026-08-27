# DRC-V4-4 Provider-free FW v6 Flutter Session Client

Status: DRC-V4-4 IMPLEMENTED / AWAITING_REVIEW

Baseline: `d194c213fdecc84ec06d8b63f0cb94f8689c5ed7`

## Scope

DRC-V4-4 adds a provider-free Flutter model, injectable HTTP client, and
ChangeNotifier controller for the accepted DRC-V4-3 Backend API:

```text
POST   /realtime/framework-v6/provider-free/sessions
POST   /realtime/framework-v6/provider-free/sessions/{session_id}/turns
POST   /realtime/framework-v6/provider-free/sessions/{session_id}/interrupt
GET    /realtime/framework-v6/provider-free/sessions/{session_id}/diagnostics
DELETE /realtime/framework-v6/provider-free/sessions/{session_id}
```

Flutter imports no Framework package directly. It knows only the DRC-owned HTTP
contract and uses the canonical FW session id returned by the Backend.

## Network Boundary

```text
Backend HTTP capability: YES / explicit method invocation only
automatic network on construction/startup: NO
verification network: NO / fake injected HTTP client only
external provider execution: NO
provider network: NO
microphone: NO
real STT: NO
real LLM: NO
real TTS: NO
playback: NO
VTube Studio: NO
```

## Runtime Boundary

```text
provider-free Flutter client/controller only
HomeScreen wiring: NOT_IMPLEMENTED
main.dart wiring: NOT_IMPLEMENTED
configured runtime wiring: NOT_IMPLEMENTED
SSE: NOT_IMPLEMENTED
WebSocket: NOT_IMPLEMENTED
streaming output UI: NOT_IMPLEMENTED
direct Framework import: NOT_IMPLEMENTED
provider SDK import: NOT_IMPLEMENTED
real unified runtime: NOT_CLAIMED
commit / push: NOT_AUTHORIZED
```

FW v6.0.0 does not provide a production real unified
`RealtimeSession.run_turn()` pipeline coordinating real STT -> streaming LLM ->
TTS -> motion. DRC-V4-4 does not claim or enable that real unified pipeline.

## Flutter Contract

The model enforces accepted schema versions, canonical `fw_session_*`,
`fw_turn_*`, and `fw_generation_*` identifiers, provider-free open invariants,
and bounded problem projection.

Turn requests are validated locally before HTTP:

```text
non-empty
non-blank
max 4096 Unicode code points
body fields: input_text only
```

Interrupt requests are validated locally before HTTP:

```text
allowed scopes: current_turn, llm_stream, tts_queue, voice_output, motion, all
allowed reasons: user_barge_in, user_cancel, new_turn_started, session_closed, timeout, host_app_request, provider_failure
default scope: current_turn
default reason: host_app_request
body fields: scope, reason only
```

The client bounds decoded response bodies to 64 KiB and converts malformed or
unexpected responses to safe local problems without exposing raw HTTP bodies.

The controller starts idle, opens only on explicit `open()`, rejects a second
simultaneous turn with a host-side `turn_already_active` problem, permits
interrupt while a turn is in flight, tracks diagnostics independently, and keeps
late turn/interrupt/diagnostics completions from resurrecting state after close.

## Privacy Boundary

Flutter may retain only bounded accepted metadata:

```text
phase
session ID
latest accepted turn result
latest accepted interrupt result
latest diagnostics snapshot
bounded problem
interruptInFlight
diagnosticsInFlight
```

Flutter does not retain raw decoded JSON after parsing, raw HTTP bodies, request
JSON, input text in public state/problem text, event payload maps, provider
payloads, transcripts, raw audio, credentials, private paths, or operator
evidence.
