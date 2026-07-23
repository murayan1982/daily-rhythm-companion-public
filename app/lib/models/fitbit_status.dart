// App-facing health status model for the legacy /fitbit/status route.
// Existing fields remain compatible; W-2 adds conservative lifecycle states.
class FitbitStatus {
  const FitbitStatus({
    required this.connected,
    required this.provider,
    required this.message,
    this.connectionState,
    this.verified = false,
  });

  final bool connected;
  final String provider;
  final String message;
  final String? connectionState;
  final bool verified;

  factory FitbitStatus.fromJson(Map<String, dynamic> json) {
    return FitbitStatus(
      connected: json['connected'] as bool? ?? false,
      provider: json['provider']?.toString() ?? 'unknown',
      message: json['message']?.toString() ?? '',
      connectionState: json['connection_state']?.toString(),
      verified: json['verified'] as bool? ?? false,
    );
  }

  bool get isLegacyFitbitRoute => provider == 'fitbit';

  String get resolvedConnectionState {
    final explicitState = connectionState?.trim();
    if (explicitState != null && explicitState.isNotEmpty) {
      return explicitState;
    }

    // Backward-compatible fallback for pre-W-2 responses.
    if (isLegacyFitbitRoute) {
      if (connected) {
        return 'token_present_unverified';
      }
      if (message.contains('credentials are configured')) {
        // A pre-W-2 response has no explicit lifecycle state. Preserve the
        // accepted M-7 presentation instead of inferring authorization-ready.
        return 'unavailable';
      }
      if (message.contains('not configured')) {
        return 'unconfigured';
      }
      return 'unavailable';
    }

    return connected ? 'connected' : 'unavailable';
  }

  String get displayTitle => 'Health Data Status';

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
    if (!isLegacyFitbitRoute) {
      return connected ? '連携済み' : '未連携';
    }

    switch (resolvedConnectionState) {
      case 'unconfigured':
        return '未設定';
      case 'authorization_ready':
        return '認証準備済み';
      case 'token_present_unverified':
        return 'ローカルトークン検出';
      case 'connected':
        return verified ? '連携済み' : '未検証';
      case 'refresh_required':
        return 'トークン更新が必要';
      case 'reconnect_required':
        return '再接続が必要';
      case 'permission_blocked':
        return '認証未許可';
      case 'error':
        return '状態確認エラー';
      case 'unavailable':
      default:
        return '未検証';
    }
  }

  String get displayMessage {
    if (!isLegacyFitbitRoute) {
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

    switch (resolvedConnectionState) {
      case 'unconfigured':
        return '互換用ウェアラブル経路は未設定です。'
            '現在は設定済みの睡眠データ経路またはサンプルデータで動作します。';
      case 'authorization_ready':
        return '互換用ウェアラブル設定を検出しました。認証ページから接続または再接続できます。';
      case 'token_present_unverified':
        return '互換用ウェアラブル経路のローカルトークン情報を検出しました。'
            '実トークン検証・実睡眠データ取得の受け入れ確認は未完了です。';
      case 'connected':
        return verified
            ? '互換用ウェアラブル連携は検証済みです。'
            : '互換用ウェアラブル経路はまだ実利用未検証です。';
      case 'refresh_required':
        return 'ローカルトークンの更新が必要です。状態確認だけでは外部更新を実行しません。';
      case 'reconnect_required':
        return 'ローカルトークンを安全に継続利用できません。認証ページから再接続してください。';
      case 'permission_blocked':
        return 'ウェアラブル認証が許可されませんでした。権限を確認して再接続してください。';
      case 'error':
        return 'ローカルトークン状態を安全に確認できませんでした。再接続が必要です。';
      case 'unavailable':
      default:
        if (message.contains('credentials are configured')) {
          return '互換用ウェアラブル設定を検出しましたが、'
              'ローカルトークン情報は確認できません。実利用未検証です。';
        }
        return message.trim().isEmpty
            ? '互換用ウェアラブル経路は実利用未検証です。'
            : message;
    }
  }
}
