# Rhythm report user-facing copy contract

## Position

v1.7.0 Day3 defines user-facing copy rules for the weekly/monthly rhythm report cards before changing Flutter layout or widget tests.

The goal is to keep the backend/API contract stable while making the app-side explanation easier to understand:

```text
backend labels → Flutter display helpers → History screen copy → widget/manual smoke checks
```

This document is source-tree only. It does not change runtime behavior, call external providers, create release artifacts, or rebuild the fixed v1.6.0 zip.

## Card titles and purpose

Keep the existing card titles for continuity:

```text
Weekly Rhythm Report
Monthly Rhythm Report
```

User-facing intro copy should explain the card as a saved-history reflection, not today's sleep result:

```text
過去のDailyRecordから作る軽いリズムレポートです。
今日の睡眠や健康状態の診断には使いません。
```

Allowed tone:

```text
lightweight reflection
saved history
reference memo
local/demo use
```

Avoid:

```text
diagnosis
treatment
guaranteed improvement
clinical scoring
alarmist health warnings
```

## Period and date range rules

The report period should be understandable without reading raw API field names.

Backend period/window rules remain:

```text
weekly: 7 days
monthly: 30 days
```

Flutter should display an explicit date range derived from `range_start` and `range_end`.

Recommended Japanese labels:

```text
レポート範囲: YYYY-MM-DD 〜 YYYY-MM-DD
対象期間: 週次 / 月次
```

The copy should make clear that the range is a saved-history window ending at `reference_date`, not a live health-provider query.

## Record coverage rules

Show total saved records and usable sleep records in plain language.

Backend fields:

```text
total_record_count
usable_sleep_record_count
display_coverage
```

Recommended user-facing labels:

```text
保存記録: N件
睡眠つき記録: N件
```

Keep `display_coverage` as a backend-provided compatibility field, but prefer clearer Flutter-side labels when polishing the History screen.

## Source-label display rules

Do not show raw source_label values directly to users in the polished History card.

Translate source_label into compact app-facing copy:

```text
saved_daily_record_history → 保存済みDailyRecord
saved_daily_record_history_with_mock_sleep → 保存済みDailyRecord（デモ睡眠データ）
saved_daily_record_history_with_real_sleep → 保存済みDailyRecord（実データを含む）
insufficient_saved_history → 保存済み履歴がまだ少ない状態
```

Recommended label prefix:

```text
データ元: ...
```

The raw value may remain useful in docs, tests, logs, or debug-only checks, but the default card should not look like a developer payload dump.

## Data-scope display rules

Do not show raw data_scope values directly to users in the polished History card.

Translate data_scope into compact app-facing copy:

```text
weekly_history → 週次の保存履歴
monthly_history → 月次の保存履歴
```

Recommended label prefix:

```text
集計範囲: ...
```

## Data-quality display rules

Do not show raw data_quality values as `Quality: usable` in the polished History card.

Translate data_quality into conservative app-facing copy:

```text
usable → 参考にしやすい記録数です
partial → 記録が少なめなので参考程度です
insufficient → まだ判断材料が少ないです
```

Recommended label prefix:

```text
記録状態: ...
```

## Sparse and empty-history copy rules

Sparse and empty states should encourage saving more records without blaming the user.

For `data_quality=partial`:

```text
記録が少なめなので、今は参考メモとして見てください。
```

For `data_quality=insufficient` or `source_label=insufficient_saved_history`:

```text
まだリズムを振り返るには記録が少なめです。DailyRecordをためると、ここで週や月の流れを見返せます。
```

Fallback when the API call fails or the card is not loaded yet should stay calm:

```text
リズムレポートはまだ読み込めていません。
履歴一覧と既存の週次まとめはそのまま確認できます。
```

Avoid wording that suggests a health problem, a failure, or a required provider setup.

## Caution and non-medical wording

Keep the existing safety message visible in or near each report card:

```text
今日の睡眠や健康状態の診断には使いません。
```

Acceptable optional expansion:

```text
これは保存済み履歴をもとにした軽い振り返りです。医療的な判断や改善保証ではありません。
```

Do not add medical advice, clinical analysis, disease-risk assessment, treatment guidance, or guaranteed sleep-improvement wording.

## Implementation direction for Day4

Day4 should update Flutter display helpers and the History screen card while preserving the existing backend/API contract.

Expected implementation targets:

```text
app/lib/models/rhythm_report.dart
app/lib/screens/history_screen.dart
```

Preferred helper direction:

```text
displayDateRange
displaySourceLabel
displayDataScope
displayDataQuality
```

Day4 should keep weekly/monthly report loading optional and safe. It should not require external LLM providers, real Google Health APIs, or AI Character Framework checkout.
