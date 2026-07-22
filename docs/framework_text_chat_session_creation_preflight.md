# Framework text chat session creation preflight

This document records the v1.9.0 Day20 session creation preflight for framework text chat.

## Purpose

Day19 confirmed that the vendored AI Character Framework v4.0.0 checkout can be imported and exposes `create_text_chat_session`.

Day20 adds a safe preflight for creating a text chat session without sending messages.

## Explicit gate

Public default:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=0
```

Strict configured run requires:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
```

## Source-tree smoke

```text
scripts/smoke_framework_text_chat_session_creation_preflight.py
```

Default source-tree smoke uses a temporary fake framework module.

It verifies:

```text
- create_text_chat_session can be called
- session object is created
- session info is visible
- ask is not called
- ask_stream is not called
- provider APIs are not called
```

## Strict configured operator run

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_preflight.py --require-real-framework
```

## Public-safe success shape

```text
[smoke-framework-text-chat-session-creation-configured] OK
module: framework
project_root_shape: <configured-framework-root>
session_created: True
has_session_info: True
session_info_shape: <session-info>
No ask, ask_stream, or provider call was made.
```

## What this does not verify

This does not verify:

```text
- framework text chat can generate a response
- ask works
- ask_stream works
- provider-backed LLM calls work
- STT, TTS, Live2D/VTS, or Google Health integration works
```

## Day20 conclusion

Day20 prepares a safe session creation preflight boundary.

The next step can record strict configured session creation evidence against the vendored framework checkout.
