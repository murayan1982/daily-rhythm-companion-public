# v2.1.0 TTS player current behavior inventory

Updated: 2026-07-24
Status: T-1a CURRENT / NOT_COMPLETED
Purpose: record the accepted audio handoff, retention, Flutter playback, and test behavior before T-1 runtime changes

## Interpretation rule

```text
Generated audio metadata != in-app playback
Opaque audio URL != raw Framework path exposure
HTTP 404 != a dedicated expired-artifact state
External browser/application launch != Flutter player lifecycle
Mock-safe widget visibility != audible playback acceptance
```

This inventory is source-tree only. It does not read `backend/local_data`, call AI Character Framework or a TTS provider, generate/download/play audio, launch a browser, inspect private evidence, or modify released v2.0.0/v2.0.1 records.

## Accepted Backend artifact boundary

The accepted v2.0.x M-5 behavior remains:

```text
VOICE_OUTPUT_ARTIFACT_TTL_SECONDS=86400
VOICE_OUTPUT_ARTIFACT_MAX_COUNT=100
managed staging and public directories
lazy TTL and capacity cleanup
resolving an artifact does not refresh lifetime
MP3-only public handoff
```

`VoiceOutputArtifactStore` moves a validated Framework staging MP3 into a separate DRC-owned public directory. The public handoff contains a random 32-character hexadecimal artifact ID and the relative opaque URL:

```text
/demo/voice-output/audio/{artifact_id}
```

The public metadata does not expose the staging path, Framework path, provider payload, or original filename. Symlinks, traversal-like IDs, outside paths, unsupported formats, and expired staging files are rejected.

## Audio route behavior

The current route is:

```text
GET /demo/voice-output/audio/{artifact_id}
```

Successful responses use:

```text
Content-Type: audio/mpeg
Cache-Control: no-store
X-Content-Type-Options: nosniff
```

Current limitation:

```text
expired, capacity-removed, malformed, and unknown artifact IDs all return HTTP 404
detail: Voice output audio artifact was not found.
```

The route does not return a structured app-facing playback problem or a dedicated expired state.

## Flutter response and API boundary

`VoiceOutputDemoRequestResponse` already parses:

```text
audio_url
audio_artifact_ref
audio_format
audio_ready
audio_handoff_kind
has_audio_handoff
is_generated
audio_playback_status
evidence_status
```

`BackendApiClient` can submit `POST /demo/voice-output`, but it has no audio GET/HEAD/download helper and no typed audio HTTP exception.

The accepted response model hides the raw URL/ref in normal diagnostic copy and reports presence only.

## Current Flutter playback behavior

`HomeScreen` treats a response as a playback candidate only when it is generated, audio-ready, has a handoff, and uses a supported handoff kind. For URL handoffs it resolves a relative URL against the configured Backend base URL.

Current playback action:

```text
launchUrl(uri, mode: LaunchMode.externalApplication)
button: 音声を開いて再生確認する
```

This opens the URL outside the Flutter app. The current app has no owned player/controller and no deterministic player lifecycle.

Missing user-facing states:

```text
loading
playing
stopped
completed
replay-ready
failed
expired
```

The only current playback error is a generic `音声URLを開けませんでした。` string.

## Flutter dependency and test baseline

`app/pubspec.yaml` currently includes `url_launcher` and no dedicated audio-player package.

Current widget tests verify:

```text
- no playback action for guarded/not-generated results;
- a playback action appears for generated opaque URL handoffs;
- legacy non-generated URL responses remain non-playable;
- raw audio URLs are not printed in the widget tree.
```

They do not execute audio, observe play/stop/completion events, simulate an expired HTTP response, or validate replay behavior.

## T-1 implementation split

```text
T-1a  CURRENT / NOT_COMPLETED  inventory and implementation contract only
T-1b  PLANNED                 player abstraction/state model and mock-safe tests
T-1c  PLANNED                 Home UI integration, expired recovery, aggregate T-1 acceptance
```

### T-1b responsibility

```text
- select and document one Flutter-supported in-app audio boundary;
- add a testable player abstraction rather than coupling widget tests to a real browser/audio runtime;
- add play, stop, replay, loading, playing, completed, and failure states;
- keep generated/opaque handoff eligibility checks and hide raw URLs from normal UI;
- use fake player events in normal tests;
- do not complete parent T-1 or perform private audible acceptance.
```

### T-1c responsibility

```text
- integrate the player into the normal voice-output card;
- map an unavailable opaque artifact to a clear expired/regenerate state;
- dispose/stop playback safely when replacing output or leaving the screen;
- preserve accepted Backend TTL/capacity/security headers unless a separately reviewed change is required;
- run focused/full Flutter and Backend regressions;
- synchronize T-1 acceptance only after diff review and operator approval.
```

## T-1a non-change boundary

```text
backend/app/**
backend/tests/**
app/lib/**
app/test/**
app/pubspec.yaml
private audio and operator evidence
AI Character Framework/provider execution
V-1 / R-1 runtime
release versions, fixed ZIPs, tags, and GitHub Releases
```

## T-1a verification boundary

Allowed:

```text
read Public source/docs
compare normalized source hashes
run compileall and credential-free test suites
inspect stable source markers
```

Forbidden:

```text
read backend/local_data audio
call voice-output endpoints against a running private backend
invoke Framework/TTS providers
download or play audio
launch external URLs
add an audio dependency
change runtime or existing tests
build or publish a release
```

T-1a remains NOT_COMPLETED until source-tree checks, full tests, diff review, and operator approval pass. Parent T-1 remains CURRENT / NOT_COMPLETED.
