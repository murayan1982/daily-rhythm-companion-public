# DRC v3.0.0 RT-4f4 configured local stream acceptance

Updated: 2026-07-30

## Status

```text
RT-4: COMPLETED / ACCEPTED
RT-4f: COMPLETED / ACCEPTED
RT-4f3: COMPLETED / ACCEPTED / PUSHED
RT-4f4: COMPLETED / ACCEPTED / PUSHED
Current implementation commit: none
```

RT-4f4 implementation:
`9b19e379634a718df2ab3ed5eb49bb20bfe7e240`

RT-4f3 implementation:
`d651a00be8713a70be3a46524f33c787299bbe9c`

RT-4f3 acceptance docs:
`ad28994`

## Purpose

RT-4f4 makes the accepted RT-4e Flutter realtime text stream client/controller
constructible from the normal Flutter startup path, behind a default-off
compile-time flag. This source implementation prepares configured local
Backend/FW text streaming and cooperative cancel.

The implementation is committed and pushed at
`9b19e379634a718df2ab3ed5eb49bb20bfe7e240`. The later configured operator
acceptance is completed and accepted. Operator evidence itself is not
committed or pushed. The RT-4f4 milestone is COMPLETED / ACCEPTED / PUSHED.

## Configured Flutter Runtime Contract

`ConfiguredRealtimeTextStreamRuntime` builds an optional
`RealtimeTextStreamController Function()` from:

```text
package:http/http.dart
BackendApiClient.defaultBaseUrl or an injected base URL
RealtimeTextStreamClient
RealtimeTextStreamController
```

The Backend base URL continues to come from the existing
`DRC_BACKEND_API_BASE_URL` / `BackendApiClient.baseUrl` path; RT-4f4 adds no
second Backend URL configuration system.

The runtime owns no DRC provider client and imports no Framework module. It
stores no credential, provider name, model name, FW path, session ID, turn ID,
transcript, manual input, or generated output.

The runtime accepts only absolute `http` or `https` base URLs with a nonempty
host, no user info, and no fragment. Invalid URLs return `null` from
`buildControllerFactory()` safely without throwing or exposing the raw URL in
public state.

The HTTP client is constructed lazily only when the returned controller factory
is invoked. Each factory invocation creates an independent `http.Client`,
`RealtimeTextStreamClient`, and `RealtimeTextStreamController`. Controller
dispose closes the underlying HTTP client through the accepted RT-4e ownership
path. Runtime construction and factory lookup do not start network requests.

## Main Wiring Contract

`main.dart` constructs one `BackendApiClient`, reads
`DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM`, passes the existing
`BackendApiClient.baseUrl` into `ConfiguredRealtimeTextStreamRuntime`, and
passes the optional realtime controller factory into `DailyRhythmCompanionApp`.

`DailyRhythmCompanionApp` accepts injectable `BackendApiClient` and optional
`RealtimeTextStreamController Function()?` values, then passes both to
HomeScreen. HomeScreen itself is unchanged and keeps its accepted RT-4f2
controller ownership, listener, and dispose order.

## Default-Off Contract

Flutter configured realtime text streaming is default-off:

```text
DRC_RT4_ENABLE_CONFIGURED_TEXT_STREAM=false
```

The existing Backend-side FW streaming remains independently default-off via:

```text
DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM
```

When disabled, the runtime returns no controller factory and does not invoke an
HTTP client factory. Normal app startup remains realtime-stream-unconfigured.

## Mock-Safe Test Boundary

Focused tests use fake/in-memory clients only. They execute no socket,
localhost, real Backend, Framework, provider, STT, microphone, or network
acceptance. Widget tests inject a fake `BackendApiClient` so HomeScreen initial
loading does not contact a real Backend.

## Configured Local Operator Acceptance Boundary

Configured real local Backend/FW streaming and cooperative cancel visible UI
acceptance passed. The accepted operator execution used bounded manual input
only and recorded public-safe markers only.

Manual bounded input is the only configured local stream input accepted by
RT-4f4. No separately reviewed safe app-visible real transcript source is
configured.

## Operator Acceptance Record

```text
configured Flutter stream runtime: true
configured local Backend/FW execution: passed
Framework root-public ask_stream path exercised: true
input source: bounded manual input only
real transcript source configured: false
real STT execution: false
real-STT-to-stream executed: false
provider-specific execution acceptance: not claimed
provider identity/model/payload recorded: false
SSE events request observed: true
stream_started event count: 1
stream_chunk event count: 23
stream_completed event count: 1
chunks arrived at multiple distinct times: true
real incremental streaming: accepted
incremental UI output before terminal: confirmed
completed terminal: confirmed
duplicate start blocked while active: confirmed
cancel button enabled only while active: confirmed
cooperative cancel POST: HTTP 200
cancel_requested UI phase: confirmed
cancelled terminal: confirmed
partial output retained at cancellation: confirmed
output stopped after cancelled: confirmed
start button re-enabled after cancelled: confirmed
cancel button disabled after cancelled: confirmed
cancel mode: cooperative
hard cancel supported: false
automatic TTS start: false
provider-neutral transcript handoff: unconfigured
private evidence committed: false
operator evidence committed: false
operator evidence pushed: false
Backend Framework-stream flag restored off: true
DRC working tree after execution: clean
DRC HEAD after execution: 9b19e379634a718df2ab3ed5eb49bb20bfe7e240
FW working tree after execution: clean
FW HEAD after execution: d313eb6acb643103fe25988720ebee5976a04f78
```

## Real Transcript Boundary

RT-4f4 does not configure a real transcript source. Private real-STT operator
output still does not reach Flutter. Real-STT-to-stream acceptance is false.

## Cooperative Cancel Boundary

RT-4f4 keeps cooperative cancel only. `hard_cancel_supported` remains false.
Provider-level immediate cancellation is not claimed.

## Protected Boundaries

Protected unchanged surfaces include HomeScreen, accepted RT-4e client and
controller, accepted RT-4f3 transcript handoff and provider-neutral transcript
model, Backend runtime/tests, Framework repository, dependencies, versions,
platform permissions, release artifacts, and historical RT-4e/RT-4f2/RT-4f3
dedicated gates.

## Non-Actions

```text
RT-4f4 ACCEPTED: true
RT-4f4 PUSHED: true
configured real Backend/FW execution passed: true
real incremental streaming accepted: true
cooperative cancel accepted: true
real-STT-to-stream accepted: false
provider-level hard cancel supported: false
RT-4 completed: true
RT-4f completed: true
real Backend/FW execution: true
real STT execution: false
Framework root-public ask_stream path exercised: true
provider-specific execution acceptance: not claimed
provider-specific implementation details accepted: false
provider identity/model/payload recorded: false
provider-specific payload recorded: false
VoiceInputDemo transcript wired: false
transcript persistence: false
generated output persistence: false
WebSocket added: false
reconnect/resume added: false
TTS automatic start: false
RT-5 TTS queue/flush/barge-in started: false
```

Private paths, LAN IPs, actual input/output, provider payloads, screenshots,
operator evidence, credentials, raw audio, raw HTTP bodies, session IDs, and
turn IDs are not committed.

## Candidate Verification Record

Implementation verification passed with compileall, the dedicated RT-4f4
source-tree gate, Backend full tests, Flutter analyze, focused RT-4f4 runtime
unit tests, focused main wiring widget tests, Flutter full tests, exact
thirteen-file surface review, and `git diff --check`. Later operator
acceptance passed with the public-safe markers above.

## RT-4 Parent Acceptance Result

```text
real incremental LLM streaming: accepted
DRC normalized stream event consumption: accepted
configured local Backend/FW stream completion: accepted
cooperative cancel: accepted
bounded Backend transport lifecycle: accepted from RT-4c
disconnect cleanup: accepted from RT-4c
Flutter incremental response consumption: accepted
provider-level hard cancel: not claimed
hard_cancel_supported: false
real-STT-to-stream: not accepted and not executed
automatic TTS: not started
TTS queue/flush/barge-in: RT-5 only, not started
RT-5 status: NOT_STARTED / NOT_AUTHORIZED
```

## Historical Gate Marker

The dedicated implementation gate
`scripts/check_v300_rt4f4_configured_local_stream_acceptance.py` is unchanged.
Its historical implementation-candidate output remains:

```text
v300_rt4f4_configured_local_stream_acceptance_status: implemented-awaiting-acceptance
```

That marker describes the uncommitted thirteen-file implementation candidate.
It does not conflict with this later acceptance documentation sync.

## Exact Change Surface

```text
app/lib/main.dart
app/lib/services/configured_realtime_text_stream_runtime.dart
app/test/configured_realtime_text_stream_runtime_test.dart
app/test/main_realtime_text_stream_wiring_widget_test.dart
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt4f_ui_streaming_acceptance_inventory.md
docs/v300_rt4f3_transcript_stream_handoff.md
docs/v300_rt4f4_configured_local_stream_acceptance.md
scripts/check_v300_rt4f4_configured_local_stream_acceptance.py
```
