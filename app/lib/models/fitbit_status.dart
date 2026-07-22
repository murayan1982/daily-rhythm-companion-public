// App-facing health status model for the current legacy /fitbit/status route.
// The route name remains for compatibility, while UI wording stays provider-neutral.
class FitbitStatus {
  const FitbitStatus({
    required this.connected,
    required this.provider,
    required this.message,
  });

  final bool connected;
  final String provider;
  final String message;

  factory FitbitStatus.fromJson(Map<String, dynamic> json) {
    return FitbitStatus(
      connected: json['connected'] as bool? ?? false,
      provider: json['provider']?.toString() ?? 'unknown',
      message: json['message']?.toString() ?? '',
    );
  }

  String get displayTitle {
    return 'Health Data Status';
  }

  String get displayProvider {
    switch (provider) {
      case 'fitbit':
        return 'ウェアラブル連携';
      case 'google_health':
        return 'Google Health';
      default:
        return provider;
    }
  }

  String get displayConnectionState {
    return connected ? '連携済み' : '未連携';
  }

  String get displayMessage {
    if (connected) {
      return 'ヘルスデータ連携は利用可能です。';
    }

    if (message.contains('not configured')) {
      return 'ヘルスデータ連携はまだ設定されていません。現在はサンプルデータまたは未取得状態で動作します。';
    }

    if (message.trim().isEmpty) {
      return 'ヘルスデータ連携の状態を確認できませんでした。';
    }

    return message;
  }
}
