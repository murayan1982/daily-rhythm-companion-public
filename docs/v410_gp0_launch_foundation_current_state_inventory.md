# DRC v4.1.0 GP-0 Launch Foundation Current-State Inventory

## 1. Control metadata

```text
Task: DRC_V410_GP0_LAUNCH_FOUNDATION_INVENTORY_R1
Development line: DRC v4.1.0
Phase: GP-0
Baseline commit: d7e39ad37667c6f3f104c2097f5ca54f9089df5c
Exact implementation surface: M2 A2 D0
Implementation authorization: APPROVED
Stage / commit / push authorization: NOT_AUTHORIZED
Control character: source-backed inventory, not final decision
```

This control records repository evidence and decision boundaries. It does not
approve an identity, provider, account, signing model, policy answer, or launch.

## 2. Source evidence boundary

The inventory was derived from:

- `app/android/app/build.gradle.kts`
- `app/android/app/src/main/AndroidManifest.xml`
- `app/pubspec.yaml`
- `app/lib/main.dart`
- `app/lib/screens/home_screen.dart`
- `app/lib/services/backend_api_client.dart`
- `backend/app/config.py`
- `backend/.env.example`
- `docs/v410_google_play_launch_roadmap.md`
- `docs/v410_google_play_launch_tasklist.md`

Play Console, provider-account, organization, contract, domain, trademark, and
current policy facts are external evidence and remain `NOT_VERIFIED` or
`NOT_DECIDED`.

## 3. Android identity and release configuration

| Item | Observed current value | Evidence |
| --- | --- | --- |
| namespace | `com.example.app` | `app/android/app/build.gradle.kts:9` |
| applicationId | `com.example.app` | `app/android/app/build.gradle.kts:24` |
| Android application label | `app` | `app/android/app/src/main/AndroidManifest.xml:5` |
| release signing | Debug signing | `app/android/app/build.gradle.kts:33-37` |
| compileSdk | `flutter.compileSdkVersion` | `app/android/app/build.gradle.kts:10` |
| targetSdk | `flutter.targetSdkVersion` | `app/android/app/build.gradle.kts:28` |
| minSdk | `flutter.minSdkVersion` | `app/android/app/build.gradle.kts:27` |
| Flutter version metadata | `4.0.0+5` | `app/pubspec.yaml:5` |
| RECORD_AUDIO | Declared in main manifest | `app/android/app/src/main/AndroidManifest.xml:2` |

Formal application ID and display name are `NOT_DECIDED`. API 36-or-later
compliance is `NOT_VERIFIED`. Production release signing and Play App Signing
are not configured, and no signed v4.1.0 AAB exists. Control A changes no
Android setting.

## 4. Backend publication and connectivity

| Item | Observed current value | Evidence |
| --- | --- | --- |
| Configuration key | `DRC_BACKEND_API_BASE_URL` | `app/lib/services/backend_api_client.dart:26-28` |
| Default Backend URL | `http://127.0.0.1:8000` | `app/lib/services/backend_api_client.dart:28` |
| Production Backend URL | `NOT_DECIDED` | No production URL in inspected source |
| Production hosting/provider | `NOT_DECIDED` | External decision/evidence required |

`String.fromEnvironment` provides an override boundary. The default is not a
production endpoint usable from an Android device. A development hint permits
a LAN endpoint for smartphone Web demonstrations. Production HTTPS,
environment separation, availability, monitoring, maintenance, and incident
response remain `NOT_DECIDED`. No cloud deployment is claimed. Control A
changes no Backend source or environment setting. No actual private LAN IP,
secret, or credential is recorded.

## 5. Product UI and non-product UI boundary

`HomeScreen` currently combines:

- General-user daily flow, daily-record handoff, and history.
- Character, advice, post-advice chat, and history-related UI.
- Demo status and capability presentation.
- Voice input demo and voice output demo.
- Motion demo and motion presentation.
- Framework realtime sessions and text-stream controls.
- Backend and framework diagnostics.
- Google Health diagnostics, preflight, self-check, and developer information.
- Detailed developer/operator-facing state and configuration.

Production versus developer/operator/demo/diagnostic separation is not
implemented. Visual hiding alone is insufficient. Routes, entry points, build
configuration, and Backend reachability require GP-1 inventory and GP-2
separation. Control A changes no Flutter product source.

## 6. Permissions, health data, and privacy boundary

The launch inventory must cover microphone permission; Fitbit and Google Health
connectivity; sleep and health data; chat and advice data; diagnostic and
configuration data; local and Backend logs; and retention/deletion behavior.
Repository source cannot establish Play Console Data safety answers, Health Apps
declarations, Console state, retention periods, ownership, or deletion SLA.
Those facts remain `NOT_VERIFIED` or `NOT_DECIDED`. This document includes no
real health data, email address, token, OAuth secret, personal identifier, or
credential.

## 7. Launch-blocker matrix

| ID | Area | Observed current state | Source evidence | Required destination state | Owning phase | Decision required | Current status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LB-01 | application ID | Placeholder `com.example.app` | Gradle 9,24 | Permanent unique ID | GP-0/GP-4 | GP0-D01 | NOT_DECIDED |
| LB-02 | application label | Generic `app` | Manifest 5 | Approved public name | GP-0/GP-4 | GP0-D02 | NOT_DECIDED |
| LB-03 | release signing | Debug signing | Gradle 33-37 | Secure release signing | GP-0/GP-4 | GP0-D06 | NOT_DECIDED |
| LB-04 | Play App Signing | Model absent | Android evidence | Approved ownership model | GP-0/GP-4 | GP0-D06 | NOT_DECIDED |
| LB-05 | target API | Flutter delegated | Gradle 28 | Current Play requirement met | GP-0/GP-4 | GP0-D07 | NOT_VERIFIED |
| LB-06 | signed AAB | No v4.1.0 artifact | Planning boundary | Authorized signed AAB | GP-4 | D06,D09 | NOT_CREATED |
| LB-07 | Backend publication | Provider/HTTPS absent | Client/config | Hosted HTTPS service | GP-0/GP-4 | GP0-D03 | NOT_DECIDED |
| LB-08 | localhost dependency | Loopback default | Client 26-40 | No production localhost | GP-4 | GP0-D03 | OPEN |
| LB-09 | production UI separation | Mixed HomeScreen | HomeScreen | Structural boundary | GP-1/GP-2 | GP0-D04 | OPEN |
| LB-10 | permission explanation | Permission declared; UX unverified | Manifest/HomeScreen | Contextual explanation | GP-3/GP-5 | GP0-D08 | NOT_VERIFIED |
| LB-11 | settings | Launch settings unverified | HomeScreen | Production settings/support | GP-3 | GP0-D04 | NOT_VERIFIED |
| LB-12 | Privacy Policy | Public URL unverified | Planning docs | Approved public policy | GP-5 | GP0-D08 | NOT_VERIFIED |
| LB-13 | data deletion | Process/SLA unverified | Planning docs | Verified deletion process | GP-5 | GP0-D08 | NOT_VERIFIED |
| LB-14 | Data safety | Console answers unavailable | External boundary | Reconciled declaration | GP-5 | GP0-D08 | NOT_VERIFIED |
| LB-15 | Health Apps declaration | Console state unavailable | External boundary | Reconciled declaration | GP-5 | GP0-D08 | NOT_VERIFIED |
| LB-16 | accessibility/device/error validation | Launch matrix not run | Tasklist | Accepted evidence | GP-6 | GP0-D10 | NOT_RUN |
| LB-17 | Play listing assets | Final set absent | Tasklist | Approved complete set | GP-7 | D02,D08 | NOT_CREATED |
| LB-18 | internal/closed testing | Evidence unavailable | External boundary | Track evidence accepted | GP-8 | GP0-D05 | NOT_RUN |
| LB-19 | production submission | Not authorized | Authorization boundary | Approved submission | GP-9 | GP0-D10 | NOT_AUTHORIZED |
| LB-20 | post-release smoke check | No v4.1.0 release | Phase sequence | Public smoke evidence | GP-9 | GP0-D10 | NOT_RUN |

Matrix statuses describe blockers; they are not decision-register statuses and
do not approve launch actions.

## 8. External-evidence boundary

The repository cannot establish the Google Play developer account type,
personal-account 12-testers/14-days applicability, current target API rule,
current Health Apps requirements, Play Console application record,
organization/domain/trademark ownership, or Backend provider/account/contract.
None is inferred or marked complete.

## 9. Control A completion and non-claims

Control A completes only inventory and decision-boundary documentation. It does
not claim GP-0 completion, identity approval, Backend selection, signing setup,
Play App Signing setup, API 36 verification, privacy/declaration completion,
testing completion, or production readiness.