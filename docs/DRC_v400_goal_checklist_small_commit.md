# DRC v4.0.0 Goal Checklist

Status: DRC-V4-1 IMPLEMENTED / AWAITING_REVIEW

## Current State

```text
current released version: v3.0.0 RELEASED / ACCEPTED
current released metadata: Backend 3.0.0 / Flutter 3.0.0+4 RELEASED
current small commit: DRC-V4-1 FW v6.0.0 readiness acceptance sync
current implementation baseline: 6311864237d8f5d86db49c14d17ca083e1af5c03
current implementation state: IMPLEMENTED / AWAITING_REVIEW
current implementation commit: none
DRC-V4-1 aggregate decision: PARTIAL_READY
DRC-V4-2: NOT_STARTED / NOT_AUTHORIZED
commit / push: NOT_AUTHORIZED
```

## Framework v6.0.0 Provenance

```text
Framework release: v6.0.0
Framework annotated tag target: 61e15f62d1ecc5faee016abae82200f8de56c5dd
Framework official ZIP: ai-character-framework_v6.0.0.zip
Framework official ZIP SHA-256: 6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2
Framework root-public inventory: 127 names / frozen
```

## Scope

DRC-V4-1 records the public acceptance sync for AI Character Framework v6.0.0
readiness. It is a documentation and static-gate update only.

Allowed files:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
docs/v400_framework_v600_readiness_acceptance.md
scripts/check_v400_framework_v600_readiness_acceptance.py
```

Out of scope:

```text
backend runtime/tests
Flutter runtime/tests
dependencies/lockfiles
version metadata
Framework vendor
.gitignore
v3 release records
private config/evidence
```

Forbidden execution:

```text
provider/network
microphone
real STT/LLM/TTS
playback
VTube Studio / real motion
```

## Readiness Decision

Required aggregate decision: **PARTIAL_READY**

DRC may begin v4 planning against FW v6.0.0 only through root-public Framework
contracts and only where the relevant capability is classified READY or
PARTIAL_READY below. The existing accepted v3 real runtime paths and fixed FW
v5.5.0 integration remain preserved.

DRC-V4-2 remains **NOT_STARTED / NOT_AUTHORIZED**.

Detailed matrix:
`docs/v400_framework_v600_readiness_acceptance.md`.

## DRC-V4-2 Future Boundary

DRC-V4-2 is still **NOT_STARTED / NOT_AUTHORIZED**.

Proposed future exact-review scope:

```text
provider-free FW v6 RealtimeSession adapter first
session identity
turn identity
generation identity
canonical event ordering
exactly-once terminal
cooperative interrupt results
stale-result rejection
truthful capability snapshot
safe diagnostics
initial FW imports from root framework only
explicit FW submodule adoption requires a separate exact review
existing accepted v3 real adapters remain retained
removal of v3 real adapters is NOT_AUTHORIZED
real unified RealtimeSession remains NOT_CLAIMED / NOT_AVAILABLE
```

DRC-owned responsibilities outside FW ownership:

```text
Flutter microphone permission / foreground lifecycle
product UX and explicit opt-in policy
DailyRecord / sleep / mood / character context
host-local playback final control
presentation state
persistence
```
