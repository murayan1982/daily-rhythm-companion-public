class WeeklySleepSummary {
  const WeeklySleepSummary({
    required this.referenceDate,
    required this.days,
    required this.label,
    required this.usableRecordCount,
    this.averageTotalSleepMinutes,
    this.recentDates = const [],
    this.displayTitle = 'Simple Weekly Summary',
    required this.displayLabel,
    required this.displaySummary,
    required this.displayCoverage,
    required this.displayNote,
    required this.actionHint,
    this.dataScope = 'weekly_history',
    this.isMedicalAdvice = false,
  });

  final String referenceDate;
  final int days;
  final String label;
  final int usableRecordCount;
  final int? averageTotalSleepMinutes;
  final List<String> recentDates;
  final String displayTitle;
  final String displayLabel;
  final String displaySummary;
  final String displayCoverage;
  final String displayNote;
  final String actionHint;
  final String dataScope;
  final bool isMedicalAdvice;

  factory WeeklySleepSummary.fromJson(Map<String, dynamic> json) {
    return WeeklySleepSummary(
      referenceDate: json['reference_date']?.toString() ?? '',
      days: json['days'] as int? ?? 7,
      label: json['label']?.toString() ?? 'insufficient_data',
      usableRecordCount: json['usable_record_count'] as int? ?? 0,
      averageTotalSleepMinutes: json['average_total_sleep_minutes'] as int?,
      recentDates: _parseStringList(json['recent_dates']),
      displayTitle: json['display_title']?.toString() ?? 'Simple Weekly Summary',
      displayLabel: json['display_label']?.toString() ?? '週次まとめはまだ参考程度',
      displaySummary: json['display_summary']?.toString() ??
          'もう少し記録が増えると、軽い週次まとめを表示できます。',
      displayCoverage: json['display_coverage']?.toString() ??
          '対象: 直近7日 / 使用記録: 0件',
      displayNote: json['display_note']?.toString() ??
          '過去のDailyRecordから作る軽い振り返りです。今日の睡眠や健康状態の診断には使いません。',
      actionHint: json['action_hint']?.toString() ??
          'まずは記録をためながら、日々の流れを軽く振り返ります。',
      dataScope: json['data_scope']?.toString() ?? 'weekly_history',
      isMedicalAdvice: json['is_medical_advice'] as bool? ?? false,
    );
  }

  bool get hasUsableSummary {
    return label != 'insufficient_data' && usableRecordCount > 0;
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

  String get displayRecentDates {
    if (recentDates.isEmpty) {
      return '対象日: -';
    }

    return '対象日: ${recentDates.join(', ')}';
  }

  static List<String> _parseStringList(dynamic value) {
    if (value is List) {
      return value.map((item) => item.toString()).toList();
    }

    return const [];
  }
}
