# Framework text chat unavailable UI verification

This document records the v1.9.0 Day16 verification target for the configured framework text chat unavailable state.

## Purpose

Day15 added the configured framework text chat adapter skeleton.

Day16 verifies that the app can expose a safe unavailable state when the framework text chat gate is enabled but real framework execution is not available yet.

## Target visible state

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE=1
→ post-advice chat starts with framework / framework_text_chat_boundary
→ user sends a message
→ response source becomes framework / framework_text_chat_unavailable
→ safe unavailable guidance is visible
```

## Backend smoke

Backend smoke script:

```text
scripts/smoke_post_advice_framework_text_chat_unavailable.py
```

The smoke script verifies:

```text
- AppConfig.framework_text_chat_smoke_enabled=True
- FRAMEWORK_ROOT / FRAMEWORK_PROJECT_ROOT is not configured
- PostAdviceChatService starts a framework boundary chat session
- sending a message returns framework_text_chat_unavailable
- reply text includes safe guidance
```

It does not call AI Character Framework.

## Flutter widget verification

Flutter widget test verifies:

```text
- Post-advice Chat is visible after advice
- 少し話す starts the framework boundary chat session
- Chat source initially shows framework / framework_text_chat_boundary
- sending a message updates Chat source to framework / framework_text_chat_unavailable
- the safe unavailable message is visible
```

## Success definition

Day16 success means:

```text
framework_text_chat_unavailable is visible and safely separated from mock-safe success and configured framework success
```

Day16 success does not mean:

```text
configured AI Character Framework text chat succeeded
```

## Non-success state rule

```text
framework_text_chat_unavailable != configured framework text chat success
```

## Day16 conclusion

The UI and backend can represent the configured framework text chat unavailable state safely.

Real AI Character Framework execution remains a later explicit opt-in implementation.
