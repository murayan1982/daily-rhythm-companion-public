import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:drc_public_app/debug_ai_advice.dart';
import 'package:drc_public_app/debug_advice_conversation.dart';
import 'package:drc_public_app/debug_advice_playback.dart';
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
  DebugCharacterVoice Function(DebugAiAdviceClient)? characterVoice,
  bool adviceChat = false,
}) async {
  final client = DebugAiAdviceClient(
    endpoint: _endpoint,
    transport: transport,
    timeout: timeout,
  );
  await tester.pumpWidget(
    SleepDebugApp(
      adviceClient: client,
      characterAiVoice: characterVoice?.call(client),
      adviceChat: adviceChat,
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
  const adviceRef = 'cccccccccccccccccccccccccccccccc';
  const sessionId = 'dddddddddddddddddddddddddddddddd';
  const chatPath = '/debug/conversation';
  DebugAdviceHttpResponse chatJson(Map<String, Object?> body) =>
      (statusCode: 200, body: jsonEncode(body));
  final initialAdvice = chatJson({
    'message': '元のアドバイス',
    'expression_tag': 'supportive',
    'voice_ref': null,
    'advice_ref': adviceRef,
  });
  final startReply = chatJson({'session_id': sessionId, 'turn_limit': 8});

  Future<void> enterQuestion(WidgetTester tester, String value) async {
    final input = find.byType(TextField);
    await tester.ensureVisible(input);
    await tester.enterText(input, value);
    await tester.pumpAndSettle();
  }

  testWidgets(
    'conversation starts only by choice and a retry uses the same turn',
    (tester) async {
      final requests = <(String, Object?)>[];
      var firstAttempts = 0;
      await _start(tester, (endpoint, body) async {
        final data = jsonDecode(body);
        requests.add((endpoint.path, data));
        switch (endpoint.path) {
          case '$chatPath/advice':
            expect(data, {'character_id': 'gentle_mina', 'mood': 'tired'});
            return initialAdvice;
          case '$chatPath/start':
            expect(data, {'advice_ref': adviceRef});
            return startReply;
          case '$chatPath/turn':
            final turn = (data as Map)['turn'];
            expect(data, {
              'session_id': sessionId,
              'turn': turn,
              'message': turn == 1 ? '最初の質問' : '追加質問',
            });
            if (turn == 1 && firstAttempts++ == 0) {
              return (statusCode: 502, body: '{}');
            }
            return chatJson({
              'message': turn == 1 ? '最初の返信' : '次の返信',
              'expression_tag': turn == 1 ? 'supportive' : 'speaking',
              'voice_ref': null,
            });
          case '$chatPath/end':
            expect(data, {'session_id': sessionId});
            return chatJson({'closed': true});
          default:
            throw StateError('Unexpected route');
        }
      }, adviceChat: true);
      await _select(tester);
      expect(requests, isEmpty);
      expect(find.text('会話を続ける'), findsNothing);
      await _tap(tester, _generateLabel);
      expect(requests.map((r) => r.$1), ['$chatPath/advice']);
      await _tap(tester, '会話を続ける');
      expect(requests.map((r) => r.$1), [
        '$chatPath/advice',
        '$chatPath/start',
      ]);
      await enterQuestion(tester, '最初の質問');
      expect(requests.length, 2);
      await _tap(tester, '質問を送る');
      expect(find.text('元のアドバイス'), findsOneWidget);
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        '最初の質問',
      );
      await _tap(tester, '質問を再試行');
      expect(find.text('あなた：最初の質問'), findsOneWidget);
      expect(find.text('ミナ：最初の返信'), findsOneWidget);
      expect(find.text('😌'), findsOneWidget);
      await enterQuestion(tester, '追加質問');
      await _tap(tester, '質問を送る');
      expect(find.text('ミナ：次の返信'), findsOneWidget);
      expect(find.text('🙂'), findsOneWidget);
      await _tap(tester, '会話を終了');
      expect(find.text('ミナ：次の返信'), findsNothing);
      expect(find.text('元のアドバイス'), findsOneWidget);
      expect(requests.last.$1, '$chatPath/end');
      await _tap(tester, '会話を続ける');
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        isEmpty,
      );
      expect(find.text('あなた：最初の質問'), findsNothing);
    },
  );

  for (final resetAction in ['会話を終了', 'ソラ', _generateLabel]) {
    testWidgets('conversation drops an old reply after $resetAction', (
      tester,
    ) async {
      final pending = Completer<DebugAdviceHttpResponse>();
      var ended = 0;
      await _start(tester, (endpoint, _) async {
        switch (endpoint.path) {
          case '$chatPath/advice':
            return initialAdvice;
          case '$chatPath/start':
            return startReply;
          case '$chatPath/turn':
            return pending.future;
          case '$chatPath/end':
            ended++;
            return chatJson({'closed': true});
          default:
            throw StateError('Unexpected route');
        }
      }, adviceChat: true);
      await _select(tester);
      await _tap(tester, _generateLabel);
      await _tap(tester, '会話を続ける');
      await enterQuestion(tester, '遅い質問');
      await _tap(tester, '質問を送る');
      await _tap(tester, resetAction);
      pending.complete(
        chatJson({
          'message': '遅れて届いた返信',
          'expression_tag': 'supportive',
          'voice_ref': null,
        }),
      );
      await tester.pumpAndSettle();
      expect(ended, 1);
      expect(find.textContaining('遅れて届いた返信'), findsNothing);
      expect(find.byType(TextField), findsNothing);
      if (resetAction != 'ソラ') expect(find.text('元のアドバイス'), findsOneWidget);
    });
  }

  testWidgets(
    'reply playback is optional and pending audio is dropped on close',
    (tester) async {
      final playback = DebugAdvicePlayback();
      final pending = Completer<Uint8List>();
      var requests = 0;
      var plays = 0;
      var stops = 0;
      var ended = 0;
      var open = true;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) => !open
                  ? const SizedBox()
                  : DebugAdviceConversation(
                      character: ProductionCharacter.cheerfulSora,
                      adviceTag: 'idle',
                      playback: playback,
                      start: () async => (id: sessionId, turnLimit: 8),
                      send: (_, _, _) async => (
                        message: 'ソラの返信',
                        expressionTag: 'happy',
                        voiceRef: adviceRef,
                      ),
                      end: (_) async => ended++,
                      voice: (id) => (
                        fetch: (ref) {
                          expect(id, sessionId);
                          expect(ref, adviceRef);
                          requests++;
                          return requests == 1
                              ? Future.value(Uint8List(1))
                              : pending.future;
                        },
                        play: (_) async => plays++,
                        stop: () async => stops++,
                      ),
                      onClose: () {
                        playback.stop();
                        setState(() => open = false);
                      },
                    ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      await enterQuestion(tester, '質問');
      await _tap(tester, '質問を送る');
      expect(find.text('😄'), findsOneWidget);
      expect(requests, 0);
      await _tap(tester, '再生');
      expect(requests, 1);
      expect(plays, 1);
      await _tap(tester, '再生');
      expect(requests, 2);
      await _tap(tester, '会話を終了');
      pending.complete(Uint8List(1));
      await tester.pumpAndSettle();
      expect(plays, 1);
      expect(stops, 1);
      expect(ended, 1);
      playback.dispose();
    },
  );

  const firstRef = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  const freshRef = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
  const audioPath = '/demo/voice-output/audio/$firstRef';
  const audioFailure = '音声を再生できませんでした。再試行できます。';

  DebugAdviceHttpResponse characterReply(
    String message,
    String tag,
    String? ref,
  ) => (
    statusCode: 200,
    body: jsonEncode({
      'message': message,
      'expression_tag': tag,
      'voice_ref': ref,
    }),
  );

  testWidgets(
    'Mina expressions update and play sends only the issued reference',
    (tester) async {
      final requests = <String>[];
      var plays = 0;
      var stops = 0;
      final playback = Completer<void>();
      await _start(
        tester,
        (endpoint, body) async {
          requests.add(endpoint.path);
          if (endpoint.path == '/debug/character/ai-advice') {
            expect(jsonDecode(body), {
              'mood': 'tired',
              'character_id': 'gentle_mina',
            });
            return characterReply('生成済みの本文', 'supportive', firstRef);
          }
          expect(endpoint.path, '/debug/character/voice');
          expect(jsonDecode(body), {
            'voice_ref': firstRef,
            'character_id': 'gentle_mina',
          });
          if (requests.length == 2) return (statusCode: 503, body: '{}');
          return (
            statusCode: 200,
            body: jsonEncode({
              'accepted': true,
              'audio_ready': true,
              'audio_format': 'mp3',
              'audio_url': audioPath,
            }),
          );
        },
        characterVoice: (client) =>
            (character) => (
              fetch: (ref) async {
                expect(
                  (await client.requestGeneratedCharacterAudio(
                    character,
                    ref,
                  )).path,
                  audioPath,
                );
                return Uint8List.fromList([1]);
              },
              play: (_) {
                plays++;
                return playback.future;
              },
              stop: () async => stops++,
            ),
      );
      await _select(tester);
      expect(requests, isEmpty);
      await _tap(tester, _generateLabel);
      expect(requests, ['/debug/character/ai-advice']);
      expect(find.text('生成済みの本文'), findsOneWidget);
      expect(find.text('😌'), findsOneWidget);
      await _tap(tester, '再生');
      expect(find.text(audioFailure), findsOneWidget);
      expect(find.text('生成済みの本文'), findsOneWidget);
      expect(find.text('😌'), findsOneWidget);
      await _tap(tester, '再生');
      expect(plays, 1);
      await _tap(tester, '停止');
      expect(stops, 1);
      playback.complete();
      await tester.pumpAndSettle();
      expect(find.text('停止'), findsNothing);
      expect(find.text('生成済みの本文'), findsOneWidget);
    },
  );

  for (final (character, tag, emoji) in [
    (ProductionCharacter.cheerfulSora, 'happy', '😄'),
    (ProductionCharacter.coolRei, 'thinking', '🤔'),
  ]) {
    final option = productionCharacterOptionFor(character);
    testWidgets(
      '${option.displayName} uses its own response, face and voice reference',
      (tester) async {
        final message = '${option.displayName}の生成本文';
        final requests = <String>[];
        var plays = 0;
        await _start(
          tester,
          (endpoint, body) async {
            requests.add(endpoint.path);
            if (endpoint.path == '/debug/character/ai-advice') {
              expect(jsonDecode(body), {
                'mood': 'tired',
                'character_id': option.characterId,
              });
              return characterReply(message, tag, freshRef);
            }
            expect(endpoint.path, '/debug/character/voice');
            expect(jsonDecode(body), {
              'voice_ref': freshRef,
              'character_id': option.characterId,
            });
            return (
              statusCode: 200,
              body: jsonEncode({
                'accepted': true,
                'audio_ready': true,
                'audio_format': 'mp3',
                'audio_url': audioPath,
              }),
            );
          },
          characterVoice: (client) =>
              (selected) => (
                fetch: (ref) async {
                  expect(selected, character);
                  expect(
                    (await client.requestGeneratedCharacterAudio(
                      selected,
                      ref,
                    )).path,
                    audioPath,
                  );
                  return Uint8List(1);
                },
                play: (_) async => plays++,
                stop: () async {},
              ),
        );
        await _tap(tester, '😪 だるい');
        await _tap(tester, option.displayName);
        expect(requests, isEmpty);
        await _tap(tester, _generateLabel);
        expect(find.text(message), findsOneWidget);
        expect(find.text(emoji), findsOneWidget);
        expect(requests, ['/debug/character/ai-advice']);
        await _tap(tester, '再生');
        expect(requests, [
          '/debug/character/ai-advice',
          '/debug/character/voice',
        ]);
        expect(plays, 1);
      },
    );
  }

  testWidgets('unconfigured Sora voice preserves the advice and expression', (
    tester,
  ) async {
    await _start(
      tester,
      (endpoint, _) async {
        expect(endpoint.path, '/debug/character/ai-advice');
        return characterReply('ソラの本文', 'happy', null);
      },
      characterVoice: (_) =>
          (_) => (
            fetch: (_) async => throw StateError('unexpected play'),
            play: (_) async {},
            stop: () async {},
          ),
    );
    await _tap(tester, '😪 だるい');
    await _tap(tester, 'ソラ');
    await _tap(tester, _generateLabel);
    expect(find.text('ソラの本文'), findsOneWidget);
    expect(find.text('😄'), findsOneWidget);
    expect(find.text('ソラの読み上げは利用できません。'), findsOneWidget);
    expect(find.text('再生'), findsNothing);
  });

  for (final action in ['再生成', '停止', '気分変更', 'ソラ', 'レイ']) {
    testWidgets('Mina ignores audio arriving after $action', (tester) async {
      final pending = Completer<Uint8List>();
      final refs = <String>[];
      var plays = 0;
      var stops = 0;
      var generates = 0;
      await _start(
        tester,
        (endpoint, body) async {
          expect(endpoint.path, '/debug/character/ai-advice');
          return generates++ == 0
              ? characterReply('古い本文', 'supportive', firstRef)
              : characterReply('新しい本文', 'thinking', freshRef);
        },
        characterVoice: (_) =>
            (character) => (
              fetch: (ref) {
                refs.add(ref);
                return ref == firstRef
                    ? pending.future
                    : Future.value(Uint8List(1));
              },
              play: (_) async => plays++,
              stop: () async => stops++,
            ),
      );
      await _select(tester);
      await _tap(tester, _generateLabel);
      await _tap(tester, '再生');
      await _tap(tester, switch (action) {
        '再生成' => _generateLabel,
        '停止' => '停止',
        '気分変更' => '☀️ 元気',
        _ => action,
      });
      pending.complete(Uint8List(1));
      await tester.pumpAndSettle();
      expect(plays, 0);
      expect(stops, 1);
      expect(refs, [firstRef]);
      if (action == '再生成') {
        expect(find.text('古い本文'), findsNothing);
        expect(find.text('新しい本文'), findsOneWidget);
        expect(find.text('🙂'), findsOneWidget);
        await _tap(tester, '再生');
        expect(refs, [firstRef, freshRef]);
        expect(plays, 1);
      }
    });
  }

  for (final nextChoice in ['☀️ 元気', 'ソラ', 'レイ']) {
    testWidgets('Mina ignores an older AI result after selecting $nextChoice', (
      tester,
    ) async {
      final old = Completer<DebugAdviceHttpResponse>();
      var count = 0;
      await _start(
        tester,
        (endpoint, _) {
          expect(endpoint.path, '/debug/character/ai-advice');
          return count++ == 0
              ? old.future
              : Future.value(characterReply('現在の本文', 'speaking', freshRef));
        },
        characterVoice: (_) =>
            (character) => (
              fetch: (_) async => throw StateError('unexpected play'),
              play: (_) async {},
              stop: () async {},
            ),
      );
      await _select(tester);
      await _tap(tester, _generateLabel);
      await _tap(tester, nextChoice);
      await _tap(tester, _generateLabel);
      old.complete(characterReply('以前の本文', 'supportive', firstRef));
      await tester.pumpAndSettle();
      expect(find.text('現在の本文'), findsOneWidget);
      expect(find.text('以前の本文'), findsNothing);
      expect(find.text('🙂'), findsOneWidget);
    });
  }

  testWidgets('Mina AI failure keeps local advice and offers no playback', (
    tester,
  ) async {
    await _start(
      tester,
      (endpoint, _) async {
        expect(endpoint.path, '/debug/character/ai-advice');
        return (statusCode: 502, body: '{}');
      },
      characterVoice: (_) =>
          (character) => (
            fetch: (_) async => throw StateError('unexpected play'),
            play: (_) async {},
            stop: () async {},
          ),
    );
    await _select(tester);
    await _tap(tester, _generateLabel);
    _expectLocalAdvice();
    expect(find.text(_failure), findsOneWidget);
    expect(find.text('再生'), findsNothing);
    expect(find.text('🙂'), findsOneWidget);
  });

  for (final includeSyntheticSleep in [false, true]) {
    testWidgets(
      'only Generate sends the selected fields, synthetic sleep: $includeSyntheticSleep',
      (tester) async {
        const sleepChannel = MethodChannel('drc/health_connect_sleep');
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
