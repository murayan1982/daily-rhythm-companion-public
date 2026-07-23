# v2.1.0 W-4b Flutter sleep-provider/source-label UI contract

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED
Parent phase: W-4 COMPLETED / ACCEPTED
Current small commit: W-5

## Purpose

```text
- Consume the accepted read-only GET /sleep/providers metadata contract in Flutter.
- Present the configured provider separately from SleepSummary.source.
- Present available / unavailable and real / demo state without inferring provider success.
- Simplify the normal Google Health user surface.
- Retain detailed Google Health diagnostics, preflight, self-check, state details,
  recovery actions, and developer fields below the Advanced Demo Tools boundary.
- Keep configured real Fitbit operator verification in W-5.
```

## App-facing presentation contract

The normal daily-loop surface adds one `Sleep Data Source` card.

```text
configured provider
  GET /sleep/providers configured_provider_label

actual data source
  /sleep/summary source rendered through SleepSummary.displaySource

data kind
  unavailable / real data / demo data / unverified

selection ownership
  backend configuration; a provider change requires backend restart
```

The UI must not treat these as equivalent:

```text
provider configured
provider token-like data detected
provider connection verified
real sleep data retrieved
```

### Mock-safe providers

`mock`, `wearable_stub`, and the deprecated `fitbit_stub` alias remain usable without external credentials. The normal card explains that external service connection is unnecessary.

### Google Health

The normal card shows only:

```text
- configured provider
- actual SleepSummary source and data kind
- short connection title/message
- user guidance
- next action
- safe refresh action
```

The following remain under Advanced Demo Tools:

```text
- state stage / reason / details
- recovery steps and grouped connection/retry/reset actions
- developer summary/details
- diagnostics
- preflight
- self-check
- real API guard and readiness fields
```

### Fitbit

The normal card may show the accepted W-2 local status classification and a guarded connect preparation action. It must also state that real OAuth, scope/permission, live token validity, real sleep retrieval, and smartphone Web acceptance remain W-5 work.

`Fitbit Operator Status` remains an advanced-only surface. W-4b does not set `verified=true`, does not infer `connected`, and does not perform real operator execution.

## Change surface

```text
app/lib/models/sleep_provider_selection.dart
app/lib/services/backend_api_client.dart
app/lib/screens/home_screen.dart
app/test/sleep_provider_selection_test.dart
app/test/widget_test.dart
docs/v210_flutter_sleep_provider_source_ui.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_fitbit_current_behavior_inventory.py
scripts/check_v210_fitbit_token_status_reconnect.py
scripts/check_v210_fitbit_real_sleep_normalization.py
scripts/check_v210_sleep_provider_selection_source_labels.py
scripts/check_v210_flutter_sleep_provider_source_ui.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

## Explicit non-change surface

```text
backend/app/**
backend/tests/**
app/pubspec.yaml
Fitbit OAuth/token/sleep runtime
Google Health OAuth/token/sleep runtime
post-advice chat runtime
voice-output artifact runtime
character display runtime
version metadata
v2.0.0 / v2.0.1 tags, GitHub Releases, fixed ZIPs, and publication records
```

## Mock-safe verification boundary

Normal verification uses only deterministic Flutter models and fake `BackendApiClient` implementations.

```text
- parse configured provider metadata;
- keep mock provider credential-free;
- avoid /fitbit/status when Fitbit is not configured;
- display configured provider separately from actual source;
- show Google Health concise user guidance in the normal card;
- keep detailed Google Health operator fields in the advanced card;
- keep Fitbit real operator verification explicitly pending;
- render no token, secret, raw payload, private path, or private sleep value.
```

Normal verification must not use:

```text
external network
OAuth browser
real authorization code
real token exchange or refresh
Fitbit live API
Google Health live API
raw provider payload
private operator evidence
```

## Accepted verification result

```text
implementation commit: 1fbea58
compileall: passed
W-1/W-2/W-3/W-4a/W-4b source-tree checks: passed
v2.0.x compatibility and maintenance guards: passed
focused Flutter provider model tests: 4 passed
focused Flutter widget tests: 35 passed
full backend pytest: 92 passed
full Flutter test: 57 passed
diff review: passed
operator approval: passed
real operator execution: false
release records changed: false
```

W-4b and parent phase W-4 were completed and accepted on 2026-07-23. W-5 is now `CURRENT / NOT_COMPLETED`; C-1 and later phases remain `PLANNED`. This mock-safe UI acceptance does not prove configured real Fitbit acceptance or smartphone Web real-provider acceptance.

## W-5b1 correction

Flutter now reads the backend `provider_options` field (the previous `available_providers` key was inconsistent), labels legacy Fitbit as migration-reference only, and removes the normal-user legacy OAuth action.
