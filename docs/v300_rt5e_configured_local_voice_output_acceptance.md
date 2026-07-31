# RT-5e configured local Backend/FW voice output acceptance

Status: **IMPLEMENTED / AWAITING_REVIEW**

RT-5e adds a default-off Flutter runtime assembly that connects one explicitly
processed app-owned queue item to the existing DRC Backend voice-output route,
the released Framework v5.4.0 root-public voice-output boundary, and a
binding-owned local playback controller.

This implementation does not execute the private operator run and does not
claim real provider or local playback acceptance yet.

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

## Private operator isolation

Private Framework/provider settings remain in the existing ignored local
operator environment. Credential values, provider payloads, raw audio,
utterance/transcript text, audio URLs, artifact IDs, private paths, LAN
addresses, screenshots, raw exceptions, and operator evidence must not be
committed.

Generated audio remains under the existing ignored Backend local-data
lifecycle. The operator run must begin and end with clean DRC and Framework
working trees. Public acceptance notes may record only booleans, fixed typed
outcomes, fixed technical codes, test counts, and commit hashes.

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

## Verification before commit authorization

```powershell
$ErrorActionPreference = "Stop"

python -m compileall -q backend scripts
if ($LASTEXITCODE -ne 0) { throw "compileall failed: $LASTEXITCODE" }

python scripts\check_v300_rt5e_configured_local_voice_output_acceptance.py
if ($LASTEXITCODE -ne 0) { throw "RT-5e gate failed: $LASTEXITCODE" }

python scripts\smoke_v200_fw_voice_output_boundary_for_drc.py
if ($LASTEXITCODE -ne 0) { throw "FW voice-output smoke failed: $LASTEXITCODE" }

python -m pytest -q backend\tests --basetemp .pytest-tmp -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed: $LASTEXITCODE" }

Push-Location app
try {
    flutter analyze
    if ($LASTEXITCODE -ne 0) { throw "Flutter analyze failed: $LASTEXITCODE" }

    flutter test `
        test\configured_realtime_terminal_voice_output_runtime_test.dart `
        test\main_realtime_terminal_voice_output_wiring_widget_test.dart `
        test\realtime_terminal_voice_output_home_screen_widget_test.dart `
        test\realtime_terminal_voice_output_orchestrator_test.dart `
        test\voice_output_queue_test.dart `
        test\voice_output_audio_player_test.dart `
        test\audioplayers_voice_output_audio_engine_test.dart
    if ($LASTEXITCODE -ne 0) { throw "Focused Flutter tests failed: $LASTEXITCODE" }

    flutter test
    if ($LASTEXITCODE -ne 0) { throw "Flutter tests failed: $LASTEXITCODE" }
}
finally {
    Pop-Location
}

git -c core.whitespace=cr-at-eol diff --check
if ($LASTEXITCODE -ne 0) { throw "git diff --check failed: $LASTEXITCODE" }

git status --short
if ($LASTEXITCODE -ne 0) { throw "git status failed: $LASTEXITCODE" }
```

Stop before commit and push. Private operator execution starts only after the
implementation candidate is separately reviewed, explicitly approved,
committed, and pushed. RT-5e acceptance does not authorize RT-5f.
