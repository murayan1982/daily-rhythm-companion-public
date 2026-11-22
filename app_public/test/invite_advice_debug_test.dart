import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_local_advice.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_production/production_app.dart';
import 'package:drc_public_app/health_connect_sleep_card.dart';
import 'package:drc_public_app/invite_advice_debug.dart';
import 'package:drc_public_app/main_invite_debug.dart' as invite_app;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

const _generate = 'AIアドバイスを生成';
const _tokenLabel = '招待トークン（検証用）';

Future<void> _tap(WidgetTester tester, String label) async {
  final target = find.text(label);
  await tester.ensureVisible(target);
  await tester.tap(target);
  await tester.pumpAndSettle();
}

Future<void> _mount(
  WidgetTester tester,
  InviteAdviceTransport transport,
) async {
  final client = InviteAdviceClient(transport: transport);
  await tester.pumpWidget(
    ProductionApp(
      journeyHeader: const HealthConnectSleepCard(),
      adviceExtension: (mood, character) => InviteAdviceDebugCard(
        mood: mood,
        character: character,
        client: client,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _selectAndEnterToken(WidgetTester tester) async {
  await _tap(tester, '☀️ 元気');
  await _tap(tester, 'ミナ');
  final field = find.byType(TextField);
  await tester.ensureVisible(field);
  await tester.enterText(field, 'synthetic-invite');
  await tester.pumpAndSettle();
}

void _expectLocalAdvice() {
  final advice = productionLocalAdviceFor(
    mood: ProductionMood.energetic,
    character: ProductionCharacter.gentleMina,
  );
  expect(find.text(advice.message), findsOneWidget);
}

void main() {
  testWidgets('invite entry point exposes a masked token field', (
    tester,
  ) async {
    invite_app.main();
    await tester.pumpAndSettle();
    expect(find.text(_tokenLabel), findsOneWidget);
    expect(
      tester.widget<TextField>(find.byType(TextField)).obscureText,
      isTrue,
    );
    expect(
      tester
          .widget<TextButton>(find.widgetWithText(TextButton, _generate))
          .onPressed,
      isNull,
    );
  });

  testWidgets('only Generate sends the Bearer and two selection fields', (
    tester,
  ) async {
    const sleepChannel = MethodChannel('drc/health_connect_sleep');
    final messenger =
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
    messenger.setMockMethodCallHandler(sleepChannel, (_) async {
      return {'status': 'ok', 'start': 0, 'end': 3600000, 'minutes': 60};
    });
    addTearDown(() => messenger.setMockMethodCallHandler(sleepChannel, null));
    var calls = 0;
    await _mount(tester, (endpoint, headers, body) async {
      calls++;
      expect(endpoint.toString(), 'http://127.0.0.1:8000/v1/advice');
      expect(headers['authorization'], 'Bearer synthetic-invite');
      expect(headers['content-type'], 'application/json; charset=utf-8');
      expect(jsonDecode(body), {
        'mood': 'energetic',
        'character_id': 'gentle_mina',
      });
      return (status: 200, body: jsonEncode({'message': '固定の検証応答です。'}));
    });
    await _tap(tester, 'Health Connect から読み込む');
    expect(find.textContaining('記録の長さ 1時間0分'), findsOneWidget);
    await _selectAndEnterToken(tester);
    _expectLocalAdvice();
    expect(calls, 0);

    await _tap(tester, _generate);
    expect(find.text('固定の検証応答です。'), findsOneWidget);
    expect(calls, 1);
  });

  for (final (status, message) in [
    (401, '招待トークンを確認してください。'),
    (429, '生成の上限に達しました。'),
    (502, 'AIアドバイスを利用できません。'),
    (503, 'AIアドバイスを利用できません。'),
    (null, 'AIアドバイスを取得できませんでした。'),
    (200, 'AIアドバイスを取得できませんでした。'),
  ]) {
    testWidgets('status $status leaves the offline advice available', (
      tester,
    ) async {
      var calls = 0;
      await _mount(tester, (_, _, _) async {
        calls++;
        if (status == null) throw const SocketException('disconnected');
        return (status: status, body: '{"message":""}');
      });
      await _selectAndEnterToken(tester);
      await _tap(tester, _generate);
      expect(find.textContaining(message), findsOneWidget);
      _expectLocalAdvice();
      expect(calls, 1);
    });
  }

  for (final changed in ['😪 だるい', 'ソラ']) {
    testWidgets('reply after selection changes to $changed is discarded', (
      tester,
    ) async {
      final first = Completer<InviteAdviceHttpResponse>();
      var calls = 0;
      await _mount(tester, (_, _, _) {
        if (++calls == 1) return first.future;
        return Future.value((status: 200, body: '{"message":"新しい応答"}'));
      });
      await _selectAndEnterToken(tester);
      await _tap(tester, _generate);
      await _tap(tester, changed);
      await _tap(tester, _generate);
      first.complete((status: 200, body: '{"message":"古い応答"}'));
      await tester.pumpAndSettle();
      expect(find.text('古い応答'), findsNothing);
      expect(find.text('新しい応答'), findsOneWidget);
      expect(calls, 2);
    });
  }
}
