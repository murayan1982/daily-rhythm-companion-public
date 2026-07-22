import 'advice_source.dart';
import 'sleep_summary.dart';

class DailyRecord {
  const DailyRecord({
    required this.date,
    required this.characterId,
    required this.characterName,
    required this.mood,
    required this.sleepSummary,
    required this.adviceMessage,
    required this.adviceBasis,
    this.adviceSource,
    required this.createdAt,
    required this.updatedAt,
  });

  final String date;
  final String characterId;
  final String characterName;
  final String mood;
  final SleepSummary sleepSummary;
  final String adviceMessage;
  final String adviceBasis;
  final AdviceSource? adviceSource;
  final String createdAt;
  final String updatedAt;

  factory DailyRecord.fromJson(Map<String, dynamic> json) {
    return DailyRecord(
      date: json['date']?.toString() ?? '',
      characterId: json['character_id']?.toString() ?? '',
      characterName: json['character_name']?.toString() ?? '',
      mood: json['mood']?.toString() ?? '',
      sleepSummary: SleepSummary.fromJson(
        json['sleep_summary'] is Map
            ? Map<String, dynamic>.from(json['sleep_summary'] as Map)
            : {},
      ),
      adviceMessage: json['advice_message']?.toString() ?? '',
      adviceBasis: json['advice_basis']?.toString() ?? '',
      adviceSource: _parseAdviceSource(json['advice_source']),
      createdAt: json['created_at']?.toString() ?? '',
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }

  static AdviceSource? _parseAdviceSource(dynamic value) {
    if (value is Map) {
      return AdviceSource.fromJson(Map<String, dynamic>.from(value));
    }

    return null;
  }

  String get displayMood {
    switch (mood) {
      case 'energetic':
        return '元気';
      case 'normal':
        return 'ふつう';
      case 'tired':
        return 'だるい';
      case '':
        return '-';
      default:
        return mood;
    }
  }

  String get shortAdviceMessage {
    final normalized = adviceMessage.trim().replaceAll('\n', ' ');

    if (normalized.length <= 80) {
      return normalized;
    }

    return '${normalized.substring(0, 80)}...';
  }

  String get displayHistorySleepSummary {
    if (sleepSummary.available) {
      return '睡眠時間: ${sleepSummary.formattedTotalSleep}';
    }

    return '睡眠: ${sleepSummary.displayUnavailableReason}';
  }

  String get displayHistorySleepSource {
    final dataKind = sleepSummary.displayDataKind;
    final source = sleepSummary.displaySource.trim();

    if (source.isEmpty || source == '-') {
      return 'データ種別: $dataKind';
    }

    return 'データ種別: $dataKind / $source';
  }

  String get displayHistoryContextNote {
    if (!sleepSummary.available) {
      return 'この日は睡眠データ未取得です。過去トレンドや今日の睡眠としては扱いません。';
    }

    if (sleepSummary.isRealData) {
      return 'この日の実データ記録です。今日の睡眠状態の断定には使いません。';
    }

    return 'この日のデモ/サンプル記録です。今日の睡眠状態の断定には使いません。';
  }

  String get displayAdviceBasis {
    final basis = adviceBasis.trim();

    if (basis.isEmpty) {
      return '-';
    }

    if (basis.startsWith('rhythm_report_partial')) {
      return 'リズムレポートを参考程度にしたアドバイス';
    }

    if (basis.startsWith('rhythm_report')) {
      return 'リズムレポートも参考にしたアドバイス';
    }

    if (basis.startsWith('recent_sleep_trend')) {
      return '直近傾向を参考にしたアドバイス';
    }

    if (basis.startsWith('sleep+mood+character')) {
      return 'この日の睡眠・気分・キャラクター';
    }

    if (basis.startsWith('mood+character')) {
      return '気分・キャラクター';
    }

    return basis;
  }

  bool get hasReportReflection {
    return adviceSource?.hasReportHandoff ?? false;
  }

  String get displayReportReflectionLabel {
    return adviceSource?.reportHandoff?.displayReflectionLabel ?? '-';
  }

  String get displayReportReflectionSummary {
    return adviceSource?.reportHandoff?.displayUserFacingSummary ?? '-';
  }

  String get displayReportReflectionQuality {
    return adviceSource?.reportHandoff?.displayQuality ?? '-';
  }

  String get displayReportReflectionSource {
    return adviceSource?.reportHandoff?.displaySource ?? '-';
  }

  String get displayUpdatedAt {
    final parsed = DateTime.tryParse(updatedAt);

    if (parsed == null) {
      return updatedAt.isEmpty ? '-' : updatedAt;
    }

    final local = parsed.toLocal();
    final month = local.month.toString().padLeft(2, '0');
    final day = local.day.toString().padLeft(2, '0');
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');

    return '${local.year}-$month-$day $hour:$minute';
  }
}
