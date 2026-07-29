# DRC v3.0.0 RT-4d FW root-public streaming adapter

Updated: 2026-07-29

```text
RT-4: CURRENT / NOT_COMPLETED
RT-4a: COMPLETED / ACCEPTED / PUSHED
RT-4b: COMPLETED / ACCEPTED / PUSHED
RT-4c: IMPLEMENTED / AWAITING_ACCEPTANCE
RT-4d: IMPLEMENTED / AWAITING_ACCEPTANCE
DRC baseline HEAD: 72622cab2e73699adaff4b628cfbc4b14323a23a
FW v5.4.0 tag: d313eb6acb643103fe25988720ebee5976a04f78
```

## Purpose

RT-4d connects the accepted RT-4b/c Backend text-stream lifecycle to the FW
v5.4.0 text-chat root public surface. The adapter starts one FW text-chat
session, consumes `ask_stream()` chunks, publishes bounded DRC stream events,
requests public `interrupt()` on cancel, and closes/disposes the public session.

Normal regression tests use an injected fake root `framework` package. They do
not call a real provider.

## Public Framework Boundary

Allowed root public API:

```text
framework.create_text_chat_session()
TextChatSession.ask_stream()
TextChatSession.interrupt()
TextChatSession.close()
TextChatSession.dispose()
```

Forbidden:

```text
Framework internal-module import: forbidden
DRC provider client: forbidden
provider payload forwarding: forbidden
provider-level hard cancel claim: forbidden
Flutter changed: false
```

The Backend continues to report:

```text
cancel_mode=cooperative
hard_cancel_supported=false
```

`interrupt()` is treated as a cooperative request. RT-4d does not claim that an
in-flight provider request, provider billing, or provider-side work was stopped.

## Runtime Gate

Framework streaming is default-off:

```text
DRC_RT4_ENABLE_FRAMEWORK_TEXT_STREAM=0
```

When the gate is off, the existing RT-4c provider-free SSE session path remains
unchanged. When the gate is on, the API registry constructs
`FrameworkRealtimeTextStreamAdapter` and connects it to the transport producer
interface.

## Change Surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
backend/.env.example
backend/app/config.py
backend/app/api/realtime_text.py
backend/app/services/realtime_text_stream_transport.py
backend/app/services/framework_realtime_text_stream_adapter.py
backend/tests/test_framework_realtime_text_stream_adapter.py
backend/tests/test_temporary_lifecycle_config.py
docs/v300_rt4_framework_public_streaming_adapter.md
scripts/check_v300_rt4_framework_public_streaming_adapter.py
```

## Tests

Focused candidate tests cover:

```text
fake root-public ask_stream chunks to SSE
input text not echoed publicly
public interrupt requested on cancel
hard_cancel_supported=false
safe failure when configured FW root is missing
config gate default-off and explicit-on
existing RT-4b/c stream and transport regressions
```

Candidate acceptance remains pending operator verification.
