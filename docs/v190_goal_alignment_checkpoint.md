# v1.9.0 goal alignment checkpoint

This document keeps the v1.9.0 work aligned with the original DRC demo-app goal.

## v1.9.0 product goal

v1.9.0 is not a general consumer app-store release.

v1.9.0 is the smartphone Web demo hardening milestone for Daily Rhythm Companion as an explicit demo app for:

```text
https://github.com/murayan1982/ai-character-framework.git
```

The app must remain suitable for public repository release as a demo app.

## Required v1.9.0 outcome

v1.9.0 should allow the operator to use their own smartphone Web browser to verify the app through the actual DRC backend API.

The required verification shape is:

```text
smartphone browser
→ Flutter Web UI
→ actual DRC backend API
→ AI Character Framework v4.0.0 capability surfaces
→ visible Web UI evidence
→ public-safe docs/check evidence
```

## Required FW capability targets

The v1.9.0 roadmap keeps these FW4.0.0 capability targets in scope:

```text
LLM / text chat
STT / voice input boundary
TTS / voice output boundary
Live2D / VTS motion boundary
```

## Current confirmed progress

Already verified and recorded:

```text
smartphone Web app load
backend API connection
API base URL display
advice result display
post-advice chat mock-safe API
post-advice chat Flutter UI
post-advice chat smartphone Web manual evidence
configured framework text chat boundary
framework unavailable UI state
framework local import preflight
vendor AI Character Framework v4.0.0 import/API visibility
session creation preflight boundary
session creation diagnosis evidence
```

## Current LLM / text chat status

The LLM/text chat integration path is currently blocked before provider calls by vendor framework session creation.

Current public-safe strict diagnosis:

```text
current-cwd -> FacadeConfigError
framework-root-cwd -> ModuleNotFoundError: No module named 'registry'
likely_cwd_dependency -> False
```

This means the next LLM/text chat step may diagnose package/import layout only as a blocker to the v1.9.0 FW demo goal.

## Scope guardrails

The following are in scope for v1.9.0:

```text
- DRC adapter / preflight / evidence code needed to verify FW4.0.0 capability surfaces.
- public-safe evidence docs.
- smartphone Web UI evidence.
- mock-safe fallback paths that keep the demo usable.
- explicit opt-in checks for real/configured behavior.
- diagnosis that identifies why the FW4.0.0 demo path cannot proceed.
```

The following are not in scope for v1.9.0:

```text
- general app-store consumer polish
- production OAuth rollout
- broad FW internal refactoring inside the DRC repo
- unbounded debugging of framework internals
- provider calls without explicit opt-in
- storing secrets, real API keys, private absolute paths, or private LAN IP values in repo
```

## Registry import diagnosis scope

The `registry` import issue may be investigated only to answer:

```text
Can DRC's vendored AI Character Framework v4.0.0 checkout be imported and used through its public API boundary from the DRC backend?
```

The DRC side may document and work around package root/sys.path configuration if needed.

If the issue requires framework-side source changes, record it as an FW-side feedback item rather than turning the DRC v1.9.0 milestone into framework internal repair work.

## Next-step decision rule

Before each new v1.9.0 day, choose work that directly contributes to one of:

```text
- smartphone Web verification
- FW4.0.0 capability surface verification
- public-safe evidence
- explicit opt-in real/configured smoke checks
- keeping mock-safe demo behavior usable
```

If a task does not support one of these, defer it to v2.0.0 or to the AI Character Framework repo.
