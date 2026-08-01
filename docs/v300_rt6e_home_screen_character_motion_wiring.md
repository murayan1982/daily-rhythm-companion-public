# Daily Rhythm Companion v3.0.0 RT-6e HomeScreen character-motion wiring

Updated: 2026-08-01

## Candidate state

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6c: COMPLETED / ACCEPTED / PUSHED
RT-6d: COMPLETED / ACCEPTED / PUSHED
RT-6e: IMPLEMENTED / AWAITING_REVIEW
implementation baseline: 8d69b539e974ba71fde5d9b15dd951d0c670b7ff
implementation commit: none
implementation surface: exact 10 files
RT-6f: NOT_STARTED / BLOCKED_PENDING_RT6E_ACCEPTANCE / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
commit/push: NOT_AUTHORIZED
```

## Purpose

RT-6e adds default-off HomeScreen ownership and visible presentation for the
accepted RT-6d Flutter provider-neutral character-motion controller. It does
not configure a transport in `main.dart`. Normal application startup therefore
remains unconfigured and performs no motion request.

The candidate follows the accepted HomeScreen integration patterns used by
RT-4f2 and RT-5d: an optional injected factory, one owned listener, session-local
opt-in that defaults off, explicit manual action, safe visible state, and
listener removal before owned controller disposal.

## Exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6e_home_screen_character_motion_wiring.md
scripts/check_v300_rt6e_home_screen_character_motion_wiring.py
app/lib/screens/home_screen.dart
app/lib/widgets/character_motion_presentation_panel.dart
app/test/character_motion_home_screen_test.dart
```

```text
documentation/static gate: 7 files
Flutter runtime: 2 files
Flutter focused test: 1 file
total: exact 10 files
```

## Optional HomeScreen ownership

`HomeScreen` accepts:

```dart
CharacterMotionPresentationController Function()?
    characterMotionPresentationControllerFactory
```

The factory is invoked at most once from `initState()`.

```text
factory absent: unconfigured
factory throws: configuration_failed
factory returns controller: configured with opt-in off
```

HomeScreen registers one listener. During disposal it marks the screen as
disposing, removes that listener, and disposes the owned controller once. The
RT-6d controller's operation generation rejects late completion after reset or
dispose.

## Default-off and explicit-action boundary

The session-local opt-in starts false and is not persisted. Toggling it on does
not apply a request. Initial data loading, character selection, advice creation,
text streaming, voice capture, TTS playback, interruption, and barge-in do not
automatically apply motion.

A transport call is possible only after both explicit actions:

```text
1. Enable character motion presentation
2. Apply selected lifecycle fact
```

One apply press creates at most one request. There is no queueing, coalescing,
automatic retry, active replacement, or lifecycle subscription. The controller
disables duplicate apply while one request is active.

Opting out calls only local `controller.reset()`. It invalidates a delayed
completion and returns the visible state to idle. It sends no stop-motion,
reset-expression, Framework, provider, or network request.

The explicit Reset presentation action is also local-only and performs zero
transport calls.

## Manual request contract

The UI exposes the accepted bounded RT-6d lifecycle vocabulary:

```text
idle
listening
transcribing
thinking
responding
tts_preparing
speaking
motion_active
interrupted
completed
failed
closed
unavailable
unknown
```

The initial selection is `idle`. An explicit apply creates:

```dart
CharacterMotionPresentationRequest(
  sourceFact: selectedFact,
  sourceEventType: "home_screen_manual_motion",
  characterId: selectedCharacter?.characterId,
)
```

The HomeScreen request does not set a source session ID or source turn ID.

## Visible panel boundary

`app/lib/widgets/character_motion_presentation_panel.dart` displays only:

```text
configuration
session-local opt-in
selected lifecycle fact
presentation phase
execution status
cue
commands requested/completed
number of normalized event types
fixed adapter and real/provider/network safety booleans
bounded reason code
bounded safe message
```

It does not display:

```text
source event/session/turn/character IDs
Framework request/session/result IDs
raw command results or command payloads
event type strings
raw response JSON or exception text
filesystem paths
credentials/tokens
provider payloads
private logs or operator evidence
```

The panel states that it is normalized mock motion presentation only. The
repository character image remains static and no Live2D or VTube Studio
animation is executed.

## Static character separation

RT-6e does not modify:

```text
app/lib/models/character_display_presentation.dart
app/lib/widgets/character_display_card.dart
```

The accepted static character card continues to expose its existing
idle/loading/speaking activity and `静的表示` marker. RT-6e does not reinterpret
those static states as Framework motion events and does not claim that the
character image moves.

## Configuration boundary

RT-6e does not modify `app/lib/main.dart`. It adds no configured transport,
Backend route, HTTP client, Framework import, provider client, VTS connection,
Live2D runtime, token read, dependency, environment flag, or platform change.

Configured local mock transport assembly, normal `main.dart` wiring, and
operator-visible mock presentation acceptance remain RT-6f work.

## Focused test contract

`app/test/character_motion_home_screen_test.dart` uses fake/in-memory transport
only and covers:

```text
normal unconfigured state
factory called once
factory failure normalization
configured default-off state
opt-in alone calls no transport
all accepted lifecycle facts available
one explicit bounded request
fixed source event type and no session/turn IDs
completed/ignored/disabled/unavailable/failed presentation
applying state and duplicate apply prevention
local reset without another transport call
opt-out stale-completion invalidation
dispose stale-completion invalidation and one disposal
raw/private ID, command, event, response, and exception non-display
static-character baseline preservation
no automatic apply during initial loading
```

## Exact non-actions and non-claims

RT-6e changes no Backend, Framework/vendor source, API route, dependency,
lockfile, platform manifest, asset, environment profile, version, release
metadata, existing test, RT-6d model/client/controller, existing motion demo,
or configured runtime.

It does not claim Backend-to-Flutter motion transport, Framework execution,
provider execution, real adapter support, network execution, VTS/Live2D
connection, animated character output, smartphone/PC motion acceptance, or
v3.0.0 release readiness.

## Verification target

```text
compileall: PASS
dedicated RT-6e gate: PASS
Backend full: 279 passed with 3 known dependency warnings
Dart format: PASS
Flutter analyze: PASS
focused Flutter tests: 16 passed
Flutter full regression: 468 passed
exact ten-file review: PASS
privacy review: PASS
CRLF-aware git diff --check: PASS
```

## Candidate gate markers

```text
v300_rt6e_status: implemented-awaiting-review
v300_rt6e_exact_change_surface: True
v300_rt6e_change_file_count: 10
v300_rt6e_flutter_runtime_file_count: 2
v300_rt6e_flutter_test_file_count: 1
v300_rt6e_focused_flutter_defined: 16
v300_rt6e_flutter_full_expected: 468
v300_rt6e_main_changed: False
v300_rt6e_rt6d_runtime_changed: False
v300_rt6e_character_display_changed: False
v300_rt6e_backend_changed: False
v300_rt6e_existing_tests_changed: False
v300_rt6e_dependencies_changed: False
v300_rt6e_framework_changed: False
v300_rt6e_vendor_changed: False
v300_rt6e_controller_factory_optional: True
v300_rt6e_default_unconfigured: True
v300_rt6e_default_opt_in: False
v300_rt6e_opt_in_persisted: False
v300_rt6e_opt_in_triggers_transport: False
v300_rt6e_explicit_apply_only: True
v300_rt6e_apply_transport_limit: 1
v300_rt6e_automatic_lifecycle_subscription: False
v300_rt6e_queueing: False
v300_rt6e_automatic_retry: False
v300_rt6e_reset_triggers_transport: False
v300_rt6e_opt_out_invalidates_stale_result: True
v300_rt6e_dispose_invalidates_stale_result: True
v300_rt6e_source_event_type_fixed: home_screen_manual_motion
v300_rt6e_source_session_id_used: False
v300_rt6e_source_turn_id_used: False
v300_rt6e_raw_result_exposed: False
v300_rt6e_raw_exception_exposed: False
v300_rt6e_private_ids_exposed: False
v300_rt6e_real_http_execution: False
v300_rt6e_framework_execution: False
v300_rt6e_provider_execution: False
v300_rt6e_network_execution: False
v300_rt6e_live2d_animation_claimed: False
v300_rt6f_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6e_commit_push_authorized: False
```

## Next action

```text
Verify and review the exact RT-6e candidate.
Do not commit or push without explicit approval.
RT-6f remains blocked pending RT-6e acceptance.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
