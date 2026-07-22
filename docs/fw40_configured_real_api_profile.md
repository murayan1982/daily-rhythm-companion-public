# FW4.0.0 configured real API profile

This document defines the configured real API environment profile for the v1.9.0 smartphone Web FW4.0.0 demo hardening milestone.

## Purpose

DRC must remain mock-safe by default while still supporting explicit configured checks for real FW/provider-backed behavior.

The configured real API profile is used only when the operator intentionally wants to verify real or configured demo behavior.

## Profile file

Public placeholder file:

```text
backend/env_profiles/fw40_configured_real_api.env.example
```

This file must contain environment variable names and empty or placeholder values only.

A private local copy may contain real values, but that private file must not be committed.

## API credentials available for configured tests

The following credentials have been obtained by the operator and may be represented as configured test environment variables:

```text
OpenAI
Gemini
Grok
ElevenLabs
Google Health API
```

Public variable names:

```text
OPENAI_API_KEY
GEMINI_API_KEY
GOOGLE_API_KEY
XAI_API_KEY
ELEVENLABS_API_KEY
GOOGLE_HEALTH_CREDENTIALS_FILE
```

## Explicit opt-in gates

Configured checks must require explicit opt-in.

```text
DRC_FW40_ENABLE_CONFIGURED_REAL_API_SMOKE
DRC_FW40_ENABLE_WEB_UI_RUNTIME_VERIFICATION
DRC_FW40_ENABLE_LLM_REAL_API_SMOKE
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE
DRC_FW40_ENABLE_STT_REAL_API_SMOKE
DRC_FW40_ENABLE_TTS_REAL_API_SMOKE
DRC_FW40_ENABLE_LIVE2D_VTS_RUNTIME_SMOKE
DRC_FW40_ENABLE_GOOGLE_HEALTH_REAL_API_SMOKE
```

Default value in public examples:

```text
0
```

A configured real check must not run just because an API key exists.

## Mock-safe default

Mock-safe/default checks must continue to work without:

```text
- AI Character Framework checkout
- provider API keys
- ElevenLabs key
- Google Health credentials
- VTube Studio connection
- smartphone Web runtime
```

## Non-exposure rules

Do not commit or paste into shared logs:

```text
- real API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- raw provider payloads
- local credential files
- private absolute paths
- full debug traces that contain provider request/response bodies
```

## Provider mapping

```text
LLM:
- OpenAI: OPENAI_API_KEY
- Gemini: GEMINI_API_KEY or GOOGLE_API_KEY
- Grok: XAI_API_KEY

TTS:
- ElevenLabs: ELEVENLABS_API_KEY

Health data:
- Google Health API: GOOGLE_HEALTH_CREDENTIALS_FILE and explicit Google Health real API flags
```

## Configured success rule

Configured success requires:

```text
- explicit opt-in gate enabled
- required private credential configured outside the public repository
- runtime/provider path available
- actual backend API call
- visible Web UI result where the feature is part of the smartphone Web demo
- safe logs with no secrets or raw payloads
```

Skipped, unavailable, or fallback states are valid visible states, but they must not be counted as configured real execution success.

## Framework text chat configured gate

Post-advice chat has a mock-safe path by default.

Configured AI Character Framework text chat must require this explicit opt-in gate:

```text
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SMOKE
```

Default public value:

```text
0
```

A configured framework text chat check must not run just because framework paths or provider keys exist.
