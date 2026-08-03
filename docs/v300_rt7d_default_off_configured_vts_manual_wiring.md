# Daily Rhythm Companion v3.0.0 RT-7d default-off configured VTS manual wiring

Updated: 2026-08-03

## Candidate state

```text
RT-7: CURRENT / NOT_COMPLETED
RT-7c: COMPLETED / ACCEPTED / PUSHED
RT-7d: IMPLEMENTED / AWAITING_REVIEW
RT-7d baseline: 2a5e3b035bcfdd273a7d056d59af01235e2459f5
RT-7d surface: exact 28 files
RT-7e: NOT_AUTHORIZED
real VTube Studio execution: NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```

## Purpose

RT-7d adds a separately owned, default-off manual route from Flutter to the
accepted RT-7c fixed-vendor Framework v5.5.0 VTS adapter. It does not replace,
modify, or reinterpret the accepted RT-6 mock-motion presentation path.

```text
explicit HomeScreen Apply
→ POST /demo/character-motion/vts/presentation
→ bounded one-command request
→ private Backend configuration loader
→ FrameworkVtsMotionSessionAdapter
→ fixed vendor/ai-character-framework-5.5.0 root-public facade
```

Normal startup, HomeScreen construction, controller construction, local opt-in,
opt-out, reset, and disposal execute no HTTP, Framework, provider, network, or
motion operation.

## Four closed gates

Execution requires all of the following independently:

```text
Flutter compile-time configured runtime enabled
HomeScreen session-local opt-in enabled
Backend adapter enabled
Backend provider execution allowed
```

Runtime availability, model selection, endpoint configuration, Framework
preflight, and public intent capability remain additional fail-closed checks.
RT-7d verification keeps every provider/network/real-motion gate closed.

## Backend request and response

New route:

```text
POST /demo/character-motion/vts/presentation
```

The request schema is
`drc.v3.framework-vts-motion-presentation-request.1` and contains exactly one
command with `order=1`. Allowed intents are `expression`, `emotion`, `gesture`,
`reset_expression`, and optional `stop_motion`. Selector intents carry exactly
their matching value. `speaking_state`, `idle_motion`, `look_at`, lifecycle
facts, session IDs, turn IDs, automatic execution, and command arrays are not
accepted.

The response is the accepted RT-7c
`FrameworkVtsMotionExecutionResult` without an additional wrapper. It contains
only bounded public-safe status, counts, command outcomes, event-type names,
session markers, execution markers, reason code, and safe message. It contains
no endpoint, port, authentication token, hotkey value, private model ID,
provider payload, raw WebSocket payload, private path, Framework internal ID,
or raw exception.

## Private configuration

The tracked example remains blank/default-off:

```text
DRC_RT7_ENABLE_FRAMEWORK_VTS_MOTION=0
DRC_RT7_ALLOW_VTS_PROVIDER_EXECUTION=0
DRC_RT7_VTS_RUNTIME_AVAILABLE=0
DRC_RT7_VTS_MODEL_SELECTED=0
DRC_RT7_VTS_ENDPOINT_HOST=
DRC_RT7_VTS_ENDPOINT_PORT=
DRC_RT7_VTS_AUTHENTICATION_TOKEN=
DRC_RT7_VTS_HOTKEY_BINDINGS_JSON={}
```

The loader bounds raw values, accepts an optional port from 1 through 65535,
accepts a JSON object with at most 32 nonblank string pairs, and converts any
invalid private configuration into a fixed public-safe unavailable result
before Framework import. Private token and hotkey values are excluded from
`AppConfig` representation and from every result, exception, and test output.

## Flutter boundary

The compile-time flag is
`DRC_RT7_ENABLE_CONFIGURED_VTS_MOTION`, default false. The runtime accepts only
an absolute HTTP(S) Backend base URL, sends POST with redirects disabled, uses a
10-second whole-request timeout, and accepts at most 65536 response bytes of
JSON.

HomeScreen owns a session-local opt-in, one intent selector, one bounded value
field for selector intents, explicit Apply, and local Reset. Apply sends at
most one request while idle. No request occurs on startup, factory creation,
controller creation, opt-in, opt-out, reset, or disposal. The currently
selected DRC character ID is passed only as the bounded public character ID.
The panel displays only normalized public-safe values.

## Frozen RT-6 boundary

The existing route remains:

```text
POST /demo/character-motion/presentation
```

It continues to use `CharacterMotionMapper` and
`FrameworkMockMotionSessionAdapter`. RT-7d does not pass RT-6 lifecycle plans to
VTS because RT-6 includes `speaking_state` and `idle_motion`, which RT-7c does
not assume or authorize.

## Exact surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt7d_default_off_configured_vts_manual_wiring.md
scripts/check_v300_rt7d_default_off_configured_vts_manual_wiring.py
backend/.env.example
backend/app/config.py
backend/app/main.py
backend/app/api/framework_vts_motion_presentation.py
backend/app/models/framework_vts_motion_presentation.py
backend/app/services/framework_vts_motion_presentation_service.py
backend/tests/conftest.py
backend/tests/test_framework_vts_motion_configuration.py
backend/tests/test_framework_vts_motion_presentation_api.py
app/lib/main.dart
app/lib/screens/home_screen.dart
app/lib/models/framework_vts_motion_presentation.dart
app/lib/services/framework_vts_motion_presentation_client.dart
app/lib/services/framework_vts_motion_presentation_controller.dart
app/lib/services/configured_framework_vts_motion_presentation_runtime.dart
app/lib/widgets/framework_vts_motion_presentation_panel.dart
app/test/framework_vts_motion_presentation_model_test.dart
app/test/framework_vts_motion_presentation_controller_test.dart
app/test/configured_framework_vts_motion_presentation_runtime_test.dart
app/test/framework_vts_motion_home_screen_test.dart
app/test/main_framework_vts_motion_wiring_widget_test.dart
```

## Protected surface

RT-7c models, adapter, tests, dependency pins, fixed vendor, Framework
development checkout, all RT-6 runtime/models/tests, existing RT-6 Flutter
stack and tests, versions, release records, fixed ZIPs, tags, and GitHub
Releases are unchanged.

## Verification

```text
compileall
RT-7d dedicated gate before and after regression
focused Backend configuration/API tests
Backend full regression
Dart format check
Flutter analyze
five focused Flutter test files
Flutter full regression
exact 28-file review
privacy scan
CRLF-aware diff check
```

Provider execution, network execution, and real VTube Studio execution remain
false throughout RT-7d verification. RT-7e and commit/push require separate
approval.
