# Framework text chat session creation diagnosis

This document records the v1.9.0 Day21 diagnosis path for the `FacadeConfigError` observed during strict vendor framework session creation preflight.

## Observed Day20 strict result

```text
Configured framework session creation preflight did not create a session:
error: create_text_chat_session failed safely: FacadeConfigError
```

## Purpose

Day21 adds safe diagnosis for session creation without sending chat messages.

The diagnosis compares:

```text
current-cwd
framework-root-cwd
```

This helps identify whether preset or character resolution depends on the current working directory.

## Source-tree smoke

```text
scripts/smoke_framework_text_chat_session_creation_diagnosis.py
```

The default source-tree smoke uses a temporary fake framework module.

It intentionally raises:

```text
FacadeConfigError
```

when `presets/text_chat.json` cannot be found from the current working directory.

Then it retries with:

```text
cwd_shape: <configured-framework-root>
```

and confirms that the session can be created.

## Strict configured operator run

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

## Public-safe output fields

```text
status
module
project_root_shape
likely_cwd_dependency
attempt
cwd_shape
exception_type
safe_message
session_created
has_session_info
```

## Safety

The diagnosis must not call:

```text
ask
ask_stream
provider APIs
```

The diagnosis must redact:

```text
private absolute paths
API keys
OAuth client secrets
access tokens
refresh tokens
authorization headers
raw provider payloads
private LAN IP values
```

## Expected interpretation

If:

```text
current-cwd: FacadeConfigError
framework-root-cwd: created
likely_cwd_dependency: True
```

then the likely issue is framework-side preset/character resolution depending on the process current working directory.

## Day21 conclusion

Day21 adds a safe way to diagnose vendor framework session creation failures without sending messages or calling providers.
