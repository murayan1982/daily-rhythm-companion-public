# DRC-V4-4 Provider-free FW v6 Flutter Session Client

Status: DRC-V4-4 COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED

Baseline: `d194c213fdecc84ec06d8b63f0cb94f8689c5ed7`

Implementation commit:
`a05d62447e85be28d674201853d0667aef11e2ae`

## Acceptance Evidence

```text
exact surface: 13 files
R1 PASS
R2 PASS
R3 PASS
focused Backend: 62 PASS
full Backend: 479 PASS
Flutter analyze: PASS
focused Flutter: 40 PASS
full Flutter: 540 PASS
git diff --check: PASS
protected-file review: PASS
privacy/security review: PASS
post-push working tree: clean
```

Corrective history:

```text
R1: open re-entry race corrected
R1: close-during-opening cleanup corrected
R1: 64 KiB response bound enforced before chunk append
R2: normal concurrent close made single-flight
R3: synchronous ChangeNotifier close reentrancy corrected
R3: _closeInFlight established before close lifecycle starts
R3: reentrant closing-listener test PASS
```

## Final Acceptance-sync Provenance

```text
DRC-V4-4 implementation: COMPLETED / VERIFIED / ACCEPTED / COMMITTED / PUSHED / CLOSED
implementation commit: a05d62447e85be28d674201853d0667aef11e2ae
DRC-V4-4 final acceptance sync: IMPLEMENTED / AWAITING_REVIEW
final acceptance-sync baseline: a05d62447e85be28d674201853d0667aef11e2ae
acceptance-sync commit: none
acceptance-sync commit / push: NOT_AUTHORIZED
```

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
