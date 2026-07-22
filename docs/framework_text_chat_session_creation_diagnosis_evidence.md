# Framework text chat session creation diagnosis evidence

This document records the v1.9.0 Day21 strict configured diagnosis result for the vendored AI Character Framework v4.0.0 checkout.

## Public-safe checkout shape

```text
vendor/AI-Character-Framework_v4.0.0
```

The actual private absolute path is intentionally not recorded.

## Strict configured diagnosis command shape

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

## Recorded result

```text
[smoke-framework-text-chat-session-diagnosis-configured] RESULT
status: error
module: framework
project_root_shape: <configured-framework-root>
likely_cwd_dependency: False
attempt: current-cwd
  status: error
  cwd_shape: <current-working-directory>
  exception_type: FacadeConfigError
  safe_message: Facade preset not found: 'text_chat'. Pass an existing text-only preset name, such as 'text_chat'.
  session_created: False
  has_session_info: False
attempt: framework-root-cwd
  status: error
  cwd_shape: <configured-framework-root>
  exception_type: ModuleNotFoundError
  safe_message: No module named 'registry'
  session_created: False
  has_session_info: False
No ask, ask_stream, or provider call was made.
```

## Interpretation

The strict configured diagnosis shows two different failure modes:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: registry
likely_cwd_dependency -> False
```

This means the issue is not solved by simply running session creation from the configured framework root.

The next likely integration issue is framework import/package layout resolution for the vendored checkout, especially around modules imported as top-level names such as:

```text
registry
```

## What this verifies

This verifies:

```text
- strict configured diagnosis can safely execute and report public-safe results.
- current-CWD session creation fails with FacadeConfigError.
- framework-root-CWD session creation reaches a different failure mode.
- no ask, ask_stream, or provider call was made.
```

## What this does not verify

This does not verify:

```text
- framework session creation succeeds from DRC.
- framework text chat can generate a response.
- provider-backed LLM calls work.
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

## Day21 conclusion

Day21 confirms that the vendored framework strict session creation diagnosis is safe and reproducible.

The next step should diagnose the vendored framework package import layout and top-level `registry` import resolution before attempting chat responses.
