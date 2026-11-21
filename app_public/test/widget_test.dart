import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_local_advice.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_production/production_app.dart';
import 'package:drc_public_app/main.dart' as public_app;

void main() {
  const channel = MethodChannel('drc/health_connect_sleep');

  testWidgets('main starts the shared production application', (tester) async {
    public_app.main();
    await tester.pump();

    expect(find.byType(ProductionApp), findsOneWidget);
    expect(find.text('Daily Rhythm Companion'), findsOneWidget);
    expect(find.text('今日のリズム'), findsOneWidget);
    expect(find.text('AIアドバイスを生成'), findsNothing);
    expect(
      find.text('気分とキャラクターを選ぶと、端末内で今日のアドバイスを表示します。選択内容は保存されません。'),
      findsOneWidget,
    );
  });

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

      public_app.main();
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
      final advice = productionLocalAdviceFor(
        mood: ProductionMood.energetic,
        character: ProductionCharacter.gentleMina,
      );
      expect(find.text(advice.message), findsOneWidget);
      expect(calls, status == null ? 0 : 1);
    });
  }

  testWidgets(
    'public sleep display clears on background and reads only on tap',
    (tester) async {
      final messenger =
          TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      final read = find.text('Health Connect から読み込む');
      final session = find.text('11/20 23:15 〜 11/21 06:30\n記録の長さ 7時間15分');
      var calls = 0;
      messenger.setMockMethodCallHandler(channel, (call) async {
        expect(call.method, 'read');
        if (++calls == 1) {
          return {
            'status': 'ok',
            'start': DateTime(2026, 11, 20, 23, 15).millisecondsSinceEpoch,
            'end': DateTime(2026, 11, 21, 6, 30).millisecondsSinceEpoch,
            'minutes': 435,
          };
        }
        return {'status': 'denied'};
      });
      addTearDown(() => messenger.setMockMethodCallHandler(channel, null));

      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
      public_app.main();
      await tester.pumpAndSettle();
      expect(calls, 0);
      expect(session, findsNothing);

      await tester.tap(read);
      await tester.pumpAndSettle();
      expect(calls, 1);
      expect(session, findsOneWidget);

      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.paused);
      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
      await tester.pumpAndSettle();
      expect(session, findsNothing);
      expect(calls, 1);

      await tester.tap(read);
      await tester.pumpAndSettle();
      expect(calls, 2);
      expect(session, findsNothing);
      expect(find.text('睡眠の読み取りが許可されていません。'), findsOneWidget);
    },
  );
}
