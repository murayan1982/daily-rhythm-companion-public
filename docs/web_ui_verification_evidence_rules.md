# Web UI verification evidence rules

This document defines the UI-visible evidence rules for the v1.9.0 smartphone Web FW4.0.0 demo hardening milestone.

## Core rule

```text
API success alone is not enough.
```

A capability or flow is not considered demo-verified until the operator can see the relevant result, status, fallback, unavailable state, skipped state, error explanation, or save result in the Web UI.

Required path:

```text
smartphone browser or browser UI
→ Flutter Web UI
→ actual Daily Rhythm Companion backend API
→ configured runtime when enabled
→ visible Web UI result
```

## Evidence state definitions

### configured success

Configured success means:

```text
- explicit opt-in gate is enabled
- required private credential or runtime is configured outside the public repository
- actual backend API call runs
- configured runtime/provider path succeeds
- Web UI shows the result or success state
- shared evidence contains no secrets or raw provider payloads
```

### fallback

Fallback means:

```text
- the app returns a safe fallback response or mode
- the UI shows that fallback happened
- fallback is useful for demo continuity
- fallback must not be counted as configured real execution success
```

### unavailable

Unavailable means:

```text
- the capability is not available in the current environment
- the UI shows why it is unavailable or how to configure it
- unavailable must not be counted as configured real execution success
```

### skipped

Skipped means:

```text
- a check or capability was intentionally not run
- the UI or log explains the missing opt-in, dependency, credential, or runtime
- skipped must not be counted as configured real execution success
```

### error

Error means:

```text
- the runtime or request failed
- the UI shows a safe operator-facing explanation
- shared evidence must not include secrets, tokens, raw provider payloads, or full provider debug traces
```

## LLM / advice evidence

Required UI surfaces:

```text
- Home advice action
- Home advice result
- source/fallback explanation
- DailyRecord save result when saved
- History review when saved
```

Configured success evidence later requires:

```text
- selected character is visible
- selected mood is visible
- advice result is visible
- source state indicates configured framework/provider success
- fallback state is not counted as configured success
```

Valid non-success visible states:

```text
- mock
- framework_fallback
- skipped
- unavailable
- error with safe guidance
```

## STT / voice input evidence

Required UI surfaces:

```text
- voice input demo section
- voice input status
- recognized text when configured STT succeeds
- unavailable/skipped/fallback state when configured STT is not available
```

Configured success evidence later requires:

```text
- explicit STT opt-in is enabled
- Web UI initiates the voice input path
- recognized text or equivalent configured STT result is visible
- metadata-only request/status wiring is not counted as real STT success
```

## TTS / voice output evidence

Required UI surfaces:

```text
- voice output demo section
- voice output status
- request/result state
- playback state if audio playback is implemented
- unavailable/skipped/fallback state when configured TTS is not available
```

Configured success evidence later requires:

```text
- explicit TTS opt-in is enabled
- ElevenLabs or FW voice output path is configured outside the public repo
- Web UI initiates the voice output path
- generated voice output status or playback state is visible
- metadata-only request/status wiring is not counted as real TTS success
```

## Live2D / VTS motion evidence

Required UI surfaces:

```text
- motion demo section
- motion status
- trigger/result state
- visible motion evidence or safe connected/status indicator
- unavailable/skipped/fallback state when configured Live2D/VTS is not available
```

Configured success evidence later requires:

```text
- explicit Live2D/VTS opt-in is enabled
- VTube Studio or FW motion bridge is available
- Web UI triggers the motion path
- UI shows motion trigger/result status
- visible motion or connected runtime evidence is available
- metadata-only request/status wiring is not counted as real VTS success
```

## Google Health / health data evidence

Required UI surfaces:

```text
- health data status
- Google Health connection UX
- Google Health diagnostics / self-check / preflight
- sleep summary or safe unavailable state
```

Configured success evidence later requires:

```text
- explicit Google Health real API opt-in is enabled
- private credentials are configured outside the public repo
- backend request succeeds without exposing tokens or raw payloads
- Web UI shows health data source/status or safe result
- unavailable/skipped/fallback is not counted as real health API success
```

## DailyRecord and History evidence

Required UI surfaces:

```text
- save DailyRecord action/result
- History saved record list
- advice message summary
- advice basis
- source display
- report-informed reflection when applicable
```

Configured evidence later requires:

```text
- advice is generated or safely returned
- save result is visible
- saved record appears in History
- History copy does not confuse historical report context with today's sleep data
```

## Report-informed advice/reflection evidence

Required UI surfaces:

```text
- report-informed advice context card or text
- DailyRecord report-informed reflection copy
- History report-informed reflection copy
```

Configured evidence later requires:

```text
- report_handoff metadata is present when used
- UI translates raw metadata into understandable copy
- historical report context is described as auxiliary context
- report-informed advice is not presented as medical analysis or today's sleep data
```

## Manual evidence record

Manual smartphone Web smoke evidence should record:

```text
- device/browser
- Web UI URL shape
- backend API base URL shape
- selected character
- selected mood
- selected capability mode
- visible UI result
- visible success/fallback/unavailable/skipped/error state
- whether the run was mock-safe or configured real API
```

Manual evidence must not include:

```text
- API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- private credential paths
- raw provider payloads
- full provider debug traces
- private absolute paths
```

## Day5 conclusion

The v1.9.0 demo requirement is UI-evidence based.

API-only success can support debugging, but it is not enough for smartphone Web demo completion.
