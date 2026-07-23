# v2.1.0 W-4a — Sleep-provider selection status contract

Updated: 2026-07-23
Status: COMPLETED / ACCEPTED
Parent phase: W-4 CURRENT / NOT_COMPLETED

## Purpose

```text
- Expose the backend-owned SLEEP_PROVIDER selection as a read-only app contract.
- Separate configured provider metadata from the SleepSummary data source.
- Keep credentials, OAuth, tokens, refresh, and provider execution outside this endpoint.
- Preserve the accepted W-3 Fitbit API/normalization/SleepSummary contract.
- Prepare the later Flutter provider/source-label UI without completing W-4 or W-5.
```

## Endpoint

```text
GET /sleep/providers
```

The endpoint returns configuration metadata only. It does not instantiate a sleep
provider, retrieve sleep data, read provider token stores, refresh a token, open an
OAuth browser, or call an external API.

## Response contract

```text
configured_provider
configured_provider_label
configured_provider_role
configured_provider_supported
selection_mode=backend_config
change_requires_backend_restart=true
available_providers[]
message
```

Each available provider entry contains:

```text
provider
display_label
role
deprecated
alias_for
real_operator_verification_required
```

## Provider roles

```text
mock
  role: credential_free_default
  label: サンプルデータ

wearable_stub
  role: deterministic_sample
  label: ウェアラブル連携サンプル

existing google_health
  role: configured_real_provider
  label: Google Health

fitbit_stub
  role: deprecated_alias
  alias_for: wearable_stub
  label: ウェアラブル連携サンプル（旧設定）

fitbit
  role: legacy_real_provider
  real_operator_verification_required: true
  label: Fitbit（実利用検証待ち）
```

The Fitbit wording remains conservative. Source presence, local token-like data,
fake HTTP success, or this metadata endpoint does not establish configured real
Fitbit acceptance.

## Configured provider and data source are different

```text
configured provider
  Backend SLEEP_PROVIDER configuration returned by GET /sleep/providers.

app-facing data source
  SleepSummary.source returned by GET /sleep/summary.

real/demo availability
  SleepSummary.available and SleepSummary.is_real_data.
```

The later Flutter UI must present these concepts separately rather than treating a
configured provider as proof of successful real data retrieval.

## Unknown provider behavior

An unknown configured value is reported conservatively:

```text
configured_provider_supported=false
configured_provider_role=unsupported
configured_provider_label=未対応のsleep provider設定
```

The status endpoint itself remains readable so the UI can explain the invalid
configuration. Existing `/sleep/summary` unsupported-provider behavior is unchanged.

## W-4a change surface

```text
backend/app/main.py
backend/app/api/sleep_provider_selection.py
backend/app/models/sleep_provider_selection.py
backend/app/services/sleep_provider_selection_service.py
backend/tests/test_sleep_provider_selection_contract.py
docs/v210_sleep_provider_selection_source_labels.md
docs/DRC_v210_goal_checklist_small_commit.md
scripts/check_v210_sleep_provider_selection_source_labels.py
README.md
roadmap.md
tasklist.md
scripts/README.md
```

## Explicit non-change surface

```text
backend/app/api/sleep.py
backend/app/models/sleep.py
backend/app/services/sleep_providers/factory.py
backend/app/services/fitbit_api_client.py
backend/app/services/fitbit_sleep_service.py
backend/app/services/fitbit_sleep_normalizer.py
backend/app/services/sleep_providers/fitbit.py
backend/tests/test_fitbit_real_sleep_normalization.py
app/lib/**
app/test/**
app/pubspec.yaml
Fitbit and Google Health OAuth/token/runtime services
post-advice chat, voice output, and character runtime
version metadata
v2.0.0 / v2.0.1 release records, tags, GitHub Releases, and fixed ZIPs
```

## Mock-safe verification boundary

Allowed:

```text
- AppConfig instances with deterministic provider names.
- FastAPI TestClient against the read-only metadata route.
- Response classification and alias regression tests.
- Source-tree checks and immutable release-record hashes.
```

Not allowed or required:

```text
- backend/local_data access
- real credentials or tokens
- OAuth browser or callback execution
- token exchange or refresh
- external network requests
- real Fitbit or Google Health sleep retrieval
- raw provider payloads or exact private sleep values
- smartphone Web acceptance evidence
```

## Acceptance conditions

W-4a acceptance required all of the following to pass:

```text
- compileall
- accepted W-1/W-2/W-3 checks
- W-4a source-tree check
- v2.0.x compatibility and maintenance guards
- focused and full backend pytest
- full Flutter test, even though W-4a changes no Flutter file
- diff review
- operator approval
```

## Accepted verification result

```text
implementation commit: 1619b0b
compileall: passed
accepted W-1/W-2/W-3 checks: passed
W-4a source-tree check: passed
v2.0.x compatibility and maintenance guards: passed
focused backend pytest: 8 passed
full backend pytest: 92 passed
full Flutter test: 50 passed
diff review: passed
operator approval: passed
real operator execution: false
release records changed: false
```

W-4a was completed and accepted on 2026-07-23. W-4 remains CURRENT /
NOT_COMPLETED and W-4b is now CURRENT / NOT_COMPLETED. Flutter provider/source
labels and simplified Google Health user UX remain the next W-4 implementation work.
Configured real Fitbit operator verification remains W-5.

## W-5b1 correction

The accepted W-4a API shape remains, but `fitbit` is now labeled as a legacy migration reference and no longer requires configured-real operator verification. `google_health` is the configured-real provider.
