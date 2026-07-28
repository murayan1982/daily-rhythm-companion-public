# DRC v3.0.0 RT-3d2a Framework v5.4.0 executor-path correction

Updated: 2026-07-28

```text
RT-3d2a: COMPLETED / ACCEPTED
RT-3d2: CURRENT / NOT_COMPLETED
RT-3d: BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
Framework release: v5.4.0
Framework tag commit: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-3d2a corrects the DRC adoption plan before Backend runtime wiring begins.

The accepted RT-3d1 inventory correctly identified the public OpenAI adapter
and execution configuration, but incorrectly described
`VoiceInputSession.transcribe_audio_result(..., adapter=adapter)` as the real
provider execution path.

FW v5.4.0 intentionally keeps the Voice Input session data-only. The session
calls `adapter.transcribe(...)`. The released
`OpenAIVoiceInputProviderAdapter.transcribe(...)` returns a typed unavailable
result and does not execute a provider.

## Correct released execution boundaries

### Session/fake compatibility path

```text
VoiceInputSession.transcribe_audio_result(...)
-> adapter.transcribe(...)
```

This remains the accepted RT-3c4 fake-session path. It is not the FW v5.4.0
real-provider runtime.

### Bounded fake-client executor path for normal DRC tests

```text
VoiceInputProviderExecutionConfig
-> OpenAIVoiceInputProviderAdapter(direct marked fake client)
-> OpenAIVoiceInputFakeExecutionPolicy
-> OpenAIVoiceInputFakeExecutor.execute(...)
-> provider-neutral VoiceInputResult
```

This path may read only a bounded synthetic/private-staging test artifact and
may invoke only a client inheriting `OpenAIVoiceInputFakeClientMarker`. It does
not import the OpenAI SDK, create a real provider client, read credentials, or
perform network execution.

### Real provider executor path reserved for RT-3d3

```text
VoiceInputProviderExecutionConfig
-> OpenAIVoiceInputPrivateCredential
-> OpenAIVoiceInputRealProviderPolicy
-> OpenAIVoiceInputRealClientFactory
-> OpenAIVoiceInputProviderAdapter
-> OpenAIVoiceInputRealProviderExecutor.execute(...)
-> provider-neutral VoiceInputResult
```

DRC RT-3d2b must not instantiate the private credential or concrete real client
factory during normal application startup or normal tests. Private credential
resolution and actual provider execution remain operator-only RT-3d3 work.

## Corrected RT-3d2 split

```text
RT-3d2a  FW v5.4.0 executor-path correction
RT-3d2b  Backend private-staging to bounded marked-fake executor wiring
RT-3d2c  Guarded real-executor assembly and operator handoff contract
RT-3d3   Private DRC real-STT operator acceptance
RT-3d4   RT-3 aggregate acceptance and block removal
```

## RT-3d2b authorized boundary after acceptance

RT-3d2b may add a DRC-owned Backend service and tests that:

- consume one existing private staged WAV;
- construct FW public `VoiceInputAudioSource` and `VoiceInputRequest`;
- construct explicit provider execution configuration;
- inject a marked fake client;
- execute through `OpenAIVoiceInputFakeExecutor`;
- normalize the public provider-neutral result;
- expose no private path, raw audio, provider payload, or staging ID;
- preserve single-use cleanup;
- perform no real provider execution.

## Framework requirement result

```text
Additional Framework development requirement discovered by RT-3d2a: False
```

The required executor classes are public exports in FW v5.4.0. This is a DRC
adoption-path correction, not a new FW implementation request.

## Non-actions

RT-3d2a changes no Backend or Flutter runtime, dependency, version, environment
contract, Framework source, private audio, microphone, credential, SDK/client,
network, tag, release, or publication surface.

## Acceptance record

RT-3d2a is **COMPLETED / ACCEPTED** after:

```text
FW v5.4.0 exact HEAD/tag: PASS
Voice Input session data-only delegation: PASS
OpenAI adapter session-facing transcribe execution-free: PASS
public fake and real executor exports: PASS
FW fake-execution safe smoke: PASS
FW real-runtime safe smoke: PASS
Backend tests: 145 passed, one existing warning
Flutter analyze: No issues found
Flutter tests: 200 passed
exact eight-file change surface: PASS
git diff --check: PASS
explicit operator approval: RECEIVED
```

No new Framework development requirement was identified. RT-3d2b is `AUTHORIZED / NOT_STARTED`. RT-3d remains blocked.
