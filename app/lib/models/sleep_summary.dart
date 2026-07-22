class SleepSummary {
  const SleepSummary({
    required this.date,
    required this.totalSleepMinutes,
    this.efficiency,
    this.deepSleepMinutes,
    this.remSleepMinutes,
    this.awakeMinutes,
    this.source = 'unknown',
    this.available = true,
    this.message,
    this.sleepStart,
    this.sleepEnd,
    this.qualityLabel,
    this.confidence,
    this.isRealData = false,
    this.unavailableReason,
  });

  final String date;
  final int totalSleepMinutes;
  final int? efficiency;
  final int? deepSleepMinutes;
  final int? remSleepMinutes;
  final int? awakeMinutes;
  final String source;
  final bool available;
  final String? message;
  final String? sleepStart;
  final String? sleepEnd;
  final String? qualityLabel;
  final String? confidence;
  final bool isRealData;
  final String? unavailableReason;

  factory SleepSummary.fromJson(Map<String, dynamic> json) {
    return SleepSummary(
      date: json['date']?.toString() ?? '',
      totalSleepMinutes: json['total_sleep_minutes'] as int? ?? 0,
      efficiency: json['efficiency'] as int?,
      deepSleepMinutes: json['deep_sleep_minutes'] as int?,
      remSleepMinutes: json['rem_sleep_minutes'] as int?,
      awakeMinutes: json['awake_minutes'] as int?,
      source: json['source']?.toString() ?? 'unknown',
      available: json['available'] as bool? ?? true,
      message: json['message']?.toString(),
      sleepStart: json['sleep_start']?.toString(),
      sleepEnd: json['sleep_end']?.toString(),
      qualityLabel: json['quality_label']?.toString(),
      confidence: json['confidence']?.toString(),
      isRealData: json['is_real_data'] as bool? ?? false,
      unavailableReason: json['unavailable_reason']?.toString(),
    );
  }

  String get formattedTotalSleep {
    final hours = totalSleepMinutes ~/ 60;
    final minutes = totalSleepMinutes % 60;
    return '$hours時間$minutes分';
  }

  String get formattedSleepWindow {
    final start = _formatLocalDateTime(sleepStart);
    final end = _formatLocalDateTime(sleepEnd);

    if (start == null && end == null) {
      return '-';
    }

    if (start == null) {
      return '終了: $end';
    }

    if (end == null) {
      return '開始: $start';
    }

    return '$start 〜 $end';
  }

  String get displayQualityLabel {
    switch (qualityLabel) {
      case 'good':
        return '良好';
      case 'fair':
        return 'ふつう';
      case 'short':
        return '短め';
      case 'unavailable':
        return '未取得';
      case null:
      case '':
        return '-';
      default:
        return qualityLabel!;
    }
  }

  String get displayConfidence {
    switch (confidence) {
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      case null:
      case '':
        return '-';
      default:
        return confidence!;
    }
  }

  String get displayDataKind {
    if (!available) {
      return '未取得';
    }

    if (isRealData) {
      return '実データ';
    }

    if (source == 'mock' || source.endsWith('_stub')) {
      return 'デモデータ';
    }

    return '未確認';
  }

  String get displaySource {
    switch (source) {
      case 'mock':
        return 'サンプルデータ';
      case 'wearable_stub':
        return 'ウェアラブル連携サンプル';
      case 'fitbit_stub':
        return 'ウェアラブル連携サンプル（旧設定）';
      case 'fitbit':
        return 'ウェアラブル連携';
      case 'google_health':
        return 'Google Health';
      default:
        return source;
    }
  }

  String get displayAvailability {
    return available ? '取得済み' : '未取得';
  }

  String get displayUnavailableReason {
    final trimmedReason = unavailableReason?.trim();

    if (trimmedReason == null || trimmedReason.isEmpty) {
      return '-';
    }

    switch (trimmedReason) {
      case 'api_disabled':
        return '実APIリクエストは安全のためOFFです';
      case 'no_stored_tokens':
        return 'Google Healthの再認証が必要です';
      case 'refresh_required':
      case 'refresh_not_completed':
        return 'Google Healthの認証更新が必要です';
      case 'no_sleep_data_points':
        return '対象日の睡眠データが見つかりません';
      case 'no_usable_sleep_intervals':
        return '睡眠時間帯を読み取れませんでした';
      case 'provider_permission_denied':
      case 'permission_denied':
        return 'Google Healthの権限確認が必要です';
      case 'http_error':
        return 'Google Health APIからエラーが返りました';
      case 'invalid_payload':
        return '睡眠データの形式を読み取れませんでした';
      default:
        return trimmedReason;
    }
  }

  String get displayUnavailableMessage {
    final trimmedMessage = message?.trim();

    if (trimmedMessage != null && trimmedMessage.isNotEmpty) {
      return trimmedMessage;
    }

    return '今日は睡眠データを確認できませんでした。気分をもとに、軽めのアドバイスを作ります。';
  }

  Map<String, dynamic> toAdviceJson() {
    return {
      'date': date,
      'total_sleep_minutes': totalSleepMinutes,
      'efficiency': efficiency,
      'deep_sleep_minutes': deepSleepMinutes,
      'rem_sleep_minutes': remSleepMinutes,
      'awake_minutes': awakeMinutes,
      'source': source,
      'available': available,
      'message': message,
      'sleep_start': sleepStart,
      'sleep_end': sleepEnd,
      'quality_label': qualityLabel,
      'confidence': confidence,
      'is_real_data': isRealData,
      'unavailable_reason': unavailableReason,
    };
  }

  static String? _formatLocalDateTime(String? value) {
    if (value == null || value.trim().isEmpty) {
      return null;
    }

    final parsed = DateTime.tryParse(value);
    if (parsed == null) {
      return value;
    }

    final local = parsed.toLocal();
    final month = local.month.toString().padLeft(2, '0');
    final day = local.day.toString().padLeft(2, '0');
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');

    return '$month/$day $hour:$minute';
  }
}
