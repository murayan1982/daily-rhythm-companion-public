class ReportHandoffContext {
  const ReportHandoffContext({
    required this.period,
    required this.rangeStart,
    required this.rangeEnd,
    required this.label,
    required this.reportSummary,
    required this.actionHint,
    required this.sourceLabel,
    required this.dataScope,
    required this.dataQuality,
    required this.totalRecordCount,
    required this.usableSleepRecordCount,
    required this.isMedicalAdvice,
    required this.shouldInformAdvice,
    required this.adviceBasisPrefix,
    required this.userFacingSourceLabel,
    required this.userFacingScopeLabel,
    required this.userFacingQualityLabel,
    required this.userFacingSummary,
    required this.promptGuidance,
  });

  final String period;
  final String rangeStart;
  final String rangeEnd;
  final String label;
  final String reportSummary;
  final String actionHint;
  final String sourceLabel;
  final String dataScope;
  final String dataQuality;
  final int totalRecordCount;
  final int usableSleepRecordCount;
  final bool isMedicalAdvice;
  final bool shouldInformAdvice;
  final String adviceBasisPrefix;
  final String userFacingSourceLabel;
  final String userFacingScopeLabel;
  final String userFacingQualityLabel;
  final String userFacingSummary;
  final String promptGuidance;

  factory ReportHandoffContext.fromJson(Map<String, dynamic> json) {
    return ReportHandoffContext(
      period: json['period']?.toString() ?? '',
      rangeStart: json['range_start']?.toString() ?? '',
      rangeEnd: json['range_end']?.toString() ?? '',
      label: json['label']?.toString() ?? '',
      reportSummary: json['display_summary']?.toString() ?? '',
      actionHint: json['action_hint']?.toString() ?? '',
      sourceLabel: json['source_label']?.toString() ?? '',
      dataScope: json['data_scope']?.toString() ?? '',
      dataQuality: json['data_quality']?.toString() ?? '',
      totalRecordCount: _intValue(json['total_record_count']),
      usableSleepRecordCount: _intValue(json['usable_sleep_record_count']),
      isMedicalAdvice: json['is_medical_advice'] == true,
      shouldInformAdvice: json['should_inform_advice'] == true,
      adviceBasisPrefix: json['advice_basis_prefix']?.toString() ?? 'none',
      userFacingSourceLabel: json['user_facing_source_label']?.toString() ?? '',
      userFacingScopeLabel: json['user_facing_scope_label']?.toString() ?? '',
      userFacingQualityLabel: json['user_facing_quality_label']?.toString() ?? '',
      userFacingSummary: json['user_facing_summary']?.toString() ?? '',
      promptGuidance: json['prompt_guidance']?.toString() ?? '',
    );
  }


  Map<String, dynamic> toJson() {
    return {
      'period': period,
      'range_start': rangeStart,
      'range_end': rangeEnd,
      'label': label,
      'display_summary': reportSummary,
      'action_hint': actionHint,
      'source_label': sourceLabel,
      'data_scope': dataScope,
      'data_quality': dataQuality,
      'total_record_count': totalRecordCount,
      'usable_sleep_record_count': usableSleepRecordCount,
      'is_medical_advice': isMedicalAdvice,
      'should_inform_advice': shouldInformAdvice,
      'advice_basis_prefix': adviceBasisPrefix,
      'user_facing_source_label': userFacingSourceLabel,
      'user_facing_scope_label': userFacingScopeLabel,
      'user_facing_quality_label': userFacingQualityLabel,
      'user_facing_summary': userFacingSummary,
      'prompt_guidance': promptGuidance,
    };
  }

  bool get shouldShowAsAdviceContext {
    return shouldInformAdvice &&
        !isMedicalAdvice &&
        adviceBasisPrefix != 'none';
  }

  String get displayPeriodLabel {
    switch (period) {
      case 'weekly':
        return '週次レポート';
      case 'monthly':
        return '月次レポート';
      case '':
        return 'リズムレポート';
      default:
        return 'リズムレポート';
    }
  }

  String get displayAdviceContextLabel {
    if (adviceBasisPrefix == 'rhythm_report_partial') {
      return '$displayPeriodLabelを参考程度に反映';
    }

    if (adviceBasisPrefix == 'rhythm_report') {
      return '$displayPeriodLabelも参考';
    }

    return 'レポートは参考外';
  }

  String get displayReflectionLabel {
    if (adviceBasisPrefix == 'rhythm_report_partial') {
      return '$displayPeriodLabelを参考程度にした振り返り';
    }

    if (adviceBasisPrefix == 'rhythm_report') {
      return '$displayPeriodLabelも参考にした振り返り';
    }

    return 'レポートは今回の振り返りには使っていません';
  }

  String get displayDateRange {
    final start = rangeStart.trim();
    final end = rangeEnd.trim();

    if (start.isNotEmpty && end.isNotEmpty) {
      return '範囲: $start 〜 $end';
    }

    return '範囲: $displayPeriodLabel';
  }

  String get displayRecordCoverage {
    return '保存記録: $totalRecordCount件 / 睡眠つき記録: $usableSleepRecordCount件';
  }

  String get displaySource {
    return _displayOrFallback(userFacingSourceLabel, _sourceLabelFallback);
  }

  String get displayScope {
    return _displayOrFallback(userFacingScopeLabel, _scopeFallback);
  }

  String get displayQuality {
    return _displayOrFallback(userFacingQualityLabel, _qualityFallback);
  }

  String get displayUserFacingSummary {
    return _displayOrFallback(userFacingSummary, reportSummary);
  }

  String get displayActionHint {
    return _displayOrFallback(actionHint, '今日は気分と手元の睡眠情報を中心に、無理なく整えます。');
  }

  String get displaySafetyNote {
    return '過去の保存記録から見た軽い参考情報です。今日の睡眠や健康状態の診断としては扱いません。';
  }

  String get _sourceLabelFallback {
    switch (sourceLabel) {
      case 'saved_daily_record_history_with_mock_sleep':
        return '保存済みDailyRecord（デモ睡眠データ）からの振り返り';
      case 'saved_daily_record_history_with_real_sleep':
        return '保存済みDailyRecord（連携睡眠データ）からの振り返り';
      case 'saved_daily_record_history':
        return '保存済みDailyRecordからの振り返り';
      case 'insufficient_saved_history':
        return '保存済み記録が少ないため参考表示';
      default:
        return '保存済みDailyRecordからの振り返り';
    }
  }

  String get _scopeFallback {
    switch (dataScope) {
      case 'weekly_history':
        return '週次の保存履歴';
      case 'monthly_history':
        return '月次の保存履歴';
      default:
        return '保存履歴';
    }
  }

  String get _qualityFallback {
    switch (dataQuality) {
      case 'usable':
        return '参考にしやすい保存記録があります';
      case 'partial':
        return '保存記録が少なめなので参考程度です';
      case 'insufficient':
        return 'レポートに使える保存記録がまだ少ないです';
      default:
        return '記録状態を確認中です';
    }
  }

  static int _intValue(dynamic value) {
    if (value is int) {
      return value;
    }

    return int.tryParse(value?.toString() ?? '') ?? 0;
  }

  static String _displayOrFallback(String value, String fallback) {
    final text = value.trim();

    if (text.isNotEmpty) {
      return text;
    }

    final fallbackText = fallback.trim();
    return fallbackText.isEmpty ? '-' : fallbackText;
  }
}
