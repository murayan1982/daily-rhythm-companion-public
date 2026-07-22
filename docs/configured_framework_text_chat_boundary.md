# Configured AI Character Framework text chat boundary

This document defines the v1.9.0 Day14 boundary for moving from mock-safe post-advice chat to configured AI Character Framework text chat.

## Current verified state

The current verified state is:

```text
mock-safe smartphone Web post-advice chat UI verified
```

The app can already demonstrate this path:

```text
smartphone browser
→ release-built Flutter Web UI
→ actual DRC backend API
→ advice result
→ Post-advice Chat
→ mock-safe chat session
→ visible user and character messages
```

## Target configured boundary

Future configured framework text chat path:

```text
smartphone browser
→ Flutter Web post-advice chat UI
→ DRC backend /chat boundary
→ configured AI Character Framework text chat adapter
→ visible Web UI character response
```

## Explicit opt-in gate

Configured AI Character Framework text chat must be disabled by default in public examples.

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=0
```

A configured framework text chat check must not run just because:

```text
- AI Character Framework checkout exists
- FRAMEWORK_ROOT is set
- provider API keys exist
- the mock-safe post-advice chat UI works
```

It must require explicit opt-in.

## Request context boundary

A future configured text chat adapter may receive:

```text
- session_id
- character_id
- mood
- advice_message
- advice_basis
- AdviceSource metadata
- report_handoff metadata when present
- prior chat messages
- latest user message
```

The adapter must not require raw provider payloads or secrets in request bodies.

## State definitions

### configured success

Configured framework text chat success requires:

```text
- DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
- framework path configured outside public docs
- DRC backend /chat API called
- configured AI Character Framework text chat path used
- Web UI shows the character response
- Chat source or equivalent UI state indicates configured framework success
- shared logs contain no secrets, raw provider payloads, private paths, or private LAN IP values
```

### mock

Mock chat means:

```text
- the current provider-free post-advice chat service generated the response
- the UI can show a useful character-like reply
- no external framework/provider was called
```

Mock chat is not configured framework text chat success.

### framework fallback

Framework fallback means:

```text
- the app attempted or selected a framework-capable path but returned a safe fallback
- the UI shows fallback clearly
- the flow remains usable
```

Framework fallback is not configured framework text chat success.

### unavailable

Unavailable means:

```text
- framework checkout, configuration, dependency, or runtime is missing
- the UI or logs show safe operator guidance
```

Unavailable is not configured framework text chat success.

### skipped

Skipped means:

```text
- explicit opt-in gate is off
- the configured check intentionally did not run
```

Skipped is not configured framework text chat success.

### error

Error means:

```text
- configured framework text chat was attempted and failed
- UI/logs show a safe operator-facing error
- secrets, raw provider payloads, private paths, and private LAN IP values are not exposed
```

Error is not configured framework text chat success.

## Public-safe evidence requirements

Configured framework text chat evidence should record only:

```text
- runtime mode shape
- opt-in gate enabled: yes
- backend API route shape
- Web UI response visible: yes/no
- Chat source visible: yes/no
- state: configured success / mock / framework_fallback / unavailable / skipped / error
```

Do not record:

```text
- real API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- raw provider payloads
- private credential paths
- private absolute paths
- private LAN IP values
```

## Implementation boundary for a later day

A later implementation day should add a narrow backend adapter boundary rather than mixing framework-specific code directly into the UI.

Candidate backend components:

```text
FrameworkPostAdviceChatAdapter
FrameworkTextChatResult
PostAdviceChatMode
```

Candidate API behavior:

```text
POST /chat/sessions
POST /chat/sessions/{session_id}/messages
```

The API shape should remain stable for the Flutter UI. The backend should choose mock-safe or configured framework behavior based on explicit configuration.

## Day14 conclusion

Day14 does not call AI Character Framework.

It defines the safe boundary required before adding configured framework text chat execution.
