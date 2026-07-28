# DRC v3.0.0 RT-3d1 Framework v5.4.0 real STT adoption inventory

Updated: 2026-07-28

```text
RT-3d1: COMPLETED / ACCEPTED
RT-3d: BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
Framework release: v5.4.0
Framework tag commit: d313eb6acb643103fe25988720ebee5976a04f78
Framework release ZIP SHA-256: 3acebbc250d575df86cde710d07b962158b266fc6dc969e49c3fbce2e3d6c65d
```

## Purpose

RT-3d1 freezes the released FW v5.4.0 real-STT public surface selected for
later DRC adoption. This is docs/test-only. It does not wire DRC runtime to
OpenAI, read audio or credentials, create a provider client, execute a network
request, expose transcript text, or unblock RT-3d.

## Verified release identity

```text
DRC baseline HEAD/origin:
7b1d0154079dc38cce41b3a813df07a0053815e4

FW v5.4.0 tag and clean main HEAD:
d313eb6acb643103fe25988720ebee5976a04f78

ZIP:
ai-character-framework_v5.4.0.zip
size: 505403 bytes
SHA-256: 3acebbc250d575df86cde710d07b962158b266fc6dc969e49c3fbce2e3d6c65d

sidecar:
ai-character-framework_v5.4.0.zip.sha256
size: 100 bytes
```

The GitHub Release is published, non-draft, non-prerelease, and contains the
ZIP and sidecar. The downloaded published ZIP matched the accepted local ZIP.

## Required public exports

```text
OpenAIVoiceInputProviderAdapter
VoiceInputProviderExecutionConfig
VoiceInputAudioSource
VoiceInputSession
create_voice_input_session
```

The selected released execution path is:

```text
VoiceInputProviderExecutionConfig
-> OpenAIVoiceInputProviderAdapter
-> VoiceInputSession.transcribe_audio_result(..., adapter=adapter)
```

The default Voice Input session adapter remains fake. DRC must explicitly
inject the released OpenAI adapter for configured real execution.

## Accepted FW v5.4.0 evidence

```text
smoke_v540_provider_execution_configuration_status.py
smoke_v540_openai_adapter_client_injection_contract.py
smoke_v540_openai_fake_execution_boundary.py
smoke_v540_openai_real_provider_runtime.py
smoke_v540_openai_private_real_provider_operator_acceptance.py
```

These boundaries preserve default-off execution, explicit provider selection,
lazy SDK/client creation, provider-safe root import, fake execution, safe error
classification, and accepted private real-provider evidence.

## RT-3d continuation

```text
RT-3d1  Framework v5.4.0 released-surface adoption inventory
RT-3d2  DRC private staging to public v5.4.0 adapter wiring
RT-3d3  DRC private real-STT operator acceptance
RT-3d4  RT-3 aggregate acceptance and block removal
```

RT-3d2 may wire only:

```text
DRC private staged WAV
-> VoiceInputAudioSource
-> VoiceInputProviderExecutionConfig
-> OpenAIVoiceInputProviderAdapter
-> VoiceInputSession
-> typed provider-neutral result
-> single-use cleanup
```

Normal tests must use injected fake execution and make no real provider call.

## Framework requirement result

```text
Additional Framework development requirement discovered by RT-3d1: False
```

If RT-3d2 discovers an incompatible public FW boundary, DRC work must stop and
the issue must return to the dedicated FW development thread.

## Non-actions

RT-3d1 changes no DRC Backend/Flutter runtime, Framework source, dependency,
version, platform, audio, microphone, credential, provider SDK/client, network,
release, tag, or publication surface.


## Acceptance record

RT-3d1 is **COMPLETED / ACCEPTED** after:

```text
FW v5.4.0 tag/HEAD/ZIP/sidecar verification: PASS
FW required public exports and signatures: PASS
FW accepted safe runtime gates: PASS
DRC dedicated RT-3d1 source-only gate: PASS
Backend tests: 145 passed, one existing warning
Flutter analyze: No issues found
Flutter tests: 200 passed
exact seven-file change surface: PASS
git diff --check: PASS
explicit operator approval: RECEIVED
```

No new Framework development requirement was identified. RT-3d2 is authorized
for guarded DRC wiring with injected fake-client tests. RT-3d remains
`BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING`.
