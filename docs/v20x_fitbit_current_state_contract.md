# v2.0.x Fitbit current-state contract

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED
Small commit: M-7 — `docs/test: clarify Fitbit current-state contract`

## Purpose

M-7 records what the retained Fitbit-related code does today without treating source availability, local token presence, an OAuth URL, or deterministic stub data as verified real Fitbit operation.

This is a maintenance clarification and regression boundary. It does not complete the v2.1.0 real wearable daily loop.

## Current classification

| Surface | Current role | What it proves | What it does not prove |
| --- | --- | --- | --- |
| `SLEEP_PROVIDER=mock` | recommended credential-free default | deterministic app behavior | wearable connectivity |
| `SLEEP_PROVIDER=wearable_stub` | recommended wearable-shaped sample | deterministic wearable-shaped `SleepSummary` | any external API execution |
| `SLEEP_PROVIDER=fitbit_stub` | deprecated compatibility alias | old local configuration still resolves to sample behavior | Fitbit connectivity or Fitbit data |
| `SLEEP_PROVIDER=fitbit` | legacy migration/reference provider | retained OAuth/token/read/normalization boundaries are callable | accepted real Fitbit daily use |
| `/fitbit/status` | compatibility status route | configuration and token-like local-file presence | live token validity, permissions, refresh success, or sleep retrieval |
| `/fitbit/connect` | compatibility authorization-URL route | an OAuth state and authorization URL can be prepared | successful authorization, token exchange, or connected state |
| `/fitbit/callback` | guarded legacy callback boundary | callback/state and guarded token-exchange states can be represented | operator-accepted real token exchange |
| Fitbit sleep service/provider | retained migration/reference implementation | raw payloads stay behind backend boundaries and normalize to `SleepSummary` | current provider acceptance against real Fitbit data |

## Status semantics

The existing response models and routes remain backward compatible.

For `/fitbit/status`:

```text
connected=false
  -> configuration or complete local token-like data is absent

connected=true
  -> legacy credentials and local access/refresh token-like fields were detected
  -> does not mean the token is live or that real sleep data was retrieved
```

M-7 intentionally keeps the existing `connected` Boolean shape. The backend message must continue to state that real token validation is not implemented for this status result.

Flutter presentation must not turn legacy `connected=true` into an unqualified `連携済み` or `利用可能` claim. It displays a local-token-detected / unverified state instead.

For `/fitbit/connect`:

```text
ready=true + connect_url
  -> an authorization URL was prepared
  -> does not mean authorization, token exchange, connection, or sleep retrieval succeeded
```

## Stub and unavailable semantics

`wearable_stub` and `fitbit_stub` are deterministic sample paths. Their available sleep summary is sample availability, not real wearable-data availability.

The legacy `fitbit` provider returns `available=false` when token data, refresh, API access, or response normalization is unavailable. That unavailable state is a normal app state and must not expose raw tokens or raw Fitbit payloads.

## Real-use acceptance state

Current v2.0.x status:

```text
Fitbit source boundaries present: yes
Legacy OAuth/token/read code present: yes
Mock-safe regression coverage: yes
Configured real Fitbit operator acceptance: no
Fitbit real-use completion: deferred to v2.1.0
```

No M-7 source-tree or mock-safe test may be reported as real Fitbit execution evidence.

## v2.1.0 handoff

The v2.1.0 wearable work starts from this inventory and must separately verify:

```text
W-1  current behavior inventory and accepted contract
W-2  token validity, refresh, reconnect, and permission-state hardening
W-3  real sleep retrieval and normalization regression coverage
W-4  provider selection and source-label UI
W-5  explicit configured real Fitbit operator verification
```

A later task may replace or remove compatibility `/fitbit/*` names only through an explicit migration plan. M-7 does not remove routes, response fields, provider names, local storage formats, or legacy configuration values.

## Mock-safe regression boundary

Backend tests use fakes and deterministic providers. They do not read or write `backend/local_data`, call Fitbit endpoints, require credentials, or expose token values.

Flutter tests verify that:

```text
- legacy token presence is shown as local-token detection, not verified connection
- authorization URL readiness is not shown as connection success
- verified non-legacy provider wording remains backward compatible
```

## Explicit non-change surface

```text
docs/DRC_v200_goal_checklist_small_commit.md
release_notes/v2.0.0.md
/fitbit/status, /fitbit/connect, and /fitbit/callback route shapes
Fitbit response-model fields
OAuth state, token exchange, refresh, token storage, sleep API, and normalization logic
Google Health behavior accepted in v2.0.0
real provider execution and private operator evidence
release ZIP, tag, GitHub Release, or v2.0.1 publication
```

## Accepted verification commands

```powershell
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py
python scripts\check_v20x_backend_mock_safe_regression.py
python scripts\check_v20x_framework_fallback_voice_artifact_regression.py
python scripts\check_v20x_temporary_lifecycle_limits.py
python scripts\check_v20x_web_cors_origins.py
python scripts\check_v20x_fitbit_current_state_contract.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

M-7 was accepted on 2026-07-23 after compileall, M-1 through M-7 checks, 38 backend pytest tests, 43 Flutter tests, diff review, and operator approval passed. This acceptance records the maintenance contract only; configured real Fitbit operator acceptance remains deferred to v2.1.0, and M-7 did not release v2.0.1.
