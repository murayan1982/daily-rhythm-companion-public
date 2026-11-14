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
Current update task: DRC_V410_GP2_PUBLIC_BETA_CORE_FLOW_R1
Current update baseline: 7d24b4bfc344ac5854ede1f1e72b5faf3d337b11
Current decision state: D01 NOT_DECIDED; D02 APPROVED as Daily Rhythm Companion;
  D03 APPROVED for v4.1.0 GitHub beta local-only mode; D04 APPROVED;
  D05-D09 NOT_DECIDED; D10 PROPOSED; D11 APPROVED
GP0-D04: APPROVED
Product-source implementation: AUTHORIZED_FOR_GP2_PUBLIC_BETA_CORE_FLOW_R1
Documentation authorization: APPROVED_FOR_GP2_PUBLIC_BETA_CORE_FLOW_R1
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
| Status | APPROVED |
| Current observed state | The v4.1.0 GitHub Android Public Beta active track uses local deterministic advice and no remote production Backend. |
| Decision to make | Select the active beta Backend mode while deferring any future Cloud Backend provider, topology, HTTPS endpoint, environment, monitoring, maintenance, and incident ownership decision. |
| Required inputs/evidence | Provider/account/contract evidence, domain ownership, security, operations, cost, and the unresolved field inventory in `docs/v410_gp0_backend_privacy_decision_control.md`. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-2, GP-3, GP-4, GP-5, GP-6, GP-8, GP-9 |
| Must be decided before | Any future Cloud Backend or production connectivity implementation. |
| Approved value | V410_GITHUB_BETA_LOCAL_ONLY_NO_REMOTE_BACKEND |
| Approval evidence | User selection recorded 2026-11-13 |
| Implementation authorization | AUTHORIZED_FOR_GP2_LOCAL_ADVICE_MIGRATION_R1 |
| Notes | The v4.1.0 GitHub Android Public Beta uses no remote production Backend and only local deterministic advice. Endpoint, hosting, domain, credential, and monitoring are not required for this active mode. A future Cloud Backend is `DEFERRED / NOT_CANCELLED`; resuming it requires a new decision and authorization. D08 remains `NOT_DECIDED`; health, persistence, and privacy publication remain unapproved. |

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
| Dependencies | GP0-D03 is approved only for the active local-only GitHub beta mode; GP0-D08 privacy/data ownership remains NOT_DECIDED. |
| Notes | `TEXT_CORE_PLUS_CHAT` remains the approved long-term capability range. The active Public Beta main screen intentionally presents only Mood selection, Character selection, and deterministic local advice. Optional text chat, sleep/health connection, and history are not exposed in this Beta flow. Persistence, Backend fetch, Framework routing, provider/model selection, and health connectivity remain unimplemented. D08 remains NOT_DECIDED; D11 remains APPROVED; GP-2 and GP-3 remain incomplete. |

## GP2-S02 Active beta Mood persistence policy

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Approved value | EPHEMERAL_NO_PERSISTENCE_FOR_V410_GITHUB_BETA |
| Approval evidence | User selection recorded 2026-11-14 |
| Scope | v4.1.0 GitHub Android Public Beta |
| Behavior | Mood selection exists only in the current ProductionJourneyOverview instance and returns to unselected when a fresh instance is created. |
| Persistence | NOT_IMPLEMENTED / NOT_INCLUDED_IN_ACTIVE_BETA |
| External transmission | NONE |
| D08 | NOT_DECIDED |
| Notes | This decision does not approve health-data storage, history, analytics, Cloud Backend, account synchronization, device backup behavior, retention, deletion policy, or any future persistence implementation. |

## GP2-S03 Strict product artifact exclusion policy

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Approved value | STRICT_PRODUCT_ONLY_ANDROID_ARTIFACT |
| Approval evidence | User selection recorded 2026-11-14 |
| Scope | GitHub Android Public Beta and later final public candidates |
| Required exclusion | Non-product Dart graph, permissions, native plugins, assets, endpoints, and operator/developer surfaces not approved for the product. |
| Architecture | GP2-S04 APPROVED — SEPARATE_PUBLIC_FLUTTER_APPLICATION_BOUNDARY |
| Artifact proof | PRIVATE_ARM64_UNSIGNED_PROOF_CAPTURED_FROM_ED2454D / FINAL_SIGNED_APK_REPROOF_PENDING_GP4 |
| Dependencies | GP-2 source boundary, GP2-S04 implementation, GP-4 release wiring and final artifact verification |
| Notes | D03 remains APPROVED for the active local-only beta. D08 remains NOT_DECIDED. D11 remains APPROVED. This decision does not authorize build, signing, publication, or architecture implementation. |

## GP2-S04 Product dependency-boundary architecture

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Approved value | SEPARATE_PUBLIC_FLUTTER_APPLICATION_BOUNDARY |
| Decision owner | User |
| Approval evidence | User approved Option A with `A案承認` on 2026-11-14. |
| Scope | v4.1.0 GitHub Android Public Beta; implements the dependency ownership required by GP2-S03 when separately authorized. |
| Directory ownership | `app_public/` owns the public Flutter app and Android build inputs; `packages/drc_production/` owns the production journey; `app/` owns developer/demo/operator tooling and the production preview. |
| Design and migration | [GP-2 production boundary architecture](v410_gp2_production_boundary_architecture.md#control-g-public-flutter-application-boundary) |
| Documentation authorization | APPROVED — exact M5 A0 D0 |
| Architecture implementation | NOT_AUTHORIZED |
| Build / signing / stage / commit / push / publication | NOT_AUTHORIZED |
| Impact | BLOCKER-G and the separate public-app implementation boundary are complete. An unsigned ARM64 proof APK from `ed2454da9277b425e62a72c8b29357ad0780b49b` has exclusion evidence; formal identity, version, signing, and final-candidate reproof remain GP-4 gates. |

## GP2-S05 Active Public Beta core-flow presentation

| Field | Value |
| --- | --- |
| Status | APPROVED |
| Approved value | THREE_STEP_LOCAL_MOOD_CHARACTER_ADVICE_WITH_MOOD_SPECIFIC_CHARACTER_INVARIANT_ACKNOWLEDGEMENT |
| Approval evidence | User approval recorded 2026-11-14. |
| Active Beta steps | 1. Mood selection; 2. Character selection; 3. deterministic local daily advice. |
| Mood acknowledgement | Each Mood keeps its accepted mood-specific immediate response. For a fixed Mood, that response is identical across all Character choices; Character-aware variation is reserved for the nine deterministic advice messages. |
| Input order | Mood and Character may be selected in either order; advice appears and updates only after both are selected. |
| Excluded from active screen | Sleep/health connection, optional text chat, and history cards. |
| Long-term boundary | GP2-S01 `TEXT_CORE_PLUS_CHAT` remains approved and unchanged. |
| State and data | Current-screen selection only; no persistence, network, or Backend wiring. GP2-S02 remains in force. |
| Verification | Flutter 3.41.7 / Dart 3.11.5: shared package analyze PASS and 29 tests PASS; `app_public/` analyze PASS and startup test PASS; app product-boundary suite 31 tests PASS. |
| Acceptance state | The active Beta GP-2 three-step implementation is implemented and statically verified, pending review and acceptance of the current diff. |
| Remaining work | Sleep/health connection, optional text chat, and history remain future scope. GP-4 formal identity/version/signing and final signed-APK reproof, plus GP-3 refinement, remain separate. |

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
