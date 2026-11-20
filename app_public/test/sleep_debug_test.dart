import 'package:drc_public_app/main_sleep_debug.dart' as sleep_debug;
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const channel = MethodChannel('drc/sleep_debug');

  for (final (status, message) in [
    (null, '睡眠を読み込まずにアドバイスへ進むこともできます。'),
    ('denied', '睡眠の読み取りが許可されていません。'),
    ('empty', '昨夜の対象になる睡眠記録が見つかりませんでした。'),
    ('unavailable', 'この端末では Health Connect を利用できません。'),
  ]) {
    testWidgets('local advice works with sleep status $status', (tester) async {
      final messenger =
          TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      var calls = 0;
      messenger.setMockMethodCallHandler(channel, (call) async {
        calls++;
        expect(call.method, 'read');
        return {'status': status};
      });
      addTearDown(() => messenger.setMockMethodCallHandler(channel, null));

      sleep_debug.main();
      await tester.pumpAndSettle();
      expect(calls, 0);

      if (status != null) {
        await tester.tap(find.text('Health Connect から読み込む'));
        await tester.pumpAndSettle();
        expect(calls, 1);
      }
      expect(find.text(message), findsOneWidget);

      for (final label in ['☀️ 元気', 'ミナ']) {
        final choice = find.text(label);
        await tester.ensureVisible(choice);
        await tester.tap(choice);
        await tester.pumpAndSettle();
      }

      expect(find.text('気分: 元気'), findsOneWidget);
      expect(find.text('キャラクター: ミナ'), findsOneWidget);
      expect(calls, status == null ? 0 : 1);
    });
  }
}
