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

  bool get isLegacyFitbitRoute => provider == 'fitbit';

  String get displayTitle {
    return 'Health Data Status';
  }

  String get displayProvider {
    switch (provider) {
      case 'fitbit':
        return 'ウェアラブル連携（互換経路）';
      case 'google_health':
        return 'Google Health';
      default:
        return provider;
    }
  }

  String get displayConnectionState {
    if (isLegacyFitbitRoute) {
      return connected ? 'ローカルトークン検出' : '未検証';
    }

    return connected ? '連携済み' : '未連携';
  }

  String get displayMessage {
    if (isLegacyFitbitRoute) {
      if (connected) {
        return '互換用ウェアラブル経路のローカルトークン情報を検出しました。'
            '実トークン検証・実睡眠データ取得の受け入れ確認は未完了です。';
      }

      if (message.contains('credentials are configured')) {
        return '互換用ウェアラブル設定は検出しましたが、'
            'ローカルトークン情報は確認できません。';
      }

      if (message.contains('not configured')) {
        return '互換用ウェアラブル経路は未設定です。'
            '現在は設定済みの睡眠データ経路またはサンプルデータで動作します。';
      }

      return '互換用ウェアラブル経路は実利用未検証です。';
    }

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
