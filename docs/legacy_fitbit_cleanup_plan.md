# Daily Rhythm Companion v0.17.0 Day2
# Legacy Fitbit Cleanup Plan

## Purpose

Daily Rhythm Companion is moving the public wearable direction away from legacy Fitbit Web API integration and toward Google Health / future wearable provider boundaries.

The legacy Fitbit implementation is still useful as a migration/reference boundary because it already contains examples for:

- OAuth state handling
- token exchange guard rails
- local token storage
- token refresh before API access
- sleep API request boundaries
- app-facing `SleepSummary` normalization

However, it should not be presented as the recommended public integration path.

## Current public direction

Recommended sample sleep providers:

```env
SLEEP_PROVIDER=mock
```

or:

```env
SLEEP_PROVIDER=wearable_stub
```

Compatibility-only provider:

```env
SLEEP_PROVIDER=fitbit_stub
```

Legacy migration/reference provider:

```env
SLEEP_PROVIDER=fitbit
```

## Boundary policy

### Keep for now

Keep the legacy Fitbit implementation in the repository while Google Health sleep summary integration is still being designed and verified.

Allowed legacy Fitbit areas:

- `backend/app/api/fitbit.py`
- `backend/app/models/fitbit.py`
- `backend/app/services/fitbit_*.py`
- `backend/app/services/sleep_providers/fitbit.py`
- `backend/app/services/sleep_providers/fitbit_stub.py`
- `backend/.env.example` legacy reference variables
- README legacy reference section
- `docs/fitbit_integration_plan.md`

### Do not expand

Do not add new app-facing features that make Fitbit look like the primary future direction.

Avoid adding:

- new Fitbit-first UI copy
- new onboarding copy centered on Fitbit
- new release notes that present Fitbit as the recommended provider
- new public README setup paths that recommend `SLEEP_PROVIDER=fitbit`
- new release package docs for users that focus on Fitbit setup

### Keep UI wording neutral

Flutter UI may keep calling existing backend routes such as `/fitbit/status` internally for compatibility, but user-facing labels should use neutral wording such as:

- Health data connection
- Health provider
- Wearable data
- Sleep data

Avoid user-facing labels such as:

- Fitbit connection status
- Fitbit connect button
- Fitbit setup

## Removal decision gate

Do not remove legacy Fitbit code until at least one replacement path is verified.

Recommended removal gate:

1. Google Health OAuth real token exchange works locally.
2. Google Health token storage and refresh are implemented.
3. Google Health sleep summary provider is wired into `/sleep/summary`.
4. Local smoke/API test confirms sleep summary retrieval from the replacement provider.
5. README and `.env.example` no longer need Fitbit as a concrete migration reference.

After the gate is met, remove or quarantine the legacy Fitbit provider.

## Proposed removal steps

### Step 1: Stop presenting legacy Fitbit as public setup

Status: done in v0.16.0.

- `wearable_stub` is the recommended sample provider.
- `fitbit_stub` is a deprecated compatibility alias.
- `fitbit` is a migration/reference provider only.

### Step 2: Keep legacy code behind explicit boundaries

Status: v0.17.0 target.

- Add this cleanup plan.
- Add a lightweight boundary check for legacy Fitbit wording.
- Keep legacy provider names explicit in backend code.
- Keep UI wording neutral.

### Step 3: Implement Google Health sleep provider

Status: future version.

- Add Google Health token refresh.
- Add Google Health sleep data read service.
- Add Google Health sleep provider.
- Wire provider into `/sleep/summary`.

### Step 4: Remove or quarantine Fitbit code

Status: after Google Health real API verification.

Candidate removals:

- `backend/app/api/fitbit.py`
- `backend/app/models/fitbit.py`
- `backend/app/services/fitbit_*.py`
- `backend/app/services/sleep_providers/fitbit.py`
- `backend/app/services/sleep_providers/fitbit_stub.py`
- Fitbit env variables from `backend/.env.example`
- Flutter model/client names that still say Fitbit internally

Candidate migration replacement:

- `/health-data/status`
- `/health-data/connect`
- `/health-data/callback`
- app-facing `HealthConnectionStatus`
- app-facing `HealthConnectResponse`

## v0.17.0 Day2 acceptance criteria

Day2 is complete when:

- This cleanup plan exists in docs.
- The project has a repeatable check for accidental Fitbit-first public wording.
- Existing legacy Fitbit code is allowed only as an explicit migration/reference boundary.
- No public release-facing README/app README text presents Fitbit as the recommended provider.

