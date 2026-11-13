# DRC v4.1.0 GP-0 Launch Decision Register

## Control boundary

```text
Original inventory control: DRC_V410_GP0_LAUNCH_FOUNDATION_INVENTORY_R1
Development line: DRC v4.1.0
Phase: GP-0
Baseline commit: d7e39ad37667c6f3f104c2097f5ca54f9089df5c
Decision owner: User
Implementation support: Codex
Design/review support: ChatGPT
Original Control A decisions: NONE
Current update task: DRC_V410_GP2_MOOD_CHECK_IN_MIGRATION_R1
Current decision state: D01 NOT_DECIDED; D02 APPROVED as Daily Rhythm Companion;
  D03 NOT_DECIDED; D04 APPROVED; D05-D09 NOT_DECIDED; D10 PROPOSED; D11 APPROVED
GP0-D04: APPROVED
Product-source implementation: AUTHORIZED_FOR_GP2_MOOD_CHECK_IN_MIGRATION_R1_EXACT_M6_A4_D0
```

Codex does not make irreversible business, account, identity, provider, legal,
policy, signing-ownership, or publication decisions. ChatGPT support does not
substitute for user approval.

## Decision status schema

Every `Status` field uses exactly one closed-vocabulary value:

```text
NOT_DECIDED
PROPOSED
APPROVED
BLOCKED
DEFERRED
SUPERSEDED
```

## GP0-D01 Formal Android application ID

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Namespace and application ID are com.example.app. |
| Decision to make | Select the permanent unique Android application ID for direct-distribution continuity and later Google Play use. |
| Required inputs/evidence | Organization/domain ownership, naming policy, signing/update continuity, future Play availability, and migration constraints. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-5, GP-6, GP-7, GP-8, GP-9 |
| Must be decided before | Public-beta Android identity implementation, release signing, or artifact creation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Required for direct APK update continuity and later Play continuity. A later ID change creates a different installed application. |

## GP0-D02 Formal application display name

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Current observed state | Android label is app. |
| Decision to make | Approve the public display name and consistency rules. |
| Required inputs/evidence | Product naming, localization, trademark review, listing constraints. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-3, GP-4, GP-7, GP-9 |
| Must be decided before | Release-facing UI and listing assets are frozen. |
| Approved value | Daily Rhythm Companion |
| Approval evidence | User selection recorded 2026-09-18. |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Android source implementation is not authorized. Japanese store representation and localization remain a separate decision. |

## GP0-D03 Production Backend hosting and HTTPS endpoint model

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Default is `http://127.0.0.1:8000`; environment override exists. |
| Decision to make | Select provider, topology, HTTPS endpoint, environments, monitoring, maintenance, and incident ownership. |
| Required inputs/evidence | Provider/account/contract evidence, domain ownership, security, operations, cost, and the unresolved field inventory in `docs/v410_gp0_backend_privacy_decision_control.md`. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-2, GP-3, GP-4, GP-5, GP-6, GP-8, GP-9 |
| Must be decided before | Production connectivity implementation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No cloud deployment is claimed. The decision-control document supplies evidence and a questionnaire only; it does not approve a provider, domain, region, owner, price, or implementation. |

## GP0-D04 Production versus non-product separation architecture

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Current observed state | HomeScreen mixes general-user, demo, realtime, diagnostic, and developer/operator UI. |
| Decision to make | Approve route, entry-point, build-configuration, and Backend-reachability boundaries. |
| Required inputs/evidence | GP-1 screen/route/data-flow inventory and production journey requirements. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-1, GP-2, GP-3, GP-4, GP-5, GP-6, GP-7 |
| Must be decided before | GP-2 production separation. |
| Approved value | Separate production entrypoint and production-only composition with structural import, route, and Backend reachability boundaries. |
| Approval evidence | User selection recorded 2026-09-18. |
| Implementation authorization | AUTHORIZED_FOR_GP2_CONTROL_A |
| Notes | Visual hiding alone is insufficient; production Backend allowlist, core-flow migration, artifact proof, and release wiring remain incomplete. |

## GP2-S01 Production text-core capability scope

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Approved value | TEXT_CORE_PLUS_CHAT |
| Included capabilities | Sleep/health connection; mood check-in; character selection; daily advice; optional text chat; history. |
| Excluded capabilities | Voice input/output; realtime; motion; demo; developer/operator controls; raw diagnostics; framework lifecycle controls. |
| Approval evidence | User selection recorded 2026-09-19. |
| Backend/health implementation | NOT_AUTHORIZED |
| Dependencies | GP0-D03 Backend publication model and GP0-D08 privacy/data ownership remain NOT_DECIDED. |
| Notes | Mood check-in remains included. This control authorizes only a local three-choice production mood UI and typed model. Persistence, advice wiring, character-aware copy, Backend, and health connectivity are not authorized. D03/D08 remain NOT_DECIDED; GP-2 and GP-3 remain incomplete. |

## GP0-D05 Google Play account type and testing applicability

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Account type and production-access history are external and `NOT_VERIFIED`. |
| Decision to make | Confirm account type and applicable testing requirements. |
| Required inputs/evidence | Play Console account evidence and current official requirements. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | Deferred Google Play Track only |
| Must be decided before | Reactivating a Play testing-track plan. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Deferred for the GitHub beta and not cancelled. No tester-count or duration rule is assumed or dismissed. |

## GP0-D06 Release signing ownership and future Play App Signing model

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Release uses debug signing; production ownership is absent. |
| Decision to make | Approve direct-distribution APK signing ownership, custody, recovery, rotation, update continuity, and the future Play App Signing relationship. |
| Required inputs/evidence | Account ownership, custodians, secure storage and recovery requirements. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-6, GP-8, GP-9; Play App Signing is Deferred Google Play Track |
| Must be decided before | Any public-beta signing configuration, APK build, or later AAB creation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No key or credential is recorded. Direct-distribution signing must preserve update continuity; future Play App Signing remains a deferred decision. |

## GP0-D07 Android compatibility and deferred Play target-API policy

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | targetSdk is delegated; API 36 compliance is `NOT_VERIFIED`. |
| Decision to make | Approve the public-beta supported Android range and maintenance policy; reconfirm the current Play target-API requirement when Play is reactivated. |
| Required inputs/evidence | Resolved build-tool values, representative-device evidence, and current official Play policy at reactivation. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-6; Play target API is Deferred Google Play Track |
| Must be decided before | Android release-foundation acceptance. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | This replan asserts neither supported-version acceptance nor API 36 compliance. Play confirmation is deferred, not cancelled. |

## GP0-D08 Data, policy, deletion, Data safety, and Health Apps ownership

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Microphone, health, sleep, chat/advice, diagnostics, configuration, and logs require reconciliation. |
| Decision to make | Assign accountable owners and approve the evidence/reconciliation process. |
| Required inputs/evidence | Runtime/network inventory, retention/deletion behavior, policy and Console evidence, and the unresolved field inventory in `docs/v410_gp0_backend_privacy_decision_control.md`. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-3, GP-5, GP-6, GP-7, GP-8, GP-9 |
| Must be decided before | Public Privacy Policy/support publication, Android beta publication, Play declarations, or submission. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No legal or policy completion is claimed. The evidence control approves no operator, contact, retention/deletion period, processor, provider, territory, or legal conclusion. GitHub distribution does not bypass this gate. |

## GP0-D09 v4.1.0 version/build-number sequence

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | `app/pubspec.yaml` remains `4.0.0+5`. |
| Decision to make | Approve v4.1.0 public-beta version and monotonic Android version-code sequence that remains compatible with later Play work. |
| Required inputs/evidence | Existing version-code history, direct-update policy, and later Play continuity. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-8, GP-9 |
| Must be decided before | Version change, public APK creation, or later AAB creation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Control A does not modify version metadata. |

## GP0-D10 Phase evidence, stop, rollback, and publication authorization model

| Field | Value |
| --- | --- |
| Status | PROPOSED |
| Current observed state | Planning R1 and this replan define gated phases and separate authorization boundaries. |
| Decision to make | Approve or revise phase evidence, stop, rollback, and publication controls. |
| Required inputs/evidence | Planning R1, this GitHub beta replan, and each phase evidence contract. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-1 through GP-9 |
| Must be decided before | Any phase closure or publication authorization. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | `PROPOSED_BASELINE_FROM_PLANNING_R1`; GP-0 is not complete. |

## GP0-D11 Distribution sequence and primary repository landing

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Current observed state | No installable public Android APK is published; the existing v4.0.0 ZIP is not an APK. |
| Decision to make | Select the first public Android distribution channel and the repository landing-page role without cancelling later Google Play work. |
| Required inputs/evidence | User-facing release status, safe download guidance, Framework attribution, policy/support prerequisites, and preserved v4.0.0 history. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4 through GP-9 |
| Must be decided before | Publishing an installable Android Public Beta. |
| Approved value | `GITHUB_ANDROID_PUBLIC_BETA_FIRST / GOOGLE_PLAY_LATER`; repository README is the primary general-Android-user landing page. |
| Approval evidence | User scope amendment recorded 2026-11-13. |
| Implementation authorization | `AUTHORIZED_FOR_REPLAN_ONLY` |
| Notes | Google Play is deferred, not cancelled. Build, signing, key, tag, GitHub Release, asset, Console, provider, domain, privacy, support, and publication operations remain unauthorized. |
## Dependency and decision order

1. GP0-D11 GitHub Android Public Beta first and README landing (approved).
2. GP0-D01 permanent application ID.
3. GP0-D06 direct-distribution signing ownership and update continuity.
4. GP0-D09 public-beta version/build sequence.
5. GP0-D03 Backend publication model.
6. GP0-D08 privacy/data/support ownership.
7. GP0-D07 Android compatibility range.
8. GP0-D10 evidence, stop, rollback, and publication controls.
9. GP-8 Public Beta testing and candidate freeze.
10. GP-9 GitHub Release publication and post-release verification.
11. GP0-D05 and the Play-specific part of D06/D07 only when the separate
    Deferred Google Play Track is reactivated.

This is a planning order, not approval of a decision.

## Version and immutable release boundary

- Development line: DRC v4.1.0.
- `app/pubspec.yaml` remains unchanged.
- The v4.0.0 tag, GitHub Release, asset, fixed ZIP, and history are immutable.
- No v4.1.0 build, tag, Release, or asset is created.
