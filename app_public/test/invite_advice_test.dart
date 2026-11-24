import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:drc_production/core/production_character.dart';
import 'package:drc_production/core/production_local_advice.dart';
import 'package:drc_production/core/production_mood.dart';
import 'package:drc_production/components/production_daily_advice.dart';
import 'package:drc_public_app/invite_advice.dart';
import 'package:drc_public_app/main_invite_debug.dart' as invite_app;
import 'package:drc_public_app/main_invite_release.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

const _generate = 'アドバイス生成';
const _endpointUrl = 'https://invite.example.invalid/v1/advice';
const _loading = 'AIアドバイスを生成しています。';
const _fallback = ProductionDailyAdvice.fallbackNotice;
const _play = '音声再生';
const _stop = '停止';
const _voiceRef = 'abcdabcdabcdabcdabcdabcdabcdabcd';

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
  await tester.pumpWidget(
    buildInviteReleaseApp(endpointUrl: _endpointUrl, transport: transport),
  );
  await tester.pumpAndSettle();
}

Future<void> _selectAndEnterToken(WidgetTester tester) async {
  await _tap(tester, '☀️ 元気');
  await _tap(tester, 'ミナ');
  final field = find.byType(TextField);
  expect(field, findsNothing);
  final reveal = find.text('招待トークンを入力');
  expect(
    find.descendant(of: find.byType(ProductionDailyAdvice), matching: reveal),
    findsOneWidget,
  );
  await _tap(tester, '招待トークンを入力');
  await tester.ensureVisible(field);
  await tester.enterText(field, 'synthetic-invite');
  await tester.pumpAndSettle();
}

final _localBody = find.text(
  productionLocalAdviceFor(
    mood: ProductionMood.energetic,
    character: ProductionCharacter.gentleMina,
  ).message,
);

Future<void> _mountDebugVoice(
  WidgetTester tester, {
  required Future<Uint8List> Function(String) fetch,
  required Future<void> Function(Uint8List) play,
  required Future<void> Function() stop,
  Future<InviteAdviceHttpResponse> Function()? reply,
}) async {
  await tester.pumpWidget(
    invite_app.buildInviteDebugApp(
      enableVoice: true,
      transport: (url, headers, body) async {
        expect(url.path, '/debug/invite/advice');
        expect(headers['authorization'], 'Bearer synthetic-invite');
        expect(jsonDecode(body), {
          'mood': 'energetic',
          'character_id': 'cheerful_sora',
        });
        return reply == null
            ? (
                status: 200,
                body: '{"message":"読み上げる本文","voice_ref":"$_voiceRef"}',
              )
            : await reply();
      },
      characterVoice: (character) {
        expect(character, ProductionCharacter.cheerfulSora);
        return (fetch: fetch, play: play, stop: stop);
      },
    ),
  );
  await tester.pumpAndSettle();
  await _tap(tester, '☀️ 元気');
  await _tap(tester, 'ソラ');
  final field = find.byType(TextField);
  await tester.ensureVisible(field);
  await tester.enterText(field, 'synthetic-invite');
  await tester.pumpAndSettle();
}

void main() {
  for (final (status, actual, useSleep) in <(String?, int?, bool)>[
    ('ok', 367, true),
    (null, null, true),
    ('ok', null, true),
    ('denied', 367, true),
    ('ok', 367, false),
  ]) {
    testWidgets('debug sleep input: $status / $actual / opt-in $useSleep', (
      tester,
    ) async {
      const channel = MethodChannel('drc/health_connect_sleep');
      final messenger =
          TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
      messenger.setMockMethodCallHandler(channel, (call) async {
        expect(call.arguments, {'includeActualSleep': true});
        return {
          'status': status,
          'start': 0,
          'end': 25200000,
          'minutes': 420,
          'actualSleepMinutes': ?actual,
        };
      });
      addTearDown(() => messenger.setMockMethodCallHandler(channel, null));
      final received = <Map<String, dynamic>>[];
      final expected = status == 'ok' && useSleep ? actual : null;
      await tester.pumpWidget(
        invite_app.buildInviteDebugApp(
          enableVoice: false,
          transport: (url, _, body) async {
            received.add(jsonDecode(body) as Map<String, dynamic>);
            expect(
              url.path,
              expected == null ? '/v1/advice' : '/debug/invite/advice',
            );
            return (
              status: 200,
              body: jsonEncode({
                'message': '差し替え応答',
                if (expected != null) 'voice_ref': null,
              }),
            );
          },
        ),
      );
      await tester.pumpAndSettle();
      if (status != null) await _tap(tester, '睡眠を読み込む');
      await _tap(tester, '☀️ 元気');
      await _tap(tester, 'ミナ');
      final token = find.byType(TextField);
      await tester.ensureVisible(token);
      await tester.enterText(token, 'synthetic-invite');
      await tester.pumpAndSettle();
      final setting = find.widgetWithText(SwitchListTile, '睡眠時間をアドバイスに使う');
      expect(tester.widget<SwitchListTile>(setting).value, isFalse);
      if (useSleep) await _tap(tester, '睡眠時間をアドバイスに使う');
      expect(received, isEmpty);
      await _tap(tester, _generate);
      expect(find.text('差し替え応答'), findsOneWidget);
      expect(received, [
        {
          'mood': 'energetic',
          'character_id': 'gentle_mina',
          'total_sleep_minutes': ?expected,
        },
      ]);
    });
  }

  testWidgets('invite entry point exposes a masked token field', (
    tester,
  ) async {
    invite_app.main();
    await tester.pumpAndSettle();
    expect(find.text('招待トークン（検証用）'), findsOneWidget);
    expect(
      tester
          .widget<InviteAdviceApp>(find.byType(InviteAdviceApp))
          .client
          .endpoint,
      Uri.parse('http://127.0.0.1:8000/v1/advice'),
    );
    expect(
      tester.widget<TextField>(find.byType(TextField)).obscureText,
      isTrue,
    );
    expect(
      tester
          .widget<FilledButton>(find.widgetWithText(FilledButton, _generate))
          .onPressed,
      isNull,
    );
  });

  for (final url in [
    '',
    'http://invite.example.invalid/v1/advice',
    'https:///v1/advice',
    'https://invite.example.invalid:99999/v1/advice',
    'https://invite.example.invalid:notaport/v1/advice',
    'https://example.invalid/other',
    'https://example.invalid/v1/advice?',
    'https://example.invalid/v1/advice#ref',
    'https://user@example.invalid/v1/advice',
    'https://example.invalid /v1/advice',
  ]) {
    testWidgets('invalid release URL keeps offline advice available: $url', (
      tester,
    ) async {
      var calls = 0;
      await tester.pumpWidget(
        buildInviteReleaseApp(
          endpointUrl: url,
          transport: (_, _, _) async {
            calls++;
            return (status: 200, body: '{"message":"unexpected"}');
          },
        ),
      );
      await tester.pumpAndSettle();
      await _tap(tester, '☀️ 元気');
      await _tap(tester, 'ミナ');
      expect(_localBody, findsNothing);
      await _tap(tester, _generate);
      expect(_localBody, findsOneWidget);
      expect(find.text(_fallback), findsNothing);
      expect(find.byType(TextField), findsNothing);
      expect(calls, 0);
    });
  }

  testWidgets('only Generate sends the Bearer and two selection fields', (
    tester,
  ) async {
    const sleepChannel = MethodChannel('drc/health_connect_sleep');
    final messenger =
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
    messenger.setMockMethodCallHandler(sleepChannel, (_) async {
      return {
        'status': 'ok',
        'start': 0,
        'end': 3600000,
        'minutes': 60,
        'actualSleepMinutes': 40,
      };
    });
    addTearDown(() => messenger.setMockMethodCallHandler(sleepChannel, null));
    var calls = 0;
    await _mount(tester, (endpoint, headers, body) async {
      calls++;
      expect(endpoint.toString(), _endpointUrl);
      expect(headers['authorization'], 'Bearer synthetic-invite');
      expect(headers['content-type'], 'application/json; charset=utf-8');
      expect(jsonDecode(body), {
        'mood': 'energetic',
        'character_id': 'gentle_mina',
      });
      return (status: 200, body: jsonEncode({'message': '固定の検証応答です。'}));
    });
    await _tap(tester, '睡眠を読み込む');
    expect(find.text('睡眠時間をアドバイスに使う'), findsNothing);
    expect(find.textContaining('記録の長さ 1時間0分'), findsOneWidget);
    await _selectAndEnterToken(tester);
    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.decoration?.labelText, '招待トークン');
    expect(field.obscureText, isTrue);
    expect(_localBody, findsNothing);
    expect(calls, 0);

    await _tap(tester, _generate);
    expect(find.text('固定の検証応答です。'), findsOneWidget);
    expect(find.text(_play), findsNothing);
    expect(_localBody, findsNothing);
    expect(find.text(ProductionDailyAdvice.localRuleNotice), findsNothing);
    expect(find.text(_fallback), findsNothing);
    expect(calls, 1);
  });

  for (final failure in [401, 429, 502, 503, 307, 200, 'offline', 'timeout']) {
    testWidgets('$failure falls back and the same button retries', (
      tester,
    ) async {
      var calls = 0;
      await _mount(tester, (_, _, _) async {
        if (++calls > 1) {
          return (status: 200, body: '{"message":"再試行の応答"}');
        }
        return switch (failure) {
          'offline' => throw const SocketException('disconnected'),
          'timeout' => throw TimeoutException('request timed out'),
          final int status => (status: status, body: '{"message":""}'),
          _ => throw StateError('Unexpected test case'),
        };
      });
      await _selectAndEnterToken(tester);
      await _tap(tester, _generate);
      expect(find.text(_fallback), findsOneWidget);
      expect(_localBody, findsOneWidget);
      expect(find.text(ProductionDailyAdvice.localRuleNotice), findsOneWidget);
      expect(calls, 1);
      await _tap(tester, _generate);
      expect(find.text('再試行の応答'), findsOneWidget);
      expect(find.text(_fallback), findsNothing);
      expect(_localBody, findsNothing);
      expect(calls, 2);
    });
  }

  for (final (changed, status) in [('😪 だるい', 200), ('ソラ', 503)]) {
    testWidgets('stale $status after changing to $changed is discarded', (
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
      expect(find.text(_loading), findsOneWidget);
      final button = find.widgetWithText(FilledButton, _generate);
      expect(tester.widget<FilledButton>(button).onPressed, isNull);
      await tester.tap(button, warnIfMissed: false);
      expect(calls, 1);
      await _tap(tester, changed);
      expect(find.text(_loading), findsNothing);
      first.complete((status: status, body: '{"message":"古い応答"}'));
      await tester.pumpAndSettle();
      expect(find.text('古い応答'), findsNothing);
      expect(find.text(_fallback), findsNothing);
      expect(find.text(ProductionDailyAdvice.localRuleNotice), findsNothing);
      expect(_localBody, findsNothing);
      expect(calls, 1);
      await _tap(tester, _generate);
      expect(find.text('新しい応答'), findsOneWidget);
      expect(calls, 2);
    });
  }

  testWidgets('voice is fetched only on play, then the button stops playback', (
    tester,
  ) async {
    var downloaded = 0;
    var stopped = 0;
    final playing = Completer<void>();
    await _mountDebugVoice(
      tester,
      fetch: (ref) async {
        expect(ref, _voiceRef);
        downloaded++;
        return Uint8List.fromList([1, 2, 3]);
      },
      play: (audio) {
        expect(audio, orderedEquals([1, 2, 3]));
        return playing.future;
      },
      stop: () async {
        stopped++;
        playing.complete();
      },
    );
    expect(find.text(_play), findsNothing);
    await _tap(tester, _generate);
    expect(find.text('読み上げる本文'), findsOneWidget);
    expect(downloaded, 0);
    await _tap(tester, _play);
    expect(downloaded, 1);
    expect(find.text(_play), findsNothing);
    await _tap(tester, _stop);
    expect(stopped, 1);
    expect(find.text(_stop), findsNothing);
    expect(find.text(_play), findsOneWidget);
    expect(find.text('読み上げる本文'), findsOneWidget);
  });

  for (final failFetch in [true, false]) {
    testWidgets('voice can retry after a failure (fetch: $failFetch)', (
      tester,
    ) async {
      var attempts = 0;
      await _mountDebugVoice(
        tester,
        fetch: (_) async {
          if (++attempts == 1 && failFetch) {
            throw const SocketException('offline');
          }
          return Uint8List.fromList([1]);
        },
        play: (_) async {
          if (attempts == 1) throw PlatformException(code: 'playback_failed');
        },
        stop: () async {},
      );
      await _tap(tester, _generate);
      await _tap(tester, _play);
      expect(find.text('読み上げる本文'), findsOneWidget);
      expect(find.textContaining('音声を再生できませんでした'), findsOneWidget);
      await _tap(tester, _play);
      expect(attempts, 2);
      expect(find.textContaining('音声を再生できませんでした'), findsNothing);
    });
  }

  for (final changed in ['😪 だるい', 'ミナ', _generate]) {
    testWidgets('changing $changed stops and drops late audio', (tester) async {
      final pending = Completer<Uint8List>();
      var played = 0;
      var stopped = 0;
      await _mountDebugVoice(
        tester,
        fetch: (_) => pending.future,
        play: (_) async {
          played++;
        },
        stop: () async {
          stopped++;
        },
      );
      await _tap(tester, _generate);
      await _tap(tester, _play);
      expect(find.text(_stop), findsOneWidget);
      await _tap(tester, changed);
      expect(stopped, 1);
      pending.complete(Uint8List.fromList([1]));
      await tester.pumpAndSettle();
      expect(played, 0);
      expect(find.text(_stop), findsNothing);
      expect(
        find.text(_play),
        changed == _generate ? findsOneWidget : findsNothing,
      );
    });
  }

  testWidgets(
    'changing character stops active audio and clears the old advice',
    (tester) async {
      final playing = Completer<void>();
      var stopped = 0;
      await _mountDebugVoice(
        tester,
        fetch: (_) async => Uint8List.fromList([1]),
        play: (_) => playing.future,
        stop: () async {
          stopped++;
          playing.complete();
        },
      );
      await _tap(tester, _generate);
      await _tap(tester, _play);
      await _tap(tester, 'ミナ');
      expect(stopped, 1);
      expect(find.text('読み上げる本文'), findsNothing);
      expect(find.text(_play), findsNothing);
    },
  );

  testWidgets('failed AI uses local advice without playback controls', (
    tester,
  ) async {
    await _mountDebugVoice(
      tester,
      reply: () async => (status: 503, body: ''),
      fetch: (_) async => fail('Local advice triggered audio fetch'),
      play: (_) async => fail('Local advice triggered playback'),
      stop: () async {},
    );
    await _tap(tester, _generate);
    expect(find.text(_fallback), findsOneWidget);
    expect(find.text(_play), findsNothing);
  });

  testWidgets('missing voice configuration keeps the successful advice', (
    tester,
  ) async {
    await _mountDebugVoice(
      tester,
      reply: () async =>
          (status: 200, body: '{"message":"本文のみ","voice_ref":null}'),
      fetch: (_) async => fail('Missing voice triggered audio fetch'),
      play: (_) async => fail('Missing voice triggered playback'),
      stop: () async {},
    );
    await _tap(tester, _generate);
    expect(find.text('本文のみ'), findsOneWidget);
    expect(find.text(_fallback), findsNothing);
    expect(find.text(_play), findsNothing);
  });
}
