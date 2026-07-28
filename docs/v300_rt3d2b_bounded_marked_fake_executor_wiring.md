# DRC v3.0.0 RT-3d2b bounded marked-fake executor wiring

Updated: 2026-07-28

```text
RT-3d2b: IMPLEMENTED / NOT_ACCEPTED
RT-3d2: CURRENT / NOT_COMPLETED
RT-3d: BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
Framework release: v5.4.0
Framework tag commit: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-3d2b connects the accepted DRC private Backend staging store to the released
FW v5.4.0 bounded marked-fake OpenAI execution boundary.

It proves the runtime shape needed by later guarded real execution while
remaining credential-free and network-free.

## Added runtime path

```text
POST /demo/voice-input/staging
-> opaque staging ID
-> POST /demo/voice-input/staging/{id}/openai-fake-executor
-> private path available only inside VoiceInputStagingStore.consume()
-> VoiceInputAudioSource
-> VoiceInputProviderExecutionConfig
-> OpenAIVoiceInputProviderAdapter
-> marked fake OpenAI client
-> OpenAIVoiceInputFakeExecutionPolicy
-> OpenAIVoiceInputFakeExecutor.execute()
-> provider-neutral VoiceInputResult
-> DRC path-free response
-> staged WAV single-use cleanup
```

The existing RT-3c4 `/fake-handoff` session route remains unchanged.

## Safety boundary

Normal application startup and normal tests do not:

- read an API key or credential value;
- import the OpenAI SDK;
- create an actual OpenAI client;
- execute a network request;
- access a microphone;
- expose a private path, raw audio, provider payload, or staging ID in the
  execution result;
- claim real provider or real STT execution.

The explicit `credentials_available=True` value is only the released FW
execution-config availability assertion required by the marked-fake preflight.
No credential name or value is supplied or read.

## Result distinction

The response records:

```text
adapter_name: openai
executor_name: openai_marked_fake
fake_provider_protocol_call_executed: true
audio_read: true
provider_sdk_imported: false
provider_client_created: false
credential_values_read: false
real_provider_execution_executed: false
fake_stt_executed: true
real_stt_executed: false
```

## Cleanup behavior

Framework-root and public-contract preflight failures occur before
`VoiceInputStagingStore.consume()` and preserve the artifact for retry.

Once bounded execution begins, success, executor failure, and unsafe-result
rejection all end in single-use staged-artifact removal.

## Framework requirement result

```text
Additional Framework development requirement discovered by RT-3d2b: False
```

The required fake marker, adapter, policy, executor, source, request, and result
contracts are all released public FW v5.4.0 exports.

## Non-actions

RT-3d2b adds no Flutter runtime, dependency, platform declaration, environment
credential setting, OpenAI dependency, real provider assembly, private operator
evidence, version, release, tag, or publication change.
