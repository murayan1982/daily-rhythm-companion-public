import 'package:flutter_test/flutter_test.dart';

import 'package:app/models/fitbit_connect_response.dart';
import 'package:app/models/fitbit_status.dart';

void main() {
  group('Fitbit W-2 token/status/reconnect presentation', () {
    test('new token-present state remains explicitly unverified', () {
      final status = FitbitStatus.fromJson({
        'connected': true,
        'provider': 'fitbit',
        'message': 'public-safe status',
        'connection_state': 'token_present_unverified',
        'verified': false,
      });

      expect(status.resolvedConnectionState, 'token_present_unverified');
      expect(status.displayConnectionState, 'ローカルトークン検出');
      expect(status.displayConnectionState, isNot('連携済み'));
      expect(status.displayMessage, contains('受け入れ確認は未完了'));
    });

    test('refresh-required state is visible without claiming refresh execution', () {
      final status = FitbitStatus.fromJson({
        'connected': true,
        'provider': 'fitbit',
        'message': 'public-safe status',
        'connection_state': 'refresh_required',
        'verified': false,
      });

      expect(status.displayConnectionState, 'トークン更新が必要');
      expect(status.displayMessage, contains('外部更新を実行しません'));
    });

    test('reconnect-required state provides conservative recovery wording', () {
      final status = FitbitStatus.fromJson({
        'connected': false,
        'provider': 'fitbit',
        'message': 'public-safe status',
        'connection_state': 'reconnect_required',
      });

      expect(status.displayConnectionState, '再接続が必要');
      expect(status.displayMessage, contains('再接続してください'));
    });

    test('permission-blocked and error states stay distinct', () {
      final permission = FitbitStatus.fromJson({
        'provider': 'fitbit',
        'connection_state': 'permission_blocked',
      });
      final error = FitbitStatus.fromJson({
        'provider': 'fitbit',
        'connection_state': 'error',
      });

      expect(permission.displayConnectionState, '認証未許可');
      expect(permission.displayMessage, contains('権限を確認'));
      expect(error.displayConnectionState, '状態確認エラー');
      expect(error.displayMessage, contains('安全に確認できませんでした'));
    });

    test('old legacy response still maps to token-present-unverified', () {
      final status = FitbitStatus.fromJson({
        'connected': true,
        'provider': 'fitbit',
        'message':
            'Fitbit appears to be connected using local development token data.',
      });

      expect(status.resolvedConnectionState, 'token_present_unverified');
      expect(status.displayConnectionState, 'ローカルトークン検出');
    });

    test('verified connected wording requires explicit verified flag', () {
      final unverified = FitbitStatus.fromJson({
        'connected': true,
        'provider': 'fitbit',
        'connection_state': 'connected',
        'verified': false,
      });
      final verified = FitbitStatus.fromJson({
        'connected': true,
        'provider': 'fitbit',
        'connection_state': 'connected',
        'verified': true,
      });

      expect(unverified.displayConnectionState, '未検証');
      expect(verified.displayConnectionState, '連携済み');
    });

    test('connect response parses authorization-ready state', () {
      final response = FitbitConnectResponse.fromJson({
        'ready': true,
        'connect_url': 'https://www.fitbit.com/oauth2/authorize?state=test',
        'message': 'public-safe status',
        'connection_state': 'authorization_ready',
        'verified': false,
      });

      expect(response.resolvedConnectionState, 'authorization_ready');
      expect(response.displayMessage, contains('認証URL'));
      expect(response.displayMessage, isNot(contains('連携済み')));
    });
  });
}
