import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/fitbit_connect_response.dart';
import 'package:app/models/fitbit_status.dart';

void main() {
  group('Fitbit current-state presentation contract', () {
    test('legacy token presence is not displayed as verified connection', () {
      const status = FitbitStatus(
        connected: true,
        provider: 'fitbit',
        message:
            'Fitbit appears to be connected using local development token data. Real token validation is not implemented yet.',
      );

      expect(status.displayProvider, 'ウェアラブル連携（互換経路）');
      expect(status.displayConnectionState, 'ローカルトークン検出');
      expect(status.displayConnectionState, isNot('連携済み'));
      expect(status.displayMessage, contains('実トークン検証'));
      expect(status.displayMessage, contains('受け入れ確認は未完了'));
      expect(status.displayMessage, isNot(contains('利用可能です')));
    });

    test('legacy configured state without token remains unverified', () {
      const status = FitbitStatus(
        connected: false,
        provider: 'fitbit',
        message:
            'Fitbit credentials are configured, but local token data is not available yet.',
      );

      expect(status.displayConnectionState, '未検証');
      expect(status.displayMessage, contains('ローカルトークン情報は確認できません'));
    });

    test('verified non-legacy providers keep the existing connected wording', () {
      const status = FitbitStatus(
        connected: true,
        provider: 'google_health',
        message: 'Google Health is connected.',
      );

      expect(status.displayProvider, 'Google Health');
      expect(status.displayConnectionState, '連携済み');
      expect(status.displayMessage, 'ヘルスデータ連携は利用可能です。');
    });

    test('prepared legacy authorization URL is not shown as connection success', () {
      const response = FitbitConnectResponse(
        ready: true,
        connectUrl: 'https://www.fitbit.com/oauth2/authorize?state=test',
        message: 'Fitbit OAuth connect URL is ready. Open the URL to continue.',
      );

      expect(response.displayMessage, contains('互換用ウェアラブル認証URL'));
      expect(response.displayMessage, contains('確認完了を意味しません'));
      expect(response.displayMessage, isNot(contains('連携済み')));
    });
  });
}
