# Rhythm report inventory

## Position

This document records the current DailyRecord, trend, weekly summary, API, and Flutter History surfaces that can support v1.6.0 Weekly/monthly rhythm reports.

Day2 is an inventory and boundary pass. It does not implement monthly reports yet, does not change the saved DailyRecord schema, and does not create or rebuild a release zip.

## Existing backend history model

Current saved history is based on `DailyRecordCreateRequest` and `DailyRecordResponse`.

Stable fields already available for report input:

```text
date
character_id
character_name
mood
sleep_summary
advice_message
advice_basis
advice_source
created_at
updated_at
```

Useful nested `SleepSummary` fields for conservative reports:

```text
sleep_summary.date
sleep_summary.total_sleep_minutes
sleep_summary.efficiency
sleep_summary.deep_sleep_minutes
sleep_summary.rem_sleep_minutes
sleep_summary.awake_minutes
sleep_summary.source
sleep_summary.available
sleep_summary.message
sleep_summary.sleep_start
sleep_summary.sleep_end
sleep_summary.quality_label
sleep_summary.confidence
sleep_summary.is_real_data
sleep_summary.unavailable_reason
```

Fields that are safe to use directly in v1.6.0 rhythm reports:

```text
- date, created_at, updated_at for ordering and coverage wording
- mood as a stable canonical mood ID
- character_id and character_name for grouping or lightweight context copy
- sleep_summary.available to decide whether a record is usable for sleep-duration summaries
- sleep_summary.total_sleep_minutes only when available and greater than zero
- sleep_summary.source / is_real_data / confidence for source and data-kind wording
- sleep_summary.quality_label as lightweight history metadata when present
- advice_basis / advice_source as source-label hints
```

Fields that should be treated carefully:

```text
- advice_message should not be reinterpreted as medical evidence
- efficiency, deep/rem/awake minutes should stay optional and provider-dependent
- unavailable_reason is useful for explanation but should not be shown as a raw technical failure label without friendly copy
```

## Existing backend store/query surface

`DailyRecordStore` already provides:

```text
upsert(request)
get(date)
list_recent(limit=30)
list_recent_sleep_available_records(reference_date, days=7, limit=7)
```

Current useful behavior:

```text
- records are ordered by date descending for recent history
- sleep-available history excludes unavailable sleep summaries
- sleep-available history excludes zero-minute summaries
- date-window filtering already exists for recent trend and weekly summary use
```

Day2 keeps this store contract stable. Monthly reports can start with the same pattern by using a wider day window before deciding whether a more general range query is needed.

## Existing backend report-like surfaces

The project already has two history-derived surfaces:

```text
RecentSleepTrendService
WeeklySleepSummaryService
```

Current API endpoints:

```text
GET /daily-records
GET /daily-records/recent-sleep-trend
GET /daily-records/weekly-summary
```

Existing labels and scopes:

```text
RecentSleepTrend.data_scope = recent_history
RecentSleepTrend.is_fallback_context = true
WeeklySleepSummary.data_scope = weekly_history
WeeklySleepSummary.is_medical_advice = false
```

These are good precedents for v1.6.0 because they already frame output as history/reference context and avoid treating history as today's measured sleep.

## Existing Flutter History surface

`HistoryScreen` already loads and displays:

```text
DailyRecord list
RecentSleepTrend
WeeklySleepSummary
```

Current Flutter model/client surfaces:

```text
app/lib/models/daily_record.dart
app/lib/models/recent_sleep_trend.dart
app/lib/models/weekly_sleep_summary.dart
app/lib/services/backend_api_client.dart
app/lib/screens/history_screen.dart
```

Existing Flutter behavior useful for v1.6.0:

```text
- History overview explains that records are historical reference information.
- Recent trend is loaded safely and can fail without blocking DailyRecord history.
- Weekly summary is loaded safely and can fail without blocking DailyRecord history.
- DailyRecord display copy separates unavailable sleep, mock/sample data, real data, and advice basis.
```

## Current weekly-summary foundation

Weekly summary already exists as a lightweight foundation.

Available fields:

```text
reference_date
days
label
usable_record_count
average_total_sleep_minutes
recent_dates
display_title
display_label
display_summary
display_coverage
display_note
action_hint
data_scope
is_medical_advice
```

Current labels:

```text
weekly_short
weekly_balanced
weekly_enough
insufficient_data
```

For v1.6.0, this can either be kept as the weekly report surface or wrapped into a broader rhythm report contract later. Day2 does not rename or remove the existing weekly summary endpoint.

## Current monthly-report gap

There is no dedicated monthly report model, service, endpoint, Dart model, API client method, or History UI card yet.

Missing monthly-specific surfaces:

```text
backend/app/models/monthly_rhythm_report.py
backend/app/services/monthly_rhythm_report_service.py
GET /daily-records/monthly-summary or equivalent
app/lib/models/monthly_rhythm_report.dart
BackendApiClient.fetchMonthlyRhythmReport or equivalent
HistoryScreen monthly report card
monthly report tests/checks
```

Day3 should define whether monthly reports reuse a generic rhythm-report model or get a separate monthly model. Day4/Day5 can then add the mock-safe backend foundation.

## Recommended v1.6.0 report inputs

The first implementation should use only saved DailyRecord history and should not fetch real provider data directly.

Recommended input rules:

```text
- Use DailyRecordStore as the report source.
- Use records within an explicit date window.
- Count coverage using all records in the window when useful.
- Use sleep-duration averages only from available records with positive total_sleep_minutes.
- Include recent_dates or covered_dates only as saved record dates, not provider raw event timestamps.
- Preserve canonical mood IDs; convert to display copy only at presentation boundaries.
- Keep character fields as optional context, not as a report identity system.
```

## Recommended source/data labels

Existing scopes should remain valid:

```text
recent_history
weekly_history
```

Suggested future scopes:

```text
monthly_history
rhythm_report_history
daily_record_history
mock_history
```

Source labels should make it clear whether a report is:

```text
- built from saved DailyRecord history
- based on mock/sample sleep data
- based on explicitly configured real-data records already saved as DailyRecords
- unavailable or too sparse
- optional framework/fallback wording in the future
```

Avoid implying that a weekly/monthly report directly queried a provider unless that behavior is explicitly implemented, guarded, and labeled.

## Conservative wording boundaries

Report wording must stay conservative and non-medical.

Allowed report wording:

```text
- "過去のDailyRecordから作る軽い振り返りです。"
- "直近の使える記録では..."
- "記録が少ないので参考程度です。"
- "短め寄り / ほどほど安定 / 確保できた日が多め"
- "今日の睡眠や健康状態の診断には使いません。"
```

Avoid report wording:

```text
- diagnosis-like labels
- treatment advice
- guaranteed improvement claims
- alarmist sleep scoring
- "健康状態が悪い" style assertions
- presenting history-derived averages as today's sleep measurement
- exposing raw provider payloads, tokens, local data paths, authorization headers, or private prompts
```

## Day2 conclusion

v1.6.0 can start from the existing DailyRecord history, RecentSleepTrend, and WeeklySleepSummary surfaces.

The safest next step is Day3: define the weekly/monthly rhythm report contract and source-label policy before adding a monthly backend implementation.
