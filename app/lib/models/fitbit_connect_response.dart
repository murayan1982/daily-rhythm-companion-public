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
      return 'ヘルスデータ連携の認証URLを準備しました。';
    }

    if (message.contains('not available yet') ||
        message.contains('not configured')) {
      return 'ヘルスデータ連携はまだ利用できません。現在はサンプルデータまたは未取得状態で確認できます。';
    }

    if (message.trim().isEmpty) {
      return 'ヘルスデータ連携の準備状態を確認できませんでした。';
    }

    return message;
  }
}