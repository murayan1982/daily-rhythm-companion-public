# Post-v2.0.0 release baseline

Updated: 2026-07-22
Status: active maintenance baseline

## Immutable released baseline

```text
Public repository: murayan1982/daily-rhythm-companion-public
Release / annotated tag: DRC_v2.0.0
Release status: RELEASED
Fixed release ZIP: DailyRhythmCompanion_20260722_180426.zip
Fixed release ZIP SHA-256: b32c7b8a64842480898fcc86ca7838625efb712f1429ab9fe7b33a4001ddc0c1
Post-publication SHA-256 re-verification: completed
```

The published tag, source snapshot, release body, and release asset are immutable. Corrections and improvements must use a new commit and a new version.

## Historical completion records

The following files describe the completed v2.0.0 release process and remain historical evidence:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
```

They must not be rewritten to become the active v2.0.x task list. Their pre-build wording reflects the frozen source used to create the final artifact; release completion is established by the published annotated tag, GitHub Release, fixed artifact, and post-publication SHA-256 verification.

## Active maintenance records

```text
docs/DRC_v20x_maintenance_checklist.md
roadmap.md
tasklist.md
```

The maintenance checklist owns detailed small-commit status. `roadmap.md` owns version direction. `tasklist.md` is the concise operator index.

## Capability baseline carried forward from v2.0.0

Accepted and preserved:

```text
- Smartphone Web UI and actual DRC backend path.
- Sleep, mood, character advice, DailyRecord history, and rhythm reports.
- Configured AI Character Framework / LLM answer path with visible fallback state.
- Real TTS output through the released Framework v5 public boundary.
- DRC-owned opaque MP3 handoff.
- Real Google Health sleep normalization and Web display.
- Repository-safe character image intake and Web display.
```

Not accepted as real runtime in v2.0.0:

```text
- Microphone capture and real STT execution.
- Real Live2D / VTube Studio adapter execution.
- Realtime full-duplex voice orchestration or barge-in.
```

These distinctions must remain visible. Guarded or detected capability boundaries do not count as connected real execution.

## M-1 boundary

M-1 changes documentation and one credential-free source-tree check only. It does not change runtime behavior or claim completion of M-2 or later work.
