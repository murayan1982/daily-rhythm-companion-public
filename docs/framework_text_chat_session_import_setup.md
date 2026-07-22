# Framework text chat session import setup

This document records the v1.9.0 Day24 boundary for the framework text chat session import setup.

## Background

Day23 strict configured import layout diagnosis showed:

```text
configured-root-only
  framework_spec_status: found
  registry_spec_status: found
```

That means the vendored FW4.0.0 checkout can expose both the public `framework` package and the top-level `registry` package from the configured project root.

The next DRC-side risk is narrower:

```text
import framework succeeds
sys.path cleanup happens
create_text_chat_session performs lazy top-level imports
lazy import can fail as ModuleNotFoundError
```

## Purpose

Day24 adds a shared import setup helper for framework text chat session preflight and diagnosis.

The helper keeps the selected FW import layout active through the full session creation attempt, not only through `import framework`.

## Implementation boundary

```text
backend/app/services/framework_text_chat_import_setup.py
```

The helper provides:

```text
framework_text_chat_sys_path_roots
framework_text_chat_import_context
framework_text_chat_import_layout_summary
```

The session preflight and session diagnosis use the shared context around both:

```text
import framework
create_text_chat_session
```

## Selected layout

For the real vendored FW v4.0.0 shape, Day23 evidence recommends:

```text
configured-root-only
```

The helper also supports a narrow fallback for temporary or legacy checkouts where the top-level `registry` name is exposed by:

```text
<configured-framework-root>/framework/registry.py
```

That fallback is recorded as:

```text
framework-package-dir-fallback
```

## Safety

Day24 may call:

```text
create_text_chat_session
```

Day24 must not call:

```text
ask
ask_stream
provider APIs
STT/TTS runtime paths
Live2D/VTS runtime paths
```

Day24 must not commit:

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

## Expected strict configured interpretation

Run:

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_session_creation_diagnosis.py --require-real-framework
```

If the result still fails, the expected value is now the next session-creation failure site after import layout setup. A repeated `ModuleNotFoundError: No module named 'registry'` would mean the helper did not cover the actual lazy import path and should be treated as a DRC import setup bug or a more specific FW packaging feedback item.

## Day24 conclusion

Day24 keeps the fix local to DRC import setup, records the behavior as public-safe evidence, and keeps actual chat execution deferred.
