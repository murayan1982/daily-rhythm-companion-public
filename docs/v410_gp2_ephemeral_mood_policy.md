# DRC v4.1.0 GP-2 Ephemeral Mood Policy Corrective R2

## Control metadata

```text
Task: DRC_V410_GP2_EPHEMERAL_MOOD_POLICY_CORRECTIVE_R2
Date: 2026-11-14
Baseline: c10db09a0ce1e8acd8960df65032fd97c3f73de8
Surface: exact M4 A1 D0
State: CORRECTIVE_IMPLEMENTED / STATIC_VERIFIED / GP2_INCOMPLETE / READY_FOR_REVIEW
Stage / commit / push: NOT_AUTHORIZED
```

## User decision and approved value

The user selected 「保存しない（推奨）」 on 2026-11-14 for the active
v4.1.0 GitHub Android Public Beta.

```text
EPHEMERAL_NO_PERSISTENCE_FOR_V410_GITHUB_BETA
```

## Active beta scope

This decision applies only to Mood selection in the active GitHub Android
Public Beta. It does not close GP0-D08 and does not decide Character
persistence or any future release policy.

## Current implementation behavior

- A user starts with Mood unselected and can choose one of three options.
- The selection remains available inside the same
  `ProductionJourneyOverview` widget instance.
- A fresh `ProductionJourneyOverview` instance starts unselected again.
- Mood is not saved across process termination, app restart, or devices.

This is intentional product behavior for the active beta, not an omitted
persistence implementation.

## Fresh-instance reset contract and test evidence

`production_journey_shell_test.dart` pumps the journey, confirms unselected
state, selects `☀️ 元気` and `ミナ`, and verifies the selected character,
selected Mood, and materialized `今日は調子がよさそうですね` local advice.
It then replaces the widget tree to dispose its State, pumps a fresh journey,
and verifies that Mood is unselected, initial guidance is restored, and the
previous local advice is absent. Character selection is test setup for
materializing advice and does not establish a Character persistence decision.

The test shares no state and uses no timer, sleep, network, filesystem,
platform storage, mock storage, or production test hook.

## Source and dependency boundary

Product source is unchanged. No storage dependency is added. The dependency
guard covers `shared_preferences`, `sqflite`, `hive`, `isar`, `sembast`,
`drift`, and `hydrated_bloc` in `app/pubspec.yaml` and `app/lib/production`.
No remote Backend, persistence, AI generation, or AI Character Framework
runtime routing is introduced.

## Decision state

- D03: `APPROVED` for the active local-only/no-remote-Backend beta mode.
- D08: `NOT_DECIDED`.
- D11: `APPROVED`.

## Explicit non-claims

This Control does not approve Character persistence, health-data storage,
history, analytics, Cloud Backend, account synchronization, device backup,
retention/deletion policy, Privacy Policy completion, or future persistence.
It does not claim GP-2 or GP-3 complete.

## Remaining GP-2 work and stop boundary

Character-aware mood copy, remaining Core-flow migration, artifact exclusion
proof, and GP-3 refinement remain open. Stop after the required verification
and exact five-entry review handoff. Do not stage, commit, push, build, sign,
tag, publish a Release/asset, or expand the five-path surface.
