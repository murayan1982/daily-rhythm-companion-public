class RecentSleepTrend {
  const RecentSleepTrend({
    required this.referenceDate,
    required this.days,
    required this.label,
    required this.usableRecordCount,
    this.averageTotalSleepMinutes,
    this.recentDates = const [],
    required this.message,
    required this.displayLabel,
    required this.displaySummary,
    required this.displayNote,
    this.dataScope = 'recent_history',
    this.isFallbackContext = true,
  });

  final String referenceDate;
  final int days;
  final String label;
  final int usableRecordCount;
  final int? averageTotalSleepMinutes;
  final List<String> recentDates;
  final String message;
  final String displayLabel;
  final String displaySummary;
  final String displayNote;
  final String dataScope;
  final bool isFallbackContext;

  factory RecentSleepTrend.fromJson(Map<String, dynamic> json) {
    return RecentSleepTrend(
      referenceDate: json['reference_date']?.toString() ?? '',
      days: json['days'] as int? ?? 7,
      label: json['label']?.toString() ?? 'insufficient_data',
      usableRecordCount: json['usable_record_count'] as int? ?? 0,
      averageTotalSleepMinutes: json['average_total_sleep_minutes'] as int?,
      recentDates: _parseStringList(json['recent_dates']),
      message: json['message']?.toString() ?? '',
      displayLabel: json['display_label']?.toString() ?? '傾向はまだ参考程度',
      displaySummary: json['display_summary']?.toString() ??
          'もう少し記録が増えると、直近傾向を表示できます。',
      displayNote: json['display_note']?.toString() ??
          '履歴から見た参考情報です。今日の睡眠としては扱いません。',
      dataScope: json['data_scope']?.toString() ?? 'recent_history',
      isFallbackContext: json['is_fallback_context'] as bool? ?? true,
    );
  }

  bool get hasUsableTrend {
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

  String get displayWindowSummary {
    return '対象: 直近$days日 / 使用記録: $usableRecordCount件';
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
