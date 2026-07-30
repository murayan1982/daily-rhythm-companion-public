import 'dart:async';
import 'dart:convert';

import 'package:app/models/provider_neutral_transcript.dart';
import 'package:app/models/realtime_text_stream.dart';
import 'package:app/services/realtime_text_stream_client.dart';
import 'package:app/services/realtime_text_stream_controller.dart';
import 'package:app/services/realtime_text_stream_transcript_handoff.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('RealtimeTextStreamTranscriptHandoff', () {
    test(
      'valid final transcript starts exactly once and retains no text',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient();
        final controller = _controller(fakeHttp);
        var providerCalls = 0;
        final handoff = RealtimeTextStreamTranscriptHandoff(
          controller: controller,
          transcriptProvider: () async {
            providerCalls += 1;
            return const ProviderNeutralTranscriptResult(
              resultId: 'result-1',
              text: ' injected final text ',
              isFinal: true,
            );
          },
        );

        await handoff.startFromNextTranscript();

        expect(providerCalls, 1);
        expect(fakeHttp.createCalls, 1);
        expect(fakeHttp.lastInputText, 'injected final text');
        expect(
          handoff.state.phase,
          RealtimeTextStreamTranscriptHandoffPhase.accepted,
        );
        expect(
          handoff.state.safeMessage,
          isNot(contains('injected final text')),
        );
        expect(handoff.state.safeMessage, isNot(contains('result-1')));

        handoff.dispose();
        controller.dispose();
      },
    );

    test('active stream rejects before invoking provider', () async {
      final fakeHttp = _FakeRealtimeHttpClient();
      final controller = _controller(fakeHttp);
      await controller.start(inputText: 'already active');
      var providerCalls = 0;
      final handoff = RealtimeTextStreamTranscriptHandoff(
        controller: controller,
        transcriptProvider: () async {
          providerCalls += 1;
          return _result('active-result', 'unused final text');
        },
      );

      await handoff.startFromNextTranscript();

      expect(providerCalls, 0);
      expect(fakeHttp.createCalls, 1);
      expect(
        handoff.state.phase,
        RealtimeTextStreamTranscriptHandoffPhase.rejected,
      );
      expect(handoff.state.safeMessage, isNot(contains('unused final text')));

      handoff.dispose();
      controller.dispose();
    });

    test(
      'simultaneous duplicate invocation calls provider and create once',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient();
        final controller = _controller(fakeHttp);
        final providerCompleter = Completer<ProviderNeutralTranscriptResult>();
        var providerCalls = 0;
        final handoff = RealtimeTextStreamTranscriptHandoff(
          controller: controller,
          transcriptProvider: () {
            providerCalls += 1;
            return providerCompleter.future;
          },
        );

        final first = handoff.startFromNextTranscript();
        final second = handoff.startFromNextTranscript();
        final third = handoff.startFromNextTranscript();
        expect(providerCalls, 1);
        expect(
          handoff.state.phase,
          RealtimeTextStreamTranscriptHandoffPhase.acquiring,
        );
        expect(fakeHttp.createCalls, 0);

        providerCompleter.complete(_result('result-1', 'one transcript'));
        await Future.wait(<Future<void>>[first, second, third]);

        expect(providerCalls, 1);
        expect(fakeHttp.createCalls, 1);

        handoff.dispose();
        controller.dispose();
      },
    );

    test(
      'simultaneous duplicate invocation during create failure creates once',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient(createStatus: 500);
        final controller = _controller(fakeHttp);
        final providerCompleter = Completer<ProviderNeutralTranscriptResult>();
        var providerCalls = 0;
        final handoff = RealtimeTextStreamTranscriptHandoff(
          controller: controller,
          transcriptProvider: () {
            providerCalls += 1;
            if (providerCalls == 1) {
              return providerCompleter.future;
            }
            return Future<ProviderNeutralTranscriptResult>.value(
              _result('result-$providerCalls', 'duplicate transcript'),
            );
          },
        );

        final first = handoff.startFromNextTranscript();
        final second = handoff.startFromNextTranscript();
        final third = handoff.startFromNextTranscript();
        expect(providerCalls, 1);
        expect(
          handoff.state.phase,
          RealtimeTextStreamTranscriptHandoffPhase.acquiring,
        );
        expect(fakeHttp.createCalls, 0);

        providerCompleter.complete(_result('result-1', 'one transcript'));
        await Future.wait(<Future<void>>[first, second, third]);

        expect(providerCalls, 1);
        expect(fakeHttp.createCalls, 1);
        expect(
          handoff.state.phase,
          RealtimeTextStreamTranscriptHandoffPhase.failed,
        );

        handoff.dispose();
        controller.dispose();
      },
    );

    test('non-final transcript is rejected without create', () async {
      final fakeHttp = _FakeRealtimeHttpClient();
      final controller = _controller(fakeHttp);
      final handoff = _handoff(
        controller,
        _result('result-1', 'draft transcript', isFinal: false),
      );

      await handoff.startFromNextTranscript();

      expect(fakeHttp.createCalls, 0);
      expect(
        handoff.state.phase,
        RealtimeTextStreamTranscriptHandoffPhase.rejected,
      );

      handoff.dispose();
      controller.dispose();
    });

    test('whitespace transcript is rejected without create', () async {
      final fakeHttp = _FakeRealtimeHttpClient();
      final controller = _controller(fakeHttp);
      final handoff = _handoff(controller, _result('result-1', '   '));

      await handoff.startFromNextTranscript();

      expect(fakeHttp.createCalls, 0);
      expect(
        handoff.state.phase,
        RealtimeTextStreamTranscriptHandoffPhase.rejected,
      );

      handoff.dispose();
      controller.dispose();
    });

    test(
      'over 4096 code point transcript is rejected without create',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient();
        final controller = _controller(fakeHttp);
        final handoff = _handoff(
          controller,
          _result('result-1', List<String>.filled(4097, 'x').join()),
        );

        await handoff.startFromNextTranscript();

        expect(fakeHttp.createCalls, 0);
        expect(
          handoff.state.phase,
          RealtimeTextStreamTranscriptHandoffPhase.rejected,
        );
        expect(handoff.state.safeMessage, isNot(contains('xxxx')));

        handoff.dispose();
        controller.dispose();
      },
    );

    test(
      'invalid and overlong result IDs are rejected without create',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient();
        final controller = _controller(fakeHttp);
        final blank = _handoff(controller, _result('   ', 'transcript'));
        await blank.startFromNextTranscript();
        expect(fakeHttp.createCalls, 0);
        expect(blank.state.safeMessage, isNot(contains('transcript value')));
        blank.dispose();

        final overlong = _handoff(
          controller,
          _result(List<String>.filled(129, 'r').join(), 'transcript'),
        );
        await overlong.startFromNextTranscript();
        expect(fakeHttp.createCalls, 0);
        expect(overlong.state.safeMessage, isNot(contains('transcript value')));

        overlong.dispose();
        controller.dispose();
      },
    );

    test(
      'duplicate consumed result ID does not create an additional session',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient(createStatus: 500);
        final controller = _controller(fakeHttp);
        final handoff = _handoff(controller, _result('result-1', 'transcript'));

        await handoff.startFromNextTranscript();
        await handoff.startFromNextTranscript();

        expect(fakeHttp.createCalls, 1);
        expect(
          handoff.state.phase,
          RealtimeTextStreamTranscriptHandoffPhase.rejected,
        );

        handoff.dispose();
        controller.dispose();
      },
    );

    test('provider returns null with fixed safe rejection', () async {
      final fakeHttp = _FakeRealtimeHttpClient();
      final controller = _controller(fakeHttp);
      final handoff = RealtimeTextStreamTranscriptHandoff(
        controller: controller,
        transcriptProvider: () async => null,
      );

      await handoff.startFromNextTranscript();

      expect(fakeHttp.createCalls, 0);
      expect(
        handoff.state.safeMessage,
        'No final transcript is available for streaming.',
      );

      handoff.dispose();
      controller.dispose();
    });

    test('provider throws without exposing raw exception', () async {
      final fakeHttp = _FakeRealtimeHttpClient();
      final controller = _controller(fakeHttp);
      final handoff = RealtimeTextStreamTranscriptHandoff(
        controller: controller,
        transcriptProvider: () async {
          throw StateError('raw provider exception private transcript');
        },
      );

      await handoff.startFromNextTranscript();

      expect(fakeHttp.createCalls, 0);
      expect(
        handoff.state.phase,
        RealtimeTextStreamTranscriptHandoffPhase.failed,
      );
      expect(handoff.state.safeMessage, isNot(contains('raw provider')));
      expect(handoff.state.safeMessage, isNot(contains('private transcript')));

      handoff.dispose();
      controller.dispose();
    });

    test('controller create failure uses bounded safe message only', () async {
      final fakeHttp = _FakeRealtimeHttpClient(createStatus: 500);
      final controller = _controller(fakeHttp);
      final handoff = _handoff(controller, _result('result-1', 'transcript'));

      await handoff.startFromNextTranscript();

      expect(fakeHttp.createCalls, 1);
      expect(
        handoff.state.phase,
        RealtimeTextStreamTranscriptHandoffPhase.failed,
      );
      expect(handoff.state.safeMessage, 'The text stream request failed.');
      expect(handoff.state.safeMessage, isNot(contains('create_failed')));
      expect(handoff.state.safeMessage, isNot(contains('raw body')));
      expect(handoff.state.safeMessage, isNot(contains('/realtime/text')));

      handoff.dispose();
      controller.dispose();
    });

    test('long safe message is compacted and bounded to 240 code points', () {
      final safeMessage =
          boundRealtimeTextStreamTranscriptHandoffSafeMessageForTesting(
            'safe  safe  ${List<String>.filled(300, 'x').join()}',
          );

      expect(
        safeMessage.runes.length,
        realtimeTextStreamMaxProblemMessageChars,
      );
      expect(safeMessage, startsWith('safe safe'));
    });

    test(
      'disposal during pending provider has no late start or controller dispose',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient();
        final controller = _controller(fakeHttp);
        final providerCompleter = Completer<ProviderNeutralTranscriptResult>();
        final phases = <RealtimeTextStreamTranscriptHandoffPhase>[];
        late final RealtimeTextStreamTranscriptHandoff handoff;
        handoff = RealtimeTextStreamTranscriptHandoff(
          controller: controller,
          transcriptProvider: () => providerCompleter.future,
        );
        handoff.addListener(() => phases.add(handoff.state.phase));

        final pending = handoff.startFromNextTranscript();
        handoff.dispose();
        providerCompleter.complete(_result('result-1', 'late transcript'));
        await pending;

        expect(fakeHttp.createCalls, 0);
        expect(phases, <RealtimeTextStreamTranscriptHandoffPhase>[
          RealtimeTextStreamTranscriptHandoffPhase.acquiring,
        ]);
        await controller.start(inputText: 'controller still owned elsewhere');
        expect(fakeHttp.createCalls, 1);

        controller.dispose();
      },
    );

    test(
      'consumed result ID memory is bounded to 32 and evicts oldest ID',
      () async {
        final fakeHttp = _FakeRealtimeHttpClient(createStatus: 500);
        final controller = _controller(fakeHttp);
        var nextResultId = 'result-0';
        final handoff = RealtimeTextStreamTranscriptHandoff(
          controller: controller,
          transcriptProvider: () async => _result(nextResultId, 'transcript'),
        );

        for (var i = 0; i < 33; i += 1) {
          nextResultId = 'result-$i';
          await handoff.startFromNextTranscript();
        }

        expect(handoff.rememberedResultIdCount, 32);
        nextResultId = 'result-0';
        await handoff.startFromNextTranscript();
        expect(fakeHttp.createCalls, 34);
        expect(handoff.rememberedResultIdCount, 32);
        expect(handoff.state.safeMessage, isNot(contains('transcript')));

        handoff.dispose();
        controller.dispose();
      },
    );
  });
}

RealtimeTextStreamController _controller(_FakeRealtimeHttpClient fakeHttp) {
  return RealtimeTextStreamController(
    client: RealtimeTextStreamClient(
      baseUrl: 'http://backend.test',
      client: fakeHttp,
    ),
  );
}

RealtimeTextStreamTranscriptHandoff _handoff(
  RealtimeTextStreamController controller,
  ProviderNeutralTranscriptResult result,
) {
  return RealtimeTextStreamTranscriptHandoff(
    controller: controller,
    transcriptProvider: () async => result,
  );
}

ProviderNeutralTranscriptResult _result(
  String resultId,
  String text, {
  bool isFinal = true,
}) {
  return ProviderNeutralTranscriptResult(
    resultId: resultId,
    text: text,
    isFinal: isFinal,
  );
}

class _FakeRealtimeHttpClient extends http.BaseClient {
  _FakeRealtimeHttpClient({this.createStatus = 201});

  final int createStatus;
  var createCalls = 0;
  String? lastInputText;

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    if (request.method == 'POST' &&
        request.url.path == '/realtime/text/sessions') {
      createCalls += 1;
      if (request is http.Request) {
        final body = jsonDecode(request.body) as Map<String, Object?>;
        lastInputText = body['input_text'] as String?;
      }
      if (createStatus != 201) {
        return _jsonResponse(createStatus, <String, Object?>{
          'code': 'create_failed',
          'message': 'safe create failure',
          'retryable': true,
          'response_body': 'raw body',
          'path': '/realtime/text/sessions',
        });
      }
      return _jsonResponse(201, _createResponse());
    }
    if (request.method == 'GET' &&
        request.url.path == '/realtime/text/sessions/session-1/events') {
      return http.StreamedResponse(const Stream<List<int>>.empty(), 200);
    }
    return _jsonResponse(404, <String, Object?>{
      'code': 'unexpected_request',
      'message': 'Unexpected fake request.',
      'retryable': false,
    });
  }
}

http.StreamedResponse _jsonResponse(int status, Map<String, Object?> body) {
  return http.StreamedResponse(
    Stream<List<int>>.value(utf8.encode(jsonEncode(body))),
    status,
    headers: const {'content-type': 'application/json'},
  );
}

Map<String, Object?> _createResponse() {
  return <String, Object?>{
    'accepted': true,
    'session': <String, Object?>{
      'session_id': 'session-1',
      'state': 'streaming',
      'active_turn_id': 'turn-1',
      'last_sequence': 0,
      'is_closed': false,
      'cancel_mode': 'cooperative',
      'hard_cancel_supported': false,
    },
    'turn': <String, Object?>{
      'session_id': 'session-1',
      'turn_id': 'turn-1',
      'state': 'streaming',
      'chunk_count': 0,
      'output_char_count': 0,
      'cancel_requested': false,
      'terminal_outcome': null,
    },
    'events_path': '/realtime/text/sessions/session-1/events',
    'cancel_path': '/realtime/text/sessions/session-1/cancel',
    'idle_ttl_seconds': 30,
    'max_duration_seconds': 120,
    'max_pending_events': 64,
    'max_event_bytes': 32768,
  };
}
