# Configured framework text chat adapter skeleton

This document records the v1.9.0 Day15 backend skeleton for configured AI Character Framework text chat.

## Purpose

Day15 adds a narrow adapter boundary for future configured framework text chat execution.

The current verified app behavior remains:

```text
mock-safe smartphone Web post-advice chat UI verified
```

## Explicit opt-in

Configured framework text chat still requires:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
```

The public example remains off:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=0
```

## New backend skeleton

New file:

```text
backend/app/services/framework_text_chat_adapter.py
```

New boundary names:

```text
FrameworkPostAdviceChatAdapter
FrameworkTextChatResult
```

New source mode names:

```text
framework_text_chat_boundary
framework_text_chat_skipped
framework_text_chat_unavailable
```

## Default behavior

When the explicit gate is off:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=0
→ PostAdviceChatService uses the mock-safe post-advice chat path
→ Chat source remains mock / post_advice_chat
```

## Enabled skeleton behavior

When the explicit gate is on:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
→ PostAdviceChatService routes replies through FrameworkPostAdviceChatAdapter
→ Day15 adapter does not call AI Character Framework
→ missing FRAMEWORK_ROOT returns framework_text_chat_unavailable
→ configured root still returns framework_text_chat_unavailable because real execution is intentionally not implemented yet
```

## Safety rule

Day15 must not import or call AI Character Framework.

Day15 must not call provider APIs.

The skeleton only prepares the boundary for later implementation.

## Future implementation target

A later day can replace the unavailable result with a real adapter implementation behind the same boundary.

Future configured success must still require:

```text
- explicit opt-in
- configured framework path
- backend /chat API call
- framework text chat path used
- Web UI visible character response
- source/fallback state visible
- no secrets, raw provider payloads, private paths, or private LAN IP values in logs
```

## Day15 conclusion

Day15 adds the backend skeleton needed for configured AI Character Framework text chat while preserving mock-safe behavior as the default.
