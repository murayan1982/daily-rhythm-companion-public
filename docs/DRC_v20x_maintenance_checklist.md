# Daily Rhythm Companion v2.0.x maintenance checklist

Updated: 2026-07-22
Status: IN_PROGRESS
Current small commit: M-1
Expected first patch release: v2.0.1

## Source-of-truth rule

This file is the detailed source of truth for v2.0.x maintenance. `tasklist.md` is the concise operator index and `roadmap.md` defines version direction.

The completed v2.0.0 checklist remains historical and must not be edited into a post-release checklist:

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
GitHub Release / annotated tag: DRC_v2.0.0
```

## Progress rule

```text
- Only one small commit is CURRENT at a time.
- A task remains NOT_COMPLETED until its files, checks, and operator review pass.
- Later tasks remain PLANNED and must not be marked complete early.
- A guarded boundary is not counted as real runtime implementation.
- A source-tree check is not counted as configured real execution evidence.
```

## Immutable baseline

```text
v2.0.0 status: RELEASED
fixed ZIP: DailyRhythmCompanion_20260722_180426.zip
SHA-256: b32c7b8a64842480898fcc86ca7838625efb712f1429ab9fe7b33a4001ddc0c1
post-publication SHA-256 re-verification: completed
```

The published v2.0.0 tag and release asset are not edit targets.

---

# M-1 — Establish post-v2.0.0 maintenance baseline

Status: CURRENT / NOT_COMPLETED
Commit title:

```text
docs: establish post-v2.0.0 maintenance baseline
```

## Purpose

```text
- Synchronize current status to v2.0.0 RELEASED.
- Establish this v2.0.x checklist without rewriting the v2.0.0 checklist.
- Separate active maintenance checks from historical release-evidence validators.
- Record Public source and Private operator-environment boundaries.
- Keep all runtime behavior unchanged.
```

## Change surface

```text
README.md
roadmap.md
tasklist.md
scripts/README.md
docs/post_v200_release_baseline.md
docs/DRC_v20x_maintenance_checklist.md
docs/public_private_development_policy.md
scripts/check_v20x_maintenance_baseline.py
```

## Explicit non-change surface

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
backend runtime files
Flutter runtime files
provider and OAuth implementation
health, LLM, TTS, STT, and motion execution paths
persistence schema
```

## Completion requirements

```text
- README, roadmap, root task list, and scripts README identify v2.0.0 as RELEASED.
- This file is linked as the v2.0.x detailed source of truth.
- The post-release baseline and Public/Private policy documents exist.
- M-2 through M-9 remain PLANNED.
- Historical v2.0.0 checklist and release-note normalized content hashes remain unchanged.
- python -m compileall -q backend scripts passes.
- python scripts\check_v20x_maintenance_baseline.py passes.
- The operator reviews the diff and approves the small commit.
```

M-1 must remain `CURRENT / NOT_COMPLETED` until the final operator approval and commit.

---

# Planned queue

## M-2 — Align application version metadata

Status: PLANNED

```text
- Inventory backend, Flutter, Web, and user-visible version surfaces.
- Define the patch version without duplicating conflicting constants.
- Add focused version-metadata regression tests.
```

## M-3 — Add backend mock-safe regression foundation

Status: PLANNED

```text
- Introduce a normal pytest layout for core mock-safe behavior.
- Cover health, characters, sleep, advice, and DailyRecord basics.
- Keep credentials and real integrations optional.
```

## M-4 — Cover Framework fallback and voice artifact safety

Status: PLANNED

```text
- Cover framework success/fallback source labels.
- Cover opaque voice artifact lookup and unsafe-path rejection.
- Keep real provider execution outside default tests.
```

## M-5 — Bound temporary chat sessions and TTS artifacts

Status: PLANNED

```text
- Define capacity and expiry behavior.
- Add deterministic cleanup tests.
- Preserve current API compatibility where possible.
```

## M-6 — Make Web CORS origins configurable

Status: PLANNED

```text
- Preserve a documented local-demo default.
- Allow explicit origin restrictions.
- Add configuration and API-boundary tests.
```

## M-7 — Clarify Fitbit current-state contract

Status: PLANNED

```text
- Inventory real, legacy, stub, unavailable, and migration wording.
- Do not claim real-use acceptance before explicit operator verification.
- Define the handoff into the v2.1.0 Fitbit feature scope.
```

## M-8 — Add aggregate maintenance readiness

Status: PLANNED

```text
- Aggregate the accepted v2.0.x regression surface.
- Keep historical release evidence separate.
- Define patch-release entry conditions.
```

## M-9 — Patch release

Status: PLANNED

```text
- Freeze accepted patch scope.
- Build one fixed ZIP from final committed Public source.
- Verify the same ZIP and publish a new patch tag and GitHub Release.
- Do not replace DRC_v2.0.0 assets.
```

---

# Future-version boundary

v2.1.0 is planned for the real wearable daily loop led by Fitbit completion. v3.0.0 is reserved for realtime multimodal work such as real STT, microphone capture, interruption/cancel, and Live2D/VTS execution. These are not v2.0.x completion requirements.
