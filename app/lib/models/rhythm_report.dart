class RhythmReport {
  const RhythmReport({
    required this.period,
    required this.referenceDate,
    required this.rangeStart,
    required this.rangeEnd,
    required this.days,
    required this.label,
    required this.totalRecordCount,
    required this.usableSleepRecordCount,
    this.averageTotalSleepMinutes,
    this.recordDates = const [],
    required this.displayTitle,
    required this.displayLabel,
    required this.displaySummary,
    required this.displayCoverage,
    required this.displayNote,
    required this.actionHint,
    required this.sourceLabel,
    required this.dataScope,
    required this.dataQuality,
    this.isMedicalAdvice = false,
  });

  final String period;
  final String referenceDate;
  final String rangeStart;
  final String rangeEnd;
  final int days;
  final String label;
  final int totalRecordCount;
  final int usableSleepRecordCount;
  final int? averageTotalSleepMinutes;
  final List<String> recordDates;
  final String displayTitle;
  final String displayLabel;
  final String displaySummary;
  final String displayCoverage;
  final String displayNote;
  final String actionHint;
  final String sourceLabel;
  final String dataScope;
  final String dataQuality;
  final bool isMedicalAdvice;

  factory RhythmReport.fromJson(Map<String, dynamic> json) {
    final normalizedPeriod = json['period']?.toString() ?? 'weekly';

    return RhythmReport(
      period: normalizedPeriod,
      referenceDate: json['reference_date']?.toString() ?? '',
      rangeStart: json['range_start']?.toString() ?? '',
      rangeEnd: json['range_end']?.toString() ?? '',
      days: json['days'] as int? ?? _defaultDaysForPeriod(normalizedPeriod),
      label: json['label']?.toString() ?? 'insufficient_data',
      totalRecordCount: json['total_record_count'] as int? ?? 0,
      usableSleepRecordCount: json['usable_sleep_record_count'] as int? ?? 0,
      averageTotalSleepMinutes: json['average_total_sleep_minutes'] as int?,
      recordDates: _parseStringList(json['record_dates']),
      displayTitle: json['display_title']?.toString() ??
          _defaultTitleForPeriod(normalizedPeriod),
      displayLabel: json['display_label']?.toString() ??
          _defaultLabelForPeriod(normalizedPeriod),
      displaySummary: json['display_summary']?.toString() ??
          '記録が少ないので、今は参考メモとして見てください。',
      displayCoverage: json['display_coverage']?.toString() ??
          '対象: 直近${_defaultDaysForPeriod(normalizedPeriod)}日 / 保存記録: 0件 / 使用記録: 0件',
      displayNote: json['display_note']?.toString() ??
          '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
      actionHint: json['action_hint']?.toString() ??
          'まずはDailyRecordをためて、あとで流れを見返します。',
      sourceLabel: json['source_label']?.toString() ?? 'insufficient_saved_history',
      dataScope: json['data_scope']?.toString() ?? '${normalizedPeriod}_history',
      dataQuality: json['data_quality']?.toString() ?? 'insufficient',
      isMedicalAdvice: json['is_medical_advice'] as bool? ?? false,
    );
  }

  bool get hasUsableReport {
    return dataQuality != 'insufficient' && usableSleepRecordCount > 0;
  }

  String get formattedAverageSleep {
    final minutes = averageTotalSleepMinutes;

    if (minutes == null) {
      return '-';
    }

    final hours = minutes ~/ 60;
    final restMinutes = minutes % 60;

    return '$hours時間$restMinutes分';
  }

  String get displayRecordDates {
    if (recordDates.isEmpty) {
      return '対象日: -';
    }

    return '対象日: ${recordDates.join(', ')}';
  }

  String get displayPeriodLabel {
    return period == 'monthly' ? '月次' : '週次';
  }


  String get displayDateRange {
    if (rangeStart.isNotEmpty && rangeEnd.isNotEmpty) {
      return 'レポート範囲: $rangeStart 〜 $rangeEnd';
    }

    if (referenceDate.isNotEmpty) {
      return 'レポート範囲: $displayPeriodLabel / 基準日: $referenceDate';
    }

    return 'レポート範囲: $displayPeriodLabel';
  }

  String get displayRecordCoverage {
    return '保存記録: $totalRecordCount件 / 睡眠つき記録: $usableSleepRecordCount件';
  }

  String get displaySourceLabel {
    return 'データ元: ${_sourceLabelText(sourceLabel)}';
  }

  String get displayDataScope {
    return '集計範囲: ${_dataScopeText(dataScope)}';
  }

  String get displayDataQuality {
    return '記録状態: ${_dataQualityText(dataQuality)}';
  }

  static String _sourceLabelText(String sourceLabel) {
    switch (sourceLabel) {
      case 'saved_daily_record_history':
        return '保存済みDailyRecord';
      case 'saved_daily_record_history_with_mock_sleep':
        return '保存済みDailyRecord（デモ睡眠データ）';
      case 'saved_daily_record_history_with_real_sleep':
        return '保存済みDailyRecord（実データを含む）';
      case 'insufficient_saved_history':
        return '保存済み履歴がまだ少ない状態';
    }

    return '保存済みDailyRecord';
  }

  static String _dataScopeText(String dataScope) {
    switch (dataScope) {
      case 'weekly_history':
        return '週次の保存履歴';
      case 'monthly_history':
        return '月次の保存履歴';
    }

    return '保存履歴';
  }

  static String _dataQualityText(String dataQuality) {
    switch (dataQuality) {
      case 'usable':
        return '参考にしやすい記録数です';
      case 'partial':
        return '記録が少なめなので参考程度です';
      case 'insufficient':
        return 'まだ判断材料が少ないです';
    }

    return '記録状態を確認中です';
  }

  static int _defaultDaysForPeriod(String period) {
    return period == 'monthly' ? 30 : 7;
  }

  static String _defaultTitleForPeriod(String period) {
    return period == 'monthly' ? 'Monthly Rhythm Report' : 'Weekly Rhythm Report';
  }

  static String _defaultLabelForPeriod(String period) {
    return period == 'monthly' ? '月次レポートはまだ参考程度' : '週次レポートはまだ参考程度';
  }

  static List<String> _parseStringList(dynamic value) {
    if (value is List) {
      return value.map((item) => item.toString()).toList();
    }

    return const [];
  }
}
