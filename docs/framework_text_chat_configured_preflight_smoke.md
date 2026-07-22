# Configured framework text chat local import preflight smoke

This document records the v1.9.0 Day18 configured local import preflight smoke for a real AI Character Framework checkout.

## Purpose

Day17 added the source-tree preflight boundary and a fake-framework smoke.

Day18 adds an operator-facing smoke that can be run against the real framework checkout.

## Script

```text
scripts/smoke_framework_text_chat_configured_preflight.py
```

## Default skip-safe behavior

```powershell
python scripts\smoke_framework_text_chat_configured_preflight.py
```

When the explicit preflight gate is off:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT=0
→ result: SKIPPED
```

## Strict configured operator run

Use placeholder-safe docs:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_configured_preflight.py --require-real-framework
```

Do not commit private absolute framework paths.

## What the smoke verifies

The configured preflight smoke verifies:

```text
- FRAMEWORK_PROJECT_ROOT / FRAMEWORK_ROOT is configured by the operator
- configured root can be used for local import
- framework module imports
- create_text_chat_session is visible
- optional text chat session metadata class is visible when exposed
```

## What the smoke does not do

The configured preflight smoke must not:

```text
- create_text_chat_session()
- create a text chat session
- send a chat message
- call OpenAI
- call Gemini
- call Grok
- call ElevenLabs
- call Google Health
- connect to VTube Studio
```

## Success states

```text
SKIPPED:
- preflight gate is off
- acceptable for normal source-tree checks

UNAVAILABLE:
- preflight gate is on but configured framework checkout cannot be imported
- acceptable only when --require-real-framework is not used

OK:
- preflight gate is on
- configured framework checkout imports
- create_text_chat_session is visible
- no session was created
- no provider call was made
```

## Public-safe evidence

Record only:

```text
- result: SKIPPED / UNAVAILABLE / OK
- project_root_shape: <configured-framework-root>
- has_create_text_chat_session: true/false
- has_text_chat_session_class: true/false
- "No session was created and no provider call was made."
```

Do not record:

```text
- private absolute framework paths
- API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- raw provider payloads
- private LAN IP values
```

## Day18 conclusion

Day18 prepares strict operator preflight for a real framework checkout while still avoiding real framework chat execution.
