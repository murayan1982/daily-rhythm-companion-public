# Daily Rhythm Companion v3.0.0 RT-6a character-motion mapping readiness

Updated: 2026-08-01

## Status

```text
RT-5: COMPLETED / ACCEPTED
RT-5f: COMPLETED / ACCEPTED
RT-5f4 acceptance sync: COMPLETED / ACCEPTED / PUSHED
RT-6: CURRENT / NOT_COMPLETED
RT-6a: COMPLETED / ACCEPTED / PUSHED
RT-6a implementation baseline: ca1bd17ed32aba1e6b7d4dfd4f8eea3f10652ef7
RT-6a implementation commit: cbcb218aa54d286da7515a01e899121b22d8f3fc
RT-6a acceptance-sync commit/push: NOT_AUTHORIZED
RT-6b: NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
RT-6c through RT-6f: NOT_STARTED / NOT_AUTHORIZED
RT-7: BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
FW v5.4.0 HEAD/tag: d313eb6acb643103fe25988720ebee5976a04f78
```

## Accepted result

RT-6a accepted the exact seven-file documentation/static-gate inventory and
child split at implementation commit `cbcb218aa54d286da7515a01e899121b22d8f3fc`. Acceptance passed with the
normal dedicated gate against the real DRC/FW checkouts, Backend full
regression, Flutter analyze/full regression, exact-surface and privacy review,
explicit commit approval, push, and clean-tree verification.

```text
compileall: PASS
dedicated RT-6a gate: PASS
Backend full tests: 204 passed
Backend dependency warnings: 3
Flutter analyze: No issues found
Flutter full tests: 411 passed
exact seven-file review: PASS
changed-content privacy scan: PASS
git diff --check: PASS
explicit operator approval: ACCEPTED
implementation commit/push: COMPLETED
DRC post-push clean: true
FW clean: true
```

The three Backend warnings came from installed dependency deprecations and did
not fail the regression suite. RT-6a changed no runtime or dependency.

## Accepted DRC current behavior

The Backend exposes `GET /demo/motion/status` and `POST /demo/motion`. Its
application-owned vocabulary remains:

```text
greeting
thinking
happy
tired_supportive
speaking
idle
```

The request boundary remains metadata-only:

```text
accepted: false
request_state: not_started
motion_sent: false
vts_connection_used: false
```

It does not import FW motion implementation modules, connect to VTube Studio,
load a Live2D runtime, read a token, or send an expression/motion command.

Flutter continues to provide static mood/advice/fallback character
presentation with activity states:

```text
idle
loading
speaking
```

`VoiceOutputPlaybackPhase.playing` maps to static `speaking` presentation. It
is not an FW motion event or animation command. No realtime
lifecycle-to-motion mapper, motion request/result model, motion client,
ChangeNotifier motion controller, stale request handling, or HomeScreen motion
session ownership was added by RT-6a.

## Accepted FW v5.4.0 boundary

FW v5.4.0 exports the root-public provider-neutral motion types and factory:

```text
MotionAdapterStatus
MotionCapability
MotionErrorCode
MotionEventType
MotionIntent
MotionOutcome
MotionRequest
MotionResult
MotionState
MotionSession
MotionSessionInfo
create_motion_session
```

The mock adapter is local and credential-free. Real adapter support remains
false and real Live2D/VTS execution remains typed not implemented. The public
mock session opens no VTS WebSocket, reads no token, loads no private model or
Live2D runtime, and imports no provider SDK.

## Accepted readiness decision

```text
READY_FOR_RT6_APP_OWNED_MOCK_SAFE_MAPPING_WORK
BLOCKED_FOR_REAL_LIVE2D_VTS_EXECUTION
```

DRC may proceed only through separately reviewed small commits using app-owned
provider-neutral contracts and, later, the FW root-public mock session. Direct
imports from `framework.motion`, `framework.motion_session`, provider modules,
VTS libraries, or internal adapters remain prohibited.

## Accepted RT-6 split

```text
RT-6a  COMPLETED / ACCEPTED / PUSHED
       current behavior inventory, readiness, and exact split
RT-6b  NOT_STARTED / READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED
       app-owned provider-neutral motion mapping contract
RT-6c  NOT_STARTED / NOT_AUTHORIZED
       guarded FW root-public mock motion-session adapter
RT-6d  NOT_STARTED / NOT_AUTHORIZED
       Flutter motion presentation model/client/controller
RT-6e  NOT_STARTED / NOT_AUTHORIZED
       default-off HomeScreen character-motion wiring
RT-6f  NOT_STARTED / NOT_AUTHORIZED
       configured local mock-motion presentation acceptance
RT-7   BLOCKED_REAL_LIVE2D_VTS_ADAPTER_NOT_IMPLEMENTED
```

RT-6b must be pure, deterministic, provider-neutral, bounded, and fake-only.
It may map accepted DRC lifecycle facts such as listening, transcribing,
thinking, responding, TTS preparing/speaking, interruption, completion,
failure, and idle to app-owned normalized motion requests. It must call no FW
session, route, network, VTS, Live2D, audio, or provider. A concrete mapping
table is not authorized until RT-6b exact contract review is accepted.

## Exact acceptance-sync change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v300_goal_checklist_small_commit.md
docs/v300_rt6a_character_motion_mapping_readiness.md
scripts/check_v300_rt6a_character_motion_mapping_readiness.py
```

The acceptance sync changes only these seven documentation/static-gate files.
The implementation commit `cbcb218aa54d286da7515a01e899121b22d8f3fc` also changed exactly these same seven
files.

## Non-actions and non-claims

The RT-6a implementation and acceptance sync change no Backend runtime,
Flutter runtime, existing test, dependency, lockfile, platform manifest,
environment profile, API route, asset, version, release metadata, Framework
source, provider client, network execution, VTS WebSocket, Live2D runtime,
token/credential access, private model path, microphone/audio, STT, LLM, TTS,
screenshot, raw log, transcript, provider payload, or private operator
evidence.

RT-6a does not claim realtime character animation, real VTS/Live2D execution,
provider motion execution, smartphone/PC motion acceptance, or v3.0.0 release
readiness. Mock-safe readiness does not prove real adapter behavior.

## Next action

```text
Review the exact RT-6b contract separately.
RT-6b implementation remains NOT_AUTHORIZED.
RT-6c through RT-6f remain NOT_AUTHORIZED.
RT-7 remains blocked.
```
