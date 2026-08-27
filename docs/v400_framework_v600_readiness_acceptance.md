# DRC-V4-1 FW v6.0.0 Readiness Acceptance

Status: IMPLEMENTED / AWAITING_REVIEW

## Decision

Required aggregate decision: **PARTIAL_READY**

## Framework v6.0.0 Provenance

```text
Framework release: v6.0.0
Framework annotated tag target: 61e15f62d1ecc5faee016abae82200f8de56c5dd
Framework official ZIP: ai-character-framework_v6.0.0.zip
Framework official ZIP SHA-256: 6b303dba53830dc9bd65ec881bac6f498dbf80f0d0adf1385cea728a86e066f2
Framework root-public inventory: 127 names / frozen
```

```text
Unified RealtimeSession       PARTIAL_READY
Typed lifecycle events        READY
Interrupt/cancellation        READY
TTS queue/flush/invalidation  READY
Stale/late result rejection   READY
Capability snapshot           READY
Voice-input streaming         PARTIAL_READY
Backpressure                  READY
Motion lifecycle              PARTIAL_READY
Recovery/reset                PARTIAL_READY
Safe diagnostics              READY
Aggregate                     PARTIAL_READY
```

## Critical Non-Claim

FW v6.0.0 does **not** provide a production real unified
`RealtimeSession.run_turn()` pipeline coordinating real STT -> streaming LLM ->
TTS -> motion.

```text
FW v6.0.0 does NOT provide a production real unified
RealtimeSession.run_turn() pipeline coordinating
real STT -> streaming LLM -> TTS -> motion.
```

The v4 readiness decision therefore remains **PARTIAL_READY**, not READY.

## Preserved Boundaries

```text
DRC v3.0.0 current released version: RELEASED / ACCEPTED / preserved
existing accepted v3 real runtime paths: preserved
existing fixed FW v5.5.0 integration: preserved
root-public-only Framework policy for initial v4 adoption: preserved
DRC-V4-2: NOT_STARTED / NOT_AUTHORIZED
```

## Acceptance Surface

DRC-V4-1 changes only:

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/DRC_v400_goal_checklist_small_commit.md
docs/v400_framework_v600_readiness_acceptance.md
scripts/check_v400_framework_v600_readiness_acceptance.py
```

DRC-V4-1 does not modify Backend runtime/tests, Flutter runtime/tests,
dependencies/lockfiles, version metadata, Framework vendor, `.gitignore`, v3
release records, or private config/evidence.

DRC-V4-1 does not execute provider/network, microphone, real STT/LLM/TTS,
playback, VTube Studio, or real motion.

## Next Step Boundary

DRC-V4-2 remains **NOT_STARTED / NOT_AUTHORIZED**. It must not be reported as
implemented, accepted, committed, pushed, or released by this readiness sync.

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
