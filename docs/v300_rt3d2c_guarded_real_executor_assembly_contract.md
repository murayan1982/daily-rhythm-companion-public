# DRC v3.0.0 RT-3d2c guarded real-executor assembly contract

Updated: 2026-07-28

```text
RT-3d2c: COMPLETED / ACCEPTED
RT-3d2: CURRENT / NOT_COMPLETED
RT-3d: BLOCKED_DRC_V540_REAL_STT_WIRING_AND_OPERATOR_ACCEPTANCE_PENDING
Framework release: v5.4.0
Framework tag commit: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-3d2c adds the guarded assembly contract needed before any private DRC
real-provider execution. It proves that DRC can assemble the released FW v5.4.0
public OpenAI real-executor object graph without executing it.

## Public assembly sequence

```text
resolve_voice_input_provider_execution_config(...)
-> OpenAIVoiceInputPrivateCredential supplied by a private caller
-> OpenAIVoiceInputRealProviderPolicy
-> OpenAIVoiceInputRealClientFactory
-> OpenAIVoiceInputProviderAdapter
-> OpenAIVoiceInputRealProviderExecutor
-> safe DRC assembly snapshot plus opaque private executor handle
```

Only FW v5.4.0 root public exports are used. DRC does not import a Framework
internal module and does not create a custom provider client.

## Explicit guard order

Before Framework public import or credential-object preparation, the request
must explicitly enable all of:

```text
operator_handoff_enabled
allow_provider_execution
credentials_available
allow_provider_sdk_import
allow_provider_client_creation
allow_real_provider_execution
```

An incomplete request fails before the public context or private credential
builder is entered.

## Credential boundary

Credential resolution remains outside the DRC service. A private operator caller
supplies a builder that receives the released public
`OpenAIVoiceInputPrivateCredential` type and returns one opaque object.

DRC validates only the object's public type. It does not read, log, serialize,
return, or persist the credential value. Normal tests use a synthetic credential
class with no private value.

## Assembly-only boundary

RT-3d2c constructs but does not invoke:

```text
OpenAIVoiceInputRealClientFactory
OpenAIVoiceInputRealProviderExecutor
```

The returned public-safe snapshot records:

```text
credential_object_injected: true
credential_value_read_by_drc: false
provider_sdk_imported: false
provider_client_created: false
network_request_executed: false
real_provider_execution_executed: false
audio_read: false
microphone_accessed: false
private_path_exposed: false
raw_audio_exposed: false
provider_payload_exposed: false
```

The opaque executor is available only through
`private_operator_executor` for a later private handoff. RT-3d2c never calls
`execute()`.

## Normal-test result

Focused synthetic Backend tests verify:

```text
successful public object-graph assembly
operator guard before Framework context
incomplete opt-in before credential builder
missing public contract before credential preparation
invalid credential object before factory/executor use
client factory calls: 0
executor calls: 0
focused tests: 5 passed
```

## Framework requirement result

```text
Additional Framework development requirement discovered by RT-3d2c: False
```

The required configuration, credential type, real policy, runtime mode, client
factory, adapter, and real executor are all released FW v5.4.0 public exports.

## Non-actions

RT-3d2c adds no API route, AppConfig/environment credential flag, credential
value, OpenAI dependency, staging consume, audio source/read, microphone access,
provider client, network request, provider payload, transcript, real STT
evidence, Flutter change, version, release, tag, or publication change.

## Current validation state

```text
compileall: PASS
dedicated RT-3d2c gate: PASS
focused Backend: 5 passed
Backend full pytest: 158 passed, one existing warning
Flutter analyze: No issues found
Flutter full tests: 200 passed
exact nine-file surface: PASS
git diff --check: PASS
explicit operator approval: ACCEPTED
```

RT-3d2c is **COMPLETED / ACCEPTED**. Acceptance passed with implementation
commit `12a9d35b161da303325097a58f3913fe0c3b5708`, the dedicated gate,
focused Backend 5, full Backend 158 with one existing warning, clean Flutter
analysis, Flutter 200, exact nine-file implementation review, acceptance-only
seven-file review, `git diff --check`, and explicit operator approval.

RT-3d3 is `AUTHORIZED / NOT_STARTED`. Private credential use, OpenAI SDK/client
creation, network execution, provider payload, transcript evidence, and real STT
operator acceptance remain separate explicit work.
