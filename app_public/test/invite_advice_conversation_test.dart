import 'dart:async';
import 'dart:convert';

import 'package:drc_public_app/debug_ai_advice.dart';
import 'package:drc_public_app/main_invite_debug.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

const _adviceRef = 'abcdabcdabcdabcdabcdabcdabcdabcd';
const _session = 'abcdabcd1234abcdabcdabcdabcdabcd';
const _advice = '今日はゆっくりいきましょう。';

Future<void> _tap(WidgetTester tester, String label) async {
  final target = find.text(label);
  await tester.ensureVisible(target);
  await tester.tap(target);
  await tester.pumpAndSettle();
}

Finder get _input => find.widgetWithText(TextField, 'メッセージ');

Future<void> _enter(WidgetTester tester, String message) async {
  await tester.ensureVisible(_input);
  await tester.enterText(_input, message);
  await tester.pumpAndSettle();
}

DebugAdviceHttpResponse _reply(String message) => (
  statusCode: 200,
  body: jsonEncode({
    'message': message,
    'expression_tag': 'idle',
    'voice_ref': null,
  }),
);

Future<void> _mount(
  WidgetTester tester,
  DebugAdviceTransport chat, {
  bool adviceFails = false,
}) async {
  await tester.pumpWidget(
    buildInviteDebugApp(
      enableVoice: false,
      enableConversation: true,
      transport: (url, headers, body) async {
        expect(url.path, '/debug/invite/conversation/advice');
        expect(headers['authorization'], 'Bearer example-invite');
        return adviceFails
            ? (status: 502, body: '')
            : (
                status: 200,
                body: jsonEncode({
                  'message': _advice,
                  'voice_ref': null,
                  'advice_ref': _adviceRef,
                }),
              );
      },
      conversationTransport: chat,
    ),
  );
  await tester.pumpAndSettle();
  await _tap(tester, '🌿 ふつう');
  await _tap(tester, 'ミナ');
  final token = find.widgetWithText(TextField, '招待トークン（検証用）');
  await tester.ensureVisible(token);
  await tester.enterText(token, 'example-invite');
  await tester.pumpAndSettle();
  await _tap(tester, 'アドバイス生成');
}

void main() {
  testWidgets(
    'conversation sends only on tap, retries the same turn, and resets',
    (tester) async {
      final calls = <String>[];
      final turns = <Map<String, dynamic>>[];
      var failures = 0;
      await _mount(tester, (url, body) async {
        final action = url.pathSegments.last;
        final payload = jsonDecode(body) as Map<String, dynamic>;
        calls.add(action);
        return switch (action) {
          'start' => () {
            expect(payload, {'advice_ref': _adviceRef});
            return (
              statusCode: 200,
              body: '{"session_id":"$_session","turn_limit":4}',
            );
          }(),
          'turn' => () {
            turns.add(payload);
            if (++failures == 1) return (statusCode: 502, body: '');
            return _reply(payload['turn'] == 1 ? '猫が好きです。' : '三毛猫が好きです。');
          }(),
          'end' => (statusCode: 200, body: '{"closed":true}'),
          _ => throw StateError('Unexpected conversation action'),
        };
      });
      expect(find.text(_advice), findsOneWidget);
      await _tap(tester, '会話を続ける');
      expect(calls, isEmpty);
      await _enter(tester, '好きな動物は？');
      expect(calls, isEmpty);
      await _tap(tester, '送信');
      expect(find.textContaining('返信を取得できませんでした'), findsOneWidget);
      expect(tester.widget<TextField>(_input).controller!.text, '好きな動物は？');
      await _tap(tester, '送信');
      expect(turns[0], turns[1]);
      expect(turns[1], {
        'session_id': _session,
        'turn': 1,
        'message': '好きな動物は？',
      });
      expect(find.text('ミナ：猫が好きです。'), findsOneWidget);
      await _enter(tester, 'どんな猫？');
      await _tap(tester, '送信');
      expect(turns[2], {'session_id': _session, 'turn': 2, 'message': 'どんな猫？'});
      expect(find.text('ミナ：三毛猫が好きです。'), findsOneWidget);
      expect(find.text('再生'), findsNothing);
      await _tap(tester, '会話を終了');
      expect(calls, ['start', 'turn', 'turn', 'turn', 'end']);
      await _tap(tester, '会話を続ける');
      expect(tester.widget<TextField>(_input).controller!.text, isEmpty);
      expect(find.text('ミナ：猫が好きです。'), findsNothing);
      expect(calls.last, 'end');
    },
  );

  for (final dismiss in ['会話を終了', 'ソラ', 'アドバイス生成']) {
    testWidgets('$dismiss closes the session and discards late replies', (
      tester,
    ) async {
      final pending = Completer<DebugAdviceHttpResponse>();
      var ended = 0;
      await _mount(tester, (url, body) async {
        return switch (url.pathSegments.last) {
          'start' => (
            statusCode: 200,
            body: '{"session_id":"$_session","turn_limit":4}',
          ),
          'turn' => await pending.future,
          'end' => () {
            expect(jsonDecode(body), {'session_id': _session});
            ended++;
            return (statusCode: 200, body: '{"closed":true}');
          }(),
          _ => throw StateError('Unexpected conversation action'),
        };
      });
      await _tap(tester, '会話を続ける');
      await _enter(tester, '映画の話をしよう');
      await _tap(tester, '送信');
      expect(find.text('返信を待っています。'), findsOneWidget);
      await _tap(tester, dismiss);
      expect(ended, 1);
      pending.complete(_reply('古い返信'));
      await tester.pumpAndSettle();
      expect(find.textContaining('古い返信'), findsNothing);
      expect(find.text('映画の話をしよう'), findsNothing);
    });
  }

  testWidgets('local fallback does not offer a conversation', (tester) async {
    await _mount(
      tester,
      (_, _) async => fail('Local fallback started a conversation'),
      adviceFails: true,
    );
    expect(find.textContaining('端末内のアドバイスを表示しています'), findsOneWidget);
    expect(find.text('会話を続ける'), findsNothing);
  });
}
