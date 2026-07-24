# v2.1.0 T-1b Flutter TTS player abstraction and state contract

Updated: 2026-07-24
Status: IMPLEMENTED / NOT_ACCEPTED
Current small commit: T-1b
Parent phase: T-1 CURRENT / NOT_COMPLETED

## Purpose

```text
- Add one app-owned, testable audio-player boundary before HomeScreen integration.
- Represent loading, playing, stopped, completed, failed, and expired states explicitly.
- Keep platform audio code behind an engine interface so normal tests use no browser,
  decoder, network, audio device, Framework checkout, or TTS provider.
- Keep raw audio URLs out of user-facing state and error text.
- Leave concrete player plugin wiring and HomeScreen controls to T-1c.
```

## Added Flutter boundary

```text
app/lib/services/voice_output_audio_player.dart
```

The file adds:

```text
VoiceOutputPlaybackPhase
VoiceOutputAudioEngineEventType
VoiceOutputAudioEngineEvent
VoiceOutputAudioEngineException
VoiceOutputAudioEngine
VoiceOutputPlaybackState
VoiceOutputAudioPlayerController
```

`VoiceOutputAudioEngine` owns only the minimum operations needed by DRC:

```text
load(Uri source)
play()
stop()
seekToStart()
dispose()
events
```

No plugin-specific class or provider-specific object is exposed to widgets.

## State contract

```text
idle       no retained source
loading    source accepted and engine load/play operation is pending
playing    playback started
stopped    playback stopped; replay remains available
completed  end-of-stream reached; replay remains available
failed     playback/load failed; source may remain retryable
expired    opaque artifact is unavailable/expired; source is cleared
```

Control rules:

```text
canStop   = loading or playing
canReplay = retained source plus stopped/completed/failed
expired   = no retained source and no replay
```

Only `http` and `https` sources are accepted. Local file, asset, data, and other URI schemes are rejected before reaching the engine. This keeps the controller aligned with the DRC-owned Backend URL handoff and avoids accepting private local paths.

## Error and privacy contract

The controller stores a short provider-neutral `technicalCode` and fixed user-facing copy. It does not copy the source URI, Framework artifact path, provider payload, exception text, or original filename into the user message.

Error mapping:

```text
VoiceOutputAudioEngineException(expired=true) -> expired
generic/engine failure                         -> failed
unsupported URI                               -> failed / unsupported_audio_uri
explicit markExpired                          -> expired / audio_artifact_expired
```

## Concurrency and disposal contract

Each operation receives an internal sequence number. A reset, stop replacement, expiry, or disposal invalidates older asynchronous load/play completions so stale operations cannot overwrite the latest state.

`dispose()` cancels the engine event subscription and disposes the injected engine. T-1c must own the controller lifetime from the integrating widget/state object.

## Mock-safe tests

```text
app/test/voice_output_audio_player_test.dart
```

The focused tests use a fake engine and cover:

```text
initial idle state
loading -> playing
stop -> replayable stopped
completion -> replay-ready
replay seek/play
expired load failure
ordinary retryable failure
unsupported URI rejection
pending-load invalidation after reset
engine disposal
```

The tests do not download or decode audio and do not require an audio plugin.

## T-1b change surface

```text
app/lib/services/voice_output_audio_player.dart
app/test/voice_output_audio_player_test.dart
docs/v210_tts_player_controller.md
docs/v210_tts_player_current_behavior_inventory.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_tts_player_controller.py
scripts/check_v210_tts_player_current_behavior_inventory.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

## Explicit non-change surface

```text
backend/app/**
backend/tests/**
app/lib/screens/home_screen.dart
app/lib/models/voice_output_demo.dart
app/lib/services/backend_api_client.dart
app/test/widget_test.dart
app/pubspec.yaml
app/pubspec.lock
AI Character Framework and real TTS runtime
private audio artifacts and operator evidence
V-1 / R-1 runtime
v2.0.0 / v2.0.1 release records, ZIPs, tags, and GitHub Releases
```

## T-1c handoff

T-1c owns:

```text
- concrete Flutter audio engine/plugin wiring;
- HomeScreen play, stop, and replay controls;
- mapping Backend audio HTTP unavailability to markExpired();
- regenerate/retry guidance after expiry;
- safe stop/dispose when output changes or HomeScreen is disposed;
- focused widget tests and aggregate T-1 acceptance;
- separately reviewed audible PC/smartphone Web evidence when required.
```

T-1b does not complete parent T-1 and does not provide audible playback acceptance.
