# Vendor framework registry import diagnosis scope

This document defines the safe scope for the next `registry` import diagnosis.

## Background

Day21 strict configured diagnosis produced:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
likely_cwd_dependency -> False
```

The `registry` issue is relevant only because it blocks the v1.9.0 LLM/text chat demo path.

## Allowed diagnosis questions

The next diagnosis may answer:

```text
- Which import root makes the vendored framework package importable?
- Does the vendored FW v4.0.0 package expect a different sys.path root?
- Is `registry` a top-level module, package-local module, or missing module?
- Can DRC configure sys.path safely without private paths in docs?
- Is this a DRC adapter configuration issue or an FW-side packaging issue?
```

## Disallowed work in DRC v1.9.0

Do not drift into:

```text
- rewriting framework internals inside the DRC repo
- broad dependency cleanup
- provider API execution
- ask / ask_stream execution
- app-store product polish
```

## Expected Day23 output

The next implementation day may add a source-tree diagnosis script/check that records only public-safe facts:

```text
candidate import roots
module import status
registry import status
public-safe failure type
recommendation: DRC adapter config / FW-side fix / deferred
```

No private absolute paths should be committed.
