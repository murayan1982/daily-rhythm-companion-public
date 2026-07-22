# Framework text chat import layout diagnosis

This document records the v1.9.0 Day23 diagnosis boundary for the vendored framework package/import layout issue.

## Background

Day21 strict configured diagnosis produced:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
likely_cwd_dependency -> False
```

That means the next blocker is not a simple current-working-directory switch. Day23 checks how the vendored framework checkout exposes the `framework` package and the top-level `registry` module name.

## Purpose

Day23 adds a safe import layout diagnosis that answers:

```text
- Which candidate sys.path root makes framework discoverable?
- Which candidate sys.path root makes top-level registry discoverable?
- Does a combined configured-root plus framework-package-dir layout resolve both specs?
- Is the result absorbable by DRC adapter configuration, or should it be FW-side packaging feedback?
```

## Source-tree smoke

```text
scripts/smoke_framework_text_chat_import_layout_diagnosis.py
```

The default source-tree smoke uses a temporary fake framework checkout:

```text
<configured-framework-root>/framework/__init__.py
<configured-framework-root>/framework/registry.py
```

It confirms:

```text
configured-root-only -> framework found, registry missing
framework-package-dir-only -> framework missing, registry found
configured-root-plus-framework-package-dir -> framework found, registry found
```

## Strict configured operator run

```powershell
$env:FRAMEWORK_PROJECT_ROOT="<configured-framework-root>"
$env:DRC_FW40_ENABLE_FRAMEWORK_TEXT_CHAT_SESSION_PREFLIGHT="1"
python scripts\smoke_framework_text_chat_import_layout_diagnosis.py --require-real-framework
```

## Public-safe output fields

```text
status
project_root_shape
registry_file_shapes
candidate
sys_path_shapes
framework_spec_status
registry_spec_status
safe_message
recommendation
```

## Safety

The diagnosis may inspect module specs and repo-relative file shapes.

The diagnosis must not call:

```text
create_text_chat_session
ask
ask_stream
provider APIs
STT/TTS runtime paths
Live2D/VTS runtime paths
```

The diagnosis must not commit:

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
configured-root-plus-framework-package-dir -> framework found, registry found
```

then DRC may be able to absorb the issue with a narrow adapter `sys.path` layout while keeping FW-side relative import cleanup as the better long-term fix.

If no tested layout resolves both names, record it as FW-side packaging/import-layout feedback instead of expanding DRC v1.9.0 into framework internals.

## Day23 conclusion

Day23 keeps the diagnosis public-safe and provider-free while collecting enough evidence to decide between DRC adapter configuration and FW-side packaging feedback.
