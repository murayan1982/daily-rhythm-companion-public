# Vendor framework checkout preflight evidence

This document records the v1.9.0 Day19 strict configured preflight result for the vendored AI Character Framework v4.0.0 checkout.

## Public-safe checkout shape

```text
vendor/AI-Character-Framework_v4.0.0
```

The actual private absolute path is intentionally not recorded.

## Strict configured preflight command shape

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_configured_preflight.py --require-real-framework
```

## Recorded result

```text
[smoke-framework-text-chat-configured-preflight] OK
module: framework
project_root_shape: <configured-framework-root>
has_create_text_chat_session: True
has_text_chat_session_class: True
No session was created and no provider call was made.
```

## What this verifies

This verifies:

```text
- DRC can use the configured framework root for local import.
- The framework module imports.
- create_text_chat_session is visible.
- Text chat session metadata class is visible.
- The app vendor AI Character Framework v4.0.0 checkout exposes the required public text chat API surface for the next integration step.
```

## What this does not verify

This does not verify:

```text
- create_text_chat_session() can create a usable session from DRC.
- framework text chat can generate a response.
- provider-backed LLM calls work.
- OpenAI, Gemini, or Grok configured chat works.
- STT, TTS, Live2D/VTS, or Google Health integration works.
```

## Non-exposure confirmation

This public-safe evidence file does not include:

```text
- private absolute framework paths
- real API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- raw provider payloads
- private LAN IP values
```

## Day19 conclusion

Day19 confirms the vendored AI Character Framework v4.0.0 checkout can be local-imported from DRC and exposes the expected public text chat API surface.

The next integration step can focus on safe session-creation preflight without sending chat messages or calling providers.
