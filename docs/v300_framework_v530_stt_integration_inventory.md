# Daily Rhythm Companion v3.0.0 RT-3a Framework v5.3.0 STT integration inventory

Status:

```text
RT-3a: COMPLETED / ACCEPTED
RT-3: CURRENT / BLOCKED_REAL_PROVIDER_EXECUTION_NOT_IMPLEMENTED
RT-3b: CURRENT / NOT_COMPLETED
```

## Exact sources

```text
DRC source commit:
c7a6afd85f29fe07564ded02a76fa645b2fb9a69

DRC tracked-tree archive SHA-256:
5432DE388BD4AE13CDD2663839DBBE628C7BC319D821E2C845500A3F920AF786

AI Character Framework release:
v5.3.0

FW DRC/STT surface archive SHA-256:
60AF94A8C3623C0F8D5421B5CA2A6E798E04CD39A1EEA3E9B3A8A29E54BD0096
```

The local vendor path is private operator configuration and is not recorded in
this document or printed by the gate.

## Purpose

RT-3a reassesses the exact released FW v5.3.0 source against the accepted DRC
RT-2 capture boundary before any STT runtime integration begins.

It answers four questions:

1. Which public FW host-audio/STT contracts are available?
2. Does FW v5.3.0 actually execute a real STT provider?
3. Can the current DRC mobile artifact reach the Backend/FW boundary?
4. Which mock-safe DRC work may proceed while real provider execution remains blocked?

## FW v5.3.0 public surface

Present public exports:

```text
VoiceInputAudioSourceKind
VoiceInputAudioEncoding
VoiceInputAudioFormat
VoiceInputAudioRef
VoiceInputAudioSource
VoiceInputRequest
VoiceInputResult
VoiceInputSession
create_voice_input_session
VoiceInputProviderAdapter
FakeVoiceInputProviderAdapter
GuardedRealVoiceInputProviderAdapter
```

Present session methods:

```text
VoiceInputSession.transcribe_audio_result(...)
VoiceInputSession.listen_audio_result(...)
```

The fake adapter returns a typed transcript without dereferencing the audio
source. This is suitable for public-contract tests only.

## Honest real-provider status

`GuardedRealVoiceInputProviderAdapter` is a guard boundary, not a concrete STT
provider implementation.

After explicit provider opt-in and credential-presence checks pass, its preflight
still returns:

```text
available: false
guard: real_stt_not_implemented
provider_execution_executed: false
```

Its `transcribe(...)` method returns a typed unavailable result and records:

```text
audio_read: false
microphone_accessed: false
provider_execution_executed: false
```

Therefore FW v5.3.0 does not unblock DRC real-STT acceptance.

```text
FW v5.3.0 actual provider execution: absent
DRC voice-input audio upload/staging: absent
```

## Current DRC capture and API surface

DRC RT-2 provides:

```text
physical Android permission/capture
WAV 16 kHz mono
15-second maximum
private temporary artifact
opaque capture ID
private artifact path resolver
explicit discard
```

The current RT-2 operator harness is evidence-only. On successful stop it calls
`discardPrivateArtifact(...)` immediately. It does not retain or transfer the
artifact to Backend/FW.

The current Backend voice-input request is metadata-only. It contains optional
format/duration/reference metadata but no audio body, multipart upload, private
staging token, or server-side artifact ownership contract. The endpoint states
that it does not process audio.

A mobile-local file path also cannot be treated as a Backend-local file path.
RT-3 requires an explicit private transfer/staging boundary; forwarding a phone
path string to Backend/FW would be invalid.

## Integration gaps

```text
GAP-1  DRC capture artifact retention/lease ownership for STT handoff
GAP-2  private mobile-to-Backend audio transfer and bounded staging
GAP-3  staged artifact cleanup on success/cancel/error/timeout
GAP-4  DRC Backend adapter constructing FW public host-audio/session objects
GAP-5  concrete FW real-provider adapter that reads staged audio and executes STT
GAP-6  typed transcript/error normalization into the DRC realtime model
```

GAP-1 through GAP-4 may be developed and tested with fake dependencies.
GAP-5 blocks real STT execution and acceptance.

## Small-commit decision

```text
RT-3a
exact DRC/FW v5.3.0 integration inventory
docs/test-only

RT-3b
app-owned capture artifact handoff lifecycle contract
fake-only; no upload and no FW import

RT-3c
private Backend staging boundary plus fake FW public-session handoff
no real provider execution

RT-3d
real provider execution and physical-device STT evidence
blocked until FW provides an accepted concrete real-provider adapter
```

## RT-3b authorization after RT-3a acceptance

```text
authorized-app-owned-host-audio-lifecycle-contract-fake-only
```

RT-3b may define retain/lease/consume/discard semantics around an opaque capture
artifact. It must not add a network upload, expose a private path, import FW,
execute STT, or change the accepted RT-2 operator evidence path by default.

## Non-actions

RT-3a does not:

- change Backend or Flutter runtime;
- change existing tests;
- change dependencies or platform files;
- change vendor FW;
- load private `.env`;
- print `FRAMEWORK_ROOT`;
- import FW;
- read or upload audio;
- open a microphone;
- create a provider client;
- execute STT;
- persist a transcript;
- change version or release records.

## Acceptance evidence

RT-3a is accepted after the following local checks passed:

```text
source-only gate against the vendored FW v5.3.0 surface
Backend: 116 passed with one existing Starlette warning
flutter analyze: No issues found
Flutter: 171 passed
git diff --check
exact seven-file surface review
acceptance-state synchronization
```

No Backend/Flutter runtime, dependency, platform, vendor, private environment,
audio, microphone, provider, STT, version, or release surface changed.
