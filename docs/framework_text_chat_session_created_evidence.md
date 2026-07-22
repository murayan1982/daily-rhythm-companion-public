# Framework text chat session created evidence

Day28 records the public-safe result after Day27 local opt-in allowed the strict session diagnosis to progress from provider env readiness to session creation.

## Confirmed local operator shape

The operator strict diagnosis reached:

```text
status: created
likely_cwd_dependency: True
attempt: current-cwd
  status: error
  exception_type: FacadeConfigError
  failure_kind: unknown
  session_created: False
attempt: framework-root-cwd
  status: created
  exception_type: None
  failure_kind: none
  session_created: True
  has_session_info: True
No ask, ask_stream, or provider call was made.
```

This means the vendored AI Character Framework v4.0.0 public text chat session can be created when:

```text
FRAMEWORK_PROJECT_ROOT points at vendor/AI-Character-Framework_v4.0.0
DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT=1
required provider env names are configured locally
session creation runs with the framework root CWD/import layout
```

## Public-safe evidence renderer

Day28 adds:

```text
backend/app/services/framework_text_chat_session_created_evidence.py
scripts/smoke_framework_text_chat_session_created_evidence.py
```

The renderer records only:

```text
status
likely_cwd_dependency
created attempt name
created CWD shape
current-CWD exception/failure kind
session_created=True|False
has_session_info=True|False
next_step
safe summary
```

It does not record prompts, responses, provider payloads, API key values, raw paths, LAN IPs, or user-specific secrets.

## Optional strict evidence command

Run only after local env readiness is already `ready`:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<repo-root>\vendor\AI-Character-Framework_v4.0.0"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"

python scripts\smoke_framework_text_chat_session_created_evidence.py --require-real-framework
```

Expected public-safe shape:

```text
session_created_evidence_status: created
session_created_evidence_likely_cwd_dependency: True
session_created_evidence_created_attempt: framework-root-cwd
session_created_evidence_session_created: True
session_created_evidence_has_session_info: True
session_created_evidence_next_step: design-explicit-live-text-chat-message-gate
```

## Day28 conclusion

The DRC side has now verified the configured FW4.0.0 text chat path through session creation. The active next step is not more import/provider-env diagnosis; it is designing an explicit live text-chat message gate before any `ask` or `ask_stream` call is allowed.

Day28 does not call `ask`, `ask_stream`, OpenAI, Gemini, Grok, ElevenLabs, Google Health, or VTube Studio. It does not expose or persist API key values.
