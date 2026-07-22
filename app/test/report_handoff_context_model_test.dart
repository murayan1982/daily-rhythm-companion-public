import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/advice_source.dart';
import 'package:app/models/daily_record.dart';
import 'package:app/models/report_handoff_context.dart';
import 'package:app/models/sleep_summary.dart';

void main() {
  test('ReportHandoffContext display helpers keep report metadata user-facing', () {
    final context = ReportHandoffContext.fromJson(const <String, dynamic>{
      'period': 'weekly',
      'range_start': '2026-05-11',
      'range_end': '2026-05-17',
      'label': 'weekly_balanced',
      'display_summary': '保存済み記録から見ると、平均睡眠は6h 30mです。',
      'action_hint': '予定を詰めすぎず休憩を先に置くとよさそうです。',
      'source_label': 'saved_daily_record_history_with_mock_sleep',
      'data_scope': 'weekly_history',
      'data_quality': 'usable',
      'total_record_count': 3,
      'usable_sleep_record_count': 3,
      'is_medical_advice': false,
      'should_inform_advice': true,
      'advice_basis_prefix': 'rhythm_report',
      'user_facing_source_label': '保存済みDailyRecord（デモ睡眠データ）からの振り返り',
      'user_facing_scope_label': '週次の保存履歴',
      'user_facing_quality_label': '参考にしやすい保存記録があります',
      'user_facing_summary': '過去の保存記録から見た軽い振り返りとして扱います。',
      'prompt_guidance': 'Use this report as lightweight historical context only.',
    });

    expect(context.shouldShowAsAdviceContext, isTrue);
    expect(context.displayAdviceContextLabel, '週次レポートも参考');
    expect(context.displayReflectionLabel, '週次レポートも参考にした振り返り');
    expect(context.displayDateRange, '範囲: 2026-05-11 〜 2026-05-17');
    expect(context.displayRecordCoverage, '保存記録: 3件 / 睡眠つき記録: 3件');
    expect(context.displaySource, '保存済みDailyRecord（デモ睡眠データ）からの振り返り');
    expect(context.displayScope, '週次の保存履歴');
    expect(context.displayQuality, '参考にしやすい保存記録があります');
  });

  test('AdviceSource and DailyRecord reflection helpers parse report_handoff', () {
    final source = AdviceSource.fromJson(const <String, dynamic>{
      'engine': 'mock',
      'drc_character_id': 'gentle_mina',
      'drc_character_name': 'ミナ',
      'report_handoff': <String, dynamic>{
        'period': 'monthly',
        'range_start': '2026-04-18',
        'range_end': '2026-05-17',
        'label': 'monthly_sparse',
        'display_summary': '月次としては記録が少ないので、今は参考メモとして見てください。',
        'action_hint': 'まずはDailyRecordをためて、あとで月の流れを見返します。',
        'source_label': 'saved_daily_record_history_with_real_sleep',
        'data_scope': 'monthly_history',
        'data_quality': 'partial',
        'total_record_count': 3,
        'usable_sleep_record_count': 1,
        'is_medical_advice': false,
        'should_inform_advice': true,
        'advice_basis_prefix': 'rhythm_report_partial',
        'user_facing_source_label': '保存済みDailyRecord（連携睡眠データ）からの振り返り',
        'user_facing_scope_label': '月次の保存履歴',
        'user_facing_quality_label': '保存記録が少なめなので参考程度です',
        'user_facing_summary': '保存記録が少なめなので、レポート要素は参考程度に扱います。',
        'prompt_guidance': 'Use this report only as low-confidence historical context.',
      },
    });

    final record = DailyRecord(
      date: '2026-05-17',
      characterId: 'gentle_mina',
      characterName: 'ミナ',
      mood: 'normal',
      sleepSummary: const SleepSummary(
        date: '2026-05-17',
        totalSleepMinutes: 390,
        efficiency: 88,
        source: 'mock',
        available: true,
        qualityLabel: 'fair',
        confidence: 'mock',
        isRealData: false,
      ),
      adviceMessage: '今日は無理なく整えましょう。',
      adviceBasis: 'rhythm_report_partial+mood+character+mock',
      adviceSource: source,
      createdAt: '2026-05-17T00:00:00Z',
      updatedAt: '2026-05-17T00:00:00Z',
    );

    expect(source.hasReportHandoff, isTrue);
    expect(source.displayReportHandoffLabel, '月次レポートを参考程度に反映');
    expect(record.displayAdviceBasis, 'リズムレポートを参考程度にしたアドバイス');
    expect(record.hasReportReflection, isTrue);
    expect(record.displayReportReflectionLabel, '月次レポートを参考程度にした振り返り');
    expect(record.displayReportReflectionSource, '保存済みDailyRecord（連携睡眠データ）からの振り返り');
  });
}
