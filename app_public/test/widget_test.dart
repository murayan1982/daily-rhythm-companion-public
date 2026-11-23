import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:drc_production/components/production_daily_advice.dart';
import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_local_advice.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_production/production_app.dart';
import 'package:drc_public_app/main.dart' as public_app;
import 'package:drc_public_app/main_invite_release.dart';

void main() {
  const channel = MethodChannel('drc/health_connect_sleep');

  testWidgets('main starts the shared production application', (tester) async {
    public_app.main();
    await tester.pump();

    expect(find.byType(ProductionApp), findsOneWidget);
    expect(find.text('Daily Rhythm Companion'), findsOneWidget);
    expect(find.text('今日のリズム'), findsOneWidget);
    expect(find.text('アドバイス生成'), findsOneWidget);
    expect(find.text('睡眠を読み込む'), findsOneWidget);
    expect(find.text('招待トークンを入力'), findsNothing);
    _expectBundledPortraits(tester);
  });

  testWidgets('invite release uses the same three bundled portraits', (
    tester,
  ) async {
    await tester.pumpWidget(
      buildInviteReleaseApp(
        endpointUrl: 'https://invite.example.invalid/v1/advice',
      ),
    );
    await tester.pumpAndSettle();
    _expectBundledPortraits(tester);
  });

  for (final invite in [false, true]) {
    for (final moodFirst in [true, false]) {
      testWidgets(
        '${invite ? 'invite' : 'standard'} advice notice follows complete selection (mood first: $moodFirst)',
        (tester) async {
          if (invite) {
            await tester.pumpWidget(
              buildInviteReleaseApp(
                endpointUrl: 'https://invite.example.invalid/v1/advice',
                transport: (_, _, _) async => fail('No token was entered'),
              ),
            );
          } else {
            public_app.main();
          }
          await tester.pumpAndSettle();

          final notice = find.text(ProductionDailyAdvice.localRuleNotice);
          final bothRequired = find.text('気分とキャラクターを選んでください。');
          final oneRequired = find.text(
            moodFirst ? 'キャラクターを選んでください。' : '気分を選んでください。',
          );
          final localBody = find.text(
            productionLocalAdviceFor(
              mood: ProductionMood.energetic,
              character: ProductionCharacter.gentleMina,
            ).message,
          );
          final generate = find.widgetWithText(FilledButton, 'アドバイス生成');
          expect(bothRequired, findsOneWidget);
          expect(localBody, findsNothing);
          expect(notice, findsNothing);
          expect(tester.widget<FilledButton>(generate).onPressed, isNull);

          final (first, second) = moodFirst ? ('☀️ 元気', 'ミナ') : ('ミナ', '☀️ 元気');
          final firstChoice = find.text(first);
          await tester.ensureVisible(firstChoice);
          await tester.tap(firstChoice);
          await tester.pumpAndSettle();
          expect(bothRequired, findsNothing);
          expect(oneRequired, findsOneWidget);
          expect(localBody, findsNothing);
          expect(notice, findsNothing);
          expect(tester.widget<FilledButton>(generate).onPressed, isNull);

          final secondChoice = find.text(second);
          await tester.ensureVisible(secondChoice);
          await tester.tap(secondChoice);
          await tester.pumpAndSettle();
          expect(oneRequired, findsNothing);
          expect(localBody, findsNothing);
          expect(notice, findsNothing);
          expect(tester.widget<FilledButton>(generate).onPressed, isNotNull);
          await tester.ensureVisible(generate);
          await tester.tap(generate);
          await tester.pumpAndSettle();
          expect(localBody, findsOneWidget);
          expect(notice, findsOneWidget);
        },
      );
    }
  }

  testWidgets(
    'failed portrait uses its initial and the card stays selectable',
    (tester) async {
      final bundle = _MissingSoraPortrait();
      await tester.pumpWidget(
        DefaultAssetBundle(
          bundle: bundle,
          child: buildInviteReleaseApp(endpointUrl: ''),
        ),
      );
      await tester.pumpAndSettle();
      final sora = find.widgetWithText(InkWell, 'ソラ');
      expect(bundle.failedLoads, greaterThan(0));
      expect(
        find.descendant(of: sora, matching: find.text('ソ')),
        findsOneWidget,
      );
      await tester.ensureVisible(sora);
      await tester.tap(sora);
      await tester.pumpAndSettle();
      expect(
        find.descendant(of: sora, matching: find.byIcon(Icons.check_circle)),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );

  for (final (status, message) in [
    (null, '読み込まなくても気分を選べます。'),
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
        await tester.tap(find.text('睡眠を読み込む'));
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
      final generate = find.text('アドバイス生成');
      await tester.ensureVisible(generate);
      await tester.tap(generate);
      await tester.pumpAndSettle();

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
      final read = find.text('睡眠を読み込む');
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

void _expectBundledPortraits(WidgetTester tester) {
  const characters = {
    'ミナ': 'gentle_mina',
    'ソラ': 'cheerful_sora',
    'レイ': 'cool_rei',
  };
  for (final entry in characters.entries) {
    final card = find.widgetWithText(InkWell, entry.key);
    final portrait = tester.widget<Image>(
      find.descendant(of: card, matching: find.byType(Image)),
    );
    final asset = (portrait.image as ResizeImage).imageProvider as AssetImage;
    expect(asset.assetName, 'assets/characters/${entry.value}_demo.png');
  }
}

class _MissingSoraPortrait extends CachingAssetBundle {
  int failedLoads = 0;

  @override
  Future<ByteData> load(String key) async {
    if (key == 'assets/characters/cheerful_sora_demo.png') {
      failedLoads++;
      throw FlutterError('Missing test asset');
    }
    return rootBundle.load(key);
  }
}
