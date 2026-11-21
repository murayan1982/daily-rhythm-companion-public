import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_public_app/debug_ai_advice.dart';
import 'package:drc_public_app/debug_mina_demo.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

const advice = 'ひと息ついてから、できることを一つ選びましょう。';
final generate = find.text('固定アドバイスを表示');
final play = find.text('再生');
final stop = find.text('停止');
final failure = find.text('音声を再生できませんでした。再試行できます。');

Future<void> showDemo(
  WidgetTester tester, {
  DebugMinaVoice? voice,
  DebugMinaResponse response = fixedMinaResponse,
  ProductionMood mood = ProductionMood.normal,
  ProductionCharacter character = ProductionCharacter.gentleMina,
}) => tester.pumpWidget(
  MaterialApp(
    home: Scaffold(
      body: DebugMinaDemo(
        mood: mood,
        character: character,
        response: response,
        voice: voice,
      ),
    ),
  ),
);

Future<void> press(WidgetTester tester, Finder button) async {
  await tester.tap(button);
  await tester.pump();
}

void main() {
  testWidgets('switches expression before an explicit play and supports stop', (
    tester,
  ) async {
    final events = <String>[];
    final completed = Completer<void>();
    await showDemo(
      tester,
      voice: (
        fetch: (message) async {
          events.add(message);
          return Uint8List.fromList([1]);
        },
        play: (audio) {
          expect(audio, [1]);
          events.add('play');
          return completed.future;
        },
        stop: () async => events.add('stop'),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.bySemanticsLabel('ミナの表情：通常'), findsOneWidget);
    expect(play, findsNothing);
    await press(tester, generate);
    expect(find.bySemanticsLabel('ミナの表情：寄り添い'), findsOneWidget);
    expect(find.text(advice), findsOneWidget);
    expect(events, isEmpty);
    await press(tester, play);
    expect(events, [advice, 'play']);
    await press(tester, stop);
    expect(events, [advice, 'play', 'stop']);
    completed.completeError(StateError('late native error'));
    await tester.pump();
    expect(failure, findsNothing);
    expect(stop, findsNothing);
    expect(find.text(advice), findsOneWidget);
    expect(find.bySemanticsLabel('ミナの表情：寄り添い'), findsOneWidget);
  });

  testWidgets('unsupported tags show the normal expression and keep the text', (
    tester,
  ) async {
    await showDemo(
      tester,
      response: () async => (message: advice, expressionTag: 'thinking'),
    );
    await press(tester, generate);
    expect(find.bySemanticsLabel('ミナの表情：通常'), findsOneWidget);
    expect(find.text(advice), findsOneWidget);
    expect(
      tester
          .widget<TextButton>(find.widgetWithText(TextButton, '再生'))
          .onPressed,
      isNull,
    );
  });

  for (final failsAtFetch in [true, false]) {
    testWidgets(
      'keeps advice and allows retry after failure at fetch=$failsAtFetch',
      (tester) async {
        var fetches = 0;
        await showDemo(
          tester,
          voice: (
            fetch: (_) async {
              fetches++;
              if (failsAtFetch && fetches == 1) throw StateError('fetch');
              return Uint8List.fromList([1]);
            },
            play: (_) async {
              if (!failsAtFetch && fetches == 1) throw StateError('play');
            },
            stop: () async {},
          ),
        );
        await press(tester, generate);
        await press(tester, play);
        expect(failure, findsOneWidget);
        expect(find.text(advice), findsOneWidget);
        expect(find.bySemanticsLabel('ミナの表情：寄り添い'), findsOneWidget);
        await press(tester, play);
        expect(fetches, 2);
        expect(failure, findsNothing);
      },
    );
  }

  for (final action in ['stop', 'regenerate', 'mood', 'character']) {
    testWidgets('ignores delayed audio after $action', (tester) async {
      final fetched = Completer<Uint8List>();
      var plays = 0;
      var stops = 0;
      final DebugMinaVoice voice = (
        fetch: (_) => fetched.future,
        play: (_) async => plays++,
        stop: () async => stops++,
      );
      await showDemo(tester, voice: voice);
      await press(tester, generate);
      await press(tester, play);
      switch (action) {
        case 'stop':
          await press(tester, stop);
        case 'regenerate':
          await press(tester, generate);
        case 'mood':
          await showDemo(tester, voice: voice, mood: ProductionMood.tired);
        case 'character':
          await showDemo(
            tester,
            voice: voice,
            character: ProductionCharacter.cheerfulSora,
          );
      }
      fetched.complete(Uint8List.fromList([1]));
      await tester.pump();
      expect(plays, 0);
      expect(stops, 1);
      expect(stop, findsNothing);
      expect(failure, findsNothing);
      if (action == 'mood' || action == 'character') {
        expect(find.text(advice), findsNothing);
        expect(find.text('😌'), findsNothing);
      }
    });
  }

  testWidgets('a late response cannot restore the old expression or advice', (
    tester,
  ) async {
    final old = Completer<DebugAdviceResult>();
    var calls = 0;
    Future<DebugAdviceResult> response() => calls++ == 0
        ? old.future
        : Future.value((message: '現在の本文', expressionTag: 'idle'));
    await showDemo(tester, response: response);
    await press(tester, generate);
    await showDemo(tester, response: response, mood: ProductionMood.energetic);
    await press(tester, generate);
    old.complete(await fixedMinaResponse());
    await tester.pump();
    expect(find.text('現在の本文'), findsOneWidget);
    expect(find.text(advice), findsNothing);
    expect(find.bySemanticsLabel('ミナの表情：通常'), findsOneWidget);
  });

  test(
    'FW request sends only displayed text and Mina voice metadata',
    () async {
      const path = '/demo/voice-output/audio/0123456789abcdef0123456789abcdef';
      final endpoint = Uri.parse('http://127.0.0.1:8000/debug/ai-advice');
      var audioUrl = path;
      final client = DebugAiAdviceClient(
        endpoint: endpoint,
        transport: (url, body) async {
          expect(url, endpoint.replace(path: '/demo/voice-output'));
          expect(jsonDecode(body), {
            'output_mode': 'tts',
            'text_content': advice,
            'character_id': 'gentle_mina',
            'voice_profile_id': 'mina_test',
            'audio_format': 'mp3',
          });
          return (
            statusCode: 200,
            body: jsonEncode({
              'accepted': true,
              'audio_ready': true,
              'audio_format': 'mp3',
              'audio_url': audioUrl,
            }),
          );
        },
      );
      expect(
        await client.requestMinaAudio(advice, 'mina_test'),
        endpoint.replace(path: path),
      );
      audioUrl = 'https://example.test$path';
      await expectLater(
        client.requestMinaAudio(advice, 'mina_test'),
        throwsFormatException,
      );
    },
  );
}
