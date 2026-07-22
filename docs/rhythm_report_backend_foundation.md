# Rhythm report backend foundation

v1.6.0 adds a mock-safe backend foundation for weekly/monthly rhythm reports.

## Runtime scope

The backend foundation introduces:

```text
backend/app/models/rhythm_report.py
backend/app/services/rhythm_report_service.py
GET /daily-records/rhythm-report?period=weekly
GET /daily-records/rhythm-report?period=monthly
```

The service reads saved `DailyRecord` history only. It does not call external LLM providers, AI Character Framework, Google Health, Fitbit, or any real health API.

## Contract

The response model is `RhythmReport`.

Stable period values:

```text
weekly
monthly
```

Core fields:

```text
period
reference_date
range_start
range_end
days
label
total_record_count
usable_sleep_record_count
average_total_sleep_minutes
record_dates
display_title
display_label
display_summary
display_coverage
display_note
action_hint
source_label
data_scope
data_quality
is_medical_advice
```

## Labels

Weekly labels:

```text
insufficient_data
weekly_short
weekly_balanced
weekly_enough
```

Monthly labels:

```text
monthly_sparse
monthly_mixed
monthly_stable
monthly_enough
```

## Source labels

The report source is history-derived and saved-record based:

```text
saved_daily_record_history
saved_daily_record_history_with_mock_sleep
saved_daily_record_history_with_real_sleep
insufficient_saved_history
```

These labels describe the saved DailyRecord history used for the report. They must not expose raw provider payloads, authorization headers, token values, private prompts, or machine-specific local paths.

## Data quality

```text
insufficient
partial
usable
```

Weekly reports are considered usable from two usable sleep records. Monthly reports are considered usable from five usable sleep records. Sparse history returns conservative fallback wording instead of invented trends.

## Non-medical wording policy

Rhythm reports are lightweight reflection, not medical advice.

User-facing report text must avoid:

```text
diagnosis
treatment advice
medical score
health improvement guarantees
alarmist health claims
```

Required framing:

```text
過去のDailyRecordから作る軽い振り返りです。
今日の睡眠や健康状態の診断には使いません。
```

Sparse-history wording:

```text
記録が少ないので、今は参考メモとして見てください。
```

## Compatibility

`GET /daily-records/weekly-summary` and `WeeklySleepSummaryService` remain available. The new rhythm report API does not remove the older weekly summary endpoint and does not change the `DailyRecord` schema.

## Release safety

Day4/Day5 backend work is source-tree only. It does not create or rebuild release artifacts and does not change the fixed v1.5.0 release zip.
