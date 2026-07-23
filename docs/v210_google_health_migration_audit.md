# v2.1.0 W-5b1 — Google Health API migration audit

Status: IMPLEMENTED / NOT_ACCEPTED

## Official platform direction

As of 2026-07-24, Google documents the Google Health API as the next generation of the Fitbit Web API. The legacy Fitbit Web API is scheduled to be turned down in September 2026. Existing Fitbit integrations must move to Google Health API and Google OAuth 2.0; legacy access and refresh tokens cannot be transferred, so users must consent again.

Official references:

- https://developers.google.com/health/about
- https://developers.google.com/health/migration
- https://developers.google.com/health/migration/data-access
- https://developers.google.com/health/reference/rest/v4/users.dataTypes.dataPoints/list

## DRC source audit

The existing `google_health` provider already targets the new Google Health API v4 contract:

```text
base URL: https://health.googleapis.com/v4
sleep path: /users/me/dataTypes/sleep/dataPoints
scope: https://www.googleapis.com/auth/googlehealth.sleep.readonly
filter: sleep.interval.civil_end_time closed-open date range
response: dataPoints[].sleep.interval and dataPoints[].sleep.summary
```

The parser already supports the documented `minutesAsleep`, `minutesAwake`, and `stagesSummary` fields. Mock-safe tests now lock this contract.

The legacy `fitbit` provider remains source-compatible only as a migration/reference path. New OAuth execution and configured-real acceptance through the legacy Fitbit Web API are retired. The accepted W-5a record is retained as history, but its real-execution launcher and smoke are now hard-stopped.

## Contract correction

- `google_health` is the configured real wearable provider.
- `fitbit` is labeled `legacy_migration_reference`.
- Flutter reads the backend `provider_options` field; the previous `available_providers` key was inconsistent with the backend response.
- Normal user UI no longer offers a legacy Fitbit OAuth connection action.
- Advanced legacy diagnostics may remain for migration/reference compatibility.

## W-5 split after correction

```text
W-5a   COMPLETED / ACCEPTED   Historical public-safe Fitbit operator contract; no real execution
W-5b1  IMPLEMENTED / NOT_ACCEPTED  Google Health migration audit and legacy Fitbit execution retirement
W-5b2  PLANNED                Configured Google Health API operator verification for Fitbit-origin sleep and smartphone Web evidence
```

## Mock-safe boundary

W-5b1 may inspect source, run synthetic Google Health v4 payload tests, validate endpoint/filter/schema markers, and verify that legacy Fitbit execution is blocked. It must not open OAuth, read private credentials or tokens, call Google Health or Fitbit, retrieve real sleep data, or create release artifacts.

## Completion conditions

- Official migration direction and DRC implementation are accurately documented.
- Google Health v4 endpoint, scope, filter, and sleep payload tests pass.
- Flutter parses `provider_options` from the actual backend contract.
- Legacy Fitbit user-facing labels and operator actions no longer imply future configured-real acceptance.
- W-5b2 and all later phases remain not completed.
