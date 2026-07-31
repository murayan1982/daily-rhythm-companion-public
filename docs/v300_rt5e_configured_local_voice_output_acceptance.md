# RT-5e configured local Backend/FW voice output acceptance

Updated: 2026-07-31

## Status

```text
RT-5: CURRENT / NOT_COMPLETED
RT-5d: COMPLETED / ACCEPTED / PUSHED
RT-5e: COMPLETED / ACCEPTED / PUSHED
RT-5f: NOT_STARTED / BLOCKED_READINESS / NOT_AUTHORIZED
implementation commit: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
DRC HEAD / origin/main after acceptance: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
FW v5.4.0 HEAD after acceptance: d313eb6acb643103fe25988720ebee5976a04f78
```

RT-5e adds a default-off Flutter runtime assembly that connects one explicitly
processed app-owned queue item to the existing DRC Backend voice-output route,
the released Framework v5.4.0 root-public voice-output boundary, and a
binding-owned local playback controller.

The implementation is committed and pushed at `ef5f96337b5f601277a9bcc38b9e6fedc520b0a6`. The later private
configured operator run passed real root-public synthesis, natural audible
local playback, explicit playback-stop during active playback, private cleanup,
and final clean-tree verification. Operator evidence itself is not committed
or pushed.

## Exact runtime path

```text
completed realtime terminal
→ explicit opt-in
→ explicit enqueue button
→ explicit process button
→ processNext() at most once
→ BackendApiClient.submitVoiceOutputDemoRequest()
→ POST /demo/voice-output
→ framework.create_voice_output_session().create_output
→ generated root-relative DRC audio URL
→ RT-5e binding-owned local player
→ terminal playback result
```

Building the runtime, building its factory, completing a realtime stream,
enabling opt-in, or enqueueing an item does not start HTTP, synthesis,
playback, queue draining, or flushing.

## Default-off configuration

Normal `main.dart` uses the compile-time switch below:

```text
DRC_RT5_ENABLE_CONFIGURED_VOICE_OUTPUT=false
```

The default is false. A disabled runtime or invalid Backend base URL returns no
HomeScreen binding factory and leaves the UI `unconfigured`.

## Exact Backend request

The configured synthesis adapter sends only the existing provider-neutral DRC
request fields:

```text
client_event_id: rt5e-realtime-terminal-voice-output
output_mode: tts
text_content: queued utterance
audio_format: mp3
utterance_purpose: realtime_terminal
character_id: null
voice_profile_id: null
```

Session IDs, turn IDs, queue item IDs, provider IDs, provider settings, and
credentials are not sent by the RT-5e adapter.

## Exact generated-result acceptance

Local playback is permitted only when all conditions are true:

```text
accepted == true
request_state == generated
framework_call_state == generated
framework_api_name == framework.create_voice_output_session().create_output
audio_ready == true
has_audio_handoff == true
audio_handoff_kind == url
is_generated == true
audio_artifact_ref == null
audio_format == mp3
```

The audio URL must also exactly match:

```text
/demo/voice-output/audio/<32 lowercase hexadecimal characters>
```

Absolute provider URLs, file URIs, query strings, fragments, user-info,
artifact refs, and non-opaque paths are rejected before local playback. The
accepted root-relative URL is resolved against the configured Backend origin.

## Player ownership and flush

RT-5e creates a dedicated `VoiceOutputAudioPlayerController` and dedicated
`AudioplayersVoiceOutputAudioEngine` inside the binding factory. It does not
reuse or control the existing Voice Output Demo player owned directly by
HomeScreen.

An explicit flush:

```text
- invalidates active app-owned work;
- clears pending app-owned queue items;
- requests stop on the RT-5e binding-owned local player;
- rejects stale synthesis/playback completion through the existing generation
  and operation-epoch protections.
```

Flush does not cancel an in-flight Backend request, delete generated artifacts,
call a Framework real-output flush, or cancel provider synthesis.

## Operator acceptance record

Private configured operator acceptance passed on 2026-07-31.

Preflight and runtime readiness:

```text
DRC implementation HEAD verified: true
DRC origin/main matched implementation: true
FW v5.4.0 HEAD verified: true
DRC/FW working trees clean before execution: true
private env files ignored: true
DRC RT-4 configured stream gate ready: true
DRC voice-output gate ready: true
FW provider configuration isolated in FW private env: true
FW root-public voice-output session ready: true
FW root-public text session ready: true
Backend health ready: true
Backend voice-output engine: framework
Backend voice-output adapter: framework
Backend real-TTS gate enabled for operator process: true
Backend voice-output capability: available
Flutter RT-4 configured runtime enabled: true
Flutter RT-5 configured runtime enabled: true
configured UI visible: true
session opt-in default: off
TTS provider call before explicit process action: false
```

Natural playback acceptance:

```text
completed realtime terminal: confirmed
explicit opt-in: on
explicit enqueue: accepted
pending before process: 1
explicit process action count: 1
real FW root-public synthesis: accepted
audible playback started: confirmed
audible playback completed naturally: confirmed
last process after natural completion: completed
final pending after natural completion: 0
final active after natural completion: no
```

Playback-stop acceptance:

```text
second completed realtime terminal: confirmed
second explicit enqueue: accepted
pending before second process: 1
playback phase before flush: playing
active before flush: yes
last process before flush: processing
explicit flush action count: 1
audible playback stopped by flush: confirmed
last flush: completed
cleared pending: 0
local playback stop requested: true
local playback stop succeeded: true
final phase: idle
final pending: 0
final active: no
technical error code: none
```

Cleanup and privacy:

```text
Flutter operator runtime stopped: true
Backend operator runtime stopped: true
FW real-TTS gate restored disabled: true
FW provider-execution guard restored disabled: true
operator artifact files removed: 3
operator artifacts remaining: false
private operator logs removed: true
temporary private backups removed or restored: true
DRC corrected private Framework root retained: true
DRC working tree after cleanup: clean
DRC HEAD after cleanup: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
FW working tree after cleanup: clean
FW HEAD after cleanup: d313eb6acb643103fe25988720ebee5976a04f78
credential values recorded: false
input or generated text committed: false
provider payload committed: false
audio URL or artifact ID committed: false
raw audio committed: false
private path or LAN address committed: false
screenshot or raw operator log committed: false
operator evidence committed or pushed: false
```

## Explicit non-claims

RT-5e does not claim or add:

```text
- automatic terminal-to-TTS;
- automatic queue drain;
- Backend HTTP request cancellation;
- provider synthesis hard cancellation;
- Framework real queue flush;
- speech-triggered barge-in;
- real-STT-to-stream-to-TTS;
- a DRC provider-specific client;
- a Framework internal-module import;
- changes to the existing Voice Output Demo player.
```

Real provider synthesis was accepted only through the released FW root-public
boundary. Provider-specific implementation details, identity, model, payload,
or hard-cancel behavior are not accepted or recorded by this milestone.

## Private operator isolation

Private Framework/provider settings remain in ignored local operator
environments. Credential values, provider payloads, raw audio,
utterance/transcript text, audio URLs, artifact IDs, private paths, LAN
addresses, screenshots, raw exceptions, and operator evidence are not
committed.

Generated audio used the ignored Backend local-data lifecycle. The accepted
operator run began and ended with clean DRC and Framework working trees. Public
acceptance records contain only booleans, fixed typed outcomes, test counts,
cleanup counts, and commit hashes.

## Exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt5e_configured_local_voice_output_acceptance.md
scripts/check_v300_rt5e_configured_local_voice_output_acceptance.py
app/lib/main.dart
app/lib/screens/home_screen.dart
app/lib/services/configured_realtime_terminal_voice_output_runtime.dart
app/test/configured_realtime_terminal_voice_output_runtime_test.dart
app/test/main_realtime_terminal_voice_output_wiring_widget_test.dart
app/test/realtime_terminal_voice_output_home_screen_widget_test.dart
```

## Explicit non-change surface

```text
backend/**
Framework repository
app/lib/services/backend_api_client.dart
app/lib/models/voice_output_demo.dart
app/lib/services/realtime_terminal_voice_output_home_screen_binding.dart
app/lib/services/realtime_terminal_voice_output_orchestrator.dart
app/lib/services/voice_output_queue.dart
app/lib/services/voice_output_audio_player.dart
app/lib/services/audioplayers_voice_output_audio_engine.dart
app/lib/services/configured_realtime_text_stream_runtime.dart
app/pubspec.yaml
app/pubspec.lock
platform wrappers
dependency versions
release metadata
```

## Implementation verification record

```text
compileall: passed
RT-5e dedicated candidate gate: passed
FW root-public voice-output boundary smoke: passed
Backend full tests: 192 passed / 1 existing warning
Flutter analyze: passed
focused Flutter tests: 82 passed
Flutter full tests: 343 passed
exact implementation surface: 13 files
HomeScreen semantic diff: +6 / -6
git diff --check: passed
implementation commit: ef5f96337b5f601277a9bcc38b9e6fedc520b0a6
implementation push: completed
```

The dedicated source gate is bound to baseline
`ead613d27cd32c625b1b0a07eef96387027d70d5` and the exact thirteen-file
pre-commit candidate. It remains a historical credential-free,
provider-free, network-free, and platform-audio-free gate and is not rerun for
this later six-document acceptance sync.

## Result and stop rule

```text
RT-5e completed: true
RT-5e accepted: true
RT-5e implementation pushed: true
configured real FW synthesis accepted: true
natural audible playback accepted: true
explicit binding-owned playback-stop accepted: true
operator cleanup accepted: true
private evidence committed or pushed: false
RT-5 parent completed: false
RT-5f started: false
RT-5f authorized: false
```

RT-5 remains `CURRENT / NOT_COMPLETED`. RT-5e acceptance does not authorize
RT-5f. No RT-5f implementation begins through this six-document acceptance
sync.
