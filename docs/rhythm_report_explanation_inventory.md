# Rhythm report explanation inventory

## Position

v1.7.0 Day2 inventories the current v1.6.0 rhythm report explanation surfaces before changing Flutter copy or layout.

The purpose is to make the next UI polish small and testable:

```text
backend contract → API payload → Flutter model → History screen card → widget/manual smoke checks
```

This inventory is source-tree only. It does not change runtime behavior, call external providers, create release artifacts, or rebuild the fixed v1.6.0 zip.

## Current backend contract surface

Current backend model:

```text
backend/app/models/rhythm_report.py
```

Current stable payload fields:

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

Current stable period values:

```text
weekly
monthly
```

Current source labels:

```text
saved_daily_record_history
saved_daily_record_history_with_mock_sleep
saved_daily_record_history_with_real_sleep
insufficient_saved_history
```

Current data-quality labels:

```text
insufficient
partial
usable
```

Current data scopes:

```text
weekly_history
monthly_history
```

## Current backend service behavior

Current service:

```text
backend/app/services/rhythm_report_service.py
```

Current window rules:

```text
weekly: 7 days including reference_date
monthly: 30 days including reference_date
```

Current usable-record thresholds:

```text
weekly minimum usable sleep records: 2
monthly minimum usable sleep records: 5
```

Current summary behavior:

```text
- Records are filtered from saved DailyRecord history.
- Usable sleep records require sleep_summary.available and positive total_sleep_minutes.
- average_total_sleep_minutes is calculated from usable sleep records only.
- data_quality is insufficient when usable count is 0.
- data_quality is partial when usable count is below the period threshold.
- data_quality is usable when usable count meets the period threshold.
- source_label is based on usable record source kind.
- is_medical_advice remains false.
```

Current display_coverage format:

```text
対象: 直近7日 / 保存記録: N件 / 使用記録: N件
対象: 直近30日 / 保存記録: N件 / 使用記録: N件
```

Day2 finding:

```text
display_coverage includes period length and counts, but the History card does not display range_start / range_end as an explicit date range yet.
```

## Current API surface

Current API file:

```text
backend/app/api/daily_records.py
```

Current API endpoint:

```http
GET /daily-records/rhythm-report?period=weekly
GET /daily-records/rhythm-report?period=monthly
```

Optional reference-date query:

```http
GET /daily-records/rhythm-report?period=weekly&reference_date=YYYY-MM-DD
```

Current API behavior:

```text
- period defaults to weekly.
- reference_date defaults to Date.today().isoformat().
- the response_model is RhythmReport.
- the endpoint is under the DailyRecord history surface, not the sleep summary surface.
```

Day2 finding:

```text
The API already exposes enough raw fields for better UI explanation without changing the backend contract.
```

## Current Flutter model surface

Current Flutter model:

```text
app/lib/models/rhythm_report.dart
```

Current useful presentation helpers:

```text
hasUsableReport
formattedAverageSleep
displayRecordDates
displayPeriodLabel
```

Current fallback defaults:

```text
source_label defaults to insufficient_saved_history
data_quality defaults to insufficient
display_summary defaults to sparse-history reference copy
display_note defaults to non-diagnosis wording
```

Day2 finding:

```text
The Flutter model has rangeStart and rangeEnd fields, but there is no dedicated displayDateRange helper yet.
```

## Current History screen surface

Current screen:

```text
app/lib/screens/history_screen.dart
```

Current History order:

```text
History / DailyRecord overview
Recent Sleep Trend
Simple Weekly Summary
Weekly Rhythm Report
Monthly Rhythm Report
DailyRecord list
```

Current rhythm report card displays:

```text
displayTitle
history-derived framing
non-diagnosis boundary
displayLabel
formattedAverageSleep
dataQuality
displaySummary
displayCoverage
displayRecordDates
sourceLabel
dataScope
actionHint
displayNote
```

Current unavailable report fallback text:

```text
週次リズムレポート: 読み込み未完了
月次リズムレポート: 読み込み未完了
履歴一覧と既存の週次まとめはそのまま確認できます。
```

Day2 finding:

```text
The card is functionally transparent but debug-like. `Source: ...`, `Scope: ...`, and `Quality: ...` are useful for development, but app-side explanation could be friendlier while still keeping labels visible for demo review.
```

## Current widget-test surface

Current widget test:

```text
app/test/widget_test.dart
```

Current rhythm report assertions cover:

```text
Weekly Rhythm Report
Monthly Rhythm Report
data quality labels
source label visibility
scope label visibility
summary and conservative wording through shared History expectations
```

Day2 finding:

```text
The test already protects source, scope, and quality visibility. Day5 should update or extend it after Day4 changes the user-facing card copy.
```

## Explanation gaps to address after Day2

Day3 should define copy rules for these gaps before code changes:

```text
- display an explicit date range using range_start / range_end.
- explain total_record_count and usable_sleep_record_count in friendlier wording.
- translate source_label into user-facing source copy while preserving the raw label where useful.
- translate data_quality into user-facing quality copy while preserving the raw label where useful.
- keep sparse-history and unavailable-report wording conservative.
- avoid making monthly partial reports sound stronger than the available data allows.
- avoid presenting reports as today's sleep result, diagnosis, treatment advice, medical score, or improvement guarantee.
```

Day4 should then polish Flutter UI using existing backend fields first. Backend contract changes should be avoided unless Day3 finds a concrete missing field.

## Recommended Day3 direction

Recommended Day3 output:

```text
docs/rhythm_report_explanation_copy_rules.md
```

Recommended copy-rule categories:

```text
- card introduction
- date range
- record coverage
- data quality
- source label
- sparse history
- unavailable report fallback
- non-medical boundary
- debug/raw-label visibility
```

## Safety notes

v1.7.0 explanation polish must keep these boundaries:

```text
- mock-safe checks stay default.
- no external LLM provider call is required.
- no real Google Health / Fitbit call is required.
- no AI Character Framework checkout is required.
- reports remain saved-history reflections.
- reports are not today's sleep result.
- reports are not medical advice, diagnosis, treatment guidance, or health improvement guarantees.
- fixed v1.6.0 release zip is not rebuilt.
```
