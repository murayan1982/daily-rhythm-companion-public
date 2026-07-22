# v2.0.x backend mock-safe regression foundation

Updated: 2026-07-22
Small commit: M-3
Status: CURRENT / NOT_COMPLETED

## Purpose

M-3 introduces a normal backend pytest suite for frequent local regression checks. It is intentionally separate from the historical v2.0.0 release-evidence and fixed-ZIP validation chain.

## Dependency boundary

Production dependencies remain in:

```text
backend/requirements.txt
```

Development test dependencies are added through:

```text
backend/requirements-dev.txt
```

The development file includes the production requirements and adds pytest. Pytest is not added to the backend runtime dependency list.

Test layout:

```text
backend/tests/**
- conftest.py
- test_core_api.py
- test_mock_advice.py
- test_daily_record_store.py
```

## Mock-safe boundary

The shared test configuration:

```text
- sets DRC_SKIP_BACKEND_DOTENV=1
- selects CONVERSATION_ENGINE=mock
- selects SLEEP_PROVIDER=mock
- removes known provider keys and real-execution opt-in variables
```

Normal M-3 tests must not require an AI Character Framework checkout, provider key, OAuth credential, token file, real health data, network call, audio generation, browser, or smartphone.

## Covered behavior

```text
health API
- status=ok
- active backend APP_VERSION

characters API
- gentle_mina / ミナ
- cheerful_sora / ソラ
- cool_rei / レイ

mock sleep API
- deterministic mock summary
- source=mock
- available=true
- is_real_data=false

mock advice
- stable character and AdviceSource metadata
- deterministic sleep/mood wording
- unavailable sleep does not produce an invented duration

DailyRecord tests use pytest tmp_path and cover:
- create/read
- same-date upsert
- advice source persistence
- temporary SQLite database only
```

## Explicit exclusions

```text
- Framework success/fallback regression: M-4
- voice artifact path and lookup safety: M-4
- chat/TTS lifecycle limits and cleanup: M-5
- CORS configuration: M-6
- Fitbit current-state contract: M-7
- real provider or OAuth execution
- runtime implementation changes
```

## Commands

From the repository root:

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m compileall -q backend scripts
python scripts\check_v20x_maintenance_baseline.py
python scripts\check_v20x_application_version_metadata.py
python scripts\check_v20x_backend_mock_safe_regression.py
python -m pytest -q backend/tests

cd app
flutter test
cd ..
```

The M-3 checker also invokes the backend pytest suite. The explicit pytest command remains documented so developers can run the normal regression suite directly.

## Non-release statement

M-3 does not create a fixed ZIP, tag, GitHub Release, or v2.0.1 release. It does not alter the published DRC_v2.0.0 asset or historical records.
