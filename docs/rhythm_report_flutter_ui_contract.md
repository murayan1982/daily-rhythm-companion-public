# Rhythm report Flutter UI contract

v1.6.0 Day6 adds the Flutter presentation path for weekly/monthly rhythm reports.

## Placement

Rhythm reports are shown on the existing History screen, not on the Home screen.

The History screen order is:

```text
History / DailyRecord overview
Recent Sleep Trend
Simple Weekly Summary
Weekly Rhythm Report
Monthly Rhythm Report
DailyRecord list
```

Why:

```text
- rhythm reports are history-derived, not today's sleep result.
- History already owns DailyRecord review and conservative trend wording.
- Home should stay focused on today's loop: sleep, mood, character, advice, save.
```

## API usage

Flutter uses the Day5 API through `BackendApiClient.fetchRhythmReport`.

```text
GET /daily-records/rhythm-report?period=weekly
GET /daily-records/rhythm-report?period=monthly
```

The UI model is:

```text
app/lib/models/rhythm_report.dart
```

Stable display fields:

```text
displayTitle
displayLabel
displaySummary
displayCoverage
displayNote
actionHint
sourceLabel
dataScope
dataQuality
isMedicalAdvice
```

## User-facing card policy

Each rhythm report card must show:

```text
- display title
- lightweight history-derived framing
- non-diagnosis boundary
- display label
- formatted average sleep if available
- data quality
- display summary
- coverage
- record dates
- source label
- data scope
- action hint
- display note
```

The source label and data quality should remain visible enough for demo/debug review:

```text
Source: saved_daily_record_history_with_mock_sleep
Scope: weekly_history
Quality: usable
```

## Safe fallback behavior

The History screen loads weekly and monthly rhythm reports safely. If a rhythm report request fails, the History screen still shows:

```text
- DailyRecord overview
- Recent Sleep Trend if available
- Simple Weekly Summary if available
- saved DailyRecord list
```

Unavailable report text:

```text
週次リズムレポート: 読み込み未完了
月次リズムレポート: 読み込み未完了
履歴一覧と既存の週次まとめはそのまま確認できます。
```

## Non-medical wording

Rhythm reports remain lightweight reflection.

Required wording:

```text
過去のDailyRecordから作る軽いリズムレポートです。
今日の睡眠や健康状態の診断には使いません。
```

The UI must not present reports as:

```text
- diagnosis
- treatment advice
- medical score
- today's sleep result
- health improvement guarantee
```

## Compatibility

Day6 keeps existing History cards and routes visible:

```text
Recent Sleep Trend
Simple Weekly Summary
DailyRecord list
```

The new cards do not remove `WeeklySleepSummary` and do not change the saved `DailyRecord` schema.
