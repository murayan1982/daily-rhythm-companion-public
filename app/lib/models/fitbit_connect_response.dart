class FitbitConnectResponse {
  const FitbitConnectResponse({
    required this.ready,
    this.connectUrl,
    required this.message,
    this.connectionState,
    this.verified = false,
  });

  final bool ready;
  final String? connectUrl;
  final String message;
  final String? connectionState;
  final bool verified;

  factory FitbitConnectResponse.fromJson(Map<String, dynamic> json) {
    return FitbitConnectResponse(
      ready: json['ready'] as bool? ?? false,
      connectUrl: json['connect_url']?.toString(),
      message: json['message']?.toString() ?? '',
      connectionState: json['connection_state']?.toString(),
      verified: json['verified'] as bool? ?? false,
    );
  }

  String get resolvedConnectionState {
    final explicitState = connectionState?.trim();
    if (explicitState != null && explicitState.isNotEmpty) {
      return explicitState;
    }
    return ready ? 'authorization_ready' : 'unavailable';
  }

  String get displayMessage {
    if (ready && connectUrl != null && connectUrl!.isNotEmpty) {
      return resolvedConnectionState == 'reconnect_required'
          ? '互換用ウェアラブル再認証URLを準備しました。実接続の確認完了を意味しません。'
          : '互換用ウェアラブル認証URLを準備しました。'
              '実連携や実睡眠データ取得の確認完了を意味しません。';
    }

    if (resolvedConnectionState == 'unconfigured' ||
        message.contains('not available yet') ||
        message.contains('not configured')) {
      return '互換用ウェアラブル認証経路はまだ利用できません。'
          '現在は設定済みの睡眠データ経路またはサンプルデータで確認できます。';
    }

    if (message.trim().isEmpty) {
      return '互換用ウェアラブル認証経路の準備状態を確認できませんでした。';
    }

    return message;
  }
}
