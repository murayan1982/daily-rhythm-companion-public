# Daily Rhythm Companion v3.0.0 RT-6c Framework mock motion-session adapter

## Accepted state

```text
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6b: COMPLETED / ACCEPTED / PUSHED
RT-6c: COMPLETED / ACCEPTED / PUSHED
implementation baseline: 9442f511f9e41d18f64a65cf7fa44a375e7a67ce
implementation commit: f929e8faa65a817f1ba4fed82b729438b73dbfab
implementation surface: exact 10 files
acceptance-sync surface: exact 7 documentation/static-gate files
RT-6d: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-6e through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
acceptance-sync commit/push: NOT_AUTHORIZED
```

## Framework baseline record

```text
Framework baseline version: 5.4.0
Framework canonical reference commit: d313eb6acb643103fe25988720ebee5976a04f78
Framework local source mode: external-vendored-snapshot
Framework vendor Git identity required: false
```

The local Framework copy is intentionally outside DRC Git history. RT-6c
records the version and canonical reference commit used by the small-commit
contract, while normal verification checks the required root-public symbols
and representative local mock execution. It does not require vendor Git HEAD,
working-tree clean status, or full-source identity.

## Accepted exact implementation surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6c_framework_mock_motion_session_adapter.md
scripts/check_v300_rt6c_framework_mock_motion_session_adapter.py
backend/app/models/character_motion_adapter.py
backend/app/services/framework_mock_motion_session_adapter.py
backend/tests/test_framework_mock_motion_session_adapter.py
```

```text
documentation/static gate: 7 files
Backend runtime: 2 files
Backend focused test: 1 file
total: exact 10 files
```

The acceptance-state sync changes only the seven documentation/static-gate
files. The accepted two Backend runtime files and focused test remain unchanged.

## Accepted boundary

RT-6c provides a DRC-owned, default-off adapter from an accepted RT-6b
`CharacterMotionPlan` to a newly created FW root-public mock motion session.
The adapter constructor defaults to `enabled=False`; disabled and ignored plans
return before FW import. A configured execution dynamically imports only the
root `framework` package and obtains:

```text
create_motion_session
MotionRequest
MotionIntent
```

It creates a fresh session with fixed arguments:

```python
create_motion_session(
    project_root=str(framework_root),
    adapter="mock",
    real_adapter_enabled=False,
    allow_provider_execution=False,
    public_metadata={
        "boundary": "drc_rt6c",
        "mode": "mock",
    },
)
```

The adapter performs one capability preflight, accepts only the released
mock-safe capability, converts the five bounded RT-6b command intents through
FW root-public requests, applies at most three commands synchronously in order,
stops at the first non-completed result, and closes its owned session from
`finally`.

## Accepted result safety

The DRC-owned result retains only bounded values:

```text
aggregate status
source fact and cue
bounded source event/session/turn/character IDs
commands requested/completed
maximum three normalized command results
maximum twelve event type strings
Framework import/session lifecycle booleans
fixed mock/real/provider/network booleans
bounded reason code and fixed safe message
```

It does not retain:

```text
FW session or request IDs
raw FW request/result/session/capability/event objects
arbitrary metadata mappings
raw exception text
filesystem paths
provider payloads
tokens or credentials
screenshots, recordings, logs, or operator evidence
```

The adapter exposes no route and has no configuration enablement or normal
runtime caller. It changes no accepted RT-6b model/mapper/test, existing
motion-demo/realtime route, Flutter source, Framework source, dependency,
lockfile, platform file, asset, version, or release metadata.

## Accepted verification

```text
compileall: PASS
dedicated normal-mode gate: PASS
external vendor root-public contract/mock smoke: PASS
focused Backend: 38 passed
Backend full: 279 passed
Backend dependency warnings: 3
Flutter analyze: No issues found
Flutter full: 411 passed
exact ten-file surface: PASS
changed-content privacy review: PASS
CRLF-aware git diff --check: PASS
explicit commit approval: ACCEPTED
implementation commit/push: COMPLETED
DRC post-push working tree: clean
```

The warnings are installed dependency deprecations and did not fail the suite.
The accepted run made no provider call, network connection, VTS connection, or
Live2D runtime load and did not read private credentials, paths, payloads, or
evidence.

## Historical acceptance-sync gate markers

```text
v300_rt6c_status: completed-accepted-pushed
v300_rt6c_exact_acceptance_sync_surface: True
v300_rt6c_acceptance_sync_file_count: 7
v300_rt6c_implementation_commit: f929e8faa65a817f1ba4fed82b729438b73dbfab
v300_rt6c_implementation_surface: 10
v300_rt6c_backend_runtime_file_count: 2
v300_rt6c_backend_test_file_count: 1
v300_rt6c_focused_backend_passed: 38
v300_rt6c_backend_full_passed: 279
v300_rt6c_backend_warning_count: 3
v300_rt6c_flutter_analyze_passed: True
v300_rt6c_flutter_full_passed: 411
v300_rt6c_framework_version: 5.4.0
v300_rt6c_framework_reference_commit: d313eb6acb643103fe25988720ebee5976a04f78
v300_rt6c_framework_source_mode: external-vendored-snapshot
v300_rt6c_framework_git_identity_required: False
v300_rt6c_framework_root_public_contract_passed: True
v300_rt6c_framework_mock_smoke_passed: True
v300_rt6c_real_fw_mock_smoke_passed: True
v300_rt6c_runtime_changed_by_acceptance_sync: False
v300_rt6c_backend_runtime_changed_by_acceptance_sync: False
v300_rt6c_backend_tests_changed_by_acceptance_sync: False
v300_rt6c_api_routes_changed: False
v300_rt6c_config_changed: False
v300_rt6c_flutter_changed: False
v300_rt6c_framework_changed: False
v300_rt6c_dependencies_changed: False
v300_rt6c_network_execution: False
v300_rt6c_provider_execution: False
v300_rt6c_vts_connection_used: False
v300_rt6c_live2d_runtime_loaded: False
v300_rt6_status: current-not-completed
v300_rt6d_status: ready-for-exact-contract-review-not-authorized
v300_rt6d_implementation_authorized: False
v300_rt7_real_adapter_blocked: True
v300_rt6c_acceptance_sync_commit_push_authorized: False
```

## Next action

```text
Review the exact RT-6d contract separately.
RT-6d implementation remains NOT_AUTHORIZED.
RT-6e through RT-6f remain NOT_STARTED / NOT_AUTHORIZED.
RT-7 remains blocked on a real Live2D/VTS adapter.
```
