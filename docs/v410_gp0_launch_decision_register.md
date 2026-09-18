# DRC v4.1.0 GP-0 Launch Decision Register

## Control boundary

```text
Task: DRC_V410_GP0_LAUNCH_FOUNDATION_INVENTORY_R1
Development line: DRC v4.1.0
Phase: GP-0
Baseline commit: d7e39ad37667c6f3f104c2097f5ca54f9089df5c
Decision owner: User
Implementation support: Codex
Design/review support: ChatGPT
Final decisions taken by Control A: NONE
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
| Current observed state | Namespace and application ID are `com.example.app`. |
| Decision to make | Select the permanent unique Google Play application ID. |
| Required inputs/evidence | Organization/domain ownership, naming policy, Console availability, migration constraints. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-5, GP-7, GP-8, GP-9 |
| Must be decided before | Android identity implementation and Play application creation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | A later ID change can create a different Play application. |

## GP0-D02 Formal application display name

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Android label is `app`. |
| Decision to make | Approve the public display name and consistency rules. |
| Required inputs/evidence | Product naming, localization, trademark review, listing constraints. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-3, GP-4, GP-7, GP-9 |
| Must be decided before | Release-facing UI and listing assets are frozen. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No final name is preferred by Control A. |

## GP0-D03 Production Backend hosting and HTTPS endpoint model

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Default is `http://127.0.0.1:8000`; environment override exists. |
| Decision to make | Select provider, topology, HTTPS endpoint, environments, monitoring, maintenance, and incident ownership. |
| Required inputs/evidence | Provider/account/contract evidence, domain ownership, security, operations, cost. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-2, GP-3, GP-4, GP-5, GP-6, GP-8, GP-9 |
| Must be decided before | Production connectivity implementation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No cloud deployment is claimed. |

## GP0-D04 Production versus non-product separation architecture

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | HomeScreen mixes general-user, demo, realtime, diagnostic, and developer/operator UI. |
| Decision to make | Approve route, entry-point, build-configuration, and Backend-reachability boundaries. |
| Required inputs/evidence | GP-1 screen/route/data-flow inventory and production journey requirements. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-1, GP-2, GP-3, GP-4, GP-5, GP-6, GP-7 |
| Must be decided before | GP-2 production separation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Visual hiding alone is insufficient. |

## GP0-D05 Google Play account type and closed-testing applicability

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Account type and production-access history are external and `NOT_VERIFIED`. |
| Decision to make | Confirm account type and applicable testing requirements. |
| Required inputs/evidence | Play Console account evidence and current official requirements. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-7, GP-8, GP-9 |
| Must be decided before | Testing-track plan acceptance. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | The 12-testers/14-days rule is neither assumed nor dismissed. |

## GP0-D06 Release signing ownership and Play App Signing model

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Release uses debug signing; production ownership is absent. |
| Decision to make | Approve upload-key ownership, custody, recovery, rotation, and Play App Signing. |
| Required inputs/evidence | Account ownership, custodians, secure storage and recovery requirements. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-8, GP-9 |
| Must be decided before | Signing configuration or AAB creation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No key or credential is recorded. |

## GP0-D07 Android target API confirmation and upgrade policy

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | targetSdk is delegated; API 36 compliance is `NOT_VERIFIED`. |
| Decision to make | Confirm current Play requirement, target, upgrade path, and maintenance policy. |
| Required inputs/evidence | Current official Play policy and resolved build-tool values. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-6, GP-8, GP-9 |
| Must be decided before | Android release-foundation acceptance. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Control A does not assert API 36 compliance. |

## GP0-D08 Data, policy, deletion, Data safety, and Health Apps ownership

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | Microphone, health, sleep, chat/advice, diagnostics, configuration, and logs require reconciliation. |
| Decision to make | Assign accountable owners and approve the evidence/reconciliation process. |
| Required inputs/evidence | Runtime/network inventory, retention/deletion behavior, policy and Console evidence. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-3, GP-5, GP-6, GP-7, GP-8, GP-9 |
| Must be decided before | Policy text, declarations, and submission. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | No legal or policy completion is claimed. |

## GP0-D09 v4.1.0 version/build-number sequence

| Field | Value |
| --- | --- |
| Status | NOT_DECIDED |
| Current observed state | `app/pubspec.yaml` remains `4.0.0+5`. |
| Decision to make | Approve v4.1.0 version and monotonic Play build-number sequence. |
| Required inputs/evidence | Existing Play version-code history and release-candidate policy. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-4, GP-8, GP-9 |
| Must be decided before | Version change or AAB creation. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | Control A does not modify version metadata. |

## GP0-D10 Phase evidence, stop, rollback, and publication authorization model

| Field | Value |
| --- | --- |
| Status | PROPOSED |
| Current observed state | Planning R1 defines gated phases and separate authorization boundaries. |
| Decision to make | Approve or revise phase evidence, stop, rollback, and publication controls. |
| Required inputs/evidence | Planning R1 and each phase evidence contract. |
| Decision owner | User |
| Implementation owner | NOT_DECIDED |
| Dependent phases | GP-1 through GP-9 |
| Must be decided before | Any phase closure or publication authorization. |
| Approved value | NOT_DECIDED |
| Approval evidence | NONE |
| Implementation authorization | NOT_AUTHORIZED |
| Notes | `PROPOSED_BASELINE_FROM_PLANNING_R1`; GP-0 is not complete. |

## Dependency and decision order

1. GP0-D01 application ID.
2. GP0-D02 display name.
3. GP0-D05 Play account type.
4. GP0-D03 Backend publication model.
5. GP0-D04 production separation architecture.
6. GP0-D06 signing ownership.
7. GP0-D07 target API.
8. GP0-D08 privacy/data ownership.
9. GP0-D09 version/build sequence.
10. GP0-D10 evidence and authorization closure.

This is a planning order, not approval of a decision.

## Version and immutable release boundary

- Development line: DRC v4.1.0.
- `app/pubspec.yaml` remains unchanged.
- The v4.0.0 tag, GitHub Release, asset, fixed ZIP, and history are immutable.
- No v4.1.0 build, tag, Release, or asset is created.