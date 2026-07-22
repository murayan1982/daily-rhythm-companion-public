# FW4.0.0 Smartphone Web demo requirements

Daily Rhythm Companion is a public demo application for AI Character Framework.

Target framework repository:

```text
https://github.com/murayan1982/ai-character-framework.git
```

## Required outcome

The developer must be able to demonstrate DRC from their own smartphone through Web access.

The demo path is:

```text
smartphone browser
→ Flutter Web UI
→ actual Daily Rhythm Companion backend API
→ configured AI Character Framework integration
→ visible result in the Web UI
```

## Required FW4.0.0-era capability targets

The app must include verification requirements for the following configured FW capabilities:

```text
- LLM
- STT / voice input
- TTS / voice output
- Live2D / VTS motion
```

## Verification rule

API-only success is not enough.

A capability is not considered demo-verified until the result or status is visible through the Web UI.

Valid UI-visible states include:

```text
- configured success
- unavailable
- skipped
- fallback
- error with safe operator guidance
```

However:

```text
skipped / unavailable / fallback must not be counted as configured real execution success.
```

## Public repository rule

This repository is public because DRC is a framework demo app.

Do not commit:

```text
- API keys
- OAuth client secrets
- access tokens
- refresh tokens
- authorization headers
- raw provider payloads
- local credential files
- private absolute paths
```

## Configured real API inputs

The configured test environment may use already-obtained credentials for:

```text
- OpenAI
- Gemini
- Grok
- ElevenLabs
- Google Health API
```

These are represented only by environment variable names and empty placeholders in public files.

## Store release boundary

General consumer App Store / Google Play release work is deferred to v2.0.0 or later.

v1.x should focus on public FW demo validity, smartphone Web demonstration, mock-safe operation, and configured real capability verification.
