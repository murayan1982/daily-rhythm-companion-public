# Framework text chat provider env diagnosis

Day25 records the next strict configured session-creation blocker after the Day24 import setup fix.

## Context

Day23 showed that `configured-root-only` resolves both `framework` and the top-level `registry` module.

Day24 kept that import layout active through `create_text_chat_session`, so the strict configured diagnosis no longer stops at `ModuleNotFoundError: registry`.

The next observed strict configured failure site is:

```text
framework-root-cwd -> OSError
safe_message: GOOGLE_API_KEY is not defined.
```

This means session creation has reached provider environment initialization. It does not mean a provider request was sent.

## Day25 boundary

Day25 adds a provider-env diagnosis helper:

```text
backend/app/services/framework_text_chat_provider_env_diagnosis.py
```

The helper may classify sanitized session-creation failure messages such as:

```text
GOOGLE_API_KEY is not defined.
```

It records only:

```text
- failure_kind
- public env var names
- boolean set/unset status
- public-safe operator message
```

It must not record or print actual API key values.

## Known provider env names

The current public-safe inventory recognizes these names:

```text
GOOGLE_API_KEY
GEMINI_API_KEY
OPENAI_API_KEY
XAI_API_KEY
```

The Day24 strict result specifically references `GOOGLE_API_KEY`.

## Operator guidance

To continue strict FW text chat session creation, configure provider credentials only in the local operator environment or `backend/.env`.

do not commit secrets, provider credentials, raw payloads, bearer tokens, or absolute private paths.

Example shape only:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<repo-root>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
# $env:GOOGLE_API_KEY="<local-secret-only>"

python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

The strict command may create a FW text chat session for diagnosis. It must still not call `ask`, `ask_stream`, or provider APIs.

## Day25 conclusion

The Day24 import-layout blocker is resolved. The next blocker is provider environment readiness during session construction.

Day25 keeps the work public-safe by documenting and classifying the requirement without storing secrets or making provider calls.
