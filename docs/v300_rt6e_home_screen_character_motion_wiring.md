# Daily Rhythm Companion v3.0.0 RT-6e HomeScreen character-motion wiring

Updated: 2026-08-01

## Accepted state

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6c: COMPLETED / ACCEPTED / PUSHED
RT-6d: COMPLETED / ACCEPTED / PUSHED
RT-6e: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 8d69b539e974ba71fde5d9b15dd951d0c670b7ff
implementation commit: 13343017738d0bb5fe23583467856233d62196fb
implementation surface: exact 10 files
acceptance-sync surface: exact 7 documentation/static-gate files
RT-6f: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
acceptance-sync commit/push: NOT_AUTHORIZED
```

## Framework baseline record

```text
Framework baseline version: 5.4.0
Framework canonical reference commit: d313eb6acb643103fe25988720ebee5976a04f78
Framework local source mode: external-vendored-snapshot
Framework execution in RT-6e: false
Framework vendor Git identity required: false
```

## Accepted exact implementation surface

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

The acceptance-state sync changes only the seven documentation/static-gate
files. The accepted two Flutter runtime files and one focused test file remain
unchanged.

## Accepted ownership and default-off boundary

HomeScreen accepts an optional
`CharacterMotionPresentationController Function()?` factory, invokes it at
most once, owns one listener/controller lifecycle, removes the listener before
disposal, and normalizes factory failure to `configuration_failed`.

Normal `main.dart` remains unchanged and does not inject the factory. Regular
startup is therefore unconfigured. A configured test instance starts with a
session-local, non-persistent opt-in set to false. Opt-in alone performs zero
transport calls.

## Accepted explicit-action boundary

A request can occur only after explicit opt-in and one explicit Apply action.
Each Apply press creates at most one bounded request. There is no automatic
lifecycle subscription, queueing, coalescing, active replacement, or retry.
Initial loading, character selection, advice, streaming, voice capture, TTS,
interruption, and barge-in perform zero automatic motion requests.

The request uses fixed `home_screen_manual_motion`, the selected bounded
lifecycle fact, and the selected character ID. It supplies no source session ID
or source turn ID. Reset and opt-out call only local controller reset, perform
zero transport calls, and invalidate delayed completion. Disposal also
invalidates delayed completion.

## Accepted visible panel boundary

The panel displays only configuration, opt-in, selected fact, presentation
phase, execution status/cue, aggregate command counts, normalized event-type
count, fixed adapter/safety booleans, bounded reason code, and bounded safe
message.

It does not display source event/session/turn/character IDs, Framework IDs,
raw command results, command payloads, event strings, response JSON, raw
exceptions, filesystem paths, credentials, provider payloads, private logs, or
operator evidence.

The panel explicitly states that this is normalized mock motion state only.
The repository character image remains static and no Live2D/VTS animation is
executed or claimed.

## Accepted focused tests

The focused file defines 16 widget tests covering normal unconfigured state,
one factory call, factory failure, configured default-off state, zero-call
opt-in, complete lifecycle-fact availability, one bounded manual request,
duplicate apply prevention, completed/ignored/disabled/unavailable/failed
presentation, local reset, stale completion after opt-out/dispose, one disposal,
privacy non-display, static-character preservation, and zero automatic apply.

The initial dropdown assertion used a nonexistent
`DropdownButtonFormField.items` getter. The real checkout corrective replaced
it with a structural inspection of the descendant typed `DropdownButton` and
its public items. The corrective remained inside the accepted focused test
file and passed format, analyze, focused tests, and full regression.

## Exact non-actions and non-claims

RT-6e changes no `main.dart`, RT-6d model/client/controller, existing static
character display files, Backend, Framework/vendor source, API route,
dependency, lockfile, platform manifest, asset, environment profile, version,
release metadata, or existing test.

It does not claim Backend-to-Flutter motion transport, Framework/provider
execution, real adapter support, network execution, VTS/Live2D connection,
animated character output, smartphone/PC motion acceptance, or v3.0.0 release
readiness. Configured local mock transport wiring and operator-visible mock
presentation acceptance remain RT-6f work.

## Accepted verification

```text
implementation commit: 13343017738d0bb5fe23583467856233d62196fb
implementation pushed: true
compileall: PASS
dedicated RT-6e gate: PASS
Backend full: 279 passed
Backend dependency warnings: 3
Dart format: PASS
Flutter analyze: No issues found
focused Flutter: 16 passed
Flutter full: 468 passed
lifecycle dropdown structural corrective: PASS
exact ten-file review: PASS
changed-content privacy review: PASS
CRLF-aware git diff --check: PASS
explicit operator commit approval: ACCEPTED
post-push DRC working tree: clean
```

## Historical acceptance-sync gate markers

```text
v300_rt6e_status: completed-accepted-pushed
v300_rt6e_exact_acceptance_sync_surface: True
v300_rt6e_acceptance_sync_file_count: 7
v300_rt6e_implementation_baseline: 8d69b539e974ba71fde5d9b15dd951d0c670b7ff
v300_rt6e_implementation_commit: 13343017738d0bb5fe23583467856233d62196fb
v300_rt6e_implementation_surface: 10
v300_rt6e_flutter_runtime_file_count: 2
v300_rt6e_flutter_test_file_count: 1
v300_rt6e_focused_flutter_passed: 16
v300_rt6e_flutter_full_passed: 468
v300_rt6e_backend_full_passed: 279
v300_rt6e_backend_warning_count: 3
v300_rt6e_dart_format_passed: True
v300_rt6e_flutter_analyze_passed: True
v300_rt6e_lifecycle_dropdown_corrective_passed: True
v300_rt6e_runtime_changed_by_acceptance_sync: False
v300_rt6e_flutter_runtime_changed_by_acceptance_sync: False
v300_rt6e_flutter_tests_changed_by_acceptance_sync: False
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
v300_rt6e_framework_version: 5.4.0
v300_rt6e_framework_reference_commit: d313eb6acb643103fe25988720ebee5976a04f78
v300_rt6e_framework_source_mode: external-vendored-snapshot
v300_rt6e_framework_execution: False
v300_rt6e_provider_execution: False
v300_rt6e_network_execution: False
v300_rt6e_live2d_animation_claimed: False
v300_rt6_status: current-not-completed
v300_rt6f_status: ready-for-exact-contract-review-not-authorized
v300_rt6f_implementation_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6e_acceptance_sync_commit_push_authorized: False
```

## Next action

```text
Review the exact RT-6f contract separately.
RT-6f implementation remains NOT_AUTHORIZED.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
