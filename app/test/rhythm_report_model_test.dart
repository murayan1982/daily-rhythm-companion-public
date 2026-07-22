import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/rhythm_report.dart';

void main() {
  test('RhythmReport display helpers translate weekly usable report metadata', () {
    const report = RhythmReport(
      period: 'weekly',
      referenceDate: '2026-05-17',
      rangeStart: '2026-05-11',
      rangeEnd: '2026-05-17',
      days: 7,
      label: 'weekly_short',
      totalRecordCount: 3,
      usableSleepRecordCount: 3,
      averageTotalSleepMinutes: 340,
      recordDates: ['2026-05-08', '2026-05-07', '2026-05-06'],
      displayTitle: 'Weekly Rhythm Report',
      displayLabel: '週次リズムは短め寄り',
      displaySummary: '保存済み記録から見ると、平均睡眠は5時間40分で短め寄りです。',
      displayCoverage: '対象: 直近7日 / 保存記録: 3件 / 使用記録: 3件',
      displayNote: '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
      actionHint: '短めの日が続く時は、無理な予定を詰めすぎない参考にしてください。',
      sourceLabel: 'saved_daily_record_history_with_mock_sleep',
      dataScope: 'weekly_history',
      dataQuality: 'usable',
      isMedicalAdvice: false,
    );

    expect(report.displayDateRange, 'レポート範囲: 2026-05-11 〜 2026-05-17');
    expect(report.displayRecordCoverage, '保存記録: 3件 / 睡眠つき記録: 3件');
    expect(report.displaySourceLabel, 'データ元: 保存済みDailyRecord（デモ睡眠データ）');
    expect(report.displayDataScope, '集計範囲: 週次の保存履歴');
    expect(report.displayDataQuality, '記録状態: 参考にしやすい記録数です');
  });

  test('RhythmReport display helpers keep sparse and insufficient states conservative', () {
    const monthlyReport = RhythmReport(
      period: 'monthly',
      referenceDate: '2026-05-17',
      rangeStart: '2026-04-18',
      rangeEnd: '2026-05-17',
      days: 30,
      label: 'monthly_sparse',
      totalRecordCount: 3,
      usableSleepRecordCount: 1,
      averageTotalSleepMinutes: null,
      recordDates: ['2026-05-08'],
      displayTitle: 'Monthly Rhythm Report',
      displayLabel: '月次レポートはまだ参考程度',
      displaySummary: '月次としては記録が少ないので、今は参考メモとして見てください。',
      displayCoverage: '対象: 直近30日 / 保存記録: 3件 / 使用記録: 1件',
      displayNote: '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
      actionHint: 'まずはDailyRecordをためて、あとで月の流れを見返します。',
      sourceLabel: 'saved_daily_record_history_with_real_sleep',
      dataScope: 'monthly_history',
      dataQuality: 'partial',
      isMedicalAdvice: false,
    );

    final insufficientReport = RhythmReport.fromJson(const <String, dynamic>{
      'period': 'weekly',
      'reference_date': '2026-05-17',
      'total_record_count': 0,
      'usable_sleep_record_count': 0,
      'source_label': 'insufficient_saved_history',
      'data_scope': 'weekly_history',
      'data_quality': 'insufficient',
    });

    expect(monthlyReport.displayDataQuality, '記録状態: 記録が少なめなので参考程度です');
    expect(monthlyReport.displaySourceLabel, 'データ元: 保存済みDailyRecord（実データを含む）');
    expect(monthlyReport.displayDataScope, '集計範囲: 月次の保存履歴');
    expect(insufficientReport.displayDateRange, 'レポート範囲: 週次 / 基準日: 2026-05-17');
    expect(insufficientReport.displayRecordCoverage, '保存記録: 0件 / 睡眠つき記録: 0件');
    expect(insufficientReport.displaySourceLabel, 'データ元: 保存済み履歴がまだ少ない状態');
    expect(insufficientReport.displayDataQuality, '記録状態: まだ判断材料が少ないです');
  });
}
