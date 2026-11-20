import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:drc_public_app/debug_ai_advice.dart';
import 'package:drc_public_app/main_sleep_debug.dart';
import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_local_advice.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

final _endpoint = Uri.parse('http://127.0.0.1:8000/debug/ai-advice');
const _generateLabel = 'AIアドバイスを生成';
const _failure = 'AIアドバイスを取得できませんでした。上の端末内アドバイスを利用できます。時間をおいて再試行してください。';

DebugAdviceHttpResponse _reply(String message) => (
  statusCode: 200,
  body: jsonEncode({'message': message, 'expression_tag': 'supportive'}),
);

Future<void> _start(
  WidgetTester tester,
  DebugAdviceTransport transport, {
  Duration timeout = const Duration(seconds: 15),
}) async {
  await tester.pumpWidget(
    SleepDebugApp(
      adviceClient: DebugAiAdviceClient(
        endpoint: _endpoint,
        transport: transport,
        timeout: timeout,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _tap(WidgetTester tester, String text) async {
  final target = find.text(text);
  await tester.ensureVisible(target);
  await tester.tap(target);
  await tester.pumpAndSettle();
}

Future<void> _select(WidgetTester tester) async {
  await _tap(tester, '😪 だるい');
  await _tap(tester, 'ミナ');
}

void _expectLocalAdvice() {
  final message = productionLocalAdviceFor(
    mood: ProductionMood.tired,
    character: ProductionCharacter.gentleMina,
  ).message;
  expect(find.text(message), findsOneWidget);
}

void main() {
  for (final includeSyntheticSleep in [false, true]) {
    testWidgets(
      'only Generate sends the selected fields, synthetic sleep: $includeSyntheticSleep',
      (tester) async {
        const sleepChannel = MethodChannel('drc/sleep_debug');
        final messenger =
            TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
        messenger.setMockMethodCallHandler(sleepChannel, (call) async {
          expect(call.method, 'read');
          return {'status': 'ok', 'start': 0, 'end': 43020000, 'minutes': 717};
        });
        addTearDown(
          () => messenger.setMockMethodCallHandler(sleepChannel, null),
        );

        final requests = <Object?>[];
        await _start(tester, (endpoint, body) async {
          expect(endpoint, _endpoint);
          requests.add(jsonDecode(body));
          return _reply('AI：一息ついて始めましょう。');
        });
        expect(
          tester
              .widget<TextButton>(
                find.widgetWithText(TextButton, _generateLabel),
              )
              .onPressed,
          isNull,
        );
        expect(requests, isEmpty);
        await _tap(tester, 'Health Connect から読み込む');
        expect(find.textContaining('記録の長さ 11時間57分'), findsOneWidget);
        await _select(tester);
        if (includeSyntheticSleep) {
          await _tap(tester, '合成睡眠要約（385分）を含める');
        }
        expect(requests, isEmpty);

        await _tap(tester, _generateLabel);

        expect(requests, [
          {
            'mood': 'tired',
            'character_id': 'gentle_mina',
            if (includeSyntheticSleep)
              'sleep_summary': {'total_sleep_minutes': 385},
          },
        ]);
        expect(find.text('AI：一息ついて始めましょう。'), findsOneWidget);
      },
    );
  }

  final failures = <String, DebugAdviceTransport>{
    'network': (_, _) async =>
        throw const SocketException('connection refused'),
    '502': (_, _) async => (statusCode: 502, body: '{}'),
    '503': (_, _) async => (statusCode: 503, body: '{}'),
    'malformed JSON': (_, _) async => (statusCode: 200, body: '<html>'),
    'unknown expression': (_, _) async => (
      statusCode: 200,
      body: '{"message":"表示しない","expression_tag":"invalid"}',
    ),
    'timeout': (_, _) => Completer<DebugAdviceHttpResponse>().future,
  };
  for (final entry in failures.entries) {
    testWidgets('${entry.key} keeps local advice and allows retry', (
      tester,
    ) async {
      var calls = 0;
      await _start(tester, (endpoint, body) {
        calls++;
        return calls == 1
            ? entry.value(endpoint, body)
            : Future.value(_reply('再試行で取得できました。'));
      }, timeout: const Duration(seconds: 2));
      await _select(tester);
      await _tap(tester, _generateLabel);
      if (entry.key == 'timeout') await tester.pump(const Duration(seconds: 2));
      expect(find.text(_failure), findsOneWidget);
      _expectLocalAdvice();

      await _tap(tester, _generateLabel);
      expect(calls, 2);
      expect(find.text('再試行で取得できました。'), findsOneWidget);
      expect(find.text(_failure), findsNothing);
    });
  }

  for (final changedChoice in ['☀️ 元気', 'ソラ']) {
    testWidgets('a new advice response wins after changing $changedChoice', (
      tester,
    ) async {
      final requests = <Completer<DebugAdviceHttpResponse>>[];
      await _start(tester, (_, _) {
        final request = Completer<DebugAdviceHttpResponse>();
        requests.add(request);
        return request.future;
      });
      await _select(tester);
      await _tap(tester, _generateLabel);
      await _tap(tester, changedChoice);
      expect(requests, hasLength(1));
      await _tap(tester, _generateLabel);
      expect(requests, hasLength(2));

      requests[1].complete(_reply('現在の選択へのアドバイス。'));
      await tester.pumpAndSettle();
      requests[0].complete(_reply('古い選択へのアドバイス。'));
      await tester.pumpAndSettle();

      expect(find.text('現在の選択へのアドバイス。'), findsOneWidget);
      expect(find.text('古い選択へのアドバイス。'), findsNothing);
    });
  }

  test('client reads the expression tag from a valid response', () async {
    final client = DebugAiAdviceClient(
      endpoint: _endpoint,
      transport: (_, _) async => _reply('ひと息つきましょう。'),
    );
    final result = await client.generate(
      mood: ProductionMood.tired,
      character: ProductionCharacter.gentleMina,
    );
    expect(result, (message: 'ひと息つきましょう。', expressionTag: 'supportive'));
  });
}
