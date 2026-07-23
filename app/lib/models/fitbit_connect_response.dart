class FitbitConnectResponse {
  const FitbitConnectResponse({
    required this.ready,
    this.connectUrl,
    required this.message,
  });

  final bool ready;
  final String? connectUrl;
  final String message;

  factory FitbitConnectResponse.fromJson(Map<String, dynamic> json) {
    return FitbitConnectResponse(
      ready: json['ready'] as bool? ?? false,
      connectUrl: json['connect_url']?.toString(),
      message: json['message']?.toString() ?? '',
    );
  }

  String get displayMessage {
    if (ready && connectUrl != null && connectUrl!.isNotEmpty) {
      return '互換用ウェアラブル認証URLを準備しました。'
          '実連携や実睡眠データ取得の確認完了を意味しません。';
    }

    if (message.contains('not available yet') ||
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
