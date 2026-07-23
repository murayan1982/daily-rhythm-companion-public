# Daily Rhythm Companion v2.0.x aggregate maintenance readiness

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED
Small commit: M-8

## Purpose

M-8 provides one credential-free maintenance command for the accepted M-1 through M-7 regression surface. It keeps normal current-main maintenance checks separate from historical v2.0.0 release-evidence validators and defines the conditions that must be satisfied before M-9 patch-release work may begin.

## Aggregate command

Source-tree and backend checks:

```powershell
python scripts\check_v20x_maintenance_readiness.py
```

Local full developer gate, including Flutter:

```powershell
python scripts\check_v20x_maintenance_readiness.py --with-flutter
```

The default command runs:

```text
- python -m compileall -q backend scripts
- the accepted M-7 terminal maintenance check chain, which reaches M-1 through M-6
- python -m pytest -q backend/tests
- immutable v2.0.0 normalized-content hash verification
- backend/local_data non-modification verification
```

`--with-flutter` additionally runs `flutter test` from `app/`. Flutter is optional only for the portable default invocation; it remains required for M-8 operator acceptance.

## Separation from historical release evidence

The M-8 aggregate does not:

```text
- invoke v2.0.0 Web evidence, screenshot, fixed-ZIP, final-release, or publication validators
- build, rebuild, inspect, or modify a release ZIP
- create or update a tag or GitHub Release
- call real LLM, TTS, STT, health, OAuth, or motion providers
- read private operator evidence or credentials
```

Historical v2.0.0 validators remain available for their released evidence surface, but they are not children of the current-main maintenance aggregate.

## Patch-release entry contract

M-9 may become CURRENT only after all of the following are true:

```text
1. M-1 through M-8 are COMPLETED / ACCEPTED in docs/DRC_v20x_maintenance_checklist.md.
2. The final M-8 aggregate passes from the intended committed Public source state.
3. backend pytest and Flutter test pass without credentials or real-provider execution.
4. The normalized hashes of docs/DRC_v200_goal_checklist_small_commit.md and release_notes/v2.0.0.md remain unchanged.
5. The accepted patch scope is frozen and no unrelated working-tree changes are included.
6. v2.0.1 has not already been represented by a conflicting tag, release, or rebuilt asset.
7. M-9 builds one fixed ZIP from the final committed Public source, then verifies that same ZIP without rebuilding it.
8. The DRC_v2.0.0 tag and published v2.0.0 release asset remain untouched.
```

M-8 defines and verifies this entry contract. It does not itself declare the repository release-ready, create v2.0.1, or perform M-9.

## Mock-safe guarantees

```text
- no credentials are required
- no network or provider execution is required
- normal checks do not import private operator evidence
- backend/local_data is not created or modified
- existing API routes, response models, and Flutter behavior are unchanged
```

## Acceptance state

M-8 was accepted on 2026-07-23 after compileall, the aggregate check with `--with-flutter`, 38 backend pytest tests, 43 Flutter tests, historical-record and `backend/local_data` protection checks, diff review, and explicit operator approval passed. M-9 remains PLANNED, and v2.0.1 has not been released.
