# Framework text chat local import preflight

This document records the v1.9.0 Day17 local import preflight for future configured AI Character Framework text chat.

## Purpose

Day17 checks whether DRC can safely prepare for framework text chat local import before actually executing framework chat.

The preflight is intentionally limited to:

```text
- resolving FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT
- temporarily adding the configured root to sys.path
- importing the framework module
- checking whether create_text_chat_session is visible
- checking whether a text chat session metadata class is visible
```

The preflight must not:

```text
- create a text chat session
- send a chat message
- call LLM providers
- call TTS providers
- call STT providers
- open VTube Studio
- expose private paths
```

## Explicit preflight gate

Public default:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=0
```

Preflight must be explicit. It must not run just because framework paths or provider keys exist.

## New backend boundary

```text
backend/app/services/framework_text_chat_preflight.py
```

Boundary names:

```text
FrameworkTextChatPreflightService
FrameworkTextChatPreflightResult
```

Possible statuses:

```text
skipped
unavailable
available
```

## Smoke strategy

Day17 uses a temporary fake framework module in:

```text
scripts/smoke_framework_text_chat_local_import_preflight.py
```

The smoke verifies mechanics without depending on the real framework checkout.

It confirms that `create_text_chat_session` can be detected without calling it.

## Public-safe result shape

Preflight results should use placeholder-safe root descriptions:

```text
<configured-framework-root>
```

Public docs and logs must not include private absolute paths.

## Day17 conclusion

Day17 prepares the local import preflight boundary.

Configured framework text chat execution remains a later explicit opt-in step.
